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
