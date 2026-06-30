"""Similarity matching against reference fingerprints."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from backend.embedding import embed_query
from backend.es_client import knn_search_references, list_references
from backend.fingerprint.evasion import detect_evasion_types
from backend.vision import secondary_review, vision_confidence_for_evasion


def _match_threshold() -> float:
    return float(os.getenv("MATCH_THRESHOLD", "0.78"))


def _secondary_threshold() -> float:
    return float(os.getenv("SECONDARY_MATCH_THRESHOLD", "0.70"))


def _knn_candidates() -> int:
    return int(os.getenv("KNN_CANDIDATES", "5"))


def _use_hybrid_match() -> bool:
    return os.getenv("HYBRID_MATCH", "true").lower() == "true"


def compute_final_score(
    video_hash_score: float,
    audio_score: float,
    vision_confidence: float,
    evasion_types: list[str] | None = None,
) -> float:
    video = float(video_hash_score)
    audio = float(audio_score)
    vision = float(vision_confidence)
    if video >= 0.85 and evasion_types:
        return 0.65 * video + 0.05 * audio + 0.30 * vision
    return 0.4 * video + 0.4 * audio + 0.2 * vision


def _candidate_references(suspect_path: Path) -> list[dict[str, Any]]:
    all_refs = list_references()
    if not all_refs:
        return []
    if not _use_hybrid_match():
        return all_refs

    query_text = suspect_path.stem.replace("_", " ")
    query_vec = embed_query(query_text)
    if not any(v != 0.0 for v in query_vec):
        return all_refs

    knn_refs = knn_search_references(query_vec, k=_knn_candidates())
    return knn_refs if knn_refs else all_refs


def match_suspect(
    suspect_path: str | Path,
    platform: str = "unknown",
    suspect_url: str = "",
) -> list[dict[str, Any]]:
    suspect_path = Path(suspect_path)
    references = _candidate_references(suspect_path)
    if not references:
        return []

    matches: list[dict[str, Any]] = []
    threshold = _match_threshold()
    secondary = _secondary_threshold()

    for ref in references:
        evasion = detect_evasion_types(
            suspect_path,
            ref.get("frame_hashes", []),
            ref.get("audio_fingerprint", ""),
        )
        vision_conf = vision_confidence_for_evasion(
            suspect_path,
            evasion.get("evasion_types", []),
        )
        final_score = compute_final_score(
            evasion.get("video_hash_score", 0.0),
            evasion.get("audio_score", 0.0),
            vision_conf,
            evasion.get("evasion_types", []),
        )

        if secondary <= final_score < threshold:
            review = secondary_review(suspect_path, final_score)
            if review.get("is_infringement"):
                boost = float(review.get("confidence", 0.75))
                final_score = min(1.0, (final_score + boost) / 2)

        if final_score < secondary:
            continue

        status = "confirmed" if final_score >= threshold else "review"
        matches.append(
            {
                "content_id": ref.get("content_id"),
                "reference_title": ref.get("title"),
                "suspect_url": suspect_url,
                "suspect_path": str(suspect_path),
                "platform": platform,
                "final_score": round(final_score, 4),
                "video_hash_score": round(evasion.get("video_hash_score", 0.0), 4),
                "audio_score": round(evasion.get("audio_score", 0.0), 4),
                "vision_confidence": round(vision_conf, 4),
                "evasion_types": evasion.get("evasion_types", []),
                "status": status,
            }
        )

    matches.sort(key=lambda m: m["final_score"], reverse=True)
    return matches
