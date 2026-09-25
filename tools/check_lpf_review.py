"""Check source identity and LPF review accounting, not visual/runtime correctness."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def verify(game):
    review = json.loads((ROOT / 'docs/lpf-image-review.json').read_text(encoding='utf-8'))
    rows = review['records']
    names = [r['source_path'] for r in rows]
    assert len(names) == len(set(names)) == 2
    assert review['complete'] is False
    with zipfile.ZipFile(game / 'content/packages/uqm-0.8.0-content.uqm') as source:
        assert set(names) == {n for n in source.namelist() if n.endswith('.lpf')}
        for row in rows:
            raw = source.read(row['source_path'])
            assert hashlib.sha256(raw).hexdigest() == row['source_sha256']
            audit = row['record_table_audit']
            assert struct.unpack_from('<I', raw, 8)[0] == audit['header_records']
            assert struct.unpack_from('<I', raw, 64)[0] == audit['header_frames']
            assert raw[26] == audit['has_last_delta'] == 1
            assert raw[27] == audit['last_delta_valid'] == 1
            page_count = struct.unpack_from('<H', raw, 6)[0]
            table = struct.unpack_from('<H', raw, 14)[0]
            records = {}
            for i in range(page_count):
                base, count, size = struct.unpack_from('<HHH', raw, table + i * 6)
                page = table + 1536 + i * 65536
                sizes = struct.unpack_from('<' + 'H' * count, raw, page + 8)
                assert page + 8 + 2 * count + sum(sizes) <= len(raw)
                for j, record_size in enumerate(sizes):
                    assert base + j not in records
                    records[base + j] = record_size
            assert sorted(records) == list(range(audit['header_records']))
            empty = sorted(k for k, v in records.items() if v == 0)
            assert empty == sorted(r['id'] for r in audit['empty'])
            assert sum(v > 0 for v in records.values()) == audit['nonempty']
            assert row['frames'] == len(row['frame_png_sha256'])
            assert row['decoder_exit_code'] == 0
            assert row['action'] == 'preserve_original_bytes'
            # Original decoding omitted the separate-page victory2 loop only.
            omitted_loop = int(row['source_path'].endswith('victory2.lpf'))
            assert row['frames'] + omitted_loop == audit['nonempty']
        refs = [n for n in source.namelist() if n.endswith(('.ani', '.txt', '.rmp'))
                and any(Path(name).name.encode() in source.read(n) for name in names)]
        assert refs == [], refs
    return {'status': 'source_and_record_accounting_passed', 'lpf_files': len(rows),
            'default_decoded_frames': sum(r['frames'] for r in rows),
            'supplemental_loop_frames_reviewed': 1,
            'limitations': 'Does not rerun FFmpeg, verify visual judgments, or certify game playback.'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--game', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(verify(args.game), ensure_ascii=False, indent=2))
