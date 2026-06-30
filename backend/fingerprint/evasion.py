"""Evasion detection: flip, pitch, speed, split-screen normalization."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from backend.fingerprint.audio_fingerprint import compare_with_pitch_evasions, extract_audio_fingerprint
from backend.fingerprint.video_hash import compare_with_evasions, extract_frame_hashes


def detect_evasion_types(video_path: str | Path, ref_hashes: list[str], ref_audio: str) -> dict[str, Any]:
    path = Path(video_path)
    video_result = compare_with_evasions(ref_hashes, path)
    audio_result = compare_with_pitch_evasions(ref_audio, path)

    evasion_types: list[str] = []
    evasion_type = video_result.get("evasion_type")
    if evasion_type == "flipped":
        evasion_types.append("flipped")
    elif evasion_type == "split_screen":
        evasion_types.append("split_screen")
    elif evasion_type == "cropped":
        evasion_types.append("cropped")
    elif evasion_type == "speed_changed":
        evasion_types.append("speed_changed")
    if audio_result.get("audio_evasion_type") in ("pitch_up", "pitch_down"):
        evasion_types.append("pitch_shifted")

    return {
        "video": video_result,
        "audio": audio_result,
        "evasion_types": evasion_types,
        "video_hash_score": video_result.get("video_hash_score", 0.0),
        "audio_score": audio_result.get("audio_score", 0.0),
    }


def build_reference_profile(video_path: str | Path, content_id: str, title: str) -> dict[str, Any]:
    path = Path(video_path)
    from backend.fingerprint.video_hash import get_duration_sec

    return {
        "content_id": content_id,
        "title": title,
        "source_path": str(path),
        "frame_hashes": extract_frame_hashes(path),
        "audio_fingerprint": extract_audio_fingerprint(path),
        "duration_sec": get_duration_sec(path),
    }
