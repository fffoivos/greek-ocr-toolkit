"""N1 launcher. Real reads require explicit operator invocation of run_n1.sh."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import shlex
import sys

HERE = Path(__file__).resolve().parent
WORK = HERE.parents[2]
sys.path.insert(0, str(WORK))
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(WORK/'scripts/numerics'))
from ledger import weekly, record, append
from n1_map_answers import map_answers, output_stem
from n1_calibration import score

BASE = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs')


def save(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n')


def reading_command(script, args, data, answers=None):
    # Existing reading helpers are read-only. Reuse their exact shell body,
    # redirecting only their hardcoded RU1 log root in memory. $0 stays the
    # original script path, so its sibling helper and workspace resolution hold.
    if script in (HERE/'run_read.sh', HERE/'limit_probe.sh'):
        body=script.read_text()
        token='D="$W/artifacts/ru1"' if script.name=='run_read.sh' else 'A="$W/artifacts/ru1/answers"'
        if body.count(token)!=1: raise ValueError('reading helper log assignment changed')
        target=data if script.name=='run_read.sh' else (answers or data/'answers')
        body=body.replace(token, token[:2]+shlex.quote(str(target)))
        return ['bash','-c',body,str(script),*args]
    return [str(script),*args]


def main():
    import re
    p=argparse.ArgumentParser(); p.add_argument('root', choices=['n1','n1cal','n1cal2','n1t','n1t2','n1t3','n1e']); p.add_argument('ctx'); p.add_argument('reader', nargs='?', default='r1')
    p.add_argument('--dry-run', action='store_true', help='validate pack/key/manifest locally; no probes or reads')
    a=p.parse_args()
    if not re.fullmatch('ctx[0-9]{2}' if a.root in ('n1','n1t','n1t2','n1t3','n1e') else 'cal[0-9]{2}', a.ctx) or a.reader not in ('r1','r2','r3'):
        p.error('root/context or reader mismatch')
    modern=a.root in ('n1cal2','n1t','n1t2','n1t3','n1e')
    calibration=a.root in ('n1cal','n1cal2')
    data=WORK/'artifacts/n1'; base=BASE
    if modern: data=data/a.root
    reader=HERE/'run_read.sh'; probe=HERE/'limit_probe.sh'
    # Test mode fails closed unless BOTH executable fixtures and isolated roots are explicit.
    if os.environ.get('N1_TEST_MODE')=='1':
        data=Path(os.environ['N1_TEST_DATA']); base=Path(os.environ['N1_TEST_PACKS'])
        reader=Path(os.environ['N1_TEST_READER']); probe=Path(os.environ['N1_TEST_PROBE'])
    rd=base/a.root/a.ctx/a.reader
    suffix='' if a.reader=='r1' else '.'+a.reader
    keypath=data/'keys'/(a.ctx+suffix+'.json')
    key=json.loads(keypath.read_text())
    if key.get('calibration') != calibration: raise ValueError('key mode mismatch')
    n=len((rd/'items.jsonl').read_text().splitlines())
    if key['readers'][a.reader] != [json.loads(l)['item_id'] for l in (rd/'items.jsonl').read_text().splitlines()]:
        raise ValueError('pack/key order mismatch')
    stem=output_stem(Path(os.environ['N1_TEST_DATA']) if os.environ.get('N1_TEST_MODE')=='1' else WORK/'artifacts/n1',a.root,a.ctx,a.reader)
    if a.dry_run:
        from n1_pack_closure import scan
        from greekocr.numerics.combine_v2 import MEANINGS
        result=scan(rd, data, completed=True, meanings=MEANINGS if modern else None)
        if not result['ok']: raise ValueError(result['violations'])
        print(json.dumps(dict(dry_run=True, context=a.ctx, reader=a.reader, items=n, root=a.root, output_stem=str(stem), closure=True)))
        return 0
    answers=stem.parent; answers.mkdir(parents=True, exist_ok=True)
    if list(answers.glob(stem.name+'.*')) or (rd/'answers.jsonl').exists():
        raise ValueError('refusing to overwrite an existing attempt')
    ledger=data/'usage_ledger.json'
    if ledger.exists() and any(e['bed']==a.root+'/'+a.ctx and e['reader']==a.reader for e in json.loads(ledger.read_text())):
        raise ValueError('attempt already in ledger')
    env=dict(os.environ)
    def limit(phase):
        out=subprocess.check_output(reading_command(probe,[phase+':'+a.root+'/'+a.ctx+'.'+a.reader],data,answers), text=True, env=env).strip().splitlines()[-1]
        weekly(out)  # fail closed on missing/ambiguous readings
        print(out, flush=True)
        return out
    before=limit('before')
    if weekly(before)>=78: raise ValueError('STOP: weekly usage >= 78%')
    prompt=WORK/'docs/records/labelfix/secondary/prompts'/('sep2.md' if modern else 'sep.md')
    (Path(str(stem)+'.prompt.md')).write_bytes(prompt.read_bytes())
    status=2; run=None; failure=None
    try:
        result=subprocess.run(reading_command(reader,['N1-'+a.root+'-'+a.ctx+'.'+a.reader,str(rd),str(prompt),'medium'],data), capture_output=True,text=True,env=env)
        Path(str(stem)+'.launcher.log').write_text(result.stdout+result.stderr)
        run=json.loads(result.stdout.strip().splitlines()[-1])
        save(Path(str(stem)+'.run.json'),run)
        scanpath=Path(str(stem)+'.scan.json')
        scanned=subprocess.run(['/usr/bin/arch','-x86_64','/Library/Frameworks/Python.framework/Versions/3.11/bin/python3','-B','-s',str(HERE/'scan_rollout.py'),run['rollout'],str(rd)],capture_output=True,text=True)
        scanpath.write_text(scanned.stdout)
        scan=json.loads(scanned.stdout)
        if result.returncode or run['rc'] or run['model']!='gpt-6.1-sol' or scanned.returncode or not scan['ok'] or scan['scanner_version'] not in (4, 'v4.4-canonical'):
            raise ValueError('reader or v4 leak scan failed')
        target=Path(str(stem)+'.jsonl'); target.write_bytes((rd/'answers.jsonl').read_bytes())
        mapped=map_answers(key,[json.loads(l) for l in target.read_text().splitlines() if l.strip()])
        if modern:
            from greekocr.numerics.combine_v2 import decode_and_gate
            gate, decoded=decode_and_gate(key,[json.loads(l) for l in target.read_text().splitlines() if l.strip()])
            mapped['context_status']=gate['status']
            mapped['control_errors']=gate['wrong']
            mapped['control_abstentions']=gate['abstentions']
            for slot in mapped['slots']: slot['context_status']=gate['status']
        save(Path(str(stem)+'.mapped.json'),mapped)
        if calibration:
            approved=[json.loads(l) for l in (data/'controls/approved.jsonl').read_text().splitlines() if l.strip()]
            assignments=[json.loads(l) for l in (WORK/'artifacts/n1/controls/dash_types.jsonl').read_text().splitlines() if l.strip()] if a.root=='n1cal2' and os.environ.get('N1_TEST_MODE')!='1' else None
            save(Path(str(stem)+'.calibration.json'), score(key,mapped,approved,assignments))
        valid=all(r['status'] in ('ok','unreadable') for r in mapped['slots']) and not mapped['unexpected_ids']
        status=0 if valid and mapped['context_status']=='VALID' else 2
    except Exception as exc:
        failure=str(exc)
    finally:
        after=limit('after')
        if weekly(after)>=78:
            failure='STOP: weekly usage >= 78% after run'; status=2
        if run is not None:
            entry=record(run,before,after,a.root+'/'+a.ctx,a.reader,n)
            entry['launcher_status']='FAILED' if failure or status else 'VALID'
            append(ledger,entry)
    if failure: print(failure,file=sys.stderr)
    return status


if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print(str(exc),file=sys.stderr); sys.exit(2)
