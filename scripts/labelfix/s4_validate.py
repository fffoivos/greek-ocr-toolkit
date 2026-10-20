"""S4 whole-line comparison using frozen print truth and cached alignments only.

Detection consumes recogniser text, pixels and alignment. Google/human labels
are read only by the frozen evaluation instruments, never by reading.py.
"""
from greekocr.ops.data_root import input_path as _data_input
import os
for k in ('VECLIB_MAXIMUM_THREADS', 'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ[k] = '1'
import gzip
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
from PIL import Image
from greekocr.labelfix import ink as I, markshape as M
from greekocr.labelfix.reading import read_ink, render_reading
from greekocr.labelfix.validate import load_three_way
from greekocr.labelfix.sheet import load_alignments, crop_key
from greekocr.labelfix.linemetric import mark_set, score_slots, pooled
from greekocr.labelfix.owner_slots import overlap_slots

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/records/labelfix/spellcheck'


def read(path):
    with (gzip.open if str(path).endswith('.gz') else open)(_data_input(path), 'rt') as f:
        return [json.loads(x) for x in f]


def write(path, rows):
    with (gzip.open if str(path).endswith('.gz') else open)(path, 'wt') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False)+'\n')


def metric(lines, key):
    return pooled([score_slots([dict(s, detected=s[key], unknown_kinds=[]) for s in l['slots']]) for l in lines])


def main():
    raise RuntimeError('Historical validator is pinned to its saved artifacts; SF1 runtime has a new pixel/schema contract. Use sf1_rescore for saved-evidence truth/policy comparisons, or copy this validator to an explicitly versioned output workflow.')
    start = time.monotonic()
    lines = load_three_way(0)
    old = {l['line_id']:l for l in read(OUT/'S3_lines.jsonl.gz')}
    als = load_alignments(ROOT/'.cache/labelfix/align_s0.jsonl')
    model = M.load_model(ROOT/'docs/records/labelfix/markshape_model_S4.json')
    rows = []
    for l in lines:
        baseline = old[l['line_id']]
        with Image.open(l['crop']) as im:
            ci = I.analyse(im)
        reading = read_ink(ci, l['model'], als[crop_key(l['crop'])], model, filtered=False)
        slots = []
        old_render = []
        for bs in baseline['slots']:
            s = dict(bs, before=[x for x in bs['detected'] if x[0] not in bs.get('unknown_kinds',[])], before_evidence=bs['evidence'],
                     before_above=bs['above'], before_below=bs['below'], detected=[], cls='none',
                     above=0, below=0, unknown_kinds=[], unnamed=[])
            # Blank evidence for an unlocated component is explicit, never a
            # carry-forward of S3's marks.
            s['evidence'] = dict(bs['evidence'], above=[], below=[], diagnostics=[], apostrophes=[])
            slots.append(s)
        serial = []
        for rs in reading.slots:
            c = rs['component']
            d = {k:v for k,v in rs.items() if k not in ('component','evidence','naming')}
            if c is not None:
                original = next((q for q in ci.components if q.index == c.index), None)
                primary = next((s for s in slots if s['bbox'] ==
                                [original.x0,original.y0,original.x1,original.y1]), None) if original is not None else None
                if primary is not None:
                    ev = rs['evidence']; names = rs['naming']
                    detected = sorted(mark_set('+'.join(rs['parts'])))
                    if ev.clipped_bottom:
                        detected = [x for x in detected if x[0] != 'subscript']
                    if names.unnamed:
                        detected.append(('accent', 'unclassified'))
                    if rs.get('apostrophe'):
                        detected.append(('apostrophe','apostrophe'))
                    primary.update(detected=detected, cls='+'.join(rs['parts']) or 'none', evidence=ev.to_record(),
                                   above=len(ev.above), below=len(ev.below), unnamed=list(names.unnamed),
                                   recogniser_base=rs['base'], recogniser_start=rs['start'])
                    # S3's frozen component sequence rendered over exactly the
                    # same recogniser letters, for a transparent before string.
                    oldparts = []
                    for kind, value in primary['before']:
                        if kind == 'compound':
                            oldparts.extend(value.split('+'))
                        elif value in ('acute','grave','circumflex','psili','dasia','subscript','dialytika'):
                            oldparts.append(value)
                    old_render.append(dict(rs, parts=oldparts,
                                           apostrophe=any(k=='apostrophe' for k,v in primary['before'])))
                    d['component_slot'] = primary['slot']
                d['bbox'] = [c.x0,c.y0,c.x1,c.y1]
                d['evidence'] = rs['evidence'].to_record()
            serial.append(d)
        rows.append(dict(line_id=l['line_id'], doc=l['doc'], dev=baseline['dev'], crop=l['crop'],
                         slots=slots, recogniser_text=l['model'], before_reading=render_reading(l['model'],old_render),
                         reading=reading.text, reading_flags=reading.unnamed,
                         opening_quotes=reading.opening_quotes, recogniser_slots=serial))
    write(OUT/'S4_lines.jsonl.gz', rows)
    held = [l for l in rows if not l['dev']]
    dev = [l for l in rows if l['dev']]
    result = dict(before=metric(held,'before'), after=metric(held,'detected'),
                  dev_before=metric(dev,'before'), dev_after=metric(dev,'detected'),
                  heldout_lines=len(held), dev_lines=len(dev), ctc_forward_passes=0, network=False,
                  cpu_only=True, elapsed_seconds=time.monotonic()-start)
    frozen = json.loads((OUT/'S3_metrics.json').read_text())['after']['total']
    assert all(result['before']['total'][k] == frozen[k] for k in ('tp','fp','fn','known_slots','unknown_slots'))
    def atomic(ms):
        out=[]
        for kind,value in ms:
            if kind == 'compound':
                out.extend(('accent' if p in ('acute','grave','circumflex') else 'breathing',p)
                           for p in value.split('+'))
            else:
                out.append((kind,value))
        return out
    result['atomic'] = {key:pooled([score_slots([dict(s,truth=atomic(s['truth']) if s['truth'] is not None else None,
                                                           detected=atomic(s[key]),unknown_kinds=[]) for s in l['slots']])
                                               for l in held]) for key in ('before','detected')}
    result['per_book'] = {d:dict(before=metric([l for l in held if l['doc']==d],'before'),
                               after=metric([l for l in held if l['doc']==d],'detected')) for d in sorted({l['doc'] for l in held})}
    capitals = [s for l in held for s in l['slots'] if s['base'].isupper()
                and s['truth'] and any(k != 'apostrophe' for k,v in s['truth'])]
    result['capitals'] = {k:score_slots([dict(s,detected=s[k],unknown_kinds=[]) for s in capitals]) for k in ('before','detected')}
    result['capital_slots'] = len(capitals)
    eligible = [(l,s) for l in rows for s in l['slots'] if s['truth']==[] and (s['base'] in 'δβλθφξζ' or s['base'].isupper())]
    result['ascender'] = {split:dict(n=len(ss), before=sum(bool(s['before_above']) for s in ss),
                                   after=sum(bool(s['above']) for s in ss))
                          for split,ss in [('all',[s for l,s in eligible]),('held-out',[s for l,s in eligible if not l['dev']])]}
    result['per_class'] = {}
    classes = sorted(set(model.classes))
    known = [s for l in held for s in l['slots'] if s['truth'] is not None]
    for cls in classes:
        target = mark_set(cls)
        tp = sum(set(map(tuple,s['truth']))==target and set(map(tuple,s['detected']))==target for s in known)
        support = sum(set(map(tuple,s['truth']))==target for s in known)
        predicted = sum(set(map(tuple,s['detected']))==target for s in known)
        result['per_class'][cls] = dict(support=support,predicted=predicted,tp=tp,
                                       recall=tp/support if support else None,
                                       precision=tp/predicted if predicted else None,
                                       fit=model.meta['fit_counts'].get(cls,0))
        bt = sum(set(map(tuple,s['truth']))==target and set(map(tuple,s['before']))==target for s in known)
        bp = sum(set(map(tuple,s['before']))==target for s in known)
        result['per_class'][cls]['before_precision'] = bt/bp if bp else None
        result['per_class'][cls]['before_recall'] = bt/support if support else None
    result['model_sha256'] = hashlib.sha256((ROOT/'docs/records/labelfix/markshape_model_S4.json').read_bytes()).hexdigest()
    (OUT/'S4_metrics.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('before','after','capital_slots','ascender','elapsed_seconds')},ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
