"""Issue the explicitly authorized, sample-audited RU4EF3 sparse overlay offline.

Run ru4ef2_collect.py first. No reader, network, or child process is launched here.
The 30 sampled cells are confirmed; other edits inherit the accepted audit policy,
not a claim of individual pixel adjudication. Unruled review cells remain holds.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT/'artifacts/ru1/ru4e2'
OUT = ROOT/'artifacts/ru1/ru1_v3_test_edits.jsonl'
REG = ROOT/'docs/labelfix/lqb/versions.json'
AUDIT = ROOT/'docs/labelfix/secondary/RU4E_LEAD_AUDIT.md'


def guard(event, args):
    if event.startswith('socket.') or event in {'subprocess.Popen', 'os.system'}:
        raise RuntimeError('offline issuance: network/process launch disabled')
    if event == 'open':
        p, mode, flags = args
        writing = (isinstance(mode, str) and any(c in mode for c in 'wax+')) or (isinstance(flags, int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))
        if writing and isinstance(p, (str, bytes, os.PathLike)) and '.git' in Path(os.fsdecode(p)).resolve().parts:
            raise RuntimeError('.git writes disabled')


sys.addaudithook(guard)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def rows(p):
    return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]


def dump(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n')


def jsonl(p, rr):
    Path(p).write_text(''.join(json.dumps(r, ensure_ascii=False, separators=(',', ':'))+'\n' for r in rr))


def main():
    assert not OUT.exists(), 'refuse issued overlay overwrite'
    combine = json.loads((ART/'RU4EF2_COMBINE.json').read_text())
    assert sha(ART/'decisions.jsonl') == combine['decisions_sha256']
    for p, h in combine['evidence'].items():
        assert sha(p) == h, p
    assert len(combine['r5_replacements']) == 3
    assert all(r['identity'] in combine['contexts'] for r in combine['r5_replacements'])
    png = json.loads((ART/'RU4EF2_RECEIPT.json').read_text())['lead_material']
    for p, h in png['outputs'].items():
        assert sha(p) == h, p
    cells = rows(Path(png['path'])/'template.jsonl')
    audited = {(r['row_id'], r['offset']): r for r in cells if r['set'] == 'audit'}
    review = {(r['row_id'], r['offset']) for r in cells if r['set'] == 'review'}
    assert len(audited) == 30 and len(review) == 30
    assert '30/30 decisions match the ink' in AUDIT.read_text()
    source_decisions = rows(ART/'decisions.jsonl')
    ds = []
    for d in source_decisions:
        k = d['row_id'], d['offset']
        if k in audited:
            assert d['decision'] == audited[k]['decision']
        d = copy.deepcopy(d)
        d['provenance'] = dict(decision_file=str(ART/'decisions.jsonl'), decision_file_sha256=sha(ART/'decisions.jsonl'), lead_audit=str(AUDIT), lead_audit_sha256=sha(AUDIT), audit_policy='lead_audit_confirmed', individually_audited=k in audited, original_offset=d['offset'], offset_remapped=False)
        if k in audited:
            d['lead_audit_confirmed'] = True
        if k in review:
            d.update(decision='hold', reason='review_png_unruled_cost_decision')
        ds.append(d)
    assert len({(d['row_id'], d['offset']) for d in ds}) == len(ds) == 1753
    assert set(audited) | review <= {(d['row_id'], d['offset']) for d in ds}
    grouped = defaultdict(list)
    for d in ds:
        grouped[d['row_id']].append(d)
        if d['decision'] == 'edit_hard':
            assert {v['logical_reader'] for v in d['reads']} == {'r1', 'r2'} and len(d['reads']) == 2
            assert all(v['call'] == 'ъ' and v['gate_status'] == 'VALID' for v in d['reads'])
    build = json.loads((ART/'build.json').read_text())
    sources = {s: dict(path=str(p), sha256=sha(p), text_field='label', id_field='id') for s, p in build['sources'].items()}
    result, verification, originals = [], [], {}
    for split, spec in sources.items():
        assert build['inputs'][spec['path']] == spec['sha256']
        for r in rows(spec['path']):
            rid = r['id']; raw = r['label']
            assert rid not in originals
            originals[rid] = raw
            dd = grouped.get(rid, [])
            assert all(d['split'] == split and raw[d['offset']] == 'ь' and d['kind'] == 'final' for d in dd)
            edits = [dict(d, **{'from': 'ь', 'to': 'ъ'}) for d in dd if d['decision'] == 'edit_hard']
            holds = [d for d in dd if d['decision'] == 'hold']
            if not edits and not holds:
                continue
            chars = list(raw)
            for d in edits:
                chars[d['offset']] = 'ъ'
            text = ''.join(chars)
            changed = [i for i, (a, b) in enumerate(zip(raw, text)) if a != b]
            assert len(raw) == len(text) and set(changed) == {d['offset'] for d in edits}
            assert all((raw[i], text[i]) == ('ь', 'ъ') for i in changed)
            restored = list(text)
            for i in changed:
                restored[i] = 'ь'
            assert ''.join(restored).encode() == raw.encode()
            assert all(text[d['offset']] == 'ь' for d in holds)
            parent_sha = hashlib.sha256(raw.encode()).hexdigest()
            result.append(dict(id=rid, split=split, label=text, label_parent=raw, parent_utf8_sha256=parent_sha, status='hold' if holds else 'ok', edits=edits, holds=holds))
            verification.append(dict(id=rid, split=split, offsets=changed, holds=[d['offset'] for d in holds], parent_utf8_sha256=parent_sha, diff_equals_listed_edits=True, restored_raw_bytes=True))
    assert set(grouped) <= set(originals)
    wave = json.loads((ART/'wave1c_comparison.json').read_text())
    populations = []
    for c in wave['comparisons']:
        if c['view'] != 'v2_test':
            continue
        assert sha(c['path']) == c['sha256'] and sha(c['receipt']) == c['receipt_sha256']
        ids = {r['line_id'] for r in rows(c['path']) if r.get('script_class') == 'cyrillic'}
        assert len(ids) == 1742
        populations.append(ids)
    assert len(populations) == 6 and all(ids == populations[0] for ids in populations)
    wave_rows = [r for r in result if r['id'] in populations[0] and r['edits']]
    counts = dict(rows=len(result), splits=dict(Counter(r['split'] for r in result)), edited_rows=sum(bool(r['edits']) for r in result), edits=sum(len(r['edits']) for r in result), hold_rows=sum(bool(r['holds']) for r in result), hold_positions=sum(len(r['holds']) for r in result), wave1c_edits=sum(len(r['edits']) for r in wave_rows), wave1c_edited_rows=len(wave_rows), wave1c_slice_ids=1742)
    reg = json.loads(REG.read_text())
    assert 'ru1_v3_test_edits' not in reg['versions']
    parent = reg['versions']['google_raw_v2_import']
    for s, spec in sources.items():
        assert parent.setdefault('splits', {}).get(s, spec) == spec
        parent['splits'][s] = spec
    jsonl(OUT, result)
    assert rows(OUT) == result
    jsonl(ART/'RU4EF3_row_verification.jsonl', verification)
    jsonl(ART/'RU4EF3_decisions.jsonl', ds)
    digest = sha(OUT)
    manifest = dict(version='ru1_v3_test_edits', parent=dict(version='google_raw_v2_import', splits=sources), output=dict(path=str(OUT), sha256=digest, rows=len(result)), counts=counts, decisions=dict(Counter(d['decision'] for d in ds)), lead_audit_confirmed=30, audit_policy='User-authorized sampled audit acceptance; only 30 sampled positions individually pixel-confirmed; all remaining lead_review and unruled PNG cells hold, retaining Google ь.', offset_unit='zero-based Unicode code point in exact RAW Google import label', inheritance='Omitted IDs inherit exact RAW Google text in their recorded test/dev split', contexts=combine['contexts'], coverage=combine['coverage'], evidence=combine['evidence'], provenance={str(p): sha(p) for p in [Path(__file__), AUDIT, ART/'RU4EF2_COMBINE.json', ART/'RU4EF3_decisions.jsonl', ART/'RU4EF3_row_verification.jsonl', ART/'wave1c_comparison.json', Path(png['path'])/'template.jsonl']}, constraints=dict(network_used=False, git_writes=False, reader_runs=0, browser=False, computer_use=False))
    manifest_path = OUT.with_name(OUT.stem+'_manifest.json')
    dump(manifest_path, manifest)
    OUT.with_suffix('.sha256').write_text(digest+'  '+OUT.name+'\n')
    reg['versions']['ru1_v3_test_edits'] = dict(path=str(OUT), sha256=digest, parent='google_raw_v2_import', overlay=True, text_field='label', id_field='id', parent_splits=list(sources), split_field='split', sources=sources, status='local', manifest=str(manifest_path), population=counts, read='Exact id overlay; omitted IDs inherit exact RAW Google import label in recorded split; holds retain Google ь')
    dump(REG, reg)
    print(json.dumps(counts))


if __name__ == '__main__':
    main()
