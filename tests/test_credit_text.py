import hashlib,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from credit_text import compile_credits

class CreditTextTests(unittest.TestCase):
    def fixture(self):
        body='13 R/146,L/165\nActor Name\tRole\n\tOther role'
        raw=('#(same)\n'+body+'\n\n#(same)\n\n').encode()
        spec={'source_sha256':hashlib.sha256(raw).hexdigest(),'records':[{'id':'0000','source_body_sha256':hashlib.sha256(body.encode()).hexdigest(),
            'edits':[{'line':0,'column':1,'source':'Role','ko':'배역'}]}]}
        return raw,spec
    def test_name_and_duplicate_header_are_untouched(self):
        raw,spec=self.fixture();self.assertEqual(compile_credits(raw,spec),raw.replace(b'\tRole','\t배역'.encode()))
    def test_rejects_source_change(self):
        raw,spec=self.fixture()
        with self.assertRaises(ValueError):compile_credits(raw+b'\n',spec)
    def test_rejects_column_injection(self):
        raw,spec=self.fixture();spec['records'][0]['edits'][0]['ko']='배역\t추가'
        with self.assertRaises(ValueError):compile_credits(raw,spec)
    def test_rejects_wrong_source_cell(self):
        raw,spec=self.fixture();spec['records'][0]['edits'][0]['source']='Actor Name'
        with self.assertRaises(ValueError):compile_credits(raw,spec)
    def test_rejects_unknown_record(self):
        raw,spec=self.fixture();spec['records'][0]['id']='0009'
        with self.assertRaises(ValueError):compile_credits(raw,spec)

if __name__=='__main__':unittest.main()
