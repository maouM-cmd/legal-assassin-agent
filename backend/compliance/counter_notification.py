"""Counter-notification and legal hold compliance workflows."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.es_client import (
    get_takedown_by_url,
    list_takedowns,
    list_takedowns_compliance,
    log_takedown_request,
    update_takedown_by_url,
)

VALID_COUNTER_STATUSES = frozenset({"received", "under_review", "restored", "dismissed"})


def compliance_overview() -> dict[str, int]:
    items = list_takedowns(1000)
    legal_holds = sum(1 for td in items if td.get("legal_hold"))
    counter_received = sum(
        1 for td in items if td.get("counter_notification_status") == "received"
    )
    under_review = sum(
        1 for td in items if td.get("counter_notification_status") == "under_review"
    )
    return {
        "legal_holds": legal_holds,
        "counter_received": counter_received,
        "under_review": under_review,
    }


def _ensure_takedown_record(suspect_url: str) -> dict[str, Any]:
    existing = get_takedown_by_url(suspect_url)
    if existing:
        return existing
    record = {
        "suspect_url": suspect_url,
        "status": "logged",
        "legal_hold": False,
        "counter_notification_status": "none",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    log_takedown_request(record)
    return get_takedown_by_url(suspect_url) or record


def record_counter_notification(
    suspect_url: str,
    status: str,
    notes: str = "",
) -> dict[str, Any]:
    if status not in VALID_COUNTER_STATUSES:
        raise ValueError(f"invalid counter_notification status: {status}")

    _ensure_takedown_record(suspect_url)
    now = datetime.now(timezone.utc).isoformat()
    updates: dict[str, Any] = {
        "counter_notification_status": status,
        "counter_notification_at": now,
        "counter_notification_notes": notes,
    }
    if not update_takedown_by_url(suspect_url, updates):
        raise LookupError(f"takedown not found for url: {suspect_url}")

    record = get_takedown_by_url(suspect_url) or {**updates, "suspect_url": suspect_url}
    return record


def set_legal_hold(
    suspect_url: str,
    legal_hold: bool,
    notes: str = "",
) -> dict[str, Any]:
    _ensure_takedown_record(suspect_url)
    updates: dict[str, Any] = {"legal_hold": legal_hold}
    if notes:
        updates["legal_hold_notes"] = notes
    if not update_takedown_by_url(suspect_url, updates):
        raise LookupError(f"takedown not found for url: {suspect_url}")

    return get_takedown_by_url(suspect_url) or {**updates, "suspect_url": suspect_url}


def list_counter_notifications(limit: int = 50) -> list[dict[str, Any]]:
    return list_takedowns_compliance(counter_status="active", limit=limit)


def list_legal_holds(limit: int = 50) -> list[dict[str, Any]]:
    return list_takedowns_compliance(legal_hold=True, limit=limit)
