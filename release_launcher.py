"""Double-click menu for the Windows release; arguments retain the patcher CLI."""
from pathlib import Path
import sys
import patcher


def choose_game():
    candidates = patcher.discover_games()
    if len(candidates) == 1:
        print(f'감지된 게임: {candidates[0]}')
        answer = input('이 폴더 사용: Enter / 다른 폴더: 경로 입력 > ').strip().strip('"')
        return Path(answer) if answer else candidates[0]
    for candidate in candidates:
        print(f'설치 후보: {candidate}')
    return Path(input('uqm.exe가 있는 게임 폴더 경로 > ').strip().strip('"'))


def interactive():
    print(f'Ur-Quan Masters 한국어 패치 {patcher.VERSION}')
    print('게임을 저장하고 종료한 다음 설치·업데이트·제거하세요.')
    game = choose_game()
    while True:
        print(f'\n대상: {game}')
        print('1 설치 / 업데이트   2 한국어로 게임 실행   3 설치 상태')
        print('4 패치 제거         5 게임 폴더 변경       0 종료')
        print('6 Steam 플레이 버튼 연결   7 Steam 실행 옵션 복원')
        choice = input('번호 입력 > ').strip()
        try:
            if choice == '0':
                return
            if choice == '5':
                game = choose_game()
            elif choice == '1':
                print('원본 확인 및 한글 이미지 생성 중입니다. 잠시 기다려 주세요.', flush=True)
                result = patcher.install(game)
                print(f"패치 설치 완료: {result['version']}.")
                print('이어서 Steam 플레이 버튼을 연결합니다. 게임과 Steam을 완전히 종료해 주세요.')
                print('Steam 창의 X 대신 왼쪽 위 Steam 메뉴 → 끝내기를 선택하세요.')
                if input('종료 후 Enter / 나중에 연결하려면 s > ').strip().lower() != 's':
                    from steam_launch import configure
                    try:
                        configure(game)
                        print('연결 완료! Steam을 다시 열고 플레이를 누르세요.')
                    except (OSError, ValueError) as exc:
                        print(f'패치 설치는 완료됐지만 Steam 연결은 완료하지 못했습니다: {exc}')
                        print('문제를 해결한 뒤 6번으로 연결하거나, 지금은 2번으로 실행하세요.')
                else:
                    print('Steam 연결은 보류했습니다. 6번으로 연결하거나 2번으로 실행할 수 있습니다.')
            elif choice == '2':
                patcher.launch(game)
                print('게임을 실행했습니다.')
            elif choice == '3':
                result = patcher.status(game)
                print(f"설치 버전: {result.get('version')}" if result['state'] == 'installed' else '설치되어 있지 않습니다.')
            elif choice == '4':
                patcher.uninstall(game)
                print('제거 완료. 자동 등록한 Steam 실행 옵션은 원래대로 복원했습니다.')
                print('과거에 직접 넣었던 패치 실행 옵션이 있다면 Steam에서 지워 주세요.')
            elif choice == '6':
                from steam_launch import configure
                configure(game)
                print('연결 완료! Steam을 다시 열고 플레이를 누르세요.')
            elif choice == '7':
                from steam_launch import restore
                restore(game)
                print('Steam 실행 옵션 복원 완료.')
            else:
                print('메뉴의 번호를 입력하세요.')
        except (OSError, ValueError) as exc:
            print(f'작업 실패: {exc}')
            print('폴더 경로·쓰기 권한을 확인하세요. 자세한 해결 방법은 README.md를 참고하세요.')


if __name__ == '__main__':
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        stream.reconfigure(encoding='utf-8')
    if len(sys.argv) > 1:
        patcher.main()
    else:
        try:
            interactive()
        except (EOFError, KeyboardInterrupt):
            pass
        except Exception as exc:
            print(f'실행 오류: {exc}')
            input('Enter를 누르면 종료합니다.')
            sys.exit(1)
