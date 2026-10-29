"""Управление координатами и полями ввода в консоли."""
import sys
from .colors import colorize
from .terminal import terminal
from .menu import _get_key

class InputField:
    def __init__(self, x, y, prompt="", fg=None, bg=None):
        self.x = x
        self.y = y
        self.prompt = prompt
        self.fg = fg
        self.bg = bg
        self.text = ""

    def _render(self, term):
        if not term._is_tty(): return
        term.cursor_move(self.x, self.y)
        sys.stdout.write("\033[K")
        prompt_str = colorize(self.prompt, fg=self.fg, bg=self.bg) if self.fg else self.prompt
        text_str = colorize(self.text, fg=self.fg, bg=self.bg) if self.fg else self.text
        sys.stdout.write(prompt_str + text_str)
        sys.stdout.flush()

    def read(self, term):
        if not term._is_tty():
            try:
                self.text = input(self.prompt)
                return self.text
            except (EOFError, KeyboardInterrupt):
                return None

        self._render(term)
        while True:
            key = _get_key()
            if key in ("enter", "\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                return self.text
            elif key in ("esc",) and not self.text:
                sys.stdout.write("\n")
                sys.stdout.flush()
                return None
            elif key in ("backspace", "\x7f", "\x08"):
                if self.text:
                    self.text = self.text[:-1]
                    self._render(term)
            elif len(key) == 1 and key.isprintable():
                self.text += key
                self._render(term)

class Screen:
    def __init__(self, term=None):
        self.term = term or terminal()

    def clear(self):
        self.term.clear()

    def put(self, x, y, text, fg=None, bg=None):
        if not self.term._is_tty():
            print(text)
            return
        self.term.cursor_move(x, y)
        if fg or bg:
            text = colorize(text, fg=fg, bg=bg)
        sys.stdout.write(text)
        sys.stdout.flush()

    def input(self, x, y, prompt="", fg=None, bg=None):
        field = InputField(x, y, prompt, fg, bg)
        return field.read(self.term)

    def box(self, x, y, width, height, style="round", fg=None):
        if not self.term._is_tty(): return
        from .boxes import STYLES
        tl, h, tr, v, bl, br = STYLES.get(style, STYLES["round"])
        
        top = tl + h * (width - 2) + tr
        self.put(x, y, top, fg=fg)
        
        for i in range(1, height - 1):
            self.put(x, y + i, v + " " * (width - 2) + v, fg=fg)
            
        bot = bl + h * (width - 2) + br
        self.put(x, y + height - 1, bot, fg=fg)