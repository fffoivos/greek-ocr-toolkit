"""Release-v3 custody helpers for the existing wave-2 driver.

Population scans and crop reads are compute-job work. Binding a sealed suite
uses a previously prepared, hash-bound training inventory; it never guesses
training membership from a release receipt.
"""
from __future__ import annotations
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import re

from bench.common import read_rows, write_rows
from bench.e1_common import atomic_json, read_json, sha256

HEX = re.compile(r'^[0-9a-f]{64}$')
ARMS = ('ctrl', 'add', 'add_corr')


def refuse_locked(cfg):
    if 'locked' in cfg:
        raise ValueError('LOCKED_STRATA_REMOVED: coordinator amendment 20 Oct; remove the locked key')


def split2_ledgers(cfg):
    """Check edition-level and row-level ledgers; include every forced holdout."""
    editions = {}
    for row in read_rows(bound(cfg['editions'])):
        ident = row['edition_id']
        if ident in editions or row['split'] not in ('train', 'dev', 'test'):
            raise ValueError('INVALID_SPLIT2_EDITION_MAP')
        editions[ident] = row
    mapping = {}
    with gzip.open(bound(cfg['split2']), 'rt', encoding='utf-8') as f:
        for row in map(json.loads, f):
            ident = row['row_id']; edition = row['edition_id']
            if ident in mapping or edition not in editions or row['split'] != editions[edition]['split']:
                raise ValueError('SPLIT2_ROW_EDITION_MISMATCH')
            mapping[ident] = edition
    heldout = {e for e,r in editions.items() if r['split'] in ('dev','test')}
    forced = {e for e,r in editions.items() if r.get('forced')}
    if not heldout or not forced <= heldout:
        raise ValueError('SPLIT2_FORCED_HOLDOUT_MISMATCH')
    if set(read_json(bound(cfg['heldout_editions']))['edition_ids']) != heldout:
        raise ValueError('SPLIT2_HELDOUT_LEDGER_MISMATCH')
    receipt = read_json(bound(cfg['split2_receipt']))
    counts = receipt['counts']
    if counts['editions'] != len(editions) or len(counts['forced_edition_details']) != len(forced):
        raise ValueError('SPLIT2_RECEIPT_COUNT_MISMATCH')
    if {r['edition_id'] for r in counts['forced_edition_details']} != forced:
        raise ValueError('SPLIT2_RECEIPT_FORCED_MISMATCH')
    return mapping, heldout


def inventory_summary(old, oldmix, added, components, overlay, out, *, rows=None, epochs=8):
    """Count actual canonical sampler output; model seeds share the data seed."""
    from bench.e4_wave1b import ROWS
    from train.mix import assemble
    rows = ROWS if rows is None else rows
    per_version = {}
    for version, unmatched in overlay['unmatched'].items():
        c = Counter()
        for item in overlay['counts']:
            if item['version'] == version:
                c[item['outcome']] += item['rows']
        per_version[version] = dict(accepted=c['substituted']+c['unchanged'],
            rejected=c['codec_rejected'], unmatched=len(unmatched), substituted=c['substituted'],
            unchanged=c['unchanged'])
    result = dict(schema='e4-wave2-inventory-summary-v1', arms={},
        data_seed=oldmix['seed'], model_seeds=[0,1,2],
        label_sources=dict(ctrl='factory', add='factory + raw release-v3 import',
            add_corr='add + RU1/N1 exact-ID edits'), versions=per_version)
    for arm in ARMS:
        groups, mix = (old,oldmix) if arm == 'ctrl' else (added,dict(components=components,seed=oldmix['seed']))
        unique = {r['line_id'] for g,c in zip(groups,mix['components']) if c['kind']=='real' for r in g}
        per_epoch = {}; total = Counter(); support = set()
        for epoch in range(1,epochs+1):
            drawn, _ = assemble(groups,[c['fraction'] for c in mix['components']],mix['seed'],epoch,rows,
                exact_rows=True,recovery=mix.get('codec_recovery'),replay=mix.get('matched_replay'))
            real = [r for r in drawn if mix['components'][r['_component']]['kind']=='real']
            ids = {r['line_id'] for r in real}; support.update(ids)
            per_epoch[str(epoch)] = dict(unique_real_rows=len(ids),real_draws=len(real),synthetic_draws=len(drawn)-len(real))
            total.update(real_draws=len(real),synthetic_draws=len(drawn)-len(real))
        summary = dict(unique_real_rows=len(unique),unique_real_rows_drawn=len(support),
            epochs=per_epoch,total=dict(total))
        result['arms'][arm] = {str(seed):summary for seed in range(3)}
    result['candidate_crop_exposure'] = read_json(Path(out)/'EXPOSURE_CANDIDATES.json')['arms']
    atomic_json(Path(out)/'INVENTORY_SUMMARY.json',result)
    text = '| Arm | Model seed | Unique real pool | Unique real drawn | Real draws total | Synthetic draws total | Label source |\n|---|---:|---:|---:|---:|---:|---|\n'
    for arm, seeds in result['arms'].items():
        for seed,v in seeds.items():
            text += f"| {arm} | {seed} | {v['unique_real_rows']} | {v['unique_real_rows_drawn']} | {v['total']['real_draws']} | {v['total']['synthetic_draws']} | {result['label_sources'][arm]} |\n"
    text += '\nPer-epoch counts, per-version accepted/rejected/unmatched edits and all-arm original/factory candidate crop exposure:\n\n```json\n'+json.dumps(result,indent=2)+'\n```\n'
    (Path(out)/'INVENTORY_SUMMARY.md').write_text(text)
    return result


def bound(spec):
    if not isinstance(spec, dict) or not isinstance(spec.get('path'), str) or not spec['path']:
        raise ValueError('INPUT_PATH_UNBOUND')
    p = Path(spec['path']).resolve()
    if not HEX.fullmatch(spec.get('sha256') or '') or sha256(p) != spec['sha256']:
        raise ValueError('INPUT_SHA_MISMATCH: ' + str(p))
    return p


def key(row):
    return row['parent_id'], row.get('row_id', row.get('line_id', row.get('id')))


def exposure(train, benchmark, heldout_editions=(), protected_crops=()):
    """Count train observations hit by each independent exposure check.

    Call for all real and corrector-derived rows. Missing identity is fatal;
    an empty held-out set is a caller error, never evidence of zero exposure.
    """
    editions, keys, crops = set(), set(), set()
    for row in benchmark:
        if not row.get('edition_id') or not row.get('crop_sha256') or not all(key(row)):
            raise ValueError('INCOMPLETE_BENCHMARK_IDENTITY')
        editions.add(row['edition_id']); keys.add(key(row)); crops.add(row['crop_sha256'])
    if not keys:
        raise ValueError('EMPTY_BENCHMARK')
    counts = Counter({k: 0 for k in ('benchmark_edition', 'benchmark_row_key', 'benchmark_crop_sha256',
                                     'split2_dev_test_edition', 'census05_protected_crop')})
    heldout_editions, protected_crops = set(heldout_editions), set(protected_crops)
    n = 0
    for row in train:
        if not row.get('edition_id') or not HEX.fullmatch(row.get('crop_sha256') or '') or not all(key(row)):
            raise ValueError('INCOMPLETE_TRAIN_IDENTITY')
        n += 1
        counts['benchmark_edition'] += row['edition_id'] in editions
        counts['benchmark_row_key'] += key(row) in keys
        counts['benchmark_crop_sha256'] += bool({row['crop_sha256'], row.get('factory_crop_sha256')} & crops)
        counts['split2_dev_test_edition'] += row['edition_id'] in heldout_editions
        counts['census05_protected_crop'] += bool({row['crop_sha256'], row.get('factory_crop_sha256')} & protected_crops)
    return dict(rows=n, checks=dict(counts), hits=sum(counts.values()))


def sealed_rows(suite_spec):
    suite_path = bound(suite_spec); suite = read_json(suite_path)
    if suite.get('schema') != 'ocr-benchmark-suite-v1' or suite.get('version') != '0.2' or suite.get('mock') is not False:
        raise ValueError('BENCHMARK_0_2_NOT_SEALED')
    if set(suite.get('panels', {})) != {'benchmark_v02_test', 'benchmark_v02_dev'}:
        raise ValueError('BENCHMARK_0_2_PANEL_SET')
    result, files = [], [dict(path=str(suite_path), sha256=sha256(suite_path))]
    for name, panel in suite['panels'].items():
        p = (suite_path.parent / panel['path']).resolve()
        if not p.is_relative_to(suite_path.parent) or panel.get('scorable') is not True:
            raise ValueError('BENCHMARK_0_2_UNSCORABLE_PANEL')
        bound(dict(path=str(p), sha256=panel['sha256']))
        rows = list(read_rows(p))
        if len(rows) != panel['rows'] or not rows:
            raise ValueError('BENCHMARK_0_2_PANEL_COUNT')
        for row in rows:
            # SEAL02 panels retain parent_id/row_id, edition and original crop SHA.
            if row.get('split') != name.removeprefix('benchmark_v02_'):
                raise ValueError('BENCHMARK_0_2_PANEL_SPLIT')
        rows = [dict(r, edition_id=r['doc']) for r in rows]
        result.extend(rows); files.append(dict(path=str(p), sha256=sha256(p)))
    return result, files


def audit_inventories(cfg, benchmark):
    """Audit exact prepared membership, including the corrected arm separately."""
    inventories = cfg.get('training_inventories', {})
    if set(inventories) != set(ARMS):
        raise ValueError('TRAINING_INVENTORIES_UNBOUND')
    split = bound(cfg['split2'])
    with gzip.open(split, 'rt', encoding='utf-8') as f:
        heldout = {r['edition_id'] for r in map(json.loads, f) if r['split'] in ('dev', 'test')}
    protected = list(read_rows(bound(cfg['protected_crops'])))
    crop_shas = {r['crop_sha256'] for r in protected}
    if not heldout or not crop_shas:
        raise ValueError('EMPTY_PROTECTED_POPULATION')
    result = {}
    for arm in ARMS:
        result[arm] = exposure(read_rows(bound(inventories[arm])), benchmark, heldout, crop_shas)
    return result


def seal_receipt(suite_spec):
    """Validate the coordinator receipt next to this hash-bound suite."""
    suite_path = bound(suite_spec)
    path = suite_path.parent / 'SEAL_RECEIPT.json'
    try:
        data = path.read_bytes()
    except FileNotFoundError as exc:
        raise ValueError('SEAL_RECEIPT_MISSING: ' + str(path)) from exc
    try:
        receipt = json.loads(data)
    except (ValueError, UnicodeError) as exc:
        raise ValueError('SEAL_RECEIPT_NOT_SEALED: invalid JSON') from exc
    if (not isinstance(receipt, dict) or receipt.get('status') != 'SEALED'
        or receipt.get('version') != '0.2' or receipt.get('mock') is not False):
        raise ValueError('SEAL_RECEIPT_NOT_SEALED')
    suite = read_json(suite_path)
    # seal03 records suite_sha256, but no suite filename. Counts are the
    # total rows and the sum of quota_counts["<split>:<primary>"].sealed.
    mismatch = 'suite_sha256' in receipt and receipt['suite_sha256'] != suite_spec['sha256']
    try:
        panels = suite['panels']
        if 'rows' in receipt:
            mismatch |= receipt['rows'] != sum(p['rows'] for p in panels.values())
        if 'quota_counts' in receipt:
            for name, panel in panels.items():
                prefix = name.removeprefix('benchmark_v02_') + ':'
                counts = [v['sealed'] for k, v in receipt['quota_counts'].items() if k.startswith(prefix)]
                mismatch |= not counts or sum(counts) != panel['rows']
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError('SEAL_RECEIPT_SUITE_MISMATCH: invalid counts') from exc
    if mismatch:
        raise ValueError('SEAL_RECEIPT_SUITE_MISMATCH')
    return dict(path=str(path), sha256=hashlib.sha256(data).hexdigest())


def bind_benchmark(inputs, suite, digest, output):
    """Publish a NEW input revision only after re-auditing the sealed population."""
    inputs, output = Path(inputs).resolve(), Path(output).resolve()
    if output.exists():
        raise ValueError('BIND_OUTPUT_EXISTS')
    cfg = read_json(inputs)
    refuse_locked(cfg)
    spec = dict(path=str(Path(suite).resolve()), sha256=digest)
    receipt = seal_receipt(spec)
    rows, files = sealed_rows(spec)
    audit = audit_inventories(cfg, rows)
    if any(v['hits'] for v in audit.values()):
        raise ValueError('BENCHMARK_0_2_EXPOSURE_FATAL: ' + json.dumps(audit, sort_keys=True))
    if cfg.get('status') == 'INVENTORY_ONLY':
        cfg['status'] = 'FINAL'
    cfg['benchmark_0_2'] = dict(spec, files=files, exposure=audit,
        seal_directory=str(Path(spec['path']).parent), seal_receipt=receipt,
        parent_inputs=dict(path=str(inputs), sha256=sha256(inputs)),
        audit_inputs={k: cfg[k] for k in ('training_inventories','split2','protected_crops')})
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open('x') as f:
            json.dump(cfg, f, indent=2, sort_keys=True)
            f.write('\n')
    except FileExistsError as exc:
        raise ValueError('BIND_OUTPUT_EXISTS') from exc
    return cfg


def verify_inputs(cfg):
    errors, checked = [], []
    try:
        refuse_locked(cfg)
        if cfg.get('editions'):
            split2_ledgers(cfg)
    except (ValueError, KeyError, OSError) as exc:
        errors.append(str(exc))
    if set(cfg.get('training_inventories', {})) != set(ARMS) or not cfg.get('protected_crops'):
        errors.append('INVENTORY_PENDING')
    # All external file inputs must be explicit path/SHA pairs. Crop roots are
    # verified in the compute job; never recursively hash them on the login node.
    for spec in cfg.get('input_files', []):
        try:
            p = bound(spec); checked.append(str(p))
        except (ValueError, OSError) as exc:
            errors.append(str(exc))
    if not cfg.get('input_files'):
        errors.append('INPUT_FILE_INVENTORY_UNBOUND')
    benchmark = cfg.get('benchmark_0_2')
    if not benchmark:
        errors.append('BENCHMARK_0_2_UNBOUND')
    else:
        try:
            receipt = seal_receipt(benchmark)
            if (receipt != benchmark.get('seal_receipt')
                or benchmark.get('seal_directory') != str(Path(benchmark['path']).resolve().parent)):
                raise ValueError('SEAL_RECEIPT_SUITE_MISMATCH: binding changed')
            _, files = sealed_rows(benchmark)
            if files != benchmark['files']:
                raise ValueError('BENCHMARK_0_2_BINDING_CHANGED')
            if set(benchmark.get('exposure', {})) != set(ARMS) or any(v['hits'] for v in benchmark['exposure'].values()):
                raise ValueError('BENCHMARK_0_2_EXPOSURE_FATAL')
            if benchmark.get('audit_inputs') != {k: cfg[k] for k in ('training_inventories','split2','protected_crops')}:
                raise ValueError('BENCHMARK_0_2_AUDIT_INPUTS_CHANGED')
            for spec in cfg['training_inventories'].values():
                bound(spec)
            bound(cfg['split2']); bound(cfg['protected_crops'])
        except (ValueError, KeyError, OSError) as exc:
            errors.append(str(exc))
    return dict(state='VERIFY_INPUTS_OK' if not errors else 'VERIFY_INPUTS_FAIL', checked=len(checked), errors=errors)


class Census05Admission:
    """Read the generation-pinned census in a compute job; preserve factory labels.

    This adapts selection only. It does not reinterpret final_text as a target
    and does not run the toolkit producer. Ambiguous IDs fail closed.
    """
    def __init__(self, cfg):
        self.cfg, self.rows, self.inputs = cfg, {}, []
        current_path = bound(cfg['current']); current = read_json(current_path)
        summary_path = bound(cfg['summary']); summary = read_json(summary_path)
        if (current['status'] != 'completed' or summary.get('complete') is not True
            or current['summary_sha256'] != sha256(summary_path)
            or current['export_id'] != summary['export_id']):
            raise ValueError('CENSUS05_NOT_COMPLETE')
        records = bound(cfg['records'])
        if summary['outputs']['admission_records']['sha256'] != sha256(records):
            raise ValueError('CENSUS05_GENERATION_MISMATCH')
        self.inputs = [current_path, summary_path, records]
        self.reasons, self.groups = Counter(), {}
        for row in read_rows(records):
            ident = row['row_id']; d = row['decision']
            if ident in self.rows:
                raise ValueError('CENSUS05_AMBIGUOUS_ROW_ID: ' + ident)
            if (d['binding'] != dict(parent_id=row['parent_id'], id=ident, split=row['split'], crop_sha256=row['crop_sha256'])
                or type(row['pass']) is not bool or row['pass'] != (row['disposition'] == 'ADMIT')
                or d['disposition'] != row['disposition'] or d['run_binding_sha256'] != current['run_binding_sha256']):
                raise ValueError('CENSUS05_DECISION_IDENTITY')
            selected = row['pass'] and row['split'] == 'train'
            reasons = [r['reason'] for r in d['reasons']]
            if not selected:
                self.reasons.update(reasons)
                self.groups.setdefault(row['source'], {}).setdefault(row['primary_class'], Counter()).update(reasons)
            self.rows[ident] = dict(parent_id=row['parent_id'], row_id=ident, split=row['split'],
                crop_sha256=row['crop_sha256'], final_text=d['final_text'], source=row['source'],
                primary_class=row['primary_class'], **{'pass': selected})
        if len(self.rows) != summary['input_rows']:
            raise ValueError('CENSUS05_COUNT_MISMATCH')
        # Detect mutation during the population scan.
        bound(cfg['records']); bound(cfg['current']); bound(cfg['summary'])

    def decision(self, row):
        ident = row.get('row_id', row.get('line_id'))
        if ident not in self.rows:
            raise ValueError('real row absent from census05: ' + str(ident))
        d = self.rows[ident]
        if row.get('parent_id', d['parent_id']) != d['parent_id']:
            raise ValueError('CENSUS05_PARENT_MISMATCH')
        if row.get('crop_sha256', d['crop_sha256']) != d['crop_sha256']:
            raise ValueError('CENSUS05_CROP_MISMATCH')
        return d

    def filter(self, rows):
        return [r for r in rows if self.decision(r)['pass']]

    def require_pass(self, rows):
        for r in rows:
            if not self.decision(r)['pass']:
                raise ValueError('refuses failed census05 row: ' + str(r.get('row_id', r.get('line_id'))))

    def require_coverage(self, paths):
        # Release files are independently bound by the driver; exact membership
        # is checked by filter/require_pass. They are not old-format receipts.
        for p in paths:
            for r in read_rows(p): self.decision(r)

    def require_census(self, rows, new_paths):
        for r in rows:
            if self.decision(r)['parent_id'] != 'collection-v2-train':
                raise ValueError('CENSUS05_OLD_PARENT_MISMATCH')

    def receipt(self, control):
        return dict(files=[dict(path=str(p), sha256=sha256(p)) for p in self.inputs],
            rows_total=len(self.rows), rows_pass=sum(r['pass'] for r in self.rows.values()),
            drops_per_rule=dict(self.reasons), drops_per_source_class=self.groups,
            control_rows=control, filtering='census05 ADMIT intersection train split',
            refuses_unfiltered_rows=True, labels='factory labels retained; final_text selection evidence only')


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='action', required=True)
    b = sub.add_parser('bind-benchmark')
    b.add_argument('--inputs', type=Path, required=True); b.add_argument('--suite', type=Path, required=True)
    b.add_argument('--sha256', required=True); b.add_argument('--out', type=Path, required=True)
    v = sub.add_parser('verify-inputs'); v.add_argument('--inputs', type=Path, required=True)
    a = p.parse_args(argv)
    if a.action == 'bind-benchmark':
        bind_benchmark(a.inputs, a.suite, a.sha256, a.out); print('BENCHMARK_0_2_BOUND')
    else:
        result = verify_inputs(read_json(a.inputs)); print(json.dumps(result, sort_keys=True))
        return 0 if result['state'] == 'VERIFY_INPUTS_OK' else 3
    return 0




def release_row(row, spec):
    """Adapt REL3's exact schema without changing the raw Google label."""
    if row.get('split') != 'train' or row.get('parent_id') not in spec['crop_roots']:
        raise ValueError('REL3_PARENT_OR_SPLIT')
    if hashlib.sha256(row['label'].encode('utf-8')).hexdigest() != row['raw_text_sha256']:
        raise ValueError('REL3_LABEL_IS_NOT_RAW_IMPORT')
    root = Path(spec['crop_roots'][row['parent_id']]).resolve()
    expected = Path(root.name) / row['source'] / (row['row_id'] + '.png')
    if row['crop_relative_path'] != str(expected):
        raise ValueError('REL3_CROP_PATH_IDENTITY')
    return dict(row, crop='original', arm='release-v3', primary_class=None,
        page_id=None, crop_bbox=None, provenance=row['admission_decision'],
        crops_root=str(root), crops_layout='source/row_id')


def prepare_exposure(real, new, gate, cfg, out):
    """Compute-job audit using census identities, original crop hashes and pixels.

    This must run before imports/training. It writes small inventories that the
    later seal bind can audit without scanning crop trees on a login node.
    """
    metadata = {}
    path = bound(cfg['census05']['admitted_train'])
    wanted = {r['line_id'] for r in real} | {r['row_id'] for r in new}
    for r in read_rows(path):
        ident = r['id']
        if ident in wanted:
            if ident in metadata:
                raise ValueError('CENSUS05_AMBIGUOUS_TRAIN_ID')
            metadata[ident] = dict(parent_id=r['parent_id'], row_id=ident,
                edition_id=r['edition_id'], crop_sha256=r['crop_sha256'])
    if set(metadata) != wanted:
        raise ValueError('CENSUS05_MISSING_TRAIN_IDENTITY')
    bound(cfg['census05']['admitted_train'])
    ctrl = []
    for r in real:
        m = metadata[r['line_id']]
        d = gate.decision(r)
        if m['parent_id'] != d['parent_id'] or m['crop_sha256'] != d['crop_sha256']:
            raise ValueError('CENSUS05_TRAIN_CROP_IDENTITY')
        if not r.get('edition_id'): raise ValueError('OLD_V2_EDITION_UNBOUND')
        m = dict(m, edition_id=r['edition_id'])
        ctrl.append(m)
        # Original-crop identity and embedded factory PNG bytes are distinct
        # witnesses; audit both when the byte streams differ.
        h = hashlib.sha256(r['image_png']).hexdigest()
        if h != m['crop_sha256']:
            m['factory_crop_sha256'] = h
    old_ids = {r['line_id'] for r in real}
    union = ctrl + [metadata[r['row_id']] for r in new if r['row_id'] not in old_ids]
    protected = {r['crop_sha256'] for r in gate.rows.values() if r['split'] not in ('train', 'unassigned')}
    # The census also protects configured external crop hashes. An independently
    # hash-bound policy snapshot is mandatory; never infer that it is empty.
    policy = read_json(bound(cfg['census05']['final_policy']))
    protected.update(policy['heldout_crop_sha256'])
    out = Path(out)
    protected_path = out/'protected_crops.jsonl'
    write_rows(protected_path, [dict(crop_sha256=h) for h in sorted(protected)])
    local = dict(cfg, protected_crops=dict(path=str(protected_path), sha256=sha256(protected_path)), training_inventories={})
    for arm, rows in [('ctrl', ctrl), ('add', union), ('add_corr', union)]:
        p = out/(arm+'_train_inventory.jsonl'); write_rows(p, rows)
        local['training_inventories'][arm] = dict(path=str(p), sha256=sha256(p))
    candidates = list(read_rows(bound(cfg['candidates'])))
    readout = {key(r): r for r in read_rows(bound(cfg['candidates_readout']))}
    for r in candidates:
        r['crop_sha256'] = readout[key(r)]['crop_sha256']
    audit = audit_inventories(local, candidates)
    atomic_json(out/'EXPOSURE_CANDIDATES.json', dict(arms=audit, files=dict(
        candidates=cfg['candidates'], readout=cfg['candidates_readout'], split2=cfg['split2'],
        admitted_train=cfg['census05']['admitted_train'], final_policy=cfg['census05']['final_policy'],
        protected=local['protected_crops'], inventories=local['training_inventories'])))
    if any(v['hits'] for v in audit.values()):
        raise ValueError('CANDIDATE_EXPOSURE_FATAL: ' + json.dumps(audit, sort_keys=True))
    if cfg.get('benchmark_0_2'):
        sealed, _ = sealed_rows(cfg['benchmark_0_2'])
        sealed_audit = audit_inventories(local, sealed)
        if any(v['hits'] for v in sealed_audit.values()):
            raise ValueError('SEALED_EXPOSURE_FATAL')
        atomic_json(out/'EXPOSURE_SEALED.json', sealed_audit)
    atomic_json(out/'INPUTS.with_inventories.json', local)
    return local




def prepare_benchmark(cfg, out, factory, codec):
    """Import sealed originals for inference; 0.1 scores literal panel references."""
    from bench.e1_prepare import factory_build
    from bench import e4_wave1c as labels
    from train.mix import shard_inventory
    spec = cfg.get('benchmark_0_2')
    if not spec:
        raise ValueError('BENCHMARK_0_2_UNBOUND')
    _, files = sealed_rows(spec)
    suite_path = Path(spec['path']); suite = read_json(suite_path)
    result = {}
    context = labels.encoding_context(codec)
    for name, panel in suite['panels'].items():
        records = []
        for r in read_rows(suite_path.parent/panel['path']):
            image = (suite_path.parent/r['crop_path']).resolve()
            if not image.is_relative_to(suite_path.parent) or sha256(image) != r['crop_sha256']:
                raise ValueError('BENCHMARK_0_2_IMAGE_IDENTITY')
            text, _, bad = labels.encode(r['text'], codec, context)
            if bad:
                raise ValueError('BENCHMARK_0_2_REFERENCE_CODEC_REJECTION: '+r['id'])
            records.append(dict(id=r['id'], text=text, crop_path=r['crop_path'], doc=r['doc'],
                split='reserved', source_dataset=r['source'], script_class='benchmark', admitted=True))
        folder = Path(out)/name; folder.mkdir(parents=True, exist_ok=True)
        feed = folder/'records.jsonl'; write_rows(feed, records)
        build = folder/'factory'
        if not build.exists():
            factory_build(factory, ['import-real','--records',feed,'--crops',suite_path.parent,
                '--partition','benchmark-0.2','--codec-json',codec], build)
        info = read_json(build/'build_info.json')
        if info['records_sha256'] != sha256(feed) or info.get('drop_ledger'):
            raise ValueError('BENCHMARK_0_2_FACTORY_DROPPED_ROWS')
        mix = folder/'mix.json'
        atomic_json(mix, dict(schema_version=1, seed=20261015, codec_version='v2.1', created_by='E4 wave2',
            notes='Sealed benchmark 0.2 inference only; literal references scored by pinned 0.1 scorer',
            components=[dict(kind='real', shard_dir=str(build), shard_sha256=shard_inventory(build),
                partition_id='benchmark-0.2', source=name, fraction=1.)]))
        result[name] = mix
    return result


def score_benchmark(cfg, out, run, smoke=False):
    """Invoke the unchanged SEAL02-bound 0.1 scorer separately on test and dev."""
    import os
    import subprocess
    import sys
    binding = read_json(bound(cfg['benchmark_scorer_binding']))
    scorer_root = Path(cfg['benchmark_scorer_root'])
    for relative, digest in binding['files'].items():
        bound(dict(path=str(scorer_root/relative), sha256=digest))
    suite = Path(cfg['benchmark_0_2']['path'])
    complete = read_json(Path(out)/'runs'/run/'E1_RUN_COMPLETE.json')
    model = dict(id=run, model_revision=complete['checkpoint_hashes']['best.pt'], decoder='CTC greedy',
        preprocessing='canonical factory height 48', runtime='bound E1_RUN_COMPLETE.json',
        training_audit=dict(complete=False, evidence='edition/row/crop audit only; synthetic and corrector provenance not fully certified'),
        smoke_only=smoke)
    manifest = Path(out)/'predictions'/(run+'_benchmark_model.json'); atomic_json(manifest, model)
    for name in read_json(suite)['panels']:
        pred = Path(out)/'predictions'/(run+'_'+name+'.jsonl')
        target = Path(out)/'predictions'/(run+'_'+name+'.score.json')
        subprocess.run([sys.executable, '-B', str(scorer_root/'bench/benchmark_suite.py'), str(suite),
            '--panel', name, '--predictions', str(pred), '--model', str(manifest), '--out', str(target)],
            check=True, env={**os.environ, 'PYTHONPATH': str(scorer_root), 'PYTHONDONTWRITEBYTECODE':'1'})


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError) as exc:
        print('E4_WAVE2_R3_FAIL:', exc); raise SystemExit(2)
