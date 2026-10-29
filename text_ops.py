"""Текстовые операции: чтение, запись, JSON, атомарная запись."""
import json
import os
from pathlib import Path

def read_text(path, encoding="utf-8"):
    return Path(path).read_text(encoding=encoding)

def write_text(path, content, encoding="utf-8", atomic=True):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if atomic:
        tmp = p.with_suffix(p.suffix + ".tmp")
        tmp.write_text(content, encoding=encoding)
        os.replace(str(tmp), str(p))
    else:
        p.write_text(content, encoding=encoding)
    return p

def append_text(path, content, encoding="utf-8"):
    with open(str(path), "a", encoding=encoding) as f:
        f.write(content)

def read_lines(path, encoding="utf-8", strip=True):
    with open(str(path), "r", encoding=encoding) as f:
        return [l.rstrip("\n") if strip else l for l in f]

def write_lines(path, lines, encoding="utf-8"):
    with open(str(path), "w", encoding=encoding) as f:
        for line in lines:
            f.write(line + "\n")

def read_json(path, encoding="utf-8"):
    return json.loads(Path(path).read_text(encoding=encoding))

def read_json_safe(path, encoding="utf-8", default=None):
    """Читает JSON, но если файл битый или его нет — возвращает default."""
    try:
        return read_json(path, encoding)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default

def write_json(path, data, indent=2, encoding="utf-8"):
    return write_text(path, json.dumps(data, indent=indent, ensure_ascii=False), encoding=encoding)

def replace_in_file(path, old, new, encoding="utf-8", count=-1):
    text = read_text(path, encoding=encoding)
    result = text.replace(old, new, count)
    if result != text:
        write_text(path, result, encoding=encoding)
    return text.count(old) if count == -1 else min(text.count(old), count)