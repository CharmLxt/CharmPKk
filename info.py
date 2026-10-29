"""Информация о файлах и папках."""
import os
from datetime import datetime
from pathlib import Path

def file_info(path):
    p = Path(path)
    if not p.exists():
        return None
    st = p.stat()
    return {
        "path": str(p.resolve()),
        "name": p.name,
        "is_file": p.is_file(),
        "is_dir": p.is_dir(),
        "size": st.st_size if p.is_file() else None,
        "created": datetime.fromtimestamp(st.st_ctime).isoformat(),
        "modified": datetime.fromtimestamp(st.st_mtime).isoformat(),
        "accessed": datetime.fromtimestamp(st.st_atime).isoformat(),
        "mode": oct(st.st_mode),
        "readable": os.access(str(p), os.R_OK),
        "writable": os.access(str(p), os.W_OK),
    }

def file_exists(path):
    return Path(path).exists()

def is_empty_dir(path):
    p = Path(path)
    return p.is_dir() and not any(p.iterdir())

def count_files(path):
    from .operations import walk_files
    return sum(1 for _ in walk_files(path))