"""Tests for patrol API key enforcement."""
from __future__ import annotations

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_patrol_requires_api_key_when_configured(client):
    with patch.dict(os.environ, {"API_KEY": "secret-key"}, clear=False), patch(
        "backend.main.agent.patrol_all", new_callable=AsyncMock, return_value={}
    ):
        denied = client.post("/api/patrol")
        assert denied.status_code == 401

        ok = client.post("/api/patrol", headers={"X-API-Key": "secret-key"})
        assert ok.status_code == 200
