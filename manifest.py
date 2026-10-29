"""Манифест установки: список созданных файлов и папок для корректного удаления."""
import json
from datetime import datetime
from pathlib import Path

class Manifest:
    def __init__(self, path=None, data=None):
        self.path = Path(path) if path else None
        self.data = data or {
            "version": 1,
            "installed_at": datetime.now().isoformat(),
            "name": "",
            "files": [],
            "dirs": [],
        }

    def set_name(self, name):
        self.data["name"] = name

    def add_file(self, path, size=None):
        p = str(Path(path).resolve())
        self.data["files"].append({"path": p, "size": size})

    def add_dir(self, path):
        p = str(Path(path).resolve())
        if p not in self.data["dirs"]:
            self.data["dirs"].append(p)

    def save(self, path=None):
        target = Path(path) if path else self.path
        if target is None:
            raise ValueError("Не задан путь для сохранения манифеста")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        self.path = target
        return target

    @classmethod
    def load(cls, path):
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls(path=p, data=data)

    def remove_files(self):
        removed = 0
        for entry in self.data.get("files", []):
            try:
                Path(entry["path"]).unlink()
                removed += 1
            except (FileNotFoundError, OSError):
                pass
        for d in reversed(self.data.get("dirs", [])):
            try:
                Path(d).rmdir()
            except OSError:
                pass
        return removed