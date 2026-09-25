"""Compile Korean text-only UI panels at the original sprite dimensions."""
import hashlib,io,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent

def load_panels():
    return json.loads((ROOT/'translations/control-panels.ko.json').read_text(encoding='utf-8'))

def render_panel(row,font):
    width,height=row['size'];masks=[]
    for text in row['lines']:
        box=font.getbbox(text);mask=Image.new('L',(box[2]-box[0],box[3]-box[1]))
        ImageDraw.Draw(mask).text((-box[0],-box[1]),text,font=font,fill=255)
        mask=mask.point(lambda p:255 if p>=128 else 0)
        if mask.width>width-2 or mask.height>7:raise ValueError('Control panel text does not fit: '+text)
        masks.append(mask)
    total=sum(m.height for m in masks)+3*(len(masks)-1)
    if not masks or total>height-2:raise ValueError('Control panel rows do not fit')
    im=Image.new('RGBA',(width,height),tuple(row['background']));d=ImageDraw.Draw(im)
    if row['style']=='bevel':
        d.line((0,height-1,0,0,width-1,0),fill=(145,145,145,255))
        d.line((width-1,0,width-1,height-1,0,height-1),fill=(58,58,58,255))
    y=(height-total)//2
    for mask in masks:
        im.paste(tuple(row['foreground']),((width-mask.width)//2,y,(width+mask.width)//2,y+mask.height),mask)
        y+=mask.height+3
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()

def add_panels(entries,rmp,source,spec):
    reachable=set()
    for group in spec['groups']:
        path=group['source_path'];raw=source.read(path)
        if hashlib.sha256(raw).hexdigest()!=group['source_sha256']:raise ValueError('Panel ANI changed')
        target=path.replace('base/','ko/',1);entries[target]=raw
        for line in raw.decode().splitlines():
            fields=line.split()
            if len(fields)!=5:raise ValueError('Invalid panel ANI')
            name=str(Path(path).parent/fields[0]).replace('\\','/');reachable.add(name)
            entries[name.replace('base/','ko/',1)]=source.read(name)
        rmp.append(group['resource_key']+' = GFXRES:'+target)
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri'/(spec['font']['family']+'.ttf')),spec['font']['raster_px'])
    seen=set()
    for row in spec['panels']:
        path=row['source_path'];raw=source.read(path)
        if path not in reachable or path in seen or hashlib.sha256(raw).hexdigest()!=row['source_sha256']:raise ValueError('Panel source mismatch')
        if list(Image.open(io.BytesIO(raw)).size)!=row['size']:raise ValueError('Panel dimensions changed')
        seen.add(path);entries[path.replace('base/','ko/',1)]=render_panel(row,font)
