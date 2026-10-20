"""Offline saved-evidence re-report. No Pipeline.evaluate, native, reader or detector calls."""
import sys, os, json, gzip, hashlib, datetime, importlib.util, unicodedata as ud, math
from pathlib import Path
from collections import Counter, defaultdict
from zoneinfo import ZoneInfo
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[4]; OUT=Path(__file__).resolve().parent; STEPS=OUT.parent
sys.path.insert(0,str(ROOT))
def guard(event,args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo'): raise RuntimeError('network OFF')
    if event=='open':
        path,mode,flags=args
        if isinstance(path,(str,bytes,os.PathLike)) and ((isinstance(mode,str) and any(c in mode for c in 'wax+')) or (flags and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))):
            if not Path(path).resolve().is_relative_to(OUT): raise RuntimeError('write outside output: '+str(path))
sys.addaudithook(guard)
import numpy as np
from greekocr.harvest import admission as adm
from greekocr.harvest.line_pipeline import inventory,expectations,content_gate_exclusion,short_line_exclusion,crop_aspect,canonical
from greekocr.harvest.text_primitives import codec_letter_script
INPUTS={}
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def track(p):
    p=Path(p).resolve();INPUTS[str(p)]=sha(p);return p
def read(p):return [json.loads(l) for l in track(p).read_text().splitlines() if l.strip()]
def load(p):return json.loads(track(p).read_text())
def dump(name,x): (OUT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
def write(name,rs):
    with (OUT/name).open('w') as f:
        for r in rs:f.write(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n')
def module(name,p):
    track(p);s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def snapshot():
    out={}
    for base,dirs,files in os.walk(ROOT):
        dirs[:]=[d for d in dirs if Path(base)/d!=OUT]
        for f in files:
            p=Path(base)/f
            try:s=p.stat();out[str(p.relative_to(ROOT))]=[s.st_size,s.st_mtime_ns,s.st_ctime_ns]
            except FileNotFoundError:pass
    # Linked worktree git metadata also remains read only.
    return out

def stamp(m):
    s=m.get('updated','')
    if not s:return 0
    d=datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
    return (d if d.tzinfo else d.replace(tzinfo=ZoneInfo('Europe/Athens'))).timestamp()
def latest(ms):
    ans={}
    for i,m in enumerate(ms):
        if m['line_id'] not in ans or (stamp(m),i)>=(stamp(ans[m['line_id']]),ans[m['line_id']]['file_line']):ans[m['line_id']]=dict(m,file_line=i)
    return ans

def named_script(c):
    s=codec_letter_script(c,CODEC)
    if s!='other':return s
    name=ud.name(c,'UNNAMED')
    if c in 'ºªµ':return 'codec:'+name
    return 'CJK' if name.startswith(('CJK','IDEOGRAPHIC')) else name.split()[0]

CODEC=adm.load_codec();track(CODEC['path'])
for p in ['greekocr/harvest/line_pipeline.py','greekocr/harvest/admission.py','greekocr/harvest/text_primitives.py','greekocr/harvest/filtering_assets/segmentation-policy.js','docs/harvest/line_pipeline/gate03/REPORT.md','docs/harvest/line_pipeline/gate03/REPORT_part2.md','docs/harvest/seg_steps/s4/REPORT.md','docs/harvest/seg_steps/s5/BAND_PROPOSAL.md','docs/harvest/seg_steps/s5/build_population.py','docs/harvest/seg_steps/sheet/README.md','docs/harvest/seg_steps/sheet/build.py'] :track(ROOT/p)
BASE=ROOT.parent/'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1'
SWEEP=module('saved_band_sweep',STEPS/'s5/band_sweep.py')
COMMON=module('saved_cells_common',BASE/'cells_opus/scripts/common.py')
PART2=module('saved_part2_metadata',ROOT/'docs/harvest/line_pipeline/gate03/part2_analysis.py')

def main():
    initial=snapshot();dump('initial_scope.json',initial)
    rs=read(STEPS/'s4/replay.jsonl');ts=read(STEPS/'s4/typology_replay.jsonl');extra=read(STEPS/'s4/extra_numeric.jsonl')
    bp=read(STEPS/'s5/band_population.jsonl');changed=read(STEPS/'s5/changed_lines.jsonl');cards=read(STEPS/'sheet/cards.jsonl')
    ms=read(STEPS/'s4/owner_marks_snapshot.jsonl');tm=read(STEPS/'s4/typology_owner_marks_snapshot.jsonl');marks=latest(ms);tmarks=latest(tm)
    # Same finite-set reconstruction as the gate03 part-2 diagnostic; all original fields retained.
    track(PART2.INPUTS);track(PART2.SAMPLES);track(PART2.TYPOLOGY)
    sets=PART2.sets(); rows_by_set={k:{r['id']:r for r in v} for k,v in sets.items()}
    samples={r['line_id']:r for r in read(BASE/'cells_opus/samples.jsonl')}
    pool={}
    for r in rs:pool[r['line_id']]=dict(r,versions=dict(s3=r['before'],s4=r['after']))
    for t in ts:
        if t['line_id'] not in pool:pool[t['line_id']]=t
    for r in extra:pool[r['line_id']]=r
    meta={}
    for k,v in rows_by_set.items():
        for rid,r in v.items():
            if rid not in meta:meta[rid]=r
    for r in ts:
        if r['line_id'] not in meta:
            meta[r['line_id']]=dict(r['row'],source=r['manifest']['source'],wave=r['manifest']['wave'])
    for r in extra:
        m=samples[r['line_id']];meta[r['line_id']]=dict(r['row'],source=m.get('source',r['line_id'].split('--')[0]))
        if 'wave' in m:meta[r['line_id']]['wave']=m['wave']
    for rid,row in meta.items():
        row.setdefault('source',rid.split('--',1)[0]);row.setdefault('book_id',rid.rsplit('--s',1)[0]);row.setdefault('page_id',rid.rsplit('-l',1)[0])
    # No books/pages declarations are carried by step-1 inputs; source_policy is the pipeline fallback.
    all_inputs=read(STEPS/'s1/inputs.jsonl')
    metadata_fields=Counter(k for x in all_inputs for k in x if k in ('metadata','books','pages','expectations'))
    assert not metadata_fields,metadata_fields
    unresolved=[];dimension_sha={};decisions={}
    def gate(row,setname,independent=True):
        text=row['raw_text'];inv=inventory(text,CODEC)
        try:ex=expectations(row,{})
        except (ValueError,KeyError) as e:
            unresolved.append(dict(set=setname,id=row['id'],error=str(e),text=text));return dict(id=row['id'],text=text,kind=None,unresolved=str(e),part1=None,part2=None)
        if row.get('crop_bbox') is None and row.get('crop_path'):
            p=row['crop_path']
            if p not in dimension_sha:dimension_sha[p]=sha(p)
            assert dimension_sha[p]==row['crop_sha256'],row['id']
        result=content_gate_exclusion(text,inv,ex,CODEC,row,{})
        issues=result[1] if result else []
        reason=issues[0]['reason'] if issues else None
        p1='mixed' if reason=='mixed_script_word' else 'foreign' if reason=='unexpected_script' else None
        # Part-2-only ablation: independently apply the pipeline's length helper, also on part-1 failures.
        p2=short_line_exclusion(row,inv,ex,{})
        return dict(id=row['id'],text=text,kind=p1 or reason,part1=p1,part2=p2['reason'] if p2 else None,outcome=result[0] if result else 'ADMIT',reasons=issues,words=inv['mixed_words'],scripts=inv['scripts'],expected=ex,resolution='source policy adm.expected_policy',source=row['source'],book_id=row['book_id'],page_id=row['page_id'],A=crop_aspect(row))
    for name,rows in sets.items():
        decisions[name]={r['id']:gate(r,name) for r in rows}
    global_dec={rid:gate(r,'unique_saved_pool') for rid,r in meta.items()}
    def ds(ids):return {rid:global_dec[rid] for rid in ids}
    decisions['owner_marks']=ds(marks)
    decisions['rated_888']=ds(r['line_id'] for r in rs if r['cohort']=='calibration' and (r.get('owner_rating') or {}).get('decision') in ('KEEP','DROP'))
    decisions['typology_marked']=ds(r['line_id'] for r in ts if not r['manifest']['control'] and r['line_id'] in tmarks)
    small=read(STEPS/'s4/small.jsonl')
    # Small diagnostics contain overlapping cohort records, retained as such in the counts.
    decisions['small']={str(i):global_dec[r['line_id']] for i,r in enumerate(small)}
    decisions['band_population']=ds(r['line_id'] for r in bp)
    decisions['changed_lines']=ds(dict.fromkeys(r['line_id'] for r in changed))
    decisions['sheet']=ds(r['line_id'] for r in cards)
    nums=[r for r in pool.values() if r['small'] and COMMON.output_type(r['row']['raw_text'])=='numeric']
    decisions['numeric_fit']=ds(r['line_id'] for r in nums)
    tw=read(STEPS/'s4/two_by_two_predictions.jsonl');decisions['two_by_two']=ds(r['line_id'] for r in tw)
    write('row_decisions.jsonl',[dict(d,set=k,entry=entry) for k,v in decisions.items() for entry,d in v.items()])
    write('gate_failed.jsonl',[dict(d,set=k) for k,v in decisions.items() for d in v.values() if d['kind']])
    dump('unresolved_expectations.json',unresolved)
    def removed(d,mode):return bool(d['kind']) if mode=='all' else bool(d['part1']) if mode=='mixed_foreign' else bool(d['part2']) if mode=='part2_only' else False
    def keep_rows(rows,mode):return [r for r in rows if not removed(global_dec[r['line_id']],mode)]
    modes=('before','mixed_foreign','part2_only','all')
    counts={}
    for name,v in decisions.items():
        dd=list(v.values());p1=Counter(d['part1'] for d in dd if d['part1']);p2=Counter(d['part2'] for d in dd if d['part2']);actual=Counter(d['kind'] for d in dd if d['kind'] and not d['part1'])
        counts[name]=dict(before=len(dd),after=sum(not d['kind'] for d in dd),mixed=p1['mixed'],foreign=p1['foreign'],part2_after_precedence=dict(actual),part2_only=dict(p2),mixed_foreign_only_after=sum(not d['part1'] for d in dd),part2_only_after=sum(not d['part2'] for d in dd),resolution=dict(Counter(d.get('resolution','unresolved') for d in dd)))
    # All original scoring functions are simple saved-label comparisons; no validation main is called.
    VERS=('08','s1','s2','s3','s4')
    def score(rows,pred,label):
        c={v:{m:sum(pred(r)==v and label(r)==m for r in rows) for m in ('KEEP','DROP')} for v in ('KEEP','DROP','UNCERTAIN')}
        return dict(n=len(rows),agreement=c['KEEP']['KEEP']+c['DROP']['DROP'],confusion=c)
    scores={}
    for mode in modes:
        mainrows=keep_rows(rs,mode);out={}
        a=[r for r in mainrows if r['cohort']=='segeval1'];b=[r for r in mainrows if r['cohort']=='calibration' and (r.get('owner_rating') or {}).get('decision') in ('KEEP','DROP')];c=[r for r in mainrows if r['cohort']=='cells']
        unique={r['line_id']:r for r in mainrows};marked=[unique[rid] for rid in marks if rid in unique]
        for v in VERS:
            out[v]=dict(segeval1=dict(n=len(a),FP=sum(r['verdict_'+v]=='DROP' and r['owner_standard_state']=='fine' for r in a),FN=sum(r['verdict_'+v]=='KEEP' and r['owner_standard_state']=='faulty' for r in a),UNC=sum(r['verdict_'+v]=='UNCERTAIN' for r in a)),rated=score(b,lambda r:r['verdict_'+v],lambda r:r['owner_rating']['decision']),marks=score(marked,lambda r:r['verdict_'+v],lambda r:marks[r['line_id']]['owner_mark']),cells=dict(n=len(c),verdicts=dict(Counter(r['verdict_'+v] for r in c)),transitions=dict(Counter(r['verdict_s3']+'->'+r['verdict_s4'] for r in c))))
        bed=keep_rows([t for t in ts if not t['manifest']['control']],mode)
        out['typology']={v:dict(overall=score([t for t in bed if t['line_id'] in tmarks],lambda t:t['versions'][v]['verdict'],lambda t:tmarks[t['line_id']]['owner_mark']),final_type={g:dict(bed_n=sum(t['manifest']['final_type']==g for t in bed),**score([t for t in bed if t['manifest']['final_type']==g and t['line_id'] in tmarks],lambda t:t['versions'][v]['verdict'],lambda t:tmarks[t['line_id']]['owner_mark'])) for g in sorted({t['manifest']['final_type'] for t in ts if not t['manifest']['control']})}) for v in ('08','s3','s4')}
        scores[mode]=out
    old=load(STEPS/'s4/summary.json')
    for v in VERS:
        assert scores['before'][v]['segeval1']==dict(n=150,**old['cohorts']['segeval1']['errors'][v])
        assert scores['before'][v]['rated']==old['cohorts']['calibration']['rated'][v]
        assert scores['before'][v]['marks']==old['owner_marks'][v]
    for v in ('08','s3','s4'):assert scores['before']['typology'][v]['overall']==old['typology']['results'][v]['overall']
    # Unchanged saved fits' owner exclusions = union of explicit marks and ratings.
    judged={r['line_id'] for r in rs if (r.get('owner_rating') or {}).get('decision') in ('KEEP','DROP')}|set(marks)|set(tmarks)
    def ratio(r,box):
        g=r['geometry'];f=g['s3_frame']
        if box=='s3':return max(f['length'],f['height'])/min(f['length'],f['height']) if f else None
        b=g['all_box'];return (b[2]-b[0])/(b[3]-b[1]) if b else None
    def fit(rows,box,exclude):
        sel=[r for r in rows if r['line_id'] not in exclude and ratio(r,box) is not None]
        x=np.array([r['chars'] for r in sel]);y=np.array([ratio(r,box) for r in sel]);a,b=np.polyfit(x,y,1);res=y-(a*x+b)
        return dict(a=float(a),b=float(b),SD=float(res.std(ddof=2)),MAD=float(np.median(np.abs(res-np.median(res)))),n=len(sel),ids=[r['line_id'] for r in sel])
    fits={mode:{box:{kind:fit(keep_rows(nums,mode),box,judged if kind=='without_owner' else set()) for kind in ('all','without_owner')} for box in ('s3','s4')} for mode in modes}
    for box in ('s3','s4'):
        for kind in ('all','without_owner'):
            f=fits['before'][box][kind];z=old['numeric']['fits'][box][kind]
            assert f['n']==z['n'] and abs(f['a']-z['a'])<1e-12 and abs(f['SD']-z['residual_SD'])<1e-12
    matrix={mode:{kind:{typ:{key:score([r for r in keep_rows(tw,mode) if r['fit']==kind and r['type']==typ],lambda r:r['predictions'][key],lambda r:r['owner']['owner_mark']) for key in ('s3/text-font','s4/text-font','s3/short-numeric','s4/short-numeric')} for typ in ('numeric','mixed','non-numeric')} for kind in ('without_owner','all')} for mode in modes}
    # Refit diagnostic uses only saved gate/box/padding, no service/detector calls.
    def pure_decide(z,pred):
        e=z['evidence'];g=e['gate']
        if g['verdict']!='PASS':return g['verdict']
        b=e['box_evidence'];ch=e['characters']
        if not b['available'] or pred is None or not math.isfinite(pred) or pred<0:return 'UNCERTAIN'
        rr=(ch+1)/(pred+1)
        if rr<.5 or rr>1.5:return 'DROP'
        p=e['padding_evidence'];pad=p.get('total_padding_line_heights')
        if not p['available'] or pad is None or not math.isfinite(pad):return 'UNCERTAIN'
        return 'DROP' if pad>1.5 else 'KEEP'
    refitted={};refit_rows=[]
    for mode in modes:
        tt=[]
        for t in keep_rows(tw,mode):
            r=pool[t['line_id']];preds={}
            for box in ('s3','s4'):
                z=r['versions'][box];preds[box+'/text-font']=z['verdict'];f=fits[mode][box][t['fit']];q=ratio(r,box)
                pred=(q-f['b'])/f['a'] if z['evidence']['box_evidence']['available'] and q is not None else None
                preds[box+'/short-numeric']=pure_decide(z,pred)
                if mode=='before':assert preds[box+'/short-numeric']==t['predictions'][box+'/short-numeric'],t['line_id']
            tt.append(dict(t,predictions=preds))
        refitted[mode]={kind:{typ:{key:score([r for r in tt if r['fit']==kind and r['type']==typ],lambda r:r['predictions'][key],lambda r:r['owner']['owner_mark']) for key in ('s3/text-font','s4/text-font','s3/short-numeric','s4/short-numeric')} for typ in ('numeric','mixed','non-numeric')} for kind in ('without_owner','all')}
        if mode=='all':refit_rows=tt
    write('two_by_two_refitted.jsonl',refit_rows)
    def best(m):
        return {t:[k for k,s in z.items() if s['agreement']==max(v['agreement'] for v in z.values())] for t,z in m['without_owner'].items()}
    small_survival={mode:dict(Counter(COMMON.output_type(pool[rid]['row']['raw_text']) for rid in pool if pool[rid]['small'] and not removed(global_dec[rid],mode))) for mode in modes}
    # Full saved-grid sweep, ablations and stability, using only the pure original sweep functions.
    sweeps={};stabilities={};weights={};fixed={}
    for mode in modes:
        p=keep_rows(bp,mode);sweeps[mode]={g:SWEEP.sweep_group([r for r in p if fn(r)]) for g,fn in SWEEP.GROUPS.items() if any(fn(r) for r in p)}
        weights[mode]={g:SWEEP.weight_sensitivity([r for r in p if SWEEP.GROUPS[g](r)]) for g in ('overall','numeric')}
        fixed[mode]={g:{f'{L:.2f}-{U:.2f}':dict(n=len(rr),objective_n=sum(not r['length_blind'] for r in rr),**SWEEP.errors(rr,L,U,True)) for L,U in ((.5,1.5),(.3,2),(.35,2),(.55,1.3))} for g,rr in [('overall',p),('numeric',[r for r in p if r['output_type']=='numeric'])]}
        if mode in ('before','all'):
            stabilities[mode]={}
            for g in ('overall','numeric'):
                rr=[r for r in p if SWEEP.GROUPS[g](r)];opt=sweeps[mode][g]['end_to_end']['proposed'];band=(opt['L'],opt['U']);halves=[[r for r in rr if SWEEP.h(r['line_id'])==i] for i in (0,1)]
                stabilities[mode][g]=dict(split_half=[SWEEP.heldout(halves[0],halves[1],'1'),SWEEP.heldout(halves[1],halves[0],'0')],loso_source_set=[SWEEP.heldout([r for r in rr if r['source_set']!=s],[r for r in rr if r['source_set']==s],s) for s in sorted({r['source_set'] for r in rr})],loso_cohort=[SWEEP.heldout([r for r in rr if r['cohort']!=s],[r for r in rr if r['cohort']==s],s) for s in sorted({r['cohort'] for r in rr})],bootstrap=SWEEP.bootstrap(rr,band))
    orig_sweep=load(STEPS/'s5/sweep.json')
    assert sweeps['before']==orig_sweep['groups']
    changed_new=[]
    for scheme in ('overall','numeric'):
        band=sweeps['all'][scheme]['end_to_end']['proposed'];L,U=band['L'],band['U']
        for r in keep_rows(bp,'all'):
            if not SWEEP.GROUPS[scheme](r):continue
            a,b=SWEEP.verdict(r,.5,1.5),SWEEP.verdict(r,L,U)
            if (a=='KEEP')!=(b=='KEEP'):changed_new.append(dict(r,scheme=scheme,band=[L,U],current=a,proposed=b,effect='length cannot see this' if r['length_blind'] else 'fixes' if (b=='KEEP')==(r['owner_mark']=='KEEP') else 'breaks'))
    write('changed_lines_before.jsonl',changed);write('changed_lines_filtered_original_band.jsonl',keep_rows(changed,'all'));write('changed_lines.jsonl',changed_new)
    write('band_population.jsonl',keep_rows(bp,'all'))
    # Coordinator cross-check is only scripts; part-2 never participates.
    coordinator_path=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/db202b49-34e2-49d2-9fbd-271fe776b56d/scratchpad/foreign_mixed_ids.json')
    coord=load(coordinator_path);disagreements=[]
    for rid,d in global_dec.items():
        c='mixed' if rid in coord['mixed'] else 'foreign' if rid in coord['foreign'] else None
        if c!=d['part1']:
            chars=[dict(char=c,name=ud.name(c,''),pipeline_script=codec_letter_script(c,CODEC)) for c in sorted(set(d['text'])) if ud.category(c).startswith('L') and (c in 'ºªµ' or codec_letter_script(c,CODEC) in ('other','cyrillic'))]
            disagreements.append(dict(id=rid,coordinator=c,pipeline=d['part1'],text=d['text'],reason='Pipeline codec-aware letter votes and adm.words tokenization; mixed-word DROP precedes foreign HOLD; expected scripts use source/class policy.',words=d.get('words',[]),scripts=d.get('scripts',{}),expected=d.get('expected'),characters=chars,sets=[k for k,v in decisions.items() if any(x['id']==rid for x in v.values())]))
    write('coordinator_disagreements.jsonl',disagreements)
    group_counts={mode:dict(Counter(c['section']+'/'+c['group'] for c in keep_rows(cards,mode))) for mode in modes}
    proposed_ids={r['line_id'] for r in changed_new};moves=[]
    for c in keep_rows(cards,'all'):
        sec='proposal' if c['line_id'] in proposed_ids else 'changed' if c['changed_08_s4'] else 'absent'
        if sec!=c['section']:moves.append(dict(id=c['line_id'],before=c['section'],after=sec,group=c['group']))
    write('sheet_failed_cards.jsonl',[dict(c,gate=global_dec[c['line_id']]) for c in cards if global_dec[c['line_id']]['kind']]);dump('sheet_section_changes.json',moves)
    ownercases=[]
    for rid,why in SWEEP.OWNER_CASES:
        p=next((r for r in bp if r['line_id']==rid),None)
        ownercases.append(dict(id=rid,why=why,gate=global_dec.get(rid),saved=p,after='excluded before segmentation' if global_dec.get(rid,{}).get('kind') else 'survives',current=SWEEP.verdict(p,.5,1.5) if p else None,original_proposal=SWEEP.verdict(p,.3,2) if p else None))
    summary=dict(counts=counts,scores=scores,fits=fits,two_by_two_saved=matrix,two_by_two_refitted=refitted,best_before=best(matrix['before']),best_after=best(matrix['all']),best_refitted_after=best(refitted['all']),small_survival=small_survival,sweeps=sweeps,stability=stabilities,weights=weights,fixed_bands=fixed,sheet_groups=group_counts,sheet_section_changes=moves,owner_cases=ownercases,coordinator_disagreements=len(disagreements),unresolved=unresolved,metadata_declarations_carried=dict(metadata_fields),dimension_sha_verified=len(dimension_sha),changed_counts=dict(before=len({r['line_id'] for r in changed}),filtered_original=len({r['line_id'] for r in keep_rows(changed,'all')}),refitted=len({r['line_id'] for r in changed_new})))
    dump('finite_summary.json',summary)
    print('FINITE COMPLETE',json.dumps(counts,ensure_ascii=False),flush=True)
    census(summary,coord)
    dump('summary.json',summary)
    final=snapshot();assert initial==final,{'changed':[p for p in initial if final.get(p)!=initial[p]],'added':list(set(final)-set(initial))}
    dump('receipt.json',dict(created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),network='OFF audit hook',readers=0,segmentation_runs=0,pipeline_evaluate_calls=0,git_writes=False,scope='Only docs/harvest/seg_steps/gate_rereport/',unchanged_outside_output=len(initial),scope_stat_identity=True,baseline_scores_reproduced=True,baseline_sweep_reproduced=True,baseline_numeric_fits_reproduced=True,baseline_two_by_two_reproduced=True,input_sha256=INPUTS,artifacts={p.name:sha(p) for p in OUT.iterdir() if p.is_file() and p.name!='receipt.json'}))


def census(summary,coord):
    path=track(BASE/'cells/population_cells.jsonl.gz');track(BASE/'script_inventory_20261019.md')
    groups={};codec_rows=[];unknown=[];outcomes=Counter();resolution=Counter();n=0;flagged=[]
    with gzip.open(path,'rt') as f:
        for line in f:
            r=json.loads(line);rid=r['row_id'];text=r['raw_text'];n+=1
            # Owner defines book as second segment. Non-W1/W2 IDs without '--' remain explicit unresolved book identity.
            parts=rid.split('--');book=parts[1] if len(parts)>1 else None
            row=dict(r,id=rid,book_id=r.get('book_id',book or rid.rsplit('-l',1)[0]),page_id=r.get('page_id',rid.rsplit('-l',1)[0]))
            if r.get('width_px',0)>0 and r.get('height_px',0)>0:row['crop_bbox']=[0,0,r['width_px'],r['height_px']]
            inv=inventory(text,CODEC)
            try:ex=expectations(row,{});resolution['source policy adm.expected_policy']+=1
            except (ValueError,KeyError) as e:unknown.append(dict(id=rid,source=r['source'],error=str(e),text=text));continue
            gate=content_gate_exclusion(text,inv,ex,CODEC,row,{})
            outcome=gate[0] if gate else 'ADMIT';reason=gate[1][0]['reason'] if gate else 'gate_admitted';outcomes[reason]+=1
            allowed=set(ex['scripts'])|({'latin'} if ex.get('latin_policy')=='mixed_class_or_minority' else set())
            unexpected={s for s in inv['scripts'] if s not in allowed}
            named=Counter(named_script(c) for c in text if codec_letter_script(c,CODEC) in unexpected and c not in 'ºªµ')
            for c in 'ºªµ':
                if c in text:codec_rows.append(dict(id=rid,source=r['source'],book=book,character=c,name=ud.name(c),count=text.count(c),pipeline_script=codec_letter_script(c,CODEC),gate_outcome=outcome,gate_reason=reason,text=text))
            for script,ct in named.items():
                key=(r['source'],book,script)
                if key not in groups:groups[key]=dict(source=r['source'],book=book,script=script,rows=0,outcomes=Counter(),whole_token_rows=0,mixed_word_rows=0,examples=[],ids=[])
                g=groups[key];g['rows']+=1;g['outcomes'][outcome+' '+reason]+=1;g['ids'].append(rid)
                tokens=adm.words(text);whole=[w for w in tokens if len([c for c in w if named_script(c)==script])>=2 and {named_script(c) for c in w if codec_letter_script(c,CODEC)}=={script}]
                g['whole_token_rows']+=bool(whole);g['mixed_word_rows']+=any(any(named_script(c)==script for c in w) for w in inv['mixed_words'])
                # Keep a varied witness reservoir, including longer script tokens.
                example=dict(id=rid,text=text,outcome=outcome,reason=reason,whole_words=whole,mixed_words=inv['mixed_words'])
                if len(g['examples'])<3:g['examples'].append(example)
                elif whole and not any(e['whole_words'] for e in g['examples']):g['examples'][-1]=example
            if unexpected:flagged.append(dict(id=rid,source=r['source'],book=book,text=text,expected=ex,scripts=inv['scripts'],unexpected_scripts=sorted(unexpected),mixed_words=inv['mixed_words'],outcome=outcome,reason=reason))
            if n%100000==0:print('CENSUS',n,'unexpected',len(flagged),flush=True)
    assert n==592466,n
    gs=[]
    for key,g in sorted(groups.items(),key=lambda kv:tuple(str(x) for x in kv[0])):
        g['outcomes']=dict(g['outcomes']);script=g['script'];whole=g['whole_token_rows'];mixed=g['mixed_word_rows']
        # Evidence flags, no expectation changes. Low counts or a mixture of token patterns remain borderline.
        if script in ('CJK','SYRIAC','ARABIC','HEBREW') and whole>=3 and whole>=.25*g['rows']:
            cls='a';why='Repeated stand-alone multi-letter tokens in this script; plausible real other-language content.'
        elif script in ('greek','latin','cyrillic') and mixed>=.5*g['rows']:
            cls='b';why='Most rows contain this script inside mixed-script words; letter-level confusion.'
        else:cls='c';why='Sparse or short script fragments; noise candidate, not proof of damaged pixels.'
        g.update(classification=cls,rationale=why,borderline=(g['rows']<10 or (cls=='a' and whole<.75*g['rows']) or (cls=='c' and whole>0)))
        gs.append(g)
    write('unexpected_scripts_rows.jsonl',flagged);write('unexpected_scripts_by_book.jsonl',gs);write('codec_questions.jsonl',codec_rows);dump('census_unresolved_expectations.json',unknown)
    summary['census']=dict(rows=n,unexpected_rows=len(flagged),table_entries=len(gs),gate_counts=dict(outcomes),expectation_resolution=dict(resolution),unresolved=unknown,book_identity='Second -- segment where present; null for IDs without it. No synthetic distinct books inferred.',class_counts=dict(Counter(g['classification'] for g in gs)),codec_rows=len({r['id'] for r in codec_rows}),codec_entries=len(codec_rows),codec_counts={c:dict(rows=len({r['id'] for r in codec_rows if r['character']==c}),books=len({(r['source'],r['book']) for r in codec_rows if r['character']==c})) for c in 'ºªµ'},script_totals={s:dict(rows=sum(g['rows'] for g in gs if g['script']==s),books=len({(g['source'],g['book']) for g in gs if g['script']==s})) for s in sorted({g['script'] for g in gs})})
    print('CENSUS COMPLETE',n,len(gs),flush=True)

if __name__=='__main__':main()
