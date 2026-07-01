"""Retry failed DMCA takedown requests with exponential backoff."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from backend.dmca.generator import generate_dmca_notice
from backend.dmca.submitters.tiktok import TikTokSubmitter
from backend.dmca.submitters.twitter import TwitterSubmitter
from backend.dmca.submitters.youtube import YouTubeSubmitter
from backend.es_client import (
    get_hit,
    list_failed_takedowns_ready,
    log_takedown_request,
    update_takedown_by_url,
)

SUBMITTERS = {
    "youtube": YouTubeSubmitter(),
    "tiktok": TikTokSubmitter(),
    "twitter": TwitterSubmitter(),
}

MAX_RETRIES = int(os.getenv("DMCA_MAX_RETRIES", "3"))
BACKOFF_SEC = [60, 120, 240]


def _parse_dt(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def backoff_seconds(retry_count: int) -> int:
    idx = min(max(retry_count, 0), len(BACKOFF_SEC) - 1)
    return BACKOFF_SEC[idx]


def next_retry_at(td: dict[str, Any], now: datetime | None = None) -> datetime | None:
    """When this failed takedown becomes eligible for retry."""
    retries = int(td.get("retry_count", 0))
    if retries >= MAX_RETRIES:
        return None
    now = now or datetime.now(timezone.utc)
    last_raw = td.get("last_retry_at") or td.get("retried_at") or td.get("timestamp")
    if not last_raw:
        return now
    last = _parse_dt(str(last_raw))
    if last is None:
        return now
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    return last + timedelta(seconds=backoff_seconds(retries))


def is_ready_for_retry(td: dict[str, Any], now: datetime | None = None) -> bool:
    retries = int(td.get("retry_count", 0))
    if retries >= MAX_RETRIES:
        return False
    nxt = next_retry_at(td, now)
    if nxt is None:
        return False
    now = now or datetime.now(timezone.utc)
    return now >= nxt


async def retry_failed_takedowns() -> list[dict[str, Any]]:
    now = datetime.now(timezone.utc)
    failed = list_failed_takedowns_ready(50)
    results: list[dict[str, Any]] = []

    for td in failed:
        if td.get("legal_hold"):
            results.append(
                {
                    "status": "skipped",
                    "reason": "legal_hold",
                    "suspect_url": td.get("suspect_url"),
                }
            )
            continue

        retries = int(td.get("retry_count", 0))
        if not is_ready_for_retry(td, now):
            results.append(
                {
                    "status": "skipped",
                    "reason": "backoff",
                    "suspect_url": td.get("suspect_url"),
                    "next_retry_at": next_retry_at(td, now).isoformat() if next_retry_at(td, now) else None,
                }
            )
            continue

        platform = td.get("platform", "youtube")
        submitter = SUBMITTERS.get(platform)
        if not submitter:
            continue

        hit_id = td.get("hit_id")
        hit = get_hit(hit_id) if hit_id else None
        notice = generate_dmca_notice(hit or td)

        result = await submitter.submit(notice)
        retried_at = datetime.now(timezone.utc).isoformat()
        result["retry_count"] = retries + 1
        result["retried_at"] = retried_at
        result["last_retry_at"] = retried_at
        log_takedown_request(result)

        url = td.get("suspect_url", "")
        if url:
            update_takedown_by_url(
                url,
                {
                    "status": result.get("status"),
                    "retry_count": retries + 1,
                    "last_retry_at": retried_at,
                },
            )

        results.append(result)

    return results
