"""Deeper verification: check both parts, detect empty measures, voice issues."""
from pathlib import Path
from music21 import converter, note, chord

MXL = Path(r"c:/Users/onest/Documents/music_arrange/output_full/모짜르트 피아노 소나타 no.10, K.330 (Henle).mvt1.mxl")
score = converter.parse(str(MXL))
parts = score.parts

print("=== Both parts, measures 1-8 ===")
for pi, p in enumerate(parts):
    print(f"\n-- Part {pi} ({p.partName!r}) --")
    for m in p.getElementsByClass('Measure')[:8]:
        notes_in = list(m.notesAndRests)
        # Also check voices
        voices = list(m.voices)
        v_summary = ""
        if voices:
            v_summary = f" [voices: {len(voices)}]"
            for vi, v in enumerate(voices):
                v_notes = list(v.notesAndRests)
                v_summary += f" v{vi}={len(v_notes)}"
        print(f"  m{m.number}: top-level={len(notes_in)}{v_summary}")

print("\n=== Empty measure count (top-level only) ===")
for pi, p in enumerate(parts):
    measures = list(p.getElementsByClass('Measure'))
    empty = [m.number for m in measures if len(list(m.notesAndRests)) == 0 and not list(m.voices)]
    voice_only = [m.number for m in measures if len(list(m.notesAndRests)) == 0 and list(m.voices)]
    print(f"  Part {pi}: total={len(measures)}, truly empty={len(empty)}, voice-only={len(voice_only)}")
    if empty[:10]:
        print(f"    truly empty (first 10): {empty[:10]}")
    if voice_only[:10]:
        print(f"    voice-only (first 10): {voice_only[:10]}")

print("\n=== Detail: Part 0 measure 2 (suspected empty) ===")
m2 = parts[0].measure(2)
if m2:
    print(f"  Number: {m2.number}, length: {m2.duration.quarterLength}")
    print(f"  All elements: {[type(e).__name__ for e in m2]}")
    for v in m2.voices:
        print(f"  Voice {v.id}: {[(type(n).__name__, getattr(n,'nameWithOctave','-'), n.duration.quarterLength) for n in v.notesAndRests][:10]}")

print("\n=== Detail: Part 1 measure 2 ===")
m2b = parts[1].measure(2)
if m2b:
    for v in m2b.voices:
        print(f"  Voice {v.id}: {[(type(n).__name__, getattr(n,'nameWithOctave','-'), n.duration.quarterLength) for n in v.notesAndRests][:10]}")
    if not m2b.voices:
        print(f"  Top-level: {[(type(e).__name__, getattr(e,'nameWithOctave','-'), getattr(e,'duration',None) and e.duration.quarterLength) for e in m2b.notesAndRests][:10]}")

print("\n=== mm.1-8 RH melody (Part 0, all voices) ===")
for m in parts[0].getElementsByClass('Measure')[:8]:
    seq = []
    if m.voices:
        for v in m.voices:
            for n in v.notesAndRests:
                if isinstance(n, note.Note):
                    seq.append(f"{n.nameWithOctave}({n.duration.quarterLength})")
                elif isinstance(n, chord.Chord):
                    seq.append(f"<{'/'.join(p.nameWithOctave for p in n.pitches)}>({n.duration.quarterLength})")
                elif isinstance(n, note.Rest):
                    seq.append(f"R({n.duration.quarterLength})")
    else:
        for n in m.notesAndRests:
            if isinstance(n, note.Note):
                seq.append(f"{n.nameWithOctave}({n.duration.quarterLength})")
            elif isinstance(n, chord.Chord):
                seq.append(f"<{'/'.join(p.nameWithOctave for p in n.pitches)}>({n.duration.quarterLength})")
            elif isinstance(n, note.Rest):
                seq.append(f"R({n.duration.quarterLength})")
    print(f"  m{m.number}: {' '.join(seq) if seq else '(empty)'}")

print("\n=== mm.1-8 LH (Part 1) ===")
for m in parts[1].getElementsByClass('Measure')[:8]:
    seq = []
    if m.voices:
        for v in m.voices:
            for n in v.notesAndRests:
                if isinstance(n, note.Note):
                    seq.append(f"{n.nameWithOctave}({n.duration.quarterLength})")
                elif isinstance(n, chord.Chord):
                    seq.append(f"<{'/'.join(p.nameWithOctave for p in n.pitches)}>({n.duration.quarterLength})")
                elif isinstance(n, note.Rest):
                    seq.append(f"R({n.duration.quarterLength})")
    else:
        for n in m.notesAndRests:
            if isinstance(n, note.Note):
                seq.append(f"{n.nameWithOctave}({n.duration.quarterLength})")
            elif isinstance(n, chord.Chord):
                seq.append(f"<{'/'.join(p.nameWithOctave for p in n.pitches)}>({n.duration.quarterLength})")
            elif isinstance(n, note.Rest):
                seq.append(f"R({n.duration.quarterLength})")
    print(f"  m{m.number}: {' '.join(seq) if seq else '(empty)'}")
