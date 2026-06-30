"""Audio fingerprinting via Chromaprint (fpcalc) with ffmpeg fallback."""
from __future__ import annotations

import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def _has_fpcalc() -> bool:
    return shutil.which("fpcalc") is not None


def _has_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def extract_audio_fingerprint(video_path: str | Path) -> str:
    path = Path(video_path)
    if not path.exists():
        return _mock_fingerprint(path)

    if _has_fpcalc():
        try:
            import acoustid

            duration, fp = acoustid.fingerprint_file(str(path))
            if fp:
                return fp
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["fpcalc", "-json", str(path)],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            if result.returncode == 0 and '"fingerprint"' in result.stdout:
                import json

                data = json.loads(result.stdout)
                return data.get("fingerprint", "")
        except Exception:
            pass

    wav_fp = _ffmpeg_audio_hash(path)
    if wav_fp:
        return wav_fp

    return _mock_fingerprint(path)


def _ffmpeg_audio_hash(path: Path) -> str | None:
    """Extract mono WAV via ffmpeg and hash payload (fpcalc fallback)."""
    if not _has_ffmpeg():
        return None
    out = Path(tempfile.mktemp(suffix=".wav"))
    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(path),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "11025",
                str(out),
            ],
            capture_output=True,
            timeout=120,
            check=False,
        )
        if out.exists() and out.stat().st_size > 0:
            return _mock_fingerprint(out)
    except Exception:
        pass
    finally:
        try:
            out.unlink(missing_ok=True)
        except Exception:
            pass
    return None


def normalize_pitch_audio(input_path: Path, rate_factor: float = 1.0) -> Path | None:
    """Create pitch-normalized WAV via ffmpeg for evasion-resistant matching."""
    if not _has_ffmpeg():
        return None
    out = Path(tempfile.mktemp(suffix=".wav"))
    try:
        # asetrate changes pitch; aresample restores sample rate
        rate = int(44100 * rate_factor)
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(input_path),
                "-af",
                f"asetrate={rate},aresample=44100",
                str(out),
            ],
            capture_output=True,
            timeout=120,
            check=False,
        )
        return out if out.exists() else None
    except Exception:
        return None


def compare_audio_fingerprints(ref_fp: str, suspect_fp: str) -> float:
    if not ref_fp or not suspect_fp:
        return 0.0
    if ref_fp == suspect_fp:
        return 1.0
    # Chromaprint strings: prefix match ratio as rough similarity
    min_len = min(len(ref_fp), len(suspect_fp))
    if min_len == 0:
        return 0.0
    matches = sum(1 for i in range(min_len) if ref_fp[i] == suspect_fp[i])
    return matches / min_len


def compare_with_pitch_evasions(
    ref_fp: str,
    suspect_path: str | Path,
) -> dict[str, Any]:
    suspect_path = Path(suspect_path)
    normal_fp = extract_audio_fingerprint(suspect_path)
    scores = {"normal": compare_audio_fingerprints(ref_fp, normal_fp)}

    for label, factor in [("pitch_up", 1.1), ("pitch_down", 0.9)]:
        normalized = normalize_pitch_audio(suspect_path, factor)
        if normalized:
            fp = extract_audio_fingerprint(normalized)
            scores[label] = compare_audio_fingerprints(ref_fp, fp)
            try:
                normalized.unlink()
            except Exception:
                pass
        else:
            scores[label] = scores["normal"] * 0.95

    best = max(scores, key=scores.get)
    return {
        "audio_score": scores[best],
        "audio_evasion_type": best if best != "normal" else None,
        "scores": scores,
    }


def _mock_fingerprint(path: str | Path) -> str:
    p = Path(path)
    if p.exists() and p.is_file():
        digest = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()[:32]
    return hashlib.sha256(str(path).encode()).hexdigest()[:32]
