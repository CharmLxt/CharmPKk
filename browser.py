"""Полноценный консольный и оконный браузер CharmPkk."""
import urllib.request
import urllib.parse
import urllib.error
import re
import hashlib
import gzip
import zlib
import socket
import time
import html as html_module
import sys
import json
import http.cookiejar
from html.parser import HTMLParser
from pathlib import Path

from .files import ensure_dir, write_text, read_text, remove_tree

CACHE_VERSION = 4
CACHE_DIR = Path.home() / ".charmpkk" / "cache"
BOOKMARKS_FILE = Path.home() / ".charmpkk" / "bookmarks.json"

try:
    if CACHE_DIR.exists():
        marker = CACHE_DIR / f"v{CACHE_VERSION}.marker"
        if not marker.exists():
            remove_tree(CACHE_DIR)
            ensure_dir(CACHE_DIR)
            write_text(marker, "ok")
    else:
        ensure_dir(CACHE_DIR)
        write_text(CACHE_DIR / f"v{CACHE_VERSION}.marker", "ok")
except Exception:
    pass

_COOKIE_JAR = http.cookiejar.CookieJar()
_LAST_URL = {"url": None}

MAX_RESPONSE_SIZE = 10 * 1024 * 1024
MAX_TOTAL_TIME = 20

VOID_ELEMENTS = {"area", "base", "br", "col", "embed", "hr", "img",
                 "input", "link", "meta", "param", "source", "track", "wbr"}
NEWLINE_TAGS = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
                "li", "tr", "section", "article", "blockquote", "pre", "table"}

def _load_bookmarks():
    if not BOOKMARKS_FILE.exists():
        return []
    try:
        return json.loads(BOOKMARKS_FILE.read_text("utf-8"))
    except Exception:
        return []

def _save_bookmarks(bookmarks):
    BOOKMARKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    BOOKMARKS_FILE.write_text(json.dumps(bookmarks, indent=2, ensure_ascii=False), "utf-8")

def _add_bookmark(url, title):
    bookmarks = _load_bookmarks()
    if not any(b["url"] == url for b in bookmarks):
        bookmarks.append({"url": url, "title": title, "date": time.strftime("%Y-%m-%d %H:%M:%S")})
        _save_bookmarks(bookmarks)
        return True
    return False

def _looks_like_url(query):
    if not query or " " in query.strip():
        return False
    if query.startswith(("http://", "https://")):
        return True
    if "." in query or ":" in query:
        return True
    return False

def _normalize_url(url):
    if url.startswith(("http://", "https://")):
        return url
    if url.startswith(("localhost", "127.", "192.168.", "10.", "172.")):
        return "http://" + url
    return "https://" + url

def _extract_main_html(html):
    for tag in ("main", "article"):
        pattern = re.compile(rf'<{tag}[\s>].*?</{tag}>', re.DOTALL | re.IGNORECASE)
        matches = pattern.findall(html)
        if matches:
            combined = "\n".join(matches)
            text_only = re.sub(r'<.*?>', '', combined).strip()
            if len(text_only) > 200:
                return combined
    return html

class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.skip_tags = {"script", "style", "template", "noscript",
                          "iframe", "nav", "aside", "form", "button", "select"}
        self._skip_depth = 0
        self._current_link = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in VOID_ELEMENTS:
            if tag in ("br", "hr"):
                self.text.append("\n")
            return
        if tag in self.skip_tags:
            self._skip_depth += 1
        elif tag == "a":
            for name, value in attrs:
                if name == "href" and value and not value.startswith(("#", "javascript:", "mailto:")):
                    self._current_link = value
        elif tag in NEWLINE_TAGS:
            self.text.append("\n")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID_ELEMENTS:
            return
        if tag in self.skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1
        elif tag == "a" and self._current_link:
            self._current_link = None
        elif tag in NEWLINE_TAGS:
            self.text.append("\n")

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        clean = data.strip()
        if not clean:
            return
        self.text.append(clean + " ")
        if self._current_link:
            self.links.append((clean, self._current_link))

    def get_text(self):
        raw = "".join(self.text)
        raw = raw.replace("\r\n", "\n").replace("\r", "\n")
        raw = html_module.unescape(raw)
        raw = re.sub(r'[ \t]+', ' ', raw)
        raw = re.sub(r'\n\s*\n+', '\n\n', raw)
        return raw.strip()

class BrowserEngine:
    @staticmethod
    def _fetch(url, referer=None):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "identity",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin" if referer else "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        }
        ref = referer or _LAST_URL.get("url")
        if ref:
            headers["Referer"] = ref

        req = urllib.request.Request(url, headers=headers)
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_COOKIE_JAR))

        try:
            resp = opener.open(req, timeout=8)
            start = time.time()
            raw = b""
            while True:
                if time.time() - start > MAX_TOTAL_TIME:
                    return None, "", f"Превышено время ожидания ({MAX_TOTAL_TIME} сек)"
                try:
                    chunk = resp.read1(8192)
                except (socket.timeout, TimeoutError):
                    if raw:
                        break
                    return None, "", "Сервер не отвечает (таймаут)"
                if not chunk:
                    break
                raw += chunk
                if len(raw) > MAX_RESPONSE_SIZE:
                    break

            try:
                encoding = resp.headers.get("Content-Encoding", "").lower()
                content_type = resp.headers.get("Content-Type", "").lower()
            finally:
                resp.close()

            if encoding == "gzip":
                try:
                    raw = gzip.decompress(raw)
                except Exception:
                    return None, content_type, "Ошибка: некорректный gzip"
            elif encoding == "deflate":
                try:
                    raw = zlib.decompress(raw)
                except Exception:
                    return None, content_type, "Ошибка: некорректный deflate"
            elif encoding == "br":
                try:
                    import brotli
                    raw = brotli.decompress(raw)
                except ImportError:
                    return None, content_type, "Сервер отдал Brotli, установите: pip install brotli"
                except Exception:
                    return None, content_type, "Ошибка: некорректный brotli"

            charset_match = re.search(r'charset=([\w-]+)', content_type, re.IGNORECASE)
            if charset_match:
                charset = charset_match.group(1)
            else:
                preview = raw[:3000].decode('ascii', errors='replace')
                meta_match = re.search(r'<meta[^>]+charset=["\']?([\w-]+)', preview, re.IGNORECASE)
                charset = meta_match.group(1) if meta_match else 'utf-8'

            try:
                text = raw.decode(charset, errors='replace')
            except LookupError:
                text = raw.decode('utf-8', errors='replace')

            _LAST_URL["url"] = url
            return text, content_type, None

        except urllib.error.HTTPError as e:
            if e.code == 403:
                return None, "", f"403 Forbidden.\nСайт блокирует автоматические запросы (антибот/Cloudflare).\nОткройте вручную: {url}"
            elif e.code == 404:
                return None, "", f"404 Not Found.\nСтраница не существует: {url}"
            elif e.code == 429:
                return None, "", f"429 Too Many Requests.\nСлишком много запросов. Подождите немного."
            elif e.code == 401:
                return None, "", f"401 Unauthorized.\nТребуется авторизация: {url}"
            else:
                return None, "", f"HTTP {e.code} {e.reason}:\n{url}"
        except urllib.error.URLError as e:
            reason = str(getattr(e, "reason", e))
            return None, "", f"Сетевая ошибка: {reason}"
        except (socket.timeout, TimeoutError):
            return None, "", f"Таймаут: сервер не ответил вовремя ({url})"
        except Exception as e:
            return None, "", f"Ошибка: {type(e).__name__}: {e}"

    @staticmethod
    def search(query):
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
        html, _, err = BrowserEngine._fetch(url)
        if err or not html:
            return []

        results = []
        pattern = re.compile(
            r'<a rel="nofollow" class="result__a" href="(.*?)">(.*?)</a>'
            r'.*?<a class="result__snippet".*?>(.*?)</a>',
            re.DOTALL,
        )
        for match in pattern.finditer(html):
            link = match.group(1)
            title = html_module.unescape(re.sub(r'<.*?>', '', match.group(2)).strip())
            snippet = html_module.unescape(re.sub(r'<.*?>', '', match.group(3)).strip())

            if "uddg=" in link:
                link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])

            results.append({"title": title, "url": link, "snippet": snippet})
        return results

    @staticmethod
    def read_page(url):
        url = _normalize_url(url)

        html = None
        content_type = "text/html"
        err = None
        cache_file = CACHE_DIR / f"v{CACHE_VERSION}_{hashlib.md5(url.encode()).hexdigest()}.html"
        try:
            if cache_file.exists():
                html = read_text(cache_file)
        except Exception:
            html = None

        if html is None:
            html, content_type, err = BrowserEngine._fetch(url)
            if err:
                return "Ошибка", err, [], err
            if not html:
                return "Ошибка", "Пустой ответ от сервера", [], "Пустой ответ"

            ct_lower = content_type.lower()
            is_html = ("text" in ct_lower or "html" in ct_lower
                       or "xml" in ct_lower or not ct_lower)
            if not is_html:
                return (
                    "Файл",
                    f"Это не HTML-страница.\nТип содержимого: {content_type or 'неизвестно'}.\n"
                    f"Скачайте файл через S.download_via(url, path).",
                    [],
                    None,
                )
            try:
                write_text(cache_file, html)
            except Exception:
                pass

        main_html = _extract_main_html(html)

        parser = _HTMLTextExtractor()
        try:
            parser.feed(main_html)
            parser.close()
        except Exception as e:
            return "Ошибка", f"Не удалось разобрать HTML: {e}", [], str(e)

        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
        title = html_module.unescape(title_match.group(1).strip()) if title_match else url

        text = parser.get_text()
        links = []
        seen = set()
        for txt, link_url in parser.links:
            if len(txt) < 2 or link_url in seen:
                continue
            if link_url.startswith(("#", "javascript:", "mailto:")):
                continue
            if not link_url.startswith(("http://", "https://")):
                link_url = urllib.parse.urljoin(url, link_url)
            seen.add(link_url)
            links.append((txt[:80], link_url))

        return title, text, links, None

# ============================================================
# КОНСОЛЬНЫЙ ИНТЕРФЕЙС
# ============================================================

def run_console():
    from .console import (
        ask, error, rule, get_theme, fg_hex, colorize,
        select, Spinner, banner, terminal, BOLD, Table, box, pause
    )

    p = get_theme("tokyo_night")
    clear = terminal().clear

    while True:
        clear()
        print(banner("BROWSER", "Поиск и чтение", fg=fg_hex(p.accent), gradient="ocean"))
        
        bookmarks = _load_bookmarks()
        if bookmarks:
            print(colorize("  ⭐ Быстрый доступ (Закладки):", fg=fg_hex(p.muted)))
            for b in bookmarks[:5]:
                print(f"    • {b['title'][:40]} — {b['url']}")
            print()

        query = ask("Введите запрос или URL (или /bm — закладки, q — выход)", fg=fg_hex(p.accent))
        if not query or query.lower() == "q":
            break
            
        if query == "/bm":
            clear()
            print(banner("BOOKMARKS", "Ваши закладки", fg=fg_hex(p.accent)))
            if not bookmarks:
                print(colorize("  У вас пока нет закладок.", fg=fg_hex(p.muted)))
            else:
                t = Table(headers=["Дата", "Заголовок", "Ссылка"], border_fg=fg_hex(p.border), header_fg=fg_hex(p.accent))
                for b in bookmarks:
                    t.add_row([b.get("date", ""), b["title"][:40], b["url"][:40]])
                print(t.render())
            pause()
            continue

        if _looks_like_url(query):
            clear()
            with Spinner("Загрузка страницы...", fg=fg_hex(p.accent)):
                title, text, links, err = BrowserEngine.read_page(query)
            if err:
                print(error(err))
                pause()
                continue
            _console_reader(title, text, links, query)
            continue

        clear()
        with Spinner(f"Поиск: {query}...", fg=fg_hex(p.accent)):
            results = BrowserEngine.search(query)

        if not results:
            print(error("Ничего не найдено или поисковик заблокировал запрос."))
            pause()
            continue

        while True:
            clear()
            print(banner("SEARCH", f"Запрос: {query}", fg=fg_hex(p.accent)))
            
            t = Table(headers=["#", "Заголовок", "Ссылка"], border_fg=fg_hex(p.border), header_fg=fg_hex(p.accent))
            for i, res in enumerate(results[:10], 1):
                t.add_row([str(i), res['title'][:50], res['url'][:40] + "..."])
            print(t.render())
            
            print()
            options = [f"{i}. {res['title'][:60]}" for i, res in enumerate(results[:10], 1)]
            choice = select("Выберите результат для чтения:", options + ["← Назад"], fg_cursor=fg_hex(p.accent))
            if not choice or choice == "← Назад":
                break

            idx = int(choice.split(".")[0]) - 1
            url = results[idx]['url']

            clear()
            with Spinner("Загрузка...", fg=fg_hex(p.accent)):
                title, text, links, err = BrowserEngine.read_page(url)
            if err:
                print(error(err))
                pause()
                continue
            _console_reader(title, text, links, url)

def _console_reader(title, text, links, url):
    from .console import (
        rule, get_theme, fg_hex, colorize, terminal, Spinner, error, BOLD, box, success
    )
    from .console.text import wrap as text_wrap
    from .console.menu import _get_key

    p = get_theme("tokyo_night")
    history = []
    current_url = url

    if not text or len(text.strip()) < 20:
        terminal().clear()
        print(box(f"На этой странице нет читаемого текста.\nСсылок найдено: {len(links)}", title=f"📄 {title[:60]}", border_fg=fg_hex(p.accent)))
        input("\n  Enter — назад...")
        return

    while True:
        terminal().clear()
        out = []
        out.append(colorize(f"  📄 {title[:70]}", fg=fg_hex(p.accent), style=BOLD))
        out.append(rule(width=74, fg=fg_hex(p.border)))
        out.append("")

        for line in text.split("\n"):
            if not line.strip():
                out.append("")
                continue
            for sub in text_wrap(line, 72):
                out.append("  " + sub)

        out.append("")
        out.append(rule(width=74, fg=fg_hex(p.border)))

        shown_links = links[:9] if links else []
        if shown_links:
            out.append(colorize("  🔗 Ссылки на странице:", fg=fg_hex(p.accent), style=BOLD))
            for i, (txt, _) in enumerate(shown_links, 1):
                out.append(f"  [{i}] {txt[:60]}")
            out.append("")
            back_hint = " | [B] Назад" if history else ""
            out.append(colorize(f"  [1-{len(shown_links)}] Перейти{back_hint} | [S] Сохранить | [M] В закладки | [Q] Выход", fg=fg_hex(p.muted)))
        else:
            back_hint = " | [B] Назад" if history else ""
            out.append(colorize(f"  [S] Сохранить | [M] В закладки | [Q] Выход{back_hint}", fg=fg_hex(p.muted)))

        sys.stdout.write("\n".join(out) + "\n")
        sys.stdout.flush()

        key = _get_key()

        if key in ("q", "Q", "esc"):
            return
            
        if key in ("s", "S"):
            try:
                filename = "article.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"{title}\n\n{text}\n\nИсточник: {current_url}")
                print(success(f"Статья сохранена в файл: {filename}"))
            except PermissionError:
                print(error("Ошибка доступа: Нет прав на запись в текущую папку."))
            except Exception as e:
                print(error(f"Ошибка сохранения: {e}"))
            input("Enter — продолжить...")
            continue

        if key in ("m", "M"):
            if _add_bookmark(current_url, title):
                print(success("Добавлено в закладки!"))
            else:
                print(error("Эта страница уже есть в закладках."))
            input("Enter — продолжить...")
            continue

        if key in ("b", "B") and history:
            title, text, links, current_url = history.pop()
            continue

        if key.isdigit() and shown_links:
            idx = int(key) - 1
            if 0 <= idx < len(shown_links):
                new_url = shown_links[idx][1]
                terminal().clear()
                print(colorize(f"  Загрузка: {new_url[:60]}...", fg=fg_hex(p.muted)))
                with Spinner("Загрузка...", fg=fg_hex(p.accent)):
                    new_title, new_text, new_links, err = BrowserEngine.read_page(new_url)
                if err:
                    print(error(err))
                    input("Enter — назад...")
                    continue
                history.append((title, text, links, current_url))
                title, text, links = new_title, new_text, new_links
                current_url = new_url
                continue

# ============================================================
# ОКОННЫЙ ИНТЕРФЕЙС
# ============================================================

def run_window():
    try:
        import tkinter as tk
        from .window import App, StyledEntry, StyledButton, Card, Badge
        from .window.theme import Theme
    except ImportError as e:
        print(f"tkinter или модуль window недоступен: {e}")
        return

    app = App("Charm Browser", size="1100x750", theme_name="liquid_glass")
    app.header("Charm Browser", "Современный просмотр веб-страниц")

    top_frame = tk.Frame(app.container, bg=app.theme.surface, padx=10, pady=10)
    top_frame.pack(fill="x", pady=(0, 10))
    
    btn_back = StyledButton(top_frame, "←", command=lambda: go_back(), variant="secondary", theme=app.theme, width=2)
    btn_back.pack(side="left", padx=(0, 5))
    
    btn_fwd = StyledButton(top_frame, "→", command=lambda: go_forward(), variant="secondary", theme=app.theme, width=2)
    btn_fwd.pack(side="left", padx=(0, 5))

    btn_refresh = StyledButton(top_frame, "🔄", command=lambda: load_page(current_url), variant="secondary", theme=app.theme, width=2)
    btn_refresh.pack(side="left", padx=(0, 5))
    
    url_entry = StyledEntry(top_frame, app.theme, placeholder="Введите запрос или URL...")
    url_entry.pack(side="left", fill="x", expand=True, padx=5)
    
    btn_go = StyledButton(top_frame, "Найти", command=lambda: do_search(), theme=app.theme)
    btn_go.pack(side="left", padx=(5, 0))

    tool_frame = tk.Frame(app.container, bg=app.theme.bg)
    tool_frame.pack(fill="x", pady=(0, 5))
    
    btn_save = StyledButton(tool_frame, "💾 Сохранить", command=lambda: save_article(), variant="ghost", size="sm", theme=app.theme)
    btn_save.pack(side="left")
    
    btn_bookmark = StyledButton(tool_frame, "⭐ В закладки", command=lambda: bookmark_page(), variant="ghost", size="sm", theme=app.theme)
    btn_bookmark.pack(side="left", padx=5)

    paned = tk.PanedWindow(app.container, orient="horizontal", bg=app.theme.bg, sashwidth=6, bd=0)
    paned.pack(fill="both", expand=True)

    left_card = Card(paned, app.theme, title="Ссылки", subtitle="Нажмите, чтобы перейти")
    listbox = tk.Listbox(left_card.inner, bg=app.theme.surface, fg=app.theme.fg,
                         font=app.theme.tk_font(), bd=0, highlightthickness=0,
                         selectbackground=app.theme.accent, selectforeground=app.theme.accent_fg)
    listbox.pack(fill="both", expand=True, pady=(10, 0))

    right_frame = tk.Frame(paned, bg=app.theme.surface, bd=1, relief="flat")
    text_area = tk.Text(right_frame, bg=app.theme.surface, fg=app.theme.fg,
                        font=app.theme.tk_font(), wrap="word", bd=0,
                        padx=20, pady=20, insertbackground=app.theme.accent)
    scrollbar = tk.Scrollbar(right_frame, command=text_area.yview, bd=0)
    text_area.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    text_area.pack(side="left", fill="both", expand=True)

    paned.add(left_card, width=320)
    paned.add(right_frame)

    state = {"links": [], "mode": "search", "history": [], "forward": [], "current_url": "", "current_text": "", "current_title": ""}

    def load_page(url, from_click=False):
        if not url: return
        state["mode"] = "page"
        state["current_url"] = url
        text_area.delete("1.0", "end")
        text_area.insert("end", "Загрузка...")
        app.root.update()

        title, text, links, err = BrowserEngine.read_page(url)
        state["links"] = links
        state["current_title"] = title
        state["current_text"] = text

        text_area.delete("1.0", "end")
        if err:
            text_area.insert("end", f"Ошибка:\n{err}")
            return

        text_area.insert("end", f"{title}\n\n", "title")
        if not text or len(text) < 20:
            text_area.insert("end", "(На этой странице нет читаемого текста.)")
        else:
            text_area.insert("end", text)

        text_area.tag_config("title", font=app.theme.tk_font(4, "bold"),
                             foreground=app.theme.accent, spacing3=10)

        for i, (txt, link_url) in enumerate(links[:50]):
            tag_name = f"link_{i}"
            start = "1.0"
            while True:
                pos = text_area.search(txt, start, stopindex="end", nocase=True)
                if not pos:
                    break
                end = f"{pos}+{len(txt)}c"
                text_area.tag_add(tag_name, pos, end)
                start = end
            text_area.tag_config(tag_name, foreground="#7aa2ff", underline=1)
            text_area.tag_bind(tag_name, "<Button-1>",
                               lambda e, u=link_url: load_page(u, from_click=True))
            text_area.tag_bind(tag_name, "<Enter>", lambda e: text_area.config(cursor="hand2"))
            text_area.tag_bind(tag_name, "<Leave>", lambda e: text_area.config(cursor=""))

        if from_click:
            state["history"].append(url)
            state["forward"].clear()

        listbox.delete(0, "end")
        for txt, _ in links[:30]:
            listbox.insert("end", f"🔗 {txt}")

    def on_listbox_select(event):
        w = event.widget
        if w.curselection():
            idx = w.curselection()[0]
            if idx < len(state["links"]):
                load_page(state["links"][idx][1], from_click=True)

    listbox.bind("<<ListboxSelect>>", on_listbox_select)

    def do_search():
        query = url_entry.get()
        if not query:
            return
        if _looks_like_url(query):
            load_page(query)
            return

        state["mode"] = "search"
        listbox.delete(0, "end")
        text_area.delete("1.0", "end")
        text_area.insert("end", "Поиск...")
        app.root.update()

        results = BrowserEngine.search(query)
        listbox.delete(0, "end")
        for res in results[:20]:
            listbox.insert("end", f"🔗 {res['title']}")

        text_area.delete("1.0", "end")
        text_area.insert("end", f"Найдено {len(results)} результатов.\nКликните на результат в списке слева.", "info")
        text_area.tag_config("info", foreground=app.theme.muted, font=app.theme.tk_font(1))
        state["links"] = [(r["title"], r["url"]) for r in results]

    def go_back():
        if state["history"]:
            state["forward"].append(state["current_url"])
            prev = state["history"].pop()
            load_page(prev, from_click=False)

    def go_forward():
        if state["forward"]:
            state["history"].append(state["current_url"])
            nxt = state["forward"].pop()
            load_page(nxt, from_click=False)

    def save_article():
        if state["mode"] == "page" and state["current_text"]:
            try:
                filename = "article.txt"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"{state['current_title']}\n\n{state['current_text']}\n\nИсточник: {state['current_url']}")
                app.toast(f"Сохранено в {filename}", variant="success")
            except PermissionError:
                app.toast("Нет прав на запись в эту папку", variant="error")
            except Exception as e:
                app.toast(f"Ошибка: {e}", variant="error")
        else:
            app.toast("Нечего сохранять", variant="warning")

    def bookmark_page():
        if state["mode"] == "page" and state["current_url"]:
            if _add_bookmark(state["current_url"], state["current_title"]):
                app.toast("Добавлено в закладки!", variant="success")
            else:
                app.toast("Уже в закладках", variant="info")
        else:
            app.toast("Сначала откройте страницу", variant="warning")

    url_entry.entry.bind("<Return>", lambda e: do_search())
    app.footer("Charm Browser ready", right_items=[f"Version 28.10.26b1"])
    app.run()

# ============================================================
# ГЛАВНОЕ МЕНЮ БРАУЗЕРА
# ============================================================

def run():
    from .console import banner, select, get_theme, fg_hex, terminal
    p = get_theme("tokyo_night")
    terminal().clear()
    print(banner("CHARM", "Выберите режим", fg=fg_hex(p.accent), gradient="cyberpunk"))
    choice = select("Как запустим?",
                    ["Консольный браузер", "Оконный браузер", "← Назад"],
                    fg_cursor=fg_hex(p.accent))

    if choice == "Консольный браузер":
        run_console()
    elif choice == "Оконный браузер":
        run_window()

def extract_urls(text):
    import re
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return list(set(url_pattern.findall(text)))