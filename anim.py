"""Плавная анимация свойств виджетов tkinter."""
import math

def linear(t): return t
def ease_in_quad(t): return t * t
def ease_out_quad(t): return 1 - (1 - t) ** 2
def ease_in_out_quad(t): return 2 * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 2 / 2
def ease_in_cubic(t): return t ** 3
def ease_out_cubic(t): return 1 - (1 - t) ** 3
def ease_in_out_cubic(t): return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2
def ease_in_out_sine(t): return -(math.cos(math.pi * t) - 1) / 2
def ease_in_expo(t): return 0 if t == 0 else 2 ** (10 * t - 10)
def ease_out_expo(t): return 1 if t == 1 else 1 - 2 ** (-10 * t)

def ease_out_back(t):
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def ease_out_elastic(t):
    if t in (0.0, 1.0): return t
    c4 = (2 * math.pi) / 3
    return 2 ** (-10 * t) * math.sin((t * 10 - 0.75) * c4) + 1

def ease_out_bounce(t):
    n1, d1 = 7.5625, 2.75
    if t < 1 / d1: return n1 * t * t
    if t < 2 / d1:
        t -= 1.5 / d1
        return n1 * t * t + 0.75
    if t < 2.5 / d1:
        t -= 2.25 / d1
        return n1 * t * t + 0.9375
    t -= 2.625 / d1
    return n1 * t * t + 0.984375

EASINGS = {
    "linear": linear, "in_quad": ease_in_quad, "out_quad": ease_out_quad,
    "in_out_quad": ease_in_out_quad, "in_cubic": ease_in_cubic,
    "out_cubic": ease_out_cubic, "in_out_cubic": ease_in_out_cubic,
    "in_out_sine": ease_in_out_sine, "in_expo": ease_in_expo,
    "out_expo": ease_out_expo, "out_back": ease_out_back,
    "out_elastic": ease_out_elastic, "out_bounce": ease_out_bounce,
}

def ease(t, kind="out_cubic"):
    return EASINGS.get(kind, ease_out_cubic)(max(0.0, min(1.0, t)))

def lerp(a, b, t):
    return a + (b - a) * t

def _hex_to_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*(max(0, min(255, int(c))) for c in rgb))

def lerp_color(c1, c2, t):
    a, b = _hex_to_rgb(c1), _hex_to_rgb(c2)
    return _rgb_to_hex((a[i] + (b[i] - a[i]) * t for i in range(3)))


class Animator:
    def __init__(self, widget):
        self.widget = widget
        self._jobs = {}

    def stop(self, key=None):
        keys = [key] if key else list(self._jobs.keys())
        for k in keys:
            job = self._jobs.pop(k, None)
            if job:
                try: self.widget.after_cancel(job)
                except Exception: pass

    def _is_alive(self):
        try: return self.widget.winfo_exists()
        except Exception: return False

    def tween(self, key, from_, to, duration=0.3, fps=60,
              kind="out_cubic", on_step=None, on_done=None):
        self.stop(key)
        n = max(int(duration * fps), 1)
        state = {"i": 0}
        widget = self.widget

        def _step():
            if not self._is_alive():
                self._jobs.pop(key, None)
                return

            t = state["i"] / n
            v = lerp(from_, to, ease(t, kind))
            if isinstance(from_, str) and from_.startswith("#"):
                v = lerp_color(from_, to, ease(t, kind))
            if on_step:
                try: on_step(v)
                except Exception: pass
            state["i"] += 1
            if state["i"] <= n:
                try:
                    self._jobs[key] = widget.after(int(1000 / fps), _step)
                except Exception:
                    self._jobs.pop(key, None)
            else:
                self._jobs.pop(key, None)
                if on_done:
                    try: on_done()
                    except Exception: pass

        _step()

    def color(self, key, widget_or_fn, from_, to, duration=0.3, fps=60, kind="out_cubic"):
        target = widget_or_fn if hasattr(widget_or_fn, "configure") else None
        setter = widget_or_fn if callable(widget_or_fn) and target is None else None

        def step(c):
            if target is not None:
                try: target.configure(bg=c)
                except Exception: pass
            elif setter: setter(c)

        self.tween(key, from_, to, duration, fps, kind, on_step=step)

    def pulse(self, key, widget_or_fn, base_color, peak_color="#ffffff",
              duration=0.6, fps=60, cycles=1, on_done=None):
        self.stop(key)
        total = int(duration * fps)
        state = {"i": 0}
        target = widget_or_fn if hasattr(widget_or_fn, "configure") else None
        setter = widget_or_fn if callable(widget_or_fn) and target is None else None

        def _set(c):
            if target is not None:
                try: target.configure(bg=c)
                except Exception: pass
            elif setter: setter(c)

        def _step():
            if not self._is_alive():
                self._jobs.pop(key, None)
                return

            t = state["i"] / max(total, 1)
            k = 0.5 + 0.5 * math.sin(t * math.pi * 2 * cycles)
            _set(lerp_color(base_color, peak_color, k))
            state["i"] += 1
            if state["i"] <= total:
                try:
                    self._jobs[key] = self.widget.after(int(1000 / fps), _step)
                except Exception:
                    self._jobs.pop(key, None)
            else:
                _set(base_color)
                self._jobs.pop(key, None)
                if on_done:
                    try: on_done()
                    except Exception: pass

        _step()

    def sequence(self, steps, on_done=None):
        it = iter(steps)
        def _next():
            if not self._is_alive(): return
            try: s = next(it)
            except StopIteration:
                if on_done:
                    try: on_done()
                    except Exception: pass
                return
            if isinstance(s, tuple) and callable(s[1]):
                try:
                    self.widget.after(int(s[0] * 1000), s[1])
                    self.widget.after(int(s[0] * 1000) + 1, _next)
                except Exception: pass
                return
            key = s.get("key", f"seq{id(s)}")
            done = s.get("on_done")
            s2 = dict(s)
            s2["key"] = key
            s2["on_done"] = lambda: (done() if done else None, _next())
            self.tween(**s2)
        _next()


def animate(widget, key, from_, to, **kw):
    Animator(widget).tween(key, from_, to, **kw)

def sequence(widget, steps, on_done=None):
    Animator(widget).sequence(steps, on_done=on_done)

def fade_in_after(widget, delay=0, step_ms=16, duration=0.4, kind="out_cubic"):
    try: widget.attributes("-alpha", 0.0)
    except Exception: return
    anim = Animator(widget)
    anim.tween("alpha", 0.0, 1.0, duration=duration, fps=60, kind=kind,
               on_step=lambda v: widget.attributes("-alpha", v))

def fade_out_destroy(widget, duration=0.35, on_done=None):
    anim = Animator(widget)
    target = 0.02
    def _done():
        try: widget.destroy()
        except Exception: pass
        if on_done: on_done()
    anim.tween("alpha", 1.0, target, duration=duration, fps=60,
               kind="in_out_sine",
               on_step=lambda v: widget.attributes("-alpha", v),
               on_done=_done)