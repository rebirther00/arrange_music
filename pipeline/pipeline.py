"""Music Arrangement Pipeline — orchestrator CLI.

Stages:
  init       create a new task.json template
  convert    PDF -> MusicXML (Audiveris)
  analyze    extract measure range from MusicXML, dump musical data
  compile    run versions/<vN>.py to produce vN.musicxml + vN.mid
  decide     parse reviews/<vN>_review.md, compute average, decide pass/fail
  export     final version -> PDF + MIDI + WAV + MP3 (MuseScore)
  status     show current pipeline state

Usage:
  python pipeline.py init [task.json]
  python pipeline.py convert <task.json>
  python pipeline.py analyze <task.json>
  python pipeline.py compile <task.json> <vN>
  python pipeline.py decide  <task.json> <vN>
  python pipeline.py export  <task.json> <vN>
  python pipeline.py status  <task.json>
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Force UTF-8 stdout/stderr on Windows for non-ASCII filenames
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

PIPELINE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = PIPELINE_DIR / "templates"

DEFAULT_TASK = {
    "input": {
        "pdf_path": "input.pdf",
        "movement": 1,
        "measure_range": [1, 16]
    },
    "arrangement": {
        "ensemble": "violin duet",
        "style": "Disney",
        "tempo_text": "Allegretto",
        "tempo_bpm": 104,
        "key": "C major"
    },
    "quality": {
        "passing_score": 85,
        "max_iterations": 5,
        "reviewers": [
            {"name": "Dr. Hans Müller",   "specialty": "Harmony / Theory",
             "criteria": ["harmonic progression", "voice leading", "preservation of original", "formal coherence"]},
            {"name": "Prof. Sarah Chen",  "specialty": "Performance / Chamber Music",
             "criteria": ["range", "playability", "ensemble balance", "idiomatic writing"]},
            {"name": "Prof. Alan Whitman", "specialty": "Film / Disney Arrangement",
             "criteria": ["style fidelity", "melodic appeal", "emotional arc", "creative reimagining"]}
        ]
    },
    "output": {
        "title": "An Arrangement",
        "subtitle": "after [Original Title]",
        "filename_prefix": "Arrangement",
        "formats": ["pdf", "midi", "wav", "mp3"]
    },
    "paths": {
        "audiveris_exe":   "C:\\Program Files\\Audiveris\\Audiveris.exe",
        "musescore_exe":   "C:\\Program Files\\MuseScore 4\\bin\\MuseScore4.exe",
        "tessdata_dir":    None,
        "ocr_languages":   ["ita", "eng", "deu"],
        "workspace":       "."
    }
}


# ---------------------------- utility ----------------------------
def load_task(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        die(f"Task file not found: {p}")
    return json.loads(p.read_text(encoding='utf-8'))


def save_task(task: dict, path: str | Path):
    Path(path).write_text(json.dumps(task, indent=2, ensure_ascii=False), encoding='utf-8')


def die(msg: str, code: int = 1):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(code)


def info(msg: str):
    print(f"[INFO]  {msg}")


def ok(msg: str):
    print(f"[ OK ]  {msg}")


def warn(msg: str):
    print(f"[WARN]  {msg}")


def workspace(task: dict) -> Path:
    return Path(task["paths"]["workspace"]).resolve()


def out_dirs(task: dict):
    ws = workspace(task)
    return {
        "convert":  ws / "output_full",
        "extracts": ws / "arrangement" / "extracts",
        "versions": ws / "arrangement" / "versions",
        "reviews":  ws / "arrangement" / "reviews",
        "final":    ws / "arrangement" / "final",
    }


# ---------------------------- init ----------------------------
def cmd_init(args):
    out = Path(args.task or "task.json")
    if out.exists() and not args.force:
        die(f"{out} exists. Use --force to overwrite.")
    save_task(DEFAULT_TASK, out)
    ok(f"Created template: {out}")
    print("\nNext steps:")
    print("  1) Edit the file: set 'input.pdf_path', 'arrangement.ensemble', 'arrangement.style'")
    print(f"  2) Run: python {Path(__file__).name} convert {out}")


# ---------------------------- convert ----------------------------
def cmd_convert(args):
    task = load_task(args.task)
    pdf_path = Path(task["input"]["pdf_path"]).resolve()
    if not pdf_path.exists():
        die(f"PDF not found: {pdf_path}")

    audiveris = task["paths"]["audiveris_exe"]
    if not Path(audiveris).exists():
        die(f"Audiveris not found at: {audiveris}\nInstall: winget install Audiveris")

    out_dir = out_dirs(task)["convert"]
    out_dir.mkdir(parents=True, exist_ok=True)

    langs = "+".join(task["paths"].get("ocr_languages", ["eng"]))
    info(f"Audiveris: {audiveris}")
    info(f"Input PDF: {pdf_path}")
    info(f"Output:    {out_dir}")
    info(f"OCR langs: {langs}")

    arglist = [
        audiveris,
        "-batch", "-transcribe", "-export",
        "-constant", f"org.audiveris.omr.text.Language.defaultSpecification={langs}",
        "-output", str(out_dir),
        "--", str(pdf_path),
    ]
    info("Running Audiveris (this can take several minutes for multi-page scores)...")
    t0 = datetime.now()
    res = subprocess.run(arglist, capture_output=True, text=True, encoding='utf-8', errors='replace')
    elapsed = (datetime.now() - t0).total_seconds()
    info(f"Done in {elapsed:.1f}s, exit={res.returncode}")
    if res.returncode != 0:
        warn("Non-zero exit. Last stderr lines:")
        for line in (res.stderr or "").splitlines()[-20:]:
            print("    " + line)

    mxl_files = sorted(out_dir.glob("*.mxl"))
    if not mxl_files:
        die("No .mxl files produced. Check Audiveris log in output folder.")
    print(f"\n{len(mxl_files)} MusicXML file(s) produced:")
    for f in mxl_files:
        size_kb = f.stat().st_size / 1024
        print(f"  {f.name}  ({size_kb:.1f} KB)")
    ok("Conversion complete.")


# ---------------------------- analyze ----------------------------
def cmd_analyze(args):
    """Verify converted MusicXML and dump the requested measure range."""
    task = load_task(args.task)
    mvt = task["input"].get("movement", 1)
    mr = task["input"].get("measure_range")  # [start, end] or None

    out_dir = out_dirs(task)["convert"]
    pdf_stem = Path(task["input"]["pdf_path"]).stem
    # Audiveris names: "<stem>.mvtN.mxl" or "<stem>.mxl" if single movement
    cand = sorted(out_dir.glob(f"*.mvt{mvt}.mxl")) + sorted(out_dir.glob("*.mxl"))
    cand = [c for c in cand if not c.name.endswith('.zip')]
    if not cand:
        die(f"No MusicXML found in {out_dir}. Run 'convert' first.")
    mxl = cand[0]
    info(f"Analyzing: {mxl.name}")

    from music21 import converter, key as keymod, meter, note as notemod, chord as chordmod
    score = converter.parse(str(mxl))
    parts = list(score.parts)
    info(f"Parts: {len(parts)}")

    # Time/Key check
    ts_list = list(score.recurse().getElementsByClass(meter.TimeSignature))[:3]
    ks_list = list(score.recurse().getElementsByClass(keymod.KeySignature))[:3]
    if ts_list:
        info(f"Time sig (first): {ts_list[0].ratioString}")
    if ks_list:
        info(f"Key sig  (first): {ks_list[0].sharps} sharps")

    # Measure count
    m_count = max(len(p.getElementsByClass('Measure')) for p in parts) if parts else 0
    info(f"Total measures: {m_count}")

    # Range to extract
    if not mr:
        mr = [1, m_count]
    start, end = mr[0], min(mr[1], m_count)
    info(f"Extracting mm.{start}-{end} into dump...")

    extracts = out_dirs(task)["extracts"]
    extracts.mkdir(parents=True, exist_ok=True)
    dump_path = extracts / f"mvt{mvt}_mm{start}-{end}_dump.txt"

    def fmt(n):
        if isinstance(n, notemod.Note):
            return f"{n.nameWithOctave}({n.duration.quarterLength:g})"
        if isinstance(n, chordmod.Chord):
            return f"<{'/'.join(p.nameWithOctave for p in n.pitches)}>({n.duration.quarterLength:g})"
        if isinstance(n, notemod.Rest):
            return f"R({n.duration.quarterLength:g})"
        return f"?{type(n).__name__}"

    def measure_seq(m):
        events = []
        if not m:
            return events
        if m.voices:
            for v in m.voices:
                for n in v.notesAndRests:
                    events.append((float(n.offset), n))
        else:
            for n in m.notesAndRests:
                events.append((float(n.offset), n))
        events.sort(key=lambda x: x[0])
        return events

    lines = []
    lines.append(f"# Source: {mxl.name}")
    lines.append(f"# Parts: {len(parts)}")
    if ts_list:
        lines.append(f"# Time: {ts_list[0].ratioString}")
    if ks_list:
        lines.append(f"# Key (first sig): {ks_list[0].sharps} sharps")
    lines.append(f"# Measure range: {start}-{end}")
    lines.append("")
    for mn in range(start, end + 1):
        for pi, p in enumerate(parts):
            m = p.measure(mn)
            seq = measure_seq(m)
            label = f"P{pi}" + (f"({p.partName})" if p.partName else "")
            lines.append(f"  {label} m{mn:>3}: " + " ".join(f"@{o:g}{fmt(n)}" for o, n in seq))
        lines.append("")

    dump_path.write_text("\n".join(lines), encoding='utf-8')
    ok(f"Dump saved: {dump_path}")

    # Empty measure detection
    print("\n--- Empty / suspicious measures (excluding voice-only) ---")
    for pi, p in enumerate(parts):
        empties = []
        for m in p.getElementsByClass('Measure'):
            if start <= m.number <= end:
                top = list(m.notesAndRests)
                if len(top) == 0 and not list(m.voices):
                    empties.append(m.number)
        print(f"  Part {pi}: empty measures in range = {empties or 'none'}")

    print("\nNext step:")
    print(f"  Read the dump and use Claude to write versions/v1.py based on:")
    print(f"    - {dump_path}")
    print(f"    - Arrangement spec: {task['arrangement']}")


# ---------------------------- compile ----------------------------
def cmd_compile(args):
    """Execute versions/<vN>.py which must call helpers.export_xml_midi(...)."""
    task = load_task(args.task)
    version = args.version
    versions_dir = out_dirs(task)["versions"]
    versions_dir.mkdir(parents=True, exist_ok=True)
    py = versions_dir / f"{version}.py"
    if not py.exists():
        die(f"Arrangement script not found: {py}\n"
            f"Have Claude write it (use templates/arrange.template.py as a guide).")
    info(f"Compiling: {py}")
    # Inject pipeline dir into sys.path so 'from helpers import ...' works
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PIPELINE_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    res = subprocess.run([sys.executable, str(py), str(args.task)],
                         env=env, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)
    if res.returncode != 0:
        die(f"Arrangement script failed (exit {res.returncode}).")
    expected_xml = versions_dir / f"{version}.musicxml"
    expected_mid = versions_dir / f"{version}.mid"
    if expected_xml.exists() and expected_mid.exists():
        ok(f"Arrangement compiled: {expected_xml.name}, {expected_mid.name}")
    else:
        warn("Expected output files not found. Did the script write to the correct path?")


# ---------------------------- decide ----------------------------
def cmd_decide(args):
    """Parse reviews/<vN>_review.md, extract per-reviewer scores, compute average."""
    task = load_task(args.task)
    version = args.version
    review_path = out_dirs(task)["reviews"] / f"{version}_review.md"
    if not review_path.exists():
        die(f"Review file not found: {review_path}\n"
            f"Have Claude write it (use templates/review.template.md as a guide).")

    text = review_path.read_text(encoding='utf-8')

    # Extract scores from rows containing "소계"/"Total"/"Subtotal".
    # Convention: such a row has bolded numbers like "**소계** | **100** | **89** | ...".
    # The 2nd bolded number is the actual score (1st is the max points 100).
    score_line_re = re.compile(r'(?:소계|total|sub[- ]?total)', re.IGNORECASE)
    # Capture bolded integers, allowing optional +/- prefix (so we can detect deltas)
    bold_num_re = re.compile(r'\*\*\s*([+\-]?\d{1,3})\s*\*\*')

    scores = []
    for line in text.splitlines():
        if not score_line_re.search(line):
            continue
        all_nums = bold_num_re.findall(line)
        # Filter out delta entries ("+8", "-3"). These belong to comparison columns.
        plain_nums = [int(n) for n in all_nums if not n.startswith(('+', '-'))]
        if len(plain_nums) < 2:
            # Only one bolded number found — treat as the score itself
            if plain_nums:
                scores.append(plain_nums[0])
            continue
        # Convention: 1st bolded = max points (e.g. 100), last = current score
        scores.append(plain_nums[-1])

    if not scores:
        die("Could not parse scores from review markdown.\n"
            "Ensure each '소계' row uses the format: '| **소계** | **100** | **NN** |'\n"
            "(2nd bolded number is the actual score).")

    avg = sum(scores) / len(scores)
    mn = min(scores)
    pass_score = task["quality"]["passing_score"]
    criterion = task["quality"].get("passing_criterion", "average").lower()
    print(f"\nReview: {review_path.name}")
    print(f"  Per-reviewer scores: {scores}")
    print(f"  Average: {avg:.1f}")
    print(f"  Minimum: {mn}")
    print(f"  Passing score: {pass_score}")
    print(f"  Criterion:    {criterion} (every reviewer >= passing_score = '{criterion}=='all'')")
    if criterion == "all":
        verdict = mn >= pass_score
        print(f"  Verdict: {'PASS' if verdict else 'FAIL'}  (min {mn} >= {pass_score})")
    else:
        verdict = avg >= pass_score
        print(f"  Verdict: {'PASS' if verdict else 'FAIL'}  (avg {avg:.1f} >= {pass_score})")
    if not verdict:
        gap = pass_score - (mn if criterion == "all" else avg)
        print(f"\nGap: {gap:.1f} points")
        next_v = f"v{int(version[1:])+1}" if version.startswith('v') and version[1:].isdigit() else "next"
        print(f"Next: have Claude write versions/{next_v}.py "
              f"addressing the lowest-scoring reviewer's feedback.")


# ---------------------------- export ----------------------------
def cmd_export(args):
    """Use MuseScore CLI to convert <vN>.musicxml -> PDF, MIDI, WAV, MP3."""
    task = load_task(args.task)
    version = args.version
    src = out_dirs(task)["versions"] / f"{version}.musicxml"
    if not src.exists():
        die(f"Source MusicXML not found: {src}")

    musescore = task["paths"]["musescore_exe"]
    if not Path(musescore).exists():
        die(f"MuseScore not found at: {musescore}\nInstall: winget install Musescore.Musescore")

    final = out_dirs(task)["final"]
    final.mkdir(parents=True, exist_ok=True)
    prefix = task["output"]["filename_prefix"]
    formats = task["output"]["formats"]

    info(f"Source: {src.name}")
    info(f"Output: {final}")
    info(f"Formats: {formats}")

    success = []
    for ext in formats:
        ext = ext.lower()
        if ext not in {'pdf', 'midi', 'mid', 'wav', 'mp3'}:
            warn(f"Skipping unknown format: {ext}")
            continue
        out_ext = 'mid' if ext == 'midi' else ext
        out_file = final / f"{prefix}.{out_ext}"
        info(f"Exporting {ext} -> {out_file.name}")
        res = subprocess.run([musescore, "-o", str(out_file), str(src)],
                             capture_output=True, text=True, encoding='utf-8', errors='replace')
        if res.returncode == 0 and out_file.exists():
            ok(f"  {out_file.name} ({out_file.stat().st_size/1024:.1f} KB)")
            success.append(out_file.name)
        else:
            warn(f"  failed (exit {res.returncode}): {res.stderr.strip()[:200]}")

    print(f"\nFinal outputs in: {final}")
    for f in sorted(final.iterdir()):
        if f.is_file():
            print(f"  {f.name}  ({f.stat().st_size/1024:.1f} KB)")


# ---------------------------- status ----------------------------
def cmd_status(args):
    task = load_task(args.task)
    print(f"Task: {Path(args.task).resolve()}")
    print(f"Input PDF: {task['input']['pdf_path']}")
    print(f"Arrangement: {task['arrangement']['ensemble']} / {task['arrangement']['style']}")
    print(f"Passing score: {task['quality']['passing_score']}\n")
    dirs = out_dirs(task)
    for label, d in dirs.items():
        present = sorted(p.name for p in d.iterdir()) if d.exists() else []
        marker = "X" if present else " "
        print(f"  [{marker}] {label:9s} {d}")
        for f in present[:8]:
            print(f"        - {f}")
        if len(present) > 8:
            print(f"        ... +{len(present)-8} more")


# ---------------------------- main ----------------------------
def main():
    ap = argparse.ArgumentParser(description="Music Arrangement Pipeline")
    sub = ap.add_subparsers(dest='cmd', required=True)

    p_init = sub.add_parser('init', help='create new task.json template')
    p_init.add_argument('task', nargs='?', default='task.json')
    p_init.add_argument('--force', action='store_true')
    p_init.set_defaults(func=cmd_init)

    p_conv = sub.add_parser('convert', help='PDF -> MusicXML (Audiveris)')
    p_conv.add_argument('task')
    p_conv.set_defaults(func=cmd_convert)

    p_an = sub.add_parser('analyze', help='Inspect MusicXML, dump measure range')
    p_an.add_argument('task')
    p_an.set_defaults(func=cmd_analyze)

    p_co = sub.add_parser('compile', help='Run versions/<vN>.py to build vN.musicxml')
    p_co.add_argument('task')
    p_co.add_argument('version')
    p_co.set_defaults(func=cmd_compile)

    p_de = sub.add_parser('decide', help='Parse review .md, compute pass/fail')
    p_de.add_argument('task')
    p_de.add_argument('version')
    p_de.set_defaults(func=cmd_decide)

    p_ex = sub.add_parser('export', help='Final outputs (PDF/MIDI/WAV/MP3)')
    p_ex.add_argument('task')
    p_ex.add_argument('version')
    p_ex.set_defaults(func=cmd_export)

    p_st = sub.add_parser('status', help='Show pipeline state')
    p_st.add_argument('task')
    p_st.set_defaults(func=cmd_status)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
