"""Live — плавно обновляемый блок контента в терминале."""
import sys
import time


class Live:
    """Перерисовывает многострочный блок на месте."""

    def __init__(self, stream=sys.stdout):
        self.stream = stream
        self._lines = 0
        self._first = True
        try:
            self._is_tty = self.stream.isatty()
        except Exception:
            self._is_tty = False

    def update(self, content):
        if not isinstance(content, str):
            content = "\n".join(str(x) for x in content)
            
        if not self._is_tty:
            print(content)
            return

        lines = content.split("\n")

        if not self._first:
            self.stream.write(f"\033[{self._lines}A")
        
        max_lines = max(self._lines, len(lines))
        for i in range(max_lines):
            self.stream.write("\033[2K")
            if i < len(lines):
                self.stream.write(lines[i])
            self.stream.write("\n")
            
        if max_lines > len(lines):
            self.stream.write(f"\033[{max_lines - len(lines)}A")

        self._lines = len(lines)
        self._first = False
        self.stream.flush()

    def clear(self):
        if not self._is_tty: return
        if self._lines:
            self.stream.write(f"\033[{self._lines}A")
            for _ in range(self._lines):
                self.stream.write("\033[2K\n")
            self.stream.write(f"\033[{self._lines}A")
            self.stream.flush()
        self._lines = 0
        self._first = True

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self._is_tty:
            self.stream.write("\n")
            self.stream.flush()
        return False


def animate_to(live, frames, fps=30):
    dt = 1 / fps
    for frame in frames:
        live.update(frame)
        time.sleep(dt)