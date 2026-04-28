"""Crop a region from a page PNG for closer inspection.

Usage:
    python crop_system.py <page_num> <y_top> <y_bot> [<out_name>] [<x_left>] [<x_right>] [--hires|--lo]

Coordinates are fractions of page dimensions (0.0..1.0).
- 3 args (page, y_top, y_bot): full-width band
- 4 args (+ out_name): full-width band with custom name
- 6 args (+ x_left, x_right): rectangular crop with custom name
- --hires (default): use rendered/highres_pages/page_NN_dpi400.png  (run highres_page.py first)
- --lo: use clean_pages/page_NN.png

Output written to manual/rendered/source_crops/.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
LO_DIR = ROOT / "clean_pages"
HI_DIR = Path(__file__).resolve().parents[1] / "rendered" / "highres_pages"
OUT_DIR = Path(__file__).resolve().parents[1] / "rendered" / "source_crops"


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]
    use_lo = "--lo" in flags

    if len(args) < 3:
        print(__doc__)
        sys.exit(2)
    page = int(args[0])
    y_top = float(args[1])
    y_bot = float(args[2])
    out_name = args[3] if len(args) > 3 else f"page{page:02d}_{int(y_top*100):03d}_{int(y_bot*100):03d}.png"
    x_left = float(args[4]) if len(args) > 4 else 0.0
    x_right = float(args[5]) if len(args) > 5 else 1.0

    if use_lo:
        src = LO_DIR / f"page_{page:02d}.png"
    else:
        src = HI_DIR / f"page_{page:02d}_dpi400.png"
        if not src.exists():
            # fallback to lo-res
            src = LO_DIR / f"page_{page:02d}.png"
    if not src.exists():
        print(f"[ERR] missing source: {src}")
        sys.exit(1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    img = Image.open(src)
    w, h = img.size
    box = (int(w * x_left), int(h * y_top), int(w * x_right), int(h * y_bot))
    crop = img.crop(box)
    out = OUT_DIR / out_name
    crop.save(out)
    print(f"[OK] page {page} y=[{y_top:.3f},{y_bot:.3f}] x=[{x_left:.3f},{x_right:.3f}] -> {out} ({crop.size[0]}x{crop.size[1]})")


if __name__ == "__main__":
    main()
