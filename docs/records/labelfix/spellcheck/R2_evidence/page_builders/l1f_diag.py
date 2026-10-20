import gzip, json, math, glob, sys
from collections import Counter
root = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1f_3680752/shards'
def score(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) and 0<=v<=1
reasons = Counter(); ex = {}; worst = 0.0; n = 0
for p in sorted(glob.glob(root + '/*/frames.jsonl.gz')):
    for line in gzip.open(p, 'rt'):
        r = json.loads(line); n += 1
        f = r['frame_confidences']; c = r['recognition_confidence']; w = r['image_width']
        bad = []
        if not score(c): bad.append('conf_not_score:%r' % (type(c).__name__))
        if not f: bad.append('no_frames')
        elif not all(score(v) for v in f): bad.append('frame_not_score')
        if not isinstance(w, int) or isinstance(w, bool) or w <= 0: bad.append('width:%r' % (w,))
        if f and score(c) and all(score(v) for v in f):
            d = abs(sum(f)/len(f) - c); worst = max(worst, d)
            if d > 2e-7: bad.append('mean_gap')
        for b in bad:
            reasons[b] += 1
            ex.setdefault(b, (r['line_id'], c, len(f) if f else 0, w, (abs(sum(f)/len(f)-c) if f and score(c) else None)))
print('rows', n, 'ok', n - sum(1 for _ in []), 'max_mean_gap', worst)
for k, v in reasons.most_common(): print(k, v, ex[k])
