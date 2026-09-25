"""Track actual game-string blocks, keeping duplicate labels and pending text."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import patcher
from inventory_text import blocks

PRESERVED={'Vindicator':'default_player_editable_ship_name','Zelnick':'default_player_editable_captain_name',
           'Cr':'unit_abbreviation','RU':'unit_abbreviation',' a.u.':'unit_abbreviation',
           ' atm':'unit_abbreviation',' e.s.':'unit_abbreviation',' g.':'unit_abbreviation'}

def audit_ui(raw,translations,overrides=None):
    original=raw.decode('utf-8-sig')
    translated,counts=patcher.translate_table(original,translations,overrides)
    before=list(blocks(original));after=list(blocks(translated))
    assert len(before)==len(after)
    rows=[]
    for (index,label,src),(new_index,new_label,dst) in zip(before,after):
        assert (index,label)==(new_index,new_label)
        override=(overrides or {}).get('records',{}).get(f'{index:04d}')
        if src in translations or override:
            assert dst==(override['ko'] if override else translations[src])
            assert re.findall(r'%[-+0-9.]*[sduf]',src)==re.findall(r'%[-+0-9.]*[sduf]',dst)
            months='JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC'.split()
            if src in months:
                assert dst==str(months.index(src)+1)+'월'
            else:
                assert re.findall(r'\d+(?:[.,]\d+)*',src)==re.findall(r'\d+(?:[.,]\d+)*',dst),index
            assert len(src)-len(src.lstrip(' '))==len(dst)-len(dst.lstrip(' ')),index
            assert len(src)-len(src.rstrip(' '))==len(dst)-len(dst.rstrip(' ')),index
            decision='translated_draft'
        else:
            assert src==dst
            decision='preserve_blank' if not src else PRESERVED.get(src,'translation_pending')
        rows.append({'id':f'{index:04d}','source_text_sha256':hashlib.sha256(src.encode()).hexdigest(),'status':decision})
    return {'source_path':'base/gamestrings.txt','source_sha256':hashlib.sha256(raw).hexdigest(),
            'translated_records':sum(counts.values()),'total_records':len(rows),
            'pending_records':sum(row['status']=='translation_pending' for row in rows),
            'status':'structure_passed_linguistic_and_runtime_review_pending',
            'context_specific_records':sorted((overrides or {}).get('records',{})),
            'limitations':['Record coverage does not prove meaning, screen fit, dynamic formatting, or installed UI behavior.','Repeated source labels require ordinal handling when meanings differ.'],
            'records':rows}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--game',type=Path,required=True);p.add_argument('--write-report',action='store_true');a=p.parse_args()
    with ZipFile(a.game/patcher.SOURCE) as z:
        result=audit_ui(z.read('base/gamestrings.txt'),json.loads((ROOT/'translations/ui.ko.json').read_text(encoding='utf-8')),patcher.load_ui_overrides())
    if a.write_report:(ROOT/'docs/ui-progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False,indent=2))
