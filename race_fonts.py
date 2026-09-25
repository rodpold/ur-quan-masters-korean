"""Install the registry's 24 binary Korean race font families into an addon."""
import hashlib,io,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent

def add_race_fonts(entries,rmp,source,chars):
    reg=json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
    groups=[r for r in reg['dialogue_fonts'] if r['id']==r['font_group']]
    report=[]
    for row in groups:
        name=row['candidate_font'];info=reg['fonts'][name];file=ROOT/info['file']
        if hashlib.sha256(file.read_bytes()).hexdigest()!=info['sha256']:raise ValueError('Race font hash changed: '+name)
        f=ImageFont.truetype(str(file),row['candidate_raster_px']);notdef=bytes(f.getmask(chr(0x10ffff)))
        boxes={c:f.getbbox(c) for c in chars};top=min(b[1] for b in boxes.values());bottom=max(b[3] for b in boxes.values());ink=bottom-top
        height=8 if ink<=7 else ink+3
        prefix=row['original_font'].removeprefix('FONTRES:')+'/'
        target=f"ko/fonts/races/{row['id']}.fon/"
        originals=[n for n in source.namelist() if n.startswith(prefix) and n.endswith('.png')]
        if not originals:raise ValueError('Missing original font: '+prefix)
        for n in originals:entries[target+Path(n).name]=source.read(n)
        for c in chars:
            if not any(f.getmask(c)) or bytes(f.getmask(c))==notdef:raise ValueError(f'{name}: missing {c}')
            b=boxes[c];left=min(0,b[0]);width=max(1,b[2]-left,math.ceil(f.getlength(c)))
            mask=Image.new('L',(width,height));ImageDraw.Draw(mask).text((-left,-top),c,font=f,fill=255);mask=mask.point(lambda a:255 if a>=128 else 0)
            if not mask.getbbox():raise ValueError(f'{name}: blank binary glyph {c}')
            image=Image.new('RGBA',mask.size,(255,255,255,0));image.putalpha(mask);out=io.BytesIO();image.save(out,format='PNG');entries[target+f'{ord(c):05x}.png']=out.getvalue()
        key=row['font_resource'];rmp[:]=[line for line in rmp if line.split('=',1)[0].strip()!=key];rmp.append(f"{key} = FONTRES:{target.rstrip('/')}")
        license_files=[info['license_file'],*info.get('additional_licenses',[])]
        if info.get('authors_file'):license_files.append(info['authors_file'])
        for n in dict.fromkeys(license_files):entries['ko/licenses/'+n.removeprefix('vendor/')]=(ROOT/n).read_bytes()
        entries[f'ko/licenses/{name}-CREDIT.txt']=(f"{name} / {info['author']}\n{info['source']}\n{info['license']}\nUnmodified font rasterized as binary glyphs at {row['candidate_raster_px']}px.\n").encode()
        report.append({'group':row['id'],'font':name,'raster_px':row['candidate_raster_px'],'ink_height':ink,'png_height':height,'glyphs':len(chars)})
    return report
