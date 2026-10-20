"""Fresh isolated RU4EF2 r5 packs and explicit driver; preparation never reads."""
import argparse
import json
from pathlib import Path
import random
import ru4ef1 as f
m=f.m

def closure(pack,art,runtime=False,replacement=False):
    if not (Path(pack)/'ctx01/r5').exists():return f.closure(pack,art,runtime,replacement)
    m.external(pack);ctx=Path(pack)/'ctx01'
    if {p.name for p in Path(pack).iterdir()}!={'ctx01'}:raise ValueError('r5 root closure')
    expected={'r5','MANIFEST.r5.json'} if runtime else {'r5'}
    if {p.name for p in ctx.iterdir()}!=expected:raise ValueError('r5 context closure')
    m.scan_packs.ROOT=art
    result=m.scan_packs.scan(ctx/'r5','yer',write_manifest=not runtime,allow_runtime=runtime)
    if not result['ok']:raise ValueError('r5 closure failed '+str(result['violations']))
    return [result]

def checked(task):
    for p,h in task['bindings'].items():
        if m.sha(p)!=h:raise ValueError('r5 binding changed '+p)
    closure(Path(task['pack']),Path(task['art']),runtime=True,replacement=True)

def build():
    report=json.loads((f.ART/'RU4EF2_COMBINE.json').read_text());tasks=[]
    used={i for p in (f.ART/'keys').glob('*.json') for i in json.loads(p.read_text())['items']}
    used.update(i for p in f.ART.glob('r*_replacements/*/keys/*.json') for i in json.loads(p.read_text())['items'])
    for repl in report['replacements']:
        if report['contexts'][repl['identity']]['status']=='VALID':continue
        ctx,role=repl['replaces'].split('/');ra=f.ART/'r5_replacements'/(ctx+'-'+role);rp=f.PACK.parent/'ru4e_r5'/(ctx+'-'+role)
        receipt=ra/'replacement.json'
        if receipt.exists():task=json.loads(receipt.read_text());checked(task);tasks.append(task);continue
        if ra.exists() or rp.exists():raise ValueError('partial r5 exists')
        public=m.rows(f.PACK/ctx/role/'items.jsonl');key=json.loads((f.ART/f'keys/{m.stem(ctx,role)}.json').read_text())
        seed='RU4EF2:20261018:'+ctx+':'+role+':r5';random.Random(seed).shuffle(public)
        order=[dict(key['items'][i['item_id']],masked_text=i['masked_text'],image=str(f.PACK/ctx/role/i['crop'])) for i in public]
        m.assignment(rp/'ctx01/r5',ra,'ctx01','r5',order,used);closure(rp,ra)
        task=dict(identity=ctx+'/'+role+'/r5',logical_reader=role,replaces=repl['replaces'],replaces_invalid=repl['identity'],art=str(ra),pack=str(rp),context='ctx01',reader='r5',seed=seed,status='READY_FOR_READING',no_reader_run=True,bindings=m.bindings([*rp.rglob('*'),*(ra/'keys').glob('*.json')]))
        m.dump(receipt,task);tasks.append(task)
    m.jsonl(f.ART/'r5_to_run.jsonl',tasks)
    m.dump(f.ART/'RU4EF2_R5_BUILD.json',dict(contexts=len(tasks),items=sum(len(m.rows(Path(t['pack'])/'ctx01/r5/items.jsonl')) for t in tasks),tasks=tasks,no_reader_run=True,threshold=70))
    print(json.dumps(dict(contexts=len(tasks),identities=[t['identity'] for t in tasks])))

def drive(dry_run):
    f.n.configure();plan=m.rows(f.ART/'r5_to_run.jsonl')
    for task in plan:checked(task)
    m.tasks=lambda *args:plan;m.closure=closure
    def runner(cmd,**kwargs):
        task=next(t for t in plan if str(Path(t['pack'])/'ctx01/r5')==cmd[3]);checked(task)
        return m.subprocess.run(cmd,**kwargs)
    # Canonical driver retains explicit attempts, before/after probes and 70% stop.
    print(json.dumps(m.drive(f.ART,f.PACK,dry_run=dry_run,runner=runner),indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','drive']);p.add_argument('--execute',action='store_true');a=p.parse_args()
    if a.action=='build':build()
    else:drive(not a.execute)
