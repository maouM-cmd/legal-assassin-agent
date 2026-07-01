"""YouTube scanner via Data API v3."""
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta, timezone

from backend.scanners.base import BaseScanner, ScanCandidate, ScanResult
from backend.scanners.demo_candidates import demo_candidates as _demo_candidates


class ApiYouTubeScanner(BaseScanner):
    platform = "youtube"

    async def scan(self, keywords: list[str]) -> ScanResult:
        api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
        if not api_key:
            return ScanResult(
                platform=self.platform,
                candidates=_demo_candidates(keywords),
                error="YOUTUBE_API_KEY not set — using demo candidates",
            )

        try:
            from googleapiclient.discovery import build

            youtube = build("youtube", "v3", developerKey=api_key)
            published_after = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
            own_channel = os.getenv("YOUTUBE_OWN_CHANNEL_ID", "").strip()
            candidates: list[ScanCandidate] = []

            for kw in keywords:
                resp = youtube.search().list(
                    q=kw,
                    part="snippet",
                    type="video",
                    maxResults=10,
                    publishedAfter=published_after,
                    order="date",
                ).execute()
                for item in resp.get("items", []):
                    vid = item["id"].get("videoId", "")
                    channel_id = item["snippet"].get("channelId", "")
                    if not vid:
                        continue
                    if own_channel and channel_id == own_channel:
                        continue
                    candidates.append(
                        ScanCandidate(
                            platform=self.platform,
                            url=f"https://www.youtube.com/watch?v={vid}",
                            title=item["snippet"].get("title", ""),
                            metadata={"keyword": kw},
                        )
                    )
                await asyncio.sleep(float(os.getenv("YOUTUBE_SCAN_DELAY_SEC", "1.0")))
            return ScanResult(platform=self.platform, candidates=candidates)
        except Exception as e:
            return ScanResult(
                platform=self.platform,
                candidates=_demo_candidates(keywords),
                error=str(e),
            )
