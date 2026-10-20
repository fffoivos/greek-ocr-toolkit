"""Build and verify M1's exact, width/script-matched substitutions offline."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import copy
import gzip
import hashlib
import json
from pathlib import Path
import random
from train.mix import assemble, marginals, sha256


def stratum(row): return (row['script_class'], (row['width']+127)//128*128)


def identity_digest(rows):
    h=hashlib.sha256()
    for r in rows:
        h.update(json.dumps([r['_component'],r['_pool_index'],r['line_id']],ensure_ascii=False,separators=(',',':')).encode()+b'\n')
    return h.hexdigest()


def allocate(counts,total):
    n=sum(counts.values())
    if n<total: raise ValueError('insufficient supported scanned draws')
    quota={k:total*v//n for k,v in counts.items()}
    for k in sorted(counts,key=lambda k:(-(total*counts[k]%n),k))[:total-sum(quota.values())]:quota[k]+=1
    return quota


def replacement_plan(base, born, count, seed, epoch):
    available=defaultdict(list);scanned=defaultdict(list)
    for i,r in enumerate(born):available[stratum(r)].append(i)
    for i,r in enumerate(base):
        if r['_component']<7:scanned[stratum(r)].append(i)
    supported={k:len(v) for k,v in scanned.items() if available[k]}
    quotas=allocate(supported,count);pairs=[];stats=[]
    for key,indices in sorted(scanned.items()):
        n=quotas.get(key,0);rng=random.Random(f'e4:m1:{seed}:{epoch}:{key}')
        chosen=rng.sample(indices,n);pool=available[key];drawn=[]
        while len(drawn)<n:
            cycle=list(pool);rng.shuffle(cycle);drawn.extend(cycle[:n-len(drawn)])
        pairs.extend(zip(chosen,drawn))
        stats.append(dict(script_class=key[0],width_bucket=key[1],base_scanned_draws=len(indices),
            removed_scanned_draws=n,born_digital_draws=len(drawn),born_digital_pool_rows=len(pool),
            distinct_born_digital_rows=len(set(drawn)),stay_scanned=len(indices)-n,unmatched=not bool(pool)))
    return sorted(pairs),stats


def apply_plan(rows, born, plan, replay_component, scanned_components=None):
    rows=list(rows)
    scanned_components=set(range(replay_component-1) if scanned_components is None else scanned_components)
    if identity_digest(rows)!=plan['base_order_sha256']:raise ValueError('matched replay base draws changed')
    used=set()
    for index,born_index in plan['replacements']:
        if index in used or not 0<=index<len(rows) or not 0<=born_index<len(born):raise ValueError('invalid replay index')
        used.add(index)
        if rows[index]['_component'] not in scanned_components or stratum(rows[index])!=stratum(born[born_index]):raise ValueError('replay stratum mismatch')
        rows[index]=dict(born[born_index],_component=replay_component,_pool_index=born_index)
    if identity_digest(rows)!=plan['final_order_sha256']:raise ValueError('matched replay final draws changed')
    return rows


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--inputs',type=Path,default=Path('out/e4prep/inputs'))
    ap.add_argument('--out',type=Path,default=Path('out/e4prep'));a=ap.parse_args();out=a.out;out.mkdir(parents=True,exist_ok=True)
    receipt=json.loads((a.inputs/'metadata_receipt.json').read_text());groups=[]
    for r in receipt:
        p=a.inputs/r['file']
        if sha256(p)!=r['sha256']:raise ValueError('metadata export changed')
        with gzip.open(p,'rt') as f:groups.append([json.loads(line) for line in f])
    full=json.loads((a.inputs/'full.json').read_text());base_groups,born,test=groups[:8],groups[8],groups[9]
    if any(r['split']!='train' for pool in groups[:9] for r in pool) or any(r['split']!='reserved' for r in test):raise ValueError('wrong exported split')
    if len(born)!=19657 or len(test)!=3600:raise ValueError('wrong E1 partition')
    if {r['source_doc_id'] for r in born}&{r['source_doc_id'] for r in test}:raise ValueError('born digital TEST document overlap')
    if {r['line_id'] for r in born}&{r['line_id'] for r in test}:raise ValueError('born digital TEST identity overlap')
    fractions=[c['fraction'] for c in full['components']];epoch_rows=428872
    source_path=a.inputs/'full_source.json'
    base_sha=json.loads(source_path.read_text())['sha256'] if source_path.exists() else sha256(a.inputs/'full.json')
    plan=dict(schema='e4-matched-replay-v1',base_mix_sha256=base_sha,scanned_components=list(range(7)),
        base_fractions=fractions,base_components=8,replay_component=8,identity_fields=['component','pool_index','line_id'],seed=full['seed'],epoch_rows=epoch_rows,
        metadata_receipt_sha256=sha256(a.inputs/'metadata_receipt.json'),epochs={})
    report=dict(schema='e4-m1-verification-v1',status='metadata-verified; real shard validation pending',
        train_rows=len(born),test_rows=len(test),document_disjoint=True,epochs={},unmatched_strata=[],
        matching='For each epoch, replace exactly round(0.10*N) scanned draws. Allocate that quota proportionally across supported class x ceil(width/128)*128 strata (largest remainder); unsupported strata remain scanned. Sample positions without replacement; born-digital pool cycles shuffled independently within stratum. No pixel/label changes. Synthetic positions identical.',
        data_seed=full['seed'],model_seeds=[0,1,2])
    unmatched=set()
    for epoch in range(1,9):
        rows,counts=assemble(base_groups,fractions,full['seed'],epoch,epoch_rows,exact_rows=True)
        pairs,stats=replacement_plan(rows,born,round(epoch_rows*.1),full['seed'],epoch)
        new=list(rows)
        for index,j in pairs:new[index]=dict(born[j],_component=8,_pool_index=j)
        entry=dict(replacements=pairs,base_order_sha256=identity_digest(rows),final_order_sha256=identity_digest(new))
        plan['epochs'][str(epoch)]=entry
        assert apply_plan(rows,born,entry,8)==new
        assert Counter(stratum(r) for r in rows)==Counter(stratum(r) for r in new)
        report['epochs'][str(epoch)]=dict(strata=stats,marginals=marginals(new),
            base_component_counts=counts,realized_component_counts=dict(Counter(r['_component'] for r in new)),
            drawn_manifest_order_sha256=entry['final_order_sha256'],
            distinct_born_digital_rows=len({r['line_id'] for r in new if r['_component']==8}))
        unmatched.update((s['script_class'],s['width_bucket']) for s in stats if s['unmatched'])
    report['unmatched_strata']=[dict(script_class=k[0],width_bucket=k[1]) for k in sorted(unmatched)]
    mixes=out/'mixes';mixes.mkdir(exist_ok=True);draw=mixes/'m1_replay10.draws.json.gz'
    with gzip.GzipFile(filename=str(draw),mode='wb',mtime=0) as f:f.write(json.dumps(plan,separators=(',',':')).encode())
    mix=copy.deepcopy(full)
    for c in mix['components']:
        if c['kind']=='real':c['fraction']*=.8
    info=json.loads((a.inputs/'build_info_8.json').read_text())
    mix['components'].append(dict(kind='real',shard_dir=receipt[8]['root'],shard_sha256=info['shard_sha256'],
        partition_id=info['partition_id'],source='E1-O5-born-digital-train-only',fraction=.1))
    mix['created_by']='e4_replay';mix['notes']='E4 M1: 50/40/10 synthetic/scanned/born-digital; exact paired substitutions override nominal component quotas; original synthetic draws fixed. Shared validation is E3 val_mix.json. PREPARATION ONLY; regenerate against F1 release.'
    mix['matched_replay']=dict(path=draw.name,sha256=sha256(draw))
    (mixes/'m1_replay10.json').write_text(json.dumps(mix,ensure_ascii=False,indent=2)+'\n')
    report['mix_sha256']=sha256(mixes/'m1_replay10.json');report['draws_sha256']=sha256(draw)
    report['strata_unmatched']=len(unmatched)
    (out/'m1_verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    md=['# M1 matched born-digital replay','',report['matching'],'',
        f"Born-digital: {len(born):,} train rows; excluded TEST: {len(test):,}, document and ID disjoint.",
        f"Epoch budget {epoch_rows:,}; synthetic 214,436; born-digital {round(epoch_rows*.1):,}; scanned {214436-round(epoch_rows*.1):,}. Integer rounding: born-digital = 9.999953%.",
        f"{len(unmatched)} unavailable strata stay scanned; the replacement quota is redistributed across supported strata. Exact overall class x width marginals match control each epoch.",
        'E3 data seed 20261015 is retained for all three model seeds. Draw entries use zero-based base-assembly position and born-digital pool index in sorted-shard/physical-row order. Each epoch binds ordered base and final (component,pool_index,line_id) SHA256. All unchanged draws are reconstructed by train.mix.assemble with the bound base fractions and 428872 exact rows. The compressed draw plan, mix, shard inventories, build receipts, validation mix, codec and data release must all be bound by the M1 arm.',
        'The trainer uses matched_replay for train only; shared val is concatenated once. Packed sampler seed = mix seed and set_epoch(epoch). Width marginals match, so its 6702-step horizon stays fixed. Test rows never enter the replay component.','',
        '| Epoch | Synthetic | Scanned | Born-digital | Distinct replay rows |', '|---:|---:|---:|---:|---:|']
    for e,v in report['epochs'].items():
        c=v['realized_component_counts'];md.append(f"| {e} | {c[7]} | {sum(c.get(i,0) for i in range(7))} | {c[8]} | {v['distinct_born_digital_rows']} |")
    md+=['','Full per-epoch class, width, appearance and per-stratum removed/inserted/still-scanned counts are in m1_verification.json. Repetition is intentional and explicit.','', '| Class | Width bucket |', '|---|---:|']
    md += [f'| {k[0]} | {k[1]} |' for k in sorted(unmatched)]
    md += ['','This is an E3-based preparation receipt. F1 has not been frozen; regenerate and validate the exact draw plan against the repaired release before campaign submission.']
    (out/'m1_mix.md').write_text('\n'.join(md)+'\n');print('M1 metadata verified',len(unmatched),'unmatched strata')

if __name__=='__main__':main()
