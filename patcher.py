"""UQM 0.8 Steam Korean common UI patch. Does not modify game binaries."""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
ADDON = 'uqm-korean-ui-poc'
VERSION = '0.1.0'
SOURCE = Path('content/packages/uqm-0.8.0-content.uqm')
SUPPORTED_HASH = 'ee730116f1a3d3f77689e7cbdfb26f43a1773d236db986dc0d47abf93b14e7d6'
LABELS = ['새 게임', '불러오기', '함대 대전', '설정', '종료']

def sha(data):
    return hashlib.sha256(data).hexdigest()

def validate_game(game):
    game = Path(game).resolve(strict=True)
    if not (game / 'uqm.exe').is_file():
        raise ValueError('uqm.exe가 있는 게임 설치 폴더를 선택하세요.')
    if sha((game / SOURCE).read_bytes()) != SUPPORTED_HASH:
        raise ValueError('검증되지 않은 게임 데이터입니다. 이 테스트는 확인된 Steam 0.8.0 데이터만 지원합니다.')
    return game

def translate_table(text, translations):
    # Keep every header, record order, blank record and newline intact.
    chunks = re.split(r'(?m)(^#\([^\r\n]*\)[^\r\n]*\r?\n)', text)
    counts = {key: 0 for key in translations}
    for i in range(2, len(chunks), 2):
        body = chunks[i]
        value = body.rstrip('\r\n')
        if value in translations:
            chunks[i] = translations[value] + body[len(value):]
            counts[value] += 1
    missing = [key for key, count in counts.items() if not count]
    if missing:
        raise ValueError(f'원본 문자열을 찾지 못했습니다: {missing}')
    return ''.join(chunks), counts

def png(image):
    out = io.BytesIO()
    image.save(out, format='PNG')
    return out.getvalue()

def font(name, size):
    return ImageFont.truetype(str(ROOT / 'vendor/galmuri' / (name + '.ttf')), size)

def text_mask(text, f):
    box = f.getbbox(text)
    im = Image.new('L', (box[2]-box[0], box[3]-box[1]))
    ImageDraw.Draw(im).text((-box[0], -box[1]), text, font=f, fill=255)
    return im.point(lambda p: 255 if p >= 128 else 0)

def menu_assets(z):
    # The original unselected English labels are baked into the background.
    # For this POC use a solid panel; no AI reconstruction of the artwork.
    bg = Image.open(io.BytesIO(z.read('base/ui/newgame-000.png'))).convert('RGB')
    d = ImageDraw.Draw(bg)
    d.rectangle((79, 24, 244, 216), fill=(8, 13, 26), outline=(85, 104, 127))
    entries = {'ko/ui/newgame-000.png': None}
    ani = ['newgame-000.png -1 -1 0 0']
    for i, label in enumerate(LABELS, 1):
        mask = text_mask(label, font('Galmuri11', 24))
        x, y = (320-mask.width)//2, 45+(i-1)*32
        bg.paste((174, 184, 199), (x, y), mask)
        selected = Image.new('RGBA', mask.size, (255, 255, 255, 0))
        selected.putalpha(mask)
        entries[f'ko/ui/newgame-{i:03}.png'] = png(selected)
        ani.append(f'newgame-{i:03}.png -1 -1 {-x} {-y}')
    entries['ko/ui/newgame-000.png'] = png(bg)
    entries['ko/ui/newgame.ani'] = ('\n'.join(ani)+'\n').encode()
    return entries

def translate_setup(text, translations):
    chunks = re.split(r'(?m)(^#\(([^\r\n]*)\)[^\r\n]*\r?\n)', text)
    seen = set()
    for i in range(1, len(chunks), 3):
        header, key, body = chunks[i:i+3]
        if key not in translations:
            raise ValueError(f'설정 번역 누락: {key}')
        value = translations[key]
        # Lists are indexed by the game: preserve even the initial empty item.
        if key.endswith('_OPTS') or key in {'SUBTITLES','CHOICES','SLIDERS','BUTTONS','LABELS','TEXT_ENTRIES','TEXT_ENTRIES_INITIAL','CONTROL_ENTRIES'}:
            if len(body.rstrip('\r\n').splitlines()) != len(value.splitlines()):
                raise ValueError(f'설정 항목 수 불일치: {key}')
        trailing = body[len(body.rstrip('\r\n')):]
        chunks[i+1] = ''  # captured key is metadata, not output
        chunks[i+2] = value.replace('\n', '\r\n' if '\r\n' in text else '\n') + trailing
        seen.add(key)
    if set(translations) != seen:
        raise ValueError(f'존재하지 않는 설정 키: {set(translations)-seen}')
    return ''.join(chunks)

def panel_assets(z):
    entries = {}
    # Copy to a private namespace at build time, never into the source repo.
    ani = z.read('base/ui/playmenu.ani')
    entries['ko/ui/playmenu.ani'] = ani
    for line in ani.decode().splitlines():
        name = line.split()[0]
        entries['ko/ui/'+name] = z.read('base/ui/'+name)
    f = font('Galmuri7', 8)
    def label(im, text, box, color=(255,0,255,255)):
        x,y,w,h=box
        mask=text_mask(text,f)
        if mask.width>w or mask.height>h:
            raise ValueError(f'이미지 영역보다 긴 번역: {text}')
        ImageDraw.Draw(im).rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,255))
        im.paste(color,(x+(w-mask.width)//2,y+(h-mask.height)//2),mask)
    for n,text in [(61,'저장'),(62,'불러오기')]:
        im=Image.new('RGBA',(90,7),(0,0,0,255))
        label(im,text,(0,0,90,7))
        entries[f'ko/ui/playmenu-{n:03}.png']=png(im)
    im=Image.open(io.BytesIO(entries['ko/ui/playmenu-060.png'])).convert('RGBA')
    # Replace only the old EMPTY SLOT text, keeping the surrounding frame.
    label(im,'빈 슬롯',(50,50,140,35))
    entries['ko/ui/playmenu-060.png']=png(im)
    im=Image.open(io.BytesIO(entries['ko/ui/playmenu-063.png'])).convert('RGBA')
    for text,box in [('화물',(10,1,69,10)),('장치',(157,1,72,10)),('착륙선',(10,73,69,10)),('자원',(157,84,72,10)),('크레딧',(157,109,72,10))]:
        label(im,text,box)
    entries['ko/ui/playmenu-063.png']=png(im)
    return entries

def translate_dialogue(text, translations):
    chunks = re.split(r'(?m)(^#\(([^\r\n)]*)\)[^\r\n]*\r?\n)', text)
    seen = set()
    for i in range(1, len(chunks), 3):
        header, key, body = chunks[i:i+3]
        chunks[i+1] = ''
        if key not in translations:
            continue
        value = translations[key]
        old = body.rstrip('\r\n')
        if len(old.splitlines()) != len(value.splitlines()):
            raise ValueError(f'Dialogue timing segment count changed: {key}')
        chunks[i+2] = value.replace('\n', '\r\n' if '\r\n' in text else '\n') + body[len(old):]
        seen.add(key)
    if seen != set(translations):
        raise ValueError(f'Missing dialogue IDs: {set(translations)-seen}')
    return ''.join(chunks)

def dialogue_source(game, source, key, base_bytes):
    """Resolve the installed voice edition while retaining its audio/timing suffix."""
    voice = Path(game)/'content/addons/uqm-0.8.0-voice.uqm'
    if not voice.is_file():
        return base_bytes, ''
    with ZipFile(voice) as archive:
        mappings = {}
        for name in archive.namelist():
            if name.endswith('.rmp'):
                for line in archive.read(name).decode('utf-8').splitlines():
                    if '=' in line:
                        k, value = line.split('=', 1)
                        mappings[k.strip()] = value.strip()
        if key not in mappings:
            return base_bytes, ''
        parts = mappings[key].split(':', 2)
        alternate = 'addons/3dovoice/' + source.removeprefix('base/comm/')
        if len(parts) < 2 or parts[0] != 'CONVERSATION' or parts[1] not in (source, alternate):
            raise ValueError(f'Unexpected voice mapping: {key}')
        data = base_bytes if parts[1] == source else archive.read(parts[1].removeprefix('addons/'))
        return data, ':' + parts[2] if len(parts) == 3 else ''


def edition_translations(species, base, active, translations):
    """Changed voice-edition records require an explicit, reviewed translation."""
    def bodies(text):
        parts = re.split(r'(?m)^#\(([^\r\n)]*)\)[^\r\n]*\r?\n', text)
        return {parts[i]:parts[i+1].rstrip('\r\n') for i in range(1,len(parts),2)}
    before, after = bodies(base), bodies(active)
    if before.keys() != after.keys():
        raise ValueError(f'Voice edition IDs changed: {species}')
    changed = {k for k in before if before[k] != after[k]}
    path = ROOT/'translations/dialogue-voice'/f'{species}.ko.json'
    overrides = json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}
    if not set(overrides) <= before.keys():
        raise ValueError(f'Unknown voice translation ID: {species}')
    if changed and not changed.intersection(translations) <= overrides.keys():
        raise ValueError(f'Unreviewed voice-edition translation: {species}: {sorted(changed.intersection(translations)-overrides.keys())}')
    return {**translations, **{k:overrides[k] for k in changed if k in overrides}}


def report_translations():
    path = ROOT/'translations/reports.ko.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else {}


def report_assets(archive, translations):
    """Override only mapped lander text resources; keep record/paragraph structure."""
    mappings = {}
    for line in archive.read('uqm.rmp').decode('utf-8').splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            mappings.setdefault(value.strip(), []).append(key.strip())
    entries, overrides = {}, []
    for source, records in sorted(translations.items()):
        if not re.fullmatch(r'base/lander/(?:bio|energy)/[a-z_]+\.txt', source):
            raise ValueError(f'Unexpected report path: {source}')
        keys = mappings.get('STRTAB:' + source, [])
        if len(keys) != 1:
            raise ValueError(f'Unexpected report mapping: {source}')
        target = source.replace('base/', 'ko/', 1)
        before = archive.read(source).decode('utf-8')
        after = translate_dialogue(before, records)
        if [bool(line.strip()) for line in before.splitlines()] != [bool(line.strip()) for line in after.splitlines()]:
            raise ValueError(f'Report paragraph structure changed: {source}')
        from report_layout import compile_table
        entries[target] = compile_table(before, records).encode('utf-8')
        overrides.append(f'{keys[0]} = STRTAB:{target}')
    if translations:
        from report_layout import font_assets
        entries.update(font_assets(archive, [v for rows in translations.values() for v in rows.values()] + ['(다음)'], ROOT))
        overrides.append('font.lander = FONTRES:ko/fonts/lander.fon')
    return entries, overrides


def build(game, ui_font="compact"):
    if ui_font not in {"compact", "larger"}:
        raise ValueError("Unknown UI font preset")
    game = validate_game(game)
    translations = json.loads((ROOT/'translations/ui.ko.json').read_text(encoding='utf-8'))
    setup = json.loads((ROOT/'translations/setup.ko.json').read_text(encoding='utf-8'))
    if ui_font == 'larger':
        # The engine fixes title/subtitle baselines only 8px apart.
        # Keep one heading at the subtitle position, including on the main page.
        # A space retains the title record without drawing visible ink.
        subtitles = setup['SUBTITLES'].split('\n')
        if subtitles[0] != '':
            raise ValueError('Expected empty main setup subtitle')
        subtitles[0] = setup['TITLE']
        setup['SUBTITLES'] = '\n'.join(subtitles)
        setup['TITLE'] = ' '
    dialogue = {p.name.removesuffix('.ko.json'): json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'translations/dialogue').glob('*.ko.json'))}
    registry = json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
    dialogue_rows = {row['id']: row for row in registry['dialogue_fonts']}
    reports = report_translations()
    dialogue_values = [v for records in [*dialogue.values(), *reports.values()] for v in records.values()]
    for p in (ROOT/'translations/dialogue-voice').glob('*.ko.json'):
        dialogue_values.extend(json.loads(p.read_text(encoding='utf-8')).values())
    chars = sorted({c for s in [*translations.values(), *setup.values(), *dialogue_values] for c in s if ord(c)>127})
    entries = {}
    rmp = ['text.starcon = STRTAB:ko/gamestrings.txt',
           'graphics.newgame = GFXRES:ko/ui/newgame.ani',
           'graphics.playmenu = GFXRES:ko/ui/playmenu.ani',
           'text.setupmenu = STRTAB:ko/setupmenu.txt']
    with ZipFile(game/SOURCE) as z:
        report_entries, report_rmp = report_assets(z, reports)
        entries.update(report_entries)
        rmp.extend(report_rmp)
        original = z.read('base/gamestrings.txt').decode('utf-8')
        if reports:
            from report_layout import spaced
            translations = {**translations, '(MORE)': spaced(translations.get('(MORE)', '(다음)'))}
        translated, counts = translate_table(original, translations)
        entries['ko/gamestrings.txt'] = translated.encode('utf-8')
        entries.update(menu_assets(z))
        entries.update(panel_assets(z))
        entries['ko/setupmenu.txt'] = translate_setup(z.read('base/ui/setupmenu.txt').decode('utf-8'),setup).encode('utf-8')
        for species, records in dialogue.items():
            source_species = 'yehatrebels' if species == 'yehat.rebel' else species
            source = f'base/comm/{source_species}/{source_species}.txt'
            target = f'ko/comm/{species}/{species}.txt'
            key = dialogue_rows[species]['dialogue_resource']
            base = z.read(source)
            active, suffix = dialogue_source(game, source, key, base)
            selected = edition_translations(species, base.decode('utf-8'), active.decode('utf-8'), records)
            entries[target] = translate_dialogue(active.decode('utf-8'), selected).encode('utf-8')
            rmp.append(f'{key} = CONVERSATION:{target}{suffix}')
        for family in ['starcon','tiny','micro','player','urquan']:
            prefix = f'base/fonts/{family}.fon/'
            # Retain original ASCII/symbol metrics; add only translated Hangul.
            for name in z.namelist():
                if name.startswith(prefix) and name.endswith('.png'):
                    entries[name.replace('base/fonts/', 'ko/fonts/', 1)] = z.read(name)
            for char in chars:
                large = family == 'micro'
                larger_ui = family in {'player','urquan'} or (family == 'starcon' and ui_font == 'larger')
                mask = text_mask(char, font('Galmuri11' if large else 'Galmuri9' if larger_ui else 'Galmuri7', 12 if large else 10 if larger_ui else 8))
                if mask.size != ((12,11) if large else (10,9) if larger_ui else (8,7)):
                    raise ValueError(f'예상하지 못한 글자 크기: {ord(char):x} {mask.size}')
                # Keep the baseline at the bottom of the ink; UQM uses h-3 above 9px.
                # Larger starcon is experimental: fixed 8px in-game rows need visual QA.
                glyph = Image.new('RGBA', (12,14) if large else (10,12) if larger_ui else (8,8), (255,255,255,0))
                glyph.paste(Image.new('RGBA', mask.size, (255,255,255,255)), (0,0), mask)
                entries[f'ko/fonts/{family}.fon/{ord(char):05x}.png'] = png(glyph)
            resource = 'comm.urquan.font' if family == 'urquan' else f'font.{family}'
            rmp.append(f'{resource} = FONTRES:ko/fonts/{family}.fon')
        rmp.append('comm.commander.font = FONTRES:ko/fonts/player.fon')
        from race_fonts import add_race_fonts
        race_font_report = add_race_fonts(entries, rmp, z, chars)
        entries['ko-ui.rmp'] = ('\n'.join(line.replace(':ko/', f':addons/{ADDON}/ko/') for line in rmp)+'\n').encode()
    entries['ko/OFL.txt'] = (ROOT/'vendor/galmuri/OFL.txt').read_bytes()
    data = io.BytesIO()
    with ZipFile(data, 'w', ZIP_DEFLATED) as archive:
        for name, value in sorted(entries.items()):
            from zipfile import ZipInfo
            item = ZipInfo(name, date_time=(2026,1,1,0,0,0))
            item.compress_type = ZIP_DEFLATED
            archive.writestr(item, value)
    return data.getvalue(), {'ui_font':ui_font, 'race_fonts':race_font_report, 'dialogue_records':sum(map(len,dialogue.values())), 'report_records':sum(map(len,reports.values())), 'glyphs_per_font':len(chars), 'translated_records':sum(counts.values()), 'setup_records':len(setup), 'files':len(entries)}

def addon_dir(game):
    game = Path(game).resolve(strict=True)
    target = game / 'content/addons' / ADDON
    for part in [game/'content', game/'content/addons', target]:
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('애드온 경로의 링크/정션은 지원하지 않습니다.')
    if not target.resolve().is_relative_to(game):
        raise ValueError('애드온 경로가 게임 폴더 외부를 가리킵니다.')
    return target

def status(game):
    target = addon_dir(game)
    if not target.exists():
        return {'state':'not_installed'}
    manifest = target/'manifest.json'
    package = target/'ko-ui.uqm'
    if not manifest.is_file() or not package.is_file():
        raise ValueError('불완전하거나 다른 파일이 있는 애드온 폴더입니다. 자동 변경하지 않습니다.')
    meta = json.loads(manifest.read_text(encoding='utf-8'))
    if meta.get('addon') != ADDON or sha(package.read_bytes()) != meta.get('sha256'):
        raise ValueError('패치 파일이 설치 이후 변경되었습니다. 자동 변경하지 않습니다.')
    if {p.name for p in target.iterdir()} != {'manifest.json', 'ko-ui.uqm'}:
        raise ValueError('애드온 폴더에 추가 파일이 있습니다. 자동 변경하지 않습니다.')
    for p in [manifest, package]:
        if p.is_symlink() or not p.resolve().is_relative_to(Path(game).resolve()):
            raise ValueError('외부 경로 또는 심볼릭 링크는 지원하지 않습니다.')
    return {'state':'installed', **meta}

def atomic_write(path, data):
    fd, temp = tempfile.mkstemp(prefix='.ko-', dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(data)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def install(game, ui_font="compact"):
    validate_game(game)
    current = status(game)
    data, report = build(game, ui_font)
    if current['state'] == 'installed' and current['sha256'] == sha(data):
        return current
    target = addon_dir(game)
    previous = None
    if current['state'] == 'installed':
        previous = [(target/name, (target/name).read_bytes()) for name in ['ko-ui.uqm','manifest.json']]
    else:
        target.mkdir(parents=True, exist_ok=False)
    meta = {'addon':ADDON,'version':VERSION,'sha256':sha(data),'source_sha256':SUPPORTED_HASH,**report}
    try:
        atomic_write(target/'ko-ui.uqm',data)
        atomic_write(target/'manifest.json',(json.dumps(meta,indent=2)+'\n').encode())
    except BaseException:
        if previous:
            for path, old in previous:
                atomic_write(path, old)
        else:
            for name in ['ko-ui.uqm','manifest.json']:
                (target/name).unlink(missing_ok=True)
            target.rmdir()
        raise
    return {'state':'installed', **meta}

def uninstall(game):
    current = status(game)
    if current['state'] == 'not_installed':
        return current
    target = addon_dir(game)
    (target/'ko-ui.uqm').unlink()
    (target/'manifest.json').unlink()
    target.rmdir()
    return {'state':'not_installed'}

def launch(game, test_config=None):
    game = validate_game(game)
    if status(game)['state'] != 'installed':
        raise ValueError('먼저 install을 실행하세요.')
    args = [str(game/'uqm.exe'), '--addon', ADDON, '--menu', 'pc', '--font', '3do', '--scale', 'none']
    if test_config:
        cfg = Path(test_config).resolve()
        cfg.mkdir(parents=True,exist_ok=True)
        args += ['--configdir',str(cfg),'--windowed','--res','960x720',
                 '--logfile',str(cfg/'uqm.log')]
    return subprocess.Popen(args,cwd=game).pid

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['inspect','build','install','status','uninstall','launch'])
    parser.add_argument('--game',required=True,type=Path)
    parser.add_argument('--output',type=Path,default=ROOT/'artifacts/ko-ui.uqm')
    parser.add_argument('--test-config',type=Path)
    parser.add_argument('--ui-font',choices=['compact','larger'],default='compact',
                        help='Experimental larger preset: 9px common UI glyphs (build/install only).')
    args = parser.parse_args()
    try:
        if args.command == 'inspect':
            print(validate_game(args.game)); return
        if args.command == 'build':
            data, result = build(args.game, args.ui_font)
            args.output.parent.mkdir(parents=True,exist_ok=True)
            atomic_write(args.output,data)
        elif args.command == 'install':
            result = install(args.game, args.ui_font)
        elif args.command == 'launch':
            result = {'pid':launch(args.game,args.test_config)}
        else:
            result = globals()[args.command](args.game)
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except (ValueError,OSError) as exc:
        parser.exit(1,f'{exc}\n')

if __name__ == '__main__':
    main()
