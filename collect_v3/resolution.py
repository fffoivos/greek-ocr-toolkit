"""Durable item/page resolution with W1 spread across the full planned books.

Metadata/PDF bounds are resolved before OCR. W1 and W2 share the same seeded
allocation, with 20% per book where possible; no paid read happens here.
"""
from pathlib import Path
import random
from .common import rows,read_json,write_json,sha,sha_bytes
from .config import SPECS,ITEM_CAPS
from .planner import split_waves


def resolve_source(out,source,tranche,routes,seed,price=1500):
    out=Path(out);orderpath=out/'item_draws'/f'{source}.jsonl'
    if not orderpath.exists():orderpath=Path(str(orderpath)+'.gz')
    if not orderpath.exists():raise ValueError('portable item order missing; rerun offline plan')
    order=rows(orderpath);identity=dict(item_order_sha256=sha(orderpath),seed=seed,schema=2)
    statepath=out/'resolution'/(source+'.json')
    state=read_json(statepath) if statepath.exists() else dict(identity=identity,cursor=0,allocated=[],tranches={},excluded_items=[])
    if state['identity']!=identity:raise ValueError('item order changed after bounds resolution')
    if tranche=='W2' and not state['tranches'].get('W1'):raise ValueError('W2 requires complete W1 resolved draw')
    if state['tranches'].get(tranche):return state['tranches'][tranche]
    blocked=set()
    for wave in ('W1','W2'):
        for r in rows(out/f'{wave}_manifest.jsonl'):
            if r.get('source')!=source and r.get('item_record'):
                item=r['item_record'];blocked.add((item['provider'],item['id']))
    for p in (out/'resolution').glob('*.json'):
        if p.stem==source:continue
        for r in read_json(p).get('allocated',[]):
            item=r['item_record'];blocked.add((item['provider'],item['id']))
    total=SPECS[source][0]
    while len(state['allocated'])<total:
        if state['cursor']>=len(order):raise ValueError(f'{source}: eligible resolved frame exhausted at {len(state["allocated"])}/{total} pages')
        entry=order[state['cursor']];item=entry['item_record']
        if (item['provider'],item['id']) in blocked:
            state['excluded_items'].append(dict(item=item['id'],reason='already allocated to another source cohort'));state['cursor']+=1;write_json(statepath,state);continue
        try:resolved=routes.resolve(item)
        except ValueError as e:
            if source=='kosmopolis' and item['id']=='xrysallis-4141':raise ValueError('required remaining pre-1900 Kosmopolis issue unavailable') from e
            state['excluded_items'].append(dict(item=item['id'],reason=str(e)));state['cursor']+=1;write_json(statepath,state);continue
        leaves=resolved.get('valid_leaves') or (list(range(resolved['page_count'])) if item['route']=='ia' else list(range(1,resolved['page_count']+1)))
        n=min(entry['quota'],ITEM_CAPS.get(source,40),len(leaves),total-len(state['allocated']))
        if not n:
            if source=='kosmopolis' and item['id']=='xrysallis-4141':raise ValueError('required pre-1900 Kosmopolis issue has no pages')
            state['excluded_items'].append(dict(item=item['id'],reason='empty page bounds'));state['cursor']+=1;write_json(statepath,state);continue
        chosen=random.Random(entry['page_seed']).sample(leaves,n)
        for slot,page in enumerate(chosen):
            prefix=source+'--'+sha_bytes(item['id'].encode())[:16]
            state['allocated'].append(dict(id=f'{prefix}--s{slot:03d}',source=source,item=item['id'],item_record=item,item_rank=entry['item_rank'],item_pages=n,page=page,page_slot=slot,page_seed=entry['page_seed'],resolve_at_run=False,bounds_basis=resolved.get('bounds_basis','resolved provider page count'),seed=seed,route=item['route'],rights=entry['rights'],projected_micro_usd=price,exclusion_manifest_sha256=entry.get('exclusion_manifest_sha256')))
        if hasattr(routes,'prepare_pages'):
            try:routes.prepare_pages(state['allocated'][-n:])
            except ValueError as e:
                # Download/render failure (network, status, access) stops this item only, like resolve().
                del state['allocated'][-n:]
                if source=='kosmopolis' and item['id']=='xrysallis-4141':raise ValueError('required remaining pre-1900 Kosmopolis issue unavailable') from e
                state['excluded_items'].append(dict(item=item['id'],reason='prepare: '+str(e)));state['cursor']+=1;write_json(statepath,state);continue
        state['cursor']+=1;write_json(statepath,state)
    split_waves(state['allocated'],total)
    state['tranches']['W1']=[r for r in state['allocated'] if r['tranche']=='W1']
    state['tranches']['W2']=[r for r in state['allocated'] if r['tranche']=='W2']
    # Persist both allocations before returning either; resume cannot redraw.
    write_json(statepath,state)
    return state['tranches'][tranche]
