"""Встроенные терминалы CharmPkk: Pretmod и Collquan."""
import shlex
import platform
import re
import inspect
import subprocess
from pathlib import Path
from urllib.parse import urlparse
import traceback


def _sanitize_ident(name):
    return "".join(c if c.isalnum() or c == "_" else "_" for c in name)


class BaseShell:
    prompt = "> "
    title = "Terminal"
    _custom_commands = {}

    _system_commands = {
        "sh":       "Выполнить OS-команду: sh <cmd>",
        "files":    "Файлы: files <list|rm|mkdir> [path]",
        "net":      "Сеть: net <ping|get> [url]",
        "ui":       "Визуал: ui <sunset|banner|browser> [text]",
        "download": "Скачать файл: download <url>",
        "sys":      "Информация о системе",
        "test":     "Проверить интернет",
        "theme":    "Сменить цветовую тему",
        "run":      "Запустить .cllqn скрипт: run <file>",
        "lint":     "Проверить .cllqn скрипт: lint <file>",
        "history":  "Показать историю команд",
        "alias":    "Создать псевдоним: alias ll = files list .",
    }

    def __init__(self, theme="tokyo_night"):
        from . import console as c
        self.theme = c.get_theme(theme)
        self.running = True
        self._history = []
        self._aliases = {}

    @classmethod
    def register(cls, name, description=""):
        def wrapper(func):
            try:
                source = inspect.getsource(func)
                lines = source.split("\n")
                start = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith("def "):
                        start = i + 1
                        break
                body_lines = lines[start:]
                if body_lines:
                    non_empty = [l for l in body_lines if l.strip()]
                    if non_empty:
                        min_indent = min(len(l) - len(l.lstrip()) for l in non_empty)
                        body_lines = [
                            l[min_indent:] if len(l) >= min_indent else l
                            for l in body_lines
                        ]
                code = "\n".join(body_lines).rstrip()
            except (OSError, TypeError):
                code = ""
            cls._custom_commands[name] = {
                "func": func,
                "desc": description,
                "code": code,
            }
            return func
        return wrapper

    def print_banner(self):
        pass

    def get_commands(self):
        cmds = dict(self._system_commands)
        for name in sorted(self._custom_commands):
            desc = self._custom_commands[name].get("desc") or "своя"
            cmds[name] = f"→ {desc}"
        for name, target in self._aliases.items():
            cmds[name] = f"↳ {target}"
        return cmds

    def _handle_system_command(self, cmd, args, raw=""):
        from . import console as c
        from . import seclipse as S

        if cmd == "run":
            if not args:
                print(c.error("run <file.cllqn>"))
                return True
            from .cllqn import CllqnScript, CllqnRunner
            path = Path(args[0])
            if not path.exists():
                print(c.error(f"Файл не найден: {path}"))
                return True
            try:
                text = path.read_text(encoding="utf-8")
                script = CllqnScript(text)
                runner = CllqnRunner(self, script)
                runner.run()
            except Exception as e:
                print(c.error(f"Ошибка чтения скрипта: {e}"))
            return True

        if cmd == "lint":
            if not args:
                print(c.error("lint <file.cllqn>"))
                return True
            from .cllqn import CllqnScript
            path = Path(args[0])
            if not path.exists():
                print(c.error(f"Файл не найден: {path}"))
                return True
            try:
                text = path.read_text(encoding="utf-8")
                script = CllqnScript(text)
                ok, errors = script.validate()
                print(c.key_value({
                    "Имя": script.metadata.get("name", "—"),
                    "Версия": script.metadata.get("version", "—"),
                    "Админ": script.metadata.get("requires_admin", "false"),
                    "Команд": len(script.commands)
                }, key_fg=c.fg_hex(self.theme.accent)))
                if ok:
                    print(c.success("Синтаксис в порядке."))
                else:
                    for err in errors:
                        print(c.error(err))
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return True

        if cmd == "sh":
            os_cmd = raw[3:].strip() if raw.lower().startswith("sh ") else " ".join(args)
            if not os_cmd:
                print(c.error("sh <os-команда>"))
                return True
            print(c.colorize(f"  $ {os_cmd}", fg=c.fg_hex(self.theme.muted)))
            try:
                subprocess.run(os_cmd, shell=True, check=False)
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return True

        if cmd == "files":
            if not args:
                print(c.error("files <list|rm|mkdir> [path]"))
                return True
            sub = args[0].lower()
            path = args[1] if len(args) > 1 else "."
            try:
                if sub == "list":
                    for p in S.find(path):
                        print(f"  {'📁' if p.is_dir() else '📄'} {p.name}")
                elif sub == "rm":
                    if Path(path).is_dir():
                        S.remove_tree(path)
                    else:
                        S.remove_file(path)
                    print(c.success(f"Удалено: {path}"))
                elif sub == "mkdir":
                    S.ensure_dir(path)
                    print(c.success(f"Создана: {path}"))
                else:
                    print(c.error(f"Неизвестная подкоманда: {sub}"))
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return True

        if cmd == "net":
            if not args:
                print(c.error("net <ping|get> [url]"))
                return True
            sub = args[0].lower()
            url = args[1] if len(args) > 1 else ""
            try:
                if sub == "ping":
                    print(c.success("Интернет доступен") if S.is_online() else c.error("Нет интернета"))
                elif sub == "get":
                    if not url:
                        print(c.error("Укажите URL"))
                        return True
                    print(c.info(f"GET {url}..."))
                    text = S.fetch_text(url)
                    print(c.truncate(text, 500) + "\n...")
                else:
                    print(c.error(f"Неизвестная подкоманда: {sub}"))
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return True

        if cmd == "ui":
            if not args:
                print(c.error("ui <sunset|banner|browser> [text]"))
                return True
            from . import browser
            sub = args[0].lower()
            if sub == "sunset":
                print(c.render_sunset())
            elif sub == "browser":
                browser.run()
            elif sub == "banner":
                text = " ".join(args[1:]) if len(args) > 1 else "HELLO"
                print(c.big_text(text, gradient=(self.theme.accent, self.theme.success)))
            else:
                print(c.error(f"Неизвестная подкоманда: {sub}"))
            return True

        if cmd == "download":
            if not args:
                print(c.error("download <url>"))
                return True
            url = args[0]
            parsed = urlparse(url)
            filename = Path(parsed.path).name or "downloaded"
            try:
                print(c.info(f"Скачивание {url} -> {filename}..."))
                S.download(url, filename)
                print(c.success("Готово!"))
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return True

        if cmd == "sys":
            print(c.key_value({
                "ОС": f"{platform.system()} {platform.release()}",
                "Python": platform.python_version(),
                "CharmPkk": "28.10.26b1",
                "Терминал": self.title,
            }, key_fg=c.fg_hex(self.theme.accent)))
            return True

        if cmd == "test":
            try:
                online = S.is_online()
                print(c.success(f"Интернет: {'OK' if online else 'Нет'}"))
            except Exception as e:
                print(c.error(str(e)))
            return True

        if cmd == "theme":
            choice = c.select("Тема", c.list_themes(),
                              fg_cursor=c.fg_hex(self.theme.accent))
            if choice:
                self.theme = c.get_theme(choice)
                print(c.success(f"Тема: {choice}"))
            return True

        return False

    def execute(self, cmd, args, raw=""):
        pass

    def run(self):
        from . import console as c
        self.print_banner()
        while self.running:
            try:
                line = input(c.colorize(f"\n{self.prompt}",
                                        fg=c.fg_hex(self.theme.accent),
                                        style=c.BOLD))
            except (EOFError, KeyboardInterrupt):
                print()
                break

            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("//"):
                self._handle_block(stripped[2:])
                continue

            if stripped.lower() == "endoff":
                print(c.warning("endoff без открытого блока //"))
                continue

            cmd_lower = stripped.split()[0].lower()
            if cmd_lower in ("exit", "quit", "q"):
                self.running = False
                continue
            if cmd_lower == "clear":
                c.terminal().clear()
                continue
            if cmd_lower == "help":
                self._print_help()
                continue

            if cmd_lower == "history":
                if not self._history:
                    print(c.info("История пуста."))
                else:
                    for i, h in enumerate(self._history[-20:], 1):
                        print(f"  {i:>3}  {h}")
                continue
                
            if cmd_lower == "alias":
                parts = stripped.split("=", 1)
                if len(parts) == 2:
                    name = parts[0].replace("alias", "").strip()
                    target = parts[1].strip()
                    if name and target:
                        self._aliases[name] = target
                        print(c.success(f"Алиас '{name}' -> '{target}' создан."))
                    else:
                        print(c.error("Неверный формат алиаса."))
                else:
                    print(c.info("Использование: alias <имя> = <команда>"))
                continue

            if not self._history or self._history[-1] != stripped:
                self._history.append(stripped)

            first_word = stripped.split()[0]
            if first_word in self._aliases:
                target = self._aliases[first_word]
                rest_of_line = stripped[len(first_word):].strip()
                stripped = f"{target} {rest_of_line}".strip()
                cmd_lower = stripped.split()[0].lower()

            try:
                parts = shlex.split(stripped)
            except ValueError as e:
                print(c.error(f"Ошибка парсинга: {e}"))
                continue

            self.execute(parts[0].lower(), parts[1:], raw=stripped)

    def _print_help(self):
        from . import console as c
        print(c.banner("Справка", f"Доступные команды в {self.title}",
                       fg=c.fg_hex(self.theme.accent)))
        for k, v in sorted(self.get_commands().items()):
            print(f"  {c.colorize(k.ljust(22), fg=c.fg_hex(self.theme.accent), style=c.BOLD)} {v}")
        print()
        print(c.colorize("  Создание своих команд (блоки):",
                         fg=c.fg_hex(self.theme.accent), style=c.BOLD))
        print("    //name               — Python-код (многострочно)")
        print("    //name py            — явно Python")
        print("    //name cmd           — последовательность внутренних команд")
        print("    //name os            — последовательность OS-команд (shell)")
        print("    //name (код) endoff  — однострочный вариант")
        print("    endoff               — закрыть блок")

    def _handle_block(self, header):
        from . import console as c

        header_stripped = header.strip()
        inline_complete = False
        if header_stripped.lower().endswith(" endoff"):
            header_stripped = header_stripped[:-len(" endoff")].rstrip()
            inline_complete = True

        if not header_stripped:
            print(c.error("Нужно имя блока: //<name>"))
            return

        parts = header_stripped.split(None, 1)
        name = parts[0]
        rest = parts[1] if len(parts) > 1 else ""

        mode = None
        rest_lower = rest.lower()
        for m in ("cmd", "os", "py"):
            if rest_lower == m:
                mode = m
                rest = ""
                break
            if rest_lower.startswith(m + " "):
                mode = m
                rest = rest[len(m):].strip()
                break

        lines = []
        if rest:
            rest_stripped = rest.strip()
            if rest_stripped.startswith("(") and rest_stripped.endswith(")"):
                rest_stripped = rest_stripped[1:-1].strip()
            if rest_stripped:
                lines.append(rest_stripped)

        if not inline_complete:
            while True:
                try:
                    body = input(c.colorize("... ", fg=c.fg_hex(self.theme.muted)))
                except (EOFError, KeyboardInterrupt):
                    print(c.error("Блок отменён"))
                    return
                b_stripped = body.strip()
                if b_stripped.lower() == "endoff":
                    break
                if b_stripped.lower().endswith(" endoff"):
                    body_stripped = body.rstrip()[:-len(" endoff")].rstrip()
                    if body_stripped.strip():
                        lines.append(body_stripped)
                    break
                lines.append(body)

        if not lines or not any(l.strip() for l in lines):
            print(c.error("Пустой блок"))
            return

        if mode is None:
            mode = self._detect_mode(lines)

        code = "\n".join(lines)

        try:
            if mode == "os":
                cmds = [l.strip() for l in lines if l.strip()]

                def os_runner(args):
                    for cmd in cmds:
                        print(c.colorize(f"  $ {cmd}", fg=c.fg_hex(self.theme.muted)))
                        try:
                            subprocess.run(cmd, shell=True, check=False)
                        except Exception as e:
                            print(c.error(f"  Ошибка: {e}"))

                self._custom_commands[name] = {
                    "func": os_runner,
                    "desc": f"os shell ({len(cmds)})",
                    "code": code,
                }
                print(c.success(f"OS-команда '{name}' создана ({len(cmds)} команд)"))

            elif mode == "cmd":
                compiled = []
                for line in lines:
                    s = line.strip()
                    if not s:
                        continue
                    try:
                        sub_parts = shlex.split(s)
                    except ValueError as e:
                        print(c.error(f"Ошибка в '{s}': {e}"))
                        return
                    if sub_parts:
                        compiled.append((sub_parts[0], sub_parts[1:], s))

                def cmd_runner(args):
                    for cmd_name, cmd_args, raw_line in compiled:
                        self.execute(cmd_name, cmd_args, raw=raw_line)

                self._custom_commands[name] = {
                    "func": cmd_runner,
                    "desc": f"cmd block ({len(compiled)})",
                    "code": code,
                }
                print(c.success(f"Cmd-блок '{name}' создан ({len(compiled)} подкоманд)"))

            else:
                func = self._compile(name, code)
                self._custom_commands[name] = {
                    "func": func,
                    "desc": "python",
                    "code": code,
                }
                print(c.success(f"Python-команда '{name}' создана"))

        except Exception as e:
            print(c.error(f"Ошибка: {type(e).__name__}: {e}"))

    def _detect_mode(self, lines):
        shell_verbs = set(self._system_commands.keys()) | {
            "echo", "new", "edit", "show", "del", "save", "load",
            "clear", "help", "exit", "quit", "q", "history", "alias"
        } | set(self._custom_commands.keys())

        py_markers = (
            "def ", "class ", "import ", "from ", "print(",
            "if ", "elif ", "else:", "for ", "while ", "return ",
            "try:", "except ", "with ", "lambda ", "async ",
        )

        code = "\n".join(lines)
        for marker in py_markers:
            if marker in code:
                return "py"

        for line in lines:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.startswith("echo"):
                continue
            if "=" in s and not any(op in s for op in ("==", "!=", "<=", ">=")):
                return "py"

        all_internal = True
        for line in lines:
            s = line.strip()
            if not s:
                continue
            first = s.split()[0].lower()
            if first not in shell_verbs:
                all_internal = False
                break

        return "cmd" if all_internal else "py"

    def _compile(self, name, code):
        lines = code.split("\n")
        wrapped = ["def __cmd__(args):"]
        if not lines or not any(l.strip() for l in lines):
            wrapped.append("    pass")
        else:
            for line in lines:
                if line.strip():
                    wrapped.append("    " + line)
                else:
                    wrapped.append(line)
        source = "\n".join(wrapped)
        namespace = {"__builtins__": __builtins__}
        exec(source, namespace)
        return namespace["__cmd__"]


# ============================================================
# Pretmod
# ============================================================

class PretmodShell(BaseShell):
    prompt = "Pretmod > "
    title = "Pretmod"
    _custom_commands = {}

    def print_banner(self):
        from . import console as c
        c.terminal().clear()
        print(c.banner("Pretmod", "Интерпретатор CharmPkk",
                       fg=c.fg_hex(self.theme.accent)))
        print(c.colorize("  'help' — команды. // для своих блоков. 'exit' — выход.",
                         fg=c.fg_hex(self.theme.muted)))

    def get_commands(self):
        cmds = super().get_commands()
        cmds.update({
            "sys":   "Информация о системе",
            "test":  "Проверить интернет",
            "theme": "Сменить цветовую тему",
        })
        return cmds

    def execute(self, cmd, args, raw=""):
        from . import console as c

        if cmd in self._custom_commands:
            try:
                self._custom_commands[cmd]["func"](args)
            except Exception as e:
                print(c.error(f"Ошибка в '{cmd}': {e}"))
            return

        if self._handle_system_command(cmd, args, raw):
            return

        print(c.error(f"Команда '{cmd}' не найдена. Введите 'help'."))


# ============================================================
# Collquan
# ============================================================

class CollquanShell(BaseShell):
    prompt = "Collquan > "
    title = "Collquan"
    _custom_commands = {}

    def print_banner(self):
        from . import console as c
        c.terminal().clear()
        print(c.banner("Collquan", "Твой личный терминал",
                       fg=c.fg_hex(self.theme.accent)))
        print(c.colorize(
            "  'help' — справка. // для блоков. 'exit' — выход.",
            fg=c.fg_hex(self.theme.muted),
        ))
        print(c.colorize(
            "  Пример: //hello ( print('Hi ' + (args[0] if args else '')) ) endoff",
            fg=c.fg_hex(self.theme.muted),
        ))

    def get_commands(self):
        cmds = super().get_commands()
        cmds.update({
            "echo <text>":           "Вывести текст",
            "new <name> <code>":     "Однострочная Python-команда",
            "edit <name>":           "Изменить код многострочно",
            "show <name>":           "Показать код команды",
            "del <name>":            "Удалить команду",
            "save <file.py>":        "Сохранить все команды в файл",
            "load <file.py>":        "Загрузить команды из файла",
        })
        return cmds

    def execute(self, cmd, args, raw=""):
        from . import console as c

        if cmd in self._custom_commands:
            try:
                self._custom_commands[cmd]["func"](args)
            except Exception as e:
                print(c.error(f"Ошибка в '{cmd}': {e}"))
            return

        if cmd == "echo":
            print(" ".join(args))
            return

        if cmd == "new":
            m = re.match(r'^\s*new\s+(\S+)\s+(.+)$', raw, re.DOTALL)
            if not m:
                print(c.error("new <name> <код>"))
                return
            name = m.group(1)
            body = m.group(2).strip()
            if len(body) >= 2 and body[0] == body[-1] and body[0] in ('"', "'"):
                body = body[1:-1].strip()
            try:
                func = self._compile(name, body)
                self._custom_commands[name] = {"func": func, "desc": "one-line", "code": body}
                print(c.success(f"Команда '{name}' создана"))
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return

        if cmd == "edit":
            if not args:
                print(c.error("edit <name>"))
                return
            name = args[0]
            print(c.info(f"Введите код '{name}' (пустая строка — конец):"))
            body_lines = []
            while True:
                try:
                    l = input("... ")
                except (EOFError, KeyboardInterrupt):
                    break
                if not l:
                    break
                body_lines.append(l)
            body = "\n".join(body_lines)
            try:
                func = self._compile(name, body)
                self._custom_commands[name] = {"func": func, "desc": "edited", "code": body}
                print(c.success(f"Команда '{name}' обновлена"))
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return

        if cmd == "show":
            if not args:
                print(c.error("show <name>"))
                return
            name = args[0]
            if name not in self._custom_commands:
                print(c.error(f"'{name}' не найдена"))
                return
            code = self._custom_commands[name].get("code", "")
            if code:
                print(c.colorize("─" * 60, fg=c.fg_hex(self.theme.muted)))
                for line in code.split("\n"):
                    print("  " + line)
                print(c.colorize("─" * 60, fg=c.fg_hex(self.theme.muted)))
            else:
                print(c.warning("Исходный код недоступен"))
            return

        if cmd == "del":
            if not args:
                print(c.error("del <name>"))
                return
            name = args[0]
            if name in self._custom_commands:
                del self._custom_commands[name]
                print(c.success(f"'{name}' удалена"))
            else:
                print(c.error(f"'{name}' не найдена"))
            return

        if cmd == "save":
            if not args:
                print(c.error("save <file.py>"))
                return
            try:
                self._save_to_file(args[0])
                print(c.success(f"Сохранено в {args[0]}"))
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return

        if cmd == "load":
            if not args:
                print(c.error("load <file.py>"))
                return
            try:
                total, new = self._load_from_file(args[0])
                print(c.success(f"Загружено: {total} команд (новых: {new})"))
            except Exception as e:
                print(c.error(f"Ошибка: {e}"))
            return

        if cmd.startswith("@") or "register" in cmd.lower():
            print(c.warning("@CollquanShell.register работает только в .py файлах."))
            print(c.colorize("  В терминале используйте: //name <код> endoff",
                             fg=c.fg_hex(self.theme.muted)))
            return

        if self._handle_system_command(cmd, args, raw):
            return

        print(c.error(f"Команда '{cmd}' не найдена. 'help' для справки."))

    def _save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write('"""Collquan: сохранённые команды."""\n\n')
            f.write("from charmpkk.terminals import CollquanShell\n")
            f.write("import shlex as _shlex\n\n")
            for name, info in self._custom_commands.items():
                code = info.get("code") or ""
                desc = info.get("desc", "")
                fname = _sanitize_ident(name)
                if desc.startswith("os shell"):
                    f.write(f"@CollquanShell.register({name!r}, {desc!r})\n")
                    f.write(f"def cmd_{fname}(args):\n")
                    f.write("    import subprocess\n")
                    for line in code.split("\n"):
                        if line.strip():
                            f.write(f"    subprocess.run({line.strip()!r}, shell=True)\n")
                    f.write("\n")
                elif desc.startswith("cmd block"):
                    cmd_lines = [l.strip() for l in code.split("\n") if l.strip()]
                    f.write(f"@CollquanShell.register({name!r}, {desc!r})\n")
                    f.write(f"def cmd_{fname}(args):\n")
                    f.write("    from charmpkk.terminals import CollquanShell as _CS\n")
                    f.write("    _sh = _CS()\n")
                    f.write(f"    for _line in {cmd_lines!r}:\n")
                    f.write("        _p = _shlex.split(_line)\n")
                    f.write("        _sh.execute(_p[0] if _p else '', _p[1:] if _p else [], raw=_line)\n")
                    f.write("\n")
                else:
                    f.write(f"@CollquanShell.register({name!r}, {desc!r})\n")
                    f.write(f"def cmd_{fname}(args):\n")
                    if code.strip():
                        for line in code.split("\n"):
                            f.write("    " + line + "\n")
                    else:
                        f.write("    pass\n")
                    f.write("\n")

    def _load_from_file(self, path):
        before = set(self._custom_commands.keys())
        ns = {
            "CollquanShell": CollquanShell,
            "__name__": "__load__",
            "__builtins__": __builtins__,
        }
        with open(path, "r", encoding="utf-8") as f:
            exec(f.read(), ns)
        after = set(self._custom_commands.keys())
        return len(after), len(after - before)


def _safe_run(func):
    try:
        func()
    except KeyboardInterrupt:
        print("\nВыход.")
    except Exception:
        print("\nПроизошла ошибка:")
        traceback.print_exc()
        try:
            input("\nНажмите Enter, чтобы выйти...")
        except (EOFError, KeyboardInterrupt):
            pass


def run_pretmod():
    _safe_run(lambda: PretmodShell().run())


def run_collquan():
    _safe_run(lambda: CollquanShell().run())