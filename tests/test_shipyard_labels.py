import unittest,io
from PIL import Image
from shipyard_labels import render_label
class ShipyardLabelsTests(unittest.TestCase):
    def test_native_two_rows(self):
        im=Image.open(io.BytesIO(render_label({'size':[56,15],'lines':['조크-포트-피크','스팅어']})))
        self.assertEqual(im.size,(56,15));self.assertEqual(im.getchannel('A').getextrema(),(255,255))
    def test_width_overflow(self):
        with self.assertRaises(ValueError):render_label({'size':[56,15],'lines':['가'*8,'스팅어']})
    def test_original_header_too_short_for_two_rows(self):
        with self.assertRaises(ValueError):render_label({'size':[56,11],'lines':['촘르','아바타']})
