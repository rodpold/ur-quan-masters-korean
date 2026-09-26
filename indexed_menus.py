"""Restore original palette semantics after all menu text compositing."""
import hashlib,json
from pathlib import Path
from special_labels import preserve_indexed_colors
ROOT=Path(__file__).resolve().parent

def load_indexed_menus():
    return json.loads((ROOT/'translations/indexed-menus.ko.json').read_text(encoding='utf8'))['rows']

def finalize_menu(target,raw,rendered):
    row=next((r for r in load_indexed_menus() if r['target']==target),None)
    if row is None:return rendered
    if hashlib.sha256(raw).hexdigest()!=row['source_sha256']:raise ValueError('Menu palette source changed')
    return preserve_indexed_colors(raw,rendered)

def add_indexed_menus(entries,source):
    for row in load_indexed_menus():
        target=row['target']
        entries[target]=finalize_menu(target,source.read(row['source']),entries[target])
