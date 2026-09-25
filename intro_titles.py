"""Translate intro connector words while preserving logos and creator names."""
import io,json,hashlib
from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
ROOT=Path(__file__).resolve().parent
def load_titles():
    return json.loads((ROOT/'translations/intro-titles.ko.json').read_text(encoding='utf-8'))
def render_title(raw,row):
    if hashlib.sha256(raw).hexdigest()!=row['source_sha256']:raise ValueError('Intro title source changed')
    im=Image.open(io.BytesIO(raw)).convert('RGBA')
    if list(im.size)!=row['size']:raise ValueError('Intro title size changed')
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri'/(row['font']+'.ttf')),row['raster_px'])
    missing=bytes(font.getmask(chr(0x10ffff)))
    for region in row['regions']:
        text=region['text'];x,y,w,h=region['box'];b=font.getbbox(text)
        for c in text:
            if not c.isspace() and (bytes(font.getmask(c))==missing or not any(bytes(font.getmask(c)))):raise ValueError('Missing title glyph')
        mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),text,font=font,fill=255);mask=mask.point(lambda p:255 if p>=128 else 0)
        if x<0 or y<0 or x+w>im.width or y+h>im.height or mask.width>w or mask.height>h:raise ValueError('Intro title overflow')
        im.paste((0,0,0,255),(x,y,x+w,y+h));im.paste((255,255,255,255),(x+(w-mask.width)//2,y+(h-mask.height)//2),mask)
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()
def add_titles(entries,source,addon):
    spec=load_titles();p=spec['source_ani'];raw=source.read(p)
    if hashlib.sha256(raw).hexdigest()!=spec['ani_sha256']:raise ValueError('Intro title ANI changed')
    entries[p.replace('base/','ko/',1)]=raw
    for line in raw.decode().splitlines():
        name='base/cutscene/intro/'+line.split()[0];entries[name.replace('base/','ko/',1)]=source.read(name)
    for row in spec['rows']:
        name=row['source_path'];entries[name.replace('base/','ko/',1)]=render_title(source.read(name),row)
    return {'ANI '+p:'ANI addons/'+addon+'/'+p.replace('base/','ko/',1)}
