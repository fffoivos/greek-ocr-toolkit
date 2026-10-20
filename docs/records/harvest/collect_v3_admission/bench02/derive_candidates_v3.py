#!/usr/bin/env python3
"""Append BENCH02L quota fields without redrawing or rewriting existing JSON values."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEW_FIELDS = {'quota_scope', 'scope_rank', 'in_quota', 'overdraw_order'}
# Candidate tag names used by the recorded draw (not quota values).
SUBGROUP_TAGS = {'modern_cyrillic': 'cyrillic_language', 'font_extremes': 'font_size'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        assert key not in result, f'duplicate JSON member: {key}'
        result[key] = value
    return result


def decode(data):
    return json.loads(data, object_pairs_hook=unique_object)


def key(row):
    return row['parent_id'], row['row_id']


def scope_config(counts, plan):
    scopes = {}
    configured_subgroups = {}
    for split, classes in plan['subquotas'].items():
        for cl, subs in classes.items():
            assert f'{split}:{cl}' in counts['classes'], 'unknown subgroup class'
            configured_subgroups[f'{split}:{cl}'] = subs
    for base, record in counts['classes'].items():
        split, cl = base.split(':')
        quota = plan['quotas' if split == 'test' else 'dev_quotas'][cl]
        assert record['quota'] == quota, f'quota disagreement: {base}'
        subs = configured_subgroups.get(base, {})
        assert record['subgroup_quotas'] == subs, f'subquota disagreement: {base}'
        if subs:
            assert cl in SUBGROUP_TAGS, f'unknown subgroup tag: {cl}'
            assert sum(subs.values()) == quota, f'subquota sum: {base}'
            scopes.update({f'{base}:{sub}': q for sub, q in subs.items()})
        else:
            scopes[base] = quota
    return scopes, configured_subgroups


def validate(original, derived, counts, plan):
    """Assert identity, rank/quota rules, and exact accounting including subgroup gaps."""
    quotas, subgroups = scope_config(counts, plan)
    assert len({key(r) for r in original}) == len(original), 'duplicate row key'
    stripped = [{k: v for k, v in r.items() if k not in NEW_FIELDS} for r in derived]
    assert stripped == original, 'row order/set or existing values changed'
    assert len({key(r) for r in derived}) == len(derived), 'duplicate output key'
    grouped = defaultdict(list)
    classes = defaultdict(list)
    for row in derived:
        base = f"{row['split']}:{row['class']}"
        assert base in counts['classes'], f'unknown class: {base}'
        expected = base
        if subgroups.get(base):
            sub = row['tags'][SUBGROUP_TAGS[row['class']]]
            expected += ':' + sub
        assert row['quota_scope'] == expected and expected in quotas, 'invalid scope'
        grouped[expected].append(row)
        classes[base].append(row)
    for base, rows in classes.items():
        assert sorted(r['rank'] for r in rows) == list(range(1, len(rows) + 1)), f'invalid draw ranks: {base}'
    for scope, rows in grouped.items():
        for rank, row in enumerate(sorted(rows, key=lambda r: r['rank']), 1):
            expected_rank = rank if scope.count(':') == 2 else row['rank']
            assert type(row['scope_rank']) is int and row['scope_rank'] == expected_rank, 'scope rank'
            inside = expected_rank <= quotas[scope]
            assert type(row['in_quota']) is bool and row['in_quota'] == inside, 'in_quota rule'
            order = row['overdraw_order']
            assert (order is None if inside else type(order) is int and order == expected_rank - quotas[scope]), 'reserve order'
    scope_stats = {s: dict(quota=q, in_quota=sum(r['in_quota'] for r in grouped[s]),
                          reserve=sum(not r['in_quota'] for r in grouped[s])) for s, q in sorted(quotas.items())}
    class_stats = {}
    for base, record in counts['classes'].items():
        rows = classes[base]
        assert len(rows) == record['drawn'], f'drawn count: {base}'
        inside = sum(r['in_quota'] for r in rows)
        reserve = len(rows) - inside
        subs = subgroups.get(base)
        if subs:
            observed = Counter(r['tags'][SUBGROUP_TAGS[r['class']]] for r in rows)
            assert dict(observed) == record['subgroups'], f'subgroup counts: {base}'
            expected = sum(min(observed[s], q) for s, q in subs.items())
            # counts.json credited=min(drawn,class quota) can count subgroup reserves.
            assert record['credited'] == min(record['drawn'], record['quota']), f'credited formula: {base}'
            gap = record['credited'] - expected
            assert gap >= 0, f'negative subgroup gap: {base}'
        else:
            expected, gap = record['credited'], 0
        assert inside == expected, f'in-quota count: {base}'
        assert inside == record['credited'] - gap, f'credited reconciliation: {base}'
        assert reserve == record['drawn'] - record['credited'] + gap, f'reserve count: {base}'
        class_stats[base] = dict(in_quota=inside, reserve=reserve, credited=record['credited'], subgroup_gap=gap)
    return dict(scopes=scope_stats, classes=class_stats)


def derive(data, counts, plan):
    lines = data.splitlines()
    original = [decode(line) for line in lines]
    quotas, subgroups = scope_config(counts, plan)
    grouped = defaultdict(list)
    for index, row in enumerate(original):
        assert not NEW_FIELDS.intersection(row), 'derived fields already present'
        base = f"{row['split']}:{row['class']}"
        scope = base
        if subgroups.get(base):
            scope += ':' + row['tags'][SUBGROUP_TAGS[row['class']]]
        assert scope in quotas, f'unknown quota scope: {scope}'
        grouped[scope].append(index)
    additions = {}
    for scope, indices in grouped.items():
        for rank, index in enumerate(sorted(indices, key=lambda i: original[i]['rank']), 1):
            scope_rank = rank if scope.count(':') == 2 else original[index]['rank']
            inside = scope_rank <= quotas[scope]
            additions[index] = dict(quota_scope=scope, scope_rank=scope_rank,
                                    in_quota=inside, overdraw_order=None if inside else scope_rank - quotas[scope])
    output = []
    for index, line in enumerate(lines):
        raw = line.rstrip()
        assert raw.endswith(b'}'), 'candidate must be a JSON object'
        # Retain every byte of each existing member, including numeric spellings.
        extra = json.dumps(additions[index], ensure_ascii=False, separators=(',', ':')).encode()
        output.append(raw[:-1] + b',' + extra[1:] + b'\n')
    result = b''.join(output)
    summary = validate(original, [decode(line) for line in result.splitlines()], counts, plan)
    return result, summary


def receipt(data, result, summary, counts_bytes, plan_bytes):
    sha = lambda b: hashlib.sha256(b).hexdigest()
    lines = ['# BENCH02L candidates v3', '',
             f'- Output SHA-256: `{sha(result)}`', f'- Output bytes: {len(result)}',
             f'- Output lines: {len(result.splitlines())}', f'- Input SHA-256: `{sha(data)}`',
             f'- counts.json SHA-256: `{sha(counts_bytes)}`', f'- draw_plan.json SHA-256: `{sha(plan_bytes)}`', '',
             'Quotas come from counts.json classes and are cross-checked against draw_plan.json quotas, '
             'dev_quotas and subquotas. Subgroup quotas are cross-checked between both files. '
             'Subgroup tags are cyrillic_language for modern_cyrillic and font_size for font_extremes.', '',
             'quota_scope is split:class, extended with :subgroup for every recorded subgroup quota. '
             'For ordinary scopes, scope_rank is the original rank. For subgroup scopes, sort the class rows '
             'by original numeric rank, restrict to that subgroup, and number from 1. '
             'JSONL emission order is never used as draw rank. in_quota is scope_rank <= scope quota; '
             'overdraw_order is null in quota and scope_rank - scope quota otherwise. '
             'Reserve use follows increasing overdraw_order within scope; a replacement must also share '
             'split, class and source with the replaced row. No replacements are performed.', '',
             'Original JSON member bytes are retained; only four members are appended. '
             'Row keys are (parent_id, row_id). All scopes, including empty scopes, appear below.', '',
             '| Scope | Quota | In quota | Reserve |', '| --- | ---: | ---: | ---: |']
    for scope, stats in summary['scopes'].items():
        lines.append(f"| {scope} | {stats['quota']} | {stats['in_quota']} | {stats['reserve']} |")
    lines += ['', '| Split/class | Credited | In quota | Drawn - credited | Reserve | Subgroup gap |',
              '| --- | ---: | ---: | ---: | ---: | ---: |']
    for base, stats in summary['classes'].items():
        lines.append(f"| {base} | {stats['credited']} | {stats['in_quota']} | {stats['reserve'] - stats['subgroup_gap']} | {stats['reserve']} | {stats['subgroup_gap']} |")
    lines += ['', '| Split | Credited | In quota | Reserve | Subgroup gap |',
              '| --- | ---: | ---: | ---: | ---: |']
    for split in ('test', 'dev'):
        stats = [v for k, v in summary['classes'].items() if k.startswith(split + ':')]
        totals = [sum(v[field] for v in stats) for field in ('credited', 'in_quota', 'reserve', 'subgroup_gap')]
        lines.append('| ' + split + ' | ' + ' | '.join(map(str, totals)) + ' |')
    lines += ['', f"Scopes: {len(summary['scopes'])}; subgroup scopes: {sum(s.count(':') == 2 for s in summary['scopes'])}.", '', 'counts.json uses credited = min(drawn, class quota). For subgroup scopes the rule instead '
              'credits sum(min(subgroup drawn, subgroup quota)). The subgroup gap is the difference. '
              'Assertions require in_quota = credited - gap and reserve = drawn - credited + gap. '
              'Thus an unqualified in_quota = credited assertion is false wherever gap is nonzero; '
              'the input accounting is preserved.', '',
              'Verified: unique input/output row keys; unique JSON member names; identical row order, '
              'row set and existing values; contiguous original class ranks; scope ranks and reserve order; '
              'all class and subgroup counts; second independent derivation byte-identical; '
              'written output read back byte-identical; input files unchanged.', '']
    return '\n'.join(lines)


def run(directory):
    paths = [directory / name for name in ('candidates.jsonl', 'counts.json', 'draw_plan.json')]
    data, counts_bytes, plan_bytes = snapshots = [p.read_bytes() for p in paths]
    counts, plan = decode(counts_bytes), decode(plan_bytes)
    result, summary = derive(data, counts, plan)
    again, again_summary = derive(data, decode(counts_bytes), decode(plan_bytes))
    assert result == again and summary == again_summary, 'nondeterministic derivation'
    output = directory / 'candidates_v3.jsonl'
    output.write_bytes(result)
    assert output.read_bytes() == result, 'output readback'
    assert [p.read_bytes() for p in paths] == snapshots, 'input changed'
    (directory / 'CANDIDATES_V3.md').write_text(receipt(data, result, summary, counts_bytes, plan_bytes), encoding='utf-8')
    return result, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=HERE / 'census05')
    args = parser.parse_args()
    result, summary = run(args.directory)
    print(json.dumps(dict(lines=len(result.splitlines()), bytes=len(result), sha256=hashlib.sha256(result).hexdigest(),
                          **summary), sort_keys=True))


if __name__ == '__main__':
    main()
