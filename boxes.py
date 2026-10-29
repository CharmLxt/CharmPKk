"""Рамки, панели, секции, баннеры."""
from .colors import colorize
from .text import align, wrap, visible_len

STYLES = {
    "single": ("┌", "─", "┐", "│", "└", "┘"),
    "double": ("╔", "═", "╗", "║", "╚", "╝"),
    "round":  ("╭", "─", "╮", "│", "╰", "╯"),
    "heavy":  ("┏", "━", "┓", "┃", "┗", "┛"),
    "dashed": ("┌", "╌", "┐", "╎", "└", "┘"),
    "dotted": ("┌", "┄", "┐", "┆", "└", "┘"),
    "ascii":  ("+", "-", "+", "|", "+", "+"),
    "none":   ("", "", "", "", "", ""),
    "shadow": ("┌", "─", "┐", "│", "└", "┘"),
}


def box(content, title=None, style="round", padding=1, width=None,
        border_fg=None, bg=None, align_mode="left",
        title_align="left", subtitle=None) -> str:
    """Рамка вокруг текста. content — строка или список строк."""
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
    if subtitle:
        inner = max(inner, visible_len(subtitle) + 2)
    inner += padding * 2

    tl, h, tr, v, bl, br = STYLES.get(style, STYLES["round"])
    pad = " " * padding

    if style == "none":
        return "\n".join(pad + align(l, inner - padding * 2, align_mode) + pad
                         for l in lines)

    if title:
        t = f" {title} "
        if title_align == "center":
            side = max((inner - visible_len(t)) // 2, 0)
            top = tl + h * side + t + h * max(inner - side - visible_len(t), 0) + tr
        elif title_align == "right":
            top = tl + h * max(inner - visible_len(t), 0) + t + tr
        else:
            top = tl + h + t + h * max(inner - visible_len(t) - 1, 0) + tr
    else:
        top = tl + h * inner + tr

    out = [top]
    for line in lines:
        content_aligned = align(line, inner - padding * 2, align_mode)
        out.append(v + pad + content_aligned + pad + v)

    if subtitle:
        s = f" {subtitle} "
        bot = bl + h * max(inner - visible_len(s), 0) + s + br
    else:
        bot = bl + h * inner + br
    out.append(bot)

    if border_fg:
        out = [colorize(x, fg=border_fg, bg=bg) for x in out]
    elif bg:
        out = [colorize(x, bg=bg) for x in out]
    return "\n".join(out)


def rule(width=60, char="─", fg=None, title=None, title_align="center",
         bg=None) -> str:
    """Горизонтальный разделитель."""
    if title:
        t = f" {title} "
        tw = visible_len(t)
        if title_align == "left":
            line = char * 2 + t + char * max(width - tw - 2, 0)
        elif title_align == "right":
            line = char * max(width - tw - 2, 0) + t + char * 2
        else:
            side = max((width - tw) // 2, 0)
            line = char * side + t + char * max(width - side - tw, 0)
    else:
        line = char * width
    return colorize(line, fg=fg, bg=bg)


def section(title, width=60, style="round", fg=None, bg=None) -> str:
    """Заголовок секции."""
    return rule(width=width, title=title, fg=fg, bg=bg, title_align="left")


def panel(title, content, style="round", border_fg=None, bg=None,
          width=None, padding=1) -> str:
    """Панель с заголовком."""
    return box(content, title=title, style=style, border_fg=border_fg,
               bg=bg, width=width, padding=padding)


def banner(text, subtitle=None, style="double", fg=None, bg=None,
           width=None) -> str:
    """Крупный центрированный заголовок."""
    lines = [text]
    if subtitle:
        lines.append(subtitle)
    return box(lines, style=style, border_fg=fg, bg=bg, padding=2,
               width=width, align_mode="center")