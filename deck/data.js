/* Business data transcribed from 「프리미엄 프라이빗 커플 스파 사업계획서 ㈜C&C
   (수정 가격정책 및 매출모델 반영본)」. Units: 원 for prices, 만원 for monthly figures.
   Two arithmetic fixes vs. the source are marked FIX below. */

window.PLAN = {
  prices2p: [
    { name: "프라이빗 스파 대실", basis: "2인 · 3시간", min: 100000, max: 100000, role: "고객 유입용 핵심 상품", tag: "진입" },
    { name: "스파 + 스킨케어", basis: "2인", min: 150000, max: 150000, role: "가장 대중적인 주력 패키지", tag: "대표", hero: true },
    { name: "스파 + 바디케어", basis: "2인", min: 190000, max: 190000, role: "체류시간·만족도 강화", tag: "결합" },
    { name: "스파 + 스킨 + 바디케어", basis: "2인", min: 230000, max: 250000, role: "주력 업셀 상품", tag: "업셀" },
    { name: "프리미엄 커플 패키지", basis: "2인", min: 290000, max: 330000, role: "기념일·데이트 수요", tag: "VIP" },
    { name: "6F 프라이빗 풀 패키지", basis: "최대 4인", min: 250000, max: 350000, role: "VIP·기념일", tag: "VIP" }
  ],
  prices1p: [
    { name: "스킨케어 단독", basis: "1인", min: 90000, max: 120000, role: "비숙박/비스파 고객 유입" },
    { name: "바디케어", basis: "1인", min: 90000, max: 180000, role: "5F 부가매출" },
    { name: "다이어트 케어", basis: "1인", min: 120000, max: 180000, role: "스파 고객 업셀" }
  ],
  membership: { name: "다이어트 프로그램", basis: "회원권", min: 550000, max: 1200000, role: "반복매출·회원 라인" },

  // 월 매출 시뮬레이션 (만원)
  scenarios: [
    { name: "보수적", spa: 4050, spaSkin: 900, body: 960, skin: 600, diet: 540, total: 7050 },
    { name: "기준", spa: 5940, spaSkin: 1800, body: 2160, skin: 1320, diet: 1375, total: 12595 },
    { name: "공격적", spa: 8100, spaSkin: 3570, body: 3600, skin: 2730, diet: 2600, total: 20600 }
  ],
  lines: [
    { key: "spa", name: "스파 대실" },
    { key: "spaSkin", name: "스파+스킨" },
    { key: "body", name: "바디케어" },
    { key: "skin", name: "스킨케어" },
    { key: "diet", name: "다이어트" }
  ],
  bep: { min: 6500, max: 7000 },

  // 권장 기준 시나리오 산출 근거 (만원)
  // FIX: 원문 '스파 대실 594만원'은 9실×2.2회×10만원×30일 = 5,940만원의 자릿수 오기,
  //      합계 7,249만원 → 12,595만원 (7장 '기준' 시나리오와 일치)
  baseCase: [
    { name: "스파 대실", formula: "9실 × 2.2회/일 × 10만원 × 30일", value: 5940 },
    { name: "스파 + 스킨케어", formula: "4팀/일 × 15만원 × 30일", value: 1800 },
    { name: "바디케어", formula: "4건/일 × 18만원 × 30일", value: 2160 },
    { name: "스킨케어", formula: "4건/일 × 11만원 × 30일", value: 1320 },
    { name: "다이어트", formula: "월 25명 × 55만원", value: 1375 }
  ],
  roadmap: [
    { stage: "초기", target: "월 7,000만원 이상", lo: 7000, hi: 7000 },
    { stage: "안정화", target: "월 1억원", lo: 10000, hi: 10000 },
    { stage: "브랜드 정착", target: "월 1.2~1.5억원", lo: 12000, hi: 15000 }
  ],

  // 공사 목표 예산 (만원, VAT 별도)
  // FIX(확인 필요): 원문 합계 37,000 / 세부 항목 합 38,300 (차이 1,300)
  capex: [
    { name: "설계·현장관리", v: 1900 },
    { name: "철거·폐기물", v: 1200 },
    { name: "경량벽체·방음·도어", v: 2800 },
    { name: "바닥·벽·천장 마감", v: 3800 },
    { name: "습식·방수·타일", v: 2000 },
    { name: "급배수·펌프", v: 2500 },
    { name: "전기·조명·제어", v: 2200 },
    { name: "환기·제습·냉난방", v: 2000 },
    { name: "2인 욕조 6실", v: 1800 },
    { name: "샤워 6실", v: 600 },
    { name: "핀란드식 사우나 6실", v: 3000 },
    { name: "유리 파티션", v: 1200 },
    { name: "가구·티존·집기", v: 1800 },
    { name: "5F 야외 데크·방수", v: 1500 },
    { name: "5F 바디케어실 3실", v: 1500 },
    { name: "3F 리셉션·상담", v: 1200 },
    { name: "6F 4인 풀", v: 3500 },
    { name: "소방", v: 800 },
    { name: "사인·브랜딩", v: 500 },
    { name: "예비비", v: 2500 }
  ],
  capexTarget: 37000,

  // 월 고정·변동비 (만원)
  opex: [
    { name: "인건비", v: 1500, note: "운영·리셉션·바디케어·스킨케어 인력 포함 목표치" },
    { name: "임차료", v: 1000, note: "실제 임대조건에 따라 조정" },
    { name: "전기·수도·가스", v: 800, note: "욕조·사우나·제습·풀로 일반 매장보다 높게 설정" },
    { name: "마케팅·플랫폼", v: 500, note: "최소 6개월 · 초기 고객 확보" },
    { name: "소모품·세탁", v: 400, note: "타월·어메니티·스킨케어 등" },
    { name: "수선·기타", v: 300, note: "시설 유지관리" }
  ],

  kpis: [
    { name: "스파 객실 평균 회전", init: "1.5~2.0회/일", stable: "2.2~2.5회/일" },
    { name: "팀당 평균 객단가", init: "120,000원 이상", stable: "160,000~220,000원" },
    { name: "스파 → 스킨케어 전환", init: "20% 이상", stable: "30~40%" },
    { name: "바디케어/다이어트 케어 추가율", init: "10% 이상", stable: "20~30%" },
    { name: "재방문율", init: "15% 이상", stable: "25% 이상" },
    { name: "월 매출", init: "7,000만원", stable: "1억원+" }
  ],

  schedule: [
    { step: "1단계", dur: "1~2주", lo: 1, hi: 2, task: "사업성 확정, 임대조건, 구조·전기·급배수 조사" },
    { step: "2단계", dur: "2~3주", lo: 2, hi: 3, task: "디자인·견적·BOQ 확정 및 시공사 선정" },
    { step: "3단계", dur: "4~8주", lo: 4, hi: 8, task: "철거·설비·방수·전기·인테리어 공사" },
    { step: "4단계", dur: "2주", lo: 2, hi: 2, task: "가구·장비 설치, 테스트, 직원 교육" },
    { step: "5단계", dur: "1주", lo: 1, hi: 1, task: "촬영·온라인 등록·사전예약·소프트오픈" }
  ]
};

/* Photo slots. Each slot is filled by assets/images/<slot>.(jpg|png|webp) when present;
   otherwise it falls back to a procedural atmosphere image and shows a tag describing
   the intended shot. `pos` is the CSS object-position focal point. */
window.SLOTS = {
  cover:          { fb: "atmos_haeundae_dusk",   pos: "60% 50%", brief: "해운대 루프탑 야외 스파 · 커플 모델 · 야경(광안대교/마린시티)" },
  concept:        { fb: "atmos_sauna_warm",      pos: "50% 50%", brief: "4F 실내 프라이빗 스파룸 · 2인 욕조 · 커플 모델" },
  loc_haeundae:   { fb: "atmos_haeundae_dusk",   pos: "70% 50%", brief: "해운대 해변·마린시티 배경 · 커플 모델" },
  loc_nampo:      { fb: "atmos_nampo_night",     pos: "50% 50%", brief: "남포동 야경(부산타워·영도대교) 배경 · 커플 모델" },
  loc_myeongji:   { fb: "atmos_myeongji_sunset", pos: "62% 50%", brief: "명지 낙동강 하구 노을·갈대 배경 · 커플 모델" },
  floor4_spa:     { fb: "atmos_sauna_warm",      pos: "50% 50%", brief: "4F 스파룸 · 2인 욕조 + 샤워 + 유리 파티션 · 커플" },
  floor4_sauna:   { fb: "atmos_sauna_warm",      pos: "50% 50%", brief: "핀란드식 사우나 · 커플" },
  floor4_tea:     { fb: "atmos_city_bokeh",      pos: "50% 50%", brief: "티/리프레시 존 · 가운 차림 커플" },
  floor5_outdoor: { fb: "atmos_myeongji_sunset", pos: "55% 50%", brief: "5F 야외 스파 + 테라스 티존 · 노을 · 커플" },
  floor5_body:    { fb: "atmos_sauna_warm",      pos: "50% 50%", brief: "5F 바디케어실 · 여성 모델 관리 장면" },
  floor6_pool:    { fb: "atmos_pool_dusk",       pos: "50% 50%", brief: "6F 4인 프라이빗 풀 + 테라스 · 야경 · 모델 3~4인" },
  reception:      { fb: "atmos_city_bokeh",      pos: "50% 50%", brief: "3F 리셉션·상담 라운지 · 스태프와 커플" },
  skincare:       { fb: "atmos_sauna_warm",      pos: "50% 50%", brief: "스킨케어 · 여성 2인 모델" },
  anniversary:    { fb: "atmos_city_bokeh",      pos: "50% 50%", brief: "기념일 연출 · 꽃·케이크·무알코올 스파클링" },
  diet:           { fb: "atmos_pool_dusk",       pos: "50% 50%", brief: "바디 리셋 프로그램 상담 · 모델" },
  sns:            { fb: "atmos_nampo_night",     pos: "50% 50%", brief: "스파에서 사진 찍는 커플 (SNS 숏폼용)" },
  closing:        { fb: "atmos_nampo_night",     pos: "50% 50%", brief: "테라스 야경 · 커플 뒷모습" }
};
