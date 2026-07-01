"""Tests for TikTok platform adapter layer."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.platforms.factory import get_tiktok_scanner, get_tiktok_submitter, tiktok_backend
from backend.platforms.tiktok_partner import PartnerTikTokScanner, PartnerTikTokSubmitter
from backend.platforms.tiktok_playwright import PlaywrightTikTokScanner, PlaywrightTikTokSubmitter


def test_factory_defaults_to_playwright():
    with patch.dict(os.environ, {"TIKTOK_BACKEND": "playwright"}, clear=False):
        assert tiktok_backend() == "playwright"
        assert isinstance(get_tiktok_scanner(), PlaywrightTikTokScanner)
        assert isinstance(get_tiktok_submitter(), PlaywrightTikTokSubmitter)


def test_factory_partner_backend():
    with patch.dict(os.environ, {"TIKTOK_BACKEND": "partner"}, clear=False):
        assert isinstance(get_tiktok_scanner(), PartnerTikTokScanner)
        assert isinstance(get_tiktok_submitter(), PartnerTikTokSubmitter)


@pytest.mark.asyncio
async def test_partner_scanner_not_configured():
    with patch.dict(
        os.environ,
        {"TIKTOK_BACKEND": "partner", "TIKTOK_PARTNER_API_URL": "", "TIKTOK_PARTNER_API_KEY": ""},
        clear=False,
    ):
        scanner = PartnerTikTokScanner()
        result = await scanner.scan(["test"])
    assert result.candidates == []
    assert "TIKTOK_PARTNER_API not configured" in (result.error or "")


@pytest.mark.asyncio
async def test_partner_submitter_not_configured():
    with patch.dict(
        os.environ,
        {"TIKTOK_BACKEND": "partner", "TIKTOK_PARTNER_API_URL": "", "TIKTOK_PARTNER_API_KEY": ""},
        clear=False,
    ):
        submitter = PartnerTikTokSubmitter()
        result = await submitter.submit({"suspect_url": "https://example.com", "body": "notice"})
    assert result["status"] == "failed"
    assert "TIKTOK_PARTNER_API not configured" in result.get("error", "")


@pytest.mark.asyncio
async def test_partner_scanner_parses_search_response():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "videos": [{"url": "https://www.tiktok.com/@u/video/1", "title": "clip"}]
    }

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch.dict(
        os.environ,
        {
            "TIKTOK_BACKEND": "partner",
            "TIKTOK_PARTNER_API_URL": "https://partner.example.com",
            "TIKTOK_PARTNER_API_KEY": "secret",
        },
        clear=False,
    ), patch("backend.platforms.tiktok_partner.httpx.AsyncClient", return_value=mock_client):
        scanner = PartnerTikTokScanner()
        result = await scanner.scan(["anime"])

    assert len(result.candidates) == 1
    assert result.candidates[0].url == "https://www.tiktok.com/@u/video/1"


@pytest.mark.asyncio
async def test_partner_submitter_posts_dmca():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"status": "submitted"}

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch.dict(
        os.environ,
        {
            "TIKTOK_BACKEND": "partner",
            "TIKTOK_PARTNER_API_URL": "https://partner.example.com",
            "TIKTOK_PARTNER_API_KEY": "secret",
            "DMCA_AUTO_SUBMIT": "true",
            "DEMO_MODE": "false",
        },
        clear=False,
    ), patch("backend.platforms.tiktok_partner.httpx.AsyncClient", return_value=mock_client):
        submitter = PartnerTikTokSubmitter()
        result = await submitter.submit(
            {"suspect_url": "https://www.tiktok.com/@u/video/1", "body": "notice"}
        )

    assert result["status"] == "submitted"
    assert result["mode"] == "partner_api"
    mock_client.post.assert_called_once()


def test_health_includes_tiktok_backend():
    client = TestClient(app)
    with patch.dict(os.environ, {"TIKTOK_BACKEND": "playwright"}, clear=False):
        data = client.get("/api/health").json()
    assert data["tiktok_backend"] == "playwright"
    assert "tiktok_partner_configured" in data
