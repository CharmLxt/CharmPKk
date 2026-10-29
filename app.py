"""Корневое окно приложения."""
import tkinter as tk

from .theme import ThemeManager
from . import widgets as W
from . import dialogs as D


class App:
    def __init__(self, title="CharmPkk App", size="1000x680",
                 theme=None, theme_name="dark", resizable=(True, True),
                 min_size=(480, 360)):
        self.manager = ThemeManager(theme_name)
        if theme is not None:
            self.manager._current = theme
        self.theme = self.manager.current

        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(size)
        self.root.minsize(*min_size)
        self.root.resizable(*resizable)
        self.root.configure(bg=self.theme.bg)

        self.header_frame = tk.Frame(self.root, bg=self.theme.bg)
        self.container = tk.Frame(self.root, bg=self.theme.bg)
        self.container.pack(fill="both", expand=True, padx=24, pady=(12, 12))
        self.statusbar = None

    # ---------- темы ----------

    def set_theme(self, name):
        self.theme = self.manager.set(name)
        self._restyle()

    def _restyle(self):
        self.root.configure(bg=self.theme.bg)
        self.container.configure(bg=self.theme.bg)
        self.header_frame.configure(bg=self.theme.bg)

    # ---------- шапка и футер ----------

    def header(self, title, subtitle=None, actions=None):
        """actions: список (label, callback) или функций, принимающих родителя."""
        self.header_frame.pack(fill="x", padx=24, pady=(20, 4))
        left = tk.Frame(self.header_frame, bg=self.theme.bg)
        left.pack(side="left", anchor="w")
        tk.Label(left, text=title, bg=self.theme.bg, fg=self.theme.fg,
                 font=self.theme.tk_font(8, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(left, text=subtitle, bg=self.theme.bg, fg=self.theme.muted,
                     font=self.theme.tk_font(1)).pack(anchor="w", pady=(2, 0))

        if actions:
            right = tk.Frame(self.header_frame, bg=self.theme.bg)
            right.pack(side="right", anchor="e")
            for action in actions:
                if callable(action):
                    action(right)
                else:
                    text, cmd = action
                    W.StyledButton(right, text, command=cmd, theme=self.theme,
                                   variant="secondary", size="sm"
                                   ).pack(side="left", padx=(8, 0))
        return self.header_frame

    def footer(self, text="", right_items=None):
        self.statusbar = tk.Frame(self.root, bg=self.theme.surface, height=28)
        self.statusbar.pack(fill="x", side="bottom")
        self.statusbar.pack_propagate(False)
        if text:
            tk.Label(self.statusbar, text=text, bg=self.theme.surface,
                     fg=self.theme.muted, font=self.theme.tk_font(-1),
                     padx=12).pack(side="left")
        if right_items:
            for text_r in right_items:
                tk.Label(self.statusbar, text=text_r, bg=self.theme.surface,
                         fg=self.theme.muted, font=self.theme.tk_font(-1),
                         padx=12).pack(side="right")
        return self.statusbar

    def sidebar(self, width=220, items=None):
        """items: list of (label, callback). Возвращает (frame, buttons)."""
        side = tk.Frame(self.root, bg=self.theme.surface, width=width)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        buttons = []
        for label, cb in (items or []):
            b = tk.Label(side, text=label, bg=self.theme.surface,
                         fg=self.theme.fg, font=self.theme.tk_font(0, "bold"),
                         padx=16, pady=12, anchor="w", cursor="hand2")
            b.pack(fill="x", pady=1)
            b.bind("<Enter>", lambda e, w=b: w.configure(bg=self.theme.surface2))
            b.bind("<Leave>", lambda e, w=b: w.configure(bg=self.theme.surface))
            b.bind("<Button-1>", lambda e, c=cb: (c() if c else None))
            buttons.append(b)
        return side, buttons

    # ---------- диалоги ----------

    def toast(self, message, variant="info", duration=2500):
        return D.Toast(self.root, message, self.theme, variant=variant,
                       duration=duration)

    def message(self, title, message, variant="info"):
        return D.MessageDialog(self.root, title, message, self.theme,
                               variant=variant)

    def confirm(self, title, message, on_confirm=None, on_cancel=None):
        return D.ConfirmDialog(self.root, title, message, self.theme,
                               on_confirm=on_confirm, on_cancel=on_cancel)

    def input(self, title, label=None, initial="", on_submit=None,
              password=False):
        return D.InputDialog(self.root, title, self.theme, label=label,
                             initial=initial, on_submit=on_submit,
                             password=password)

    # ---------- запуск ----------

    def run(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()