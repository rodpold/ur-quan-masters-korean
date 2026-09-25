import io
from PIL import Image,ImageChops,ImageDraw
from ending_card import load_card,render_card
def verify_ending_card(package,source):
    spec=load_card();p=spec['source_ani'];assert source.read(p)==package.read(p.replace('base/','ko/',1))
    for line in source.read(p).decode().splitlines():
        name='base/cutscene/ending/'+line.split()[0]
        if name!=spec['source_path']:assert source.read(name)==package.read(name.replace('base/','ko/',1))
    p=spec['source_path'];old=source.read(p);raw=package.read(p.replace('base/','ko/',1));assert raw==render_card(old,spec)
    a=Image.open(io.BytesIO(old)).convert('RGBA');b=Image.open(io.BytesIO(raw)).convert('RGBA');assert a.size==b.size
    x,y,w,h=spec['box'];diff=ImageChops.difference(a,b);ImageDraw.Draw(diff).rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,0))
    assert all(c.getbbox() is None for c in diff.split()),'Copyright or other ending pixels changed'
    assert set(b.crop((x,y,x+w,y+h)).getdata())=={(0,0,0,255),(255,255,255,255)}
    script=package.read('ko/cutscene/ending/final.txt').decode()
    assert script.count('ANI addons/uqm-korean-ui-poc/ko/cutscene/ending/ending.ani')==1
    return {'status':'static_passed_runtime_pending','translated_image_titles':1,'unchanged_frames':5,'copyright_pixels':'preserved','limitations':['Timing/control commands are checked separately; actual ending playback still needs runtime review.']}
