"""Ordered N1TR driver: permanent attempt claims, pre-context probes, 70% stop."""
import argparse
import fcntl
import json
from pathlib import Path
import subprocess
import sys
HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(HERE.parents[2]/'scripts/numerics'),str(HERE)]
import n1tr as m
from ledger import weekly, record, append
from n1_launch import reading_command

def drive(art=m.ART,pack=m.PACK,dry_run=False,runner=subprocess.run,prober=subprocess.check_output):
    info=m.validate(art,pack)
    todo=[(c['context'],r) for r in ('r1','r2') for c in info['contexts']]
    if dry_run:
        for ctx,r in todo:print(json.dumps(dict(context=ctx+'/'+r,items=next(c['readers'][r] for c in info['contexts'] if c['context']==ctx),closure='ok',dry_run=True,model='gpt-6.1-sol',effort='medium',network=False)))
        return 0
    with (art/'driver.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        stop=art/'STOPPED_AT_70.json'
        if stop.exists():return 0
        answers=art/'answers';answers.mkdir(exist_ok=True)
        for ctx,r in todo:
            stem=ctx+'.'+r;base=answers/stem;rd=pack/ctx/r
            if list(answers.glob(stem+'.*')) or (rd/'answers.jsonl').exists():continue
            before=prober(reading_command(HERE/'limit_probe.sh',['before:N1TR/'+stem],art,answers),text=True).strip().splitlines()[-1]
            used=weekly(before)
            if used>=70:
                m.dump(stop,dict(threshold=70,weekly_used_percent=used,probe=before,next_context=ctx+'/'+r));return 0
            attempt=Path(str(base)+'.attempt.json')
            with attempt.open('x') as f:json.dump(dict(status='CLAIMED',probe=before),f)
            run=None
            try:
                result=runner(reading_command(HERE/'run_read.sh',['N1TR-'+stem,str(rd),str(m.ROOT/'docs/records/labelfix/secondary/prompts/sep2.md'),'medium'],art),text=True,capture_output=True)
                Path(str(base)+'.launcher.log').write_text(result.stdout+result.stderr)
                run=json.loads(result.stdout.strip().splitlines()[-1]);m.dump(Path(str(base)+'.run.json'),run)
                if result.returncode or run['rc'] or run['model']!='gpt-6.1-sol':raise ValueError('reader failed')
                m.dump(attempt,dict(status='DONE',run=run,probe=before))
            except (OSError,ValueError,KeyError) as e:
                m.dump(attempt,dict(status='FAILED',reason=str(e),probe=before))
            finally:
                after=prober(reading_command(HERE/'limit_probe.sh',['after:N1TR/'+stem],art,answers),text=True).strip().splitlines()[-1]
                if run:append(art/'usage_ledger.json',record(run,before,after,'n1tr/'+ctx,r,next(c['readers'][r] for c in info['contexts'] if c['context']==ctx)))
                if weekly(after)>=70:
                    m.dump(stop,dict(threshold=70,weekly_used_percent=weekly(after),probe=after,last_context=ctx+'/'+r));return 0
        return 0

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dry-run',action='store_true');a=p.parse_args();raise SystemExit(drive(dry_run=a.dry_run))
