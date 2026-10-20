"""Offline CENSUS2 reissue; read-only source checkouts, assert local import."""
from greekocr.ops.data_root import input_path as _data_input
from pathlib import Path
import greekocr
ROOT = Path(__file__).resolve().parents[2]
assert Path(greekocr.__file__).resolve().is_relative_to(ROOT), greekocr.__file__
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from itertools import zip_longest
from greekocr.harvest import admission as a

BASE = ROOT.parent / 'greek-ocr-toolkit'
OUT = ROOT / 'docs/records/harvest/collection/v2'
OUT.mkdir(parents=True, exist_ok=True)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def write(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n')

inputs = [BASE / f'docs/harvest/collection/v2/import_real_v2_{s}.jsonl' for s in ('train', 'dev', 'test')]
rows = [json.loads(line) for p in inputs for line in p.read_text().splitlines() if line.strip()]
assert len(rows) == 271987
docs = defaultdict(Counter)
for r in rows:
    if r.get('wave') == 'cyrillic':
        docs[r['doc']][r['source']] += 1
# Each saved catalogue entry is also checked against the acquisition manifest.
evidence = BASE / 'docs/harvest/cyrillic/source_books.json'
books = {b['source']: b for b in json.loads(evidence.read_bytes())}
languages = {}
for doc, sources in sorted(docs.items()):
    assert len(sources) == 1
    source = next(iter(sources))
    b = books[source]
    acquisition = BASE / f"docs/records/harvest/cyrillic/acquisitions/{b['key']}.json"
    saved = json.loads(acquisition.read_bytes())['book']
    assert saved['catalogue_language'] == b['catalogue_language']
    raw_language = b['catalogue_language']
    values = raw_language if isinstance(raw_language, list) else [raw_language]
    codes = [{'Serbian': 'srp', 'Russian': 'rus'}.get(v, v) for v in values]
    assert all(c in ('srp', 'rus', 'bul', 'eng', 'ger', 'lat') for c in codes)
    languages[doc] = dict(language=codes[0] if len(codes) == 1 else codes,
                          recorded_language=raw_language, serbian='srp' in codes,
                          source=source, identifier=b['book'], rows=sum(sources.values()),
                          evidence_path=str(evidence), evidence_sha256=sha(evidence.read_bytes()),
                          evidence_field=f"[source={source}].catalogue_language",
                          corroborating_path=str(acquisition),
                          corroborating_sha256=sha(acquisition.read_bytes()),
                          evidence_url=f"https://archive.org/metadata/{b['book']}")
assert sorted(d for d, v in languages.items() if v['serbian']) == list(a.SERBIAN_DOCUMENTS)
write(OUT / 'census2_document_language.json', languages)
prefix = OUT / 'ADMISSION_CENSUS_20261018'
receipt = a.run_files(inputs, census=prefix)
assert receipt['rows_total'] == 271987
old_raw = subprocess.check_output(['git', 'show', 'c9fbf9a8:docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017_admission.jsonl'], cwd=ROOT)
old_receipt = json.loads(subprocess.check_output(['git', 'show', 'c9fbf9a8:docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261017_admission_receipt.json'], cwd=ROOT))
assert old_receipt['rows_total'] - old_receipt['rows_pass'] == 10370
assert old_receipt['input_sha256'] == receipt['input_sha256']
assert old_receipt['serbian_extension_sha256'] == receipt['serbian_extension_sha256']
old = [json.loads(l) for l in old_raw.splitlines()]
new_path = OUT / 'ADMISSION_CENSUS_20261018_admission.jsonl'
new = [json.loads(l) for l in _data_input(new_path).read_text().splitlines()]
changes, details = Counter(), []
wave = defaultdict(lambda: {'old': Counter(), 'new': Counter()})
for index, (r, before, after) in enumerate(zip_longest(rows, old, new), 1):
    assert r is not None and before is not None and after is not None
    assert before.keys() == after.keys()
    assert before['row_id'] == after['row_id']
    w = r.get('wave', r['source'])
    wave[w]['old'].update(before['rules_failed'])
    wave[w]['new'].update(after['rules_failed'])
    if before != after:
        assert r['wave'] == 'cyrillic' and r['doc'] in a.SERBIAN_DOCUMENTS
        assert set(before['rules_failed']) - set(after['rules_failed']) <= {'foreign_char'}
        assert set(before['foreign_chars']) - set(after['foreign_chars']) <= set(a.SERBIAN_EXTENSION_ATOMS)
        assert set(after['foreign_chars']) < set(before['foreign_chars'])
        assert not set(after['rules_failed']) - set(before['rules_failed'])
        assert not before['pass']
        details.append(dict(input_row=index, row_id=after['row_id'], doc=r['doc'],
                            old_pass=before['pass'], new_pass=after['pass'],
                            old_rules=before['rules_failed'], new_rules=after['rules_failed']))
    if before['pass'] != after['pass']:
        changes[r['doc']] += 1
write(OUT / 'census2_changed_rows.json', details)
comparison = dict(old_fail=10370, new_fail=receipt['rows_total'] - receipt['rows_pass'],
                  old_per_rule=old_receipt['drops_per_rule'], new_per_rule=receipt['drops_per_rule'],
                  per_wave_rule=wave, decision_changes_by_document=changes,
                  changed_decisions=sum(changes.values()), changed_output_rows=len(details),
                  no_non_serbian_changes=True, unknown_or_ambiguous_documents=[],
                  serbian_rows=sum(v['rows'] for v in languages.values() if v['serbian']),
                  admission_sha256=sha(_data_input(new_path).read_bytes()),
                  old_admission_sha256=sha(old_raw), network_requests=0)
write(OUT / 'census2_comparison.json', comparison)
receipt.update(admission_sha256=comparison['admission_sha256'],
               document_language_sha256=sha((OUT / 'census2_document_language.json').read_bytes()),
               serbian_document_rows=comparison['serbian_rows'])
write(OUT / 'ADMISSION_CENSUS_20261018_admission_receipt.json', receipt)
md = prefix.with_suffix('.md')
with md.open('a') as f:
    f.write('\n## CENSUS2 comparison against committed ADM5c c9fbf9a8\n\n')
    f.write(f"Fails: 10,370 → {comparison['new_fail']:,}. Changed pass/fail decisions: {sum(changes.values())}. Changed output rows: {len(details)}. No non-Serbian output or decision changed (full ordered comparison).\n\n")
    f.write('The sole new table entry adds exactly the ADM5c Serbian codec atoms to wave `cyrillic` documents in the recorded Serbian list. Script/class expectations remain in force, including Latin-class rows; no new script exemption.\n\n')
    f.write('| rule | ADM5c | CENSUS2 |\n|---|---:|---:|\n')
    for rule in a.RULES:
        f.write(f"| {rule} | {old_receipt['drops_per_rule'][rule]} | {receipt['drops_per_rule'][rule]} |\n")
    f.write('\n### Wave × rule (old → new)\n\n| wave | ' + ' | '.join(a.RULES) + ' |\n|---|' + '---:|' * len(a.RULES) + '\n')
    for w, counts in sorted(wave.items()):
        f.write('| ' + w + ' | ' + ' | '.join(f"{counts['old'][r]} → {counts['new'][r]}" for r in a.RULES) + ' |\n')
    f.write('\n### Document language and changed decisions\n\n| document | language | Serbian | rows | changed decisions |\n|---|---|---|---:|---:|\n')
    for d, info in languages.items():
        f.write(f"| {d} | {info['language']} | {info['serbian']} | {info['rows']} | {changes[d]} |\n")
    f.write('\nAll 12 languages were recorded in `source_books.json` and corroborated by acquisition manifests. No unknown or ambiguous documents; no network used. Multilingual `srp/ger/lat` explicitly includes Serbian. Evidence fields and hashes: [language map](census2_document_language.json). Exact affected rows (including rows still failing other rules): [changed rows](census2_changed_rows.json). Machine-readable comparison: [comparison](census2_comparison.json).\n\n')
    f.write(f"Serbian document-list SHA-256 (sorted compact JSON, no newline): `{a.serbian_documents_sha256()}`. Extension SHA-256 unchanged: `{a.serbian_extension_sha256()}`.\n\nAdmission file SHA-256: `{comparison['admission_sha256']}`.\n")
print(json.dumps(comparison, ensure_ascii=False, default=dict))
