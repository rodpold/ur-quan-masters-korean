"""Credit-cell translation, retaining format instructions and unedited names."""
import hashlib,io,json,re
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
HEADER=re.compile(r'^#\([^\r\n]*\)[^\r\n]*\r?\n',re.M)

def load_credits():
    return json.loads((ROOT/'translations/credits.ko.json').read_text(encoding='utf-8'))

def compile_credits(raw,spec):
    if hashlib.sha256(raw).hexdigest()!=spec['source_sha256']:raise ValueError('Credit source hash mismatch')
    text=raw.decode();matches=list(HEADER.finditer(text));records={r['id']:r for r in spec['records']};seen=set();changes=[]
    if len(records)!=len(spec['records']):raise ValueError('Duplicate credit record')
    for index,m in enumerate(matches):
        end=matches[index+1].start() if index+1<len(matches) else len(text)
        body=text[m.end():end];clean=body.rstrip('\r\n');key=f'{index:04d}'
        if not clean.strip():continue
        if key not in records:raise ValueError('Unclassified credit record')
        row=records[key];seen.add(key)
        if hashlib.sha256(clean.encode()).hexdigest()!=row['source_body_sha256']:raise ValueError('Credit body changed')
        fmt=re.match(r'(\d+\s+\S+\s+)([\s\S]*)',clean)
        if not fmt:raise ValueError('Credit format missing')
        lines=fmt[2].split('\n');visited=set()
        for edit in row['edits']:
            pos=(edit['line'],edit['column']);value=edit['ko']
            if pos in visited or any(c in value for c in '\r\n\t') or not value.strip():raise ValueError('Invalid credit cell')
            visited.add(pos)
            try:cells=lines[pos[0]].split('\t');old=cells[pos[1]]
            except IndexError:raise ValueError('Unknown credit cell')
            if old!=edit['source']:raise ValueError('Credit cell source mismatch')
            cells[pos[1]]=value;lines[pos[0]]='\t'.join(cells)
        changes.append((m.end(),m.end()+len(clean),fmt[1]+'\n'.join(lines)))
    if seen!=set(records):raise ValueError('Unknown credit IDs')
    for start,end,value in reversed(changes):text=text[:start]+value+text[end:]
    return text.encode()

def add_credits(entries,rmp,source,spec):
    entries['ko/cutscene/credits/credits.txt']=compile_credits(source.read(spec['source_path']),spec)
    rmp.append('credits.credits = STRTAB:ko/cutscene/credits/credits.txt')
    chars={c for row in spec['records'] for edit in row['edits'] for c in edit['ko'] if ord(c)>127}
    for size,info in spec['fonts'].items():
        prefix=f'base/fonts/pt{size}.fon/'
        for name in source.namelist():
            if name.startswith(prefix) and name.endswith('.png'):entries[name.replace('base/','ko/',1)]=source.read(name)
        face=ImageFont.truetype(str(ROOT/'vendor/galmuri'/(info['family']+'.ttf')),info['size'])
        for char in chars:
            box=face.getbbox(char);mask=Image.new('L',(box[2]-box[0],box[3]-box[1]))
            ImageDraw.Draw(mask).text((-box[0],-box[1]),char,font=face,fill=255)
            mask=mask.point(lambda p:255 if p>=128 else 0)
            scale=info['scale'];mask=mask.resize((mask.width*scale,mask.height*scale),Image.Resampling.NEAREST)
            top=info['height']-3-mask.height
            if top<0:raise ValueError('Credit glyph taller than original font')
            glyph=Image.new('RGBA',(mask.width,info['height']),(255,255,255,0))
            glyph.paste((255,255,255,255),(0,top,mask.width,top+mask.height),mask)
            out=io.BytesIO();glyph.save(out,format='PNG')
            entries[f'ko/fonts/pt{size}.fon/{ord(char):05x}.png']=out.getvalue()
        rmp.append(f'credits.font.pt{size} = FONTRES:ko/fonts/pt{size}.fon')
