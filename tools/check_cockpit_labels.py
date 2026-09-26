"""Check caption bounds, non-caption pixels, glossary and resource links."""
import io,json,posixpath
from PIL import Image,ImageChops,ImageDraw,ImageFont
from cockpit_labels import ROOT,load_cockpit

def verify_cockpit(package,source):
    spec=load_cockpit();font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    missing=bytes(font.getmask(chr(0x10ffff)))
    terms=json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']
    term=next(t['ko'] for t in terms if t['source']=='Sa-Matra')
    assert len(spec['rows'])==2
    for group in spec['groups']:
        p=group['source_path'];target=p.replace('base/','ko/',1)
        assert source.read(p)==package.read(target)
        assert group['resource_key']+' = GFXRES:addons/uqm-korean-ui-poc/'+target in package.read('ko-ui.rmp').decode().splitlines()
    for row in spec['rows']:
        p=row['source_path'];a=Image.open(io.BytesIO(source.read(p))).convert('RGBA');b=Image.open(io.BytesIO(package.read(p.replace('base/','ko/',1))))
        assert list(a.size)==list(b.size)==row['size'];diff=ImageChops.difference(a,b)
        assert any(c.getbbox() for c in diff.split()),'Caption unchanged'
        for region in row['regions']:
            assert region['text']==term
            x,y,w,h=region['box'];assert 0<=x<x+w<=b.width and 0<=y<y+h<=b.height
            assert set(b.crop((x,y,x+w,y+h)).getchannel('A').getdata())=={255}
            for char in region['text']:assert bytes(font.getmask(char))!=missing and any(bytes(font.getmask(char)))
            ImageDraw.Draw(diff).rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,0))
        assert all(c.getbbox() is None for c in diff.split()),'Non-caption pixels changed'
        if row['usage']=='unreferenced_asset_prepared_only':
            filename=posixpath.basename(p).encode()
            for name in package.namelist():
                if name.endswith(('.ani','.rmp','.txt')):assert filename not in package.read(name)
    return dict(status='static_passed_runtime_pending',images=2,active_images=1,prepared_unlinked_images=1,limitations=['Runtime animation and palette behavior remain unverified.'])
