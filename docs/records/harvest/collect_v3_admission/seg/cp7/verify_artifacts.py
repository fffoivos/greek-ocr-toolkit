"""Read-only final CP7a mechanical checks. Synthetic answers never enter packs."""
import sys
from cp7_common import *
from freeze import verify_freeze
from build import population,select,exclusion_sets,fresh_ids
from runtime import map_records,RUBRIC


def main():
    verify_freeze();receipt=read(HERE/'build_receipt.json')
    assert receipt['canonical_scanner_sha256']==SCANNER==sha(HERE/'tools/scan_rollout.py')
    for p,d in receipt['inputs'].items():assert sha(p)==d
    selected=rows(HERE/'keys/draw.jsonl');assert len(selected)==100
    rr=[]
    for p in receipt['inputs']:
        if Path(p).name.startswith(('W1_features_','W2_features_')):rr.extend(rows(p))
    _,classes,_=exclusion_sets();excluded=set().union(*classes.values());fresh=fresh_ids(read(SEG/'calibration_ledger.json'))
    pool=population(rr,excluded,fresh)
    assert [r['id'] for r in select(pool)]==[r['id'] for r in selected]
    assert not {r['id'] for r in selected}&(excluded|fresh)
    mapping={};controls=[];allids=set();count=0
    for bed in BEDS:
        key=read(HERE/'keys'/(bed+'.json'));directory=PACK_ROOT/bed/'r1'
        actual=closure(directory,key['readers']['r1'])
        assert actual==read(directory.parent/'MANIFEST.r1.json')['files']
        items=rows(directory/'cards.jsonl');answers=[]
        for item in items:
            # This proves the mapping path only. It is not a reader result.
            a=dict(card_id=item['card_id'],letters='u',marks='u',crop_ok='u',errors=[],detail='synthetic validation only')
            for f in RUBRIC:a[f]='no';a[f+'_reason']='Synthetic validation only.'
            answers.append(a)
            assert item['card_id'] not in allids;allids.add(item['card_id'])
            meta=key['items'][item['card_id']]
            assert sha(directory/item['crop'])==meta['crop_sha256']
            if meta['control']:controls.append(meta['control_public_id'])
            else:mapping[item['card_id']]=meta['line_id']
        mapped,c=map_records(answers,items,key);assert len(mapped)==50 and len(c)==5
        count+=len(mapped)
    assert count==100 and mapping==read(HERE/'keys/answer_mapping.json')
    assert set(mapping.values())=={r['id'] for r in selected}
    assert len(controls)==10 and set(controls)==CONTROL_IDS
    assert not any((PACK_ROOT/bed/'r1/answers.jsonl').exists() for bed in BEDS)
    import gzip
    sealed=[json.loads(l) for l in gzip.decompress((HERE/'keys/sealed_decisions.jsonl.gz').read_bytes()).splitlines()]
    assert len(sealed)==100 and {c['row_id'] for c in sealed}==set(mapping.values())
    assert sha(HERE/'keys/sealed_decisions.jsonl.gz')==receipt['sealed_decisions_sha256']
    for c in sealed:assert {'merged','neighbour_words','orientation','geometry_unavailable','orientation_unknown','text_rules'}<=c.keys()
    print(json.dumps(dict(passed=True,deterministic_draw=100,fresh_ids=100,crop_shas=110,
        mapped=100,controls=10,closure_contexts=2,public_only_contexts=2,leaks=0,
        canonical_scanner_sha256=SCANNER,readers_started=0,publish_actions=0)))

if __name__=='__main__':main()
