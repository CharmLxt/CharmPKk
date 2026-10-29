"""Готовые цветовые палитры для консоли."""

class Palette:
    def __init__(self, bg, fg, muted, accent, success, warning, danger, info,
                 border, surface=None, surface2=None, accent_fg=None, name="custom"):
        self.bg = bg
        self.fg = fg
        self.muted = muted
        self.accent = accent
        self.success = success
        self.warning = warning
        self.danger = danger
        self.info = info
        self.border = border
        self.surface = surface or border
        self.surface2 = surface2 or border
        self.accent_fg = accent_fg or bg
        self.name = name

    def __getitem__(self, k):
        return getattr(self, k)

    def __repr__(self):
        return f"<Palette {self.name}>"

dark = Palette(bg="#0b0d14", fg="#e6e9f0", muted="#8b93a7",
               accent="#7aa2ff", success="#22c55e", warning="#f59e0b",
               danger="#ef4444", info="#3b82f6", border="#2a2f3d", name="dark")
light = Palette(bg="#f6f7fb", fg="#1a1d26", muted="#6b7280",
                accent="#3355ff", success="#16a34a", warning="#d97706",
                danger="#dc2626", info="#2563eb", border="#d1d5db", name="light")
nord = Palette(bg="#2e3440", fg="#eceff4", muted="#8fa1b3",
               accent="#88c0d0", success="#a3be8c", warning="#ebcb8b",
               danger="#bf616a", info="#81a1c1", border="#4c566a", name="nord")
dracula = Palette(bg="#282a36", fg="#f8f8f2", muted="#6272a4",
                  accent="#bd93f9", success="#50fa7b", warning="#f1fa8c",
                  danger="#ff5555", info="#8be9fd", border="#44475a", name="dracula")
gruvbox = Palette(bg="#282828", fg="#ebdbb2", muted="#a89984",
                  accent="#fabd2f", success="#b8bb26", warning="#fabd2f",
                  danger="#fb4934", info="#83a598", border="#504945", name="gruvbox")
tokyo_night = Palette(bg="#1a1b26", fg="#c0caf5", muted="#565f89",
                      accent="#7aa2f7", success="#9ece6a", warning="#e0af68",
                      danger="#f7768e", info="#7dcfff", border="#2f334d", name="tokyo_night")
catppuccin = Palette(bg="#1e1e2e", fg="#cdd6f4", muted="#7f849c",
                     accent="#cba6f7", success="#a6e3a1", warning="#f9e2af",
                     danger="#f38ba8", info="#89b4fa", border="#45475a", name="catppuccin")
monokai = Palette(bg="#272822", fg="#f8f8f2", muted="#75715e",
                  accent="#a6e22e", success="#a6e22e", warning="#e6db74",
                  danger="#f92672", info="#66d9ef", border="#3e3d32", name="monokai")
cyberpunk = Palette(bg="#000b14", fg="#e0f8ff", muted="#6e8a9e",
                    accent="#00ffcc", success="#39ff14", warning="#fffc00",
                    danger="#ff003c", info="#00b3ff", border="#1a3b4c", name="cyberpunk")
monochrome = Palette(bg="#121212", fg="#f5f5f5", muted="#888888",
                     accent="#ffffff", success="#aaaaaa", warning="#cccccc",
                     danger="#666666", info="#dddddd", border="#333333", name="monochrome")
retro = Palette(bg="#001100", fg="#00ff00", muted="#008800",
                accent="#33ff33", success="#66ff33", warning="#ccff00",
                danger="#ff3300", info="#00ccff", border="#003300", name="retro")
sunset = Palette(bg="#2d1b4e", fg="#ffe9c4", muted="#9a7cae",
                 accent="#ff6b6b", success="#4ecdc4", warning="#ffe66d",
                 danger="#ff5252", info="#95e1d3", border="#5a3d7a", name="sunset")
forest = Palette(bg="#1a2f1a", fg="#d4e8c2", muted="#6b8a5f",
                 accent="#a7c957", success="#6a994e", warning="#e9c46a",
                 danger="#bc4749", info="#4a7c59", border="#3a5a3a", name="forest")
vaporwave = Palette(bg="#1a0033", fg="#ffe4f3", muted="#b85b8c",
                    accent="#ff71ce", success="#01cdfe", warning="#fffb96",
                    danger="#ff0055", info="#05ffa1", border="#4a1a6b", name="vaporwave")
acrylic = Palette(bg="#14161c", fg="#e8ebf2", muted="#8b93a7",
                  accent="#a0b4ff", success="#4ade80", warning="#fbbf24",
                  danger="#f87171", info="#60a5fa", border="#2e3342", name="acrylic")
liquid_glass = Palette(bg="#0f1117", fg="#eef1f8", muted="#9aa3b5",
                       accent="#8ab4ff", success="#6ee7b7", warning="#fcd34d",
                       danger="#fb7185", info="#7dd3fc", border="#3b4254", name="liquid_glass")

# Новые палитры
sakura = Palette(bg="#1a1218", fg="#f5e6ec", muted="#a68d97",
                 accent="#ffb7c5", success="#98e4b4", warning="#ffd59e",
                 danger="#ff6b8b", info="#9ecfff", border="#3a2a32", name="sakura")
coffee = Palette(bg="#1e1714", fg="#f0e6d2", muted="#9e8a7a",
                 accent="#c49a6c", success="#a3c293", warning="#e2b86e",
                 danger="#d96c6c", info="#8fbcd4", border="#3b2e26", name="coffee")
matrix = Palette(bg="#0a0f0a", fg="#c4ffc4", muted="#4d7a4d",
                 accent="#00ff41", success="#00ff41", warning="#c4ff00",
                 danger="#ff4141", info="#00ffcc", border="#143014", name="matrix")
ocean = Palette(bg="#0f1a24", fg="#d0e8f5", muted="#6a95b0",
                accent="#4cc9f0", success="#06d6a0", warning="#ffd166",
                danger="#ef476f", info="#118ab2", border="#1c3040", name="ocean")
vampire = Palette(bg="#140a0f", fg="#e8d0d8", muted="#9a6a75",
                  accent="#ff0055", success="#a8e6cf", warning="#ffe0a3",
                  danger="#ff3355", info="#a084d1", border="#2b1520", name="vampire")

REGISTRY = {
    "dark": dark, "light": light, "nord": nord, "dracula": dracula,
    "gruvbox": gruvbox, "tokyo_night": tokyo_night, "catppuccin": catppuccin,
    "monokai": monokai, "cyberpunk": cyberpunk, "monochrome": monochrome,
    "retro": retro, "sunset": sunset, "forest": forest, "vaporwave": vaporwave,
    "sakura": sakura, "coffee": coffee, "matrix": matrix, "ocean": ocean, "vampire": vampire,
    "acrylic": acrylic, "liquid_glass": liquid_glass,
}

def get(name):
    return REGISTRY.get(name, dark)

def list_names():
    return list(REGISTRY.keys())