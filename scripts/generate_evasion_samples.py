"""Generate evasion sample clips from reference video using ffmpeg."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF_DIR = ROOT / "data" / "reference_clips"
OUT_DIR = ROOT / "data" / "evasion_samples"


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _find_source() -> Path | None:
    for mp4 in sorted(REF_DIR.glob("*.mp4")):
        if not mp4.name.startswith("evasion_"):
            return mp4
    return None


def _run(cmd: list[str]) -> bool:
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=120, check=False)
        return r.returncode == 0
    except Exception:
        return False


def generate_samples() -> list[Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = _find_source()
    if not source:
        print("No reference clip found. Add data/reference_clips/original.mp4 first.")
        return _create_placeholder_samples()

    if not _ffmpeg_available():
        print("ffmpeg not found — creating placeholder copies")
        return _create_placeholder_samples(source)

    outputs: list[Path] = []

    flipped = OUT_DIR / "evasion_flipped.mp4"
    if _run(["ffmpeg", "-y", "-i", str(source), "-vf", "hflip", "-t", "30", str(flipped)]):
        outputs.append(flipped)

    pitch = OUT_DIR / "evasion_pitch.mp4"
    if _run(
        [
            "ffmpeg", "-y", "-i", str(source),
            "-af", "asetrate=44100*1.15,aresample=44100",
            "-t", "30", str(pitch),
        ]
    ):
        outputs.append(pitch)

    split = OUT_DIR / "evasion_split_game.mp4"
    if _run(
        [
            "ffmpeg", "-y", "-i", str(source),
            "-vf", "split[v1][v2];[v1]scale=iw:ih/2[v1s];[v2]scale=iw:ih/2,geq=r='255*sin(X/10)':g='128':b='64'[game];[v1s][game]vstack",
            "-t", "30", str(split),
        ]
    ):
        outputs.append(split)

    speed = OUT_DIR / "evasion_speed.mp4"
    if _run(
        [
            "ffmpeg", "-y", "-i", str(source),
            "-filter:v", "setpts=0.87*PTS",
            "-t", "30", str(speed),
        ]
    ):
        outputs.append(speed)

    crop = OUT_DIR / "evasion_crop.mp4"
    if _run(
        [
            "ffmpeg", "-y", "-i", str(source),
            "-vf", "crop=iw*0.8:ih*0.8,scale=iw:ih",
            "-t", "30", str(crop),
        ]
    ):
        outputs.append(crop)

    if not outputs:
        return _create_placeholder_samples(source)
    return outputs


def _create_placeholder_samples(source: Path | None = None) -> list[Path]:
    """Copy reference with evasion naming for mock detection."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    outputs: list[Path] = []
    if source and source.exists():
        for name in [
            "evasion_flipped.mp4",
            "evasion_pitch.mp4",
            "evasion_split_game.mp4",
            "evasion_speed.mp4",
            "evasion_crop.mp4",
        ]:
            dest = OUT_DIR / name
            shutil.copy2(source, dest)
            outputs.append(dest)
    else:
        # Minimal valid placeholder text files renamed — skip, use empty dir message
        print("Cannot create samples without reference video.")
    return outputs


def main() -> int:
    samples = generate_samples()
    print(f"Generated {len(samples)} evasion sample(s) in {OUT_DIR}")
    for s in samples:
        print(f"  - {s.name}")
    return 0 if samples else 1


if __name__ == "__main__":
    raise SystemExit(main())
