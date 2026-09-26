"""Exercise a release EXE against disposable copies; never launch the game."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import patcher


def verify(archive, source_game):
    patcher.validate_game(source_game)
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    with tempfile.TemporaryDirectory(prefix='uqm-release-') as temporary:
        tmp = Path(temporary)
        with ZipFile(archive) as z:
            assert z.testzip() is None
            assert not any(Path(n).suffix.lower() in ('.uqm', '.ogg', '.lpf') for n in z.namelist())
            z.extractall(tmp/'배포 시험')
        exe = tmp/'배포 시험/UQM-Korean-Patcher/UQM-Korean-Patcher.exe'
        game = tmp/'게임 설치'
        originals = ('uqm.exe', patcher.SOURCE.as_posix(), 'content/addons/uqm-0.8.0-voice.uqm')
        hashes = {}
        for relative in originals:
            source = source_game/relative
            if not source.exists():
                continue
            dest = game/relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            hashes[relative] = digest(dest)
        (game/'save-fixture').write_bytes(b'untouched user save')
        (game/'settings-fixture').write_bytes(b'untouched user settings')
        hashes.update({name: digest(game/name) for name in ('save-fixture', 'settings-fixture')})
        env = os.environ.copy()
        env['PATH'] = str(Path(os.environ['SystemRoot'])/'System32')
        env.pop('PYTHONPATH', None)
        def run(*args, input_data=None):
            result = subprocess.run([str(exe), *args], cwd=tmp, env=env, input=input_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
            if result.returncode:
                raise RuntimeError(repr(result.stdout)+repr(result.stderr))
            return result.stdout
        assert run('--version').strip() == patcher.VERSION.encode()
        print('Installing with frozen executable and no Python on PATH...', flush=True)
        first = json.loads(run('install', '--game', str(game)))
        assert first['version'] == patcher.VERSION
        expected, _ = patcher.build(source_game)
        package = patcher.addon_dir(game)/'ko-ui.uqm'
        assert package.read_bytes() == expected, 'Frozen and source builds differ'
        print('Checking repeat install and removal...', flush=True)
        assert json.loads(run('install', '--game', str(game))) == first
        assert json.loads(run('status', '--game', str(game))) == first
        # Exercise the interactive menu without opening the game.
        menu = run(input_data=(str(game)+'\n3\n0\n').encode('utf-8'))
        assert patcher.VERSION.encode() in menu
        assert json.loads(run('uninstall', '--game', str(game)))['state'] == 'not_installed'
        assert json.loads(run('status', '--game', str(game)))['state'] == 'not_installed'
        assert not patcher.addon_dir(game).exists()
        assert all(digest(game/name) == value for name, value in hashes.items())
        return {'version': patcher.VERSION, 'archive_sha256': digest(archive), 'generated_addon_sha256': hashlib.sha256(expected).hexdigest(), 'frozen_matches_source': True, 'install_repeat_status_uninstall': 'passed', 'interactive_status_exit': 'passed', 'non_ascii_paths': 'passed', 'originals_and_user_fixtures_unchanged': True, 'game_launched': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.archive.resolve(), args.game.resolve())
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
