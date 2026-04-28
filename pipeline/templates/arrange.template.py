"""Arrangement template — copy/adapt to versions/<vN>.py.

This script is invoked by `pipeline.py compile <task.json> <vN>` and is
expected to produce  versions/<vN>.musicxml  and  versions/<vN>.mid.

Claude (or human) fills in:
  1. vn1_data / vn2_data / etc. — measure-by-measure music
  2. Dynamics + expressions per measure
  3. Title metadata (override task.output.title if needed)

Usage by pipeline:
  python <this file> <task.json>
"""
import json
import sys
from pathlib import Path

# Make 'helpers' importable when invoked directly
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from helpers import (N, R, CH, make_part, make_score, export_xml_midi,
                     check_range, summarize_score, INSTRUMENTS, verify_durations)

# ----------- Read the task spec -----------
task_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("task.json")
TASK = json.loads(task_path.read_text(encoding='utf-8'))

VERSION = Path(__file__).stem      # e.g. "v1"
OUT_DIR = Path(TASK["paths"]["workspace"]) / "arrangement" / "versions"

# ===== Music key/time/tempo (override per arrangement intent) =====
KEY_SHARPS = 0                     # C major (use -1 for F, 1 for G, etc.)
TIME_SIG   = "2/4"                 # match the original or change for rearrangement
TEMPO_TEXT = TASK["arrangement"].get("tempo_text", "Allegretto")
TEMPO_BPM  = TASK["arrangement"].get("tempo_bpm", 104)
BAR_QL     = 2.0                   # quarterLength per bar (2/4 -> 2.0, 4/4 -> 4.0, etc.)

# ===== Per-part data: {measure_number: [events, ...]} =====
# Replace these with your actual arrangement.

vn1_data = {
    1: [N('G5', 0.5), N('G5', 0.75), N('F5', 0.125), N('E5', 0.125),
        N('E5', 0.125), N('D5', 0.125), N('C5', 0.125), N('B4', 0.125)],
    2: [N('C5', 0.75), N('D5', 0.125), N('E5', 0.125),
        N('F5', 0.25), N('E5', 0.25), N('D5', 0.25), N('C5', 0.25)],
    # ... continue measures 3..N
}

vn2_data = {
    1: [N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25),
        N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25)],
    2: [N('A3', 0.25), N('E4', 0.25), N('C4', 0.25), N('G4', 0.25),
        N('F4', 0.25), N('C4', 0.25), N('A3', 0.25), N('E4', 0.25)],
    # ... continue measures 3..N
}

# Dynamics map: {measure_num: 'pp'|'p'|'mp'|'mf'|'f'|'ff'}
vn1_dyn  = {1: 'mp', 7: 'mf', 12: 'f', 13: 'mp', 16: 'pp'}
vn2_dyn  = {1: 'p',  5: 'mp', 7: 'mf', 12: 'f', 13: 'mp', 16: 'pp'}

# Expression text (italic): {measure_num: 'cresc.'|'rit.'|...}
vn1_expr = {1: 'dolce', 7: 'cresc.', 13: 'dim. e poco rit.', 15: 'rit.', 16: 'lunga'}
vn2_expr = {5: 'cantabile', 13: 'dim. e poco rit.', 15: 'rit.'}

# ===== Build parts =====
vn1 = make_part(
    name="Violin 1", abbrev="Vn 1", instr_key="violin",
    data=vn1_data, key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
    tempo_text=f"{TEMPO_TEXT}, dolce", tempo_bpm=TEMPO_BPM,
    dyn_map=vn1_dyn, expr_map=vn1_expr,
    measures_per_bar_ql=BAR_QL,
)

vn2 = make_part(
    name="Violin 2", abbrev="Vn 2", instr_key="violin",
    data=vn2_data, key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
    tempo_text=f"{TEMPO_TEXT}, dolce", tempo_bpm=TEMPO_BPM,
    dyn_map=vn2_dyn, expr_map=vn2_expr,
    measures_per_bar_ql=BAR_QL,
)

# Range check (warn but do not fail by default)
for part_obj, (lo, hi) in [(vn1, INSTRUMENTS["violin"][1]), (vn2, INSTRUMENTS["violin"][1])]:
    bad = check_range(part_obj, (lo, hi))
    if bad:
        print(f"[RANGE WARNING] {part_obj.partName}: {bad[:5]}{' ...' if len(bad) > 5 else ''}")

# ===== Assemble score =====
score = make_score(
    title=TASK["output"]["title"],
    subtitle=TASK["output"]["subtitle"],
    composer="W.A. Mozart",        # change per source
    arranger=f"arr. for {TASK['arrangement']['ensemble']} ({TASK['arrangement']['style']})",
    parts=[vn1, vn2],
    group_label="Violin Duet",
    group_symbol="bracket",
)

# ===== Export =====
xml_path, mid_path = export_xml_midi(score, OUT_DIR, VERSION)
print(f"\n=== {VERSION} GENERATED ===")
print(f"  MusicXML: {xml_path}")
print(f"  MIDI:     {mid_path}")

# Summary
for entry in summarize_score(score):
    print(f"  {entry['part']}: {entry['measures']} mm, {entry['events']} events, "
          f"range {entry['range'][0]}-{entry['range'][1]}, "
          f"double-stops: {entry['double_stops']}")
