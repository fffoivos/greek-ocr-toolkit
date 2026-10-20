"""Offline CENSUS3 census, full ordered CENSUS2 comparison and input readback."""
from pathlib import Path
import greekocr
ROOT = Path(__file__).resolve().parents[2]
assert Path(greekocr.__file__).resolve().is_relative_to(ROOT), greekocr.__file__
import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from itertools import chain, zip_longest
from greekocr.harvest import admission as a

OUT = ROOT / 'docs/harvest/collection/v2'
BASE = ROOT.parent / 'greek-ocr-toolkit'
BASELINE = '3f93d204'
PREFIX = OUT / 'ADMISSION_CENSUS_20261018b'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n')

def records(path):
    with path.open() as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

inputs = [BASE / f'docs/harvest/collection/v2/import_real_v2_{s}.jsonl' for s in ('train', 'dev', 'test')]
input_hashes = {str(p): sha(p) for p in inputs}
old_path = OUT / 'ADMISSION_CENSUS_20261018_admission.jsonl'
old_hash = sha(old_path)
committed = subprocess.check_output(['git', 'show', f'{BASELINE}:{old_path.relative_to(ROOT)}'], cwd=ROOT)
assert hashlib.sha256(committed).hexdigest() == old_hash
old_receipt = json.loads((OUT / 'ADMISSION_CENSUS_20261018_admission_receipt.json').read_text())
assert old_receipt['rows_total'] - old_receipt['rows_pass'] == 9427
receipt = a.run_files(inputs, census=PREFIX)
assert receipt['rows_total'] == 271987
assert receipt['input_sha256'] == old_receipt['input_sha256']
for key in ('serbian_documents_sha256', 'serbian_extension_sha256'):
    assert receipt[key] == old_receipt[key]
new_path = PREFIX.with_name(PREFIX.name + '_admission.jsonl')
per_class = defaultdict(lambda: Counter(fail_to_pass=0, pass_to_fail=0))
per_doc = defaultdict(lambda: Counter(fail_to_pass=0, pass_to_fail=0))
per_wave = defaultdict(Counter)
word_examples = Counter()
changed_rows = []
reclassified = decision_changes = rule_changed = 0
invariant_fields = ('row_id', 'source', 'letters', 'nonletter_frac', 'scripts_seen', 'mixed_script_words', 'foreign_chars')
for index, (r, before, after) in enumerate(zip_longest(chain.from_iterable(records(p) for p in inputs), records(old_path), records(new_path)), 1):
    assert r is not None and before is not None and after is not None
    assert set(after) == set(before) | {'class_original', 'lookalike_only_words'}
    assert all(before[k] == after[k] for k in invariant_fields)
    assert after['class_original'] == before['class']
    assert set(before['rules_failed']) - set(after['rules_failed']) <= {'unexpected_script'}
    assert set(after['rules_failed']) - set(before['rules_failed']) <= {'lookalike_only_word'}
    for rule in a.RULES:
        if rule not in ('unexpected_script', 'lookalike_only_word'):
            assert (rule in before['rules_failed']) == (rule in after['rules_failed'])
    cls = after['class_original']
    per_class[cls] # include zero-change classes
    if cls not in a.SECONDARY_SCRIPT_POLICIES:
        assert all(before[k] == after[k] for k in before)
        assert not after['lookalike_only_words']
    if before['class'] != after['class']:
        assert before['class'] == 'latin' and after['class'] == 'mixed_greek_latin'
        reclassified += 1
    word_examples.update(after['lookalike_only_words'])
    per_wave[r.get('wave', r['source'])].update(after['rules_failed'])
    if before['pass'] != after['pass']:
        direction = 'fail_to_pass' if after['pass'] else 'pass_to_fail'
        per_class[cls][direction] += 1
        per_doc[r['doc']][direction] += 1
        decision_changes += 1
    if before['rules_failed'] != after['rules_failed']:
        rule_changed += 1
    if any(before[k] != after[k] for k in before):
        changed_rows.append(dict(input_row=index, row_id=after['row_id'], doc=r['doc'],
            class_original=cls, new_class=after['class'], old_pass=before['pass'], new_pass=after['pass'],
            old_rules=before['rules_failed'], new_rules=after['rules_failed'],
            lookalike_only_words=after['lookalike_only_words']))
assert index == 271987
assert input_hashes == {str(p): sha(p) for p in inputs}
assert old_hash == sha(old_path)
comparison = dict(baseline_commit=BASELINE, old_fail=9427,
    new_fail=receipt['rows_total'] - receipt['rows_pass'], new_pass=receipt['rows_pass'],
    rows=receipt['rows_total'], per_class=per_class,
    decision_changes=decision_changes, changed_existing_field_rows=len(changed_rows), rule_changed_rows=rule_changed,
    decision_changes_by_document=per_doc,
    top_10_documents=[dict(doc=d, **c) for d,c in sorted(per_doc.items(), key=lambda item: (-sum(item[1].values()), item[0]))[:10]],
    reclassified_latin_to_mixed_greek_latin=reclassified,
    lookalike_only_word_fail_rows=receipt['drops_per_rule']['lookalike_only_word'],
    lookalike_word_examples=word_examples.most_common(20),
    old_per_rule=old_receipt['drops_per_rule'], new_per_rule=receipt['drops_per_rule'],
    per_wave_rule=per_wave, admission_sha256=sha(new_path), baseline_admission_sha256=old_hash,
    input_hashes_after_readback=input_hashes, inputs_unchanged=True, baseline_unchanged=True,
    unchanged_existing_rules_except_unexpected_script=True, network_requests=0,
    lookalike_table_name=a.LOOKALIKE_TABLE_NAME, lookalike_table_sha256=a.lookalike_table_sha256(),
    lookalike_provenance='Exact original e1_readout.HOMOGLYPHS groups, extracted to shared module. CENSUS2 mixed_script_word used script identities, no lookalike table. R6 remains unchanged.')
write(OUT / 'census3_changed_rows.json', changed_rows)
write(OUT / 'census3_comparison.json', comparison)
receipt.update(admission_sha256=comparison['admission_sha256'],
    reclassified_latin_to_mixed_greek_latin=reclassified, network_requests=0,
    document_language_sha256=sha(OUT / 'census2_document_language.json'))
write(PREFIX.with_name(PREFIX.name + '_admission_receipt.json'), receipt)
md = PREFIX.with_suffix('.md')
with md.open('a') as f:
    f.write('\n## CENSUS3 comparison against CENSUS2 3f93d204\n\n')
    f.write(f"Fails: 9,427 → {comparison['new_fail']:,}; passes: {receipt['rows_pass']:,}. Decision changes: {decision_changes:,}. Reclassified Latin → mixed_greek_latin: {reclassified:,} (includes rows failing another rule).\n\n")
    f.write('Class comparisons below use class_original. Every row adds class_original and lookalike_only_words; changed_existing_field_rows counts differences in prior fields, including expanded expected_scripts. Inputs and CENSUS2 decisions are hash-verified unchanged. All other existing rules and codec coverage are identical row by row. Serbian document policy, headings and numerics remain unchanged. Zero network requests.\n\n')
    f.write('| original class | fail → pass | pass → fail |\n|---|---:|---:|\n')
    for cls,c in sorted(per_class.items()):
        f.write(f"| {cls} | {c['fail_to_pass']} | {c['pass_to_fail']} |\n")
    f.write('\n### Top 10 documents by changed decisions\n\n| document | fail → pass | pass → fail |\n|---|---:|---:|\n')
    for entry in comparison['top_10_documents']:
        f.write(f"| {entry['doc']} | {entry['fail_to_pass']} | {entry['pass_to_fail']} |\n")
    f.write('\n### Per-rule failures\n\n| rule | CENSUS2 | CENSUS3 |\n|---|---:|---:|\n')
    for rule in a.RULES:
        f.write(f"| {rule} | {old_receipt['drops_per_rule'].get(rule, 0)} | {receipt['drops_per_rule'][rule]} |\n")
    f.write(f"\nlookalike_only_word: {comparison['lookalike_only_word_fail_rows']:,} failed rows. Twenty example tokens (most frequent, case-sensitive): " + ', '.join(f'`{w}` ({n})' for w,n in word_examples.most_common(20)) + '.\n\n')
    f.write(f"Lookalike table: `{a.LOOKALIKE_TABLE_NAME}`, SHA-256 `{a.lookalike_table_sha256()}` (ordered compact UTF-8 JSON, no newline).\n\n")
    f.write('Provenance clarification: CENSUS2 mixed_script_word did **not** use any lookalike table: it rejects any token containing multiple letter scripts. The existing case-sensitive `greekocr/_vendor/bench/e1_readout.py::HOMOGLYPHS` groups were extracted unchanged into a shared module for the new rule and the existing diagnostic consumer. No external table, folding or mapping is introduced; tests compare all groups against CENSUS2. The P in Paris has a Cyrillic counterpart in that table; s is distinguishing, so Paris passes. Checks inspect NFC letter code points exactly, without stripping accents or changing labels.\n\n')
    f.write('Secondary word admission is per declared cyrillic/latin class. Only all-single-script tokens qualify; lookalike-only tokens fail and are listed. Any admitted Greek token reclassifies a Latin row even if another rule fails. Receipt source|class groups use the resulting class.\n\n')
    f.write('[Full comparison](census3_comparison.json) · [Changed rows](census3_changed_rows.json)\n\n')
    f.write(f"Admission file SHA-256: `{comparison['admission_sha256']}`.\n")
print(json.dumps({k:v for k,v in comparison.items() if k not in ('decision_changes_by_document','input_hashes_after_readback','per_wave_rule')}, ensure_ascii=False))
