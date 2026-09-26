from pathlib import Path
import io,json
from PIL import Image,ImageChops,ImageDraw,ImageFont
from special_labels import ROOT,load_special,render_regions
def verify_special_labels(package,source):
    spec=load_special();assert len(spec['rows'])==8
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8);missing=bytes(font.getmask(chr(0x10ffff)))
    targets={r['source_path'] for r in spec['rows']}
    for group in spec['groups']:
        p=group['source_path'];assert source.read(p)==package.read(p.replace('base/','ko/',1))
        assert group['resource_key']+' = GFXRES:addons/uqm-korean-ui-poc/'+p.replace('base/','ko/',1) in package.read('ko-ui.rmp').decode().splitlines()
        for line in source.read(p).decode().splitlines():
            name=str(Path(p).parent/line.split()[0]).replace('\\','/')
            if name not in targets:assert source.read(name)==package.read(name.replace('base/','ko/',1))
    for row in spec['rows']:
        p=row['source_path'];old=source.read(p);new=package.read(p.replace('base/','ko/',1));assert new==render_regions(old,row,font)
        a=Image.open(io.BytesIO(old)).convert('RGBA');b=Image.open(io.BytesIO(new)).convert('RGBA');assert a.size==b.size
        diff=ImageChops.difference(a,b)
        for r in row['regions']:
            x,y,w,h=r['box'];ImageDraw.Draw(diff).rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,0))
            assert set(b.crop((x,y,x+w,y+h)).getchannel('A').getdata())=={255}
            for c in r['text']:
                if not c.isspace():assert bytes(font.getmask(c))!=missing and any(bytes(font.getmask(c)))
        assert all(c.getbbox() is None for c in diff.split()),'Non-caption pixels changed'
    prepared=[r for r in spec['rows'] if r.get('usage')=='unreferenced_asset_prepared_only']
    assert len(prepared)==2
    for row in prepared:
        filename=row['source_path'].split('/')[-1].encode()
        for archive in (source,package):
            for name in archive.namelist():
                if name.endswith(('.ani','.txt','.rmp')):assert filename not in archive.read(name),'Unused SAFEX variant activated'
    assert [r['text'] for r in prepared[1]['regions'][-2:]]==['실행','취소']
    terms={r['id']:r['ko'] for r in json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']}
    assert spec['rows'][0]['regions'][1]['text']==terms['precursors']+' 폭탄'
    assert spec['rows'][0]['regions'][2]['text']==spec['rows'][2]['regions'][1]['text']==terms['escape_pod']
    assert spec['rows'][1]['regions'][0]['text']==json.loads((ROOT/'translations/ui.ko.json').read_text(encoding='utf-8'))['UNLIMITED']
    lander=next(r for r in spec['rows'] if r['source_path']=='base/lander/lander-032.png')
    ui=json.loads((ROOT/'translations/ui.ko.json').read_text(encoding='utf-8'))
    assert [r['text'] for r in lander['regions']]==[ui['mineral'],ui['biological']]
    # ANI hotspot (-1,-1) places this panel at radar (1,1).
    boxes=[(r['box'][0]+1,r['box'][1]+1,r['box'][0]+1+r['box'][2],r['box'][1]+1+r['box'][3]) for r in lander['regions']]
    frames=[line.split() for line in source.read('base/lander/lander.ani').decode().splitlines()]
    assert frames[32][3:]==['-1','-1']
    def separated(a,b):return a[2]<=b[0] or b[2]<=a[0] or a[3]<=b[1] or b[3]<=a[1]
    for i in list(range(33,41))+[57,58,59]:
        f=frames[i];w,h=Image.open(io.BytesIO(source.read('base/lander/'+f[0]))).size
        x,y=-int(f[3]),-int(f[4]);assert all(separated(b,(x,y,x+w,y+h)) for b in boxes)
    for i in (41,42,43,44):
        f=frames[i];w,h=Image.open(io.BytesIO(source.read('base/lander/'+f[0]))).size
        x=-int(f[3]);assert all(b[2]<=x or x+w<=b[0] for b in boxes),'Moving hold bar overlaps label'
    for i in (55,56):
        f=frames[i];w,h=Image.open(io.BytesIO(source.read('base/lander/'+f[0]))).size
        for crew in range(12):
            x=11+6*(crew%6)-int(f[3]);y=35-6*(crew//6)-int(f[4])
            assert all(separated(b,(x,y,x+w,y+h)) for b in boxes)
    assert all(b[0]>=5 and b[2]<=51 and b[3]<=53 for b in boxes),'Radar bounds / storage-mask overlap'
    hud=next(r for r in spec['rows'] if r['source_path']=='base/ui/flagshipstatus-000.png')
    assert [r['text'] for r in hud['regions']]==[ui['CAPTAIN'],ui['FUEL'],ui['CREW']]
    assert [r['box'] for r in hud['regions']]==[[2,1,58,7],[18,29,26,7],[18,108,26,7]]
    assert source.read('base/ui/flagshipstatus.ani').decode().splitlines()[0].split()[3:]==['-1','-1']
    hud_image=Image.open(io.BytesIO(package.read('ko/ui/flagshipstatus-000.png'))).convert('RGBA')
    for region in hud['regions']:
        start=31-((9*len(region['text'])-1)//2)
        for i,c in enumerate(region['text']):
            glyph=Image.open(io.BytesIO(package.read(f'ko/fonts/tiny.fon/{ord(c):05x}.png'))).convert('RGBA')
            alpha=glyph.getchannel('A').crop((0,0,8,7))
            expected=Image.new('RGBA',(8,7),tuple(region['background']))
            expected.paste(tuple(region['foreground']),(0,0),alpha)
            assert hud_image.crop((start+i*9,region['box'][1],start+i*9+8,region['box'][1]+7)).tobytes()==expected.tobytes(),'HUD does not match dynamic TinyFont'
    # Image origin is status (1,1). Caption bottoms precede dynamic name/fuel/crew clears.
    for region,clear_y in zip(hud['regions'],[10,38,117]):
        assert region['box'][1]+1+region['box'][3]<=clear_y
    return {'status':'static_passed_runtime_pending','sprites':8,'caption_regions':21,'hud_caption_regions':3,'prepared_only_safex_variants':2,'unchanged_outfit_sprites':55,'orbit_entry_captions':2,'lander_caption_regions':2,'unchanged_lander_sprites':59,'limitations':['Two SAFEX=16 variants have no base-package reference; translated assets are prepared but not activated.','Bomb/escape-pod art and ANI positions are preserved; actual outfitting screen and status visibility still need runtime review.']}
