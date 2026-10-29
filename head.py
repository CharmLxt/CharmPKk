"""HTTP-заголовки без скачивания тела."""
import urllib.request

def get_headers(url, timeout=10):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "CharmPkk/22.10"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return dict(resp.headers)
    except Exception:
        return {}

def content_length(url):
    h = get_headers(url)
    cl = h.get("Content-Length") or h.get("content-length")
    return int(cl) if cl else None