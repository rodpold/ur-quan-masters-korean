import io
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from check_intro import verify_slides

class SlideLimitsTests(unittest.TestCase):
    def verify(self,text):
        path='base/cutscene/intro/intro.txt'
        raw='#(font0)\nFONT 0 base/fonts/starcon.fon\n#(font1)\nFONT 1 base/fonts/slides.fon\n#(text)\nTFI '+text+'\n'
        spec={'source_path':path,'records':{'0002':text}}
        source_buffer=io.BytesIO();package_buffer=io.BytesIO()
        with ZipFile(source_buffer,'w') as z:z.writestr(path,raw)
        with ZipFile(package_buffer,'w') as z:
            z.writestr('ko/cutscene/intro/intro.txt',raw.replace('base/fonts/','addons/uqm-korean-ui-poc/ko/fonts/'))
            for name,width in [('starcon',4),('slides',2)]:
                for char in set(text)-{'\n'}:
                    buf=io.BytesIO();Image.new('RGBA',(width,3),'white').save(buf,format='PNG')
                    z.writestr(f'ko/fonts/{name}.fon/{ord(char):05x}.png',buf.getvalue())
        with ZipFile(package_buffer) as package,ZipFile(source_buffer) as source:
            return verify_slides(package,source,spec,1)

    def test_loading_nonzero_font_selects_it(self):
        row=self.verify('Hi')['subtitles'][0]
        self.assertEqual(row['font'],'slides')
        self.assertEqual(row['widths'],[6])

    def test_utf8_byte_limit(self):
        with self.assertRaisesRegex(AssertionError,'buffer exceeded'):
            self.verify('가'*171)

    def test_line_limit(self):
        with self.assertRaisesRegex(AssertionError,'line buffer exceeded'):
            self.verify('\n'.join(['Hi']*16))

if __name__=='__main__':unittest.main()
