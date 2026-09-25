import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from check_localization import canonical_terms

class CanonicalTermTests(unittest.TestCase):
    terms = [{"source": "Arilou", "ko": "아릴루"},
             {"source": "Arilou Lalee'lay", "ko": "아릴룰랄릴레이"}]

    def names(self, text):
        return {t["source"] for t in canonical_terms(text, self.terms)}

    def test_full_name_uses_existing_full_translation(self):
        self.assertEqual(self.names("I am Arilou Lalee'lay."), {"Arilou Lalee'lay"})

    def test_separate_short_name_still_required(self):
        self.assertEqual(self.names("Arilou... the Arilou Lalee'lay."),
                         {"Arilou", "Arilou Lalee'lay"})

    def test_case_and_word_boundaries(self):
        self.assertEqual(self.names("ARILOU Ariloulaleelay"), {"Arilou"})
        self.assertEqual(self.names("Ariloulaleelay"), set())

    def test_proper_star_name_is_not_common_noun(self):
        term = {"source": "Root", "ko": "루트", "case_sensitive": True}
        self.assertEqual(list(canonical_terms("the star, Root.", [term])), [term])
        self.assertEqual(list(canonical_terms("the same root.", [term])), [])
        self.assertEqual(list(canonical_terms("your roots", [term])), [])
