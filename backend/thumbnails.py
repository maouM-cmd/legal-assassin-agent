"""Thumbnail extraction for hit comparison UI."""
from __future__ import annotations

import base64
from pathlib import Path

import cv2

from backend.es_client import get_hit, list_references


def _frame_b64(video_path: Path) -> str | None:
    if not video_path.exists():
        return None
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    _, buf = cv2.imencode(".jpg", frame)
    return base64.b64encode(buf).decode("ascii")


def get_hit_thumbnails(hit_id: str) -> dict | None:
    hit = get_hit(hit_id)
    if not hit:
        return None

    suspect_path = Path(hit.get("suspect_path", ""))
    suspect_b64 = _frame_b64(suspect_path) if suspect_path.exists() else None

    reference_b64 = None
    content_id = hit.get("content_id")
    for ref in list_references():
        if ref.get("content_id") == content_id:
            ref_path = Path(ref.get("source_path", ""))
            reference_b64 = _frame_b64(ref_path) if ref_path.exists() else None
            break

    return {
        "hit_id": hit_id,
        "content_id": content_id,
        "reference_title": hit.get("reference_title"),
        "reference_thumbnail": reference_b64,
        "suspect_thumbnail": suspect_b64,
    }
