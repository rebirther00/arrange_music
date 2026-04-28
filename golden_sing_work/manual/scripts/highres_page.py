"""Re-render a single page of the source PDF at higher DPI for finer note inspection.

Usage:
    python highres_page.py <page_num> [<dpi>]
"""
from __future__ import annotations

import sys
from pathlib import Path

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "golden_sing_note_clean.pdf"
OUT_DIR = Path(__file__).resolve().parents[1] / "rendered" / "highres_pages"


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    page = int(sys.argv[1])
    dpi = int(sys.argv[2]) if len(sys.argv) > 2 else 400

    if not PDF.exists():
        sys.exit(f"missing pdf: {PDF}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(PDF)
    if page < 1 or page > len(doc):
        sys.exit(f"page out of range 1..{len(doc)}")
    pg = doc[page - 1]
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    pix = pg.get_pixmap(matrix=mat, alpha=False)
    out = OUT_DIR / f"page_{page:02d}_dpi{dpi}.png"
    pix.save(str(out))
    print(f"[OK] page {page} @ {dpi} dpi -> {out} ({pix.width}x{pix.height})")


if __name__ == "__main__":
    main()
