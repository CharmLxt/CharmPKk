"""Живые частицы на tk.Canvas: дождь, снег, звёзды, пыль, пузыри, светлячки, матрица."""
import math
import random

import tkinter as tk

from .anim import lerp_color


class ParticleCanvas(tk.Canvas):
    """Полотно с частицами.

    Режимы: rain, snow, stars, dust, bubbles, fireflies, matrix, custom.
    Для custom: передайте emitter(frame, canvas) — вызывается каждый кадр.
    """

    MODES = ("rain", "snow", "stars", "dust", "bubbles", "fireflies",
             "matrix", "custom")

    def __init__(self, master, theme, mode="rain", count=80, speed=1.0,
                 fps=60, fg=None, bg=None, click_spawn=False, **kw):
        super().__init__(master, bg=(bg or theme.bg), highlightthickness=0,
                         bd=0, **kw)
        self.theme = theme
        self.mode = mode
        self.count = count
        self.speed = speed
        self.fps = fps
        self.fg = fg or theme.accent
        self.click_spawn = click_spawn
        self.rng = random.Random()
        self._particles = []
        self._items = []
        self._running = False
        self._job = None
        self._emitter = None
        self._initialized = False

        self.bind("<Configure>", lambda e: self._rebuild())
        self.bind("<Destroy>", self._on_destroy)
        if click_spawn:
            self.bind("<Button-1>", self._on_click_spawn)

    # ---------- публичное ----------

    def set_mode(self, mode, **opts):
        self.mode = mode
        for k, v in opts.items():
            setattr(self, k, v)
        self._rebuild()

    def set_speed(self, speed):
        self.speed = speed

    def set_count(self, count):
        self.count = count
        self._rebuild()

    def set_color(self, fg):
        self.fg = fg
        self._rebuild()

    def set_emitter(self, emitter):
        self._emitter = emitter
        self.mode = "custom"

    def spawn_burst(self, x, y, n=14, color=None, chars=None):
        color = color or self.fg
        chars = chars or ["✦", "*", "·", "+"]
        for _ in range(n):
            ang = self.rng.uniform(0, math.tau)
            sp = self.rng.uniform(1.5, 4.0)
            self._particles.append({
                "type": "burst",
                "x": x, "y": y,
                "vx": math.cos(ang) * sp, "vy": math.sin(ang) * sp,
                "life": self.rng.uniform(0.6, 1.4),
                "ch": self.rng.choice(chars),
                "color": color,
            })

    def start(self):
        if self._running:
            return self
        self._running = True
        if not self._initialized:
            self.after(30, self._rebuild)
        self._tick()
        return self

    def stop(self):
        self._running = False
        if self._job:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None

    # ---------- внутреннее ----------

    def _on_destroy(self, event):
        if event.widget is self:
            self.stop()

    def _on_click_spawn(self, e):
        self.spawn_burst(e.x, e.y)

    def _size(self):
        w = self.winfo_width() or int(self["width"]) or 400
        h = self.winfo_height() or int(self["height"]) or 200
        return w, h

    def _rebuild(self):
        if not self.winfo_exists():
            return
        self._initialized = True
        for it in self._items:
            try:
                self.delete(it)
            except Exception:
                pass
        self._items.clear()
        self._particles.clear()
        w, h = self._size()
        mode = self.mode

        if mode == "rain":
            for _ in range(self.count):
                x = self.rng.uniform(0, w)
                y = self.rng.uniform(-h, h)
                ln = self.rng.uniform(8, 22)
                speed = self.rng.uniform(3.5, 8.5) * self.speed
                item = self.create_line(x, y, x, y + ln,
                                        fill=self.fg, width=1)
                self._particles.append({"x": x, "y": y, "v": speed,
                                        "len": ln, "item": item,
                                        "type": "line"})
        elif mode == "snow":
            for _ in range(self.count):
                x = self.rng.uniform(0, w)
                y = self.rng.uniform(-h, h)
                r = self.rng.uniform(1.2, 2.6)
                speed = self.rng.uniform(0.6, 1.8) * self.speed
                sway = self.rng.uniform(0.4, 1.4)
                phase = self.rng.uniform(0, math.tau)
                item = self.create_oval(x - r, y - r, x + r, y + r,
                                        fill=self.fg, outline="")
                self._particles.append({"x": x, "y": y, "v": speed, "r": r,
                                        "sway": sway, "phase": phase,
                                        "item": item, "type": "circle"})
        elif mode == "stars":
            for _ in range(self.count):
                x = self.rng.uniform(0, w)
                y = self.rng.uniform(0, h)
                r = self.rng.uniform(0.8, 1.8)
                phase = self.rng.uniform(0, math.tau)
                sp = self.rng.uniform(0.8, 2.2)
                item = self.create_oval(x - r, y - r, x + r, y + r,
                                        fill=self.fg, outline="")
                self._particles.append({"x": x, "y": y, "r": r,
                                        "phase": phase, "sp": sp,
                                        "item": item, "type": "star"})
        elif mode == "dust":
            for _ in range(self.count):
                x = self.rng.uniform(0, w)
                y = self.rng.uniform(0, h)
                r = self.rng.uniform(0.6, 1.4)
                vx = self.rng.uniform(-0.5, 0.5)
                vy = self.rng.uniform(-0.2, 0.2)
                item = self.create_oval(x - r, y - r, x + r, y + r,
                                        fill=self.fg, outline="")
                self._particles.append({"x": x, "y": y, "r": r,
                                        "vx": vx * self.speed,
                                        "vy": vy * self.speed,
                                        "item": item, "type": "dust"})
        elif mode == "bubbles":
            for _ in range(self.count):
                x = self.rng.uniform(0, w)
                y = self.rng.uniform(0, h)
                r = self.rng.uniform(2, 7)
                speed = self.rng.uniform(0.4, 1.2) * self.speed
                phase = self.rng.uniform(0, math.tau)
                item = self.create_oval(x - r, y - r, x + r, y + r,
                                        outline=self.fg, width=1, fill="")
                self._particles.append({"x": x, "y": y, "r": r, "v": speed,
                                        "phase": phase, "item": item,
                                        "type": "bubble"})
        elif mode == "fireflies":
            for _ in range(self.count):
                x = self.rng.uniform(0, w)
                y = self.rng.uniform(0, h)
                r = self.rng.uniform(1.5, 3.0)
                vx = self.rng.uniform(-0.6, 0.6)
                vy = self.rng.uniform(-0.4, 0.4)
                phase = self.rng.uniform(0, math.tau)
                sp = self.rng.uniform(1.5, 3.5)
                item = self.create_oval(x - r, y - r, x + r, y + r,
                                        fill=self.fg, outline="")
                self._particles.append({"x": x, "y": y, "r": r,
                                        "vx": vx * self.speed,
                                        "vy": vy * self.speed,
                                        "phase": phase, "sp": sp,
                                        "item": item, "type": "firefly"})
        elif mode == "matrix":
            for _ in range(self.count):
                x = self.rng.uniform(0, w)
                y = self.rng.uniform(-h, h)
                speed = self.rng.uniform(1.5, 4.5) * self.speed
                chars = [self.rng.choice("01ABCDEF#@%") for _ in range(12)]
                item = self.create_text(x, y, text="\n".join(chars),
                                        fill=self.fg, font=("Consolas", 10),
                                        anchor="n")
                self._particles.append({"x": x, "y": y, "v": speed,
                                        "chars": chars, "item": item,
                                        "type": "matrix", "phase": 0})

    def _tick(self):
        if not self._running:
            return
        try:
            if not self.winfo_exists():
                self._running = False
                return
        except Exception:
            self._running = False
            return

        w, h = self._size()
        mode = self.mode
        speed = self.speed

        if mode == "custom" and self._emitter is not None:
            try:
                self._emitter(self, self)
            except Exception:
                pass
        else:
            for p in list(self._particles):
                t = p.get("type")

                if t == "line":
                    p["y"] += p["v"] * speed
                    if p["y"] - p["len"] > h:
                        p["y"] = -p["len"]
                        p["x"] = self.rng.uniform(0, w)
                    x, y = p["x"], p["y"]
                    try:
                        self.coords(p["item"], x, y, x, y + p["len"])
                    except Exception:
                        pass

                elif t == "circle":
                    p["y"] += p["v"] * speed
                    p["phase"] += 0.05
                    p["x"] += math.sin(p["phase"]) * p["sway"] * 0.3
                    if p["y"] - p["r"] > h:
                        p["y"] = -p["r"]
                        p["x"] = self.rng.uniform(0, w)
                    r = p["r"]
                    try:
                        self.coords(p["item"], p["x"] - r, p["y"] - r,
                                    p["x"] + r, p["y"] + r)
                    except Exception:
                        pass

                elif t == "star":
                    p["phase"] += 0.05 * p["sp"]
                    k = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(p["phase"]))
                    c = lerp_color("#11131a", self.fg, k)
                    try:
                        self.itemconfigure(p["item"], fill=c)
                    except Exception:
                        pass

                elif t == "dust":
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    if p["x"] < -5:
                        p["x"] = w + 5
                    elif p["x"] > w + 5:
                        p["x"] = -5
                    if p["y"] < -5:
                        p["y"] = h + 5
                    elif p["y"] > h + 5:
                        p["y"] = -5
                    r = p["r"]
                    try:
                        self.coords(p["item"], p["x"] - r, p["y"] - r,
                                    p["x"] + r, p["y"] + r)
                    except Exception:
                        pass

                elif t == "bubble":
                    p["y"] -= p["v"] * speed
                    p["phase"] += 0.04
                    x = p["x"] + math.sin(p["phase"]) * 4
                    r = p["r"]
                    if p["y"] + r < 0:
                        p["y"] = h + r
                        p["x"] = self.rng.uniform(0, w)
                    try:
                        self.coords(p["item"], x - r, p["y"] - r,
                                    x + r, p["y"] + r)
                    except Exception:
                        pass

                elif t == "firefly":
                    p["vx"] += self.rng.uniform(-0.06, 0.06)
                    p["vy"] += self.rng.uniform(-0.04, 0.04)
                    p["vx"] = max(-0.8, min(0.8, p["vx"]))
                    p["vy"] = max(-0.5, min(0.5, p["vy"]))
                    p["x"] += p["vx"] * speed
                    p["y"] += p["vy"] * speed
                    p["phase"] += 0.1 * p["sp"]
                    if p["x"] < 0 or p["x"] > w:
                        p["vx"] *= -1
                    if p["y"] < 0 or p["y"] > h:
                        p["vy"] *= -1
                    k = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(p["phase"]))
                    c = lerp_color("#3b2f0b", self.fg, k)
                    r = p["r"]
                    try:
                        self.coords(p["item"], p["x"] - r, p["y"] - r,
                                    p["x"] + r, p["y"] + r)
                        self.itemconfigure(p["item"], fill=c)
                    except Exception:
                        pass

                elif t == "matrix":
                    p["y"] += p["v"] * speed
                    if p["y"] - 12 * 16 > h:
                        p["y"] = -12 * 16
                        p["x"] = self.rng.uniform(0, w)
                    try:
                        self.coords(p["item"], p["x"], p["y"])
                    except Exception:
                        pass

                elif t == "burst":
                    p["x"] += p["vx"]
                    p["y"] += p["vy"]
                    p["vy"] += 0.15
                    p["life"] -= 1 / max(self.fps, 1)
                    if p["life"] <= 0:
                        try:
                            self.delete(p["item"])
                        except Exception:
                            pass
                        self._particles.remove(p)
                        continue
                    c = lerp_color(self.theme.bg, p["color"],
                                   min(p["life"], 1.0))
                    try:
                        self.itemconfigure(p["item"], fill=c)
                    except Exception:
                        pass

        for p in list(self._particles):
            if p.get("type") == "burst" and "item" not in p:
                try:
                    item = self.create_text(p["x"], p["y"], text=p["ch"],
                                            fill=p["color"],
                                            font=("Segoe UI", 11))
                    p["item"] = item
                except Exception:
                    pass

        self._job = self.after(int(1000 / max(self.fps, 1)), self._tick)


# ------------------------------------------------------------
# Хелперы для оконных частиц
# ------------------------------------------------------------

def attach_background(parent, theme, mode="dust", count=60, speed=0.6,
                      fg=None, **kw):
    """Создать ParticleCanvas и растянуть на всю родительскую область."""
    pc = ParticleCanvas(parent, theme, mode=mode, count=count, speed=speed,
                        fg=fg, **kw)
    pc.place(x=0, y=0, relwidth=1, relheight=1)
    pc.lower()
    return pc