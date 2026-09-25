"""Ordinal-preserving ship tables; player save data is never rewritten."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def load_ships():
    return json.loads((ROOT/'translations/ships.ko.json').read_text(encoding='utf-8'))


def compile_ship(raw, spec):
    if hashlib.sha256(raw).hexdigest() != spec['source_sha256']:
        raise ValueError('Ship source hash mismatch: '+spec['source_path'])
    chunks = re.split(r'(?m)(^#\([^\r\n]*\)[^\r\n]*\r?\n)', raw.decode())
    records = {row['id']: row for row in spec['records']}
    if len(records) != len(spec['records']):
        raise ValueError('Duplicate ship ordinal')
    seen = set()
    for i in range(2, len(chunks), 2):
        ordinal = f'{(i-2)//2:04d}'
        if ordinal not in records:
            continue
        row = records[ordinal]
        body = chunks[i]; text = body.rstrip('\r\n')
        if text != row['source'] or not row['ko'].strip() or '\n' in row['ko'] or '\r' in row['ko']:
            raise ValueError('Invalid ship label: '+ordinal)
        chunks[i] = row['ko']+body[len(text):]
        seen.add(ordinal)
    if seen != set(records):
        raise ValueError('Unknown ship ordinal')
    return ''.join(chunks).encode()


def add_ships(source, spec):
    entries = {}; mappings = []
    rmp = source.read('uqm.rmp').decode().splitlines()
    for row in spec['resources']:
        path = row['source_path']
        expected = row['resource_key']+' = STRTAB:'+path
        if not any(re.sub(r'\s*=\s*', ' = ', line) == expected for line in rmp):
            raise ValueError('Ship resource mapping mismatch: '+path)
        target = path.replace('base/', 'ko/', 1)
        if target in entries:
            raise ValueError('Duplicate ship target')
        entries[target] = compile_ship(source.read(path), row)
        mappings.append(row['resource_key']+' = STRTAB:'+target)
    return entries, mappings
