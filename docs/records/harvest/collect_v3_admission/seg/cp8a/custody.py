"""Portable reader-custody check using repository copies only."""
import gzip,hashlib,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;CP7=HERE.parent/'cp7';ROOT=CP7.parents[4]
sys.path.insert(0,str(CP7))
from runtime_r2 import map_records

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def rows(p):return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()]
def validate():
    custody=[];controls=[];records=[]
    scored=[json.loads(l) for l in gzip.open(CP7/'r2/scored.jsonl.gz','rt')]
    by={r['row_id']:r for r in scored}
    approved={c['source_card']['card_id']:c for c in read(ROOT/'docs/harvest/recut_v1/w1_masked/caps1/keys/control_truth.json')}
    for bed in ('segcp7r2_a','segcp7r2_b'):
        public=HERE/'sol_packs'/bed/'r1';key=read(CP7/'r2/keys'/(bed+'.json'))
        manifest=read(public.parent/'MANIFEST.r1.json')['files']
        assert all(sha(public/p)==h for p,h in manifest.items())
        raw=CP7/'r2/answers'/bed
        mapped,control=map_records(rows(raw/'r1.jsonl'),rows(public/'cards.jsonl'),key)
        assert mapped==rows(raw/'r1.mapped.jsonl') and control==rows(raw/'r1.controls.jsonl')
        assert rows(public/'answers.jsonl')==rows(raw/'r1.jsonl')
        cards={r['card_id']:r for r in rows(public/'cards.jsonl')}
        for a in mapped:
            s=by[a['line_id']];assert s['reader']==a
            assert sha(public/cards[a['card_id']]['crop'])==s['crop_sha256']==key['items'][a['card_id']]['crop_sha256']
            records.append(s)
        for a in control:
            meta=key['items'][a['card_id']];ref=approved[meta['control_public_id']]['reference_verdict']
            assert ref==meta['reference_verdict']
            controls.append(dict(passed=all(a[f]==ref[f] for f in ('letters','marks','crop_ok'))))
        scan=read(CP7/'r2/scan'/bed/'r1.scan.json')
        assert scan['ok'] and not scan['violations'] and not scan['manifest_check_skipped']
        assert hashlib.sha256(gzip.decompress((HERE/'rollouts'/(bed+'.jsonl.gz')).read_bytes())).hexdigest()==scan['rollout_sha256']
        custody.append(dict(context=bed,mapped=len(mapped),controls=len(control),scan_ok=True,violations=0,rollout_sha256=scan['rollout_sha256'],portable=True))
    return records,controls,custody
