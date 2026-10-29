"""Command palette в стиле Ctrl+K."""
import tkinter as tk

from .effects import fade_in, fade_out, slide_in


class CommandPalette:
    """Модальное окно с поиском команд.

    palette = CommandPalette(app, app.theme, commands)
    palette.open()   # по Ctrl+K
    """

    def __init__(self, app, theme, commands, placeholder="Введите команду…"):
        self.app = app
        self.theme = theme
        self.commands = list(commands)  # [(title, callback, keywords?) ...]
        self.placeholder = placeholder
        self._win = None

    def bind(self, root=None):
        root = root or self.app.root
        root.bind_all("<Control-k>", lambda e: self.open())
        root.bind_all("<Control-K>", lambda e: self.open())

    def open(self):
        if self._win and self._win.winfo_exists():
            self._win.destroy()
        self._win = tk.Toplevel(self.app.root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.configure(bg=self.theme.border)

        w, h = 520, 320
        self.app.root.update_idletasks()
        x = self.app.root.winfo_rootx() + (self.app.root.winfo_width() - w) // 2
        y = self.app.root.winfo_rooty() + 100
        self._win.geometry(f"{w}x{h}+{x}+{y}")

        inner = tk.Frame(self._win, bg=self.theme.surface)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        # поиск
        search_wrap = tk.Frame(inner, bg=self.theme.surface)
        search_wrap.pack(fill="x", padx=12, pady=(12, 8))
        self._var = tk.StringVar()
        entry = tk.Entry(search_wrap, textvariable=self._var, bd=0,
                         relief="flat", bg=self.theme.surface2,
                         fg=self.theme.fg, insertbackground=self.theme.accent,
                         font=self.theme.tk_font(2))
        entry.pack(fill="x", ipady=10, padx=1, pady=1)
        entry.insert(0, self.placeholder)
        entry.configure(fg=self.theme.muted)

        def on_focus_in(_):
            if self._var.get() == self.placeholder:
                entry.delete(0, "end")
                entry.configure(fg=self.theme.fg)
        def on_focus_out(_):
            if not self._var.get():
                entry.insert(0, self.placeholder)
                entry.configure(fg=self.theme.muted)

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        entry.focus_set()

        # список
        self._list = tk.Frame(inner, bg=self.theme.surface)
        self._list.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        self._filtered = []
        self._selected = 0

        def refresh(*_):
            self._render_list()
        self._var.trace_add("write", refresh)
        self._render_list()

        self._win.bind("<Escape>", lambda e: self._close())
        entry.bind("<Down>", lambda e: self._move(1))
        entry.bind("<Up>", lambda e: self._move(-1))
        entry.bind("<Return>", lambda e: self._execute())

        # закрытие по клику вне
        self._win.bind("<FocusOut>", lambda e: self._close())

        fade_in(self._win, duration=0.18)
        slide_in(self._win, from_dy=-20, duration=0.22)

    def _render_list(self):
        for w in self._list.winfo_children():
            w.destroy()
        q = self._var.get().lower()
        if q == self.placeholder.lower():
            q = ""
        filtered = []
        for cmd in self.commands:
            title, cb = cmd[0], cmd[1]
            kw = cmd[2] if len(cmd) > 2 else ""
            if not q or q in title.lower() or q in str(kw).lower():
                filtered.append((title, cb))
        self._filtered = filtered

        if self._selected >= len(filtered):
            self._selected = max(len(filtered) - 1, 0)

        for i, (title, _) in enumerate(filtered):
            bg = self.theme.surface2 if i == self._selected else self.theme.surface
            fg = self.theme.accent if i == self._selected else self.theme.fg
            lbl = tk.Label(self._list, text=title, bg=bg, fg=fg,
                           font=self.theme.tk_font(1),
                           anchor="w", padx=12, pady=8, cursor="hand2")
            lbl.pack(fill="x", pady=1)
            lbl.bind("<Button-1>", lambda e, idx=i: self._execute(idx))
            lbl.bind("<Enter>", lambda e, idx=i: self._hover(idx))

    def _hover(self, idx):
        self._selected = idx
        self._render_list()

    def _move(self, delta):
        if not self._filtered:
            return
        self._selected = (self._selected + delta) % len(self._filtered)
        self._render_list()

    def _execute(self, idx=None):
        i = self._selected if idx is None else idx
        if 0 <= i < len(self._filtered):
            title, cb = self._filtered[i]
            self._close()
            try:
                cb()
            except Exception:
                pass

    def _close(self):
        if self._win and self._win.winfo_exists():
            fade_out(self._win, duration=0.15)
        self._win = None