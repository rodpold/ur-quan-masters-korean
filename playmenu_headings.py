"""Compile native 7px headings without changing icon pixels or ANI geometry."""
import hashlib,io,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
def load_headings():
    return json.loads((ROOT/'translations/playmenu-headings.ko.json').read_text(encoding='utf-8'))
def render_heading(raw,row,font):
    if hashlib.sha256(raw).hexdigest()!=row['source_sha256']:raise ValueError('Heading source changed')
    im=Image.open(io.BytesIO(raw)).convert('RGBA')
    if list(im.size)!=row['size']:raise ValueError('Heading dimensions changed')
    x,y,w,h=row['box']
    if x<0 or y<0 or w<=0 or h<=0 or x+w>im.width or y+h>im.height:raise ValueError('Heading box outside image')
    b=font.getbbox(row['text']);mask=Image.new('L',(b[2]-b[0],b[3]-b[1]))
    ImageDraw.Draw(mask).text((-b[0],-b[1]),row['text'],font=font,fill=255)
    mask=mask.point(lambda p:255 if p>=128 else 0)
    if not mask.getbbox() or mask.width>w-2 or mask.height>7 or mask.height>h:raise ValueError('Heading does not fit')
    im.paste((23,23,23,0),(x,y,x+w,y+h))
    im.paste((116,116,116,255),(x+(w-mask.width)//2,y+(h-mask.height)//2),mask)
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()
def add_headings(entries,source):
    spec=load_headings();ani=source.read('base/ui/playmenu.ani')
    if hashlib.sha256(ani).hexdigest()!=spec['ani_sha256']:raise ValueError('Playmenu ANI changed')
    reachable={'base/ui/'+line.split()[0] for line in ani.decode().splitlines()}
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri'/ (spec['font']+'.ttf')),spec['raster_px'])
    seen=set()
    for row in spec['rows']:
        path=row['source_path']
        if path in seen or path not in reachable:raise ValueError('Duplicate or unreachable heading')
        seen.add(path);entries[path.replace('base/','ko/',1)]=render_heading(source.read(path),row,font)
