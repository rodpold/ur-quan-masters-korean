import hashlib
import unittest
from cutscene_text import compile_script

class CutsceneTests(unittest.TestCase):
    raw=b'#(time)\r\nSYNC 2000\r\n#(text)\r\nTFI First\r\nSecond\r\n\r\n#(end)\r\nWAIT 100\r\n'
    def spec(self):return {'source_sha256':hashlib.sha256(self.raw).hexdigest(),'records':{'0001':'첫째\n둘째'}}
    def test_timing_headers_newlines_preserved(self):
        result=compile_script(self.raw,self.spec())
        expected=self.raw.replace(b'First\r\nSecond','첫째\r\n둘째'.encode())
        self.assertEqual(result,expected)
    def test_hash_change_rejected(self):
        with self.assertRaises(ValueError):compile_script(self.raw+b' ',self.spec())
    def test_injected_record_rejected(self):
        spec=self.spec();spec['records']['0001']='번역\n#(WAIT)'
        with self.assertRaises(ValueError):compile_script(self.raw,spec)
    def test_missing_and_extra_ids_rejected(self):
        for data in [{},{'0001':'첫째\n둘째','0002':'잘못'}]:
            spec=self.spec();spec['records']=data
            with self.assertRaises(ValueError):compile_script(self.raw,spec)

if __name__=='__main__':unittest.main()
