import hashlib,unittest
import patcher

class UiOverrideTests(unittest.TestCase):
    raw='#(Mercury)\r\nMercury\r\n#(empty)\r\n\r\n#(Mercury)\r\nMercury\r\n'
    def spec(self):return {'source_sha256':hashlib.sha256(self.raw.encode()).hexdigest(),'records':{'0000':{'source':'Mercury','ko':'수은'},'0002':{'source':'Mercury','ko':'수성'}}}
    def test_context_and_duplicate_headers_preserved(self):
        result,counts=patcher.translate_table(self.raw,{},self.spec())
        self.assertEqual(result,'#(Mercury)\r\n수은\r\n#(empty)\r\n\r\n#(Mercury)\r\n수성\r\n')
        self.assertEqual(sum(counts.values()),2)
    def test_source_version_change_rejected(self):
        with self.assertRaises(ValueError):patcher.translate_table(self.raw+'\n',{},self.spec())
    def test_global_collision_rejected(self):
        with self.assertRaises(ValueError):patcher.translate_table(self.raw,{'Mercury':'수성'},self.spec())
    def test_wrong_record_source_rejected(self):
        spec=self.spec();spec['records']['0000']['source']='Venus'
        with self.assertRaises(ValueError):patcher.translate_table(self.raw,{},spec)
    def test_unknown_record_rejected(self):
        spec=self.spec();spec['records']['0999']={'source':'Mercury','ko':'수은'}
        with self.assertRaises(ValueError):patcher.translate_table(self.raw,{},spec)
    def test_record_injection_rejected(self):
        spec=self.spec();spec['records']['0000']['ko']='수은\n#(invalid)'
        with self.assertRaises(ValueError):patcher.translate_table(self.raw,{},spec)

if __name__=='__main__':unittest.main()
