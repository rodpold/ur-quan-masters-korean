"""Verify communication-image review source coverage, not visual conclusions."""
import argparse
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import zipfile
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]

def verify(game):
    report = json.loads((ROOT / 'docs/comm-image-review.json').read_text(encoding='utf-8'))
    rows = report['records']
    names = [r['source_path'] for r in rows]
    assert len(names) == len(set(names)) == report['reviewed_images'] == 1492
    assert report['complete'] is False
    counts = Counter(n.split('/')[2] for n in names)
    assert dict(counts) == report['race_directory_counts']
    assert len(counts) == 25
    with zipfile.ZipFile(game / 'content/packages/uqm-0.8.0-content.uqm') as source:
        expected = {n for n in source.namelist() if n.startswith('base/comm/') and n.endswith('.png')}
        assert set(names) == expected, {'missing': sorted(expected-set(names)), 'extra': sorted(set(names)-expected)}
        for row in rows:
            raw = source.read(row['source_path'])
            assert hashlib.sha256(raw).hexdigest() == row['source_sha256'], row['source_path']
            assert list(Image.open(io.BytesIO(raw)).size) == row['size'], row['source_path']
            assert row['status'] == 'no_readable_language_text_observed'
            assert row['review_method'].startswith('contact_sheet')
        assert sum(r['size'][0] >= 200 and r['size'][1] >= 80 for r in rows) == report['large_background_images'] == 27
    return {'status':'source_inventory_binding_passed','images':len(rows),'directories':len(counts),
            'limitations':'Source coverage only; visual conclusions and composited game playback are not automatically verified.'}

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--game', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(verify(a.game),ensure_ascii=False,indent=2))
