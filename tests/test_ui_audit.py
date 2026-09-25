import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from check_ui import audit_ui

class UiAuditTests(unittest.TestCase):
    def test_duplicate_labels_and_blank_records_are_counted(self):
        report=audit_ui(b'#(label)\nOrbit: \n#(label)\nOrbit: \n#()\n\n',{'Orbit: ':'궤도: '})
        self.assertEqual(report['translated_records'],2)
        self.assertEqual([r['id'] for r in report['records']],['0000','0001','0002'])
        self.assertEqual(report['records'][2]['status'],'preserve_blank')

    def test_dynamic_suffix_space_is_required(self):
        with self.assertRaises(AssertionError):audit_ui(b'#(label)\nOrbit: \n',{'Orbit: ':'궤도:'})

    def test_game_number_cannot_be_changed(self):
        with self.assertRaises(AssertionError):audit_ui(b'#(points)\n200 points\n',{'200 points':'100점'})

    def test_month_conversion_is_explicit(self):
        self.assertEqual(audit_ui(b'#(month)\nFEB\n',{'FEB':'2월'})['translated_records'],1)
        with self.assertRaises(AssertionError):audit_ui(b'#(month)\nFEB\n',{'FEB':'3월'})

    def test_untranslated_is_not_marked_complete(self):
        report=audit_ui(b'#(name)\nMercury\n#(captain)\nZelnick\n',{})
        self.assertEqual(report['pending_records'],1)
        self.assertEqual(report['records'][1]['status'],'default_player_editable_captain_name')

if __name__=='__main__':unittest.main()
