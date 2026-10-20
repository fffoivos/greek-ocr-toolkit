import sys,json,os
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'scripts/secondary'))
import ru4ef1 as f
m=f.m

def guard(event,args):
    if event.startswith('socket.') or event == 'os.system':raise RuntimeError('offline collect: process/network disabled')
    if event=='subprocess.Popen':
        argv=args[1]
        if not (isinstance(argv,(list,tuple)) and len(argv)==4 and argv[1]=='-B' and Path(argv[2]).resolve()==f.n.BOUND/'replay_literal.py'):
            raise RuntimeError('only bound local scanner reproduction may launch')
    if event=='open':
        p,mode,flags=args
        if ((isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC))) and isinstance(p,(str,bytes,os.PathLike)):
            if '.git' in Path(os.fsdecode(p)).resolve().parts or 'ru1_v3_test_edits' in str(p):raise RuntimeError('forbidden write')
sys.addaudithook(guard)
f.n.configure();info=m.validate(f.ART,f.PACK);repls=m.rows(f.ART/'r3_to_run.jsonl');seen=set();votes=f.defaultdict(list)
report=dict(contexts={},coverage={},evidence={},replacements=repls)
byrole={r['replaces']:r for r in repls}
for c in info['contexts']:
 for role in ('r1','r2'):
    identity=c['context']+'/'+role
    _,obj=f.precollect((str(f.ART),str(f.PACK),c['context'],role))
    run=json.loads((f.ART/'answers'/(m.stem(c['context'],role)+'.run.json')).read_text());digest=m.sha(run['rollout'])
    if digest in seen:raise ValueError('reused rollout')
    seen.add(digest)
    if obj.get('error'):report['contexts'][identity]=dict(status='FAILED',reason=obj['error']);continue
    mapped,gate,cov,ev=obj['result'];report['contexts'][identity]=dict(status=gate['status'],gate=gate);report['coverage'][identity]=cov;report['evidence'].update(ev)
    if gate['status']!='VALID':continue
    for p in mapped:
      if not p['control'] and p['google']=='ь' and p['kind']=='final':votes[p['row_id'],p['offset']].append(dict(logical_reader=role,context=identity,call=p['call'],gate_status='VALID',confidence=p['confidence'],item_id=p['item_id'],evidence=ev))
for r in repls:
 for p,h in r['bindings'].items():
    if m.sha(p)!=h:raise ValueError('replacement binding changed '+p)
 f.closure(Path(r['pack']),Path(r['art']),runtime=True,replacement=True)
 identity=r['identity']
 try:
    mapped,gate,cov,ev=f.ORIGINAL_COLLECT(Path(r['art']),Path(r['pack']),r['context'],r['reader'],seen)
    report['contexts'][identity]=dict(status=gate['status'],gate=gate);report['coverage'][identity]=cov;report['evidence'].update(ev)
    if gate['status']=='VALID':
      for p in mapped:
       if not p['control'] and p['google']=='ь' and p['kind']=='final':votes[p['row_id'],p['offset']].append(dict(logical_reader=r['logical_reader'],context=identity,call=p['call'],gate_status='VALID',confidence=p['confidence'],item_id=p['item_id'],evidence=ev))
 except (OSError,ValueError,KeyError,TypeError) as e:report['contexts'][identity]=dict(status='FAILED',reason=str(e))
 print(identity,report['contexts'][identity]['status'],flush=True)
# A later explicit r5 reading replaces only its failed logical role.
report['r5_replacements']=[]
if (f.ART/'r5_to_run.jsonl').exists():
 from ru4ef2_r5 import checked
 for r in m.rows(f.ART/'r5_to_run.jsonl'):
    checked(r);report['r5_replacements'].append(r)
    a,p=Path(r['art']),Path(r['pack']);identity=r['identity']
    if not (a/'answers/ctx01.r5.run.json').exists():continue
    if report['contexts'][r['replaces_invalid']]['status']=='VALID':raise ValueError('r5 would overwrite valid replacement')
    try:
      mapped,gate,cov,ev=f.ORIGINAL_COLLECT(a,p,'ctx01','r5',seen)
      report['contexts'][identity]=dict(status=gate['status'],gate=gate);report['coverage'][identity]=cov;report['evidence'].update(ev)
      if gate['status']=='VALID':
       for point in mapped:
        if not point['control'] and point['google']=='ь' and point['kind']=='final':votes[point['row_id'],point['offset']].append(dict(logical_reader=r['logical_reader'],context=identity,call=point['call'],gate_status='VALID',confidence=point['confidence'],item_id=point['item_id'],evidence=ev))
    except (OSError,ValueError,KeyError,TypeError) as e:report['contexts'][identity]=dict(status='FAILED',reason=str(e))

ds=[m.combine(p,votes[p['row_id'],p['offset']]) for p in m.rows(f.ART/'candidate_positions.full.jsonl')]
assert all(len({v['logical_reader'] for v in d['reads']})==len(d['reads']) for d in ds)
m.jsonl(f.ART/'decisions.jsonl',ds)
report.update(counts=dict(f.Counter(d['decision'] for d in ds)),lead_review_reasons=dict(f.Counter(d['reason'] for d in ds if d['decision']=='hold')),decisions_sha256=m.sha(f.ART/'decisions.jsonl'),status='PENDING_READS' if any(len(d['reads'])!=2 for d in ds) else 'AWAITING_LEAD')
m.dump(f.ART/'RU4EF2_COMBINE.json',report)
print(json.dumps({k:report[k] for k in ('counts','lead_review_reasons','status')}))
