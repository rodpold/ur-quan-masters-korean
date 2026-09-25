"""Compile equipment labels in the original 11px heading area."""
import hashlib,json
from playmenu_headings import ROOT,render_heading
from PIL import ImageFont
def load_modules():
    return json.loads((ROOT/'translations/module-labels.ko.json').read_text(encoding='utf-8'))
def add_modules(entries,rmp,source):
    spec=load_modules();ani=source.read(spec['source_ani'])
    if hashlib.sha256(ani).hexdigest()!=spec['ani_sha256']:raise ValueError('Module ANI changed')
    paths=['base/ui/'+line.split()[0] for line in ani.decode().splitlines()]
    if paths!=[r['source_path'] for r in spec['rows']]:raise ValueError('Module sprite order changed')
    target=spec['source_ani'].replace('base/','ko/',1);entries[target]=ani
    rmp.append(spec['resource_key']+' = GFXRES:'+target)
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    for row in spec['rows']:
        p=row['source_path'];entries[p.replace('base/','ko/',1)]=render_heading(source.read(p),row,font)
