"""Seven-pixel outline-alpha trial for starcon/tiny; restores baseline dialogue fonts."""
import argparse,io,json,sys
from pathlib import Path
from zipfile import ZipFile,ZipInfo,ZIP_DEFLATED
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import patcher
from trial_commander_font import install_trial

def build_trial(game,mode='alpha'):
    if mode not in {'alpha','binary'}:raise ValueError('Unknown rendering mode')
    data,report=patcher.build(game,'compact')
    with ZipFile(io.BytesIO(data)) as z: entries={n:z.read(n) for n in z.namelist()}
    info=json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))['fonts']['DoHyeon']
    file=ROOT/info['file']
    if patcher.sha(file.read_bytes())!=info['sha256']:raise ValueError('Font hash mismatch')
    face=ImageFont.truetype(str(file),32)
    names=[n for n in entries if n.startswith(('ko/fonts/starcon.fon/','ko/fonts/tiny.fon/')) and n.endswith('.png') and 0xac00<=int(Path(n).stem,16)<=0xd7a3]
    chars={chr(int(Path(n).stem,16)) for n in names}
    boxes={c:face.getbbox(c) for c in chars};top=min(b[1] for b in boxes.values());bottom=max(b[3] for b in boxes.values())
    width=max(b[2]-min(0,b[0]) for b in boxes.values());height=bottom-top
    scale=min(7/width,7/height);target=(max(1,round(width*scale)),max(1,round(height*scale)))
    masks={};levels=set();notdef=bytes(face.getmask(chr(0x10ffff)))
    for c in chars:
        if bytes(face.getmask(c))==notdef:raise ValueError('Missing glyph: '+c)
        mask=Image.new('L',(width,height));ImageDraw.Draw(mask).text((-min(0,boxes[c][0]),-top),c,font=face,fill=255)
        mask=mask.resize(target,Image.Resampling.LANCZOS)
        if mode=='binary':mask=mask.point(lambda p:255 if p>=128 else 0)
        out=Image.new('L',(8,8));out.paste(mask,(0,7-target[1]));masks[c]=out;levels.update(out.tobytes())
        assert out.getbbox() and out.getbbox()[3]<=7
    for n in names:
        glyph=Image.new('RGBA',(8,8),(255,255,255,0));glyph.putalpha(masks[chr(int(Path(n).stem,16))]);entries[n]=patcher.png(glyph)
    if mode=='alpha':assert any(0<a<255 for a in levels)
    else:assert levels=={0,255}
    entries['ko/licenses/dohyeon/OFL.txt']=(ROOT/info['license_file']).read_bytes()
    entries['ko/licenses/dohyeon/CREDIT.txt']=(f"Do Hyeon / {info['author']}\n{info['source']}\nUnmodified OFL font. Rasterized at 32px and area-fitted to a maximum 7x7px ink box with Lanczos resampling for UI trial.\n").encode()
    output=io.BytesIO()
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for n,b in sorted(entries.items()):
            item=ZipInfo(n,date_time=(2026,1,1,0,0,0));item.compress_type=ZIP_DEFLATED;z.writestr(item,b)
    report.update(files=len(entries),font_trial={'id':'ui7-alpha','families':['starcon','tiny'],'font':'DoHyeon','render':mode,'source_raster_px':32,'ink_box':list(target),'png_size':[8,8],'advance_px':9,'alpha_levels':len(levels),'changed_glyphs':len(names),'dialogue':'baseline Galmuri9','visual_status':'pending'})
    return output.getvalue(),report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['build','install']);p.add_argument('--game',required=True,type=Path);p.add_argument('--render',choices=['alpha','binary'],default='alpha');a=p.parse_args()
    if a.command=='install':result=install_trial(a.game,a.render,builder=build_trial)
    else:
        data,result=build_trial(a.game,a.render);output=ROOT/'artifacts'/f'ui7-{a.render}.uqm';output.parent.mkdir(exist_ok=True);output.write_bytes(data);result['output']=str(output)
    print(json.dumps(result,ensure_ascii=False,indent=2))
