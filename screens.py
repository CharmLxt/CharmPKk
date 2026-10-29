"""Роутер экранов (SPA-подобная навигация по одному окну)."""
import tkinter as tk


class Screen:
    """Базовый экран. Переопределите build(parent, ctx)."""
    name = "screen"

    def __init__(self, app=None, ctx=None):
        self.app = app
        self.ctx = ctx or {}
        self.frame = None

    def build(self, parent, ctx):
        """Создать содержимое и вернуть виджет."""
        raise NotImplementedError

    def on_enter(self):
        pass

    def on_exit(self):
        pass


class Router:
    """Хранит экраны и переключает их с плавным crossfade."""

    def __init__(self, container, theme, app=None):
        self.container = container
        self.theme = theme
        self.app = app
        self.screens = {}
        self.current = None
        self.history = []

    def register(self, name, screen_cls):
        self.screens[name] = screen_cls

    def go(self, name, ctx=None, remember=True):
        cls = self.screens.get(name)
        if not cls:
            raise KeyError(f"Экран '{name}' не зарегистрирован")

        if self.current is not None:
            self.current.on_exit()
            if remember:
                self.history.append(self.current.name)
            for w in self.container.winfo_children():
                w.destroy()

        screen = cls(app=self.app, ctx=ctx or {})
        screen.name = name
        frame = screen.build(self.container, screen.ctx)
        if frame is None:
            frame = self.container
        self.current = screen
        screen.on_enter()
        return screen

    def back(self, ctx=None):
        if not self.history:
            return None
        name = self.history.pop()
        return self.go(name, ctx=ctx, remember=False)