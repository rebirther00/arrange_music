"""Phase 4b: V2 — Disney style violin duet, addressing V1 reviewer feedback.

Key V2 improvements over V1:
1. m.7 climax: extended sustained high note + Vn2 double-stop response
2. Dotted rhythms in mm.9, 11 (Disney signature)
3. Counter-melody dialogue between Vn1/Vn2 in mm.5-6, 10-11
4. Double-stops at cadence points (m.4, 8, 12, 16)
5. Full dynamic palette (pp, p, mp, mf, f, ff) + cresc/dim/rit/fermata
"""
from pathlib import Path
from music21 import (stream, note, chord, meter, key, clef, instrument,
                     tempo, metadata, dynamics, expressions, articulations,
                     spanner, bar, layout, repeat)

OUT_DIR = Path(r"c:/Users/onest/Documents/music_arrange/arrangement/versions")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def N(name, ql, **kwargs):
    n = note.Note(name, quarterLength=ql)
    return n


def R(ql):
    return note.Rest(quarterLength=ql)


def CH(names, ql):
    return chord.Chord(names, quarterLength=ql)


# ============================================================
# VIOLIN 1 (Solo melody — Disney lyrical with Mozart soul)
# ============================================================
vn1_data = {
    # m.1: Mozart's opening, intact
    1: [N('G5', 0.5), N('G5', 0.75), N('F5', 0.125), N('E5', 0.125),
        N('E5', 0.125), N('D5', 0.125), N('C5', 0.125), N('B4', 0.125)],
    # m.2: Mozart skeleton with Disney lyrical fill — "echo response"
    2: [N('C5', 0.75), N('D5', 0.125), N('E5', 0.125),
        N('F5', 0.25), N('E5', 0.25), N('D5', 0.25), N('C5', 0.25)],
    # m.3: Mozart variation — repeated G with descent
    3: [N('G5', 0.25), N('G5', 0.25), N('G5', 0.75), N('F5', 0.125), N('E5', 0.125),
        N('E5', 0.125), N('D5', 0.125), N('C5', 0.125), N('B4', 0.125)],
    # m.4: cadential — Vn1 holds while Vn2 takes over (handoff)
    4: [N('C5', 1.0), R(1.0)],
    # m.5: Vn1 silent — Vn2 has counter-melody (DIALOGUE)
    5: [R(2.0)],
    # m.6: Vn1 returns with answering arpeggio
    6: [N('G4', 0.25), N('C5', 0.25), N('E5', 0.25), N('G5', 0.25),
        N('C6', 0.5), N('G5', 0.25), N('E5', 0.25)],
    # m.7: DISNEY CLIMAX — sustained high note with crescendo
    7: [N('A5', 0.5), N('B5', 0.5), N('C6', 1.0)],   # rising to peak, sustained
    # m.8: cadential descent — gentle resolution
    8: [N('B5', 0.5), N('A5', 0.5), N('G5', 0.5), N('E5', 0.5)],

    # ===== Section B: Disney development =====
    # m.9: Disney signature dotted rhythm — "dance theme"
    9:  [N('E5', 0.75), N('F5', 0.25),    # dotted-eighth+sixteenth (♩.♬)
         N('G5', 0.5), N('A5', 0.5)],
    # m.10: continuing dance, ascending
    10: [N('A5', 0.75), N('G5', 0.25),    # dotted again
         N('F5', 0.5), N('E5', 0.5)],
    # m.11: dotted rhythm + leap (Disney lift)
    11: [N('D5', 0.75), N('E5', 0.25),
         N('F5', 0.5), N('G5', 0.5)],
    # m.12: peak — leap to high note with double-stop
    12: [N('A5', 0.5), N('B5', 0.5), CH(['C6', 'E6'], 1.0)],   # double-stop climax

    # ===== Section C: Triumphant return =====
    # m.13: descending lyrical line, decrescendo
    13: [N('G5', 0.5), N('F5', 0.5), N('E5', 0.5), N('D5', 0.5)],
    # m.14: settling, with grace
    14: [N('C5', 0.75), N('D5', 0.125), N('E5', 0.125),
         N('F5', 0.5), N('E5', 0.5)],
    # m.15: rit. preparation - dotted rhythm
    15: [N('D5', 0.75), N('C5', 0.25),
         N('B4', 0.5), N('D5', 0.5)],
    # m.16: FINAL — sustained double-stop, fermata, ff or with pause
    16: [CH(['E5', 'C6'], 2.0)],   # high tonic chord, sustained
}


# ============================================================
# VIOLIN 2 (Disney harmony + counter-melody)
# ============================================================
vn2_data = {
    # m.1: Cmaj7 broken — gentle, consistent pulse
    1: [N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25),
        N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25)],
    # m.2: Am7 → Fmaj7
    2: [N('A3', 0.25), N('E4', 0.25), N('C4', 0.25), N('G4', 0.25),
        N('F4', 0.25), N('C4', 0.25), N('A3', 0.25), N('E4', 0.25)],
    # m.3: Cmaj7 (back to home)
    3: [N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25),
        N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('B4', 0.25)],
    # m.4: Vn1 holds — Vn2 plays cadential figure with double-stop
    4: [N('D4', 0.25), N('F4', 0.25), N('A4', 0.25), N('C5', 0.25),
        CH(['G3', 'D4'], 0.5), CH(['B3', 'F4'], 0.5)],   # G7sus4 → G7 with double-stops
    # m.5: VN2 COUNTER-MELODY (Vn1 rests) — singing line
    5: [N('A4', 0.5), N('C5', 0.5), N('F5', 0.5), N('A4', 0.5)],   # F major answer melody
    # m.6: continues bass under Vn1's arpeggio
    6: [N('C4', 0.25), N('G4', 0.25), N('E4', 0.25), N('G4', 0.25),
        N('C4', 0.5), N('E4', 0.5)],
    # m.7: harmonic support for Vn1 climax — broken G dominant + double-stop
    7: [CH(['D4', 'F4'], 0.5), CH(['D4', 'B4'], 0.5),
        N('G3', 0.25), N('D4', 0.25), N('F4', 0.25), N('B4', 0.25)],
    # m.8: cadential resolution — full C major
    8: [N('C4', 0.5), N('E4', 0.5), N('G4', 0.5), CH(['C4', 'E4'], 0.5)],

    # m.9: dance bass — Disney syncopation
    9:  [N('A3', 0.5), N('E4', 0.25), N('C5', 0.25),
         N('F4', 0.5), N('A4', 0.25), N('E4', 0.25)],
    # m.10: Dm7 → Fmaj7 walking line
    10: [N('D4', 0.5), N('F4', 0.25), N('A4', 0.25),
         N('C5', 0.5), N('A4', 0.25), N('F4', 0.25)],
    # m.11: G7sus4 with sustained tension
    11: [N('G3', 0.5), N('D4', 0.25), N('C5', 0.25),
         N('B4', 0.5), N('F4', 0.25), N('D4', 0.25)],
    # m.12: G7 → C climax (under Vn1 double-stop)
    12: [N('G3', 0.25), N('B3', 0.25), N('D4', 0.25), N('F4', 0.25),
         CH(['C4', 'G4'], 1.0)],

    # m.13: F (IV) restatement — supporting Vn1 descent
    13: [N('F4', 0.25), N('A4', 0.25), N('C5', 0.25), N('A4', 0.25),
         N('F4', 0.5), N('A4', 0.5)],
    # m.14: C/E (I/3) — gentle bed
    14: [N('E4', 0.25), N('G4', 0.25), N('C5', 0.25), N('G4', 0.25),
         N('E4', 0.5), N('G4', 0.5)],
    # m.15: G7sus4 → G7 final dominant
    15: [N('G3', 0.25), N('D4', 0.25), N('C5', 0.25), N('F4', 0.25),
         N('G3', 0.5), N('B3', 0.5)],
    # m.16: C major final — perfect 5th double-stop, sustained
    16: [CH(['C4', 'G4'], 2.0)],
}

# Verify durations
def verify(data, name):
    for mn, evs in data.items():
        total = sum(float(e.duration.quarterLength) for e in evs)
        if abs(total - 2.0) > 0.001:
            raise ValueError(f"{name} m{mn} = {total} != 2.0")

verify(vn1_data, "VN1")
verify(vn2_data, "VN2")
print("Duration validation passed.")


# ============================================================
# Build score with rich expression markings
# ============================================================
def build_part(name, abbrev, data, dyn_map, expr_map):
    """
    dyn_map: {measure_number: dynamic_string}
    expr_map: {measure_number: text_expression}
    """
    p = stream.Part()
    p.id = name
    p.partName = name
    p.partAbbreviation = abbrev
    p.insert(0, instrument.Violin())

    for mn in sorted(data.keys()):
        m = stream.Measure(number=mn)
        for e in data[mn]:
            m.append(e)

        if mn == 1:
            m.insert(0, clef.TrebleClef())
            m.insert(0, key.KeySignature(0))
            m.insert(0, meter.TimeSignature("2/4"))
            m.insert(0, tempo.MetronomeMark(text="Allegretto, dolce", number=104,
                                             referent=note.Note(type='quarter')))

        if mn in dyn_map:
            m.insert(0, dynamics.Dynamic(dyn_map[mn]))
        if mn in expr_map:
            te = expressions.TextExpression(expr_map[mn])
            te.style.fontStyle = 'italic'
            m.insert(0, te)

        if mn == 16:
            # Final fermata + barline
            last = m.notesAndRests[-1] if m.notesAndRests else None
            if last:
                last.expressions.append(expressions.Fermata())
            m.rightBarline = bar.Barline('final')

        p.append(m)
    return p


# Vn1 expression plan
vn1_dyn = {
    1: 'mp',     # opening, dolce
    7: 'mf',     # climax build
    9: 'mp',     # B section, lighter
    12: 'f',     # peak
    13: 'mp',    # falling away
    16: 'pp',    # gentle ending  (override: actually fading is Vn1's poignant end)
}
vn1_expr = {
    1: 'with wonder, dolce',
    5: '(Violin 1 tacet)',
    7: 'cresc.',
    8: '',
    9: 'leggiero',
    12: 'molto espress.',
    13: 'dim. e poco rit.',
    15: 'rit.',
    16: 'lunga',
}

vn2_dyn = {
    1: 'p',
    5: 'mp',     # vn2 takes melody
    7: 'mf',     # support climax
    12: 'f',
    13: 'mp',
    16: 'pp',
}
vn2_expr = {
    5: 'cantabile (counter-melody)',
    7: '',
    13: 'dim. e poco rit.',
    15: 'rit.',
}


score = stream.Score()
score.insert(0, metadata.Metadata())
score.metadata.title = "A Disney Reverie on Mozart K.330"
score.metadata.subtitle = "after Sonata No.10, Movement I"
score.metadata.composer = "W.A. Mozart"
score.metadata.arranger = "arr. for Violin Duet (Disney style) — V2"

vn1 = build_part("Violin 1", "Vn 1", vn1_data, vn1_dyn, vn1_expr)
vn2 = build_part("Violin 2", "Vn 2", vn2_data, vn2_dyn, vn2_expr)

score.insert(0, vn1)
score.insert(0, vn2)

sg = layout.StaffGroup([vn1, vn2], name='Violin Duet', symbol='bracket')
score.insert(0, sg)

# Output
xml_path = OUT_DIR / "v2.musicxml"
mid_path = OUT_DIR / "v2.mid"
score.write('musicxml', fp=str(xml_path))
score.write('midi', fp=str(mid_path))

print(f"\n=== ARRANGEMENT V2 GENERATED ===")
print(f"  MusicXML: {xml_path}")
print(f"  MIDI:     {mid_path}")
for p in score.parts:
    pitches = []
    for x in p.recurse().notes:
        if isinstance(x, note.Note):
            pitches.append(x.pitch.midi)
        elif isinstance(x, chord.Chord):
            pitches.extend(pp.midi for pp in x.pitches)
    if pitches:
        lo, hi = min(pitches), max(pitches)
        n_count = len(list(p.recurse().notes))
        from music21 import pitch as pmod
        lo_name = pmod.Pitch(midi=lo).nameWithOctave
        hi_name = pmod.Pitch(midi=hi).nameWithOctave
        out_of_range = [m for m in pitches if m < 55 or m > 100]
        print(f"  {p.partName}: {len(p.getElementsByClass('Measure'))} mm, {n_count} events, range {lo_name}-{hi_name}, range_ok={'YES' if not out_of_range else 'NO ' + str(out_of_range)}")

# Count double-stops
ds_count_v1 = ds_count_v2 = 0
for p in score.parts:
    for c in p.recurse().getElementsByClass('Chord'):
        if len(c.pitches) >= 2:
            ds_count_v2 += 1
print(f"  Double-stops (chords): {ds_count_v2}")
