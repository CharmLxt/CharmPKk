"""Высокоуровневый установщик: копирование, распаковка, манифест, uninstall."""
import shutil
from pathlib import Path

from .operations import copy_tree, copy_file
from .manifest import Manifest
from .checks import ensure_dir


class Installer:
    def __init__(self, name, version="1.0.0", target_dir=None, verbose=True):
        self.name = name
        self.version = version
        self.target_dir = Path(target_dir) if target_dir else None
        self.verbose = verbose
        self.pre_hooks = []
        self.post_hooks = []
        self.log_lines = []

    def log(self, msg):
        self.log_lines.append(msg)
        if self.verbose:
            print(f"[{self.name}] {msg}")

    def pre(self, fn):
        self.pre_hooks.append(fn)
        return fn

    def post(self, fn):
        self.post_hooks.append(fn)
        return fn

    def _run_hooks(self, hooks):
        for h in hooks:
            try:
                h(self)
            except Exception as e:
                self.log(f"Ошибка в hook: {e}")

    def _fill_manifest(self, manifest):
        for p in self.target_dir.rglob("*"):
            if p.is_file():
                try:
                    manifest.add_file(p, p.stat().st_size)
                except OSError:
                    pass
            elif p.is_dir():
                manifest.add_dir(p)
        manifest_path = self.target_dir / f"{self.name}.manifest.json"
        manifest.save(manifest_path)
        self.log(f"Манифест: {manifest_path}")

    def install_dir(self, src_dir, files=None, ignore=None, progress=None):
        if self.target_dir is None:
            raise ValueError("target_dir не задан")
        src = Path(src_dir)
        if not src.exists():
            raise FileNotFoundError(f"Источник не найден: {src}")
        self._run_hooks(self.pre_hooks)
        self.log(f"Установка в {self.target_dir}")
        ensure_dir(self.target_dir)
        manifest = Manifest()
        manifest.set_name(self.name)
        if files:
            for item in files:
                s = src / item
                d = self.target_dir / item
                if s.is_file():
                    copy_file(s, d, progress=progress)
                elif s.is_dir():
                    copy_tree(s, d, ignore=ignore, progress=progress)
        else:
            copy_tree(src, self.target_dir, ignore=ignore, progress=progress)
        self._fill_manifest(manifest)
        self._run_hooks(self.post_hooks)
        return self.target_dir

    def install_archive(self, archive_path, strip_root=True, progress=None):
        """Распаковывает архив любого формата: zip, tar.gz, tar.bz2, tar.xz, 7z, rar.
        Для 7z нужен py7zr, для rar — rarfile + unrar.
        """
        if self.target_dir is None:
            raise ValueError("target_dir не задан")
        self._run_hooks(self.pre_hooks)
        self.log(f"Распаковка {archive_path} → {self.target_dir}")

        from .archives import extract_archive

        tmp = self.target_dir.parent / (self.target_dir.name + ".tmp_extract")
        try:
            extract_archive(archive_path, tmp)
            src = tmp
            if strip_root:
                entries = list(tmp.iterdir())
                if len(entries) == 1 and entries[0].is_dir():
                    src = entries[0]
            self.target_dir.mkdir(parents=True, exist_ok=True)
            copy_tree(src, self.target_dir, progress=progress)
            manifest = Manifest()
            manifest.set_name(self.name)
            self._fill_manifest(manifest)
        finally:
            if tmp.exists():
                shutil.rmtree(str(tmp), ignore_errors=True)

        self._run_hooks(self.post_hooks)
        return self.target_dir


def install_from_dir(name, src_dir, target_dir, version="1.0.0",
                     files=None, ignore=None, verbose=True, progress=None):
    inst = Installer(name=name, version=version, target_dir=target_dir, verbose=verbose)
    return inst.install_dir(src_dir, files=files, ignore=ignore, progress=progress)


def uninstall(target_dir, manifest_name=None, verbose=True):
    target = Path(target_dir)
    if not target.exists():
        raise FileNotFoundError(f"Папка не найдена: {target}")
    if manifest_name:
        candidates = [target / manifest_name]
    else:
        candidates = list(target.glob("*.manifest.json"))
    if not candidates:
        raise FileNotFoundError(f"Манифест не найден в {target}")
    manifest = Manifest.load(candidates[0])
    removed = manifest.remove_files()
    try:
        candidates[0].unlink()
    except OSError:
        pass
    if verbose:
        print(f"[uninstall] удалено файлов: {removed}")
    return removed