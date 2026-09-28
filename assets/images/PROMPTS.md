# 사진 슬롯 & 이미지 생성 프롬프트

제안서(PDF)와 홍보영상은 아래 **17개 사진 슬롯**을 공유합니다. 파일을 `assets/images/<슬롯>.jpg`로
넣으면(`python3 tools/place_photos.py <이미지> <슬롯>`) PDF·영상에 자동 반영됩니다.
사진이 없는 슬롯은 절차적 분위기 이미지(`assets/atmos/`)로 임시 표시됩니다.

## 공통 가이드 (ChatGPT 이미지 생성용)

- **비율**: 가로형 16:9 (ChatGPT에서는 1536×1024 가로형으로 생성 → 자동 크롭)
- **모델 일관성**: 첫 이미지에서 만든 커플을 이후 이미지에도 “같은 인물”로 유지하도록 요청
  - Model A — 20대 후반 한국 여성, 어깨 길이 다크브라운 헤어, 내추럴 메이크업
  - Model B — 30대 초반 한국 남성, 짧은 검정 머리, 깔끔한 인상
  - 복장: 흰색 와플 스파 가운 / 물속 장면은 단정한 어두운 수영복
- **공통 스타일 문구**(각 프롬프트 끝에 붙이기):

```
Photorealistic editorial photograph, full-frame camera, 35mm lens, soft warm natural light,
shallow depth of field, realistic skin texture, calm luxurious mood, Korean models,
no text, no logo, no watermark, wide 16:9 landscape.
```

- **표기**: 준공 전 사업이므로 PDF·영상에는 “공간·인물 이미지는 연출용 컨셉 이미지”라는 문구가 들어갑니다.

## 슬롯별 프롬프트

| 슬롯 | 쓰이는 곳 | 구도 메모 |
|---|---|---|
| `cover` | 표지·클로징, 영상 오프닝 | 인물은 오른쪽 1/3, 왼쪽은 어두운 여백(제목 자리) |
| `concept` | 사업 개요(세로 크롭), 영상 컨셉 | 인물 중앙 |
| `loc_haeundae` · `loc_nampo` · `loc_myeongji` | 입지 컨셉 카드(세로 크롭), 영상 3분할 | 인물 중앙, 하단 1/3은 텍스트 자리 |
| `floor4_spa` | 4F 페이지 전면, 영상 4F | 인물 오른쪽, 왼쪽 1/3 여백 |
| `floor4_sauna` · `floor4_tea` | 4F 인셋 | 자유 |
| `floor5_outdoor` | 5F 페이지(왼쪽 대형), 영상 5F | 인물 중앙~오른쪽 |
| `floor5_body` | 5F 인셋, 고객 여정 | 자유 |
| `floor6_pool` | 6F 페이지 전면, 영상 6F | 인물 왼쪽 1/2 (오른쪽에 텍스트) |
| `reception` | 고객 여정, 영상 3F | 자유 |
| `skincare` · `diet` · `sns` · `anniversary` | 목표 고객·마케팅·고객 여정 카드 | 인물 중앙 |
| `closing` | 결론 페이지 배경, 영상 엔딩 | 상단 절반 여백 |

### cover — 해운대 루프탑 야외 스파
> A Korean couple (Model A and Model B) relaxing side by side in a round outdoor rooftop spa tub at blue hour in Haeundae, Busan. Behind them the illuminated Gwangan Bridge and the Marine City skyscrapers glow across the water. Gentle steam rises from the water, warm teak deck, soft lanterns. The couple sits in the right third of the frame, seen from a three-quarter back angle, faces partly visible. The left half is darker sky and sea, leaving space for a headline.

### concept — 4F 실내 프라이빗 스파룸
> Inside an indoor private couple spa room: a freestanding two-person stone bathtub, warm oak wall panels, indirect warm lighting, a glass-partitioned rain shower in the background. Model A and Model B sit in the tub, smiling softly and holding tea cups. Subjects centered so the image also works as a vertical crop.

### loc_haeundae — 해운대
> Model A and Model B stand on a hotel-style terrace in Haeundae, Busan at golden hour in light linen outfits, with Haeundae Beach and the Marine City towers behind them, sea breeze in their hair. Subjects centered, waist-up, generous sky, works as a vertical crop.

### loc_nampo — 남포동
> Model A and Model B on a rooftop terrace in Nampo-dong, Busan at night; Busan Tower on Yongdusan hill, the lit Yeongdo Bridge and harbor lights in the background, warm string lights, the couple laughing. Centered composition, works as a vertical crop.

### loc_myeongji — 명지
> Model A and Model B sitting at the edge of an outdoor spa terrace at sunset, overlooking the Nakdong River estuary near Myeongji, Busan: golden reed fields, tidal flats and calm water, distant high-rise apartments of Myeongji new town on the horizon, warm backlight. Centered, works as a vertical crop.

### floor4_spa — 4F 스파룸 전경
> Wide interior shot of a premium private spa suite for two: a two-person freestanding bathtub by the window, a glass-enclosed rain shower, the wooden door of a small Finnish sauna, and a low tea table with floor cushions. Warm stone and oak materials, indirect lighting. Model A and Model B in white robes on the right side of the frame; the left third stays calm and darker for text.

### floor4_sauna — 핀란드식 사우나
> Inside a small Finnish sauna with horizontal cedar benches and a stone heater, warm amber light, soft steam. Model A and Model B wrapped in white towels sit relaxed on the upper bench, eyes closed.

### floor4_tea — 티/리프레시 존
> A cozy tea and refresh corner inside the spa suite: a low wooden table with a ceramic tea set, herbal tea and fruit, soft cushions, a large window with city-light bokeh. Model A and Model B in white robes clink tea cups, candid moment.

### floor5_outdoor — 5F 야외 스파 + 테라스
> An open-air private spa on a fifth-floor terrace: a rectangular spa tub framed by wooden privacy screens and potted greenery, a terrace tea zone with two lounge chairs, sunset sky. Model A and Model B in the tub looking at the view, slightly right of center.

### floor5_body — 5F 바디케어실
> A calm body-care treatment room: Model A lies face-down on a treatment bed, covered with a white towel up to the shoulders, while a professional female therapist in a neutral uniform performs a back massage. Warm candlelight, clean minimal interior, tasteful and modest.

### floor6_pool — 6F 4인 프라이빗 풀
> A small rooftop private plunge pool for up to four people on the sixth floor with a wooden terrace at night and Busan city lights beyond. Two Korean couples (including Model A and Model B) in modest swimwear celebrate with glasses of non-alcoholic sparkling drink; a small cake sits on the deck. Joyful and elegant; people on the left half of the frame.

### reception — 3F 리셉션·상담
> A premium spa reception and consultation lounge: travertine counter, warm wood slats, soft indirect lighting, a small orchid. A Korean female receptionist in a neutral linen uniform welcomes Model A and Model B and shows package options on a tablet.

### skincare — 여성 2인 스킨케어
> Two Korean women friends in their late 20s lie side by side on treatment beds with white headbands, receiving facial skincare treatments from therapists. Serene soft light, clean modern spa room.

### anniversary — 기념일 연출
> Anniversary set-up beside a two-person spa bathtub: a bouquet of white and blush roses, a small celebration cake with candles, two glasses of non-alcoholic sparkling wine, rose petals and warm candlelight. The hands of Model A and Model B touch glasses in the foreground.

### diet — 바디 리셋 프로그램 상담
> A bright, clean body-reset consultation room: a female wellness coach reviews body-composition results on a tablet with Model A (in comfortable athleisure); a measuring tape and herbal tea on the desk. Positive, professional mood.

### sns — SNS 숏폼용 셀카
> Model A and Model B in white robes take a smiling selfie with a smartphone next to the spa bathtub. Warm light, playful candid moment, shallow depth of field.

### closing — 테라스 야경 엔딩
> Back view of Model A and Model B wrapped in white robes, standing on a rooftop terrace at night and looking out over the Busan night view with the lit Gwangan Bridge across the bay; gentle steam rises from an outdoor spa beside them. Plenty of dark sky in the upper half for text.
