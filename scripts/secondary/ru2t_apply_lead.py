"""Apply RU2TF4 lead evidence offline; never launches readers or renders crops."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import ru2t as m
sys.path.insert(0, str(m.WORK))

LEAD = m.WORK / 'docs/records/labelfix/secondary/RU2T_LEAD_REVIEW.md'
INDEX = m.SCRATCH / 'ru1_review/ru2t/sheets_index.json'
RULINGS = {1: ('keep_soft', 'lead_ruling'), 2: ('hold', 'hold_yat'),
           3: ('edit_hard', 'lead_ruling'), 4: ('hold', 'hold_uncertain'),
           5: ('edit_hard', 'lead_ruling'), 6: ('edit_hard', 'lead_ruling')}


def apply_lead(decisions, index):
    """Require exact sheet/decision identity before applying the six fixed rulings."""
    result = deepcopy(decisions)
    lookup = {(d['row_id'], d['offset']): d for d in result}
    if len(lookup) != len(result):
        raise ValueError('duplicate decision position')
    items = index['items']
    if index['cells'] != len(items):
        raise ValueError('sheet count mismatch')
    review = [c for c in items if c['set'] == 'review']
    audit = [c for c in items if c['set'] == 'audit']
    if len(review) != 6 or {c['cell'] for c in review} != set(RULINGS):
        raise ValueError('expected review cells 1..6')
    if len(audit) != 30 or Counter(c['decision'] for c in audit) != {'edit_hard': 20, 'keep_soft': 10}:
        raise ValueError('expected 20 hard and 10 soft audit cells')
    seen = set()
    records = []
    for c in items:
        key = (c['row_id'], c['offset'])
        if key in seen or key not in lookup:
            raise ValueError('duplicate or unknown sheet position')
        seen.add(key)
        d = lookup[key]
        # Original sheet embeds the complete decision; verify all original fields.
        if any(c.get(k) != v for k, v in d.items()):
            raise ValueError('sheet/decision mismatch')
        prior = dict(decision=d['decision'], reason=d['reason'])
        if c['set'] == 'review':
            if d['decision'] != 'hold':
                raise ValueError('review position was not held')
            d['decision'], d['reason'] = RULINGS[c['cell']]
            d['basis'] = 'lead_ruling'
            d['lead_review_cell'] = c['cell']
            status = 'lead_ruling'
        elif c['set'] == 'audit':
            d['audit'] = 'lead_audit_confirmed'
            d['lead_audit_cell'] = c['cell']
            status = 'lead_audit_confirmed'
        else:
            raise ValueError('unknown sheet set')
        records.append(dict(set=c['set'], cell=c['cell'], row_id=key[0], offset=key[1],
                            previous=prior, decision=d['decision'], reason=d['reason'],
                            status=status, basis='lead_ruling', sheet=c['sheet'],
                            sheet_cell=c['sheet_cell']))
    if {k for k, d in lookup.items() if d['decision'] == 'hold'} != {
            (c['row_id'], c['offset']) for c in review if c['cell'] in (2, 4)}:
        raise ValueError('unexpected remaining hold')
    for d in result:
        if d['decision'] == 'edit_hard':
            d.setdefault('basis', 'two_reads')
    return result, records


def score_lqb():
    from greekocr.labelfix import lqb
    target = lqb.DEFAULT / 'score_v2_4.json'
    python = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python'
    subprocess.run(['/usr/bin/arch', '-arm64', str(python), '-B', '-m',
                    'greekocr.labelfix.lqb', 'trend', '--truth',
                    str(lqb.DEFAULT / 'truth_v1_1.jsonl'), '--registry', str(m.REGISTRY),
                    '--output', str(target)], cwd=m.WORK, check=True)
    score = json.loads(target.read_text())
    delta = score['paired']['collection_v2_train→ru1_v2_train']
    m.dump(m.ART / 'lqb_delta_v2_4.json', delta)
    report = lqb.DEFAULT / 'SCORE_v2.md'
    text = report.read_text().split('\n## RU2TF4 / v2.4')[0]
    text = text.replace('# Label Quality Scoreboard v2.2', '# Label Quality Scoreboard v2.4', 1)
    lines = ['', '## RU2TF4 / v2.4', '',
             f"All {len(score['versions'])} registered versions rescored offline against frozen truth v1.1 after the lead rulings. "
             '`ru1_v2_train` retains the exact collection-v2 train IDs. Three edits use `lead_ruling`; '
             '52 edits use `two_reads`. The 20 hard and 10 soft audit positions are `lead_audit_confirmed`. '
             'Two positions remain held (`hold_yat`, `hold_uncertain`); their parent labels are retained.', '',
             '[Scores](score_v2_4.json), [paired delta](../../../artifacts/ru1/ru2t/lqb_delta_v2_4.json). '
             'Coverage refers only to frozen-truth overlap. Uncovered positions are not scored as correct. '
             'The RU1 yer paired overlap is zero; these scores do not measure the new edits or establish a population improvement.', '',
             '| Class / tier | Paired items | Parent errors | v2 errors | Delta per 100 | 95% CI |',
             '|---|---:|---:|---:|---:|---|']
    for group, d in delta.items():
        n = d.get('n_items', d.get('pairs', d.get('items', 0)))
        if n or d.get('a_errors') or d.get('b_errors') or group.endswith('|A+B'):
            lines.append(f"| {group.replace('|', ' / ')} | {n} | {d['a_errors']} | {d['b_errors']} | {d['delta_per_100']} | {d['ci95']} |")
    report.write_text(text + '\n'.join(lines) + '\n')
    return dict(ok=True, versions=len(score['versions']), score=str(target),
                score_sha256=m.sha(target), report=str(report), report_sha256=m.sha(report))


def main():
    manifest_path = m.ART.parent / 'ru1_v2_train_manifest.json'
    output = m.ART.parent / 'ru1_v2_train.jsonl'
    manifest = json.loads(manifest_path.read_text())
    previous = json.loads((m.ART / 'RU2TF3_RECEIPT.json').read_text())
    if m.sha(INDEX) != previous['sheets']['outputs'][str(INDEX)]:
        raise ValueError('review index changed since RU2TF3')
    if m.sha(m.SOURCE) != manifest['parent']['sha256']:
        raise ValueError('parent changed')
    # Retain the original ledger as the reproducible input on subsequent runs.
    baseline = m.ART / 'decisions_pre_RU2TF4.jsonl'
    expected = manifest['artifacts'][str(m.ART / 'decisions.jsonl')]
    if baseline.exists():
        expected = manifest['lead_review']['original_decisions_sha256']
    elif m.sha(m.ART / 'decisions.jsonl') == expected:
        baseline.write_bytes((m.ART / 'decisions.jsonl').read_bytes())
    else:
        raise ValueError('original decisions changed')
    if m.sha(baseline) != expected:
        raise ValueError('baseline decisions changed')
    decisions, records = apply_lead(list(m.rows(baseline)), json.loads(INDEX.read_text()))
    result, counts = m.apply_version(list(m.rows(m.SOURCE)), decisions)
    m.jsonl(m.ART / 'decisions.jsonl', decisions)
    m.jsonl(m.ART / 'lead_review.jsonl', records)
    m.jsonl(m.ART / 'per_row_decision_counts.jsonl', counts)
    m.jsonl(output, result)
    digest = m.sha(output)
    sha_path = output.with_suffix('.sha256')
    sha_path.write_text(f'{digest}  {output.name}\n')
    edits = Counter(d['basis'] for d in decisions if d['decision'] == 'edit_hard')
    manifest['output'].update(sha256=digest, rows=len(result))
    manifest['counts'] = dict(Counter(d['decision'] for d in decisions))
    manifest['edit_basis_counts'] = dict(edits)
    manifest['lead_review'] = dict(status='lead_audit_confirmed', review_cells=6,
        audit_cells=30, audit_counts={'edit_hard': 20, 'keep_soft': 10},
        original_decisions_sha256=expected, source=str(LEAD), source_sha256=m.sha(LEAD),
        index=str(INDEX), index_sha256=m.sha(INDEX), new_readings=False)
    for p in [m.ART / 'decisions.jsonl', m.ART / 'per_row_decision_counts.jsonl',
              m.ART / 'lead_review.jsonl', baseline, LEAD, INDEX, Path(__file__), sha_path]:
        manifest['artifacts'][str(p)] = m.sha(p)
    m.dump(manifest_path, manifest)
    m.register(m.REGISTRY, m.SOURCE, output, manifest['parent']['sha256'], len(result))
    lqb = score_lqb()
    hold = sum(r['status'] == 'hold' for r in result)
    receipt = dict(status='READY', rows=len(result), ok_rows=len(result)-hold, hold_rows=hold,
        edits=sum(edits.values()), edit_basis_counts=dict(edits), sha256=digest,
        audit='lead_audit_confirmed', lqb=lqb, manifest_sha256=m.sha(manifest_path),
        registry_sha256=m.sha(m.REGISTRY), network_used=False, git_writes=False, new_readings=False)
    m.dump(m.ART / 'RU2TF4_RECEIPT.json', receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
