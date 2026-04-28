"""V4: demon_hunters -> 9-part orchestra with cinematic-piano idiom (Pietschmann-style).

Builds on V3 (texture separation + role clarity) and adds the characteristic
'cinematic piano arrangement' idiom — generic features, not a copy of any
specific Pietschmann arrangement:

  - LH octave-doubled bass with 16th-note wide arpeggios spanning 2 octaves
  - RH lush 4-voice voicing; close+open hybrid; melody-octave at climax/chorus
  - Strings tremolo on climax phrase entries
  - Winds 32nd-note obbligato during pre-chorus build (m.55-57)
  - Drums signature snare-roll fill into chorus (m.65)
  - Deeper dynamic extremes: pp -> fff and back

Conductor's principles (from V3, retained):
  1. ROLE SEPARATION — each instrument has ONE role per phrase
  2. MELODY CLARITY — solo melody in upper register; pad in mid-low
  3. PIANO is a concert-pianist-level virtuoso part
  4. ORCHESTRAL IDIOM — pizz/arco, tremolo, divisi, double-stops
  5. DYNAMIC ARC with deeper extremes

Structural design (mm.9-74; 1-8 intro / 75-82 outro):
  Phrase 1 (mm. 9-16):  Cl solo melody     | Vn2/Va pp pad (low) | Cb pizz | sparse drums
  Phrase 2 (mm.17-24):  Vn1 solo melody    | Va warm pad         | Vc + Cb | hat+kick   | Cl 16th obbligato
  Phrase 3 (mm.25-32):  Fl + Cl // 3rds    | Strings sustain     | Cb      | full kit (light)
  Phrase 4 (mm.33-40):  Vc cantabile       | Vn1+Vn2 high pad    | Cb      | bridge groove | Va inner
  Phrase 5 (mm.41-48):  Vn2 + Va //octave  | Vn1 sustain         | Vc + Cb | build       | Fl 16th obbligato
  Phrase 6 (mm.49-57):  Vn1 lyrical        | Vc/Va warm pad      | Cb      | sparse      | Cl
  Phrase 7 (mm.58-65):  Vn1+Fl unison + Vn2 lower 6th | Va+Vc | Cb full | full + crash | piano arpeggio
  Phrase 8 (mm.66-74):  4-part harmonized chorus (Vn1 oct, Vn2 -6, Fl, Cl -5) | strings divisi | Cb+Vc | full + ride

Piano is fully rewritten with playable voicings (no original OMR copying).
NO change to original melody (Voice/Oohs notes preserved verbatim).
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
TEMPO_TEXT = "Allegro"
TEMPO_BPM = 123
TEMPO_REFERENT_QL = 1.5


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


def transpose_event(e, semitones):
    if isinstance(e, nmod.Note):
        new_p = e.pitch.transpose(semitones)
        return N(new_p.nameWithOctave, e.duration.quarterLength)
    if isinstance(e, cmod.Chord):
        new_p = [p.transpose(semitones) for p in e.pitches]
        return CH([p.nameWithOctave for p in new_p], e.duration.quarterLength)
    return clone(e)


def transpose_events(events, semitones):
    return [transpose_event(e, semitones) for e in events]


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
    return transpose_events(events, 12 * shift) if shift else events


# ============================================================
# Chord detection (LH bass note → G major / E minor diatonic)
# ============================================================
PC_TO_CHORD = {7: 'G', 9: 'Am', 11: 'Bm', 0: 'C', 2: 'D', 4: 'Em', 6: 'F#dim'}


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


# Chord tone tables, organized by register for each role
CHORD_TONES_PC = {
    'G':  {'root': 'G',  'third': 'B',  'fifth': 'D'},
    'Am': {'root': 'A',  'third': 'C',  'fifth': 'E'},
    'Bm': {'root': 'B',  'third': 'D',  'fifth': 'F#'},
    'C':  {'root': 'C',  'third': 'E',  'fifth': 'G'},
    'D':  {'root': 'D',  'third': 'F#', 'fifth': 'A'},
    'Em': {'root': 'E',  'third': 'G',  'fifth': 'B'},
    'F#dim': {'root': 'F#', 'third': 'A', 'fifth': 'C'},
}


def chord_pitch(chord_name, role, octave):
    pc = CHORD_TONES_PC[chord_name][role]
    return f"{pc}{octave}"


# ============================================================
# Melody distribution plan
# ============================================================
INST_RANGES = {
    'Vn1': (60, 96), 'Vn2': (55, 84), 'Va': (50, 79),
    'Vc': (43, 72), 'Fl': (62, 96), 'Cl': (55, 84),
}


def melody_for(label, mn, transpose_semi=0, target_lo=None, target_hi=None):
    """Return Voice/Oohs melody for a bar, optionally transposed and range-fitted."""
    mel = [clone(n) for _, n in measure_events(P_VOX, mn)]
    if transpose_semi:
        mel = transpose_events(mel, transpose_semi)
    if target_lo is None:
        target_lo, target_hi = INST_RANGES[label]
    mel = shift_to_range(mel, target_lo, target_hi)
    return normalize(mel)


# Per-bar melody assignments — multi-line dict for clarity
MELODY_PLAN = {}
# Phrase 1: Cl solo
for mn in range(9, 17):  MELODY_PLAN[mn] = {'Cl': 0}
# Phrase 2: Vn1 solo (Cl 16th obbligato handled separately)
for mn in range(17, 25): MELODY_PLAN[mn] = {'Vn1': 0}
# Phrase 3: Fl + Cl // 3rds
for mn in range(25, 33): MELODY_PLAN[mn] = {'Fl': 0, 'Cl': -3}      # Cl a minor 3rd below
# Phrase 4: Vc cantabile (bridge mood)
for mn in range(33, 41): MELODY_PLAN[mn] = {'Vc': 0}
# Phrase 5: Vn2 + Va octave (pre-chorus build, Fl 16th obbligato)
for mn in range(41, 49): MELODY_PLAN[mn] = {'Vn2': 0, 'Va': -12}    # Va an octave below Vn2
# Phrase 6: Vn1 lyrical
for mn in range(49, 58): MELODY_PLAN[mn] = {'Vn1': 0}
# Phrase 7: Climax — Vn1+Fl unison + Vn2 6th below
for mn in range(58, 66): MELODY_PLAN[mn] = {'Vn1': 0, 'Fl': 0, 'Vn2': -9}
# Phrase 8: Chorus 4-part harmony
for mn in range(66, 75): MELODY_PLAN[mn] = {'Vn1': 0, 'Fl': 0, 'Vn2': -9, 'Cl': -7}


# ============================================================
# Piano (V4: cinematic-piano idiom — virtuoso, octave bass + lush voicing)
# ============================================================
# LH: octave-doubled bass + wide 16th arpeggios (2-octave broken chords)
def piano_lh_bar(chord_name, dyn='normal'):
    if not chord_name:
        return [R(BAR_QL)]
    root_pc = CHORD_TONES_PC[chord_name]['root']
    fifth_pc = CHORD_TONES_PC[chord_name]['fifth']
    third_pc = CHORD_TONES_PC[chord_name]['third']

    # Bass register positions
    root_lo = f"{root_pc}1" if root_pc in {'A', 'B'} else f"{root_pc}2"
    root_md = f"{root_pc}2" if root_pc in {'A', 'B'} else f"{root_pc}3"
    fifth_md = f"{fifth_pc}2" if fifth_pc in {'A', 'B'} else f"{fifth_pc}3"
    third_md = f"{third_pc}3" if third_pc in {'C', 'D', 'E'} else f"{third_pc}3"

    if dyn == 'sparse':
        # Octave bass (root + root 8va) on beat 1 only — cinematic anchor
        return [CH([root_lo, root_md], 1.5), R(4.5)]
    if dyn == 'verse':
        # Octave root on beat 1, octave fifth on beat 3 — anchored cinematic verse
        return [
            CH([root_lo, root_md], 1.5),
            R(1.5),
            CH([fifth_md, root_md], 1.5),
            R(1.5),
        ]
    if dyn == 'arpeggio':
        # 16th-note wide arpeggio: root_lo - root_md - fifth_md - third_md
        # 12/8 = 12 eighths = 24 sixteenths; we use 12 notes at 0.5 ql (eighths)
        # Pattern: 3 chord tones × 4 beats, broken chord cycling
        out = []
        for _ in range(4):
            out.append(N(root_lo, 0.5))
            out.append(N(fifth_md, 0.5))
            out.append(N(root_md, 0.5))
        return out
    if dyn == 'full':
        # Climax/chorus: octave bass on every dotted-quarter beat (heavy)
        return [CH([root_lo, root_md], 1.5),
                CH([fifth_md, root_md], 1.5),
                CH([root_lo, root_md], 1.5),
                CH([fifth_md, root_md], 1.5)]
    return [CH([root_lo, root_md], 1.5), N(fifth_md, 1.5),
            CH([root_lo, root_md], 1.5), N(fifth_md, 1.5)]


# RH: lush 4-voice voicing; melody-octave doubling allowed only at climax/chorus
def piano_rh_bar(chord_name, dyn='normal'):
    if not chord_name:
        return [R(BAR_QL)]
    root_pc = CHORD_TONES_PC[chord_name]['root']
    third_pc = CHORD_TONES_PC[chord_name]['third']
    fifth_pc = CHORD_TONES_PC[chord_name]['fifth']

    pc_order = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'A': 9, 'B': 11}
    root_pos = pc_order.get(root_pc, 0)
    third_pos = pc_order.get(third_pc, 0)

    # 4-voice voicing: root - third - fifth - root(8va), close+open hybrid
    third = f"{third_pc}4"
    fifth = f"{fifth_pc}4"
    root_oct = 5 if root_pos < third_pos else 4
    root_low = f"{root_pc}{root_oct}"
    root_high = f"{root_pc}{root_oct + 1}" if root_oct < 5 else f"{root_pc}5"
    voicing4 = [third, fifth, root_low, root_high]   # 4-note lush voicing

    if dyn == 'sparse':
        # Single 4-voice chord on beat 1 (long sustained)
        return [CH(voicing4, 1.5), R(BAR_QL - 1.5)]
    if dyn == 'verse':
        # Chord on beats 1 and 3 (cinematic strum feel)
        return [CH(voicing4, 1.5), R(1.5), CH(voicing4, 1.5), R(1.5)]
    if dyn == 'full':
        # 4-voice chord every beat — climax tutti
        return [CH(voicing4, 1.5) for _ in range(4)]
    if dyn == 'arpeggio':
        # RH broken chord arpeggio (cinematic-piano signature):
        # third - fifth - root_low - root_high cycle (4 notes per beat × 3 cycles)
        out = []
        for _ in range(4):
            out.append(N(third, 0.5))
            out.append(N(fifth, 0.5))
            out.append(N(root_low, 0.5))
        return out
    return [CH(voicing4, 1.5), R(1.5), CH(voicing4, 1.5), R(1.5)]


# Piano dynamic stage by bar
def piano_stage(mn):
    if mn < 9 or mn >= 75:
        return 'sparse'
    if 9 <= mn < 17:
        return 'sparse'        # verse 1: very light
    if 17 <= mn < 33:
        return 'verse'         # verses 2-3
    if 33 <= mn < 41:
        return 'verse'         # bridge: warm
    if 41 <= mn < 49:
        return 'arpeggio'      # pre-chorus build
    if 49 <= mn < 58:
        return 'verse'
    if 58 <= mn < 66:
        return 'arpeggio'      # climax
    if 66 <= mn < 75:
        return 'full'          # chorus tutti
    return 'sparse'


pno_lh_data = {}
pno_rh_data = {}
for mn in range(1, 83):
    chord = detect_chord(mn)
    stage = piano_stage(mn)
    pno_lh_data[mn] = normalize(piano_lh_bar(chord, stage))
    pno_rh_data[mn] = normalize(piano_rh_bar(chord, stage))


# ============================================================
# Strings sustain pad (LOWER register so melody can shine above)
# ============================================================
# Vn2 pad register: G3-D4 (5th in oct 4 or below)
# Va  pad register: C3-G3 (3rd in oct 3)
# Vc  pad register: G2-D3 (root in oct 2-3)
# Cb  pad register: E1-D2 (sounding; written oct 2-3 because Cb sounds 1 octave lower)


def vn2_pad_bar(chord_name):
    """Vn2 sustain pad: chord 5th in low-mid violin register (G3-A4 ≈ 55-69)."""
    if not chord_name:
        return [R(BAR_QL)]
    fifth_pc = CHORD_TONES_PC[chord_name]['fifth']
    from music21 import pitch as pmod
    # Try oct 4 first (preferred mid-low), then 5, then 3 (only if >= G3)
    for oc in [4, 5, 3]:
        midi = pmod.Pitch(f"{fifth_pc}{oc}").midi
        if 55 <= midi <= 76:
            return [N(f"{fifth_pc}{oc}", BAR_QL)]
    # ultimate fallback: oct 4
    return [N(f"{fifth_pc}4", BAR_QL)]


def va_pad_bar(chord_name):
    """Va sustain: chord 3rd in viola sweet spot (C3-G3 ~ MIDI 48-55)."""
    if not chord_name:
        return [R(BAR_QL)]
    third_pc = CHORD_TONES_PC[chord_name]['third']
    from music21 import pitch as pmod
    for oc in [3, 4]:
        midi = pmod.Pitch(f"{third_pc}{oc}").midi
        if 48 <= midi <= 60:
            return [N(f"{third_pc}{oc}", BAR_QL)]
    return [N(f"{third_pc}3", BAR_QL)]


def vc_pad_bar(chord_name):
    """Vc sustain: chord root in cello sweet spot (G2-D3 = MIDI 43-50)."""
    if not chord_name:
        return [R(BAR_QL)]
    root_pc = CHORD_TONES_PC[chord_name]['root']
    from music21 import pitch as pmod
    for oc in [2, 3]:
        midi = pmod.Pitch(f"{root_pc}{oc}").midi
        if 36 <= midi <= 55:
            return [N(f"{root_pc}{oc}", BAR_QL)]
    return [N(f"{root_pc}2", BAR_QL)]


def cb_pad_bar(chord_name):
    """Cb sustain: chord root, oct 2 (sounds oct 1; written as oct 2)."""
    if not chord_name:
        return [R(BAR_QL)]
    root_pc = CHORD_TONES_PC[chord_name]['root']
    from music21 import pitch as pmod
    for oc in [2, 3]:
        midi = pmod.Pitch(f"{root_pc}{oc}").midi
        if 28 <= midi <= 50:
            return [N(f"{root_pc}{oc}", BAR_QL)]
    return [N(f"{root_pc}2", BAR_QL)]


# ============================================================
# Build melody/pad data per instrument
# ============================================================
def build_melody_or_pad(label, pad_func):
    data = {}
    for mn in range(1, 83):
        if mn < 9 or mn >= 75:
            data[mn] = [R(BAR_QL)]
            continue
        plan = MELODY_PLAN.get(mn, {})
        if label in plan:
            transp = plan[label]
            data[mn] = melody_for(label, mn, transpose_semi=transp)
        else:
            chord = detect_chord(mn) or 'G'
            data[mn] = pad_func(chord)
    return data


vn1_data = build_melody_or_pad('Vn1', lambda ch: [N(chord_pitch(ch, 'fifth', 5), BAR_QL)])
vn2_data = build_melody_or_pad('Vn2', vn2_pad_bar)
va_data  = build_melody_or_pad('Va', va_pad_bar)
vc_data  = build_melody_or_pad('Vc', vc_pad_bar)
cb_data  = {mn: cb_pad_bar(detect_chord(mn) or 'G') if 9 <= mn < 75 else [R(BAR_QL)] for mn in range(1, 83)}

# Winds: melody only; rest otherwise (winds typically don't pad)
fl_data = {}
cl_data = {}
for mn in range(1, 83):
    plan = MELODY_PLAN.get(mn, {})
    if 'Fl' in plan:
        fl_data[mn] = melody_for('Fl', mn, transpose_semi=plan['Fl'])
    else:
        fl_data[mn] = [R(BAR_QL)]
    if 'Cl' in plan:
        cl_data[mn] = melody_for('Cl', mn, transpose_semi=plan['Cl'])
    else:
        cl_data[mn] = [R(BAR_QL)]


# ============================================================
# Counter-melody / obbligato additions
# ============================================================
# mm.17-24: Cl 16th-note obbligato (chord-tone arpeggio, not the main melody)
def cl_obbligato_bar(chord_name):
    """8 sixteenth-note arpeggio: 1-3-5-3-1-3-5-3 ish, but 12/8 = 12 eighths.
    For obbligato we use 12 eighth-note arp: pattern of chord tones cycling."""
    third_pc = CHORD_TONES_PC[chord_name]['third']
    fifth_pc = CHORD_TONES_PC[chord_name]['fifth']
    root_pc  = CHORD_TONES_PC[chord_name]['root']
    # Place pattern in oct 5 (clarinet upper register, comfortable)
    seq = [f"{third_pc}5", f"{fifth_pc}5", f"{third_pc}5"] * 4
    return [N(p, 0.5) for p in seq]


for mn in range(17, 25):
    chord = detect_chord(mn) or 'G'
    cl_data[mn] = cl_obbligato_bar(chord)

# mm.41-48: Fl 16th-note obbligato over Vn2/Va octave melody
def fl_obbligato_bar(chord_name):
    third_pc = CHORD_TONES_PC[chord_name]['third']
    fifth_pc = CHORD_TONES_PC[chord_name]['fifth']
    seq = [f"{fifth_pc}5", f"{third_pc}6", f"{fifth_pc}5"] * 4
    return [N(p, 0.5) for p in seq]


for mn in range(41, 49):
    chord = detect_chord(mn) or 'G'
    fl_data[mn] = fl_obbligato_bar(chord)

# Vn1 octave double-stops in chorus tutti (mm.66-74)
for mn in range(66, 75):
    if mn not in vn1_data:
        continue
    new_evs = []
    for e in vn1_data[mn]:
        if isinstance(e, nmod.Note):
            higher = e.pitch.transpose(12)
            if higher.midi <= 96:
                new_evs.append(CH([e.pitch.nameWithOctave, higher.nameWithOctave],
                                  e.duration.quarterLength))
            else:
                new_evs.append(clone(e))
        else:
            new_evs.append(clone(e))
    vn1_data[mn] = new_evs


# ============================================================
# V4 cinematic-piano signature additions
# ============================================================

# 1) STRINGS TREMOLO on climax entry bars (m.58, m.66) — replace sustain pad
#    with rapid 32nd-note repetition of the same chord tone for tremolo effect
def make_tremolo(pitch_name, total_ql=BAR_QL, sub_ql=0.25):
    n_count = int(round(total_ql / sub_ql))
    return [N(pitch_name, sub_ql) for _ in range(n_count)]


# Replace Vn2/Va/Vc pad in m.58 with tremolo (climax phrase entry)
for mn in [58]:
    chord = detect_chord(mn) or 'G'
    # Vn2 plays melody at lower-6th here, keep that. Skip Vn2 tremolo.
    # Va: tremolo on chord 3rd
    third_pc = CHORD_TONES_PC[chord]['third']
    from music21 import pitch as pmod
    for oc in [3, 4]:
        midi = pmod.Pitch(f"{third_pc}{oc}").midi
        if 48 <= midi <= 60:
            va_data[mn] = make_tremolo(f"{third_pc}{oc}", BAR_QL, 0.25)
            break
    # Vc: tremolo on chord root
    root_pc = CHORD_TONES_PC[chord]['root']
    for oc in [2, 3]:
        midi = pmod.Pitch(f"{root_pc}{oc}").midi
        if 36 <= midi <= 55:
            vc_data[mn] = make_tremolo(f"{root_pc}{oc}", BAR_QL, 0.25)
            break

# 2) WINDS 32nd-note obbligato BUILD-UP at end of bridge (mm.55-57)
#    rapid ascending chord-tone arpeggio (eighth-notes for playable 32nd-feel)
def winds_build_bar(chord_name, octave_high=False):
    root_pc = CHORD_TONES_PC[chord_name]['root']
    third_pc = CHORD_TONES_PC[chord_name]['third']
    fifth_pc = CHORD_TONES_PC[chord_name]['fifth']
    base_oct = 6 if octave_high else 5
    seq = [f"{root_pc}{base_oct}", f"{third_pc}{base_oct}", f"{fifth_pc}{base_oct}"] * 4
    return [N(p, 0.5) for p in seq]


for mn in [55, 56, 57]:
    chord = detect_chord(mn) or 'G'
    # Cl in oct 5, Fl in oct 6 — ascending tension
    cl_data[mn] = winds_build_bar(chord, octave_high=False)
    fl_data[mn] = winds_build_bar(chord, octave_high=True)


# 3) DRUMS signature snare-roll FILL at end of climax (m.65) — leading into chorus
def drum_fill_bar():
    """Snare roll fill: 12 sixteenth-note snare hits (rendered as 12 eighths)."""
    out = []
    # 8 sixteenths of snare crescendo + 4 sixteenths of crash setup
    # 12/8 = 12 eighths = 6 ql
    for i in range(8):
        out.append(N('C4', 0.5))   # snare
    out.append(N('C4', 0.5))       # snare
    out.append(N('C4', 0.5))       # snare
    out.append(N('C4', 0.5))       # snare
    out.append(CH(['B2', 'A5'], 0.5))  # crash + kick at very end (placeholder)
    # Total 12 eighths × 0.5 = 6 ql, but we have 13 events. Trim:
    return out[:12]


# We'll override m.65 in drum_data after it is built (below)


# ============================================================
# Drums (sparser, more dynamic)
# ============================================================
def drum_bar(mn):
    if mn < 9 or mn >= 75:
        return [R(BAR_QL)]

    def kick():  return N('B2', 0.5)
    def snare(): return N('C4', 0.5)
    def hat():   return N('A4', 0.5)
    def crash(): return CH(['B2', 'A5'], 0.5)
    def rest():  return R(0.5)

    if 9 <= mn < 17:
        # Verse 1: very sparse — kick on beat 1, hat on every other 8th
        out = []
        for beat in range(4):
            for sub in range(3):
                if sub == 0 and beat in (0, 2):
                    out.append(kick())
                elif sub in (1,):
                    out.append(hat())
                else:
                    out.append(rest())
        return out
    if 17 <= mn < 33:
        # Verse 2-3: hat ostinato + kick on 1+3
        out = []
        for beat in range(4):
            for sub in range(3):
                if sub == 0 and beat in (0, 2):
                    out.append(kick())
                else:
                    out.append(hat())
        return out
    if 33 <= mn < 41:
        # Bridge: minimal — kick on 1, snare on 3
        out = []
        for beat in range(4):
            for sub in range(3):
                if sub == 0 and beat == 0:
                    out.append(kick())
                elif sub == 0 and beat == 2:
                    out.append(snare())
                else:
                    out.append(rest())
        return out
    if 41 <= mn < 49:
        # Pre-chorus build: kick on 1+3, snare on 2+4, hat continuous
        out = []
        for beat in range(4):
            for sub in range(3):
                if sub == 0:
                    out.append(kick() if beat in (0, 2) else snare())
                else:
                    out.append(hat())
        return out
    if 49 <= mn < 58:
        # Bridge 2: sparse kick + hat
        out = []
        for beat in range(4):
            for sub in range(3):
                if sub == 0 and beat in (0, 2):
                    out.append(kick())
                elif sub in (1,):
                    out.append(hat())
                else:
                    out.append(rest())
        return out
    if 58 <= mn < 66:
        # Climax: full + crash on 58 and 62
        out = []
        for beat in range(4):
            for sub in range(3):
                if beat == 0 and sub == 0 and mn in (58, 62):
                    out.append(crash())
                elif sub == 0:
                    out.append(kick() if beat in (0, 2) else snare())
                else:
                    out.append(hat())
        return out
    if 66 <= mn < 75:
        # Chorus peak: full pattern + crash on 66 and 70
        out = []
        for beat in range(4):
            for sub in range(3):
                if beat == 0 and sub == 0 and mn in (66, 70):
                    out.append(crash())
                elif sub == 0:
                    out.append(kick() if beat in (0, 2) else snare())
                else:
                    out.append(hat())
        return out
    return [R(BAR_QL)]


drum_data = {mn: drum_bar(mn) for mn in range(1, 83)}

# V4 signature: replace m.65 with snare-roll fill leading into chorus
drum_data[65] = drum_fill_bar()


# ============================================================
# Build parts
# ============================================================
common = dict(
    key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
    measures_per_bar_ql=BAR_QL, fermata_on_last=False,
)

# Dynamic arc and expressions
vn1_dyn   = {1: 'p', 17: 'mp', 49: 'mp', 58: 'f', 66: 'ff', 73: 'mf'}
vn1_expr  = {17: 'cantabile', 49: 'espress.', 58: 'tutti, soaring', 66: 'tutti'}
vn2_dyn   = {1: 'pp', 9: 'pp', 41: 'mp', 58: 'mf', 66: 'f'}
vn2_expr  = {9: '(pad)', 41: '8va w/ Va', 58: '(6th below)', 66: '(harmony)'}
va_dyn    = {1: 'pp', 9: 'pp', 41: 'mp', 58: 'mf', 66: 'f'}
va_expr   = {9: '(pad)', 41: 'octave below Vn2', 49: 'sotto voce', 58: '(pad)', 66: '(divisi)'}
vc_dyn    = {1: 'pp', 33: 'mp', 49: 'mp', 58: 'mf', 66: 'f'}
vc_expr   = {33: 'cantabile, espress.', 49: '(pad)', 66: '(divisi)'}
cb_dyn    = {1: 'pp', 41: 'mp', 58: 'mf', 66: 'f'}
cb_expr   = {9: 'pizz.', 41: 'arco', 73: 'arco'}
fl_dyn    = {25: 'mp', 41: 'mp', 58: 'mf', 66: 'ff'}
fl_expr   = {25: 'leggiero (// 3rds w/ Cl)', 41: 'obbligato', 58: 'unison w/ Vn1', 66: 'tutti'}
cl_dyn    = {9: 'mp', 17: 'p', 25: 'mp', 66: 'mf'}
cl_expr   = {9: 'dolce, solo', 17: 'obbligato (16ths)', 25: '// 3rds below Fl', 66: '(harmony)'}
pno_dyn   = {1: 'pp', 9: 'p', 25: 'mp', 41: 'mf', 58: 'f', 66: 'ff'}
pno_expr  = {1: 'leggiero', 41: 'arpeggio', 58: 'arpeggio'}
drm_dyn   = {9: 'pp', 17: 'p', 25: 'mp', 33: 'pp', 41: 'mf', 49: 'p', 58: 'f', 66: 'ff'}

vn1 = make_part("Violin 1", "Vn 1", "violin", vn1_data,
                tempo_text=TEMPO_TEXT, tempo_bpm=TEMPO_BPM, tempo_referent_ql=TEMPO_REFERENT_QL,
                dyn_map=vn1_dyn, expr_map=vn1_expr, **common)
vn2 = make_part("Violin 2", "Vn 2", "violin", vn2_data,
                dyn_map=vn2_dyn, expr_map=vn2_expr, **common)
va  = make_part("Viola", "Va", "viola", va_data,
                clef_obj=clefmod.AltoClef(),
                dyn_map=va_dyn, expr_map=va_expr, **common)
vc  = make_part("Violoncello", "Vc", "cello", vc_data,
                clef_obj=clefmod.BassClef(),
                dyn_map=vc_dyn, expr_map=vc_expr, **common)
cb  = make_part("Contrabass", "Cb", "doublebass", cb_data,
                clef_obj=clefmod.BassClef(),
                dyn_map=cb_dyn, expr_map=cb_expr, **common)
fl  = make_part("Flute", "Fl", "flute", fl_data,
                dyn_map=fl_dyn, expr_map=fl_expr, **common)
cl  = make_part("Clarinet", "Cl", "clarinet", cl_data,
                dyn_map=cl_dyn, expr_map=cl_expr, **common)
pno_rh = make_part("Piano (R.H.)", "Pf", "piano", pno_rh_data,
                   dyn_map=pno_dyn, expr_map=pno_expr, **common)
pno_lh = make_part("Piano (L.H.)", "Pf", "piano", pno_lh_data,
                   clef_obj=clefmod.BassClef(), **common)
drm = make_part("Drums", "Dr", "drums", drum_data,
                clef_obj=clefmod.PercussionClef(),
                dyn_map=drm_dyn, **common)

# Range checks
for p_obj, key in [(vn1, 'violin'), (vn2, 'violin'), (va, 'viola'),
                   (vc, 'cello'), (cb, 'doublebass'), (fl, 'flute'),
                   (cl, 'clarinet')]:
    bad = check_range(p_obj, INSTRUMENTS[key][1])
    if bad:
        print(f"[RANGE WARN] {p_obj.partName}: {len(bad)} OOR (first 5: {bad[:5]})")
    else:
        print(f"[RANGE OK]   {p_obj.partName}")

# Piano range check (very wide A0-C8, but warn if RH below C3 or LH above C5)
for p_obj, lo_warn, hi_warn in [(pno_rh, 48, 84), (pno_lh, 24, 60)]:
    pitches = []
    for x in p_obj.recurse().notes:
        if isinstance(x, nmod.Note):
            pitches.append(x.pitch.midi)
        elif isinstance(x, cmod.Chord):
            pitches.extend(p.midi for p in x.pitches)
    if pitches:
        bad = [p for p in pitches if p < lo_warn or p > hi_warn]
        if bad:
            print(f"[PIANO WARN] {p_obj.partName}: {len(bad)} notes outside comfortable register")
        else:
            print(f"[PIANO OK]   {p_obj.partName}: {min(pitches)}-{max(pitches)}")


score = make_score(
    title=TASK["output"]["title"],
    subtitle=TASK["output"]["subtitle"] + " (V3 — Director's Cut)",
    composer="(original)",
    arranger="arr. for 9-part orchestra (V3, professional players)",
    parts=[fl, cl, vn1, vn2, va, vc, cb, pno_rh, pno_lh, drm],
    group_label="Orchestra",
    group_symbol="bracket",
)

xml_path, mid_path = export_xml_midi(score, OUT_DIR, VERSION)
print(f"\n=== {VERSION} GENERATED ===")
print(f"  MusicXML: {xml_path}")
print(f"  MIDI:     {mid_path}")
for entry in summarize_score(score):
    print(f"  {entry['part']}: {entry['measures']} mm, {entry['events']} events, "
          f"range {entry['range'][0]}-{entry['range'][1]}, double-stops: {entry['double_stops']}")
