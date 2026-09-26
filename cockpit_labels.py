"""Compile bounded cockpit captions with explicit, checked overlay geometry."""
import hashlib,json,posixpath,io
from PIL import Image,ImageFont
from melee_regions import ROOT,render_regions

def load_cockpit():
    return json.loads((ROOT/'translations/cockpit-labels.ko.json').read_text(encoding='utf-8'))

def render_cockpit(raw,row,font):
    original=Image.open(io.BytesIO(raw));original.load()
    if original.mode!='P' or list(original.size)!=row['size']:raise ValueError('Indexed cockpit source mismatch')
    size=row.get('output_size',row['size'])
    if size!=row['size']:
        if row['size']!=[34,5] or size!=[34,7] or row['regions'][0]['box']!=[0,0,34,7]:raise ValueError('Unexpected cockpit expansion')
        base=Image.new('RGBA',tuple(size),tuple(row['regions'][0]['background']))
        out=io.BytesIO();base.save(out,format='PNG');render_source=out.getvalue()
    else:render_source=raw
    rendered=Image.open(io.BytesIO(render_regions(render_source,{**row,'size':size},font))).convert('RGBA')
    result=Image.new('P',tuple(size));result.putpalette(original.getpalette())
    result.info=dict(original.info);result.paste(original,(0,0))
    palette=original.getpalette()
    for region in row['regions']:
        bg,fg=region['background_index'],region['foreground_index']
        for index,color in ((bg,region['background']),(fg,region['foreground'])):
            if palette[index*3:index*3+3]!=color[:3] or index==original.info.get('transparency'):raise ValueError('Cockpit palette index mismatch')
        x,y,w,h=region['box']
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                color=rendered.getpixel((xx,yy))
                if color==tuple(region['background']):index=bg
                elif color==tuple(region['foreground']):index=fg
                else:raise ValueError('Unexpected cockpit caption color')
                result.putpixel((xx,yy),index)
    out=io.BytesIO();result.save(out,format='PNG');return out.getvalue()

def add_cockpit(entries,rmp,source):
    spec=load_cockpit();reachable=set()
    for group in spec['groups']:
        p=group['source_path'];raw=source.read(p)
        if hashlib.sha256(raw).hexdigest()!=group['source_sha256']:raise ValueError('Cockpit ANI changed')
        target=p.replace('base/','ko/',1);entries[target]=raw
        if group.get('hotspots'):
            lines=raw.decode().splitlines()
            for frame,hotspot in group['hotspots'].items():
                fields=lines[int(frame)].split();fields[3:]=list(map(str,hotspot));lines[int(frame)]=' '.join(fields)
            entries[target]=('\n'.join(lines)+'\n').encode()
        rmp.append(group['resource_key']+' = GFXRES:'+target)
        for line in raw.decode().splitlines():
            name=posixpath.join(posixpath.dirname(p),line.split()[0]);reachable.add(name)
            entries[name.replace('base/','ko/',1)]=source.read(name)
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    seen=set()
    for row in spec['rows']:
        p=row['source_path'];raw=source.read(p)
        if p in seen or hashlib.sha256(raw).hexdigest()!=row['source_sha256']:raise ValueError('Cockpit sprite changed')
        seen.add(p)
        if p not in reachable:
            if row.get('usage')!='unreferenced_asset_prepared_only':raise ValueError('Unlinked cockpit sprite')
            filename=posixpath.basename(p).encode()
            for name in source.namelist():
                if name.endswith(('.ani','.rmp','.txt')) and filename in source.read(name):raise ValueError('Prepared cockpit variant became referenced')
        entries[p.replace('base/','ko/',1)]=render_cockpit(raw,row,font)
