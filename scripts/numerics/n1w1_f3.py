"""Apply the 63 existing lead rulings offline; never launch readers or use git."""
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from greekocr.ops.data_root import input_path as _data_input
ART = ROOT / 'artifacts/n1'
FINAL = ART / 'n1w1/r3/finalization'
RULING = ROOT / 'docs/records/labelfix/secondary/N1W1_LEAD_RAISED.md'


def sha(path):
    h = hashlib.sha256()
    with _data_input(Path(path)).open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def rows(path):
    return [json.loads(s) for s in _data_input(Path(path)).read_text().splitlines() if s.strip()]


def dump(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def jsonl(path, data):
    Path(path).write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in data))


def category(d):
    valid = [r for r in d['reads'] if r['context_status'] == 'VALID' and r['read_status'] == 'ok']
    if len(valid) != 2:
        return 'still_missing'
    a, b = [r['meaning'] for r in valid]
    if a != b:
        return 'disagreements'
    return {'raised dot': 'agreed_raised', 'baseline dot': 'baseline',
            'hyphen': 'hyphen_dash', 'en dash': 'hyphen_dash', 'em dash': 'hyphen_dash'}.get(a, 'other')


def build():
    # Network is explicitly disabled even for imported scoring code.
    def offline(*args, **kwargs):
        raise RuntimeError('N1W1F3 network OFF')
    socket.socket = offline
    socket.create_connection = offline
    socket.getaddrinfo = offline
    previous = json.loads((ART / 'n1_v1_w1_manifest.json').read_text())
    pending_path = ART / 'n1_v1_w1_pending.json'
    pending = json.loads(pending_path.read_text())
    review = Path(pending['index']).parent.parent
    features = Path(next(p for p in previous['inputs'] if p.endswith('/W1/features.jsonl')))
    source = ART / 'n1w1/parent.jsonl'
    decisions_path = FINAL / 'decisions.jsonl'
    for p in (features, source, decisions_path):
        assert sha(p) == previous['inputs'][str(p)], p
    assert '63/63' in RULING.read_text()
    indexes = [review / 'sheets/index.json', review / 'sheets2/index.json']
    assert sha(indexes[1]) == pending['index_sha256']
    cells = {}
    for index, count in zip(indexes, (22, 41)):
        data = json.loads(index.read_text())
        found = [c for sheet in data['sheets'] for c in sheet['cells']]
        assert len(found) == count
        for sheet in data['sheets']:
            assert sha(sheet['sheet']) == sheet['sha256']
        for cell in found:
            assert cell['slot_id'] not in cells
            cells[cell['slot_id']] = cell
    ds = rows(decisions_path)
    confirmed = set(cells)
    assert len(confirmed) == 63
    assert confirmed == {d['slot_id'] for d in ds if d['agreed_raised']}
    assert {s['slot_id'] for s in pending['slots']} == {c['slot_id'] for sh in json.loads(indexes[1].read_text())['sheets'] for c in sh['cells']}
    slots = {s['slot_id']: s for s in rows(ART / 'n1w1/candidates.jsonl')}
    parent = {r['id']: r for r in rows(source)}
    raw = {}
    with features.open() as f:
        for line in f:
            r = json.loads(line)
            if r['id'] in parent:
                assert r['id'] not in raw
                raw[r['id']] = r['text']
    assert set(raw) == set(parent)
    templates = [review / 'lead_template.jsonl', review / 'sheets2/lead_template.jsonl']
    for template, index in zip(templates, indexes):
        records = rows(template)
        expected = {c['slot_id'] for sh in json.loads(index.read_text())['sheets'] for c in sh['cells']}
        assert {r['slot_id'] for r in records} == expected
        for r in records:
            s = slots[r['slot_id']]
            assert r['zoom_sha256'] == s['zoom_sha256'] == cells[r['slot_id']]['zoom_sha256']
            assert sha(s['zoom']) == s['zoom_sha256']
            assert sha(s['line']) == s['line_sha256'] == cells[r['slot_id']]['line_sha256']
            text = raw[s['line_id']]
            assert text[s['start']:s['end']] in ('-', '.') and s['end'] == s['start'] + 1
            r.update(pixel_checked=True, printed=text[:s['start']] + '·' + text[s['end']:],
                     note='Lead-confirmed raised dot; ' + str(RULING.relative_to(ROOT)))
        jsonl(template, records)
    byline = defaultdict(list)
    for d in ds:
        byline[d['line_id']].append(d)
    output = []
    for lid in parent:
        text = raw[lid]
        edits, holds = [], []
        for d in byline[lid]:
            assert text[d['start']:d['end']] == d['old'] and d['end'] == d['start'] + 1
            if d['slot_id'] in confirmed:
                assert d['old'] in '-.' and 'range' not in slots[d['slot_id']]['grammar_candidates']
                edits.append(dict(slot_id=d['slot_id'], start=d['start'], end=d['end'], original=d['old'], replacement='·', pixel_checked=True, ruling=str(RULING.relative_to(ROOT))))
            elif category(d) not in ('baseline', 'hyphen_dash'):
                holds.append(dict(slot_id=d['slot_id'], start=d['start'], end=d['end'], status='hold', reason=d['reason']))
        if not edits and not holds:
            continue
        chars = list(text)
        for e in edits:
            chars[e['start']] = '·'
        output.append(dict(id=lid, text=''.join(chars), parent_text=text, status='edit' if edits else 'hold', edits=edits, holds=holds, slot_provenance=byline[lid]))
    path = ART / 'n1_v1_w1.jsonl'
    jsonl(path, output)
    # Independent serialized readback, including exact untouched UTF-8 segments.
    verification = []
    for r in rows(path):
        text = raw[r['id']]
        assert r['parent_text'].encode() == text.encode()
        actual = [(i, a, b) for i, (a, b) in enumerate(zip(text, r['text'])) if a != b]
        expected = sorted((e['start'], e['original'], e['replacement']) for e in r['edits'])
        assert len(text) == len(r['text']) and actual == expected
        assert len({e['start'] for e in r['edits']}) == len(r['edits'])
        cursor = 0
        for e in sorted(r['edits'], key=lambda e: e['start']):
            assert r['text'][cursor:e['start']].encode() == text[cursor:e['start']].encode()
            cursor = e['end']
        assert r['text'][cursor:].encode() == text[cursor:].encode()
        assert r['edits'] or r['status'] == 'hold'
        assert not any(h['slot_id'] in confirmed for h in r['holds'])
        verification.append(dict(id=r['id'], exact_diff=True, edits=len(r['edits']), holds=len(r['holds'])))
    assert {e['slot_id'] for r in output for e in r['edits']} == confirmed
    assert sum(len(r['edits']) for r in output) == 63
    path.with_suffix('.sha256').write_text(sha(path) + '  ' + path.name + '\n')
    verify_path = FINAL / 'f3_row_verification.json'
    dump(verify_path, verification)
    registry_path = ROOT / 'docs/records/labelfix/lqb/versions.json'
    registry = json.loads(registry_path.read_text())
    assert registry['versions']['google_raw_w1']['sha256'] == sha(features)
    registration = registry['versions']['n1_v1_w1']
    registration.update(path=str(path), sha256=sha(path), parent='google_raw_w1', overlay=True, text_field='text', id_field='id', status='local', population=dict(overlay_rows=len(output), definition='63 lead-confirmed separator edits and explicitly marked unresolved holds; otherwise inherit raw W1 text'))
    dump(registry_path, registry)
    from greekocr.labelfix import lqb
    truth = ROOT / 'docs/records/labelfix/lqb/truth_v1_1.jsonl'
    score = lqb.run(truth, json.loads(registry_path.read_text()), ['google_raw_w1', 'n1_v1_w1'])
    score_path = FINAL / 'f3_lqb_rescore.json'
    dump(score_path, score)
    dump(pending_path, dict(status='resolved', pending_slots=0, resolved_slots=41, total_confirmed=63, index=str(indexes[1]), index_sha256=sha(indexes[1]), slots=rows(templates[1]), ruling=str(RULING.relative_to(ROOT)), output_sha256=sha(path)))
    docs = sorted({slots[s]['line_id'].split('--')[1] for s in confirmed})
    manifest = {k: previous[k] for k in ('counts', 'contexts_physical', 'contexts_effective')}
    manifest.update(schema='N1W1F3-v1', version='n1_v1_w1', parent='google_raw_w1', output=dict(path=str(path), sha256=sha(path), rows=len(output)), edits=63, holds=sum(len(r['holds']) for r in output), hold_only_rows=sum(r['status']=='hold' for r in output), hold_rows=sum(bool(r['holds']) for r in output), docs=docs, confirmed_slots=sorted(confirmed), pending=str(pending_path), pending_status='resolved', exact_diff_verified_rows=len(verification), network=False, new_readers=0, git_writes=False, browser_or_computer_use=False,
        inputs={str(p): sha(p) for p in [features, source, decisions_path, RULING, Path(__file__), truth, truth.with_name('truth_v1_1_flags.jsonl'), *indexes]},
        evidence={str(p): sha(p) for p in [*templates, verify_path, score_path, registry_path, pending_path]},
        lqb=dict(rescored=True, registration_verified=True, truth=str(truth), edited_rows_on_truth=len({r['id'] for r in output if r['edits']} & {r['line_id'] for r in rows(truth)}), separator=score['versions']['n1_v1_w1']['n1_separator|A+B'], paired_separator=score['paired']['google_raw_w1→n1_v1_w1']['n1_separator|A+B'], note='N1 wildcard contamination keeps separator truth in_sample; no paired separator headline or improvement claim.'))
    dump(ART / 'n1_v1_w1_manifest.json', manifest)
    receipt = FINAL / 'N1W1F3_RECEIPT.json'
    dump(receipt, manifest)
    receipt.with_suffix('.sha256').write_text(sha(receipt) + '  ' + receipt.name + '\n')
    return manifest


if __name__ == '__main__':
    result = build()
    print(json.dumps({k: result[k] for k in ('output', 'edits', 'holds', 'hold_only_rows', 'hold_rows', 'docs', 'pending_status')}, indent=2))
