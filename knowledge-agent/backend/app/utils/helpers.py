"""
Shared helper utilities.
"""

import hashlib
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current UTC timestamp."""
    return datetime.now(timezone.utc)


def content_hash(text: str) -> str:
    """Return a SHA-256 hex digest for deduplication."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
