"""Phase 2: Extract mm.1-16 RH/LH and produce a clean musical analysis dump."""
from pathlib import Path
from music21 import converter, note, chord

MXL = Path(r"c:/Users/onest/Documents/music_arrange/output_full/모짜르트 피아노 소나타 no.10, K.330 (Henle).mvt1.mxl")
score = converter.parse(str(MXL))
parts = score.parts
rh, lh = parts[0], parts[1]

def measure_seq(m):
    """Flatten all voices in a measure into a chronological event list."""
    events = []
    if m.voices:
        # Sort all voice elements by offset
        for v in m.voices:
            for n in v.notesAndRests:
                events.append((float(n.offset), n))
    else:
        for n in m.notesAndRests:
            events.append((float(n.offset), n))
    events.sort(key=lambda x: x[0])
    return events

def fmt(n):
    if isinstance(n, note.Note):
        return f"{n.nameWithOctave}({n.duration.quarterLength:g})"
    if isinstance(n, chord.Chord):
        return f"<{'/'.join(p.nameWithOctave for p in n.pitches)}>({n.duration.quarterLength:g})"
    if isinstance(n, note.Rest):
        return f"R({n.duration.quarterLength:g})"
    return f"?{type(n).__name__}"

print("=== K.330 Mvt.I, mm.1-16 (Original) ===\n")
out_lines = []
for mn in range(1, 17):
    m_rh = rh.measure(mn)
    m_lh = lh.measure(mn)
    rh_events = measure_seq(m_rh) if m_rh else []
    lh_events = measure_seq(m_lh) if m_lh else []
    line_rh = f"  RH m{mn:>2}: " + " ".join(f"@{o:g}{fmt(n)}" for o, n in rh_events)
    line_lh = f"  LH m{mn:>2}: " + " ".join(f"@{o:g}{fmt(n)}" for o, n in lh_events)
    out_lines.append(line_rh)
    out_lines.append(line_lh)
    out_lines.append("")

print("\n".join(out_lines))

# Save to file for reference
out_path = Path(r"c:/Users/onest/Documents/music_arrange/arrangement/extracts/mm1_16_dump.txt")
out_path.write_text("\n".join(out_lines), encoding="utf-8")
print(f"\nSaved to: {out_path}")
