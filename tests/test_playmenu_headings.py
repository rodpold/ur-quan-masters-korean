import unittest,io,hashlib
from PIL import Image,ImageFont
from playmenu_headings import ROOT,render_heading
class HeadingTests(unittest.TestCase):
    def setUp(self):
        im=Image.new('RGBA',(56,63),(12,34,56,255));b=io.BytesIO();im.save(b,format='PNG');self.raw=b.getvalue()
        self.row={'source_sha256':hashlib.sha256(self.raw).hexdigest(),'size':[56,63],'box':[0,0,56,8],'text':'광물 탐사'}
        self.font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
    def test_preserves_art_and_binary_heading(self):
        im=Image.open(io.BytesIO(render_heading(self.raw,self.row,self.font))).convert('RGBA')
        self.assertEqual(im.getpixel((0,8)),(12,34,56,255))
        self.assertEqual(set(im.crop((0,8,56,63)).getdata()),{(12,34,56,255)})
        self.assertEqual(set(im.crop((0,0,56,8)).getchannel('A').getdata()),{0,255})
    def test_rejects_overflow(self):
        self.row['text']='가'*20
        with self.assertRaises(ValueError):render_heading(self.raw,self.row,self.font)
    def test_rejects_changed_source(self):
        self.row['source_sha256']='0'*64
        with self.assertRaises(ValueError):render_heading(self.raw,self.row,self.font)
    def test_rejects_out_of_bounds(self):
        self.row['box']=[0,60,56,8]
        with self.assertRaises(ValueError):render_heading(self.raw,self.row,self.font)

    def test_embedded_caption_keeps_art_below(self):
        self.row['extra_labels']=[{'box':[7,17,42,8],'text':'사이보그','background':[2,4,62,255],'foreground':[186,0,0,255]}]
        im=Image.open(io.BytesIO(render_heading(self.raw,self.row,self.font))).convert('RGBA')
        self.assertEqual(im.getpixel((7,17)),(2,4,62,255))
        self.assertEqual(im.getpixel((7,25)),(12,34,56,255))
        self.assertEqual(im.getpixel((6,20)),(12,34,56,255))
        self.assertIn((186,0,0,255),set(im.crop((7,17,49,25)).getdata()))
