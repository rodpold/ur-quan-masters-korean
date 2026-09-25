"""Audit source coverage, immutable glossary terms, dialogue structure and persona links."""
import argparse,hashlib,json,re,sys
from pathlib import Path
from zipfile import ZipFile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import patcher

def records(text):
 p=re.split(r'(?m)^#\(([^\r\n)]*)\)[^\r\n]*\r?\n',text)
 return [(p[i],p[i+1].rstrip('\r\n')) for i in range(1,len(p),2)]

def canonical_terms(source, terms, source_path=None):
 # A full name owns its span; its embedded short name need not be repeated in Korean.
 # A separately occurring short name still has its own terminology requirement.
 matches=[]
 for term in terms:
  if 'audit_source_paths' in term and source_path not in term['audit_source_paths']:
   continue
  if term['ko']:
   pattern=r'(?<![A-Za-z])'+re.escape(term['source'])+r'(?![A-Za-z])'
   matches.extend((m.start(),m.end(),term) for m in re.finditer(pattern,source,0 if term.get('case_sensitive',False) else re.I))
 for start,end,term in matches:
  if not any(a<=start and end<=b and b-a>end-start for a,b,_ in matches):
   yield term

def check_dialogue_record(original, translated, terms, source_path, label):
 assert len(original.splitlines())==len(translated.splitlines()),f'Voice segmentation: {label}'
 assert re.findall(r'%[-+0-9.]*[sduf]',original)==re.findall(r'%[-+0-9.]*[sduf]',translated),f'Placeholder: {label}'
 for token in re.findall(r'\d+(?:[.,]\d+)*',original):assert token in translated,f'Number lost: {label}: {token}'
 if original.endswith(' '):assert translated.endswith(' '),f'Dynamic suffix space: {label}'
 for term in canonical_terms(original,terms,source_path):
  assert term['ko'] in translated,f'Canonical term missing: {label}: {term["source"]} -> {term["ko"]}'

def audit(game):
 reg=json.loads((ROOT/'translations/fonts.ko.json').read_text(encoding='utf-8'))
 per=json.loads((ROOT/'translations/personas.ko.json').read_text(encoding='utf-8'))
 terms={t['id']:t for t in json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))['terms']}
 lock=json.loads((ROOT/'translations/glossary.lock.json').read_text(encoding='utf-8'))['terms']
 for id,t in lock.items():assert id in terms and all(terms[id][k]==v for k,v in t.items()),f'Locked term changed: {id}'
 rows=[];other=[];translated_total=0;total=0
 reports=patcher.report_translations()
 with ZipFile(Path(game)/patcher.SOURCE) as z:
  patcher.report_assets(z,reports)
  for row in reg['dialogue_fonts']:
   id=row['id'];group=row['font_group'];profile=per['profiles'][group]
   assert row['glossary_ids'] and set(row['glossary_ids'])<=terms.keys()
   assert profile['font_group']==group
   source_id='yehatrebels' if id=='yehat.rebel' else id
   path=f'base/comm/{source_id}/{source_id}.txt';source=z.read(path);src=dict(records(source.decode('utf-8-sig')))
   evidence=dict(records(z.read(profile['source_path']).decode('utf-8-sig')))
   assert set(profile['evidence_record_ids'])<=evidence.keys()
   p=ROOT/'translations/dialogue'/f'{id}.ko.json';trans=json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}
   assert set(trans)<=src.keys(),f'Unknown IDs: {id}'
   active,suffix=patcher.dialogue_source(game,path,row['dialogue_resource'],source)
   selected=patcher.edition_translations(id,source.decode('utf-8'),active.decode('utf-8'),trans)
   patcher.translate_dialogue(active.decode('utf-8'),selected)
   for key,text in trans.items():
    check_dialogue_record(src[key],text,terms.values(),path,f'{id}/{key} [base]')
   active_src=dict(records(active.decode('utf-8-sig')))
   for key,text in selected.items():
    if active_src[key]!=src[key] or text!=trans.get(key):
     check_dialogue_record(active_src[key],text,terms.values(),path,f'{id}/{key} [active edition]')
   translated_total+=len(trans);total+=len(src)
   rows.append({'id':id,'source_path':path,'source_sha256':hashlib.sha256(source).hexdigest(),'records':len(src),'translated':len(trans),'untranslated_ids':[k for k in src if k not in trans],'persona':group,'status':'translated_draft' if len(trans)==len(src) else 'partial' if trans else 'not_started','linguistic_review':'pending','in_game_review':'pending'})
  for n in z.namelist():
   if n.endswith('.txt') and not n.startswith('base/comm/'):
    data=z.read(n);rr=records(data.decode('utf-8-sig'))
    report_trans=reports.get(n,{})
    for key,text in report_trans.items():
     original=dict(rr)[key]
     assert [bool(x.strip()) for x in original.splitlines()]==[bool(x.strip()) for x in text.splitlines()],f'Report paragraphs: {n}/{key}'
     assert re.findall(r'%[-+0-9.]*[sduf]',original)==re.findall(r'%[-+0-9.]*[sduf]',text),f'Report placeholder: {n}/{key}'
     for token in re.findall(r'\d+(?:[.,]\d+)*',original):assert token in text,f'Report number: {n}/{key}: {token}'
     for term in canonical_terms(original,terms.values(),n):assert term['ko'] in text,f'Report term: {n}/{key}: {term["source"]}'
    status=('translated_draft' if len(report_trans)==len(rr) else 'partial') if report_trans else ('partial_existing_patch' if n in ['base/gamestrings.txt','base/ui/setupmenu.txt'] else 'not_started_or_requires_classification')
    other.append({'source_path':n,'source_sha256':hashlib.sha256(data).hexdigest(),'records':len(rr),'translated':len(report_trans) if n.startswith('base/lander/') else None,'status':status,'linguistic_review':'pending','in_game_review':'pending'})
 return {'goal':'full_game_korean_localization','complete':False,'dialogue_records':total,'translated_report_records':sum(map(len,reports.values())),'report_records':sum(row['records'] for row in other if row['source_path'].startswith('base/lander/')),'translated_dialogue_records':translated_total,'dialogue_coverage_percent':round(translated_total*100/total,2),'locked_terms':len(lock),'persona_groups':len(per['profiles']),'dialogue':rows,'other_text_resources':other,'limitations':['Coverage counts translated records, not meaning/style quality or rendered layout.','Other text includes technical/credit/name fragments; classify before marking preserved/translated.','Numeric check preserves source digit tokens but does not prove dynamic numeral grammar.']}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--game',required=True,type=Path);p.add_argument('--write-report',action='store_true');a=p.parse_args();report=audit(a.game)
 if a.write_report:(ROOT/'docs/localization-progress.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({k:v for k,v in report.items() if k not in ['dialogue','other_text_resources']},ensure_ascii=False,indent=2))
