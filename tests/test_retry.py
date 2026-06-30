"""Tests for DMCA retry exponential backoff."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from backend.dmca.retry import (
    BACKOFF_SEC,
    backoff_seconds,
    is_ready_for_retry,
    next_retry_at,
)


def test_backoff_seconds_clamps_index():
    assert backoff_seconds(0) == BACKOFF_SEC[0]
    assert backoff_seconds(99) == BACKOFF_SEC[-1]


def test_ready_when_no_last_retry():
    td = {"retry_count": 0, "status": "failed"}
    assert is_ready_for_retry(td) is True


def test_not_ready_during_backoff_window():
    now = datetime.now(timezone.utc)
    td = {
        "retry_count": 1,
        "last_retry_at": now.isoformat(),
        "status": "failed",
    }
    assert is_ready_for_retry(td, now) is False


def test_ready_after_backoff_elapsed():
    now = datetime.now(timezone.utc)
    past = now - timedelta(seconds=backoff_seconds(1) + 1)
    td = {
        "retry_count": 1,
        "last_retry_at": past.isoformat(),
        "status": "failed",
    }
    assert is_ready_for_retry(td, now) is True


def test_next_retry_at_returns_none_at_max_retries():
    td = {"retry_count": 3, "last_retry_at": datetime.now(timezone.utc).isoformat()}
    assert next_retry_at(td) is None
