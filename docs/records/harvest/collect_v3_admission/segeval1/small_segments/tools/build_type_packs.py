"""Q3 adapter: common IO reused; build_packs has bed-specific render/selection.
Unlike that builder, copy original PNG bytes; no options, render or r2.
"""
import json,math,random,secrets,shutil
from ss4_common import *
def build():
    check_scanner()
    if any(PACK_ROOT.iterdir()): raise ValueError('PACK_ROOT must be empty; do not overwrite runs')
    data=rows(SS/'q3/sample.jsonl'); controls=json.loads((SS/'q3/LEAD_CONTROLS.json').read_text())['controls']; byid={r['line_id']:r for r in data}
    assert len(byid)==len(data) and set(controls)<=set(byid)
    bed=[r for r in data if r['line_id'] not in controls]; rng=random.Random(20261019); rng.shuffle(bed)
    n=math.ceil(len(bed)/90); assert 8*n>=len(controls) or 10*n>=len(controls)
    ctl=list(controls); rng.shuffle(ctl); nc=max(8,min(10,round(len(bed)/n*.1))); assert nc<=len(ctl) and nc*n>=len(ctl)
    key=dict(seed=20261019,contexts={},items={}); offset=0
    for i in range(n):
        ctx=f't{i+1:02d}'; size=len(bed)//n+(i<len(bed)%n)
        selected=[ctl[(i*nc+j)%len(ctl)] for j in range(nc)]
        records=bed[offset:offset+size]+[byid[x] for x in selected]; offset+=size; rng.shuffle(records)
        rd=PACK_ROOT/'type'/ctx/'r1'; (rd/'crops').mkdir(parents=True)
        public=[]
        for r in records:
            cid='k'+secrets.token_hex(5)
            while cid in key['items']: cid='k'+secrets.token_hex(5)
            p=Path(r['crop_path']); digest=sha(p); assert digest==r['crop_sha256']
            crop=f'crops/{digest}.png'; shutil.copyfile(p,rd/crop)
            public.append(dict(card_id=cid,crop=crop,google_text=r['raw_text']))
            meta=dict(line_id=r['line_id'],control=r['line_id'] in controls)
            if meta['control']: meta['expected']=controls[r['line_id']]
            key['items'][cid]=meta
        jsonl(rd/'cards.jsonl',public)
        key['contexts'][ctx]=dict(card_ids=[r['card_id'] for r in public],bed=size,controls=nc)
        shutil.copyfile(SS/'prompts/type.md',SS/'q3/prompts_rendered'/f'{ctx}.md')
    dump(SS/'q3/keys/type.json',key)
if __name__=='__main__': build()
