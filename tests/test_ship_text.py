import hashlib,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ship_text import compile_ship

class ShipTextTests(unittest.TestCase):
    def fixture(self):
        raw=b'#(Race)\r\nRace\r\n#(Race)\r\nRace\r\n#(Captain)\r\nFoo\r\n'
        return raw,{'source_path':'ship.txt','source_sha256':hashlib.sha256(raw).hexdigest(),
                    'records':[{'id':'0001','source':'Race','ko':'종족'}]}
    def test_duplicate_headers_and_untranslated_captain_preserved(self):
        raw,spec=self.fixture()
        self.assertEqual(compile_ship(raw,spec),b'#(Race)\r\nRace\r\n#(Race)\r\n'+'종족'.encode()+b'\r\n#(Captain)\r\nFoo\r\n')
    def test_source_change_rejected(self):
        raw,spec=self.fixture()
        with self.assertRaises(ValueError):compile_ship(raw+b'\n',spec)
    def test_unknown_index_rejected(self):
        raw,spec=self.fixture();spec['records'][0]['id']='0009'
        with self.assertRaises(ValueError):compile_ship(raw,spec)
    def test_duplicate_index_rejected(self):
        raw,spec=self.fixture();spec['records']*=2
        with self.assertRaises(ValueError):compile_ship(raw,spec)
    def test_header_injection_rejected(self):
        raw,spec=self.fixture();spec['records'][0]['ko']='종족\n#(Injected)'
        with self.assertRaises(ValueError):compile_ship(raw,spec)
    def test_misbound_label_rejected(self):
        raw,spec=self.fixture();spec['records'][0]['source']='Other'
        with self.assertRaises(ValueError):compile_ship(raw,spec)

if __name__=='__main__':unittest.main()
