"""Reusable music helpers for arrangement scripts.
Imported by versions/*.py written by Claude.
"""
from music21 import (stream, note, chord, meter, key, clef, instrument,
                     tempo, metadata, dynamics, expressions, articulations,
                     spanner, bar, layout)


def N(name, ql):
    """Build a Note. Example: N('G5', 0.5)"""
    return note.Note(name, quarterLength=ql)


def R(ql):
    """Build a Rest. Example: R(0.5)"""
    return note.Rest(quarterLength=ql)


def CH(names, ql):
    """Build a Chord (multi-note). Example: CH(['C5','E5','G5'], 1.0)"""
    return chord.Chord(names, quarterLength=ql)


def make_measure(num, events):
    m = stream.Measure(number=num)
    for e in events:
        m.append(e)
    return m


def verify_durations(data, name, expected_per_bar):
    """Raise ValueError if any measure's total duration != expected_per_bar."""
    for mn, evs in data.items():
        total = sum(float(e.duration.quarterLength) for e in evs)
        if abs(total - expected_per_bar) > 0.001:
            raise ValueError(
                f"{name} measure {mn}: duration={total} != {expected_per_bar} "
                f"(events: {[(type(e).__name__, e.duration.quarterLength) for e in evs]})")


# Standard violin range (open G string to safe high E)
VIOLIN_RANGE = (55, 100)        # G3 to E7 (extreme upper, comfortable to A6=93)
VIOLA_RANGE = (48, 93)          # C3 to A6
CELLO_RANGE = (36, 84)          # C2 to C6
DOUBLE_BASS_RANGE = (28, 64)    # E1 to E4 (sounding)
FLUTE_RANGE = (60, 96)          # C4 to C7
CLARINET_RANGE = (50, 91)       # D3 to G6 (sounding Bb instrument)
PIANO_RANGE = (21, 108)         # A0 to C8


def check_range(part, midi_range, label=""):
    """Return list of (measure_number, midi_value) for out-of-range notes."""
    lo, hi = midi_range
    out = []
    for m in part.getElementsByClass('Measure'):
        for x in m.recurse().notes:
            if isinstance(x, note.Note):
                if not (lo <= x.pitch.midi <= hi):
                    out.append((m.number, x.pitch.midi, x.pitch.nameWithOctave))
            elif isinstance(x, chord.Chord):
                for p in x.pitches:
                    if not (lo <= p.midi <= hi):
                        out.append((m.number, p.midi, p.nameWithOctave))
    return out


# Common instrument factory by name (extensible)
INSTRUMENTS = {
    'violin':       (instrument.Violin,     VIOLIN_RANGE),
    'viola':        (instrument.Viola,      VIOLA_RANGE),
    'cello':        (instrument.Violoncello, CELLO_RANGE),
    'bass':         (instrument.Contrabass, DOUBLE_BASS_RANGE),
    'doublebass':   (instrument.Contrabass, DOUBLE_BASS_RANGE),
    'flute':        (instrument.Flute,      FLUTE_RANGE),
    'clarinet':     (instrument.Clarinet,   CLARINET_RANGE),
    'piano':        (instrument.Piano,      PIANO_RANGE),
    'drums':        (instrument.UnpitchedPercussion, (35, 81)),  # GM drum kit MIDI range
    'percussion':   (instrument.UnpitchedPercussion, (35, 81)),
}


def make_part(name, abbrev, instr_key, data, key_sharps=0, time_sig="4/4",
              tempo_text=None, tempo_bpm=None, tempo_referent_ql=1.0,
              dyn_map=None, expr_map=None,
              measures_per_bar_ql=4.0,
              clef_obj=None, fermata_on_last=True):
    """Build a complete music21 Part from a {measure_num: [events]} dict.

    Parameters
    ----------
    name           : str       part display name
    abbrev         : str       short abbreviation
    instr_key      : str       key into INSTRUMENTS, or instrument.Instrument subclass
    data           : dict      {measure_num: list_of_events}
    key_sharps     : int       -7..+7  (0=C, 1=G, -1=F, etc.)
    time_sig       : str       "4/4", "2/4", "3/4", "6/8", ...
    tempo_text     : str       "Allegretto" (None to skip)
    tempo_bpm      : int       104 (None to skip)
    dyn_map        : dict      {measure_num: 'mp'/'f'/...}
    expr_map       : dict      {measure_num: 'cresc.'/'rit.'/...}
    measures_per_bar_ql : float   total quarterLength per bar (verify)
    clef_obj       : music21 clef instance (default by instrument)
    fermata_on_last: bool      add fermata to final note
    """
    dyn_map = dyn_map or {}
    expr_map = expr_map or {}

    if isinstance(instr_key, str):
        instr_cls, _range = INSTRUMENTS[instr_key.lower()]
        instr = instr_cls()
    else:
        instr = instr_key()

    p = stream.Part()
    p.id = name
    p.partName = name
    p.partAbbreviation = abbrev
    p.insert(0, instr)

    sorted_keys = sorted(data.keys())
    for idx, mn in enumerate(sorted_keys):
        m = make_measure(mn, data[mn])

        if idx == 0:
            if clef_obj is not None:
                m.insert(0, clef_obj)
            else:
                m.insert(0, clef.TrebleClef() if instr_key in ('violin', 'flute', 'clarinet') else clef.BassClef())
            m.insert(0, key.KeySignature(key_sharps))
            m.insert(0, meter.TimeSignature(time_sig))
            if tempo_text or tempo_bpm:
                ref_note = note.Note(quarterLength=tempo_referent_ql)
                mark = tempo.MetronomeMark(
                    text=tempo_text,
                    number=tempo_bpm,
                    referent=ref_note)
                m.insert(0, mark)

        if mn in dyn_map:
            m.insert(0, dynamics.Dynamic(dyn_map[mn]))
        if mn in expr_map and expr_map[mn]:
            te = expressions.TextExpression(expr_map[mn])
            te.style.fontStyle = 'italic'
            m.insert(0, te)

        if idx == len(sorted_keys) - 1:
            if fermata_on_last and m.notesAndRests:
                last = m.notesAndRests[-1]
                last.expressions.append(expressions.Fermata())
            m.rightBarline = bar.Barline('final')

        p.append(m)

    # Verify
    verify_durations(data, name, measures_per_bar_ql)
    return p


def make_score(title, subtitle, composer, arranger, parts, group_label="Ensemble", group_symbol='bracket'):
    """Combine multiple parts into a Score with metadata + staff group."""
    score = stream.Score()
    score.insert(0, metadata.Metadata())
    score.metadata.title = title
    score.metadata.subtitle = subtitle
    score.metadata.composer = composer
    score.metadata.arranger = arranger

    for p in parts:
        score.insert(0, p)

    if len(parts) > 1:
        sg = layout.StaffGroup(parts, name=group_label, symbol=group_symbol)
        score.insert(0, sg)

    return score


def export_xml_midi(score, out_dir, name_stem):
    """Write MusicXML and MIDI files. Returns (xml_path, mid_path)."""
    from pathlib import Path
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    xml_path = out_dir / f"{name_stem}.musicxml"
    mid_path = out_dir / f"{name_stem}.mid"
    score.write('musicxml', fp=str(xml_path))
    score.write('midi', fp=str(mid_path))
    return xml_path, mid_path


def summarize_score(score, ranges_to_check=None):
    """Print and return a structured summary of the score."""
    info = []
    for p in score.parts:
        m_count = len(p.getElementsByClass('Measure'))
        notes = list(p.recurse().notes)
        pitches = []
        for x in notes:
            if isinstance(x, note.Note):
                pitches.append(x.pitch.midi)
            elif isinstance(x, chord.Chord):
                pitches.extend(pp.midi for pp in x.pitches)
        from music21 import pitch as pmod
        if pitches:
            lo_n = pmod.Pitch(midi=min(pitches)).nameWithOctave
            hi_n = pmod.Pitch(midi=max(pitches)).nameWithOctave
        else:
            lo_n = hi_n = "(empty)"
        chords = sum(1 for x in notes if isinstance(x, chord.Chord) and len(x.pitches) >= 2)
        info.append({
            "part": p.partName,
            "measures": m_count,
            "events": len(notes),
            "double_stops": chords,
            "range": (lo_n, hi_n),
            "midi_lo": min(pitches) if pitches else None,
            "midi_hi": max(pitches) if pitches else None,
        })
    return info
