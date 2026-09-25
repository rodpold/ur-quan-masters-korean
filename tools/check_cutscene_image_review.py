"""Verify review inventory binding; this cannot replace human visual review."""
import argparse,hashlib,io,json,zipfile
from pathlib import Path
from collections import Counter
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def verify(game):
    review=json.loads((ROOT/'docs/cutscene-image-review.json').read_text(encoding='utf-8'))
    rows=review['records'];names=[r['source_path'] for r in rows]
    assert len(names)==len(set(names))==review['reviewed_images']
    with zipfile.ZipFile(game/'content/packages/uqm-0.8.0-content.uqm') as source:
        expected={n for n in source.namelist() if n.startswith('base/cutscene/') and n.endswith('.png')}
        assert set(names)==expected,{'unreviewed':sorted(expected-set(names)),'unexpected':sorted(set(names)-expected)}
        for row in rows:
            raw=source.read(row['source_path'])
            assert hashlib.sha256(raw).hexdigest()==row['source_sha256'],row['source_path']
            assert list(Image.open(io.BytesIO(raw)).size)==row['size'],row['source_path']
        victory=[r for r in rows if r['source_path'].startswith('base/cutscene/ending/victory2-')]
        spins=[r for r in rows if r['source_path'].startswith('base/cutscene/spins/')]
        assert len(victory)==239 and len(spins)==3
        assert review['pending_victory2_frames']==review['pending_spin_images']==0
        assert review['complete'] is False
    return {'status':'inventory_binding_passed_visual_and_runtime_limits_apply','cutscene_pngs':len(rows),'victory2_pngs':len(victory),'spin_pngs':len(spins),'review_states':dict(sorted(Counter(r['status'] for r in rows).items())),'limitations':['Hashes and dimensions verify source identity and coverage, not human review accuracy.','No composited playback, LPF, other asset groups or runtime certification.']}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',required=True,type=Path);p.add_argument('--write-report',action='store_true');a=p.parse_args();report=verify(a.game)
    if a.write_report:(ROOT/'docs/cutscene-image-review-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
