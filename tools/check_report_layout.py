# SPDX-License-Identifier: GPL-2.0-or-later
# Pagination logic adapted from UQM report.c and unicode.c.
# Copyright Paul Reiche, Fred Ford. 1992-2002
# Python adaptation copyright (c) 2026 ur-quan-masters-korean contributors.
# See LICENSES/UQM-GPL.txt and THIRD_PARTY.md.
"""Static report.c pagination/ink audit; this does not replace game playback."""
import io,json,re
from pathlib import Path
from PIL import Image


def graph(c):
    n=ord(c)
    return (n>0xa0 and (n<0xe000 or n>0xf8ff)) or 0x20<n<0x7f


def simulate(text, prompt='(다 음 )\n'):
    """Independent port of MakeReport's character-count/page loop (no timing)."""
    source=text.replace('\r\n','\n')
    stream=source; pos=0; remaining=len(source); row=0
    pages=[[]]; iterations=0
    def get(s,p):return (s[p],p+1) if p<len(s) else ('\0',p)
    while remaining:
        iterations+=1
        if iterations>len(source)*4+100:raise AssertionError('Report renderer stalled')
        original_pos=pos
        lf_pos=remaining; look=pos
        while lf_pos:
            c,look=get(stream,look)
            if c=='\n':break
            lf_pos-=1
        col=0; is_prompt=False
        if row==11 and (remaining>40 or lf_pos>1):
            col=20-len(prompt)//2
            stream=prompt;pos=0;remaining+=len(prompt);is_prompt=True
        x=2+col*6; baseline=(row+1)*6
        while True:
            end=pos;look=pos
            while True:
                c,look=get(stream,look)
                if not graph(c):break
                end=look
            count=end-pos;col+=count
            if col<=40:
                remaining-=count
                if remaining:remaining-=1
                for _ in range(count):
                    c,pos=get(stream,pos)
                    pages[-1].append((c,x,baseline,is_prompt,row))
                    x+=6
                col+=1
                last,pos=get(stream,pos);x+=6
            else:last='\0'
            if col>40 or last=='\n' or not remaining:break
        row+=1
        if row==12 or not remaining:
            if remaining:
                pos=original_pos;stream=source;row=0;pages.append([])
    return pages


def verify_reports(original, package, translations, preview_dir=None):
    from report_layout import FONT_TARGET
    maps={l.split('=',1)[0].strip():l.split('=',1)[1].strip() for l in original.read('uqm.rmp').decode().splitlines() if '=' in l}
    frame_path=maps['graphics.orbitbackground'].split(':',1)[1]
    frame_name=original.read(frame_path).decode().splitlines()[18].split()[0]
    frame=Image.open(io.BytesIO(original.read(str(Path(frame_path).parent/frame_name).replace('\\','/'))))
    assert frame.size==(5,5),'Report cell geometry changed'
    for n in original.namelist():
        if n.startswith('base/fonts/lander.fon/') and n.endswith('.png'):
            assert package.read(n.replace('base/fonts/','ko/fonts/',1))==original.read(n),'Original lander glyph changed'
    table=package.read('ko/gamestrings.txt').decode()
    prompt=re.search(r'(?m)^#\(\(MORE\)\)[^\r\n]*\r?\n([^\r\n]*)',table)[1]+'\n'
    result=[]
    def records(text):
        a=re.split(r'(?m)^#\(([^\r\n)]*)\)[^\r\n]*\r?\n',text)
        return {a[i]:a[i+1].rstrip('\r\n') for i in range(1,len(a),2)}
    glyphs={}
    for path,rows in translations.items():
        packed=records(package.read(path.replace('base/','ko/',1)).decode())
        for key,plain in rows.items():
            pages=simulate(packed[key],prompt)
            rendered=''.join(c for page in pages for c,_,_,indicator,_ in page if not indicator)
            assert rendered==''.join(plain.split()),f'Lost/reordered report text: {key}'
            for index,page in enumerate(pages):
                occupied=set();canvas=Image.new('RGB',(242,75),'black')
                for c,x,baseline,indicator,row in page:
                    if c not in glyphs:
                        im=Image.open(io.BytesIO(package.read(FONT_TARGET+f'{ord(c):05x}.png'))).convert('RGBA')
                        alpha=im.getchannel('A')
                        assert set(alpha.tobytes())<={0,255},f'Report alpha: {c}'
                        assert alpha.getbbox(),f'Blank report glyph: {c}'
                        h=im.height;hot=h+(-1 if h==8 else -2 if h==9 else -3 if h>9 else 0)
                        glyphs[c]=(alpha,hot)
                    alpha,hot=glyphs[c];y=baseline-hot
                    pixels={(x+xx,y+yy) for yy in range(alpha.height) for xx in range(alpha.width) if alpha.getpixel((xx,yy))}
                    assert all(0<=xx<242 and 0<=yy<75 for xx,yy in pixels),f'Report clipping: {key}/{index}/{c}'
                    assert not pixels.intersection(occupied),f'Report overlap: {key}/{index}/{c}'
                    occupied.update(pixels)
                    canvas.paste((0,255,0),(x,y),alpha)
                if preview_dir:
                    target=Path(preview_dir);target.mkdir(parents=True,exist_ok=True)
                    canvas.resize((968,300),Image.Resampling.NEAREST).save(target/(key.replace(' ','-')+f'-{index+1:02}.png'))
            result.append({'id':key,'pages':len(pages),'nonspace_characters':len(rendered),'static_ink_check':'passed','in_game_review':'pending'})
    return result
