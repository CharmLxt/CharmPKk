"""Генерация ANSI-графики и живописи прямо в консоли."""
import random
import math
import shutil
from .colors import RESET, fg_hex, bg_hex

class PixelCanvas:
    """Холст для рисования ANSI-графики (попиксельно)."""
    def __init__(self, width=80, height=24):
        self.w = width
        self.h = height
        self.buf = [[' ' for _ in range(width)] for _ in range(height)]
        self.colors = [[None for _ in range(width)] for _ in range(height)]

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.buf[y][x] = '█'
            self.colors[y][x] = color

    def render(self) -> str:
        out = []
        for y in range(self.h):
            row = []
            last_color = None
            for x in range(self.w):
                ch = self.buf[y][x]
                c = self.colors[y][x]
                if c != last_color:
                    row.append(RESET)
                    if c:
                        row.append(fg_hex(c))
                    last_color = c
                row.append(ch)
            row.append(RESET)
            out.append("".join(row))
        return "\n".join(out)

def _lerp_color(c1, c2, t):
    """Смешивает два hex-цвета. Исправлен баг с float."""
    from .colors import _hex_to_rgb, _rgb_to_hex
    a, b = _hex_to_rgb(c1), _hex_to_rgb(c2)
    # Явно приводим к int, чтобы избежать ValueError: Unknown format code 'x'
    rgb = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return _rgb_to_hex(rgb)

def render_sunset(width=None, height=None) -> str:
    if not width or not height:
        size = shutil.get_terminal_size((80, 24))
        width = size.columns - 1
        height = size.lines - 2

    canvas = PixelCanvas(width, height)
    horizon = int(height * 0.45)
    sun_cx = width // 2
    sun_cy = horizon
    sun_r = int(height * 0.3)

    # 1. Небо
    for y in range(horizon):
        t = y / max(1, horizon)
        color = _lerp_color("#7aa2ff", "#ff6b00", t)
        for x in range(width):
            canvas.put(x, y, color)

    # 2. Солнце
    for y in range(sun_cy - sun_r, sun_cy + 1):
        for x in range(sun_cx - sun_r, sun_cx + sun_r + 1):
            if (x - sun_cx)**2 + (y - sun_cy)**2 <= sun_r**2:
                canvas.put(x, y, "#ffea00")

    # 3. Вода
    for y in range(horizon, height):
        t = (y - horizon) / max(1, height - horizon)
        color = _lerp_color("#ff9a9e", "#000022", t)
        for x in range(width):
            canvas.put(x, y, color)
            if abs(x - sun_cx) < sun_r and random.random() < 0.15 * (1 - t):
                canvas.put(x, y, "#ffffff")

    # 4. Горы
    for x in range(width):
        if x < width * 0.35:
            mx = x / (width * 0.35)
            mh = int((height * 0.8) * (1 - mx)**2 + height * 0.1 * random.random())
            for y in range(height - mh, height):
                canvas.put(x, y, "#000000")
        if x > width * 0.65:
            mx = (width - x) / (width * 0.35)
            mh = int((height * 0.7) * (1 - mx)**2 + height * 0.1 * random.random())
            for y in range(height - mh, height):
                canvas.put(x, y, "#000000")

    return canvas.render()

def render_starry_night(width=None, height=None) -> str:
    if not width or not height:
        size = shutil.get_terminal_size((80, 24))
        width = size.columns - 1
        height = size.lines - 2

    canvas = PixelCanvas(width, height)

    for y in range(height):
        t = y / max(1, height)
        color = _lerp_color("#000022", "#0f1a24", t)
        for x in range(width):
            canvas.put(x, y, color)

    for _ in range(int(width * height * 0.05)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        brightness = random.choice(["#ffffff", "#e6e9f0", "#fde68a", "#7aa2ff"])
        canvas.put(x, y, brightness)

    mx, my = int(width * 0.8), int(height * 0.2)
    mr = int(height * 0.15)
    for y in range(my - mr, my + mr + 1):
        for x in range(mx - mr, mx + mr + 1):
            if (x - mx)**2 + (y - my)**2 <= mr**2:
                canvas.put(x, y, "#fdf6e3")

    for y in range(int(height * 0.85), height):
        for x in range(width):
            canvas.put(x, y, "#000000")
            if random.random() < 0.02:
                canvas.put(x, y, "#ff6b00")

    return canvas.render()