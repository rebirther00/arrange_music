"""Verify playability of all notes in V9 against professional ranges + chord stretches."""
import sys
from pathlib import Path
from music21 import converter, note as nmod, chord as cmod, pitch as pmod

mxl = Path(sys.argv[1] if len(sys.argv) > 1 else r"c:/Users/onest/Documents/music_arrange/demon_hunters_work/arrangement/versions/v10.musicxml")
score = converter.parse(str(mxl))

PRO_RANGES = {
    # MuseScore amateur ranges (default highlight threshold)
    # (name, lo, hi, comfortable_lo, comfortable_hi, max_chord_stretch_semi)
    'Flute':         (60, 93, 62, 91, 0),     # C4-A6 amateur
    'Clarinet':      (52, 91, 53, 89, 0),     # E3-G6 written amateur
    'Violin 1':      (55, 91, 55, 88, 12),    # G3-G6 amateur
    'Violin 2':      (55, 91, 55, 88, 12),
    'Viola':         (48, 86, 48, 81, 12),    # C3-D6 amateur
    'Violoncello':   (36, 81, 36, 76, 12),    # C2-A5 amateur
    'Contrabass':    (40, 55, 40, 50, 12),    # E2-G3 written amateur (4-string)
    'Piano (R.H.)':  (21, 108, 48, 84, 14),
    'Piano (L.H.)':  (21, 108, 24, 60, 14),
    'Drums':         (35, 81, 35, 81, 0),
}

print(f"{'Instrument':<16} {'Notes':<6} {'Range':<14} {'OOR_strict':<12} {'OOR_comfort':<13} {'Chord_max':<10} {'Status'}")
print("-" * 110)

issues = []
for p in score.parts:
    name = p.partName
    if name not in PRO_RANGES:
        continue
    pro_lo, pro_hi, comf_lo, comf_hi, max_stretch = PRO_RANGES[name]

    notes_or_chords = list(p.recurse().notes)
    all_pitches = []
    chord_spans = []
    for nc in notes_or_chords:
        if isinstance(nc, nmod.Note):
            all_pitches.append(nc.pitch.midi)
        elif isinstance(nc, cmod.Chord):
            midis = sorted(p.midi for p in nc.pitches)
            all_pitches.extend(midis)
            if len(midis) >= 2:
                chord_spans.append((max(midis) - min(midis), midis))
    if not all_pitches:
        continue

    lo, hi = min(all_pitches), max(all_pitches)
    lo_n = pmod.Pitch(midi=lo).nameWithOctave
    hi_n = pmod.Pitch(midi=hi).nameWithOctave
    oor_strict = sum(1 for m in all_pitches if m < pro_lo or m > pro_hi)
    oor_comfort = sum(1 for m in all_pitches if m < comf_lo or m > comf_hi)
    chord_max = max((s for s, _ in chord_spans), default=0)
    chord_violations = sum(1 for s, _ in chord_spans if s > max_stretch)

    status = []
    if oor_strict > 0:
        status.append(f"OOR_PRO={oor_strict}")
    if max_stretch > 0 and chord_violations > 0:
        status.append(f"CHORD_STRETCH={chord_violations}")
    status_str = " ".join(status) if status else "OK"

    print(f"{name:<16} {len(notes_or_chords):<6} {lo_n}-{hi_n:<10} {oor_strict:<12} {oor_comfort:<13} {chord_max:<10} {status_str}")

    if oor_strict > 0:
        bad = sorted({m for m in all_pitches if m < pro_lo or m > pro_hi})
        bad_names = [pmod.Pitch(midi=m).nameWithOctave for m in bad]
        issues.append(f"  {name}: {oor_strict} note(s) outside pro range. Specifics: {bad_names[:8]}")

    if max_stretch > 0 and chord_violations > 0:
        worst = sorted(chord_spans, key=lambda x: -x[0])[:3]
        for span_semi, midis in worst:
            note_names = [pmod.Pitch(midi=m).nameWithOctave for m in midis]
            issues.append(f"  {name}: chord stretch {span_semi} semitones (max {max_stretch}): {note_names}")

print("-" * 110)
if issues:
    print("\nISSUES FOUND:")
    for iss in issues:
        print(iss)
else:
    print("\nALL INSTRUMENTS WITHIN PROFESSIONAL PLAYABLE RANGES.")
