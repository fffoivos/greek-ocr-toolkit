"""RU3T offline full-coverage pack builder and fail-closed finaliser. No readers run here."""
import argparse
from collections import Counter, defaultdict
import json, math, random, secrets, shutil, sys
from pathlib import Path
import ru2t as base
from ru2t import (HERE, WORK, SOURCE, REGISTRY, SCANNER_SHA, SCRATCH, rows, sha, dump,
    jsonl, census, book_id, controls, mask, require_external_pack_root, check_scanner,
    reader_stem, combine_position, apply_version, scan_rollout, map_records, score_controls, coverage)
ART=WORK/'artifacts/ru1/ru3t'
PACK=base.PACK.with_name('ru3t')
OLD_ART=base.ART
PRIOR=WORK/'artifacts/ru1/ru1_v2_train.jsonl'
PRIOR_SHA='b47c113ff926bf73adc9d76bb46d1ad443befbd014ae4c8a22c5d83c55ba40e8'
SEED='RU3T0:20261017:full-remaining-v1'
def accepted_readers(context):return ('r1','r2')
def closure(pack,art,runtime=False):
    # RU3T has no inherited VOID routing from RU2T ctx02/ctx03.
    from unittest.mock import patch
    with patch.object(base,'R3_SEEDS',{}):return base.closure(pack,art,runtime)
def tool_inputs():
    return list(dict.fromkeys(base.tool_inputs()+[HERE/n for n in ['ru3t.py','ru3t_delivery.py','ru2t_launch.py','ru3t_driver.py','ru3t_finalize.sh','reading/run_ru3t_all.sh']]))
def validate(art=ART,pack=PACK):
    require_external_pack_root(pack);check_scanner()
    info=json.loads((art/'build.json').read_text())
    for p,h in {**info['inputs'],**info['pack_inputs']}.items():
        if sha(p)!=h:raise ValueError('bound input changed: '+p)
    if not all(s['ok'] for s in closure(pack,art,runtime=True)):raise ValueError('pack closure failed')
    return info

def build(source=SOURCE, art=ART, pack=PACK, prior=PRIOR, old_art=OLD_ART, expected_prior=PRIOR_SHA):
    require_external_pack_root(pack)
    check_scanner()
    if pack.exists() and any(pack.iterdir()):raise ValueError('refuse overwrite of nonempty pack root')
    before=sha(source);data=list(rows(source));ids=[r['id'] for r in data]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate parent ids')
    rr,books,pp,candidates=census(data);lineids={p['row_id'] for p in candidates}
    if sha(prior)!=expected_prior:raise ValueError('RU2T frozen label hash differs')
    old_info=json.loads((old_art/'build.json').read_text())
    if old_info['parent_sha256']!=before:raise ValueError('RU2T parent differs')
    old_selected={r['row_id'] for r in rows(old_art/'selected_lines.jsonl')}
    old_decisions=list(rows(old_art/'decisions.jsonl'))
    if {(d['row_id'],d['offset']) for d in old_decisions}!={(p['row_id'],p['offset']) for p in candidates if p['row_id'] in old_selected}:raise ValueError('RU2T decision coverage differs')
    full=True; chosen=sorted(lineids-old_selected);random.Random(SEED).shuffle(chosen)
    quotas=dict(Counter(book_id(r) for r in rr if r['id'] in chosen))
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
    info=dict(schema='RU3T0-v1',status='READY_FOR_READINGS',source=str(source),parent_sha256=before,seed=SEED,books=books,
        counts=dict(parent_rows=len(data),cyrillic_rows=len(rr),orthography_books=dict(Counter(b['orthography'] for b in books.values())),candidate_positions=len(candidates),candidate_lines=len(lineids),selected_lines=len(chosen),selected_positions=sum(p['row_id'] in chosen for p in candidates),missing_crops=len(unavailable),modern_spot_positions=min(10,len(modern))),
        plan='full' if full else 'sample 200',quotas=quotas,contexts=contexts,inputs=inputs,scanner_sha256=SCANNER_SHA,
        pack_inputs={str(p):sha(p) for p in list(pack.rglob('*'))+list((art/'keys').glob('*.json'))+[art/'candidate_positions.full.jsonl',art/'selected_lines.jsonl'] if p.is_file()},
        budget=dict(points_per_100_reads=.2,full_reads=2*(len(lineids)+fullcontrols),full_points=round(2*(len(lineids)+fullcontrols)*.002,3),selected_reads=2*sum(c['items'] for c in contexts),selected_points=round(2*sum(c['items'] for c in contexts)*.002,3)),
        policy='Every lowercase word-final ь including pre_hyphen is read twice. Google ъ never changes. Two hard calls with RU1 valid control evidence permit ъ; unreadable/disagreement holds. Modern books excluded. Prior unknown: no lexical veto.',
        no_reader_run=True,network=False,git_writes=False)
    if any(sha(p)!=h for p,h in inputs.items()):raise ValueError('input changed during build')
    info['inputs'].update({str(p):sha(p) for p in tool_inputs()+[prior,old_art/'decisions.jsonl',old_art/'selected_lines.jsonl',old_art/'build.json']})
    info.update(prior=str(prior),prior_sha256=expected_prior,old_art=str(old_art),inherited_lines=len(old_selected),pack=str(pack),planned_reads=2*sum(c['items'] for c in contexts))
    dump(art/'build.json',info)
    return info

def collect_context(art,pack,name,reader,seen):
    stem=reader_stem(name,reader);ans=art/'answers'/stem;rd=pack/name/reader
    runpath=Path(str(ans)+'.run.json');run=json.loads(runpath.read_text())
    if run['rc']!=0 or run['model']!='gpt-6.1-sol':raise ValueError('failed reader/model')
    rollout=Path(run['rollout']);digest=sha(rollout)
    if digest in seen:raise ValueError('independent reads reuse rollout')
    seen.add(digest)
    metadata=[r.get('payload',{}) for r in rows(rollout) if r.get('type') in {'session_meta','turn_context'}]
    models={r['model'] for r in metadata if r.get('model')}
    efforts={r.get('effort',r.get('reasoning_effort')) for r in metadata if r.get('effort',r.get('reasoning_effort'))}
    if models!={'gpt-6.1-sol'} or efforts!={'medium'}:raise ValueError('rollout model/effort mismatch')
    scan=scan_rollout.inspect(rollout,rd);dump(Path(str(ans)+'.scan.json'),scan)
    if not scan['ok'] or scan['scanner_version']!='v4.4-canonical':raise ValueError('unclean canonical scan')
    items=list(rows(rd/'items.jsonl'));cov=coverage(scan,rollout,rd,items)
    dump(Path(str(ans)+'.coverage.json'),cov)
    answerpath=rd/'answers.jsonl';keypath=art/f'keys/{stem}.json'
    mapped,_=map_records(list(rows(answerpath)),json.loads(keypath.read_text()),items,reader)
    mapped=[p for p in mapped if p['item_id'] not in set(cov['dropped_items'])]
    gate=score_controls(mapped,name)
    # No observed, usable controls cannot certify this context.
    if not gate['correct']:gate['status']='VOID';gate['reason']='no_usable_correct_controls'
    for p in mapped:
        p['context_void']=gate['status']=='VOID'
        p['edit_proposal']=dict(offset=p['offset'],old='ь',new='ъ') if not p['control'] and p['google']=='ь' and p['call']=='ъ' and not p['context_void'] else None
    jsonl(Path(str(ans)+'.mapped.jsonl'),mapped);dump(Path(str(ans)+'.controls.json'),gate)
    evidence={str(p):sha(p) for p in [runpath,rollout,answerpath,keypath,*[Path(str(ans)+s) for s in ['.scan.json','.coverage.json','.mapped.jsonl','.controls.json']]]}
    return mapped,gate,cov,evidence


def merge_labels(data,prior,decisions):
    """Apply new decisions to the v2-train labels; retain RU2T final rows exactly."""
    result,counts=apply_version(data,[dict(d,decision='hold' if d['decision']=='lead_review' else d['decision']) for d in decisions])
    old={r['id']:r for r in prior}
    if len(old)!=len(prior) or set(old)!={r['id'] for r in result}:raise ValueError('RU2T ids differ')
    changed={d['row_id'] for d in decisions}
    return [r if r['id'] in changed else old[r['id']] for r in result],counts


def finalize(art=ART,pack=PACK,source=SOURCE,registry=REGISTRY,output=None):
    info=validate(art,pack)
    if sha(source)!=info['parent_sha256']:raise ValueError('parent changed')
    old_art=Path(info['old_art']);prior=Path(info['prior'])
    if sha(prior)!=info['prior_sha256']:raise ValueError('RU2T labels changed')
    selected={r['row_id'] for r in rows(art/'selected_lines.jsonl')}
    expected={(p['row_id'],p['offset']):dict(p,source_id=p['row_id'],prior='unknown',control=False) for p in rows(art/'candidate_positions.full.jsonl') if p['row_id'] in selected}
    votes=defaultdict(list);seen=set();evidence={};coverages={};contexts={};fresh=[]
    for c in info['contexts']:
        name=c['context']
        for reader in ('r1','r2'):
            identity=name+'/'+reader
            try:
                mapped,gate,cov,ev=collect_context(art,pack,name,reader,seen)
                evidence.update(ev);coverages[identity]=cov
                contexts[identity]=dict(status=gate['status'],gate=gate)
                if gate['status']=='VOID':continue
                for p in mapped:
                    k=p['row_id'],p['offset']
                    if p['control'] or k not in expected:continue
                    if any(v['reader']==reader for v in votes[k]):raise ValueError('duplicate independent vote')
                    votes[k].append(dict(reader=reader,context=identity,call=p['call'],gate_status='VALID',confidence=p['confidence'],item_id=p['item_id']))
            except (OSError,ValueError,KeyError,TypeError) as exc:
                contexts[identity]=dict(status='FAILED',reason=str(exc))
    decisions=[]
    for k,p in sorted(expected.items()):
        d=combine_position(p,votes[k])
        if d['decision']=='hold':d['decision']='lead_review'
        decisions.append(d)
        missing=[r for r in ('r1','r2') if not any(v['reader']==r for v in votes[k])]
        if missing:fresh.append(dict(row_id=k[0],offset=k[1],missing_readers=missing,action='fresh-r3 re-read; fresh ids and independent context required'))
    inherited=list(rows(old_art/'decisions.jsonl'))
    if {(d['row_id'],d['offset']) for d in inherited}&set(expected):raise ValueError('inherited/new decisions overlap')
    partial=(art/'STOPPED_AT_70.json').exists();version='ru1_v3_train'+('_partial' if partial else '')
    output=output or WORK/f'artifacts/ru1/{version}.jsonl'
    result,counts=merge_labels(list(rows(source)),list(rows(prior)),decisions)
    jsonl(art/'decisions.jsonl',decisions);jsonl(art/'decisions_merged.jsonl',inherited+decisions)
    jsonl(art/'fresh_r3_positions.jsonl',fresh);jsonl(art/'per_row_decision_counts.jsonl',counts);jsonl(output,result)
    # Covered means every candidate position in the line has two admitted reads,
    # including inherited RU2T decisions (whose final adjudications stay frozen).
    lineok=defaultdict(list)
    for d in decisions:lineok[d['row_id']].append(len(votes[d['row_id'],d['offset']])==2)
    covered={r['row_id'] for r in rows(old_art/'selected_lines.jsonl')}|{i for i,v in lineok.items() if all(v)}
    if partial:(art/'covered_lines.txt').write_text(''.join(i+'\n' for i in sorted(covered)))
    manifest=dict(version=version,parent=dict(path=str(source),sha256=sha(source)),inherited=dict(path=str(prior),sha256=sha(prior),lines=info['inherited_lines']),output=dict(path=str(output),sha256=sha(output),rows=len(result)),counts=dict(Counter(d['decision'] for d in decisions)),partial=partial,covered_lines=len(covered),contexts=contexts,coverage=coverages,evidence=evidence,scanner_sha256=SCANNER_SHA,fresh_r3_positions=len(fresh))
    manifest['artifacts']={str(p):sha(p) for p in [art/'build.json',art/'decisions.jsonl',art/'decisions_merged.jsonl',art/'fresh_r3_positions.jsonl',art/'per_row_decision_counts.jsonl']}
    if partial:manifest['artifacts'][str(art/'STOPPED_AT_70.json')]=sha(art/'STOPPED_AT_70.json');manifest['artifacts'][str(art/'covered_lines.txt')]=sha(art/'covered_lines.txt')
    dump(output.with_name(version+'_manifest.json'),manifest)
    output.with_suffix('.sha256').write_text(sha(output)+'  '+output.name+'\n')
    obj=json.loads(registry.read_text());versions=obj['versions'];parent='collection_v2_train'
    if parent in versions and versions[parent]['sha256']!=info['parent_sha256']:raise ValueError('registered parent differs')
    versions[parent]=dict(path=str(source),sha256=sha(source),parent=None,text_field='label',id_field='id',status='local')
    versions[version]=dict(path=str(output),sha256=sha(output),parent=parent,text_field='label',id_field='id',status='local',population=dict(rows=len(result),definition='exact full train labels; RU2T inherited, RU3T corrections; unresolved positions HOLD',covered_candidate_lines=len(covered)),read='exact id label; no fallback')
    dump(registry,obj)
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','finalize']);a=p.parse_args()
    if a.action=='build':print(json.dumps(build(),ensure_ascii=False,indent=2))
    else:
        result=finalize()
        from ru3t_delivery import deliver
        print(json.dumps(deliver(result),ensure_ascii=False,indent=2))
