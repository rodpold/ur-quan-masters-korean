"""Verify composed planet labels; measured widths still require runtime review."""
import hashlib
import io
import json
from pathlib import Path
from PIL import Image
from inventory_text import blocks

ROOT = Path(__file__).resolve().parents[1]


def verify_world_types(package, source):
    spec = json.loads((ROOT/'translations/world-types.ko.json').read_text(encoding='utf-8'))
    raw = source.read(spec['source_path'])
    assert hashlib.sha256(raw).hexdigest() == spec['source_sha256']
    before = list(blocks(raw.decode()))
    after = list(blocks(package.read('ko/gamestrings.txt').decode()))
    assert [int(row['id']) for row in spec['records']] == list(range(309, 361))
    for row in spec['records']:
        index = int(row['id'])
        assert before[index][2] == row['source']
        assert after[index][2] == row['ko']
    rows = []
    for index in range(309, 359):
        rows.append({'id': f'{index:04d}', 'ko': after[index][2]+' '+after[359][2]})
    rows.append({'id': '0360', 'ko': after[360][2]})
    for row in rows:
        row['fonts'] = {}
        for family in ['tiny', 'micro']:
            width = height = 0
            for char in row['ko']:
                im = Image.open(io.BytesIO(package.read(f'ko/fonts/{family}.fon/{ord(char):05x}.png'))).convert('RGBA')
                alpha = im.getchannel('A')
                assert set(alpha.tobytes()) <= {0, 255}
                bbox = alpha.getbbox()
                assert bbox or char == ' '
                if bbox:
                    height = max(height, bbox[3]-bbox[1])
                width += im.width+1
            row['fonts'][family] = {'conservative_width': width, 'ink_height': height}
    assert next(row['ko'] for row in rows if before[int(row['id'])][2] == 'Rainbow') == '무지개 행성'
    assert next(row['ko'] for row in rows if before[int(row['id'])][2] == 'Shattered') == '산산이 부서진 행성'
    return {'status': 'static_passed_runtime_pending', 'source_records': 52,
            'composed_labels': rows,
            'limitations': ['Widths include a conservative one-pixel advance per glyph; no universal screen-fit limit is asserted.',
                            'PC and 3DO scan layouts and ambiguous type meanings require runtime and linguistic review.']}
