# 이미지·미디어 번역 추적

`tools/inventory_media.py --game "게임 경로" --write-report`는 설치 패키지와 UI PNG의 원본 해시·크기·ANI 프레임·RMP 연결을 기록한다. `media-inventory.json`은 리소스 연결 근거이며 런타임 접근 가능성을 증명하지 않는다. 애드온에 같은 경로의 사본이 있어도 번역된 이미지라는 뜻이 아니다.

기본 UI PNG 420개 모두에 대해 초기 접촉 시트 육안 검토를 마쳤다. `ui-image-review.json`에 이미지별 상태를 기록한다. 이는 번역 완료/실기 통과가 아니며 초기 확인한 121개 중 24개는 한글 패널을 생성했으며, 97개는 번역 적용 대기다. 일부 작은 버튼 안내는 별도 확대 검토가 필요하다. 게임 그림은 Git에 넣지 않는다.

확인한 잔여 대상:

- activity: GAME PAUSED, TO QUIT PRESS B.
- flagshipstatus: CAPTAIN, FUEL, CREW. 사용자 요청에 따라 크기 때문에 영문으로 돌아간 HUD도 전체 번역 검토 대상으로 남긴다.
- meleemenu: SUPER-MELEE, HUMAN CONTROL, 세 CYBORG 등급, LOAD/SAVE/QUIT, BATTLE, PICK SHIP/SHIP INFO와 작은 조작 안내.
- modulesmenu: 착륙선·추진기·선실·연료 탱크·무장 등의 그림 내 이름 14개와 BUY/SELL.
- netplay: NETWORK CONTROL과 NET 상태 라벨.
- playmenu: SCAN 등 그림 메뉴 0–37, 장치 그림의 AMPLIFIED PRECURSOR BOMB/ESCAPE POD, NO LIMIT, QUIT. 38–57의 숫자는 보존한다. 60–63 일반 버전은 기존 교체 대상이나 SAFEX=16 변형은 별도 연결 확인이 필요하다.
- shipyard: 3–23의 종족/함종 이름과 일부 약칭. 지난 함선 텍스트 번역만으로 이 그림은 바뀌지 않는다.

설치된 기본/음성/3DO 음악 패키지와 게임 폴더에서는 `.mle`가 발견되지 않았다. 사용자 설정 폴더의 팀은 조사하지 않았으므로 “기본 팀 파일이 어디에도 없다”는 결론은 아니다. 기본 팀 구성의 생성 코드를 계속 조사한다.

현재 세 패키지 안에는 DUK/AVI/MP4 등 조사한 영상 확장자가 없다. 그러나 기본 패키지의 LPF 2개, PNG 기반 소개/승리/엔딩 애니메이션, 통신 배경과 함선 그림은 이 결론에서 제외되며 글자 검토가 남아 있다. 별도 영상 팩은 미설치 상태이며 범위가 추가되면 재조사한다.

다음 구현은 텍스트 배치만 치환하고 그림 크기·ANI 프레임 순서·핫스폿·숫자/버튼 식별자를 보존해야 한다. 작은 영문 영역에 한글이 들어가는지는 실제 글리프와 배경 경계를 검토해야 하며, 가독성을 확인하지 않고 잘라 넣지 않는다. 이름은 기존 용어집을 재사용한다.

추가 확인: outfitmodules-055의 NO ROOM FOR LANDERS / ESCAPE POD도 번역 대상이다. 소개/엔딩/크레딧 배경 19개를 별도로 보고 cutscene-image-review.json에 기록했다. ending-006의 THE END는 크레딧 문자열과 다른 이미지이며 아직 영문이다. victory2 239프레임과 spins 3개 그림은 별도 미검토로 남긴다.

조선소는 DrawRaceStrings가 지우는 상단 영역이 11픽셀이다. 7픽셀 한글 두 줄을 단순히 키우면 영역 밖 잔상/함선 그림 겹침이 생길 수 있으므로 shipyard-label-layout-review.json에서 제약을 추적한다. 실제 해결책과 적용은 아직 대기다.

일시정지/종료 안내 2개, 함대 대전 조작 방식 16개, 네트워크 조작/NET 패널 6개를 동일 크기의 새 텍스트 패널로 생성한다. 원래 입력 처리와 B 식별자는 유지한다. 초급/중급/고급은 WEAK/GOOD/AWESOME 세 사이보그 난이도에 대응한다. 기본/선택 배경·글자 색상은 각 원본 패널의 팔레트를 유지하며 음영 글자 대신 native Galmuri7을 쓴다. control-panel-checks.json의 구조 검증과 정적 미리보기는 실기 검토를 대체하지 않는다.
