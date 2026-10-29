"""Формат .cllqn: скрипты для Collquan."""
import os
import sys
import time
import shlex
import platform
import traceback


def _is_admin():
    try:
        if platform.system() == "Windows":
            import ctypes
            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        return os.geteuid() == 0
    except Exception:
        return False


class CllqnScript:
    def __init__(self, text):
        self.metadata = {}
        self.commands = []
        self._parse(text)

    def _parse(self, text):
        in_header = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "---":
                in_header = not in_header
                continue
            if in_header:
                if ":" in stripped:
                    k, v = stripped.split(":", 1)
                    self.metadata[k.strip().lower()] = v.strip()
            else:
                if stripped and not stripped.startswith("#"):
                    self.commands.append(stripped)

    def validate(self):
        """Возвращает (bool, list[str]) — успешно ли и список ошибок/предупреждений."""
        errors = []
        if not self.commands:
            errors.append("Скрипт не содержит команд.")
        return len(errors) == 0, errors


class CllqnRunner:
    def __init__(self, shell, script):
        self.shell = shell
        self.script = script
        self.vars = {}

    def run(self):
        meta = self.script.metadata
        
        # Проверки перед запуском
        if meta.get("requires_admin", "").lower() == "true":
            if not _is_admin():
                from .console import error
                print(error("Этот скрипт требует прав администратора. Запустите терминал от имени администратора."))
                return

        if meta.get("requires_internet", "").lower() == "true":
            from .network import is_online
            from .console import error
            if not is_online():
                print(error("Этот скрипт требует подключения к интернету."))
                return

        from .console import info, success
        
        if meta.get("name"):
            info(f"Запуск скрипта: {meta['name']} (v{meta.get('version', '1.0')})")
            
        for i, cmd_line in enumerate(self.script.commands, 1):
            # Подстановка переменных
            for k, v in self.vars.items():
                cmd_line = cmd_line.replace(f"{{{k}}}", v)
                
            if cmd_line.startswith("sleep "):
                try:
                    sec = float(cmd_line.split()[1])
                    time.sleep(sec)
                except Exception:
                    print(f"  [x] Ошибка в директиве sleep: {cmd_line}")
                continue
                
            if cmd_line.startswith("ask "):
                parts = cmd_line.split(maxsplit=2)
                if len(parts) >= 3:
                    var_name = parts[1]
                    prompt = parts[2]
                    try:
                        self.vars[var_name] = input(f"? {prompt}: ")
                    except (EOFError, KeyboardInterrupt):
                        print("\nОтменено.")
                        return
                else:
                    print(f"  [x] Ошибка в директиве ask: {cmd_line}")
                continue
                
            if cmd_line.startswith("echo "):
                print(cmd_line[5:])
                continue

            # Обычная команда Collquan
            try:
                parts = shlex.split(cmd_line)
                if parts:
                    self.shell.execute(parts[0].lower(), parts[1:], raw=cmd_line)
            except Exception as e:
                print(f"  [x] Ошибка при выполнении '{cmd_line}': {e}")
                if meta.get("stop_on_error", "").lower() == "true":
                    print("Остановка скрипта из-за ошибки.")
                    return

        success("Скрипт завершён.")