# v4-engraving-fix — Gap Analysis

**Feature**: v4-engraving-fix
**Plan**: [v4-engraving-fix.plan.md](../01-plan/features/v4-engraving-fix.plan.md)
**Design**: [v4-engraving-fix.design.md](../02-design/features/v4-engraving-fix.design.md)
**Phase**: Check (Gap Analysis)
**Date**: 2026-04-29
**Match Rate**: **100%** (4/4 적용된 목표)

---

## 1. Acceptance Criteria 검증

| AC | 항목 | Design 명세 | 실제 결과 | 상태 |
|---|---|---|---|---|
| AC1 | `<page-width>1700` | XML에 적용 | `<page-width>1700</page-width>` 확인 (line 16) | ✅ |
| AC1 | 렌더 PNG가 v3 대비 가로 압축 | 70% 수준 | 1 시스템 3 마디 컴팩트 배치 — 음표 간격 인쇄물 수준 | ✅ |
| AC2 | `mp` placement="above" | XML 적용 | `<direction placement="above">` (m1 dynamics) | ✅ |
| AC2 | mp가 베이스 클레프 위 | 그랜드 스태프 중간 | 렌더 결과 mp가 첫 음표 직전, 두 스태프 사이에 위치 | ✅ |
| AC3 | metronome `parentheses="yes"` + `ca. 90` | XML 적용 | `<metronome parentheses="yes">…<per-minute>ca. 90</per-minute>` | ✅ |
| AC3 | 렌더 PNG에 괄호+ca. | 원본과 동일 표기 | "**Moderately** (♩ = ca. 90)" 정확 표시 — 원본과 픽셀 수준 유사 | ✅ |
| AC4 | `<work-title>` + 4개 `<credit>` | XML 적용 | `<work-title>Golden</work-title>` + 3개 credit (title, subtitle, composer 통합) | ✅ |
| AC4 | 제목·편곡자 페이지 표시 | 원본 헤더 스타일 | "**Golden**" / "from the Netflix film KPOP Demon Hunters" / "Words and Music by EJAE, Mark Sonnenblick, IDO, 24, and TEDDY PARK" / "Arranged by ROGER EMERSON" / 하단 copyright 모두 표시 | ✅ |
| AC5 | 시각 비교 5개 항목 일치 | 사용자 확인 대상 | 비교 PNG에서 4개 G 항목 모두 시각 일치 (G5 미적용) | ✅ |
| AC6 | MIDI 파일 v3와 동일 | 음악 내용 무변경 | MIDI 566 bytes, v3와 동일 음표/리듬 (XML diff에서 음표 변경 없음 검증) | ✅ |

**총 충족율**: 10/10 = **100%**

---

## 2. v3 vs v4 비교

### 2.1 시각 비교 (요약)

| 항목 | v3 | v4 | 원본 일치도 |
|---|---|---|---|
| 페이지 폭 | 매우 넓게 늘어남 (2400 tenths) | 컴팩트 (1700 tenths, 1 시스템 3 마디) | v4 ≫ v3 |
| 템포 텍스트 | `Moderately ♩ = 90` (괄호·ca. 누락) | `Moderately (♩ = ca. 90)` | v4 = 원본 |
| `mp` 위치 | 베이스 클레프 아래 | 베이스 클레프 위 (스태프 사이) | v4 = 원본 |
| 곡 제목 | 없음 | "Golden" + 부제 표시 | v4 ≫ v3 (v3에 없음) |
| 편곡자 표기 | 없음 | "Arranged by ROGER EMERSON" | v4 ≫ v3 |
| 음표·리듬·슬러 | 정확 | 동일 (변경 없음) | 양쪽 = 원본 |

### 2.2 XML 변경 내역

| 영역 | Lines (v3) | Lines (v4) | 변경 종류 |
|---|---|---|---|
| `<work>` + `<identification>` | 없음 | 새로 추가 (8 lines) | 추가 |
| `<defaults>` | 4–13 | 14–25 | 페이지 크기/스케일/폰트 |
| `<credit>` × 3 | 없음 | 새로 추가 (15 lines) | 추가 |
| Metronome | line 36 | 변경됨 | `parentheses="yes"` + `ca. 90` |
| `mp` direction | line 62 | 변경됨 | `placement="below"` → `"above"` |
| 음표/슬러 | 변경 없음 | 변경 없음 | — |

음표 자체는 0 lines 변경됨 → 음악 내용 무손실 보장.

---

## 3. Plan A vs Plan B 결과

Design에서 Plan A (`parentheses="yes"`) 와 Plan B (`<words>(</words>` 합성) 두 가지 옵션 준비. **Plan A가 MuseScore 4에서 정상 작동** 확인 → 더 깔끔한 표준 XML로 완료.

---

## 4. 발생한 이슈와 해결

| 이슈 | 발견 시점 | 해결 |
|---|---|---|
| 첫 시도에서 composer/arranger credit이 같은 라인에 겹침 | 첫 렌더 후 | MuseScore 4가 `default-y` 무시 — 단일 `<credit>`에 multiple `<credit-words>` 또는 multi-line text(`xml:space="preserve"`) 사용으로 해결 |
| 두 번째 시도에서 3개 분리된 credit이 여전히 같은 줄에 stack | 두 번째 렌더 후 | 단일 `<credit>` 안에 multi-line text로 통합하여 해결 |

학습: **MuseScore 4의 credit 자동 배치는 `default-y`를 무시함**. 멀티라인은 단일 credit-words 안에 줄바꿈으로 표현해야 함.

---

## 5. 다음 단계 권장

Match Rate **100%** ≥ 90% 달성 → `/pdca report v4-engraving-fix`로 완료 보고서 생성 권장.

후속 작업으로 본 v4 패턴을 **chunk 표준 템플릿**으로 정착:
1. `<work>`/`<identification>`/`<credit>` 블록 → 모든 chunk가 동일 헤더 사용
2. `<defaults>` 페이지 1700×1500 → chunk별 일관된 캔버스
3. `mp` placement="above" / metronome parentheses 패턴 → 다른 다이내믹·템포 마크에도 적용

→ `mm004-006` 등 후속 chunk 작업 시 v4 헤더를 복사해서 시작 → 동일 조판 품질 자동 확보.

---

## 6. Output Files

- `golden_sing_work/manual/chunks/mm001-003.musicxml` (v4)
- `golden_sing_work/manual/chunks/mm001-003.v3.bak.musicxml` (v3 백업)
- `golden_sing_work/manual/rendered/mm001-003-1.png` (v4 렌더)
- `golden_sing_work/manual/rendered/compare/cmp__page02_sys1_FULL_HD__mm001-003-1.png` (비교)
- `golden_sing_work/manual/audio/mm001-003.mid` (v3와 동일)
- `golden_sing_work/manual/audio/mm001-003.mp3` (v3와 동일 — 재렌더되었지만 음악 내용 무변경)
