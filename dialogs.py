"""Модальные диалоги для окна."""
import tkinter as tk


class Modal(tk.Toplevel):
    def __init__(self, master, title, theme, size=None, modal=True):
        super().__init__(master)
        self.theme = theme
        self.title(title)
        self.configure(bg=theme.bg)
        if size:
            self.geometry(size)
        self.resizable(False, False)
        if modal:
            self.transient(master)
            self.grab_set()
            self.focus_set()

        self.update_idletasks()
        master.update_idletasks()
        w = self.winfo_width() or self.winfo_reqwidth()
        h = self.winfo_height() or self.winfo_reqheight()
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + (master.winfo_height() - h) // 2
        self.geometry(f"+{max(x, 0)}+{max(y, 0)}")


class MessageDialog(Modal):
    def __init__(self, master, title, message, theme, variant="info"):
        super().__init__(master, title, theme)
        colors = {
            "info": theme.info, "success": theme.success,
            "warning": theme.warning, "danger": theme.danger,
            "error": theme.danger,
        }
        accent = colors.get(variant, theme.accent)

        wrap = tk.Frame(self, bg=theme.bg, padx=24, pady=20)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text=title, bg=theme.bg, fg=accent,
                 font=theme.tk_font(2, "bold")).pack(anchor="w", pady=(0, 8))
        tk.Label(wrap, text=message, bg=theme.bg, fg=theme.fg,
                 font=theme.tk_font(), justify="left", wraplength=360
                 ).pack(anchor="w", pady=(0, 16))

        from .widgets import StyledButton
        StyledButton(wrap, "OK", command=self.destroy, theme=theme,
                     variant="primary").pack(anchor="e")


class ConfirmDialog(Modal):
    def __init__(self, master, title, message, theme, on_confirm=None,
                 on_cancel=None, confirm_text="OK", cancel_text="Отмена"):
        super().__init__(master, title, theme)
        self._result = False
        self._on_confirm = on_confirm
        self._on_cancel = on_cancel

        wrap = tk.Frame(self, bg=theme.bg, padx=24, pady=20)
        wrap.pack(fill="both", expand=True)

        tk.Label(wrap, text=title, bg=theme.bg, fg=theme.fg,
                 font=theme.tk_font(2, "bold")).pack(anchor="w", pady=(0, 8))
        tk.Label(wrap, text=message, bg=theme.bg, fg=theme.muted,
                 font=theme.tk_font(), justify="left", wraplength=360
                 ).pack(anchor="w", pady=(0, 16))

        from .widgets import StyledButton
        btns = tk.Frame(wrap, bg=theme.bg)
        btns.pack(anchor="e")
        StyledButton(btns, cancel_text, command=self._cancel, theme=theme,
                     variant="secondary").pack(side="left", padx=(0, 8))
        StyledButton(btns, confirm_text, command=self._confirm, theme=theme,
                     variant="primary").pack(side="left")

    def _confirm(self):
        self._result = True
        if self._on_confirm:
            self._on_confirm()
        self.destroy()

    def _cancel(self):
        if self._on_cancel:
            self._on_cancel()
        self.destroy()


class InputDialog(Modal):
    def __init__(self, master, title, theme, label=None, initial="",
                 on_submit=None, password=False):
        super().__init__(master, title, theme)
        self._on_submit = on_submit

        wrap = tk.Frame(self, bg=theme.bg, padx=24, pady=20)
        wrap.pack(fill="both", expand=True)
        tk.Label(wrap, text=title, bg=theme.bg, fg=theme.fg,
                 font=theme.tk_font(2, "bold")).pack(anchor="w", pady=(0, 12))

        from .widgets import StyledEntry, StyledButton
        self.entry = StyledEntry(wrap, theme, label=label,
                                 show="•" if password else None)
        self.entry.pack(fill="x", pady=(0, 16))
        self.entry.set(initial)

        btns = tk.Frame(wrap, bg=theme.bg)
        btns.pack(anchor="e")
        StyledButton(btns, "Отмена", command=self.destroy, theme=theme,
                     variant="secondary").pack(side="left", padx=(0, 8))
        StyledButton(btns, "OK", command=self._submit, theme=theme,
                     variant="primary").pack(side="left")

        self.entry.entry.focus_set()
        self.entry.entry.bind("<Return>", lambda e: self._submit())

    def _submit(self):
        if self._on_submit:
            self._on_submit(self.entry.get())
        self.destroy()