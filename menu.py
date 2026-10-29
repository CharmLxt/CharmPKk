"""Интерактивные меню: single-select, multi-select, tabs."""
import os
import sys

from .colors import colorize, BOLD, DIM


def _get_key() -> str:
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getch()
        if ch == b"\x03":
            raise KeyboardInterrupt
        if ch in (b"\x00", b"\xe0"):
            ch2 = msvcrt.getch().decode("latin1", "ignore")
            return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(ch2, "")
        if ch in (b"\r", b"\n"):
            return "enter"
        if ch == b"\x1b":
            return "esc"
        if ch == b" ":
            return "space"
        try:
            return ch.decode("utf-8")
        except Exception:
            return ""

    import termios
    import tty
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                return {"A": "up", "B": "down", "C": "right", "D": "left"}.get(ch3, "")
            return "esc"
        if ch in ("\r", "\n"):
            return "enter"
        if ch == " ":
            return "space"
        if ch == "\x03":
            raise KeyboardInterrupt
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def _safe_print(text):
    """Печатает текст, не падая при ошибках кодировки (например, при перенаправлении в файл на Windows)."""
    try:
        print(text)
    except UnicodeEncodeError:
        enc = sys.stdout.encoding or 'utf-8'
        try:
            print(text.encode(enc, errors='replace').decode(enc))
        except Exception:
            print(text.encode('ascii', errors='replace').decode('ascii'))


def _fallback_select(title, options, return_index=False, hint=""):
    _safe_print(title)
    if hint: _safe_print(hint)
    for i, opt in enumerate(options, 1):
        _safe_print(f"  {i}. {opt}")
    try:
        raw = input("> ").strip()
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            return idx if return_index else options[idx]
    except (ValueError, EOFError, KeyboardInterrupt):
        pass
    return None


def _fallback_multiselect(title, options, return_indices=False, hint=""):
    _safe_print(title)
    if hint: _safe_print(hint)
    for i, opt in enumerate(options, 1):
        _safe_print(f"  {i}. {opt}")
    try:
        raw = input("Номера через запятую: ").strip()
        idxs = [int(x) - 1 for x in raw.split(",") if x.strip().isdigit()]
        idxs = [i for i in idxs if 0 <= i < len(options)]
        return idxs if return_indices else [options[i] for i in idxs]
    except (ValueError, EOFError, KeyboardInterrupt):
        pass
    return [] if return_indices else None


def select(title, options, fg_cursor=None, fg_title=None, cursor="❯",
           return_index=False, subtitle=None,
           hint="↑/↓ — выбор, Enter — ОК"):
    if not options:
        return None
        
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return _fallback_select(title, options, return_index, hint)

    idx = 0
    n = len(options)

    def total_lines():
        return n + (1 if title else 0) + (1 if subtitle else 0) + (1 if hint else 0)

    def draw(first=False):
        if not first:
            sys.stdout.write(f"\033[{total_lines()}A")
        if title:
            t = (colorize(title, fg=fg_title, style=BOLD) if fg_title
                 else colorize(title, style=BOLD))
            sys.stdout.write(t + "\033[K\n")
        for i, opt in enumerate(options):
            prefix = f"{cursor} " if i == idx else "  "
            line = prefix + str(opt)
            if i == idx and fg_cursor:
                line = colorize(line, fg=fg_cursor, style=BOLD)
            elif i == idx:
                line = colorize(line, style=BOLD)
            sys.stdout.write(line + "\033[K\n")
        if subtitle:
            sys.stdout.write(colorize(subtitle, style=DIM) + "\033[K\n")
        if hint:
            sys.stdout.write(colorize(hint, style=DIM) + "\033[K\n")
        sys.stdout.flush()

    if title or hint:
        sys.stdout.write("\n")
    draw(first=True)

    try:
        while True:
            key = _get_key()
            if key == "up":
                idx = (idx - 1) % n
                draw()
            elif key == "down":
                idx = (idx + 1) % n
                draw()
            elif key == "enter":
                return idx if return_index else options[idx]
            elif key in ("esc", "q"):
                return None
            elif key.isdigit() and key != "0":
                j = int(key) - 1
                if 0 <= j < n:
                    idx = j
                    draw()
    except KeyboardInterrupt:
        return None


def multiselect(title, options, fg_cursor=None, fg_title=None, cursor="❯",
                selected_mark="◉", unselected_mark="◯", return_indices=False,
                preselect=None,
                hint="↑/↓ — навигация, Space — выбрать, Enter — ОК"):
    if not options:
        return []
        
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return _fallback_multiselect(title, options, return_indices, hint)

    selected = set(preselect or [])
    idx = 0
    n = len(options)

    def total_lines():
        return n + (1 if title else 0) + (1 if hint else 0)

    def draw(first=False):
        if not first:
            sys.stdout.write(f"\033[{total_lines()}A")
        if title:
            t = (colorize(title, fg=fg_title, style=BOLD) if fg_title
                 else colorize(title, style=BOLD))
            sys.stdout.write(t + "\033[K\n")
        for i, opt in enumerate(options):
            marker = selected_mark if i in selected else unselected_mark
            arrow = f"{cursor} " if i == idx else "  "
            line = f"{arrow}{marker} {opt}"
            if i == idx and fg_cursor:
                line = colorize(line, fg=fg_cursor, style=BOLD)
            elif i == idx:
                line = colorize(line, style=BOLD)
            sys.stdout.write(line + "\033[K\n")
        if hint:
            sys.stdout.write(colorize(hint, style=DIM) + "\033[K\n")
        sys.stdout.flush()

    if title or hint:
        sys.stdout.write("\n")
    draw(first=True)

    try:
        while True:
            key = _get_key()
            if key == "up":
                idx = (idx - 1) % n
                draw()
            elif key == "down":
                idx = (idx + 1) % n
                draw()
            elif key == "space":
                if idx in selected:
                    selected.discard(idx)
                else:
                    selected.add(idx)
                draw()
            elif key == "enter":
                picked = sorted(selected)
                return picked if return_indices else [options[i] for i in picked]
            elif key in ("esc", "q"):
                return None
    except KeyboardInterrupt:
        return None


def tabs(title, tab_names, render_tab, fg_cursor=None, fg_title=None,
         hint="←/→ — вкладки, q — выход"):
    if not tab_names:
        return
        
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return

    idx = 0
    n = len(tab_names)

    def header():
        parts = []
        for i, name in enumerate(tab_names):
            if i == idx:
                s = f"[ {name} ]"
                s = colorize(s, fg=fg_cursor, style=BOLD) if fg_cursor else colorize(s, style=BOLD)
            else:
                s = colorize(f"  {name}  ", style=DIM)
            parts.append(s)
        return " ".join(parts)

    def body_lines():
        body = render_tab(idx)
        return body.split("\n") if isinstance(body, str) else list(body)

    def redraw(first=False):
        if not first:
            sys.stdout.write(f"\033[{len(body_lines()) + 1}A")
        if title:
            sys.stdout.write(colorize(title, style=BOLD) + "\n")
        sys.stdout.write(header() + "\033[K\n")
        for l in body_lines():
            sys.stdout.write(l + "\033[K\n")
        sys.stdout.flush()

    sys.stdout.write("\n")
    redraw(first=True)
    try:
        while True:
            k = _get_key()
            if k == "left":
                idx = (idx - 1) % n
                redraw()
            elif k == "right":
                idx = (idx + 1) % n
                redraw()
            elif k in ("q", "esc"):
                return
    except KeyboardInterrupt:
        return