import io
import unittest
from zipfile import ZipFile
import patcher

class ReportTests(unittest.TestCase):
    path = 'base/lander/energy/ruins.txt'

    def archive(self, mapping=None):
        stream=io.BytesIO()
        with ZipFile(stream,'w') as z:
            z.writestr('uqm.rmp', mapping if mapping is not None else 'text.ruins = STRTAB:'+self.path+'\n')
            z.writestr(self.path, '#(RUINS 1) metadata\r\nFirst\r\n\r\nLast\r\n\r\n#(RUINS 2)\r\nUntouched\r\n')
        return ZipFile(io.BytesIO(stream.getvalue()))

    def test_mapping_headers_newlines_and_untranslated_record(self):
        with self.archive() as z:
            assets, mappings=patcher.report_assets(z,{self.path:{'RUINS 1':'처음\n\n끝'}})
        self.assertEqual(mappings,['text.ruins = STRTAB:ko/lander/energy/ruins.txt', 'font.lander = FONTRES:ko/fonts/lander.fon'])
        self.assertEqual(assets['ko/lander/energy/ruins.txt'].decode(), '#(RUINS 1) metadata\r\n\r\n처 음 \r\n\r\n\r\n\r\n끝 \r\n\r\n#(RUINS 2)\r\nUntouched\r\n')

    def test_reject_unknown_id_and_shifted_paragraph(self):
        for rows in [{'NO SUCH ID':'처음'}, {'RUINS 1':'처음\n끝\n추가'}]:
            with self.archive() as z, self.assertRaises(ValueError):
                patcher.report_assets(z,{self.path:rows})

    def test_reject_unmapped_and_ambiguous_resource(self):
        for mapping in ['', 'text.a = STRTAB:'+self.path+'\ntext.b = STRTAB:'+self.path]:
            with self.archive(mapping) as z, self.assertRaises(ValueError):
                patcher.report_assets(z,{self.path:{'RUINS 1':'처음\n\n끝'}})

    def test_reject_path_outside_reports(self):
        for path in ['base/gamestrings.txt','base/lander/energy/../../escape.txt']:
            with self.archive() as z, self.assertRaises(ValueError):
                patcher.report_assets(z,{path:{'RUINS 1':'처음'}})

class ReportLayoutTests(unittest.TestCase):
    def test_long_words_are_not_lost_or_overflowed(self):
        from report_layout import compile_body
        from tools.check_report_layout import simulate
        text='함장님 '+('가'*51)+'\n\n숫자 639.5 : 231.2, 끝.'
        packed=compile_body(text)
        self.assertTrue(all(len(line)<=40 for line in packed.splitlines()))
        pages=simulate(packed)
        self.assertEqual(''.join(c for page in pages for c,_,_,more,_ in page if not more), ''.join(text.split()))

    def test_page_boundary_reserves_first_row_and_prompt_row(self):
        from report_layout import compile_body
        from tools.check_report_layout import simulate
        pages=simulate(compile_body('\n'.join(['한글 보고']*13)))
        self.assertEqual(len(pages),3)
        for page in pages:
            self.assertTrue(all(row in {1,3,5,7,9} for _,_,_,more,row in page if not more))
        self.assertTrue(any(more for page in pages for _,_,_,more,_ in page))

    def test_private_use_codepoints_are_not_graphical_in_engine(self):
        from tools.check_report_layout import graph
        self.assertFalse(graph('\ue000'))
        self.assertTrue(graph('한'))
