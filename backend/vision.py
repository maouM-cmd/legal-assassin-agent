"""Gemini Vision for split-screen and game overlay detection."""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any

import cv2


PROMPT = """Analyze this video frame for copyright evasion tactics.
Return ONLY valid JSON:
{
  "split_screen": false,
  "game_overlay": false,
  "inverted": false,
  "confidence": 0.0,
  "description": "..."
}
Detect: split screen with unrelated game, horizontal flip, picture-in-picture overlays."""


def _extract_keyframe(video_path: Path) -> str | None:
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


def analyze_evasion_frame(video_path: str | Path) -> dict[str, Any]:
    path = Path(video_path)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    image_b64 = _extract_keyframe(path)

    if not api_key or not image_b64:
        return _mock_analyze(str(path))

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            [
                PROMPT,
                {"mime_type": "image/jpeg", "data": base64.b64decode(image_b64)},
            ]
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text)
    except Exception:
        return _mock_analyze(str(path))


def vision_confidence_for_evasion(video_path: str | Path, evasion_types: list[str]) -> float:
    result = analyze_evasion_frame(video_path)
    base = float(result.get("confidence", 0.5))
    if evasion_types:
        if result.get("split_screen") and "split_screen" in evasion_types:
            base = max(base, 0.85)
        if result.get("inverted") and "flipped" in evasion_types:
            base = max(base, 0.8)
        if result.get("game_overlay") and "split_screen" in evasion_types:
            base = max(base, 0.9)
        if result.get("speed_changed") and "speed_changed" in evasion_types:
            base = max(base, 0.82)
        if result.get("cropped") and "cropped" in evasion_types:
            base = max(base, 0.8)
    return min(base, 1.0)


SECONDARY_PROMPT = """You are a copyright analyst. Given a video frame, determine if this is likely
an unauthorized copy of commercial VOD content with evasion (flip, crop, speed change, split screen).
Return ONLY valid JSON:
{
  "is_infringement": false,
  "confidence": 0.0,
  "description": "..."
}"""


def secondary_review(video_path: str | Path, preliminary_score: float) -> dict[str, Any]:
    """Gemini secondary review for scores in the review band."""
    path = Path(video_path)
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    image_b64 = _extract_keyframe(path)

    if not api_key or not image_b64:
        return _mock_secondary(str(path), preliminary_score)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            [
                SECONDARY_PROMPT,
                {"mime_type": "image/jpeg", "data": base64.b64decode(image_b64)},
            ]
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
        return json.loads(text)
    except Exception:
        return _mock_secondary(str(path), preliminary_score)


def _mock_secondary(seed: str, score: float) -> dict[str, Any]:
    lowered = seed.lower()
    evasion = any(x in lowered for x in ("evasion", "flip", "pitch", "speed", "crop", "split"))
    return {
        "is_infringement": evasion or score >= 0.72,
        "confidence": 0.82 if evasion else 0.45,
        "description": f"mock secondary review for {Path(seed).name}",
    }


def _mock_analyze(seed: str) -> dict[str, Any]:
    lowered = seed.lower()
    split = "split" in lowered or "game" in lowered
    flipped = "flip" in lowered or "mirror" in lowered
    pitch = "pitch" in lowered
    speed = "speed" in lowered
    crop = "crop" in lowered
    return {
        "split_screen": split,
        "game_overlay": split,
        "inverted": flipped,
        "pitch_shifted": pitch,
        "speed_changed": speed,
        "cropped": crop,
        "confidence": 0.75 if (split or flipped or pitch or speed or crop) else 0.3,
        "description": "mock vision analysis",
    }
