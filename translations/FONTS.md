# 종족별 대화 폰트 선정안

2026-09-25: 종족별 **디자인 방향을 선정**했습니다. 게임 적용 완료나 사용자 승인 확정을 뜻하지 않습니다.
실제 적용은 헤이스/우르콴 Galmuri9 시험판 그대로이며, 이번 변경은 선정표·비교 자료입니다.
fonts.ko.json의 selected_font는 다음 적용 대상, current_korean_font는 현재 적용 상태입니다. 빌드는 아직 배정표를 자동 소비하지 않습니다.

## 선택 기준

설치 데이터에서 종족별 원본 영문 글리프를 비교하고, 아래 네 계열로 한글의 차이를 줍니다.
서로 다른 서체를 27개 억지로 배정하기보다 같은 계열 안에서 원작 색상·배치를 유지합니다.
11픽셀 글자는 12px, 9픽셀 글자는 10px로 렌더링합니다. 임의 축소나 가짜 굵기/기울임을 사용하지 않습니다.

![선정 글꼴 비교 — 게임 화면이 아닌 3배 최근접 확대 표본](../docs/font-selection.png)

| 계열 | 선정 이유 |
|---|---|
| Galmuri9 | 소형: 짧은 자막 영역과 촘촘한 문장의 가독성을 우선한다. |
| Galmuri11-Bold | 굵은형: 원작의 두꺼운 획/강한 존재감을 한글의 굵기로 옮긴다. |
| Galmuri11-Condensed | 좁은형: 가는 인상과 독특한 리듬을 폭의 차이로 표현한다. |
| Galmuri11 | 기본형: 넉넉한 한글 내부 공간과 안정적인 문장 가독성을 사용한다. |

## 종족/대화별 결정

이름은 용어집의 잠정 표기를 포함합니다. 공유 관계 미확인 항목은 적용 시 소스 확인이 필요합니다.

| 대화 ID | 용어집 표기 | 선정 글꼴 | 현재 적용 |
|---|---|---|---|
| arilou | 아릴루 | Galmuri11-Condensed | 미적용 |
| chmmr | 촘르 | Galmuri11-Bold | 미적용 |
| commander | 헤이스 | Galmuri9 | Galmuri9 |
| druuge | 드루지 | Galmuri11-Bold | 미적용 |
| ilwrath | 일라스 | Galmuri11 | 미적용 |
| kohrah | 코르아 | Galmuri11-Bold | 미적용 |
| melnorme | 멜노름 | Galmuri9 | 미적용 |
| mycon | 마이콘 | Galmuri11 | 미적용 |
| orz | 오르즈 | Galmuri11 | 미적용 |
| pkunk | 프쿤크 | Galmuri11-Condensed | 미적용 |
| probe | 슬라이랜드로 탐사선 / 슬라이랜드로 | Galmuri9 | 미적용 |
| safeones | 스파시 | Galmuri11 | 미적용 |
| shofixti | 쇼픽스티 | Galmuri11-Condensed | 미적용 |
| slylandro | 슬라이랜드로 | Galmuri11 | 미적용 |
| spathi | 스파시 | Galmuri11 | 미적용 |
| starbase | 헤이스 | Galmuri9 | 미적용 |
| supox | 수폭스 | Galmuri11-Condensed | 미적용 |
| syreen | 시린 | Galmuri11 | 미적용 |
| talkingpet | 말하는 애완동물 | Galmuri11-Bold | 미적용 |
| thraddash | 스래대시 | Galmuri11-Bold | 미적용 |
| umgah | 움가 | Galmuri9 | 미적용 |
| urquan | 우르콴 / 크저자 | Galmuri11-Bold | Galmuri9 |
| utwig | 우트위그 | Galmuri11-Condensed | 미적용 |
| vux | VUX | Galmuri11-Condensed | 미적용 |
| yehat | 예하트 | Galmuri11 | 미적용 |
| yehat.rebel | 예하트 | Galmuri11 | 미적용 |
| zoqfotpik | 조크-포트-피크 | Galmuri11-Condensed | 미적용 |

## 공간과 적용 기준

- 오른쪽 메뉴·초록색 로그는 Galmuri7 유지, 플레이어 선택지는 Galmuri9 유지.
- 우르콴은 현재 Galmuri9에서 Galmuri11-Bold로 바꾸는 것이 다음 목표다. 현재 설치본은 변경하지 않았다.
- 11픽셀 표본의 획은 선명하지만 자막 높이와 영어 이름의 기준선은 실제 화면에서 확인해야 한다.
- 폭/높이 초과가 생기면 번역 길이와 발화 구간을 먼저 검토한다. 그래도 맞지 않으면 해당 종족만 Galmuri9로 명시적으로 재선정한다. 축소하지 않는다.
- safeones/starbase/yehat.rebel은 독립 FONTRES 선언이 없어 공유 관계 확인 후 적용한다.
- 외부 후보 Neo둥근모도 검토했으나 이번 소형 자막 선정에는 포함하지 않았다. 추가 서체가 필요하면 별도 원본 크기 표본과 공간 검증부터 한다.

## 검증 상태

- 표본 및 현재 시험 번역에 쓰인 글리프의 존재 여부 확인.
- 새 Bold/Condensed 파일 해시·라이선스·용어집 연결 검증.
- 종족별 실제 자막 폭, 줄 수, 음성 타이밍과 기준선 검증은 적용 단계에서 진행.

출처: [Galmuri 공식 배포](https://github.com/quiple/galmuri), [OFL 안내](https://quiple.dev/font/galmuri).
[용어집](GLOSSARY.md) · [상세 출처](../THIRD_PARTY.md) · [배정 JSON](fonts.ko.json)
