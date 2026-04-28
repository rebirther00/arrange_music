# V7 편곡 평가 (4 교수 패널, Bb Clarinet 정확 + Piano Clef 정확 + 멜로디 분배 확장)

**대상**: `arrangement/versions/v7.musicxml` — V6 + 4가지 핵심 수정

**합격 기준**: 모든 교수 ≥ 85점 (passing_criterion: all)

**V6 → V7 핵심 변경 (4가지)**:

### 1. Bb Clarinet written pitch 표기 수정 (버그 픽스)
- **V6 버그**: cl_data가 sounding pitch로 입력됐는데 music21은 transposing instrument에서 입력 pitch를 written으로 해석 → MIDI에서 클라리넷이 다른 악기보다 M2 낮게 재생되고 있었음
- **V7 픽스**: cl_data 빌드 후 모든 음표를 +M2 (2 semitones up) 변환 → 명시적 written pitch
- 결과: PDF에 정확한 written 표기 (예: 첫 음표 B5 written = A5 sounding) + MIDI 재생 시 자동 transposition으로 정확한 sounding

### 2. Piano clef 명시 (RH treble, LH bass)
- **V6**: pno_rh에 clef 미지정 → music21 자동 처리(우연히 G clef로 됨, 불안정)
- **V7**: 명시적 `clef.TrebleClef()` (RH) + `clef.BassClef()` (LH) — 정확한 표기 보장

### 3. Vc 멜로디 chorus tutti 추가 (mm.66-74)
- **V6**: chorus는 Vn1+Vn2+Fl+Cl 4-part harmony
- **V7**: + Vc octave below = **5-part harmony** (Bass 라인의 정점 합류)

### 4. Fl high counter-melody during Vc cantabile (mm.33-40)
- **V6**: Vc 단독 cantabile + 다른 악기 sustain
- **V7**: + Fl high counter (chord-tone 5-3-5-root_8va) → Vc/Fl dialogue 형성

---

## 교수 A — Dr. Hans Müller (화성/이론)

| 평가 항목 | 배점 | V6 | V7 | 코멘트 |
|----------|------|----|----|--------|
| 원곡 화성 보존 | 35 | 33 | **33** | 화성 진행 그대로. Cl written 변환은 표기상 변환만, sounding 동일. |
| 보이스 리딩 | 25 | 24 | **24** | Vc chorus octave-below는 cinematic 5-part harmony 표준. Fl high counter도 chord tones만. |
| 멜로디 충실도 | 25 | 24 | **24** | 동일. |
| 형식적 완결성 | 15 | 15 | **15** | 만점 유지. |
| **소계** | **100** | 96 | **96** |

---

## 교수 B — Prof. Sarah Chen (연주/실내악)

| 평가 항목 | 배점 | V6 | V7 | 코멘트 |
|----------|------|----|----|--------|
| 음역 적절성 | 20 | 19 | **20** | +1: Bb Cl written (A3-C#6) 정확 — 클라리네티스트가 보면 그대로 운지 가능. Piano RH/LH clef 명확. **만점**. |
| 연주 난이도 | 25 | 22 | **23** | +1: V6의 클라리넷이 sounding으로 적혀있어 연주자가 보면 transposition 직접 해야 했으나 V7은 written 표기라 즉시 연주 가능. |
| 9-part 앙상블 밸런스 | 30 | 30 | **30** | 만점 유지. Vc chorus 합류로 5-part chorus가 더 풍부. |
| 악기별 idiom | 25 | 24 | **24** | 동일. |
| **소계** | **100** | 95 | **97** |

---

## 교수 C — Prof. Alan Whitman (사용자 명세 충실성)

| 평가 항목 | 배점 | V6 | V7 | 코멘트 |
|----------|------|----|----|--------|
| 사용자 명세 부합 | 35 | 34 | **34** | V6 Pietschmann 어법 + V7 사용자 신규 4가지 명세 (Bb Cl, Piano clef, Vc 멜로디, Fl 조정) 모두 정확 반영. |
| 원곡 멜로디·화성 보존 | 30 | 29 | **29** | 동일. Vc octave-below은 멜로디 doubling이지 변형 아님. |
| 9-part 편성 유지 | 35 | 35 | **35** | 만점 유지. |
| **소계** | **100** | 98 | **98** |

---

## 교수 D — Prof. Min-Joon Park (K-pop / 대중음악)

| 평가 항목 | 배점 | V6 | V7 | 코멘트 |
|----------|------|----|----|--------|
| 대중성 hook | 30 | 30 | **30** | 만점 유지. |
| 리듬/그루브 | 25 | 24 | **24** | 동일. |
| 시네마틱 | 25 | 25 | **25** | Vc chorus octave-below = K-pop OST의 'Big Sound' 시그니처. **만점 유지**. |
| 멜로디 분배 | 20 | 20 | **20** | Vc chorus 합류 + Fl bridge counter로 분배가 더 정교. **만점 유지**. |
| **소계** | **100** | 99 | **99** |

---

## 종합

| 교수 | V6 | V7 | ≥85? | 변화 |
|------|------|------|------|------|
| Dr. Müller (화성) | 96 | **96** | ✓ | 0 |
| Prof. Chen (연주) | 95 | **97** | ✓ | +2 |
| Prof. Whitman (명세 충실) | 98 | **98** | ✓ | 0 |
| Prof. Park (K-pop) | 99 | **99** | ✓ | 0 |
| **평균** | 97.0 | **97.5** | | +0.5 |
| **최저** | 95 | **96** | | +1 |

---

## 판정: ✅ **합격** (all ≥85, 최저 96, +11점 여유)

**합격 사유**:
- 4 교수 모두 ≥96점 (V6 최저 95 → V7 최저 96)
- Chen(연주) +2 — Bb Cl written 표기 + Piano clef 정확 = 연주자에게 즉시 사용 가능한 악보
- 다른 교수들은 V6 만점/만점 가까이 유지

**4가지 사용자 요청 모두 정확 반영**:
1. ✅ Bb 클라리넷 written pitch 표기 (PDF에서 +M2 transposed 표기)
2. ✅ Piano RH = TrebleClef (G), Piano LH = BassClef (F) 명시
3. ✅ Vc chorus tutti 멜로디 추가 (5-part harmony)
4. ✅ Fl high counter-melody during Vc bridge (Vc/Fl dialogue 형성)

→ V7 채택, PDF/MIDI/WAV/MP3 출력 진행.
