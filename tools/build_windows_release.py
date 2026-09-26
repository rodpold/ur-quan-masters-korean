"""Build a Windows x64 folder distribution without any game files."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from patcher import VERSION


def build(output_root=None):
    if sys.platform != 'win32' or platform.machine().lower() not in ('amd64', 'x86_64'):
        raise ValueError('Build on Windows x64 with 64-bit Python.')
    output_root = Path(output_root) if output_root else ROOT/'dist'
    out = output_root/'UQM-Korean-Patcher'
    if out.exists():
        raise ValueError('dist/UQM-Korean-Patcher already exists; use a fresh checkout/build directory.')
    command = [sys.executable, '-m', 'PyInstaller', '--noconfirm', '--onedir', '--console', '--noupx',
               '--name', 'UQM-Korean-Patcher', '--distpath', str(output_root),
               '--workpath', str(ROOT/'build/pyinstaller'), '--specpath', str(ROOT/'build')]
    for folder in ('translations', 'vendor', 'LICENSES'):
        command += ['--add-data', f'{ROOT/folder}:{folder}']
    command.append(str(ROOT/'release_launcher.py'))
    subprocess.run(command, cwd=ROOT, check=True)
    for name in ('README.md', 'THIRD_PARTY.md', 'LICENSE', 'CHANGELOG.md'):
        shutil.copy2(ROOT/name, out/name)
    shutil.copytree(ROOT/'LICENSES', out/'LICENSES')
    # Include notices from the actual distributions, including Pillow's bundled libraries.
    licenses = out/'LICENSES/runtime'
    licenses.mkdir(parents=True)
    records = {}
    for name in ('Pillow', 'pyinstaller', 'pyinstaller-hooks-contrib', 'altgraph', 'packaging', 'pefile', 'pywin32-ctypes', 'setuptools'):
        dist = importlib.metadata.distribution(name)
        records[name] = {'version': dist.version, 'license_files': {}}
        for entry in dist.files or ():
            if any(word in str(entry).lower() for word in ('license', 'copying', 'notice')) and '.dist-info/' in entry.as_posix():
                source = Path(dist.locate_file(entry))
                if source.is_file():
                    target = licenses/name/Path(*entry.parts[1:])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, target)
                    records[name]['license_files'][target.relative_to(out).as_posix()] = hashlib.sha256(source.read_bytes()).hexdigest()
    python_license = Path(sys.base_prefix)/'LICENSE.txt'
    if not python_license.is_file():
        raise ValueError('Python LICENSE.txt is required for redistribution.')
    shutil.copy2(python_license, licenses/'Python-LICENSE.txt')
    records['Python'] = {'version': platform.python_version(), 'license_sha256': hashlib.sha256(python_license.read_bytes()).hexdigest()}
    revision = subprocess.check_output(['git', '-c', 'safe.directory='+ROOT.as_posix(), 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(['git', '-c', 'safe.directory='+ROOT.as_posix(), 'status', '--porcelain'], cwd=ROOT).strip())
    (out/'BUILD-INFO.json').write_text(json.dumps({'version': VERSION, 'source_revision': revision, 'dirty_worktree': dirty, 'runtime': records}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    # Runtime command can load all packaged modules and must report the release version.
    actual = subprocess.check_output([str(out/'UQM-Korean-Patcher.exe'), '--version'], text=True).strip()
    if actual != VERSION:
        raise ValueError('Frozen version mismatch: '+actual)
    artifact = ROOT/f'artifacts/uqm-korean-{VERSION}-windows-x64.zip'
    artifact.parent.mkdir(exist_ok=True)
    with ZipFile(artifact, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(out.rglob('*')):
            if path.is_file():
                if path.suffix.lower() in ('.uqm', '.ogg', '.lpf') or path.name.startswith('uqmsave'):
                    raise ValueError('Game payload in release: '+str(path))
                archive.write(path, path.relative_to(out.parent).as_posix())
    with ZipFile(artifact) as archive:
        if archive.testzip():
            raise ValueError('Corrupt release archive')
    print(json.dumps({'archive': str(artifact), 'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest()}, indent=2))


if __name__ == '__main__':
    build()
