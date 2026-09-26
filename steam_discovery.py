"""Read Steam metadata without changing libraries, settings, or game files."""
import os
from pathlib import Path
import re

APP_ID = '2645580'
CONTENT = Path('content/packages/uqm-0.8.0-content.uqm')


def parse_vdf(text):
    # Steam's quoted KeyValues subset; reject malformed or ambiguous metadata.
    tokens = []
    pattern = re.compile(r'\s+|//[^\n]*|"((?:\\.|[^"\\])*)"|([{}])')
    pos = 0
    while pos < len(text):
        match = pattern.match(text, pos)
        if not match:
            raise ValueError('Unsupported Steam metadata syntax')
        pos = match.end()
        if match.group(1) is not None:
            value = re.sub(r'\\(["\\])', r'\1', match.group(1))
            tokens.append(('text', value))
        elif match.group(2):
            tokens.append((match.group(2), match.group(2)))
    index = 0

    def object_(nested=False, depth=0):
        nonlocal index
        if depth > 16:
            raise ValueError('Steam metadata nesting limit')
        result = {}
        while index < len(tokens):
            kind, key = tokens[index]
            index += 1
            if kind == '}' and nested:
                return result
            if kind != 'text' or key in result or index >= len(tokens):
                raise ValueError('Malformed Steam metadata')
            kind, value = tokens[index]
            index += 1
            if kind == '{':
                value = object_(True, depth+1)
            elif kind != 'text':
                raise ValueError('Malformed Steam metadata value')
            result[key] = value
        if nested:
            raise ValueError('Unclosed Steam metadata object')
        return result

    return object_()


def read_vdf(path):
    try:
        return parse_vdf(path.read_text(encoding='utf-8-sig'))
    except (OSError, UnicodeError, ValueError):
        return {}


def steam_roots():
    roots = []
    if os.name == 'nt':
        import winreg
        for hive, key, name in (
            (winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam', 'SteamPath'),
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\WOW6432Node\Valve\Steam', 'InstallPath'),
            (winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Valve\Steam', 'InstallPath'),
        ):
            try:
                with winreg.OpenKey(hive, key) as handle:
                    value, _ = winreg.QueryValueEx(handle, name)
                    if isinstance(value, str) and value:
                        roots.append(Path(value))
            except OSError:
                pass
    for variable in ('ProgramFiles(x86)', 'ProgramFiles'):
        if os.environ.get(variable):
            roots.append(Path(os.environ[variable])/'Steam')
    return roots


def discover_games(roots=None):
    libraries = set()
    for root in steam_roots() if roots is None else roots:
        root = Path(root)
        libraries.add(root.resolve())
        data = read_vdf(root/'steamapps/libraryfolders.vdf').get('libraryfolders', {})
        if not isinstance(data, dict):
            continue
        for key, entry in data.items():
            if not key.isdigit():
                continue
            value = entry.get('path') if isinstance(entry, dict) else entry
            if isinstance(value, str) and value and Path(value).is_absolute():
                libraries.add(Path(value).resolve())
    games = set()
    for library in libraries:
        data = read_vdf(library/f'steamapps/appmanifest_{APP_ID}.acf').get('AppState', {})
        if not isinstance(data, dict) or data.get('appid') != APP_ID:
            continue
        folder = data.get('installdir')
        # installdir is one directory name, never a path supplied by metadata.
        if not isinstance(folder, str) or folder in ('', '.', '..') or any(c in folder for c in '/\\:'):
            continue
        common = (library/'steamapps/common').resolve()
        candidate = (common/folder).resolve()
        if candidate.parent != common:
            continue
        if (candidate/'uqm.exe').is_file() and (candidate/CONTENT).is_file():
            games.add(candidate)
    return sorted(games, key=lambda p: str(p).casefold())


def select_game(explicit=None):
    if explicit is not None:
        return Path(explicit)
    games = discover_games()
    if len(games) == 1:
        return games[0]
    if not games:
        raise ValueError('Steam 게임 설치를 찾지 못했습니다. --game으로 설치 폴더를 지정하세요.')
    raise ValueError('게임 설치가 여러 개입니다. --game으로 선택하세요: ' + ', '.join(map(str, games)))
