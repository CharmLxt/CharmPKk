"""Декоративные элементы консоли: градиентные рамки, подсветка, анимации."""
import re
import sys
import time

from .colors import (
    colorize, fg_hex, fg_rgb, RESET, multi_gradient, BOLD,
    _hex_to_rgb, _lerp,
)
from .boxes import STYLES, box
from .text import align, wrap, visible_len

def _apply_gradient(text, colors):
    if not colors or not text:
        return text
    rgb_colors = [_hex_to_rgb(c) for c in colors]
    n = max(len(text) - 1, 1)
    out = []
    for i, ch in enumerate(text):
        if ch == " ":
            out.append(ch)
            continue
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

def gradient_box(content, colors, style="round", padding=1, title=None, width=None, align_mode="left"):
    """Рамка, где каждая линия границы окрашена градиентом из списка цветов."""
    if isinstance(content, str):
        lines = content.split("\n")
    else:
        lines = [str(x) for x in content]
    if width:
        content_w = max(width - 2 - padding * 2, 1)
        new_lines = []
        for line in lines:
            new_lines.extend(wrap(line, content_w))
        lines = new_lines
    inner = max((visible_len(l) for l in lines), default=0)
    if title:
        inner = max(inner, visible_len(title) + 2)
    inner += padding * 2
    tl, h, tr, v, bl, br = STYLES.get(style, STYLES["round"])
    pad = " " * padding
    if title:
        t = f" {title} "
        top = tl + h + t + h * max(inner - visible_len(t) - 1, 0) + tr
    else:
        top = tl + h * inner + tr
    rows = [top]
    for line in lines:
        rows.append(v + pad + align(line, inner - padding * 2, align_mode) + pad + v)
    rows.append(bl + h * inner + br)
    return "\n".join(_apply_gradient(r, colors) for r in rows)

def highlight(text, query, fg="#000000", bg="#facc15"):
    if not query:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: colorize(m.group(0), fg=fg_hex(fg), bg=fg_hex(bg)), text)

def pill(text, fg=None, bg=None, style=None):
    inner = f" {text} "
    return colorize(f"({inner})", fg=fg, bg=bg, style=style)

def flash(text, times=3, on_fg="#ffffff", off_fg="#666666", duration=0.25, end="\n"):
    for i in range(times * 2):
        color = on_fg if i % 2 == 0 else off_fg
        sys.stdout.write(f"\r{colorize(text, fg=fg_hex(color))}")
        sys.stdout.flush()
        time.sleep(duration)
    sys.stdout.write(f"\r{colorize(text, fg=fg_hex(on_fg))}{end}")
    sys.stdout.flush()

def progress_dots(text="Loading", duration=2.0, interval=0.3, fg=None, end="\n"):
    frames = int(duration / interval)
    for i in range(frames):
        dots = "." * (i % 3 + 1)
        line = f"\r{text}{dots}   "
        sys.stdout.write(colorize(line, fg=fg) if fg else line)
        sys.stdout.flush()
        time.sleep(interval)
    sys.stdout.write(f"\r{colorize(text + '...', fg=fg) if fg else text + '...'}{end}")
    sys.stdout.flush()

def counter(target, duration=1.0, fps=30, prefix="", suffix="", fg=None, end="\n"):
    frames = max(int(duration * fps), 1)
    for i in range(frames + 1):
        val = int(target * i / frames)
        line = f"\r{prefix}{val}{suffix}"
        sys.stdout.write(colorize(line, fg=fg) if fg else line)
        sys.stdout.flush()
        time.sleep(1 / fps)
    sys.stdout.write(f"\r{colorize(prefix + str(target) + suffix, fg=fg) if fg else prefix + str(target) + suffix}{end}")
    sys.stdout.flush()

def countdown(seconds, label="Timer", on_finish=None, fg="#22c55e", warn_fg="#f59e0b", danger_fg="#ef4444", end="\n"):
    for remaining in range(seconds, -1, -1):
        mins, secs = divmod(remaining, 60)
        t_str = f"{mins:02d}:{secs:02d}"
        color = danger_fg if remaining <= 10 else (warn_fg if remaining <= 30 else fg)
        line = f"\r{colorize(label + ': ', fg=fg_hex(fg))}{colorize(t_str, fg=fg_hex(color))}"
        sys.stdout.write(line + "\033[K")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write(end)
    sys.stdout.flush()
    if on_finish:
        on_finish()

def gradient_bar(value, total=100, width=40, colors=("#ff0055", "#00ffcc"), empty_fg="#333333", label=""):
    """Прогресс-бар, заполненная часть которого окрашена в градиент."""
    ratio = max(0, min(value / (total or 1), 1))
    n = int(ratio * width)
    filled = "█" * n
    empty = "░" * (width - n)
    colored_filled = multi_gradient(filled, list(colors))
    colored_empty = colorize(empty, fg=fg_hex(empty_fg))
    pre = f"{label} " if label else ""
    return f"{pre}[{colored_filled}{colored_empty}] {ratio * 100:5.1f}%"

def typewriter_slow(text, delay=0.05, punct_delay=0.3, end="\n", stream=sys.stdout):
    """Печатает текст с паузой на знаках препинания."""
    for ch in text:
        stream.write(ch)
        stream.flush()
        if ch in ".!?":
            time.sleep(punct_delay)
        elif ch in ",;:":
            time.sleep(punct_delay / 2)
        else:
            time.sleep(delay)
    stream.write(end)
    stream.flush()

def rainbow_shimmer(text, duration=2.0, fps=30, stream=sys.stdout):
    """Радужный блик пробегает по тексту."""
    import math
    from .colors import fg_hex, lerp_color
    import colorsys
    
    n = len(text)
    frames = int(duration * fps)
    for f in range(frames):
        head = (f * (n + 10)) // frames - 5
        out = []
        for i, ch in enumerate(text):
            if head - 5 <= i <= head + 5:
                hue = (i / max(n, 1)) * 360
                r, g, b = colorsys.hsv_to_rgb(hue / 360.0, 0.8, 1.0)
                c = fg_hex(f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}")
                out.append(colorize(ch, fg=c, style=BOLD))
            else:
                out.append(colorize(ch, fg=fg_hex("#666666")))
        stream.write("\r" + "".join(out))
        stream.flush()
        time.sleep(1 / fps)
    stream.write("\r" + colorize(text, fg=fg_hex("#ffffff")) + "\n")
    stream.flush()