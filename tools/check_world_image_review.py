"""Verify world-image review coverage and retain unresolved captions."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
from collections import Counter
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
GROUPS={'battle':117,'lander':331,'nav':294,'planets':177}
PENDING={'base/lander/lander-032.png'}

def verify(game):
    review=json.loads((ROOT/'docs/world-image-review.json').read_text(encoding='utf-8'))
    rows=review['records'];names=[r['source_path'] for r in rows]
    assert len(names)==len(set(names))==review['reviewed_images']==919
    assert review['complete'] is False
    assert dict(Counter(n.split('/')[1] for n in names))==review['group_counts']==GROUPS
    assert {r['source_path'] for r in rows if r['status']=='embedded_text_pending'}==PENDING
    assert review['pending_image_translations']==len(PENDING)
    assert {r['source_path'] for r in rows if r['status']=='preserve_unit_symbol'}=={'base/nav/orbitbackground-020.png'}
    with zipfile.ZipFile(game/'content/packages/uqm-0.8.0-content.uqm') as source:
        expected={n for n in source.namelist() if n.endswith('.png') and n.startswith('base/') and n.split('/')[1] in GROUPS}
        assert set(names)==expected,{'missing':sorted(expected-set(names)),'extra':sorted(set(names)-expected)}
        for row in rows:
            raw=source.read(row['source_path'])
            assert hashlib.sha256(raw).hexdigest()==row['source_sha256'],row['source_path']
            assert list(Image.open(io.BytesIO(raw)).size)==row['size'],row['source_path']
            assert row['status'] in {'no_readable_language_text_observed','embedded_text_pending','preserve_unit_symbol','generated_korean_caption_runtime_pending'}
    return {'status':'source_inventory_binding_passed','images':len(rows),'pending_image_translations':len(PENDING),'limitations':'Visual judgments and runtime playback are not certified.'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);a=p.parse_args()
    print(json.dumps(verify(a.game),ensure_ascii=False,indent=2))
