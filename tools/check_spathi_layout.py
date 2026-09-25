"""Conservative static voice-segment layout estimate, not an engine screenshot test."""
import argparse,io,json,sys
from pathlib import Path
from zipfile import ZipFile
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import patcher

def estimate(game):
    data,_=patcher.build(game)
    with ZipFile(io.BytesIO(data)) as z:
        prefix='ko/fonts/races/spathi.fon/'
        sizes={chr(int(Path(n).stem,16)):Image.open(io.BytesIO(z.read(n))).size for n in z.namelist() if n.startswith(prefix) and n.endswith('.png')}
    width=224 # 320 - 64 status - 14 margins - 2 text offsets - 16 spathi inset
    leading=max(h for w,h in sizes.values())+1
    def measure(text):return sum(sizes[c][0]+1 for c in text)
    translations=json.loads((patcher.ROOT/'translations/dialogue/spathi.ko.json').read_text(encoding='utf-8'))
    rows=[]
    for key,text in translations.items():
        if not key.isupper():continue
        for i,segment in enumerate(text.splitlines(),1):
            lines=[];current=''
            for word in segment.split():
                if measure(word)>width:
                    raise ValueError(f'Overwide word: {key}/{i}: {word}')
                test=(current+' '+word).lstrip()
                if current and measure(test)>width:lines.append(current);current=word
                else:current=test
            if current:lines.append(current)
            rows.append({'id':key,'segment':i,'lines':len(lines),'estimated_bottom':len(lines)*leading+3})
    return {'mode':'static_estimate_pending_in_game','subtitle_width':width,'slider_y':107,'leading':leading,'segments':len(rows),'max_estimated_bottom':max(x['estimated_bottom'] for x in rows),'near_or_below_slider':[x for x in rows if x['estimated_bottom']>=107], 'limitations':['Assumes one original text line per voice subtitle segment.','Word wrapping and glyph spacing are conservative approximations; compare with engine.','Does not cover no-speech pagination, speaker animation overlap, or player options.']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);a=p.parse_args()
    print(json.dumps(estimate(a.game),ensure_ascii=False,indent=2))
