# 음성판 대사와 번역

설치된 `uqm-0.8.0-voice.uqm`의 RMP를 읽어 실제 대사 원문과 음성/타임스탬프 경로를 사용한다. 기본 콘텐츠 대사로 음성판 대사를 무조건 대체하지 않는다. 실행 파일은 변경하지 않는다.

음성판에 별도 원문이 있는 종족: arilou, melnorme, mycon, starbase, syreen, utwig.
`translations/dialogue/*.ko.json`은 기본판 기준이고, 내용이 다른 음성판 레코드는 `translations/dialogue-voice/*.ko.json`에 별도로 검토한 번역을 둔다. 별도 파일이 없거나 해당 ID가 없으면 이미 번역된 다른 원문 레코드의 빌드를 거부한다. 아직 번역하지 않은 레코드는 설치된 원문 그대로 남긴다. 음성 패키지가 없으면 기본판 번역만 쓴다.

우주기지 차이는 `HEAVY_LOAD_D1`, `HEAVY_LOAD_E1`의 선행 쉼표뿐이다. 현재 두 판은 같은 한국어 번역을 사용한다. 인사/납품의 앞뒤 조각 사이에 음성 비사용 시 `SPACE`와 실제 함장 이름을 넣고, 음성 사용 시 이를 생략하는 원본 코드 구조를 고려했다. `STARBASE_IS_READY_*`, `ABOUT_CREW*`는 실제 함선 이름 또는 음성판의 기함 지칭이 삽입된다.

원작 연결 확인: [starbas.c](https://github.com/intgr/uqm-wasm/blob/main/sc2/src/uqm/comm/starbas/starbas.c). 설치된 원본 콘텐츠와 음성 패키지가 실제 데이터 기준이다. 원본 대사·음성 파일은 저장소에 복제하지 않는다.

자동 검사는 대사 ID/구간 수와 RMP 음성/타임스탬프 경로 보존, 미검토 판본 차이 차단을 확인한다. 자막이 실제 음성과 맞물리는 시점, 이름 삽입 후의 화면 배치와 문법은 별도의 실기 검토 대상이다.

아릴루 `BAD_NEWS_ABOUT_TPET` 첫 구간은 일반판의 psychically coercive와 음성판 자막 원문의 physically coercive가 다르다. 각각 정신적 강제력/물리적 강제력으로 번역해 판본 차이를 유지한다. 실제 녹음과의 일치는 별도 청취 검토 대상이다.
