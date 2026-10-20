"""Independent receipt, unchanged-verdict, dimensions, sample and scope readback."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from PIL import Image

D = Path(__file__).resolve().parent
ROOT = D.parents[4]


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    initial = json.loads((D / 'initial_state.json').read_text())
    receipt = json.loads((D / 'export_receipt.json').read_text())
    summary = json.loads((D / 'population_summary.json').read_text())
    assert sha(D / 'population_cells.jsonl.gz') == receipt['reduced_sha256']
    assert receipt['export_receipt']['export_sha256'] == '568d4759257787086ee8c0780cd0d4cf633c5ebf7b355d519d6053ff8c42764a'
    assert receipt['export_receipt']['rows'] == 592466
    assert receipt['export_receipt']['stat_unchanged'] and receipt['export_receipt']['current_unchanged']
    assert sha(ROOT / 'greekocr/harvest/numeric_cells.py') == receipt['classifier_sha256']
    old = gzip.open(D.parent / 'keys/pipeline_population.jsonl.gz', 'rt')
    old_provenance = json.loads(next(old))['_provenance']
    assert old_provenance['current'] == receipt['provenance']['current']
    counts, verdicts, dispositions, ids, numeric_ids = Counter(), Counter(), Counter(), set(), set()
    with gzip.open(D / 'population_cells.jsonl.gz', 'rt') as stream:
        for line in stream:
            r = json.loads(line)
            prior = json.loads(next(old))
            key = r['parent_id'], r['row_id']
            assert key not in ids
            ids.add(key)
            for k in ('row_id', 'parent_id', 'crop_sha256', 'pipeline_disposition'):
                assert r[k] == prior[k], (r['row_id'], k)
            assert r['verdict_05'] == prior['segmentation']['verdict']
            assert r['reason_05'] == prior['segmentation']['reason']
            assert r['segmentation_version'] == prior['segmentation']['tool_version'] == '0.5'
            assert hashlib.sha256(r['raw_text'].encode()).hexdigest() == r['raw_text_sha256']
            assert r['is_cell'] == (r['is_numeric_output'] and r['is_small_image'])
            counts['all'] += 1
            if r['is_numeric_output']:
                counts['numeric'] += 1
                numeric_ids.add(r['row_id'])
            if r['is_cell']:
                counts['cells'] += 1
            if r['is_numeric_output'] and not r['is_small_image']:
                counts['numeric_not_small'] += 1
            if r['is_small_image'] and not r['is_numeric_output']:
                counts['small_not_numeric'] += 1
            verdicts[r['verdict_05']] += 1
            dispositions[r['pipeline_disposition']] += 1
    old_receipt = json.loads(next(old))['_receipt']
    assert old_receipt['export_sha256'] == receipt['export_receipt']['export_sha256']
    assert not old.read()
    old.close()
    assert counts == summary['total'] and counts['all'] == 592466
    assert verdicts == summary['segmentation_verdicts']['all']
    assert dispositions == summary['pipeline_dispositions']['all']
    for axis, groups in summary['by'].items():
        for group, n in counts.items():
            assert sum(v.get(group, 0) for v in groups.values()) == n, (axis, group)
    distributions = json.loads((D / 'distributions.json').read_text())
    q = distributions['quantiles']['numeric']
    assert q['width_px']['0.95'] == 169 and q['height_px']['0.75'] == 35 and q['characters']['0.9'] == 10
    assert next(x['numeric_rows'] for x in distributions['candidate_cuts'] if (x['width'], x['height'], x['chars']) == (200, 40, 10)) == counts['cells']
    samples = [json.loads(line) for line in (D / 'samples.jsonl').read_text().splitlines()]
    sample_receipt = json.loads((D / 'sample_receipt.json').read_text())
    assert len(samples) == sample_receipt['fetched']
    assert len({r['row_id'] for r in samples}) == len(samples)
    assert len(list((D / 'samples').glob('*.png'))) == len(samples)
    for r in samples:
        p = D / r['crop_path']
        assert sha(p) == r['sha256']
        with Image.open(p) as im:
            assert im.size == (r['w'], r['h'])
            im.verify()
    failures = [json.loads(line) for line in (D / 'sample_failures.jsonl').read_text().splitlines()]
    if len(samples) < 250:
        unavailable_numeric = {r['row_id'] for r in failures if r['group'] in ('cells', 'numeric_not_small')}
        assert unavailable_numeric == numeric_ids and len(unavailable_numeric) == 54440
        assert Counter(r['sample_group'] for r in samples) == {'small_not_numeric': 50}
    for name, expected in initial['protected'].items():
        assert sha(ROOT / name) == expected, name
    policies = ('greekocr/harvest/filtering_assets/segmentation-policy.js',
                'greekocr/harvest/filtering_assets/crop-tools.py',
                'greekocr/harvest/line_pipeline_native.py',
                'docs/harvest/line_pipeline/tool_versions.json',
                'scripts/harvest/build_filter_versions.py')
    for name in policies:
        assert (ROOT / name).read_bytes() == git('show', initial['base'] + ':' + name), name
    assert git('rev-parse', 'HEAD').decode().strip() == initial['head']
    assert git('for-each-ref', '--format=%(refname) %(objectname)').decode().strip() == initial['refs']
    index = Path(git('rev-parse', '--path-format=absolute', '--git-path', 'index').decode().strip())
    assert sha(index) == initial['index_sha256']
    assert hashlib.sha256(git('diff', '--binary')).hexdigest() == initial['diff_sha256']
    result = dict(status='PASS_CLASSIFIER_CENSUS_SCOPE; SAMPLE_DELIVERY_BLOCKED' if len(samples) < 250 else 'PASS',
                  rows_verified=592466, unchanged_segmentation_verdicts_and_reasons=592466,
                  unchanged_pipeline_dispositions=592466, axes_reconciled=list(summary['by']),
                  numeric_output_rows=counts['numeric'], cells=counts['cells'],
                  fetched_crop_hashes_and_physical_dimensions_verified=len(samples),
                  missing_numeric_crop_paths=54440 if len(samples) < 250 else None,
                  protected_five_files_unchanged=True, shared_refs_and_index_unchanged=True,
                  policy_versions_and_native_segmenter_equal_to_base=True,
                  classifier_not_integrated_into_pipeline=True)
    (D / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
