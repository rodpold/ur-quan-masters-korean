"""Check translated ship labels, glossary links and untouched captain ordinals."""
import io,json,re
from pathlib import Path
from PIL import Image
from inventory_text import blocks
from ship_text import load_ships,compile_ship
ROOT=Path(__file__).resolve().parents[1]

def verify_ships(package,source):
    spec=load_ships();terms={t['id']:t for t in json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']}
    captain_data=json.loads((ROOT/'translations/captain-names.ko.json').read_text(encoding='utf-8'))
    captains={r['id']:r for r in captain_data['entries']}
    assert len(captains)==len(captain_data['entries'])==403
    concepts={r['source']:r['ko'] for r in json.loads((ROOT/'translations/orz-concepts.ko.json').read_text(encoding='utf-8'))['concepts']}
    rows=[];pending=0;preserved=0;seen=set()
    assert len(spec['resources'])==25
    for resource in spec['resources']:
        path=resource['source_path'];raw=source.read(path);target=path.replace('base/','ko/',1)
        actual=package.read(target);assert actual==compile_ship(raw,resource)
        before=list(blocks(raw.decode()));after=list(blocks(actual.decode()))
        assert [(a[0],a[1]) for a in before]==[(a[0],a[1]) for a in after]
        assert resource['pending_captain_ids']==[]
        pending+=len(resource['pending_captain_ids'])
        assert [r['id'] for r in resource['records']]==[f'{i:04d}' for i in range(len(before))]
        for row in resource['records']:
            if int(row['id'])<5:
                assert row['ko']==terms[row['glossary_id']]['ko']
            else:
                entry=captains[row['captain_id']];seen.add(entry['id'])
                assert (entry['source_path'],entry['ordinal'],entry['source'],entry['ko'],entry['decision'])==(path,row['id'],row['source'],row['ko'],row['decision'])
                assert re.findall(r'\d+',row['source'])==re.findall(r'\d+',row['ko'])
                assert row['source'].count('*')==row['ko'].count('*')
                if 'glossary_id' in entry:assert entry['ko']==terms[entry['glossary_id']]['ko']
                if 'orz_concept' in entry:assert entry['ko']=='*'+concepts[entry['orz_concept']]+'*'
                if entry['decision']=='preserve_alphanumeric_identifier':
                    assert entry['ko']==entry['source'] and entry['status']=='preserve'
                    preserved+=1
                else:assert entry['decision']=='translated_draft' and entry['status']=='in_use'
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
            if int(row['id'])>=5:assert widths['tiny']<=60,(path,row['id'],widths)
            rows.append({'source_path':path,'id':row['id'],'ko':row['ko'],'widths':widths})
    assert len(rows)==528 and pending==0 and preserved==32 and seen==set(captains)
    return {'status':'draft_static_passed_runtime_pending','translated_labels':125,'translated_captain_names':403-preserved,'preserved_captain_identifiers':preserved,
            'pending_captain_names':pending,'records':rows,
            'limitations':['Index 1 uses the project conservative 54px sidebar budget; other contexts require runtime review.',
                            'Captain name widths use a 60px budget within the source 64px status area; linguistic and runtime review remain.',
                            'Source saves store captain indices; save compatibility still needs in-game verification.']}
