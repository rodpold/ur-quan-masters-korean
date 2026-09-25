"""Audit marked Orz phrases without asserting their hidden meaning."""
from collections import Counter
import re

def marked(line):
    result = re.findall(r'\*([^*\n]+)\*', line)
    if line.count('*') != 2 * len(result):
        raise ValueError('Unpaired or empty Orz marker')
    return result

def validate(source, translated, data):
    if data.get('schema_version') != 1:
        raise ValueError('Unsupported Orz concept schema')
    mapping = {}
    for item in data['concepts']:
        key, value = item['source'], item['ko']
        if (not key or key != key.lower().rstrip('.!') or key in mapping
                or not value or any(c in key + value for c in '*\r\n')):
            raise ValueError('Invalid or duplicate Orz concept')
        mapping[key] = value
    source_concepts = {x.lower().rstrip('.!') for body in source.values()
                       for line in body.splitlines() for x in marked(line)}
    if source_concepts != mapping.keys():
        raise ValueError('Orz concept inventory differs from source')
    occurrences = 0
    for key, body in translated.items():
        before, after = source[key].splitlines(), body.splitlines()
        if len(before) != len(after):
            raise ValueError(f'Orz segment count: {key}')
        for index, (english, korean) in enumerate(zip(before, after), 1):
            expected = Counter(mapping[x.lower().rstrip('.!')] for x in marked(english))
            actual = Counter(x.rstrip('.!') for x in marked(korean))
            if expected != actual:
                raise ValueError(f'Orz marked terms: {key}/{index}: {expected} != {actual}')
            occurrences += sum(expected.values())
    return {'concept_forms': len(mapping), 'translated_marked_occurrences': occurrences,
            'status': 'structure_passed_meaning_review_pending'}
