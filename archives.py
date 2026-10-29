"""Работа с архивами: zip, tar.gz, 7z, rar.

Опциональные зависимости:
    py7zr     — для работы с 7z    (pip install py7zr)
    rarfile   — для работы с rar   (pip install rarfile)
                                   (также требуется системный unrar)
"""
import os
import shutil
import zipfile
import tarfile
import tempfile
from pathlib import Path

# ------------------------------------------------------------
# Определение типа
# ------------------------------------------------------------

_EXTENSIONS = {
    ".zip": "zip",
    ".tar": "tar", ".tar.gz": "tar", ".tgz": "tar",
    ".tar.bz2": "tar", ".tbz2": "tar",
    ".tar.xz": "tar", ".txz": "tar",
    ".7z": "7z",
    ".rar": "rar",
}


def is_archive(path):
    """Определяет, является ли путь архивом по расширению."""
    p = Path(path)
    name_lower = p.name.lower()
    # сначала проверяем двойные расширения
    for ext in (".tar.gz", ".tar.bz2", ".tar.xz"):
        if name_lower.endswith(ext):
            return True
    return p.suffix.lower() in {".zip", ".tar", ".tgz", ".7z", ".rar", ".tbz2", ".txz"}


def _detect_format(path):
    name_lower = Path(path).name.lower()
    for ext in (".tar.gz", ".tar.bz2", ".tar.xz"):
        if name_lower.endswith(ext):
            return "tar"
    return _EXTENSIONS.get(Path(path).suffix.lower())


# ------------------------------------------------------------
# Zip-Slip защита
# ------------------------------------------------------------

def _safe_extract_zip(zf, dst):
    dst = Path(dst).resolve()
    for member in zf.namelist():
        target = (dst / member).resolve()
        try:
            target.relative_to(dst)
        except ValueError:
            raise ValueError(f"Небезопасный путь в архиве: {member}")
    zf.extractall(str(dst))


def _safe_extract_tar(tf, dst):
    dst = Path(dst).resolve()
    for member in tf.getmembers():
        target = (dst / member.name).resolve()
        try:
            target.relative_to(dst)
        except ValueError:
            raise ValueError(f"Небезопасный путь в архиве: {member.name}")
    # В Python 3.12+ поддерживается filter="data"
    try:
        tf.extractall(str(dst), filter="data")
    except TypeError:
        tf.extractall(str(dst))


# ------------------------------------------------------------
# Просмотр без распаковки
# ------------------------------------------------------------

def list_archive(path):
    """Возвращает список (name, size) внутри архива.
    Работает для zip, tar, 7z, rar.
    """
    path = Path(path)
    fmt = _detect_format(path)

    if fmt == "zip":
        with zipfile.ZipFile(str(path)) as z:
            return [(info.filename, info.file_size) for info in z.infolist()]

    if fmt == "tar":
        with tarfile.open(str(path)) as t:
            result = []
            for m in t.getmembers():
                size = m.size if m.isfile() else 0
                result.append((m.name, size))
            return result

    if fmt == "7z":
        try:
            import py7zr
        except ImportError:
            raise RuntimeError(
                "Для просмотра 7z установите: pip install py7zr"
            )
        with py7zr.SevenZipFile(str(path), mode="r") as z:
            return [(info.filename, info.uncompressed)
                    for info in z.list()]

    if fmt == "rar":
        try:
            import rarfile
        except ImportError:
            raise RuntimeError(
                "Для просмотра rar установите: pip install rarfile\n"
                "Также нужен системный unrar (например, choco install unrar)."
            )
        with rarfile.RarFile(str(path)) as r:
            return [(info.filename, info.file_size) for info in r.infolist()]

    raise ValueError(f"Неизвестный формат архива: {path.name}")


# ------------------------------------------------------------
# Распаковка
# ------------------------------------------------------------

def extract_archive(path, dst, strip_root=False):
    """Распаковывает архив в dst. strip_root — если внутри один корневой каталог,
    его содержимое поднимается на уровень выше."""
    path = Path(path)
    dst = Path(dst)
    dst.mkdir(parents=True, exist_ok=True)

    fmt = _detect_format(path)

    if fmt == "zip":
        with zipfile.ZipFile(str(path)) as z:
            _safe_extract_zip(z, dst)
    elif fmt == "tar":
        with tarfile.open(str(path)) as t:
            _safe_extract_tar(t, dst)
    elif fmt == "7z":
        try:
            import py7zr
        except ImportError:
            raise RuntimeError(
                "Для распаковки 7z установите: pip install py7zr"
            )
        with py7zr.SevenZipFile(str(path), mode="r") as z:
            z.extractall(str(dst))
    elif fmt == "rar":
        try:
            import rarfile
        except ImportError:
            raise RuntimeError(
                "Для распаковки rar установите: pip install rarfile и unrar."
            )
        with rarfile.RarFile(str(path)) as r:
            r.extractall(str(dst))
    else:
        raise ValueError(f"Неизвестный формат архива: {path.name}")

    # Если нужно поднять содержимое из единственной корневой папки
    if strip_root:
        entries = list(dst.iterdir())
        if len(entries) == 1 and entries[0].is_dir():
            inner = entries[0]
            tmp = dst.parent / f"{dst.name}_tmp_extract"
            shutil.move(str(inner), str(tmp))
            shutil.rmtree(str(dst))
            tmp.rename(dst)

    return dst


# ------------------------------------------------------------
# Создание архивов
# ------------------------------------------------------------

def create_zip(src_dir, zip_path, ignore=None):
    """Создаёт zip из папки. ignore — имена файлов/папок для пропуска."""
    src_dir = Path(src_dir)
    zip_path = Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    ignore = set(ignore or [])
    with zipfile.ZipFile(str(zip_path), "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(str(src_dir)):
            dirs[:] = [d for d in dirs if d not in ignore]
            for f in files:
                if f in ignore:
                    continue
                file_path = Path(root) / f
                arcname = file_path.relative_to(src_dir)
                zf.write(str(file_path), str(arcname))
    return zip_path


def create_tar(src_dir, tar_path, mode="w:gz", ignore=None):
    """Создаёт tar-архив. mode: 'w:gz' (tar.gz), 'w:bz2', 'w:xz' или 'w'."""
    src_dir = Path(src_dir)
    tar_path = Path(tar_path)
    tar_path.parent.mkdir(parents=True, exist_ok=True)
    ignore = set(ignore or [])
    with tarfile.open(str(tar_path), mode) as tf:
        for root, dirs, files in os.walk(str(src_dir)):
            dirs[:] = [d for d in dirs if d not in ignore]
            for f in files:
                if f in ignore:
                    continue
                file_path = Path(root) / f
                arcname = file_path.relative_to(src_dir)
                tf.add(str(file_path), arcname=str(arcname))
    return tar_path


def create_7z(src_dir, seven_path, ignore=None):
    """Создаёт 7z из папки. Требует pip install py7zr."""
    try:
        import py7zr
    except ImportError:
        raise RuntimeError(
            "Для создания 7z установите: pip install py7zr"
        )
    src_dir = Path(src_dir)
    seven_path = Path(seven_path)
    seven_path.parent.mkdir(parents=True, exist_ok=True)
    ignore = set(ignore or [])
    with py7zr.SevenZipFile(str(seven_path), "w") as z:
        for root, dirs, files in os.walk(str(src_dir)):
            dirs[:] = [d for d in dirs if d not in ignore]
            for f in files:
                if f in ignore:
                    continue
                file_path = Path(root) / f
                arcname = file_path.relative_to(src_dir)
                z.write(str(file_path), str(arcname))
    return seven_path


# ------------------------------------------------------------
# Удаление из архива (пока только zip — самый частый)
# ------------------------------------------------------------

def remove_from_zip(zip_path, name):
    """Удаляет один файл из zip. Возвращает True при успехе."""
    zip_path = Path(zip_path)
    name = str(name).replace("\\", "/")
    if not zip_path.exists():
        return False

    with zipfile.ZipFile(str(zip_path)) as z:
        if name not in z.namelist():
            return False
        tmp = zip_path.with_suffix(".zip.tmp")
        try:
            with zipfile.ZipFile(str(tmp), "w", zipfile.ZIP_DEFLATED) as out:
                for item in z.infolist():
                    if item.filename == name:
                        continue
                    out.writestr(item, z.read(item.filename))
            os.replace(str(tmp), str(zip_path))
            return True
        except Exception:
            if tmp.exists():
                tmp.unlink(missing_ok=True)
            raise


def add_to_zip(zip_path, files, arcname_prefix=""):
    """Добавляет файлы в zip (создаёт zip, если его нет).
    files — список путей или один путь. arcname_prefix — префикс внутри архива.
    """
    zip_path = Path(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(files, (str, Path)):
        files = [files]
    with zipfile.ZipFile(str(zip_path), "a", zipfile.ZIP_DEFLATED) as z:
        for fp in files:
            fp = Path(fp)
            arc = (arcname_prefix + fp.name).replace("\\", "/")
            z.write(str(fp), arc)
    return zip_path


# ------------------------------------------------------------
# Быстрый API: автоопределение
# ------------------------------------------------------------

def extract_auto(path, dst=None, strip_root=False):
    """Распаковывает любой архив. Если dst=None — рядом с архивом
    в папку с тем же именем."""
    path = Path(path)
    if dst is None:
        dst = path.with_suffix("")
    return extract_archive(path, dst, strip_root=strip_root)