"""Validate the glossary and explicitly linked UI terms (stdlib only)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def validate(data, ui):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported glossary schema')
    ids, sources, bindings = set(), set(), set()
    entries = data.get('terms')
    if not isinstance(entries, list) or not entries:
        raise ValueError('Expected nonempty terms list')
    for entry in entries:
        key = entry.get('id')
        source = entry.get('source')
        if not isinstance(key, str) or not key.strip() or key in ids:
            raise ValueError(f'Empty or duplicate id: {key}')
        if not isinstance(source, str) or not source.strip() or source.casefold() in sources:
            raise ValueError(f'Empty or duplicate source: {source}')
        ids.add(key); sources.add(source.casefold())
        status = entry.get('status')
        if status not in {'in_use', 'proposed', 'approved', 'preserve'}:
            raise ValueError(f'{key}: invalid status')
        if not entry.get('category') or not isinstance(entry.get('notes'), str):
            raise ValueError(f'{key}: missing category or notes')
        ko = entry.get('ko')
        if status == 'preserve':
            if ko is not None:
                raise ValueError(f'{key}: preserved names must not have fixed translations')
        elif not isinstance(ko, str) or not ko.strip():
            raise ValueError(f'{key}: missing Korean term')
        links = entry.get('ui_keys')
        if not isinstance(links, list):
            raise ValueError(f'{key}: ui_keys must be a list')
        for link in links:
            if not isinstance(link, str) or link in bindings:
                raise ValueError(f'{key}: invalid or duplicate UI binding')
            if status not in {'in_use', 'approved'} or link not in ui or ui[link] != ko:
                raise ValueError(f'{key}: UI translation mismatch for {link}')
            bindings.add(link)
    return len(entries), len(bindings)

if __name__ == '__main__':
    data = json.loads((ROOT/'translations/glossary.ko.json').read_text(encoding='utf-8'))
    ui = json.loads((ROOT/'translations/ui.ko.json').read_text(encoding='utf-8'))
    count, linked = validate(data, ui)
    print(f'Glossary OK: {count} entries, {linked} linked UI terms')
