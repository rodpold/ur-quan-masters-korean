"""Compile special equipment captions without changing sprites or positions."""
import hashlib,json
from pathlib import Path
from PIL import ImageFont
from melee_regions import ROOT,render_regions
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
