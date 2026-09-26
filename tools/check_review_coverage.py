"""Bind agent review coverage to current bytes; never certify linguistic quality."""
import argparse
import hashlib
import json
from pathlib import Path
import re
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
REVIEW_STATUS = 'agent_semantic_review_pass_human_and_runtime_pending'


def evidence_errors(item, translated_bytes, source_bytes, allowed_ids):
    errors = []
    if hashlib.sha256(translated_bytes).hexdigest() != item['translation_sha256']:
        errors.append('translation_changed_since_review')
    if hashlib.sha256(source_bytes).hexdigest() != item['source_sha256']:
        errors.append('source_changed_since_review')
    ids = item['reviewed_record_ids']
    if len(ids) != len(set(ids)):
        errors.append('duplicate_reviewed_ids')
    if not set(ids) <= set(allowed_ids):
        errors.append('unknown_reviewed_ids')
    return errors


def credit_source_ids(raw):
    text = raw.decode('utf-8-sig')
    headers = list(re.finditer(r'^#\([^\r\n]*\)[^\r\n]*\r?\n', text, re.M))
    return {f'{i:04d}' for i, header in enumerate(headers)
            if text[header.end():headers[i+1].start() if i+1<len(headers) else len(text)].strip()}


def audit(root, game):
    specs = {}
    for folder, category in [('dialogue', 'base_dialogue'), ('dialogue-voice', 'voice_overrides')]:
        for p in sorted((root/'translations'/folder).glob('*.ko.json')):
            species = p.name.removesuffix('.ko.json')
            source_species = 'yehatrebels' if species == 'yehat.rebel' else species
            source = (f'base/comm/{source_species}/{source_species}.txt' if category == 'base_dialogue'
                      else f'3dovoice/{source_species}/{source_species}.txt')
            specs[p.relative_to(root).as_posix()] = (category, source, json.loads(p.read_text(encoding='utf-8')))
    for name in ['intro', 'ending']:
        p = root/f'translations/{name}.ko.json'
        spec = json.loads(p.read_text(encoding='utf-8'))
        specs[p.relative_to(root).as_posix()] = ('cutscene_subtitles', spec['source_path'], spec['records'])
    report_path = root/'translations/reports.ko.json'
    if report_path.exists():
        for source, records in json.loads(report_path.read_text(encoding='utf-8')).items():
            specs['translations/reports.ko.json::'+source] = ('surface_reports', source, records)
    credit_path = root/'translations/credits.ko.json'
    if credit_path.exists():
        spec = json.loads(credit_path.read_text(encoding='utf-8'))
        specs['translations/credits.ko.json'] = ('credits', spec['source_path'], {row['id']: row for row in spec['records']})
    evidence = {key: [] for key in specs}
    issues = []
    for p in sorted((root/'docs').glob('*language-review.json')):
        report = json.loads(p.read_text(encoding='utf-8'))
        if report.get('status') != REVIEW_STATUS:
            continue
        items = report.get('resources', [report])
        for item in items:
            key = item['translation_path']
            if key == 'translations/reports.ko.json':
                key += '::'+item['source_path']
            if key not in specs:
                issues.append({'report': p.name, 'error': 'unknown_translation_path', 'path': key})
                continue
            evidence[key].append((p.name, item))
        if 'voice_variant' in report:
            key = report['translation_path'].replace('/dialogue/', '/dialogue-voice/')
            if key not in specs:
                issues.append({'report': p.name, 'error': 'unknown_voice_path', 'path': key})
            else:
                evidence[key].append((p.name, report['voice_variant']))
    rows = []
    with ZipFile(game/'content/packages/uqm-0.8.0-content.uqm') as base, ZipFile(game/'content/addons/uqm-0.8.0-voice.uqm') as voice:
        for key, (category, source, records) in specs.items():
            raw = (voice if category == 'voice_overrides' else base).read(source)
            translation_path = key.split('::', 1)[0]
            translated = (root/translation_path).read_bytes()
            valid_ids = set()
            reports = []
            for report_name, item in evidence[key]:
                errors = evidence_errors(item, translated, raw, records)
                if item['source_path'] != source:
                    errors.append('wrong_source_path')
                if category != 'cutscene_subtitles':
                    source_ids = set(re.findall(r'^#\(([^)]*)\)', raw.decode('utf-8-sig'), re.M))
                    if category == 'credits':
                        source_ids = credit_source_ids(raw)
                    if not set(item['reviewed_record_ids']) <= source_ids:
                        errors.append('review_ids_missing_in_source')
                if errors:
                    issues.append({'report': report_name, 'path': key, 'errors': errors})
                else:
                    valid_ids.update(item['reviewed_record_ids'])
                    reports.append(report_name)
            rows.append(dict(translation_path=translation_path, source_path=source, category=category, total_records=len(records),
                             current_agent_review_records=len(valid_ids),
                             pending_ids=[i for i in records if i not in valid_ids], reports=reports))
    totals = {}
    for category in ['base_dialogue', 'voice_overrides', 'cutscene_subtitles', 'surface_reports', 'credits']:
        selected = [r for r in rows if r['category'] == category]
        total = sum(r['total_records'] for r in selected)
        reviewed = sum(r['current_agent_review_records'] for r in selected)
        totals[category] = dict(total_records=total, current_agent_review_records=reviewed, pending_records=total-reviewed)
    return dict(status='current_review_evidence_audited', complete=False, totals=totals, issues=issues, resources=rows,
                limitations=['Counts attest current source/translation bytes and recorded review IDs, not semantic correctness or human approval.',
                             'Dialogue, voice overrides, cutscenes, surface reports and credits are counted separately; other UI and image text are outside this report.',
                             'All runtime and human review remains a separate requirement.'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game', type=Path, required=True)
    parser.add_argument('--write-report', action='store_true')
    args = parser.parse_args()
    result = audit(ROOT, args.game)
    if args.write_report:
        (ROOT/'docs/review-coverage.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'resources'}, ensure_ascii=False, indent=2))
    raise SystemExit(bool(result['issues']))
