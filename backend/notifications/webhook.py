"""Slack/Teams-compatible webhook notifications."""
from __future__ import annotations

import os
from typing import Any

import httpx


def _enabled() -> bool:
    if os.getenv("WEBHOOK_ENABLED", "false").lower() != "true":
        return False
    return bool(os.getenv("WEBHOOK_URL", "").strip())


def format_payload(event: dict[str, Any]) -> dict[str, Any]:
    event_type = event.get("type", "EVENT")
    text = f"[Legal Assassin] {event_type}"
    if event_type == "TARGET_ACQUIRED":
        hit = event.get("hit", {})
        text = (
            f"TARGET ACQUIRED: {hit.get('reference_title')} "
            f"score={hit.get('final_score')} url={hit.get('suspect_url')}"
        )
    elif event_type == "TAKEDOWN_SENT":
        td = event.get("takedown", {})
        text = f"TAKEDOWN SENT: {td.get('platform')} {td.get('suspect_url')}"
    elif event_type == "PENDING_APPROVAL":
        hit = event.get("hit", {})
        text = f"PENDING APPROVAL: {hit.get('suspect_url')} score={hit.get('final_score')}"
    elif event_type == "PENDING_MANUAL":
        td = event.get("takedown", {})
        text = f"MANUAL REQUIRED: {td.get('platform')} {td.get('reason', 'CAPTCHA')}"
    elif event_type == "COUNTER_NOTIFICATION":
        td = event.get("takedown", {})
        text = (
            f"COUNTER-NOTIFICATION {td.get('counter_notification_status', 'received')}: "
            f"{td.get('suspect_url')}"
        )
    elif event_type == "LEGAL_HOLD":
        td = event.get("takedown", {})
        hold = "ON" if td.get("legal_hold") else "OFF"
        text = f"LEGAL HOLD {hold}: {td.get('suspect_url')}"
    return {"text": text}


async def send_webhook(event: dict[str, Any]) -> bool:
    if not _enabled():
        return False
    url = os.getenv("WEBHOOK_URL", "").strip()
    payload = format_payload(event)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            return resp.status_code < 400
    except Exception:
        return False
