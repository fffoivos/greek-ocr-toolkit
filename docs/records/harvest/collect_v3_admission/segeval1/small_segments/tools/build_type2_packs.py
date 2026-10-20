"""SS4b: retain type membership, fresh IDs and seeded per-context order."""
import copy,json,random,secrets,shutil
from ss4_common import *
from scan_type_packs import scan

def build():
    check_scanner()
    target=PACK_ROOT/'type2'
    if target.exists() or (SS/'q3/keys/type2.json').exists():
        raise ValueError('refuse overwrite of type2')
    old=json.loads((SS/'q3/keys/type.json').read_text())
    source={r['line_id']:r for r in rows(SS/'q3/sample.jsonl')}
    rng=random.Random(20261020)
    key=dict(seed=20261020,layout='type2',contexts={},items={})
    for ctx,c in old['contexts'].items():
        ids=list(c['card_ids']); rng.shuffle(ids)
        rd=target/ctx/'r1'; (rd/'img').mkdir(parents=True)
        public=[]
        for oid in ids:
            meta=copy.deepcopy(old['items'][oid]); r=source[meta['line_id']]
            cid='k'+secrets.token_hex(5)
            while cid in old['items'] or cid in key['items']: cid='k'+secrets.token_hex(5)
            src=Path(r['crop_path']); digest=sha(src)
            if digest!=r['crop_sha256']: raise ValueError('source changed')
            crop=f'img/{digest}.png'; shutil.copyfile(src,rd/crop)
            public.append(dict(card_id=cid,crop=crop,google_text=r['raw_text']))
            key['items'][cid]=meta
        jsonl(rd/'items.jsonl',public)
        key['contexts'][ctx]=dict(card_ids=[r['card_id'] for r in public],bed=c['bed'],controls=c['controls'])
        prompt=SS/'q3/prompts_rendered/type2'/f'{ctx}.md'; prompt.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(SS/'prompts/type.md',prompt)
    dump(SS/'q3/keys/type2.json',key)
    results=[scan(ctx,layout='type2') for ctx in key['contexts']]
    dump(SS/'q3/TYPE2_PACK_SCAN.json',results)
    if any(not r['ok'] for r in results): raise ValueError('closure failed')
    print(json.dumps({ctx:{k:v for k,v in c.items() if k!='card_ids'} for ctx,c in key['contexts'].items()}))
if __name__=='__main__': build()
