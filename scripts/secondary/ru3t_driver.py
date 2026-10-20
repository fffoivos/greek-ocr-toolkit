"""Ordered, restart-safe RU3T driver. --dry-run is entirely offline."""
import argparse, fcntl, json, subprocess, sys
from pathlib import Path
import ru3t as m
from reading.ledger import weekly
import ru2t_launch as launcher


def plan(info):return [(c['context'],r) for r in ('r1','r2') for c in info['contexts']]

def done_contexts(art,pack,info):
    out=[]
    for ctx,r in plan(info):
        stem=m.reader_stem(ctx,r);ans=art/'answers'/stem
        if any(Path(str(ans)+s).exists() for s in ('.attempt.json','.run.json','.launcher.log')) or (pack/ctx/r/'answers.jsonl').exists():out.append(ctx+'/'+r)
    return out


def drive(art=m.ART,pack=m.PACK,dry_run=False,runner=subprocess.run,prober=subprocess.check_output):
    info=m.validate(art,pack);done=set(done_contexts(art,pack,info));todo=[(c,r) for c,r in plan(info) if c+'/'+r not in done]
    if dry_run:
        for ctx,r in todo:print(json.dumps(dict(root='ru3t',context=ctx,reader=r,pack=str(pack/ctx/r),dry_run=True,closure='ok',model='gpt-6.1-sol',effort='medium',network=False)))
        return 0
    art.mkdir(parents=True,exist_ok=True)
    with (art/'driver.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        stop=art/'STOPPED_AT_70.json'
        if stop.exists():print('STOPPED_AT_70 exists; no contexts launched');return 0
        answers=art/'answers';answers.mkdir(exist_ok=True)
        for ctx,r in todo:
            identity=ctx+'/'+r
            if identity in done_contexts(art,pack,info):continue
            m.validate(art,pack)
            # Existing helper, rebound to RU3T artifacts; no account probe in dry-run.
            launcher.ART=art
            probe=prober(launcher.helper(m.HERE/'reading/limit_probe.sh',['before:RU3T/'+identity]),text=True).strip().splitlines()[-1]
            used=weekly(probe)
            if used>=70:
                m.dump(stop,dict(weekly_used_percent=used,probe=probe,contexts_done=done_contexts(art,pack,info),next_context=identity,threshold=70));print('STOPPED_AT_70 '+identity);return 0
            stem=m.reader_stem(ctx,r);attempt=answers/(stem+'.attempt.json')
            # Permanent claim before launch: even a crash must never cause a repeat.
            with attempt.open('x') as f:json.dump(dict(context=identity,probe=probe,status='CLAIMED'),f)
            cmd=['/usr/bin/arch','-x86_64','/Library/Frameworks/Python.framework/Versions/3.11/bin/python3','-B',str(m.HERE/'ru2t_launch.py'),'ru3t',ctx,r]
            try:result=runner(cmd,text=True,capture_output=True)
            except OSError as exc:result=subprocess.CompletedProcess(cmd,127,'',str(exc))
            log=answers/(stem+'.driver.log');log.write_text(result.stdout+result.stderr)
            line=(result.stdout.strip().splitlines() or result.stderr.strip().splitlines() or ['no launcher output'])[-1]
            row=dict(context=identity,rc=result.returncode,result_line=line,log=str(log))
            with (art/'context_results.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
            m.dump(attempt,dict(row,status='DONE' if result.returncode==0 else 'FAILED',probe=probe))
            print(json.dumps(row),flush=True)
            if 'STOP weekly limit' in result.stdout+result.stderr:
                m.dump(stop,dict(contexts_done=done_contexts(art,pack,info),next_context=identity,threshold=70,reason='launcher second pre-context probe reached threshold',launcher_log=str(log)));return 0
        return 0

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');a=p.parse_args();raise SystemExit(drive(dry_run=a.dry_run))
