"""Файловые операции: копирование, перемещение, удаление, поиск, архивация, синхронизация."""
import os
import shutil
import zipfile
import tarfile
import stat
import sys
from pathlib import Path

def _norm(p):
    return Path(p)

def human_size(bytes_count, suffix="B"):
    if bytes_count == 0:
        return f"0 {suffix}"
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if abs(bytes_count) < 1024.0:
            return f"{bytes_count:3.1f} {unit}{suffix}"
        bytes_count /= 1024.0
    return f"{bytes_count:.1f} Y{suffix}"

def human_time(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds}s"
    m, s = divmod(seconds, 60)
    if m < 60:
        return f"{m}m {s}s"
    h, m = divmod(m, 60)
    if h < 24:
        return f"{h}h {m}m"
    d, h = divmod(h, 24)
    return f"{d}d {h}h {m}m"

def walk_files(src):
    src = _norm(src)
    if src.is_file():
        try:
            yield src, src.stat().st_size
        except OSError:
            return
        return
    if not src.exists():
        return
    for root, _dirs, files in os.walk(str(src)):
        for f in files:
            p = Path(root) / f
            try:
                yield p, p.stat().st_size
            except OSError:
                continue

def dir_size(path):
    return sum(size for _, size in walk_files(path))

def get_newest_file(root_dir, extensions=None):
    """Возвращает путь к самому новому файлу в директории (по mtime)."""
    newest_file = None
    newest_time = 0
    for p, _ in walk_files(root_dir):
        if extensions and p.suffix.lower() not in extensions:
            continue
        try:
            mtime = p.stat().st_mtime
            if mtime > newest_time:
                newest_time = mtime
                newest_file = p
        except OSError:
            pass
    return newest_file

def find_largest_files(root_dir, limit=5):
    """Возвращает список из `limit` самых тяжелых файлов в директории."""
    files = []
    for p, size in walk_files(root_dir):
        files.append((p, size))
    files.sort(key=lambda x: x[1], reverse=True)
    return files[:limit]

def _copy_with_progress(src, dst, progress, chunk_size=1024 * 1024):
    total = src.stat().st_size
    copied = 0
    with open(str(src), "rb") as fsrc:
        with open(str(dst), "wb") as fdst:
            while True:
                chunk = fsrc.read(chunk_size)
                if not chunk:
                    break
                fdst.write(chunk)
                copied += len(chunk)
                if progress:
                    progress(dst, len(chunk))
    shutil.copystat(str(src), str(dst))

def copy_file(src, dst, overwrite=True, preserve=True, progress=None):
    src = _norm(src)
    dst = _norm(dst)
    if dst.exists() and not overwrite:
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.stat().st_size < 5 * 1024 * 1024:
        if preserve:
            shutil.copy2(str(src), str(dst))
        else:
            shutil.copyfile(str(src), str(dst))
        if progress:
            progress(dst, src.stat().st_size)
    else:
        _copy_with_progress(src, dst, progress)
    return True

def copy_tree(src, dst, overwrite=True, preserve=True, ignore=None,
              ignore_fn=None, progress=None, on_error="raise"):
    src = _norm(src)
    dst = _norm(dst)
    ignore = set(ignore or [])
    stats = {"files": 0, "skipped": 0, "bytes": 0, "errors": []}
    if src.is_file():
        written = copy_file(src, dst, overwrite, preserve, progress)
        if written:
            stats["files"] = 1
            stats["bytes"] = src.stat().st_size
        else:
            stats["skipped"] = 1
        return stats
    if not src.exists():
        raise FileNotFoundError(f"Источник не найден: {src}")
    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(str(src)):
        dirs[:] = [d for d in dirs if d not in ignore
                   and not (ignore_fn and ignore_fn(Path(root) / d))]
        rel = os.path.relpath(root, str(src))
        target_dir = dst if rel == "." else dst / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            if f in ignore:
                continue
            s = Path(root) / f
            if ignore_fn and ignore_fn(s):
                continue
            d = target_dir / f
            try:
                written = copy_file(s, d, overwrite, preserve, progress)
                if written:
                    size = s.stat().st_size
                    stats["files"] += 1
                    stats["bytes"] += size
                else:
                    stats["skipped"] += 1
            except OSError as e:
                stats["errors"].append((str(s), str(e)))
                if on_error == "raise":
                    raise
                elif on_error == "warn":
                    print(f"[files] Ошибка {s}: {e}")
    return stats

def sync_tree(src, dst, ignore=None, ignore_fn=None, progress=None, on_error="warn"):
    src = _norm(src)
    dst = _norm(dst)
    ignore = set(ignore or [])
    stats = {"files": 0, "skipped": 0, "bytes": 0, "errors": []}
    if not src.exists():
        raise FileNotFoundError(f"Источник не найден: {src}")
    dst.mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(str(src)):
        dirs[:] = [d for d in dirs if d not in ignore
                   and not (ignore_fn and ignore_fn(Path(root) / d))]
        rel = os.path.relpath(root, str(src))
        target_dir = dst if rel == "." else dst / rel
        target_dir.mkdir(parents=True, exist_ok=True)
        for f in files:
            if f in ignore:
                continue
            s = Path(root) / f
            if ignore_fn and ignore_fn(s):
                continue
            d = target_dir / f
            need_copy = False
            if not d.exists():
                need_copy = True
            else:
                s_stat = s.stat()
                d_stat = d.stat()
                if s_stat.st_size != d_stat.st_size or s_stat.st_mtime > d_stat.st_mtime:
                    need_copy = True
            if need_copy:
                try:
                    copy_file(s, d, progress=progress)
                    stats["files"] += 1
                    stats["bytes"] += s.stat().st_size
                except OSError as e:
                    stats["errors"].append((str(s), str(e)))
                    if on_error == "raise":
                        raise
                    elif on_error == "warn":
                        print(f"[sync] Ошибка {s}: {e}")
            else:
                stats["skipped"] += 1
    return stats

def move(src, dst, overwrite=False):
    src = _norm(src)
    dst = _norm(dst)
    if dst.exists() and not overwrite:
        raise FileExistsError(f"Цель уже существует: {dst}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.move(str(src), str(dst))
    except OSError:
        copy_tree(src, dst, overwrite=overwrite)
        remove_tree(src)
    return dst

def _remove_readonly(func, path, exc):
    exc_val = exc[1] if isinstance(exc, tuple) else exc
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise exc_val

def remove_tree(path, on_error="ignore"):
    path = _norm(path)
    if not path.exists():
        return 0
    if path.is_file():
        try:
            path.unlink()
            return 1
        except OSError:
            return 0
    kwargs = {}
    if sys.version_info >= (3, 12):
        kwargs["onexc"] = _remove_readonly
    else:
        kwargs["onerror"] = _remove_readonly
    if on_error == "raise":
        shutil.rmtree(str(path), **kwargs)
    else:
        kwargs["ignore_errors"] = True
        shutil.rmtree(str(path), **kwargs)
    return 1

def remove_file(path):
    p = _norm(path)
    try:
        p.unlink()
        return True
    except (FileNotFoundError, OSError):
        try:
            os.chmod(str(p), stat.S_IWRITE)
            p.unlink()
            return True
        except Exception:
            return False

def move_to_trash(path):
    path = _norm(path)
    if not path.exists():
        return False
    try:
        import send2trash
        send2trash.send2trash(str(path))
        return True
    except ImportError:
        pass
    except Exception:
        pass
    if sys.platform == "win32":
        try:
            import subprocess
            ps = (
                'Add-Type -AssemblyName Microsoft.VisualBasic;'
                f'[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile('
                f'"{path}",'
                '"OnlyErrorDialogs","SendToRecycleBin")'
            ) if path.is_file() else (
                'Add-Type -AssemblyName Microsoft.VisualBasic;'
                f'[Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory('
                f'"{path}",'
                '"OnlyErrorDialogs","SendToRecycleBin")'
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps],
                capture_output=True, timeout=10,
            )
            return not path.exists()
        except Exception:
            pass
    if path.is_file():
        return remove_file(path)
    return remove_tree(path, on_error="ignore") > 0

def find(root, pattern="*", recursive=True, include_dirs=False):
    root = _norm(root)
    if not root.exists():
        return
    it = root.rglob(pattern) if recursive else root.glob(pattern)
    for p in it:
        if p.is_dir() and not include_dirs:
            continue
        yield p

def search_in_files(root, text, extensions=None, case_sensitive=False,
                    max_results=100):
    root = _norm(root)
    if not root.exists():
        return []
    default_exts = {".py", ".txt", ".md", ".rst", ".json", ".yaml", ".yml",
                    ".toml", ".ini", ".cfg", ".html", ".css", ".js", ".ts",
                    ".xml", ".csv", ".log", ".sh", ".bat"}
    exts = {e.lower() for e in (extensions or default_exts)}
    needle = text if case_sensitive else text.lower()
    results = []
    for p in find(root, "*", recursive=True):
        if p.suffix.lower() not in exts:
            continue
        try:
            with open(str(p), "r", encoding="utf-8", errors="ignore") as f:
                for i, line in enumerate(f, 1):
                    haystack = line if case_sensitive else line.lower()
                    if needle in haystack:
                        results.append((p, i, line.rstrip("\n")))
                        if len(results) >= max_results:
                            return results
        except OSError:
            continue
    return results

def replace_in_tree(root, old, new, extensions=None, case_sensitive=True,
                    dry_run=False):
    root = _norm(root)
    if not root.exists():
        return [], 0
    default_exts = {".py", ".txt", ".md", ".rst", ".json", ".yaml", ".yml",
                    ".toml", ".ini", ".cfg", ".html", ".css", ".js", ".ts",
                    ".xml", ".csv", ".log", ".sh", ".bat"}
    exts = {e.lower() for e in (extensions or default_exts)}
    changed = []
    total = 0
    for p in find(root, "*", recursive=True):
        if p.suffix.lower() not in exts:
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if case_sensitive:
            count = content.count(old)
            if count:
                if not dry_run:
                    p.write_text(content.replace(old, new), encoding="utf-8")
                changed.append((p, count))
                total += count
        else:
            import re
            pattern = re.compile(re.escape(old), re.IGNORECASE)
            matches = pattern.findall(content)
            count = len(matches)
            if count:
                if not dry_run:
                    p.write_text(pattern.sub(new, content), encoding="utf-8")
                changed.append((p, count))
                total += count
    return changed, total

def compare_files(a, b, chunk_size=65536):
    a = _norm(a)
    b = _norm(b)
    if not a.exists() or not b.exists():
        return False
    if a.stat().st_size != b.stat().st_size:
        return False
    with open(str(a), "rb") as fa, open(str(b), "rb") as fb:
        while True:
            ca = fa.read(chunk_size)
            cb = fb.read(chunk_size)
            if ca != cb:
                return False
            if not ca:
                return True

def compare_dirs(a, b, ignore=None):
    from .checksums import sha256
    a = _norm(a)
    b = _norm(b)
    ignore = set(ignore or [])
    files_a = {p.relative_to(a): p for p in find(a, "*", recursive=True)
               if p.name not in ignore}
    files_b = {p.relative_to(b): p for p in find(b, "*", recursive=True)
               if p.name not in ignore}
    only_a = [k for k in files_a if k not in files_b]
    only_b = [k for k in files_b if k not in files_a]
    different = []
    for k in set(files_a) & set(files_b):
        pa, pb = files_a[k], files_b[k]
        try:
            if sha256(pa) != sha256(pb):
                different.append(k)
        except OSError:
            different.append(k)
    return {
        "only_in_a": sorted(only_a),
        "only_in_b": sorted(only_b),
        "different": sorted(different),
    }

def tree_view(root, prefix="", depth_limit=None, show_files=True):
    root = _norm(root)
    if not root.exists():
        return f"[не найдено] {root}"
    if depth_limit is not None and depth_limit < 0:
        return ""
    lines = [f"{prefix}📁 {root.name or root}"]
    if root.is_file():
        return lines[0]
    try:
        entries = sorted(root.iterdir(),
                         key=lambda p: (p.is_file(), p.name.lower()))
    except OSError:
        return lines[0]
    _tree_recurse(entries, lines, prefix="", depth_limit=depth_limit,
                  show_files=show_files, current_depth=0)
    return "\n".join(lines)

def _tree_recurse(entries, lines, prefix, depth_limit, show_files, current_depth):
    if depth_limit is not None and current_depth >= depth_limit:
        return
    visible = [e for e in entries if show_files or e.is_dir()]
    for i, e in enumerate(visible):
        is_last = (i == len(visible) - 1)
        branch = "└── " if is_last else "├── "
        icon = "📁" if e.is_dir() else "📄"
        lines.append(f"{prefix}{branch}{icon} {e.name}")
        if e.is_dir():
            try:
                sub_entries = sorted(e.iterdir(),
                                     key=lambda p: (p.is_file(), p.name.lower()))
            except OSError:
                continue
            new_prefix = prefix + ("    " if is_last else "│   ")
            _tree_recurse(sub_entries, lines, new_prefix, depth_limit,
                          show_files, current_depth + 1)

def ensure_path(path):
    p = _norm(path)
    if p.suffix and not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
    else:
        p.mkdir(parents=True, exist_ok=True)
    return p

def create_zip(src_dir, zip_path, ignore=None, progress=None):
    src_dir = _norm(src_dir)
    zip_path = _norm(zip_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    ignore = set(ignore or [])
    files = list(walk_files(src_dir))
    total_bytes = sum(size for _, size in files)
    done_bytes = 0
    with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path, size in files:
            if any(part in ignore for part in file_path.parts):
                continue
            arcname = file_path.relative_to(src_dir)
            zf.write(str(file_path), str(arcname))
            done_bytes += size
            if progress:
                progress(zip_path, size)
    return zip_path