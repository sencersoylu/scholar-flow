"""File-based response cache with TTL."""

import hashlib
import json
import time
from pathlib import Path


class ResponseCache:
    def __init__(self, cache_dir: Path | str, ttl_seconds: int = 86400):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_seconds = ttl_seconds

    def _key_path(self, key: str) -> Path:
        hashed = hashlib.sha256(key.encode()).hexdigest()[:16]
        return self.cache_dir / f"{hashed}.json"

    def get(self, key: str) -> dict | None:
        path = self._key_path(key)
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            if time.time() - data["timestamp"] > self.ttl_seconds:
                path.unlink(missing_ok=True)
                return None
            return data["value"]
        except (json.JSONDecodeError, KeyError):
            path.unlink(missing_ok=True)
            return None

    def set(self, key: str, value: dict) -> None:
        path = self._key_path(key)
        data = {"timestamp": time.time(), "value": value}
        path.write_text(json.dumps(data))
