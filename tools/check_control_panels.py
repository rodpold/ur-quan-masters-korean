import io,json
from pathlib import Path
from PIL import Image
from ui_text_panels import load_panels
ROOT=Path(__file__).resolve().parents[1]

def verify_control_panels(package,source):
    spec=load_panels();targets={r['source_path']:r for r in spec['panels']};assert len(targets)==24
    for group in spec['groups']:
        path=group['source_path'];assert source.read(path)==package.read(path.replace('base/','ko/',1))
        for line in source.read(path).decode().splitlines():
            name='base/ui/'+line.split()[0]
            if name not in targets:assert source.read(name)==package.read(name.replace('base/','ko/',1))
    rows=[]
    for name,row in targets.items():
        im=Image.open(io.BytesIO(package.read(name.replace('base/','ko/',1)))).convert('RGBA')
        assert list(im.size)==row['size'] and im.getchannel('A').getextrema()==(255,255)
        colors=set(im.getdata());assert tuple(row['foreground']) in colors and tuple(row['background']) in colors
        assert colors<={tuple(row['foreground']),tuple(row['background']),(145,145,145,255),(58,58,58,255)}
        rows.append({'source_path':name,'lines':row['lines'],'size':row['size']})
    assert targets['base/ui/activity-001.png']['lines']==['종료하려면','B 버튼']
    return {'status':'static_passed_runtime_pending','panels':len(rows),'records':rows,
            'limitations':['Sprite sizes, ANI frame order/hotspots and unedited sprites are preserved.','Native input handling is unchanged; B is the original displayed button identifier.','Runtime visibility and selected-state contrast need in-game review.']}
