"""Реестр горячих клавиш."""
import tkinter as tk


class Shortcuts:
    """Регистрирует биндинги клавиш и хранит их описания (для справки/палитры).

    sc = Shortcuts(app.root)
    sc.add("<Control-s>", save, "Сохранить")
    sc.add("<F1>", help_, "Справка")
    sc.help_window()   # окно со списком
    """

    def __init__(self, root):
        self.root = root
        self._binds = []

    def add(self, sequence, callback, description=""):
        try:
            self.root.bind_all(sequence, lambda e: (callback(), None))
        except Exception:
            pass
        self._binds.append((sequence, description, callback))
        return self

    def remove(self, sequence):
        try:
            self.root.unbind_all(sequence)
        except Exception:
            pass
        self._binds = [b for b in self._binds if b[0] != sequence]

    def list(self):
        return [(s, d) for s, d, _ in self._binds]

    def help_window(self, theme=None):
        """Окно-подсказка со списком горячих клавиш."""
        top = tk.Toplevel(self.root)
        top.title("Горячие клавиши")
        bg = theme.bg if theme else "#1b1e28"
        fg = theme.fg if theme else "#e6e9f0"
        muted = theme.muted if theme else "#8b93a7"
        accent = theme.accent if theme else "#7aa2ff"
        font = theme.tk_font() if theme else ("Segoe UI", 11)

        top.configure(bg=bg)
        tk.Label(top, text="Горячие клавиши", bg=bg, fg=accent,
                 font=(font[0], font[1] + 4, "bold"),
                 padx=20, pady=12).pack(anchor="w")

        body = tk.Frame(top, bg=bg)
        body.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        for seq, desc, _ in self._binds:
            row = tk.Frame(body, bg=bg)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=seq, bg=bg, fg=accent, font=font,
                     width=18, anchor="w").pack(side="left")
            tk.Label(row, text=desc, bg=bg, fg=fg, font=font,
                     anchor="w").pack(side="left")

        top.bind("<Escape>", lambda e: top.destroy())
        return top