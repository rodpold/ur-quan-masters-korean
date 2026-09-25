"""Two-line shipyard captions extend four pixels into the cleared radar."""
import io,json,hashlib
from pathlib import Path
from PIL import Image,ImageFont,ImageDraw
ROOT=Path(__file__).resolve().parent
def load_shipyard():
    return json.loads((ROOT/'translations/shipyard-labels.ko.json').read_text(encoding='utf-8'))
def render_label(row):
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8);w,h=row['size'];lines=row['lines']
    im=Image.new('RGBA',(w,h),(82,82,82,255));total=len(lines)*7+len(lines)-1
    if not lines or total>h:raise ValueError('Shipyard label height overflow')
    y=(h-total)//2;missing=bytes(font.getmask(chr(0x10ffff)))
    for text in lines:
        for c in text:
            if not c.isspace() and (bytes(font.getmask(c))==missing or not any(bytes(font.getmask(c)))):raise ValueError('Missing shipyard glyph')
        b=font.getbbox(text);mask=Image.new('L',(b[2]-b[0],b[3]-b[1]));ImageDraw.Draw(mask).text((-b[0],-b[1]),text,font=font,fill=255);mask=mask.point(lambda p:255 if p>=128 else 0)
        if mask.width>w or mask.height>7:raise ValueError('Shipyard label width/ink overflow')
        im.paste((232,232,232,255),((w-mask.width)//2,y+(7-mask.height)//2),mask);y+=8
    b=io.BytesIO();im.save(b,format='PNG');return b.getvalue()
def add_shipyard(entries,rmp,source):
    spec=load_shipyard();p=spec['source_ani'];raw=source.read(p)
    if hashlib.sha256(raw).hexdigest()!=spec['ani_sha256']:raise ValueError('Shipyard ANI changed')
    lines=raw.decode().splitlines();rows={r['frame']:r for r in spec['rows']}
    for i,line in enumerate(lines):
        fields=line.split();name='base/ui/'+fields[0];data=source.read(name)
        if i in rows:
            row=rows[i]
            if name!=row['source_path'] or hashlib.sha256(data).hexdigest()!=row['source_sha256']:raise ValueError('Shipyard image mismatch')
            if list(Image.open(io.BytesIO(data)).size)!=row['source_size']:raise ValueError('Shipyard source size changed')
            fields[3:]=[str(n) for n in row['hotspot']];lines[i]=' '.join(fields);data=render_label(row)
        entries[name.replace('base/','ko/',1)]=data
    target=p.replace('base/','ko/',1);entries[target]=('\n'.join(lines)+'\n').encode();rmp.append(spec['resource_key']+' = GFXRES:'+target)
