"""Tests for compliance audit CSV export."""
from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import patch

from backend.audit.export import export_compliance_report


def test_export_csv_header():
    with patch("backend.audit.export.list_hits", return_value=[]), patch(
        "backend.audit.export.list_takedowns", return_value=[]
    ):
        csv_data = export_compliance_report()
    assert csv_data.startswith("timestamp,platform,content_id")
    lines = csv_data.strip().splitlines()
    assert len(lines) == 1


def test_export_includes_hit_row():
    hits = [
        {
            "timestamp": "2026-06-30T12:00:00+00:00",
            "platform": "youtube",
            "content_id": "demo-1",
            "suspect_url": "https://example.com/v/1",
            "final_score": 0.91,
            "evasion_types": ["flipped"],
            "workflow_status": "confirmed",
        }
    ]
    takedowns = [
        {
            "suspect_url": "https://example.com/v/1",
            "status": "submitted",
        }
    ]
    with patch("backend.audit.export.list_hits", return_value=hits), patch(
        "backend.audit.export.list_takedowns", return_value=takedowns
    ):
        csv_data = export_compliance_report()
    assert "youtube" in csv_data
    assert "flipped" in csv_data
    assert "submitted" in csv_data


def test_export_date_filter_naive_bounds():
    """Smoke test uses naive from/to query params; must not 500."""
    hits = [
        {
            "timestamp": "2026-06-30T12:00:00+00:00",
            "platform": "youtube",
            "content_id": "demo",
            "suspect_url": "https://example.com/v/1",
            "final_score": 0.9,
            "evasion_types": [],
            "workflow_status": "confirmed",
        }
    ]
    start = datetime(2020, 1, 1)
    end = datetime(2030, 1, 1)
    with patch("backend.audit.export.list_hits", return_value=hits), patch(
        "backend.audit.export.list_takedowns", return_value=[]
    ):
        csv_data = export_compliance_report(start, end)
    assert "youtube" in csv_data

    hits = [
        {
            "timestamp": "2026-01-01T00:00:00+00:00",
            "platform": "youtube",
            "content_id": "old",
            "suspect_url": "https://example.com/old",
            "final_score": 0.5,
            "evasion_types": [],
            "workflow_status": "confirmed",
        },
        {
            "timestamp": "2026-06-30T00:00:00+00:00",
            "platform": "tiktok",
            "content_id": "new",
            "suspect_url": "https://example.com/new",
            "final_score": 0.9,
            "evasion_types": ["cropped"],
            "workflow_status": "confirmed",
        },
    ]
    start = datetime(2026, 6, 1, tzinfo=timezone.utc)
    end = datetime(2026, 7, 1, tzinfo=timezone.utc)
    with patch("backend.audit.export.list_hits", return_value=hits), patch(
        "backend.audit.export.list_takedowns", return_value=[]
    ):
        csv_data = export_compliance_report(start, end)
    assert "tiktok" in csv_data
    assert "https://example.com/new" in csv_data
    assert "https://example.com/old" not in csv_data
