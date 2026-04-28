# v4-engraving-fix — Completion Report

**Feature**: v4-engraving-fix
**Status**: ✅ Completed
**Match Rate**: 100% (10/10 AC)
**Iteration Count**: 0 (no rework cycles needed)
**Duration**: 2026-04-28 ~ 2026-04-29 (≈ 1 working day)

---

## Executive Summary

| 관점 | 내용 |
|---|---|
| **Problem** | v3 MusicXML(`mm001-003.musicxml`)은 음표·리듬·화성·슬러는 정확하나 페이지 폭 과대(2400 tenths), `mp` 다이내믹 위치 부정확(베이스 클레프 아래), 템포 텍스트(`(♩ = ca. 90)`)와 곡 메타데이터(제목·작가·편곡자) 누락 — 인쇄물 품질에서 원본 Hal Leonard 악보와 시각적 차이가 큼 |
| **Solution** | XML 헤더 5개 영역만 손봄 (음표 0건 변경): ① `<work>`/`<identification>` 추가, ② `<defaults>` 페이지 1700×1500 + 폰트 지정, ③ `<credit>` 통합 multi-line(`xml:space="preserve"`), ④ `<metronome parentheses="yes">`+`ca. 90`, ⑤ `mp` direction `placement="above"` |
| **Function/UX Effect** | 1 시스템 3 마디 컴팩트 배치 / "**Moderately** (♩ = ca. 90)" 정확 표기 / `mp`가 그랜드 스태프 중간 / "**Golden**" 제목 + 부제 + writers 2줄 + arranger + 하단 copyright 모두 표시 → 시각적으로 Hal Leonard 인쇄 악보 수준 도달 |
| **Core Value** | "Recording-faithful" 단계에서 "**Print-faithful**" 단계로 진입. v4의 헤더 블록이 **모든 후속 chunk의 표준 템플릿**으로 확정되어, mm.4–6 등 후속 작업이 동일 조판 품질로 자동 산출 가능 — 작업 효율↑ + 일관성↑ |

### Value Delivered (4-perspective with metrics)

| 관점 | Before (v3) | After (v4) | 개선 정도 |
|---|---|---|---|
| **Problem 해소** | 5개 조판 이슈 | 0개 | -100% |
| **Solution 적용** | 0개 G 항목 | 4개 G 항목 적용 (G5 deferred) | +400% |
| **Function UX** | 페이지 폭 2400, mp 베이스 아래, 메타 0개 | 페이지 폭 1700, mp 스태프 중간, 메타 5종 | 페이지 -29%, 메타 +5종 |
| **Core Value** | chunk별 일회성 작업 | 표준 헤더 → 모든 chunk 자동 적용 | 후속 chunk 작업 시간 ≈30% 단축 예상 |

---

## 1. Project Overview

| 항목 | 값 |
|---|---|
| Feature | v4-engraving-fix |
| Started | 2026-04-28 |
| Completed | 2026-04-29 |
| Duration | ≈1 working day |
| Iterations | 0 (Match Rate 100% on first analysis) |
| Match Rate | 100% (10/10 AC) |

### Goals (Plan에서 정의)

| Goal | 상태 | 비고 |
|---|---|---|
| G1: 페이지 폭 압축 (2400→1500–1700) | ✅ 1700 tenths 적용 | scaling 5→7mm 동시 조정 |
| G2: `mp` placement 보정 | ✅ below→above | 베이스 클레프 위로 이동 |
| G3: 템포 `(♩ = ca. 90)` 표기 | ✅ Plan A 성공 | `parentheses="yes"` MuseScore 4 호환 |
| G4: 곡 메타데이터 추가 | ✅ 5종 표시 | 제목·부제·writers·arranger·copyright |
| G5: 베이스 stem 명시 | ⏸️ Deferred | 점겹온음표라 시각 효과 없음 → 후속 chunk에서 |

---

## 2. Implementation Summary

### 2.1 Files Changed

| 파일 | 변경 종류 | 라인 변경 |
|---|---|---|
| `golden_sing_work/manual/chunks/mm001-003.musicxml` | 수정 | +30 / -7 |
| `golden_sing_work/manual/chunks/mm001-003.v3.bak.musicxml` | 신규 (v3 백업) | +133 (전체 복사) |
| `golden_sing_work/manual/rendered/mm001-003-1.png` | 재생성 | — |
| `golden_sing_work/manual/audio/mm001-003.mid` | 재생성 | 변경 없음 (566 bytes) |

### 2.2 PDCA 문서

| 단계 | 파일 |
|---|---|
| Plan | [docs/01-plan/features/v4-engraving-fix.plan.md](../01-plan/features/v4-engraving-fix.plan.md) |
| Design | [docs/02-design/features/v4-engraving-fix.design.md](../02-design/features/v4-engraving-fix.design.md) |
| Analysis | [docs/03-analysis/v4-engraving-fix.analysis.md](../03-analysis/v4-engraving-fix.analysis.md) |
| Report | (this file) |

### 2.3 검증 산출물

- 렌더 PNG: [golden_sing_work/manual/rendered/mm001-003-1.png](../../golden_sing_work/manual/rendered/mm001-003-1.png)
- Side-by-side 비교: [cmp__page02_sys1_FULL_HD__mm001-003-1.png](../../golden_sing_work/manual/rendered/compare/cmp__page02_sys1_FULL_HD__mm001-003-1.png)
- MIDI/MP3 (v3 음악 내용 보존): [audio/mm001-003.mid](../../golden_sing_work/manual/audio/mm001-003.mid), [.mp3](../../golden_sing_work/manual/audio/mm001-003.mp3)

---

## 3. Key Learnings

### 3.1 MuseScore 4 Credit 동작 (중요 발견)

**현상**: `<credit>` 블록을 여러 개 만들고 각각 다른 `default-y`를 줘도 MuseScore 4가 **`default-y`를 무시하고 자동 stack** → 모두 같은 라인에 텍스트 겹침.

**해결책**: 단일 `<credit>` 안에 multi-line 텍스트를 `xml:space="preserve"`로 보존:
```xml
<credit page="1">
  <credit-type>composer</credit-type>
  <credit-words ... xml:space="preserve">Words and Music by EJAE, Mark Sonnenblick,
IDO, 24, and TEDDY PARK
Arranged by ROGER EMERSON</credit-words>
</credit>
```

→ **후속 chunk 모든 헤더에 동일 패턴 적용 필요**.

### 3.2 MusicXML `<metronome parentheses="yes">` 호환성

MusicXML 3.0+ 표준이지만 일부 렌더러가 무시할 수 있다는 우려 → **MuseScore 4에서 정상 작동 확인**. Fallback (Plan B) 불필요.

### 3.3 Per-minute 자유 텍스트

`<per-minute>`은 숫자 외에도 `ca. 90`, `60-72` 같은 자유 텍스트 허용 → 원본 Hal Leonard의 "ca." 표기 정확 재현 가능.

### 3.4 Iteration 효율성

Plan + Design을 사전에 정확히 작성한 결과 → **Do phase에서 단 3번의 렌더로 완료** (1차: 음표 OK, 2차: credit 겹침 발견, 3차: 통합 multi-line으로 해결). Iteration 0건으로 100% 도달 — Plan/Design 투자가 후행 작업 단축.

---

## 4. Issues Encountered & Resolutions

| # | 이슈 | 단계 | 해결 |
|---|---|---|---|
| 1 | 첫 렌더에서 composer credit이 줄바꿈(\n)을 인식하지 못해 다음 credit과 겹침 | Do (렌더 1차) | 줄바꿈 제거 + credit 분리 시도 |
| 2 | 분리된 3개 credit이 여전히 같은 라인에 stack | Do (렌더 2차) | `xml:space="preserve"` + 단일 credit 내 multi-line 텍스트 |
| 3 | 비교 PNG에서 v4 영역이 너무 작게 표시 | Check | `compare_side.py`에 explicit y-fraction(0.16-0.36) 사용 |

---

## 5. Standardization (다음 chunk를 위한 표준)

본 v4의 다음 헤더 블록을 **모든 후속 chunk가 복사**해야 함:

```xml
<score-partwise version="4.0">
  <work>
    <work-title>Golden</work-title>
  </work>
  <identification>
    <creator type="composer">EJAE, Mark Sonnenblick, IDO, 24, Teddy Park</creator>
    <creator type="lyricist">EJAE, Mark Sonnenblick</creator>
    <creator type="arranger">Arranged by Roger Emerson</creator>
    <rights>(c) 2025 Maisie Anthems, THEBLACKLABEL Inc., YG Entertainment</rights>
  </identification>
  <defaults>
    <scaling><millimeters>7</millimeters><tenths>40</tenths></scaling>
    <page-layout>
      <page-height>1500</page-height>
      <page-width>1700</page-width>
      <page-margins type="both">
        <left-margin>100</left-margin><right-margin>100</right-margin>
        <top-margin>180</top-margin><bottom-margin>120</bottom-margin>
      </page-margins>
    </page-layout>
    <word-font font-family="Times New Roman" font-size="10"/>
    <lyric-font font-family="Times New Roman" font-size="10"/>
  </defaults>
  <credit page="1">
    <credit-type>title</credit-type>
    <credit-words default-x="850" default-y="1420" justify="center" valign="top" font-size="22" font-weight="bold">Golden</credit-words>
  </credit>
  <credit page="1">
    <credit-type>subtitle</credit-type>
    <credit-words default-x="850" default-y="1380" justify="center" valign="top" font-size="12" font-style="italic">from the Netflix film KPOP Demon Hunters</credit-words>
  </credit>
  <credit page="1">
    <credit-type>composer</credit-type>
    <credit-words default-x="1600" default-y="1350" justify="right" valign="top" font-size="9" xml:space="preserve">Words and Music by EJAE, Mark Sonnenblick,
IDO, 24, and TEDDY PARK
Arranged by ROGER EMERSON</credit-words>
  </credit>
  ...
```

추가 표준:
- 첫 마디 템포 표기: `<metronome parentheses="yes">` + `<per-minute>ca. {bpm}</per-minute>`
- 다이내믹: `<direction placement="above">` (베이스 staff에 붙일 때)

---

## 6. Next Steps

### 6.1 즉시 진행 가능
- **mm.4–6 chunk 작업**: v4 헤더 블록 복사 → 음표만 입력 → render → diff (PDCA 불필요)
- 본 chunk를 `verified/` 디렉토리로 이동 검토 (plan.md의 verification gate)

### 6.2 향후 PDCA 트리거 시점 (구조 변화 시)
- mm.7–8: SAB 보컬 첫 등장 → `/pdca plan sab-staves`
- mm.8: 3/2 → 12/8 metric modulation → `/pdca plan time-signature-change`
- 가사 입력 표준 → `/pdca plan lyrics-encoding`

### 6.3 권장 commands
```
# 현 사이클 정리 (선택사항)
/pdca archive v4-engraving-fix --summary

# 다음 chunk 시작 (PDCA 없이)
cp golden_sing_work/manual/chunks/mm001-003.musicxml \
   golden_sing_work/manual/chunks/mm004-006.musicxml
# → 음표 영역만 m1-3 → m4-6로 교체 → render → diff
```

---

## 7. Sign-off

- ✅ All AC met (10/10)
- ✅ Match Rate 100%
- ✅ Music content unchanged (MIDI 동일성 검증)
- ✅ Standardization template 확립
- ✅ Documentation complete (Plan/Design/Analysis/Report)

**Status**: Ready for archive or continued chunk work.
