"""Acrylic / Mica (Windows) + эффект «жидкого стекла» для tkinter."""
import os
import sys
import tkinter as tk

from .anim import lerp_color, Animator


# ============================================================
# Системный акрил / mica на Windows 10 и 11
# ============================================================

def _hwnd_of(root):
    """Реальный HWND верхнего окна."""
    try:
        import ctypes
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        if not hwnd:
            hwnd = root.winfo_id()
        return hwnd
    except Exception:
        return None


def apply_acrylic_win11(root, kind="acrylic", tint=None):
    """Acrylic / Mica на Windows 11 через DWMWA_SYSTEMBACKDROP_TYPE."""
    if os.name != "nt":
        return False
    import ctypes
    hwnd = _hwnd_of(root)
    if not hwnd:
        return False

    DWMWA_SYSTEMBACKDROP_TYPE = 38
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    DWMWA_BORDER_COLOR = 34
    DWMWA_CAPTION_COLOR = 35
    DWMWA_TEXT_COLOR = 36

    kinds = {
        "auto": 0,
        "none": 1,
        "mica": 2,
        "acrylic": 3,           # TransientWindow
        "tabbed": 4,
    }
    try:
        value = ctypes.c_int(kinds.get(kind, 3))
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd), DWMWA_SYSTEMBACKDROP_TYPE,
            ctypes.byref(value), ctypes.sizeof(value))

        dark = ctypes.c_int(1)
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            ctypes.c_void_p(hwnd), DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(dark), ctypes.sizeof(dark))

        if tint:
            r, g, b, a = tint
            colorref = ctypes.c_int((b << 16) | (g << 8) | r)
            for attr in (DWMWA_CAPTION_COLOR, DWMWA_BORDER_COLOR):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    ctypes.c_void_p(hwnd), attr,
                    ctypes.byref(colorref), ctypes.sizeof(colorref))
            text = ctypes.c_int(0x00FFFFFF)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.c_void_p(hwnd), DWMWA_TEXT_COLOR,
                ctypes.byref(text), ctypes.sizeof(text))
        return True
    except Exception:
        return False


def apply_acrylic_win10(root, color=(20, 24, 34, 180)):
    """Acrylic через SetWindowCompositionAttribute (Win10 1803+)."""
    if os.name != "nt":
        return False
    import ctypes
    from ctypes import wintypes

    class ACCENTPOLICY(ctypes.Structure):
        _fields_ = [("AccentState", ctypes.c_uint),
                    ("AccentFlags", ctypes.c_uint),
                    ("GradientColor", ctypes.c_uint),
                    ("AnimationId", ctypes.c_uint)]

    class WINCOMPATTRDATA(ctypes.Structure):
        _fields_ = [("Attribute", ctypes.c_int),
                    ("Data", ctypes.POINTER(ACCENTPOLICY)),
                    ("SizeOfData", ctypes.c_size_t)]

    hwnd = _hwnd_of(root)
    if not hwnd:
        return False

    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

    r, g, b, a = color
    # GradientColor — ABGR
    gradient = (a << 24) | (b << 16) | (g << 8) | r

    accent = ACCENTPOLICY()
    accent.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
    accent.AccentFlags = 2
    accent.GradientColor = gradient

    data = WINCOMPATTRDATA()
    data.Attribute = 19
    data.Data = ctypes.pointer(accent)
    data.SizeOfData = ctypes.sizeof(accent)

    try:
        ctypes.windll.user32.SetWindowCompositionAttribute(
            wintypes.HWND(hwnd), ctypes.byref(data))
        return True
    except Exception:
        return False


def apply_acrylic(root, kind="acrylic", tint=None, fallback_alpha=None):
    """Универсально: пробует Win11 → Win10 → плавный alpha-fallback."""
    tint = tint or (18, 20, 28, 200)
    if apply_acrylic_win11(root, kind=kind, tint=tint):
        return "win11"
    if apply_acrylic_win10(root, color=tint):
        return "win10"
    if fallback_alpha is not None:
        try:
            root.attributes("-alpha", fallback_alpha)
        except Exception:
            pass
        return "alpha"
    return "none"


# ============================================================
# GlassCard — карточка "жидкое стекло"
# ============================================================

class GlassCard(tk.Frame):
    """Имитация матового стекла: подсветка краёв, градиент, тень.

    Параметры:
        alpha       — «прозрачность» (0..1), влияет на яркость верхнего слоя
        depth       — толщина стекла (насколько темнее нижний край)
        shine       — яркость верхней подсветки
        dispersion  — лёгкий цветовой сдвиг по краям (имитация дисперсии)
        hover_glow  — включать свечение при наведении
    """

    def __init__(self, master, theme, padding=16, width=None, height=None,
                 title=None, subtitle=None, tint=None, alpha=0.5,
                 hover_glow=True, accent=None, depth=0.04, shine=0.06,
                 dispersion=0.0):
        self.theme = theme
        self.alpha = alpha
        self.hover_glow = hover_glow
        self.accent = accent or theme.accent
        self.depth = depth
        self.shine = shine
        self.dispersion = dispersion

        base = tint or theme.surface
        top = lerp_color(base, "#ffffff", self.shine * (1 + alpha))
        bottom = lerp_color(base, "#000000", self.depth)

        super().__init__(master, bg=theme.bg)

        self.border_frame = tk.Frame(self,
                                     bg=lerp_color(base, "#ffffff", 0.18),
                                     bd=0)
        self.border_frame.pack(fill="both", expand=True)

        self.mid = tk.Frame(self.border_frame, bg=top, bd=0)
        self.mid.pack(fill="both", expand=True, padx=1, pady=1)

        self.bottom_strip = tk.Frame(self.mid, bg=bottom, bd=0, height=1)
        self.bottom_strip.pack(side="bottom", fill="x")

        self.inner = tk.Frame(self.mid, bg=top, bd=0)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)

        if title:
            tk.Label(self.inner, text=title, bg=top, fg=theme.fg,
                     font=theme.tk_font(2, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(self.inner, text=subtitle, bg=top, fg=theme.muted,
                     font=theme.tk_font(-1)).pack(anchor="w", pady=(2, 8))

        self._base_border = lerp_color(base, "#ffffff", 0.18)

        if self.dispersion > 0:
            self._base_border = lerp_color(self._base_border, theme.accent,
                                           self.dispersion)

        if hover_glow:
            for w in (self, self.border_frame, self.mid, self.inner):
                w.bind("<Enter>", self._on_enter, add="+")
                w.bind("<Leave>", self._on_leave, add="+")

    def _on_enter(self, _=None):
        anim = Animator(self)
        anim.tween("glow", 0.0, 1.0, duration=0.25,
                   on_step=lambda v: self.border_frame.configure(
                       bg=lerp_color(self._base_border, self.accent, v)))

    def _on_leave(self, _=None):
        anim = Animator(self)
        anim.tween("glow", 1.0, 0.0, duration=0.25,
                   on_step=lambda v: self.border_frame.configure(
                       bg=lerp_color(self._base_border, self.accent, v)))


# ============================================================
# LiquidGlassPanel — многослойная панель с "преломлением"
# ============================================================

class LiquidGlassPanel(tk.Frame):
    """Панель с усиленным эффектом «жидкого стекла»:
    несколько слоёв, градиент, блик и опциональная дисперсия.

    Параметры:
        layers      — количество слоёв подложки (2..5 обычно)
        refraction  — сила «преломления» (сдвиг цвета по слоям)
        shine       — яркость верхней подсветки
    """

    def __init__(self, master, theme, padding=18, tint=None, layers=3,
                 refraction=0.12, shine=0.08):
        super().__init__(master, bg=theme.bg)
        base = tint or theme.surface

        cur = self
        self.layers = []
        for i in range(max(layers, 1)):
            shade = lerp_color(base, "#ffffff",
                               shine * (layers - i) / max(layers, 1))
            if refraction > 0:
                shade = lerp_color(shade, theme.accent,
                                   refraction * (i / max(layers - 1, 1)))
            f = tk.Frame(cur, bg=shade, bd=0)
            f.pack(fill="both", expand=True, padx=1, pady=1)
            self.layers.append(f)
            cur = f

        self.inner = tk.Frame(cur, bg=lerp_color(base, "#ffffff", shine),
                              bd=0)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)


# ============================================================
# GlassPanel — упрощённый вариант (оставлен для совместимости)
# ============================================================

class GlassPanel(tk.Frame):
    """Панель с несколькими полупрозрачными слоями (визуальный blur-эффект)."""

    def __init__(self, master, theme, layers=3, padding=18, tint=None):
        super().__init__(master, bg=theme.bg)
        base = tint or theme.surface
        self.layers = []

        cur = self
        for i in range(layers):
            shade = lerp_color(base, "#ffffff", 0.04 * (layers - i))
            f = tk.Frame(cur, bg=shade, bd=0)
            f.pack(fill="both", expand=True, padx=1, pady=1)
            self.layers.append(f)
            cur = f

        self.inner = tk.Frame(cur, bg=lerp_color(base, "#ffffff", 0.04),
                              bd=0)
        self.inner.pack(fill="both", expand=True, padx=padding, pady=padding)


# ============================================================
# Frost — "морозное" затемнение поверх окна
# ============================================================

class Frost(tk.Toplevel):
    """Полупрозрачный слой, имитирующий blur заднего фона."""

    def __init__(self, master, theme, tint="#0b0d14", alpha=0.45):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(bg=tint)
        try:
            self.attributes("-alpha", 0.0)
        except Exception:
            pass
        self._target_alpha = alpha
        self.geometry(f"{master.winfo_width()}x{master.winfo_height()}"
                      f"+{master.winfo_rootx()}+{master.winfo_rooty()}")
        self.after(10, self._fade_in)
        self.bind("<Button-1>", lambda e: self.close())

    def _fade_in(self):
        anim = Animator(self)
        anim.tween("a", 0.0, self._target_alpha, duration=0.2,
                   on_step=lambda v: self.attributes("-alpha", v))

    def close(self):
        anim = Animator(self)
        target = 0.02  # не 0.0 — иначе на Windows остаётся «призрак»

        def _done():
            try:
                self.destroy()
            except Exception:
                pass

        anim.tween("a", self._target_alpha, target, duration=0.18,
                   on_step=lambda v: self.attributes("-alpha", v),
                   on_done=_done)


# ============================================================
# Хелпер для быстрого "стеклянного" окна
# ============================================================

def make_glass_app(app, kind="acrylic", tint=(18, 20, 28, 200),
                   fallback_alpha=0.96):
    """Навешивает акрил на App (или tk.Tk) и возвращает строку с результатом."""
    return apply_acrylic(app.root, kind=kind, tint=tint,
                         fallback_alpha=fallback_alpha)