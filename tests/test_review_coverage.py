import hashlib
import unittest
from tools.check_review_coverage import evidence_errors


class ReviewEvidenceTests(unittest.TestCase):
    def item(self, ids=None):
        return dict(translation_sha256=hashlib.sha256(b'ko').hexdigest(),
                    source_sha256=hashlib.sha256(b'en').hexdigest(),
                    reviewed_record_ids=['A'] if ids is None else ids)

    def test_current_partial_review_is_valid(self):
        self.assertEqual(evidence_errors(self.item(), b'ko', b'en', ['A', 'B']), [])

    def test_changed_translation_is_not_current(self):
        self.assertIn('translation_changed_since_review', evidence_errors(self.item(), b'new', b'en', ['A']))

    def test_changed_source_is_not_current(self):
        self.assertIn('source_changed_since_review', evidence_errors(self.item(), b'ko', b'new', ['A']))

    def test_duplicate_and_unknown_ids_rejected(self):
        errors = evidence_errors(self.item(['B', 'B']), b'ko', b'en', ['A'])
        self.assertEqual(set(errors), {'duplicate_reviewed_ids', 'unknown_reviewed_ids'})


class CoverageIntegrationTests(unittest.TestCase):
    def test_overlapping_reports_count_once_and_stale_report_is_excluded(self):
        import json
        import tempfile
        from pathlib import Path
        from zipfile import ZipFile
        from tools.check_review_coverage import audit, REVIEW_STATUS

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'translations/dialogue').mkdir(parents=True)
            (root/'docs').mkdir()
            game = root/'game'
            (game/'content/packages').mkdir(parents=True)
            (game/'content/addons').mkdir()
            source = b'#(A)\nHello\n#(B)\nBye\n'
            ko = json.dumps({'A': ['hello'], 'B': ['bye']}).encode()
            (root/'translations/dialogue/probe.ko.json').write_bytes(ko)
            for name in ['intro', 'ending']:
                (root/f'translations/{name}.ko.json').write_text(json.dumps(
                    {'source_path': name, 'records': {}}), encoding='utf-8')
            report_ko = json.dumps({'first-report': {'SAME 1': 'one'}, 'second-report': {'SAME 1': 'two'}}).encode()
            (root/'translations/reports.ko.json').write_bytes(report_ko)
            report_source = b'#(SAME 1)\nText\n'
            with ZipFile(game/'content/packages/uqm-0.8.0-content.uqm', 'w') as archive:
                archive.writestr('base/comm/probe/probe.txt', source)
                archive.writestr('first-report', report_source)
                archive.writestr('second-report', report_source)
                archive.writestr('intro', b'')
                archive.writestr('ending', b'')
            with ZipFile(game/'content/addons/uqm-0.8.0-voice.uqm', 'w'):
                pass
            report = dict(status=REVIEW_STATUS,
                          translation_path='translations/dialogue/probe.ko.json',
                          source_path='base/comm/probe/probe.txt',
                          source_sha256=hashlib.sha256(source).hexdigest(),
                          translation_sha256=hashlib.sha256(ko).hexdigest(),
                          reviewed_record_ids=['A'])
            for name in ['first', 'overlap']:
                (root/f'docs/{name}-language-review.json').write_text(json.dumps(report))
            stale = dict(report, reviewed_record_ids=['B'], translation_sha256='stale')
            (root/'docs/stale-language-review.json').write_text(json.dumps(stale))
            surface = dict(report, translation_path='translations/reports.ko.json', source_path='first-report',
                           source_sha256=hashlib.sha256(report_source).hexdigest(),
                           translation_sha256=hashlib.sha256(report_ko).hexdigest(), reviewed_record_ids=['SAME 1'])
            (root/'docs/surface-language-review.json').write_text(json.dumps(surface))
            result = audit(root, game)
            self.assertEqual(result['totals']['base_dialogue'], {
                'total_records': 2, 'current_agent_review_records': 1, 'pending_records': 1})
            self.assertEqual(result['resources'][0]['pending_ids'], ['B'])
            self.assertEqual(len(result['issues']), 1)
            self.assertIn('translation_changed_since_review', result['issues'][0]['errors'])
            self.assertEqual(result['totals']['surface_reports'], dict(total_records=2, current_agent_review_records=1, pending_records=1))
            surface_rows = [row for row in result['resources'] if row['category']=='surface_reports']
            self.assertEqual(surface_rows[1]['source_path'], 'second-report')
            self.assertEqual(surface_rows[1]['pending_ids'], ['SAME 1'])
            self.assertFalse(result['complete'])
