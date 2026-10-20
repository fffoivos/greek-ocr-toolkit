"""Read-only full qualification, plus bounded real crop sample.
Run via stdin with core/pipeline modules supplied in memory; emits JSON only.
"""
from pipeline import *
import base64

def qualify():
    real,record=load_real();pools,blocked,text_audit=load_candidates()
    samples=defaultdict(list);crops=defaultdict(list)
    for r in real:
        parent=r['key'][0]
        if len(samples[parent])>=334:continue
        payload=Path(r['crop_path']).read_bytes();h=hashlib.sha256(payload).hexdigest();require(h==r['crop_sha256'],'sample crop SHA')
        with Image.open(io.BytesIO(payload)) as im:
            width=max(64,min(2560,math.floor(im.width*48/im.height+.5)))
        require(r['width'] is None or width==r['width'],'census bbox width disagrees with crop');r['width']=width
        samples[parent].append(r)
        if len(crops[parent])<20:crops[parent].append(dict(path=r['crop_path'],sha256=h,bytes=len(payload)))
    sample=[r for p in sorted(samples) for r in samples[p]][:1000]
    # Exercise shared real arithmetic paths, including M1 and all ruled M3/M4 weights.
    base=[(0,i,r['line_id']) for i,r in enumerate(sample)]+[(1,i,r['line_id']) for i,r in enumerate(pools[0][:1000])]
    try:replaced,ledger=replay(base,sample,pools[1],200,1);m1=dict(status='ok',sample_draws=len(replaced),ledger=ledger)
    except ValueError as e:m1=dict(status='stopped',reason=str(e))
    counts=Counter((r['dominant_script'],r['wave']=='parliament') for r in real)
    for capped in (False,True):script_quota(counts,{k for k in counts if k[0]=='cyrillic'},{k for k in counts if k[1]},capped)
    for alpha in (1,.5):temperature(Counter(r['wave'] for r in real),alpha,{'parliament'})
    return dict(record=record,text_audit=text_audit,arms=dict(M1=m1,M2=dict(status='ok'),M3=dict(status='ok' if record['M3_ok'] else 'stopped'),M4=dict(status='ok')),ref_sample=dict(rows=len(sample),parents={p:dict(rows=len(v),crops=crops[p]) for p,v in samples.items()},arithmetic=True),sample=sample)
if __name__=='__main__':print(json.dumps(qualify(),sort_keys=True))
