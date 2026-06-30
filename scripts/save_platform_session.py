"""Save Playwright storageState after manual platform login."""
from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PLATFORM_URLS = {
    "youtube": "https://www.youtube.com/copyright_complaint_form",
    "tiktok": "https://www.tiktok.com/legal/report/Copyright",
    "twitter": "https://help.twitter.com/forms/dmca",
}


async def save_session(platform: str) -> int:
    url = PLATFORM_URLS.get(platform)
    if not url:
        print(f"Unknown platform: {platform}")
        return 1

    from playwright.async_api import async_playwright

    session_dir = ROOT / "data" / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    out = session_dir / f"{platform}.json"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url)
        print(f"Log in to {platform} in the browser window, then press Enter here...")
        input()
        await context.storage_state(path=str(out))
        await browser.close()

    print(f"Saved session: {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Save platform login session for DMCA forms")
    parser.add_argument("platform", choices=list(PLATFORM_URLS.keys()))
    args = parser.parse_args()
    return asyncio.run(save_session(args.platform))


if __name__ == "__main__":
    raise SystemExit(main())
