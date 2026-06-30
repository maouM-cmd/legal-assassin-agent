"""Tests for webhook notification payloads."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest

from backend.notifications.webhook import format_payload, send_webhook


def test_format_target_acquired():
    payload = format_payload(
        {
            "type": "TARGET_ACQUIRED",
            "hit": {
                "reference_title": "Demo Show",
                "final_score": 0.92,
                "suspect_url": "https://example.com/v/1",
            },
        }
    )
    assert "TARGET ACQUIRED" in payload["text"]
    assert "Demo Show" in payload["text"]


def test_format_takedown_sent():
    payload = format_payload(
        {
            "type": "TAKEDOWN_SENT",
            "takedown": {"platform": "youtube", "suspect_url": "https://youtu.be/x"},
        }
    )
    assert "TAKEDOWN SENT" in payload["text"]
    assert "youtube" in payload["text"]


@pytest.mark.asyncio
async def test_send_webhook_disabled():
    with patch.dict(os.environ, {"WEBHOOK_ENABLED": "false", "WEBHOOK_URL": ""}):
        assert await send_webhook({"type": "TARGET_ACQUIRED"}) is False


@pytest.mark.asyncio
async def test_send_webhook_posts_when_enabled():
    with patch.dict(
        os.environ,
        {"WEBHOOK_ENABLED": "true", "WEBHOOK_URL": "https://hooks.example.com/abc"},
    ):
        with patch("backend.notifications.webhook.httpx.AsyncClient") as mock_client:
            instance = mock_client.return_value.__aenter__.return_value
            instance.post = AsyncMock(return_value=type("R", (), {"status_code": 200})())
            ok = await send_webhook({"type": "PENDING_APPROVAL", "hit": {"suspect_url": "u"}})
            assert ok is True
            instance.post.assert_called_once()
