"""XeronLegacy - кастом, файлы и сеть."""
from .. import console
try:
    from .. import window
    HAS_WINDOW = True
except Exception:
    window = None
    HAS_WINDOW = False

from .. import seclipse, network
from ..seclipse import (
    copy_file, copy_tree, move, remove_tree, find,
    download, sha256, md5, verify,
    is_writable, free_space, ensure_dir, ensure_space,
    Manifest, Installer, install_from_dir, uninstall,
    download_via, open_in_browser, detect_browsers, download_interactive,
)
from ..files import walk_files
from ..console import FancyProgressBar, get_theme
from ..console.installer_ui import (
    install_header, install_step, install_progress, animated_progress,
    install_rocket, install_gears, install_complete, install_warning,
    install_error, install_success, install_wizard,
)


def copy_with_progress(src, dst, ignore=None, theme="tokyo_night"):
    total_bytes = sum(size for _, size in walk_files(src))
    if total_bytes == 0:
        return copy_tree(src, dst, ignore=ignore)
    p = get_theme(theme)
    state = {"bytes": 0}
    with FancyProgressBar(total=total_bytes, width=50, style="block",
                          gradient=(p.accent, p.success),
                          label="copy", show_count=True) as pb:
        def _cb(path, size):
            state["bytes"] += size
            pb.update(state["bytes"])
        stats = copy_tree(src, dst, ignore=ignore, progress=_cb)
    print(console.success(f"Скопировано {stats['files']} файлов ({stats['bytes'] // 1024} KB)"))
    return stats


def download_with_progress(url, dst, title="download", theme="tokyo_night",
                           retries=3, expected_hash=None, browser=None):
    p = get_theme(theme)
    with FancyProgressBar(total=100, width=50, style="block",
                          gradient=(p.accent, p.success),
                          label=title, show_percent=True) as pb:
        def _cb(downloaded, total):
            if total:
                pb.update(int(downloaded / total * 100))
            else:
                mb = downloaded / (1024 * 1024)
                pb.update(min(99, int(mb)))
        if browser:
            res = download_via(url, dst, browser=browser, progress=_cb)
        else:
            res = download(url, dst, progress=_cb, retries=retries)
    if expected_hash:
        print(console.info("Проверка хеша..."))
        if not verify(res, expected_hash):
            raise ValueError(f"Хеш файла не совпадает! Ожидался: {expected_hash}")
        print(console.success("Хеш верен."))
    return res


__all__ = [
    "console", "window", "HAS_WINDOW", "seclipse", "network",
    "copy_file", "copy_tree", "move", "remove_tree", "find",
    "download", "sha256", "md5", "verify",
    "is_writable", "free_space", "ensure_dir", "ensure_space",
    "Manifest", "Installer", "install_from_dir", "uninstall",
    "copy_with_progress", "download_with_progress",
    "download_via", "open_in_browser", "detect_browsers", "download_interactive",
    "install_header", "install_step", "install_progress", "animated_progress",
    "install_rocket", "install_gears", "install_complete", "install_warning",
    "install_error", "install_success", "install_wizard",
]