"""Compile special equipment captions without changing sprites or positions."""
import hashlib,json,io
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from melee_regions import ROOT,render_regions as render_base_regions
def render_regions(raw,row,font):
    result=render_base_regions(raw,row,font)
    if row['source_path']!='base/ui/flagshipstatus-000.png':return result
    # Match TinyFont's 8px glyph + 1px advance and TextRect's final -1 width.
    # DrawPC_SIS redraws these same pixels; its 5px clears must not leave ghosts.
    im=Image.open(io.BytesIO(result)).convert('RGBA')
    for region in row['regions']:
        x,y,w,h=region['box'];im.paste(tuple(region['background']),(x,y,x+w,y+h))
        start=31-((9*len(region['text'])-1)//2)
        for i,char in enumerate(region['text']):
            b=font.getbbox(char);mask=Image.new('L',(b[2]-b[0],b[3]-b[1]))
            ImageDraw.Draw(mask).text((-b[0],-b[1]),char,font=font,fill=255)
            mask=mask.point(lambda p:255 if p>=128 else 0)
            assert mask.size==(8,7) and x<=start+i*9 and start+i*9+8<=x+w
            im.paste(tuple(region['foreground']),(start+i*9,y),mask)
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()


def load_special():
    return json.loads((ROOT/'translations/special-labels.ko.json').read_text(encoding='utf-8'))
def add_special(entries,rmp,source):
    spec=load_special();reachable=set()
    for group in spec['groups']:
        p=group['source_path'];raw=source.read(p)
        if hashlib.sha256(raw).hexdigest()!=group['source_sha256']:raise ValueError('Special ANI changed')
        target=p.replace('base/','ko/',1);entries[target]=raw
        rmp.append(group['resource_key']+' = GFXRES:'+target)
        for line in raw.decode().splitlines():
            name=str(Path(p).parent/line.split()[0]).replace('\\','/');reachable.add(name);entries[name.replace('base/','ko/',1)]=source.read(name)
    reachable.update('base/ui/'+line.split()[0] for line in source.read('base/ui/playmenu.ani').decode().splitlines())
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8);seen=set()
    for row in spec['rows']:
        p=row['source_path'];raw=source.read(p)
        if (p not in reachable and row.get('usage')!='unreferenced_asset_prepared_only') or p in seen or hashlib.sha256(raw).hexdigest()!=row['source_sha256']:raise ValueError('Special sprite source mismatch')
        if row.get('usage')=='unreferenced_asset_prepared_only':
            filename=Path(p).name.encode()
            for name in source.namelist():
                if name.endswith(('.ani','.txt','.rmp')) and filename in source.read(name):raise ValueError('Prepared-only asset has a reference')
        seen.add(p);entries[p.replace('base/','ko/',1)]=render_regions(raw,row,font)
