"""Таблица с сортировкой, скроллом и выбором строки."""
import tkinter as tk


class TableView(tk.Frame):
    """Простая таблица с сортировкой по клику на заголовке.

    tv = TableView(parent, theme, columns=[("Имя", "name"), ("Возраст", "age")])
    tv.set_rows([{"name": "Anna", "age": 30}, ...])
    """

    def __init__(self, master, theme, columns, rows=None, height=10,
                 on_select=None, sortable=True, zebra=True,
                 column_widths=None):
        super().__init__(master, bg=theme.border)
        self.theme = theme
        self.columns = list(columns)  # [(title, key), ...]
        self.on_select = on_select
        self.sortable = sortable
        self.zebra = zebra
        self.column_widths = column_widths or [None] * len(self.columns)
        self._sort_key = None
        self._sort_desc = False
        self._selected = None
        self._wheel_bound = False

        body = tk.Frame(self, bg=theme.surface)
        body.pack(fill="both", expand=True, padx=1, pady=1)

        # header
        self._header = tk.Frame(body, bg=theme.surface2)
        self._header.pack(fill="x")
        self._header_labels = []
        for i, (title, key) in enumerate(self.columns):
            lb = tk.Label(self._header, text=title, bg=theme.surface2,
                          fg=theme.accent, font=theme.tk_font(0, "bold"),
                          anchor="w", padx=10, pady=8, cursor="hand2")
            if self.column_widths[i]:
                lb.configure(width=self.column_widths[i])
            lb.pack(side="left", fill="x",
                    expand=not bool(self.column_widths[i]))
            if self.sortable:
                lb.bind("<Button-1>", lambda e, k=key: self._sort_by(k))
            self._header_labels.append(lb)

        # scroll area
        wrap = tk.Frame(body, bg=theme.surface)
        wrap.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(wrap, bg=theme.surface, bd=0,
                                highlightthickness=0, height=height * 32)
        self.canvas.pack(side="left", fill="both", expand=True)

        sb = tk.Scrollbar(wrap, orient="vertical",
                          command=self.canvas.yview, bd=0)
        sb.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=sb.set)

        self.inner = tk.Frame(self.canvas, bg=theme.surface)
        self._win = self.canvas.create_window((0, 0), window=self.inner,
                                              anchor="nw")
        self.inner.bind("<Configure>",
                        lambda e: self.canvas.configure(
                            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>",
                         lambda e: self.canvas.itemconfigure(self._win,
                                                             width=e.width))

        # колесо мыши — только когда курсор над таблицей
        self.canvas.bind("<Enter>", self._bind_wheel)
        self.canvas.bind("<Leave>", self._unbind_wheel)
        self.bind("<Destroy>", self._on_destroy)

        self._rows_data = []
        self._row_widgets = []
        if rows:
            self.set_rows(rows)

    def _bind_wheel(self, _=None):
        if not self._wheel_bound:
            self.canvas.bind_all("<MouseWheel>", self._on_wheel)
            self._wheel_bound = True

    def _unbind_wheel(self, _=None):
        if self._wheel_bound:
            try:
                self.canvas.unbind_all("<MouseWheel>")
            except Exception:
                pass
            self._wheel_bound = False

    def _on_wheel(self, event):
        try:
            self.canvas.yview_scroll(int(-event.delta / 60), "units")
        except Exception:
            pass

    def _on_destroy(self, event):
        if event.widget is self:
            self._unbind_wheel()

    def set_rows(self, rows):
        self._rows_data = list(rows)
        self._render()

    def _sort_by(self, key):
        if not self.sortable:
            return
        if self._sort_key == key:
            self._sort_desc = not self._sort_desc
        else:
            self._sort_key = key
            self._sort_desc = False
        self._rows_data.sort(key=lambda r: r.get(key, ""),
                             reverse=self._sort_desc)
        self._update_header_indicators()
        self._render()

    def _update_header_indicators(self):
        for i, (title, key) in enumerate(self.columns):
            arrow = ""
            if self._sort_key == key:
                arrow = " ▼" if self._sort_desc else " ▲"
            self._header_labels[i].configure(text=title + arrow)

    def _render(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self._row_widgets.clear()

        for idx, row in enumerate(self._rows_data):
            bg = (self.theme.surface2 if (self.zebra and idx % 2)
                  else self.theme.surface)
            rw = tk.Frame(self.inner, bg=bg)
            rw.pack(fill="x")

            for i, (title, key) in enumerate(self.columns):
                cell = tk.Label(rw, text=str(row.get(key, "")), bg=bg,
                                fg=self.theme.fg, font=self.theme.tk_font(),
                                anchor="w", padx=10, pady=6)
                if self.column_widths[i]:
                    cell.configure(width=self.column_widths[i])
                cell.pack(side="left", fill="x",
                          expand=not bool(self.column_widths[i]))
                cell.bind("<Button-1>",
                          lambda e, r=row, w=rw: self._select(r, w))

            self._row_widgets.append((rw, row))
            rw.bind("<Button-1>",
                    lambda e, r=row, w=rw: self._select(r, w))

    def _select(self, row, widget):
        for i, (rw, r) in enumerate(self._row_widgets):
            rw.configure(bg=self.theme.surface2 if (self.zebra and i % 2)
                            else self.theme.surface)
            for child in rw.winfo_children():
                child.configure(bg=rw.cget("bg"))
        widget.configure(bg=self.theme.accent)
        for child in widget.winfo_children():
            child.configure(bg=self.theme.accent, fg=self.theme.accent_fg)
        self._selected = row
        if self.on_select:
            self.on_select(row)

    def selected(self):
        return self._selected

    def clear(self):
        self.set_rows([])