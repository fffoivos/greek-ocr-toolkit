"""ADM2: append the recorded T6g pool; preserve the preregistered bytes.

Local standard-library file reads only. Writes are confined to this directory.
The original builder has top-level writes, so its selection/hash/row construction
is reused below without importing or running it.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE_HEAD = '84ef9f428f82f8e5cba66a986bcdb59c798e0783'
BASE_SHA = 'e16f824c3349f6fa20c4e693964d020096306ebab210c8799020f63b0bdf2b5d'
BASE_ROWS = 16562
WAVE_ARM = 'wave-1d only'  # Existing literal; changing it violates byte preservation.
ARM = 'release-v3-candidate'
PARAMS_SHA = '801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8'
W = Path.home() / 'Projects/greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked'
RUN = Path.home() / 'Projects/collect-v3-data/run'
EXCLUSIONS = ROOT / 'docs/harvest/collect_v3/release_exclusions'
ADMISSIONS = HERE / 'w1_masked_1d.jsonl'
SUMMARY = HERE / 'w1_masked_1d_summary.json'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def git_bytes(revision, path, root=ROOT):
    return subprocess.run(['git', 'show', revision + ':' + path], cwd=root,
                          check=True, capture_output=True).stdout


def baseline():
    data = git_bytes(BASE_HEAD, str(ADMISSIONS.relative_to(ROOT)))
    require(digest(data) == BASE_SHA and data.endswith(b'\n'), 'baseline hash/newline mismatch')
    rows = [json.loads(line) for line in data.splitlines()]
    require(len(rows) == BASE_ROWS and all(r['arm'] == WAVE_ARM for r in rows),
            'unexpected baseline rows/arm')
    return data, rows


def input_paths():
    paths = {
        'original_builder': HERE / 'build_w1_masked_1d.py',
        'w1_features': RUN / 'W1/features.jsonl',
        'crop_tight_page': RUN / 'W1/crop_tight_page.jsonl',
        'kosmopolis_t6b_records': W / 'kosmopolis/records.jsonl',
        't6b_check_results': W / 'checks/t6b_results.json',
        'release_exclusions': EXCLUSIONS / 'release_exclusions.json',
        'rotated_ids': EXCLUSIONS / 'w1_rotated_crop_ids.txt',
        't6g_key': W / 'cards_kosmo_poly1850_key.json',
        'previous_t6b_key': W / 'cards/kosmopolis_key.json',
        't6g_receipt': W / 't6g/receipt.json',
        't6g_pack': W / 't6g/pack.py',
        't6g_cards': W / 'cards_kosmo_poly1850/reader/cards.jsonl',
        'label_check_protocol': W / 'cards/LABEL_CHECK_v2.md',
        'srk2_results': W / 'checks/kosmo_poly1850_sol/results.json',
    }
    exclusions = json.loads(paths['release_exclusions'].read_text())
    for name, spec in exclusions['classes'].items():
        paths['exclusion_ids:' + name] = EXCLUSIONS / spec['file']
    return paths


def bindings():
    return {name: {'path': str(path), 'sha256': sha(path)}
            for name, path in sorted(input_paths().items())}


def make_row(r, x):
    """Same crop hash checks and fields as build_w1_masked_1d.py, plus ADM2 tags."""
    rid = r['id']
    kind = x['output_kind']
    require(kind in ('masked', 'guarded_original'), 'unsupported output kind: ' + rid)
    crop = W / x['masked_crop']
    csha = sha(crop)
    want = x['masked_crop_sha256'] if kind == 'masked' else x['original_crop_sha256']
    require(csha == want, 'T6b crop hash mismatch: ' + rid)
    require(x['original_crop_sha256'] == r['crop_sha256'], 'collector crop hash mismatch: ' + rid)
    return dict(row_id=rid, source=r['source'], primary_class=r['primary_class'],
                gazette_stratum=None, page_id=r['page_id'], line_index=int(rid.rsplit('-l', 1)[1]),
                tranche='W1', label=r['label'], crop=str(crop), crop_sha256=csha,
                original_crop_sha256=x['original_crop_sha256'],
                guard_status='masked' if kind == 'masked' else 'guarded_original',
                wrong_line_risk=bool(x.get('wrong_line_risk')),
                crop_masked_tag='crop_masked' if kind == 'masked' else None,
                arm=ARM, marks_status='pending_opus',
                provenance=dict(t6b_commit='sol/recut-v1 63c640a3',
                                t6b_checks_commit='sol/recut-v1 7f70de90',
                                params_sha256=x.get('params_sha256', PARAMS_SHA),
                                sol_reading='sol/recut-v1 87db4392'))


def candidates():
    before = bindings()
    key = json.loads((W / 'cards_kosmo_poly1850_key.json').read_text())
    receipt = json.loads((W / 't6g/receipt.json').read_text())
    srk2 = json.loads((W / 'checks/kosmo_poly1850_sol/results.json').read_text())
    for spec in key['_inputs'].values():
        require(sha(spec['path']) == spec['sha256'], 'T6g input drift: ' + spec['path'])
    require(receipt['key_sha256'] == before['t6g_key']['sha256'], 'T6g receipt/key mismatch')
    require(srk2['inputs'][str(W / 'cards_kosmo_poly1850_key.json')] == before['t6g_key']['sha256'],
            'SRK2/T6g key mismatch')
    require(srk2['n'] == 100 and srk2['totals']['letters']['y'] == 96
            and srk2['totals']['crop_ok']['y'] == 99 and srk2['totals']['marks']['y'] == 90,
            'unexpected SRK2 results')
    require(srk2['ruling'] == dict(letters='final', crop_ok='final', marks='pending_opus'),
            'unexpected SRK2 ruling')
    for revision, name in [('72ae7114', 'cards_kosmo_poly1850_key.json'),
                           ('87db4392', 'checks/kosmo_poly1850_sol/results.json')]:
        require(git_bytes(revision, 'docs/harvest/recut_v1/w1_masked/' + name, W.parents[3])
                == (W / name).read_bytes(), 'evidence commit/file mismatch: ' + name)

    records = {}
    with (W / 'kosmopolis/records.jsonl').open() as stream:
        for line in stream:
            x = json.loads(line)
            require(x['id'] not in records, 'duplicate T6b id: ' + x['id'])
            records[x['id']] = x
    rows = {}
    with (RUN / 'W1/crop_tight_page.jsonl').open() as stream:
        for line in stream:
            r = json.loads(line)
            if (r['source'], r['primary_class']) == ('kosmopolis', 'poly1850'):
                require(r['id'] not in rows, 'duplicate W1 id: ' + r['id'])
                rows[r['id']] = r
    rotated = set((EXCLUSIONS / 'w1_rotated_crop_ids.txt').read_text().split())
    line_excluded = set()
    for name, spec in before.items():
        if name.startswith('exclusion_ids:'):
            line_excluded.update(Path(spec['path']).read_text().split())
    old_key = json.loads((W / 'cards/kosmopolis_key.json').read_text())
    previous = {v['line_id'] for v in old_key.values() if isinstance(v, dict) and 'line_id' in v}
    pool = key['_pool_line_ids']
    require(len(pool) == len(set(pool)) == key['_pool'] == receipt['counts']['pool'] == 462,
            'unexpected T6g pool')
    counts = Counter(class_rows=len(rows))
    dropped = defaultdict(list)
    out = []
    for rid, r in sorted(rows.items()):
        x = records.get(rid)
        if r.get('screen_merged') or (x and x.get('screen_merged')):
            reason = 'screen_merged'
        elif rid in rotated:
            reason = 'rotated_crop'
        elif rid in line_excluded:
            reason = 'release_exclusions_line_class'
        elif x is None:
            reason = 'not_in_t6b_eligible (caps/heading or earlier exclusion)'
        elif x.get('output_kind') not in ('masked', 'guarded_original'):
            reason = 'output_kind:' + str(x.get('output_kind'))
        elif not (W / x['masked_crop']).exists():
            reason = 'crop_file_missing'
        else:
            counts['builder_eligible'] += 1
            if rid in previous:
                reason = 'previous_t6b_card (outside recorded T6g pool)'
            else:
                out.append(make_row(r, x))
                counts['admitted'] += 1
                continue
        counts[reason] += 1
        dropped[reason].append(rid)
    require([r['row_id'] for r in out] == pool, 'candidate IDs differ from recorded T6g pool')
    require(bindings() == before, 'inputs changed during validation')
    return out, dict(counts), dict(dropped), before


def encode(rows):
    return ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows).encode('utf-8')


def expected_summary(base, rows, counts, dropped, inputs):
    summary = json.loads(git_bytes(BASE_HEAD, str(SUMMARY.relative_to(ROOT))))
    all_rows = [json.loads(line) for line in base.splitlines()] + rows
    by_arm = Counter(r['arm'] for r in all_rows)
    summary.update(
        rows=len(all_rows), sha256=digest(base + encode(rows)),
        status='wave-1d bytes preserved; kosmopolis/poly1850 is a separate release-v3 candidate; marks pending Opus',
        wave1d_subset_sha256=digest(base), wave1d_subset_before_sha256=BASE_SHA,
        wave1d_subset_bytes_unchanged=True, wave1d_subset_rows=BASE_ROWS,
        wave1d_subset_arm_values=[WAVE_ARM],
        arm_contract_note='The existing literal arm is "wave-1d only", not "wave-1d". '
                          'It is preserved byte-for-byte. Exact arm == "wave-1d" matches zero rows; '
                          'the preserved legacy-arm selector matches 16562. No consumer was changed.',
        arm_filter_counts={arm: by_arm[arm] for arm in ('wave-1d', WAVE_ARM, ARM)},
        counts_per_arm_source_class=[dict(arm=a, source=s, primary_class=c, rows=n)
            for (a, s, c), n in sorted(Counter((r['arm'], r['source'], r['primary_class'])
                                               for r in all_rows).items())],
        bound_inputs=inputs, srk2_results_sha256=inputs['srk2_results']['sha256'],
        adm2=dict(arm=ARM, source='kosmopolis', primary_class='poly1850', rows=len(rows),
                  marks_status='pending_opus', cards='sol/recut-v1 72ae7114',
                  sol_reading='sol/recut-v1 87db4392', expected_t6g_pool=462,
                  difference_from_t6g_pool=len(rows) - 462,
                  selection_counts=counts, excluded_row_ids=dropped,
                  pool_rule='Exact recorded T6g pool: builder-eligible 473 minus 11 previous T6b cards.',
                  guard_status_counts=dict(Counter(r['guard_status'] for r in rows)),
                  letters=dict(y=96, n=100, status='final'),
                  crop_ok=dict(y=99, n=100, status='final'),
                  marks=dict(y=90, n=100, status='pending_opus')))
    # Preserve the historical wave-1d counts/admitted_strata above; new admissions
    # are separately identified by arm and cannot be mistaken for a 1d extension.
    return summary


def verify():
    base, _ = baseline()
    rows, counts, dropped, inputs = candidates()
    expected = base + encode(rows)
    data = ADMISSIONS.read_bytes()
    require(data == expected, 'admission bytes differ from frozen prefix plus exact candidate rows')
    parsed = [json.loads(line) for line in data.splitlines(keepends=True)]
    subset = b''.join(line for line in data.splitlines(keepends=True)
                      if json.loads(line)['arm'] == WAVE_ARM)
    require(subset == base and digest(subset) == BASE_SHA, 'wave-1d subset changed')
    require(len({r['row_id'] for r in parsed}) == len(parsed), 'duplicate admission row id')
    require(json.loads(SUMMARY.read_text()) == expected_summary(base, rows, counts, dropped, inputs),
            'summary differs from verified evidence')
    return dict(wave1d_rows=BASE_ROWS, candidate_rows=len(rows),
                wave1d_subset_sha256=digest(subset), sha256=digest(data),
                literal_wave1d_filter_rows=sum(r['arm'] == 'wave-1d' for r in parsed))


def append():
    base, _ = baseline()
    rows, counts, dropped, inputs = candidates()
    current = ADMISSIONS.read_bytes()
    expected = base + encode(rows)
    require(current in (base, expected), 'refusing to overwrite unexpected admission bytes')
    summary = expected_summary(base, rows, counts, dropped, inputs)
    if current == base:
        with ADMISSIONS.open('ab') as stream:
            stream.write(encode(rows))
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=1) + '\n')
    return verify()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    print(json.dumps(verify() if args.check_only else append(), indent=2))
