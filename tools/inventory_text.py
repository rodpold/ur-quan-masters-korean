"""Inventory non-dialogue text without treating slide commands as prose."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path('content/packages/uqm-0.8.0-content.uqm')
CONTROL = set('CALL DIMS CLS FTB TC TBC TE FONT ANI TVA DRAW FTC WAIT MUSIC RESYNC SYNC TFO TFC FTW BATCH RESTBG UNBATCH DSYNC SAVEBG LINE FE'.split())

def blocks(text):
    """Keep duplicate labels; ordinal identity is tied to the file hash."""
    matches = list(re.finditer(r'^#\(([^\r\n]*)\)[^\r\n]*\r?\n', text, re.M))
    for index, match in enumerate(matches):
        end = matches[index+1].start() if index+1 < len(matches) else len(text)
        yield index, match.group(1), text[match.end():end].rstrip('\r\n')

def classify(path, text):
    if path == 'base/cutscene/ending/pc_credits.txt':
        assert 'not used directly in UQM' in text
        return [{'id':'reference', 'kind':'reference_for_image_text', 'text':text}]
    result = []
    for index, label, body in blocks(text):
        entry = dict(id=f'{index:04d}', label=label, text=body)
        if not body.strip():
            entry['kind'] = 'comment_only'
        elif path == 'base/cutscene/credits/credits.txt':
            match = re.fullmatch(r'(\d+)\s+([LCR](?:/-?\d+)?(?:,[LCR](?:/-?\d+)?)*)[ \t]*(?:\n)?(.*)', body, re.S)
            if not match: raise ValueError(f'Unknown credit block: {path}/{index}')
            entry.update(kind='credit_text', format=match.group(1)+' '+match.group(2), text=match.group(3))
        elif path.startswith('base/cutscene/'):
            first, *rest = body.splitlines()
            op, _, args = first.partition(' ')
            if op == 'TFI':
                entry.update(kind='slide_text', command=op, text='\n'.join([args]+rest))
            elif op == 'TEXT':
                match = re.fullmatch(r'(-?\d+)\s+(-?\d+)\s+(.*)', args)
                if not match: raise ValueError(f'Unknown TEXT format: {path}/{index}')
                entry.update(kind='positioned_text', command=op, x=int(match[1]), y=int(match[2]), text='\n'.join([match[3]]+rest))
            elif op in CONTROL and not any(line.strip() for line in rest):
                entry.update(kind='control', command=op)
            else:
                raise ValueError(f'Unclassified slide command: {path}/{index}: {op}')
        elif path.startswith('base/ships/'):
            entry['kind'] = 'ship_name' if index < 5 else 'captain_name'
        elif path == 'base/ui/joyalpha.txt':
            entry['kind'] = 'name_entry_alphabet'
        else:
            entry['kind'] = 'string_table_entry'
        result.append(entry)
    if not result and text.strip():
        raise ValueError(f'Unclassified file: {path}')
    return result

def inventory(game):
    rows=[]
    with ZipFile(game/SOURCE) as archive:
        for path in sorted(archive.namelist()):
            if not path.endswith('.txt') or path.startswith(('base/comm/','base/lander/')): continue
            raw=archive.read(path)
            entries=classify(path,raw.decode('utf-8-sig').replace('\r\n','\n'))
            # Original prose stays in installed assets; only metadata is published.
            metadata=[]
            for entry in entries:
                body=entry['text']
                metadata.append({**{k:v for k,v in entry.items() if k not in ('text','label')},
                                 'text_sha256':hashlib.sha256(body.encode('utf-8')).hexdigest(),
                                 'lines':len(body.splitlines()),
                                 'decision':'preserve_control' if entry['kind'] in ('control','comment_only') else 'review_pending'})
            rows.append(dict(source_path=path,source_sha256=hashlib.sha256(raw).hexdigest(),
                             counts=dict(Counter(e['kind'] for e in entries)),entries=metadata))
    return dict(complete=False,scope='Base package text files outside dialogue and lander reports',
                limitations=['Not an inventory of text baked into images or video, or alternate add-on assets.',
                             'Ship-name/captain-name positions are candidate classification; runtime resource consumers need review.',
                             'Credit names, URLs and titles require separate preserve/translate decisions.',
                             'Ordinal IDs are only valid with the matching source file hash.'],resources=rows)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--game',type=Path,required=True);parser.add_argument('--write-report',action='store_true');args=parser.parse_args()
    result=inventory(args.game)
    if args.write_report:(ROOT/'docs/text-inventory.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts=Counter()
    for row in result['resources']:counts.update(row['counts'])
    print(json.dumps(dict(resources=len(result['resources']),counts=dict(counts)),indent=2))
