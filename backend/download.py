"""Download suspect media for fingerprinting."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
from urllib.parse import urlparse


def download_candidate(url: str, max_duration_sec: int = 60) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme == "file":
        from urllib.parse import unquote

        raw = unquote(parsed.path)
        if raw.startswith("/") and len(raw) > 2 and raw[2] == ":":
            raw = raw[1:]
        local = Path(raw)
        if local.exists():
            return local
        return None

    try:
        import yt_dlp

        out_dir = Path(tempfile.mkdtemp(prefix="legal_assassin_"))
        opts = {
            "format": "best[ext=mp4]/best",
            "outtmpl": str(out_dir / "%(id)s.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
            "download_sections": f"*0-{max_duration_sec}",
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
        files = list(out_dir.glob("*"))
        return files[0] if files else None
    except Exception:
        return None


def cleanup_download(path: Path) -> None:
    try:
        if path.parent.name.startswith("legal_assassin_"):
            shutil.rmtree(path.parent, ignore_errors=True)
    except Exception:
        pass
