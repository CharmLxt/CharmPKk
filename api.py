"""Простой REST API клиент с JSON."""
import json
import gzip
import zlib
import urllib.request
import urllib.error
from urllib.parse import urlencode


class NetworkError(Exception):
    pass


class HTTPError(NetworkError):
    def __init__(self, status, reason, url):
        self.status = status
        self.reason = reason
        self.url = url
        super().__init__(f"HTTP {status} {reason} для {url}")


class APIClient:
    def __init__(self, base_url="", headers=None, timeout=15):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "User-Agent": "CharmPkk/1.26.0",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        }
        if headers:
            self.headers.update(headers)
        self.timeout = timeout

    def _build_url(self, path, params=None):
        url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path
        if params:
            url += ("&" if "?" in url else "?") + urlencode(params)
        return url

    def _request(self, method, path, params=None, data=None, json_data=None,
                 headers=None):
        url = self._build_url(path, params)
        hdrs = dict(self.headers)
        if headers:
            hdrs.update(headers)

        body = None
        if json_data is not None:
            body = json.dumps(json_data).encode("utf-8")
            hdrs["Content-Type"] = "application/json"
        elif data is not None:
            body = data if isinstance(data, bytes) else data.encode("utf-8")

        req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read()
                encoding = resp.headers.get("Content-Encoding", "").lower()
                ct = resp.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            raise HTTPError(e.code, e.reason, url) from e
        except urllib.error.URLError as e:
            raise NetworkError(f"Ошибка соединения: {e.reason}") from e

        if encoding == "gzip":
            raw = gzip.decompress(raw)
        elif encoding == "deflate":
            raw = zlib.decompress(raw)
        elif encoding == "br":
            try:
                import brotli
                raw = brotli.decompress(raw)
            except ImportError:
                raise NetworkError("Сервер отдал Brotli, установите: pip install brotli")

        if "json" in ct:
            return json.loads(raw.decode("utf-8"))
        return raw.decode("utf-8", errors="replace")

    def get(self, path, params=None, **kw):
        return self._request("GET", path, params=params, **kw)

    def post(self, path, json_data=None, data=None, **kw):
        return self._request("POST", path, json_data=json_data, data=data, **kw)

    def put(self, path, json_data=None, data=None, **kw):
        return self._request("PUT", path, json_data=json_data, data=data, **kw)

    def delete(self, path, **kw):
        return self._request("DELETE", path, **kw)


def get_json(url, **kw):
    return APIClient().get(url, **kw)


def post_json(url, payload, **kw):
    return APIClient().post(url, json_data=payload, **kw)