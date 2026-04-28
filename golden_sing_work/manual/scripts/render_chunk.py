"""Render a chunk MusicXML with MuseScore CLI to PNG / MIDI / MP3.

Usage:
    python render_chunk.py chunks/mm001-003.musicxml [--no-mp3]
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / "chunks"
RENDERED = ROOT / "rendered"
AUDIO = ROOT / "audio"
MUSESCORE = Path(r"C:\Program Files\MuseScore 4\bin\MuseScore4.exe")


def run(cmd: list[str]) -> None:
    print("[CMD]", " ".join(f'"{c}"' if " " in c else c for c in cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + "\n" + proc.stderr + "\n")
        raise SystemExit(f"command failed: {proc.returncode}")


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)

    mxl_path = Path(sys.argv[1])
    if not mxl_path.is_absolute():
        mxl_path = (Path.cwd() / mxl_path).resolve()
    if not mxl_path.exists():
        # try CHUNKS
        cand = CHUNKS / mxl_path.name
        if cand.exists():
            mxl_path = cand
        else:
            sys.exit(f"not found: {mxl_path}")

    skip_mp3 = "--no-mp3" in sys.argv

    if not MUSESCORE.exists():
        sys.exit(f"MuseScore not found at {MUSESCORE}")

    RENDERED.mkdir(parents=True, exist_ok=True)
    AUDIO.mkdir(parents=True, exist_ok=True)

    stem = mxl_path.stem
    png_target = RENDERED / f"{stem}.png"  # MuseScore writes {stem}-1.png, {stem}-2.png …
    mid_target = AUDIO / f"{stem}.mid"
    mp3_target = AUDIO / f"{stem}.mp3"

    # PNG (sheet image)
    run([str(MUSESCORE), str(mxl_path), "-o", str(png_target)])
    # MIDI
    run([str(MUSESCORE), str(mxl_path), "-o", str(mid_target)])
    # MP3
    if not skip_mp3:
        run([str(MUSESCORE), str(mxl_path), "-o", str(mp3_target)])

    # Show what we produced
    print()
    print("[RENDERED]")
    for p in sorted(RENDERED.glob(f"{stem}*")):
        print("  ", p)
    for p in sorted(AUDIO.glob(f"{stem}*")):
        print("  ", p)


if __name__ == "__main__":
    main()
