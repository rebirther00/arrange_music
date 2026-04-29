"""Generate a complete SAB+Piano arrangement INSPIRED by Golden (KPOP Demon Hunters).

This is a DERIVATIVE WORK using path C (motif-based new arrangement):
- Same key (G major)
- Same lilting 12/8 feel (verse/chorus)
- New melody, new lyrics, new voice leading
- NOT a transcription — independently composed

Output:
  arrangement/golden_inspired.musicxml
  arrangement/golden_inspired.mid

Run:
  python golden_sing_work/arrangement/generate_inspired.py
"""
from __future__ import annotations
import sys
from pathlib import Path

# Make pipeline.helpers importable
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "pipeline"))

from helpers import N, R, CH, make_part, make_score, export_xml_midi, INSTRUMENTS
from music21 import clef, instrument, layout, stream, expressions, dynamics, tempo, key, meter, metadata, note, bar

# ============================================================================
# Parameters
# ============================================================================
TIME_SIG     = "12/8"
KEY_SHARPS   = 1            # G major
BAR_QL       = 6.0          # 12 eighths * 0.5 ql = 6.0
TOTAL_BARS   = 24
TEMPO_TEXT   = "Lilting Pop"
TEMPO_BPM    = 90           # dotted-quarter = 90
OUT_DIR      = Path(__file__).parent
NAME_STEM    = "golden_inspired"

# ============================================================================
# Soprano (P1) — silent intro, hums in verse, harmony in chorus
# ============================================================================
soprano = {}
# mm.1-4 Intro: silent
for m in range(1, 5):
    soprano[m] = [R(BAR_QL)]
# mm.5-12 Verse: hum on chord 5th, dotted-half + dotted-half per measure
verse_hum = [
    ('D5',), ('A4',),  # m5: G chord (5th=D) ... actually for D/F# chord A is 5th
    ('B4',), ('G4',),  # m6
    ('D5',), ('A4',),  # m7
    ('B4',), ('A4',),  # m8 — actually let's keep simple alternation
]
# Simpler: long held notes, 2 per bar, both dotted-halfs
soprano_verse = [
    [N('D5', 3.0), N('D5', 3.0)],   # m5: G
    [N('A4', 3.0), N('A4', 3.0)],   # m6: D/F#
    [N('B4', 3.0), N('B4', 3.0)],   # m7: Em
    [N('C5', 3.0), N('C5', 3.0)],   # m8: C
    [N('D5', 3.0), N('D5', 3.0)],   # m9: G
    [N('A4', 3.0), N('A4', 3.0)],   # m10: D
    [N('C5', 3.0), N('C5', 3.0)],   # m11: C
    [N('A4', 3.0), N('A4', 3.0)],   # m12: D
]
for i, evs in enumerate(soprano_verse):
    soprano[5 + i] = evs

# mm.13-20 Chorus: full harmony melody (top voice of SAB triad)
# Chord progression: C - D - G - Em - C - D - G - G
# Soprano gets the top note of each chord, dotted-quarter rhythm with stepwise melody
chorus_soprano = [
    # m.13 C: notes E5-E5-E5-D5 (lyric "Ri-sing up to-")
    [N('E5', 1.5), N('E5', 1.5), N('E5', 1.5), N('D5', 1.5)],
    # m.14 D: F#5-F#5-F#5-E5
    [N('F#5', 1.5), N('F#5', 1.5), N('F#5', 1.5), N('E5', 1.5)],
    # m.15 G: D5-D5-D5-G5 (climax)
    [N('D5', 1.5), N('D5', 1.5), N('D5', 1.5), N('G5', 1.5)],
    # m.16 Em: G5-F#5-E5-D5
    [N('G5', 1.5), N('F#5', 1.5), N('E5', 1.5), N('D5', 1.5)],
    # m.17 C: E5-E5-E5-D5
    [N('E5', 1.5), N('E5', 1.5), N('E5', 1.5), N('D5', 1.5)],
    # m.18 D: F#5-F#5-F#5-E5
    [N('F#5', 1.5), N('F#5', 1.5), N('F#5', 1.5), N('E5', 1.5)],
    # m.19 G: held dotted-whole (sustained "gold")
    [N('G5', 6.0)],
    # m.20 G: held continues — dotted-whole
    [N('G5', 6.0)],
]
for i, evs in enumerate(chorus_soprano):
    soprano[13 + i] = evs

# mm.21-24 Outro: sustained final cadence
soprano[21] = [N('E5', 6.0)]   # C chord
soprano[22] = [N('D5', 6.0)]   # G/B
soprano[23] = [N('F#5', 6.0)]  # D7
soprano[24] = [N('G5', 6.0)]   # G — final

# ============================================================================
# Alto (P2) — Solo lead in verse, mid-harmony in chorus
# ============================================================================
alto = {}
for m in range(1, 5):
    alto[m] = [R(BAR_QL)]

# Verse melody (Alto solo with lyrics)
# Each bar = dotted-quarter rest + 3 eighths + dotted-quarter + 3 eighths approach
# Pattern: short pickup phrase per bar
# m5 G: rest then "I was a ghost"
alto[5]  = [R(1.5), N('A3', 0.5), N('B3', 0.5), N('B3', 0.5),
            N('B3', 1.5), N('G3', 0.5), N('A3', 0.5), N('B3', 0.5)]
# m6 D/F#: "I was a-lone, just"
alto[6]  = [N('A3', 1.5), N('A3', 0.5), N('B3', 0.5), N('A3', 0.5),
            N('A3', 1.5), N('A3', 0.5), N('G3', 0.5), N('A3', 0.5)]
# m7 Em: "wait-ing for the morn-ing"
alto[7]  = [N('B3', 1.5), N('B3', 0.5), N('A3', 0.5), N('G3', 0.5),
            N('A3', 1.5), N('G3', 0.5), N('F#3', 0.5), N('E3', 0.5)]
# m8 C: "to come-, then I"
alto[8]  = [N('E3', 3.0), R(1.5), N('G3', 0.5), N('A3', 0.5), N('B3', 0.5)]
# m9 G: "saw a light a-ris-ing"
alto[9]  = [N('D4', 1.5), N('B3', 0.5), N('D4', 0.5), N('B3', 0.5),
            N('D4', 1.5), N('B3', 0.5), N('A3', 0.5), N('B3', 0.5)]
# m10 D: "shin-ing in the dis-tance"
alto[10] = [N('A3', 1.5), N('B3', 0.5), N('A3', 0.5), N('G3', 0.5),
            N('A3', 1.5), N('A3', 0.5), N('B3', 0.5), N('A3', 0.5)]
# m11 C: "call-ing my name in"
alto[11] = [N('G3', 1.5), N('G3', 0.5), N('A3', 0.5), N('G3', 0.5),
            N('G3', 1.5), N('E3', 0.5), N('G3', 0.5), N('A3', 0.5)]
# m12 D: "warm-th and lift-ing me up high"
alto[12] = [N('B3', 1.5), N('A3', 0.5), N('B3', 0.5), N('A3', 0.5),
            N('B3', 1.5), N('A3', 0.5), N('G3', 0.5), N('F#3', 0.5)]

# Chorus (mm.13-20): mid-harmony — chord 3rd of each, simpler rhythm
chorus_alto = [
    # m.13 C: C4-C4-C4-A3
    [N('C4', 1.5), N('C4', 1.5), N('C4', 1.5), N('A3', 1.5)],
    # m.14 D: D4-D4-D4-C4
    [N('D4', 1.5), N('D4', 1.5), N('D4', 1.5), N('C4', 1.5)],
    # m.15 G: B3-B3-B3-D4
    [N('B3', 1.5), N('B3', 1.5), N('B3', 1.5), N('D4', 1.5)],
    # m.16 Em: E4-D4-C4-B3
    [N('E4', 1.5), N('D4', 1.5), N('C4', 1.5), N('B3', 1.5)],
    # m.17 C: C4 chord 3rd held
    [N('C4', 1.5), N('C4', 1.5), N('C4', 1.5), N('A3', 1.5)],
    # m.18 D: D4
    [N('D4', 1.5), N('D4', 1.5), N('D4', 1.5), N('C4', 1.5)],
    # m.19 G: D4 sustained
    [N('D4', 6.0)],
    # m.20 G: D4
    [N('D4', 6.0)],
]
for i, evs in enumerate(chorus_alto):
    alto[13 + i] = evs

# Outro
alto[21] = [N('C4', 6.0)]
alto[22] = [N('B3', 6.0)]
alto[23] = [N('A3', 6.0)]
alto[24] = [N('B3', 6.0)]

# ============================================================================
# Baritone (P3) — silent intro/verse, bass line in chorus, low pedal in outro
# ============================================================================
baritone = {}
for m in range(1, 5):
    baritone[m] = [R(BAR_QL)]
# Verse: silent OR low chord roots whole note. Let's make Baritone enter softly at m11
for m in range(5, 11):
    baritone[m] = [R(BAR_QL)]
# m.11-12: Baritone enters with simple chord roots (foreshadow chorus)
baritone[11] = [N('C3', 6.0)]   # C chord root
baritone[12] = [N('D3', 6.0)]   # D chord root

# Chorus: bass line — chord roots, mostly whole or two halves
chorus_baritone = [
    # m.13 C: dotted-half + dotted-half
    [N('C3', 3.0), N('C3', 3.0)],
    # m.14 D: D3 held, then move to C3
    [N('D3', 3.0), N('C3', 3.0)],
    # m.15 G: G2 (low G)
    [N('G2', 3.0), N('G2', 3.0)],
    # m.16 Em: E3
    [N('E3', 3.0), N('E3', 3.0)],
    # m.17 C: C3
    [N('C3', 3.0), N('C3', 3.0)],
    # m.18 D: D3
    [N('D3', 3.0), N('A2', 3.0)],
    # m.19 G: G2 held
    [N('G2', 6.0)],
    # m.20 G: G2 held continues
    [N('G2', 6.0)],
]
for i, evs in enumerate(chorus_baritone):
    baritone[13 + i] = evs

# Outro
baritone[21] = [N('C3', 6.0)]
baritone[22] = [N('G2', 6.0)]
baritone[23] = [N('D3', 6.0)]
baritone[24] = [N('G2', 6.0)]

# ============================================================================
# Piano RH (treble) — arpeggio ostinato throughout
# ============================================================================
# A 12/8 ostinato pattern with 12 eighths, broken into:
# 3-eighth dotted-quarter beat × 4 = 12 eighths
# Pattern: bottom-mid-top per beat (arpeggiating chord)

def arpeggio_pattern(low, mid, hi):
    """3 eighths per beat, ascending arpeggio. 4 beats per measure."""
    return [
        N(low, 0.5), N(mid, 0.5), N(hi, 0.5),
        N(low, 0.5), N(mid, 0.5), N(hi, 0.5),
        N(low, 0.5), N(mid, 0.5), N(hi, 0.5),
        N(low, 0.5), N(mid, 0.5), N(hi, 0.5),
    ]

piano_rh = {}
# Intro mm.1-4: gentle arpeggio
piano_rh[1] = arpeggio_pattern('G4', 'B4', 'D5')   # G chord
piano_rh[2] = arpeggio_pattern('A4', 'C5', 'D5')   # D/F# (using D-F#-A but with A on top)
piano_rh[3] = arpeggio_pattern('G4', 'B4', 'E5')   # Em
piano_rh[4] = arpeggio_pattern('G4', 'C5', 'E5')   # C

# Verse mm.5-12: similar ostinato (vocal carries melody)
piano_rh[5]  = arpeggio_pattern('G4', 'B4', 'D5')   # G
piano_rh[6]  = arpeggio_pattern('A4', 'C5', 'D5')   # D/F#
piano_rh[7]  = arpeggio_pattern('G4', 'B4', 'E5')   # Em
piano_rh[8]  = arpeggio_pattern('G4', 'C5', 'E5')   # C
piano_rh[9]  = arpeggio_pattern('G4', 'B4', 'D5')   # G
piano_rh[10] = arpeggio_pattern('A4', 'C5', 'D5')   # D
piano_rh[11] = arpeggio_pattern('G4', 'C5', 'E5')   # C
piano_rh[12] = arpeggio_pattern('A4', 'C5', 'D5')   # D

# Chorus mm.13-20: bigger chord blocks (rhythmic strikes)
def chord_strike_pattern(chord_notes):
    """Chord struck on beats 1, 2, 3, 4 with passing eighths."""
    return [
        CH(chord_notes, 1.5), CH(chord_notes, 1.5),
        CH(chord_notes, 1.5), CH(chord_notes, 1.5),
    ]

piano_rh[13] = chord_strike_pattern(['C5', 'E5', 'G5'])    # C
piano_rh[14] = chord_strike_pattern(['D5', 'F#5', 'A5'])   # D
piano_rh[15] = chord_strike_pattern(['G4', 'D5', 'G5'])    # G
piano_rh[16] = chord_strike_pattern(['E5', 'G5', 'B5'])    # Em
piano_rh[17] = chord_strike_pattern(['C5', 'E5', 'G5'])    # C
piano_rh[18] = chord_strike_pattern(['D5', 'F#5', 'A5'])   # D
piano_rh[19] = [CH(['G4', 'D5', 'G5'], 6.0)]               # G held
piano_rh[20] = [CH(['G4', 'D5', 'G5'], 6.0)]               # G held

# Outro mm.21-24: sustained chord
piano_rh[21] = [CH(['C5', 'E5', 'G5'], 6.0)]
piano_rh[22] = [CH(['B4', 'D5', 'G5'], 6.0)]
piano_rh[23] = [CH(['A4', 'D5', 'F#5'], 6.0)]
piano_rh[24] = [CH(['G4', 'D5', 'G5'], 6.0)]

# ============================================================================
# Piano LH (bass) — chord roots and bass line
# ============================================================================
piano_lh = {}
# Intro: held bass roots
piano_lh[1] = [N('G2', 6.0)]
piano_lh[2] = [N('F#2', 6.0)]
piano_lh[3] = [N('E2', 6.0)]
piano_lh[4] = [N('C3', 6.0)]
# Verse
piano_lh[5]  = [N('G2', 6.0)]
piano_lh[6]  = [N('F#2', 6.0)]
piano_lh[7]  = [N('E2', 6.0)]
piano_lh[8]  = [N('C3', 6.0)]
piano_lh[9]  = [N('G2', 6.0)]
piano_lh[10] = [N('D3', 6.0)]
piano_lh[11] = [N('C3', 6.0)]
piano_lh[12] = [N('D3', 6.0)]
# Chorus: octave bass with passing notes
piano_lh[13] = [N('C2', 3.0), N('C3', 3.0)]
piano_lh[14] = [N('D2', 3.0), N('D3', 3.0)]
piano_lh[15] = [N('G2', 3.0), N('G3', 3.0)]
piano_lh[16] = [N('E2', 3.0), N('E3', 3.0)]
piano_lh[17] = [N('C2', 3.0), N('C3', 3.0)]
piano_lh[18] = [N('D2', 3.0), N('A2', 3.0)]
piano_lh[19] = [N('G2', 6.0)]
piano_lh[20] = [N('G2', 6.0)]
# Outro
piano_lh[21] = [N('C2', 6.0)]
piano_lh[22] = [N('G2', 6.0)]
piano_lh[23] = [N('D2', 6.0)]
piano_lh[24] = [N('G2', 6.0)]


# ============================================================================
# Lyrics for Alto (verse only, since chorus uses different syllables per voice)
# ============================================================================
alto_lyrics = {
    5: ["", "", "I", "was", "", "a", "ghost,"],   # rest=skip lyric
    6: ["I", "", "was", "a", "lone,", "just"],
    7: ["wait-", "ing", "for", "the", "morn-", "ing"],
    8: ["light"],
    9: ["I", "saw", "it", "rise", "", "shi-", "ning"],
    10:["bright,", "", "in", "the", "dis-", "tant"],
    11:["call-", "ing", "my", "name", "to", "rise"],
    12:["up,", "lift-", "ing", "high"],
    # Chorus syllables
    13:["Ri-", "sing", "up", "to"],
    14:["meet", "the", "gol-", "den"],
    15:["light", "now", "I'm", "free"],
    16:["sin-", "ging", "out", "loud"],
    17:["ev-", "'ry", "voice", "joined"],
    18:["in", "har-", "mo-", "ny"],
    19:["gold-"],
    20:["en-"],
    # Outro
    21:["light"],
    22:["of"],
    23:["our"],
    24:["dreams"],
}


# ============================================================================
# Build parts
# ============================================================================
def attach_lyrics(part_data, lyrics_map):
    """Attach lyrics to Note events in part_data based on lyrics_map.
    lyrics_map[measure_num] = list of strings (one per Note in measure, "" for skip)."""
    out = {}
    for mn, evs in part_data.items():
        if mn not in lyrics_map:
            out[mn] = evs
            continue
        ly = lyrics_map[mn]
        ly_idx = 0
        new_evs = []
        for ev in evs:
            if isinstance(ev, note.Note):
                if ly_idx < len(ly) and ly[ly_idx]:
                    ev.addLyric(ly[ly_idx])
                ly_idx += 1
            new_evs.append(ev)
        out[mn] = new_evs
    return out


alto_with_lyrics = attach_lyrics(alto, alto_lyrics)


def build_choir_part(name, abbrev, data, clef_obj=None, dyn_map=None):
    p = stream.Part()
    p.id = name
    p.partName = name
    p.partAbbreviation = abbrev
    p.insert(0, instrument.Soprano() if name == "Soprano" else
             instrument.Alto() if name == "Alto" else
             instrument.Baritone())

    sorted_keys = sorted(data.keys())
    dyn_map = dyn_map or {}
    for idx, mn in enumerate(sorted_keys):
        m = stream.Measure(number=mn)
        for e in data[mn]:
            m.append(e)
        if idx == 0:
            m.insert(0, clef_obj or clef.TrebleClef())
            m.insert(0, key.KeySignature(KEY_SHARPS))
            m.insert(0, meter.TimeSignature(TIME_SIG))
        if mn in dyn_map:
            m.insert(0, dynamics.Dynamic(dyn_map[mn]))
        if idx == len(sorted_keys) - 1:
            m.rightBarline = bar.Barline('final')
        p.append(m)
    return p


def build_piano_score():
    """Piano grand staff: combine RH (treble) and LH (bass) with single Piano instrument."""
    # Music21 typically uses two Parts grouped together with a PianoStaff layout
    rh = stream.Part()
    rh.id = "Piano-RH"
    rh.partName = "Piano"
    rh.partAbbreviation = "Pno."
    rh.insert(0, instrument.Piano())
    for idx, mn in enumerate(sorted(piano_rh.keys())):
        m = stream.Measure(number=mn)
        for e in piano_rh[mn]:
            m.append(e)
        if idx == 0:
            m.insert(0, clef.TrebleClef())
            m.insert(0, key.KeySignature(KEY_SHARPS))
            m.insert(0, meter.TimeSignature(TIME_SIG))
            m.insert(0, dynamics.Dynamic('mp'))
        if idx == 12:  # m.13 chorus enters
            m.insert(0, dynamics.Dynamic('f'))
        if idx == 20:  # m.21 outro decrescendo
            m.insert(0, dynamics.Dynamic('p'))
        if idx == len(piano_rh) - 1:
            m.rightBarline = bar.Barline('final')
        rh.append(m)

    lh = stream.Part()
    lh.id = "Piano-LH"
    lh.partName = "Piano"
    lh.partAbbreviation = "Pno."
    lh.insert(0, instrument.Piano())
    for idx, mn in enumerate(sorted(piano_lh.keys())):
        m = stream.Measure(number=mn)
        for e in piano_lh[mn]:
            m.append(e)
        if idx == 0:
            m.insert(0, clef.BassClef())
            m.insert(0, key.KeySignature(KEY_SHARPS))
            m.insert(0, meter.TimeSignature(TIME_SIG))
        if idx == len(piano_lh) - 1:
            m.rightBarline = bar.Barline('final')
        lh.append(m)

    return rh, lh


# Verify all parts have correct duration per measure
def verify_part(data, name):
    for mn, evs in data.items():
        total = sum(float(e.duration.quarterLength) for e in evs)
        if abs(total - BAR_QL) > 0.001:
            print(f"  WARN: {name} m.{mn}: total={total} (expected {BAR_QL})")

print("[VERIFY]")
for nm, d in [('Soprano', soprano), ('Alto', alto_with_lyrics),
              ('Baritone', baritone), ('Piano-RH', piano_rh), ('Piano-LH', piano_lh)]:
    verify_part(d, nm)


# ============================================================================
# Build score
# ============================================================================
sop_part = build_choir_part('Soprano', 'S', soprano,
                             dyn_map={5: 'mp', 13: 'f', 21: 'p'})
alto_part = build_choir_part('Alto', 'A', alto_with_lyrics,
                              dyn_map={5: 'mf', 13: 'f', 21: 'p'})
bar_part = build_choir_part('Baritone', 'B', baritone, clef_obj=clef.BassClef(),
                             dyn_map={11: 'mp', 13: 'f', 21: 'p'})
pno_rh, pno_lh = build_piano_score()

# Add tempo to first measure of soprano
first_meas = sop_part.getElementsByClass('Measure')[0]
mark = tempo.MetronomeMark(text=TEMPO_TEXT, number=TEMPO_BPM,
                           referent=note.Note(quarterLength=1.5))  # dotted-quarter
first_meas.insert(0, mark)

# Compose score
score = stream.Score()
score.insert(0, metadata.Metadata())
score.metadata.title = "Golden (Inspired)"
score.metadata.subtitle = "A derivative arrangement based on the song from KPOP Demon Hunters"
score.metadata.composer = "Original by EJAE, Mark Sonnenblick, IDO, 24, Teddy Park"
score.metadata.arranger = "Independent arrangement (motif-based, not transcription)"

# Add parts in order: Soprano, Alto, Baritone, Piano-RH, Piano-LH
for p in [sop_part, alto_part, bar_part, pno_rh, pno_lh]:
    score.insert(0, p)

# Group SAB choir
choir_group = layout.StaffGroup([sop_part, alto_part, bar_part],
                                 name="SAB Choir", abbreviation="SAB", symbol="bracket")
score.insert(0, choir_group)

# Group Piano (grand staff)
piano_group = layout.StaffGroup([pno_rh, pno_lh],
                                 name="Piano", abbreviation="Pno.", symbol="brace")
score.insert(0, piano_group)


# ============================================================================
# Export
# ============================================================================
xml_path, mid_path = export_xml_midi(score, OUT_DIR, NAME_STEM)
print(f"[OK] Wrote {xml_path}")
print(f"[OK] Wrote {mid_path}")
print(f"\nSummary:")
print(f"  Total measures: {TOTAL_BARS}")
print(f"  Time: {TIME_SIG}, Key: G major, Tempo: dotted-quarter = {TEMPO_BPM}")
print(f"  Sections: Intro (1-4) | Verse (5-12) | Chorus (13-20) | Outro (21-24)")
print(f"  Parts: Soprano, Alto, Baritone, Piano (grand staff)")
