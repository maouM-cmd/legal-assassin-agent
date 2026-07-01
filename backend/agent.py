"""Legal Assassin Agent: scan -> match -> dmca -> submit."""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Awaitable, Callable

from backend.dmca.generator import generate_dmca_notice
from backend.dmca.submitters.tiktok import TikTokSubmitter
from backend.dmca.submitters.twitter import TwitterSubmitter
from backend.dmca.submitters.youtube import YouTubeSubmitter
from backend.download import cleanup_download, download_candidate
from backend.es_client import (
    get_hit,
    is_url_under_legal_hold,
    log_infringement_hit,
    log_takedown_request,
    update_hit,
    url_already_processed,
)
from backend.matchers.similarity import match_suspect
from backend.scanners.base import ScanCandidate, ScanResult
from backend.scanners.tiktok import TikTokScanner
from backend.scanners.twitter import TwitterScanner
from backend.scanners.youtube import YouTubeScanner

DEBOUNCE_SEC = 300.0
_recent_urls: dict[str, float] = {}
_patrol_status: dict[str, Any] = {
    "youtube": {"last_scan": None, "candidates": 0, "error": None},
    "tiktok": {"last_scan": None, "candidates": 0, "error": None},
    "twitter": {"last_scan": None, "candidates": 0, "error": None},
}

SUBMITTERS = {
    "youtube": YouTubeSubmitter(),
    "tiktok": TikTokSubmitter(),
    "twitter": TwitterSubmitter(),
}

SCANNERS = {
    "youtube": YouTubeScanner(),
    "tiktok": TikTokScanner(),
    "twitter": TwitterScanner(),
}


def _is_demo() -> bool:
    return os.getenv("DEMO_MODE", "true").lower() == "true"


def _should_process(url: str) -> bool:
    if url_already_processed(url):
        return False
    now = time.time()
    last = _recent_urls.get(url, 0)
    if now - last < DEBOUNCE_SEC:
        return False
    _recent_urls[url] = now
    return True


def _keywords() -> list[str]:
    raw = os.getenv("MONITOR_KEYWORDS", "作品名,キャラクター名")
    return [k.strip() for k in raw.split(",") if k.strip()]


def _resolve_workflow(hit: dict[str, Any]) -> str:
    status = hit.get("status", "")
    if status == "review" and not _is_demo():
        return "pending_approval"
    if status in ("confirmed", "review"):
        return "auto_submitted"
    return "logged"


def _should_auto_submit(hit: dict[str, Any]) -> bool:
    if hit.get("status") == "confirmed":
        return True
    return _is_demo() and hit.get("status") == "review"


class LegalAssassinAgent:
    def __init__(self, notify: Callable[[dict[str, Any]], Awaitable[None]] | None = None):
        self._notify = notify

    async def _emit(self, event: dict[str, Any]) -> None:
        if self._notify:
            await self._notify(event)
        try:
            from backend.notifications.webhook import send_webhook

            await send_webhook(event)
        except Exception:
            pass

    async def submit_dmca_for_hit(self, hit: dict[str, Any]) -> dict[str, Any]:
        suspect_url = hit.get("suspect_url", "")
        platform = hit.get("platform", "youtube")
        if suspect_url and is_url_under_legal_hold(suspect_url):
            skipped = {
                "status": "skipped",
                "reason": "legal_hold",
                "platform": platform,
                "suspect_url": suspect_url,
            }
            await self._emit({"type": "LEGAL_HOLD", "takedown": skipped})
            return skipped

        notice = generate_dmca_notice(hit)
        submitter = SUBMITTERS.get(platform)
        takedown_result: dict[str, Any] = {"status": "skipped", "platform": platform}
        if submitter:
            takedown_result = await submitter.submit(notice)

        takedown_log = {
            **takedown_result,
            "hit_id": hit.get("hit_id"),
            "suspect_url": hit.get("suspect_url"),
            "content_id": hit.get("content_id"),
            "notice_preview": notice.get("body", "")[:500],
            "notice_body": notice.get("body", ""),
            "retry_count": takedown_result.get("retry_count", 0),
            "legal_hold": False,
            "counter_notification_status": "none",
        }
        log_takedown_request(takedown_log)

        if takedown_result.get("status") == "submitted":
            await self._emit({"type": "TAKEDOWN_SENT", "takedown": takedown_log})
        elif takedown_result.get("status") == "pending_manual":
            await self._emit({"type": "PENDING_MANUAL", "takedown": takedown_log})

        return {**takedown_result, "notice": notice}

    async def approve_hit(self, hit_id: str) -> dict[str, Any] | None:
        hit = get_hit(hit_id)
        if not hit or hit.get("workflow_status") != "pending_approval":
            return None
        update_hit(hit_id, {"workflow_status": "approved"})
        hit["workflow_status"] = "approved"
        result = await self.submit_dmca_for_hit(hit)
        return {"hit": hit, "takedown": result}

    async def reject_hit(self, hit_id: str) -> dict[str, Any] | None:
        hit = get_hit(hit_id)
        if not hit or hit.get("workflow_status") != "pending_approval":
            return None
        update_hit(hit_id, {"workflow_status": "rejected"})
        await self._emit({"type": "HIT_REJECTED", "hit_id": hit_id})
        return {"hit_id": hit_id, "workflow_status": "rejected"}

    async def process_candidate(self, candidate: ScanCandidate) -> list[dict[str, Any]]:
        if not _should_process(candidate.url):
            return []

        suspect_path: Path | None = None
        cleanup = False

        if candidate.url.startswith("file://"):
            from urllib.parse import unquote, urlparse

            parsed = urlparse(candidate.url)
            raw = unquote(parsed.path)
            if raw.startswith("/") and len(raw) > 2 and raw[2] == ":":
                raw = raw[1:]
            suspect_path = Path(raw)
        else:
            suspect_path = download_candidate(candidate.url)
            cleanup = suspect_path is not None

        if suspect_path is None or not suspect_path.exists():
            return []

        if not suspect_path.is_file() or suspect_path.name == ".":
            return []

        try:
            suspect_path = suspect_path.resolve()
        except Exception:
            return []

        if not suspect_path.is_file():
            return []

        try:
            matches = match_suspect(suspect_path, candidate.platform, candidate.url)
            results: list[dict[str, Any]] = []

            for hit in matches:
                if hit.get("status") not in ("confirmed", "review"):
                    continue

                hit["workflow_status"] = _resolve_workflow(hit)
                hit_id = log_infringement_hit(hit)
                hit["hit_id"] = hit_id
                await self._emit({"type": "TARGET_ACQUIRED", "hit": hit})

                takedown_result: dict[str, Any] = {"status": "skipped"}
                if hit["workflow_status"] == "pending_approval":
                    await self._emit({"type": "PENDING_APPROVAL", "hit": hit})
                elif _should_auto_submit(hit):
                    takedown_result = await self.submit_dmca_for_hit(hit)

                results.append({**hit, "takedown": takedown_result})

            return results
        finally:
            if cleanup and suspect_path:
                cleanup_download(suspect_path)

    async def patrol_platform(self, platform: str) -> ScanResult:
        scanner = SCANNERS.get(platform)
        if not scanner:
            return ScanResult(platform=platform, candidates=[], error="unknown platform")

        result = await scanner.scan(_keywords())
        _patrol_status[platform] = {
            "last_scan": result.scanned_at,
            "candidates": len(result.candidates),
            "error": result.error,
        }

        for candidate in result.candidates:
            await self.process_candidate(candidate)

        await self._emit(
            {
                "type": "PATROL_COMPLETE",
                "platform": platform,
                "candidates": len(result.candidates),
                "error": result.error,
            }
        )
        return result

    async def patrol_all(self) -> dict[str, ScanResult]:
        outcomes: dict[str, ScanResult] = {}
        for platform in SCANNERS:
            outcomes[platform] = await self.patrol_platform(platform)
        return outcomes

    @staticmethod
    def get_patrol_status() -> dict[str, Any]:
        return dict(_patrol_status)
