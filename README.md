# 프리미엄 프라이빗 커플 스파 — 사업계획서(가로형) · 홍보영상

㈜C&C 「프리미엄 프라이빗 커플 스파 사업계획서 (수정 가격정책 및 매출모델 반영본)」의 텍스트를
영업·투자 협의용 **16:9 가로형 제안서 PDF**와 **홍보영상(MP4)**으로 재구성한 작업물입니다.

## 결과물 (`out/`)

| 파일 | 내용 |
|---|---|
| `C&C_프리미엄프라이빗커플스파_사업계획서_가로형.pdf` | 24페이지 가로형 제안서 (1920×1080, 텍스트 선택·검색 가능) |
| `C&C_프리미엄프라이빗커플스파_홍보영상.mp4` | 84초 홍보영상 (1920×1080, 30fps, H.264 + AAC, 자체 제작 배경음악) |

## 구조

```
deck/            제안서 소스 (HTML/CSS/JS) → build.py 로 PDF·PNG 렌더
  data.js        사업계획서 수치(가격·매출·공사비·KPI 등)와 사진 슬롯 정의
  charts.js      차트(SVG) — 제안서와 영상이 공유
video/           홍보영상 소스
  promo.html     장면 타임라인 (renderFrame(t)로 프레임 단위 제어)
  music.py       배경음악 합성 (80 BPM, 84초)
  render.py      헤드리스 Chromium 프레임 캡처 → ffmpeg 인코딩
assets/
  images/        실사 사진 슬롯 (PROMPTS.md 참고) — 비어 있으면 atmos 이미지로 대체
  atmos/         절차적 분위기 배경 (tools/atmos.py)
  fonts/         Pretendard · Noto Serif KR(서브셋) · Cormorant Garamond — 모두 OFL
tools/           atmos.py · fonts.py · place_photos.py
```

## 다시 만들기

```bash
pip install playwright numpy scipy pillow fonttools brotli pymupdf
sudo apt-get install -y ffmpeg          # 영상 인코딩
python3 deck/build.py                   # PDF + out/preview/*.png
python3 video/music.py                  # 배경음악 (video/music.wav)
python3 video/render.py                 # 홍보영상 MP4 (약 5~6분)
```

Chromium 경로는 `CHROME_PATH` 환경변수로 바꿀 수 있습니다.
텍스트를 고친 뒤 드문 한글 글자가 빠져 보이면 `python3 tools/fonts.py`로 폰트 서브셋을 다시 만듭니다.

## 사진 넣기

```bash
python3 tools/place_photos.py --list                     # 슬롯 목록과 채워진 상태
python3 tools/place_photos.py ~/Downloads/a.png cover     # 사진을 슬롯에 배치
python3 tools/place_photos.py b.png loc_nampo --pos "40% 55%"   # 크롭 초점 지정
python3 deck/build.py && python3 video/render.py
```

슬롯별 구도와 ChatGPT용 프롬프트는 [`assets/images/PROMPTS.md`](assets/images/PROMPTS.md)에 있습니다.

## 원문 대비 수정·확인 사항

- **8. 권장 기준 시나리오** — 원문 ‘스파 대실 594만원’은 `9실 × 2.2회 × 10만원 × 30일 = 5,940만원`의
  자릿수 오기로 보고 수정했습니다. 합계도 7,249만원 → **1억 2,595만원**(7장 ‘기준’ 시나리오와 일치).
- **9. 비용 및 투자계획** — 세부 항목 합계는 **3억 8,300만원**으로, 원문 합계(목표액) 3억 7,000만원과
  1,300만원 차이가 있습니다. 제안서에는 목표액 3.7억원을 유지하고 차이를 각주로 표기했습니다.
- 매출 시뮬레이션의 ‘스파 회전(환산)’ 1.5/2.2/3.0회는 스파 대실 매출 ÷ (9실 × 10만원 × 30일)로 역산한 값입니다.
- 부산 3대 권역(해운대·남포동·명지) 페이지와 고객 여정·포지셔닝 비교는 원문을 바탕으로 한 영업용 연출(안)입니다.
