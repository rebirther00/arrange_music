# v4-engraving-fix — Design

**Feature**: v4-engraving-fix
**Plan**: [v4-engraving-fix.plan.md](../../01-plan/features/v4-engraving-fix.plan.md)
**Target**: `golden_sing_work/manual/chunks/mm001-003.musicxml`
**Phase**: Design
**Created**: 2026-04-29

---

## 1. XML Diff 명세 (G1–G5)

### G1. 페이지 폭 압축

**현재** (line 4–13):
```xml
<defaults>
  <scaling><millimeters>5</millimeters><tenths>40</tenths></scaling>
  <page-layout>
    <page-height>1200</page-height>
    <page-width>2400</page-width>
    <page-margins type="both">
      <left-margin>80</left-margin><right-margin>80</right-margin>
      <top-margin>120</top-margin><bottom-margin>120</bottom-margin>
    </page-margins>
  </page-layout>
</defaults>
```

**변경 후**:
```xml
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
```

**근거**:
- `page-width 2400 → 1700` (≈70% 축소): 시스템이 가로로 조밀해져 음표 간격이 인쇄물 수준으로 압축됨
- `millimeters 5 → 7`: tenths 단위 대비 실제 인쇄 mm가 커지므로 음표 자체는 크지만 페이지가 작아져 동일 페이지에 음표가 빽빽하게 들어감
- `top-margin 120 → 180`: 새로 추가될 `<work-title>`과 `<credit>` 공간 확보
- `word-font`, `lyric-font` 추가: 원본 Hal Leonard와 유사한 Times 계열 적용

---

### G2. `mp` 다이내믹 위치 보정

**현재** (line 62–65):
```xml
<direction placement="below">
  <direction-type><dynamics><mp/></dynamics></direction-type>
  <staff>2</staff>
</direction>
```

**변경 후**:
```xml
<direction placement="above">
  <direction-type><dynamics><mp/></dynamics></direction-type>
  <staff>2</staff>
</direction>
```

**근거**:
- `placement="below"` + `staff=2` → bass clef 아래에 표시 (잘못)
- `placement="above"` + `staff=2` → bass clef 위에 표시 = 그랜드 스태프 중간 (정확)
- 원본은 `mp`가 첫 음표 직전, 두 스태프 사이의 간격에 위치함

---

### G3. 템포 텍스트 `(♩ = ca. 90)`

**현재** (line 35–39):
```xml
<direction placement="above">
  <direction-type><words font-weight="bold">Moderately</words></direction-type>
  <direction-type><metronome><beat-unit>half</beat-unit><per-minute>90</per-minute></metronome></direction-type>
  <sound tempo="180"/>
</direction>
```

**변경 후** (Plan A — `parentheses="yes"` 시도):
```xml
<direction placement="above">
  <direction-type><words font-weight="bold">Moderately </words></direction-type>
  <direction-type><metronome parentheses="yes"><beat-unit>half</beat-unit><per-minute>ca. 90</per-minute></metronome></direction-type>
  <sound tempo="180"/>
</direction>
```

**Fallback (Plan B — Plan A가 ca. 90 텍스트를 깰 경우)**:
```xml
<direction placement="above">
  <direction-type><words font-weight="bold">Moderately </words></direction-type>
  <direction-type><words>(</words></direction-type>
  <direction-type><metronome><beat-unit>half</beat-unit><per-minute>ca. 90</per-minute></metronome></direction-type>
  <direction-type><words>)</words></direction-type>
  <sound tempo="180"/>
</direction>
```

**근거**:
- `<per-minute>`은 텍스트 자유 입력 가능 — `ca. 90`을 직접 넣으면 "♩ = ca. 90" 으로 렌더됨
- `parentheses="yes"`는 MusicXML 3.0+ 표준 — MuseScore 4가 지원하지만 일부 버전에서 무시될 수 있어 fallback 준비
- `<sound tempo="180">`는 그대로 유지 (재생용 메타데이터, 시각에는 영향 없음)

---

### G4. 곡 메타데이터 (제목·작가·편곡자)

**현재**: `<score-partwise>` 직후에 `<defaults>`만 있음

**변경 후** — `<defaults>` 직전에 다음 추가:
```xml
<work>
  <work-title>Golden</work-title>
</work>
<identification>
  <creator type="composer">EJAE, Mark Sonnenblick, IDO, 24, Teddy Park</creator>
  <creator type="lyricist">EJAE, Mark Sonnenblick</creator>
  <creator type="arranger">Arranged by Roger Emerson</creator>
  <rights>© 2025 Maisie Anthems, THEBLACKLABEL Inc., YG Entertainment</rights>
</identification>
```

추가로 `<defaults>` 다음 `<part-list>` 직전에 `<credit>` 블록을 둠:
```xml
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
  <credit-words default-x="1600" default-y="1340" justify="right" valign="top" font-size="10">Words and Music by EJAE, Mark Sonnenblick,
IDO, 24, and Teddy Park</credit-words>
</credit>
<credit page="1">
  <credit-type>arranger</credit-type>
  <credit-words default-x="1600" default-y="1300" justify="right" valign="top" font-size="10">Arranged by ROGER EMERSON</credit-words>
</credit>
```

**근거**:
- `<work-title>` 은 score 메타데이터 (검색·OS-level)
- `<credit>` 은 페이지 인쇄용 텍스트 (시각적으로 노출)
- `default-x/y` 좌표는 새 `page-width 1700`, `page-height 1500` 기준 (왼쪽 위 시작)
- `writers`/`arranger`는 `structure.json`에서 그대로 사용

---

### G5. 베이스 보이싱 stem 방향 명시 (선택적)

현재 v3는 voice 2(상위 dyad)와 voice 3(하위 single)이 모두 staff 2에 있고 stem 지정 없음 → MuseScore가 자동 결정. 시각 분리가 약할 수 있음.

**선택적 변경** — voice 2 모든 음표에 `<stem>up</stem>`, voice 3 모든 음표에 `<stem>down</stem>` 추가.

**예시 (m1 voice 2)**:
```xml
<note><pitch><step>C</step><octave>3</octave></pitch><duration>12</duration><voice>2</voice><type>whole</type><dot/><stem>up</stem><staff>2</staff></note>
```

**근거**: 점겹온음표는 stem이 없어 시각 효과가 미미하지만, 후속 chunk(반음표·4분음표 등이 voice 2/3에 들어가는 경우)에서 일관된 보이싱 표현을 위해 표준화.

**적용 여부**: m1–m3 모두 점겹온음표 → stem 시각 효과 없음. **이번 사이클에서는 G5 미적용** 결정. 후속 chunk(짧은 음표 포함) 작업 시 별도로 적용.

---

## 2. 구현 순서 (Do phase)

| 순서 | 작업 | 검증 |
|---|---|---|
| 1 | 기존 `mm001-003.musicxml` 백업 → `mm001-003.v3.bak.musicxml` | 파일 존재 확인 |
| 2 | G4: `<work>` + `<identification>` + `<credit>` 4개 삽입 | XML well-formed |
| 3 | G1: `<defaults>` 의 scaling·page-layout 수정 | 동상 |
| 4 | G2: m1의 `mp` direction `placement="below" → "above"` | 동상 |
| 5 | G3: m1의 metronome에 `parentheses="yes"` + `<per-minute>ca. 90</per-minute>` | 동상 |
| 6 | `python golden_sing_work/manual/scripts/render_chunk.py golden_sing_work/manual/chunks/mm001-003.musicxml --no-mp3` | PNG 생성 확인 |
| 7 | `python golden_sing_work/manual/scripts/stitch_systems.py mm001-003-1.png` | hstitch.png 생성 |
| 8 | `python golden_sing_work/manual/scripts/compare_side.py page02_sys1_FULL_HD.png mm001-003-1__hstitch.png` | compare PNG 생성 |
| 9 | 비교 PNG 시각 확인 — Plan A 실패 시 G3를 Plan B로 재시도 | 5개 항목 검증 |

---

## 3. Acceptance Criteria 매핑

| Plan AC | Design 검증 방법 |
|---|---|
| AC1 (page-width) | XML에서 `<page-width>1700` 확인 + 렌더 PNG width 측정 |
| AC2 (mp 위치) | XML에서 `placement="above"` 확인 + 렌더 PNG에서 mp가 베이스 클레프 위 |
| AC3 (템포 텍스트) | XML에서 `parentheses="yes"` + `ca. 90` 확인 + 렌더 PNG에서 괄호+ca. 표시 |
| AC4 (메타) | XML에서 `<work-title>`, 4개 `<credit>` 확인 + 렌더 PNG에 제목·편곡자 표시 |
| AC5 (시각 비교) | compare PNG 사용자 확인 |
| AC6 (MIDI/MP3 동일) | `audio/mm001-003.mid` 파일 크기·체크섬 v3와 동일 |

---

## 4. Risk Mitigation

- **Risk**: Plan A의 `parentheses="yes"`가 MuseScore 4에서 무시될 수 있음 → Plan B로 즉시 전환 (텍스트 합성)
- **Risk**: `<credit>` 좌표가 페이지 영역 밖이 될 수 있음 → 첫 렌더에서 잘렸으면 좌표 재조정
- **Risk**: `page-height 1500`으로 줄이면 첫 시스템이 페이지 하단에 잘릴 수 있음 → 잘리면 1500 → 1700으로 재조정

---

## 5. Next Step

Design 승인 후 `/pdca do v4-engraving-fix` → 위 9단계 순서대로 실행.
