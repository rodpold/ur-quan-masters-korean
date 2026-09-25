import io,json
from PIL import Image,ImageChops,ImageDraw,ImageFont
from special_labels import ROOT,load_special,render_regions
def verify_special_labels(package,source):
    spec=load_special();assert len(spec['rows'])==5
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8);missing=bytes(font.getmask(chr(0x10ffff)))
    targets={r['source_path'] for r in spec['rows']}
    for group in spec['groups']:
        p=group['source_path'];assert source.read(p)==package.read(p.replace('base/','ko/',1))
        assert group['resource_key']+' = GFXRES:addons/uqm-korean-ui-poc/'+p.replace('base/','ko/',1) in package.read('ko-ui.rmp').decode().splitlines()
        for line in source.read(p).decode().splitlines():
            name='base/ui/'+line.split()[0]
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
    return {'status':'static_passed_runtime_pending','sprites':5,'caption_regions':14,'prepared_only_safex_variants':2,'unchanged_outfit_sprites':55,'limitations':['Two SAFEX=16 variants have no base-package reference; translated assets are prepared but not activated.','Bomb/escape-pod art and ANI positions are preserved; actual outfitting screen and status visibility still need runtime review.']}
