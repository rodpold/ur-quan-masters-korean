# Ur-Quan Masters Korean Patcher

Steam판 Free Stars: The Ur-Quan Masters 0.8.0의 한국어 패치 개발판입니다.
완성된 전체 한글 패치가 아닙니다. 게임 실행 파일은 수정하지 않습니다.

## 준비 / 실행

Python 3.11 이상이 필요합니다. Windows에서 게임을 종료한 다음 실행하세요.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
$game = 'C:\Program Files (x86)\Steam\steamapps\common\Free Stars The Ur-Quan Masters'
.\.venv\Scripts\python patcher.py inspect --game "$game"
.\.venv\Scripts\python patcher.py install --game "$game"
.\.venv\Scripts\python patcher.py launch --game "$game"
```

설치 폴더의 쓰기 권한이 필요합니다. 별도 테스트 설정/세이브를 쓰려면 launch에
`--test-config artifacts/test-profile`을 추가하세요. 일반 launch는 원래 사용자 설정을 사용합니다.
`install`은 전용 애드온 폴더만 추가하며, Steam 실행 옵션은 자동 변경하지 않습니다.
Steam으로 실행하려면 게임 속성의 실행 옵션에 `--addon uqm-korean-ui-poc --menu pc --font 3do --scale none`를 추가하세요.
런처도 같은 옵션을 사용합니다. 목록 메뉴·단색 글자·픽셀 확대를 선택해 작은 한글의 대비를 확보합니다.
음악·음성·효과음 크기는 변경하지 않습니다.

```powershell
.\.venv\Scripts\python patcher.py status --game "$game"
.\.venv\Scripts\python patcher.py uninstall --game "$game"
```

제거는 이 도구가 설치한 두 파일만 삭제하며 원본은 그대로입니다.
패치 파일이 사용자가 수정한 상태이거나 추가 파일이 있으면 제거를 거부합니다.
Steam 실행 옵션을 직접 추가했다면 제거 후 해당 옵션도 지우세요.

## 현재 범위

- 27개 대화 파일의 3,451개 레코드 번역 초안과 24종 독립 종족 글꼴
- 설정 121개, 공통 문자열 581개 번역 / 13개 보존
- 행성 보고 29개, 소개 32개·최종 엔딩 42개 자막 초안
- 함선 종족/함종 표기 125개와 함장 이름 371개 번역 / 코드 이름 32개 보존
- 메뉴·조선소·장비·궤도 진입·착륙정 등의 그림 문구 교체
- 원본 데이터 SHA-256 확인, 독립 애드온 설치·업데이트·상태 확인·제거

대화 초안의 기록 수가 100%라고 해서 게임 전체 번역이 완료된 것은 아닙니다. 의미·말투 교정,
실제 자막·음성 타이밍·선택지 스크롤, 남은 그림과 이름 입력 검증은 진행 중입니다.
작은 오른쪽 HUD의 CAPTAIN/FUEL/CREW와 일부 장식 문구는 아직 영문입니다.
3DO 그림 메뉴의 일부 라벨은 번역 자산이 연결되어 있으나 전체 실기 검증을 마치지 않았습니다.
한글 이름 입력은 아직 지원 확인되지 않았습니다.

시작 메뉴는 원작 그림 중앙을 어두운 패널로 덮어 한글을 표시합니다.
고정 8픽셀 줄 간격 UI에는 7픽셀 한글을 사용하며 글리프의 반투명은 사용하지 않습니다.
함장·함선의 실제 사용자 지정 이름과 숫자·좌표·원래 음성은 유지합니다.
현재 검증 범위는 [전체 목표](docs/LOCALIZATION_GOAL.md), [이미지 검토](docs/MEDIA_LOCALIZATION.md),
[설치 검증](docs/VERIFICATION.md)을 참조하세요.

## 9픽셀 공통 UI 시험 옵션

게임 종료 후 `python patcher.py install --game "$game" --ui-font larger`로 설치하고
기존 `launch` 명령으로 실행합니다. 공통 starcon 폰트의 한글만 7→9픽셀 높이로 바꿉니다.
9픽셀용 Galmuri9를 권장 크기 10px로 래스터화하며 글리프 폭도 8→10픽셀로 늘어납니다.
설정 화면은 제목 겹침을 피하도록 현재 페이지 제목 한 줄만 표시합니다.
설정 화면과 게임 목록 메뉴에 함께 영향을 주므로, 고정 8픽셀 줄에서 겹침이 생기는지 확인해야 합니다.
기본값은 기존 7픽셀이며 `install --ui-font compact`로 되돌릴 수 있습니다.
음량이나 개인 설정은 바꾸지 않습니다. `python tools/verify_build.py "$game" larger`로 패키지를 검사합니다.

## 개발

```powershell
python -m unittest discover -s tests -v
python tools/check_glossary.py
python tools/verify_build.py "$game"
python patcher.py build --game "$game" --output artifacts/ko-ui.uqm
```

`translations/setup.ko.json`은 설정 리소스 ID별 번역입니다. 선택지 개수와 빈 항목을 보존합니다.
`translations/ui.ko.json`은 원문 본문과 번역의 대응표입니다. 게임 문자열 헤더와
순서는 유지하며, 중복 원문은 모두 교체합니다. 새 번역에 필요한 글자는 자동 생성됩니다.
현재 실험은 확인된 Steam 데이터 해시만 허용합니다. 다른 버전 지원은 원본 리소스 비교 후 추가하세요.

## 공개 저장소 / 라이선스

프로그램의 기본 라이선스는 MIT이며, 원본 렌더링을 참고한 일부 검사 도구에는 별도 GPL 조건이 있습니다.
동봉한 24종 종족 폰트와 공통 폰트의 라이선스·저자·출처는 `THIRD_PARTY.md` 및 각 vendor 폴더를 확인하세요.
원본 게임 파일, 로컬 생성 패키지, 세이브, 실행 로그를 저장소에 올리지 않습니다.
빌드 시 사용자의 설치본에서 필요한 원본 데이터를 읽습니다. 생성 패키지는 원작 데이터를
포함하므로 공개 릴리스에 무심코 첨부하지 마세요. 별도의 원작 라이선스 검토가 필요합니다.

## 다음 단계

[검증 현황](docs/VERIFICATION.md)을 참조하세요.
실기 검증 완료 → Steam 경로 자동 탐색 → GUI → 실행 파일 패키징.
현재는 개발판이며, 검증하지 않은 항목을 완료로 표시하지 않습니다.

## 번역 표기와 출처 관리

고유명사는 [용어집](translations/GLOSSARY.md)과 [독립 JSON](translations/glossary.ko.json)에서 관리합니다.
종족명 초안은 proposed이며 확정 표기가 아닙니다. 기존 UI 표기와 연결한 항목은 검사 도구로 검증합니다.
폰트별 공식 다운로드·권장 크기·라이선스는 [출처](THIRD_PARTY.md)에 기록합니다.
새 외부 자료를 사용할 때는 출처와 라이선스 기록을 같은 변경에 포함해야 합니다.

## 현재 교신 번역과 종족 글꼴

`install --ui-font compact`로 오른쪽 목록/로그는 7픽셀, 플레이어 선택지는
Galmuri9 9픽셀로 구성합니다. 종족 자막은 24개 독립 폰트 파일을 27개 대화에 연결합니다.
같은 종족의 별도 대화만 글꼴을 공유하며, 한글은 모두 흑백 픽셀로 생성합니다.
[배정표](translations/FONTS.md), [표본 1](docs/binary-race-fonts-1.png), [표본 2](docs/binary-race-fonts-2.png)를 참조하세요.
원본 영문 비교는 `tools/review_binary_fonts.py --game "게임 경로"`로 로컬 생성합니다.

현재 탐사선 86개, 헤이스 초반 대화 99개, 우주기지 300개, 스파시 134개, 스파시와 지도부 145개, 아릴루 97개, 우르콴 76개, 코르아 76개, 촘르 78개, 일라스 108개, 수폭스 97개, 쇼픽스티 95개, 움가 87개, VUX 102개, 예하트 75개, 예하트 반란군 34개, 드루지 105개, 슬라이랜드로 116개, 마이콘 109개, 우트위그 117개, 오르즈 116개, 시린 131개, 말하는 애완동물 113개, 프쿤크 182개, 스래대시 154개, 멜노름 282/282개, 조크-포트-피크 337/337개를 초안 번역했습니다.
행성 탐사 보고는 별도로 29/29개를 초안 번역했습니다. `translations/reports.ko.json`에서 원본 경로와 레코드 ID별로 관리합니다. 전용 폰트와 두 칸 배치 방식으로 시험 설치했으며, 실제 화면 검토는 대기 중입니다. [표시 방식](docs/REPORT_LAYOUT.md).

총 3451 / 3451 대화 레코드의 초안을 작성했습니다. 대화 외 텍스트에는 미번역 항목이 남아 있습니다. 번역 진척은 대화 레코드 기준이고 게임 전체 완료율이 아닙니다.
함장/함선 이름 삽입과 원래 음성/타임스탬프 경로를 보존합니다.
사용자가 저장한 테스트 프로필로 같은 지점에서 교신을 재현할 수 있습니다.
대화 도중 설치하지 말고 게임 종료 후 설치/재실행하세요.
실제 자막 타이밍, 긴 어절 줄바꿈 및 선택지 스크롤은 실기 확인 대상입니다.

## 전체 번역 진행

전체 번역 목표를 진행 중입니다. 24종 종족 폰트는 실제 빌드에 연결됐으며, 대화 3,451개 레코드의 번역 초안을 작성했습니다. 의미·말투·실기 검토와 나머지 비대화 텍스트 번역은 진행 중입니다. [진행률과 완료 기준](docs/LOCALIZATION_GOAL.md), [페르소나](translations/PERSONAS.md), [용어집](translations/GLOSSARY.md)을 기준으로 작업합니다. `tools/check_localization.py --game "게임 경로" --write-report`로 누락을 추적합니다.

보고서 정적 시뮬레이터 `tools/check_report_layout.py`에는 별도 GPL-2.0-or-later 라이선스가 적용됩니다. [출처와 라이선스](THIRD_PARTY.md#report-font-and-rendering-audit)를 참조하세요.

대화 외 텍스트는 [구조별 목록](docs/TEXT_INVENTORY.md)에서 추적한다. 소개/최종 엔딩 자막 74개, 위치 지정 문구 12개, 크레딧 블록 55개를 연출 명령과 분리했다. 아직 번역 완료가 아니며 이미지 내 텍스트·애드온 판본은 별도 조사 대상이다.

PC 소개 슬라이드 자막 32개 초안을 패키지에 연결했습니다. 원문 타이밍은 유지하며 실제 재생·음성/음악 시점 검토는 남아 있습니다. 3DO 영상 소개와 영상 내 글자는 별도 범위입니다.

최종 엔딩 슬라이드 자막 42개도 번역 초안을 연결했습니다. 함장의 회고·손주·노년 함장 말투를 구분했으며 실제 엔딩 재생 검토는 남아 있습니다.

기지·조우 결과·행성 수치·통신 대전 안내 번역을 추가했습니다. 공통 문자열의 남은 항목은 [UI 진행 기록](docs/ui-progress.json)에서 추적합니다.


## 개발판 소스 ZIP

커밋된 작업 트리에서 `python tools/build_source_release.py`를 실행하면
`artifacts/uqm-korean-development-source.zip`을 만듭니다. 아직 Python이 필요한 소스 배포이며
독립 실행형 EXE가 아닙니다. ZIP에는 폰트·라이선스·번역·실행 코드와 파일별 SHA-256 목록을 포함하고,
게임 원본·생성 패치·세이브·개발용 미리보기 PNG는 포함하지 않습니다.
미리보기 이미지는 [GitHub 저장소](https://github.com/rodpold/ur-quan-masters-korean)에서 볼 수 있습니다.

다른 폴더에 압축을 풀고 해당 폴더에서 위의 가상환경 생성·의존성 설치·inspect/install 순서로 실행하세요.
업데이트도 게임을 종료한 뒤 같은 `install` 명령을 사용합니다. 동일 빌드는 설치 파일을 다시 쓰지 않습니다.
제거 중 파일 잠금 오류가 나면 삭제된 패치 파일을 복구한 뒤 오류를 반환합니다.
지속적인 쓰기 거부나 전원 차단 복구까지 검증한 것은 아닙니다.


## 현재 파일 기준 의미 검수 기록

`python tools/check_review_coverage.py --game "게임 경로" --write-report`는 원문·번역 파일의 SHA-256과 검토한 레코드 ID를 대조해 [검수 집계](docs/review-coverage.json)를 갱신합니다. 파일이 바뀐 검수 기록과 잘못된 ID는 집계에서 제외하고 오류로 알립니다. 중복 기록은 한 번만 셉니다.

현재 정식 에이전트 의미 검수 기록은 기본 대사 1437/3451개, 음성판 별도 번역 6/15개, 소개·엔딩 자막 74/74개입니다. 이 수치는 현재 파일과 일치하는 검수 기록의 범위이며 번역 정확성, 사용자 승인 또는 게임 전체 완료율을 뜻하지 않습니다. UI·탐사 보고·크레딧·이미지 문구와 실제 게임 화면 검증은 별도로 추적합니다.
