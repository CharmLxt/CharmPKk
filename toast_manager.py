"""Менеджер всплывающих уведомлений в углу окна."""
import tkinter as tk

from .effects import fade_in, fade_out, slide_in


class ToastManager:
    """Очередь тостов в правом нижнем или верхнем углу.

    tm = ToastManager(app, theme, position="bottom-right")
    tm.show("Привет!", variant="success")
    """

    POSITIONS = ("top-left", "top-right", "bottom-left", "bottom-right")

    def __init__(self, app, theme, position="bottom-right", width=280,
                 duration=3000, gap=10):
        self.app = app
        self.theme = theme
        self.position = position
        self.width = width
        self.duration = duration
        self.gap = gap
        self._toasts = []

    def show(self, message, variant="info", duration=None, title=None,
             icon=None, on_click=None):
        duration = duration or self.duration
        win = tk.Toplevel(self.app.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.configure(bg=self.theme.border)

        colors = {
            "info": self.theme.info, "success": self.theme.success,
            "warning": self.theme.warning, "danger": self.theme.danger,
            "error": self.theme.danger, "muted": self.theme.surface2,
        }
        accent = colors.get(variant, self.theme.accent)
        icons = {"info": "ℹ", "success": "✔", "warning": "⚠",
                 "danger": "✖", "error": "✖", "muted": "•"}
        icon = icon or icons.get(variant, "•")

        inner = tk.Frame(win, bg=self.theme.surface)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        left = tk.Frame(inner, bg=accent, width=4)
        left.pack(side="left", fill="y")

        body = tk.Frame(inner, bg=self.theme.surface)
        body.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        head = tk.Frame(body, bg=self.theme.surface)
        head.pack(fill="x")
        tk.Label(head, text=f"{icon} {title or variant.capitalize()}",
                 bg=self.theme.surface, fg=accent,
                 font=self.theme.tk_font(0, "bold")).pack(side="left")
        close = tk.Label(head, text="✕", bg=self.theme.surface,
                         fg=self.theme.muted, cursor="hand2",
                         font=self.theme.tk_font(-2))
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: self._dismiss(win))

        tk.Label(body, text=message, bg=self.theme.surface, fg=self.theme.fg,
                 font=self.theme.tk_font(), wraplength=self.width - 60,
                 justify="left").pack(anchor="w", pady=(4, 0))

        win.update_idletasks()
        w = self.width
        h = win.winfo_reqheight()
        win.geometry(f"{w}x{h}")

        self._toasts.append(win)
        self._reposition()

        if on_click:
            for child in (win, inner, body, head):
                child.bind("<Button-1>", lambda e: on_click())

        fade_in(win, duration=0.22)
        if duration:
            win.after(duration, lambda: self._dismiss(win))
        return win

    def _dismiss(self, win):
        if win not in self._toasts:
            return
        self._toasts.remove(win)
        try:
            fade_out(win, duration=0.2)
        except Exception:
            try:
                win.destroy()
            except Exception:
                pass
        self._reposition()

    def _reposition(self):
        self.app.root.update_idletasks()
        rx = self.app.root.winfo_rootx()
        ry = self.app.root.winfo_rooty()
        rw = self.app.root.winfo_width()
        rh = self.app.root.winfo_height()

        total_h = 0
        for i, win in enumerate(self._toasts):
            win.update_idletasks()
            h = win.winfo_height()
            if "bottom" in self.position:
                y = ry + rh - 20 - h - total_h
            else:
                y = ry + 20 + total_h
            if "right" in self.position:
                x = rx + rw - self.width - 20
            else:
                x = rx + 20
            try:
                win.geometry(f"{self.width}x{h}+{int(x)}+{int(y)}")
            except Exception:
                pass
            total_h += h + self.gap

    def clear(self):
        for win in list(self._toasts):
            try:
                win.destroy()
            except Exception:
                pass
        self._toasts.clear()