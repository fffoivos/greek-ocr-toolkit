"""Supplemental read-only checks of scalar receipt links and unreferenced metadata."""
import pathlib,json,hashlib
ROOT=pathlib.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019');RUN=ROOT/'output_3702849'
def load(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(p,w):
 h=sha(p);assert h==w,str(p);checks.append(dict(path=str(p.relative_to(RUN)),sha256=h))
for s in ('test','dev'):
 b=RUN/s;sf=load(b/'sf7/receipt.json');check(b/'recompose.json',sf['config_sha256'])
 assert load(b/'l1/alignment/binding.json')==load(b/'l1/alignment/summary.json')['binding']
 w=load(b/'windows_receipt.json')
 check(b/'l1/detector/detector_receipt.json',w['detector_receipt_sha256']);check(b/'l1/run_receipt.json',w['run_receipt_sha256']);check(b/'selection.jsonl',w['selection_sha256'])
 for e in w['entries']:check(b/'l1/detector'/('shard-%05d-receipt.json'%e['shard']),e['receipt_sha256'])
 detector=load(b/'l1/detector/detector_receipt.json');
 for path,h in detector['alignment_sha256'].items():check(pathlib.Path(path),h)
 ens=load(b/'ensemble/r1e_receipt.json');check(b/'l1/run_receipt.json',ens['historical_run_receipt_sha256']);check(b/'selection.jsonl',ens['selection_sha256'])
 for p in (b/'ensemble').glob('shard-*-receipt.json'):
  r=load(p);prefix=p.name.replace('-receipt.json','')
  check(b/'l1/combined'/(prefix+'-combined.jsonl.gz'),r['inputs']['historical_combined_sha256'])
  check(b/'l1/detector'/(prefix+'-receipt.json'),r['inputs']['window_receipt_sha256'])
print(json.dumps(dict(all_ok=True,checks=checks,alignment_binding_equals_summary=True),indent=2))
