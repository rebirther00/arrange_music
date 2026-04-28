"""Inspect demon_hunters mxl: parts, tempo, key, structure summary."""
from pathlib import Path
from music21 import converter, tempo, key as keymod, meter, note, chord

mxl = Path(r"c:/Users/onest/Documents/music_arrange/demon_hunters_work/output_full/demon_hunters_original.mxl")
score = converter.parse(str(mxl))
parts = list(score.parts)

print(f"Parts: {len(parts)}")
for i, p in enumerate(parts):
    instr = p.getInstrument()
    n_count = len(list(p.recurse().notes))
    pitches = []
    for x in p.recurse().notes:
        if isinstance(x, note.Note):
            pitches.append(x.pitch.midi)
        elif isinstance(x, chord.Chord):
            pitches.extend(pp.midi for pp in x.pitches)
    rng = (min(pitches), max(pitches)) if pitches else (None, None)
    m_count = len(p.getElementsByClass('Measure'))
    print(f"  Part {i}: name={p.partName!r} instr={instr.instrumentName} measures={m_count} notes={n_count} midi_range={rng}")

print("\nTempo marks:")
for t in score.recurse().getElementsByClass(tempo.MetronomeMark):
    print(f"  {t!r} (number={t.number}, text={t.text}, ref_ql={t.referent.quarterLength if t.referent else '?'})")

print("\nText expressions (first 10):")
from music21 import expressions
for i, te in enumerate(list(score.recurse().getElementsByClass(expressions.TextExpression))[:10]):
    print(f"  '{te.content}'")

# Per-part activity over measures (which parts have notes in which bars)
print("\nMeasure-by-measure activity (P=has_pitch, .=rest only):")
header = "      " + "".join(f"{m:3d}" for m in range(1, 83))
print(header[:240])
for pi, p in enumerate(parts):
    row = f"P{pi}: "
    for mn in range(1, 83):
        m = p.measure(mn)
        if not m:
            row += "   "
            continue
        has = False
        evs = list(m.notesAndRests)
        if m.voices:
            evs = [n for v in m.voices for n in v.notesAndRests]
        for n in evs:
            if isinstance(n, (note.Note, chord.Chord)) and n.duration.quarterLength > 0:
                has = True
                break
        row += " P " if has else " . "
    print(row[:240])
