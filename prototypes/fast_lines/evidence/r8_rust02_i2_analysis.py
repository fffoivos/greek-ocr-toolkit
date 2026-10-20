"""Summarize fixed27 attribution without treating inclusive library time as Python."""
import json,collections,statistics,math
from pathlib import Path

def analyze():
    O=Path('.astra/fast_lines/out/round8/R8-RUST-02-i2')
    r=json.loads((O/'PROFILE_RAW.json').read_text());assert len(r)==108
    # Raw v1 labels left frozen-code frames unresolved; conservatively charge
    # all their self time to Python here. No clock/call/edge value changes.
    for entry in r:
        if not entry['instrumented']:continue
        for stage in entry['profiles']:
            for f in stage['functions']:f['kind']='python_upper' if f['file']!='~' else 'builtin_or_unresolved'
            stage['python_upper_s']=sum(f['self_s'] for f in stage['functions'] if f['file']!='~')
            stage['builtin_or_unresolved_s']=sum(f['self_s'] for f in stage['functions'] if f['file']=='~')
    pure=json.loads((O/'PURE_CLOCK_RAW.json').read_text());assert len(pure)==54
    pure_by_id={(x['page'],x['repetition']):x for x in pure}
    for entry in r:
        if not entry['instrumented']:
            entry['stage_clock_total_timing']=entry['timing']
            entry['timing']=pure_by_id[(entry['page'],entry['repetition'])]['timing']
    pages=json.loads((O/'SLOW27.json').read_text())['pages']
    stages=sorted({s['stage'] for x in r for s in x['profiles']});records=[];pool=[]
    for rep in range(2):
     u={x['page']:x for x in r if x['repetition']==rep and not x['instrumented']}
     p={x['page']:x for x in r if x['repetition']==rep and x['instrumented']}
     total=sum(x['timing']['correction_s'] for x in u.values())
     for stage in stages:
      rows=[]
      for page in pages:
       name=page['page'];us=[s for s in u[name]['profiles'] if s['stage']==stage];ps=[s for s in p[name]['profiles'] if s['stage']==stage]
       py=sum(s['python_upper_s'] for s in ps);c=sum(s['builtin_or_unresolved_s'] for s in ps);elapsed=sum(s['elapsed_s'] for s in us)
       self_root=sum(max((f for f in s['functions'] if f['kind']=='python_upper'),key=lambda f:f['inclusive_s'])['self_s'] for s in ps)
       alloc=sum(f['self_s'] for s in ps for f in s['functions'] if f['kind']!='python_upper' and any(w in f['function'] for w in ('astype','array','empty','zeros','copy','reshape','ravel')))
       libpy=sum(f['self_s'] for s in ps for f in s['functions'] if f['kind']=='python_upper' and '/prototypes/fast_lines/' not in f['file'])
       row=dict(page=name,repetition=rep,stage=stage,calls=len(ps),uninstrumented_boundary_s=elapsed,correction_s=u[name]['timing']['correction_s'],root_python_self_upper_s=self_root,descendant_python_self_upper_s=py-self_root,library_python_self_upper_s=libpy,all_python_upper_s=py,visible_builtin_or_opaque_self_s=c,visible_conversion_allocation_self_s=alloc,raw_upper_fraction=py/u[name]['timing']['correction_s'],stage_scaled_upper_s=elapsed*py/(py+c) if py+c else 0,ufunc_caveat='untraced compiled work remains inside Python upper bound, not established interpreter cost')
       rows.append(row);records.append(row)
      py=sum(x['all_python_upper_s'] for x in rows);scaled=sum(x['stage_scaled_upper_s'] for x in rows)
      pool.append(dict(stage=stage,repetition=rep,pages=27,call_pages=sum(x['calls']>0 for x in rows),calls=sum(x['calls'] for x in rows),correction_s=total,uninstrumented_boundary_s=sum(x['uninstrumented_boundary_s'] for x in rows),raw_python_upper_s=py,raw_upper_fraction=py/total,scaled_python_upper_s=scaled,scaled_upper_fraction=scaled/total,free_upper_ceiling=1/(1-py/total)))
    # Deliberately conservative cross-pass upper envelope: largest numerator / smallest denominator.
    worst=[]
    for stage in stages:
     v=[x for x in pool if x['stage']==stage];f=max(x['raw_python_upper_s'] for x in v)/min(x['correction_s'] for x in v)
     worst.append(dict(stage=stage,upper_fraction=f,free_upper_ceiling=1/(1-f),raw_fraction_range=[min(x['raw_upper_fraction'] for x in v),max(x['raw_upper_fraction'] for x in v)],scaled_fraction_range=[min(x['scaled_upper_fraction'] for x in v),max(x['scaled_upper_fraction'] for x in v)]))
    worst.sort(key=lambda x:-x['upper_fraction']);assert worst[0]['upper_fraction']<.25
    res=[]
    for x in r:
     if x['instrumented']:continue
     elapsed=sum(s['elapsed_s'] for s in x['profiles']);res.append(dict(page=x['page'],repetition=x['repetition'],outside_named_stages_s=x.get('stage_clock_total_timing',x['timing'])['correction_s']-elapsed))
    result=dict(decision='NO PORT; close translation branch at 2/3; no safe new duplicate deletion established',gate=.25,largest=worst[0],stage_envelopes=worst,pooled_passes=pool,classification='Derived summaries include all Python code frames, including frozen-code frames that raw v1 left unresolved; clock/call values unchanged',uncertainty='Observed two-pass ranges and worst cross-pass upper envelope, not a confidence interval. Denominators are separate plain Stack passes with no extra wrappers; earlier no-profiler passes retain the lightweight per-stage boundary clocks. Raw Python self includes profiler overhead and untraced NumPy ufuncs; conservatively overstates portable interpreted time. Stage-scaled estimate is attribution only, never speed.',outside_named_stages_upper_s=sum(max(0,x['outside_named_stages_s']) for x in res)/2,source='SLOW27.json; PROFILE_PLAN/RAW stage attribution; PURE_CLOCK_PLAN/RAW plain Stack denominators; per-invocation pstats',runtime_change=False)
    for name,data in [('PROFILE_PER_PAGE.json',records),('BOUNDARY_DECISION.json',result),('OUTSIDE_STAGE_RESIDUAL.json',res)]: (O/name).write_text(json.dumps(data,indent=1)+'\n')
    lines=['# Fixed27 boundary decision — no new port','',str(result['decision']),'','Two complete uninstrumented correction passes: '+', '.join(f'{sum(x["timing"]["correction_s"] for x in r if not x["instrumented"] and x["repetition"]==rep):.6f}s' for rep in range(2))+'.','','| Stage | Calls/pass | Boundary seconds/pass | Python upper seconds/pass | Conservative fraction | Free upper ceiling |','|---|---:|---:|---:|---:|---:|']
    for w in worst:
     v=[x for x in pool if x['stage']==w['stage']];lines.append(f'| {w["stage"]} | '+ '/'.join(str(x['calls']) for x in v)+' | '+' / '.join(f'{x["uninstrumented_boundary_s"]:.3f}' for x in v)+' | '+' / '.join(f'{x["raw_python_upper_s"]:.3f}' for x in v)+f' | {100*w["upper_fraction"]:.3f}% | {w["free_upper_ceiling"]:.4f}× |')
    lines+=['',result['uncertainty'],'','No stage reaches 25% even with unresolved ufunc time charged to Python. Every nested boundary is bounded by its enclosing stage; shared helpers are separately retained in the operation census. Stages are alternatives, never summed to pass the gate. The complete compose route is not a numerical boundary. Source inspection finds existing exact field preparation reuse, but no new proven interchangeable preparation group. Zero runtime calls removed; fixture storage changes are not runtime consolidation.','',f'Outside measured direct-stage calls (Footprints/control/output assembly and wrapper overhead combined): mean pooled upper residual {result["outside_named_stages_upper_s"]:.6f}s. Full compose census additionally records the actual calls.','', 'All27 pages remain in each denominator, including zero-call pages. Profile clocks are attribution only. No new candidate exists, so B/C adoption clocks and redundant 208/22 processing are not required.']
    (O/'BOUNDARY_DECISION.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(result['largest'],indent=1));print('\n'.join(lines[5:14]))

if __name__=='__main__':analyze()
