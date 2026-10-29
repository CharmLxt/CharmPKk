"""Хеши и проверка целостности файлов."""
import hashlib

def hash_file(path, algorithm="sha256", chunk_size=65536):
    h = hashlib.new(algorithm)
    with open(str(path), "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def sha256(path):
    return hash_file(path, "sha256")

def md5(path):
    return hash_file(path, "md5")

def verify(path, expected, algorithm=None):
    if algorithm is None:
        if isinstance(expected, str) and ":" in expected:
            algorithm, expected = expected.split(":", 1)
        else:
            algorithm = "sha256"
    try:
        actual = hash_file(path, algorithm)
    except (OSError, ValueError):
        return False
    return actual.lower() == expected.lower()