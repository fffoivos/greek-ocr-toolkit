"""E4 fixed draw replay. All arms consume these exact indexed rows in the trainer."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import random

CATEGORIES = ('all_caps', 'numerics', 'mixed_script', 'punctuation_heavy', 'cyrillic', 'dotted_leaders')


def row_tags(row):
    from bench.line_categories import categories
    tags = set(categories(row)) & set(CATEGORIES)
    if row['script_class'] == 'cyrillic':
        tags.add('cyrillic')
    return tags


def row_weight(tags, multipliers):
    """Overlap rule: MAX, never product or sum. Untagged rows have weight one."""
    return max([1] + [multipliers.get(tag, 1) for tag in tags])


def quota(weights, n):
    """Integer largest remainder, stable mask tie order; no floating point."""
    denominator = sum(weights.values())
    if denominator <= 0:
        raise ValueError('empty weighted population')
    counts = {k: n*w//denominator for k, w in weights.items()}
    order = sorted(weights, key=lambda k: (-(n*weights[k] % denominator), k))
    for k in order[:n-sum(counts.values())]:
        counts[k] += 1
    return counts


def weighted_epoch(previous, pools, kinds, active, multiplier, seed, epoch):
    """Reweight the exact previous real DRAW measure, retaining synthetic slots.

    Apportion overlapping-tag mask strata by count * MAX(category multipliers),
    then seeded shuffled cycles of the previous occurrences within each stratum.
    Thus repeats retain their previous probability mass; no pool-uniform reset.
    """
    if multiplier not in (1, 2, 4):
        raise ValueError('unsupported multiplier')
    if multiplier == 1:
        return list(previous)
    strata = {}
    real_slots = []
    for position, (component, index, ident) in enumerate(previous):
        if kinds[component] != 'real':
            continue
        real_slots.append(position)
        mask = pools[component][index][1]
        strata.setdefault(mask, []).append((component, index, ident))
    weights = {mask: len(rows)*row_weight({name for j, name in enumerate(CATEGORIES) if mask & (1 << j)},
                                         {name: multiplier for name in active}) for mask, rows in strata.items()}
    counts = quota(weights, len(real_slots))
    chosen = []
    for mask, rows in sorted(strata.items()):
        rng = random.Random(f'{seed}:{epoch}:e4-1e:{mask}')
        sample = []
        while len(sample) < counts[mask]:
            cycle = list(rows)
            rng.shuffle(cycle)
            sample.extend(cycle[:counts[mask]-len(sample)])
        chosen.extend(sample)
    random.Random(f'{seed}:{epoch}:e4-1e:real-order').shuffle(chosen)
    result = list(previous)
    for position, row in zip(real_slots, chosen):
        result[position] = row
    return result


def encoded(row):
    return (json.dumps(row, separators=(',', ':'), ensure_ascii=True)+'\n').encode()


def identity(rows):
    h = hashlib.sha256()
    for row in rows:
        h.update(encoded(row))
    return h.hexdigest()


def save_epoch(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as raw, gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0, compresslevel=1) as sink:
        for row in rows:
            sink.write(encoded(row))


def read_epoch(path):
    with gzip.open(path, 'rt') as source:
        return [tuple(json.loads(line)) for line in source]


def load_plan(spec):
    from train.mix import sha256
    path = Path(spec['path'])
    if sha256(path) != spec['sha256']:
        raise ValueError('fixed draw plan changed')
    plan = json.loads(path.read_text())
    if plan.get('schema') != 'e4-fixed-draws-v1' or set(plan['epochs']) != set(map(str, range(1, 9))):
        raise ValueError('invalid fixed draw plan')
    for entry in plan['epochs'].values():
        p = Path(entry['path'])
        if p.is_absolute() or '..' in p.parts:
            raise ValueError('unsafe epoch path')
        if sha256(path.parent/p) != entry['sha256']:
            raise ValueError('fixed epoch draws changed')
    return plan


def apply_draws(groups, fractions, seed, epoch, max_rows, exact_rows, spec):
    from train.mix import sha256
    path = Path(spec['path'])
    # Recheck the plan and the selected epoch on every use, including resume.
    if sha256(path) != spec['sha256']:
        raise ValueError('fixed draw plan changed')
    plan = json.loads(path.read_text())
    if (plan['schema'] != 'e4-fixed-draws-v1' or seed != plan['seed'] or not exact_rows
            or max_rows != plan['epoch_rows'] or fractions != plan['fractions']
            or [len(g) for g in groups] != plan['pool_sizes'] or str(epoch) not in plan['epochs']):
        raise ValueError('fixed draw scope mismatch')
    entry = plan['epochs'][str(epoch)]
    target = Path(entry['path'])
    if target.is_absolute() or '..' in target.parts or sha256(path.parent/target) != entry['sha256']:
        raise ValueError('fixed epoch draws changed')
    indexed = read_epoch(path.parent/target)
    if len(indexed) != max_rows or identity(indexed) != entry['ordered_identity_sha256']:
        raise ValueError('fixed draw count/order mismatch')
    rows = []
    for c, i, ident in indexed:
        if type(c) is not int or type(i) is not int or not 0 <= c < len(groups) or not 0 <= i < len(groups[c]):
            raise ValueError('fixed draw index out of range')
        row = groups[c][i]
        if row['line_id'] != ident or row['split'] != 'train':
            raise ValueError('fixed draw identity/split mismatch')
        rows.append(dict(row, _component=c, _pool_index=i))
    counts = Counter(r['_component'] for r in rows)
    return rows, [counts[i] for i in range(len(groups))]
