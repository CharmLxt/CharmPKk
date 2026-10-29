"""Цвета и стили ANSI: truecolor, 256, hex, градиенты, радуга."""
import os
import re
import sys

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
REVERSE = "\033[7m"
HIDDEN = "\033[8m"
STRIKE = "\033[9m"

BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
BRIGHT_BLACK = "\033[90m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN = "\033[96m"
BRIGHT_WHITE = "\033[97m"

_ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _detect() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


_ENABLED = _detect()


def enable() -> None:
    global _ENABLED
    _ENABLED = True


def disable() -> None:
    global _ENABLED
    _ENABLED = False


def is_enabled() -> bool:
    return _ENABLED


def fg_rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def bg_rgb(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def fg_hex(h: str) -> str:
    return fg_rgb(*_hex_to_rgb(h))


def bg_hex(h: str) -> str:
    return bg_rgb(*_hex_to_rgb(h))


def fg_256(n: int) -> str:
    return f"\033[38;5;{n}m"


def bg_256(n: int) -> str:
    return f"\033[48;5;{n}m"


def colorize(text: str, fg=None, bg=None, style=None) -> str:
    if not _ENABLED:
        return text
    prefix = ""
    if style:
        prefix += style
    if fg:
        prefix += fg
    if bg:
        prefix += bg
    if not prefix:
        return text
    return f"{prefix}{text}{RESET}"


def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient_text(text: str, start: str, end: str) -> str:
    """Плавный градиент по символам (от одного цвета к другому)."""
    return multi_gradient(text, [start, end])


def multi_gradient(text: str, colors: list) -> str:
    """Плавный градиент по символам из списка цветов."""
    if not _ENABLED or not text or not colors:
        return text
    if len(colors) == 1:
        return colorize(text, fg=colors[0])
        
    rgb_colors = [_hex_to_rgb(c) for c in colors]
    n = max(len(text) - 1, 1)
    out = []
    for i, ch in enumerate(text):
        if ch == " ":
            out.append(ch)
            continue
        
        # Вычисляем, между какими цветами находимся
        pos = (i / n) * (len(rgb_colors) - 1)
        idx = int(pos)
        t = pos - idx
        if idx >= len(rgb_colors) - 1:
            c = rgb_colors[-1]
        else:
            c = _lerp(rgb_colors[idx], rgb_colors[idx + 1], t)
            
        out.append(f"{fg_rgb(*c)}{ch}")
    out.append(RESET)
    return "".join(out)


def rainbow_text(text: str, phase: int = 0) -> str:
    """Радужный текст (HSV-спектр)."""
    if not _ENABLED or not text:
        return text
    import colorsys
    out = []
    n = max(len(text), 1)
    for i, ch in enumerate(text):
        if ch == " ":
            out.append(ch)
            continue
        h = ((i + phase) % n) / n
        r, g, b = colorsys.hsv_to_rgb(h, 0.85, 1.0)
        out.append(f"{fg_rgb(int(r * 255), int(g * 255), int(b * 255))}{ch}")
    out.append(RESET)
    return "".join(out)


class Style:
    """Контекстный менеджер цвета/стиля для печати.

    with Style(fg=fg_hex("#7aa2ff"), style=BOLD):
        print("hello")
    """

    def __init__(self, fg=None, bg=None, style=None):
        self.fg, self.bg, self.style = fg, bg, style

    def __enter__(self):
        if _ENABLED:
            prefix = ""
            if self.style:
                prefix += self.style
            if self.fg:
                prefix += self.fg
            if self.bg:
                prefix += self.bg
            sys.stdout.write(prefix)
        return self

    def __exit__(self, *exc):
        if _ENABLED:
            sys.stdout.write(RESET)