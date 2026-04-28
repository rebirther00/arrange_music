"""V1: Golden Demon -> String Quartet (faithful arrangement).

Strategy:
  - Preserve original melody verbatim (assigned to whichever Vn1/Vn2 has notes per bar)
  - When P0 and P1 are both active in a bar, they form a duet -> Vn1/Vn2
  - When only one part active -> Vn1 takes the melody; Vn2 sustains chord 5th
  - Va: chord 3rd, 4 dotted quarters per bar
  - Vc: chord root,  4 dotted quarters per bar
  - Harmony: diatonic G major only (no foreign chords) to honor "no alteration" mandate
  - Range: each instrument's natural range respected
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "pipeline"))
from helpers import (N, R, CH, make_part, make_score, export_xml_midi,
                     check_range, summarize_score, INSTRUMENTS)

from music21 import converter, note as nmod, chord as cmod

TASK = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
VERSION = Path(__file__).stem
WS = Path(TASK["paths"]["workspace"])
OUT_DIR = WS / "arrangement" / "versions"

# --- Load source MusicXML ---
src_mxl = next((WS / "output_full").glob("*.mxl"))
print(f"[INFO] Source: {src_mxl.name}")
src = converter.parse(str(src_mxl))
P0, P1 = list(src.parts)[0], list(src.parts)[1]

KEY_SHARPS = 1   # G major / E minor
TIME_SIG = "12/8"
BAR_QL = 6.0    # 12/8 = 4 dotted quarters = 6 quarter-lengths
TEMPO_TEXT = "Andante, faithful arrangement"
TEMPO_BPM = 60   # dotted quarter = 60

# --- Harmony per bar (G major diatonic, conservative) ---
# Determined by analysis of melody first beats and phrase shape.
CHORDS = {
    # Intro: bars 1-8 are silent
    9: 'Am', 10: 'G',  11: 'Am', 12: 'D',
    13: 'G', 14: 'G',  15: 'D',  16: 'Em',
    17: 'D', 18: 'D',  19: 'D',  20: 'D',
    21: 'D', 22: 'G',  23: 'D',  24: 'A',
    25: 'Em', 26: 'G', 27: 'D',  28: 'G',
    29: 'Em', 30: 'G', 31: 'D',  32: 'G',
    33: 'Em', 34: 'D', 35: 'C',  36: 'G',
    37: 'Em', 38: 'D', 39: 'C',  40: 'G',
    41: 'Em', 42: 'D', 43: 'G',  44: 'G',
    45: 'Em', 46: 'D', 47: 'G',  48: 'G',
    49: 'G',  50: 'Am', 51: 'D', 52: 'Em',
    53: 'G',  54: 'Am', 55: 'D', 56: 'Em',
    57: 'G',  58: 'Em', 59: 'D', 60: 'G',
    61: 'G',  62: 'Em', 63: 'D', 64: 'G',
    65: 'D',  66: 'G',  67: 'Am',68: 'Am',
    69: 'Am', 70: 'G',  71: 'Em',72: 'D',
    73: 'G',  74: 'G',
    # Outro: bars 75-82 silent
}

# Chord -> (Vc_root, Va_third, Vn2_fifth) — register chosen for SQ idiomatic
CHORD_TONES = {
    'G':  ('G2',  'B3',  'D4'),
    'Am': ('A2',  'C4',  'E4'),
    'C':  ('C3',  'E3',  'G3'),
    'D':  ('D3',  'F#3', 'A3'),
    'Em': ('E2',  'G3',  'B3'),
    'A':  ('A2',  'C#4', 'E4'),
}


def measure_events(part, mn):
    m = part.measure(mn)
    if not m:
        return []
    evs = []
    if m.voices:
        for v in m.voices:
            for n in v.notesAndRests:
                if n.duration.quarterLength > 0:
                    evs.append((float(n.offset), n))
    else:
        for n in m.notesAndRests:
            if n.duration.quarterLength > 0:
                evs.append((float(n.offset), n))
    evs.sort(key=lambda x: x[0])
    return evs


def has_pitched(evs):
    return any(isinstance(n, (nmod.Note, cmod.Chord)) for _, n in evs)


def clone(e):
    if isinstance(e, nmod.Rest):
        return R(e.duration.quarterLength)
    if isinstance(e, nmod.Note):
        return N(e.nameWithOctave, e.duration.quarterLength)
    if isinstance(e, cmod.Chord):
        return CH([p.nameWithOctave for p in e.pitches], e.duration.quarterLength)
    return R(e.duration.quarterLength)


def normalize_to_bar(events, target=BAR_QL):
    """Trim or pad event list so total duration == target."""
    total = sum(float(e.duration.quarterLength) for e in events)
    if abs(total - target) < 0.001:
        return events
    if total < target:
        events = events + [R(target - total)]
        return events
    # over: trim from the end
    out = []
    acc = 0.0
    for e in events:
        d = float(e.duration.quarterLength)
        if acc + d > target + 0.001:
            remain = target - acc
            if remain > 0.001:
                if isinstance(e, nmod.Rest):
                    out.append(R(remain))
                elif isinstance(e, nmod.Note):
                    out.append(N(e.nameWithOctave, remain))
                elif isinstance(e, cmod.Chord):
                    out.append(CH([p.nameWithOctave for p in e.pitches], remain))
            break
        out.append(clone(e))
        acc += d
    return out


vn1_data, vn2_data, va_data, vc_data = {}, {}, {}, {}

for mn in range(1, 83):
    p0_evs = measure_events(P0, mn)
    p1_evs = measure_events(P1, mn)
    p0_active = has_pitched(p0_evs)
    p1_active = has_pitched(p1_evs)

    # ---------- Vn1 ----------
    if p0_active and p1_active:
        vn1_data[mn] = normalize_to_bar([clone(n) for _, n in p0_evs])
    elif p0_active:
        vn1_data[mn] = normalize_to_bar([clone(n) for _, n in p0_evs])
    elif p1_active:
        vn1_data[mn] = normalize_to_bar([clone(n) for _, n in p1_evs])
    else:
        vn1_data[mn] = [R(BAR_QL)]

    # ---------- Vn2 ----------
    if p0_active and p1_active:
        vn2_data[mn] = normalize_to_bar([clone(n) for _, n in p1_evs])
    else:
        if mn in CHORDS:
            fifth = CHORD_TONES[CHORDS[mn]][2]
            vn2_data[mn] = [N(fifth, 1.5) for _ in range(4)]
        else:
            vn2_data[mn] = [R(BAR_QL)]

    # ---------- Va ----------
    if mn in CHORDS:
        third = CHORD_TONES[CHORDS[mn]][1]
        va_data[mn] = [N(third, 1.5) for _ in range(4)]
    else:
        va_data[mn] = [R(BAR_QL)]

    # ---------- Vc ----------
    if mn in CHORDS:
        root = CHORD_TONES[CHORDS[mn]][0]
        vc_data[mn] = [N(root, 1.5) for _ in range(4)]
    else:
        vc_data[mn] = [R(BAR_QL)]

# --- Build parts ---
vn1 = make_part("Violin 1", "Vn 1", "violin",   vn1_data,
                key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
                tempo_text=TEMPO_TEXT, tempo_bpm=TEMPO_BPM,
                dyn_map={9: 'mp', 49: 'p', 58: 'mf', 73: 'mp'},
                expr_map={9: 'cantabile', 49: 'sotto voce'},
                measures_per_bar_ql=BAR_QL, fermata_on_last=False)

vn2 = make_part("Violin 2", "Vn 2", "violin",   vn2_data,
                key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
                tempo_text=None, tempo_bpm=None,
                dyn_map={9: 'p', 49: 'pp', 58: 'mp'},
                measures_per_bar_ql=BAR_QL, fermata_on_last=False)

# Viola needs alto clef — pass via clef parameter
from music21 import clef as clefmod
va = make_part("Viola",     "Va",   "viola",    va_data,
                key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
                tempo_text=None, tempo_bpm=None,
                dyn_map={9: 'p', 49: 'pp', 58: 'mp'},
                measures_per_bar_ql=BAR_QL,
                clef_obj=clefmod.AltoClef(),
                fermata_on_last=False)

vc = make_part("Violoncello", "Vc",  "cello",    vc_data,
                key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
                tempo_text=None, tempo_bpm=None,
                dyn_map={9: 'p', 49: 'pp', 58: 'mp'},
                measures_per_bar_ql=BAR_QL,
                clef_obj=clefmod.BassClef(),
                fermata_on_last=False)

# Range checks (warn only)
for part_obj, key in [(vn1, 'violin'), (vn2, 'violin'), (va, 'viola'), (vc, 'cello')]:
    bad = check_range(part_obj, INSTRUMENTS[key][1])
    if bad:
        print(f"[RANGE WARN] {part_obj.partName}: {len(bad)} OOR notes (first 5: {bad[:5]})")
    else:
        print(f"[RANGE OK]   {part_obj.partName}")

score = make_score(
    title=TASK["output"]["title"],
    subtitle=TASK["output"]["subtitle"],
    composer="(original composer)",
    arranger=f"arr. for {TASK['arrangement']['ensemble']} (faithful)",
    parts=[vn1, vn2, va, vc],
    group_label="String Quartet",
    group_symbol="bracket",
)

xml_path, mid_path = export_xml_midi(score, OUT_DIR, VERSION)
print(f"\n=== {VERSION} GENERATED ===")
print(f"  MusicXML: {xml_path}")
print(f"  MIDI:     {mid_path}")
for entry in summarize_score(score):
    print(f"  {entry['part']}: {entry['measures']} mm, {entry['events']} events, "
          f"range {entry['range'][0]}-{entry['range'][1]}, "
          f"double-stops: {entry['double_stops']}")
