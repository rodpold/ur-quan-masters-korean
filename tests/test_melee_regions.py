import unittest,io
from PIL import Image,ImageFont
from melee_regions import ROOT,render_regions
class MeleeRegionsTests(unittest.TestCase):
    def setUp(self):
        self.font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
        b=io.BytesIO();Image.new('RGBA',(50,80),(10,20,30,255)).save(b,format='PNG');self.raw=b.getvalue()
        self.label={'box':[4,4,10,70],'text':'함선선택','vertical':True,'background':[87,87,87,255],'foreground':[138,138,138,255]}
    def test_vertical_preserves_surrounding_pixels(self):
        row={'size':[50,80],'regions':[self.label]};im=Image.open(io.BytesIO(render_regions(self.raw,row,self.font)))
        self.assertEqual(im.getpixel((3,10)),(10,20,30,255));self.assertEqual(im.getpixel((14,10)),(10,20,30,255))
        self.assertIn((138,138,138,255),set(im.crop((4,4,14,74)).getdata()))
    def test_rejects_vertical_overflow(self):
        self.label['text']='함'*8
        with self.assertRaises(ValueError):render_regions(self.raw,{'size':[50,80],'regions':[self.label]},self.font)
