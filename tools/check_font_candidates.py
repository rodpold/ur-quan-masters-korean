"""Check downloaded candidates without changing installed game assets."""
import hashlib
import json
from pathlib import Path
from PIL import ImageFont

ROOT = Path(__file__).resolve().parents[1]

def check():
    registry = json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
    glossary = json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))
    ids = {entry['id'] for entry in glossary['terms']}
    texts = ['우리는 너희의 응답을 기다린다.', '함장, 교신을 계속할까요? 켬 / 끔']
    paths = [ROOT/'translations/ui.ko.json', ROOT/'translations/setup.ko.json',
             *(ROOT/'translations/dialogue').glob('*.json')]
    for path in paths:
        texts.extend(json.loads(path.read_text(encoding='utf-8')).values())
    reports = ROOT/'translations/reports.ko.json'
    if reports.is_file():
        texts.extend(v for rows in json.loads(reports.read_text(encoding='utf-8')).values() for v in rows.values())
    chars = sorted({c for text in texts for c in text if ord(c)>127})
    results = {}
    for name in dict.fromkeys(registry['specimen_order'] + registry.get('expressive_specimen_order', []) + registry.get('binary_specimen_order', [])):
        info = registry['fonts'][name]
        file = ROOT/info['file']
        if hashlib.sha256(file.read_bytes()).hexdigest() != info['sha256']:
            raise ValueError(f'{name}: file hash changed')
        for license_file in [info['license_file'], *info.get('additional_licenses', [])]:
            if not (ROOT/license_file).is_file():
                raise ValueError(f'{name}: missing license {license_file}')
        face = ImageFont.truetype(str(file), info['raster_px'])
        notdef = bytes(face.getmask(chr(0x10ffff)))
        missing = [c for c in chars if not any(face.getmask(c)) or bytes(face.getmask(c)) == notdef]
        if missing:
            raise ValueError(f'{name}: missing {missing}')
        results[name] = {'checked_characters':len(chars), 'missing':0,
                         'max_bbox_height':max(face.getbbox(c)[3]-face.getbbox(c)[1] for c in chars)}
    for row in registry['dialogue_fonts']:
        if not set(row['glossary_ids']) <= ids or row['candidate_font'] not in registry['fonts']:
            raise ValueError(f'Invalid mapping: {row["id"]}')
    for family in sorted({Path(info['file']).parts[1] for info in registry['fonts'].values()}):
        base = ROOT/'vendor'/family
        for relative, digest in json.loads((base/'SHA256.json').read_text()).items():
            if hashlib.sha256((base/relative).read_bytes()).hexdigest() != digest:
                raise ValueError(f'Vendor file changed: {family}/{relative}')
    return results

if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2))
