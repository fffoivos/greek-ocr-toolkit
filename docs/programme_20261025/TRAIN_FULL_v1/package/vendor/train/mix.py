"""Manifest-only data custody. Validation uses the standard library, never Torch/CUDA.

Paths are relative to the manifest. Synthetic recipes are hashed from HEAD blobs,
not the index or working copy. Real shard inventories must match exactly.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import re
import subprocess
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]


class MixError(ValueError):
    pass


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def git(repo, *args):
    try:
        return subprocess.check_output(['git', '-C', str(repo), *args], stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise MixError(f'git custody unavailable: {e.stderr.decode().strip()}') from e


def committed_recipes(repo=ROOT):
    exported = exported_source(repo)
    if exported is not None:
        return {digest: name for name, digest in exported['recipes'].items()}
    # ls-files identifies eligible paths; cat-file binds their COMMITTED HEAD blobs.
    result = {}
    for name in git(repo, 'ls-files', '-z', 'factory/*.json').decode().split('\0'):
        if not name:
            continue
        try:
            blob = git(repo, 'cat-file', 'blob', f'HEAD:{name}')
            obj = json.loads(blob)
        except (MixError, ValueError):
            continue  # staged-only, deleted-at-HEAD, or not recipe JSON
        if isinstance(obj, dict) and 'content_marginals' in obj and 'target_total' in obj:
            result[hashlib.sha256(blob).hexdigest()] = name
    return result


def exported_source(repo=ROOT):
    """Opt-in git-free wave1c deployment; recipe hashes come from its manifest."""
    import os
    root = Path(repo).resolve()
    if (root/'.git').exists() or os.environ.get('E4_ROOT') != str(root):
        return None
    receipt = _object(root/'DEPLOY_RECEIPT.json')
    manifest = root/receipt.get('manifest_path', 'out/e4/wave1c_prep/DEPLOY_SHA256.txt')
    if not manifest.resolve().is_relative_to(root):
        raise MixError('deployment manifest escapes root')
    if (receipt.get('state') != 'DEPLOYED' or receipt.get('root') != str(root)
        or not re.fullmatch('[0-9a-f]{40}', receipt.get('commit', ''))
        or receipt.get('manifest_sha256') != sha256(manifest)):
        raise MixError('invalid E4 deployment source receipt')
    recipes = {}
    for line in manifest.read_text().splitlines():
        digest, name = line.split('  ', 1)
        p = Path(name)
        if p.parent == Path('factory') and p.suffix == '.json':
            if sha256(root/p) != digest:
                raise MixError('changed exported recipe: '+name)
            obj = _object(root/p)
            if 'content_marginals' in obj and 'target_total' in obj:
                recipes[name] = digest
    if not recipes:
        raise MixError('no manifest-bound exported recipes')
    return dict(commit=receipt['commit'], recipes=recipes)


def source_head(repo=ROOT):
    exported = exported_source(repo)
    return exported['commit'] if exported is not None else git(repo, 'rev-parse', 'HEAD').decode().strip()


def shard_inventory(directory):
    return {str(p.relative_to(directory)): sha256(p)
            for p in sorted(Path(directory).rglob('shard-*.parquet'))}


def _object(path):
    try:
        obj = json.loads(Path(path).read_text())
    except (OSError, ValueError) as e:
        raise MixError(f'{path}: cannot read JSON: {e}') from e
    if not isinstance(obj, dict):
        raise MixError(f'{path}: expected an object')
    return obj


def _path(base, value, field):
    if not isinstance(value, str) or not value.strip():
        raise MixError(f'{field}: required nonempty path')
    return (base / value).resolve()


def validate_metadata(path, *, repo=ROOT, role='train'):
    """Resolve all mix metadata; enumerate shard paths without reading their bytes.

    Full shard digests remain the responsibility of validate() in compute jobs.
    This shared path includes checks that used to follow shard hashing.
    """
    path = Path(path).resolve()
    if role not in ('train', 'val', 'eval', 'transfer', 'reserved', 'test'):
        raise MixError(f'unknown mix role: {role}')
    mix = _object(path)
    required = {'components', 'seed', 'codec_version', 'created_by', 'notes'}
    allowed = required | {'schema_version', 'matched_replay', 'codec_recovery', 'label_versions', 's1_selection'}
    if required - mix.keys() or mix.keys() - allowed:
        raise MixError(f'mix fields: missing={sorted(required-mix.keys())}, unknown={sorted(mix.keys()-allowed)}')
    if mix.get('schema_version', 1) != 1:
        raise MixError('unsupported mix schema_version (expected 1)')
    if type(mix['seed']) is not int or mix['seed'] < 0:
        raise MixError('seed must be a nonnegative integer')
    for key in ('codec_version', 'created_by'):
        if not isinstance(mix[key], str) or not mix[key].strip():
            raise MixError(f'{key} must be a nonempty string')
    if not isinstance(mix['notes'], str):
        raise MixError('notes must be a string')
    components = mix['components']
    if not isinstance(components, list) or not components:
        raise MixError('components must be a nonempty list')
    recipes = committed_recipes(repo)
    resolved = copy.deepcopy(mix)
    fractions = []
    for i, c in enumerate(components):
        prefix = f'component {i}'
        if not isinstance(c, dict):
            raise MixError(f'{prefix}: expected an object')
        fraction = c.get('fraction')
        if type(fraction) not in (int, float) or not math.isfinite(fraction) or not 0 <= fraction <= 1:
            raise MixError(f'{prefix}: fraction must be finite and in [0,1]')
        fractions.append(fraction)
        if c.get('kind') == 'synthetic':
            fields = {'kind', 'build_dir', 'recipe_sha256', 'fraction'}
            if set(c) != fields:
                raise MixError(f'{prefix}: synthetic fields must be {sorted(fields)}')
            directory = _path(path.parent, c['build_dir'], f'{prefix}.build_dir')
            info = _object(directory / 'build_info.json')
            digest = c['recipe_sha256']
            if not isinstance(digest, str) or digest not in recipes:
                raise MixError(f'{prefix}: recipe_sha256 is not a git-tracked recipe blob at HEAD')
            if info.get('recipe_sha256') != digest:
                raise MixError(f'{prefix}: build_info recipe_sha256 mismatch')
            if info.get('audit_ok') is not True:
                raise MixError(f'{prefix}: audit_ok must be true')
            if info.get('kind', 'synthetic') != 'synthetic':
                raise MixError(f'{prefix}: synthetic component refers to a non-synthetic build')
            if info.get('codec_version') != mix['codec_version']:
                raise MixError(f'{prefix}: build codec_version mismatch')
            # New factory builds bind the files as well as the recipe. Grandfathered O5
            # directories cannot gain custody just by acquiring a committed recipe hash.
            hashes = info.get('shard_sha256')
            resolved['components'][i]['build_dir'] = str(directory)
        elif c.get('kind') == 'legacy_eval':
            fields = {'kind', 'shard_dir', 'shard_sha256', 'recipe_sha256',
                      'role', 'provenance_status', 'disclosure', 'fraction'}
            if set(c) != fields:
                raise MixError(f'{prefix}: legacy_eval fields must be {sorted(fields)}')
            if role in ('train', 'val') or c['role'] not in ('eval', 'transfer'):
                raise MixError(f'{prefix}: legacy_eval is eval/transfer-only; forbidden in train/val')
            if c['provenance_status'] != 'unprovenanced_recipe':
                raise MixError(f'{prefix}: legacy_eval requires provenance_status unprovenanced_recipe')
            if not isinstance(c['disclosure'], str) or not c['disclosure'].strip():
                raise MixError(f'{prefix}: legacy_eval requires a nonempty disclosure')
            directory = _path(path.parent, c['shard_dir'], f'{prefix}.shard_dir')
            info = _object(directory / 'build_info.json')
            digest = c['recipe_sha256']
            if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
                raise MixError(f'{prefix}: legacy_eval recipe_sha256 must be a SHA-256')
            if info.get('recipe_sha256') != digest:
                raise MixError(f'{prefix}: legacy_eval build_info recipe_sha256 mismatch')
            if info.get('codec_version') != mix['codec_version']:
                raise MixError(f'{prefix}: legacy_eval codec_version mismatch')
            hashes = c['shard_sha256']
            resolved['components'][i]['shard_dir'] = str(directory)
        elif c.get('kind') == 'real':
            fields = {'kind', 'shard_dir', 'shard_sha256', 'partition_id', 'source', 'fraction'}
            if set(c) != fields:
                raise MixError(f'{prefix}: real fields must be {sorted(fields)}')
            for key in ('partition_id', 'source'):
                if not isinstance(c[key], str) or not c[key].strip():
                    raise MixError(f'{prefix}: {key} is required')
            directory = _path(path.parent, c['shard_dir'], f'{prefix}.shard_dir')
            hashes = c['shard_sha256']
            # P1: real data must have factory import custody, not a loose ad-hoc writer.
            info = _object(directory / 'build_info.json')
            if info.get('kind') != 'real' or info.get('partition_id') != c['partition_id']:
                raise MixError(f'{prefix}: real import kind/partition_id mismatch')
            if info.get('codec_version') != mix['codec_version']:
                raise MixError(f'{prefix}: real codec_version mismatch')
            if info.get('shard_sha256') != hashes:
                raise MixError(f'{prefix}: real import shard_sha256 mismatch')
            resolved['components'][i]['shard_dir'] = str(directory)
        else:
            raise MixError(f'{prefix}: unknown kind {c.get("kind")!r}')
        if not isinstance(hashes, dict) or not hashes:
            raise MixError(f'{prefix}: nonempty shard_sha256 inventory required')
        actual = {str(p.relative_to(directory)) for p in directory.rglob('shard-*.parquet')}
        if actual != set(hashes):
            raise MixError(f'{prefix}: shard hash mismatch or inventory mismatch in {directory}')
        # Retain the exact identities that passed custody validation, for both kinds.
        resolved['components'][i]['shard_sha256'] = copy.deepcopy(hashes)
        resolved['components'][i]['build_info_sha256'] = sha256(directory / 'build_info.json')
    if abs(math.fsum(fractions) - 1.0) > 1e-6:
        raise MixError(f'fractions sum to {math.fsum(fractions):.12g}, expected 1 (±1e-6)')
    if 'codec_recovery' in mix:
        if 'matched_replay' in mix or mix['codec_version'] != 'v2':
            raise MixError('codec recovery requires v2 without matched replay')
        spec = mix['codec_recovery']
        if not isinstance(spec, dict) or set(spec) != {'path', 'sha256'}:
            raise MixError('codec_recovery requires path and sha256')
        resolved['codec_recovery']['path'] = str(_path(path.parent, spec['path'], 'codec_recovery.path'))
        from bench.e4_recovery import load
        plan = load(resolved['codec_recovery'])
        if plan['seed'] != mix['seed'] or len(plan['old_counts']) != len(components):
            raise MixError('codec recovery component/seed mismatch')
    if 'matched_replay' in mix:
        spec = mix['matched_replay']
        if not isinstance(spec, dict) or set(spec) != {'path', 'sha256'}:
            raise MixError('matched_replay requires path and sha256')
        resolved['matched_replay']['path'] = str(_path(path.parent, spec['path'], 'matched_replay.path'))
        plan = replay_plan(resolved['matched_replay'])
        if (plan['replay_component'] != len(components)-1 or plan['base_components'] != len(components)-1
                or plan['seed'] != mix['seed'] or components[-1]['kind'] != 'real'
                or abs(components[-1]['fraction']-.1) > 1e-9):
            raise MixError('matched replay component/seed contract mismatch')
        expected = [c['fraction'] / .8 if c['kind'] == 'real' else c['fraction'] for c in components[:-1]]
        if plan['base_fractions'] != expected:
            # Accept only floating point rounding at the .8 inverse.
            if len(expected) != len(plan['base_fractions']) or any(abs(x-y)>1e-12 for x,y in zip(expected,plan['base_fractions'])):
                raise MixError('matched replay base fractions mismatch')
    if 'label_versions' in mix:
        if role != 'train' or mix['codec_version'] not in ('v2', 'v2.1'):
            raise MixError('label_versions is a v2/v2.1 train-only overlay')
        from bench.e4_wave1c import check_overlay
        spec = copy.deepcopy(mix['label_versions'])
        for key in ('registry', 'codec'):
            spec[key] = str(_path(path.parent, spec[key], 'label_versions.' + key))
        check_overlay(spec)
        resolved['label_versions'] = spec
    if 's1_selection' in mix:
        if role != 'train' or mix['codec_version'] != 'v2.1' or any(k in mix for k in ('matched_replay','codec_recovery','label_versions')):
            raise MixError('s1_selection requires raw v2.1 train pools')
        selection = mix['s1_selection']
        if set(selection) != {'subset','provenance'} or set(selection['subset']) != {'path','sha256','rows'}:
            raise MixError('invalid s1_selection schema')
        resolved['s1_selection']['subset']['path'] = str(_path(path.parent, selection['subset']['path'], 's1 subset'))
    return resolved


def validate(path, *, repo=ROOT, role='train'):
    """Validate metadata and full shard bytes. Jobs retain full custody checks."""
    resolved = validate_metadata(path, repo=repo, role=role)
    for i, c in enumerate(resolved['components']):
        directory = Path(c.get('build_dir', c.get('shard_dir')))
        if shard_inventory(directory) != c['shard_sha256']:
            raise MixError(f'component {i}: shard hash mismatch or inventory mismatch in {directory}')
    return resolved


def replay_plan(spec):
    import gzip
    path = Path(spec['path'])
    if sha256(path) != spec['sha256']:
        raise MixError('matched replay draw manifest hash mismatch')
    with gzip.open(path, 'rt') as f:
        plan = json.load(f)
    if plan.get('schema') != 'e4-matched-replay-v1':
        raise MixError('unsupported matched replay draw schema')
    return plan


def build(components, out, *, seed, codec_version, created_by, notes='', repo=ROOT, role='train'):
    """Bind a component specification to factory receipts and current shard bytes."""
    components = copy.deepcopy(components)
    base = Path(out).resolve().parent
    for c in components:
        directory = _path(base, c.get('build_dir') if c.get('kind') == 'synthetic'
                          else c.get('shard_dir'), 'component directory')
        info = _object(directory / 'build_info.json')
        if c.get('kind') == 'synthetic':
            c['recipe_sha256'] = info.get('recipe_sha256')
        elif c.get('kind') == 'legacy_eval':
            c['shard_sha256'] = shard_inventory(directory)
            c['recipe_sha256'] = info.get('recipe_sha256')
        else:
            c['shard_sha256'] = shard_inventory(directory)
            c.setdefault('partition_id', info.get('partition_id'))
    mix = dict(schema_version=1, components=components, seed=seed,
               codec_version=codec_version, created_by=created_by, notes=notes)
    # Validate a candidate before publishing. Never leave an invalid requested manifest.
    candidate = Path(out).with_name(Path(out).name + '.candidate')
    if candidate.exists():
        raise MixError(f'candidate already exists: {candidate}')
    try:
        candidate.write_text(json.dumps(mix, indent=2, ensure_ascii=False) + '\n')
        validate(candidate, repo=repo, role=role)
        candidate.replace(out)
    finally:
        candidate.unlink(missing_ok=True)
    return mix


def load_rows(mix, split):
    """Load all contract rows for one role. Never silently accept a wrong directory role."""
    import pyarrow.parquet as pq
    groups = []
    for i, c in enumerate(mix['components']):
        root = Path(c.get('build_dir', c.get('shard_dir', '')))
        directory = root / split
        rows = []
        if c['kind'] == 'legacy_eval':
            if split not in ('reserved', 'eval', 'transfer', 'test'):
                raise MixError(f'component {i}: legacy_eval is eval/transfer-only; forbidden in train/val')
            directory = root  # Historical receipt and reserved shards live together.
        row_split = 'reserved' if c['kind'] == 'legacy_eval' else split
        if split in ('train', 'val') and _object(root / 'build_info.json').get('eval_only') is True:
            raise MixError(f'component {i}: eval-only factory build cannot be used for {split}')
        for p in sorted(directory.glob('shard-*.parquet')):
            chunk = pq.read_table(p).to_pylist()
            if any(r['split'] != row_split or r['codec_version'] != mix['codec_version'] for r in chunk):
                raise MixError(f'component {i} {p}: split/codec mismatch')
            rows.extend(chunk)
        if c['fraction'] > 0 and not rows:
            raise MixError(f'component {i}: no {split} rows')
        groups.append(rows)
    if 's1_selection' in mix:
        if split != 'train': raise MixError('S1 selection is train-only')
        from bench.s1_scaling import select_rows
        groups = select_rows(groups, mix['components'], mix['s1_selection'])
    if 'label_versions' in mix and split == 'train':
        from bench.e4_wave1c import substitute
        groups, _ = substitute(groups, mix['components'], mix['label_versions'])
    return groups


def assemble(groups, fractions, seed, epoch=0, max_rows=None, *, exact_rows=False, replay=None, recovery=None):
    """Weighted concatenation: N=sum(active pool sizes); largest-remainder quotas.

    Shuffle each pool using (seed, epoch, component), take its quota, cycling new
    permutations when oversampling. Pool membership is redrawn each training epoch.
    """
    if recovery is not None:
        if replay is not None:raise MixError('cannot combine replay and codec recovery')
        from bench.e4_recovery import substitute
        return substitute(groups, fractions, seed, epoch, max_rows, exact_rows, recovery)
    if replay is not None:
        from bench.e4_replay import apply_plan
        plan = replay_plan(replay)
        if (seed != plan['seed'] or max_rows != plan['epoch_rows'] or not exact_rows
                or str(epoch) not in plan['epochs'] or len(groups) != plan['base_components']+1):
            raise MixError('matched replay requires its exact seed, epoch, pool count and row budget')
        rows, _ = assemble(groups[:-1], plan['base_fractions'], seed, epoch, max_rows, exact_rows=True)
        rows = apply_plan(rows, groups[-1], plan['epochs'][str(epoch)], plan['replay_component'],plan['scanned_components'])
        return rows, [sum(r['_component']==i for r in rows) for i in range(len(groups))]
    n = sum(len(g) for g, f in zip(groups, fractions) if f > 0)
    if max_rows is not None:
        n = max_rows if exact_rows else min(n, max_rows)
    if n < 1:
        raise MixError('assembled set is empty')
    exact = [n * f / math.fsum(fractions) for f in fractions]
    counts = [math.floor(x) for x in exact]
    for i in sorted(range(len(counts)), key=lambda i: (-(exact[i]-counts[i]), i))[:n-sum(counts)]:
        counts[i] += 1
    rows = []
    for i, (group, count) in enumerate(zip(groups, counts)):
        if count and not group:
            raise MixError(f'component {i}: positive quota on empty pool')
        rng = random.Random(f'{seed}:{epoch}:{i}')
        chosen = []
        while len(chosen) < count:
            indices = list(range(len(group)))
            rng.shuffle(indices)
            chosen.extend(indices[:count-len(chosen)])
        rows.extend(dict(group[j], _component=i, _pool_index=j) for j in chosen)
    return rows, counts


def marginals(rows):
    fields = ('script_class', 'severity', 'bg_type', 'polarity', 'font')
    result = {field: dict(sorted(Counter(str(r[field]) for r in rows).items())) for field in fields}
    result['width_buckets'] = dict(sorted(Counter(str(((r['width']+127)//128)*128) for r in rows).items(), key=lambda x: int(x[0])))
    return {'n_rows': len(rows), 'counts': result,
            'fractions': {k: {v: n/len(rows) for v, n in vals.items()} for k, vals in result.items()}}


def disclose_numbers(value, disclosure):
    """Attach legacy provenance at every object containing numeric readout values."""
    if isinstance(value, dict):
        for child in list(value.values()):
            disclose_numbers(child, disclosure)
        if any(type(child) in (int, float) for child in value.values()):
            value['provenance_status'] = 'unprovenanced_recipe'
            value['disclosure'] = disclosure
    elif isinstance(value, list):
        for child in value:
            disclose_numbers(child, disclosure)


def provenance(path, mix, assembled, *, repo=ROOT):
    report = {'schema_version': 1, 'mix': _object(path), 'mix_sha256': sha256(path),
            'resolved_mix': mix,
            'git_head': source_head(repo),
            'recipe_sha256s': sorted({c['recipe_sha256'] for c in mix['components'] if c['kind']=='synthetic'}),
            'sampling': ('expanded old plus recovered pools at fixed original component/class/source quotas; seeded shuffled cycles' if 'codec_recovery' in mix else 'exact matched substitutions; ordered draw digests; unchanged base draws' if 'matched_replay' in mix else 'per-epoch weighted concatenation; largest-remainder quotas; shuffled pool cycles; seed:epoch:component'),
            'epochs': {str(epoch): {role: {'marginals': marginals(rows),
                                         'component_counts': {str(i): sum(r['_component']==i for r in rows) for i in range(len(mix['components']))}}
                                    for role, rows in roles.items()} for epoch, roles in assembled.items()}}
    disclosures = {str(i): {'provenance_status': c['provenance_status'], 'disclosure': c['disclosure']}
                   for i, c in enumerate(mix['components']) if c['kind'] == 'legacy_eval'}
    if disclosures:
        report['legacy_eval_disclosures'] = disclosures
        for roles in report['epochs'].values():
            for stats in roles.values():
                stats['legacy_eval_disclosures'] = copy.deepcopy(disclosures)
                disclose_numbers(stats, '\n'.join(d['disclosure'] for d in disclosures.values()))
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    subs = ap.add_subparsers(dest='command', required=True)
    check = subs.add_parser('validate')
    check.add_argument('mix', type=Path)
    check.add_argument('--role', choices=('train', 'val', 'eval', 'transfer'), default='train')
    make = subs.add_parser('build')
    make.add_argument('--components', type=Path, required=True, help='JSON array; paths relative to output manifest')
    make.add_argument('--out', type=Path, required=True)
    make.add_argument('--seed', type=int, required=True)
    make.add_argument('--codec-version', required=True)
    make.add_argument('--created-by', required=True)
    make.add_argument('--notes', default='')
    make.add_argument('--role', choices=('train', 'val', 'eval', 'transfer'), default='train')
    a = ap.parse_args(argv)
    try:
        if a.command == 'validate':
            validate(a.mix, role=a.role)
            print(f'VALID: {a.mix}')
        else:
            build(json.loads(a.components.read_text()), a.out, seed=a.seed,
                  codec_version=a.codec_version, created_by=a.created_by, notes=a.notes, role=a.role)
            print(f'BUILT: {a.out}')
        return 0
    except (MixError, OSError, ValueError, TypeError) as e:
        print(f'mix validation failed: {e}', file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
