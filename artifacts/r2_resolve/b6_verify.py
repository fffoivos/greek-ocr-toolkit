"""Independent readback of B6 original inputs, outputs and isolated deals."""
import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
read=lambda p:[json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]
checks=[]
for t in ['T2','T4']:
    o=ROOT/'artifacts/r2_resolve'/t;deck=ROOT/'docs/labelfix/spellcheck/R2/decks'/t
    for p in (o/'batch_gates').glob('*/b*/validation_receipt.json'):
        g=load(p);assert g['accepted']
        for f,digest in g['input_sha256'].items():assert sha(f)==digest, f
    rr=load(o/'resolution_receipt.json')
    for f,digest in rr['input_sha256'].items():assert sha(f)==digest,f
    keys={k['card_id']:k for k in read(deck/'private/key.jsonl')}
    resolved=read(o/'resolved.jsonl');unknown=read(o/'unknown_agreements.jsonl');pending=read(o/'pending_tiebreak.jsonl')
    sets=[{r['card_id'] for r in rows} for rows in [resolved,unknown,pending]]
    assert sum(map(len,sets))==len(set.union(*sets))==800
    assert set.union(*sets)=={i for i,k in keys.items() if not k['control']}
    assert all(r['status']=='resolved' for r in resolved)
    assert all(r['status']=='unresolved' for r in unknown)
    receipt=load(o/'r3_deal_receipt.json');dealt=[]
    controls={c['card_id'] for c in load(deck/'private/controls_proposed.json')['controls']}
    for f in receipt['folders']:
        p=Path(f['folder']);assert (p/'answers.jsonl').read_bytes()==b''
        assert len(read(p/'cards.jsonl'))==f['cards']<=100
        assert {str(x.relative_to(p)) for x in p.rglob('*') if x.is_file()}==set(f['hashes'])
        for name,digest in f['hashes'].items():assert sha(p/name)==digest
        assert not any(x.is_symlink() for x in p.rglob('*'))
        dealt+=f['card_ids']
    assert len(dealt)==len(set(dealt))
    assert set(dealt)==sets[2]|controls
    assert all(c['card_id'] in sets[2]|controls for c in read(o/'tiebreak/blind/cards.jsonl'))
    checks.append(dict(tranche=t,source_input_hashes_unchanged=True,disjoint_data_partition=True,r3_hash_readback=True,empty_answers=True,max_cards=max(f['cards'] for f in receipt['folders']),data_tiebreaks=len(sets[2]),folders=len(receipt['folders'])))
protocol=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck/docs/labelfix/spellcheck/R2_evidence/READER_PROTOCOL_R2.md')
report=ROOT/'docs/labelfix/spellcheck/R2/B6_RESOLVE_REPORT.md'
receipt=dict(checks=checks,network_calls=0,git_operations=0,resolver_changed=False,protocol_path=str(protocol),protocol_sha256=sha(protocol),artifact_hashes={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'artifacts/r2_resolve').rglob('*')) if p.is_file() and p.name!='b6_final_receipt.json'},report_sha256=sha(report))
(ROOT/'artifacts/r2_resolve/b6_final_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(checks,indent=2))
