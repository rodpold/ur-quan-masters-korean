import unittest,io
from PIL import Image
from shipyard_labels import render_label
def source():
    im=Image.new('P',(56,11));im.putpalette([i for i in range(256) for _ in range(3)]);im.info['transparency']=0
    out=io.BytesIO();im.save(out,format='PNG');return out.getvalue()

class ShipyardLabelsTests(unittest.TestCase):
    def test_native_two_rows(self):
        im=Image.open(io.BytesIO(render_label({'size':[56,15],'lines':['조크-포트-피크','스팅어']},source())))
        self.assertEqual(im.size,(56,15));self.assertEqual(im.mode,'P');self.assertEqual(im.info['transparency'],0);self.assertEqual(set(im.getdata()),{0,227})
    def test_width_overflow(self):
        with self.assertRaises(ValueError):render_label({'size':[56,15],'lines':['가'*8,'스팅어']},source())
    def test_original_header_too_short_for_two_rows(self):
        with self.assertRaises(ValueError):render_label({'size':[56,11],'lines':['촘르','아바타']},source())
