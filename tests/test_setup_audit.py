import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from check_setup import audit_setup


class SetupAuditTests(unittest.TestCase):
    def fixture(self):
        source={'CAT_0_OPTS':'320x240\n640x480','SUBTITLES':'\nGraphics','DESC':'Use 3DO speech.'}
        source.update({f'LABEL_{i}':'An instruction.' for i in range(118)})
        raw=''.join(f'#({key})\n{value}\n\n' for key,value in source.items()).encode()
        ko={key:'설명입니다.' for key in source}
        ko.update(CAT_0_OPTS='320x240\n640x480',SUBTITLES='\n화면',DESC='3DO 음성을 사용합니다.')
        return raw,ko

    def test_preserves_initial_empty_list_item(self):
        raw,ko=self.fixture()
        self.assertEqual(audit_setup(raw,ko)['translated_records'],121)
        ko['SUBTITLES']='화면'
        with self.assertRaises(ValueError):audit_setup(raw,ko)

    def test_rejects_changed_resolution(self):
        raw,ko=self.fixture();ko['CAT_0_OPTS']='320x200\n640x480'
        with self.assertRaises(AssertionError):audit_setup(raw,ko)

    def test_rejects_missing_description(self):
        raw,ko=self.fixture();del ko['DESC']
        with self.assertRaises(ValueError):audit_setup(raw,ko)

    def test_rejects_injected_record(self):
        raw,ko=self.fixture();ko['DESC']='3DO 음성\n#(NEW)\n추가'
        with self.assertRaises(AssertionError):audit_setup(raw,ko)


if __name__=='__main__':unittest.main()
