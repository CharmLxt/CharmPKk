"""Проверка доступности сети и хостов."""
import socket
import urllib.request
import urllib.error

_DNS_SERVERS = [("1.1.1.1", 53), ("8.8.8.8", 53), ("208.67.222.222", 53)]

def ping(host="8.8.8.8", port=53, timeout=2):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except OSError:
        return False

def is_online(timeout=2):
    for host, port in _DNS_SERVERS:
        if ping(host, port, timeout):
            return True
    return False

def check_url(url, timeout=5):
    try:
        req = urllib.request.Request(url, method="HEAD", headers={
            "User-Agent": "CharmPkk/28.10.26b1",
            "Accept-Encoding": "identity",
        })
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False

def resolve_dns(host):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror:
        return None

def get_public_ip(timeout=5):
    """Возвращает ваш внешний (белый) IP-адрес."""
    try:
        req = urllib.request.Request("https://api.ipify.org", headers={"User-Agent": "CharmPkk"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8").strip()
    except Exception:
        return None

def is_port_open(host, port, timeout=2):
    """Проверяет, открыт ли конкретный порт на хосте."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((host, port))
        s.close()
        return result == 0
    except Exception:
        return False