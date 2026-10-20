"""E4 wave 1c: exact v_c draws, label-only overlays, width-x2 paired control.

No network or submission in this driver. --mock is a CPU custody/scoring mock,
never a scientific result. Production preparation requires a released registry.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import copy
import filecmp
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import unicodedata

from bench.e1_common import ROOT, atomic_json, check_files, files_binding, read_json, sha256
from bench import e3_driver as e3
from bench import e4_wave1b as base
from bench.common import read_rows, write_rows
from train.cer import load_codec, levenshtein
from train.mix import validate, load_rows, assemble

RELEASE = 'ef64d8b70f5bc946201a0d082c8ca0b711f0abefe1c1b12b46c82473f840175d'
DRAW_SHA = 'e8ad83599f7d69ab11db6c862863555eafe900572ddaf3a8855e695ef7704e6f'
JOBS = {'job01': [f'ctrl_s{s}' for s in range(3)],
        'job02': [f'lc_s{s}' for s in range(3)]}
LABEL_FIELDS = {'text', 'gt_nfd', 'gt_nfc', 'label_ids'}


# Registry adapter copied from greek-page-ocr-wave1c/bench/e4_wave1c.py;
# extended only with the explicit N1 id/text field pair.
def registry(path, names, *, production=False):
    """LQB field names; exact IDs, explicit fields, hash and provenance required.

    Disagreeing overlays are an error, regardless of selection order. Parent is
    provenance only: uncovered rows always retain the baseline factory labels.
    """
    path = Path(path).resolve()
    obj = read_json(path)
    if obj.get('schema') != 'lqb-versions-v1' or not isinstance(obj.get('versions'), dict):
        raise ValueError('unsupported label registry')
    if not names or len(names) != len(set(names)):
        raise ValueError('select distinct registered label versions')
    loaded, merged = {}, {}
    required = {'path', 'sha256', 'population', 'parent', 'text_field', 'id_field', 'status', 'read'}
    for name in names:
        if name not in obj['versions']:
            raise ValueError('unregistered label version: ' + name)
        spec = obj['versions'][name]
        if required - spec.keys() or (spec['id_field'], spec['text_field']) not in {('row_id', 'text'), ('id', 'label'), ('id', 'text')}:
            raise ValueError('label registry requires row_id/text and LQB fields')
        if production and not (spec['status'] == 'released' or
                (spec['status'] == 'local' and spec.get('e4_adoption') == 'coordinator-registered'
                 and spec.get('provenance'))):
            raise ValueError('real released label version required; mocks cannot deploy')
        source = (path.parent / spec.get('portable_path', spec['path'])).resolve()
        if sha256(source) != spec['sha256']:
            raise ValueError('label version hash mismatch: ' + name)
        records = {}
        for row in read_rows(source):
            ident, text = row.get(spec['id_field']), row.get(spec['text_field'])
            provenance = row.get('provenance', spec.get('provenance'))
            if not isinstance(ident, str) or not ident or not isinstance(text, str) or not provenance:
                raise ValueError('label row requires exact string row_id, text, provenance')
            if ident in records:
                raise ValueError('duplicate row_id: ' + ident)
            if ident in merged and merged[ident]['text'] != text:
                raise ValueError('conflicting label versions: ' + ident)
            record = dict(row, row_id=ident, text=text, provenance=provenance)
            records[ident] = record
            merged[ident] = record
        if spec['population'].get('rows') != len(records):
            raise ValueError('label population row count mismatch')
        loaded[name] = dict(spec=spec, path=source, rows=records)
    return loaded


def overlay_spec(path, names, codec, *, production=True):
    registry(path, names, production=production)
    return dict(registry=str(Path(path).resolve()), registry_sha256=sha256(path),
                versions=names, codec=str(Path(codec).resolve()), codec_sha256=sha256(codec),
                production=production)


def check_overlay(spec):
    if set(spec) != {'registry', 'registry_sha256', 'versions', 'codec', 'codec_sha256', 'production'}:
        raise ValueError('invalid wave1c overlay specification')
    if sha256(spec['registry']) != spec['registry_sha256'] or sha256(spec['codec']) != spec['codec_sha256']:
        raise ValueError('changed wave1c registry/codec')
    if read_json(spec['codec'])['version'] not in ('v2','v2.1'):
        raise ValueError('label overlay requires codec v2 or v2.1')
    return registry(spec['registry'], spec['versions'], production=spec['production'])


def encoding_context(codec_path):
    from bench.codec_coverage import load_v1
    obj = read_json(codec_path)
    _, folds = load_v1()
    return {a['ch']: a['id'] for a in obj['atoms']}, folds, {a['ch'] for a in obj['atoms'][247:]}


def encode(text, codec_path, context=None):
    # The same factory normalization/folds used by the v2 recovery release.
    atoms, folds, added = context or encoding_context(codec_path)
    normalized = ' '.join(''.join(c if c in added else folds.get(c,c)
                                for c in unicodedata.normalize('NFD', text)).split())
    bad = sorted(set(normalized) - atoms.keys())
    if bad or not normalized:
        return normalized, None, [f'U+{ord(c):04X}' for c in bad] or ['EMPTY_LABEL']
    return normalized, [atoms[c] for c in normalized], []


def substitute(groups, components, spec, *, row_waves=None):
    versions = check_overlay(spec)
    context = encoding_context(spec['codec'])
    result, counts, rejections, changes, seen = [], Counter(), [], [], set()
    matched = {v: set() for v in versions}
    for group, component in zip(groups, components):
        out = []
        for row in group:
            new = row
            if component['kind'] == 'real':
                ident = row.get('line_id')
                if not isinstance(ident, str) or not ident or ident in seen:
                    raise ValueError('missing or duplicate real row identity')
                seen.add(ident)
                hits = [(v, data['rows'][ident]) for v, data in versions.items() if ident in data['rows']]
                if hits:
                    text, ids, bad = encode(hits[0][1]['text'], spec['codec'], context)
                    changed = ids is not None and ids != row['label_ids']
                    cls = row.get('source_script_class', row['script_class'])
                    if row_waves is not None and ident not in row_waves:
                        raise ValueError('missing wave metadata for corrected row: '+ident)
                    wave = row_waves[ident] if row_waves is not None else row.get('wave', row.get('source_dataset', 'unknown'))
                    outcome = 'codec_rejected' if bad else 'substituted' if changed else 'unchanged'
                    for version, record in hits:
                        matched[version].add(ident)
                        counts[(version, cls, wave, 'covered')] += 1
                        counts[(version, cls, wave, outcome)] += 1
                        if bad:
                            rejections.append(dict(row_id=ident, version=version, script_class=cls, wave=wave,
                                corrected_text=record['text'], normalized=text, unmapped=bad,
                                retained_label_ids=row['label_ids'], provenance=record['provenance']))
                    if changed:
                        new = dict(row, label_ids=ids)
                        for field in ('text', 'gt_nfd', 'gt_nfc'):
                            if field in row:
                                new[field] = unicodedata.normalize('NFC', text) if field == 'gt_nfc' else text
                        changes.append(dict(row_id=ident, versions=[v for v, _ in hits],
                                            script_class=cls, wave=wave))
            out.append(new)
        result.append(out)
    receipt = dict(rows_substituted=len(changes), changes=changes, codec_rejections=rejections,
        counts=[dict(version=v, script_class=c, wave=w, outcome=o, rows=n)
                for (v, c, w, o), n in sorted(counts.items())],
        unmatched={v: sorted(set(d['rows']) - matched[v]) for v, d in versions.items()})
    return result, receipt


def _line(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()


def _nonlabel(row):
    return {k: hashlib.sha256(v).hexdigest() if isinstance(v, bytes) else v
            for k, v in row.items() if k not in LABEL_FIELDS}


def draw_contract(groups, corrected, mix, out, *, rows=base.ROWS, epochs=8, reference=None, indexed=None):
    """Byte-compare every ordered non-label field; pin original v_c index bytes.

    Full manifests differ only in text/encoded targets. Separate non-label
    manifests are byte-identical, including pixels, width, source and position.
    """
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    manifests = {}
    with (out/'v_c_indices.jsonl.gz').open('wb') as raw_index:
        with gzip.GzipFile(filename='', fileobj=raw_index, mode='wb', mtime=0) as index_sink:
            for epoch in range(1, epochs + 1):
                kwargs = dict(exact_rows=True, recovery=mix.get('codec_recovery'), replay=mix.get('matched_replay'))
                left, a = assemble(groups, [c['fraction'] for c in mix['components']], mix['seed'], epoch, rows, **kwargs)
                right, b = assemble(corrected, [c['fraction'] for c in mix['components']], mix['seed'], epoch, rows, **kwargs)
                if a != b or len(left) != len(right):
                    raise ValueError('draw count mismatch')
                original = hashlib.sha256(); changed = 0
                paths = [out/f'{arm}_e{epoch}{suffix}.jsonl.gz' for arm, suffix in
                         [('ctrl', ''), ('lc', ''), ('ctrl', '_nonlabel'), ('lc', '_nonlabel')]]
                from contextlib import ExitStack
                with ExitStack() as stack:
                    sinks = [stack.enter_context(gzip.GzipFile(filename='', mode='wb', mtime=0,
                             fileobj=stack.enter_context(p.open('wb')))) for p in paths]
                    for position, (x, y) in enumerate(zip(left, right)):
                        bx, by = _line(_nonlabel(x)), _line(_nonlabel(y))
                        if bx != by:
                            raise ValueError('draws differ outside text labels')
                        if mix['components'][x['_component']]['kind'] != 'real' and x != y:
                            raise ValueError('synthetic label changed')
                        for sink, row in zip(sinks[:2], (x, y)):
                            sink.write(_line(dict(position=position, row=_nonlabel(row),
                                                  text={k:row[k] for k in LABEL_FIELDS if k in row})))
                        sinks[2].write(bx); sinks[3].write(by)
                        index_sink.write((json.dumps([epoch, position, x['_component'], x['_pool_index'],
                                                     x['line_id']], separators=(',', ':')) + '\n').encode())
                        original.update((json.dumps([x['line_id'], hashlib.sha256(x['image_png']).hexdigest(),
                                                     x['label_ids']], separators=(',', ':')) + '\n').encode())
                        changed += x['label_ids'] != y['label_ids']
                if not filecmp.cmp(paths[2], paths[3], shallow=False):
                    raise ValueError('nonlabel draw manifests are not byte-identical')
                if reference and original.hexdigest() != reference['epochs'][str(epoch)]['ordered_image_label_sha256']:
                    raise ValueError('baseline differs from v_c image/label/order contract')
                manifests[str(epoch)] = dict(draws=len(left), substituted_draws=changed,
                    v_c_image_label_sha256=original.hexdigest(), files=files_binding(paths))
    if indexed and sha256(out/'v_c_indices.jsonl.gz') != sha256(indexed):
        raise ValueError('indexed v_c draw bytes differ')
    result = dict(epochs=manifests, nonlabel_byte_identical=True,
                  indexed_sha256=sha256(out/'v_c_indices.jsonl.gz'))
    atomic_json(out/'contract.json', result)
    return result


def changed_slice(rows, spec):
    """Re-score unchanged predictions twice; rejected corrected references excluded."""
    versions = check_overlay(spec); selected, rejected = [], []
    context = encoding_context(spec['codec'])
    seen = set()
    for row in rows:
        ident = row['line_id']
        if ident in seen:
            raise ValueError('duplicate test row identity')
        seen.add(ident)
        hits = [(v, d['rows'][ident]) for v, d in versions.items() if ident in d['rows']]
        if not hits:
            continue
        corrected, ids, bad = encode(hits[0][1]['text'], spec['codec'], context)
        if bad:
            rejected.append(dict(row_id=ident, versions=[v for v, _ in hits], unmapped=bad))
        elif corrected != row['gt']:
            selected.append(dict(row_id=ident, original=row['gt'], corrected=corrected,
                prediction=row['prediction'], versions=[v for v, _ in hits],
                script_class=row.get('source_script_class',row.get('script_class','unknown')),
                wave=row.get('wave','unknown'),
                provenance={v:r['provenance'] for v, r in hits},
                original_edits=levenshtein(row['gt'], row['prediction']),
                corrected_edits=levenshtein(corrected, row['prediction'])))
    def score(key):
        length = sum(len(r[key]) for r in selected)
        edits = sum(r[key+'_edits'] for r in selected)
        return dict(lines=len(selected), ref_len=length, edits=edits, cer=edits/length if length else None)
    return dict(rows=selected, original=score('original'), corrected=score('corrected'),
                codec_rejections=rejected, status='AVAILABLE' if selected else 'NO_CORRECTED_TEST_ROWS')


def verdict(control, candidate, corrected_classes, *, mode='PRODUCTION'):
    """H6: every corrected class improves > control range, no other class harms > it."""
    if mode != 'PRODUCTION':
        return mode + '_ONLY'
    if not corrected_classes:
        return 'H6_PENDING_NO_CORRECTED_CLASSES'
    if set(control) != set(candidate) or not set(corrected_classes) <= set(control):
        return 'H6_PENDING_MISSING_CLASS'
    if any(set(v) != {'0', '1', '2'} or any(x is None or not math.isfinite(x) for x in v.values())
           for v in [*control.values(), *candidate.values()]):
        return 'H6_PENDING_MISSING_SEEDS'
    def mean(v): return sum(v.values()) / 3
    improvements, harms = {}, {}
    for cls, values in control.items():
        span = max(values.values()) - min(values.values())
        delta = mean(candidate[cls]) - mean(values)
        improvements[cls] = delta < -span
        harms[cls] = delta > span
    return ('H6_CONFIRMED' if all(improvements[c] for c in corrected_classes)
            and not any(harms[c] for c in control if c not in corrected_classes) else 'H6_REFUTED')


def instruments(a):
    # Preserve all wave1b instruments; common and full are separate populations.
    common = read_json(a.campaign/'v2-codec/common_intersection.json')['instruments']
    full = read_json(a.campaign/'v2-codec/full_coverage.json')['instruments']
    paths = {name: a.prep/'mixes'/f'{name}_mix.json' for name in e3.INSTRUMENTS}
    for name, value in common.items(): paths[name] = Path(value['path'])
    for name, value in full.items(): paths[name+'_full_coverage'] = Path(value['path'])
    return paths


def slice_mix(source, target, split, budget):
    """Real smoke subset with bounded total rows and hash-bound tag sidecars."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    mix = validate(source, role='train' if split == 'train' else 'val' if split == 'val' else 'eval')
    pools = load_rows(mix, split); active = sum(c['fraction'] > 0 for c in mix['components'])
    if budget < active: raise ValueError('smoke budget below component count')
    remaining = budget
    result = copy.deepcopy(mix)
    for key in ('codec_recovery', 'matched_replay', 'label_versions'): result.pop(key, None)
    for i, (component, pool) in enumerate(zip(result['components'], pools)):
        folder = target.parent/(target.stem+f'_c{i}'); folder.mkdir(parents=True, exist_ok=True)
        count = min(len(pool), remaining - (active - 1)) if component['fraction'] > 0 else 0
        if component['fraction'] > 0: active -= 1
        chosen = pool[:count]; remaining -= count
        original = Path(component.get('build_dir', component.get('shard_dir')))
        directory = folder if component['kind'] == 'legacy_eval' else folder/split
        directory.mkdir(exist_ok=True)
        pq.write_table(pa.Table.from_pylist(chosen), directory/'shard-00000.parquet')
        info = read_json(original/'build_info.json')
        info['shard_sha256'] = {str(p.relative_to(folder)):sha256(p) for p in folder.rglob('shard-*.parquet')}
        if info.get('word_tags_sha256'):
            ids = {r['line_id'] for r in chosen}
            tags = [r for r in read_rows(original/'word_tags.jsonl') if r['line_id'] in ids]
            if {r['line_id'] for r in tags} != ids: raise ValueError('smoke missing word tags')
            write_rows(folder/'word_tags.jsonl', tags); info['word_tags_sha256'] = sha256(folder/'word_tags.jsonl')
        info['smoke_only'] = True
        atomic_json(folder/'build_info.json', info)
        component.pop('build_info_sha256', None)
        component['build_dir' if component['kind'] == 'synthetic' else 'shard_dir'] = str(folder)
        if component['kind'] != 'synthetic': component['shard_sha256'] = info['shard_sha256']
        else: component.pop('shard_sha256', None)
    e3.immutable(target, result)
    validate(target, role='train' if split == 'train' else 'val' if split == 'val' else 'eval')
    return target


def prepare(a):
    spec = overlay_spec(a.registry, a.versions.split(','), ROOT/'codec/v2.json')
    release, assets, release_sha = base.load_release(a)
    if release_sha != RELEASE or sha256(a.campaign/'v2-codec/draw_rows_v_c.jsonl.gz') != DRAW_SHA:
        raise ValueError('unpinned v_c release/draw indices')
    a.out.mkdir(parents=True, exist_ok=True); (a.out/'logs').mkdir(exist_ok=True)
    if (a.out/'node_binding.json').exists():
        return verify(a)  # idempotent, does not replace immutable runtime bindings
    mixpath, valpath = assets['recovered_mix'], assets['val_v2']
    evals = instruments(a)
    if a.smoke:
        mixpath = slice_mix(mixpath, a.out/'smoke_data/train.json', 'train', 20)
        valpath = slice_mix(valpath, a.out/'smoke_data/val.json', 'val', 8)
        evals = {k:slice_mix(v, a.out/f'smoke_data/{k}.json', 'reserved', 4) for k,v in evals.items()}
    mix = validate(mixpath); pools = load_rows(mix, 'train')
    meta_paths = list((a.prep/'records').glob('*.meta.jsonl'))
    row_waves = {}
    for path in meta_paths:
        for row in read_rows(path):
            ident = row['line_id']
            if ident in row_waves and row_waves[ident] != row['wave']:
                raise ValueError('conflicting wave metadata: '+ident)
            row_waves[ident] = row['wave']
    fixed, stats = substitute(pools, mix['components'], spec, row_waves=row_waves)
    e3.immutable(a.out/'substitution.json', stats)
    contract = draw_contract(pools, fixed, mix, a.out/'draws', rows=20 if a.smoke else base.ROWS,
        reference=None if a.smoke else read_json(assets['draw_v_c']),
        indexed=None if a.smoke else a.campaign/'v2-codec/draw_rows_v_c.jsonl.gz')
    corrected = read_json(mixpath)
    # Resolve component paths exactly as validated, then remove validation-only fields.
    for c, resolved in zip(corrected['components'], mix['components']):
        key = 'build_dir' if c['kind'] == 'synthetic' else 'shard_dir'; c[key] = resolved[key]
    for key in ('codec_recovery', 'matched_replay'):
        if key in corrected: corrected[key] = mix[key]
    corrected['label_versions'] = spec
    e3.immutable(a.out/'lc_mix.json', corrected)
    names = ['ctrl_s0', 'lc_s0'] if a.smoke else JOBS['job01'] if a.job == 'job01' else JOBS['job02'] if a.job == 'job02' else ['ctrl_s0', 'lc_s0']
    arms = []
    for run in names:
        config, seed = run.rsplit('_s', 1)
        p = base.parameters(a.out, 50, int(seed), 20 if a.smoke else base.ROWS)
        p.update(mix=str(mixpath if config == 'ctrl' else a.out/'lc_mix.json'), codec=spec['codec'],
                 val_mix=str(valpath), transfer_mix=None, repeat_to_epoch_rows=True, width_mult=2.)
        if a.smoke: p.update(workers=0)
        arms.append(dict(arm=config, run=run, seed=int(seed), parameters=p, initialization='from-scratch'))
    inputs = [a.registry, *[d['path'] for d in check_overlay(spec).values()], spec['codec'],
              a.campaign/'v2-codec/release.json', mixpath, valpath, *evals.values(),
              a.out/'lc_mix.json', a.out/'substitution.json', a.out/'draws/contract.json']
    for path in [mixpath, valpath, *evals.values()]:
        obj = validate(path, role='train' if path == mixpath else 'val' if path == valpath else 'eval')
        for c in obj['components']:
            folder = Path(c.get('build_dir', c.get('shard_dir')))
            inputs += [folder/'build_info.json', *folder.rglob('shard-*.parquet')]
            if (folder/'word_tags.jsonl').exists(): inputs.append(folder/'word_tags.jsonl')
        for key in ('codec_recovery', 'matched_replay'):
            if key in obj: inputs.append(Path(obj[key]['path']))
    inputs += base.code_files()
    inputs += list((ROOT/'codec').glob('*.json')) + [ROOT/'factory/recipe.v5.json', ROOT/'factory/src/codec.rs', *meta_paths]
    inputs += list((ROOT/'scripts/clariden').glob('*wave1c*'))
    e3.immutable(a.out/'arms.json', arms)
    e3.immutable(a.out/'node_binding.json', dict(schema='e4-wave1c-node-v1', mode='SMOKE' if a.smoke else 'PRODUCTION',
        job=a.job, root=str(ROOT), out=str(a.out), campaign=str(a.campaign), prep=str(a.prep),
        versions=spec, release_sha256=RELEASE, arms=arms, instruments={k:str(v) for k,v in evals.items()},
        corrected_classes=sorted({r['script_class'] for r in stats['changes']}),
        inputs=files_binding(inputs), draw_contract=contract, control='retrain'))
    return verify(a)


def verify(a):
    node = read_json(a.out/'node_binding.json')
    if (node['schema'] != 'e4-wave1c-node-v1' or node['out'] != str(a.out)
        or node['root'] != str(ROOT) or node['mode'] != ('SMOKE' if a.smoke else 'PRODUCTION')
        or node['prep'] != str(a.prep) or node['campaign'] != str(a.campaign)
        or node['versions']['registry'] != str(a.registry) or node['versions']['versions'] != a.versions.split(',')):
        raise ValueError('wave1c binding destination/mode/version mismatch')
    check_files(node['inputs']); check_overlay(node['versions'])
    for epoch in node['draw_contract']['epochs'].values():
        check_files(epoch['files'])
    if sha256(a.out/'draws/v_c_indices.jsonl.gz') != node['draw_contract']['indexed_sha256']:
        raise ValueError('changed draw index manifest')
    if read_json(a.out/'arms.json') != node['arms']: raise ValueError('changed arms')
    return node


def evaluate_arm(a, arm):
    from bench.e1_eval import evaluate_run
    from bench import e1_common
    node = verify(a); original = e1_common.runtime_binding
    e1_common.runtime_binding = lambda device:e3.allocation_runtime(original(device))
    try:
        for name, path in node['instruments'].items():
            codec = ROOT/'codec'/f"{read_json(path)['codec_version']}.json"
            evaluate_run(a.out, arm['run'], name, Path(path), codec_path=arm['parameters']['codec'], reference_codec_path=codec)
    finally:
        e1_common.runtime_binding = original


def report(a, roots):
    from bench.e1_readout import summarize, metric, clean_row
    results, class_values, sources, populations = {}, defaultdict(lambda:defaultdict(dict)), {}, {}
    overall_values = defaultdict(lambda:defaultdict(dict))
    common = None
    for run, root in roots.items():
        local = copy.copy(a); local.out = root
        node = verify(local)
        identity = {k:node[k] for k in ('mode','versions','release_sha256','corrected_classes')}
        if common is not None and identity != common: raise ValueError('mixed aggregate identity')
        common = identity
        done = base.verify_done(root/'runs'/run)
        arm = next(r for r in node['arms'] if r['run'] == run)
        if (done['binding']['node_binding_sha256'] != sha256(root/'node_binding.json')
            or done['binding']['parameters'] != arm['parameters']
            or done['binding'] != read_json(root/'runs'/run/'run_binding.json')):
            raise ValueError('completed run differs from arm/node binding')
        config, seed = run.rsplit('_s',1)
        for name in node['instruments']:
            pred = root/'predictions'/f'{run}_{name}.jsonl'; rec = read_json(pred.with_suffix('.receipt.json'))
            if sha256(pred) != rec['predictions_sha256']: raise ValueError('prediction hash mismatch')
            if rec['binding']['checkpoint_sha256'] != done['checkpoint_hashes']['best.pt']:
                raise ValueError('prediction checkpoint mismatch')
            if (rec['binding']['mix_sha256'] != sha256(node['instruments'][name])
                or rec['binding']['codec_sha256'] != sha256(arm['parameters']['codec'])
                or rec['binding']['provenance_sha256'] != done['provenance_sha256']):
                raise ValueError('prediction data/codec/provenance mismatch')
            check_files(rec['crop_hashes'])
            raw = list(read_rows(pred))
            if len(raw) != rec['result']['n_lines'] or any(r['arm'] != config or r['seed'] != int(seed) or r['instrument'] != name for r in raw):
                raise ValueError('prediction population identity mismatch')
            reference_population = sorted((r['line_id'], r['gt'], sha256(r['crop_path'])) for r in raw)
            if name in populations and populations[name] != reference_population: raise ValueError('different evaluation populations')
            populations[name] = reference_population
            rows = e3.joined_rows(raw, a.prep, name.removesuffix('_full_coverage')) if name.removesuffix('_full_coverage') in e3.INSTRUMENTS[:2] else [clean_row(r) for r in raw]
            result = summarize(rows)
            result['by_source_script_class'] = {c:metric([r for r in rows if r.get('source_script_class',r['script_class']) == c])
                for c in sorted({r.get('source_script_class',r['script_class']) for r in rows})}
            result['by_wave'] = {w:metric([r for r in rows if r.get('wave','unknown') == w]) for w in sorted({r.get('wave','unknown') for r in rows})}
            result['changed_label'] = changed_slice(rows, node['versions']) if name in ('v2_test', 'v2_test_full_coverage') else None
            results[run+'/'+name] = result
            overall_values[name][config][seed] = result['overall']['cer']
            if name in ('v2_test', 'v2_test_full_coverage'):
                for cls, m in result['by_source_script_class'].items():
                    if m['lines']: class_values[name][config].setdefault(cls,{})[seed] = m['cer']
            sources[str(pred)] = sha256(pred); sources[str(pred.with_suffix('.receipt.json'))] = sha256(pred.with_suffix('.receipt.json'))
    a.out.mkdir(parents=True, exist_ok=True)
    expected = {'ctrl_s0','lc_s0'} if a.smoke else set(sum(JOBS.values(), []))
    def seed_summary(values):
        finite = [v for v in values.values() if v is not None]
        return dict(seeds=values, n_seeds=len(values), complete=set(values) == {'0','1','2'},
            mean=sum(finite)/len(finite) if finite else None, min=min(finite) if finite else None,
            max=max(finite) if finite else None, range=max(finite)-min(finite) if finite else None)
    obj = dict(schema='e4-wave1c-report-v1', mode=common['mode'], control='retrain', identity=common,
        complete=set(roots) == expected, missing=sorted(expected-set(roots)), results=results,
        aggregate={i:{c:seed_summary(v) for c,v in groups.items()} for i,groups in overall_values.items()},
        class_aggregate={i:{c:{cls:seed_summary(v) for cls,v in classes.items()} for c,classes in groups.items()}
                         for i,groups in class_values.items()},
        verdicts={view:verdict(values.get('ctrl',{}), values.get('lc',{}), common['corrected_classes'], mode=common['mode']) for view,values in class_values.items()},
        sources=sources, metric='strict literal NFD codepoint CER',
        primary='v2_test_full_coverage; original references, paired changed-label slice also reported')
    atomic_json(a.out/'report.json', obj)
    (a.out/'REPORT.md').write_text('# E4 wave 1c\n\n'+obj['mode']+'\n\n'+json.dumps(obj['verdicts'],ensure_ascii=False)+'\n\nCustody: completed checkpoints, prediction/checkpoint identity, prediction files, crops, immutable code/data/label bindings and equal evaluation populations are hash checked. Original references remain visible; the changed-label slice scores the identical predictions twice.\n')
    return obj


def worker(a, gpu):
    node = verify(a)
    for arm in node['arms']:
        if arm['run'] not in a.runs.split(','): continue
        e3.run_arm(a, arm, gpu); evaluate_arm(a, arm)


def run_stage(a):
    if not os.environ.get('SLURM_JOB_ID'): raise ValueError('compute stage requires Slurm')
    node = prepare(a)
    if a.stage == 'preflight':
        # Exercise the unchanged widest-batch forward/backward/checkpoint path at width x2.
        original_rows = base.ROWS
        try:
            if a.smoke: base.ROWS = 20
            for arm in node['arms']:
                base.preflight_worker(a, arm['run'])
        finally:
            base.ROWS = original_rows
        atomic_json(a.out/'PREFLIGHT_DONE.json', dict(state='DONE', mode=node['mode'], inputs=node['inputs']))
    elif a.stage == 'runs':
        gate = a.run_root/'preflight/PREFLIGHT_DONE.json'
        pre = read_json(gate)
        if pre['state'] != 'DONE' or pre['mode'] != node['mode']: raise ValueError('fresh matching preflight required')
        check_files(pre['inputs'])
        groups = [node['arms']] if a.smoke else [[arm] for arm in node['arms']]
        procs = []
        for gpu, arms in enumerate(groups):
            cmd = [sys.executable,'-u','-m','bench.e4_wave1c', *a.child_args,
                   '--worker',str(gpu),'--runs',','.join(r['run'] for r in arms)]
            log = (a.out/'logs'/f'worker_{gpu}.log').open('a')
            procs.append((subprocess.Popen(cmd,cwd=ROOT,env=e3.pinned_env(str(gpu)),stdout=log,stderr=log),log))
        failed = []
        for proc, log in procs:
            if proc.wait(): failed.append(proc.returncode)
            log.close()
        if failed: raise ValueError('training/readout worker failed')
        report(a, {r['run']:a.out for r in node['arms']})
    else: raise ValueError('unknown compute stage')
    outputs = files_binding([p for p in a.out.rglob('*') if p.is_file() and p.name not in ('SMOKE_DONE.json','COMPLETE.json') and 'logs' not in p.parts])
    atomic_json(a.out/('SMOKE_DONE.json' if a.smoke else 'COMPLETE.json'),dict(state='DONE', mode=node['mode'],
        job_id=os.environ['SLURM_JOB_ID'], job=a.job, node_binding_sha256=sha256(a.out/'node_binding.json'), outputs=outputs))


def aggregate(a):
    roots, failures = {}, {}
    for job in (['job01'] if a.smoke else JOBS):
        root = a.run_root/job; marker = root/('SMOKE_DONE.json' if a.smoke else 'COMPLETE.json')
        if not marker.exists(): failures[job] = 'missing completion receipt'; continue
        done = read_json(marker)
        if done['state'] != 'DONE' or done['mode'] != ('SMOKE' if a.smoke else 'PRODUCTION') or done['node_binding_sha256'] != sha256(root/'node_binding.json'):
            raise ValueError('aggregate completion mismatch')
        check_files(done['outputs'])
        for arm in read_json(root/'arms.json'):
            if arm['run'] in roots: raise ValueError('duplicate aggregate run')
            roots[arm['run']] = root
    result = report(a, roots) if roots else dict(complete=False, verdicts={})
    atomic_json(a.out/'aggregate_status.json',dict(state='DONE' if result['complete'] and not failures else 'PARTIAL', failures=failures))
    if a.smoke and (failures or not result['complete']): raise ValueError('incomplete smoke aggregate')
    atomic_json(a.out/('SMOKE_DONE.json' if a.smoke else 'E4_AGGREGATE_COMPLETE.json'),dict(state='DONE' if result['complete'] and not failures else 'PARTIAL',
        mode='SMOKE' if a.smoke else 'PRODUCTION', job_id=os.environ.get('SLURM_JOB_ID'),job='aggregate',
        outputs=files_binding([a.out/'report.json',a.out/'REPORT.md',a.out/'aggregate_status.json'])))


def mock(out):
    """20 draws per arm, 10 real + 10 fixed synthetic; both fixture versions."""
    path = ROOT/'labels/mock/VERSIONS.json'
    codec = load_codec(str(ROOT/'codec/v2.json')); ids = {c:i for i,c in enumerate(codec.atom_by_id) if c}
    groups = [[dict(line_id=f'mock-{i:03d}', label_ids=[ids['α']], image_png=b'mock pixels', width=64,
                   script_class='greek_poly', source_dataset='mock_wave', split='train') for i in range(10)],
              [dict(line_id='synthetic-fixed', label_ids=[ids['α']], image_png=b'synthetic pixels', width=64,
                    script_class='greek_poly', source_dataset='synthetic', split='train')]]
    mix = dict(components=[dict(kind='real',fraction=.5),dict(kind='synthetic',fraction=.5)],seed=20261015)
    results = {}
    for version in ('stub','synthetic50'):
        spec = overlay_spec(path,[version],ROOT/'codec/v2.json',production=False)
        fixed, stats = substitute(groups,mix['components'],spec)
        contract = draw_contract(groups,fixed,mix,out/version/'draws',rows=20,epochs=1)
        preds = [dict(line_id=f'mock-{i:03d}',gt='α',prediction='β') for i in range(10)]
        results[version] = dict(mode='MOCK_ONLY',rows_per_arm=20,substitution=stats,contract=contract,
                               changed_label=changed_slice(preds,spec),verdict='MOCK_ONLY')
    atomic_json(out/'mock.json',results)
    print('E4_WAVE1C_MOCK',results['synthetic50']['substitution']['rows_substituted'])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mock',action='store_true'); ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--stage',choices=('prepare','preflight','runs','aggregate'),default='prepare')
    ap.add_argument('--root',type=Path,default=ROOT); ap.add_argument('--out',type=Path)
    ap.add_argument('--run-root',type=Path); ap.add_argument('--prep',type=Path)
    ap.add_argument('--campaign',type=Path); ap.add_argument('--registry',type=Path,default=ROOT/'labels/VERSIONS.json')
    ap.add_argument('--versions',default=''); ap.add_argument('--job',choices=('preflight','job01','job02','aggregate'),default='preflight')
    ap.add_argument('--worker'); ap.add_argument('--runs')
    a = ap.parse_args(argv)
    a.registry = a.registry.resolve()
    a.run_root = (a.run_root or ROOT/('out/e4/wave1c_smoke' if a.smoke else 'out/e4/wave1c')).resolve()
    a.out = (a.out or a.run_root/a.job).resolve()
    a.prep = (a.prep or ROOT/'out/e3').resolve(); a.campaign = (a.campaign or ROOT/'out/e4/wave1b').resolve()
    if a.mock: return mock(a.out)
    if a.root.resolve() != ROOT: raise ValueError('E4_ROOT differs from executable source root')
    a.child_args = ['--root',str(ROOT),'--run-root',str(a.run_root),'--out',str(a.out),'--prep',str(a.prep),
        '--campaign',str(a.campaign),'--registry',str(a.registry),'--versions',a.versions,'--job',a.job,'--stage',a.stage]
    if a.smoke: a.child_args += ['--smoke']
    if a.worker is not None: return worker(a,a.worker)
    if a.stage == 'aggregate': return aggregate(a)
    if a.stage == 'prepare': return prepare(a)
    return run_stage(a)

if __name__ == '__main__': main()
