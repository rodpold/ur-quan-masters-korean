"""Validate celestial-name mappings and conservative prefix combinations."""
import hashlib,io,json,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from inventory_text import blocks

def verify_celestial(package,source):
    spec=json.loads((ROOT/'docs/celestial-name-review.json').read_text(encoding='utf-8'))
    glossary={t['id']:t for t in json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']}
    raw=source.read(spec['source_path'])
    assert hashlib.sha256(raw).hexdigest()==spec['source_sha256']
    old=list(blocks(raw.decode()));new=list(blocks(package.read('ko/gamestrings.txt').decode()))
    for row in spec['records']:
        index=int(row['id'])
        assert old[index][2]==row['source'] and new[index][2]==row['ko']
        if row['glossary_id']:assert glossary[row['glossary_id']]['ko']==row['ko']
    assert new[251][2]=='수은' and new[375][2]=='수성'
    assert glossary['mercury']['ko']==new[375][2]
    prefixes=['']+[new[i][2] for i in range(361,375)]
    names=[new[i][2] for i in range(132)]
    combinations=[(prefix+' ' if prefix else '')+name for prefix in prefixes for name in names]
    max_bytes=max(len(v.encode('utf-8'))+1 for v in combinations)
    assert max_bytes<=256,'Public pstarmap.c cursor/search buffer size exceeded'
    widths={}
    for family in ['starcon','tiny']:
        glyph_widths={}
        for char in set(''.join(combinations)):
            im=Image.open(io.BytesIO(package.read(f'ko/fonts/{family}.fon/{ord(char):05x}.png'))).convert('RGBA')
            if ord(char)>127:assert set(im.getchannel('A').tobytes())<={0,255}
            glyph_widths[char]=im.width+1
        widths[family]=max(sum(glyph_widths[c] for c in v) for v in combinations)
    return {'status':'mapping_glyph_buffer_passed_runtime_pending','mapped_records':len(spec['records']),
            'conservative_combinations':len(combinations),'max_utf8_bytes_with_nul':max_bytes,
            'max_width_with_spacing':widths,'limitations':['All prefix/name combinations are an upper bound, not an actual star list.','No proof of IME entry, search success, or screen fit in installed executable.']}
