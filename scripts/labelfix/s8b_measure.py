"""S8b single offline detector pass; fixed document split and saved readers.

Outputs only under S8_DEV/s8b. Cached detector records are source/hash bound;
reaggregating evidence never repeats or retunes the detector measurement.
"""
import os
import sys
sys.dont_write_bytecode = True
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[key] = '1'
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', GIT_OPTIONAL_LOCKS='0')
import collections as C
from copy import deepcopy
import gzip
import json
from pathlib import Path
import time
import numpy as np
from PIL import Image
from scripts.labelfix import s8_prepare as p, s8_score_truth as t

OUT = p.OUT/'s8b'
SOURCE_PATHS = [p.ROOT/'greekocr/labelfix'/(s+'.py') for s in ('ink','case','segmentation','markshape','reading','text','release_gate')]


def audit(event, args):
    if event.startswith('socket.'):
        raise RuntimeError('S8b network OFF')
    paths = []
    if event == 'open':
        path, mode, flags = args
        if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
            paths = [path]
    elif event in ('os.mkdir','os.remove','os.rmdir','os.chmod','os.truncate'):
        paths = [args[0]]
    elif event in ('os.rename','os.link','os.symlink'):
        paths = args[:2]
    for path in paths:
        if isinstance(path, int):
            continue
        target = Path(os.fsdecode(path)).resolve()
        if target != OUT and OUT not in target.parents:
            raise RuntimeError('S8b write outside evidence boundary: '+str(target))


sys.addaudithook(audit)


def dump(name, obj):
    p.dump(OUT/name, obj)


def write(name, rows):
    p.write(OUT/name, rows)


def read_record(path):
    return json.loads(gzip.decompress(Path(path).read_bytes()))


def freeze():
    sources = {str(x.relative_to(p.ROOT)): p.sha(x) for x in SOURCE_PATHS}
    sources['split.json'] = p.sha(OUT/'split.json')
    lock = OUT/'candidate_lock.json'
    if lock.exists():
        measured = p.load(lock)
        if measured != sources:
            amendment = p.load(OUT/'fixture_compatibility.json')
            assert amendment['measured_sources'] == measured and amendment['final_sources'] == sources
            # Only the missing-area fixture fallback is allowed. Native
            # toolkit Components always have area, so that branch is unchanged.
            before = (OUT/'measured_case.py').read_text()
            after = (p.ROOT/'greekocr/labelfix/case.py').read_text()
            assert before.replace('c.area>=.20*ink.xh*ink.xh',
                "(c.area if hasattr(c,'area') else int(component_mask(ink,c).sum()))>=.20*ink.xh*ink.xh") == after
            assert all(measured[k] == v for k,v in sources.items() if k != 'greekocr/labelfix/case.py')
        return p.digest(measured)
    else:
        dump('candidate_lock.json', sources)
    return p.digest(sources)


def detect(crop, text, al, model):
    with Image.open(crop) as im:
        ci = p.ink.analyse(im)
    labels, native = ci.labels.copy(), ci.ink.copy()
    reading = p.reading.read_ink(ci, text, al, model, filtered=False)
    assert np.array_equal(ci.labels, labels) and np.array_equal(ci.ink, native)
    boundary_exceptions = []
    for s in reading.slots:
        ev = s['evidence']
        for side in ('above','below'):
            for b in getattr(ev, side):
                pixels = b.pixel_keys()
                assert len(pixels) == b.area and all(native[y,x] for y,x in pixels)
                assert all(int(labels[y,x]) in b.source_ids for y,x in pixels)
                if side == 'above' and b.source != 'preposed':
                    if b.y1 > ev.meanline:
                        boundary_exceptions.append(dict(start=s['start'],side=side,
                            bbox=[b.x0,b.y0,b.x1,b.y1],boundary=ev.meanline))
                if side == 'below':
                    if b.y0 < ev.baseline:
                        boundary_exceptions.append(dict(start=s['start'],side=side,
                            bbox=[b.x0,b.y0,b.x1,b.y1],boundary=ev.baseline))
    ci.font_fit['boundary_exceptions'] = boundary_exceptions
    return p.gate.serialize(reading), ci.font_fit


def aggregate(records):
    counters = C.Counter()
    for r in records:
        counters.update({k:v for k,v in r['metrics'].items() if k != 'components_per_letter_histogram'})
    return dict(lines=len(records), **counters,
        rates_percent={k:100*counters[k]/counters['letters'] if counters['letters'] else None for k in p.METRICS})


def score(rows, family, variant, seed):
    def count(r, event):
        return r['presence'][variant]['counts'][family][event]
    out = dict(counts={event:dict(raw=sum(count(r,event) for r in rows),
        weighted=sum(r['weight']*count(r,event) for r in rows)) for event in ('TP','FP','FN','TN')})
    for name, err in (('precision','FP'),('recall','FN')):
        out[name] = t.estimate(rows, lambda r:count(r,'TP'), lambda r:count(r,'TP')+count(r,err), seed)
    return out


def paired_delta(rows, family, metric, seed):
    err = 'FP' if metric == 'precision' else 'FN'
    docs = sorted({r['line_id'].split('-p')[0] for r in rows})
    if not docs:
        return None
    ix = {d:i for i,d in enumerate(docs)}
    matrix = np.zeros((len(docs),4))
    for r in rows:
        values = []
        for variant in ('before','after'):
            c = r['presence'][variant]['counts'][family]
            values += [r['weight']*c['TP'],r['weight']*(c['TP']+c[err])]
        matrix[ix[r['line_id'].split('-p')[0]]] += values
    totals = np.random.default_rng(seed).multinomial(len(docs),np.full(len(docs),1/len(docs)),size=t.REPS) @ matrix
    valid = (totals[:,1]>0)&(totals[:,3]>0)
    diffs = totals[valid,2]/totals[valid,3]-totals[valid,0]/totals[valid,1]
    total = matrix.sum(axis=0)
    return dict(value=float(total[2]/total[3]-total[0]/total[1]) if total[1] and total[3] else None,
        document_bootstrap95=np.quantile(diffs,[.025,.975]).tolist() if len(diffs) else None,valid_replicates=int(valid.sum()))


def main():
    frozen = freeze()
    sources = p.load(p.E/'sources.json')
    split = p.load(OUT/'split.json')['documents']
    remote = read_record(p.E/'remote.json.gz')
    truth = [r for r in p.rows(p.E/'dev_truth.jsonl.gz') if r.get('type')=='item' and not r['control'] and r['status']=='resolved']
    census = p.rows(p.E/'word_census.jsonl')
    ids = sorted({r['line_id'] for r in census})
    p.case.configure_model(p.ROOT/'docs/records/labelfix/case_model_S5.json')
    model = p.markshape.load_model(p.ROOT/'docs/records/labelfix/markshape_model_S4.json')
    before, after, originals = {}, {}, {}
    started = time.monotonic()
    custody = []
    for i,lid in enumerate(ids,1):
        original_path = p.E/'baseline/original'/(lid+'.json.gz')
        original = read_record(original_path)
        masked_path = p.OUT/'masked/baseline/masked'/(lid+'.json.gz')
        prior = read_record(masked_path) if masked_path.exists() else original
        crop = Path(prior['crop'])
        assert p.sha(crop) == prior['crop_sha256']
        saved = remote['runtime'][lid]
        alignment = p.Alignment.from_record(remote['alignments'][lid]['alignment'])
        assert p.nfd(saved['recogniser_text']) == alignment.prediction
        before[lid], originals[lid] = prior, original
        cache = OUT/'dev_detector'/(lid+'.json.gz')
        if cache.exists():
            record = read_record(cache)
            assert record['candidate_binding'] == frozen and record['crop_sha256'] == prior['crop_sha256']
        else:
            serial, font = detect(crop,alignment.prediction,alignment,model)
            runtime = deepcopy(saved)
            runtime['detector'] = serial
            modes = {m:p.gate.compose_runtime(runtime,m) for m in p.MODES}
            record = dict(id=lid,wave=sources[lid]['wave'],crop=str(crop),crop_sha256=p.sha(crop),
                candidate_binding=frozen,detector=serial,font_fit=font,metrics=p.metrics(serial),modes=modes)
            cache.parent.mkdir(exist_ok=True)
            cache.write_bytes(gzip.compress(json.dumps(record,ensure_ascii=False,allow_nan=False).encode(),mtime=0))
        after[lid] = record
        custody.append(dict(id=lid,before_path=str(masked_path if masked_path.exists() else original_path),
            before_sha256=p.sha(masked_path if masked_path.exists() else original_path),
            after_sha256=p.sha(cache),crop=str(crop),crop_sha256=p.sha(crop)))
        if i%100 == 0:
            print(f'S8b DEV detector {i}/600; {time.monotonic()-started:.1f}s',flush=True)
    write('dev_input_custody.jsonl',custody)
    byline = C.defaultdict(list)
    for r in truth:
        byline[r['line_id']].append(r)
    scores = []
    for lid, rr in byline.items():
        saved = remote['runtime'][lid]
        forms = dict(google=sources[lid]['label'],r1_A=p.r1_text(saved,canonical=False),
            detector_original=originals[lid]['detector']['text'],frozen_AB=originals[lid]['modes']['ENSEMBLE_AB']['text'],
            before=before[lid]['detector']['text'],after=after[lid]['detector']['text'])
        groups = p.word_groups(saved['recogniser_nfd'],forms,retain_raw=True)
        for r in rr:
            g = next(x for x in groups if (x['start'],x['end'])==(r['start'],r['end']))
            result = {k:r[k] for k in ('id','uid','line_id','wave','start','end','truth','weight','selection')}
            result.update(half=split[lid.split('-p')[0]]['half'],presence={},forms={v:g['forms'][v] for v in ('before','after')})
            for variant, record in (('before',before[lid]),('after',after[lid])):
                slots = [s for s in record['detector']['slots'] if r['start']<=s['start']<r['end'] and t.letter(s)]
                dummy = dict(r,forms=dict(r['forms'],detector_original=g['forms'][variant]))
                result['presence'][variant], _ = t.score_presence(dummy,'detector_original',slots)
            scores.append(result)
    assert len(scores)==976
    write('dev_scores.jsonl.gz',scores)
    metrics, diagnostics, gates = {}, {}, {}
    for half in ('JUDGE','TUNE','ALL'):
        metrics[half],diagnostics[half],gates[half] = {},{},{}
        for wi,wave in enumerate(t.WAVES):
            rr = [r for r in scores if r['wave']==wave and (half=='ALL' or r['half']==half)]
            metrics[half][wave] = dict(cards=len(rr),weight=sum(r['weight'] for r in rr),
                documents=len({r['line_id'].split('-p')[0] for r in rr}),
                families={k:{v:score(rr,k,v,t.SEED+wi) for v in ('before','after')}|
                    dict(paired_change={m:paired_delta(rr,k,m,t.SEED+wi) for m in ('precision','recall')}) for k in t.KINDS})
            lids = {r['line_id'] for r in scores if r['wave']==wave and (half=='ALL' or r['half']==half)}
            diagnostics[half][wave] = {v:aggregate([b[l] for l in lids]) for v,b in (('before',before),('after',after))}
            gates[half][wave] = {v:{m:dict(C.Counter(b[l].get('decisions',b[l]['modes'])[m].get('status','proposal') for l in lids)) for m in p.MODES}
                for v,b in (('before',before),('after',after))}
    # Full 600-line diagnostics also include lines with no adjudicated words.
    diagnostics['full600'] = {wave:{v:aggregate([b[l] for l in ids if sources[l]['wave']==wave])
        for v,b in (('before',before),('after',after))} for wave in t.WAVES}
    dump('dev_summary.json',metrics)
    dump('dev_diagnostics.json',diagnostics)
    dump('dev_gate_proposals.json',gates)
    dump('dev_receipt.json',dict(candidate_binding=frozen,lines=len(ids),resolved_cards=len(scores),
        detector_runs_total=len(ids),ctc_runs=0,r1_runs=0,network=False,elapsed_seconds=time.monotonic()-started,
        truth_sha256=p.sha(p.E/'dev_truth.jsonl.gz'),split_sha256=p.sha(OUT/'split.json'),
        candidate_sources=p.load(OUT/'candidate_lock.json'),all_resolved_words_scored=True,
        masks=sum('masked/baseline' in x['before_path'] for x in custody)))
    assert freeze()==frozen
    print('DEV measurement complete; no per-wave scores printed before regressions.',flush=True)


if __name__ == '__main__':
    main()
