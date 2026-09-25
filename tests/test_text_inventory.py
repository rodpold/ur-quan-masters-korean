import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from inventory_text import classify

class InventoryTests(unittest.TestCase):
    def test_duplicate_labels_and_multiline_text(self):
        rows=classify('base/cutscene/intro/intro.txt','#(Text)\nTFI First\nSecond\n\n#(Text)\nWAIT 200\n')
        self.assertEqual([r['id'] for r in rows],['0000','0001'])
        self.assertEqual(rows[0]['text'],'First\nSecond')
        self.assertEqual(rows[1]['kind'],'control')
    def test_positioned_text_keeps_coordinates(self):
        row=classify('base/cutscene/spins/ship00.txt','#(Title)\nTEXT 160 20 Name\n')[0]
        self.assertEqual((row['x'],row['y'],row['text']),(160,20,'Name'))
    def test_unknown_commands_and_control_continuations_fail(self):
        for body in ['NEW_COMMAND 1','WAIT 200\nUnexpected prose']:
            with self.assertRaises(ValueError):classify('base/cutscene/intro/intro.txt','#(x)\n'+body+'\n')
    def test_credit_layout_and_blank_lines(self):
        row=classify('base/cutscene/credits/credits.txt','#(crew)\n13 L,C/130\nAlice\tArtist\n\nBob\tMusic\n')[0]
        self.assertEqual(row['format'],'13 L,C/130')
        self.assertEqual(row['text'],'Alice\tArtist\n\nBob\tMusic')
    def test_repeated_ship_labels_are_not_lost(self):
        rows=classify('base/ships/test/test.txt','#(name)\nSame\n#(name)\nSame\n')
        self.assertEqual(len(rows),2)

if __name__=='__main__':unittest.main()
