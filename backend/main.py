"""FastAPI backend for Legal Assassin Agent."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.agent import LegalAssassinAgent
from backend.audit.export import export_compliance_report
from backend.auth import require_api_key
from backend.compliance.counter_notification import (
    compliance_overview,
    list_counter_notifications,
    list_legal_holds,
    record_counter_notification,
    set_legal_hold,
)
from backend.dmca.generator import generate_dmca_notice
from backend.dmca.retry import retry_failed_takedowns
from backend.es_client import (
    get_es,
    get_hit,
    get_stats,
    list_hits,
    list_references,
    list_takedowns,
)
from backend.thumbnails import get_hit_thumbnails

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"

scheduler = AsyncIOScheduler()
ws_clients: list[WebSocket] = []


async def broadcast(event: dict[str, Any]) -> None:
    dead: list[WebSocket] = []
    for ws in ws_clients:
        try:
            await ws.send_json(event)
        except Exception:
            dead.append(ws)
    for ws in dead:
        if ws in ws_clients:
            ws_clients.remove(ws)


agent = LegalAssassinAgent(notify=broadcast)


async def _scheduled_patrol() -> None:
    if os.getenv("PATROL_ENABLED", "true").lower() != "true":
        return
    await agent.patrol_all()


async def _scheduled_retry() -> None:
    if os.getenv("DMCA_RETRY_ENABLED", "true").lower() != "true":
        return
    await retry_failed_takedowns()


@asynccontextmanager
async def lifespan(app: FastAPI):
    interval = int(os.getenv("PATROL_INTERVAL_MIN", "15"))
    scheduler.add_job(_scheduled_patrol, "interval", minutes=interval, id="patrol")
    retry_min = int(os.getenv("DMCA_RETRY_INTERVAL_MIN", "30"))
    scheduler.add_job(_scheduled_retry, "interval", minutes=retry_min, id="dmca_retry")
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Legal Assassin Agent", version="0.3.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    video_path: str
    platform: str = "demo"
    suspect_url: str = ""


class CandidateRequest(BaseModel):
    url: str
    platform: str = "youtube"
    title: str = ""


class CounterNotificationRequest(BaseModel):
    suspect_url: str
    status: str
    notes: str = ""


class LegalHoldRequest(BaseModel):
    suspect_url: str
    legal_hold: bool
    notes: str = ""


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "elasticsearch": get_es() is not None,
        "demo_mode": os.getenv("DEMO_MODE", "true").lower() == "true",
        "gemini": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        "patrol_enabled": os.getenv("PATROL_ENABLED", "true").lower() == "true",
        "patrol_interval_min": int(os.getenv("PATROL_INTERVAL_MIN", "15")),
        "match_threshold": float(os.getenv("MATCH_THRESHOLD", "0.78")),
        "hybrid_match": os.getenv("HYBRID_MATCH", "true").lower() == "true",
        "webhook_enabled": os.getenv("WEBHOOK_ENABLED", "false").lower() == "true",
        "api_key_required": bool(os.getenv("API_KEY", "").strip()),
    }


@app.get("/api/stats")
def stats():
    return {
        **get_stats(),
        "patrol": LegalAssassinAgent.get_patrol_status(),
    }


@app.get("/api/references")
def references():
    items = list_references()
    safe = []
    for item in items:
        doc = {k: v for k, v in item.items() if k not in ("frame_hashes",)}
        doc["frame_hash_count"] = len(item.get("frame_hashes", []))
        safe.append(doc)
    return {"items": safe}


@app.get("/api/hits")
def hits(limit: int = 50):
    return {"items": list_hits(limit)}


@app.get("/api/review-queue")
def review_queue(limit: int = 50):
    return {"items": list_hits(limit, workflow_status="pending_approval")}


@app.get("/api/pending-manual")
def pending_manual(limit: int = 50):
    return {"items": list_takedowns(limit, status="pending_manual")}


@app.get("/api/hits/{hit_id}")
def hit_detail(hit_id: str):
    hit = get_hit(hit_id)
    if not hit:
        raise HTTPException(status_code=404, detail="hit not found")
    return hit


@app.get("/api/hits/{hit_id}/dmca-preview")
def dmca_preview(hit_id: str):
    hit = get_hit(hit_id)
    if not hit:
        raise HTTPException(status_code=404, detail="hit not found")
    notice = generate_dmca_notice(hit)
    return notice


@app.get("/api/hits/{hit_id}/thumbnails")
def hit_thumbnails(hit_id: str):
    data = get_hit_thumbnails(hit_id)
    if not data:
        raise HTTPException(status_code=404, detail="hit not found")
    return data


@app.get("/api/audit/export")
def audit_export(
    from_param: str | None = Query(default=None, alias="from"),
    to_param: str | None = Query(default=None, alias="to"),
    from_date: str | None = None,
    to_date: str | None = None,
):
    from backend.audit.export import export_compliance_report, parse_filter_datetime

    start_raw = from_param or from_date
    end_raw = to_param or to_date
    start = parse_filter_datetime(start_raw) if start_raw else None
    end = parse_filter_datetime(end_raw) if end_raw else None
    csv_data = export_compliance_report(start, end)
    filename = "legal_assassin_compliance.csv"
    return StreamingResponse(
        iter([csv_data]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/hits/{hit_id}/approve", dependencies=[Depends(require_api_key)])
async def approve_hit(hit_id: str):
    result = await agent.approve_hit(hit_id)
    if not result:
        raise HTTPException(status_code=404, detail="hit not in review queue")
    return result


@app.post("/api/hits/{hit_id}/reject", dependencies=[Depends(require_api_key)])
async def reject_hit(hit_id: str):
    result = await agent.reject_hit(hit_id)
    if not result:
        raise HTTPException(status_code=404, detail="hit not in review queue")
    return result


@app.get("/api/takedowns")
def takedowns(limit: int = 50, status: str | None = None):
    return {"items": list_takedowns(limit, status=status)}


@app.get("/api/compliance/overview")
def compliance_summary():
    return compliance_overview()


@app.get("/api/compliance/counter-notifications")
def compliance_counter_notifications(limit: int = 50):
    return {"items": list_counter_notifications(limit)}


@app.get("/api/compliance/legal-holds")
def compliance_legal_holds(limit: int = 50):
    return {"items": list_legal_holds(limit)}


@app.post("/api/compliance/counter-notification", dependencies=[Depends(require_api_key)])
async def compliance_record_counter(req: CounterNotificationRequest):
    try:
        record = record_counter_notification(req.suspect_url, req.status, req.notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    event = {"type": "COUNTER_NOTIFICATION", "takedown": record}
    await broadcast(event)
    from backend.notifications.webhook import send_webhook

    await send_webhook(event)
    return record


@app.post("/api/compliance/legal-hold", dependencies=[Depends(require_api_key)])
async def compliance_set_legal_hold(req: LegalHoldRequest):
    try:
        record = set_legal_hold(req.suspect_url, req.legal_hold, req.notes)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    event = {"type": "LEGAL_HOLD", "takedown": record}
    await broadcast(event)
    from backend.notifications.webhook import send_webhook

    await send_webhook(event)
    return record


@app.post("/api/takedowns/retry", dependencies=[Depends(require_api_key)])
async def retry_takedowns():
    results = await retry_failed_takedowns()
    return {"retried": len(results), "results": results}


@app.post("/api/patrol", dependencies=[Depends(require_api_key)])
async def patrol_now():
    results = await agent.patrol_all()
    return {
        "platforms": {
            k: {
                "candidates": len(v.candidates),
                "error": v.error,
                "scanned_at": v.scanned_at,
            }
            for k, v in results.items()
        }
    }


@app.post("/api/patrol/{platform}", dependencies=[Depends(require_api_key)])
async def patrol_platform(platform: str):
    result = await agent.patrol_platform(platform)
    return {
        "platform": platform,
        "candidates": len(result.candidates),
        "error": result.error,
        "scanned_at": result.scanned_at,
    }


@app.post("/api/analyze")
async def analyze_local(req: AnalyzeRequest):
    from backend.matchers.similarity import match_suspect

    matches = match_suspect(req.video_path, req.platform, req.suspect_url)
    return {"matches": matches}


@app.post("/api/process-candidate")
async def process_candidate(req: CandidateRequest):
    from backend.scanners.base import ScanCandidate

    results = await agent.process_candidate(
        ScanCandidate(platform=req.platform, url=req.url, title=req.title)
    )
    return {"results": results}


@app.websocket("/ws/events")
async def ws_events(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        if ws in ws_clients:
            ws_clients.remove(ws)


if FRONTEND.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND)), name="static")

    @app.get("/")
    def index():
        return FileResponse(FRONTEND / "index.html")
