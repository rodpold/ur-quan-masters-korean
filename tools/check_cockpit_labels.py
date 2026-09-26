"""Check caption bounds, non-caption pixels, glossary and resource links."""
import io,json,posixpath
from PIL import Image,ImageChops,ImageDraw,ImageFont
from cockpit_labels import ROOT,load_cockpit

def verify_cockpit(package,source):
    spec=load_cockpit();font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    missing=bytes(font.getmask(chr(0x10ffff)))
    terms=json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']
    term=next(t['ko'] for t in terms if t['source']=='Sa-Matra')
    assert len(spec['rows'])==12
    for group in spec['groups']:
        p=group['source_path'];target=p.replace('base/','ko/',1)
        assert source.read(p)==package.read(target)
        assert group['resource_key']+' = GFXRES:addons/uqm-korean-ui-poc/'+target in package.read('ko-ui.rmp').decode().splitlines()
    for row in spec['rows']:
        p=row['source_path'];a=Image.open(io.BytesIO(source.read(p))).convert('RGBA');b=Image.open(io.BytesIO(package.read(p.replace('base/','ko/',1))))
        assert list(a.size)==list(b.size)==row['size'];diff=ImageChops.difference(a,b)
        assert any(c.getbbox() for c in diff.split()),'Caption unchanged'
        for region in row['regions']:
            assert region['text']==(term if '/samatra/' in p else '자폭')
            x,y,w,h=region['box'];assert 0<=x<x+w<=b.width and 0<=y<y+h<=b.height
            assert set(b.crop((x,y,x+w,y+h)).getchannel('A').getdata())=={255}
            for char in region['text']:assert bytes(font.getmask(char))!=missing and any(bytes(font.getmask(char)))
            ImageDraw.Draw(diff).rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,0))
        assert all(c.getbbox() is None for c in diff.split()),'Non-caption pixels changed'
        if row['usage']=='unreferenced_asset_prepared_only':
            filename=posixpath.basename(p).encode()
            for name in package.namelist():
                if name.endswith(('.ani','.rmp','.txt')):assert filename not in package.read(name)
    # Every self-destruct animation state must cover the same caption box,
    # leaving the original counter and warning light (x >= 33) unchanged.
    rows={row['source_path']:row for row in spec['rows']}
    for stem,count in [('scout',20),('oldscout',15)]:
        ani='base/ships/shofixti/'+stem+'-cap.ani'
        lines=source.read(ani).decode().splitlines();assert len(lines)==count
        for i,line in enumerate(lines):
            fields=line.split();name=posixpath.join(posixpath.dirname(ani),fields[0]);target=name.replace('base/','ko/',1)
            if name not in rows:assert source.read(name)==package.read(target)
            else:
                region=rows[name]['regions'][0];assert region['box']==[0,23 if i==0 else 0,33,7]
                if i>=12:assert fields[3:]==['0','-23']
    for i in range(12,20):
        region=rows[f'base/ships/shofixti/scout-cap-{i:03}.png']['regions'][0]
        assert region['foreground']==([252,84,84,255] if i>=18 else [252,252,84,255] if i>=16 else [168,168,168,255])
    return dict(status='static_passed_runtime_pending',images=12,active_images=11,prepared_unlinked_images=1,limitations=['Runtime animation and palette behavior remain unverified.'])
