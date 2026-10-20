"""CAPS3 offline screen and frozen T6b worker orchestration (two processes)."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS','BLIS_NUM_THREADS'):
    os.environ[name]='1'
import importlib.util
import io
import inspect
import subprocess
import json
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[4]
sys.path.insert(0,str(REPO))
_spec=importlib.util.spec_from_file_location('caps1_build',BASE/'caps1/build.py')
caps1=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(caps1)
OUT=BASE/'caps_masked'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

def network_off():
    def audit(event,args):
        if event.startswith('socket.'):raise PermissionError('CAPS3 network OFF: '+event)
    sys.addaudithook(audit)

def original(row):
    from PIL import Image
    meta=json.loads((caps1.W1/'pages'/(row['page_id']+'.json')).read_text())
    path=Path(meta['image'])
    assert caps1.sha(path)==meta['image_sha256']
    with Image.open(path) as im: crop=im.crop(tuple(row['crop_bbox']))
    buf=io.BytesIO();crop.save(buf,format='PNG',compress_level=3)
    assert hashlib.sha256(buf.getvalue()).hexdigest()==row['crop_sha256']
    return crop

def clip_measure(crop):
    from greekocr.verify.images import image_checks
    from greekocr.verify.calibration import RULES, _predict
    c=image_checks(crop)
    fractions=c.edge_ink_fraction
    flags={side:_predict(fractions[side],*RULES['cut_'+side][1:]) for side in ('left','right')}
    return dict(edge_ink_fraction={s:fractions[s] for s in flags}, sides=flags, flagged=any(flags.values()))

def frozen_caps1_inputs():
    """Freeze the manifest input to the exact version used for CAPS1/CAPS3 start."""
    manifest=HERE/'keys/release_exclusions_at_start.json'
    assert caps1.sha(manifest)=='aaa579dce6338d95ea5d50ccece45e9b364571ebaea3b0d58c878fabde02eae3'
    source=inspect.getsource(caps1.release_exclusions)
    old="manifest = EXCLUSIONS / 'release_exclusions.json'"
    assert source.count(old)==1
    namespace=dict(caps1.__dict__,CAPS3_MANIFEST=manifest)
    exec(compile(source.replace(old,'manifest = CAPS3_MANIFEST'),str(BASE/'caps1/build.py'),'exec'),namespace)
    original_loader=caps1.release_exclusions
    caps1.release_exclusions=namespace['release_exclusions']
    try:return caps1.load_inputs()
    finally:caps1.release_exclusions=original_loader

def screen():
    network_off()
    pool,_,_,bindings,_,_=frozen_caps1_inputs()
    assert len(pool)==2211
    caps1.jsonl(HERE/'keys/pool.jsonl',pool)
    if '--resume' in sys.argv:
        measurements=caps1.rows(HERE/'screen.jsonl')
    else:
        measurements=[]
        for i,row in enumerate(pool):
            m=dict(id=row['id'],source=row['source'],crop_sha256=row['crop_sha256'],**clip_measure(original(row)))
            measurements.append(m)
            if (i+1)%200==0:print('screen',i+1,flush=True)
        caps1.jsonl(HERE/'screen.jsonl',measurements)
    byid={m['id']:m for m in measurements}
    key=json.loads((BASE/'caps1/keys/caps1.json').read_text())
    verdicts=sum([caps1.rows(BASE/'caps1/answers/caps1'/f'{c}.mapped.jsonl') for c in ('c1','c2')],[])
    checks=[]
    for v in verdicts:
        # Mapped records carry their source line id.
        rid=v.get('line_id') or v['card_id']
        checks.append(dict(id=rid,verdict=v,flagged=byid[rid]['flagged']))
    clipped=[r for r in checks if 'crop_clipped' in r['verdict']['errors']]
    good=[r for r in checks if r['verdict']['crop_ok']=='y']
    assert len(clipped)==6 and len(good)==89
    for context in ('c1','c2'):
        vp=BASE/'caps1/answers/caps1'/f'{context}.mapped.jsonl'
        bindings[str(vp)]=caps1.sha(vp)
    report=dict(pool=len(pool),removed=sum(m['flagged'] for m in measurements),
        removed_per_source={s:sum(m['flagged'] for m in measurements if m['source']==s) for s in sorted({r['source'] for r in pool})},
        clipped_flagged=sum(r['flagged'] for r in clipped),clipped_n=6,fp=sum(r['flagged'] for r in good),crop_ok_n=89,
        helper='greekocr.verify.images.image_checks; greekocr.verify.calibration._predict + RULES[cut_left/cut_right]',
        tolerance={'cut_left':['left_fraction','gt',0.0],'cut_right':['right_fraction','gt',0.0]},inputs=bindings,
        helper_sources={str(REPO/p):caps1.sha(REPO/p) for p in ('greekocr/verify/images.py','greekocr/verify/calibration.py','greekocr/real/geometry.py')},caps2_validation=checks)
    caps1.dump(HERE/'screen_receipt.json',report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs','caps2_validation')},indent=2))

def mask():
    network_off()
    t6b=load('caps3_t6b',BASE/'run.py')
    binding=t6b.frozen()
    # Bind the exact checked worker, matcher, audit and library; redirect output only.
    t6b.BASE=OUT
    t6b.frozen=lambda:binding
    sys.path.insert(0,str(BASE))
    pool=caps1.rows(HERE/'keys/pool.jsonl')
    flags={r['id']:r['flagged'] for r in caps1.rows(HERE/'screen.jsonl')}
    selected=[r for r in pool if not flags[r['id']]]
    pages=defaultdict(list)
    for r in selected:pages[(r['source'],r['page_id'])].append(r)
    selections=[]
    for (source,pid),rows in sorted(pages.items()):
        meta=json.loads((caps1.W1/'pages'/(pid+'.json')).read_text())
        selections.append(dict(source=source,page_id=pid,raster_sha256=meta['image_sha256'],guard_witness_budget=False,rows=rows))
    OUT.mkdir(exist_ok=True)
    for source in {r['source'] for r in selected}:
        for d in ('crops','curves','pages','guard_witnesses'):(OUT/source/d).mkdir(parents=True,exist_ok=True)
    (OUT/'tmp').mkdir(exist_ok=True)
    caps1.dump(OUT/'selection.json',selections)
    caps1.dump(OUT/'binding.json',dict(frozen=binding,workers=2,worker_model='fresh subprocess per page; nice 15',worker_source=str(BASE/'run.py'),population_filter_only=True,network='OFF'))
    print('mask pages',len(selections),'rows',len(selected),flush=True)
    (OUT/'logs').mkdir(exist_ok=True)
    def completed(page):
        root=OUT/page['source']/'pages'
        pp=root/(page['page_id']+'_provenance.json')
        rp=root/(page['page_id']+'.jsonl')
        if not pp.exists() or not rp.exists():return False
        provenance=json.loads(pp.read_text())
        records=caps1.rows(rp)
        if provenance['frozen']!=binding or {r['id'] for r in records}!={r['id'] for r in page['rows']}:return False
        return all(caps1.sha(OUT/r['masked_crop'])==r['masked_crop_sha256'] for r in records)
    pending=[i for i,page in enumerate(selections) if not completed(page)]
    caps1.dump(OUT/'binding.json',dict(frozen=binding,workers=2,worker_model='fresh subprocess per pending page; nice 15',resumed_pages=[selections[i]['page_id'] for i in range(len(selections)) if i not in pending],resume_validation='exact row coverage, frozen binding, every output SHA256; prior completed T6b worker records reused',worker_source=str(BASE/'run.py'),population_filter_only=True,network='OFF'))
    print('resume complete pages',len(selections)-len(pending),'pending',len(pending),flush=True)
    def launch(i):
        log=OUT/'logs'/(selections[i]['page_id']+'.log')
        with log.open('w') as stream:
            result=subprocess.run(['/usr/bin/nice','-n','15',sys.executable,'-B',str(HERE/'pipeline.py'),'worker',str(i)],cwd=REPO,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
        if result.returncode:raise RuntimeError('page failed: '+str(log)+'\n'+log.read_text()[-5000:])
        return log.read_text().splitlines()[-1]
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures=[executor.submit(launch,i) for i in pending]
        for count,future in enumerate(as_completed(futures),1):
            print(str(count)+'/'+str(len(pending))+' '+future.result(),flush=True)
    records=[]
    for s in selections:records+=caps1.rows(OUT/s['source']/'pages'/(s['page_id']+'.jsonl'))
    records.sort(key=lambda r:r['id'])
    caps1.jsonl(OUT/'records.jsonl',records)
    summary={}
    for source in sorted({r['source'] for r in pool}):
        rs=[r for r in records if r['source']==source]
        summary[source]=dict(total=len(rs),masked=sum(r['output_kind']=='masked' for r in rs),guarded=sum(r['wrong_line_risk'] for r in rs),unmatched=sum(not r['matched'] for r in rs),changed=sum(r['changed'] for r in rs))
    caps1.dump(OUT/'summary.json',summary)
    print(json.dumps(summary,indent=2))

def worker():
    network_off()
    t6b=load('caps3_page_t6b',BASE/'run.py')
    binding=t6b.frozen()
    t6b.BASE=OUT;t6b.frozen=lambda:binding
    sys.path.insert(0,str(BASE))
    t6b.worker(int(sys.argv[2]))

def parity():
    network_off()
    t6b=load('caps3_parity_t6b',BASE/'run.py')
    binding=t6b.frozen()
    selections=[]
    expected={}
    oldpages=json.loads((BASE/'selection.json').read_text())
    for source in ('gazette_modern','kosmopolis','lekythos'):
        candidates=[r for r in caps1.rows(BASE/source/'records.jsonl') if r['changed']]
        old=candidates[0]
        page=next(p for p in oldpages if p['source']==source and p['page_id']==old['page_id'])
        row=next(r for r in page['rows'] if r['id']==old['id'])
        selections.append(dict(page,rows=[row],guard_witness_budget=False))
        expected[row['id']]=old['masked_crop_sha256']
    out=OUT/'parity'
    out.mkdir(exist_ok=True)
    for source in ('gazette_modern','kosmopolis','lekythos'):
        for d in ('crops','curves','pages','guard_witnesses'):(out/source/d).mkdir(parents=True,exist_ok=True)
    (out/'tmp').mkdir(exist_ok=True)
    caps1.dump(out/'selection.json',selections)
    t6b.BASE=out;t6b.frozen=lambda:binding
    sys.path.insert(0,str(BASE))
    for i in range(3):t6b.worker(i)
    receipt=[]
    for page in selections:
        r=caps1.rows(out/page['source']/'pages'/(page['page_id']+'.jsonl'))[0]
        actual=caps1.sha(out/r['masked_crop'])
        assert actual==expected[r['id']]
        assert (out/r['masked_crop']).read_bytes()==(BASE/r['masked_crop']).read_bytes()
        receipt.append(dict(id=r['id'],sha256=actual,byte_identical=True,changed=r['changed']))
    caps1.dump(out/'receipt.json',receipt)
    print('3 T6b changed rows re-masked byte-identically',flush=True)

if __name__=='__main__':
    {'screen':screen,'mask':mask,'parity':parity,'worker':worker}[sys.argv[1]]()
