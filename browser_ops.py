"""Скачивание с выбором браузера и открытие ссылок."""
import webbrowser
import subprocess
import sys

from .download import download

USER_AGENTS = {
    "chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "edge": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "firefox": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "safari": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "local": "CharmPkk/1.26.0",
}


def download_via(url, path, browser="chrome", progress=None, **kwargs):
    """Скачивает файл, имитируя выбранный браузер через User-Agent.
    browser: 'chrome' | 'edge' | 'firefox' | 'safari' | 'local'
    """
    ua = USER_AGENTS.get(browser, USER_AGENTS["chrome"])
    headers = {
        "User-Agent": ua,
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "identity",
    }
    return download(url, path, progress=progress, headers=headers, **kwargs)


def open_in_browser(url, browser="default"):
    """Открывает ссылку во внешнем браузере.
    browser: 'default' | 'chrome' | 'edge' | 'firefox' | 'safari'
    """
    if browser == "default":
        webbrowser.open(url)
        return "default"

    if sys.platform == "win32":
        cmd_map = {
            "chrome": ["start", "chrome", url],
            "edge": ["start", "msedge", url],
            "firefox": ["start", "firefox", url],
        }
        if browser in cmd_map:
            try:
                subprocess.Popen(cmd_map[browser], shell=True)
                return browser
            except Exception:
                pass
    else:
        cmd_map = {
            "chrome": ["google-chrome", url],
            "firefox": ["firefox", url],
        }
        if browser in cmd_map:
            try:
                subprocess.Popen(cmd_map[browser])
                return browser
            except FileNotFoundError:
                pass

    webbrowser.open(url)
    return "default"


def detect_browsers():
    """Возвращает список установленных браузеров."""
    available = ["default"]
    if sys.platform == "win32":
        checks = [("chrome", "chrome"), ("edge", "msedge"), ("firefox", "firefox")]
        for name, cmd in checks:
            try:
                r = subprocess.run(["where", cmd], capture_output=True, text=True, timeout=2)
                if r.returncode == 0:
                    available.append(name)
            except Exception:
                pass
    else:
        checks = [("chrome", "google-chrome"), ("firefox", "firefox")]
        for name, cmd in checks:
            try:
                r = subprocess.run(["which", cmd], capture_output=True, text=True, timeout=2)
                if r.returncode == 0:
                    available.append(name)
            except Exception:
                pass
    return available


def download_interactive(url=None, path=None, browser=None):
    """Интерактивное скачивание через UI CharmPkk."""
    from ..console import ask, select, get_theme, success, error, info, fg_hex

    p = get_theme("tokyo_night")
    if not url:
        url = ask("URL для скачивания", fg=fg_hex(p.accent))
    if not url:
        return None
    if not path:
        path = ask("Куда сохранить", default="./download.bin", fg=fg_hex(p.accent))
    if not path:
        return None

    if not browser:
        browsers = detect_browsers()
        labels = ["Local (CharmPkk)"] + [b.capitalize() for b in browsers if b != "default"]
        labels.append("Открыть во внешнем браузере")
        choice = select("Через что читать?", labels, fg_cursor=fg_hex(p.accent))
        if not choice:
            return None
        if choice == "Открыть во внешнем браузере":
            ext_browser = select("Какой браузер?", ["chrome", "edge", "firefox", "default"],
                                 fg_cursor=fg_hex(p.accent))
            open_in_browser(url, ext_browser or "default")
            info(f"Открыто в {ext_browser or 'default'}. Скачайте вручную.")
            return None
        elif choice == "Local (CharmPkk)":
            browser = "local"
        else:
            browser = choice.lower()

    try:
        info(f"Скачивание через {browser}...")
        result = download_via(url, path, browser=browser)
        success(f"Сохранено в {result}")
        return result
    except Exception as e:
        error(f"Ошибка: {e}")
        return None