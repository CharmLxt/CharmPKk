"""Расширенные прогресс-бары: braille, dots, blocks, gradient animated, TaskList."""
import math
import sys
import threading
import time

from .colors import colorize, fg_hex, fg_rgb, RESET, _hex_to_rgb, _lerp
from .text import visible_len


_BRAILLE = "⠀⠁⠂⠃⠄⠅⠆⠇⡀⡁⡂⡃⡄⡅⡆⡇⠈⠉⠊⠋⠌⠍⠎⠏⡈⡉⡊⡋⡌⡍⡎⡏⠐⠑⠒⠓⠔⠕⠖⠗⡐⡑⡒⡓⡔⡕⡖⡗⠘⠙⠚⠛⠜⠝⠞⠟⡘⡙⡚⡛⡜⡝⡞⡟⠠⠡⠢⠣⠤⠥⠦⠧⡠⡡⡢⡣⡤⡥⡦⡧⠨⠩⠪⠫⠬⠭⠮⠯⡨⡩⡪⡫⡬⡭⡮⡯⠰⠱⠲⠳⠴⠵⠶⠷⡰⡱⡲⡳⡴⡵⡶⡷⠸⠹⠺⠻⠼⠽⠾⠿⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃⢄⢅⢆⢇⣀⣁⣂⣃⣄⣅⣆⣇⢈⢉⢊⢋⢌⢍⢎⢏⣈⣉⣊⣋⣌⣍⣎⣏⢐⢑⢒⢓⢔⢕⢖⢗⣐⣑⣒⣓⣔⣕⣖⣗⢘⢙⢚⢛⢜⢝⢞⢟⣘⣙⣚⣛⣜⣝⣞⣟⢠⢡⢢⢣⢤⢥⢦⢧⣠⣡⣢⣣⣤⣥⣦⣧⢨⢩⢪⢫⢬⢭⢮⢯⣨⣩⣪⣫⣬⣭⣮⣯⢰⢱⢲⢳⢴⢵⢶⢷⣰⣱⣲⣳⣴⣵⣶⣷⢸⢹⢺⢻⢼⢽⢾⢿⣸⣹⣺⣻⣼⣽⣾⣿"


class FancyProgressBar:
    """Прогресс-бар с настраиваемым стилем: block, line, dots, braille, stars."""

    STYLES = {
        "block":   ("█", "░"),
        "line":    ("━", "─"),
        "dots":    ("●", "○"),
        "star":    ("★", "☆"),
        "arrow":   ("=", "-"),
        "square":  ("■", "□"),
        "shade":   ("▓", "░"),
        "braille": ("⣿", "⠀"),
        "heart":   ("♥", "♡"),
    }

    def __init__(self, total=100, width=40, style="block", fg=None,
                 gradient=None, label="", show_percent=True, show_count=False,
                 brackets=("[", "]"), pulse=False):
        self.total = total or 1
        self.width = width
        self.fg = fg
        self.gradient = gradient
        self.label = label
        self.show_percent = show_percent
        self.show_count = show_count
        self.brackets = brackets
        self.pulse = pulse
        self.filled, self.empty = self.STYLES.get(style, self.STYLES["block"])

    def render(self, current):
        ratio = max(0, min(current / self.total, 1))
        n = int(ratio * self.width)
        filled = self.filled * n
        empty = self.empty * (self.width - n)

        if self.gradient:
            s = _hex_to_rgb(self.gradient[0])
            e = _hex_to_rgb(self.gradient[1])
            chars = []
            for i, ch in enumerate(filled):
                c = _lerp(s, e, i / max(len(filled) - 1, 1))
                chars.append(f"{fg_rgb(*c)}{ch}")
            filled = "".join(chars) + RESET
        elif self.fg:
            filled = colorize(filled, fg=self.fg)

        if self.fg:
            empty = colorize(empty, fg=self.fg)

        body = f"{self.brackets[0]}{filled}{empty}{self.brackets[1]}"
        pre = f"{self.label} " if self.label else ""
        suf = ""
        if self.show_percent:
            suf += f" {ratio * 100:5.1f}%"
        if self.show_count:
            suf += f" ({current}/{self.total})"
        return f"{pre}{body}{suf}"

    def update(self, current):
        if not sys.stdout.isatty(): return
        sys.stdout.write("\r" + self.render(current))
        sys.stdout.flush()

    def finish(self, message=None):
        if not sys.stdout.isatty(): return
        sys.stdout.write("\r" + (message + "\n" if message else "\n"))
        sys.stdout.flush()

    def __enter__(self): return self
    def __exit__(self, *exc): self.finish()


class AnimatedProgressBar(FancyProgressBar):
    """Плавно "догоняет" целевое значение при update()."""

    def __init__(self, *a, smooth=True, speed=6.0, fps=60, **kw):
        super().__init__(*a, **kw)
        self._current = 0.0
        self._target = 0.0
        self.smooth = smooth
        self.speed = speed
        self.fps = fps
        self._stop = threading.Event()
        self._t = None

    def start(self):
        self._stop.clear()
        self._t = threading.Thread(target=self._loop, daemon=True)
        self._t.start()
        return self

    def update(self, current):
        self._target = current
        if not self.smooth:
            self._current = current
            super().update(self._current)

    def set(self, current):
        self._target = current

    def _loop(self):
        if not sys.stdout.isatty(): return
        dt = 1 / self.fps
        while not self._stop.is_set():
            diff = self._target - self._current
            if abs(diff) < 0.01:
                self._current = self._target
            else:
                self._current += diff * min(1.0, self.speed * dt)
            sys.stdout.write("\r" + self.render(int(round(self._current))))
            sys.stdout.flush()
            time.sleep(dt)

    def stop(self, message=None):
        self._stop.set()
        if self._t:
            self._t.join()
        if not sys.stdout.isatty(): return
        sys.stdout.write("\r")
        if message:
            sys.stdout.write(message + "\n")
        else:
            sys.stdout.write(self.render(int(self._target)) + "\n")
        sys.stdout.flush()


class TaskList:
    """Список задач с независимыми состояниями (в стиле CI)."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"

    ICONS = {
        PENDING: "○",
        RUNNING: "◐",
        DONE: "✔",
        FAILED: "✖",
        SKIPPED: "→",
    }
    COLORS = {
        PENDING: "#8b93a7",
        RUNNING: "#7aa2ff",
        DONE: "#22c55e",
        FAILED: "#ef4444",
        SKIPPED: "#f59e0b",
    }

    def __init__(self, tasks):
        self.tasks = [(t, self.PENDING) for t in tasks]
        self._lines = 0

    def set(self, name, state):
        for i, (t, _) in enumerate(self.tasks):
            if t == name:
                self.tasks[i] = (t, state)
                break
        self._draw()

    def _draw(self):
        if not sys.stdout.isatty(): return
        if self._lines:
            sys.stdout.write(f"\033[{self._lines}A")
        for t, s in self.tasks:
            icon = colorize(self.ICONS[s], fg=fg_hex(self.COLORS[s]))
            line = f"{icon} {t}"
            sys.stdout.write(line + "\033[K\n")
        self._lines = len(self.tasks)
        sys.stdout.flush()

    def start(self):
        self._draw()
        return self

    def done(self):
        if not sys.stdout.isatty(): return
        sys.stdout.write("\n")
        sys.stdout.flush()