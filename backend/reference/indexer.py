"""Index reference content fingerprints into Elasticsearch."""
from __future__ import annotations

from pathlib import Path

from backend.embedding import embed_reference
from backend.es_client import index_reference
from backend.fingerprint.evasion import build_reference_profile
from backend.vision import analyze_evasion_frame


def index_video(
    video_path: str | Path,
    content_id: str,
    title: str,
) -> dict:
    path = Path(video_path)
    doc = build_reference_profile(path, content_id, title)
    vision = analyze_evasion_frame(path)
    scene_summary = vision.get("description", "")
    doc["frame_embedding"] = embed_reference(content_id, title, scene_summary)
    index_reference(doc)
    return doc


def index_directory(clips_dir: str | Path) -> list[dict]:
    clips_dir = Path(clips_dir)
    results: list[dict] = []
    if not clips_dir.exists():
        return results
    for mp4 in sorted(clips_dir.glob("*.mp4")):
        if mp4.name.startswith("evasion_"):
            continue
        content_id = mp4.stem
        title = content_id.replace("_", " ")
        results.append(index_video(mp4, content_id, title))
    return results
