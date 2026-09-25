import io,unittest
from PIL import Image,ImageFont
from melee_regions import ROOT,render_regions

class CaptionBackgroundTests(unittest.TestCase):
    def test_background_restoration_preserves_outside_and_solid_ink(self):
        im=Image.new('RGBA',(60,15),(10,20,30,255))
        for y in range(15):
            for x in range(60):im.putpixel((x,y),(x,20,30,255))
        source=io.BytesIO();im.save(source,format='PNG')
        label={'box':[10,3,40,9],'text':'궤도','background':[0,0,0,255],'foreground':[132,132,255,255],'background_from_sides':True}
        result=Image.open(io.BytesIO(render_regions(source.getvalue(),{'size':[60,15],'regions':[label]},ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)))).convert('RGBA')
        ink=0
        for y in range(15):
            for x in range(60):
                color=result.getpixel((x,y))
                if 10<=x<50 and 3<=y<12:
                    self.assertIn(color,[(x,20,30,255),(132,132,255,255)])
                    ink+=color==(132,132,255,255)
                else:self.assertEqual(color,im.getpixel((x,y)))
        self.assertGreater(ink,0)

if __name__=='__main__':unittest.main()
