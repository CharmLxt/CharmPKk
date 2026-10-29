"""Простые ASCII-графики."""
from .colors import colorize


def sparkline(values, chars="▁▂▃▄▅▆▇█", fg=None):
    if not values:
        return ""
    lo, hi = min(values), max(values)
    rng = (hi - lo) or 1
    out = []
    for v in values:
        i = int((v - lo) / rng * (len(chars) - 1))
        ch = chars[i]
        out.append(colorize(ch, fg=fg) if fg else ch)
    return "".join(out)


def bar_chart(data, width=40, char="█", fg=None, show_values=True,
              value_fmt="{:.0f}"):
    items = list(data.items()) if isinstance(data, dict) else list(data)
    if not items:
        return ""
    maxv = max(v for _, v in items) or 1
    max_label = max(len(str(k)) for k, _ in items)
    lines = []
    for label, value in items:
        n = int(value / maxv * width)
        bar = char * n
        if fg:
            bar = colorize(bar, fg=fg)
        lbl = str(label).ljust(max_label)
        suffix = f" {value_fmt.format(value)}" if show_values else ""
        lines.append(f"{lbl} │ {bar}{suffix}")
    return "\n".join(lines)


def gauge(value, total=100, width=30, fg=None, bg=None, label=""):
    ratio = max(0, min(value / (total or 1), 1))
    n = int(ratio * width)
    filled = "█" * n
    empty = "░" * (width - n)
    if fg:
        filled = colorize(filled, fg=fg)
    if bg:
        empty = colorize(empty, fg=bg)
    pre = f"{label} " if label else ""
    return f"{pre}[{filled}{empty}] {ratio * 100:5.1f}%"


def histogram(values, bins=10, width=40, char="█", fg=None,
              show_labels=True):
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi == lo:
        hi = lo + 1
    step = (hi - lo) / bins
    counts = [0] * bins
    for v in values:
        i = min(int((v - lo) / step), bins - 1)
        counts[i] += 1
    maxc = max(counts) or 1
    lines = []
    for i, c in enumerate(counts):
        n = int(c / maxc * width)
        bar = char * n
        if fg:
            bar = colorize(bar, fg=fg)
        if show_labels:
            lbl = f"{lo + i * step:>7.2f}"
            lines.append(f"{lbl} │ {bar} {c}")
        else:
            lines.append(bar)
    return "\n".join(lines)


def heatmap(values, rows, cols, char_ramp=" ░▒▓█", fg=None):
    """Простая heatmap из 2D-списка (по строкам)."""
    if not values:
        return ""
    flat = [v for row in values for v in row]
    lo, hi = min(flat), max(flat)
    rng = (hi - lo) or 1
    n = len(char_ramp) - 1
    out = []
    for r in range(rows):
        row = values[r] if r < len(values) else []
        line = []
        for c in range(cols):
            v = row[c] if c < len(row) else lo
            i = int((v - lo) / rng * n)
            ch = char_ramp[i]
            line.append(colorize(ch, fg=fg) if fg else ch)
        out.append("".join(line))
    return "\n".join(out)