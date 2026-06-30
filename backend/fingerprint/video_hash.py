"""Perceptual video hashing (pHash) for frame sequences."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import cv2
import imagehash
from PIL import Image


def _has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def _frame_to_phash(frame) -> str:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil = Image.fromarray(rgb)
    return str(imagehash.phash(pil))


def _hash_distance(h1: str, h2: str) -> int:
    try:
        return imagehash.hex_to_hash(h1) - imagehash.hex_to_hash(h2)
    except Exception:
        return 64


def hash_similarity(h1: str, h2: str) -> float:
    dist = _hash_distance(h1, h2)
    return max(0.0, 1.0 - dist / 64.0)


def extract_frame_hashes(
    video_path: str | Path,
    interval_sec: float = 5.0,
    max_frames: int = 120,
) -> list[str]:
    path = Path(video_path)
    if not path.exists():
        return _mock_hashes(str(path))

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return _mock_hashes(str(path))

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frame_step = max(int(fps * interval_sec), 1)
    hashes: list[str] = []
    frame_idx = 0

    while len(hashes) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_step == 0:
            hashes.append(_frame_to_phash(frame))
        frame_idx += 1

    cap.release()
    return hashes if hashes else _mock_hashes(str(path))


def extract_frame_hashes_flipped(video_path: str | Path, **kwargs) -> list[str]:
    path = Path(video_path)
    if not path.exists():
        return extract_frame_hashes(path, **kwargs)

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return extract_frame_hashes(path, **kwargs)

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    interval_sec = kwargs.get("interval_sec", 5.0)
    max_frames = kwargs.get("max_frames", 120)
    frame_step = max(int(fps * interval_sec), 1)
    hashes: list[str] = []
    frame_idx = 0

    while len(hashes) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_step == 0:
            flipped = cv2.flip(frame, 1)
            hashes.append(_frame_to_phash(flipped))
        frame_idx += 1

    cap.release()
    return hashes


def extract_region_hashes(
    video_path: str | Path,
    region: str = "top",
    interval_sec: float = 5.0,
    max_frames: int = 60,
) -> list[str]:
    """Extract pHash from top/bottom half for split-screen detection."""
    path = Path(video_path)
    if not path.exists():
        return []

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frame_step = max(int(fps * interval_sec), 1)
    hashes: list[str] = []
    frame_idx = 0

    while len(hashes) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_step == 0:
            h, w = frame.shape[:2]
            if region == "top":
                crop = frame[0 : h // 2, :]
            else:
                crop = frame[h // 2 :, :]
            hashes.append(_frame_to_phash(crop))
        frame_idx += 1

    cap.release()
    return hashes


def _normalize_speed_video(input_path: Path, pts_factor: float) -> Path | None:
    """Create speed-adjusted temp video via ffmpeg setpts."""
    if not _has_ffmpeg():
        return None
    out = Path(tempfile.mktemp(suffix=".mp4"))
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-filter:v",
                f"setpts={pts_factor}*PTS",
                "-t",
                "30",
                str(out),
            ],
            capture_output=True,
            timeout=120,
            check=False,
        )
        return out if out.exists() and out.stat().st_size > 0 else None
    except Exception:
        return None


def extract_center_crop_hashes(
    video_path: str | Path,
    crop_ratio: float = 0.8,
    interval_sec: float = 5.0,
    max_frames: int = 60,
) -> list[str]:
    """Extract pHash from central crop (letterbox/crop evasion)."""
    path = Path(video_path)
    if not path.exists():
        return []

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frame_step = max(int(fps * interval_sec), 1)
    hashes: list[str] = []
    frame_idx = 0

    while len(hashes) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_step == 0:
            h, w = frame.shape[:2]
            ch, cw = int(h * crop_ratio), int(w * crop_ratio)
            y0, x0 = (h - ch) // 2, (w - cw) // 2
            crop = frame[y0 : y0 + ch, x0 : x0 + cw]
            scaled = cv2.resize(crop, (w, h))
            hashes.append(_frame_to_phash(scaled))
        frame_idx += 1

    cap.release()
    return hashes


def extract_speed_normalized_hashes(
    video_path: str | Path,
    pts_factor: float,
    **kwargs,
) -> list[str]:
    path = Path(video_path)
    normalized = _normalize_speed_video(path, pts_factor)
    if normalized:
        try:
            return extract_frame_hashes(normalized, **kwargs)
        finally:
            try:
                normalized.unlink(missing_ok=True)
            except Exception:
                pass
    return []


def compare_hash_sequences(ref: list[str], suspect: list[str]) -> float:
    if not ref or not suspect:
        return 0.0
    scores: list[float] = []
    step = max(len(ref) // max(len(suspect), 1), 1)
    for i, sh in enumerate(suspect):
        ri = min(i * step, len(ref) - 1)
        scores.append(hash_similarity(ref[ri], sh))
    return sum(scores) / len(scores) if scores else 0.0


def compare_with_evasions(ref_hashes: list[str], suspect_path: str | Path) -> dict[str, Any]:
    """Compare suspect against reference including flip, region, speed, and crop."""
    suspect_path = Path(suspect_path)
    normal = extract_frame_hashes(suspect_path)
    flipped = extract_frame_hashes_flipped(suspect_path)
    top = extract_region_hashes(suspect_path, "top")
    bottom = extract_region_hashes(suspect_path, "bottom")
    center_crop = extract_center_crop_hashes(suspect_path)
    speed_up = extract_speed_normalized_hashes(suspect_path, 0.9)
    speed_down = extract_speed_normalized_hashes(suspect_path, 1.1)

    scores = {
        "normal": compare_hash_sequences(ref_hashes, normal),
        "flipped": compare_hash_sequences(ref_hashes, flipped),
        "top_half": compare_hash_sequences(ref_hashes, top) if top else 0.0,
        "bottom_half": compare_hash_sequences(ref_hashes, bottom) if bottom else 0.0,
        "center_crop": compare_hash_sequences(ref_hashes, center_crop) if center_crop else 0.0,
        "speed_up": compare_hash_sequences(ref_hashes, speed_up) if speed_up else 0.0,
        "speed_down": compare_hash_sequences(ref_hashes, speed_down) if speed_down else 0.0,
    }
    best_type = max(scores, key=scores.get)
    evasion_map = {
        "flipped": "flipped",
        "top_half": "split_screen",
        "bottom_half": "split_screen",
        "center_crop": "cropped",
        "speed_up": "speed_changed",
        "speed_down": "speed_changed",
    }
    return {
        "video_hash_score": scores[best_type],
        "evasion_type": evasion_map.get(best_type) if best_type != "normal" else None,
        "scores": scores,
    }


def _mock_hashes(seed: str) -> list[str]:
    """Deterministic hashes when video cannot be read (demo mode)."""
    out: list[str] = []
    for i in range(12):
        digest = hashlib.md5(f"{seed}:{i}".encode()).hexdigest()
        out.append(digest[:16])
    return out


def get_duration_sec(video_path: str | Path) -> float:
    path = Path(video_path)
    if not path.exists():
        return 60.0
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        return 60.0
    fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
    cap.release()
    return frames / fps if fps else 60.0
