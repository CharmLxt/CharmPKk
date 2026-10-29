"""Компоновка: колонки, строки, сетки, sidebar."""
from .text import align, visible_len


def _to_lines(x):
    if x is None:
        return [""]
    if isinstance(x, str):
        return x.split("\n")
    return [str(i) for i in x]


def columns(*blocks, gap=2, widths=None):
    """Разместить блоки рядом (горизонтально)."""
    parts = [_to_lines(b) for b in blocks]
    heights = [len(p) for p in parts]
    widths_calc = [max((visible_len(l) for l in p), default=0) for p in parts]
    if widths is None:
        widths = widths_calc
    else:
        widths = list(widths)
        for i in range(len(widths), len(widths_calc)):
            widths.append(widths_calc[i])

    rows_n = max(heights) if heights else 0
    out = []
    for r in range(rows_n):
        row_parts = []
        for i, p in enumerate(parts):
            line = p[r] if r < len(p) else ""
            row_parts.append(align(line, widths[i]))
        out.append((" " * gap).join(row_parts))
    return "\n".join(out)


def rows(*blocks):
    """Склеить блоки вертикально."""
    out = []
    for b in blocks:
        out.extend(_to_lines(b))
    return "\n".join(out)


def grid(blocks, cols=2, gap_h=2, gap_v=1, widths=None):
    """Сетка из блоков."""
    parts = [_to_lines(b) for b in blocks]
    if widths is None:
        widths = []
        for i in range(cols):
            col_blocks = parts[i::cols]
            widths.append(max(
                (max((visible_len(l) for l in p), default=0) for p in col_blocks),
                default=0,
            ))

    lines_out = []
    n = len(parts)
    for r0 in range(0, n, cols):
        row_blocks = parts[r0:r0 + cols]
        row_h = max((len(p) for p in row_blocks), default=0)
        for r in range(row_h):
            row_line = []
            for i, p in enumerate(row_blocks):
                line = p[r] if r < len(p) else ""
                row_line.append(align(line, widths[i]))
            lines_out.append((" " * gap_h).join(row_line))
        if r0 + cols < n:
            lines_out.extend([""] * gap_v)
    return "\n".join(lines_out)


def sidebar(content, side, side_width=24, gap=2, side_position="left"):
    """Боковая панель + контент."""
    c = _to_lines(content)
    s = [align(l, side_width) for l in _to_lines(side)]
    parts = [s, c] if side_position == "left" else [c, s]
    return columns(*parts, gap=gap)