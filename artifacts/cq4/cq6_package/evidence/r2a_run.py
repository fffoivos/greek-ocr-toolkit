"""R2a A-D package entry point; bounded local mock or one existing Slurm job."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import numpy as np
from scripts.labelfix.clariden.r1_common import rows, sha256, write_rows, verify_receipt, nfd, clusters, factors, HEADS
from scripts.labelfix.clariden.r2_util import atomic_json as write_json
from scripts.labelfix.clariden.r2_run import digest
from scripts.labelfix.clariden.r2_teacher import code_binding
from scripts.labelfix.clariden.r1_extract import extract
from scripts.labelfix.clariden.r1_train import Shards, predict
from scripts.labelfix.clariden.r2_manifest import ManifestPool, inventory_ids, identity
from scripts.labelfix.clariden.l1_infer import load_reader
from scripts.labelfix import r2_score
from greekocr.labelfix.release_gate import policy_binding


def unique_alignment(source,target):
    """Accept a match only if all optimal LCS paths give this exact match."""
    n,m=len(source),len(target)
    pre=[[0]*(m+1) for _ in range(n+1)];suf=[[0]*(m+1) for _ in range(n+1)]
    for i in range(n):
        for j in range(m):pre[i+1][j+1]=max(pre[i][j+1],pre[i+1][j],pre[i][j]+(source[i]==target[j]))
    for i in range(n-1,-1,-1):
        for j in range(m-1,-1,-1):suf[i][j]=max(suf[i+1][j],suf[i][j+1],suf[i+1][j+1]+(source[i]==target[j]))
    result={};best=pre[n][m]
    for i in range(n):
        possible=[j for j in range(m) if source[i]==target[j] and pre[i][j]+1+suf[i+1][j+1]==best]
        skipped=any(pre[i][j]+suf[i+1][j]==best for j in range(m+1))
        if len(possible)==1 and not skipped:result[i]=possible[0]
    return result


def validate(cfg,mock):
    if bool(cfg['mock'])!=mock:raise ValueError('mock/production mismatch')
    if policy_binding()!=cfg['policy']:raise ValueError('frozen policy changed')
    if not mock:
        from scripts.labelfix.clariden.r2_teacher import TEACHER_SHA
        if cfg['sha256'].get(cfg['teacher'])!=TEACHER_SHA or cfg['checkpoints']['A16']['path']!=cfg['teacher']:raise ValueError('not frozen R1-A teacher')
    for p,h in cfg['sha256'].items():
        if sha256(p)!=h:raise ValueError('input hash mismatch: '+p)
    for key in ('data','heldout'):verify_receipt(cfg[key])
    groups={k:list(rows(cfg[k])) for k in ('native','witness','dev')}
    for name,rr in groups.items():
        if len({r['line_id'] for r in rr})!=len(rr):raise ValueError('duplicate cohort line')
        if mock and len(rr)>64:raise ValueError('mock line limit')
        for r in rr:
            if sha256(r['crop'])!=r['crop_sha256']:raise ValueError('native crop hash mismatch')
    if {r['doc'] for r in groups['native']} & {r['doc'] for r in groups['witness']+groups['dev']}:raise ValueError('training/evaluation document leakage')
    roles=json.loads(Path(cfg['roles']).read_text())['documents']
    for name,expected in [('native','supervision'),('witness','witness')]:
        for r in groups[name]:
            if roles.get(r['doc'],{}).get('role')!=expected:raise ValueError('R2C document role firewall')
    val=verify_receipt(cfg['data'])['document_split']['validation']
    if {r['doc'] for r in groups['native']} & set(val):raise ValueError('old validation leakage')
    manifest=list(rows(cfg['manifest']));native={r['line_id']:r for r in groups['native']}
    if len(manifest)!=cfg['expected_slots']:raise ValueError('wrong overlay count')
    if len({identity(r['slot_id']) for r in manifest})!=len(manifest):raise ValueError('duplicate overlay identity')
    old=Shards(cfg['data'],'A','train');oldids={identity(r['slot_id']) for r in inventory_ids(old,cfg['inventory'])}
    for r in manifest:
        if identity(r['slot_id']) in oldids or 'replaces' in r or 'removes' in r:raise ValueError('expected all-new overlay identity')
        if r['role']!='train' or r['provenance']!='native_print' or r.get('unknown') or r['loss_weight']!=1:raise ValueError('invalid overlay admission')
        source=native[r['line_id']]
        if source['doc']!=r['doc'] or source['crop_sha256']!=r['slot_id'][0]:raise ValueError('overlay source mismatch')
    if len(groups['dev'])!=cfg['expected_dev_lines']:raise ValueError('DEV line count')
    items=[r for r in rows(cfg['dev_truth']) if r.get('type')=='item']
    if len(items)!=cfg['expected_dev_items'] or not {r['line_id'] for r in items}<={r['line_id'] for r in groups['dev']}:raise ValueError('DEV item binding')
    return dict(inputs=len(cfg['sha256']),cohort_lines={k:len(v) for k,v in groups.items()},overlay_slots=len(manifest),new_identities=len(manifest),replaced=0,policy=cfg['policy'])


def extract_cohort(selection,alignments,out,mock,workers=None):
    selected=list(rows(selection)); bycrop={r['crop']:r for r in selected}
    ar=list(rows(alignments))
    if len(ar)!=len(selected) or {r['crop'] for r in ar}!=set(bycrop):raise ValueError('missing/duplicate alignment')
    for r in ar:
        if nfd(bycrop[r['crop']]['recogniser_text'])!=r['alignment']['prediction']:raise ValueError('saved recogniser text mismatch')
    # Native and evaluation share the unchanged R1 full-height window extractor.
    roots={r['crop'].split('docs/harvest/',1)[0] for r in selected}
    if len(roots)!=1:raise ValueError('crop roots differ')
    result=extract(selection,alignments,out,roots.pop(),layout='toolkit',mode='heldout',workers=workers if workers is not None else (1 if mock else 8))
    metadata=list(rows(out/'lines.jsonl.gz'));source={r['id']:r for r in selected}
    for r in metadata:r['source']=source[r['id']]['source']
    write_rows(out/'lines.jsonl.gz',metadata)
    result['sha256']['lines.jsonl.gz']=sha256(out/'lines.jsonl.gz')
    write_json(out/'extraction_receipt.json',result);return result


def overlay_pool(cfg,path):
    old=Shards(cfg['data'],'A','train')
    pool=ManifestPool(old,cfg['manifest'],cfg['inventory'],lambda p:Shards(p,'A','train'),native_pool=path)
    if len(pool)!=len(old)+cfg['expected_slots'] or pool.binding['quarantined']:raise ValueError('overlay cardinality/quarantine')
    if pool.binding['unique_counts'].get('old')!=len(old):raise ValueError('old data changed')
    if pool.binding['overlay_hits_on_duplicated_keys']!=0:raise ValueError('overlay hits duplicated old keys')
    if not all(e['dataset'] is old and e['index']==i and e['weight']==1 and
               np.array_equal(e['target'],old.index[i]['target']) for i,e in enumerate(pool.entries[:len(old)])):
        raise ValueError('BASE old row sequence changed')
    result=dict(pool.binding,old_slots=len(old),training_slots=len(pool),new_slots=cfg['expected_slots'],
                old_sequence_assertion='pass',replacement_assertion='covered_by_fixture')
    if cfg['mock']:
        first=inventory_ids(old,cfg['inventory'])[0]
        correction=dict(first,role='train',provenance='native_print',targets=[0,1,0,0],loss_weight=1,replaces=first['slot_id'])
        p=Path(path).parent/'replacement_assertion.jsonl';write_rows(p,[correction])
        repaired=ManifestPool(old,p,cfg['inventory'])
        if len(repaired)!=len(old) or list(repaired.index[0]['target'])!=[0,1,0,0]:raise ValueError('replace-not-append assertion')
        result['replacement_assertion']='pass'
    return result


def witness_ledger(cfg,metadata,predictions):
    keys={r['card_id']:r for r in rows(cfg['witness_key'])}; meta={r['id']:r for r in metadata}
    labels={r['id']:r['label'] for r in rows(cfg['eligible'])}
    pred={(r['line_id'],r['start']):r for r in predictions};out=[]
    choices=[['none','psili','dasia'],['none','acute','grave','circumflex'],['none','present'],['none','present']]
    for card in rows(cfg['witness_truth']):
        k=keys[card['card_id']]; m=meta[k['line_id']]
        context=[c for c in clusters(nfd(m['recogniser_text'])) if c.base.isalpha()]
        mapping=unique_alignment([c.base for c in clusters(nfd(labels[k['line_id']])) if c.base.isalpha()],[c.base for c in context])
        same=[c.base for c in clusters(nfd(card['printed_form'] or '')) if c.base.isalpha()]==[c.base for c in clusters(nfd(k['mining_key'])) if c.base.isalpha()]
        for h in card['letter_heads']:
            ordinal=k['crop_letter_offset']+h['index']; start=context[mapping[ordinal]].start if same and ordinal in mapping else None
            pp=pred.get((k['line_id'],start));truth=[]
            for field,cc in zip(('breathing','accent','diaeresis','subscript'),choices):truth.append(cc.index(h[field]) if h.get(field) in cc else None)
            out.append(dict(card_id=card['card_id'],line_id=k['line_id'],doc=k['doc'],slice=k['slice'],control=card['control'],
                target_head=k['target_head'],anchor=h['index']==k['anchor_index'],letter_index=h['index'],base=h['base'],start=start,
                slot_id=[k['crop_sha256'],start] if start is not None else None,truth=truth,prediction=pp['factors'] if pp else None,
                unknown=[name for name,v in zip(HEADS,truth) if v is None],status='scored' if pp else 'unscored' if start is not None else 'alignment_unknown'))
    return out


def dev_score(cfg,metadata,predictions):
    meta={r['id']:r for r in metadata};byline={}
    for p in predictions:byline.setdefault(p['line_id'],[]).append(p)
    ll=[];pp=[];states=[]
    for item in rows(cfg['dev_truth']):
        if item.get('type')!='item':continue
        states.append({k:item.get(k) for k in ('id','wave','control','status','weight','start','end','line_id','truth','selection','scoring_policy','in_cut')})
        if item['control'] or item['status']!='resolved' or item['truth'] is None:continue
        lid=item['line_id'];m=meta[lid];start,end=item['start'],item['end'];cardid=item['id']
        ll.append(dict(line_id=cardid,doc=m['doc'],source=item['wave'],inclusion_weight=item['weight'],recogniser_text=nfd(m['recogniser_text'])[start:end],
            print_slots=[dict(id=f'{cardid}:{c.start}',base=c.base,targets=factors(c.marks),unknown=[]) for c in clusters(nfd(item['truth'])) if c.base.isalpha()]))
        pp += [dict(p,line_id=cardid,start=p['start']-start) for p in byline.get(lid,[]) if start<=p['start']<end]
    score,ledger=r2_score.score(ll,pp)
    return score,ledger,states


def witness_comparison(old,new,reps=4000):
    """Paired target witness accounting; missing/ambiguous predictions stay UNKNOWN."""
    from collections import Counter
    def key(r):return r['card_id'],r['letter_index']
    a={key(r):r for r in old};b={key(r):r for r in new}
    if set(a)!=set(b):raise ValueError('witness ledger identities differ')
    totals=Counter();slices={};documents={};ledger=[]
    for k,x in a.items():
        y=b[k]
        if any(x[f]!=y[f] for f in ('truth','doc','target_head','anchor','slice')):raise ValueError('witness truth changed')
        if x['control'] or not x['anchor'] or x['slice'] not in ('capitals','omicron_monotonic','subscript'):continue
        h=list(HEADS).index(x['target_head']);truth=x['truth'][h]
        if truth is None or x['prediction'] is None or y['prediction'] is None:
            totals['unknown']+=1;continue
        p,q=x['prediction'][h],y['prediction'][h]
        counts=Counter(known=1,negative=int(truth==0),positive=int(truth!=0),old_false_additions=int(truth==0 and p!=0),
            new_false_additions=int(truth==0 and q!=0),old_wrong=int(p!=truth),new_wrong=int(q!=truth),
            positive_regressions=int(truth!=0 and p==truth and q!=truth),positive_recoveries=int(truth!=0 and p!=truth and q==truth))
        totals.update(counts);slices.setdefault(x['slice'],Counter()).update(counts)
        d=documents.setdefault(x['doc'],[0,0]);d[0]+=counts['old_wrong']-counts['new_wrong'];d[1]+=counts['old_false_additions']-counts['new_false_additions']
        ledger.append(dict(card_id=k[0],letter_index=k[1],doc=x['doc'],slice=x['slice'],truth=truth,old=p,new=q))
    values=np.asarray(list(documents.values()),dtype=float);ci=None;fa_ci=None
    if len(values):
        rng=np.random.default_rng(20261017);draws=values[rng.integers(0,len(values),(reps,len(values)))].sum(axis=1)
        ci=np.quantile(draws[:,0],[.025,.975]).tolist();fa_ci=np.quantile(draws[:,1],[.025,.975]).tolist()
    old_fa=totals['old_false_additions'];new_fa=totals['new_false_additions']
    reduction=(old_fa-new_fa)/old_fa if old_fa else None
    return dict(counts=dict(totals),by_slice={k:dict(v) for k,v in slices.items()},documents=len(documents),
        false_addition_reduction=reduction,net_fewer_wrong=totals['old_wrong']-totals['new_wrong'],
        net_fewer_wrong_document_ci95=ci,false_additions_document_ci95=fa_ci,
        benefit_gate=dict(reduction_at_least_30_percent=reduction is not None and reduction>=.3,
            net_fewer_wrong_at_least_5=totals['old_wrong']-totals['new_wrong']>=5,
            document_ci_excludes_no_improvement=ci is not None and ci[0]>0,
            positive_regressions=totals['positive_regressions'],positive_recoveries=totals['positive_recoveries']),ledger=ledger)


def run(config,out,mock=False,dry_run_ab=False,dry_run_witness_alignments=None):
    if not mock and not dry_run_ab and not os.environ.get('SLURM_JOB_ID'):raise ValueError('production requires existing Slurm job')
    if dry_run_ab:
        if os.environ.get('SLURM_JOB_ID'):raise ValueError('dry run requires login node without allocation')
        if not mock:
            root=Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_r2a_20261017/dryrun').resolve()
            if not Path(out).resolve().is_relative_to(root):raise ValueError('dry run output must be under remote dryrun/')
            if not dry_run_witness_alignments:raise ValueError('dry run requires saved real witness alignments')
        os.environ['CUDA_VISIBLE_DEVICES']=''
    import torch
    torch.set_num_threads(2 if mock or dry_run_ab else 8)
    cfg=json.loads(Path(config).read_text());out=Path(out);out.mkdir(parents=True,exist_ok=True)
    code=code_binding();code.update({str(p):sha256(p) for p in Path('scripts/labelfix/clariden').glob('r2a*') if p.is_file()})
    code['scripts/labelfix/r2_score.py']=sha256('scripts/labelfix/r2_score.py')
    binding=digest(dict(config=sha256(config),code=code,dry_run_ab=dry_run_ab,
                        saved_witness_sha256=sha256(dry_run_witness_alignments) if dry_run_witness_alignments else None));bp=out/'input_binding.json'
    if bp.exists() and json.loads(bp.read_text())['binding']!=binding:raise ValueError('output binding changed')
    write_json(bp,dict(binding=binding,code=code))
    def stage(name,fn):
        rp=out/f'stage_{name}.json'
        if rp.exists():
            rr=json.loads(rp.read_text())
            if rr['binding']!=binding or any(sha256(out/p)!=h for p,h in rr['sha256'].items()):raise ValueError('resume receipt mismatch')
            return rr['result']
        dest=out/name
        if dest.exists():dest.rename(out/f'{name}.interrupted.{time.time_ns()}')
        dest.mkdir();tick=time.monotonic();result=fn(dest)
        write_json(rp,dict(stage=name,binding=binding,complete=True,elapsed_seconds=time.monotonic()-tick,result=result,
            sha256={str(p.relative_to(out)):sha256(p) for p in dest.rglob('*') if p.is_file()}))
        print('STAGE_DONE '+name,flush=True);return result
    checked=validate(cfg,mock);stage('A',lambda dest:checked)
    def stage_b(dest):
        selection=list(rows(cfg['witness']))
        if dry_run_witness_alignments:wap=Path(dry_run_witness_alignments)
        elif cfg.get('witness_alignments'):wap=Path(cfg['witness_alignments'])
        else:
            from greekocr.labelfix.ctc_align import Recognizer
            from PIL import Image
            rec=Recognizer(cfg['recognizer'],device='cpu' if mock else 'cuda:0',threads=2 if mock else 8)
            al=[]
            for i in range(0,len(selection),16):
                batch=selection[i:i+16];images=[]
                for r in batch:
                    with Image.open(r['crop']) as im:images.append(im.convert('L'))
                for r,a in zip(batch,rec.align_batch(images)):
                    ar=a.to_record();r['recogniser_text']=ar['prediction'];al.append(dict(crop=r['crop'],alignment=ar))
            wap=dest/'witness_alignments.jsonl.gz';write_rows(wap,al)
        if dry_run_witness_alignments:
            saved={r['crop']:r['alignment']['prediction'] for r in rows(wap)}
            if set(saved)!={r['crop'] for r in selection}:raise ValueError('saved witness alignment coverage')
            for r in selection:r['recogniser_text']=saved[r['crop']]
        wsp=dest/'witness_selection.jsonl';write_rows(wsp,selection)
        results={}
        for name,sp,ap in [('native',cfg['native'],cfg['native_alignments']),('witness',wsp,wap),('dev',cfg['dev'],cfg['dev_alignments'])]:
            if dry_run_ab and name!='native':
                selected=list(rows(sp))[:2];crops={r['crop'] for r in selected}
                sliced=dest/(name+'_slice.jsonl');aligned=dest/(name+'_slice_alignments.jsonl.gz')
                write_rows(sliced,selected);write_rows(aligned,[r for r in rows(ap) if r['crop'] in crops])
                sp,ap=sliced,aligned
            results[name]=extract_cohort(sp,ap,dest/name,mock,workers=1 if dry_run_ab else None)
        results['overlay']=overlay_pool(cfg,dest/'native');write_json(dest/'overlay_receipt.json',results['overlay'])
        return results
    stage('B',stage_b)
    if dry_run_ab:
        write_json(out/'dryrun_receipt.json',dict(complete=True,stages=['A','B'],cpu_only=True,full_old_pool=True,full_overlay=True,submitted=False))
        print('REAL_INPUT_AB_DRY_RUN_PASS',flush=True);return
    def stage_c(dest):
        def one(pair):
            gpu,seed=pair;target=dest/str(seed)
            cmd=[sys.executable,'-B','-u','scripts/labelfix/clariden/r1_train.py','--data',cfg['data'],'--heldout',cfg['heldout'],'--out',str(target),
                '--arm','A','--device','cpu' if mock else f'cuda:{gpu}','--seed',str(seed),'--sampler-seed',str(seed),'--epochs','15',
                '--batch-size','16' if mock else '512','--workers','0' if mock else '4','--threads','2' if mock else '8','--source-commit',cfg['source_commit'],
                '--manifest',cfg['manifest'],'--inventory',cfg['inventory'],'--native-pool',str(out/'B/native')]
            if mock:cmd+=['--steps','1']
            subprocess.run(cmd,check=True)
            return json.loads((target/'training_receipt.json').read_text())
        if mock:runs=[one(p) for p in enumerate(cfg['seeds'])]
        else:
            with ThreadPoolExecutor(3) as pool:runs=list(pool.map(one,enumerate(cfg['seeds'])))
        return dict(seeds=cfg['seeds'],runs=runs)
    stage('C',stage_c)
    def stage_d(dest):
        checkpoints={k:v['path'] for k,v in cfg['checkpoints'].items()}
        checkpoints.update({f'R2a{seed}':str(out/'C'/str(seed)/'best.pt') for seed in cfg['seeds']})
        results={};dev_records={};physical_records={};witness_records={}
        for name,cp in checkpoints.items():
            model=load_reader(cp,'cpu' if mock else 'cuda:0');target=dest/name;target.mkdir();result={}
            for cohort,path in [('heldout',Path(cfg['heldout'])),('witness',out/'B/witness'),('dev',out/'B/dev')]:
                prediction=target/f'{cohort}_predictions.jsonl'
                predict(model,Shards(path,'A'),prediction,torch.device('cpu' if mock else 'cuda:0'),16 if mock else 512,0 if mock else 4,Path(cp),'A')
                pp=list(rows(prediction));mm=list(rows(path/'lines.jsonl.gz'))
                if cohort=='dev':
                    score,ledger,states=dev_score(cfg,mm,pp);dev_records[name]=ledger
                    write_rows(target/'dev_item_states.jsonl',states)
                elif cohort=='witness':
                    ledger=witness_ledger(cfg,mm,pp);witness_records[name]=ledger
                    score=dict(slots=len(ledger),scored=sum(r['status']=='scored' for r in ledger),unknown=sum(r['status']=='alignment_unknown' for r in ledger))
                else:
                    ll=[r for r in r2_score.truth_lines(cfg['heldout_truth']) if not r.get('dev',False)]
                    ll,overlay=r2_score.apply_overlay(ll,json.loads(Path(cfg['overlay']).read_text()))
                    metadata={r['id']:dict(r,coverage_by_start={c['start']:c for c in r['coverage']}) for r in mm}
                    for r in ll:
                        if r['recogniser_text']!=metadata[r['line_id']]['recogniser_text']:raise ValueError('heldout recogniser text mismatch')
                    for p in pp:p['coverage']=metadata[p['line_id']]['coverage_by_start'][p['start']]
                    score,ledger=r2_score.score(ll,pp);physical_records[name]=ledger
                    result['heldout_continuity']=r2_score.continuity(ll,metadata,pp)
                write_json(target/f'{cohort}_scores.json',score);write_rows(target/f'{cohort}_ledger.jsonl.gz',ledger)
                result[cohort]=dict(predictions=len(pp),prediction_sha256=sha256(prediction),checkpoint_sha256=sha256(cp),extraction_receipt_sha256=sha256(path/'extraction_receipt.json'))
            results[name]=result
        paired={cohort:{name:r2_score.paired(records['A16'],rr) for name,rr in records.items() if name!='A16'} for cohort,records in [('heldout',physical_records),('dev',dev_records)]}
        paired['witness']={name:witness_comparison(witness_records['A16'],rr) for name,rr in witness_records.items() if name!='A16'}
        # All same-seed comparisons are also explicit for coordinator readback.
        paired['same_seed']={}
        for seed,base in [(20261016,'A16'),(20261017,'BASEs17'),(20261018,'BASEs18')]:
            name=f'R2a{seed}'
            paired['same_seed'][str(seed)]={cohort:r2_score.paired(records[base],records[name]) for cohort,records in [('heldout',physical_records),('dev',dev_records)]}
            paired['same_seed'][str(seed)]['witness']=witness_comparison(witness_records[base],witness_records[name])
        write_json(dest/'paired_scores.json',paired)
        write_json(dest/'scoring_receipt.json',dict(complete=True,arms=results,heldout_overlay_sha256=sha256(cfg['overlay']),dev_items=cfg['expected_dev_items'],witness_cards=len(list(rows(cfg['witness_truth'])))))
        return results
    stage('D',stage_d)
    if policy_binding()!=cfg['policy']:raise ValueError('policy changed during run')
    write_json(out/'run_receipt.json',dict(binding=binding,mock=mock,stages=['A','B','C','D'],complete=True,policy=policy_binding(),submitted=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--mock',action='store_true')
    ap.add_argument('--dry-run-ab',action='store_true');ap.add_argument('--dry-run-witness-alignments',type=Path)
    run(**vars(ap.parse_args()))
