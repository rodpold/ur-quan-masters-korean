import io,json
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw
from ui_text_panels import load_panels
ROOT=Path(__file__).resolve().parents[1]

def verify_control_panels(package,source):
    spec=load_panels();targets={r['source_path']:r for r in spec['panels']};assert len(targets)==34
    composites={r['source_path']:r for r in spec.get('background_composites',[])}
    ui=json.loads((ROOT/'translations/ui.ko.json').read_text(encoding='utf-8'))
    for group in spec['groups']:
        path=group['source_path'];assert source.read(path)==package.read(path.replace('base/','ko/',1))
        for line in source.read(path).decode().splitlines():
            name='base/ui/'+line.split()[0]
            if name not in targets and name not in composites:assert source.read(name)==package.read(name.replace('base/','ko/',1))
    rows=[]
    for name,row in targets.items():
        im=Image.open(io.BytesIO(package.read(name.replace('base/','ko/',1)))).convert('RGBA')
        assert list(im.size)==row['size'] and im.getchannel('A').getextrema()==(255,255)
        colors=set(im.getdata());assert tuple(row['foreground']) in colors and tuple(row['background']) in colors
        assert colors<={tuple(row['foreground']),tuple(row['background']),(145,145,145,255),(58,58,58,255)}
        if 'ui_key' in row:assert row['lines']==[ui[row['ui_key']]]
        rows.append({'source_path':name,'lines':row['lines'],'size':row['size']})
    for name,composite in composites.items():
        original=Image.open(io.BytesIO(source.read(name))).convert('RGBA')
        patched=Image.open(io.BytesIO(package.read(name.replace('base/','ko/',1)))).convert('RGBA')
        assert patched.size==original.size
        diff=ImageChops.difference(original,patched).convert('RGB');draw=ImageDraw.Draw(diff)
        boxes=[]
        for placement in composite['placements']:
            panel=Image.open(io.BytesIO(package.read(placement['panel'].replace('base/','ko/',1)))).convert('RGBA')
            x,y=placement['origin'];box=(x,y,x+panel.width,y+panel.height)
            assert patched.crop(box).tobytes()==panel.tobytes()
            assert all(box[2]<=b[0] or b[2]<=box[0] or box[3]<=b[1] or b[3]<=box[1] for b in boxes)
            boxes.append(box);draw.rectangle((x,y,box[2]-1,box[3]-1),fill=(0,0,0))
        assert diff.getbbox() is None,'Non-button background pixels changed'
    ani=[line.split() for line in source.read('base/ui/meleemenu.ani').decode().splitlines()]
    def bottom(index):return -int(ani[index][4])+targets['base/ui/'+ani[index][0]]['size'][1]
    assert bottom(18)<=-int(ani[17][4]) and bottom(17)<=-int(ani[25][4])
    assert bottom(22)<=-int(ani[21][4]) and bottom(21)<=-int(ani[13][4])
    assert bottom(29)<=240
    assert targets['base/ui/activity-001.png']['lines']==['종료하려면','B 버튼']
    return {'status':'static_passed_runtime_pending','panels':len(rows),'records':rows,
            'limitations':['Ten melee button sprites grow from 5/6px to 7px; width, ANI order and hotspots stay unchanged. Five normal buttons also replace their baked-in background copies.','Native input handling is unchanged; B is the original displayed button identifier.','Runtime visibility and selected-state contrast need in-game review.']}
