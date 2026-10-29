"""Управление терминалом: размер, курсор, гиперссылки, clipboard, alt-screen."""
import os
import shutil
import sys
import time


class Terminal:
    """Низкоуровневые операции с терминалом (ANSI/OSC)."""

    def __init__(self, stream=None):
        self.stream = stream or sys.stdout

    def _is_tty(self):
        try:
            return self.stream.isatty()
        except Exception:
            return False

    # ---------- размеры ----------

    def size(self):
        s = shutil.get_terminal_size((80, 24))
        return s.columns, s.lines

    def width(self):
        return self.size()[0]

    def height(self):
        return self.size()[1]

    # ---------- экран ----------

    def clear(self):
        if not self._is_tty(): return
        self.stream.write("\033[2J\033[H")
        self.stream.flush()

    def clear_line(self):
        if not self._is_tty(): return
        self.stream.write("\033[2K\r")
        self.stream.flush()

    def home(self):
        if not self._is_tty(): return
        self.stream.write("\033[H")
        self.stream.flush()

    def alt_screen_enter(self):
        if not self._is_tty(): return
        self.stream.write("\033[?1049h")
        self.stream.flush()

    def alt_screen_exit(self):
        if not self._is_tty(): return
        self.stream.write("\033[?1049l")
        self.stream.flush()

    # ---------- курсор ----------

    def cursor_hide(self):
        if not self._is_tty(): return
        self.stream.write("\033[?25l")
        self.stream.flush()

    def cursor_show(self):
        if not self._is_tty(): return
        self.stream.write("\033[?25h")
        self.stream.flush()

    def cursor_move(self, x, y):
        """Абсолютное позиционирование (1-based)."""
        if not self._is_tty(): return
        self.stream.write(f"\033[{y};{x}H")
        self.stream.flush()

    def cursor_up(self, n=1):
        if not self._is_tty(): return
        self.stream.write(f"\033[{n}A")
        self.stream.flush()

    def cursor_down(self, n=1):
        if not self._is_tty(): return
        self.stream.write(f"\033[{n}B")
        self.stream.flush()

    def cursor_right(self, n=1):
        if not self._is_tty(): return
        self.stream.write(f"\033[{n}C")
        self.stream.flush()

    def cursor_left(self, n=1):
        if not self._is_tty(): return
        self.stream.write(f"\033[{n}D")
        self.stream.flush()

    def save_cursor(self):
        if not self._is_tty(): return
        self.stream.write("\033[s")
        self.stream.flush()

    def restore_cursor(self):
        if not self._is_tty(): return
        self.stream.write("\033[u")
        self.stream.flush()

    # ---------- заголовок окна ----------

    def set_title(self, title: str):
        if not self._is_tty(): return
        self.stream.write(f"\033]0;{title}\007")
        self.stream.flush()

    # ---------- звук ----------

    def bell(self, times=1, delay=0.12):
        if not self._is_tty(): return
        for _ in range(times):
            self.stream.write("\a")
            self.stream.flush()
            time.sleep(delay)

    def flash(self, times=2, delay=0.08):
        if not self._is_tty(): return
        for _ in range(times):
            self.stream.write("\033[?5h")
            self.stream.flush()
            time.sleep(delay)
            self.stream.write("\033[?5l")
            self.stream.flush()
            time.sleep(delay)

    # ---------- гиперссылки (OSC 8) ----------

    def hyperlink(self, text, url):
        if not self._is_tty(): return text
        return f"\033]8;;{url}\033\\{text}\033]8;;\033\\"

    # ---------- clipboard (OSC 52) ----------

    def copy(self, text: str):
        if not self._is_tty(): return
        import base64
        payload = base64.b64encode(text.encode("utf-8")).decode("ascii")
        self.stream.write(f"\033]52;c;{payload}\a")
        self.stream.flush()

    def paste_hint(self):
        return "Вставьте из буфера вручную (Ctrl+V / Cmd+V)"

    # ---------- цвета ----------

    def supports_truecolor(self):
        ct = os.environ.get("COLORTERM", "").lower()
        return ct in ("truecolor", "24bit")

    def supports_256(self):
        return "256" in os.environ.get("TERM", "")


_default = Terminal()


def terminal() -> Terminal:
    return _default