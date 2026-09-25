import sys,io,unittest
from pathlib import Path
from PIL import Image,ImageFont
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from ui_text_panels import render_panel

class ControlPanelTests(unittest.TestCase):
    def setUp(self):
        self.font=ImageFont.truetype(str(ROOT/'vendor/galmuri/Galmuri7.ttf'),8)
        self.row={'size':[60,30],'lines':['사람','조작'],'background':[2,4,62,255],'foreground':[35,140,210,255],'style':'flat'}
    def test_panel_dimensions_and_binary_alpha(self):
        im=Image.open(io.BytesIO(render_panel(self.row,self.font)))
        self.assertEqual(im.size,(60,30));self.assertEqual(im.getchannel('A').getextrema(),(255,255))
    def test_rejects_width_overflow_without_truncation(self):
        self.row['lines']=['아주 긴 문장을 잘라 넣지 않습니다']
        with self.assertRaises(ValueError):render_panel(self.row,self.font)
    def test_rejects_rows_that_exceed_height(self):
        self.row['size']=[60,9]
        with self.assertRaises(ValueError):render_panel(self.row,self.font)
    def test_selected_palette_changes_output(self):
        normal=render_panel(self.row,self.font);self.row['background']=[4,8,124,255]
        self.assertNotEqual(normal,render_panel(self.row,self.font))

if __name__=='__main__':unittest.main()
