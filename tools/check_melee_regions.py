from indexed_menus import finalize_menu
import io
from PIL import Image,ImageFont,ImageChops,ImageDraw
from melee_regions import load_regions,render_regions,ROOT
from ui_text_panels import load_panels,render_panel
def verify_melee_regions(package,source):
    spec=load_regions();assert len(spec['rows'])==5
    font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    panels=load_panels();panel_rows={r['source_path']:r for r in panels['panels']}
    composites={r['source_path']:r for r in panels['background_composites']}
    for row in spec['rows']:
        p=row['source_path'];before=Image.open(io.BytesIO(source.read(p))).convert('RGBA')
        if p in composites:
            for placement in composites[p]['placements']:
                panel=Image.open(io.BytesIO(render_panel(panel_rows[placement['panel']],font))).convert('RGBA')
                before.paste(panel,tuple(placement['origin']))
        b=io.BytesIO();before.save(b,format='PNG');actual=package.read(p.replace('base/','ko/',1))
        assert actual==finalize_menu(p.replace('base/','ko/',1),source.read(p),render_regions(b.getvalue(),row,font))
        after=Image.open(io.BytesIO(actual)).convert('RGBA');diff=ImageChops.difference(before,after)
        for region in row['regions']:
            x,y,w,h=region['box'];ImageDraw.Draw(diff).rectangle((x,y,x+w-1,y+h-1),fill=(0,0,0,0))
            assert set(after.crop((x,y,x+w,y+h)).getchannel('A').getdata())=={255}
        assert all(c.getbbox() is None for c in diff.split()),'Non-caption art or input identifiers changed'
    assert source.read('base/ui/meleemenu.ani')==package.read('ko/ui/meleemenu.ani')
    return {'status':'static_passed_runtime_pending','sprites':5,'captions':8,'preserved':'ANI, grid, A/B/C symbols, scroll arrow, ship art and existing translated buttons','limitations':['Input mapping and in-game visibility still require runtime review.']}
