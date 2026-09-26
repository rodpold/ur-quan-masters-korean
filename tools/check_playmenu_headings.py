from indexed_menus import finalize_menu
import io,json
from PIL import Image,ImageChops,ImageDraw,ImageFont
from playmenu_headings import ROOT,load_headings,render_heading
def verify_playmenu_headings(package,source):
    spec=load_headings();assert len(spec['rows'])==39
    assert package.read('ko/ui/playmenu.ani')==source.read('base/ui/playmenu.ani')
    ui=json.loads((ROOT/'translations/ui.ko.json').read_text(encoding='utf-8'))
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    for row in spec['rows']:
        p=row['source_path'];raw=package.read(p.replace('base/','ko/',1))
        assert raw==finalize_menu(p.replace('base/','ko/',1),source.read(p),render_heading(source.read(p),row,font))
        original=Image.open(io.BytesIO(source.read(p))).convert('RGBA');patched=Image.open(io.BytesIO(raw)).convert('RGBA')
        assert original.size==patched.size
        diff=ImageChops.difference(original,patched)
        for label in [row]+row.get('extra_labels',[]):
            x,y,w,h=label['box']
            ImageDraw.Draw(diff).rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,0))
            assert set(patched.crop((x,y,x+w,y+h)).getchannel('A').getdata())<={0,255}
        assert all(c.getbbox() is None for c in diff.split()),'Non-caption icon pixels changed'
        if 'ui_key' in row:assert row['text']==ui[row['ui_key']]
    extras=[label for row in spec['rows'] for label in row.get('extra_labels',[])]
    assert [label['text'] for label in extras]==['사람','사이보그','사이보그','사이보그']
    assert all(label['box']==[7,17,42,8] for label in extras)
    return {'status':'static_passed_runtime_pending','headings':39,'embedded_control_labels':4,'limitations':['Decorative ship-name art inside icon 36 remains pending; four HUMAN/CYBORG labels are translated.','In-game visibility is not verified by this static check.']}
