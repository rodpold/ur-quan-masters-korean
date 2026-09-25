"""Track setup coverage separately from free-form linguistic/runtime review."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import patcher
from inventory_text import blocks


def audit_setup(raw, translations):
    original = raw.decode('utf-8')
    translated = patcher.translate_setup(original, translations)
    before, after = list(blocks(original)), list(blocks(translated))
    assert len(before) == len(after) == 121
    rows = []
    for (index, key, source), (new_index, new_key, value) in zip(before, after):
        assert (index, key) == (new_index, new_key)
        assert value == translations[key] and value.strip()
        assert not re.search(r'^#\(', value, re.M)
        # Digit tokens include resolution, edition, aspect ratio and algorithm names.
        assert re.findall(r'\d+', source) == re.findall(r'\d+', value), key
        assert re.findall(r'%[-+0-9.]*[sduf]', source) == re.findall(r'%[-+0-9.]*[sduf]', value), key
        rows.append({'id': key, 'source_text_sha256': hashlib.sha256(source.encode()).hexdigest(),
                     'status': 'translated_draft', 'source_lines': len(source.splitlines()),
                     'translated_lines': len(value.splitlines())})
    return {'source_path': 'base/ui/setupmenu.txt', 'source_sha256': hashlib.sha256(raw).hexdigest(),
            'total_records': len(rows), 'translated_records': len(rows), 'pending_records': 0,
            'status': 'structure_passed_linguistic_and_runtime_review_pending',
            'preserved_technical_names': ['UQM', 'PC', '3DO', 'SDL', 'OpenGL', 'OpenAL', 'MixSDL', 'Bilinear', 'Biadapt', 'Biadv', 'Triscan', 'HQ', 'HQ2X', 'Scale2x', 'FPS', 'Creative Labs', 'Precursors', 'The Precursors', 'Enter', 'Delete'],
            'limitations': ['Coverage does not prove meaning or runtime behavior.',
                            'List order/count is checked by the compiler; free-form description line wrapping may differ.',
                            'Control-template placeholders are replaced at runtime; user configuration names remain user data.'],
            'records': rows}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', required=True, type=Path)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    with ZipFile(args.game/patcher.SOURCE) as source:
        report = audit_setup(source.read('base/ui/setupmenu.txt'), json.loads((ROOT/'translations/setup.ko.json').read_text(encoding='utf-8')))
    if args.write_report:
        (ROOT/'docs/setup-progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'},ensure_ascii=False,indent=2))
