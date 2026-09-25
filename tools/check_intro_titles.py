import io
from PIL import Image,ImageChops,ImageDraw
from intro_titles import load_titles,render_title
def verify_intro_titles(package,source):
    spec=load_titles();assert len(spec['rows'])==2
    assert source.read(spec['source_ani'])==package.read(spec['source_ani'].replace('base/','ko/',1))
    assert source.read('base/cutscene/intro/title-002.png')==package.read('ko/cutscene/intro/title-002.png')
    for row in spec['rows']:
        p=row['source_path'];old=source.read(p);new=package.read(p.replace('base/','ko/',1));assert new==render_title(old,row)
        a=Image.open(io.BytesIO(old)).convert('RGBA');b=Image.open(io.BytesIO(new)).convert('RGBA');assert a.size==b.size
        diff=ImageChops.difference(a,b)
        for r in row['regions']:
            x,y,w,h=r['box'];ImageDraw.Draw(diff).rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,0))
            assert set(b.crop((x,y,x+w,y+h)).getdata())=={(0,0,0,255),(255,255,255,255)}
        assert all(c.getbbox() is None for c in diff.split()),'Logo/name pixels changed'
    script=package.read('ko/cutscene/intro/intro.txt').decode();assert script.count('ANI addons/uqm-korean-ui-poc/ko/cutscene/intro/title.ani')==1
    for name in source.namelist():
        if name.endswith(('.ani','.txt','.rmp')):assert b'title-004.png' not in source.read(name),'Unreferenced asset gained a source reference'
    for name in package.namelist():
        if name.endswith(('.ani','.txt','.rmp')):assert b'title-004.png' not in package.read(name),'Unused creator image was activated'
    return {'status':'static_passed_runtime_pending','active_image_captions':1,'unreferenced_creator_asset_prepared':1,'preserved':'IFL identity/logo, product logo, original creator name pixels, ANI order and script timing','limitations':['title-004 has no discovered installed source reference; the patch does not activate it.','Actual intro playback needs runtime review.']}
