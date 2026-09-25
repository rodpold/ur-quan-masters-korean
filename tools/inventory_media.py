"""Inventory installed media and resolve UI ANI references, without OCR claims."""
import argparse,hashlib,io,json
from collections import Counter
from pathlib import Path,PurePosixPath
from zipfile import ZipFile
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]

def inventory(game):
    source_path=game/'content/packages/uqm-0.8.0-content.uqm'
    patch_path=game/'content/addons/uqm-korean-ui-poc/ko-ui.uqm'
    with ZipFile(source_path) as z:
        mapping={}
        for line in z.read('uqm.rmp').decode().splitlines():
            if '=' in line:
                key,value=line.split('=',1)
                if value.strip().startswith('GFXRES:'):mapping.setdefault(value.strip().split(':',1)[1],[]).append(key.strip())
        refs={}
        for name in z.namelist():
            if not name.startswith('base/ui/') or not name.endswith('.ani'):continue
            for index,line in enumerate(z.read(name).decode().splitlines()):
                fields=line.split()
                if len(fields)!=5:raise ValueError('Unexpected ANI row: '+name)
                image=str(PurePosixPath(name).parent/fields[0])
                refs.setdefault(image,[]).append({'ani':name,'frame':index,'resource_keys':mapping.get(name,[])})
        patch_names=set()
        if patch_path.is_file():
            with ZipFile(patch_path) as patch:patch_names=set(patch.namelist())
        rows=[]
        for name in sorted(z.namelist()):
            if not name.startswith('base/ui/') or not name.endswith('.png'):continue
            raw=z.read(name);im=Image.open(io.BytesIO(raw))
            rows.append({'source_path':name,'sha256':hashlib.sha256(raw).hexdigest(),'size':list(im.size),
                         'ani_references':refs.get(name,[]),
                         'installed_private_copy':name.replace('base/','ko/',1) in patch_names})
        areas=Counter('/'.join(n.split('/')[:3]) if not n.startswith('base/ui/') else 'base/ui'
                      for n in z.namelist() if n.endswith('.png') and '.fon/' not in n)
    packages=[]
    for path in sorted((game/'content').rglob('*.uqm')):
        if path==patch_path:continue
        with ZipFile(path) as z:
            packages.append({'path':str(path.relative_to(game)).replace('\\','/'),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                             'extensions':dict(sorted(Counter(PurePosixPath(n).suffix for n in z.namelist()).items())),
                             'video_candidates':[n for n in z.namelist() if PurePosixPath(n).suffix.lower() in {'.duk','.avi','.mp4','.mpeg','.mpg','.webm'}],
                             'team_files':[n for n in z.namelist() if n.endswith('.mle')]})
    return {'complete':False,'scope':'Installed content packages and base UI PNG/ANI links',
            'ui_images':rows,'ui_image_count':len(rows),'nonfont_png_areas':dict(sorted(areas.items())),
            'packages':packages,
            'loose_team_files':[str(p.relative_to(game)).replace('\\','/') for p in game.rglob('*.mle')],
            'limitations':['ANI/RMP links show resource wiring, not runtime reachability.',
                            'A private package copy does not imply the pixels were translated or its resource was overridden.',
                            'No OCR or automatic no-text classification is performed.',
                            'Video-like LPF animations and text in unreviewed frames require visual review.',
                            'External/user configuration directories are not scanned for team files.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--write-report',action='store_true');a=p.parse_args()
    report=inventory(a.game)
    if a.write_report:(ROOT/'docs/media-inventory.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'ui_image_count':report['ui_image_count'],'packages':report['packages'],'loose_team_files':report['loose_team_files']},indent=2))
