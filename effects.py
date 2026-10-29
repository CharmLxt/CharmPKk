"""Виджетные эффекты: Ripple, Shimmer, Pulse, FadeIn, SlideIn, GradientFrame, NeonBorder."""
import math
import tkinter as tk
from .anim import Animator, lerp_color

def ripple(widget, x, y, color="#ffffff", rings=3, duration=0.6, max_radius=80, theme_bg=None):
    if not isinstance(widget, tk.Canvas): return
    items = []
    for i in range(rings):
        r = 4 + i * 6
        item = widget.create_oval(x - r, y - r, x + r, y + r, outline=color, width=2)
        items.append({"item": item, "phase": -i * 0.08})

    def _tick():
        still = False
        try:
            if not widget.winfo_exists(): return
        except Exception: return
        for s in items:
            if s["phase"] < 0:
                s["phase"] += 0.016
                still = True
                continue
            if s["phase"] < 1.0:
                still = True
                s["phase"] += 0.016 / duration
                t = min(s["phase"], 1.0)
                r = 4 + t * max_radius
                alpha = 1 - t
                c = lerp_color(theme_bg or "#000000", color, alpha)
                try:
                    widget.coords(s["item"], x - r, y - r, x + r, y + r)
                    widget.itemconfigure(s["item"], outline=c, width=max(1, int(3 * alpha)))
                except Exception: return
            else:
                try: widget.delete(s["item"])
                except Exception: pass
                s["phase"] = -10
        if still: widget.after(16, _tick)
    _tick()

class Shimmer:
    def __init__(self, widget, color="#ffffff", period=2.6, width=0.35, skew=2.0):
        self.w = widget
        self.color = color
        self.period = period
        self.width = width
        self.skew = skew
        self._job = None
        self._running = True
        self._t = 0.0
        self.canvas = tk.Canvas(widget, highlightthickness=0, bd=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        try: self.canvas.configure(bg=widget.cget("bg"))
        except Exception: self.canvas.configure(bg="#000000")
        
        self.w.bind("<Destroy>", self._on_destroy, add="+")
        self._loop()

    def _on_destroy(self, event):
        if event.widget is self.w: self.stop()

    def stop(self):
        self._running = False
        if self._job:
            try: self.w.after_cancel(self._job)
            except Exception: pass
            self._job = None
        try: self.canvas.destroy()
        except Exception: pass

    def _loop(self):
        if not self._running: return
        try:
            if not self.w.winfo_exists():
                self._running = False
                return
        except Exception:
            self._running = False
            return

        self.w.update_idletasks()
        W = max(self.canvas.winfo_width(), 1)
        H = max(self.canvas.winfo_height(), 1)
        try: self.canvas.delete("shimmer")
        except Exception: return

        pos = -0.4 + 1.8 * ((self._t % self.period) / self.period)
        x0 = pos * W
        bw = W * self.width
        try:
            self.canvas.create_polygon(x0, 0, x0 + bw, 0, x0 + bw - self.skew * H, H, x0 - self.skew * H, H, fill=self.color, outline="", tags="shimmer")
            self.canvas.itemconfigure("shimmer", stipple="gray25")
        except Exception: pass

        self._t += 0.03
        self._job = self.w.after(30, self._loop)

def pulse(widget, base_color=None, peak_color="#ffffff", duration=0.8, cycles=2, on_done=None):
    base = base_color or widget.cget("bg")
    Animator(widget).pulse("pulse", widget, base, peak_color, duration=duration, cycles=cycles, on_done=on_done)

def fade_in(window, duration=0.35, from_alpha=0.0, to_alpha=1.0):
    try: window.attributes("-alpha", from_alpha)
    except Exception: return
    Animator(window).tween("alpha", from_alpha, to_alpha, duration=duration, fps=60, on_step=lambda v: window.attributes("-alpha", v))

def fade_out(window, duration=0.3, destroy=True, on_done=None):
    target = 0.02
    def _done():
        if destroy:
            try: window.destroy()
            except Exception: pass
        if on_done: on_done()
    Animator(window).tween("alpha", 1.0, target, duration=duration, fps=60, on_step=lambda v: window.attributes("-alpha", v), on_done=_done)

def slide_in(window, from_dx=-60, from_dy=0, duration=0.32):
    window.update_idletasks()
    x, y = window.winfo_x(), window.winfo_y()
    start_x = x + from_dx
    start_y = y + from_dy
    def _set(vx, vy):
        try: window.geometry(f"+{int(vx)}+{int(vy)}")
        except Exception: pass
    anim = Animator(window)
    anim.tween("sx", start_x, x, duration=duration, fps=60, on_step=lambda v: _set(v, start_y))
    anim.tween("sy", start_y, y, duration=duration, fps=60, on_step=lambda v: _set(x, v))

class GradientFrame(tk.Canvas):
    def __init__(self, master, color_top, color_bottom, direction="vertical", width=200, height=100, **kw):
        super().__init__(master, width=width, height=height, highlightthickness=0, bd=0, **kw)
        self.color_top = color_top
        self.color_bottom = color_bottom
        self.direction = direction
        self.bind("<Configure>", lambda e: self._draw())

    def set_colors(self, top, bottom, redraw=True):
        self.color_top = top
        self.color_bottom = bottom
        if redraw: self._draw()

    def _draw(self):
        self.delete("grad")
        W = self.winfo_width() or int(self["width"])
        H = self.winfo_height() or int(self["height"])
        if W <= 1 or H <= 1: return
        steps = H if self.direction == "vertical" else W
        steps = min(steps, 200)
        for i in range(steps):
            t = i / max(steps - 1, 1)
            c = lerp_color(self.color_top, self.color_bottom, t)
            if self.direction == "vertical":
                y0 = int(H * i / steps)
                y1 = int(H * (i + 1) / steps) + 1
                self.create_rectangle(0, y0, W, y1, fill=c, outline="", tags="grad")
            else:
                x0 = int(W * i / steps)
                x1 = int(W * (i + 1) / steps) + 1
                self.create_rectangle(x0, 0, x1, H, fill=c, outline="", tags="grad")

class NeonBorder:
    def __init__(self, container_widget, color="#7aa2ff", base="#1b1e28", period=1.6, width=1):
        self.w = container_widget
        self.color = color
        self.base = base
        self.period = period
        self.width = width
        self._t = 0.0
        self._running = True
        self._job = None
        self.w.bind("<Destroy>", self._on_destroy, add="+")
        self._loop()

    def _on_destroy(self, event):
        if event.widget is self.w: self.stop()

    def stop(self):
        self._running = False
        if self._job:
            try: self.w.after_cancel(self._job)
            except Exception: pass
            self._job = None

    def set_color(self, color): self.color = color

    def _loop(self):
        if not self._running: return
        try:
            if not self.w.winfo_exists():
                self._running = False
                return
        except Exception:
            self._running = False
            return

        t = (self._t % self.period) / self.period
        k = 0.5 + 0.5 * math.sin(t * math.tau)
        c = lerp_color(self.base, self.color, k)
        try: self.w.configure(highlightthickness=self.width, highlightbackground=c, highlightcolor=c)
        except Exception: pass
        self._t += 0.04
        self._job = self.w.after(40, self._loop)

class GlowText:
    def __init__(self, label, base="#8b93a7", glow="#7aa2ff", period=2.0):
        self.label = label
        self.base = base
        self.glow = glow
        self.period = period
        self._t = 0.0
        self._running = True
        self._job = None
        self.label.bind("<Destroy>", self._on_destroy, add="+")
        self._loop()

    def _on_destroy(self, event):
        if event.widget is self.label: self.stop()

    def stop(self):
        self._running = False
        if self._job:
            try: self.label.after_cancel(self._job)
            except Exception: pass
            self._job = None

    def _loop(self):
        if not self._running: return
        try:
            if not self.label.winfo_exists():
                self._running = False
                return
        except Exception:
            self._running = False
            return

        t = (self._t % self.period) / self.period
        k = 0.5 + 0.5 * math.sin(t * math.tau)
        try: self.label.configure(fg=lerp_color(self.base, self.glow, k))
        except Exception: pass
        self._t += 0.03
        self._job = self.label.after(30, self._loop)