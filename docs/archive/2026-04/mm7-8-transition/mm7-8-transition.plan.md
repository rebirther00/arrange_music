# mm7-8-transition — Plan

**Feature**: mm7-8-transition
**Scope**: `golden_sing_work/manual/chunks/mm007-008.musicxml` (Golden, page 2 system 3, mm.7–8 transition section)
**Created**: 2026-04-29
**Phase**: Plan
**Predecessor**: v4-engraving-fix (헤더 표준), mm4-6 (음표 표준)

---

## Executive Summary

| 관점 | 내용 |
|---|---|
| **Problem** | mm.7–8은 곡 구조의 핵심 전환점이지만, 기존 chunk(피아노 단독 3/2)와 달리 **3개 새로운 도전**을 동반: ① Soprano + Solo(Alto/Tenor) 보컬 스태프 첫 등장 (4-staff layout), ② m.8에서 박자 3/2 → 12/8 변경, ③ 템포 텍스트 "Upbeat Pop (♩.=ca. 120)" + metric modulation `(♪=♪)` 표기. 표준화 없이 진행하면 후속 chunk(m.9 Verse 1, 12/8) 와 호환 불가 |
| **Solution** | mm.7–8 chunk를 **표준 정립용 reference**로 정의: ① part-list에 Soprano/Solo 추가 (4 staves: S, Solo, Piano-treble, Piano-bass), ② m.8에 `<attributes>` 박자 변경 + `<direction>` 으로 metric modulation 텍스트, ③ 보컬 staff는 m.7-8에서 whole rest로 표시 (음악 m.9부터). v4 헤더 표준은 그대로 계승 |
| **Function/UX Effect** | 1 시스템에 4 스태프 그랜드 배치(S, Solo, Pno-treble, Pno-bass), m.7 끝에서 m.8 시작에 맞춰 박자 표기 전환, "Upbeat Pop (♩.=ca. 120)" 신 템포 + 위에 작은 글씨 `(♪=♪)` 표시 → 원본 Hal Leonard p.2 sys3 정확 재현 |
| **Core Value** | mm.7–8 표준이 확정되면 **모든 12/8 SAB chunk(m.9~)가 동일 part-list와 4-staff 구조 사용** → 장당 30분 절약. 또한 metric modulation 표기 패턴은 후속 곡 구조 변경 시 재사용 가능한 자산 |

---

## 1. Background

`structure.json`에 정의된 chunk 메타:
```json
{"id": "mm007-008", "page": 2, "system": 3,
 "active_parts": ["Soprano", "Alto", "Piano"],
 "note": "S+A appear as empty staves; transition bar at m8"}
```

**구조적 변화 (3가지)**:
1. **Part list 확장**: P1 Piano만 있던 v4에 P0 Soprano, P0.5 Solo(Alto/Tenor) 추가 → 4 staves
2. **Time signature 전환**: m.7 = 3/2 (intro 마지막 마디, 빈 베이스 패턴), m.8 = 12/8 (전환 마디)
3. **Tempo & metric modulation**: m.8에서 "Upbeat Pop (♩. = ca. 120)" + `(♪ = ♪)` (eighth=eighth equivalence) 표기

**참고 자료**:
- 원본 크롭: [page02_sys3_FULL_HD.png](../../../golden_sing_work/manual/rendered/source_crops/page02_sys3_FULL_HD.png)
- 기존 m9 reference: [m9_reference.musicxml](../../../golden_sing_work/m9_reference.musicxml) (Verse 1 시작 — part-list 검증 가능)
- v4 헤더 표준: [mm001-003.musicxml](../../../golden_sing_work/manual/chunks/mm001-003.musicxml)
- structure.json: [structure.json](../../../golden_sing_work/manual/structure.json)

---

## 2. Goals (이번 사이클 범위)

| # | 목표 | 검증 방법 |
|---|---|---|
| **G1** | Part-list에 Soprano + Solo 추가 (3 part: P1 Soprano, P2 Solo, P3 Piano) | XML에 `<score-part id="P1">…<part-name>Soprano</part-name>…` 등 확인 + 렌더 PNG에 4-staff 표시 |
| **G2** | m.7 = 3/2 piano accompaniment 유지 (S/Solo는 whole rest), m.8에서 12/8 전환 | XML의 m.8에 `<attributes><time><beats>12</beats><beat-type>8</beat-type></time></attributes>` + 렌더에서 m.8 좌측에 `12/8` 박자표 |
| **G3** | m.8 위에 `(♪ = ♪)` metric modulation + "Upbeat Pop (♩. = ca. 120)" 템포 표기 | XML의 m.8 `<direction>`에 두 줄 words + metronome `parentheses="yes"` 적용 + 렌더 시각 확인 |
| **G4** | Soprano/Solo는 m.7-8 둘 다 비어있음 (whole rest 또는 multi-rest) | XML의 P1/P2 m.7,8에 `<note><rest measure="yes"/>...` + 렌더에 빈 마디 표시 |
| **G5** | Piano (P3)의 m.7 = 어떤 화성? (베이스 패턴 무엇?), m.8 = 비어있는지 12/8로 전환만인지 확인 | 원본 크롭 zoom 후 결정 |

---

## 3. Open Questions (Design 단계에서 해결)

소스 크롭으로 100% 명확하지 않은 것들 — Design phase에서 zoom 크롭으로 확인 필요:

| Q | 내용 | 해결 방법 |
|---|---|---|
| Q1 | m.7 piano는 어떤 코드인지? (m.6 G/B에서 어디로?) | 페이지 PNG zoom 크롭 |
| Q2 | m.8 piano는 빈 마디인가, 짧은 12/8 패턴이 있나? | zoom 크롭 |
| Q3 | "Upbeat Pop" 텍스트는 m.8 위에만 있나, m.9 위에 있나? | zoom 크롭 — 박자 변경 위치와 일치하는지 |
| Q4 | metric modulation 표기 정확한 모양 ("eighth=eighth" or "dotted-quarter=quarter") | structure.json에는 dotted-quarter=quarter지만 원본 PNG는 eighth=eighth 로 보임 — 재확인 |
| Q5 | Solo staff label은 "Solo" 만? "Alto or Tenor Solo"는 첫 entry에 붙는 캐릭터 텍스트? | zoom 크롭 + m9_reference.musicxml 비교 |

---

## 4. Non-Goals (이번 사이클에서 다루지 않음)

- m.9 이후 작업 (별도 chunk `mm009-012`)
- 가사 입력 (m.9 시점부터 시작 → 다음 PDCA에서)
- Baritone 파트 (이 chunk에는 등장 안 함, 나중 chunk에서 SAB 중 B 추가)
- Solo 음표 입력 (m.7-8은 모두 rest)
- v4 페이지 레이아웃 변경 (4 staves가 들어가도록 page-height 조정 필요할 수 있음 → Design 단계에서 결정)

---

## 5. Acceptance Criteria

다음 모두 만족 시 통과:

1. ✅ 4 staves 렌더 표시 (Soprano / Solo / Piano-treble / Piano-bass)
2. ✅ Part name "Soprano", "Solo" 좌측 라벨 표시
3. ✅ m.7 = 3/2, m.8 = 12/8 박자 표기 시각 확인
4. ✅ m.8 위에 "Upbeat Pop (♩. = ca. 120)" 템포 + 위에 작은 `(♪ = ♪)` 표기
5. ✅ Soprano/Solo의 m.7, m.8 모두 비어있음 (whole rest 또는 multi-rest)
6. ✅ Piano의 m.7 음표는 zoom 크롭으로 확인된 내용 일치
7. ✅ v4 헤더 표준 그대로 유지 (Title/subtitle/credits)
8. ✅ MIDI 파일 정상 생성 (박자 변경에도 음악 재생 가능)

---

## 6. Risks

| 위험 | 대응 |
|---|---|
| 4 staves가 page-height 1500에 들어가지 않음 | page-height 1500 → 1800 또는 2000으로 증가 |
| MuseScore 4가 metric modulation `(♪ = ♪)` 텍스트 자동 렌더링 안 함 | `<direction>`에 직접 텍스트로 작성 (`<words>(♪ = ♪)</words>`) |
| `<attributes>` 박자 변경이 measure 시작이 아닌 중간에 들어가면 무시됨 | m.8 `<measure>` 직후 `<attributes>` 배치 |
| 보컬 part가 다른 파트와 voice/staff 충돌 | 각 part가 독립 P1/P2/P3 → 충돌 없음 (스태프 번호 1만 사용) |
| Part name 라벨 길이가 다른 chunk와 일관성 없음 (Soprano vs S, Solo vs A 등) | structure.json 기준: full name(Soprano, Alto, Baritone, Piano), abbr(S, A, B, Pno.) — chunk-level은 first system에 full, 후속에 abbr |

---

## 7. Dependencies

- v4-engraving-fix 완료 (헤더 표준 확정) — ✅ 완료
- mm4-6 완료 (음표 표준 검증) — ✅ 완료
- Page 02 highres PNG 존재 — ✅ 확인됨
- m9_reference.musicxml 참고 가능 — 검증 필요

---

## 8. Estimated Effort

- **Design phase**: 1시간 (Q1–Q5 해결 + part-list 구조 확정 + metric modulation XML 명세)
- **Do phase**: 1.5–2시간 (4 stave musicxml 작성, 박자 변경, 템포 마크, 반복 렌더)
- **Check phase**: 30분 (시각 비교 + match rate)
- **총**: **3–3.5시간 예상**

v4 (2시간) + mm4-6 (30분) 와 비교 시 더 큼. 구조 변경 영향.

---

## 9. Next Step

```
/pdca design mm7-8-transition
```

Design 단계에서:
1. 5개 Open Question 해결 (페이지 zoom 크롭으로)
2. part-list/score-instrument XML 정확 명세
3. m.8 박자 변경 + 템포 + metric modulation XML 정확 명세
4. m9_reference.musicxml의 part-list 구조와 일관성 검증
