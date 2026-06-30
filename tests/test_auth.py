"""Tests for API key authentication."""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from backend.auth import require_api_key


def test_require_api_key_skips_when_unset():
    with patch.dict(os.environ, {"API_KEY": ""}, clear=False):
        require_api_key(None)


def test_require_api_key_accepts_valid_header():
    with patch.dict(os.environ, {"API_KEY": "secret-key"}, clear=False):
        require_api_key("secret-key")


def test_require_api_key_rejects_invalid():
    with patch.dict(os.environ, {"API_KEY": "secret-key"}, clear=False):
        with pytest.raises(HTTPException) as exc:
            require_api_key("wrong")
        assert exc.value.status_code == 401
