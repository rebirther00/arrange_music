# GOLDEN Manual Transcription Plan

**Goal**: Produce a complete, recording-faithful MusicXML of the SAB+Piano arrangement of *Golden* (KPOP Demon Hunters, arr. Roger Emerson, Hal Leonard 01946654) without using OMR (Audiveris). Iterate vision-driven hand transcription with render-and-compare verification.

## Why this approach

All Audiveris-based pipelines (multi-staff, voice-redistribution v1-v4, per-staff cropping v1-v2) have failed to produce output that matches the recording. See `~/.claude/projects/.../memory/feedback_audiveris_sab_limits.md`. The user has explicitly chosen direct conversion + verification rather than external tools.

## Source

- `golden_sing_work/golden_sing_note_clean.pdf` — watermark-removed clean PDF (16 pages)
- `golden_sing_work/clean_pages/page_NN.png` — page-by-page PNGs (2025x3150)
- `golden_sing_work/render/pdf_pages/pdf_page_NN.png` — alternate PNG render

## Target output

- 4-part fixed score: Soprano, Alto, Baritone, Piano (grand staff)
- Always include all 4 parts, use rests where a part is silent, instead of variable staff layout
- Lyrics, dynamics, articulations, tempo markings, chord symbols all preserved

## Working directory layout

```
manual/
├── plan.md                  (this file)
├── structure.json           (song-level metadata: sections, key/time/tempo changes)
├── scripts/
│   ├── crop_system.py       crop a region of a page PNG for closer inspection
│   ├── render_chunk.py      MuseScore CLI runner: MXL → PNG/MIDI/MP3
│   ├── compare_side.py      stitch source crop + rendered PNG side-by-side
│   └── merge_chunks.py      merge per-chunk MXLs into a single full MXL
├── chunks/
│   ├── mm001-007.musicxml   piano intro
│   ├── mm008.musicxml       transition bar (3/2 → 12/8)
│   ├── mm009-012.musicxml   verse 1 part 1
│   └── ...
├── rendered/
│   └── mmNNN-MMM-1.png      rendered output for visual diff
├── verified/                chunks the user has approved
├── audio/                   per-chunk MP3 for listening checks
├── full.musicxml            merged final
└── full.{pdf,mid,mp3}       final renders
```

## Iteration loop (per chunk)

1. **Inspect**: crop the relevant system from the source PDF page PNG. Read it with vision.
2. **Transcribe**: write a self-contained `chunks/mmXXX-YYY.musicxml`. Always all 4 parts present.
3. **Render**: `python scripts/render_chunk.py chunks/mmXXX-YYY.musicxml` → produces `rendered/mmXXX-YYY-1.png`, `audio/mmXXX-YYY.mp3`, `audio/mmXXX-YYY.mid`.
4. **Visual diff**: read both source crop and rendered PNG, list discrepancies (notes, rhythm, lyrics, marks).
5. **Structural assertions**: programmatic checks — measure count, time-sig consistency, beat sums, voice ranges in expected octaves.
6. **Audio check (optional)**: user listens to MP3 and reports.
7. **Fix**: amend MXL based on findings. Re-render. Re-compare.
8. **Approve**: when matches, copy to `verified/`. Move on.

## Chunking rule

One chunk = one system on the source PDF (≈ 2–4 measures). Chunks always start on a measure boundary. When the layout changes voicing (e.g. piano-only → SAB+piano), end the previous chunk on the boundary so each chunk has a stable staff configuration.

## Order of work

1. mm. 1–3 (page 2 system 1, piano intro, 3/2)
2. mm. 4–6 (page 2 system 2, piano intro, 3/2)
3. mm. 7–8 (page 2 system 3, piano + first SAB stave appearance, 3/2 → 12/8 transition)
4. m. 9 (page 2 system 3 last bar, verse begins, 12/8) — verify against existing `m9_reference.musicxml`
5. mm. 10+ … through to end

## Verification gates

- A chunk does NOT proceed to merge until visual diff matches AND user audio approval.
- Once merged, full-file structural assertion (no orphan voices, single key/time-sig timeline, no negative durations, no out-of-range pitches).

## Stop conditions

- Recording-faithful structural integrity
- Lyrics correct
- Tempo/meter changes preserved with metric modulation
- All 4 parts have correct entries/exits
