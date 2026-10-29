"""Красивые элементы интерфейса для установщиков."""
import sys
import time

from .colors import colorize, fg_hex, BOLD, DIM
from .boxes import box
from .decor import gradient_bar

DEFAULT_ACCENT = "#7aa2ff"


def install_header(name, version="1.0.0", subtitle="Installation Wizard", accent=DEFAULT_ACCENT):
    """Красивый заголовок установщика в стиле 'двойная рамка'."""
    print()
    title = f"  {name} v{version}  "
    width = len(title) + 4
    top = "╔" + "═" * width + "╗"
    mid = "║" + title.center(width) + "║"
    bot = "╚" + "═" * width + "╝"
    print(colorize(top, fg=fg_hex(accent), style=BOLD))
    print(colorize(mid, fg=fg_hex(accent), style=BOLD))
    print(colorize(bot, fg=fg_hex(accent), style=BOLD))
    print(colorize(f"  {subtitle}", fg=fg_hex(accent), style=DIM))
    print()


def install_step(current, total, name, accent=DEFAULT_ACCENT):
    """Рисует строку шага установки с иконкой."""
    if current < 1:
        icon = colorize("○", fg=fg_hex("#8b93a7"))
    elif current >= total:
        icon = colorize("✔", fg=fg_hex("#22c55e"), style=BOLD)
    else:
        icon = colorize("◆", fg=fg_hex(accent), style=BOLD)
    tag = colorize(f"[{current}/{total}]", fg=fg_hex(accent), style=BOLD)
    print(f"  {icon} {tag} {name}")


def install_progress(value, total=100, label="", gradient=("#7aa2ff", "#22c55e"), width=50, newline=False):
    """Красивый прогресс-бар с градиентом, обновляется в одной строке."""
    bar = gradient_bar(value, total=total, width=width, colors=gradient)
    prefix = label.ljust(20) if label else ""
    sys.stdout.write("\r  " + prefix + " " + bar)
    if newline:
        sys.stdout.write("\n")
    sys.stdout.flush()


def animated_progress(duration=3.0, fps=30, label="Installing", gradient=("#7aa2ff", "#22c55e"), width=50):
    """Прогресс, который плавно заполняется со временем."""
    frames = int(duration * fps)
    for f in range(frames + 1):
        pct = int(f / frames * 100)
        install_progress(pct, total=100, label=label, gradient=gradient, width=width)
        time.sleep(1 / fps)
    sys.stdout.write("\n")
    sys.stdout.flush()


def install_rocket(duration=2.0, fps=20, width=60, accent=DEFAULT_ACCENT):
    """Анимация взлетающей ракеты."""
    frames = int(duration * fps)
    for f in range(frames):
        progress = f / frames
        pos = int(progress * (width - 12))
        flame = ["*", "**", "***", "****"][f % 4]
        line = " " * pos + "🚀" + flame
        sys.stdout.write("\r" + colorize(line.ljust(width), fg=fg_hex(accent)))
        sys.stdout.flush()
        time.sleep(1 / fps)
    sys.stdout.write("\n")
    sys.stdout.flush()


def install_gears(duration=2.0, fps=10, text="Установка", accent=DEFAULT_ACCENT):
    """Вращающиеся шестерёнки во время установки."""
    gears = ["⚙️ ", "⚙️ ⚙️ ", "⚙️  ⚙️", " ⚙️ ⚙️", "⚙️ ⚙️ ", " ⚙️ ⚙️"]
    frames = int(duration * fps)
    for f in range(frames):
        gear = gears[f % len(gears)]
        line = f"  {gear} {text}..."
        sys.stdout.write("\r" + colorize(line.ljust(50), fg=fg_hex(accent)))
        sys.stdout.flush()
        time.sleep(1 / fps)
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()


def install_complete(stats=None, accent="#22c55e"):
    """Красивый экран завершения установки с опциональной статистикой."""
    print()
    print(colorize("  ╔═══════════════════════════════════════════╗", fg=fg_hex(accent)))
    print(colorize("  ║       ✔   УСТАНОВКА ЗАВЕРШЕНА   ✔         ║", fg=fg_hex(accent), style=BOLD))
    print(colorize("  ╚═══════════════════════════════════════════╝", fg=fg_hex(accent)))
    if stats:
        print()
        for key, value in stats.items():
            print(f"  {colorize(str(key) + ':', fg=fg_hex('#8b93a7'))} {value}")
    print()


def install_warning(message, accent="#f59e0b"):
    """Оформленное предупреждение."""
    print()
    print(box(message, title="⚠  Внимание", style="round", border_fg=fg_hex(accent)))


def install_error(message, accent="#ef4444"):
    """Оформленная ошибка."""
    print()
    print(box(message, title="✖  Ошибка", style="round", border_fg=fg_hex(accent)))


def install_success(message, accent="#22c55e"):
    """Оформленный успех."""
    print()
    print(box(message, title="✔  Успех", style="round", border_fg=fg_hex(accent)))


def install_wizard(steps, on_step=None, accent=DEFAULT_ACCENT):
    """
    Полноценный интерактивный установщик.
    steps — список (name, callback). callback(i) выполняет работу и возвращает (success, message).
    """
    total = len(steps)
    print()
    install_header("Установка", subtitle=f"{total} шагов", accent=accent)
    for i, (name, callback) in enumerate(steps, 1):
        install_step(i, total, name, accent=accent)
        try:
            success, message = callback(i)
            if success:
                print(f"      {colorize('✔', fg=fg_hex('#22c55e'))} {message}")
            else:
                install_error(message)
                return False
        except Exception as e:
            install_error(f"{type(e).__name__}: {e}")
            return False
    install_complete()
    return True


def demo():
    """Демонстрация всех красивых элементов установщика."""
    from ..console import ask
    install_header("MyApp", "2.0.0", "Красивая установка")
    ask("Нажмите Enter, чтобы начать")
    install_gears(duration=1.5, text="Подготовка")
    animated_progress(duration=2.0, label="Копирование")
    animated_progress(duration=1.5, label="Распаковка", gradient=("#f59e0b", "#ef4444"))
    install_rocket(duration=2.0)
    install_complete(stats={
        "Установлено файлов": 42,
        "Размер": "12.4 MB",
        "Время": "5 сек",
    })


if __name__ == "__main__":
    demo()