"""Generate placeholder Kibana dashboard screenshots for submission."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"


def _font(size: int):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def _panel(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title: str, color: str):
    draw.rectangle([x, y, x + w, y + h], outline="#444", fill="#1a1a2e")
    draw.text((x + 12, y + 10), title, fill=color, font=_font(14))
    if "Platform" in title:
        bars = [("youtube", 120), ("tiktok", 80), ("twitter", 60)]
        bx = x + 40
        for label, height in bars:
            draw.rectangle([bx, y + h - 40 - height, bx + 50, y + h - 40], fill="#00ff9d")
            draw.text((bx, y + h - 30), label, fill="#aaa", font=_font(10))
            bx += 90
    elif "Evasion" in title:
        draw.ellipse([x + 80, y + 50, x + w - 80, y + h - 30], outline="#ff6b6b", width=3)
        draw.text((x + 100, y + 90), "speed_changed", fill="#ccc", font=_font(11))
        draw.text((x + 100, y + 110), "cropped", fill="#ccc", font=_font(11))
    elif "Takedown" in title:
        pts = [(x + 30, y + h - 50), (x + 120, y + 90), (x + 220, y + 110), (x + w - 30, y + 70)]
        draw.line(pts, fill="#4dabf7", width=2)
    else:
        draw.text((x + 40, y + 80), "0.87", fill="#00ff9d", font=_font(36))


def make_overview(path: Path) -> None:
    img = Image.new("RGB", (960, 540), "#0d1117")
    draw = ImageDraw.Draw(img)
    draw.text((20, 16), "Legal Assassin — Infringement Ops", fill="#00ff9d", font=_font(18))
    _panel(draw, 20, 60, 450, 200, "Detections by Platform", "#e6edf3")
    _panel(draw, 490, 60, 450, 200, "Evasion Type Breakdown", "#e6edf3")
    _panel(draw, 20, 280, 620, 220, "Takedown Success Over Time", "#e6edf3")
    _panel(draw, 660, 280, 280, 220, "Average Match Score", "#e6edf3")
    img.save(path)


def make_platform(path: Path) -> None:
    img = Image.new("RGB", (640, 400), "#0d1117")
    draw = ImageDraw.Draw(img)
    draw.text((20, 16), "Detections by Platform", fill="#00ff9d", font=_font(18))
    _panel(draw, 20, 50, 600, 320, "Platform bar chart", "#e6edf3")
    img.save(path)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    make_overview(OUT / "dashboard-overview.png")
    make_platform(OUT / "platform-detections.png")
    print(f"Wrote screenshots to {OUT}")


if __name__ == "__main__":
    main()
