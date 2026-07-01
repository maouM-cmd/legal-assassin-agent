"""Tests for platform adapter layer (YouTube, TikTok, X)."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.platforms.factory import (
    get_tiktok_scanner,
    get_tiktok_submitter,
    get_x_scanner,
    get_x_submitter,
    get_youtube_scanner,
    get_youtube_submitter,
    tiktok_backend,
    x_backend,
    youtube_backend,
)
from backend.platforms.tiktok_partner import PartnerTikTokScanner, PartnerTikTokSubmitter
from backend.platforms.tiktok_playwright import PlaywrightTikTokScanner, PlaywrightTikTokSubmitter
from backend.platforms.x_api import ApiXScanner
from backend.platforms.x_partner import PartnerXScanner, PartnerXSubmitter
from backend.platforms.x_playwright import PlaywrightXSubmitter
from backend.platforms.youtube_api import ApiYouTubeScanner
from backend.platforms.youtube_partner import PartnerYouTubeScanner, PartnerYouTubeSubmitter
from backend.platforms.youtube_playwright import PlaywrightYouTubeSubmitter


def test_factory_defaults():
    with patch.dict(
        os.environ,
        {"TIKTOK_BACKEND": "playwright", "YOUTUBE_BACKEND": "api", "X_BACKEND": "api"},
        clear=False,
    ):
        assert tiktok_backend() == "playwright"
        assert youtube_backend() == "api"
        assert x_backend() == "api"
        assert isinstance(get_tiktok_scanner(), PlaywrightTikTokScanner)
        assert isinstance(get_tiktok_submitter(), PlaywrightTikTokSubmitter)
        assert isinstance(get_youtube_scanner(), ApiYouTubeScanner)
        assert isinstance(get_youtube_submitter(), PlaywrightYouTubeSubmitter)
        assert isinstance(get_x_scanner(), ApiXScanner)
        assert isinstance(get_x_submitter(), PlaywrightXSubmitter)


def test_factory_partner_backends():
    with patch.dict(
        os.environ,
        {"TIKTOK_BACKEND": "partner", "YOUTUBE_BACKEND": "partner", "X_BACKEND": "partner"},
        clear=False,
    ):
        assert isinstance(get_tiktok_scanner(), PartnerTikTokScanner)
        assert isinstance(get_youtube_scanner(), PartnerYouTubeScanner)
        assert isinstance(get_x_scanner(), PartnerXScanner)
        assert isinstance(get_youtube_submitter(), PartnerYouTubeSubmitter)
        assert isinstance(get_x_submitter(), PartnerXSubmitter)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "scanner_cls,url_env,key_env,msg",
    [
        (PartnerTikTokScanner, "TIKTOK_PARTNER_API_URL", "TIKTOK_PARTNER_API_KEY", "TIKTOK_PARTNER_API"),
        (PartnerYouTubeScanner, "YOUTUBE_PARTNER_API_URL", "YOUTUBE_PARTNER_API_KEY", "YOUTUBE_PARTNER_API"),
        (PartnerXScanner, "X_PARTNER_API_URL", "X_PARTNER_API_KEY", "X_PARTNER_API"),
    ],
)
async def test_partner_scanner_not_configured(scanner_cls, url_env, key_env, msg):
    with patch.dict(os.environ, {url_env: "", key_env: ""}, clear=False):
        scanner = scanner_cls()
        result = await scanner.scan(["test"])
    assert result.candidates == []
    assert msg in (result.error or "")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "submitter_cls,url_env,key_env,msg",
    [
        (PartnerTikTokSubmitter, "TIKTOK_PARTNER_API_URL", "TIKTOK_PARTNER_API_KEY", "TIKTOK_PARTNER_API"),
        (PartnerYouTubeSubmitter, "YOUTUBE_PARTNER_API_URL", "YOUTUBE_PARTNER_API_KEY", "YOUTUBE_PARTNER_API"),
        (PartnerXSubmitter, "X_PARTNER_API_URL", "X_PARTNER_API_KEY", "X_PARTNER_API"),
    ],
)
async def test_partner_submitter_not_configured(submitter_cls, url_env, key_env, msg):
    with patch.dict(os.environ, {url_env: "", key_env: ""}, clear=False):
        submitter = submitter_cls()
        result = await submitter.submit({"suspect_url": "https://example.com", "body": "notice"})
    assert result["status"] == "failed"
    assert msg in result.get("error", "")


@pytest.mark.asyncio
async def test_partner_scanner_parses_search_response():
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "videos": [{"url": "https://www.youtube.com/watch?v=1", "title": "clip"}]
    }

    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch.dict(
        os.environ,
        {
            "YOUTUBE_BACKEND": "partner",
            "YOUTUBE_PARTNER_API_URL": "https://partner.example.com",
            "YOUTUBE_PARTNER_API_KEY": "secret",
        },
        clear=False,
    ), patch("backend.platforms.partner_client.httpx.AsyncClient", return_value=mock_client):
        scanner = PartnerYouTubeScanner()
        result = await scanner.scan(["anime"])

    assert len(result.candidates) == 1
    assert "youtube.com" in result.candidates[0].url


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
            "X_BACKEND": "partner",
            "X_PARTNER_API_URL": "https://partner.example.com",
            "X_PARTNER_API_KEY": "secret",
            "DMCA_AUTO_SUBMIT": "true",
        },
        clear=False,
    ), patch("backend.platforms.partner_client.httpx.AsyncClient", return_value=mock_client):
        submitter = PartnerXSubmitter()
        result = await submitter.submit(
            {"suspect_url": "https://x.com/u/status/1", "body": "notice"}
        )

    assert result["status"] == "submitted"
    assert result["mode"] == "partner_api"
    mock_client.post.assert_called_once()


def test_health_includes_platform_backends():
    client = TestClient(app)
    with patch.dict(
        os.environ,
        {"TIKTOK_BACKEND": "playwright", "YOUTUBE_BACKEND": "api", "X_BACKEND": "api"},
        clear=False,
    ):
        data = client.get("/api/health").json()
    assert data["tiktok_backend"] == "playwright"
    assert data["youtube_backend"] == "api"
    assert data["x_backend"] == "api"
    assert "tiktok_partner_configured" in data
    assert "youtube_partner_configured" in data
    assert "x_partner_configured" in data
