"""Auto-detect systems in a rendered MuseScore PNG and stitch them horizontally.

When MuseScore breaks a chunk into multiple systems, this combines them into
a single horizontal strip for side-by-side comparison with the source crop.

Usage:
    python stitch_systems.py <rendered_basename>

Output:
    rendered/<basename>__hstitch.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RENDERED_DIR = ROOT / "rendered"


def find_system_bands(arr: np.ndarray, ink_threshold: int = 200, min_band_height: int = 60, gap_threshold: int = 40) -> list[tuple[int, int]]:
    """Detect contiguous bands of rows that contain ink.

    Returns list of (y_start, y_end) for each detected system band.
    """
    # Per-row ink density: count of pixels that are darker than ink_threshold
    if arr.ndim == 3:
        gray = arr.mean(axis=2)
    else:
        gray = arr
    ink_per_row = (gray < ink_threshold).sum(axis=1)
    has_ink = ink_per_row > 5

    bands = []
    in_band = False
    start = 0
    last_ink_row = -1
    for y, hi in enumerate(has_ink):
        if hi:
            if not in_band:
                start = y
                in_band = True
            last_ink_row = y
        else:
            if in_band and (y - last_ink_row) > gap_threshold:
                if last_ink_row - start >= min_band_height:
                    bands.append((start, last_ink_row + 1))
                in_band = False
    if in_band and last_ink_row - start >= min_band_height:
        bands.append((start, last_ink_row + 1))
    return bands


def trim_horizontal(im: Image.Image, ink_threshold: int = 200, pad: int = 20) -> Image.Image:
    arr = np.array(im.convert("L"))
    cols_with_ink = np.where((arr < ink_threshold).any(axis=0))[0]
    if len(cols_with_ink) == 0:
        return im
    x0 = max(0, int(cols_with_ink[0]) - pad)
    x1 = min(im.width, int(cols_with_ink[-1]) + pad)
    return im.crop((x0, 0, x1, im.height))


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    in_path = RENDERED_DIR / sys.argv[1]
    if not in_path.exists():
        sys.exit(f"missing: {in_path}")

    im = Image.open(in_path).convert("RGB")
    arr = np.array(im)
    bands = find_system_bands(arr, gap_threshold=80)
    print(f"detected {len(bands)} systems: {bands}")

    if len(bands) <= 1:
        print("[note] only 0/1 system detected, copying through")
        out = RENDERED_DIR / f"{Path(sys.argv[1]).stem}__hstitch.png"
        im.save(out)
        return

    # Crop each system band, trim horizontally, then stitch horizontally
    crops = []
    for (y0, y1) in bands:
        c = im.crop((0, y0, im.width, y1))
        c = trim_horizontal(c, pad=15)
        crops.append(c)

    target_h = max(c.height for c in crops)
    # Resize each to same height (proportional)
    rescaled = [c.resize((int(c.width * target_h / c.height), target_h)) for c in crops]
    gap = 60
    total_w = sum(c.width for c in rescaled) + gap * (len(rescaled) - 1)
    canvas = Image.new("RGB", (total_w, target_h), "white")
    x = 0
    for c in rescaled:
        canvas.paste(c, (x, 0))
        x += c.width + gap

    out = RENDERED_DIR / f"{Path(sys.argv[1]).stem}__hstitch.png"
    canvas.save(out)
    print(f"[OK] {out} ({canvas.size[0]}x{canvas.size[1]})")


if __name__ == "__main__":
    main()
