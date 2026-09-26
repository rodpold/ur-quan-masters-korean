"""Compile bounded cockpit captions with explicit, checked overlay geometry."""
import hashlib,json,posixpath,io
from PIL import Image,ImageFont
from melee_regions import ROOT,render_regions

def load_cockpit():
    return json.loads((ROOT/'translations/cockpit-labels.ko.json').read_text(encoding='utf-8'))

def render_cockpit(raw,row,font):
    if 'output_size' not in row:return render_regions(raw,row,font)
    if list(Image.open(io.BytesIO(raw)).size)!=row['size']:raise ValueError('Cockpit source dimensions changed')
    if row['size']!=[34,5] or row['output_size']!=[34,7] or row['regions'][0]['box']!=[0,0,34,7]:raise ValueError('Unexpected cockpit expansion')
    im=Image.new('RGBA',tuple(row['output_size']),tuple(row['regions'][0]['background']));out=io.BytesIO();im.save(out,format='PNG')
    return render_regions(out.getvalue(),{**row,'size':row['output_size']},font)

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
