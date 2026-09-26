# 배포 절차

Windows x64 / Python 3.12에서 빌드합니다. 설치된 게임이나 사용자 저장 파일을 Git 또는 배포 ZIP에 포함하지 않습니다.

```powershell
python -m venv .venv-release
.\.venv-release\Scripts\python -m pip install -r requirements-build.txt
.\.venv-release\Scripts\python -m unittest discover -s tests
.\.venv-release\Scripts\python tools/build_windows_release.py
.\.venv-release\Scripts\python tools/build_source_release.py --output artifacts/uqm-korean-1.0.0-source.zip
```

`dist/UQM-Korean-Patcher`가 이미 있으면 새 checkout 또는 새 작업 폴더에서 빌드합니다.
배포 소스 ZIP은 커밋된 깨끗한 작업 트리에서만 만듭니다. 태그, patcher.VERSION, CHANGELOG.md와 README 다운로드 이름을 맞추세요.
Windows ZIP의 BUILD-INFO.json에는 소스 커밋, Python 및 패키징 의존성 버전과 라이선스 해시를 기록합니다.

`.github/workflows/release.yml`은 `v*` 태그를 push하면 테스트 후 Windows ZIP과 소스 ZIP 및 SHA256SUMS.txt를 만들고 GitHub Release에 게시합니다.
태그와 소스 버전이 다르면 중단합니다. 먼저 draft를 생성하고 모든 첨부 파일 업로드가 성공한 후 공개합니다.
기존 릴리스나 태그를 덮어쓰지 않습니다. 실패한 draft가 있다면 원인을 확인한 뒤 운영자가 정리해야 합니다.

공개 전에는 해당 버전의 Windows EXE를 다른 폴더에 풀어 로컬 게임 복사본으로 install/status/uninstall을 확인합니다.
원본 게임 패키지를 읽어 생성한 애드온은 로컬 검사에만 사용하며 배포하지 않습니다.
CLI `build` 결과와 Python 빌드 결과를 비교하고 원본·음성·사용자 파일의 보존을 확인합니다.
실제 게임 플레이는 사용자 피드백으로 검수하며 자동으로 게임을 실행하지 않습니다.

패키징 형식은 [PyInstaller 문서](https://pyinstaller.org/en/stable/usage.html), 릴리스 게시 명령은 [GitHub CLI 문서](https://cli.github.com/manual/gh_release_create)를 참고하세요.

태그 push로 실행되지 않으면 Actions → Release → Run workflow에서 main과 기존 태그(예: v1.0.0)를 지정할 수 있습니다. 수동 실행도 지정한 태그의 소스를 checkout하며 태그를 변경하거나 새로 만들지 않습니다.
