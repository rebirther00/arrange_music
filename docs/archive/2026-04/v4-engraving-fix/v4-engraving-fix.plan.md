# v4-engraving-fix — Plan

**Feature**: v4-engraving-fix
**Scope**: `golden_sing_work/manual/chunks/mm001-003.musicxml` (Golden, Hal Leonard 01946654, page 2 system 1, m.1–3)
**Created**: 2026-04-28
**Phase**: Plan
**Predecessor**: v3 (current `mm001-003.musicxml`)

---

## Executive Summary

| 관점 | 내용 |
|---|---|
| **Problem** | v3는 음정·리듬·화성·슬러는 정확하나 조판 품질이 미흡: 시스템이 과도하게 늘어나고(페이지폭 2400 tenths), 다이내믹(`mp`) 위치가 베이스 클레프 아래로 부정확하며, 템포 텍스트(`(♩ = ca. 90)`) 와 곡 메타데이터가 누락됨 |
| **Solution** | MusicXML 헤더(페이지 레이아웃·`<work>`·`<credit>`)와 `<direction>` 배치(`mp` placement, metronome `parentheses` + words "ca.")를 원본 Hal Leonard 스타일에 맞춰 보정. 음표 자체는 변경하지 않음 |
| **Function/UX Effect** | 1 시스템 = 3 마디를 유지하면서 가로 폭이 약 70% 수준으로 압축, 다이내믹이 그랜드 스태프 중간에 위치, 템포 텍스트가 원본과 동일 표기, 곡명·편곡자 노출 → 출판 인쇄물 품질에 근접 |
| **Core Value** | "Recording-faithful" 단계를 넘어 "Print-faithful" 단계 진입. 이후 chunk(mm.4–6 등)에 적용할 **조판 표준 템플릿**을 v4로 확정 → 후속 chunk가 동일 품질로 자동 출력됨 |

---

## 1. Background

`/manual/rendered/compare/cmp__page02_sys1_FULL_HD__mm001-003-1__hstitch.png` 비교 결과 v3는 음악적으로는 일치하지만 시각적으로 원본 인쇄물과 차이가 있음. 후속 chunk를 양산하기 전에 **조판 기준선**을 잡는 작업이 필요함.

**관련 파일**:
- 원본 크롭: [golden_sing_work/manual/rendered/source_crops/page02_sys1_FULL_HD.png](golden_sing_work/manual/rendered/source_crops/page02_sys1_FULL_HD.png)
- v3 렌더: [golden_sing_work/manual/rendered/mm001-003-1.png](golden_sing_work/manual/rendered/mm001-003-1.png)
- v3 소스: [golden_sing_work/manual/chunks/mm001-003.musicxml](golden_sing_work/manual/chunks/mm001-003.musicxml)
- 프로젝트 plan: [golden_sing_work/manual/plan.md](golden_sing_work/manual/plan.md)

---

## 2. Goals (이번 사이클 범위)

| # | 목표 | 검증 방법 |
|---|---|---|
| G1 | 페이지 폭 압축 → 1 시스템에 3 마디가 가로 약 1500–1700 tenths에 들어가도록 | render 결과 PNG 가로 폭이 v3 대비 60–75% |
| G2 | `mp` 다이내믹을 그랜드 스태프 **중간**(또는 베이스 위)으로 이동 | 렌더 PNG에서 mp 글자가 베이스 클레프보다 위에 위치 |
| G3 | 템포 텍스트를 `**Moderately** (♩ = ca. 90)` 형식으로 정확 표기 | 렌더 PNG에서 괄호와 "ca." 표시 확인 |
| G4 | 곡 메타데이터(`<work-title>Golden</work-title>`) 및 편곡자 credit 추가 | 페이지 상단에 제목·작사·작곡 표시 |
| G5 | 베이스 보이싱(voice 2 dyad vs voice 3 single)의 시각적 분리 명확화 — 필요시 stem 방향 명시 | m1·m3는 dyad-위/single-아래, m2는 single-위/dyad-아래 — 시각 구분 가능 |

---

## 3. Non-Goals (이번 사이클에서 다루지 않음)

- 음정·리듬 변경 (이미 v3에서 정확)
- 슬러 추가/삭제 (v3 슬러는 원본과 일치)
- mm.4 이후 chunk (별도 후속 작업)
- SAB 보컬 파트 (이 chunk는 피아노 인트로만)
- MuseScore CLI 자체 옵션 변경 (`render_chunk.py` 수정은 필요시에만)

---

## 4. Acceptance Criteria

다음 모두 만족 시 `/pdca analyze v4-engraving-fix` 통과 기준:

1. ✅ `mm001-003.musicxml`에서 `<page-width>` 또는 `<system-margins>` 조정으로 가로 압축
2. ✅ `<direction placement="...">` 변경으로 `mp`가 베이스 클레프 위(staff 1 below 또는 staff 2 above)에 위치
3. ✅ `<metronome parentheses="yes">` 와 `<words>ca. </words>`로 템포 표기 보정
4. ✅ `<work><work-title>Golden</work-title></work>` 및 `<credit>` (composer / lyricist / arranger) 추가
5. ✅ 렌더 결과 시각 비교에서 5개 항목 모두 원본과 근사 (사용자 육안 확인)
6. ✅ MIDI/MP3는 v3와 동일 (음악 내용 변경 없음 검증)

---

## 5. Risks

| 위험 | 대응 |
|---|---|
| 페이지 폭 줄이면 음표가 겹쳐서 가독성 손상 | 단계적으로 2400 → 2000 → 1700 → 1500 시도하며 시각 확인 |
| `parentheses="yes"`가 MuseScore 4 버전에서 일부 무시될 수 있음 | fallback으로 `<words>(♩ = ca. 90)</words>` 직접 텍스트 사용 |
| 메타데이터 추가 시 타이틀이 시스템 위 공간을 잡아먹어 첫 시스템이 페이지 아래로 밀림 | `<top-margin>` 조정 또는 credit 위치 조정 |
| Stem 방향 명시(voice 2/3 분리)가 다른 chunk 표준과 충돌 | 이번 chunk만 적용하고 후속 chunk에 일반화 시점 검토 |

---

## 6. Dependencies

- MuseScore 4 CLI (`render_chunk.py`에서 호출) — 기존 환경 그대로
- Python compare/stitch 스크립트 — 기존 그대로
- 원본 PDF 크롭 PNG — 기존 그대로

새 의존성 없음.

---

## 7. Estimated Effort

- Design phase: 30분 (XML diff 명세 작성)
- Do phase: 1–1.5시간 (반복 렌더 포함)
- Check phase: 30분 (시각 비교 + match rate)
- 총: **2–3시간 예상**

---

## 8. Next Step

```
/pdca design v4-engraving-fix
```

Design 문서에서 각 목표(G1–G5)에 대한 정확한 XML 변경 명세(현재값 → 변경값)를 작성합니다.
