"""Read-only CP6 text census comparison; stdout is a measurement, never admission.

No run_files/evaluate_rows, geometry preparation, crop loading or output rows are
written. Only segmentation rules and the unqualified segmentation pass status
are excluded; every CENSUS3 public text field is compared in ordered lockstep.
"""
import hashlib
import ast
import json
import os
from pathlib import Path
import sys
import unicodedata as ud

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from greekocr.harvest import admission as a
SEG = ROOT / 'docs/harvest/collect_v3_admission/seg'
CENSUS = ROOT.parent / 'greek-ocr-toolkit-sol-census'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_projection(record, *, codec=None, median=None):
    result = a.evaluate(record, codec=codec, page_median_height=median)
    row = a.output_row(record, result, 'fixture')
    row['rules_failed'] = [r for r in row['rules_failed']
                           if r not in ('geometry_unavailable', 'neighbour_words')]
    row['pass'] = not row['rules_failed']
    return dict(row=row, label=result['label'], normalisations=result['normalisations'])


def read_rows(path):
    with path.open() as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def review_cp5c(codec):
    """Audit committed hook accounting and reproduce incomplete text eligibility.

    No orientation inference or new population selection is performed here.
    """
    cp5 = json.loads((SEG / 'CP5_verification.json').read_text())
    cases = cp5['cases']
    unknowns = [c for c in cases if c['orientation'].get('decision', {}).get('axis') == 'unknown']
    expected = {}
    for c in unknowns:
        key = (c['dataset_source'], c['primary_class'])
        bucket = expected.setdefault(key, dict(ids=set(), membership=set(), tall=set()))
        bucket['ids'].add(c['row_id'])
        if c['old_rotated_crop']['membership']: bucket['membership'].add(c['row_id'])
        if c['old_rotated_crop']['tall_text']: bucket['tall'].add(c['row_id'])
    for hook in cp5['cp7_orientation_unknown_hooks']:
        bucket = expected.pop((hook['source'], hook['primary_class']))
        assert set(hook['unknown_ids']) == bucket['ids']
        assert hook['unknown_count'] == len(bucket['ids'])
        assert set(hook['membership_ids']) == bucket['membership']
        assert set(hook['tall_text_ids']) == bucket['tall']
        assert set(hook['old_rotated_crop_excluded_ids']) == bucket['membership'] | bucket['tall']
        assert hook['old_rotated_crop_excluded_count'] == len(bucket['membership'] | bucket['tall'])
    assert not expected
    features_path = ROOT.parent / 'collect-v3-data/run/W1/features.jsonl'
    feature_sha = sha(features_path)
    assert feature_sha == cp5['features_sha256']
    eligible_cases = {c['row_id']: c for c in cases if c.get('text_rules', {}).get('passed')}
    omissions = {}
    for record in read_rows(features_path):
        if record['id'] not in eligible_cases:
            continue
        result = a.evaluate(record, codec=codec)
        failures = [r for r in result['failed_rules'] if r not in ('geometry_unavailable', 'neighbour_words')]
        if failures:
            omissions[record['id']] = failures
    assert sha(features_path) == feature_sha
    tree = ast.parse((SEG / 'verify_cp5.py').read_text())
    filters = [ast.literal_eval(n) for n in ast.walk(tree) if isinstance(n, ast.Tuple)
               and n.elts and isinstance(n.elts[0], ast.Constant) and n.elts[0].value == 'short_line']
    assert len(set(filters)) == 1
    eligibility_rules = filters[0]
    counterexamples = []
    for record in (dict(source='bsb_poly1850', label='ἑλληνικὸς λόγος', confidence=.88),
                   dict(source='archive_b24878935', wave='cyrillic', script_class='cyrillic',
                        label='Это чистая русская строка coco')):
        checks = a.evaluate(record, codec=codec)['checks']
        excluded = [k for k, v in checks.items() if v == 'fail' and k in eligibility_rules]
        failures = [k for k, v in checks.items() if v == 'fail' and k not in ('geometry_unavailable', 'neighbour_words')]
        assert not excluded and failures
        counterexamples.append(dict(record=record, omitted_failures=failures))
    return dict(cases=len(cases), unknowns=len(unknowns), hook_groups=len(cp5['cp7_orientation_unknown_hooks']),
                hook_accounting_differences=0, falsely_text_eligible=len(omissions),
                false_text_eligibility=omissions, population_scope='historical IDs plus calibration/challenges only',
                features_path=str(features_path), features_sha256=feature_sha,
                eligibility_predicate_counterexamples=counterexamples)


def main():
    forbidden_attempts = []
    def audit(event, args):
        if event == 'open':
            _, mode, flags = args
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                forbidden_attempts.append(event)
                raise AssertionError('CP6 writes forbidden')
        if event.startswith('socket.') or event in ('subprocess.Popen', 'os.mkdir', 'os.rename', 'os.remove', 'os.rmdir', 'os.link', 'os.symlink'):
            forbidden_attempts.append(event)
            raise AssertionError('CP6 runtime action forbidden: ' + event)
    sys.addaudithook(audit)
    codec = a.load_codec()
    fixture = json.loads((SEG / 'CP6_text_fixtures.json').read_text())
    intentional = 0
    for case in fixture['cases']:
        current = text_projection(case['input'], codec=codec)
        assert current == case['ruled'], case['input']
        # Prior fields change only under CENSUS2/3's explicit ruling.
        before = case['before']
        prior_fields = {k: current['row'][k] for k in before['row']}
        intentional += prior_fields != before['row']
        assert current['label'] == before['label']
        assert current['normalisations'] == before['normalisations']
    paths = [ROOT.parent / 'greek-ocr-toolkit' / f'docs/harvest/collection/v2/import_real_v2_{s}.jsonl'
             for s in ('train', 'dev', 'test')]
    reference = CENSUS / 'docs/harvest/collection/v2/ADMISSION_CENSUS_20261018b_admission.jsonl'
    reference_sha = sha(reference)
    assert reference_sha == 'ef694589fa0e8e6875ac712159222d19177e0d02213d48031fa92ff1efbc6451'
    receipt = json.loads(reference.with_name('ADMISSION_CENSUS_20261018b_admission_receipt.json').read_text())
    digest = hashlib.sha256()
    hashes = {}
    for path in paths:
        raw = path.read_bytes(); digest.update(raw); hashes[str(path)] = sha(path)
    assert digest.hexdigest() == receipt['input_sha256']
    total = passed = reclassified = 0
    for path in paths:
        records = list(read_rows(path))
        # This mirrors the census input-file page-median boundary exactly.
        medians = a.page_medians(records)
        if total == 0:
            expected = iter(read_rows(reference))
        for index, record in enumerate(records, 1):
            before = next(expected)
            after = text_projection(record, codec=codec, median=medians.get(a._page_key(record)))
            row = after['row']
            # Preserve input-file/index fallback IDs used by run_files.
            if 'row_id' not in record and 'id' not in record:
                row['row_id'] = f'{path.name}:{index}'
            assert row == before, (total, row, before)
            raw_label = record.get('docai_text', record.get('label'))
            # Independent frozen ADM5c normalization expression, before cleanup.
            assert after['label'] == ' '.join(ud.normalize('NFC', raw_label.replace('\u02d9', '\u00b7')).split())
            total += 1; passed += row['pass']
            reclassified += row['class'] != row['class_original']
    assert next(expected, None) is None
    assert total == 271987 and passed == 269498 and reclassified == 6799
    assert hashes == {str(p): sha(p) for p in paths} and sha(reference) == reference_sha
    assert codec['sha256'] == sha(ROOT / 'greekocr/_vendor/codec/v2.json')
    assert a.serbian_extension_sha256() == receipt['serbian_extension_sha256']
    assert a.serbian_documents_sha256() == receipt['serbian_documents_sha256']
    assert a.lookalike_table_sha256() == receipt['lookalike_table_sha256']
    protected = json.loads((SEG / 'protected_before.json').read_text())
    for path, binding in protected.items():
        assert sha(ROOT / path) == binding['sha256'], path
    cp5c = review_cp5c(codec)
    print(json.dumps(dict(schema='CP6-verification-v1', fixture_cases=len(fixture['cases']),
        fixture_intentional_changed_rows=intentional, unintended_text_changes=0, label_changes=0,
        census_rows=total, census_pass=passed, census_fail=total-passed,
        census_reclassified=reclassified, census_field_differences=0,
        census_reference_sha256=reference_sha, input_hashes=hashes,
        codec_sha256=codec['sha256'], serbian_extension_sha256=a.serbian_extension_sha256(),
        serbian_documents_sha256=a.serbian_documents_sha256(), lookalike_table_sha256=a.lookalike_table_sha256(),
        cp5c_review=cp5c,
        protected_artifacts=len(protected), forbidden_attempts=forbidden_attempts,
        publish_actions=0, detector_calls=0), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
