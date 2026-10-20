"""Explicit later RU2T reading launcher, with offline dry run."""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
from ru2t import ART, PACK, WORK, HERE, check_scanner, closure, sha, dump, require_external_pack_root, accepted_readers, reader_stem
from reading.ledger import weekly, record, append


def helper(script,args):
    body=script.read_text()
    token='D="$W/artifacts/ru1"' if script.name=='run_read.sh' else 'A="$W/artifacts/ru1/answers"'
    if body.count(token)!=1:raise ValueError('helper assignment changed')
    body=body.replace(token,token[:2]+shlex.quote(str(ART if script.name=='run_read.sh' else ART/'answers')))
    return ['bash','-c',body,str(script),*args]


def main():
    p=argparse.ArgumentParser();p.add_argument('root',choices=['ru2t','ru3t']);p.add_argument('ctx');p.add_argument('reader',choices=['r1','r2','r3']);p.add_argument('--dry-run',action='store_true');a=p.parse_args()
    if a.root=='ru3t':
        import ru3t as m
        globals().update({n:getattr(m,n) for n in ['ART','PACK','accepted_readers','closure']})
    if not re.fullmatch(r'ctx[0-9]{2}',a.ctx):raise ValueError('invalid context')
    require_external_pack_root(PACK)
    check_scanner();info=json.loads((ART/'build.json').read_text());rd=PACK/a.ctx/a.reader
    if a.ctx not in {c['context'] for c in info['contexts']}:raise ValueError('unassigned context')
    if a.reader not in accepted_readers(a.ctx):raise ValueError('VOID or unassigned reader')
    scans=closure(PACK,ART,runtime=True)
    if not all(s['ok'] for s in scans):raise ValueError('pack closure failed')
    for path,digest in {**info['inputs'],**info['pack_inputs']}.items():
        if sha(path)!=digest:raise ValueError('bound pack changed')
    stem=reader_stem(a.ctx,a.reader);answer=ART/'answers'/stem
    if a.dry_run:
        print(json.dumps(dict(root=a.root,pack=str(rd),run=str(answer)+'.run.json',closure='ok',model='gpt-6.1-sol',effort='medium',network=False)));return 0
    if [p for p in answer.parent.glob(answer.name+'.*') if a.root!='ru3t' or p.name not in {answer.name+'.attempt.json',answer.name+'.driver.log'}] or (rd/'answers.jsonl').exists():raise ValueError('refuse to overwrite reading attempt')
    answer.parent.mkdir(parents=True,exist_ok=True)
    script=HERE/'reading';prompt=WORK/'docs/records/labelfix/secondary/prompts/yer.md'
    def probe(phase):
        text=subprocess.check_output(helper(script/'limit_probe.sh',[phase+':'+a.root.upper()+'/'+stem]),text=True).strip().splitlines()[-1]
        weekly(text);return text
    before=probe('before')
    if weekly(before)>=(70 if a.root=='ru3t' else 78):raise ValueError('STOP weekly limit')
    run=None
    try:
        launched=subprocess.run(helper(script/'run_read.sh',[a.root.upper()+'-'+stem,str(rd),str(prompt),'medium']),text=True,capture_output=True)
        Path(str(answer)+'.launcher.log').write_text(launched.stdout+launched.stderr)
        run=json.loads(launched.stdout.strip().splitlines()[-1]);dump(Path(str(answer)+'.run.json'),run)
        if launched.returncode or run['rc'] or run['model']!='gpt-6.1-sol':raise ValueError('reader failed')
    finally:
        after=probe('after')
        if run is not None:
            n=sum(1 for _ in (rd/'items.jsonl').open())
            append(ART/'usage_ledger.json',record(run,before,after,a.root+'/'+a.ctx,a.reader,n))
    print(json.dumps(dict(context=a.ctx+'/'+a.reader,root=a.root,**(run or {'rc':1}))))
    return 0

if __name__=='__main__':raise SystemExit(main())
