"""Многошаговый мастер (wizard)."""
from .colors import colorize, fg_hex, BOLD, DIM
from .boxes import box, rule
from .widgets import confirm


class Step:
    def __init__(self, name, title, render=None, ask=None, on_enter=None,
                 skippable=False):
        """render(ctx) -> строка; ask(ctx) -> значение."""
        self.name = name
        self.title = title
        self.render = render
        self.ask = ask
        self.on_enter = on_enter
        self.skippable = skippable


class Wizard:
    def __init__(self, title, steps, accent="#7aa2ff", allow_back=True):
        self.title = title
        self.steps = list(steps)
        self.accent = accent
        self.allow_back = allow_back

    def run(self, initial=None):
        ctx = dict(initial or {})
        i = 0
        while 0 <= i < len(self.steps):
            step = self.steps[i]
            print()
            head = f"{self.title} — шаг {i + 1}/{len(self.steps)}"
            print(colorize(head, fg=fg_hex(self.accent), style=BOLD))
            print(rule(width=min(len(head) + 6, 72), fg=fg_hex("#4b5563")))
            if step.on_enter:
                step.on_enter(ctx)
            if step.render:
                out = step.render(ctx)
                if out:
                    print(out if isinstance(out, str) else "\n".join(out))
            if step.ask:
                value = step.ask(ctx)
                if value is None and self.allow_back:
                    i -= 1
                    continue
                ctx[step.name] = value
            elif step.skippable and self.allow_back:
                if confirm("Вернуться назад?", default=False,
                           fg=fg_hex(self.accent)):
                    i -= 1
                    continue
            i += 1
        return ctx