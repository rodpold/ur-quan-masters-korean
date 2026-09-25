# Ur-Quan Masters Korean Patcher

Steam판 Free Stars: The Ur-Quan Masters 0.8.0의 공통 UI 한글 패치 0.1 개발판입니다.
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
python patcher.py status --game "$game"
python patcher.py uninstall --game "$game"
```

제거는 이 도구가 설치한 두 파일만 삭제하며 원본은 그대로입니다.
패치 파일이 사용자가 수정한 상태이거나 추가 파일이 있으면 제거를 거부합니다.
Steam 실행 옵션을 직접 추가했다면 제거 후 해당 옵션도 지우세요.

## 현재 범위

- 시작 메뉴 5개: 새 게임 / 불러오기 / 함대 대전 / 설정 / 종료
- 함장, 연료, 승무원, 태양, 월 이름
- PC 목록 메뉴: 성도 / 함선 정보 / 게임 / 항해 및 하위 메뉴
- 설정 화면의 항목·선택지·설명문 121개 리소스
- 공통 문자열 115곳과 저장/불러오기 화면의 이미지 문구
- 원본 폰트에 번역에 필요한 한글 음절 PNG만 추가
- 원본 데이터 SHA-256 확인, 독립 애드온 설치, 상태 확인, 제거

시작 화면의 영문은 배경 그림에 합쳐져 있습니다. 이번 시제품은 메뉴 중앙을
어두운 패널로 덮어 한글을 표시합니다. 원작 배경 복원/최종 아트 작업은 후속 과제입니다.
3DO 아이콘 메뉴의 영문, 종족 대사와 한글 이름 입력은 범위 밖입니다.
원본 메뉴의 줄 간격이 8픽셀이므로 작은 UI의 한글 가독성에는 한계가 있습니다.
정보용 micro 폰트는 11픽셀 한글을 사용하며, 고정 간격 UI는 7픽셀을 유지합니다.
함장과 함선의 고유 이름 및 숫자/좌표는 유지합니다.

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

프로그램 코드는 MIT, 동봉한 갈무리 폰트는 SIL OFL 1.1입니다.
`vendor/galmuri/OFL.txt`, `THIRD_PARTY.md`를 확인하세요.
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

현재 탐사선 86개, 헤이스 초반 대화 99개, 우주기지 300개, 스파시 134개, 우르콴 경고 방송 1개를 초안 번역했습니다.
총 620 / 3451 대화 레코드이며, 나머지는 영문입니다. 번역 진척은 대화 레코드 기준이고 게임 전체 완료율이 아닙니다.
함장/함선 이름 삽입과 원래 음성/타임스탬프 경로를 보존합니다.
사용자가 저장한 테스트 프로필로 같은 지점에서 교신을 재현할 수 있습니다.
대화 도중 설치하지 말고 게임 종료 후 설치/재실행하세요.
실제 자막 타이밍, 긴 어절 줄바꿈 및 선택지 스크롤은 실기 확인 대상입니다.

## 전체 번역 진행

전체 번역 목표를 진행 중입니다. 24종 종족 폰트는 실제 빌드에 연결됐으며, 모든 대사가 번역된 것은 아닙니다. [진행률과 완료 기준](docs/LOCALIZATION_GOAL.md), [페르소나](translations/PERSONAS.md), [용어집](translations/GLOSSARY.md)을 기준으로 작업합니다. `tools/check_localization.py --game "게임 경로" --write-report`로 누락을 추적합니다.
