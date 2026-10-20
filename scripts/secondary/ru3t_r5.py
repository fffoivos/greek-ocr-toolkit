"""Offline RU3T-R5 preparation. Build/dry-run never launch readers or probes."""
import argparse
from collections import Counter
import fcntl
import hashlib
import json
import math
from pathlib import Path
import random
import secrets
import shutil
import subprocess
from unittest.mock import patch
import ru3t as m
import ru3t_r3 as prior
import ru2t_launch as launcher
from reading.ledger import weekly, record, append

ART=m.ART/'r5_replacements'
PACK=m.PACK
F2=m.SCRATCH/'ru1_review/ru3t_f2'
FRESH=F2/'fresh_r3_positions.jsonl'
RECEIPT=m.ART/'RU3TR5_RECEIPT.json'
VOID=['ctx08/r3','ctx12/r3','ctx13/r3','ctx15/r3','ctx18/r3']
SEED='20261018:RU3T-R5:v1'


def paths(a):return ART/'r5',PACK/'r5'/a['context']/'r5'


def original_info():
    prior.validate()
    return prior.original_info()


def assignments():
    previous=json.loads((prior.ART/'build.json').read_text())['assignments']
    return [dict(context=a['context'],reader='r5',replaces=a['replaces'],replaces_physical=a['context']+'/r3',seed=SEED+':'+a['context']) for a in previous if a['context']+'/r3' in VOID and a['reader']=='r3']


def causes():
    receipt=json.loads((F2/'RU3TF2_RECEIPT.json').read_text());out=[]
    invalid={v['replacement_reader'] for v in receipt['contexts'].values() if v['status']!='VALID'}
    if invalid!=set(VOID):raise ValueError('F2 invalid set differs')
    for a in assignments():
        ident=a['replaces_physical'];v=receipt['contexts'][a['replaces']]
        scan=json.loads((F2/f"evidence/r3_replacements/r3/answers/{a['context']}.r3.scan.json").read_text())
        if v['status']=='FAILED':
            counts=dict(Counter(x['reason'] for x in scan['violations']))
            out.append(dict(context=ident,cause='scan finding',findings=counts,summary='; '.join(f'{n} × {k}' for k,n in counts.items())))
        else:
            if not scan['ok']:raise ValueError('control failure also has scan findings')
            gate=v['gate'];out.append(dict(context=ident,cause='control errors',wrong_signs=gate['wrong_signs'],control_slots=gate['control_slots'],abstentions=gate['abstentions'],summary=f"{gate['wrong_signs']} wrong signs / {gate['control_slots']} scored controls; {gate['abstentions']} abstentions"))
    return out


def all_old_ids():
    return {iid for root in [m.ART/'keys',prior.ART/'r3/keys',prior.ART/'r4/keys'] for p in root.glob('*.json') for iid in json.loads(p.read_text())['items']}


def closure(info,runtime=False):
    scans=[];used=all_old_ids();represented=set()
    for a in info['assignments']:
        art,rd=paths(a);m.base.scan_packs.ROOT=art
        scan=m.base.scan_packs.scan(rd,'yer',write_manifest=not runtime,allow_runtime=runtime)
        items=list(m.rows(rd/'items.jsonl'));key=json.loads((art/f"keys/{a['context']}.r5.json").read_text())['items']
        oldkey=json.loads((m.ART/f"keys/{a['context']}.json").read_text())['items']
        olditems=list(m.rows(PACK/a['context']/'r1/items.jsonl'))
        oldbed={x['crop']:(x,oldkey[x['item_id']]) for x in olditems if not oldkey[x['item_id']]['control']}
        actualbed={x['crop']:(x,key[x['item_id']]) for x in items if not key[x['item_id']]['control']}
        strip=lambda x:{k:v for k,v in x.items() if k!='item_id'}
        if set(oldbed)!=set(actualbed):scan['violations'].append('candidate crop set differs')
        for crop,(x,meta) in actualbed.items():
            if crop not in oldbed or strip(x)!=strip(oldbed[crop][0]) or meta!=oldbed[crop][1]:scan['violations'].append('candidate assignment differs')
            represented.update((meta['row_id'],s['offset'],a['replaces'].split('/')[1]) for s in meta['slots'] if s['google']=='ь')
        ids={x['item_id'] for x in items}
        if ids&used:scan['violations'].append('opaque ids overlap earlier pack')
        used|=ids
        control_ids=[key[x['item_id']]['adjudication_id'] for x in items if key[x['item_id']]['control']]
        if control_ids!=a['control_order']:scan['violations'].append('control assignment differs')
        if set(control_ids)&set(a['excluded_controls']):scan['violations'].append('control reused from earlier context')
        if len(control_ids)!=len(set(control_ids)) or len(control_ids)!=math.ceil(len(oldbed)*.1):scan['violations'].append('control quota differs')
        order=hashlib.sha256(json.dumps([x['crop'] for x in items]).encode()).hexdigest()
        if order!=a['order_sha256']:scan['violations'].append('order differs')
        if order in a['prior_orders']:scan['violations'].append('order repeats earlier reader')
        scan['ok']=not scan['violations'];scans.append(scan)
    expected={(p['row_id'],p['offset'],r) for p in m.rows(FRESH) for r in p['missing_readers']}
    if represented-expected:raise ValueError('unexpected candidate positions')
    if len(represented)!=488 or len(expected-represented)!=10:raise ValueError('replacement coverage differs')
    return scans


def build():
    original_info();m.require_external_pack_root(PACK)
    if ART.exists() or (PACK/'r5').exists():raise ValueError('refuse overwrite r5 build')
    info=dict(schema='RU3TR5-v1',assignments=assignments(),void_causes=causes(),network=False,no_reader_run=True,git_writes=False)
    used=all_old_ids();pool=m.controls();counts=Counter();represented=set()
    bindings={str(p):m.sha(p) for p in [FRESH,F2/'RU3TF2_RECEIPT.json',prior.ART/'build.json']}
    for a in info['assignments']:
        ctx=a['context'];art,rd=paths(a);rd.mkdir(parents=True)
        key=json.loads((m.ART/f'keys/{ctx}.json').read_text())['items'];old=list(m.rows(PACK/ctx/'r1/items.jsonl'))
        batch=[(x,key[x['item_id']],PACK/ctx/'r1'/x['crop']) for x in old if not key[x['item_id']]['control']]
        excluded=set();prior_orders=[]
        for reader in ['r1','r2','r3','r4']:
            kp=(m.ART/f"keys/{m.reader_stem(ctx,reader)}.json") if reader in ['r1','r2'] else prior.ART/reader/f'keys/{ctx}.{reader}.json'
            rp=PACK/ctx/reader if reader in ['r1','r2'] else PACK/reader/ctx/reader
            if kp.exists():
                kk=json.loads(kp.read_text())['items'];excluded.update(v['adjudication_id'] for v in kk.values() if v['control'])
                prior_orders.append(hashlib.sha256(json.dumps([x['crop'] for x in m.rows(rp/'items.jsonl')]).encode()).hexdigest())
        candidates=[c for c in pool if c['adjudication_id'] not in excluded];rng=random.Random(a['seed']+':controls');rng.shuffle(candidates)
        nc=math.ceil(len(batch)*.1)
        if len(candidates)<nc:raise ValueError('insufficient fresh controls')
        for c in candidates[:nc]:
            public=dict(crop='crops/'+c['source_crop_sha256']+'.png',masked_text=c['masked_text'],slots=len(c['slots']))
            meta={k:v for k,v in c.items() if k not in {'image','masked_text'}}
            batch.append((public,meta,Path(c['image'])));bindings[str(c['image'])]=m.sha(c['image'])
        random.Random(a['seed']+':order').shuffle(batch)
        public=[];private={}
        for x,meta,src in batch:
            iid='k'+secrets.token_hex(5)
            if iid in used:raise ValueError('id collision')
            used.add(iid);public.append({k:v for k,v in dict(x,item_id=iid).items() if k in {'item_id','crop','masked_text','slots'}});private[iid]=meta
            dst=rd/x['crop'];dst.parent.mkdir(exist_ok=True)
            if not dst.exists():shutil.copyfile(src,dst)
            if m.sha(dst)!=meta['source_crop_sha256']:raise ValueError('crop hash differs')
            if meta['control']:counts['control_items']+=1;counts['control_slots']+=len(meta['slots'])
            else:
                counts['bed_items']+=1;counts['bed_slots']+=sum(s['google']=='ь' for s in meta['slots'])
                represented.update((meta['row_id'],s['offset'],a['replaces'].split('/')[1]) for s in meta['slots'] if s['google']=='ь')
        a.update(items=len(public),order_sha256=hashlib.sha256(json.dumps([x['crop'] for x in public]).encode()).hexdigest(),control_order=[private[x['item_id']]['adjudication_id'] for x in public if private[x['item_id']]['control']],excluded_controls=sorted(excluded),prior_orders=prior_orders)
        m.jsonl(rd/'items.jsonl',public);m.dump(art/f'keys/{ctx}.r5.json',dict(context=ctx,readers={'r5':[x['item_id'] for x in public]},items=private))
    expected={(p['row_id'],p['offset'],r) for p in m.rows(FRESH) for r in p['missing_readers']}
    info['residual_missing_reads']=[dict(row_id=k[0],offset=k[1],reader=k[2]) for k in sorted(expected-represented)]
    scans=closure(info);m.dump(ART/'closure.json',scans)
    if not all(x['ok'] for x in scans):raise ValueError('r5 closure failed')
    counts.update(contexts=5,items=counts['bed_items']+counts['control_items'],missing_read_slots=len(expected),replacement_read_slots=len(represented),residual_read_slots=len(expected-represented))
    info.update(counts=dict(counts),estimate_points=round(counts['items']*.002,3),estimate_basis='RU3T0 planning rate: 0.2 weekly percentage points per 100 items; excludes probes; not measured usage')
    for root in [ART,PACK/'r5']:
        bindings.update({str(p):m.sha(p) for p in root.rglob('*') if p.is_file()})
    bindings.update({str(p):m.sha(p) for p in [Path(__file__),m.HERE/'reading/run_ru3t_r5_all.sh',m.HERE/'ru3t_r5_finalize.sh']})
    info['bindings']=bindings;m.dump(ART/'build.json',info);return info


def validate():
    original_info();info=json.loads((ART/'build.json').read_text())
    for p,h in info['bindings'].items():
        if m.sha(p)!=h:raise ValueError('r5 bound input changed: '+p)
    if not all(s['ok'] for s in closure(info,runtime=True)):raise ValueError('r5 closure failed')
    return info


def attempted(a):
    art,rd=paths(a);stem=m.reader_stem(a['context'],a['reader']);ans=art/'answers'/stem
    return any(ans.parent.glob(ans.name+'.*')) or (rd/'answers.jsonl').exists() or any((art/'logs').glob('RU3TR5-'+stem+'*'))


def drive(dry_run=False,runner=subprocess.run,prober=subprocess.check_output):
    info=validate()
    if dry_run:
        for a in info['assignments']:
            if not attempted(a):print(json.dumps(dict(a,pack=str(paths(a)[1]),dry_run=True,closure='ok',model='gpt-6.1-sol',effort='medium',network=False)))
        return 0
    with (ART/'driver.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if (ART/'STOPPED_AT_70.json').exists():return 0
        for a in info['assignments']:
            if attempted(a):continue
            validate();art,rd=paths(a);launcher.ART=art
            def probe(phase):
                return prober(launcher.helper(m.HERE/'reading/limit_probe.sh',[phase+':RU3TR5/'+a['context']+'/'+a['reader']]),text=True).strip().splitlines()[-1]
            before=probe('before');used=weekly(before)
            if used>=70:
                m.dump(ART/'STOPPED_AT_70.json',dict(next_context=a,weekly_used_percent=used,threshold=70));return 0
            stem=m.reader_stem(a['context'],a['reader']);ans=art/'answers'/stem;ans.parent.mkdir(parents=True,exist_ok=True)
            with Path(str(ans)+'.attempt.json').open('x') as f:json.dump(dict(assignment=a,probe=before,status='CLAIMED'),f)
            run=None
            try:
                launched=runner(launcher.helper(m.HERE/'reading/run_read.sh',['RU3TR5-'+stem,str(rd),str(m.WORK/'docs/records/labelfix/secondary/prompts/yer.md'),'medium']),text=True,capture_output=True)
                Path(str(ans)+'.launcher.log').write_text(launched.stdout+launched.stderr)
                run=json.loads(launched.stdout.strip().splitlines()[-1]);m.dump(Path(str(ans)+'.run.json'),run)
                if launched.returncode or run['rc'] or run['model']!='gpt-6.1-sol':raise ValueError('reader failed')
            finally:
                after=probe('after');after_used=weekly(after)
                if run is not None:append(art/'usage_ledger.json',record(run,before,after,'ru3t/'+a['context'],a['reader'],a['items']))
                if after_used>=70:m.dump(ART/'STOPPED_AT_70.json',dict(last_context=a,weekly_used_percent=after_used,threshold=70))
            if (ART/'STOPPED_AT_70.json').exists():return 0
    return 0


def routes(info):
    previous=json.loads((prior.ART/'build.json').read_text())['assignments']
    result={a['replaces']:dict(a,round='r3') for a in previous}
    result.update({a['replaces']:dict(a,round='r5') for a in info['assignments']})
    return result


def finalize(dry_run=False):
    """Route lost logical roles to r5; retain the other seven r3/r4 replacements."""
    info=validate();original=original_info();routing=routes(info)
    if dry_run:
        return dict(dry_run=True,routes={k:dict(context=a['context']+'/'+a['reader'],round=a['round']) for k,a in routing.items()},r5_contexts=sum(a['round']=='r5' for a in routing.values()),labels_written=False,registry_written=False)
    collect=m.collect_context;combine=m.combine_position
    def routed(art,pack,ctx,reader,seen):
        a=routing.get(ctx+'/'+reader)
        if a:
            ra,rd=(paths(a) if a['round']=='r5' else prior.paths(a))
            return collect(ra,PACK/a['reader'],ctx,a['reader'],seen)
        return collect(art,pack,ctx,reader,seen)
    def physical(p,votes):
        out=[]
        for v in votes:
            a=routing.get(v['context'])
            out.append(dict(v,logical_reader=v['reader'],physical_reader=a['reader'] if a else v['reader'],context=a['context']+'/'+a['reader'] if a else v['context']))
        return combine(p,out)
    with patch.object(m,'validate',return_value=original),patch.object(m,'collect_context',side_effect=routed),patch.object(m,'combine_position',side_effect=physical):
        for stop in [prior.ART/'STOPPED_AT_70.json',ART/'STOPPED_AT_70.json']:
            if stop.exists() and not (m.ART/'STOPPED_AT_70.json').exists():m.dump(m.ART/'STOPPED_AT_70.json',dict(replacement_stop=str(stop),threshold=70))
        result=m.finalize()
    result['replacement_routes']={k:dict(context=a['context']+'/'+a['reader'],round=a['round']) for k,a in routing.items()}
    for logical,a in routing.items():result['contexts'][logical]['replacement_reader']=a['context']+'/'+a['reader']
    result['evidence'][str(ART/'build.json')]=m.sha(ART/'build.json')
    m.dump(Path(result['output']['path']).with_name(result['version']+'_manifest.json'),result)
    from ru3t_delivery import deliver
    return deliver(result)


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','drive','finalize']);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if a.dry_run and a.action=='build':p.error('--dry-run applies to drive/finalize')
    if a.action=='drive':return drive(a.dry_run)
    result=build() if a.action=='build' else finalize(a.dry_run)
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
