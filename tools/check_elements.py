"""Check element-name glyphs in the lander's seven-pixel line spacing."""
import hashlib,io,json
from pathlib import Path
from PIL import Image
from inventory_text import blocks
ROOT=Path(__file__).resolve().parents[1]

def verify_elements(package,source,spec_name='elements',expected_count=94):
    spec=json.loads((ROOT/f'translations/{spec_name}.ko.json').read_text(encoding='utf-8'))
    raw=source.read(spec['source_path']);assert hashlib.sha256(raw).hexdigest()==spec['source_sha256']
    before=list(blocks(raw.decode()));after=list(blocks(package.read('ko/gamestrings.txt').decode()));rows=[]
    for i in range(spec['first_ordinal'],spec['last_ordinal']+1):
        src=before[i][2];value=after[i][2];assert value==spec['labels'][src]
        widths=[];height=0
        for line in value.split(' ',1):
            width=0
            for char in line:
                im=Image.open(io.BytesIO(package.read(f'ko/fonts/tiny.fon/{ord(char):05x}.png'))).convert('RGBA')
                alpha=im.getchannel('A');bbox=alpha.getbbox()
                assert bbox and set(alpha.tobytes())<={0,255}
                height=max(height,bbox[3]-bbox[1]);width+=im.width+1
            widths.append(width)
        assert height<=7,(i,height)
        rows.append({'id':f'{i:04d}','ko':value,'widths':widths,'max_ink_height':height})
    assert len(rows)==expected_count
    assert after[251][2]=='수은' and after[375][2]=='수성'
    return {'status':'static_passed_runtime_pending','records':len(rows),'labels':rows,'limitations':['Pickup location moves with lander; edge clipping requires runtime review.','No changes to pickup quantities or resource values.']}


def verify_materials(package,source):
    return verify_elements(package,source,'materials',39)
