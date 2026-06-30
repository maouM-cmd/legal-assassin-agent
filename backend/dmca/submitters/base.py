"""Base DMCA submitter with Playwright session support."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseSubmitter(ABC):
    platform: str = "unknown"

    @abstractmethod
    async def submit(self, notice: dict[str, Any]) -> dict[str, Any]:
        ...

    def _session_dir(self) -> Path:
        d = Path(os.getenv("PLATFORM_SESSION_DIR", "./data/sessions"))
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _session_path(self) -> Path:
        return self._session_dir() / f"{self.platform}.json"

    async def _new_context(self, browser):
        from playwright.async_api import Browser

        path = self._session_path()
        if path.exists():
            return await browser.new_context(storage_state=str(path))
        return await browser.new_context()

    async def _save_context(self, context) -> None:
        try:
            await context.storage_state(path=str(self._session_path()))
        except Exception:
            pass

    async def _fill_common_fields(self, page, notice: dict[str, Any], selectors: dict[str, str]) -> None:
        body = notice.get("body", "")
        url = notice.get("suspect_url", "")

        if selectors.get("url_input"):
            loc = page.locator(selectors["url_input"]).first
            if await loc.count() > 0:
                await loc.fill(url)

        if selectors.get("description"):
            loc = page.locator(selectors["description"]).first
            if await loc.count() > 0:
                await loc.fill(body[:4000])

    async def _check_captcha(self, page) -> bool:
        for text in ("CAPTCHA", "captcha", "robot", "I'm not a robot"):
            if await page.locator(f"text={text}").count() > 0:
                return True
        return False
