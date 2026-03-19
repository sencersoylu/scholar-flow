"""Tests for response cache."""

import time

from pubmed_mcp.cache import ResponseCache


def test_cache_set_and_get(tmp_path):
    cache = ResponseCache(cache_dir=tmp_path, ttl_seconds=3600)
    cache.set("test_key", {"data": "value"})
    result = cache.get("test_key")
    assert result == {"data": "value"}


def test_cache_miss(tmp_path):
    cache = ResponseCache(cache_dir=tmp_path, ttl_seconds=3600)
    result = cache.get("nonexistent")
    assert result is None


def test_cache_expiry(tmp_path):
    cache = ResponseCache(cache_dir=tmp_path, ttl_seconds=1)
    cache.set("expires", {"data": "old"})
    time.sleep(1.1)
    result = cache.get("expires")
    assert result is None


def test_cache_key_hashing(tmp_path):
    cache = ResponseCache(cache_dir=tmp_path, ttl_seconds=3600)
    # Different queries should produce different keys
    cache.set("query_a", {"a": 1})
    cache.set("query_b", {"b": 2})
    assert cache.get("query_a") == {"a": 1}
    assert cache.get("query_b") == {"b": 2}
