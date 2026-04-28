"""V1: demon_hunters -> 9-part ensemble (faithful, melody distributed across instruments).

Source parts (from OMR):
  P_VOX = Voice (Oohs)  — main melody
  P_RH  = Piano right hand — harmony / inner voicings
  P_LH  = Piano left hand  — bass

Distribution plan (mm.9-74; mm.1-8 and 75-82 are intro/outro rests):
  Phrase 1 (mm. 9-16): Cl  solo
  Phrase 2 (mm.17-24): Vn1 solo
  Phrase 3 (mm.25-32): Fl  solo
  Phrase 4 (mm.33-40): Va  solo
  Phrase 5 (mm.41-48): Vn2 solo
  Phrase 6 (mm.49-57): Vc  solo
  Phrase 7 (mm.58-65): Vn1 + Fl unison (climax)
  Phrase 8 (mm.66-74): Tutti melody (Vn1+Vn2+Fl+Cl)

Piano keeps original RH/LH harmony exactly.
Cb doubles LH bass (octave-fitted).
Drums lay a 12/8 rock-ballad pattern (mm.9-74).
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
P_VOX, P_RH, P_LH = list(src.parts)[:3]

# ---- Music settings (original key/time preserved; tempo: faithful default) ----
KEY_SHARPS = 1
TIME_SIG = "12/8"
BAR_QL = 6.0
TEMPO_TEXT = "Andante (faithful tempo)"
TEMPO_BPM = 80
TEMPO_REFERENT_QL = 1.5    # dotted quarter

# ---- Helpers ----
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


def transpose_octave(events, octaves):
    out = []
    for e in events:
        if isinstance(e, nmod.Note):
            new_p = e.pitch.transpose(12 * octaves)
            out.append(N(new_p.nameWithOctave, e.duration.quarterLength))
        elif isinstance(e, cmod.Chord):
            new_pitches = [p.transpose(12 * octaves) for p in e.pitches]
            out.append(CH([p.nameWithOctave for p in new_pitches], e.duration.quarterLength))
        else:
            out.append(clone(e))
    return out


def normalize(events, target=BAR_QL):
    total = sum(float(e.duration.quarterLength) for e in events)
    if abs(total - target) < 0.001:
        return [clone(e) for e in events]
    if total < target:
        return [clone(e) for e in events] + [R(target - total)]
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


def shift_to_range(events, lo, hi, max_tries=4):
    pitches = []
    for e in events:
        if isinstance(e, nmod.Note):
            pitches.append(e.pitch.midi)
        elif isinstance(e, cmod.Chord):
            pitches.extend(p.midi for p in e.pitches)
    if not pitches:
        return events
    cur_lo, cur_hi = min(pitches), max(pitches)
    shift = 0
    for _ in range(max_tries):
        if cur_lo + 12 * shift < lo:
            shift += 1
        elif cur_hi + 12 * shift > hi:
            shift -= 1
        else:
            break
    if shift == 0:
        return events
    return transpose_octave(events, shift)


# ---- Melody distribution (faithful = original Voice/Oohs notes per bar) ----
MELODY_BY_BAR = {}
for mn in range(9, 17):    MELODY_BY_BAR[mn] = ['Cl']
for mn in range(17, 25):   MELODY_BY_BAR[mn] = ['Vn1']
for mn in range(25, 33):   MELODY_BY_BAR[mn] = ['Fl']
for mn in range(33, 41):   MELODY_BY_BAR[mn] = ['Va']
for mn in range(41, 49):   MELODY_BY_BAR[mn] = ['Vn2']
for mn in range(49, 58):   MELODY_BY_BAR[mn] = ['Vc']
for mn in range(58, 66):   MELODY_BY_BAR[mn] = ['Vn1', 'Fl']
for mn in range(66, 75):   MELODY_BY_BAR[mn] = ['Vn1', 'Vn2', 'Fl', 'Cl']

INST_RANGES = {
    'Vn1': (55, 96),
    'Vn2': (55, 91),
    'Va':  (48, 84),
    'Vc':  (36, 76),
    'Fl':  (60, 96),
    'Cl':  (52, 88),
}


def build_melody_part(label):
    data = {}
    lo, hi = INST_RANGES[label]
    for mn in range(1, 83):
        if mn in MELODY_BY_BAR and label in MELODY_BY_BAR[mn]:
            mel = [clone(n) for _, n in measure_events(P_VOX, mn)]
            mel = normalize(mel)
            mel = shift_to_range(mel, lo, hi)
            data[mn] = normalize(mel)
        else:
            data[mn] = [R(BAR_QL)]
    return data


vn1_data = build_melody_part('Vn1')
vn2_data = build_melody_part('Vn2')
va_data  = build_melody_part('Va')
vc_data  = build_melody_part('Vc')
fl_data  = build_melody_part('Fl')
cl_data  = build_melody_part('Cl')

# ---- Piano: original RH/LH preserved ----
pno_rh_data, pno_lh_data = {}, {}
for mn in range(1, 83):
    rh_evs = [clone(n) for _, n in measure_events(P_RH, mn)]
    lh_evs = [clone(n) for _, n in measure_events(P_LH, mn)]
    pno_rh_data[mn] = normalize(rh_evs) if rh_evs else [R(BAR_QL)]
    pno_lh_data[mn] = normalize(lh_evs) if lh_evs else [R(BAR_QL)]

# ---- Cb: LH octave-fitted to Cb range ----
cb_data = {}
for mn in range(1, 83):
    lh = measure_events(P_LH, mn)
    if has_pitched(lh):
        events = [clone(n) for _, n in lh]
        events = shift_to_range(events, 28, 60)   # Cb playable: E1..C4
        cb_data[mn] = normalize(events)
    else:
        cb_data[mn] = [R(BAR_QL)]

# ---- Drums: 12/8 rock-ballad pattern (kick on 1+3, snare on 2+4 dotted-quarter beats) ----
def drum_bar():
    """12/8 drum pattern as eighth-note grid:
       beat 1: kick + hat-hat-hat
       beat 2: snare + hat-hat-hat
       beat 3: kick + hat-hat-hat
       beat 4: snare + hat-hat-hat
    Use percussion-staff pitches: kick=B2, snare=C4, hat=A4 (placeholder; MuseScore renders as drum staff)
    """
    out = []
    pattern = [
        ('kick', 'hat', 'hat'),
        ('snare', 'hat', 'hat'),
        ('kick', 'hat', 'hat'),
        ('snare', 'hat', 'hat'),
    ]
    pitches = {'kick': 'B2', 'snare': 'C4', 'hat': 'A4'}
    for beat in pattern:
        for tok in beat:
            out.append(N(pitches[tok], 0.5))
    return out

drum_data = {}
for mn in range(1, 83):
    drum_data[mn] = drum_bar() if 9 <= mn < 75 else [R(BAR_QL)]


# ---- Build parts ----
common_kwargs = dict(
    key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
    measures_per_bar_ql=BAR_QL, fermata_on_last=False,
)

# Vn1 carries tempo mark (first stave at top of score)
vn1 = make_part("Violin 1", "Vn 1", "violin", vn1_data,
                tempo_text=TEMPO_TEXT, tempo_bpm=TEMPO_BPM,
                tempo_referent_ql=TEMPO_REFERENT_QL,
                **common_kwargs)
vn2 = make_part("Violin 2", "Vn 2", "violin", vn2_data, **common_kwargs)
va  = make_part("Viola",   "Va",   "viola",  va_data,  clef_obj=clefmod.AltoClef(), **common_kwargs)
vc  = make_part("Violoncello", "Vc", "cello", vc_data, clef_obj=clefmod.BassClef(), **common_kwargs)
cb  = make_part("Contrabass", "Cb", "doublebass", cb_data, clef_obj=clefmod.BassClef(), **common_kwargs)
fl  = make_part("Flute",    "Fl",  "flute",    fl_data, **common_kwargs)
cl  = make_part("Clarinet", "Cl",  "clarinet", cl_data, **common_kwargs)
pno_rh = make_part("Piano (R.H.)", "Pf", "piano", pno_rh_data, **common_kwargs)
pno_lh = make_part("Piano (L.H.)", "Pf", "piano", pno_lh_data,
                   clef_obj=clefmod.BassClef(), **common_kwargs)
drm = make_part("Drums", "Dr", "drums", drum_data,
                clef_obj=clefmod.PercussionClef(), **common_kwargs)

# Range check (warn-only)
for p_obj, key in [(vn1, 'violin'), (vn2, 'violin'), (va, 'viola'),
                   (vc, 'cello'), (cb, 'doublebass'), (fl, 'flute'),
                   (cl, 'clarinet')]:
    bad = check_range(p_obj, INSTRUMENTS[key][1])
    if bad:
        print(f"[RANGE WARN] {p_obj.partName}: {len(bad)} OOR (first 5: {bad[:5]})")
    else:
        print(f"[RANGE OK]   {p_obj.partName}")

# Score order: winds → strings → bass → piano → drums (cinematic standard)
score = make_score(
    title=TASK["output"]["title"],
    subtitle=TASK["output"]["subtitle"],
    composer="(original)",
    arranger="arr. for 9-part ensemble (faithful, melody rotated)",
    parts=[fl, cl, vn1, vn2, va, vc, cb, pno_rh, pno_lh, drm],
    group_label="9-Part Ensemble",
    group_symbol="bracket",
)

xml_path, mid_path = export_xml_midi(score, OUT_DIR, VERSION)
print(f"\n=== {VERSION} GENERATED ===")
print(f"  MusicXML: {xml_path}")
print(f"  MIDI:     {mid_path}")
for entry in summarize_score(score):
    print(f"  {entry['part']}: {entry['measures']} mm, {entry['events']} events, "
          f"range {entry['range'][0]}-{entry['range'][1]}")
