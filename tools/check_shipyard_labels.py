import json,io,hashlib
from pathlib import Path
from PIL import Image
from shipyard_labels import ROOT,load_shipyard,render_label
def verify_shipyard(package,source):
    spec=load_shipyard();rows={r['frame']:r for r in spec['rows']};assert set(rows)==set(range(3,24))
    old=[l.split() for l in source.read(spec['source_ani']).decode().splitlines()];new=[l.split() for l in package.read('ko/ui/shipyard.ani').decode().splitlines()];assert len(old)==len(new)==25
    ships={r['resource_key']:r for r in json.loads((ROOT/'translations/ships.ko.json').read_text(encoding='utf-8'))['resources']}
    resources={l.split(' = ')[0]:l.split(' = ')[1] for l in source.read('uqm.rmp').decode().splitlines() if ' = ' in l};checks=[]
    assert 'graphics.shipyard = GFXRES:addons/uqm-korean-ui-poc/ko/ui/shipyard.ani' in package.read('ko-ui.rmp').decode().splitlines()
    for i,(a,b) in enumerate(zip(old,new)):
        p='base/ui/'+a[0]
        if i not in rows:
            assert a==b and source.read(p)==package.read(p.replace('base/','ko/',1));continue
        row=rows[i];assert a[:3]==b[:3] and b[3:]==['0','11']
        ship=ships[row['ship_resource']];refs={r['id']:r['ko'] for r in ship['records']};assert row['lines']==[refs[k] for k in row['record_ids']]
        assert row['size']==[56,15 if len(row['lines'])==2 else 11]
        raw=package.read(p.replace('base/','ko/',1));assert raw==render_label(row)
        assert set(Image.open(io.BytesIO(raw)).convert('RGBA').getdata())<={(82,82,82,255),(232,232,232,255)}
        ani=resources['ship.'+row['race']+'.meleeicons'].split(':',1)[1];tops=[]
        for line in source.read(ani).decode().splitlines():
            f=line.split();top=26-int(f[4]);tops.append(top)
            assert row['size'][1]-11<=top,'Caption overlaps a melee icon bounding box'
        checks.append({'frame':i,'lines':row['lines'],'caption_bottom_relative_to_radar':row['size'][1]-11,'earliest_icon_top':min(tops),'icon_ani':ani,'icon_ani_sha256':hashlib.sha256(source.read(ani)).hexdigest()})
    return {'status':'static_passed_runtime_pending','labels':21,'radar_size':[56,53],'minimum_icon_top':min(r['earliest_icon_top'] for r in checks),'records':checks,'limitations':['Based on fixed public shipyard.c/units.h draw and clear geometry; installed executable behavior still needs runtime review.','One-row original placeholders retain one row; race names are expanded using existing ship text translations.']}
