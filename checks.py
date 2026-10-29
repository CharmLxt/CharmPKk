"""Проверки перед установкой: права, свободное место, директории."""
import os
import shutil
from pathlib import Path

def _nearest_existing(path):
    p = Path(path)
    while not p.exists() and p != p.parent:
        p = p.parent
    return p

def is_writable(path):
    return os.access(str(_nearest_existing(path)), os.W_OK)

def is_readable(path):
    p = Path(path)
    return p.exists() and os.access(str(p), os.R_OK)

def free_space(path):
    return shutil.disk_usage(str(_nearest_existing(path))).free

def ensure_dir(path):
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

def ensure_space(path, min_mb):
    free = free_space(path)
    req = int(min_mb) * 1024 * 1024
    if free < req:
        raise OSError(f"Мало места: свободно {free//(1024*1024)} MB, нужно {min_mb} MB")
    return True

def sanitize_filename(name):
    """Убирает недопустимые символы из имени файла."""
    bad_chars = '<>:"/\\|?*'
    for c in bad_chars:
        name = name.replace(c, '_')
    return name.strip()