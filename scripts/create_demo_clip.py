"""Create a minimal demo reference clip (no external download required)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "reference_clips" / "original.mp4"


def main() -> int:
    try:
        import cv2
        import numpy as np
    except ImportError:
        print("opencv not installed")
        return 1

    OUT.parent.mkdir(parents=True, exist_ok=True)
    if OUT.exists():
        print(f"Already exists: {OUT}")
        return 0

    w, h, fps = 640, 360, 24
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(OUT), fourcc, fps, (w, h))

    for i in range(fps * 10):
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :, 0] = (i * 7) % 256
        frame[:, :, 1] = 100
        frame[:, :, 2] = 180
        cv2.putText(
            frame,
            f"LEGAL ASSASSIN REF {i // fps}s",
            (40, h // 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )
        writer.write(frame)

    writer.release()
    print(f"Created {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
