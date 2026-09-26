import io
import unittest
from PIL import Image
from special_labels import preserve_indexed_colors


def png(image):
    b=io.BytesIO();image.save(b,format='PNG');return b.getvalue()


class IndexedCaptionTests(unittest.TestCase):
    def test_original_indexes_and_transparency_survive(self):
        original=Image.new('P',(3,1))
        palette=[0]*768
        palette[3:6]=[255,0,0]
        palette[6:9]=[255,0,0]  # Equal RGB, different runtime index identity.
        palette[9:12]=[0,255,0]
        original.putpalette(palette);original.putdata([1,2,0]);original.info['transparency']=0
        changed=original.convert('RGBA');changed.putpixel((0,0),(0,255,0,255))
        result=Image.open(io.BytesIO(preserve_indexed_colors(png(original),png(changed))))
        self.assertEqual(result.mode,'P')
        self.assertEqual(list(result.getdata()),[3,2,0])
        self.assertEqual(result.getpalette(),palette)
        self.assertEqual(result.info['transparency'],0)

    def test_unmapped_color_is_rejected_instead_of_quantized(self):
        original=Image.new('P',(1,1));original.putpalette([0]*768)
        changed=Image.new('RGBA',(1,1),(123,45,67,255))
        with self.assertRaises(ValueError):preserve_indexed_colors(png(original),png(changed))
