"""Static checks of the source renderer's first-space, two-line device labels."""
import io,json
from pathlib import Path
from PIL import Image
from inventory_text import blocks
ROOT=Path(__file__).resolve().parents[1]

def verify_devices(package,source):
    spec=json.loads((ROOT/'translations/device-labels.ko.json').read_text(encoding='utf-8'))
    before=list(blocks(source.read(spec['source_path']).decode()))
    after=list(blocks(package.read('ko/gamestrings.txt').decode()))
    constraints=spec['constraints'];rows=[]
    for i in range(spec['first_ordinal'],spec['last_ordinal']+1):
        original=before[i][2];value=after[i][2]
        assert before[i][:2]==after[i][:2] and value==spec['labels'][original]
        assert ' ' in value and '\n' not in value
        first,second=value.split(' ',1)
        assert first and second
        widths=[];max_ink=0
        for line in [first,second]:
            width=0
            for char in line:
                im=Image.open(io.BytesIO(package.read(f'ko/fonts/tiny.fon/{ord(char):05x}.png'))).convert('RGBA')
                alpha=im.getchannel('A');assert set(alpha.tobytes())<={0,255}
                bbox=alpha.getbbox()
                if char!=' ':assert bbox,('Empty device glyph',char)
                if bbox:max_ink=max(max_ink,bbox[3]-bbox[1])
                width+=im.width+1
            widths.append(width)
        assert max(widths)<=constraints['safe_line_width'],(i,value,widths)
        assert max_ink<=constraints['max_ink_height'],(i,max_ink)
        rows.append({'id':f'{i:04d}','lines':[first,second],'widths':widths,'max_ink_height':max_ink})
    return {'status':'static_passed_runtime_pending','records':len(rows),'labels':rows,
            'limitations':['Spacing uses a conservative extra pixel per glyph.','No proof of selection background, icons, or scrolling in installed executable.']}
