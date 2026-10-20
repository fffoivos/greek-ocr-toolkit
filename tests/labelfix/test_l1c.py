"""L1C exact-reason semantics, output DAG integrity and durable partials (CPU)."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.labelfix.clariden import l1c_census as c


def event(reason, start=0, letter='α'):
    # Deliberately wrong broad alias: only detail is authoritative.
    return dict(start=start, letter=letter, reason='localisation_unknown', detail=reason)


def row(events, status='hold', lid='a'):
    return dict(line_id=lid, status=status, hold_slots=events,
                original_label_sha256=hashlib.sha256('α'.encode()).hexdigest())


def write_rows(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(path, 'wt', encoding='utf-8') as f:
        for record in records:
            f.write(c.canonical(record) + '\n')


def fixture(tmp_path):
    """Two authentic-shaped shards, all three modes, two waves/two sources."""
    root = tmp_path / 'l1r'
    root.mkdir()
    policy = dict(schema='sf4-release-v1', sources={'greekocr/labelfix/release_gate.py': c.GATE_SHA256})
    policy['sha256'] = hashlib.sha256(json.dumps(policy['sources'], sort_keys=True).encode()).hexdigest()
    audit = dict(complete=True, lines=4, shards=2, inputs={'upstream': 'bound-but-never-opened'})
    audit['inputs_sha256'] = c.digest(audit['inputs'])
    c.atomic_json(root / 'input_verification.json', audit)
    ivsha = c.sha256(root / 'input_verification.json')
    binding = dict(policy_binding=policy, policy_sha256=policy['sha256'],
                   input_verification_sha256=ivsha, input_hashes_sha256=audit['inputs_sha256'])
    overlays = [row([event('detector_clipped_top'), event('detector_clipped_top'),
                     event('detector_clipped_top', 1)]),
                row([event('edit_guard:punctuation_mismatch', letter='')], lid='b'),
                row([event('K1:observation:clipped_bottom'), event('mark_kind_disagreement', 1)], lid='c'),
                row([], 'out_of_scope', 'd')]
    selected = [dict(id=r['line_id'], label='α', wave='round1' if i < 2 else 'round2',
                     source='s1' if i % 2 == 0 else 's2') for i, r in enumerate(overlays)]

    def release(parent, records, selections):
        for mode in c.MODES:
            v = mode.lower()
            write_rows(parent / f'overlay_{v}.jsonl.gz', records)
            write_rows(parent / f'ctrl_subset_{v}.jsonl.gz', [])
            (parent / f'kept_{v}_line_ids.txt').write_text('')
            coverage = {}
            for dim in ('wave', 'source'):
                buckets = {}
                for s, r in zip(selections, records):
                    buckets.setdefault(s[dim], Counter({k: 0 for k in c.STATUSES}))[r['status']] += 1
                coverage['coverage_per_' + dim] = {k: dict(b, total=sum(b.values())) for k, b in buckets.items()}
            m = dict(release_policy='sf4-release-v1', variant=v, policy_sha=policy['sha256'],
                     input_verification_sha256=ivsha, overlay=f'overlay_{v}.jsonl.gz',
                     overlay_sha256=c.sha256(parent / f'overlay_{v}.jsonl.gz'),
                     kept_line_ids=f'kept_{v}_line_ids.txt',
                     kept_line_ids_sha256=c.sha256(parent / f'kept_{v}_line_ids.txt'),
                     counts_by_status=dict(Counter(r['status'] for r in records)), **coverage)
            c.atomic_json(parent / f'release_{v}.json', m)
            c.atomic_json(parent / f'release_ctrl_subset_{v}.json', dict(m,
                          labels_file=f'ctrl_subset_{v}.jsonl.gz', labels_sha256=c.sha256(parent / f'ctrl_subset_{v}.jsonl.gz')))

    entries = []
    for n in range(2):
        shard = root / 'shards' / f'shard-{n:05d}'
        records, selections = overlays[n*2:n*2+2], selected[n*2:n*2+2]
        write_rows(shard / 'selection.jsonl', selections)
        release(shard / 'release', records, selections)
        c.atomic_json(shard / 'receipt.json', dict(schema='l1r-recomposition-shard-v1', complete=True,
                      shard=n, lines=2, inputs=dict(binding=binding), validation=dict(complete=True),
                      outputs={str(p.relative_to(shard)): c.sha256(p) for p in shard.rglob('*') if p.is_file()}))
        entries.append(dict(shard=n, receipt=str((shard / 'receipt.json').relative_to(root)), receipt_sha256=c.sha256(shard / 'receipt.json')))
    release(root / 'release', overlays, selected)
    c.atomic_json(root / 'receipt.json', dict(schema='l1r-recomposition-v2', complete=True,
                  validation=dict(complete=True, lines=4), policy=policy, binding=binding,
                  inputs_sha256=audit['inputs_sha256'], input_verification_sha256=ivsha,
                  counts={m.lower(): dict(Counter(r['status'] for r in overlays)) for m in c.MODES},
                  shards=entries, outputs={str(p.relative_to(root)): c.sha256(p) for p in (root / 'release').iterdir()}))
    return root


def test_exact_reason_slot_dedup_and_alone_are_line_based():
    b = c.empty_bucket()
    c.add(b, c.observation(row([event('detector_clipped_top'), event('detector_clipped_top'),
                               event('detector_clipped_top', 1)])))
    assert b['slots_per_exact_reason'] == {'detector_clipped_top': 2}
    assert b['hold_entries_per_exact_reason'] == {'detector_clipped_top': 3}
    assert b['lines_reason_alone'] == {'detector_clipped_top': 1}
    assert b['lines_per_reason_family'] == {'clipping': 1}
    c.add(b, c.observation(row([event('detector_clipped_top'), event('K1:flag', 1)])))
    assert b['lines_reason_alone']['detector_clipped_top'] == 1
    assert b['held_slots'] == 4


def test_blank_letter_guard_never_becomes_a_glyph_slot():
    b = c.empty_bucket()
    c.add(b, c.observation(row([event('edit_guard:punctuation_mismatch', letter='')] * 2)))
    assert not b['slots_per_exact_reason'] and b['held_slots'] == 0
    assert b['line_guards_per_exact_reason'] == {'edit_guard:punctuation_mismatch': 1}
    assert b['lines_reason_alone'] == {'edit_guard:punctuation_mismatch': 1}


@pytest.mark.parametrize('reason,expected', [
    ('detector_segmentation_uncertain', {'localisation/segmentation'}),
    ('detector_physical_mapping_ambiguous', {'localisation/segmentation'}),
    ('crop_UNSEEN:left', {'clipping'}), ('K1:flag', {'K1'}),
    ('K1:observation:clipped_top', {'K1', 'clipping'}),
    ('edit_guard:unsupported_character:7', {'edit-guard'}),
    ('ensemble_ab_mark_set_disagreement', {'A/B disagreement'}),
    ('mark_set_disagreement', {'kind disagreement'}),
    ('mark_kind_disagreement', {'kind disagreement'}),
    ('r1_B_uncertainty:unknown', {'R1 uncertainty'}),
    ('new_reason', {'other/unclassified'})])
def test_family_taxonomy_keeps_unknown_reasons(reason, expected):
    assert c.reason_families(reason) == expected


@pytest.mark.parametrize('bad', [row([], 'hold'), row([event('x')], 'corrected'),
                                 row([dict(start=0, letter='α', reason='alias')])])
def test_invalid_status_or_exact_reason_fails(bad):
    with pytest.raises(ValueError):
        c.observation(bad)


def test_exact_entrypoint_multiprocess_counts_and_receipts(tmp_path):
    root = fixture(tmp_path)
    out = tmp_path / 'census'
    subprocess.run([sys.executable, '-B', str(Path(c.__file__).resolve()), '--input-dir', str(root),
                    '--out', str(out), '--workers', '2'], check=True, capture_output=True, text=True)
    result = c.load(out / 'CENSUS.json')['modes']
    for mode in c.MODES:
        overall = result[mode]['overall']
        assert overall['total_lines'] == 4 and overall['status']['hold'] == 3
        assert overall['slots_per_exact_reason']['detector_clipped_top'] == 2
        assert overall['lines_reason_alone'] == {'detector_clipped_top': 1, 'edit_guard:punctuation_mismatch': 1}
        assert overall['lines_per_reason_family']['clipping'] == 2
        assert result[mode]['per_wave']['round2']['status']['out_of_scope'] == 1
        assert result[mode]['per_wave']['openarchives']['total_lines'] == 0
        assert result[mode]['per_wave_source']['round1']['s2']['held_slots'] == 0
        assert result[mode]['per_source']['s1']['status']['hold'] == 2
    receipt = c.load(out / 'receipt.json')
    assert receipt['analysis_only'] and receipt['complete'] and receipt['shards'] == 2
    for p, h in receipt['outputs'].items():
        assert c.sha256(out / p) == h
    before = {p: p.read_bytes() for p in (out / 'partials').rglob('*') if p.is_file()}
    (out / 'receipt.json').unlink()  # simulate interrupted final aggregation
    c.census(root, out, workers=2)
    assert all(p.read_bytes() == content for p, content in before.items())
    (out / 'partials/shard-00000/counts.json').write_text('{}')
    with pytest.raises(ValueError, match='partial counts changed'):
        c.census(root, out, workers=2)


@pytest.mark.parametrize('file', ['release/overlay_full.jsonl.gz', 'shards/shard-00000/selection.jsonl',
                                  'shards/shard-00001/release/overlay_ensemble_ab.jsonl.gz',
                                  'shards/shard-00000/receipt.json', 'input_verification.json'])
def test_tampered_input_fails_before_any_census_output(tmp_path, file):
    root = fixture(tmp_path)
    with (root / file).open('ab') as f:
        f.write(b'changed')
    with pytest.raises((ValueError, json.JSONDecodeError)):
        c.census(root, tmp_path / 'out')
    assert not (tmp_path / 'out').exists()


@pytest.mark.parametrize('case', ['incomplete', 'duplicate-shard', 'escape', 'gate'])
def test_invalid_receipt_dag_fails_closed(tmp_path, case):
    root = fixture(tmp_path)
    r = c.load(root / 'receipt.json')
    if case == 'incomplete':
        r['complete'] = False
    elif case == 'duplicate-shard':
        r['shards'].append(r['shards'][0])
    elif case == 'escape':
        r['outputs']['../outside'] = 'bad'
    else:
        r['policy']['sources']['greekocr/labelfix/release_gate.py'] = 'bad'
    c.atomic_json(root / 'receipt.json', r)
    with pytest.raises(ValueError):
        c.census(root, tmp_path / 'out')
    assert not (tmp_path / 'out').exists()


def test_job_id_resolution_is_unambiguous_and_separate_output(tmp_path):
    a = tmp_path / 'l1r_sf4/output_123'
    b = tmp_path / 'l1e_20261017/l1r_sf4_123'
    a.mkdir(parents=True)
    assert c.resolve_input('123', tmp_path) == a
    b.mkdir(parents=True)
    with pytest.raises(ValueError, match='exactly one'):
        c.resolve_input('123', tmp_path)
    for jobid in ('0', 'a', '../123'):
        with pytest.raises(ValueError):
            c.resolve_input(jobid, tmp_path)
    root = fixture(tmp_path)
    for out in (root, root / 'census', tmp_path):
        with pytest.raises(ValueError, match='disjoint'):
            c.census(root, out)


def test_partial_sets_are_not_truncated_to_top10():
    b = c.empty_bucket()
    for i in range(15):
        c.add(b, c.observation(row([event(f'exact:{i}')])))
    assert len(b['exact_reason_sets']) == 15


def test_global_top10_keeps_reason_set_below_each_shard_top10(tmp_path):
    root = fixture(tmp_path)
    out = tmp_path / 'merged'
    c.atomic_json(out / 'input_verification.json', dict(input_directory=str(root)))
    results = []
    for shard in range(2):
        groups = {}
        for mode in c.MODES:
            b = c.empty_bucket()
            for i in range(10):
                for _ in range(4):
                    c.add(b, c.observation(row([event(f'unique-{shard}-{i}')])) )
            for _ in range(3):
                c.add(b, c.observation(row([event('shared')])) )
            for w, s in (('*', '*'), ('round1', '*'), ('*', 's1'), ('round1', 's1')):
                groups[c.group_key(mode, w, s)] = b
        c.atomic_json(out / f'partials/shard-{shard:05d}/counts.json', groups)
        results.append(dict(input=dict(shard=shard)))
    # Set the read-only release coverage oracle to the synthetic ranking population.
    for mode in c.MODES:
        path = root / f'release/release_{mode.lower()}.json'
        m = c.load(path)
        m['coverage_per_wave'] = {'round1': dict.fromkeys(c.STATUSES, 0) | dict(hold=86, total=86)}
        m['coverage_per_source'] = {'s1': dict.fromkeys(c.STATUSES, 0) | dict(hold=86, total=86)}
        c.atomic_json(path, m)
    result = c.merge(results, out, dict(counts={m.lower(): dict(hold=86) for m in c.MODES}))
    for mode in c.MODES:
        b = result[mode]['overall']
        assert b['top10_exact_reason_sets'][0] == dict(reasons=['shared'], lines=6)
        assert len(b['top10_exact_reason_sets']) == 10
        assert b['distinct_exact_reason_sets'] == 21


def test_no_gate_reader_or_detector_imports():
    import ast
    tree = ast.parse(Path(c.__file__).read_text())
    imports = [node.module or '' for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert not any(m.startswith(('greekocr', 'scripts.'))
                   for m in imports if m != 'greekocr.ops.data_root')
    helper = Path(__file__).resolve().parents[2] / 'greekocr/ops/data_root.py'
    helper_tree = ast.parse(helper.read_text())
    modules = [n.module or '' for n in ast.walk(helper_tree) if isinstance(n, ast.ImportFrom)]
    modules += [a.name for n in ast.walk(helper_tree) if isinstance(n, ast.Import) for a in n.names]
    assert all(m.split('.')[0] in sys.stdlib_module_names for m in modules)
    code = ('import importlib.util,sys; '
            's=importlib.util.spec_from_file_location("standalone_data_root",sys.argv[1]); '
            'm=importlib.util.module_from_spec(s); s.loader.exec_module(m); '
            'assert not any(n == "greekocr" or n.startswith("greekocr.") for n in sys.modules)')
    subprocess.run([sys.executable, '-I', '-B', '-c', code, str(helper)], check=True)
