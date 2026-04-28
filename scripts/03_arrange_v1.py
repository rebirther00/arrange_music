"""Phase 3 V1: Mozart K.330 mvt.I → Violin Duet, Disney style.
16 measures: mm.1-8 = Mozart melody with Disney reharmonization,
mm.9-16 = Disney variation developing Mozart motives.

Output: arrangement/versions/v1.musicxml + .mid
"""
from pathlib import Path
from music21 import (stream, note, chord, meter, key, clef, instrument,
                     tempo, metadata, dynamics, expressions, articulations,
                     spanner, bar, layout)

OUT_DIR = Path(r"c:/Users/onest/Documents/music_arrange/arrangement/versions")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Helper builders ---
def N(name, ql):
    return note.Note(name, quarterLength=ql)

def R(ql):
    return note.Rest(quarterLength=ql)

def CH(names, ql):
    return chord.Chord(names, quarterLength=ql)

def make_measure(num, events):
    m = stream.Measure(number=num)
    for e in events:
        m.append(e)
    return m

# --- VIOLIN 1 (Solo melody, Mozart-derived + Disney lyric extensions) ---
vn1_data = {
    # mm.1-8: Mozart's RH (lightly adapted)
    1: [N('G5', 0.5), N('G5', 0.75), N('F5', 0.125), N('E5', 0.125),
        N('E5', 0.125), N('D5', 0.125), N('C5', 0.125), N('B4', 0.125)],
    2: [N('C5', 0.75), N('D5', 0.125), N('E5', 0.125),
        N('F5', 0.25), N('E5', 0.25), N('D5', 0.25), N('C5', 0.25)],
    3: [N('G5', 0.25), N('G5', 0.25), N('G5', 0.75), N('F5', 0.125), N('E5', 0.125),
        N('E5', 0.125), N('D5', 0.125), N('C5', 0.125), N('B4', 0.125)],
    4: [N('C5', 0.5), N('D5', 0.25), N('E5', 0.25),
        N('F5', 0.25), N('E5', 0.25), N('D5', 0.25), N('C5', 0.25)],
    # mm.5-6: arpeggio (Mozart) extended to high register
    5: [N('A4', 0.25), N('C5', 0.25), N('F5', 0.25), N('A5', 0.25),
        N('C6', 0.5), N('A5', 0.25), N('F5', 0.25)],
    6: [N('G4', 0.25), N('C5', 0.25), N('E5', 0.25), N('G5', 0.25),
        N('C6', 0.5), N('G5', 0.25), N('E5', 0.25)],
    # m.7: Disney-style climactic sustained line
    7: [N('B5', 0.5), N('A5', 0.5), N('G5', 0.5), N('F5', 0.25), N('E5', 0.25)],
    # m.8: cadential
    8: [N('D5', 0.5), N('C5', 0.5), N('E5', 0.5), N('G5', 0.5)],

    # mm.9-12: Disney bridge (developing Mozart motives, ascending sequence)
    9:  [N('E5', 0.25), N('F5', 0.25), N('G5', 0.25), N('A5', 0.25),
         N('B5', 0.5), N('A5', 0.5)],
    10: [N('A5', 0.5), N('G5', 0.5), N('F5', 0.25), N('E5', 0.25), N('D5', 0.25), N('C5', 0.25)],
    11: [N('D5', 0.25), N('E5', 0.25), N('F5', 0.25), N('G5', 0.25),
         N('A5', 0.5), N('G5', 0.5)],
    12: [N('A5', 0.25), N('B5', 0.25), N('C6', 0.25), N('B5', 0.25),
         N('C6', 0.5), N('B5', 0.5)],

    # mm.13-16: climactic return + cadence
    13: [N('A5', 0.5), N('G5', 0.5), N('F5', 0.5), N('E5', 0.5)],
    14: [N('D5', 0.25), N('E5', 0.25), N('F5', 0.25), N('G5', 0.25),
         N('A5', 0.5), N('G5', 0.5)],
    15: [N('F5', 0.25), N('E5', 0.25), N('D5', 0.25), N('B4', 0.25),
         N('C5', 0.5), N('D5', 0.5)],
    16: [N('C5', 2.0)],   # final whole note (in 2/4, this fills the bar)
}

# --- VIOLIN 2 (Disney harmonization: 7th/9th chord broken figures) ---
vn2_data = {
    # m.1: Cmaj7 broken (C E G B), gentle pulse
    1: [N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25),
        N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25)],
    # m.2: Am7 → Fmaj7  (root raised to F4 for violin range)
    2: [N('A3', 0.25), N('E4', 0.25), N('C4', 0.25), N('G4', 0.25),
        N('F4', 0.25), N('C4', 0.25), N('A3', 0.25), N('E4', 0.25)],
    # m.3: back to Cmaj7
    3: [N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25),
        N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25)],
    # m.4: Dm7 → G7
    4: [N('D4', 0.25), N('A4', 0.25), N('F4', 0.25), N('C5', 0.25),
        N('G3', 0.25), N('D4', 0.25), N('B4', 0.25), N('F4', 0.25)],
    # m.5: Fmaj9 (F A C E G) broken (root F4)
    5: [N('F4', 0.25), N('C4', 0.25), N('A4', 0.25), N('C5', 0.25),
        N('F4', 0.25), N('C4', 0.25), N('A4', 0.25), N('E5', 0.25)],
    # m.6: C/E (E G C broken)
    6: [N('E4', 0.25), N('G4', 0.25), N('C5', 0.25), N('E5', 0.25),
        N('E4', 0.25), N('G4', 0.25), N('C5', 0.25), N('E5', 0.25)],
    # m.7: G13 (G B D F A E), Disney-tinged dominant — broken via realistic violin range
    7: [N('G3', 0.25), N('D4', 0.25), N('B4', 0.25), N('F4', 0.25),
        N('G3', 0.25), N('D4', 0.25), N('A4', 0.25), N('F4', 0.25)],
    # m.8: C major resolution (C E G C broken) + cadential prep
    8: [N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('G4', 0.25),
        N('C4', 0.5), N('E4', 0.25), N('G4', 0.25)],

    # m.9: Am7 (vi) broken — Disney minor color
    9:  [N('A3', 0.25), N('E4', 0.25), N('C5', 0.25), N('E4', 0.25),
         N('A3', 0.25), N('E4', 0.25), N('C5', 0.25), N('E4', 0.25)],
    # m.10: F (IV) → Dm7 (ii)
    10: [N('F4', 0.25), N('C4', 0.25), N('A4', 0.25), N('C5', 0.25),
         N('D4', 0.25), N('A4', 0.25), N('F4', 0.25), N('A4', 0.25)],
    # m.11: G7sus4 (build tension)
    11: [N('G3', 0.25), N('D4', 0.25), N('C5', 0.25), N('F4', 0.25),
         N('G3', 0.25), N('D4', 0.25), N('C5', 0.25), N('F4', 0.25)],
    # m.12: G7 → C (climax resolution preparation)
    12: [N('G3', 0.25), N('D4', 0.25), N('B4', 0.25), N('F4', 0.25),
         N('C4', 0.25), N('G4', 0.25), N('E5', 0.25), N('C5', 0.25)],

    # m.13: F (IV) restatement — descending support
    13: [N('F4', 0.25), N('C4', 0.25), N('A4', 0.25), N('C5', 0.25),
         N('F4', 0.25), N('C4', 0.25), N('A4', 0.25), N('F4', 0.25)],
    # m.14: C/E (I/3)
    14: [N('E4', 0.25), N('G4', 0.25), N('C5', 0.25), N('E5', 0.25),
         N('E4', 0.25), N('G4', 0.25), N('C5', 0.25), N('G4', 0.25)],
    # m.15: G7sus4 → G7 (final dominant prep)
    15: [N('G3', 0.25), N('D4', 0.25), N('C5', 0.25), N('F4', 0.25),
         N('G3', 0.25), N('B3', 0.25), N('D4', 0.25), N('F4', 0.25)],
    # m.16: C major final — sustained chord (double-stop, playable: G4 + C5)
    16: [CH(['G4', 'C5'], 2.0)],
}


def build_part(name, abbrev, midi_program, data, dynamic="mp", text_mark=None):
    p = stream.Part()
    p.id = name
    p.partName = name
    p.partAbbreviation = abbrev
    p.insert(0, instrument.Violin())

    # Build measures (the first measure carries clef/key/time/tempo/dynamic)
    for mn in sorted(data.keys()):
        m = make_measure(mn, data[mn])
        if mn == 1:
            m.insert(0, clef.TrebleClef())
            m.insert(0, key.KeySignature(0))  # C major
            m.insert(0, meter.TimeSignature("2/4"))
            m.insert(0, tempo.MetronomeMark(text="Allegretto", number=104,
                                             referent=note.Note(type='quarter')))
            if text_mark:
                te = expressions.TextExpression(text_mark)
                te.style.fontStyle = 'italic'
                m.insert(0, te)
            m.insert(0, dynamics.Dynamic(dynamic))
        # Add a final barline at end
        if mn == 16:
            m.rightBarline = bar.Barline('final')
        p.append(m)

    # Verify measure lengths
    for m in p.getElementsByClass('Measure'):
        total = sum(float(e.duration.quarterLength) for e in m.notesAndRests)
        if abs(total - 2.0) > 0.001:
            raise ValueError(f"{name} measure {m.number} duration = {total}, expected 2.0")
    return p


def main():
    score = stream.Score()
    score.insert(0, metadata.Metadata())
    score.metadata.title = "A Disney Reverie on Mozart K.330"
    score.metadata.subtitle = "after Sonata No.10, Mvt.I (Allegretto)"
    score.metadata.composer = "W.A. Mozart"
    score.metadata.arranger = "arr. for Violin Duet (Disney style)"
    score.metadata.copyright = "Arrangement (c) 2026"

    vn1 = build_part("Violin 1", "Vn 1", 41, vn1_data, dynamic="mp",
                     text_mark="dolce, with wonder")
    vn2 = build_part("Violin 2", "Vn 2", 41, vn2_data, dynamic="p")

    score.insert(0, vn1)
    score.insert(0, vn2)

    # Add staff group (brace for piano not needed; 2 separate violin staves)
    sg = layout.StaffGroup([vn1, vn2], name='Violin Duet', symbol='bracket')
    score.insert(0, sg)

    # Output paths
    xml_path = OUT_DIR / "v1.musicxml"
    mid_path = OUT_DIR / "v1.mid"

    score.write('musicxml', fp=str(xml_path))
    score.write('midi', fp=str(mid_path))

    print(f"\n=== ARRANGEMENT V1 GENERATED ===")
    print(f"  MusicXML: {xml_path}")
    print(f"  MIDI:     {mid_path}")
    print(f"\nStructure summary:")
    for p in score.parts:
        m_count = len(p.getElementsByClass('Measure'))
        n_count = len(list(p.recurse().notes))
        # Pitch range
        pitches = []
        for x in p.recurse().notes:
            if isinstance(x, note.Note):
                pitches.append(x.pitch)
            elif isinstance(x, chord.Chord):
                pitches.extend(x.pitches)
        lo, hi = min(pitches, key=lambda p: p.midi), max(pitches, key=lambda p: p.midi)
        print(f"  {p.partName}: {m_count} measures, {n_count} notes/chords, range {lo.nameWithOctave}-{hi.nameWithOctave} (MIDI {lo.midi}-{hi.midi})")

    # Range check (violin: G3=55 to E7=100, comfortable up to ~A6=93)
    print(f"\nViolin range validation (G3=55 .. E7=100):")
    for p in score.parts:
        pitches = []
        for x in p.recurse().notes:
            if isinstance(x, note.Note):
                pitches.append(x.pitch.midi)
            elif isinstance(x, chord.Chord):
                pitches.extend(pp.midi for pp in x.pitches)
        out_of_range = [m for m in pitches if m < 55 or m > 100]
        print(f"  {p.partName}: {'OK' if not out_of_range else f'OUT-OF-RANGE: {out_of_range}'}")


if __name__ == "__main__":
    main()
