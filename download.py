"""Скачивание файлов с прогрессом, повторами и докачкой."""
import os
import urllib.request
import urllib.error
import time
from pathlib import Path


def download(url, dst, progress=None, chunk_size=65536,
             retries=3, timeout=30, overwrite=True, headers=None, resume=True):
    dst = Path(dst)
    if dst.exists() and not overwrite:
        return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    base_headers = headers or {"User-Agent": "CharmPkk/1.26.0"}
    tmp = dst.with_suffix(dst.suffix + ".part")
    downloaded = 0
    if resume and tmp.exists():
        downloaded = tmp.stat().st_size
        if downloaded > 0:
            base_headers["Range"] = f"bytes={downloaded}-"
        else:
            tmp.unlink(missing_ok=True)
    req = urllib.request.Request(url, headers=base_headers)
    last_error = None
    for attempt in range(max(1, retries)):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                if downloaded > 0 and resp.status != 206:
                    downloaded = 0
                    tmp.unlink(missing_ok=True)
                cr = resp.headers.get("Content-Range")
                total = None
                if cr and "/" in cr:
                    total = int(cr.split("/")[-1])
                else:
                    cl = resp.headers.get("Content-Length")
                    total = int(cl) + downloaded if cl else None
                mode = "ab" if downloaded > 0 else "wb"
                with open(tmp, mode) as f:
                    while True:
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress:
                            try:
                                progress(downloaded, total)
                            except Exception:
                                pass
            os.replace(str(tmp), str(dst))
            return dst
        except urllib.error.HTTPError as e:
            if e.code == 416:
                os.replace(str(tmp), str(dst))
                return dst
            last_error = f"HTTP {e.code}: {e.reason}"
            if e.code in (401, 403, 404):
                break
        except Exception as e:
            last_error = e
        if attempt < retries - 1:
            time.sleep(1)
    raise RuntimeError(f"Не удалось скачать {url}. Ошибка: {last_error}")


def download_many(items, progress=None, headers=None):
    if isinstance(items, dict):
        items = list(items.items())
    return [download(url, dst, progress=progress, headers=headers) for url, dst in items]