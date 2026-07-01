"""TikTok DMCA submitter — delegates to platform adapter factory."""
from __future__ import annotations

from typing import Any

from backend.dmca.submitters.base import BaseSubmitter
from backend.platforms.factory import get_tiktok_submitter


class TikTokSubmitter(BaseSubmitter):
    platform = "tiktok"

    def __init__(self) -> None:
        self._delegate = get_tiktok_submitter()

    async def submit(self, notice: dict[str, Any]) -> dict[str, Any]:
        return await self._delegate.submit(notice)
