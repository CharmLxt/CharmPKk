"""Поиск дубликатов файлов по содержимому (SHA-256)."""
import hashlib
from pathlib import Path
from collections import defaultdict

def _hash_file(path, chunk_size=65536):
    h = hashlib.sha256()
    try:
        with open(str(path), "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
    except (OSError, IOError):
        return None

def find_duplicates(root, min_size=0):
    root = Path(root)
    if not root.exists():
        return {}
    size_map = defaultdict(list)
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        try:
            size = p.stat().st_size
            if size < min_size:
                continue
            size_map[size].append(p)
        except OSError:
            continue
    candidates = [files for files in size_map.values() if len(files) > 1]
    result = defaultdict(list)
    for files in candidates:
        for f in files:
            h = _hash_file(f)
            if h:
                result[h].append(f)
    return {h: files for h, files in result.items() if len(files) > 1}