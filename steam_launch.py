"""Register UQM launch arguments without rewriting unrelated Steam settings.

Steam must be fully closed: its in-memory localconfig otherwise wins on exit.
Only the last active account is changed; its previous argument string is saved.
"""
import csv
import json
import os
from pathlib import Path
import re
import subprocess

from steam_discovery import APP_ID, discover_games, parse_vdf, read_vdf, steam_roots

ARGUMENTS = '--addon uqm-korean-ui-poc --menu pc --font 3do --scale none'
BACKUP = 'steam-launch.json'
KEY_PATH = ('UserLocalConfigStore', 'Software', 'Valve', 'Steam', 'apps', APP_ID)


def _nodes(text):
    # Validate first, then retain source spans so all other bytes stay intact.
    parse_vdf(text)
    pattern = re.compile(r'\s+|//[^\n]*|"((?:\\.|[^"\\])*)"|([{}])')
    tokens = []
    for match in pattern.finditer(text):
        if match.group(1) is not None:
            tokens.append(('text', re.sub(r'\\(["\\])', r'\1', match.group(1)), match.start(), match.end()))
        elif match.group(2):
            tokens.append((match.group(2), '', match.start(), match.end()))
    index = 0

    def walk():
        nonlocal index
        result = {}
        while index < len(tokens) and tokens[index][0] != '}':
            key = tokens[index]
            value = tokens[index + 1]
            index += 2
            name = key[1].casefold()
            if name in result:
                raise ValueError('Steam 설정에 대소문자가 다른 중복 키가 있습니다.')
            if value[0] == '{':
                children = walk()
                close = tokens[index]
                index += 1
                result[name] = (key[2], close[3], children, close[2])
            else:
                result[name] = (key[2], value[3], value[1], value[2])
        return result
    return walk()


def options(text):
    node = None
    children = _nodes(text)
    for key in KEY_PATH:
        node = children.get(key.casefold())
        if node is None or not isinstance(node[2], dict):
            raise ValueError('Steam에서 이 게임을 한 번 실행한 뒤 Steam을 완전히 종료해 주세요.')
        children = node[2]
    entry = children.get('launchoptions')
    if entry and not isinstance(entry[2], str):
        raise ValueError('Steam 실행 옵션 형식을 확인할 수 없습니다.')
    return node, entry


def replace_options(text, value):
    parent, entry = options(text)
    if entry:
        if value is None:
            return text[:entry[0]] + text[entry[1]:]
        encoded = '"' + value.replace('\\', '\\\\').replace('"', '\\"') + '"'
        return text[:entry[3]] + encoded + text[entry[1]:]
    if value is None:
        return text
    newline = '\r\n' if '\r\n' in text else '\n'
    encoded = value.replace('\\', '\\\\').replace('"', '\\"')
    pos = parent[3]
    return text[:pos] + f'"LaunchOptions"\t\t"{encoded}"{newline}\t\t\t\t\t' + text[pos:]


def require_closed():
    if os.name != 'nt':
        raise ValueError('Steam 자동 설정은 Windows에서 지원합니다.')
    try:
        result = subprocess.run(['tasklist', '/FO', 'CSV', '/NH'], capture_output=True,
                                text=True, errors='replace', check=True,
                                creationflags=subprocess.CREATE_NO_WINDOW)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError('Steam 종료 여부를 확인하지 못했습니다. 프로세스 조회 권한을 확인해 주세요.') from exc
    if any(row and row[0].casefold() in ('steam.exe', 'uqm.exe')
           for row in csv.reader(result.stdout.splitlines())):
        raise ValueError('게임과 Steam을 완전히 종료해 주세요. Steam 창의 X 대신 Steam 메뉴 → 끝내기를 사용하세요.')


def account_config():
    candidates = set()
    for root in steam_roots():
        users = read_vdf(root/'config/loginusers.vdf').get('users', {})
        if not isinstance(users, dict):
            continue
        selected = [(sid, a) for sid, a in users.items()
                    if isinstance(a, dict) and a.get('MostRecent') == '1']
        if not selected:
            selected = [(sid, a) for sid, a in users.items()
                        if isinstance(a, dict) and a.get('AutoLogin') == '1']
        if not selected and len(users) == 1:
            selected = list(users.items())
        if len(selected) != 1:
            continue
        for steam_id, account in selected:
            if isinstance(account, dict) and steam_id.isdigit():
                user = int(steam_id) - 76561197960265728
                if 0 < user < 2**32:
                    path = root.resolve()/'userdata'/str(user)/'config/localconfig.vdf'
                    if path.is_file():
                        candidates.add(path)
    if len(candidates) != 1:
        raise ValueError('Steam 계정 설정 파일을 하나로 확인하지 못했습니다.')
    return candidates.pop()


def _read(path):
    for part in (path, *path.parents):
        if part.is_symlink() or getattr(part.lstat(), 'st_file_attributes', 0) & 1024:
            raise ValueError('링크로 연결된 Steam 설정은 지원하지 않습니다.')
    return path.read_bytes().decode('utf-8')


def require_registered_game(game):
    if Path(game).resolve() not in discover_games():
        raise ValueError('Steam에 등록된 실제 게임 설치 폴더에서만 플레이 버튼을 연결할 수 있습니다.')


def configure(game):
    import patcher
    if patcher.status(game)['state'] != 'installed':
        raise ValueError('먼저 한국어 패치를 설치해 주세요.')
    require_registered_game(game)
    require_closed()
    path = account_config()
    text = _read(path)
    _, entry = options(text)
    original = entry[2] if entry else None
    backup = patcher.addon_dir(game)/BACKUP
    if backup.exists():
        saved = json.loads(_read(backup))
        if saved.get('path') != str(path) or saved.get('applied') != original:
            raise ValueError('Steam 계정 또는 실행 옵션이 변경되었습니다. 기존 등록을 복원한 뒤 다시 등록해 주세요.')
        return {'state': 'configured'}
    # A wrapper or alternate content/config path can invalidate the verified launch.
    if original and re.search(r'%command%|--(?:contentdir|addondir|configdir|safe)\b|(?:^|\s)-[cC](?:\s|$)', original):
        raise ValueError('사용자 지정 실행 경로/설정이 있습니다. 기존 Steam 실행 옵션을 직접 확인해 주세요.')
    applied = ((original.strip() + ' ') if original else '') + ARGUMENTS
    updated = replace_options(text, applied)
    saved = {'schema': 1, 'path': str(path), 'original': original, 'applied': applied}
    # Persist recovery information before touching Steam. A crash is recoverable.
    patcher.atomic_write(backup, (json.dumps(saved, ensure_ascii=False, indent=2)+'\n').encode())
    try:
        require_closed()
        if _read(path) != text:
            raise ValueError('Steam 설정이 동시에 변경되었습니다. 다시 시도해 주세요.')
        patcher.atomic_write(path, updated.encode('utf-8'))
    except BaseException:
        backup.unlink()
        raise
    return {'state': 'configured'}


def restore(game):
    import patcher
    backup = patcher.addon_dir(game)/BACKUP
    if not backup.exists():
        return {'state': 'not_configured'}
    require_closed()
    saved = json.loads(_read(backup))
    path = account_config()
    if saved.get('schema') != 1 or saved.get('path') != str(path):
        raise ValueError('등록했던 Steam 계정으로 로그인한 뒤 종료하고 다시 시도해 주세요.')
    if not isinstance(saved.get('applied'), str) or not (saved.get('original') is None or isinstance(saved['original'], str)):
        raise ValueError('Steam 실행 옵션 백업 형식이 올바르지 않습니다.')
    text = _read(path)
    _, entry = options(text)
    current = entry[2] if entry else None
    if current != saved['original']:
        if current != saved['applied']:
            raise ValueError('등록 이후 Steam 실행 옵션을 수정했습니다. 옵션을 백업의 original 값으로 복원한 뒤 다시 시도해 주세요.')
        updated = replace_options(text, saved['original'])
        require_closed()
        if _read(path) != text:
            raise ValueError('Steam 설정이 동시에 변경되었습니다. 다시 시도해 주세요.')
        patcher.atomic_write(path, updated.encode('utf-8'))
    backup.unlink()
    return {'state': 'restored'}
