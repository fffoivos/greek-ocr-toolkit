"""Offline RU3T final write step from the frozen F3 combine and lead audit.

No readers, sheet generation, network, subprocesses, or git writes.
"""
import copy
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path


def guard(event, args):
    if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system'}:
        raise RuntimeError('RU3TF4 network and process launches disabled')
    if event == 'open':
        path, mode, flags = args
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (
            isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
        if writing and isinstance(path, (str, bytes, os.PathLike)):
            if '.git' in Path(os.fsdecode(path)).resolve().parts:
                raise RuntimeError('RU3TF4 .git writes disabled')


sys.addaudithook(guard)
import ru3t as m

LEAD = m.WORK/'docs/records/labelfix/secondary/RU3T_LEAD_AUDIT.md'
F3 = m.SCRATCH/'ru1_review/ru3t_f3'
VERSION = 'ru1_v3_train'


def checked(bindings):
    for path, digest in bindings.items():
        if m.sha(path) != digest:
            raise ValueError('bound input changed: '+str(path))


def rulings(decisions, cells):
    """Retain vote/reason evidence; record all 341 explicit lead outcomes."""
    lookup = {(d['row_id'], d['offset']): d for d in decisions}
    assert len(lookup) == len(decisions)
    assert sorted(c['cell'] for c in cells) == list(range(1, 342))
    assert Counter(c['set'] for c in cells) == dict(review=281, audit=60)
    assert {(c['row_id'], c['offset']) for c in cells if c['set'] == 'review'} == {
        k for k, d in lookup.items() if d['decision'] == 'lead_review'}
    for c in cells:
        d = lookup[c['row_id'], c['offset']]
        assert d['decision'] == c['decision']
        ref = dict(reference=str(LEAD.relative_to(m.WORK)), cell=c['cell'])
        if c['set'] == 'review' or c['cell'] == 293:
            if c['cell'] == 293:
                assert c['row_id'] == '0b4bf868-p000097-l0018' and d['decision'] == 'edit_hard'
            d['decision_before_lead'] = d['decision']
            d['decision'] = 'hold' if c['set'] == 'review' else 'hold_uncertain'
            d['lead_ruling'] = dict(ref, decision=d['decision'])
        else:
            d['lead_audit_confirmed'] = dict(ref, decision=d['decision'])
    assert sum('lead_audit_confirmed' in d for d in decisions) == 59
    assert all(d['decision'] != 'lead_review' for d in decisions)
    return decisions


def finalize():
    receipt = json.loads((F3/'RU3TF3_RECEIPT.json').read_text())
    assert receipt['status'] == 'READY' and receipt['replacements_done'] == 17
    assert not receipt['incomplete_replacements']
    checked(receipt['outputs'])
    checked(receipt['evidence'])
    for c in receipt['replacement_completion'].values():
        assert c['status'] == 'DONE'
        checked(c['evidence'])
    for name in ['build.json', 'r3_replacements/build.json', 'r5_replacements/build.json']:
        build = json.loads((m.ART/name).read_text())
        checked(build.get('bindings', {**build.get('inputs', {}), **build.get('pack_inputs', {})}))
    info = json.loads((m.ART/'build.json').read_text())
    prior = Path(info['prior'])
    assert m.sha(prior) == info['prior_sha256'] == m.PRIOR_SHA
    assert m.sha(m.SOURCE) == info['parent_sha256']
    assert not (m.ART/'STOPPED_AT_70.json').exists()
    originals = list(m.rows(F3/'decisions.jsonl'))
    assert Counter(d['decision'] for d in originals) == receipt['counts']
    decisions = rulings(copy.deepcopy(originals), json.loads((F3/'sheets_index.json').read_text())['items'])
    inherited = list(m.rows(Path(info['old_art'])/'decisions.jsonl'))
    assert not ({(d['row_id'], d['offset']) for d in inherited} &
                {(d['row_id'], d['offset']) for d in decisions})
    assert list(m.rows(F3/'decisions_merged.jsonl')) == inherited+originals
    prior_rows = list(m.rows(prior))
    # apply_version's wire format uses hold; preserve hold_uncertain in the decision ledger.
    applied = [dict(d, decision='hold', reason='hold_uncertain')
               if d['decision'] == 'hold_uncertain' else d for d in decisions]
    result, counts = m.merge_labels(prior_rows, prior_rows, applied)
    previous = {r['id']: r for r in prior_rows}
    grouped = defaultdict(list)
    for d in decisions:
        grouped[d['row_id']].append(d)
    edits = 0
    for r in result:
        old = previous[r['id']]
        if r['id'] not in grouped:
            assert r == old
            continue
        assert not old['holds'], 'new decisions overlap inherited holds'
        allowed = {d['offset'] for d in grouped[r['id']] if d['decision'] == 'edit_hard'}
        actual = {i for i, (a, b) in enumerate(zip(old['label'], r['label'])) if a != b}
        assert len(old['label']) == len(r['label']) and actual == allowed
        assert all(old['label'][i] == 'ь' and r['label'][i] == 'ъ' for i in actual)
        edits += len(actual)
    row_counts = dict(Counter(r['status'] for r in result))
    assert len(result) == len(prior_rows) == len(previous)
    assert sum(d['decision'] == 'hold' for d in decisions) == 281
    assert sum(d['decision'] == 'hold_uncertain' for d in decisions) == 1
    assert Counter(d['reason'] for d in decisions if d['decision'] == 'hold') == receipt['lead_review_reasons']
    output = m.WORK/f'artifacts/ru1/{VERSION}.jsonl'
    assert not output.exists(), 'refuse overwrite of final labels'
    registry = json.loads(m.REGISTRY.read_text())
    parent = registry['versions']['ru1_v2_train']
    assert parent['sha256'] == m.sha(prior) and Path(parent['path']) == prior
    assert VERSION not in registry['versions'], 'version already registered'
    artifacts = [m.ART/'decisions.jsonl', m.ART/'decisions_merged.jsonl',
                 m.ART/'per_row_decision_counts.jsonl']
    m.jsonl(artifacts[0], decisions)
    m.jsonl(artifacts[1], inherited+decisions)
    for c, r in zip(counts, result):
        c['status'] = r['status']
    m.jsonl(artifacts[2], counts)
    m.jsonl(output, result)
    digest = m.sha(output)
    covered = {r['row_id'] for r in m.rows(Path(info['old_art'])/'selected_lines.jsonl')}
    covered.update(rid for rid, ds in grouped.items() if all(
        len([v for v in d['reads'].values() if v]) == 2 for d in ds))
    inputs = {str(p): m.sha(p) for p in [LEAD, Path(__file__), F3/'RU3TF3_RECEIPT.json',
              F3/'decisions.jsonl', F3/'sheets_index.json', m.ART/'build.json']}
    manifest = dict(version=VERSION, parent=dict(path=str(prior), sha256=m.sha(prior)),
        source_collection=dict(path=str(m.SOURCE), sha256=m.sha(m.SOURCE)),
        inherited=dict(path=str(prior), sha256=m.sha(prior), lines=info['inherited_lines']),
        output=dict(path=str(output), sha256=digest, rows=len(result)), row_counts=row_counts,
        edits=edits, counts=dict(Counter(d['decision'] for d in decisions)),
        lead_audit_confirmed=59, lead_review_reasons=receipt['lead_review_reasons'],
        partial=False, covered_lines=len(covered), contexts=receipt['contexts'],
        coverage=receipt['coverage'], evidence=receipt['evidence'], inputs=inputs,
        scanner_sha256=receipt['scanner_sha256'], fresh_r3_positions=sum(1 for _ in m.rows(F3/'fresh_r3_positions.jsonl')),
        artifacts={str(p): m.sha(p) for p in artifacts},
        constraints=dict(network=False, new_readings=False, browser=False, computer_use=False, git_writes=False))
    manifest_path = output.with_name(VERSION+'_manifest.json')
    m.dump(manifest_path, manifest)
    output.with_suffix('.sha256').write_text(digest+'  '+output.name+'\n')
    registry['versions'][VERSION] = dict(path=str(output), sha256=digest, parent='ru1_v2_train',
        text_field='label', id_field='id', status='local', read='exact id label; no fallback',
        population=dict(rows=len(result), definition='full train; RU2T inherited, RU3T lead-audited corrections; unresolved positions HOLD',
                        covered_candidate_lines=len(covered)))
    m.dump(m.REGISTRY, registry)
    sys.path.insert(0, str(m.WORK))
    from greekocr.labelfix import lqb
    truth = m.WORK/'docs/records/labelfix/lqb/truth_v1_1.jsonl'
    score_path = truth.with_name('score_'+VERSION+'.json')
    score = lqb.run(truth, registry, list(registry['versions']))
    m.dump(score_path, score)
    delta = score['paired']['ru1_v2_train→'+VERSION]
    m.dump(m.ART/'lqb_delta.json', delta)
    checked(inputs)
    assert m.sha(output) == digest
    assert json.loads(m.REGISTRY.read_text())['versions'][VERSION]['sha256'] == digest
    final = dict(status='READY', manifest=manifest, lqb=dict(registered=True, score=str(score_path),
        sha256=m.sha(score_path), truth_sha256=m.sha(truth), delta=delta),
        outputs={str(p): m.sha(p) for p in [output, manifest_path, output.with_suffix('.sha256'), m.REGISTRY, score_path]})
    m.dump(m.ART/'RU3TF4_RECEIPT.json', final)
    m.dump(m.ART/'FINALIZED_RECEIPT.json', final)
    print(json.dumps(dict(rows=len(result), row_counts=row_counts, edits=edits,
        decisions=manifest['counts'], lead_audit_confirmed=59, sha256=digest, lqb_registered=True)))
    print(f'RU3TF4 READY: ru1_v3_train rows {len(result)} (ok {row_counts.get("ok", 0)}, hold {row_counts.get("hold", 0)}); edits {edits}; sha256 {digest}; LQB registered ok')


if __name__ == '__main__':
    finalize()
