"""Frameless-окно с кастомным тайтлбаром (drag, min/max/close)."""
import tkinter as tk


class CustomTitleBar(tk.Frame):
    """Заголовок для overrideredirect-окна с кнопками и перетаскиванием."""

    def __init__(self, window, theme, title="", icon="◆", on_close=None,
                 show_maximize=True, show_minimize=True, height=36):
        super().__init__(window, bg=theme.surface, height=height)
        self.window = window
        self.theme = theme
        self._on_close = on_close
        self.pack_propagate(False)

        self._drag_x = 0
        self._drag_y = 0

        # заголовок
        self.title_label = tk.Label(
            self, text=f"{icon} {title}".strip(), bg=theme.surface,
            fg=theme.fg, font=theme.tk_font(0, "bold"), padx=12)
        self.title_label.pack(side="left")

        # кнопки (справа)
        btn_box = tk.Frame(self, bg=theme.surface)
        btn_box.pack(side="right", fill="y")

        if show_minimize:
            self._make_btn(btn_box, "—", self._minimize)
        if show_maximize:
            self._make_btn(btn_box, "▢", self._toggle_max)
        self._make_btn(btn_box, "✕", self._close, hover_bg=theme.danger,
                       hover_fg="#ffffff")

        # drag & doubleclick-to-max
        for w in (self, self.title_label):
            w.bind("<Button-1>", self._start_drag)
            w.bind("<B1-Motion>", self._drag)
            w.bind("<Double-Button-1>", lambda e: self._toggle_max())

        self._maximized = False
        self._prev_geom = None

    def _make_btn(self, parent, text, command, hover_bg=None, hover_fg=None):
        bg = self.theme.surface
        hover_bg = hover_bg or self.theme.surface2
        hover_fg = hover_fg or self.theme.fg
        btn = tk.Label(parent, text=text, bg=bg, fg=self.theme.fg,
                       font=self.theme.tk_font(0, "bold"), width=4,
                       cursor="hand2")
        btn.pack(side="left", fill="y")
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg, fg=hover_fg))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg, fg=self.theme.fg))
        btn.bind("<Button-1>", lambda e: command())
        return btn

    def _start_drag(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def _drag(self, e):
        if self._maximized:
            return
        x = self.window.winfo_x() + e.x - self._drag_x
        y = self.window.winfo_y() + e.y - self._drag_y
        self.window.geometry(f"+{x}+{y}")

    def _minimize(self):
        try:
            self.window.iconify()
        except Exception:
            pass

    def _toggle_max(self):
        if self._maximized:
            if self._prev_geom:
                self.window.geometry(self._prev_geom)
            self._maximized = False
        else:
            self._prev_geom = self.window.geometry()
            sw = self.window.winfo_screenwidth()
            sh = self.window.winfo_screenheight()
            self.window.geometry(f"{sw}x{sh}+0+0")
            self._maximized = True

    def _close(self):
        if self._on_close:
            self._on_close()
        else:
            self.window.destroy()


class FramelessWindow:
    """Готовое окно без системной рамки, с кастомным тайтлбаром.

    fw = FramelessWindow(title="My App", theme=Theme.dark(), size="900x600")
    fw.content  # tk.Frame для вашего контента
    fw.run()
    """

    def __init__(self, title="CharmPkk", theme=None, size="900x600",
                 icon="◆", resizable=True, transparent=False):
        from .theme import Theme
        self.theme = theme or Theme.dark()
        self.root = tk.Tk()
        self.root.title(title)
        self.root.overrideredirect(True)
        self.root.geometry(size)
        self.root.configure(bg=self.theme.bg)
        if transparent:
            try:
                self.root.attributes("-alpha", 0.97)
            except Exception:
                pass

        # тонкая внешняя рамка
        self.outer = tk.Frame(self.root, bg=self.theme.border)
        self.outer.pack(fill="both", expand=True)

        self.titlebar = CustomTitleBar(self.root, self.theme, title=title,
                                       icon=icon, on_close=self.close)
        self.titlebar.pack(fill="x", padx=1, pady=(1, 0))

        self.content = tk.Frame(self.outer, bg=self.theme.bg)
        self.content.pack(fill="both", expand=True, padx=1, pady=1)

        if resizable:
            self._enable_resize()

        self._drag_x = 0
        self._drag_y = 0

    def _enable_resize(self, margin=4):
        self.root.bind("<Motion>", self._on_motion)
        self._resize_edge = None

    def _on_motion(self, e):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        m = 6
        edge = None
        if e.x <= m: edge = "left"
        elif e.x >= w - m: edge = "right"
        if e.y <= m:
            edge = "top" if edge is None else f"top-{edge}"
        elif e.y >= h - m:
            edge = "bottom" if edge is None else f"bottom-{edge}"
        # смена курсора — упрощённо
        self._resize_edge = edge

    def run(self):
        self.root.mainloop()

    def close(self):
        self.root.destroy()