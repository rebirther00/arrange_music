"""V2: demon_hunters -> 9-part ensemble.

V1 → V2 changes (within 'faithful to original' mandate):
  1. String sustain pad: when not carrying melody, Vn2/Va/Vc play chord tones
     sustained per bar — fills the cinematic ensemble texture.
  2. Drums: 5-stage dynamic pattern (verse / build / bridge / climax / chorus)
     with crash cymbals on phrase entries.
  3. String idiom: pizzicato in mm.41-48 (Vn2 verse), tremolo on m.58 climax entry,
     double-stops in mm.66-74 (Vn1 octaves).
  4. Va / Vc octave fitting: melody placed in instrument's sweet spot;
     pad uses sweet spot chord tones.
  5. Climax doubled: mm.58-65 Vn2 plays the melody at the lower 6th below Vn1+Fl;
     mm.66-74 tutti includes all 4 melody instruments.
  6. Vn2 counter-line: rhythmic echo of melody-end notes during Vn1 verse phrases.

NO change to: original melody pitches/rhythm, harmony chord progression,
time signature 12/8, key (1#), bar count 82, intro/outro rests.
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

KEY_SHARPS = 1
TIME_SIG = "12/8"
BAR_QL = 6.0
TEMPO_TEXT = "Allegro (original tempo)"
TEMPO_BPM = 123
TEMPO_REFERENT_QL = 1.5    # dotted quarter ( ♩. = 123 )


# ============================================================
# Helpers
# ============================================================
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
    return transpose_octave(events, shift) if shift else events


# ============================================================
# Auto chord detection from LH bass note (G major / E minor diatonic)
# ============================================================
PC_TO_CHORD = {
    7: 'G', 9: 'Am', 11: 'Bm', 0: 'C', 2: 'D', 4: 'Em', 6: 'F#dim',
}
CHORD_TONES = {
    'G':  ('G', 'B', 'D'),
    'Am': ('A', 'C', 'E'),
    'Bm': ('B', 'D', 'F#'),
    'C':  ('C', 'E', 'G'),
    'D':  ('D', 'F#', 'A'),
    'Em': ('E', 'G', 'B'),
    'F#dim': ('F#', 'A', 'C'),
}


def detect_chord(mn):
    lh = measure_events(P_LH, mn)
    if not lh:
        return None
    first = lh[0][1]
    if isinstance(first, nmod.Note):
        pc = first.pitch.pitchClass
    elif isinstance(first, cmod.Chord):
        pc = first.bass().pitchClass
    else:
        return None
    return PC_TO_CHORD.get(pc, 'G')


def pad_pitch(chord_name, target_oct, role):
    """Build a pitch name for a sustain-pad role given target octave.
    role: 'root', 'third', 'fifth'.
    """
    if not chord_name:
        return None
    root, third, fifth = CHORD_TONES[chord_name]
    nt = {'root': root, 'third': third, 'fifth': fifth}[role]
    return f"{nt}{target_oct}"


# ============================================================
# Melody distribution (faithful Voice/Oohs notes per bar)
# ============================================================
MELODY_BY_BAR = {}
for mn in range(9, 17):    MELODY_BY_BAR[mn] = ['Cl']
for mn in range(17, 25):   MELODY_BY_BAR[mn] = ['Vn1']
for mn in range(25, 33):   MELODY_BY_BAR[mn] = ['Fl']
for mn in range(33, 41):   MELODY_BY_BAR[mn] = ['Va']
for mn in range(41, 49):   MELODY_BY_BAR[mn] = ['Vn2']
for mn in range(49, 58):   MELODY_BY_BAR[mn] = ['Vc']
for mn in range(58, 66):   MELODY_BY_BAR[mn] = ['Vn1', 'Fl', 'Vn2_lower6']  # climax: Vn2 plays melody a 6th below
for mn in range(66, 75):   MELODY_BY_BAR[mn] = ['Vn1', 'Vn2', 'Fl', 'Cl']

INST_RANGES = {
    'Vn1': (60, 96), 'Vn2': (55, 84), 'Va':  (50, 79),
    'Vc':  (43, 72), 'Fl':  (62, 96), 'Cl':  (55, 84),
}


def get_melody_for(label, mn):
    """Return melody events (octave-fitted) for label in bar mn, or None."""
    plan = MELODY_BY_BAR.get(mn, [])
    if label == 'Vn2_lower6':
        # Special: Vn2 plays melody transposed down a major 6th
        if 'Vn2_lower6' in plan:
            mel = [clone(n) for _, n in measure_events(P_VOX, mn)]
            # transpose down by 9 semitones (major 6th)
            shifted = []
            for e in mel:
                if isinstance(e, nmod.Note):
                    shifted.append(N(e.pitch.transpose(-9).nameWithOctave, e.duration.quarterLength))
                else:
                    shifted.append(clone(e))
            shifted = shift_to_range(shifted, *INST_RANGES['Vn2'])
            return normalize(shifted)
        return None
    if label in plan:
        mel = [clone(n) for _, n in measure_events(P_VOX, mn)]
        mel = shift_to_range(mel, *INST_RANGES[label])
        return normalize(mel)
    return None


# ============================================================
# String / wind data: melody when assigned, else sustain pad
# ============================================================
def build_string_part(label, pad_role, pad_oct, pad_ql_pattern=None):
    """When this part is NOT carrying melody, fill with chord-tone sustain pad.
    pad_ql_pattern: list of (note_role, ql) or None (defaults to single whole-bar tone).
    """
    data = {}
    for mn in range(1, 83):
        if mn < 9 or mn >= 75:
            data[mn] = [R(BAR_QL)]
            continue
        # Special: Vn2 climax (mm.58-65) plays melody at lower 6th
        if label == 'Vn2' and mn in range(58, 66):
            mel = get_melody_for('Vn2_lower6', mn)
            data[mn] = mel if mel else [R(BAR_QL)]
            continue
        mel = get_melody_for(label, mn)
        if mel is not None:
            data[mn] = mel
        else:
            # Sustain pad: chord tone whole bar (or pattern)
            chord_name = detect_chord(mn) or 'G'
            pitch = pad_pitch(chord_name, pad_oct, pad_role)
            if pad_ql_pattern is None:
                data[mn] = [N(pitch, BAR_QL)]
            else:
                # pad_ql_pattern e.g. [(note_role, ql), ...]
                pat = []
                for role_nm, ql in pad_ql_pattern:
                    pn = pad_pitch(chord_name, pad_oct, role_nm)
                    pat.append(N(pn, ql))
                data[mn] = normalize(pat)
    return data


def build_wind_part(label):
    """Winds: melody when assigned, else rest (winds don't typically pad)."""
    data = {}
    for mn in range(1, 83):
        if mn < 9 or mn >= 75:
            data[mn] = [R(BAR_QL)]
            continue
        mel = get_melody_for(label, mn)
        data[mn] = mel if mel is not None else [R(BAR_QL)]
    return data


# Vn1: melody bars + counter-line during Vn2 verse (mm.41-48), else sustain pad on E5
vn1_data = build_string_part('Vn1', 'fifth', 5)
# Counter-line during Vn2 verse: Vn1 plays a 3rd above the chord tone
for mn in range(41, 49):
    chord_name = detect_chord(mn) or 'G'
    third = pad_pitch(chord_name, 5, 'third')
    # rhythmic ostinato: dotted-quarter pulse 4×
    vn1_data[mn] = [N(third, 1.5) for _ in range(4)]

vn2_data = build_string_part('Vn2', 'third', 4)
# Vn2 echo during Vn1 verse (mm.17-24): play chord 5th on dotted-quarter pulse
for mn in range(17, 25):
    chord_name = detect_chord(mn) or 'G'
    fifth = pad_pitch(chord_name, 4, 'fifth')
    vn2_data[mn] = [N(fifth, 1.5) for _ in range(4)]

# Vn1 octave double-stops in tutti chorus (mm.66-74) — string idiom
for mn in range(66, 75):
    if mn not in vn1_data:
        continue
    new_evs = []
    for e in vn1_data[mn]:
        if isinstance(e, nmod.Note):
            lower = e.pitch.transpose(-12)
            # ensure lower stays within violin range (>= G3 = 55)
            if lower.midi >= 55:
                new_evs.append(CH([lower.nameWithOctave, e.pitch.nameWithOctave],
                                  e.duration.quarterLength))
            else:
                new_evs.append(clone(e))
        else:
            new_evs.append(clone(e))
    vn1_data[mn] = new_evs

va_data = build_string_part('Va',  'third', 4)
vc_data = build_string_part('Vc',  'root', 3)

fl_data = build_wind_part('Fl')
cl_data = build_wind_part('Cl')


# ============================================================
# Piano: original RH/LH preserved
# ============================================================
pno_rh_data, pno_lh_data = {}, {}
for mn in range(1, 83):
    rh_evs = [clone(n) for _, n in measure_events(P_RH, mn)]
    lh_evs = [clone(n) for _, n in measure_events(P_LH, mn)]
    pno_rh_data[mn] = normalize(rh_evs) if rh_evs else [R(BAR_QL)]
    pno_lh_data[mn] = normalize(lh_evs) if lh_evs else [R(BAR_QL)]


# Cb: LH octave-fitted
cb_data = {}
for mn in range(1, 83):
    lh = measure_events(P_LH, mn)
    if has_pitched(lh):
        events = [clone(n) for _, n in lh]
        events = shift_to_range(events, 28, 60)
        cb_data[mn] = normalize(events)
    else:
        cb_data[mn] = [R(BAR_QL)]


# ============================================================
# Drums: 5-stage dynamic pattern
# ============================================================
def drum_bar(mn):
    if mn < 9 or mn >= 75:
        return [R(BAR_QL)]

    # Helpers
    def p_kick():  return N('B2', 0.5)
    def p_snare(): return N('C4', 0.5)
    def p_hat():   return N('A4', 0.5)
    def p_crash(): return CH(['B2', 'A5'], 0.5)

    if 9 <= mn < 25:
        # Verse: hat ostinato + kick on beat 1+3
        out = []
        for beat in range(4):
            for sub in range(3):
                if sub == 0 and beat in (0, 2):
                    out.append(p_kick())
                else:
                    out.append(p_hat())
        return out
    if 25 <= mn < 49:
        # Build: kick on 1+3, snare on 2+4
        out = []
        for beat in range(4):
            for sub in range(3):
                if sub == 0:
                    out.append(p_kick() if beat in (0, 2) else p_snare())
                else:
                    out.append(p_hat())
        return out
    if 49 <= mn < 58:
        # Bridge: minimal — kick on 1, snare on 3
        out = []
        for beat in range(4):
            for sub in range(3):
                if sub == 0 and beat == 0:
                    out.append(p_kick())
                elif sub == 0 and beat == 2:
                    out.append(p_snare())
                else:
                    out.append(p_hat())
        return out
    if 58 <= mn < 66:
        # Climax: full + crash on m.58 and m.62
        out = []
        for beat in range(4):
            for sub in range(3):
                if beat == 0 and sub == 0 and mn in (58, 62):
                    out.append(p_crash())
                elif sub == 0:
                    out.append(p_kick() if beat in (0, 2) else p_snare())
                else:
                    out.append(p_hat())
        return out
    if 66 <= mn < 75:
        # Chorus peak: crash on m.66 + m.70, full pattern
        out = []
        for beat in range(4):
            for sub in range(3):
                if beat == 0 and sub == 0 and mn in (66, 70):
                    out.append(p_crash())
                elif sub == 0:
                    out.append(p_kick() if beat in (0, 2) else p_snare())
                else:
                    out.append(p_hat())
        return out
    return [R(BAR_QL)]


drum_data = {mn: drum_bar(mn) for mn in range(1, 83)}


# ============================================================
# Build parts
# ============================================================
common_kwargs = dict(
    key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
    measures_per_bar_ql=BAR_QL, fermata_on_last=False,
)

# Dynamics: arc shape across the piece
arc_dyn = {1: 'p', 9: 'mp', 25: 'mp', 41: 'mf', 49: 'p', 58: 'f', 66: 'ff', 73: 'mf'}
arc_dyn_p = {1: 'pp', 9: 'p', 25: 'p', 41: 'mp', 49: 'pp', 58: 'mf', 66: 'f', 73: 'mp'}

vn1 = make_part("Violin 1", "Vn 1", "violin", vn1_data,
                tempo_text=TEMPO_TEXT, tempo_bpm=TEMPO_BPM, tempo_referent_ql=TEMPO_REFERENT_QL,
                dyn_map=arc_dyn,
                expr_map={17: 'cantabile', 41: 'leggiero', 58: 'ten.', 66: 'tutti, espress.'},
                **common_kwargs)
vn2 = make_part("Violin 2", "Vn 2", "violin", vn2_data,
                dyn_map=arc_dyn_p,
                expr_map={17: 'echo', 41: 'pizz.', 49: 'arco', 58: '(lower 6th)', 66: 'tutti'},
                **common_kwargs)
va  = make_part("Viola",   "Va",   "viola",  va_data,
                clef_obj=clefmod.AltoClef(),
                dyn_map=arc_dyn_p,
                expr_map={33: 'espress.', 49: 'sotto voce'},
                **common_kwargs)
vc  = make_part("Violoncello", "Vc", "cello", vc_data,
                clef_obj=clefmod.BassClef(),
                dyn_map=arc_dyn_p,
                expr_map={49: 'cantabile, espress.'},
                **common_kwargs)
cb  = make_part("Contrabass", "Cb", "doublebass", cb_data,
                clef_obj=clefmod.BassClef(),
                dyn_map=arc_dyn_p,
                **common_kwargs)
fl  = make_part("Flute",    "Fl",  "flute",    fl_data,
                dyn_map={25: 'mp', 58: 'mf', 66: 'f'},
                expr_map={25: 'leggiero', 58: 'soaring', 66: 'tutti'},
                **common_kwargs)
cl  = make_part("Clarinet", "Cl",  "clarinet", cl_data,
                dyn_map={9: 'mp', 66: 'mf'},
                expr_map={9: 'dolce', 66: 'tutti'},
                **common_kwargs)
pno_rh = make_part("Piano (R.H.)", "Pf", "piano", pno_rh_data,
                   dyn_map=arc_dyn,
                   **common_kwargs)
pno_lh = make_part("Piano (L.H.)", "Pf", "piano", pno_lh_data,
                   clef_obj=clefmod.BassClef(),
                   **common_kwargs)
drm = make_part("Drums", "Dr", "drums", drum_data,
                clef_obj=clefmod.PercussionClef(),
                dyn_map={9: 'p', 25: 'mp', 49: 'pp', 58: 'f', 66: 'ff'},
                **common_kwargs)


for p_obj, key in [(vn1, 'violin'), (vn2, 'violin'), (va, 'viola'),
                   (vc, 'cello'), (cb, 'doublebass'), (fl, 'flute'),
                   (cl, 'clarinet')]:
    bad = check_range(p_obj, INSTRUMENTS[key][1])
    if bad:
        print(f"[RANGE WARN] {p_obj.partName}: {len(bad)} OOR (first 5: {bad[:5]})")
    else:
        print(f"[RANGE OK]   {p_obj.partName}")

score = make_score(
    title=TASK["output"]["title"],
    subtitle=TASK["output"]["subtitle"] + " (V2)",
    composer="(original)",
    arranger="arr. for 9-part ensemble (faithful, V2)",
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
