"""Translate bounded melee captions after existing button composites."""
import io,json,hashlib
from PIL import Image,ImageFont
from playmenu_headings import ROOT,paint_label
def load_regions():
    return json.loads((ROOT/'translations/melee-regions.ko.json').read_text(encoding='utf-8'))
def render_regions(raw,row,font):
    im=Image.open(io.BytesIO(raw)).convert('RGBA')
    if list(im.size)!=row['size']:raise ValueError('Melee region dimensions changed')
    for label in row['regions']:
        x,y,w,h=label['box']
        if x<0 or y<0 or x+w>im.width or y+h>im.height:raise ValueError('Melee region outside image')
        scale=label.get('scale',1)
        if scale not in (1,2) or w%scale or h%scale:raise ValueError('Invalid native pixel scale')
        panel=Image.new('RGBA',(w//scale,h//scale),tuple(label['background']))
        if label.get('vertical'):
            chars=label['text'];gap=5;total=7*len(chars)+gap*(len(chars)-1)
            if total>h:raise ValueError('Vertical caption does not fit')
            for i,char in enumerate(chars):paint_label(panel,{**label,'text':char,'box':[0,(h-total)//2+i*(7+gap),w,7]},font)
        else:paint_label(panel,{**label,'box':[0,0,panel.width,panel.height]},font)
        if scale!=1:panel=panel.resize((w,h),Image.Resampling.NEAREST)
        im.paste(panel,(x,y))
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()
def add_regions(entries,source):
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    for row in load_regions()['rows']:
        p=row['source_path'];raw=source.read(p);target=p.replace('base/','ko/',1)
        if hashlib.sha256(raw).hexdigest()!=row['source_sha256']:raise ValueError('Melee region source changed')
        entries[target]=render_regions(entries[target],row,font)
