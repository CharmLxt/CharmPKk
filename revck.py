"""revck — Интерактивный учебник, тест и песочница CharmPkk."""
import sys
import tempfile
import shutil
import platform
import webbrowser
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from pathlib import Path

def _version():
    try:
        from .version import __version__
        return __version__
    except Exception:
        return "unknown"

def _import_all():
    status = {}
    for mod in ["seclipse", "network", "console", "window", "xeron", "xeronlegacy", "browser", "terminals", "memory", "files"]:
        try:
            __import__(f"charmpkk.{mod}")
            status[mod] = True
        except Exception as e:
            status[mod] = f"{type(e).__name__}: {e}"
    return status

def main():
    try:
        from . import console as c
        from . import seclipse as S
        from . import xeron as X
        from . import browser
        from . import memory
        from .terminals import run_pretmod, run_collquan
    except Exception as e:
        print(f"Критическая ошибка загрузки CharmPkk: {e}")
        return 1

    p = c.get_theme("tokyo_night")
    version = _version()

    def clear():
        c.terminal().clear()

    def pause(msg="Нажмите Enter, чтобы вернуться"):
        try:
            input(c.colorize(f"\n  {msg}… ", fg=c.fg_hex(p.muted), style=c.DIM))
        except (EOFError, KeyboardInterrupt):
            pass

    def show_docs():
        while True:
            clear()
            print(c.banner("Документация", "Выберите раздел", fg=c.fg_hex(p.accent)))
            choice = c.select(
                "Что изучаем?",
                [
                    "🏗️  Архитектура (Три модуля)",
                    "📁  S()eclipse (Файлы и Сеть)",
                    "🎨  Xeron (Интерфейс и Браузер)",
                    "🧩  XeronLegacy (Комбайн)",
                    "🧠  MemoryReader (Безопасное чтение памяти)",
                    "← Назад",
                ],
                fg_cursor=c.fg_hex(p.accent)
            )
            if not choice or choice == "← Назад":
                return

            clear()
            if choice.startswith("🏗️"):
                print(c.banner("Архитектура", "Общая картина", fg=c.fg_hex(p.accent)))
                print(c.box(
                    [
                        "CharmPkk разделен на слои, чтобы вы брали только то, что нужно:",
                        "",
                        c.colorize("1. S()eclipse", style=c.BOLD, fg=c.fg_hex(p.success)),
                        "   Для скриптов, установщиков и ботов. Без визуала.",
                        "   Умеет: качать файлы, работать с архивами, искать текст.",
                        "",
                        c.colorize("2. Xeron", style=c.BOLD, fg=c.fg_hex(p.warning)),
                        "   Для визуала (консоль и окно). Темы, анимации, браузер.",
                        "   Умеет: рисовать рамки, меню, окна с акрилом.",
                        "",
                        c.colorize("3. XeronLegacy", style=c.BOLD, fg=c.fg_hex(p.danger)),
                        "   Комбинирует UI и файлы. Идеален для установщиков.",
                    ],
                    title="Как устроена библиотека", style="round", border_fg=c.fg_hex(p.accent)
                ))
                pause()

            elif choice.startswith("📁"):
                print(c.banner("S()eclipse", "Файлы и Сеть", fg=c.fg_hex(p.success)))
                print(c.box(
                    [
                        "from charmpkk import seclipse as S",
                        "",
                        "# Скачивание с имитацией браузера",
                        "S.download_via('https://...', 'app.zip', browser='chrome')",
                        "",
                        "# Архивы (zip, tar, 7z, rar)",
                        "S.extract_auto('archive.7z', 'C:/target')",
                        "",
                        "# Поиск по файлам",
                        "for path, line, text in S.search_in_files('./src', 'TODO'):",
                        "    print(f'{path}:{line} -> {text}')",
                    ],
                    title="Примеры кода", style="round", border_fg=c.fg_hex(p.success)
                ))
                pause()

            elif choice.startswith("🎨"):
                print(c.banner("Xeron", "Интерфейс и Браузер", fg=c.fg_hex(p.warning)))
                print(c.box(
                    [
                        "from charmpkk import xeron as X",
                        "",
                        "# Меню и рамки",
                        "X.select('Выбери', ['А', 'Б'])",
                        "print(X.box('Привет', title='Мир'))",
                        "",
                        "# Оконный режим",
                        "app = X.window.App('Мое окно')",
                        "app.run()",
                        "",
                        "# Браузер",
                        "X.browser.run()",
                    ],
                    title="Примеры кода", style="round", border_fg=c.fg_hex(p.warning)
                ))
                pause()

            elif choice.startswith("🧩"):
                print(c.banner("XeronLegacy", "UI + Файлы", fg=c.fg_hex(p.danger)))
                print(c.box(
                    [
                        "from charmpkk import xeronlegacy as XL",
                        "",
                        "# Красивый установщик",
                        "XL.console.banner('Установка', 'v1.0')",
                        "XL.install_gears(duration=2, text='Подготовка')",
                        "XL.copy_with_progress('./build', 'C:/App')",
                        "XL.install_complete()",
                    ],
                    title="Примеры кода", style="round", border_fg=c.fg_hex(p.danger)
                ))
                pause()

            elif choice.startswith("🧠"):
                print(c.banner("MemoryReader", "Чтение памяти", fg=c.fg_hex(p.accent)))
                print(c.box(
                    [
                        "from charmpkk import MemoryReader",
                        "m = MemoryReader()",
                        "",
                        "# Найти PID процесса",
                        "pids = m.get_pids('notepad.exe')",
                        "",
                        "# Прочитать значение по адресу",
                        "val = m.read_int(pids[0], 0x140000000)",
                        "",
                        "# Многоуровневый указатель",
                        "val = m.read_pointer_value(pid, base_addr, [0x10, 0x20])",
                    ],
                    title="Примеры кода", style="round", border_fg=c.fg_hex(p.accent)
                ))
                pause()

    def run_tests():
        clear()
        print(c.banner("Тест системы", "Проверка всех модулей", fg=c.fg_hex(p.accent)))
        print(c.info("  Запуск глубокой проверки...\n"))

        status = _import_all()
        for name, res in status.items():
            if res is True:
                print(f"  {c.colorize('✓', fg=c.fg_hex(p.success))} Модуль {name}")
            else:
                print(f"  {c.colorize('✗', fg=c.fg_hex(p.danger))} Модуль {name}: {res}")

        print("\n" + c.section("Файловая система и Архивы", width=60, fg=c.fg_hex(p.accent)))
        tmp = Path(tempfile.mkdtemp(prefix="charmpkk_test_"))
        try:
            src_dir = tmp / "src"
            src_dir.mkdir()
            (src_dir / "test.txt").write_text("hello", encoding="utf-8")

            zip_path = tmp / "test.zip"
            S.make_zip(src_dir, zip_path)
            print(f"  ✓ Архивация: {zip_path.name} создан")

            copy_dir = tmp / "copy"
            stats = S.copy_tree(src_dir, copy_dir)
            print(f"  ✓ Копирование: {stats['files']} файлов")

            extract_dir = tmp / "extracted"
            extracted = S.extract_auto(zip_path, extract_dir)
            print(f"  ✓ Распаковка: {extracted.exists()}")
        except Exception as e:
            print(f"  ✗ Ошибка файлов: {e}")
        finally:
            shutil.rmtree(str(tmp), ignore_errors=True)

        print("\n" + c.section("Сеть и Интернет", width=60, fg=c.fg_hex(p.accent)))
        try:
            from .network import get_public_ip, is_port_open, check_url
            ip = get_public_ip()
            print(f"  ✓ Внешний IP: {ip or 'Не удалось получить'}")
            
            is_open = is_port_open("google.com", 80)
            print(f"  ✓ Порт 80 google.com: {'Открыт' if is_open else 'Закрыт'}")
            
            online = S.is_online()
            print(f"  ✓ Сеть: {'Доступна' if online else 'Нет доступа'}")
        except Exception as e:
            print(f"  ✗ Ошибка сети: {e}")

        print("\n" + c.section("Браузер (Парсинг)", width=60, fg=c.fg_hex(p.accent)))
        try:
            results = browser.BrowserEngine.search("python")
            print(f"  ✓ Поиск DuckDuckGo: найдено {len(results)} результатов")
            if results:
                print(f"    (Первый: {results[0]['title'][:30]}...)")
        except Exception as e:
            print(f"  ✗ Ошибка браузера: {e}")

        print("\n" + c.section("Чтение памяти (Read-Only)", width=60, fg=c.fg_hex(p.accent)))
        try:
            m = memory.MemoryReader()
            target = "explorer.exe" if platform.system() == "Windows" else "bash"
            pids = m.get_pids(target)
            if pids:
                base = m.get_base_address(pids[0], target)
                print(f"  ✓ Найден {target} (PID: {pids[0]})")
                print(f"  ✓ Базовый адрес: {hex(base) if base else 'Не найден'}")
            else:
                print(f"  ! Процесс {target} не найден, пропускаем.")
        except Exception as e:
            print(f"  ✗ Ошибка памяти: {e}")

        print("\n" + c.section("Cllqn Скрипты", width=60, fg=c.fg_hex(p.accent)))
        try:
            from .cllqn import CllqnScript
            script_text = "---\nname: Test\n---\necho Hello\nsleep 0.1\n"
            script = CllqnScript(script_text)
            ok, errors = script.validate()
            print(f"  ✓ Парсинг Cllqn: {'OK' if ok else errors}")
        except Exception as e:
            print(f"  ✗ Ошибка Cllqn: {e}")

        print("\n" + c.section("Консольный UI", width=60, fg=c.fg_hex(p.accent)))
        try:
            out = c.box("Тест", title="Рамка")
            assert "Тест" in out
            print("  ✓ Рамки и цвета работают")
            print(f"  ✓ Тем консоли: {len(c.list_themes())}")
        except Exception as e:
            print(f"  ✗ Ошибка UI: {e}")

        print("\n" + c.success("Тест завершен!"))
        pause()

    def run_playground():
        while True:
            clear()
            print(c.banner("Песочница", "Попробуй в деле", fg=c.fg_hex(p.success)))
            choice = c.select(
                "Что запустим?",
                [
                    "🌅 Нарисовать закат",
                    "🌐 Открыть браузер",
                    "📦 Скачать и распаковать",
                    "🎨 Сменить тему",
                    "🧠 Чтение памяти (Notepad)",
                    "🖥️  Запустить Pretmod",
                    "🕳️  Запустить Collquan",
                    "← Назад",
                ],
                fg_cursor=c.fg_hex(p.accent)
            )
            if not choice or choice == "← Назад":
                return

            clear()
            if choice.startswith("🌅"):
                print(c.render_sunset())
                pause()
            
            elif choice.startswith("🌐"):
                browser.run()
            
            elif choice.startswith("📦"):
                print(c.info("Скачаем тестовый файл..."))
                tmp = Path(tempfile.mkdtemp(prefix="charmpkk_play_"))
                try:
                    url = "https://raw.githubusercontent.com/python/cpython/main/README.rst"
                    dst = tmp / "readme.rst"
                    with c.Spinner("Скачивание...", fg=c.fg_hex(p.accent)):
                        S.download(url, dst)
                    print(c.success(f"Скачано: {S.human_size(dst.stat().st_size)}"))
                except Exception as e:
                    print(c.error(f"Ошибка: {e}"))
                finally:
                    shutil.rmtree(str(tmp), ignore_errors=True)
                pause()
            
            elif choice.startswith("🎨"):
                themes = c.list_themes()
                theme_choice = c.select("Выберите тему", themes, fg_cursor=c.fg_hex(p.accent))
                if theme_choice:
                    print(c.colorize(f"Тема {theme_choice} выбрана!", fg=c.fg_hex(p.accent)))
                pause()

            elif choice.startswith("🧠"):
                try:
                    import subprocess
                    print(c.info("Открываем Блокнот для теста..."))
                    proc = subprocess.Popen(["notepad.exe"])
                    import time
                    time.sleep(1)
                    
                    m = memory.MemoryReader()
                    pids = m.get_pids("notepad.exe")
                    if pids:
                        print(c.success(f"Блокнот найден (PID: {pids[0]})"))
                        base = m.get_base_address(pids[0], "notepad.exe")
                        print(f"Базовый адрес памяти: {hex(base)}")
                    else:
                        print(c.error("Не удалось найти процесс."))
                    proc.terminate()
                except Exception as e:
                    print(c.error(f"Ошибка: {e}"))
                pause()

            elif choice.startswith("🖥️"):
                run_pretmod()
                pause()
            
            elif choice.startswith("🕳️"):
                run_collquan()
                pause()

    def show_support():
        while True:
            clear()
            print(c.banner("Поддержка", "Связаться с автором", fg=c.fg_hex(p.warning)))
            print(c.box(
                [
                    "Нашли баг? Есть идея?",
                    "Выберите способ связи:",
                    "",
                    "1. Через консоль — анонимное письмо от бота.",
                    "   (Может не дойти, если провайдер блокирует спам)",
                    "",
                    "2. Через браузер — откроет ваш почтовый клиент.",
                    "   (Гарантированная доставка, пишете от себя)",
                ],
                title="Как отправить?", border_fg=c.fg_hex(p.warning)
            ))
            
            choice = c.select("Что делаем?", [
                "📨 Отправить через консоль (Бот)",
                "📧 Открыть почтовый клиент",
                "← Назад"
            ], fg_cursor=c.fg_hex(p.accent))
            
            if not choice or choice.startswith("←"):
                return
                
            if choice.startswith("📨"):
                subject = c.ask("Тема письма", default="Баг-репорт CharmPkk")
                body = c.ask("Опишите проблему (кратко)")
                if not body:
                    c.warning("Отменено.")
                    pause()
                    continue
                
                print(c.info("Отправка письма..."))
                try:
                    msg = MIMEText(body, 'plain', 'utf-8')
                    msg['Subject'] = subject
                    msg['From'] = "charmpkk-bot@mail.ru"
                    msg['To'] = "reception.mailspypi@gmail.com"
                    
                    with smtplib.SMTP('smtp.mail.ru', 25, timeout=5) as server:
                        server.send_message(msg)
                    c.success("Письмо отправлено (анонимно)!")
                except smtplib.SMTPException as e:
                    c.error(f"Ошибка SMTP: {e}")
                    c.info("Скорее всего, ваш провайдер блокирует прямые SMTP-запросы.")
                except Exception as e:
                    c.error(f"Ошибка отправки: {e}")
                pause()

            elif choice.startswith("📧"):
                subject = c.ask("Тема письма", default="Баг-репорт CharmPkk")
                body = c.ask("Опишите проблему (кратко)")
                if not body:
                    c.warning("Отменено.")
                    pause()
                    continue
                
                mailto_url = f"mailto:reception.mailspypi@gmail.com?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"
                webbrowser.open(mailto_url)
                c.success("Почтовый клиент открыт. Осталось нажать «Отправить»!")
                pause()

    def show_system():
        clear()
        print(c.banner("О системе", "Информация", fg=c.fg_hex(p.muted)))
        print(c.key_value({
            "Версия CharmPkk": version,
            "ОС": f"{platform.system()} {platform.release()}",
            "Python": platform.python_version(),
            "Архитектура": platform.machine(),
            "Автор": "CharmLxt",
            "Почта": "reception.mailspypi@gmail.com",
        }, key_fg=c.fg_hex(p.accent)))
        pause()

    def main_menu():
        while True:
            clear()
            print()
            print(c.big_text("CHARM", gradient=(p.accent, p.success)))
            print(c.colorize(f"  CharmPkk v{version} — Интерактивный гид", fg=c.fg_hex(p.muted)))
            print(c.colorize(f"  Автор: CharmLxt | reception.mailspypi@gmail.com", fg=c.fg_hex(p.muted), style=c.DIM))
            print()

            choice = c.select(
                "Выберите раздел:",
                [
                    "📖 Документация (Как это работает)",
                    "🧪 Тест системы (Проверка всех модулей)",
                    "🎮 Песочница (Попробовать в деле)",
                    "🆘 Поддержка (Связаться с автором)",
                    "ℹ️  О системе (Версия и платформа)",
                    "❌ Выход",
                ],
                fg_cursor=c.fg_hex(p.accent),
                fg_title=c.fg_hex(p.accent),
                hint="↑/↓ — навигация, Enter — выбрать, q — выйти"
            )

            if choice is None or choice.startswith("❌"):
                clear()
                print(c.colorize("\n  До встречи! Удачного кодинга.\n", fg=c.fg_hex(p.accent)))
                return 0

            try:
                if choice.startswith("📖"): show_docs()
                elif choice.startswith("🧪"): run_tests()
                elif choice.startswith("🎮"): run_playground()
                elif choice.startswith("🆘"): show_support()
                elif choice.startswith("ℹ"): show_system()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                clear()
                print(c.error(f"Ошибка: {type(e).__name__}: {e}"))
                pause()

    return main_menu()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        sys.exit(130)