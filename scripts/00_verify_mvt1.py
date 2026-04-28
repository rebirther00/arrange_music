"""Phase 0: Verify mvt1.mxl conversion quality (music21 analysis)."""
import sys
from pathlib import Path
from music21 import converter, key, meter, pitch, note, chord, tempo

MXL = Path(r"c:/Users/onest/Documents/music_arrange/output_full/모짜르트 피아노 소나타 no.10, K.330 (Henle).mvt1.mxl")

print(f"Loading: {MXL.name}")
score = converter.parse(str(MXL))
print(f"  -> Loaded: {type(score).__name__}")

parts = score.parts
print(f"\n=== Structure ===")
print(f"  Parts: {len(parts)}")
for i, p in enumerate(parts):
    print(f"    Part {i}: {p.partName!r}, instrument={p.getInstrument().instrumentName}, measures={len(p.getElementsByClass('Measure'))}")

print(f"\n=== Time/Key signatures ===")
ts_list = list(score.recurse().getElementsByClass(meter.TimeSignature))[:3]
ks_list = list(score.recurse().getElementsByClass(key.KeySignature))[:3]
print(f"  Time sigs (first 3): {[str(t.ratioString) for t in ts_list]}")
print(f"  Key sigs (first 3): {[(k.sharps, str(k)) for k in ks_list]}")

tempo_marks = list(score.recurse().getElementsByClass(tempo.MetronomeMark))
text_dirs = list(score.recurse().getElementsByClass(tempo.TempoIndication))
print(f"  Tempo marks: {len(tempo_marks)}")
print(f"  Tempo indications (TextExpression count): {len(text_dirs)}")

print(f"\n=== Measure 1-4 detail (Part 0 = top staff) ===")
p0 = parts[0]
for m in p0.getElementsByClass('Measure')[:4]:
    notes_in = [n for n in m.notesAndRests]
    print(f"  Measure {m.number}: {len(notes_in)} elements")
    for n in notes_in[:8]:
        if isinstance(n, note.Rest):
            print(f"    Rest dur={n.duration.quarterLength}")
        elif isinstance(n, note.Note):
            print(f"    Note {n.nameWithOctave} dur={n.duration.quarterLength}")
        elif isinstance(n, chord.Chord):
            pitches = "/".join(p.nameWithOctave for p in n.pitches)
            print(f"    Chord {pitches} dur={n.duration.quarterLength}")
    if len(notes_in) > 8:
        print(f"    ... +{len(notes_in)-8} more")

print(f"\n=== Total counts ===")
all_notes = list(score.recurse().notes)
all_rests = list(score.recurse().getElementsByClass('Rest'))
print(f"  Total Note/Chord events: {len(all_notes)}")
print(f"  Total Rest events: {len(all_rests)}")

# Pitch range
pitches = []
for n in all_notes:
    if isinstance(n, note.Note):
        pitches.append(n.pitch)
    elif isinstance(n, chord.Chord):
        pitches.extend(n.pitches)
if pitches:
    lo = min(pitches, key=lambda p: p.midi)
    hi = max(pitches, key=lambda p: p.midi)
    print(f"  Pitch range: {lo.nameWithOctave} (MIDI {lo.midi}) -- {hi.nameWithOctave} (MIDI {hi.midi})")

# Measure count
m_count = max(len(p.getElementsByClass('Measure')) for p in parts)
print(f"  Max measures across parts: {m_count}")

print("\n=== VERIFICATION ===")
# Expected K.330 mvt1: C major, 2/4, ~150 measures
ok_key = ks_list and ks_list[0].sharps == 0
ok_time = ts_list and ts_list[0].ratioString == "2/4"
ok_meas = 145 <= m_count <= 155
print(f"  Key C major (0 sharps/flats): {'OK' if ok_key else 'FAIL'} (got {ks_list[0].sharps if ks_list else 'none'})")
print(f"  Time 2/4: {'OK' if ok_time else 'FAIL'} (got {ts_list[0].ratioString if ts_list else 'none'})")
print(f"  Measures ~150: {'OK' if ok_meas else 'WARN'} (got {m_count})")
print(f"\n  Overall: {'USABLE' if (ok_key and ok_time) else 'NEEDS REVIEW'}")
