"""Мини-рендер Markdown → консоль с цветом."""
import re

from .colors import colorize, fg_hex, BOLD, DIM, ITALIC, UNDERLINE, STRIKE
from .boxes import rule

DEFAULT_ACCENT = "#7aa2ff"

_HEADER_RE = re.compile(r"^(#{1,6})\s+(.*)$")
_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_ITAL_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_CODE_RE = re.compile(r"`([^`]+)`")
_STRIKE_RE = re.compile(r"~~(.+?)~~")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _inline(text, accent):
    text = _LINK_RE.sub(lambda m: f"{m.group(1)} ({m.group(2)})", text)
    text = _BOLD_RE.sub(lambda m: colorize(m.group(1), style=BOLD), text)
    text = _ITAL_RE.sub(lambda m: colorize(m.group(1), style=ITALIC), text)
    text = _STRIKE_RE.sub(lambda m: colorize(m.group(1), style=STRIKE), text)
    text = _CODE_RE.sub(
        lambda m: colorize(f" {m.group(1)} ", fg=fg_hex("#f1fa8c"),
                           bg=fg_hex("#2b2b2b")), text)
    return text


def render(md: str, width=80, accent=DEFAULT_ACCENT) -> str:
    """Возвращает готовую строку для печати."""
    lines = md.split("\n")
    out = []
    in_code = False
    code_buf = []

    for line in lines:
        if line.strip().startswith("```"):
            if in_code:
                lang = line.strip()[3:].strip()
                header = f"─── {lang or 'code'} " + "─" * max(
                    0, width - 10 - len(lang or "code"))
                out.append(colorize(header, fg=fg_hex("#4b5563")))
                for cl in code_buf:
                    out.append(colorize(cl, fg=fg_hex("#e6e9f0")))
                out.append(colorize("─" * width, fg=fg_hex("#4b5563")))
                code_buf = []
                in_code = False
            else:
                in_code = True
            continue
        if in_code:
            code_buf.append("  " + line)
            continue

        m = _HEADER_RE.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2)
            if level == 1:
                out.append(colorize(title, fg=fg_hex(accent),
                                    style=BOLD))
                out.append(rule(width=width, fg=fg_hex("#4b5563")))
            else:
                prefix = "▌ " * level
                out.append(colorize(prefix + title, fg=fg_hex(accent),
                                    style=BOLD))
            continue

        if line.startswith("- ") or line.startswith("* "):
            out.append("  • " + _inline(line[2:], accent))
            continue

        m2 = re.match(r"^(\s*)(\d+)\.\s+(.*)$", line)
        if m2:
            out.append(f"{m2.group(1)}{m2.group(2)}. " +
                       _inline(m2.group(3), accent))
            continue

        if line.startswith("> "):
            out.append("  " + colorize("│ " + line[2:], style=DIM))
            continue

        if line.strip() in ("---", "***", "___"):
            out.append(rule(width=width, fg=fg_hex("#4b5563")))
            continue

        out.append(_inline(line, accent))

    return "\n".join(out)


def print_md(md: str, width=80, accent=DEFAULT_ACCENT):
    print(render(md, width=width, accent=accent))