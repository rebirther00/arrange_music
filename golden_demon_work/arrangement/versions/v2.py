"""V2: Golden Demon -> String Quartet (faithful + chord-tone alternation).

V1 -> V2 changes (within 'no harmonic alteration' mandate):
  - Vc:  sustained root  -> root-5th-root-5th alternation (4 dotted quarters)
  - Va:  sustained 3rd   -> 3rd-5th-3rd-5th alternation
  - Vn2: sustained 5th   -> 5th-3rd-5th-3rd alternation (only when not echoing P1)
  - Dynamics: more nuanced (pp/p/mp/mf with cresc./dim. arcs)
  - Expression: cantabile, dolce, sotto voce markers per phrase
  - Coda fermata at m.74 (last sounding bar)
  - Pizzicato marker at bridge entry (m.49) for color
NO change to: melody notes, harmony chords, rhythm pattern, bar count, key, time.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "pipeline"))
from helpers import (N, R, CH, make_part, make_score, export_xml_midi,
                     check_range, summarize_score, INSTRUMENTS)

from music21 import converter, note as nmod, chord as cmod, clef as clefmod

TASK = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
VERSION = Path(__file__).stem
WS = Path(TASK["paths"]["workspace"])
OUT_DIR = WS / "arrangement" / "versions"

src_mxl = next((WS / "output_full").glob("*.mxl"))
print(f"[INFO] Source: {src_mxl.name}")
src = converter.parse(str(src_mxl))
P0, P1 = list(src.parts)[0], list(src.parts)[1]

KEY_SHARPS = 1
TIME_SIG = "12/8"
BAR_QL = 6.0
TEMPO_TEXT = "Allegro"
TEMPO_BPM = 123
TEMPO_REFERENT_QL = 1.5   # dotted quarter ( ♩. = 123 )

CHORDS = {
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
    65: 'D',  66: 'G',  67: 'Am', 68: 'Am',
    69: 'Am', 70: 'G',  71: 'Em', 72: 'D',
    73: 'G',  74: 'G',
}

# (root_low_VC, third_VA, fifth_VA, root_higher_VC)
CHORD_TONES = {
    'G':  ('G2',  'B3', 'D4',  'D3'),
    'Am': ('A2',  'C4', 'E4',  'E3'),
    'C':  ('C3',  'E3', 'G3',  'G3'),
    'D':  ('D2',  'F#3','A3',  'A2'),
    'Em': ('E2',  'G3', 'B3',  'B2'),
    'A':  ('A2',  'C#4','E4',  'E3'),
}

# Violin 2 uses higher register (must be >= G3 = MIDI 55) — third, fifth
CHORD_TONES_VN2 = {
    'G':  ('B3', 'D4'),
    'Am': ('C4', 'E4'),
    'C':  ('E4', 'G4'),
    'D':  ('F#4','A4'),
    'Em': ('G3', 'B3'),
    'A':  ('C#4','E4'),
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
    total = sum(float(e.duration.quarterLength) for e in events)
    if abs(total - target) < 0.001:
        return events
    if total < target:
        return events + [R(target - total)]
    out, acc = [], 0.0
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
    if p0_active:
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
            third_v2, fifth_v2 = CHORD_TONES_VN2[CHORDS[mn]]
            # Vn2 alternation: 5th, 3rd, 5th, 3rd  (chord tones, raised octave for violin range)
            vn2_data[mn] = [N(fifth_v2, 1.5), N(third_v2, 1.5), N(fifth_v2, 1.5), N(third_v2, 1.5)]
        else:
            vn2_data[mn] = [R(BAR_QL)]

    # ---------- Va ----------
    if mn in CHORDS:
        _, third, fifth, _ = CHORD_TONES[CHORDS[mn]]
        # 3rd-5th-3rd-5th — drop fifth one octave when too high vs 3rd
        # Simple register: keep both within Va comfortable range (C3-A5 typical)
        # third/fifth as defined are already in mid-register; OK.
        va_data[mn] = [N(third, 1.5), N(fifth, 1.5), N(third, 1.5), N(fifth, 1.5)]
    else:
        va_data[mn] = [R(BAR_QL)]

    # ---------- Vc ----------
    if mn in CHORDS:
        root_low, _, _, root_higher = CHORD_TONES[CHORDS[mn]]
        # root-fifth(or root_octave_up)-root-fifth alternation = "rocking" 12/8 bass
        vc_data[mn] = [N(root_low, 1.5), N(root_higher, 1.5), N(root_low, 1.5), N(root_higher, 1.5)]
    else:
        vc_data[mn] = [R(BAR_QL)]


# Dynamics + expressions: shape an arc across the piece
vn1_dyn  = {9:'mp', 17:'mf', 25:'mp', 33:'mf', 41:'f',  49:'p',  58:'mf', 65:'f', 71:'mp', 73:'pp'}
vn2_dyn  = {9:'p',  17:'mp', 33:'mp', 41:'mf', 49:'pp', 58:'mp', 65:'mf', 73:'pp'}
va_dyn   = {9:'p',  17:'mp', 33:'mp', 41:'mf', 49:'pp', 58:'mp', 65:'mf', 73:'pp'}
vc_dyn   = {9:'p',  17:'mp', 33:'mp', 41:'mf', 49:'pp', 58:'mp', 65:'mf', 73:'pp'}

vn1_expr = {9:'cantabile', 25:'dolce', 41:'cresc.', 49:'sotto voce', 58:'poco a poco cresc.', 73:'rit.'}
vn2_expr = {9:'',          49:'pizz.', 58:'arco',   73:'rit.'}
va_expr  = {9:'',          49:'pizz.', 58:'arco',   73:'rit.'}
vc_expr  = {9:'',          49:'pizz.', 58:'arco',   73:'rit.'}

# Build parts (fermata on m.74 = last sounding bar; m.75-82 are rests)
vn1 = make_part("Violin 1", "Vn 1", "violin", vn1_data,
                key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
                tempo_text=TEMPO_TEXT, tempo_bpm=TEMPO_BPM,
                tempo_referent_ql=TEMPO_REFERENT_QL,
                dyn_map=vn1_dyn, expr_map=vn1_expr,
                measures_per_bar_ql=BAR_QL, fermata_on_last=False)

vn2 = make_part("Violin 2", "Vn 2", "violin", vn2_data,
                key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
                dyn_map=vn2_dyn, expr_map=vn2_expr,
                measures_per_bar_ql=BAR_QL, fermata_on_last=False)

va = make_part("Viola", "Va", "viola", va_data,
                key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
                dyn_map=va_dyn, expr_map=va_expr,
                measures_per_bar_ql=BAR_QL,
                clef_obj=clefmod.AltoClef(), fermata_on_last=False)

vc = make_part("Violoncello", "Vc", "cello", vc_data,
                key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
                dyn_map=vc_dyn, expr_map=vc_expr,
                measures_per_bar_ql=BAR_QL,
                clef_obj=clefmod.BassClef(), fermata_on_last=False)

# Add fermata to last sounding bar (m.74) for each part
from music21 import expressions
for p in [vn1, vn2, va, vc]:
    m74 = p.measure(74)
    if m74 and m74.notesAndRests:
        m74.notesAndRests[-1].expressions.append(expressions.Fermata())

# Range checks
for part_obj, key in [(vn1, 'violin'), (vn2, 'violin'), (va, 'viola'), (vc, 'cello')]:
    bad = check_range(part_obj, INSTRUMENTS[key][1])
    if bad:
        print(f"[RANGE WARN] {part_obj.partName}: {len(bad)} OOR (first 5: {bad[:5]})")
    else:
        print(f"[RANGE OK]   {part_obj.partName}")

score = make_score(
    title=TASK["output"]["title"],
    subtitle=TASK["output"]["subtitle"] + " (V2)",
    composer="(original composer)",
    arranger=f"arr. for {TASK['arrangement']['ensemble']} (faithful — V2)",
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
