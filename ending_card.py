"""Compile a Korean ending title while retaining the copyright artwork."""
import hashlib,io,json
from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
ROOT=Path(__file__).resolve().parent
def load_card():
    return json.loads((ROOT/'translations/ending-card.ko.json').read_text(encoding='utf-8'))
def render_card(raw,spec):
    if hashlib.sha256(raw).hexdigest()!=spec['source_sha256']:raise ValueError('Ending card changed')
    im=Image.open(io.BytesIO(raw)).convert('RGBA')
    if list(im.size)!=spec['size']:raise ValueError('Ending card size changed')
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri'/(spec['font']+'.ttf')),spec['raster_px'])
    b=font.getbbox(spec['text']);mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),spec['text'],font=font,fill=255)
    mask=mask.point(lambda p:255 if p>=128 else 0);scale=spec['scale']
    if scale!=2:raise ValueError('Expected integer 2x title scale')
    mask=mask.resize((mask.width*scale,mask.height*scale),Image.Resampling.NEAREST)
    x,y,w,h=spec['box']
    if x<0 or y<0 or x+w>im.width or y+h>im.height or mask.width>w or mask.height>h:raise ValueError('Ending title does not fit')
    im.paste((0,0,0,255),(x,y,x+w,y+h));im.paste((255,255,255,255),(x+(w-mask.width)//2,y+(h-mask.height)//2),mask)
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()
def add_card(entries,source,addon):
    spec=load_card();p=spec['source_ani'];raw=source.read(p)
    if hashlib.sha256(raw).hexdigest()!=spec['ani_sha256']:raise ValueError('Ending ANI changed')
    entries[p.replace('base/','ko/',1)]=raw;reachable=set()
    for line in raw.decode().splitlines():
        name=str(Path(p).parent/line.split()[0]).replace('\\','/');reachable.add(name)
        entries[name.replace('base/','ko/',1)]=source.read(name)
    p=spec['source_path']
    if p not in reachable:raise ValueError('Unreachable ending card')
    entries[p.replace('base/','ko/',1)]=render_card(source.read(p),spec)
    return {'ANI '+spec['source_ani']:'ANI addons/'+addon+'/'+spec['source_ani'].replace('base/','ko/',1)}
