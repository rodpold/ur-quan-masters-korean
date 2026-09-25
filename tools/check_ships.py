"""Check translated ship labels, glossary links and untouched captain ordinals."""
import io,json
from pathlib import Path
from PIL import Image
from inventory_text import blocks
from ship_text import load_ships,compile_ship
ROOT=Path(__file__).resolve().parents[1]

def verify_ships(package,source):
    spec=load_ships();terms={t['id']:t for t in json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']}
    rows=[];pending=0
    assert len(spec['resources'])==25
    for resource in spec['resources']:
        path=resource['source_path'];raw=source.read(path);target=path.replace('base/','ko/',1)
        actual=package.read(target);assert actual==compile_ship(raw,resource)
        before=list(blocks(raw.decode()));after=list(blocks(actual.decode()))
        assert [(a[0],a[1]) for a in before]==[(a[0],a[1]) for a in after]
        assert before[5:]==after[5:]
        assert resource['pending_captain_ids']==[f'{r[0]:04d}' for r in before[5:]]
        pending+=len(before[5:])
        assert [r['id'] for r in resource['records']]==[f'{i:04d}' for i in range(5)]
        for row in resource['records']:
            assert row['ko']==terms[row['glossary_id']]['ko']
            widths={}
            for family in ['starcon','tiny','micro']:
                width=0
                for char in row['ko']:
                    im=Image.open(io.BytesIO(package.read(f'ko/fonts/{family}.fon/{ord(char):05x}.png'))).convert('RGBA')
                    alpha=im.getchannel('A');assert alpha.getbbox() or char==' '
                    if ord(char)>127:assert set(alpha.tobytes())<={0,255}
                    width+=im.width+1
                widths[family]=width
            if row['id']=='0001':assert widths['starcon']<=54,(path,widths)
            rows.append({'source_path':path,'id':row['id'],'ko':row['ko'],'widths':widths})
    assert len(rows)==125 and pending==403
    return {'status':'partial_draft_static_passed_runtime_pending','translated_labels':len(rows),
            'pending_captain_names':pending,'records':rows,
            'limitations':['Index 1 uses the project conservative 54px sidebar budget; other contexts require runtime review.',
                            'Original captain names are still untranslated, not exempted from the full goal.',
                            'Source saves store captain indices; save compatibility still needs in-game verification.']}
