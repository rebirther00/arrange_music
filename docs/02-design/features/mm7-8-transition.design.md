# mm7-8-transition — Design

**Feature**: mm7-8-transition
**Plan**: [mm7-8-transition.plan.md](../../01-plan/features/mm7-8-transition.plan.md)
**Target**: `golden_sing_work/manual/chunks/mm007-008.musicxml`
**Phase**: Design
**Created**: 2026-04-29

---

## 1. Open Questions Resolution

| Q | 결정 사항 | 근거 |
|---|---|---|
| Q1: m.7 piano 코드 | **D/A** (m.3과 동일 패턴) | source crop 확인 — 트레블 ostinato 패턴 + bass dyad+single 보임 |
| Q2: m.8 piano 내용 | **N.C. (No Chord), whole rest** + `f` 다이내믹 | source crop 확인 — 12/8 시그 직후 whole rest, "f" 마크 |
| Q3: "Upbeat Pop" 위치 | **m.8 위 (모든 staff 가시 위치)** | source에서 Soprano 위·Piano 위 두 곳에 중복 표기 |
| Q4: metric modulation | **`(♪ = ♪)`** (eighth = eighth equivalence) | source crop 시각 확인. structure.json의 dotted-quarter=quarter는 오기 |
| Q5: Solo staff label | **"Solo"** (보컬 라벨), m.9 entry 시점에 "*Alto or Tenor Solo*" 캐릭터 텍스트 추가 | source crop + m9_reference 비교 |

---

## 2. XML 명세

### 2.1 Divisions 통합

3/2와 12/8 모두 표현 가능한 공통 분모: **`divisions=12`** (per quarter note)

| 음가 | divisions |
|---|---|
| eighth | 6 |
| dotted-quarter | 18 |
| half | 24 |
| dotted-whole | 72 |
| Total per 3/2 measure | 72 (3 × 24) |
| Total per 12/8 measure | 72 (12 × 6) |

### 2.2 Part List (3 parts)

```xml
<part-list>
  <score-part id="P1">
    <part-name>Soprano</part-name>
    <part-abbreviation>S</part-abbreviation>
    <score-instrument id="P1-I1"><instrument-name>Voice</instrument-name></score-instrument>
  </score-part>
  <score-part id="P2">
    <part-name>Solo</part-name>
    <part-abbreviation>Solo</part-abbreviation>
    <score-instrument id="P2-I1"><instrument-name>Voice</instrument-name></score-instrument>
  </score-part>
  <score-part id="P3">
    <part-name>Piano</part-name>
    <part-abbreviation>Pno.</part-abbreviation>
    <score-instrument id="P3-I1"><instrument-name>Piano</instrument-name></score-instrument>
  </score-part>
</part-list>
```

### 2.3 P1 Soprano (m.7-8: all rests)

**m.7 (3/2)**:
```xml
<measure number="7">
  <attributes>
    <divisions>12</divisions>
    <key><fifths>1</fifths></key>
    <time><beats>3</beats><beat-type>2</beat-type></time>
    <clef><sign>G</sign><line>2</line></clef>
  </attributes>
  <note><rest measure="yes"/><duration>72</duration><voice>1</voice></note>
</measure>
```

**m.8 (12/8 전환, all rest)**:
```xml
<measure number="8">
  <print new-system="no"/>
  <attributes>
    <time><beats>12</beats><beat-type>8</beat-type></time>
  </attributes>
  <direction placement="above">
    <direction-type><words font-style="italic" font-size="9">(♪ = ♪)</words></direction-type>
  </direction>
  <direction placement="above">
    <direction-type><words font-weight="bold">Upbeat Pop </words></direction-type>
    <direction-type><metronome parentheses="yes"><beat-unit>quarter</beat-unit><beat-unit-dot/><per-minute>ca. 120</per-minute></metronome></direction-type>
    <sound tempo="180"/>
  </direction>
  <note><rest measure="yes"/><duration>72</duration><voice>1</voice></note>
</measure>
```

### 2.4 P2 Solo (m.7-8: all rests, 같은 구조)

P1과 동일 — Soprano 자리에 Solo 적용.

### 2.5 P3 Piano (m.7: D/A pattern, m.8: rest + f)

**m.7 (3/2, D/A)** — 음표는 m.3 v3에서 복사 (divisions만 2→12로 스케일):
```xml
<measure number="7">
  <attributes>
    <divisions>12</divisions>
    <key><fifths>1</fifths></key>
    <time><beats>3</beats><beat-type>2</beat-type></time>
    <staves>2</staves>
    <clef number="1"><sign>G</sign><line>2</line></clef>
    <clef number="2"><sign>F</sign><line>4</line></clef>
  </attributes>
  <harmony print-frame="no">
    <root><root-step>D</root-step></root>
    <kind text="">major</kind>
    <bass><bass-step>A</bass-step></bass>
  </harmony>
  <!-- voice 1 treble (12 eighths, duration 6 each) - same pattern as m.3 -->
  <note><pitch><step>A</step><octave>4</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>up</stem><staff>1</staff><beam number="1">begin</beam></note>
  <note><pitch><step>A</step><octave>4</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>up</stem><staff>1</staff><beam number="1">end</beam></note>
  <note><pitch><step>D</step><octave>5</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>down</stem><staff>1</staff><beam number="1">begin</beam></note>
  <note><pitch><step>E</step><octave>5</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>down</stem><staff>1</staff><beam number="1">continue</beam></note>
  <note><pitch><step>D</step><octave>5</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>down</stem><staff>1</staff><beam number="1">continue</beam></note>
  <note><pitch><step>A</step><octave>4</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>down</stem><staff>1</staff><beam number="1">end</beam><notations><slur type="start" number="1"/></notations></note>
  <note><pitch><step>A</step><octave>4</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>up</stem><staff>1</staff><beam number="1">begin</beam><notations><slur type="stop" number="1"/></notations></note>
  <note><pitch><step>A</step><octave>4</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>up</stem><staff>1</staff><beam number="1">end</beam></note>
  <note><pitch><step>D</step><octave>5</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>down</stem><staff>1</staff><beam number="1">begin</beam></note>
  <note><pitch><step>E</step><octave>5</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>down</stem><staff>1</staff><beam number="1">continue</beam></note>
  <note><pitch><step>D</step><octave>5</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>down</stem><staff>1</staff><beam number="1">continue</beam></note>
  <note><pitch><step>A</step><octave>4</octave></pitch><duration>6</duration><voice>1</voice><type>eighth</type><stem>down</stem><staff>1</staff><beam number="1">end</beam></note>
  <backup><duration>72</duration></backup>
  <!-- voice 2: D3+F#3 dotted whole stack -->
  <note><pitch><step>D</step><octave>3</octave></pitch><duration>72</duration><voice>2</voice><type>whole</type><dot/><staff>2</staff></note>
  <note><chord/><pitch><step>F</step><alter>1</alter><octave>3</octave></pitch><duration>72</duration><voice>2</voice><type>whole</type><dot/><staff>2</staff></note>
  <backup><duration>72</duration></backup>
  <!-- voice 3: A2 single -->
  <note><pitch><step>A</step><octave>2</octave></pitch><duration>72</duration><voice>3</voice><type>whole</type><dot/><staff>2</staff></note>
</measure>
```

**m.8 (12/8, N.C., all rest + f)**:
```xml
<measure number="8">
  <print new-system="no"/>
  <attributes>
    <time><beats>12</beats><beat-type>8</beat-type></time>
  </attributes>
  <harmony print-frame="no">
    <root><root-step>C</root-step></root><kind text="N.C.">none</kind>
  </harmony>
  <direction placement="below">
    <direction-type><dynamics><f/></dynamics></direction-type>
    <staff>1</staff>
  </direction>
  <note><rest measure="yes"/><duration>72</duration><voice>1</voice><staff>1</staff></note>
  <backup><duration>72</duration></backup>
  <note><rest measure="yes"/><duration>72</duration><voice>2</voice><staff>2</staff></note>
</measure>
```

### 2.6 Tempo & Metric Modulation 위치

원본은 m.8 위에 두 줄로 표기:
- 줄 1: `(♪ = ♪)` (italic, 작은 글씨)
- 줄 2: **Upbeat Pop** (♩. = ca. 120)

**전략**: P1 Soprano와 P3 Piano 두 part 모두 같은 m.8에 `<direction>` 추가. MuseScore가 자동으로 적절한 위치에 표시.

**Fallback**: MuseScore가 metric modulation 텍스트를 깔끔히 안 놓으면, P1에만 추가하고 P3는 생략.

### 2.7 Page Layout 조정

4 staves가 들어가야 하므로 v4 페이지 1500 → 약간 키울 수도:
- **A안**: page-height 1500 유지 + system-distance 줄임 → 컴팩트
- **B안**: page-height 1700–1800 → 여유 공간

→ **A안 우선 시도**, 잘리면 B안으로.

---

## 3. 구현 순서 (Do)

| # | 작업 | 검증 |
|---|---|---|
| 1 | v4 헤더 복사 (work/identification/credits/defaults) | 기존 v4 패턴 |
| 2 | part-list 3 parts 작성 (Soprano/Solo/Piano) | XML well-formed |
| 3 | P1 Soprano: m.7 (3/2 rest) + m.8 (12/8 rest + tempo + metric mod) | "Soprano" 라벨 + 12/8 표시 |
| 4 | P2 Solo: P1과 동일 구조, "Solo" 라벨 | "Solo" 라벨 표시 |
| 5 | P3 Piano: m.7 (D/A 패턴, divisions=12 스케일) + m.8 (rest + f) | 베이스 voicing + f 표시 |
| 6 | render → 시각 확인 | PNG 생성 |
| 7 | 잘리면 page-height 키움, metric modulation 텍스트 깨지면 fallback 적용 | 재렌더 |
| 8 | source crop 비교 → analysis | match rate |

---

## 4. Acceptance Criteria 매핑

| Plan AC | Design 검증 |
|---|---|
| AC1 (4 staves 표시) | 렌더 PNG에 Soprano + Solo + Pno-treble + Pno-bass 4개 staff |
| AC2 (Part name 라벨) | "Soprano", "Solo" 좌측 표시 |
| AC3 (m.7=3/2, m.8=12/8) | XML attributes + 렌더 시각 |
| AC4 (Upbeat Pop + ♪=♪) | direction 두 개 + 시각 확인 |
| AC5 (S/Solo m.7,8 rest) | `<rest measure="yes"/>` × 4 |
| AC6 (Piano m.7=D/A) | XML 음표 정확 + 렌더 비교 |
| AC7 (v4 헤더 유지) | XML 동일 + 렌더에 제목 표시 |
| AC8 (MIDI 정상) | mid 파일 생성 + 손상 없음 |

---

## 5. Risk Mitigation

| 위험 | 대응 |
|---|---|
| `<beat-unit-dot/>`가 dotted-quarter 표현 | MusicXML 표준 — `<beat-unit>quarter</beat-unit><beat-unit-dot/>` 조합 |
| Metric modulation `(♪ = ♪)` 텍스트가 깨짐 | 유니코드 `♪` 또는 텍스트 `(eighth = eighth)` 으로 대체 |
| 4 staves가 page-height 1500에 안 들어감 | page-height 1700으로 증가 |
| `f` 다이내믹이 staff=1 below 가 아닌 다른 위치 | placement·staff 조합 조정 |

---

## 6. Next Step

```
/pdca do mm7-8-transition
```
