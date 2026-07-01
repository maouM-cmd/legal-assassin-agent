"""YouTube DMCA submitter — delegates to platform adapter factory."""
from __future__ import annotations

from typing import Any

from backend.dmca.submitters.base import BaseSubmitter
from backend.platforms.factory import get_youtube_submitter


class YouTubeSubmitter(BaseSubmitter):
    platform = "youtube"

    def __init__(self) -> None:
        self._delegate = get_youtube_submitter()

    async def submit(self, notice: dict[str, Any]) -> dict[str, Any]:
        return await self._delegate.submit(notice)
