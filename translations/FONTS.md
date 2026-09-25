# 종족별 대화 폰트 배정표

`fonts.ko.json`에서 용어집 ID와 폰트·출처를 연결합니다. 이 파일은 현재 설계/검토용이며 빌드가 자동으로 읽어 모든 종족에 적용하는 설정은 아닙니다.

## 공통 영역

- 오른쪽 목록과 초록색 로그: Galmuri7, 8px 렌더링 → 7px 글자.
- 플레이어 선택지: Galmuri9, 10px 렌더링 → 9px 글자(시험 적용).
- 원본 영문/기호는 보존하고 한국어 글리프만 추가합니다.

## 종족/대화별 배정

헤이스와 우르콴에만 한국어 자막 시험을 적용했습니다. 나머지는 **첫 가독성 시험용 후보**이며 최종 종족별 디자인이 아닙니다.
Galmuri11 후보는 원본 글꼴 PNG 최대 높이가 14px 이상인 경우에만 제안했습니다. 이 높이는 투명 여백을 포함하므로 실제 표시 공간을 보장하지 않습니다.
같은 후보를 배정한 종족도 독립 리소스로 유지해 이후 개별 교체할 수 있게 합니다.

| 대화 ID | 용어집 표기(잠정 포함) | 한국어 현재 적용 | 다음 시험 후보 | 상태 |
|---|---|---|---|---|
| arilou | 아릴루 | 미적용 | Galmuri9 | 제안 |
| chmmr | 촘르 | 미적용 | Galmuri9 | 제안 |
| commander | 헤이스 | Galmuri9 | Galmuri9 | 시험 적용 |
| druuge | 드루지 | 미적용 | Galmuri9 | 제안 |
| ilwrath | 일라스 | 미적용 | Galmuri9 | 제안 |
| kohrah | 코르아 | 미적용 | Galmuri11 | 제안 |
| melnorme | 멜노름 | 미적용 | Galmuri9 | 제안 |
| mycon | 마이콘 | 미적용 | Galmuri9 | 제안 |
| orz | 오르즈 | 미적용 | Galmuri9 | 제안 |
| pkunk | 프쿤크 | 미적용 | Galmuri9 | 제안 |
| probe | 슬라이랜드로 탐사선 / 슬라이랜드로 | 미적용 | Galmuri9 | 제안 |
| safeones | 스파시 | 미적용 | Galmuri9 | 제안 |
| shofixti | 쇼픽스티 | 미적용 | Galmuri9 | 제안 |
| slylandro | 슬라이랜드로 | 미적용 | Galmuri9 | 제안 |
| spathi | 스파시 | 미적용 | Galmuri11 | 제안 |
| starbase | 헤이스 | 미적용 | Galmuri9 | 제안 |
| supox | 수폭스 | 미적용 | Galmuri9 | 제안 |
| syreen | 시린 | 미적용 | Galmuri11 | 제안 |
| talkingpet | 말하는 애완동물 | 미적용 | Galmuri9 | 제안 |
| thraddash | 스래대시 | 미적용 | Galmuri9 | 제안 |
| umgah | 움가 | 미적용 | Galmuri9 | 제안 |
| urquan | 우르콴 / 크저자 | Galmuri9 | Galmuri9 | 시험 적용 |
| utwig | 우트위그 | 미적용 | Galmuri11 | 제안 |
| vux | VUX | 미적용 | Galmuri9 | 제안 |
| yehat | 예하트 | 미적용 | Galmuri9 | 제안 |
| yehat.rebel | 예하트 | 미적용 | Galmuri9 | 제안 |
| zoqfotpik | 조크-포트-피크 | 미적용 | Galmuri9 | 제안 |

## 확정 절차

1. 용어집의 종족 ID와 원본 대화/글꼴 리소스를 확인합니다.
2. 대표 자막·긴 자막·로그·선택지에서 가독성, 누락, 폭, 줄 간격을 확인합니다.
3. 가독성 확인 후 종족별 원작 분위기를 비교해 최종 서체를 선택합니다. 굵게 하거나 기울이는 변형도 작은 크기에서는 반드시 실기 검증합니다.
4. 새 서체를 도입하면 THIRD_PARTY.md, 라이선스, 파일 해시와 fonts.ko.json을 함께 갱신합니다.
5. 실제 패치에 적용한 후 current_korean_font/status를 갱신합니다. 제안만으로 적용 완료나 승인 완료로 표시하지 않습니다.

safeones/starbase/yehat.rebel은 설치 데이터에 독립 폰트 선언이 없습니다. 후보를 바로 적용하지 않고 공유 관계를 먼저 확인합니다.
게임에 직접 대화 리소스가 없는 용어(예: 선구자)는 별도 폰트 배정 대상에 자동 포함하지 않습니다.

[용어집](GLOSSARY.md) · [폰트 출처](../THIRD_PARTY.md) · [기계 판독 배정표](fonts.ko.json)
