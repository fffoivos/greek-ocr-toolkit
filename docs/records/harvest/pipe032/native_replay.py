"""Replay the prescribed 150 + 888 natively against saved S5 verdict/reason."""
from pathlib import Path
from collections import Counter
import hashlib, json, os, signal, sys, time
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'docs/records/harvest/pipe032'
MAIN=ROOT.parent/'greek-ocr-toolkit-main-next'
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[key]='1'
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',PYTHONDONTWRITEBYTECODE='1')
def offline(event,args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo'):raise RuntimeError('PIPE032 network OFF')
sys.addaudithook(offline)
from greekocr.harvest.line_pipeline_native import NativeSegmenter
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    saved=MAIN/'docs/records/harvest/seg_steps/s5_adopt/replay.jsonl'
    rows=[r for r in map(json.loads,saved.read_text().splitlines()) if r['cohort'] in ('segeval1','calibration')]
    assert Counter(r['cohort'] for r in rows)=={'segeval1':150,'calibration':888}
    cp=ROOT.parent/'ocr-review-sites-20261018/qa/word-tolerance/context-evidence.json'
    contexts={r['id']:r for r in json.loads(cp.read_text())['rows']}
    predictor=MAIN/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'
    w=NativeSegmenter(json.loads((ROOT/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools'],predictor)
    def timeout(*args):raise TimeoutError('native row exceeded existing 120s bound')
    signal.signal(signal.SIGALRM,timeout)
    counts=Counter();diffs=[];started=time.monotonic()
    try:
        with (OUT/'native_replay.jsonl').open('w') as stream:
            for i,r in enumerate(rows,1):
                if r['cohort']=='calibration':w.context=lambda row,*args:contexts.get(row['id'],dict(status='unavailable',reason='no saved calibration source context'))
                else:w.context=NativeSegmenter.context.__get__(w)
                assert sha(r['row']['crop_path'])==r['row']['crop_sha256']
                signal.alarm(120)
                actual=w(r['row']);signal.alarm(0)
                before={k:r['after'][k] for k in ('verdict','reason')};after={k:actual[k] for k in ('verdict','reason')}
                rec=dict(cohort=r['cohort'],line_id=r['line_id'],crop_sha256=r['row']['crop_sha256'],before=before,after=after,equal=before==after)
                stream.write(json.dumps(rec,ensure_ascii=False)+'\n')
                counts[r['cohort']]+=rec['equal']
                if not rec['equal']:diffs.append(rec)
                if i%100==0:print('native replay',i,'/',len(rows),flush=True)
    finally:signal.alarm(0);w.close()
    receipt=dict(rows=len(rows),matching=dict(counts),differences=diffs,elapsed_seconds=time.monotonic()-started,
        saved=dict(path=str(saved),sha256=sha(saved)),contexts=dict(path=str(cp),sha256=sha(cp)),predictor=dict(path=str(predictor),sha256=sha(predictor)),network=False,readers=0,census=0)
    (OUT/'native_replay_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2));assert not diffs
if __name__=='__main__':main()
