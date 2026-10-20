#!/usr/bin/env python3
"""Score supplied reader outputs without running readers or estimating usage."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
BSB_FIELDS = ('letters', 'crop_ok', 'marks')
ALLOWED = {'letters': {'y','n','u'}, 'crop_ok': {'y','n','u'}, 'marks': {'y','n','na','u'}}
CALLS = {'ъ','ь','other','u'}


def load_rows(path):
    with Path(path).open() as f:
        return [json.loads(line) for line in f if line.strip()]


def index_rows(rows, bed):
    field = 'card_id' if bed == 'bsb' else 'item_id'
    result = {}
    for row in rows:
        iid = row.get(field)
        if not isinstance(iid, str) or not iid:
            raise ValueError(f'Missing {field}')
        if iid in result:
            raise ValueError(f'Duplicate {field}: {iid}')
        result[iid] = row
    return result


def validate_row(row, bed, expected_slots=None):
    if bed == 'bsb':
        for field in BSB_FIELDS:
            if row.get(field) not in ALLOWED[field]:
                raise ValueError(f'Invalid BSB {field}: {row.get(field)!r}')
    else:
        slots = row.get('slots')
        if not isinstance(slots, dict) or set(slots) != set(expected_slots):
            raise ValueError(f'Incorrect slot IDs for {row.get("item_id")}: {slots}')
        if any(call not in CALLS for call in slots.values()):
            raise ValueError('Invalid yer slot call')
        confidence = row.get('confidence', {})
        if not isinstance(confidence, dict) or not set(confidence) <= set(slots):
            raise ValueError('Confidence keys must name reported slots')
        if any(value not in {'high', 'low'} for value in confidence.values()):
            raise ValueError('Yer confidence must be high or low')


def agreement(left, right, truth, bed):
    """Missing outputs are explicit; equality never silently drops a field."""
    common = sorted(set(left) & set(right) & set(truth))
    result = {'expected_items': len(truth), 'compared_items': len(common),
              'missing_left_items': sorted(set(truth)-set(left)),
              'missing_right_items': sorted(set(truth)-set(right))}
    if bed == 'bsb':
        result['fields'] = {}
        for field in BSB_FIELDS:
            equal = sum(left[i][field] == right[i][field] for i in common)
            result['fields'][field] = {'agree': equal, 'disagree': len(common)-equal,
                                       'compared': len(common), 'expected': len(truth),
                                       'rate': equal/len(common) if common else None,
                                       'disagreement_ids': [i for i in common if left[i][field] != right[i][field]]}
        equal = sum(all(left[i][f] == right[i][f] for f in BSB_FIELDS) for i in common)
        result['all_fields_per_card'] = {'agree': equal, 'disagree': len(common)-equal,
                                         'compared': len(common), 'rate': equal/len(common) if common else None}
    else:
        expected = sum(len(v['slots']) for v in truth.values())
        units = [(i,s) for i in common for s in truth[i]['slots']]
        equal = sum(left[i]['slots'][s] == right[i]['slots'][s] for i,s in units)
        result['slots'] = {'agree': equal, 'disagree': len(units)-equal, 'compared': len(units),
                           'expected': expected, 'missing': expected-len(units),
                           'rate': equal/len(units) if units else None,
                           'disagreement_slots': [{'item_id': i, 'slot': s, 'left': left[i]['slots'][s], 'right': right[i]['slots'][s]} for i,s in units if left[i]['slots'][s] != right[i]['slots'][s]]}
        equal_items = sum(left[i]['slots'] == right[i]['slots'] for i in common)
        result['all_slots_per_item'] = {'agree': equal_items, 'disagree': len(common)-equal_items,
                                       'compared': len(common), 'zero_slot_items': sum(not truth[i]['slots'] for i in common),
                                       'rate': equal_items/len(common) if common else None}
    return result


def distribution(outputs, bed, truth):
    if bed == 'bsb':
        calls = {f: dict(sorted(Counter(r[f] for r in outputs.values()).items())) for f in BSB_FIELDS}
        unresolved = {f: sum(r[f] == 'u' for r in outputs.values()) for f in BSB_FIELDS}
        unresolved['cards_with_u'] = sum(any(r[f] == 'u' for f in BSB_FIELDS) for r in outputs.values())
    else:
        calls = dict(sorted(Counter(c for r in outputs.values() for c in r['slots'].values()).items()))
        unresolved = {'u': calls.get('u', 0), 'other': calls.get('other', 0),
                      'items_with_u_or_other': sum(any(v in {'u','other'} for v in r['slots'].values()) for r in outputs.values())}
    confidence = Counter()
    confidence_missing = 0
    for row in outputs.values():
        conf = row.get('confidence')
        if isinstance(conf, dict):
            confidence.update(str(v) for v in conf.values())
        elif conf is not None:
            confidence[str(conf)] += 1
        if bed == 'yer':
            confidence_missing += len(row['slots'])-len(conf or {})
    return {'calls': calls, 'unresolved': unresolved, 'confidence': dict(sorted(confidence.items())),
            'confidence_unreported_slots': confidence_missing if bed == 'yer' else None,
            'missing_items': sorted(set(truth)-set(outputs)),
            'missing_slots': sum(len(truth[i]['slots']) for i in set(truth)-set(outputs)) if bed == 'yer' else None}


def paired_quality(arm, baseline, truth, bed):
    common = sorted(set(arm) & set(baseline) & set(truth))
    fields = BSB_FIELDS if bed == 'bsb' else ('slots',)
    result = {}
    for field in fields:
        pairs = [(i,None) for i in common] if bed == 'bsb' else [(i,s) for i in common for s in truth[i]['slots']]
        counts = Counter({'better': 0, 'worse': 0, 'same_correct': 0, 'same_incorrect': 0})
        for iid, slot in pairs:
            a = arm[iid][field] if slot is None else arm[iid]['slots'][slot]
            b = baseline[iid][field] if slot is None else baseline[iid]['slots'][slot]
            t = truth[iid][field] if slot is None else truth[iid]['slots'][slot]
            counts['same_correct' if a == t and b == t else 'same_incorrect' if a != t and b != t else 'better' if a == t else 'worse'] += 1
        result[field] = {**counts, 'compared': len(pairs)}
    return result


def parse_usage(obj):
    if isinstance(obj, dict) and 'readers' not in obj:
        records = []
        for key, fields in obj.items():
            parts = key.split('/')
            if len(parts) != 3:
                raise ValueError('Usage mapping keys must be bed/arm/reader')
            records.append({'bed': parts[0], 'arm': parts[1], 'reader': parts[2], **fields})
    else:
        records = obj['readers'] if isinstance(obj, dict) else obj
    out = {}
    for record in records:
        key = (record['bed'], record['arm'], record['reader'])
        if key in out:
            raise ValueError(f'Duplicate usage reader: {key}')
        fields = {}
        for name in ('total_tokens', 'tool_uses', 'duration_ms'):
            value = record.get(name)
            if isinstance(value, bool) or not isinstance(value, (int,float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f'Usage {key}: {name} must be a nonnegative measured number')
            if name in ('total_tokens', 'tool_uses') and int(value) != value:
                raise ValueError(f'Usage {name} must be an integer')
            fields[name] = value
        out[key] = fields
    return out


def efficiency(packs, usage):
    per_reader = []
    for p in packs:
        key = (p['bed'], p['arm'], p['reader']); u = usage.get(key); n = p['items_per_reader']
        per_reader.append({'reader': p['reader'], 'assigned_items': n, 'usage_reported': u is not None,
                           **(u or {}), 'tokens_per_card': u['total_tokens']/n if u else None,
                           'reader_wall_ms_per_card': u['duration_ms']/n if u else None,
                           'tool_uses_per_card': u['tool_uses']/n if u else None})
    complete = all(r['usage_reported'] for r in per_reader)
    n = sum(p['items_per_reader'] for p in packs)
    measured = {field: sum(r.get(field,0) for r in per_reader) if complete else None for field in ('total_tokens','tool_uses','duration_ms')}
    return {'usage_complete': complete, 'assigned_items': n, 'readers': per_reader,
            'total_tokens': measured['total_tokens'], 'summed_reader_duration_ms': measured['duration_ms'],
            'total_tool_uses': measured['tool_uses'],
            'tokens_per_card': measured['total_tokens']/n if complete else None,
            'reader_wall_ms_per_card': measured['duration_ms']/n if complete else None,
            'tool_uses_per_card': measured['tool_uses']/n if complete else None,
            'wall_time_definition': 'sum of measured reader durations / assigned cards; concurrent makespan is unknown'}


def score(manifest, truth, submissions, usage=None, root=ROOT):
    usage = usage or {}
    assignments = {(p['bed'],p['arm'],p['reader']): p for p in manifest['packs']}
    if set(usage)-set(assignments):
        raise ValueError(f'Unknown usage readers: {set(usage)-set(assignments)}')
    merged = {}; seen = set(); readers_present = set()
    for bed, arm, reader, records in submissions:
        if bed == 'owner39':
            continue  # Independent repeated reads are scored separately below.
        key = (bed, arm, reader)
        if key not in assignments or key in seen:
            raise ValueError(f'Unknown or duplicate reader submission: {key}')
        seen.add(key); readers_present.add(key)
        indexed = index_rows(records, bed)
        unexpected = set(indexed)-set(assignments[key]['item_ids'])
        if unexpected:
            raise ValueError(f'IDs assigned to a different reader or unknown: {unexpected}')
        for iid, row in indexed.items():
            validate_row(row, bed, truth[bed][iid].get('slots'))
        arm_rows = merged.setdefault((bed,arm), {})
        if set(arm_rows) & set(indexed):
            raise ValueError('Item read more than once in an arm')
        arm_rows.update(indexed)
    result = {'schema_version': 1, 'beds': {},
              'interpretation': 'Descriptive experiment only. No automatic adoption or no-quality-loss claim. Unresolved calls are literal calls; missing outputs are reported separately. Usage is measured only.'}
    for bed in ('bsb','yer'):
        base = merged.get((bed,'E0a'), {}); repeat = merged.get((bed,'E0b'), {})
        variance = agreement(base, repeat, truth[bed], bed)
        result['beds'][bed] = {'E0a_E0b_agreement': variance, 'arms': {}}
        for arm in manifest['arms']:
            actual = merged.get((bed,arm), {}); packs = [p for p in manifest['packs'] if p['bed']==bed and p['arm']==arm]
            result['beds'][bed]['arms'][arm] = {
                'factor': manifest['arms'][arm], 'expected_readers': len(packs),
                'submitted_readers': sum((bed,arm,p['reader']) in readers_present for p in packs),
                'complete': set(actual)==set(truth[bed]),
                'agreement_with_truth': agreement(actual, truth[bed], truth[bed], bed),
                'agreement_with_E0a': agreement(actual, base, truth[bed], bed),
                'paired_quality_vs_E0a': paired_quality(actual, base, truth[bed], bed),
                **distribution(actual, bed, truth[bed]), 'efficiency': efficiency(packs, usage)}
    if any(p['bed']=='owner39' for p in manifest['packs']):
        from owner39_score import score_bed
        owner_truth = truth.get('owner39')
        if owner_truth is None:
            owner_truth = json.loads((Path(root)/manifest['owner39']['truth']).read_text())
        result['beds']['owner39'] = score_bed(manifest, owner_truth, submissions, usage, root, efficiency)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=ROOT/'MANIFEST.json')
    parser.add_argument('--truth', type=Path, default=ROOT/'keys/truth.json')
    parser.add_argument('--bsb-truth', type=Path, action='append', help='C1 reference JSONL; repeat for a and b')
    parser.add_argument('--yer-truth', type=Path, action='append', help='Ink reference JSONL; repeat for a and b')
    parser.add_argument('--yer-table', type=Path, help='Optional table.json cross-check of ink reference slots')
    parser.add_argument('--verdict', nargs=4, action='append', metavar=('BED','ARM','READER','PATH'), default=[])
    parser.add_argument('--verdicts', type=Path, help='JSON list (or {readers:[...]}) of bed/arm/reader/path records')
    parser.add_argument('--usage', type=Path)
    parser.add_argument('--output', type=Path, help='Otherwise write JSON to stdout')
    args = parser.parse_args(argv)
    manifest = json.loads(args.manifest.read_text()); truth = json.loads(args.truth.read_text())
    for bed, paths in (('bsb',args.bsb_truth),('yer',args.yer_truth)):
        if paths:
            override = index_rows([r for p in paths for r in load_rows(p)], bed)
            if set(override) != set(truth[bed]):
                raise ValueError(f'{bed} truth IDs do not match the fixed test bed')
            for iid,row in override.items():
                validate_row(row, bed, truth[bed][iid].get('slots'))
            # Optional external truth must match the build-bound fixed truth.
            for iid,row in override.items():
                fields = BSB_FIELDS if bed=='bsb' else ('slots',)
                if any(row[f] != truth[bed][iid][f] for f in fields):
                    raise ValueError(f'{bed}/{iid}: external truth differs from fixed build truth')
            truth[bed] = override
    if args.yer_table:
        import re
        table = json.loads(args.yer_table.read_text())
        if {r['item_id'] for r in table} != set(truth['yer']):
            raise ValueError('Yer table IDs differ from fixed truth')
        for row in table:
            slots = {}
            for value in row['slots']:
                m = re.fullmatch(r'(\d+):g=. ink=(ъ|ь|other|u) prior=.+', value)
                if not m:
                    raise ValueError('Unrecognized ink table slot')
                slots[m[1]] = m[2]
            if slots != truth['yer'][row['item_id']]['slots']:
                raise ValueError('Yer table and ink truth disagree')
    descriptors = list(args.verdict)
    if args.verdicts:
        obj = json.loads(args.verdicts.read_text()); records = obj['readers'] if isinstance(obj,dict) else obj
        for r in records:
            p = Path(r['path']); p = p if p.is_absolute() else args.verdicts.parent/p
            descriptors.append((r['bed'],r['arm'],r['reader'],p))
    submissions = [(b,a,r,load_rows(p)) for b,a,r,p in descriptors]
    usage = parse_usage(json.loads(args.usage.read_text())) if args.usage else {}
    output = score(manifest, truth, submissions, usage, args.manifest.parent)
    text = json.dumps(output, ensure_ascii=False, indent=2)+'\n'
    if args.output:
        if not args.output.resolve().is_relative_to(ROOT):
            raise ValueError('--output must stay under efficiency/')
        if args.output.resolve().is_relative_to(ROOT/'packs'):
            raise ValueError('Never put scoring results in reader packs')
        args.output.write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f'score: {exc}', file=sys.stderr)
        raise SystemExit(2)
