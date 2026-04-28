"""Stitch source crop + rendered chunk side-by-side for visual diff.

Crops the rendered chunk PNG to just the music region (auto-detect or by
explicit fractions), then aligns both at similar effective size for diff.

Usage:
    python compare_side.py <source_crop_filename> <rendered_basename> [<ren_y_top>] [<ren_y_bot>]

Example:
    python compare_side.py page02_sys1_FULL_HD.png mm001-003-1.png 0.10 0.45
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "rendered" / "source_crops"
RENDERED_DIR = ROOT / "rendered"
OUT_DIR = ROOT / "rendered" / "compare"


def auto_crop_white(img: Image.Image, pad: int = 30) -> Image.Image:
    """Trim large empty white margins; keep small padding."""
    bg = Image.new("RGB", img.size, "white")
    diff = ImageChops.difference(img.convert("RGB"), bg)
    bbox = diff.getbbox()
    if bbox:
        x0, y0, x1, y1 = bbox
        x0 = max(0, x0 - pad)
        y0 = max(0, y0 - pad)
        x1 = min(img.width, x1 + pad)
        y1 = min(img.height, y1 + pad)
        return img.crop((x0, y0, x1, y1))
    return img


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)

    src = SRC_DIR / sys.argv[1]
    ren = RENDERED_DIR / sys.argv[2]

    if not src.exists():
        sys.exit(f"missing source crop: {src}")
    if not ren.exists():
        sys.exit(f"missing rendered: {ren}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    a = Image.open(src).convert("RGB")
    b_full = Image.open(ren).convert("RGB")

    # Crop the rendered to a sub-region
    if len(sys.argv) >= 5:
        y_top = float(sys.argv[3])
        y_bot = float(sys.argv[4])
        h = b_full.height
        b = b_full.crop((0, int(h * y_top), b_full.width, int(h * y_bot)))
    else:
        # Auto-trim white margins
        b = auto_crop_white(b_full, pad=40)

    # Match heights — rescale rendered to source crop's height
    target_h = a.height
    b = b.resize((int(b.width * target_h / b.height), target_h))

    gap = 30
    canvas = Image.new("RGB", (a.width + gap + b.width, target_h), "white")
    canvas.paste(a, (0, 0))
    canvas.paste(b, (a.width + gap, 0))

    out = OUT_DIR / f"cmp__{Path(sys.argv[1]).stem}__{Path(sys.argv[2]).stem}.png"
    canvas.save(out)
    print(f"[OK] {out} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()
