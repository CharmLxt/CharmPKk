"""Текстовые утилиты: выравнивание, перенос, обрезка, эффекты."""
import sys
import time

from .colors import strip_ansi


def visible_len(text: str) -> int:
    return len(strip_ansi(text))


def wrap(text: str, width: int) -> list:
    """Перенос по словам."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if not cur:
            cur = w
        elif visible_len(cur) + 1 + len(w) <= width:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def align(text: str, width: int, mode: str = "left") -> str:
    """left | right | center — с учётом видимой длины (ANSI игнорируется)."""
    v = visible_len(text)
    if v >= width:
        return text
    if mode == "right":
        return " " * (width - v) + text
    if mode == "center":
        left = (width - v) // 2
        right = width - v - left
        return " " * left + text + " " * right
    return text + " " * (width - v)


def center(text: str, width: int) -> str:
    return align(text, width, "center")


def pad(text: str, left: int = 0, right: int = 0) -> str:
    return " " * left + text + " " * right


def truncate(text: str, width: int, ellipsis: str = "…") -> str:
    """Обрезка с сохранением видимой длины (приблизительно для ANSI)."""
    plain = strip_ansi(text)
    if len(plain) <= width:
        return text
    if width <= len(ellipsis):
        return plain[:width]
    return plain[: width - len(ellipsis)] + ellipsis


def typewriter(text: str, delay: float = 0.02, end: str = "\n") -> None:
    """Печать текста по символам."""
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()


def indent(text: str, prefix: str = "  ") -> str:
    return "\n".join(prefix + line for line in text.split("\n"))