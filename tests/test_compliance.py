"""Tests for counter-notification and legal hold compliance."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.agent import LegalAssassinAgent
from backend.compliance.counter_notification import (
    compliance_overview,
    record_counter_notification,
    set_legal_hold,
)
from backend.main import app


def test_record_counter_notification_updates_takedown():
    url = "https://example.com/v/counter"
    with patch(
        "backend.compliance.counter_notification._ensure_takedown_record",
        return_value={"suspect_url": url},
    ), patch(
        "backend.compliance.counter_notification.update_takedown_by_url",
        return_value=True,
    ) as update_mock, patch(
        "backend.compliance.counter_notification.get_takedown_by_url",
        return_value={
            "suspect_url": url,
            "counter_notification_status": "received",
            "counter_notification_notes": "uploader disputed",
        },
    ):
        result = record_counter_notification(url, "received", "uploader disputed")
    assert result["counter_notification_status"] == "received"
    update_mock.assert_called_once()
    assert update_mock.call_args[0][1]["counter_notification_status"] == "received"


def test_record_counter_notification_rejects_invalid_status():
    with pytest.raises(ValueError):
        record_counter_notification("https://example.com/v/1", "invalid")


def test_set_legal_hold():
    url = "https://example.com/v/hold"
    with patch(
        "backend.compliance.counter_notification._ensure_takedown_record",
        return_value={"suspect_url": url},
    ), patch(
        "backend.compliance.counter_notification.update_takedown_by_url",
        return_value=True,
    ) as update_mock, patch(
        "backend.compliance.counter_notification.get_takedown_by_url",
        return_value={"suspect_url": url, "legal_hold": True},
    ):
        result = set_legal_hold(url, True, "pending counsel review")
    assert result["legal_hold"] is True
    update_mock.assert_called_once()


def test_compliance_overview_counts():
    items = [
        {"legal_hold": True, "counter_notification_status": "received"},
        {"legal_hold": False, "counter_notification_status": "under_review"},
        {"legal_hold": False, "counter_notification_status": "none"},
    ]
    with patch("backend.compliance.counter_notification.list_takedowns", return_value=items):
        overview = compliance_overview()
    assert overview["legal_holds"] == 1
    assert overview["counter_received"] == 1
    assert overview["under_review"] == 1


@pytest.mark.asyncio
async def test_submit_dmca_skips_legal_hold():
    agent = LegalAssassinAgent(notify=AsyncMock())
    with patch("backend.agent.is_url_under_legal_hold", return_value=True):
        result = await agent.submit_dmca_for_hit(
            {"suspect_url": "https://example.com/v/1", "platform": "youtube"}
        )
    assert result["status"] == "skipped"
    assert result["reason"] == "legal_hold"


def test_compliance_counter_api_requires_api_key():
    client = TestClient(app)
    with patch.dict(os.environ, {"API_KEY": "secret-key"}, clear=False):
        res = client.post(
            "/api/compliance/counter-notification",
            json={
                "suspect_url": "https://example.com/v/1",
                "status": "received",
            },
        )
        assert res.status_code == 401

        ok = client.post(
            "/api/compliance/counter-notification",
            json={
                "suspect_url": "https://example.com/v/1",
                "status": "received",
            },
            headers={"X-API-Key": "secret-key"},
        )
        assert ok.status_code == 200
