import gzip, json, glob
root = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/l1f_3680752/shards'
out = []; gaps = []
for p in sorted(glob.glob(root + '/*/frames.jsonl.gz')):
    for line in gzip.open(p, 'rt'):
        r = json.loads(line); f = r['frame_confidences']
        d = abs(sum(f)/len(f) - r['recognition_confidence']); gaps.append(d)
        if d > 2e-7:
            out.append(dict(line_id=r['line_id'], shard=p.split('/')[-2], frame_confidences=f,
                            recognition_confidence=r['recognition_confidence'], image_width=r['image_width'], gap=d))
print(json.dumps(dict(rows=len(gaps), max_gap=max(gaps), above_2e7=len(out), above_1e6=sum(g > 1e-6 for g in gaps), witnesses=out)))
