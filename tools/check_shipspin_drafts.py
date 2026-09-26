"""Validate dormant ship-presentation drafts without activating them."""
from pathlib import Path
from zipfile import ZipFile
import argparse,hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]

def check(source):
    draft=json.loads((ROOT/'translations/shipspin-drafts.ko.json').read_text(encoding='utf8'))
    terms={t['id']:t['ko'] for t in json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf8'))['terms']}
    assert draft['status']=='draft_prepared_only_not_installed'
    total=0
    for resource in draft['resources']:
        raw=source.read(resource['source_path']);assert hashlib.sha256(raw).hexdigest()==resource['source_sha256']
        actual=[]
        for number,line in enumerate(raw.decode().splitlines(),1):
            m=re.fullmatch(r'TEXT (\d+) (\d+) (.*)',line)
            if m:actual.append((number,int(m[1]),int(m[2]),m[3]))
        records=resource['records'];assert len(actual)==len(records)==4
        for expected,row in zip(actual,records):
            assert expected==(row['line'],row['x'],row['y'],row['source'])
            assert row['ko'].strip() and '\n' not in row['ko'] and len(row['ko'].encode('utf8'))<=255
            for term in row['glossary_ids']:assert terms[term] in row['ko']
        total+=len(records)
    assert total==12
    return {'status':'draft_source_and_terms_checked_not_deployed','records':total,'runtime_verified':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);a=p.parse_args()
    with ZipFile(a.source) as z:print(json.dumps(check(z),indent=2))
