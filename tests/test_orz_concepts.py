import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from check_orz_concepts import validate

class OrzConceptTests(unittest.TestCase):
    data = {'schema_version': 1, 'concepts': [
        {'source': 'house', 'ko': '집'}, {'source': 'juice', 'ko': '즙'}]}

    def test_korean_order_and_original_marker_punctuation(self):
        result = validate({'A': '*House.* and *juice!*'},
                          {'A': '*즙!* 그리고 *집.*'}, self.data)
        self.assertEqual(result['translated_marked_occurrences'], 2)

    def test_missing_repeated_term_and_unmarked_explanation_rejected(self):
        source = {'A': '*house* *juice* *juice*'}
        for text in ['*집* *즙*', '*집* *즙* 피', '*집* *즙* *피*', '*집* *즙* *즙']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate(source, {'A': text}, self.data)

    def test_phrase_cannot_be_split_or_moved_to_another_segment(self):
        data = {'schema_version': 1, 'concepts': [{'source': 'heavy space', 'ko': '무거운 공간'}]}
        for text in ['*무거운* *공간*\n다음', '다음\n*무거운 공간*']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                validate({'A': '*heavy space*\nnext'}, {'A': text}, data)
