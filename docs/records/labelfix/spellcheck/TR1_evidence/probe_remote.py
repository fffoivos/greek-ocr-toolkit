"""Read-only Clariden metadata probe. No inference and no remote writes."""
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path

B = Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3')


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


result = {'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'roots': {}, 'receipts': {}, 'imports': {}}
sets = {}
for split in ['test', 'dev']:
    p = B / 'collection_v2' / ('import_real_v2_' + split + '.jsonl')
    rr = [json.loads(s) for s in p.open()]
    sets[split] = {r['id'] for r in rr if r['script_class'] == 'greek_poly'}
    result['imports'][split] = dict(path=str(p), sha256=sha(p), total=len(rr),
                                   eligible=len(sets[split]))
p = B / 'labelfix_l1_20261017/artifacts/labelfix_l1/binding/selection.jsonl'
ss = {json.loads(s)['id'] for s in p.open()}
result['selection'] = dict(path=str(p), sha256=sha(p), lines=len(ss),
                          intersections={k: len(v & ss) for k, v in sets.items()})
for name in ['labelfix_l1_20261017', 'labelfix_r1_20261016']:
    files = []
    for d, ds, fs in os.walk(B / name):
        ds[:] = [s for s in ds if not s.startswith('shard-') and s not in
                 ['.git', '__pycache__', 'greekocr', 'tests', 'shards', 'partials',
                  'detector', 'combined', 'inference', 'release', 'inventory', 'windows']]
        for f in fs:
            if f.endswith(('.json', '.jsonl', '.jsonl.gz', '.json.gz')) and any(
                    s in f for s in ['receipt', 'summary', 'selection', 'dev', 'test', 'alignments']):
                p = Path(d) / f
                files.append(dict(path=str(p.relative_to(B)), bytes=p.stat().st_size))
    result['roots'][name] = files
paths = [
    'labelfix_l1_20261017/output_3679313/run_receipt.json',
    'labelfix_l1_20261017/output_3679313/input_receipt.json',
    'labelfix_l1_20261017/output_3679313/combined/r1_receipt.json',
    'labelfix_l1_20261017/output_3679313/detector/detector_receipt.json',
    'labelfix_l1_20261017/output_3679313/alignment/summary.json',
    'labelfix_l1_20261017/l1e_20261017/output_3679545/inference/r1e_receipt.json',
    'labelfix_l1_20261017/l1e_20261017/output_3679545/run_receipt.json',
    'labelfix_l1_20261017/s8_dev_extract/receipt.json',
    'labelfix_l1_20261017/l1f_3680752/receipt.json',
    'labelfix_c1_20261016/output_3678590/summary.json',
    'labelfix_r1_20261016/output_3678928/run_receipt.json']
for rel in paths:
    p = B / rel
    if p.exists():
        r = json.loads(p.read_text())
        result['receipts'][rel] = dict(sha256=sha(p), keys=list(r),
            scalar_fields={k: v for k, v in r.items() if not isinstance(v, (list, dict))})
        if rel.endswith('input_receipt.json') or 's8_dev_extract' in rel:
            result['receipts'][rel]['content'] = r
print(json.dumps(result, indent=2))
