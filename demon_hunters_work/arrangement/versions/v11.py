"""V11: V10 + range cleanup (no MuseScore red highlights) + Bb Cl key sig fix.

V10 → V11 changes:
  1. Contrabass: notes < E2 written shifted up an octave (4-string Cb compatible)
  2. Flute: notes > A6 shifted down an octave (within MuseScore amateur range)
  3. Violin 1: chord pitches > G6 dropped (single note instead of octave double)
  4. Bb Clarinet key signature: 3 sharps (A major, the transposed key for
     concert G major). The +M2 transposition was already correct in V7+.

NO change to: melody pitch classes, harmony, time, key, tempo.

Original V10 docstring follows:

V8/V9 had a bug in piano_rh_bar voicing logic that placed the 5th in oct 4
even when it fell BELOW the 3rd, producing unplayable chord stretches up to
21 semitones (m14) — beyond any pianist's single-hand reach.

V10 fix: hardcoded close-position root-position voicings (root + 3rd + 5th + root_8va).
All voicings span exactly one octave, comfortable for any trained pianist.

Also includes V9 diatonic interval fix and all prior version features.

NO change to: melody, harmony, time, key, tempo.

Original V9 docstring follows:

V8 used CHROMATIC fixed-semitone parallel intervals (e.g., -3, -7, -9), which
produced non-diatonic notes (G#, C#, D#, F natural) clashing with G major
harmony whenever the melody hit B, E, F#, or C.

V9 fix: replace fixed-semitone with DIATONIC intervals in G major:
  - mm.25-32  Cl // 3rd below Fl  → m3 or M3 (per scale degree)
  - mm.58-65  Vn2 // 6th below    → m6 or M6
  - mm.66-74  Vn2 // 6th below    → m6 or M6
  - mm.66-74  Cl // 5th below     → P5 (or d5 from C → F# to stay in scale)

NO change to: melody notes (Voice/Oohs verbatim), harmony, time, key, tempo.

Original V8 docstring follows:

Inherits everything from V4-V7 (Pietschmann piano + tremolo/build/fill +
intro/outro figure + layered build/decay + Bb Cl written + Piano clefs +
Vc chorus + Fl bridge + Vc octave doubling).

V7 -> V8 single conceptual upgrade: ORCHESTRAL TEXTURE
  - Non-melody string parts (Vn2, Va, Vc, Cb) replace whole-bar sustains
    with rhythmic counter-figures (orchestral inner voice writing)
  - Va plays a REAL stepwise counter-melody during Vc cantabile bridge
    (mm.33-40), in dialogue with the cello melody (true counterpoint)
  - Fl mm.33-40 redesigned as sparse melodic response — rest, brief
    scale fragments, high pedal, descending phrase ending — instead of
    the static chord-tone arpeggio of V7
  - Vn1 high pedal stays sustained (preserves orchestral 'shimmer' on top)
  - mm.1-8 layered build and mm.75-82 layered decay (V6) preserved as-is

NO change to: melody, harmony, time, key, tempo, intro/outro figure.

Original V4 docstring follows:

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

# V5: Restore the ORIGINAL piano figure for intro (mm.1-8) and outro (mm.75-82).
# These bars carry the song's signature motif (RH ostinato + LH chord) and
# replacing them with sparse single chords (V4 behavior) loses that identity.
for mn in list(range(1, 9)) + list(range(75, 83)):
    rh_evs = [clone(n) for _, n in measure_events(P_RH, mn)]
    lh_evs = [clone(n) for _, n in measure_events(P_LH, mn)]
    if rh_evs:
        pno_rh_data[mn] = normalize(rh_evs)
    if lh_evs:
        pno_lh_data[mn] = normalize(lh_evs)


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
# V6: Layered intro BUILD-UP (mm.1-8) and outro DECAY (mm.75-82)
# Other instruments join progressively / drop progressively, stacking
# chord tones around the piano motif.
# ============================================================
def sustained_tone(chord_name, role, octave):
    pc = CHORD_TONES_PC[chord_name][role]
    return [N(f"{pc}{octave}", BAR_QL)]


# --- INTRO build (mm.1-2 piano alone; mm.3-8 progressive stacking) ---
# mm.3-4: bass layer enters (Vc + Cb)
for mn in [3, 4]:
    ch = detect_chord(mn) or 'G'
    vc_data[mn] = vc_pad_bar(ch)
    cb_data[mn] = cb_pad_bar(ch)

# mm.5-6: + inner voice (Va)
for mn in [5, 6]:
    ch = detect_chord(mn) or 'G'
    vc_data[mn] = vc_pad_bar(ch)
    cb_data[mn] = cb_pad_bar(ch)
    va_data[mn] = va_pad_bar(ch)

# mm.7-8: full anticipation chord (+ Vn1 high, Vn2, Cl)
for mn in [7, 8]:
    ch = detect_chord(mn) or 'G'
    vc_data[mn] = vc_pad_bar(ch)
    cb_data[mn] = cb_pad_bar(ch)
    va_data[mn] = va_pad_bar(ch)
    vn2_data[mn] = vn2_pad_bar(ch)
    vn1_data[mn] = sustained_tone(ch, 'fifth', 5)
    cl_data[mn] = sustained_tone(ch, 'root', 5)

# --- OUTRO decay (mm.75-82) ---
# mm.75-76: full ensemble sustain (chorus aftermath)
for mn in [75, 76]:
    ch = detect_chord(mn) or 'G'
    vc_data[mn] = vc_pad_bar(ch)
    cb_data[mn] = cb_pad_bar(ch)
    va_data[mn] = va_pad_bar(ch)
    vn2_data[mn] = vn2_pad_bar(ch)
    vn1_data[mn] = sustained_tone(ch, 'fifth', 5)
    cl_data[mn] = sustained_tone(ch, 'third', 5)
    fl_data[mn] = sustained_tone(ch, 'fifth', 5)

# mm.77-78: highest layers drop (Vn1, Fl out; Cl remains as warm color)
for mn in [77, 78]:
    ch = detect_chord(mn) or 'G'
    vc_data[mn] = vc_pad_bar(ch)
    cb_data[mn] = cb_pad_bar(ch)
    va_data[mn] = va_pad_bar(ch)
    vn2_data[mn] = vn2_pad_bar(ch)
    cl_data[mn] = sustained_tone(ch, 'third', 5)

# mm.79-80: Vn2 + Cl drop, low strings remain
for mn in [79, 80]:
    ch = detect_chord(mn) or 'G'
    vc_data[mn] = vc_pad_bar(ch)
    cb_data[mn] = cb_pad_bar(ch)
    va_data[mn] = va_pad_bar(ch)

# m.81: only Cb remains (deepest layer last)
for mn in [81]:
    ch = detect_chord(mn) or 'G'
    cb_data[mn] = cb_pad_bar(ch)

# m.82: piano motif alone again, fading to silence (no overrides)


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

# V7: Add Vc to chorus tutti (mm.66-74) at octave below — 5-part harmony chorus
for mn in range(66, 75):
    mel = melody_for('Vc', mn, transpose_semi=-12)
    vc_data[mn] = mel

# V7: Fl high counter-melody during Vc cantabile (mm.33-40)
def fl_high_counter_bar(chord_name):
    """Slow chord-tone counter line above Vc cantabile."""
    third_pc = CHORD_TONES_PC[chord_name]['third']
    fifth_pc = CHORD_TONES_PC[chord_name]['fifth']
    root_pc  = CHORD_TONES_PC[chord_name]['root']
    return [N(f"{fifth_pc}5", 1.5),
            N(f"{third_pc}5", 1.5),
            N(f"{fifth_pc}5", 1.5),
            N(f"{root_pc}6", 1.5)]


for mn in range(33, 41):
    chord = detect_chord(mn) or 'G'
    fl_data[mn] = fl_high_counter_bar(chord)

# V7: Bb Clarinet — convert all cl_data from sounding to written pitch (+M2)
# music21 treats Note pitches on transposing instruments as WRITTEN pitch.
# Our cl_data was constructed as sounding pitch (so it sounded right relative
# to other instruments in V6). Now we shift by +2 semitones so the input is
# written pitch — MuseScore will display written notation; the Clarinet's
# automatic -M2 transposition restores the correct sounding pitch in MIDI.
for _mn in cl_data:
    cl_data[_mn] = transpose_events(cl_data[_mn], 2)


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
# V8: ORCHESTRAL TEXTURE — rhythmic counter-figures + real Va counter-melody
# ============================================================
# Replaces sustained whole-bar pads with rhythmic figures so non-melody
# instruments contribute musical motion rather than static drone.
# Vn1 high pedal stays sustained to preserve orchestral 'shimmer' on top.

def _is_whole_bar_sustain(events):
    if len(events) == 1 and isinstance(events[0], nmod.Note):
        return abs(float(events[0].duration.quarterLength) - BAR_QL) < 0.01
    return False


def _fit_oct(pc, lo, hi, octs):
    from music21 import pitch as _pmod
    for oc in octs:
        midi = _pmod.Pitch(f"{pc}{oc}").midi
        if lo <= midi <= hi:
            return f"{pc}{oc}"
    return f"{pc}{octs[0]}"


# 1) Replace whole-bar sustained pads with rhythmic patterns (mm.9-74)
#    Skips mm.1-8 (V6 layered build) and mm.75-82 (V6 layered decay).
#    Skips Vn1 (high pedal stays sustained for shimmer).
for _mn in range(9, 75):
    _ch = detect_chord(_mn) or 'G'
    _f_pc = CHORD_TONES_PC[_ch]['fifth']
    _t_pc = CHORD_TONES_PC[_ch]['third']
    _r_pc = CHORD_TONES_PC[_ch]['root']

    # Vn2: 4-dotted-quarter pulse on chord 5th
    if _is_whole_bar_sustain(vn2_data[_mn]):
        _p = _fit_oct(_f_pc, 55, 76, (4, 3, 5))
        vn2_data[_mn] = [N(_p, 1.5) for _ in range(4)]

    # Va: 3rd-5th alternation pulse (inner voice rhythm)
    if _is_whole_bar_sustain(va_data[_mn]):
        _t = _fit_oct(_t_pc, 48, 64, (3, 4))
        _f = _fit_oct(_f_pc, 48, 64, (3, 4))
        va_data[_mn] = [N(_t, 1.5), N(_f, 1.5), N(_t, 1.5), N(_f, 1.5)]

    # Vc: root-5th alternation (orchestral bass anchor)
    if _is_whole_bar_sustain(vc_data[_mn]):
        _r = _fit_oct(_r_pc, 36, 55, (2, 3))
        _f = _fit_oct(_f_pc, 36, 55, (3, 2))
        vc_data[_mn] = [N(_r, 1.5), N(_f, 1.5), N(_r, 1.5), N(_f, 1.5)]

    # Cb: pizzicato on beat 1+3 (typical orchestral bass anchoring)
    if _is_whole_bar_sustain(cb_data[_mn]):
        _r = _fit_oct(_r_pc, 28, 50, (2, 3))
        cb_data[_mn] = [N(_r, 1.5), R(1.5), N(_r, 1.5), R(1.5)]


# 2) Va REAL stepwise counter-melody during Vc cantabile bridge (mm.33-40)
#    Genuine melodic counter-line in dialogue with Vc — diatonic G major contour
_va_bridge = {
    33: ['B3', 'A3', 'G3', 'A3'],
    34: ['A3', 'G3', 'F#3', 'G3'],
    35: ['G3', 'A3', 'B3', 'A3'],
    36: ['A3', 'B3', 'C4', 'B3'],
    37: ['B3', 'A3', 'G3', 'A3'],
    38: ['A3', 'G3', 'F#3', 'G3'],
    39: ['G3', 'A3', 'B3', 'C4'],
    40: ['B3', 'A3', 'G3', 'F#3'],
}
for _mn, _ns in _va_bridge.items():
    va_data[_mn] = [N(p, 1.5) for p in _ns]


# 3) Fl sparse melodic response during Vc cantabile bridge (mm.33-40)
#    Replaces V7 fl_high_counter (which was just chord-tone arpeggio).
#    Pattern: rest -> brief ascending response -> high pedal -> descending response,
#    cycling across two 4-bar groups for breathing dialogue with Vc.
def _fl_bridge_response(chord_name, pos):
    t_pc = CHORD_TONES_PC[chord_name]['third']
    f_pc = CHORD_TONES_PC[chord_name]['fifth']
    r_pc = CHORD_TONES_PC[chord_name]['root']
    if pos == 0:
        # Rest — let Vc establish the phrase
        return [R(BAR_QL)]
    if pos == 1:
        # Brief ascending 8th-note figure in last beat
        return [R(4.5),
                N(f"{t_pc}5", 0.5), N(f"{f_pc}5", 0.5), N(f"{r_pc}6", 0.5)]
    if pos == 2:
        # High sustained pedal in second half
        return [R(3.0), N(f"{f_pc}6", 3.0)]
    if pos == 3:
        # Descending dotted-quarter response
        return [N(f"{r_pc}6", 1.5), N(f"{f_pc}5", 1.5),
                N(f"{t_pc}5", 1.5), R(1.5)]
    return [R(BAR_QL)]


_fl_pat = [0, 1, 2, 3, 0, 1, 2, 3]
for _i, _mn in enumerate(range(33, 41)):
    _ch = detect_chord(_mn) or 'G'
    fl_data[_mn] = _fl_bridge_response(_ch, _fl_pat[_i])


# ============================================================
# V9: DIATONIC interval fixes for parallel-line phrases
# ============================================================
# Bug: V8 used fixed CHROMATIC semitones for parallel-interval transposition,
# which produced non-diatonic notes (G#, C#, D#) when the melody hit B, E, F#
# in G major. Audible clash against the diatonic harmony.
#
# Fix: use DIATONIC intervals — the interval QUALITY (m3 vs M3, etc.) varies
# per scale degree to keep all notes inside G major.

from music21 import interval as _imod


def _gmaj_3rd_below(pc):
    return _imod.Interval('-M3') if pc in ('B', 'E', 'F#') else _imod.Interval('-m3')


def _gmaj_5th_below(pc):
    return _imod.Interval('-d5') if pc == 'C' else _imod.Interval('-P5')


def _gmaj_6th_below(pc):
    return _imod.Interval('-M6') if pc in ('A', 'B', 'E', 'F#') else _imod.Interval('-m6')


def _diatonic_transform(events, interval_func):
    out = []
    for e in events:
        if isinstance(e, nmod.Note):
            iv = interval_func(e.pitch.name)
            out.append(N(e.pitch.transpose(iv).nameWithOctave, e.duration.quarterLength))
        elif isinstance(e, cmod.Chord):
            new_pcs = [p.transpose(interval_func(p.name)).nameWithOctave for p in e.pitches]
            out.append(CH(new_pcs, e.duration.quarterLength))
        else:
            out.append(clone(e))
    return out


# Phrase 3 (mm.25-32): Cl // diatonic 3rd below Fl in G major
for _mn in range(25, 33):
    _voice = [clone(n) for _, n in measure_events(P_VOX, _mn)]
    if not _voice:
        continue
    _cl_s = _diatonic_transform(_voice, _gmaj_3rd_below)
    _cl_s = shift_to_range(_cl_s, 55, 84)
    _cl_s = normalize(_cl_s)
    cl_data[_mn] = transpose_events(_cl_s, 2)   # +M2 to written (Bb Cl)

# Phrase 7 (mm.58-65) climax: Vn2 // diatonic 6th below
for _mn in range(58, 66):
    _voice = [clone(n) for _, n in measure_events(P_VOX, _mn)]
    if not _voice:
        continue
    _vn2_s = _diatonic_transform(_voice, _gmaj_6th_below)
    _vn2_s = shift_to_range(_vn2_s, 55, 84)
    _vn2_s = normalize(_vn2_s)
    vn2_data[_mn] = _vn2_s

# Phrase 8 (mm.66-74) chorus tutti:
#   Vn2 // diatonic 6th below
#   Cl // diatonic 5th below (P5 except d5 from C → F#, staying in scale)
for _mn in range(66, 75):
    _voice = [clone(n) for _, n in measure_events(P_VOX, _mn)]
    if not _voice:
        continue

    _vn2_s = _diatonic_transform(_voice, _gmaj_6th_below)
    _vn2_s = shift_to_range(_vn2_s, 55, 84)
    _vn2_s = normalize(_vn2_s)
    vn2_data[_mn] = _vn2_s

    _cl_s = _diatonic_transform(_voice, _gmaj_5th_below)
    _cl_s = shift_to_range(_cl_s, 55, 84)
    _cl_s = normalize(_cl_s)
    cl_data[_mn] = transpose_events(_cl_s, 2)


# ============================================================
# V10: Piano RH playable voicings — close-position root + 3rd + 5th + root_8va
# ============================================================
# V8/V9 had a bug: voicing logic placed 5th in oct 4 below the 3rd in some
# chord cases (e.g., Bm: D4-F#4-B4-B5 spanning 21 semitones), creating
# unplayable single-hand chord stretches > M14.
#
# V10 fix: hardcoded close-position root-position voicings, all spanning
# exactly an octave (12 semitones) — comfortable for any pianist.

CLOSE_VOICINGS_V10 = {
    'G':     ['G4', 'B4', 'D5', 'G5'],
    'Am':    ['A4', 'C5', 'E5', 'A5'],
    'Bm':    ['B4', 'D5', 'F#5', 'B5'],
    'C':     ['C5', 'E5', 'G5', 'C6'],
    'D':     ['D4', 'F#4', 'A4', 'D5'],
    'Em':    ['E4', 'G4', 'B4', 'E5'],
    'F#dim': ['F#4', 'A4', 'C5', 'F#5'],
}


def _piano_rh_bar_v10(chord_name, dyn):
    if not chord_name:
        return [R(BAR_QL)]
    voicing4 = CLOSE_VOICINGS_V10.get(chord_name, CLOSE_VOICINGS_V10['G'])
    voicing3 = voicing4[:3]   # root, 3rd, 5th (for arpeggio cycle)

    if dyn == 'arpeggio':
        out = []
        for _ in range(4):
            for nm in voicing3:
                out.append(N(nm, 0.5))
        return out
    if dyn == 'sparse':
        return [CH(voicing4, 1.5), R(BAR_QL - 1.5)]
    if dyn == 'verse':
        return [CH(voicing4, 1.5), R(1.5), CH(voicing4, 1.5), R(1.5)]
    if dyn == 'full':
        return [CH(voicing4, 1.5) for _ in range(4)]
    return [CH(voicing4, 1.5), R(1.5), CH(voicing4, 1.5), R(1.5)]


# Rebuild pno_rh_data with V10 voicings (mm.9-74)
for _mn in range(1, 83):
    _ch = detect_chord(_mn)
    _stg = piano_stage(_mn)
    pno_rh_data[_mn] = normalize(_piano_rh_bar_v10(_ch, _stg))

# Restore V5 intro/outro original ostinato figure (mm.1-8 + mm.75-82)
for _mn in list(range(1, 9)) + list(range(75, 83)):
    _rh = [clone(n) for _, n in measure_events(P_RH, _mn)]
    if _rh:
        pno_rh_data[_mn] = normalize(_rh)


# ============================================================
# V11: Range cleanup so MuseScore highlights none of the notes red.
#      Also fix Bb Clarinet key signature to A major (3 sharps).
# ============================================================
# MuseScore amateur ranges:
#   Flute      C4-A6  (60-93)
#   Violin     G3-G6  (55-91)
#   Contrabass E2-G3 written (40-55)
# Notes outside these are highlighted red. Pro players can play them, but
# the score should be clean for orchestral readability.

_E2_MIDI = 40   # Cb minimum (4-string standard)
_FL_MAX  = 93   # A6 (Fl amateur upper)
_VN1_MAX = 91   # G6 (Vn1 amateur upper)


# 1) Contrabass: shift any note < E2 up by an octave (4-string compatible)
for _mn in cb_data:
    new_evs = []
    for e in cb_data[_mn]:
        if isinstance(e, nmod.Note) and e.pitch.midi < _E2_MIDI:
            new_evs.append(N(e.pitch.transpose(12).nameWithOctave,
                             e.duration.quarterLength))
        else:
            new_evs.append(clone(e))
    cb_data[_mn] = new_evs


# 2) Flute: shift any note > A6 down by an octave (avoids B6+ highlights)
for _mn in fl_data:
    new_evs = []
    for e in fl_data[_mn]:
        if isinstance(e, nmod.Note) and e.pitch.midi > _FL_MAX:
            new_evs.append(N(e.pitch.transpose(-12).nameWithOctave,
                             e.duration.quarterLength))
        else:
            new_evs.append(clone(e))
    fl_data[_mn] = new_evs


# 3) Violin 1: in chord events, drop any pitch > G6 (keep lower note(s))
for _mn in vn1_data:
    new_evs = []
    for e in vn1_data[_mn]:
        if isinstance(e, cmod.Chord):
            kept = [p for p in e.pitches if p.midi <= _VN1_MAX]
            if len(kept) >= 2:
                new_evs.append(CH([p.nameWithOctave for p in kept],
                                  e.duration.quarterLength))
            elif len(kept) == 1:
                new_evs.append(N(kept[0].nameWithOctave, e.duration.quarterLength))
            else:
                # All pitches above G6 — transpose all down an octave
                lowered = [p.transpose(-12) for p in e.pitches]
                new_evs.append(CH([p.nameWithOctave for p in lowered],
                                  e.duration.quarterLength))
        elif isinstance(e, nmod.Note) and e.pitch.midi > _VN1_MAX:
            new_evs.append(N(e.pitch.transpose(-12).nameWithOctave,
                             e.duration.quarterLength))
        else:
            new_evs.append(clone(e))
    vn1_data[_mn] = new_evs


# ============================================================
# Build parts
# ============================================================
common = dict(
    key_sharps=KEY_SHARPS, time_sig=TIME_SIG,
    measures_per_bar_ql=BAR_QL, fermata_on_last=False,
)

# Dynamic arc and expressions (V6 adds intro build + outro decay markings)
vn1_dyn   = {1: 'p', 7: 'p', 17: 'mp', 49: 'mp', 58: 'f', 66: 'ff', 73: 'mf', 75: 'mp', 77: 'p'}
vn1_expr  = {7: 'enter, anticipation', 17: 'cantabile', 49: 'espress.',
             58: 'tutti, soaring', 66: 'tutti', 77: 'dim. (decay)'}
vn2_dyn   = {1: 'pp', 7: 'pp', 9: 'pp', 41: 'mp', 58: 'mf', 66: 'f', 75: 'mp', 79: 'p'}
vn2_expr  = {7: 'enter', 9: '(pad)', 41: '8va w/ Va', 58: '(6th below)',
             66: '(harmony)', 79: 'dim. (decay)'}
va_dyn    = {1: 'pp', 5: 'pp', 9: 'pp', 41: 'mp', 58: 'mf', 66: 'f', 75: 'mp', 79: 'p'}
va_expr   = {5: 'enter (inner)', 9: '(pad)', 41: 'octave below Vn2',
             49: 'sotto voce', 58: '(pad)', 66: '(divisi)', 79: 'dim.'}
vc_dyn    = {1: 'pp', 3: 'pp', 33: 'mp', 49: 'mp', 58: 'mf', 66: 'f', 75: 'mp', 79: 'p'}
vc_expr   = {3: 'enter (bass)', 33: 'cantabile, espress.', 49: '(pad)',
             66: '(divisi)', 79: 'dim.'}
cb_dyn    = {1: 'pp', 3: 'pp', 41: 'mp', 58: 'mf', 66: 'f', 75: 'mp', 79: 'p', 81: 'pp'}
cb_expr   = {3: 'enter, pizz.', 9: 'pizz.', 41: 'arco', 73: 'arco', 79: 'dim. e morendo'}
fl_dyn    = {25: 'mp', 41: 'mp', 58: 'mf', 66: 'ff', 75: 'mp'}
fl_expr   = {25: 'leggiero (// 3rds w/ Cl)', 41: 'obbligato',
             58: 'unison w/ Vn1', 66: 'tutti', 75: '(sustain)', 77: 'tacet'}
cl_dyn    = {7: 'pp', 9: 'mp', 17: 'p', 25: 'mp', 66: 'mf', 75: 'mp', 79: 'p'}
cl_expr   = {7: 'enter, dolce', 9: 'dolce, solo', 17: 'obbligato (16ths)',
             25: '// 3rds below Fl', 66: '(harmony)', 79: 'dim.'}
pno_dyn   = {1: 'pp', 9: 'p', 25: 'mp', 41: 'mf', 58: 'f', 66: 'ff', 75: 'mp', 81: 'pp'}
pno_expr  = {1: 'leggiero', 41: 'arpeggio', 58: 'arpeggio',
             75: 'dim. al fine', 81: 'morendo'}
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
                dyn_map=cl_dyn, expr_map=cl_expr,
                **{**common, 'key_sharps': 3})   # A major (concert G + M2)
pno_rh = make_part("Piano (R.H.)", "Pf", "piano", pno_rh_data,
                   clef_obj=clefmod.TrebleClef(),
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
