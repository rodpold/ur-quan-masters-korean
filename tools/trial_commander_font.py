"""Opt-in commander subtitle alpha trial. Does not alter the default patch build."""
import argparse, io, json, math, sys
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import patcher

def build_trial(game, mode='alpha'):
    if mode not in {'alpha','binary'}: raise ValueError('Unknown rendering mode')
    baseline,report=patcher.build(game,'compact')
    with ZipFile(io.BytesIO(baseline)) as z: entries={n:z.read(n) for n in z.namelist()}
    registry=json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
    info=registry['fonts']['DoHyeon']; file=ROOT/info['file']
    if patcher.sha(file.read_bytes())!=info['sha256']: raise ValueError('Font checksum mismatch')
    face=ImageFont.truetype(str(file),12)
    old='ko/fonts/player.fon/'; new='ko/fonts/commander-trial.fon/'
    glyph_names=[n for n in entries if n.startswith(old)]
    chars=[chr(int(Path(n).stem,16)) for n in glyph_names if 0xAC00 <= int(Path(n).stem,16) <= 0xD7A3]
    boxes={c:face.getbbox(c) for c in chars}
    top=min(b[1] for b in boxes.values()); bottom=max(b[3] for b in boxes.values())
    height=bottom-top+3
    notdef=bytes(face.getmask(chr(0x10ffff)))
    levels=set()
    for n in glyph_names:
        c=chr(int(Path(n).stem,16)); dst=new+Path(n).name
        if c not in boxes: entries[dst]=entries[n]; continue
        if not any(face.getmask(c)) or bytes(face.getmask(c))==notdef: raise ValueError('Missing glyph: '+c)
        box=boxes[c]; left=min(0,box[0]); width=max(box[2],math.ceil(face.getlength(c)))-left
        mask=Image.new('L',(width,height))
        ImageDraw.Draw(mask).text((-left,-top),c,font=face,fill=255)
        if mode=='binary': mask=mask.point(lambda p:255 if p>=128 else 0)
        levels.update(mask.tobytes())
        glyph=Image.new('RGBA',mask.size,(255,255,255,0)); glyph.putalpha(mask)
        entries[dst]=patcher.png(glyph)
    if mode=='alpha' and not any(0<x<255 for x in levels): raise ValueError('Alpha trial lost intermediate levels')
    if mode=='binary' and levels!={0,255}: raise ValueError('Binary trial has intermediate levels')
    text=entries['ko-ui.rmp'].decode()
    old_mapping=f'comm.commander.font = FONTRES:addons/{patcher.ADDON}/ko/fonts/player.fon'
    assert text.count(old_mapping)==1
    entries['ko-ui.rmp']=text.replace(old_mapping,f'comm.commander.font = FONTRES:addons/{patcher.ADDON}/ko/fonts/commander-trial.fon').encode()
    entries['ko/licenses/dohyeon/OFL.txt']=(ROOT/info['license_file']).read_bytes()
    entries['ko/licenses/dohyeon/CREDIT.txt']=(f"Do Hyeon / {info['author']}\n{info['source']}\nSIL OFL 1.1. Unmodified font rasterized at 12px for commander subtitles.\n").encode()
    output=io.BytesIO()
    with ZipFile(output,'w',ZIP_DEFLATED) as z:
        for n,data in sorted(entries.items()):
            item=ZipInfo(n,date_time=(2026,1,1,0,0,0));item.compress_type=ZIP_DEFLATED;z.writestr(item,data)
    report.update(files=len(entries),font_trial={'species':'commander','font':'DoHyeon','raster_px':12,'render':mode,'png_height':height,'ink_height':bottom-top,'alpha_levels':len(levels),'base_sha256':patcher.sha(baseline),'visual_status':'pending'})
    return output.getvalue(),report

def install_trial(game, mode, builder=build_trial):
    policy=json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8')).get('rendering_policy',{})
    if mode=='alpha' and policy.get('alpha_allowed') is False:
        raise ValueError('사용자 결정에 따라 반투명 폰트 설치가 비활성화되었습니다. 기본 patcher.py install을 사용하세요.')
    game=patcher.validate_game(game); current=patcher.status(game)
    if current['state']!='installed': raise ValueError('Install the baseline patch first')
    data,report=builder(game,mode);target=patcher.addon_dir(game)
    previous={n:(target/n).read_bytes() for n in ['ko-ui.uqm','manifest.json']}
    backup=ROOT/'artifacts/font-trial-backups'/datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup.mkdir(parents=True)
    for n,b in previous.items(): (backup/n).write_bytes(b)
    meta={'addon':patcher.ADDON,'version':patcher.VERSION,'sha256':patcher.sha(data),'source_sha256':patcher.SUPPORTED_HASH,**report}
    try:
        patcher.atomic_write(target/'ko-ui.uqm',data)
        patcher.atomic_write(target/'manifest.json',(json.dumps(meta,ensure_ascii=False,indent=2)+'\n').encode())
        patcher.status(game)
    except BaseException:
        for n,b in previous.items(): patcher.atomic_write(target/n,b)
        raise
    return {**meta,'backup':str(backup)}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['build','install']);ap.add_argument('--game',required=True,type=Path)
    ap.add_argument('--render',choices=['alpha','binary'],default='alpha');args=ap.parse_args()
    if args.command=='install': result=install_trial(args.game,args.render)
    else:
        data,result=build_trial(args.game,args.render);output=ROOT/'artifacts'/f'commander-{args.render}.uqm';output.parent.mkdir(exist_ok=True);output.write_bytes(data)
        result['output']=str(output)
    print(json.dumps(result,ensure_ascii=False,indent=2))
