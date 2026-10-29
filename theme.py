"""Темы для оконного режима."""

class Theme:
    def __init__(self, bg, surface, surface2, fg, muted, accent, accent_fg,
                 border, danger="#e06c75", success="#22c55e", warning="#f59e0b",
                 info="#3b82f6", font="Segoe UI", font_size=11,
                 mono_font="Consolas", mono_size=10, radius=8):
        self.bg = bg; self.surface = surface; self.surface2 = surface2
        self.fg = fg; self.muted = muted; self.accent = accent
        self.accent_fg = accent_fg; self.border = border
        self.danger = danger; self.success = success
        self.warning = warning; self.info = info
        self.font = font; self.font_size = font_size
        self.mono_font = mono_font; self.mono_size = mono_size
        self.radius = radius

    @classmethod
    def dark(cls):
        return cls(bg="#11131a", surface="#1b1e28", surface2="#242836",
                   fg="#e6e9f0", muted="#8b93a7", accent="#7aa2ff",
                   accent_fg="#0b0d14", border="#2a2f3d")
    @classmethod
    def light(cls):
        return cls(bg="#f6f7fb", surface="#ffffff", surface2="#eef1f8",
                   fg="#1a1d26", muted="#6b7280", accent="#3355ff",
                   accent_fg="#ffffff", border="#e3e6ee")
    @classmethod
    def nord(cls):
        return cls(bg="#2e3440", surface="#3b4252", surface2="#434c5e",
                   fg="#eceff4", muted="#8fa1b3", accent="#88c0d0",
                   accent_fg="#2e3440", border="#4c566a")
    @classmethod
    def gruvbox(cls):
        return cls(bg="#282828", surface="#3c3836", surface2="#504945",
                   fg="#ebdbb2", muted="#a89984", accent="#fabd2f",
                   accent_fg="#282828", border="#504945")
    @classmethod
    def dracula(cls):
        return cls(bg="#282a36", surface="#44475a", surface2="#52556b",
                   fg="#f8f8f2", muted="#6272a4", accent="#bd93f9",
                   accent_fg="#282a36", border="#44475a",
                   danger="#ff5555", success="#50fa7b", warning="#f1fa8c", info="#8be9fd")
    @classmethod
    def tokyo_night(cls):
        return cls(bg="#1a1b26", surface="#24283b", surface2="#2f334d",
                   fg="#c0caf5", muted="#565f89", accent="#7aa2f7",
                   accent_fg="#1a1b26", border="#2f334d",
                   danger="#f7768e", success="#9ece6a", warning="#e0af68", info="#7dcfff")
    @classmethod
    def catppuccin(cls):
        return cls(bg="#1e1e2e", surface="#313244", surface2="#45475a",
                   fg="#cdd6f4", muted="#7f849c", accent="#cba6f7",
                   accent_fg="#1e1e2e", border="#45475a",
                   danger="#f38ba8", success="#a6e3a1", warning="#f9e2af", info="#89b4fa")
    @classmethod
    def solarized_dark(cls):
        return cls(bg="#002b36", surface="#073642", surface2="#0d4b5c",
                   fg="#93a1a1", muted="#586e75", accent="#268bd2",
                   accent_fg="#fdf6e3", border="#073642",
                   danger="#dc322f", success="#859900", warning="#b58900", info="#268bd2")
    @classmethod
    def solarized_light(cls):
        return cls(bg="#fdf6e3", surface="#eee8d5", surface2="#e5ddc8",
                   fg="#073642", muted="#93a1a1", accent="#268bd2",
                   accent_fg="#fdf6e3", border="#eee8d5",
                   danger="#dc322f", success="#859900", warning="#b58900", info="#268bd2")
    @classmethod
    def monokai(cls):
        return cls(bg="#272822", surface="#3e3d32", surface2="#4b4a3d",
                   fg="#f8f8f2", muted="#75715e", accent="#a6e22e",
                   accent_fg="#272822", border="#3e3d32",
                   danger="#f92672", success="#a6e22e", warning="#e6db74", info="#66d9ef")
    @classmethod
    def cyberpunk(cls):
        return cls(bg="#000b14", surface="#071a26", surface2="#0d2838",
                   fg="#e0f8ff", muted="#6e8a9e", accent="#00ffcc",
                   accent_fg="#000b14", border="#1a3b4c",
                   danger="#ff003c", success="#39ff14", warning="#fffc00", info="#00b3ff")
    @classmethod
    def monochrome(cls):
        return cls(bg="#121212", surface="#1e1e1e", surface2="#2a2a2a",
                   fg="#f5f5f5", muted="#888888", accent="#ffffff",
                   accent_fg="#121212", border="#333333",
                   danger="#666666", success="#aaaaaa", warning="#cccccc", info="#dddddd")
    @classmethod
    def retro(cls):
        return cls(bg="#001100", surface="#002200", surface2="#003300",
                   fg="#00ff00", muted="#008800", accent="#33ff33",
                   accent_fg="#001100", border="#003300",
                   danger="#ff3300", success="#66ff33", warning="#ccff00", info="#00ccff")
    @classmethod
    def sunset(cls):
        return cls(bg="#2d1b4e", surface="#3d2b5e", surface2="#4d3b6e",
                   fg="#ffe9c4", muted="#9a7cae", accent="#ff6b6b",
                   accent_fg="#2d1b4e", border="#5a3d7a",
                   danger="#ff5252", success="#4ecdc4", warning="#ffe66d", info="#95e1d3")
    @classmethod
    def forest(cls):
        return cls(bg="#1a2f1a", surface="#2a3f2a", surface2="#3a4f3a",
                   fg="#d4e8c2", muted="#6b8a5f", accent="#a7c957",
                   accent_fg="#1a2f1a", border="#3a5a3a",
                   danger="#bc4749", success="#6a994e", warning="#e9c46a", info="#4a7c59")
    @classmethod
    def vaporwave(cls):
        return cls(bg="#1a0033", surface="#2a1043", surface2="#3a2053",
                   fg="#ffe4f3", muted="#b85b8c", accent="#ff71ce",
                   accent_fg="#1a0033", border="#4a1a6b",
                   danger="#ff0055", success="#01cdfe", warning="#fffb96", info="#05ffa1")
    @classmethod
    def sakura(cls):
        return cls(bg="#1a1218", surface="#251a20", surface2="#30222a",
                   fg="#f5e6ec", muted="#a68d97", accent="#ffb7c5",
                   accent_fg="#1a1218", border="#3a2a32",
                   danger="#ff6b8b", success="#98e4b4", warning="#ffd59e", info="#9ecfff")
    @classmethod
    def coffee(cls):
        return cls(bg="#1e1714", surface="#2a201c", surface2="#382a24",
                   fg="#f0e6d2", muted="#9e8a7a", accent="#c49a6c",
                   accent_fg="#1e1714", border="#3b2e26",
                   danger="#d96c6c", success="#a3c293", warning="#e2b86e", info="#8fbcd4")
    @classmethod
    def matrix(cls):
        return cls(bg="#0a0f0a", surface="#101810", surface2="#182218",
                   fg="#c4ffc4", muted="#4d7a4d", accent="#00ff41",
                   accent_fg="#0a0f0a", border="#143014",
                   danger="#ff4141", success="#00ff41", warning="#c4ff00", info="#00ffcc")
    @classmethod
    def ocean(cls):
        return cls(bg="#0f1a24", surface="#172633", surface2="#1f3344",
                   fg="#d0e8f5", muted="#6a95b0", accent="#4cc9f0",
                   accent_fg="#0f1a24", border="#1c3040",
                   danger="#ef476f", success="#06d6a0", warning="#ffd166", info="#118ab2")
    @classmethod
    def vampire(cls):
        return cls(bg="#140a0f", surface="#1f1018", surface2="#2b1620",
                   fg="#e8d0d8", muted="#9a6a75", accent="#ff0055",
                   accent_fg="#140a0f", border="#2b1520",
                   danger="#ff3355", success="#a8e6cf", warning="#ffe0a3", info="#a084d1")
    @classmethod
    def acrylic(cls):
        return cls(bg="#14161c", surface="#1d2029", surface2="#282c38",
                   fg="#e8ebf2", muted="#8b93a7", accent="#a0b4ff",
                   accent_fg="#0b0d14", border="#2e3342",
                   danger="#f87171", success="#4ade80", warning="#fbbf24", info="#60a5fa")
    @classmethod
    def liquid_glass(cls):
        return cls(bg="#0f1117", surface="#1a1d26", surface2="#252936",
                   fg="#eef1f8", muted="#9aa3b5", accent="#8ab4ff",
                   accent_fg="#0b0d14", border="#3b4254",
                   danger="#fb7185", success="#6ee7b7", warning="#fcd34d", info="#7dd3fc")

    def copy(self, **overrides):
        data = dict(self.__dict__); data.update(overrides)
        return Theme(**data)

    def tk_font(self, size_delta=0, weight="normal"):
        return (self.font, self.font_size + size_delta, weight)

    def tk_mono(self, size_delta=0, weight="normal"):
        return (self.mono_font, self.mono_size + size_delta, weight)


class ThemeManager:
    _registry = {
        "dark": Theme.dark, "light": Theme.light, "nord": Theme.nord,
        "gruvbox": Theme.gruvbox, "dracula": Theme.dracula,
        "tokyo_night": Theme.tokyo_night, "catppuccin": Theme.catppuccin,
        "solarized_dark": Theme.solarized_dark, "solarized_light": Theme.solarized_light,
        "monokai": Theme.monokai, "cyberpunk": Theme.cyberpunk,
        "monochrome": Theme.monochrome, "retro": Theme.retro,
        "sunset": Theme.sunset, "forest": Theme.forest, "vaporwave": Theme.vaporwave,
        "sakura": Theme.sakura, "coffee": Theme.coffee, "matrix": Theme.matrix,
        "ocean": Theme.ocean, "vampire": Theme.vampire,
        "acrylic": Theme.acrylic, "liquid_glass": Theme.liquid_glass,
    }
    def __init__(self, current="dark"):
        self._current = self._registry.get(current, Theme.dark)()
    @classmethod
    def register(cls, name, factory): cls._registry[name] = factory
    @classmethod
    def list(cls): return list(cls._registry.keys())
    @classmethod
    def get(cls, name):
        factory = cls._registry.get(name)
        return factory() if factory else None
    @property
    def current(self): return self._current
    def set(self, name):
        t = self.get(name)
        if t: self._current = t
        return self._current