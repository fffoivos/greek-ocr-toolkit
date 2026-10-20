"""run_bed pipeline adapted for Q3; only the lead invokes this driver."""
import json,re,shutil,subprocess,sys,time
from ss4_common import *
PYTHON=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python')
PILLOW=['/usr/bin/arch','-x86_64','/Library/Frameworks/Python.framework/Versions/3.11/bin/python3','-B']
def weekly(probe):
    if 'limit_id=codex ' not in probe: raise ValueError('missing codex probe')
    values=re.findall(r'(?:primary|secondary)=([0-9.]+)%/10080m',probe)
    if len(values)!=1: raise ValueError('missing/ambiguous 10080-minute weekly window')
    return float(values[0])
def probe(tag):
    p=subprocess.run(['bash',str(SS/'launchers/limit_probe.sh'),tag],capture_output=True,text=True)
    lines=p.stdout.strip().splitlines()
    return lines[-1] if p.returncode==0 and lines else ''
def main(ctx,layout="type2"):
    check_scanner(); c,_=assignment(ctx,layout); rd=PACK_ROOT/layout/ctx/'r1'
    # Refuse reruns over answers or an altered original pack.
    from scan_type_packs import scan
    if not scan(ctx,False,layout=layout)['ok']: raise ValueError('pack closure failed (rerun requires a fresh pack)')
    (SS/'q3/prompts_rendered').mkdir(exist_ok=True); (SS/'q3/answers').mkdir(exist_ok=True)
    prompt=SS/'q3/prompts_rendered'/f'{ctx}.md'; shutil.copyfile(SS/'prompts/type.md',prompt)
    before=probe('before:'+layout+'/'+ctx); print(before,flush=True)
    try: used=weekly(before)
    except ValueError as e: print(e); return 8
    if used>=78: print('STOP: weekly used >=78%'); return 8
    label='SS4-'+layout+'-'+ctx+'-r1'; start=time.monotonic(); run={}; rc=1; scan_rc=2; map_rc=None
    try:
        p=subprocess.run(['bash',str(SS/'launchers/run_read.sh'),label,str(rd),str(prompt),'medium'],capture_output=True,text=True)
        print(p.stdout,flush=True)
        run=json.loads(p.stdout.strip().splitlines()[-1]); rc=run.get('rc',1)
        if run.get('model')!='gpt-6.1-sol': raise ValueError('rollout model assertion failed')
        roll=Path(run.get('rollout',''))
        if not roll.is_file(): raise ValueError('missing rollout')
        check_scanner() # fail closed immediately before canonical in-place invocation
        output=SS/'q3/answers'/f'{ctx}.scan.json'
        with output.open('w') as f:
            sc=subprocess.run(PILLOW+[str(SCANNER),str(roll),str(rd)],stdout=f,stderr=subprocess.PIPE,text=True)
        scan_rc=sc.returncode
        if sc.stderr: print(sc.stderr,file=sys.stderr)
        if (rd/'answers.jsonl').is_file(): shutil.copyfile(rd/'answers.jsonl',SS/'q3/answers'/f'{ctx}.jsonl')
        if scan_rc==0 and rc==0:
            mapped=subprocess.run([str(PYTHON),'-B',str(SS/'tools/map_type.py'),ctx,'--layout',layout]); map_rc=mapped.returncode
    except Exception as e:
        print(str(e),file=sys.stderr)
    finally:
        after=probe('after:'+layout+'/'+ctx); print(after,flush=True)
        entry=dict(label=label,ctx=ctx,layout=layout,rc=rc,wall_s=round(time.monotonic()-start,3),model=run.get('model'),usage=run.get('usage'),probes={'before':before,'after':after},items=len(c['card_ids']),rollout=run.get('rollout'),scan_rc=scan_rc,map_rc=map_rc,void=scan_rc!=0)
        with (SS/'q3/usage_ledger.jsonl').open('a') as f: f.write(json.dumps(entry)+'\n')
    if scan_rc!=0: return 2
    return rc or (map_rc if map_rc is not None else 1)
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(); parser.add_argument('ctx'); parser.add_argument('--layout',choices=['type','type2'],default='type2'); args=parser.parse_args()
    try: sys.exit(main(args.ctx,args.layout))
    except Exception as e: print(str(e),file=sys.stderr); sys.exit(1)
