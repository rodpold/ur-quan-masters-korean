import io,json
from PIL import Image,ImageDraw,ImageChops,ImageFont
from module_labels import load_modules
from playmenu_headings import ROOT,render_heading
def verify_module_labels(package,source):
    spec=load_modules();assert len(spec['rows'])==16
    assert source.read(spec['source_ani'])==package.read(spec['source_ani'].replace('base/','ko/',1))
    assert spec['resource_key']+' = GFXRES:addons/uqm-korean-ui-poc/ko/ui/modulesmenu.ani' in package.read('ko-ui.rmp').decode().splitlines()
    terms={r['id']:r for r in json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']}
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    missing=bytes(font.getmask(chr(0x10ffff)))
    for i,row in enumerate(spec['rows']):
        p=row['source_path'];old=source.read(p);raw=package.read(p.replace('base/','ko/',1))
        assert raw==render_heading(old,row,font)
        a=Image.open(io.BytesIO(old)).convert('RGBA');b=Image.open(io.BytesIO(raw)).convert('RGBA');assert a.size==b.size
        assert row['box']==[0,0,a.width,11 if i<14 else 10]
        if i<14:assert a.crop((0,11,a.width,a.height)).tobytes()==b.crop((0,11,b.width,b.height)).tobytes(),'Equipment art changed'
        assert set(b.crop(tuple([0,0,a.width,row['box'][3]])).getchannel('A').getdata())<={0,255}
        if 'glossary_id' in row:
            full=terms[row['glossary_id']]['ko']
            if 'compact_label_note' not in row:assert row['text']==full
        for c in row['text']:
            if not c.isspace():assert bytes(font.getmask(c))!=missing and any(bytes(font.getmask(c)))
    assert [(r['text'],r.get('compact_label_note') is not None) for r in spec['rows'] if r.get('compact_label_note')]==[('회전 분사기',True),('추적 장치',True),('근접 방어',True)]
    return {'status':'static_passed_runtime_pending','equipment_labels':14,'transaction_labels':2,'source_layout':'DrawModuleStrings clears 11px above RADAR_Y; original ANI and image dimensions preserved.','limitations':['Actual outfit selection/redraw and price visibility require in-game review.']}
