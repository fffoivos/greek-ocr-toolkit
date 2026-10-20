"""Offline RU3T replacement preparation; explicit later driver/finaliser.
Original packs, tools and their bound manifest remain immutable.
"""
import argparse
from collections import Counter
import fcntl
import json
from pathlib import Path
import random
import secrets
import shutil
import subprocess
from unittest.mock import patch
import ru3t as m
import ru2t_launch as launcher
from reading.ledger import weekly, record, append

ART = m.ART/'r3_replacements'
PACK = m.PACK
FRESH = m.SCRATCH/'ru1_review/ru3t/fresh_r3_positions.jsonl'
RECEIPT = m.ART/'RU3TR3_RECEIPT.json'
VOID = ['ctx03/r1','ctx05/r1','ctx06/r1','ctx08/r1','ctx09/r2','ctx12/r2','ctx13/r1','ctx14/r1','ctx15/r1','ctx18/r1','ctx18/r2','ctx19/r2']
SEED = '20261018:RU3T-R3:v1'


def assignments():
    return [dict(context=c,reader='r4' if identity=='ctx18/r2' else 'r3',replaces=identity,seed=SEED+':'+identity) for identity in VOID for c in [identity.split('/')[0]]]


def paths(a):
    reader=a['reader'];ctx=a['context']
    return ART/reader, PACK/reader/ctx/reader


def causes():
    receipt=json.loads((m.ART/'RU3TF1_RECEIPT.json').read_text());out=[]
    invalid={k for k,v in receipt['contexts'].items() if v['status']!='VALID'}
    if invalid!=set(VOID):raise ValueError('F1 invalid context set differs')
    for identity in VOID:
        ctx,r=identity.split('/');stem=m.reader_stem(ctx,r);v=receipt['contexts'][identity]
        if v['status']=='FAILED':
            scan=json.loads((m.ART/f'answers/{stem}.scan.json').read_text())
            findings=dict(Counter(x['reason'] for x in scan['violations']))
            out.append(dict(context=identity,cause='scan finding',findings=findings,summary='; '.join(f'{n} × {k}' for k,n in findings.items())))
        else:
            g=v['gate'];out.append(dict(context=identity,cause='control errors',wrong_signs=g['wrong_signs'],abstentions=g['abstentions'],correct=g['correct'],control_slots=g['control_slots'],summary=f"{g['wrong_signs']} wrong signs / {g['control_slots']} scored controls; {g['abstentions']} abstentions"))
    return out


def closure(info,runtime=False):
    results=[];allids=set();oldids={iid for p in (m.ART/'keys').glob('ctx*.json') for iid in json.loads(p.read_text())['items']}
    for a in info['assignments']:
        art,rd=paths(a);m.base.scan_packs.ROOT=art
        scan=m.base.scan_packs.scan(rd,'yer',write_manifest=not runtime,allow_runtime=runtime)
        original=list(m.rows(PACK/a['context']/'r1/items.jsonl'));random.Random(a['seed']).shuffle(original)
        actual=list(m.rows(rd/'items.jsonl'));strip=lambda x:{k:v for k,v in x.items() if k!='item_id'}
        if list(map(strip,actual))!=list(map(strip,original)):scan['violations'].append('seeded order/content differs')
        ids={x['item_id'] for x in actual}
        if ids&(oldids|allids):scan['violations'].append('ids overlap another old/new pack')
        allids|=ids
        # Private slot and control attribution must be byte-equivalent as JSON values.
        oldkey=json.loads((m.ART/f"keys/{a['context']}.json").read_text())['items']
        newkey=json.loads((art/f"keys/{a['context']}.{a['reader']}.json").read_text())['items']
        oldmeta={x['crop']:oldkey[x['item_id']] for x in original}
        for x in actual:
            if newkey[x['item_id']]!=oldmeta[x['crop']]:scan['violations'].append('private assignment differs')
        scan['ok']=not scan['violations'];results.append(scan)
    return results


def original_info():
    info=json.loads((m.ART/'build.json').read_text());m.check_scanner()
    for p,h in {**info['inputs'],**info['pack_inputs']}.items():
        if m.sha(p)!=h:raise ValueError('original bound input changed: '+p)
    return info


def validate():
    original_info();info=json.loads((ART/'build.json').read_text())
    for p,h in info['bindings'].items():
        if m.sha(p)!=h:raise ValueError('replacement bound input changed: '+p)
    scans=closure(info,runtime=True)
    if not all(x['ok'] for x in scans):raise ValueError('replacement closure failed')
    return info


def build():
    original_info();m.require_external_pack_root(PACK)
    if ART.exists() or any((PACK/r).exists() for r in ['r3','r4']):raise ValueError('refuse overwrite replacement build')
    fresh=list(m.rows(FRESH));expected={(p['row_id'],p['offset'],r) for p in fresh for r in p['missing_readers']}
    if len(fresh)!=1100:raise ValueError('unexpected fresh position count')
    info=dict(schema='RU3TR3-v1',assignments=assignments(),void_causes=causes(),network=False,no_reader_run=True,git_writes=False)
    represented=set();used=set();counts=Counter();bindings={str(FRESH):m.sha(FRESH),str(m.ART/'RU3TF1_RECEIPT.json'):m.sha(m.ART/'RU3TF1_RECEIPT.json')}
    for a in info['assignments']:
        ctx=a['context'];oldrd=PACK/ctx/'r1';key=json.loads((m.ART/f'keys/{ctx}.json').read_text());items=list(m.rows(oldrd/'items.jsonl'));random.Random(a['seed']).shuffle(items)
        art,rd=paths(a);rd.mkdir(parents=True);public=[];private={}
        for item in items:
            iid='k'+secrets.token_hex(5)
            if iid in used:raise ValueError('id collision')
            used.add(iid);public.append(dict(item,item_id=iid));meta=key['items'][item['item_id']];private[iid]=meta
            if not meta['control']:
                represented.update((meta['row_id'],s['offset'],a['replaces'].split('/')[1]) for s in meta['slots'] if s['google']=='ь');counts['bed_items']+=1;counts['bed_slots']+=sum(s['google']=='ь' for s in meta['slots'])
            else:counts['control_items']+=1;counts['control_slots']+=len(meta['slots'])
            src=oldrd/item['crop'];dst=rd/item['crop'];dst.parent.mkdir(exist_ok=True)
            if not dst.exists():shutil.copyfile(src,dst)
        a['items']=len(items);a['order_sha256']=__import__('hashlib').sha256(json.dumps([x['crop'] for x in public]).encode()).hexdigest()
        m.jsonl(rd/'items.jsonl',public);m.dump(art/f"keys/{ctx}.{a['reader']}.json",dict(context=ctx,readers={a['reader']:[x['item_id'] for x in public]},items=private))
    if represented-expected:raise ValueError('replacement includes unexpected candidate positions')
    info['residual_missing_reads']=[dict(row_id=k[0],offset=k[1],reader=k[2]) for k in sorted(expected-represented)]
    for ctx in {a['context'] for a in info['assignments']}:
        aa=[a for a in info['assignments'] if a['context']==ctx]
        if len(aa)>1 and aa[0]['order_sha256']==aa[1]['order_sha256']:raise ValueError('independent orders coincide')
    scans=closure(info);m.dump(ART/'closure.json',scans)
    if not all(x['ok'] for x in scans):raise ValueError('closure failed')
    counts.update(items=counts['bed_items']+counts['control_items'],contexts=len(info['assignments']),fresh_unique_positions=len(fresh),covered_unique_positions=len({k[:2] for k in represented}),missing_read_slots=len(expected),replacement_read_slots=len(represented),residual_read_slots=len(expected-represented))
    info.update(counts=dict(counts),estimate_points=round(counts['items']*.002,3),estimate_basis='RU3T0 planning rate: 0.2 Codex weekly percentage points per 100 item reads; excludes probes; not measured usage')
    for root in [ART,PACK/'r3',PACK/'r4']:
        bindings.update({str(p):m.sha(p) for p in root.rglob('*') if p.is_file()})
    bindings.update({str(p):m.sha(p) for p in [Path(__file__),m.HERE/'reading/run_ru3t_r3_all.sh',m.HERE/'ru3t_r3_finalize.sh']})
    info['bindings']=bindings;m.dump(ART/'build.json',info)
    return info


def attempted(a):
    art,rd=paths(a);stem=m.reader_stem(a['context'],a['reader']);ans=art/'answers'/stem
    return any(ans.parent.glob(ans.name+'.*')) or (rd/'answers.jsonl').exists() or any((art/'logs').glob('RU3TR3-'+stem+'*'))


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
                return prober(launcher.helper(m.HERE/'reading/limit_probe.sh',[phase+':RU3TR3/'+a['context']+'/'+a['reader']]),text=True).strip().splitlines()[-1]
            before=probe('before');used=weekly(before)
            if used>=70:
                m.dump(ART/'STOPPED_AT_70.json',dict(next_context=a,weekly_used_percent=used,threshold=70));return 0
            stem=m.reader_stem(a['context'],a['reader']);ans=art/'answers'/stem;ans.parent.mkdir(parents=True,exist_ok=True)
            with Path(str(ans)+'.attempt.json').open('x') as f:json.dump(dict(assignment=a,probe=before,status='CLAIMED'),f)
            run=None
            try:
                launched=runner(launcher.helper(m.HERE/'reading/run_read.sh',['RU3TR3-'+stem,str(rd),str(m.WORK/'docs/records/labelfix/secondary/prompts/yer.md'),'medium']),text=True,capture_output=True)
                Path(str(ans)+'.launcher.log').write_text(launched.stdout+launched.stderr)
                run=json.loads(launched.stdout.strip().splitlines()[-1]);m.dump(Path(str(ans)+'.run.json'),run)
                if launched.returncode or run['rc'] or run['model']!='gpt-6.1-sol':raise ValueError('reader failed')
            finally:
                after=probe('after');after_used=weekly(after)
                if run is not None:append(art/'usage_ledger.json',record(run,before,after,'ru3t/'+a['context'],a['reader'],a['items']))
                if after_used>=70:m.dump(ART/'STOPPED_AT_70.json',dict(last_context=a,weekly_used_percent=after_used,threshold=70))
            if (ART/'STOPPED_AT_70.json').exists():return 0
    return 0


def finalize():
    """Admit exactly one replacement per lost logical role, using unchanged gates."""
    info=validate();original=original_info();routes={a['replaces']:a for a in info['assignments']}
    collect=m.collect_context;combine=m.combine_position
    def routed(art,pack,ctx,reader,seen):
        a=routes.get(ctx+'/'+reader)
        if a:
            ra,rd=paths(a)
            return collect(ra,PACK/a['reader'],ctx,a['reader'],seen)
        return collect(art,pack,ctx,reader,seen)
    def physical(p,votes):
        out=[]
        for v in votes:
            a=routes.get(v['context'])
            out.append(dict(v,logical_reader=v['reader'],physical_reader=a['reader'] if a else v['reader'],context=a['context']+'/'+a['reader'] if a else v['context']))
        return combine(p,out)
    # Original validate's root enumeration predates the two new root folders.
    # validate() above verifies every original bound byte plus new pack closure.
    with patch.object(m,'validate',return_value=original),patch.object(m,'collect_context',side_effect=routed),patch.object(m,'combine_position',side_effect=physical):
        if (ART/'STOPPED_AT_70.json').exists() and not (m.ART/'STOPPED_AT_70.json').exists():
            m.dump(m.ART/'STOPPED_AT_70.json',dict(replacement_stop=str(ART/'STOPPED_AT_70.json'),threshold=70))
        result=m.finalize()
    result['replacement_routes']={k:dict(context=a['context']+'/'+a['reader'],pack=str(paths(a)[1])) for k,a in routes.items()}
    for logical,a in routes.items():
        result['contexts'][logical]['replacement_reader']=a['context']+'/'+a['reader']
    if (ART/'STOPPED_AT_70.json').exists():result['replacement_stopped_at_70']=True
    result['evidence'][str(ART/'build.json')]=m.sha(ART/'build.json')
    m.dump(Path(result['output']['path']).with_name(result['version']+'_manifest.json'),result)
    from ru3t_delivery import deliver
    return deliver(result)


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','drive','finalize']);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if a.dry_run and a.action!='drive':p.error('--dry-run applies only to drive')
    if a.action=='drive':return drive(a.dry_run)
    print(json.dumps(build() if a.action=='build' else finalize(),ensure_ascii=False,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
