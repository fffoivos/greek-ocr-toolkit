"""S5 step A: owner-judged band population on the final 0.9-s4 measurement.

Read-only over s4/replay.jsonl, s4/typology_replay.jsonl and the owner files.
Owner join copies s4/validate_report.py exactly: every 888 rating (explicit=False),
every owner_marks_20261019 entry and every typology mark (explicit=True) is a
candidate; chosen = max over (explicit, Athens-local->UTC stamp, list index).
Pool copies s4: main replay rows (last row per line_id), then typology rows not
in the main replay. Writes s5/band_population.jsonl, s5/excluded.jsonl,
s5/owner_conflicts.jsonl and s5/population_receipt.json.
"""
import json, math, re, hashlib, datetime, importlib.util
from pathlib import Path
from collections import Counter
from zoneinfo import ZoneInfo

D = Path(__file__).resolve().parent
S4 = D.parent / 's4'
BASE = Path.home() / 'Projects/greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1'
SS = BASE / 'small_segments'
LABELS = ('KEEP', 'DROP')
spec = importlib.util.spec_from_file_location('cells_output_common', BASE / 'cells_opus/scripts/common.py')
common = importlib.util.module_from_spec(spec); spec.loader.exec_module(common)


def read(p):
    return [json.loads(l) for l in open(p, encoding='utf-8') if l.strip()]


def write(p, rows):
    with open(p, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, sort_keys=True, allow_nan=False) + '\n')


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def stamp(m):  # identical to s4/validate_report.py::stamp
    s = m.get('updated', '')
    if not s:
        return 0.
    dt = datetime.datetime.fromisoformat(s.replace('Z', '+00:00'))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo('Europe/Athens'))
    return dt.timestamp()


# Owner DROP notes that say the Google output is wrong, or that the length is
# correct: rule 2 compares only lengths, so it cannot see these. Matched on the
# literal owner note; listed in full in the report for the owner to check.
LABEL_FAULT = re.compile(r'wrong output|wrong google output|actual output is|wrong reading|bad output', re.I)
LENGTH_OK = re.compile(r'length is correct|length of output is correct|output length is correct|correct char count|evenly matched per chars', re.I)


def length_blind(mark, note):
    if mark != 'DROP' or not note:
        return None
    if LABEL_FAULT.search(note):
        return 'label fault (owner note: output wrong)'
    if LENGTH_OK.search(note):
        return 'owner note: length correct'
    return None


def main():
    rs = read(S4 / 'replay.jsonl'); ts = read(S4 / 'typology_replay.jsonl')
    assert len(rs) == 1288 and len(ts) == 437
    ms = read(BASE / 'owner_marks_20261019.jsonl'); tm = read(SS / 'owner_marks_smallseg.jsonl')
    assert len(ms) == 240 and len({m['line_id'] for m in ms}) == 235 and len(tm) == 185
    candidates = {}
    for r in rs:
        rating = (r.get('owner_rating') or {})
        if rating.get('decision') in LABELS:
            candidates.setdefault(r['line_id'], []).append(dict(owner_mark=rating['decision'], source='888 rating', explicit=False, updated=rating.get('updated', ''), note=''))
    for source, entries in [('owner_marks_20261019', ms), ('typology', tm)]:
        for m in entries:
            candidates.setdefault(m['line_id'], []).append(dict(m, source=source, explicit=True))
    judgments = {}; conflicts = []
    for rid, entries in candidates.items():
        chosen = max(enumerate(entries), key=lambda it: (it[1]['explicit'], stamp(it[1]), it[0]))[1]
        judgments[rid] = chosen
        if len({m['owner_mark'] for m in entries}) > 1:
            conflicts.append(dict(line_id=rid, chosen=chosen, judgments=entries))
    pool = {}
    for r in rs:
        pool[r['line_id']] = dict(row=r, z=r['after'], cohort=r['cohort'], control=False)
    for t in ts:
        if t['line_id'] in pool:
            assert t['row']['crop_sha256'] == pool[t['line_id']]['row']['row']['crop_sha256']
            assert t['versions']['s4']['verdict'] == pool[t['line_id']]['z']['verdict']
            pool[t['line_id']]['also_typology'] = True
        else:
            pool[t['line_id']] = dict(row=t, z=t['versions']['s4'], cohort='typology', control=t['manifest']['control'])
    missing = sorted(set(judgments) - set(pool))
    assert not missing, missing
    pop, excl = [], []
    for rid, j in sorted(judgments.items()):
        p = pool[rid]; r = p['row']; z = p['z']; e = z['evidence']
        text = r['row']['raw_text']
        sset = 'typology marks' if j['source'] == 'typology' else ('888 ratings' if j['source'] == '888 rating' else j['sheet'])
        all_notes = [c.get('note', '') for c in candidates[rid] if c.get('note')]
        rec = dict(line_id=rid, cohort=p['cohort'], source_set=sset, also_typology=bool(p.get('also_typology')),
                   text=text, chars=r['chars'], characters_evidence=e.get('characters'), A=r['A'], small=bool(r['small']),
                   output_type=common.output_type(text), owner_mark=j['owner_mark'], owner_note=j.get('note', '') or '',
                   owner_source=j['source'], owner_updated=j.get('updated', ''), other_owner_notes=[n for n in all_notes if n != (j.get('note') or '')],
                   n_judgments=len(candidates[rid]), verdict_s4=z['verdict'], reason_s4=z['reason'], gate_s4=e['gate']['verdict'],
                   gate_reason_s4=e['gate']['reason'], control=p['control'])
        if p['control']:
            rec['exclusion'] = 'typology control'; excl.append(rec); continue
        if e['gate']['verdict'] != 'PASS':
            rec['exclusion'] = 'gate ' + e['gate']['verdict']; excl.append(rec); continue
        b = e['box_evidence']; ch = e.get('characters')
        exp = b.get('predictions', [None] * 3)[2] if b.get('available') else None
        if not b.get('available') or not isinstance(exp, (int, float)) or not math.isfinite(exp) or exp < 0 or not isinstance(ch, (int, float)) or ch < 0:
            rec['exclusion'] = 'no usable box/prediction'; excl.append(rec); continue
        assert exp == b['prediction']['expected'] and ch == r['chars']
        pe = e['padding_evidence']; pad = pe.get('total_padding_line_heights') if pe.get('available') else None
        rec.update(expected=exp, r=(ch + 1) / (exp + 1), padding=pad,
                   padding_state=('UNAVAILABLE' if pad is None or not math.isfinite(pad) else ('DROP' if pad > 1.5 else 'KEEP')),
                   length_blind=length_blind(j['owner_mark'], j.get('note', '') or ''))
        # Readback: the current 0.5-1.5 band + padding 1.5 must reproduce the saved 0.9-s4 verdict.
        cur = 'DROP' if (rec['r'] < .5 or rec['r'] > 1.5) else ('KEEP' if rec['padding_state'] == 'KEEP' else ('DROP' if rec['padding_state'] == 'DROP' else 'UNCERTAIN'))
        assert cur == z['verdict'], (rid, cur, z['verdict'])
        pop.append(rec)
    write(D / 'band_population.jsonl', pop); write(D / 'excluded.jsonl', excl); write(D / 'owner_conflicts.jsonl', conflicts)
    receipt = dict(judged_ids=len(judgments), population=len(pop), excluded=len(excl),
                   exclusion_reasons=dict(Counter(x['exclusion'] for x in excl)),
                   excluded_by_reason_and_mark={k: v for k, v in Counter(f"{x['exclusion']} / owner {x['owner_mark']}" for x in excl).items()},
                   conflicts=len(conflicts), owner_marks=dict(Counter(x['owner_mark'] for x in pop)),
                   source_sets=dict(Counter(x['source_set'] for x in pop)), cohorts=dict(Counter(x['cohort'] for x in pop)),
                   output_types=dict(Counter(x['output_type'] for x in pop)), small=dict(Counter(x['small'] for x in pop)),
                   length_blind=dict(Counter(x['length_blind'] for x in pop if x['length_blind'])),
                   readback='current 0.5-1.5 + padding 1.5 reproduces every saved 0.9-s4 verdict in the population',
                   input_sha256={str(p): sha(p) for p in [S4 / 'replay.jsonl', S4 / 'typology_replay.jsonl', BASE / 'owner_marks_20261019.jsonl', SS / 'owner_marks_smallseg.jsonl', BASE / 'cells_opus/scripts/common.py']})
    (D / 'population_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=1, sort_keys=True))
    print(json.dumps({k: v for k, v in receipt.items() if k != 'input_sha256'}, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
