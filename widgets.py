"""Виджеты для оконного режима (tkinter)."""
import tkinter as tk


# ============================================================
# Утилиты
# ============================================================

def _shade(hex_color, factor):
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, min(255, int(c * factor))) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


# ============================================================
# Кнопки
# ============================================================

class StyledButton(tk.Frame):
    VARIANTS = {
        "primary":   ("accent", "accent_fg"),
        "secondary": ("surface2", "fg"),
        "ghost":     (None, "fg"),
        "danger":    ("danger", None),
        "success":   ("success", None),
        "warning":   ("warning", None),
        "info":      ("info", None),
    }
    SIZES = {
        "sm": (10, 6, 0),
        "md": (16, 10, 0),
        "lg": (22, 14, 2),
    }

    def __init__(self, master, text, command=None, theme=None,
                 variant="primary", size="md", width=None, icon=None,
                 state="normal"):
        super().__init__(master, bg=theme.bg, bd=0, highlightthickness=0)
        self.theme = theme
        self.command = command
        self.state = state

        fg_attr, bg_attr = self.VARIANTS.get(variant, self.VARIANTS["primary"])
        padx, pady, size_delta = self.SIZES.get(size, self.SIZES["md"])

        bg = getattr(theme, bg_attr) if bg_attr else theme.bg
        fg = getattr(theme, fg_attr) if fg_attr else "#ffffff"
        if variant == "ghost":
            bg = theme.bg
            fg = theme.fg

        self._bg = bg
        self._fg = fg
        self._hover = _shade(bg, 1.15) if bg != theme.bg else theme.surface

        label = f"{icon} {text}" if icon else text
        self.label = tk.Label(
            self, text=label, bg=bg, fg=fg,
            font=theme.tk_font(size_delta, "bold"),
            padx=padx, pady=pady,
            cursor="hand2" if state == "normal" else "arrow",
        )
        if width:
            self.label.configure(width=width)
        self.label.pack(fill="both", expand=True)

        if state == "normal":
            for w in (self, self.label):
                w.bind("<Enter>", self._on_enter)
                w.bind("<Leave>", self._on_leave)
                w.bind("<Button-1>", self._on_press)
                w.bind("<ButtonRelease-1>", self._on_release)
        else:
            self.label.configure(fg=theme.muted)

    def _on_enter(self, _):
        self.label.configure(bg=self._hover)

    def _on_leave(self, _):
        self.label.configure(bg=self._bg)

    def _on_press(self, _):
        self.label.configure(bg=_shade(self._bg, 0.85))

    def _on_release(self, _):
        self.label.configure(bg=self._hover)
        if self.command and self.state == "normal":
            self.command()

    def set_text(self, text):
        self.label.configure(text=text)


class IconButton(StyledButton):
    """Квадратная кнопка-иконка."""

    def __init__(self, master, icon, command=None, theme=None,
                 variant="ghost", size="md", tooltip=None):
        super().__init__(master, text="", command=command, theme=theme,
                         variant=variant, size=size, icon=icon)
        if tooltip:
            Tooltip(self, tooltip, theme)


# ============================================================
# Поля ввода
# ============================================================

class StyledEntry(tk.Frame):
    def __init__(self, master, theme, label=None, placeholder="",
                 show=None, width=None, prefix=None, suffix=None):
        super().__init__(master, bg=theme.bg, bd=0)
        self.theme = theme
        self.placeholder = placeholder

        if label:
            tk.Label(self, text=label, bg=theme.bg, fg=theme.muted,
                     font=theme.tk_font(-1)).pack(anchor="w", pady=(0, 4))

        self.border = tk.Frame(self, bg=theme.border, bd=0)
        self.border.pack(fill="x")
        self.inner = tk.Frame(self.border, bg=theme.surface, bd=0)
        self.inner.pack(fill="x", padx=1, pady=1)

        if prefix:
            tk.Label(self.inner, text=prefix, bg=theme.surface,
                     fg=theme.muted, font=theme.tk_font(), padx=8).pack(side="left")

        self.var = tk.StringVar()
        self.entry = tk.Entry(
            self.inner, textvariable=self.var, bd=0, relief="flat",
            bg=theme.surface, fg=theme.fg, insertbackground=theme.accent,
            font=theme.tk_font(),
        )
        if width:
            self.entry.configure(width=width)
        self.entry.pack(side="left", fill="x", expand=True, padx=12, pady=10)

        if suffix:
            tk.Label(self.inner, text=suffix, bg=theme.surface,
                     fg=theme.muted, font=theme.tk_font(), padx=8).pack(side="right")

        if show:
            self.entry.configure(show=show)
        self._placeholder_active = False
        self._setup_placeholder()
        self.entry.bind("<FocusIn>", self._focus_in, add="+")
        self.entry.bind("<FocusOut>", self._focus_out, add="+")

    def _setup_placeholder(self):
        if self.placeholder and not self.var.get():
            self._placeholder_active = True
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=self.theme.muted)

    def _focus_in(self, _=None):
        self.border.configure(bg=self.theme.accent)
        if self._placeholder_active:
            self.entry.delete(0, "end")
            self.entry.configure(fg=self.theme.fg)
            self._placeholder_active = False

    def _focus_out(self, _=None):
        self.border.configure(bg=self.theme.border)
        if self.placeholder and not self.var.get():
            self._placeholder_active = True
            self.entry.insert(0, self.placeholder)
            self.entry.configure(fg=self.theme.muted)

    def get(self) -> str:
        return "" if self._placeholder_active else self.var.get()

    def set(self, value):
        self.entry.delete(0, "end")
        if value:
            self.entry.insert(0, value)
            self.entry.configure(fg=self.theme.fg)
            self._placeholder_active = False
        else:
            self._setup_placeholder()


class TextArea(tk.Frame):
    def __init__(self, master, theme, label=None, height=8, width=None,
                 mono=True):
        super().__init__(master, bg=theme.bg, bd=0)
        self.theme = theme

        if label:
            tk.Label(self, text=label, bg=theme.bg, fg=theme.muted,
                     font=theme.tk_font(-1)).pack(anchor="w", pady=(0, 4))

        border = tk.Frame(self, bg=theme.border)
        border.pack(fill="both", expand=True)
        inner = tk.Frame(border, bg=theme.surface)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        font = theme.tk_mono() if mono else theme.tk_font()
        self.text = tk.Text(inner, bd=0, relief="flat", bg=theme.surface,
                            fg=theme.fg, insertbackground=theme.accent,
                            font=font, height=height, wrap="word",
                            highlightthickness=0)
        if width:
            self.text.configure(width=width)
        self.text.pack(fill="both", expand=True, padx=8, pady=8)

    def get(self):
        return self.text.get("1.0", "end-1c")

    def set(self, value):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)


# ============================================================
# Переключатели
# ============================================================

class Toggle(tk.Frame):
    """Выключатель (switch)."""

    def __init__(self, master, theme, text="", initial=False, command=None,
                 width=44, height=22):
        super().__init__(master, bg=theme.bg)
        self.theme = theme
        self.command = command
        self._value = initial
        self._on_bg = theme.accent
        self._off_bg = theme.surface2
        self._w, self._h = width, height

        self.canvas = tk.Canvas(self, width=width, height=height, bd=0,
                                highlightthickness=0, bg=theme.bg)
        self.canvas.pack(side="left")

        self._track_left = self.canvas.create_oval(0, 0, height, height,
                                                   fill=self._off_bg, outline="")
        self._track_right = self.canvas.create_oval(width - height, 0, width, height,
                                                    fill=self._off_bg, outline="")
        self._track_rect = self.canvas.create_rectangle(height / 2, 0,
                                                        width - height / 2, height,
                                                        fill=self._off_bg, outline="")
        self._knob = self.canvas.create_oval(2, 2, height - 2, height - 2,
                                             fill="#ffffff", outline="")

        self.label = None
        if text:
            self.label = tk.Label(self, text=text, bg=theme.bg, fg=theme.fg,
                                  font=theme.tk_font(), cursor="hand2")
            self.label.pack(side="left", padx=(8, 0))

        targets = (self, self.canvas) + ((self.label,) if self.label else ())
        for w in targets:
            w.bind("<Button-1>", self._on_click)
        self.canvas.configure(cursor="hand2")
        self._apply()

    def _apply(self):
        pos = self._w - self._h + 2 if self._value else 2
        self.canvas.coords(self._knob, pos, 2, pos + self._h - 4, self._h - 2)
        color = self._on_bg if self._value else self._off_bg
        for item in (self._track_left, self._track_right, self._track_rect):
            self.canvas.itemconfigure(item, fill=color)

    def _on_click(self, _):
        self._value = not self._value
        self._apply()
        if self.command:
            self.command(self._value)

    def get(self):
        return self._value

    def set(self, value):
        self._value = bool(value)
        self._apply()


class Checkbox(tk.Frame):
    def __init__(self, master, theme, text="", initial=False, command=None):
        super().__init__(master, bg=theme.bg)
        self.theme = theme
        self.command = command
        self._value = initial

        self.box = tk.Label(self, text="✓" if initial else "",
                            bg=theme.accent if initial else theme.surface,
                            fg=theme.accent_fg, font=theme.tk_font(1, "bold"),
                            width=2, height=1, cursor="hand2",
                            highlightthickness=1,
                            highlightbackground=theme.border)
        self.box.pack(side="left")

        self.label = tk.Label(self, text=text, bg=theme.bg, fg=theme.fg,
                              font=theme.tk_font(), cursor="hand2")
        if text:
            self.label.pack(side="left", padx=(8, 0))

        for w in (self, self.box, self.label):
            w.bind("<Button-1>", self._on_click)

    def _on_click(self, _):
        self._value = not self._value
        if self._value:
            self.box.configure(text="✓", bg=self.theme.accent,
                               fg=self.theme.accent_fg)
        else:
            self.box.configure(text="", bg=self.theme.surface, fg=self.theme.fg)
        if self.command:
            self.command(self._value)

    def get(self):
        return self._value

    def set(self, value):
        self._value = bool(value)
        self.box.configure(text="✓" if self._value else "",
                           bg=self.theme.accent if self._value else self.theme.surface,
                           fg=self.theme.accent_fg if self._value else self.theme.fg)


class RadioGroup(tk.Frame):
    def __init__(self, master, theme, options, initial=0, command=None,
                 vertical=True):
        super().__init__(master, bg=theme.bg)
        self.theme = theme
        self.options = list(options)
        self.command = command
        self._value = initial
        self._buttons = []

        self.var = tk.IntVar(value=initial)
        for i, opt in enumerate(self.options):
            rb = tk.Radiobutton(
                self, text=opt, variable=self.var, value=i,
                bg=theme.bg, fg=theme.fg, selectcolor=theme.surface,
                activebackground=theme.bg, activeforeground=theme.accent,
                font=theme.tk_font(), bd=0, highlightthickness=0,
                command=self._on_change,
            )
            if vertical:
                rb.pack(anchor="w", pady=2)
            else:
                rb.pack(side="left", padx=(0, 12))
            self._buttons.append(rb)

    def _on_change(self):
        self._value = self.var.get()
        if self.command:
            self.command(self._value)

    def get(self):
        return self._value

    def set(self, index):
        self.var.set(index)
        self._value = index


class Slider(tk.Frame):
    def __init__(self, master, theme, from_=0, to=100, initial=50,
                 command=None, width=200, show_value=True, label=None):
        super().__init__(master, bg=theme.bg)
        self.theme = theme
        self.command = command
        self.from_ = from_
        self.to = to
        self._value = initial
        self._width = width

        if label:
            tk.Label(self, text=label, bg=theme.bg, fg=theme.muted,
                     font=theme.tk_font(-1)).pack(anchor="w")

        row = tk.Frame(self, bg=theme.bg)
        row.pack(fill="x")
        self.canvas = tk.Canvas(row, width=width, height=24, bd=0,
                                highlightthickness=0, bg=theme.bg)
        self.canvas.pack(side="left")

        self.value_label = None
        if show_value:
            self.value_label = tk.Label(row, text=str(initial), bg=theme.bg,
                                        fg=theme.fg, font=theme.tk_mono(),
                                        width=5)
            self.value_label.pack(side="left", padx=(8, 0))

        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self._render()

    def _render(self):
        self.canvas.delete("all")
        pad = 10
        y = 12
        self.canvas.create_line(pad, y, self._width - pad, y,
                                fill=self.theme.border, width=3, capstyle="round")
        ratio = (self._value - self.from_) / max(self.to - self.from_, 1)
        x = pad + ratio * (self._width - 2 * pad)
        self.canvas.create_line(pad, y, x, y, fill=self.theme.accent,
                                width=3, capstyle="round")
        self.canvas.create_oval(x - 7, y - 7, x + 7, y + 7,
                                fill=self.theme.accent, outline=self.theme.surface,
                                width=2)

    def _pos_to_value(self, x):
        pad = 10
        ratio = max(0, min((x - pad) / (self._width - 2 * pad), 1))
        return int(self.from_ + ratio * (self.to - self.from_))

    def _on_click(self, event):
        self._value = self._pos_to_value(event.x)
        self._render()
        if self.value_label:
            self.value_label.configure(text=str(self._value))
        if self.command:
            self.command(self._value)

    def _on_drag(self, event):
        self._on_click(event)

    def get(self):
        return self._value

    def set(self, value):
        self._value = value
        self._render()
        if self.value_label:
            self.value_label.configure(text=str(value))


# ============================================================
# Списки и сегменты
# ============================================================

class Combobox(tk.Frame):
    def __init__(self, master, theme, options, initial=None, command=None,
                 width=None, label=None):
        super().__init__(master, bg=theme.bg)
        self.theme = theme
        self.options = list(options)
        self.command = command
        self._value = initial if initial in self.options else (
            self.options[0] if self.options else "")

        if label:
            tk.Label(self, text=label, bg=theme.bg, fg=theme.muted,
                     font=theme.tk_font(-1)).pack(anchor="w", pady=(0, 4))

        self.button = tk.Label(self, text=self._value + "  ▾", bg=theme.surface,
                               fg=theme.fg, font=theme.tk_font(),
                               padx=12, pady=8, anchor="w", cursor="hand2",
                               highlightthickness=1,
                               highlightbackground=theme.border)
        if width:
            self.button.configure(width=width)
        self.button.pack(fill="x")
        self.button.bind("<Button-1>", self._open)

        self._popup = None

    def _open(self, _=None):
        if self._popup:
            self._close()
            return
        self._popup = tk.Toplevel(self)
        self._popup.wm_overrideredirect(True)
        self._popup.configure(bg=self.theme.border)
        x = self.button.winfo_rootx()
        y = self.button.winfo_rooty() + self.button.winfo_height()
        w = self.button.winfo_width()
        self._popup.geometry(f"{w}x{len(self.options) * 30}+{x}+{y}")

        inner = tk.Frame(self._popup, bg=self.theme.surface)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        for opt in self.options:
            lbl = tk.Label(inner, text=opt, bg=self.theme.surface,
                           fg=self.theme.fg, font=self.theme.tk_font(),
                           anchor="w", padx=10, pady=6, cursor="hand2")
            lbl.pack(fill="x")
            lbl.bind("<Enter>", lambda e, w=lbl: w.configure(bg=self.theme.surface2))
            lbl.bind("<Leave>", lambda e, w=lbl: w.configure(bg=self.theme.surface))
            lbl.bind("<Button-1>", lambda e, o=opt: self._choose(o))

        self._popup.bind("<FocusOut>", lambda e: self._close())
        self._popup.focus_set()

    def _choose(self, value):
        self._value = value
        self.button.configure(text=value + "  ▾")
        self._close()
        if self.command:
            self.command(value)

    def _close(self):
        if self._popup:
            self._popup.destroy()
            self._popup = None

    def get(self):
        return self._value

    def set(self, value):
        if value in self.options:
            self._value = value
            self.button.configure(text=value + "  ▾")


class SegmentedControl(tk.Frame):
    def __init__(self, master, theme, options, initial=0, command=None):
        super().__init__(master, bg=theme.border, bd=0)
        self.theme = theme
        self.options = list(options)
        self.command = command
        self._value = initial
        self._labels = []

        for i, opt in enumerate(self.options):
            lbl = tk.Label(self, text=opt, font=theme.tk_font(0, "bold"),
                           padx=14, pady=8, cursor="hand2")
            lbl.pack(side="left", padx=1, pady=1)
            lbl.bind("<Button-1>", lambda e, idx=i: self._choose(idx))
            self._labels.append(lbl)
        self._render()

    def _render(self):
        for i, lbl in enumerate(self._labels):
            if i == self._value:
                lbl.configure(bg=self.theme.accent, fg=self.theme.accent_fg)
            else:
                lbl.configure(bg=self.theme.surface, fg=self.theme.fg)

    def _choose(self, index):
        self._value = index
        self._render()
        if self.command:
            self.command(self.options[index] if self.options else None)

    def get(self):
        return self.options[self._value] if self.options else None

    def set(self, index):
        self._value = index
        self._render()


# ============================================================
# Контейнеры
# ============================================================

class Card(tk.Frame):
    def __init__(self, master, theme, padding=16, title=None, subtitle=None):
        super().__init__(master, bg=theme.border, bd=0)
        self.theme = theme
        self.body = tk.Frame(self, bg=theme.surface, bd=0)
        self.body.pack(fill="both", expand=True, padx=1, pady=1)
        self.inner = tk.Frame(self.body, bg=theme.surface, bd=0)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)
        if title:
            tk.Label(self.inner, text=title, bg=theme.surface, fg=theme.fg,
                     font=theme.tk_font(2, "bold")).pack(
                anchor="w", pady=(0, 2 if subtitle else 10))
        if subtitle:
            tk.Label(self.inner, text=subtitle, bg=theme.surface, fg=theme.muted,
                     font=theme.tk_font(-1)).pack(anchor="w", pady=(0, 10))


class Badge(tk.Label):
    def __init__(self, master, text, theme, variant="accent"):
        colors = {
            "accent":  (theme.accent, theme.accent_fg),
            "success": (theme.success, "#ffffff"),
            "danger":  (theme.danger, "#ffffff"),
            "warning": (theme.warning, "#111111"),
            "info":    (theme.info, "#ffffff"),
            "muted":   (theme.surface2, theme.fg),
        }
        bg, fg = colors.get(variant, colors["accent"])
        super().__init__(master, text=text, bg=bg, fg=fg,
                         font=theme.tk_font(-2, "bold"), padx=8, pady=2)


class Divider(tk.Frame):
    def __init__(self, master, theme, orientation="horizontal", length=None):
        if orientation == "horizontal":
            super().__init__(master, bg=theme.border, height=1)
            if length:
                self.configure(width=length)
        else:
            super().__init__(master, bg=theme.border, width=1)
            if length:
                self.configure(height=length)


class Tabs(tk.Frame):
    def __init__(self, master, theme, tabs, initial=0, on_change=None):
        """tabs — dict{label: widget_factory(parent)} или list of (label, factory)."""
        super().__init__(master, bg=theme.bg)
        self.theme = theme
        self.on_change = on_change
        if isinstance(tabs, dict):
            tabs = list(tabs.items())
        self.tabs = list(tabs)
        self._current = None

        self.bar = tk.Frame(self, bg=theme.bg)
        self.bar.pack(fill="x")
        self._buttons = []

        for i, (label, _) in enumerate(self.tabs):
            b = tk.Label(self.bar, text=label, font=theme.tk_font(0, "bold"),
                         padx=14, pady=10, cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, idx=i: self.select(idx))
            self._buttons.append(b)

        self.content = tk.Frame(self, bg=theme.bg)
        self.content.pack(fill="both", expand=True)

        self.select(initial)

    def select(self, index):
        if self._current == index:
            return
        for child in self.content.winfo_children():
            child.destroy()
        self._current = index
        for i, b in enumerate(self._buttons):
            if i == index:
                b.configure(bg=self.theme.surface, fg=self.theme.accent)
            else:
                b.configure(bg=self.theme.bg, fg=self.theme.muted)
        _, factory = self.tabs[index]
        w = factory(self.content)
        if w is not None:
            w.pack(fill="both", expand=True)
        if self.on_change:
            self.on_change(index)

    def current(self):
        return self._current


# ============================================================
# Заголовки
# ============================================================

class TitleLabel(tk.Label):
    def __init__(self, master, text, theme, size_delta=4, muted=False):
        super().__init__(master, text=text, bg=theme.bg,
                         fg=theme.muted if muted else theme.fg,
                         font=theme.tk_font(size_delta, "bold"))


class SubtitleLabel(tk.Label):
    def __init__(self, master, text, theme):
        super().__init__(master, text=text, bg=theme.bg, fg=theme.muted,
                         font=theme.tk_font(0))


class Caption(tk.Label):
    def __init__(self, master, text, theme):
        super().__init__(master, text=text, bg=theme.bg, fg=theme.muted,
                         font=theme.tk_font(-1))


# ============================================================
# Индикаторы
# ============================================================

class Spinner(tk.Canvas):
    def __init__(self, master, theme, size=28, thickness=3, speed=50,
                 color=None):
        super().__init__(master, width=size, height=size, bd=0,
                         highlightthickness=0, bg=theme.bg)
        self.theme = theme
        self._size = size
        self._thickness = thickness
        self._speed = speed
        self._color = color or theme.accent
        self._angle = 0
        self._running = False

    def start(self):
        self._running = True
        self._tick()
        return self

    def stop(self):
        self._running = False
        self.delete("all")

    def _tick(self):
        if not self._running:
            return
        self.delete("all")
        pad = self._thickness
        self.create_arc(pad, pad, self._size - pad, self._size - pad,
                        start=self._angle, extent=270,
                        style="arc", outline=self._color,
                        width=self._thickness)
        self._angle = (self._angle - 15) % 360
        self.after(self._speed, self._tick)


class ProgressBar(tk.Frame):
    def __init__(self, master, theme, value=0, maximum=100, width=280,
                 height=10, color=None, show_text=False):
        super().__init__(master, bg=theme.bg)
        self.theme = theme
        self._value = value
        self._max = maximum
        self._color = color or theme.accent

        self.canvas = tk.Canvas(self, width=width, height=height, bd=0,
                                highlightthickness=0, bg=theme.bg)
        self.canvas.pack(side="left")
        self._w, self._h = width, height

        self.text_label = None
        if show_text:
            self.text_label = tk.Label(self, text=f"{value}/{maximum}",
                                       bg=theme.bg, fg=theme.muted,
                                       font=theme.tk_mono())
            self.text_label.pack(side="left", padx=(8, 0))

        self._render()

    def _render(self):
        self.canvas.delete("all")
        r = self._h / 2
        self.canvas.create_oval(0, 0, self._h, self._h,
                                fill=self.theme.surface2, outline="")
        self.canvas.create_oval(self._w - self._h, 0, self._w, self._h,
                                fill=self.theme.surface2, outline="")
        self.canvas.create_rectangle(r, 0, self._w - r, self._h,
                                     fill=self.theme.surface2, outline="")
        ratio = max(0, min(self._value / self._max, 1)) if self._max else 0
        fw = ratio * self._w
        if fw > 0:
            self.canvas.create_oval(0, 0, self._h, self._h,
                                    fill=self._color, outline="")
            if fw > self._h:
                self.canvas.create_oval(fw - self._h, 0, fw, self._h,
                                        fill=self._color, outline="")
                self.canvas.create_rectangle(self._h / 2, 0, fw - self._h / 2,
                                             self._h, fill=self._color, outline="")

    def set(self, value):
        self._value = value
        self._render()
        if self.text_label:
            self.text_label.configure(text=f"{value}/{self._max}")

    def configure_max(self, maximum):
        self._max = maximum
        self._render()


# ============================================================
# Tooltip и Toast
# ============================================================

class Tooltip:
    def __init__(self, widget, text, theme, delay=500):
        self.widget = widget
        self.text = text
        self.theme = theme
        self.delay = delay
        self._after_id = None
        self._tip = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _schedule(self, _=None):
        self._after_id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self._tip:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip = tk.Toplevel(self.widget)
        self._tip.wm_overrideredirect(True)
        self._tip.geometry(f"+{x}+{y}")
        tk.Label(self._tip, text=self.text, bg=self.theme.surface2,
                 fg=self.theme.fg, font=self.theme.tk_font(-1),
                 padx=8, pady=4, highlightthickness=1,
                 highlightbackground=self.theme.border).pack()

    def _hide(self, _=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        if self._tip:
            self._tip.destroy()
            self._tip = None


class Toast(tk.Toplevel):
    def __init__(self, master, message, theme, variant="info", duration=2500):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.theme = theme

        colors = {
            "info": theme.info, "success": theme.success,
            "warning": theme.warning, "danger": theme.danger,
            "error": theme.danger, "muted": theme.surface2,
        }
        bg = colors.get(variant, theme.surface2)
        fg = "#ffffff" if variant in ("info", "success", "danger", "error",
                                       "warning") else theme.fg

        wrap = tk.Frame(self, bg=theme.border)
        wrap.pack(fill="both", expand=True)
        inner = tk.Frame(wrap, bg=bg)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        tk.Label(inner, text=message, bg=bg, fg=fg,
                 font=theme.tk_font(0, "bold"), padx=18, pady=12).pack()

        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        master.update_idletasks()
        x = master.winfo_rootx() + (master.winfo_width() - w) // 2
        y = master.winfo_rooty() + 40
        self.geometry(f"+{x}+{y}")
        self.after(duration, self._close)

    def _close(self):
        try:
            self.destroy()
        except Exception:
            pass