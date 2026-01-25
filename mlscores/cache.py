#
# SPDX-FileCopyrightText: 2024 John Samuel <johnsamuelwrites@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

"""Local caching for SPARQL query results."""

import os
import json
import hashlib
import time
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass

from .constants import DEFAULT_CACHE_TTL_SECONDS


@dataclass
class CacheEntry:
    """A cached item with timestamp."""

    data: Any
    timestamp: float
    query_hash: str


class QueryCache:
    """File-based cache for SPARQL query results."""

    def __init__(
        self,
        cache_dir: Optional[str] = None,
        ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
        enabled: bool = True,
    ):
        """
        Initialize the cache.

        Args:
            cache_dir: Directory to store cache files. Defaults to ~/.mlscores/cache
            ttl_seconds: Time-to-live for cache entries in seconds
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.ttl_seconds = ttl_seconds

        if cache_dir is None:
            cache_dir = os.path.join(Path.home(), ".mlscores", "cache")

        self.cache_dir = Path(cache_dir)

        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _hash_query(self, query: str, endpoint: str) -> str:
        """Generate a hash for a query and endpoint combination."""
        content = f"{endpoint}:{query}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _get_cache_path(self, query_hash: str) -> Path:
        """Get the file path for a cache entry."""
        return self.cache_dir / f"{query_hash}.json"

    def get(self, query: str, endpoint: str) -> Optional[Any]:
        """
        Retrieve a cached result if available and not expired.

        Args:
            query: The SPARQL query string
            endpoint: The SPARQL endpoint URL

        Returns:
            Cached data or None if not available/expired
        """
        if not self.enabled:
            return None

        query_hash = self._hash_query(query, endpoint)
        cache_path = self._get_cache_path(query_hash)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                entry = json.load(f)

            # Check TTL
            age = time.time() - entry["timestamp"]
            if age > self.ttl_seconds:
                # Expired, remove and return None
                cache_path.unlink(missing_ok=True)
                return None

            return entry["data"]

        except (json.JSONDecodeError, KeyError, IOError):
            # Corrupted cache entry
            cache_path.unlink(missing_ok=True)
            return None

    def set(self, query: str, endpoint: str, data: Any) -> None:
        """
        Store a result in the cache.

        Args:
            query: The SPARQL query string
            endpoint: The SPARQL endpoint URL
            data: The result data to cache
        """
        if not self.enabled:
            return

        query_hash = self._hash_query(query, endpoint)
        cache_path = self._get_cache_path(query_hash)

        entry = {
            "data": data,
            "timestamp": time.time(),
            "query_hash": query_hash,
        }

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(entry, f)
        except IOError:
            # Cache write failure is non-fatal
            pass

    def clear(self) -> int:
        """
        Clear all cache entries.

        Returns:
            Number of entries cleared
        """
        count = 0
        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
        return count

    def clear_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of entries removed
        """
        count = 0
        current_time = time.time()

        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)

                    age = current_time - entry["timestamp"]
                    if age > self.ttl_seconds:
                        cache_file.unlink()
                        count += 1
                except (json.JSONDecodeError, KeyError, IOError):
                    cache_file.unlink(missing_ok=True)
                    count += 1

        return count

    def stats(self) -> dict:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        total = 0
        expired = 0
        valid = 0
        total_size = 0
        current_time = time.time()

        if self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("*.json"):
                total += 1
                total_size += cache_file.stat().st_size

                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        entry = json.load(f)

                    age = current_time - entry["timestamp"]
                    if age > self.ttl_seconds:
                        expired += 1
                    else:
                        valid += 1
                except (json.JSONDecodeError, KeyError, IOError):
                    expired += 1

        return {
            "total_entries": total,
            "valid_entries": valid,
            "expired_entries": expired,
            "total_size_bytes": total_size,
            "cache_dir": str(self.cache_dir),
            "ttl_seconds": self.ttl_seconds,
            "enabled": self.enabled,
        }


# Global cache instance
_cache: Optional[QueryCache] = None


def get_cache() -> QueryCache:
    """Get or create the global cache instance."""
    global _cache
    if _cache is None:
        _cache = QueryCache()
    return _cache


def configure_cache(
    cache_dir: Optional[str] = None,
    ttl_seconds: Optional[int] = None,
    enabled: bool = True,
) -> None:
    """
    Configure the global cache instance.

    Args:
        cache_dir: Directory to store cache files
        ttl_seconds: Time-to-live for cache entries
        enabled: Whether caching is enabled
    """
    global _cache

    _cache = QueryCache(
        cache_dir=cache_dir,
        ttl_seconds=ttl_seconds or DEFAULT_CACHE_TTL_SECONDS,
        enabled=enabled,
    )
