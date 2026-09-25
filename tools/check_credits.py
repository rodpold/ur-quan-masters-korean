"""Validate credit columns, retained names, buffers and binary Korean glyphs."""
import io,json,re
from pathlib import Path
from PIL import Image
from inventory_text import blocks
from credit_text import load_credits,compile_credits
ROOT=Path(__file__).resolve().parents[1]

def verify_credits(package,source):
    spec=load_credits();raw=source.read(spec['source_path']);actual=package.read('ko/cutscene/credits/credits.txt')
    assert actual==compile_credits(raw,spec)
    before=list(blocks(raw.decode()));after=list(blocks(actual.decode()))
    assert [(r[0],r[1]) for r in before]==[(r[0],r[1]) for r in after]
    terms={t['id']:t for t in json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']}
    records=[]
    for row in spec['records']:
        index=int(row['id']);old=re.match(r'(\d+\s+\S+\s+)([\s\S]*)',before[index][2]);new=re.match(r'(\d+\s+\S+\s+)([\s\S]*)',after[index][2])
        assert old[1]==new[1]
        size,align=old[1].split();lines=new[2].splitlines();previous=old[2].splitlines()
        assert len(lines)==len(previous) and len(new[2].encode())<2048
        assert len(lines)+sum(line.count('\t') for line in lines)<=50
        changes={(r['line'],r['column']):r for r in row['edits']}
        widths=[]
        for i,(a,b) in enumerate(zip(previous,lines)):
            aa=a.split('\t');bb=b.split('\t');assert len(aa)==len(bb)<=5
            for col,(orig,text) in enumerate(zip(aa,bb)):
                if (i,col) not in changes:assert orig==text;continue
                edit=changes[i,col];assert text==edit['ko']
                if 'glossary_id' in edit:assert text.strip()==terms[edit['glossary_id']]['ko']
                width=0
                for c in text:
                    im=Image.open(io.BytesIO(package.read(f'ko/fonts/pt{size}.fon/{ord(c):05x}.png'))).convert('RGBA')
                    assert im.height==spec['fonts'][size]['height']
                    if ord(c)>127:assert im.getchannel('A').getbbox() and set(im.getchannel('A').tobytes())<={0,255}
                    width+=im.width+1
                limit=150 if col else 310
                assert width<=limit,(row['id'],text,width,limit)
                widths.append(width)
        records.append({'id':row['id'],'decision':row['decision'],'edited_cells':len(changes),'max_edited_width':max(widths,default=0)})
    for size in spec['fonts']:
        for name in source.namelist():
            if name.startswith(f'base/fonts/pt{size}.fon/') and name.endswith('.png'):
                assert package.read(name.replace('base/','ko/',1))==source.read(name)
    return {'status':'static_passed_runtime_pending','records':len(records),'translated_blocks':sum(bool(r['edited_cells']) for r in records),
            'preserved_blocks':sum(not r['edited_cells'] for r in records),'details':records,
            'limitations':['Runtime scroll, baseline and visual review remain pending.','Original Latin glyphs and unedited names/URLs are retained; Korean glyph alpha is binary.']}
