"""Пошаговые формы с валидацией (поверх ask/confirm)."""
from .colors import colorize, fg_hex, BOLD, DIM
from .boxes import box


class Field:
    def __init__(self, name, prompt, kind="str", default=None,
                 required=False, validate=None, hide=False, hint=None,
                 choices=None, integer=False, min_value=None, max_value=None):
        self.name = name
        self.prompt = prompt
        self.kind = kind
        self.default = default
        self.required = required
        self.validate = validate
        self.hide = hide
        self.hint = hint
        self.choices = choices
        self.integer = integer or kind == "int"
        self.min_value = min_value
        self.max_value = max_value

    def ask(self, accent="#7aa2ff"):
        from .widgets import ask, ask_password, ask_number, ask_choice

        if self.hint:
            print(colorize(f"  {self.hint}", style=DIM))

        while True:
            if self.choices:
                v = ask_choice(self.prompt, self.choices,
                               default=self.default, fg=fg_hex(accent))
            elif self.kind == "password" or self.hide:
                v = ask_password(self.prompt, fg=fg_hex(accent))
                if not v:
                    v = self.default
            elif self.kind in ("int", "float") or self.integer:
                v = ask_number(self.prompt, default=self.default,
                               fg=fg_hex(accent),
                               integer=(self.kind == "int" or self.integer))
            elif self.kind == "bool":
                from .widgets import confirm
                return confirm(self.prompt, default=bool(self.default),
                               fg=fg_hex(accent))
            else:
                v = ask(self.prompt, default=self.default, fg=fg_hex(accent))

            err = self._check(v)
            if err:
                print(colorize(f"  ✖ {err}", fg=fg_hex("#ef4444")))
                continue
            return v

    def _check(self, v):
        if v is None or (isinstance(v, str) and not v.strip()):
            if self.required:
                return "Обязательное поле"
            return None
        if self.min_value is not None and v < self.min_value:
            return f"Минимум {self.min_value}"
        if self.max_value is not None and v > self.max_value:
            return f"Максимум {self.max_value}"
        if self.validate:
            try:
                res = self.validate(v)
            except Exception as e:
                return str(e)
            if res is not True and res is not None:
                return res if isinstance(res, str) else "Некорректное значение"
        return None


class Form:
    """Набор полей; последовательный ввод с прогрессом."""

    def __init__(self, title, fields, accent="#7aa2ff"):
        self.title = title
        self.fields = list(fields)
        self.accent = accent

    def run(self):
        n = len(self.fields)
        print()
        print(colorize(f"◆ {self.title}", fg=fg_hex(self.accent), style=BOLD))
        print()
        result = {}
        for i, f in enumerate(self.fields, 1):
            print(colorize(f"[{i}/{n}] {f.prompt}", style=DIM))
            result[f.name] = f.ask(self.accent)
            print()
        return result

    def summary(self, data):
        lines = [f"{k:<16}: {v}" for k, v in data.items()]
        return box(lines, title="Итог", style="round",
                   border_fg=fg_hex(self.accent))