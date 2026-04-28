# 음악 편곡 파이프라인

PDF 악보 → OMR(MusicXML) → 편곡 → 평가 → 최종 출력(PDF/MIDI/WAV/MP3)을 일관된 워크플로우로 처리합니다.

## 사전 설치 (1회)

| 도구 | 용도 | 설치 |
|------|------|------|
| Python ≥ 3.9 | 스크립트 실행 | (이미 설치됨) |
| music21 | MusicXML 조작 | `py -m pip install music21` |
| Audiveris | PDF→MusicXML | `winget install Audiveris` |
| MuseScore 4 | MusicXML→PDF/MIDI/WAV/MP3 | `winget install Musescore.Musescore` |
| Tesseract OCR 데이터 | 빠르기말 OCR | 자동 (또는 [언어팩 수동 다운로드](#tesseract-언어팩-설치)) |

## 디렉터리 구조

```
music_arrange/                              ← 작업 루트(workspace)
├── pipeline/                               ← 본 파이프라인 (재사용)
│   ├── pipeline.py                         ← orchestrator CLI
│   ├── helpers.py                          ← 음악 빌더 헬퍼
│   ├── templates/
│   │   ├── arrange.template.py             ← Claude가 복사할 편곡 템플릿
│   │   └── review.template.md              ← Claude가 복사할 평가 템플릿
│   ├── examples/
│   │   └── mozart_k330_disney.json         ← 실제 작업 예제
│   └── README.md                           ← (이 파일)
├── <원본 악보>.pdf                         ← 입력
├── output_full/                            ← Audiveris 변환 결과
└── arrangement/
    ├── extracts/   *_dump.txt              ← 원본 마디 분석
    ├── versions/   v1.py, v1.musicxml ...  ← 편곡 버전별
    ├── reviews/    v1_review.md ...        ← 교수 평가
    └── final/      <prefix>.pdf/.mid/.wav/.mp3   ← 최종 출력
```

---

## 7단계 파이프라인

### Step 1 · 작업 명세 작성 (`task.json`)

```bash
cd c:\Users\onest\Documents\music_arrange\pipeline
py pipeline.py init my_task.json
```

생성된 [my_task.json](my_task.json) 파일을 편집:

```jsonc
{
  "input": {
    "pdf_path": "../<원본 악보>.pdf",         // ← 편곡할 PDF
    "movement": 1,                            // 다악장 곡일 때 어느 악장 (1~)
    "measure_range": [1, 16]                  // 편곡할 마디 범위 [start, end]
  },
  "arrangement": {
    "ensemble": "violin duet",                // ← 자유 텍스트 (e.g. "string quartet", "piano + cello")
    "style": "Disney",                        // ← 스타일 (e.g. "jazz", "tango", "rock", "minimalist")
    "tempo_text": "Allegretto",
    "tempo_bpm": 104,
    "key": "C major"
  },
  "quality": {
    "passing_score": 85,                      // 합격 기준 평균 점수
    "max_iterations": 5,
    "reviewers": [...]                         // 3명의 가상 평가자 (자유 수정)
  },
  "output": {
    "title": "...",
    "subtitle": "...",
    "filename_prefix": "MyArrangement",        // 최종 파일명 prefix
    "formats": ["pdf", "midi", "wav", "mp3"]
  },
  "paths": {
    "audiveris_exe": "...",
    "musescore_exe": "...",
    "ocr_languages": ["ita", "eng", "deu"],
    "workspace": "../"                         // 출력 폴더 루트 (보통 상위)
  }
}
```

> 예제 참고: [examples/mozart_k330_disney.json](examples/mozart_k330_disney.json)

### Step 2 · PDF → MusicXML 변환 (자동)

```bash
py pipeline.py convert my_task.json
```

- Audiveris가 PDF 모든 페이지를 OMR 처리 (수 분 소요)
- 다악장은 자동 분리 → `<원본명>.mvt1.mxl`, `mvt2.mxl`, ...
- OCR 언어 3종(`ita+eng+deu`)으로 빠르기말·셈여림 텍스트 추출

### Step 3 · 변환 검증 + 도입부 분석 (자동)

```bash
py pipeline.py analyze my_task.json
```

- 박자/조표/마디 수 확인
- `task.json`의 `measure_range`만큼 음표 dump → `arrangement/extracts/mvt{N}_mm{X}-{Y}_dump.txt`
- 빈 마디 / OMR 오인식 의심 마디 보고

### Step 4 · 편곡 V1 작성 (Claude에게 위임)

Claude Code 세션에서 다음과 같이 요청:

> *"my_task.json의 명세대로 V1 편곡을 만들어줘. arrangement/extracts/mvt1_mm1-16_dump.txt를 원본 분석으로 사용. pipeline/templates/arrange.template.py를 기반으로 arrangement/versions/v1.py에 작성."*

Claude는:
1. dump 파일을 읽어 원본 멜로디·화성을 파악
2. 명세된 편성과 스타일에 맞춰 음표를 작성
3. `arrangement/versions/v1.py`로 저장 (template 형식 준수)

### Step 5 · V1 컴파일 (자동)

```bash
py pipeline.py compile my_task.json v1
```

- `versions/v1.py` 실행 → `v1.musicxml` + `v1.mid` 생성
- 마디 길이 자동 검증, 음역 초과 경고

### Step 6 · V1 평가 (Claude에게 위임)

Claude에게 요청:

> *"v1을 평가해줘. task.json의 reviewers 명세대로 3 교수 페르소나로 평가하고 arrangement/reviews/v1_review.md에 저장해. templates/review.template.md 형식 준수."*

Claude는:
1. `versions/v1.py` 또는 `v1.musicxml` 분석
2. 3명 페르소나로 각 항목별 점수 부여
3. `**소계** | **100** | **NN**` 형식으로 점수 작성

### Step 7 · 합격 판정 (자동)

```bash
py pipeline.py decide my_task.json v1
```

- `v1_review.md`에서 점수 자동 추출 → 평균 계산
- **PASS** (≥85): Step 8로 진행
- **FAIL** (<85): Step 4로 돌아가 V2 작성 (Claude가 V1 피드백 반영)

루프 예시:
```
v1 → 76.3 (FAIL) → v2 → 87.0 (PASS) → 종료
```

### Step 8 · 최종 출력 (자동)

```bash
py pipeline.py export my_task.json v2
```

`arrangement/final/<prefix>.{pdf,mid,wav,mp3}` 4개 파일 생성:
- **PDF**: 인쇄/연주용 악보
- **MIDI**: DAW 편집용
- **WAV**: 고품질 청취 (44.1kHz/32bit/stereo)
- **MP3**: 압축 청취 (Windows Media Player에서 더블클릭)

---

## 진행 상황 확인

```bash
py pipeline.py status my_task.json
```

체크리스트 형식으로 각 단계 산출물 표시.

---

## 자주 묻는 질문

### Q. 편곡할 마디 범위는 어떻게 정하나요?
원곡의 자체 완결적 단위(주제부, 부속절)를 선택. 보통 8~32마디. 너무 길면 편곡 작업/평가가 어려워집니다.

### Q. 다른 편성으로 편곡하려면?
`arrangement.ensemble`을 자유 텍스트로 작성:
- `"string quartet"` (현악 4중주)
- `"piano + cello"` (피아노 첼로)
- `"flute + clarinet + bassoon"` (목관 트리오)

`pipeline/helpers.py`의 `INSTRUMENTS` 딕셔너리에 정의된 악기 키:
`violin, viola, cello, bass, flute, clarinet, piano`. 추가 악기는 helpers.py에 등록.

### Q. 다른 스타일은?
`arrangement.style`을 변경. Claude가 평가 시 해당 스타일 전문가(Reviewer C) 페르소나로 평가합니다. 예:
- `"jazz"` → bebop voicing, swing rhythm 평가
- `"tango"` → habanera rhythm, bandoneon-like phrasing
- `"minimalist"` → repetition, phase-shifting

### Q. 평가 기준 점수를 바꾸려면?
`quality.passing_score` 변경 (기본 85). 더 엄격하게 90, 더 관대하게 80.

### Q. 합격 후 더 다듬고 싶다면?
v2 합격 후에도 v3 작성 가능. `compile v3` → `decide v3` → 점수 더 높으면 `export v3`.

### Q. PDF 변환이 너무 부정확하면?
- Audiveris GUI를 열어 `.omr` 파일 직접 편집(연필 모드)
- 수정 후 GUI에서 `File → Export Score → MusicXML`로 다시 저장
- `versions/`로 그 MusicXML 복사 후 진행

### Q. Tesseract 언어팩 설치
첫 실행 시 자동 다운로드되지 않으면 수동으로:
```powershell
$tessdata = "$env:APPDATA\AudiverisLtd\audiveris\config\tessdata"
foreach ($lang in @("eng", "ita", "deu")) {
  Invoke-WebRequest -Uri "https://github.com/tesseract-ocr/tessdata/raw/main/$lang.traineddata" `
    -OutFile "$tessdata\$lang.traineddata" -UseBasicParsing
}
```

---

## 빠른 실행 (Quick Start)

이미 작업한 모짜르트 K.330 디즈니 편곡을 복원/재실행하려면:

```bash
cd c:\Users\onest\Documents\music_arrange\pipeline
py pipeline.py status examples\mozart_k330_disney.json   # 현재 상태 확인
py pipeline.py decide examples\mozart_k330_disney.json v2   # 87점 합격 확인
py pipeline.py export examples\mozart_k330_disney.json v2   # 최종 출력 재생성
```

---

## 새 곡 처음부터 (전체 워크플로우)

1. PDF 파일을 `music_arrange/` 폴더에 둔다
2. 다음 명령:

```bash
cd c:\Users\onest\Documents\music_arrange\pipeline
py pipeline.py init my_task.json
notepad my_task.json    # PDF 경로, 편성, 스타일 입력
py pipeline.py convert my_task.json
py pipeline.py analyze my_task.json
```

3. Claude에게: *"my_task.json 보고 v1 편곡해줘"*
4. ```py pipeline.py compile my_task.json v1```
5. Claude에게: *"v1 평가해줘"*
6. ```py pipeline.py decide my_task.json v1```
7. **PASS면 8로, FAIL이면 Claude에게 v2 부탁 후 4로 돌아감**
8. ```py pipeline.py export my_task.json v?```
9. `arrangement/final/` 폴더에서 PDF·MP3 더블클릭 → 악보·음악 확인

> 끝.
