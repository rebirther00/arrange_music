# Music Arrangement Pipeline

PDF 악보 → OMR(MusicXML) → AI 편곡 → 4-교수 평가 루프 → PDF/MIDI/MP3 출력을
일관된 워크플로우로 자동화한 음악 편곡 파이프라인입니다.

## 작업 결과 요약

### 1. Mozart K.330 — Disney 풍 바이올린 듀엣
- 16마디 도입부, ♩.=123, 4-교수 평균 87.0점 (V2 합격)
- 출력: `arrangement/final/Mozart_K330_Disney_Violin_Duet.{pdf,mid,mp3}`

### 2. Golden Demon — 현악 4중주 (원곡 충실)
- 82마디, ♩.=123, 4-교수 평균 88.0점 (V2 합격)
- 출력: `golden_demon_work/arrangement/final/Golden_Demon_String_Quartet.{pdf,mid,mp3}`

### 3. Demon Hunters — 9-Part 오케스트라 (V11)
- 82마디, ♩.=123, 4-교수 평균 99.5점 (V11, all ≥ 99)
- 편성: Piano + Vn1 + Vn2 + Va + Vc + Cb + Cl + Fl + Drums
- 11번의 PDCA 반복으로 단계별 개선:
  - V1-V2: 멜로디 분배 + chord-tone alternation
  - V3: 음악감독 시점 (텍스처 분리, Piano 재작성)
  - V4: Pietschmann-style cinematic piano idiom
  - V5: 인트로/아웃트로 원곡 ostinato figure 복원
  - V6: 인트로 layered build + 아웃트로 layered decay
  - V7: Bb 클라리넷 written pitch + Piano clef 명시 + Vc/Fl 멜로디 조정
  - V8: 오케스트라 어법 (rhythmic counter-figures + Va stepwise counter)
  - V9: 다이어토닉 평행 라인 보정 (mm.25-32, 58-65, 66-74)
  - V10: Piano RH playable voicings (octave-span max)
  - V11: 음역 정리 (MuseScore amateur 안) + Cl key signature 3 sharps
- 출력: `demon_hunters_work/arrangement/final/Demon_Hunters_Ensemble.{pdf,mid,mp3}`

## 디렉터리 구조

```
music_arrange/
├── pipeline/                       ← 재사용 가능 파이프라인 프레임워크
│   ├── pipeline.py                 ← orchestrator CLI (init/convert/analyze/compile/decide/export/status)
│   ├── helpers.py                  ← 음악 빌더 (N, R, CH, make_part, make_score, INSTRUMENTS, ...)
│   ├── verify_playable.py          ← 자동 음역/화음 stretch 검증
│   ├── templates/
│   │   ├── arrange.template.py     ← 편곡 코드 템플릿
│   │   └── review.template.md      ← 4-교수 평가 템플릿
│   ├── examples/
│   │   └── mozart_k330_disney.json
│   ├── golden_demon_task.json
│   ├── demon_hunters_task.json
│   └── README.md                   ← 사용 가이드
├── arrangement/                    ← Mozart K.330 작업물
│   ├── extracts/
│   ├── versions/                   ← v1.py, v1.musicxml, v2.py, v2.musicxml, ...
│   ├── reviews/                    ← v1_review.md, v2_review.md
│   └── final/                      ← PDF/MIDI/MP3 (WAV는 .gitignore)
├── golden_demon_work/              ← Golden Demon 작업물 (동일 구조)
├── demon_hunters_work/             ← Demon Hunters 작업물 (동일 구조, V1~V11)
└── scripts/                        ← 분석/검증 스크립트
```

## 사용 방법 (새 PDF 편곡)

```bash
cd pipeline
py pipeline.py init my_task.json    # task.json 템플릿 생성
notepad my_task.json                # PDF 경로, 편성, 스타일 입력
py pipeline.py convert my_task.json # PDF → MusicXML (Audiveris)
py pipeline.py analyze my_task.json # 마디 dump 생성
# Claude에게 v1 편곡 의뢰 (versions/v1.py 작성)
py pipeline.py compile my_task.json v1
# Claude에게 v1 평가 의뢰 (reviews/v1_review.md 작성)
py pipeline.py decide my_task.json v1   # 합격선 판정
# 합격 시:
py pipeline.py export my_task.json v1   # PDF/MIDI/WAV/MP3 출력
```

자세한 내용은 [pipeline/README.md](pipeline/README.md) 참조.

## 사전 설치 (Windows)

```powershell
winget install Audiveris                  # PDF → MusicXML
winget install Musescore.Musescore        # MusicXML → PDF/MIDI/WAV/MP3
py -m pip install music21                  # MusicXML 조작
```

## 라이선스

이 저장소는 편곡 파이프라인 코드(`pipeline/`, `scripts/`)와 사용자가 작성한 편곡 결과물을 포함합니다.
원본 악보 PDF는 저작권 보호를 위해 `.gitignore`로 제외되어 있습니다.

## 참고

- [Audiveris](https://github.com/Audiveris/audiveris) — OMR 엔진
- [MuseScore](https://musescore.org/) — MusicXML 렌더러
- [music21](https://www.music21.org/) — Python 음악 분석/조작 라이브러리
