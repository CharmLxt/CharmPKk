"""Загрузка данных из интернета: текст, JSON, файлы."""
import urllib.request
import urllib.error
import gzip
import zlib
import re
import json

from ..files.download import download


def _fetch_raw(url, headers=None, timeout=10):
    """Внутренняя функция: загружает URL и возвращает (bytes, content_type).
    Автоматически распаковывает gzip/deflate/br.
    """
    hdrs = dict(headers or {})
    hdrs.setdefault("User-Agent", "CharmPkk/1.26.0")
    hdrs.setdefault("Accept-Encoding", "identity")

    req = urllib.request.Request(url, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            encoding = resp.headers.get("Content-Encoding", "").lower()
            content_type = resp.headers.get("Content-Type", "")
    except urllib.error.URLError as e:
        raise RuntimeError(f"Ошибка сети при загрузке {url}: {e.reason}")

    if encoding == "gzip":
        raw = gzip.decompress(raw)
    elif encoding == "deflate":
        raw = zlib.decompress(raw)
    elif encoding == "br":
        try:
            import brotli
            raw = brotli.decompress(raw)
        except ImportError:
            raise RuntimeError("Сервер отдал Brotli, установите: pip install brotli")

    return raw, content_type


def fetch_text(url, headers=None, timeout=10, encoding=None):
    raw, content_type = _fetch_raw(url, headers=headers, timeout=timeout)
    if encoding is None:
        charset_match = re.search(r'charset=([\w-]+)', content_type, re.IGNORECASE)
        if charset_match:
            encoding = charset_match.group(1)
        else:
            preview = raw[:3000].decode('ascii', errors='replace')
            meta_match = re.search(
                r'<meta[^>]+charset=["\']?([\w-]+)', preview, re.IGNORECASE)
            encoding = meta_match.group(1) if meta_match else "utf-8"
    try:
        return raw.decode(encoding, errors="replace")
    except LookupError:
        return raw.decode("utf-8", errors="replace")


def fetch_json(url, headers=None, timeout=10):
    text = fetch_text(url, headers=headers, timeout=timeout)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Сервер вернул некорректный JSON для {url}: {e}")


def download_file(url, dst, progress=None, resume=True, headers=None):
    return download(url, dst, progress=progress, resume=resume, headers=headers)