"""RU2T-0 offline preparation and fail-closed post-reading finalisation.
No OCR reading is performed by build/finalize; launch is an explicit later command.
"""
import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random
import secrets
import shutil
import sys

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[1]
sys.path.insert(0, str(HERE/'reading'))
from ru1_census import cyr, positions, mask, sha, rows, dump
from common import jsonl, SCRATCH
import scan_packs
import scan_rollout
from ru1_map_answers import map_records, score_controls
from ru2t_coverage import coverage
from ru1_decide import decide

SOURCE = Path.home()/'Projects/greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'
ART = WORK/'artifacts/ru1/ru2t'
PACK = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru2t')
REGISTRY = WORK/'docs/records/labelfix/lqb/versions.json'
SCANNER_SHA = 'dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
SEED = 'RU2T0:20261017:book-stratified-v1'
R3_SEED = '20261017:RU2T:ctx02:r3'
R3_SEEDS = {ctx: f'20261017:RU2T:{ctx}:r3' for ctx in ('ctx02', 'ctx03')}


def accepted_readers(context):
    # Lead rulings: ctx02/r2 and ctx03/r2 are retained solely as VOID evidence.
    return ('r1', 'r3') if context in R3_SEEDS else ('r1', 'r2')


def reader_stem(context, reader):
    return context + ('' if reader == 'r1' else '.' + reader)


def check_scanner():
    if sha(HERE/'reading/scan_rollout.py') != SCANNER_SHA or scan_rollout.VERSION != 'v4.4-canonical':
        raise ValueError('canonical v4.4 scanner changed')


def book_id(r):
    return r['source']+':'+r['doc']


def language(r):
    s=(r.get('attribution','') or '').casefold()+' '+r['source'].casefold()
    if any(w in s for w in ['bulgar','bŭlg','tsars','bulg','българ']): return 'Bulgarian (metadata guess)'
    if any(w in s for w in ['чупић','годишњица']): return 'Serbian (metadata guess)'
    if any(w in s for w in ['синода','kīev','ссср','sssr']): return 'Russian (metadata guess)'
    return 'unknown (metadata insufficient)'


def census(data):
    books={}; pp=[]; selected=[]
    for r in data:
        if str(r.get('script_class','')).casefold()!='cyrillic' and sum(cyr(c) for c in r['label'])<3: continue
        selected.append(r); bid=book_id(r)
        b=books.setdefault(bid,dict(book=bid,source=r['source'],doc=r['doc'],rows=0,signs=Counter(),historical=Counter(),language=language(r),metadata={k:r.get(k) for k in ['attribution','year','source_url']}))
        b['rows']+=1
        b['historical'].update(c.casefold() for c in r['label'] if c.casefold() in 'ѣіѳѵ')
        for p in positions(r['label']):
            b['signs'][p['google']+':'+p['kind']]+=1
            pp.append(dict(p,row_id=r['id'],book=bid))
    for b in books.values():
        hard=sum(b['signs'][f'ъ:{k}'] for k in ['final','pre_hyphen'])
        b['orthography']='pre_reform' if hard>=5 or sum(b['historical'].values()) else 'modern'
    for p in pp:p['orthography']=books[p['book']]['orthography']
    # Both final and pre-hyphen word-final soft signs receive two reads under this task.
    candidates=[p for p in pp if p['google']=='ь' and p['orthography']=='pre_reform']
    return selected,books,pp,candidates


def stratified(candidates, limit):
    grouped=defaultdict(set)
    for p in candidates: grouped[p['book']].add(p['row_id'])
    total=sum(map(len,grouped.values())); limit=min(limit,total)
    quotas={b:limit*len(v)//total for b,v in grouped.items()}
    for b in sorted(grouped,key=lambda b:(-(limit*len(grouped[b])%total),b))[:limit-sum(quotas.values())]:quotas[b]+=1
    rng=random.Random(SEED); chosen=[]
    for b in sorted(grouped):chosen.extend(rng.sample(sorted(grouped[b]),quotas[b]))
    rng.shuffle(chosen)
    return chosen,quotas


def controls():
    inventory=json.loads((WORK/'artifacts/ru1/keys/control_inventory.json').read_text())
    saved={m['adjudication_id']:m for p in sorted((WORK/'artifacts/ru1/keys').glob('ctx*.json')) for m in json.loads(p.read_text())['items'].values() if m['control']}
    pool=[]
    for c in inventory:
        if not c['slots']:continue
        m=saved[c['adjudication_id']]
        if m['slots']!=c['slots']:raise ValueError('control adjudication mismatch')
        digest=m['source_crop_sha256']; src=SCRATCH/'ru1_cache/crops'/(digest+'.png')
        if sha(src)!=digest:raise ValueError('control crop hash mismatch')
        pool.append(dict(c,source_crop_sha256=digest,image=str(src)))
    if len(pool)!=31 or sum(len(c['slots']) for c in pool)!=65:raise ValueError('RU1 65-position inventory incomplete')
    return pool


def closure(pack,art,runtime=False):
    scan_packs.ROOT=art
    dirs=sorted(pack.glob('ctx*/r[123]'))
    results=[scan_packs.scan(d,'yer',write_manifest=not runtime,allow_runtime=runtime,r3_seed=R3_SEEDS.get(d.parent.name)) for d in dirs]
    expected={d.parent.name for d in dirs}
    extra=[str(p) for p in pack.iterdir() if p.is_symlink() or not p.is_dir() or p.name not in expected]
    for ctx in expected:
        extra.extend(str(p) for p in (pack/ctx).iterdir() if p.is_symlink() or p.name not in ({'r1','r2','MANIFEST.r1.json','MANIFEST.r2.json'} | ({'r3','MANIFEST.r3.json'} if ctx in R3_SEEDS else set())))
        if not all((pack/ctx/r/'items.jsonl').is_file() for r in ['r1','r2']):extra.append('missing independent reader: '+ctx)
    if extra or not dirs:results.append(dict(ok=False,violations=extra or ['no packs']))
    return results


def tool_inputs():
    return [HERE/n for n in ['ru2t.py','ru2t_coverage.py','ru2t_delivery.py','ru1_lead_sheets.py','ru1_review.py','ru2t_launch.py','ru2t_finalize.sh','ru1_census.py','ru1_decide.py','reading/ru1_map_answers.py','reading/scan_packs.py','reading/scan_rollout.py','reading/replay_literal.py','reading/common.py','reading/run_read.sh','reading/limit_probe.sh','reading/ledger.py','reading/run_ru2t.sh']]+[WORK/'docs/records/labelfix/secondary/prompts/yer.md',WORK/'artifacts/n1/N1TS3_RECEIPT.json']


def require_external_pack_root(pack):
    """Reject repository ancestors, including worktree .git files and symlinks.

    Inspect both lexical and resolved ancestors without invoking git or writing it.
    This also works before the destination directory exists.
    """
    path = Path(pack).expanduser().absolute()
    for candidate in (path, path.resolve()):
        for parent in (candidate, *candidate.parents):
            marker = parent/'.git'
            if marker.exists() or marker.is_symlink():
                raise ValueError('pack root must be outside every git worktree: '+str(pack))


def build(source=SOURCE, art=ART, pack=PACK):
    require_external_pack_root(pack)
    check_scanner()
    if pack.exists() and any(pack.iterdir()):raise ValueError('refuse overwrite of nonempty pack root')
    before=sha(source);data=list(rows(source));ids=[r['id'] for r in data]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate parent ids')
    rr,books,pp,candidates=census(data);lineids={p['row_id'] for p in candidates}
    full=len(lineids)<=225; chosen,quotas=stratified(candidates,len(lineids) if full else 200)
    art.mkdir(parents=True,exist_ok=True);pack.mkdir(parents=True,exist_ok=True)
    jsonl(art/'candidate_positions.full.jsonl',candidates)
    jsonl(art/'candidate_lines.full.jsonl',[dict(row_id=i,book=book_id(r),crop=r['crop']) for i,r in sorted((r['id'],r) for r in rr if r['id'] in lineids)])
    jsonl(art/'selected_lines.jsonl',[dict(row_id=i,book=book_id(next(r for r in rr if r['id']==i))) for i in chosen])
    modern=[p for p in pp if p['orthography']=='modern' and p['google']=='ь']; random.Random(SEED+':modern').shuffle(modern)
    jsonl(art/'modern_spot_positions.jsonl',modern[:10])
    # Inventory every Cyrillic crop, without fetching or regenerating anything.
    byid={r['id']:r for r in rr}; paths={}; unavailable=[]
    for r in rr:
        p=Path(r['crop']).expanduser()
        if not p.is_absolute():p=source.parents[4]/p
        if not p.is_file():unavailable.append(dict(row_id=r['id'],crop=str(p),selected=r['id'] in chosen))
        else:paths[r['id']]=p
    jsonl(art/'crop_unavailable.jsonl',unavailable)
    pool=controls();dump(art/'control_inventory.json',[{k:v for k,v in c.items() if k!='image'} for c in pool])
    missing_selected=[i for i in chosen if i not in paths]
    if missing_selected:raise ValueError('selected crops unavailable; see crop_unavailable.jsonl (no replacements/fetches)')
    bed=[]
    inputs={str(source.resolve()):before,str(WORK/'artifacts/ru1/keys/control_inventory.json'):sha(WORK/'artifacts/ru1/keys/control_inventory.json')}
    for kp in (WORK/'artifacts/ru1/keys').glob('ctx*.json'):inputs[str(kp)]=sha(kp)
    for i in chosen:
        r=byid[i];masked,slots=mask(r['label']);digest=sha(paths[i]);inputs[str(paths[i])]=digest
        for s in slots:s.update(prior='unknown',control_truth=None)
        bed.append(dict(control=False,row_id=i,source_id=i,book=book_id(r),orthography=books[book_id(r)]['orthography'],slots=slots,masked_text=masked,source_crop_sha256=digest,image=str(paths[i])))
    rng=random.Random(SEED+':controls');rng.shuffle(pool)
    contexts=[];cursor=0;used=set();nctx=math.ceil(len(bed)/90)
    for j in range(nctx):
        ctx=f'ctx{j+1:02d}'; batch=bed[j*len(bed)//nctx:(j+1)*len(bed)//nctx];nc=math.ceil(len(batch)*.1)
        combined=batch+[pool[(cursor+k)%len(pool)] for k in range(nc)];cursor+=nc;rng.shuffle(combined)
        for reader,order in [('r1',combined),('r2',list(reversed(combined)))]:
            dest=pack/ctx/reader;dest.mkdir(parents=True); public=[];private={}
            for m in order:
                iid='k'+secrets.token_hex(5)
                if iid in used:raise ValueError('opaque collision')
                used.add(iid);h=m['source_crop_sha256'];src=Path(m['image']);inputs[str(src)]=h
                rel='crops/'+h+'.png';target=dest/rel;target.parent.mkdir(exist_ok=True)
                if not target.exists():shutil.copyfile(src,target)
                if sha(target)!=h:raise ValueError('copied crop hash differs')
                public.append(dict(item_id=iid,crop=rel,masked_text=m['masked_text'],slots=len(m['slots'])))
                private[iid]={k:v for k,v in m.items() if k not in {'image','masked_text'}}
            jsonl(dest/'items.jsonl',public)
            dump(art/f"keys/{ctx}{'.r2' if reader=='r2' else ''}.json",dict(context=ctx,readers={reader:[p['item_id'] for p in public]},items=private))
        contexts.append(dict(context=ctx,bed_lines=len(batch),control_lines=nc,items=len(combined)))
    scans=closure(pack,art);dump(art/'closure.json',scans)
    if not all(s['ok'] for s in scans):raise ValueError('pack closure failed: '+str([s['violations'] for s in scans if not s['ok']]))
    fullcontrols=sum(math.ceil((len(lineids)*(j+1)//math.ceil(len(lineids)/90)-len(lineids)*j//math.ceil(len(lineids)/90))*.1) for j in range(math.ceil(len(lineids)/90))) if lineids else 0
    info=dict(schema='RU2T0-v1',status='READY_FOR_READINGS',source=str(source),parent_sha256=before,seed=SEED,books=books,
        counts=dict(parent_rows=len(data),cyrillic_rows=len(rr),orthography_books=dict(Counter(b['orthography'] for b in books.values())),candidate_positions=len(candidates),candidate_lines=len(lineids),selected_lines=len(chosen),selected_positions=sum(p['row_id'] in chosen for p in candidates),missing_crops=len(unavailable),modern_spot_positions=min(10,len(modern))),
        plan='full' if full else 'sample 200',quotas=quotas,contexts=contexts,inputs=inputs,scanner_sha256=SCANNER_SHA,
        pack_inputs={str(p):sha(p) for p in list(pack.rglob('*'))+list((art/'keys').glob('*.json'))+[art/'candidate_positions.full.jsonl',art/'selected_lines.jsonl'] if p.is_file()},
        budget=dict(points_per_100_reads=.2,full_reads=2*(len(lineids)+fullcontrols),full_points=round(2*(len(lineids)+fullcontrols)*.002,3),selected_reads=2*sum(c['items'] for c in contexts),selected_points=round(2*sum(c['items'] for c in contexts)*.002,3)),
        policy='Every lowercase word-final ь including pre_hyphen is read twice. Google ъ never changes. Two hard calls with RU1 valid control evidence permit ъ; unreadable/disagreement holds. Modern books excluded. Prior unknown: no lexical veto.',
        no_reader_run=True,network=False,git_writes=False)
    if any(sha(p)!=h for p,h in inputs.items()):raise ValueError('input changed during build')
    info['inputs'].update({str(p):sha(p) for p in tool_inputs()})
    dump(art/'build.json',info)
    return info



def build_ctx02_r3(art=ART, pack=PACK):
    return build_r3('ctx02', art, pack)


def build_r3(context, art=ART, pack=PACK):
    """Copy the exact r1 assignment with fresh IDs and the lead's seeded order."""
    seed=R3_SEEDS[context]
    require_external_pack_root(pack)
    check_scanner()
    dest=pack/context/'r3'
    if dest.exists() or (art/f'keys/{context}.r3.json').exists():
        raise ValueError('refuse overwrite of r3 assignment')
    info=json.loads((art/'build.json').read_text())
    # Data and all old pack bindings remain immutable. Tool rebinding is explicit below.
    tools={str(p) for p in tool_inputs()}
    previous_tools={p:h for p,h in info['inputs'].items() if p in tools}
    for p,h in {**info['inputs'],**info['pack_inputs']}.items():
        if p not in tools and sha(p)!=h:raise ValueError('bound input changed: '+p)
    original=pack/context/'r1'
    key=json.loads((art/f'keys/{context}.json').read_text())
    ordered=list(rows(original/'items.jsonl'))
    random.Random(seed).shuffle(ordered)
    used={i for kp in (art/'keys').glob('ctx*.json') for i in json.loads(kp.read_text())['items']}
    public=[];private={}
    dest.mkdir(parents=True)
    for item in ordered:
        iid='k'+secrets.token_hex(5)
        while iid in used:iid='k'+secrets.token_hex(5)
        used.add(iid)
        public.append(dict(item,item_id=iid));private[iid]=key['items'][item['item_id']]
        target=dest/item['crop'];target.parent.mkdir(exist_ok=True)
        if not target.exists():shutil.copyfile(original/item['crop'],target)
        if sha(target)!=private[iid]['source_crop_sha256']:raise ValueError('r3 crop mismatch')
    jsonl(dest/'items.jsonl',public)
    keypath=art/f'keys/{context}.r3.json'
    dump(keypath,dict(context=context,readers={'r3':[i['item_id'] for i in public]},items=private))
    scan_packs.ROOT=art
    result=scan_packs.scan(dest,'yer',r3_seed=seed)
    dump(art/f'{context}.r3.closure.json',result)
    if not result['ok']:raise ValueError('r3 closure failed: '+str(result['violations']))
    added=[p for p in dest.rglob('*') if p.is_file()]+[pack/context/'MANIFEST.r3.json',keypath]
    info['pack_inputs'].update({str(p):sha(p) for p in added})
    info['inputs'].update({str(p):sha(p) for p in tool_inputs()})
    info.setdefault('reader_routing',{})[context]=dict(accepted=['r1','r3'],void=['r2'],seed=seed)
    dump(art/'build.json',info)
    receipt=dict(status='READY_FOR_READING',context=context+'/r3',seed=seed,items=len(public),
        controls=sum(bool(m['control']) for m in private.values()),closure_ok=True,
        void_context=context+'/r2',void_answers_retained=True,previous_tool_bindings=previous_tools,
        tool_bindings={str(p):sha(p) for p in tool_inputs()},added_bindings={str(p):sha(p) for p in added},
        new_readings=False,finalizer_run=False,network=False,git_writes=False)
    dump(art/('RU2TR3b_RECEIPT.json' if context=='ctx03' else 'RU2TR3_RECEIPT.json'),receipt)
    return receipt


def combine_position(p,votes):
    # Reuse RU1 combiner, routing independently of legacy RU1 ctx04/r3 special case.
    # RU1 expects logical r1/r2 roles; retain physical reader identity in evidence.
    adapted=[dict(v,reader='r2' if v['reader']=='r3' else v['reader'],
                  context='ru2t/'+v['reader']) for v in votes]
    d=decide(dict(p,kind='final',prior='unknown'),adapted)
    if d is None:raise ValueError('not a soft-sign candidate')
    d['kind']=p['kind']
    second='r3' if any(v['reader']=='r3' for v in votes) else 'r2'
    d['reads']={r:next((v for v in votes if v['reader']==r),None) for r in ('r1',second)}
    if d['decision']=='lead_review':d['decision']='hold'
    return d


def apply_version(data,decisions):
    lookup={r['id']:r for r in data}; grouped=defaultdict(list)
    for d in decisions:
        r=lookup[d['row_id']]
        if d['google']!='ь' or r['label'][d['offset']]!='ь':raise ValueError('parent soft-sign mismatch')
        grouped[d['row_id']].append(d)
    out=[];counts=[]
    for r in data:
        ds=grouped[r['id']];chars=list(r['label']);cc=Counter(d['decision'] for d in ds)
        for d in ds:
            if d['decision']=='edit_hard':chars[d['offset']]='ъ'
        holds=[dict(offset=d['offset'],reason=d['reason']) for d in ds if d['decision']=='hold']
        out.append(dict(id=r['id'],label=''.join(chars),status='hold' if holds else 'ok',holds=holds))
        counts.append(dict(id=r['id'],status='hold' if holds else 'ok',decisions=dict(cc),positions=len(ds),changed=bool(cc['edit_hard'])))
    return out,counts


def register(registry,source,output,parent_sha,nrows):
    obj=json.loads(registry.read_text());v=obj['versions'];parent='collection_v2_train'
    if parent in v and (v[parent]['sha256']!=parent_sha or v[parent]['path']!=str(source)):raise ValueError('registered parent differs')
    v[parent]=dict(path=str(source),sha256=parent_sha,parent=None,text_field='label',id_field='id',status='local',population=dict(rows=nrows,definition='collection-v2 train label, exact input rows'))
    v['ru1_v2_train']=dict(path=str(output),sha256=sha(output),parent=parent,text_field='label',id_field='id',status='local',population=dict(rows=nrows,definition='complete collection-v2 train; sampled RU1 corrections, other labels inherited unchanged'),read='exact id label; no fallback')
    dump(registry,obj)


def finalize(art=ART,pack=PACK,source=SOURCE,registry=REGISTRY,output=None):
    require_external_pack_root(pack)
    check_scanner();info=json.loads((art/'build.json').read_text())
    if sha(source)!=info['parent_sha256']:raise ValueError('parent changed')
    for p,h in info['inputs'].items():
        if sha(p)!=h:raise ValueError('bound input changed: '+p)
    for p,h in info['pack_inputs'].items():
        if sha(p)!=h:raise ValueError('bound pack changed: '+p)
    scans=closure(pack,art,runtime=True)
    if not all(s['ok'] for s in scans):raise ValueError('pack closure failed')
    votes=defaultdict(list);meta={};evidence={};seen_rollouts=set();coverages={}
    for ctx in info['contexts']:
        name=ctx['context']
        for reader in accepted_readers(name):
            stem=reader_stem(name,reader);rd=pack/name/reader;ans=art/'answers'/stem
            runpath=Path(str(ans)+'.run.json');run=json.loads(runpath.read_text())
            if run['rc']!=0 or run['model']!='gpt-6.1-sol':raise ValueError('reader failed/model mismatch')
            rollout=Path(run['rollout'])
            digest=sha(rollout)
            if digest in seen_rollouts:raise ValueError('independent reads reuse rollout')
            seen_rollouts.add(digest)
            metadata=[r.get('payload',{}) for r in rows(rollout) if r.get('type') in {'session_meta','turn_context'}]
            models={r['model'] for r in metadata if r.get('model')}
            efforts={r.get('effort',r.get('reasoning_effort')) for r in metadata if r.get('effort',r.get('reasoning_effort'))}
            if models!={'gpt-6.1-sol'} or efforts!={'medium'}:raise ValueError('rollout model/effort mismatch')
            scan=scan_rollout.inspect(rollout,rd)
            dump(Path(str(ans)+'.scan.json'),scan)
            if not scan['ok'] or scan['scanner_version']!='v4.4-canonical':raise ValueError('unclean canonical scan')
            items=list(rows(rd/'items.jsonl'))
            cov=coverage(scan,rollout,rd,items)
            coverages[name+'/'+reader]=cov
            coveragepath=Path(str(ans)+'.coverage.json');dump(coveragepath,cov)
            answerpath=rd/'answers.jsonl';keypath=art/f'keys/{stem}.json'
            mapped,gate=map_records(list(rows(answerpath)),json.loads(keypath.read_text()),items,reader)
            # Validate every answer first; then drop only unviewed items, including controls.
            dropped=set(cov['dropped_items'])
            for p in mapped:
                if not p['control'] and p['google']=='ь':
                    k=(p['row_id'],p['offset'])
                    meta[k]=p
            mapped=[p for p in mapped if p['item_id'] not in dropped]
            gate=score_controls(mapped,name)
            for p in mapped:
                p['context_void']=gate['status']=='VOID'
                p['edit_proposal']=dict(offset=p['offset'],old='ь',new='ъ') if (not p['control'] and p['google']=='ь' and p['kind']=='final' and p['call']=='ъ' and not p['context_void']) else None
            gate.update(dropped_items=sorted(dropped),edit_proposals=sum(p['edit_proposal'] is not None for p in mapped))
            jsonl(Path(str(ans)+'.mapped.jsonl'),mapped);dump(Path(str(ans)+'.controls.json'),gate)
            for path in [coveragepath,runpath,rollout,answerpath,keypath,Path(str(ans)+'.scan.json'),Path(str(ans)+'.mapped.jsonl'),Path(str(ans)+'.controls.json')]:evidence[str(path)]=sha(path)
            for p in mapped:
                if p['control'] or p['google']!='ь':continue
                k=(p['row_id'],p['offset'])
                if any(v['reader']==reader for v in votes[k]):raise ValueError('duplicate independent vote')
                meta[k]=p;votes[k].append(dict(reader=reader,context=name+'/'+reader,call=p['call'],gate_status=gate['status'],confidence=p['confidence'],item_id=p['item_id']))
    selected={r['row_id'] for r in rows(art/'selected_lines.jsonl')}
    expected={(p['row_id'],p['offset']) for p in rows(art/'candidate_positions.full.jsonl') if p['row_id'] in selected}
    if set(meta)!=expected or any(len(v)>2 for v in votes.values()):raise ValueError('candidate coverage differs')
    decisions=[combine_position(meta[k],votes[k]) for k in sorted(expected)]
    output=output or WORK/'artifacts/ru1/ru1_v2_train.jsonl'
    result,counts=apply_version(list(rows(source)),decisions)
    jsonl(art/'decisions.jsonl',decisions);jsonl(art/'per_row_decision_counts.jsonl',counts)
    jsonl(output,result)
    manifest=dict(version='ru1_v2_train',parent=dict(path=str(source),sha256=sha(source)),output=dict(path=str(output),sha256=sha(output),rows=len(result)),scanner_sha256=SCANNER_SHA,evidence=evidence,counts=dict(Counter(d['decision'] for d in decisions)),plan=info['plan'],coverage=coverages)
    manifest['artifacts']={str(p):sha(p) for p in [art/'build.json',art/'decisions.jsonl',art/'per_row_decision_counts.jsonl',art/'selected_lines.jsonl',art/'candidate_positions.full.jsonl']}
    dump(output.with_name('ru1_v2_train_manifest.json'),manifest)
    register(registry,source,output,info['parent_sha256'],len(result))
    return manifest


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','build-r3','finalize']);p.add_argument('--context',choices=sorted(R3_SEEDS),default='ctx02');a=p.parse_args()
    if a.action=='finalize':
        # The CLI completes the requested delivery; fixtures call finalize directly.
        manifest=finalize()
        sys.modules['ru2t']=sys.modules[__name__]
        from ru2t_delivery import deliver
        print(json.dumps(deliver(manifest),ensure_ascii=False,indent=2))
    else:
        print(json.dumps(build() if a.action=='build' else build_r3(a.context),ensure_ascii=False,indent=2))
