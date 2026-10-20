"""CQ7 offline build and coordinator-only read/import entry points."""
import collections as C
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import uuid

HERE = Path(__file__).resolve().parent
CQ = HERE.parent
sys.path.insert(0, str(CQ/'tools'))
import build as b
import workflow as w
import closure
import scan_rollout

SCANNER = 'e44f8c8a3c6d478c3dc299863478fcab210298f1c1429870d516c546f0f54ad1'
ADDENDUM = '\n# CQ7 no-loop addendum (takes precedence over batching guidance above)\nview each image with one explicit call, never iterate over paths in code\n'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def load(p):
    return json.loads(Path(p).read_text())

def rows(p):
    return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]

def dump(p, value):
    b.dump(p, value)

def sid(x):
    return tuple(x['slot_id'])

def readable(a):
    return a is not None and 'unreadable' not in a.values()

def resolve(contexts, ledger):
    """Two NEW independent readable exact tuples required, regardless of old votes."""
    tags = [c['tag'] for c in contexts]
    assert len({r['tag'] for r in ledger}) == len(ledger)
    assert set(tags) == {r['tag'] for r in ledger}, 'CQ7 incomplete; no import'
    records = {r['tag']: r for r in ledger}
    votes = C.defaultdict(dict)
    for c in contexts:
        record = records[c['tag']]
        for item, x in load(c['key'])['items'].items():
            if not x['control']:
                votes[sid(x)][c['reader']] = record.get('answers', {}).get(item) if record['status']=='VALID' else None
    accepted = {}; rejected = []
    for slot, v in votes.items():
        assert set(v) == {'r1', 'r2'}
        a, z = v['r1'], v['r2']
        reason = ('missing/VOID CQ7 reader' if a is None or z is None else
                  'CQ7 unreadable' if not readable(a) or not readable(z) else
                  'CQ7 disagreement' if a != z else None)
        if reason:
            rejected.append(dict(slot_id=list(slot), reason=reason, votes=v))
        else:
            accepted[slot] = a
    return accepted, rejected

def build():
    assert not (HERE/'contexts.json').exists(), 'Refuse to overwrite built CQ7'
    assert sha(CQ/'tools/scan_rollout.py') == SCANNER and scan_rollout.VERSION == '4.5.5'
    selected = rows(CQ/'keys/topup_selected.jsonl')
    truth = rows(CQ/'truth/topup.jsonl')
    quarantine = rows(CQ/'quarantine/topup.jsonl')
    unresolved = {sid(x) for x in selected} - {sid(x) for x in truth}
    assert unresolved == {sid(x) for x in quarantine} and len(unresolved)==196
    initial = w.valid_answers('initial'); second = w.valid_answers('reread')
    data = [x for x in selected if sid(x) in unresolved]
    prior = [dict(slot_id=x['slot_id'], initial=initial.get(sid(x), (None,None))[1],
                  reread=second.get(sid(x), (None,None))[1],
                  reason=next(q['reason'] for q in quarantine if sid(q)==sid(x))) for x in data]
    positive = sum(readable(x['initial']) and x['initial']!={'breathing':'none','accent':'none'} for x in prior)
    pool = w.verified_control_pool()
    nonce = uuid.uuid4().hex
    pack = Path('/private/tmp')/('cq7_'+nonce)/'packs'
    rng = random.Random(20261019)
    rng.shuffle(data)
    contexts = []
    for batch, offset in enumerate(range(0,len(data),90)):
        cards = [x|dict(control=False) for x in data[offset:offset+90]] + rng.sample(pool,10)
        rng.shuffle(cards)
        for reader in ('r1','r2'):
            tag = f'cq7_{nonce[:12]}_b{batch:02d}_{reader}'
            rd = pack/f'b{batch:02d}'/reader
            (rd/'img').mkdir(parents=True)
            ordered = cards if reader=='r1' else cards[::-1]
            private = {}; public = []
            options = random.Random(f'{nonce}:{batch}:{reader}')
            for x in ordered:
                item = b.render(x,rd,options,tag)
                assert item['item_id'] not in private
                public.append(item);private[item['item_id']]=x|dict(public=item)
            b.jsonl(rd/'items.jsonl',public)
            for name in ('README.md','answer_schema.json'):
                shutil.copyfile(CQ/'templates'/name, rd/name)
            key = HERE/'keys'/f'{tag}.json'
            dump(key,dict(set='topup',phase='cq7',reader=reader,items=private))
            result=closure.scan(rd,private)
            assert result['ok'],result
            dump(HERE/'closure'/f'{tag}.json',result)
            contexts.append(dict(tag=tag,set='topup',phase='cq7',reader=reader,batch=batch,
                directory=str(rd),key=str(key),items=len(public),bed_items=len(ordered)-10,controls=10,
                manifest_sha256=sha(rd.parent/f'MANIFEST.{rd.name}.json'),scanner_sha256=SCANNER))
    # Verbatim frozen protocol body; precedence-only appended user instruction.
    shutil.copyfile(CQ/'prompts/cap1.md',HERE/'prompts/cap1.verbatim.md')
    (HERE/'prompts/cap1.md').write_text((HERE/'prompts/cap1.verbatim.md').read_text()+ADDENDUM)
    for name in ('truth/topup.jsonl','truth/wcap.jsonl','quarantine/topup.jsonl','aggregate_receipt.json'):
        target=HERE/'baseline'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(CQ/name,target)
    dump(HERE/'contexts.json',contexts)
    b.jsonl(HERE/'prior_reads.jsonl',prior)
    dump(HERE/'ledger.json',[])
    dump(HERE/'build_receipt.json',dict(status='BUILT_NOT_RUN',unresolved_slots=len(data),contexts=len(contexts),
         target_reads=2*len(data),controls_per_context=10,expected_positives=positive,
         expected_basis='171 readable marked initial single reads; 25 unreadable initial tuples unestimated; no guarantee of new agreement',
         prior_reasons=dict(C.Counter(x['reason'] for x in prior)),pack_root=str(pack),
         scanner_version='4.5.5',scanner_sha256=SCANNER,reader_runs=0,usage_probes=0,network_used=False,
         frozen_quota=dict(negative=800,positive=500,current_positive=416,shortfall=84),
         handover_sha256=sha(HERE/'HANDOVER.md')))

def verify():
    assert scan_rollout.VERSION=='4.5.5' and sha(CQ/'tools/scan_rollout.py')==SCANNER
    for path,digest in load(HERE/'freeze.json').items():
        assert sha(path)==digest, 'CQ7 custody changed: '+path
    contexts=load(HERE/'contexts.json')
    w.frozen_verified();w.controls_verified(contexts)
    for c in contexts:
        rd=Path(c['directory']);mp=rd.parent/f'MANIFEST.{rd.name}.json'
        assert sha(mp)==c['manifest_sha256']
        errors,skipped=scan_rollout.integrity(rd)
        assert not errors and not skipped,(c['tag'],errors)
    return contexts

def audit(c, record):
    rd=Path(c['directory']);meta=record['run']
    assert meta['rc']==0 and meta['model']=='gpt-6.1-sol'
    scan=scan_rollout.inspect(Path(meta['rollout']),rd)
    scan.update(scanner_sha256=SCANNER)
    dump(HERE/'scans'/f'{c["tag"]}.json',scan)
    assert scan['ok'] and not scan['manifest_check_skipped'],'reader/closure leak scan failed'
    answers,errors=w.decode(c)
    assert errors<=1,'more than one control error'
    return dict(answers=answers,control_errors=errors,answers_sha256=sha(rd/'answers.jsonl'),
                rollout_sha256=sha(meta['rollout']),scan_sha256=sha(HERE/'scans'/f'{c["tag"]}.json'))

def run():
    contexts=verify();path=HERE/'ledger.json';ledger=load(path)
    assert len({r['tag'] for r in ledger})==len(ledger)
    assert {r['tag'] for r in ledger}<={c['tag'] for c in contexts}
    for c in contexts:
        if c['tag'] in {r['tag'] for r in ledger}:continue
        verify()
        assert not (Path(c['directory'])/'answers.jsonl').exists(),'unexplained answers; stop'
        before=w.probe(c['tag']+'_before')
        assert before['weekly_used']<78,'weekly usage >=78%; refuse reader'
        record=dict(tag=c['tag'],set='topup',phase='cq7',reader=c['reader'],status='VOID',before=before,
                    scanner_version='4.5.5',scanner_sha256=SCANNER,prompt_sha256=sha(HERE/'prompts/cap1.md'))
        try:
            result=subprocess.run(['bash',str(CQ/'launchers/run_read.sh'),c['tag'],c['directory'],str(HERE/'prompts/cap1.md'),'medium'],text=True,capture_output=True)
            record.update(run_stdout=result.stdout,run_stderr=result.stderr)
            assert result.returncode==0,'reader launcher failed'
            record['run']=[json.loads(l) for l in result.stdout.splitlines() if l.startswith('{')][-1]
            record.update(audit(c,record),status='VALID')
        except Exception as exc:
            record.pop('answers',None);record.update(status='VOID',void_reason=str(exc))
        try:
            record['after']=w.probe(c['tag']+'_after')
        except Exception as exc:
            record.pop('answers',None);record.update(status='VOID',void_reason='post-probe failure: '+str(exc))
            ledger.append(record);dump(path,ledger);raise
        ledger.append(record);dump(path,ledger)
        if record['after']['weekly_used']>=78:raise RuntimeError('weekly usage >=78%; stop')

def imported_answers():
    """Called by CQ4 aggregate. No launch, and no reliance on unbound ledger answers."""
    if not (HERE/'import_receipt.json').exists():return {},[]
    verify()
    receipt=load(HERE/'import_receipt.json')
    assert receipt['ledger_sha256']==sha(HERE/'imported_ledger.json')
    for r in load(HERE/'imported_ledger.json'):
        if r['status']=='VALID':
            assert sha(r['run']['rollout'])==r['rollout_sha256']
            c=next(c for c in load(HERE/'contexts.json') if c['tag']==r['tag'])
            assert sha(Path(c['directory'])/'answers.jsonl')==r['answers_sha256']
            assert sha(HERE/'scans'/f'{r["tag"]}.json')==r['scan_sha256']
            a,e=w.decode(c);assert a==r['answers'] and e==r['control_errors']<=1
    accepted,rejected=resolve(load(HERE/'contexts.json'),load(HERE/'imported_ledger.json'))
    assert len(accepted)==receipt['accepted'] and len(rejected)==receipt['quarantined']
    return accepted,rejected

def import_reads():
    contexts=verify();ledger=load(HERE/'ledger.json')
    resolve(contexts,ledger) # completeness before any publication
    checked=[]
    for c in contexts:
        r=next(r for r in ledger if r['tag']==c['tag']).copy()
        if r['status']=='VALID':
            assert r['scanner_sha256']==SCANNER and r['prompt_sha256']==sha(HERE/'prompts/cap1.md')
            assert r['before']['weekly_used']<78 and 'after' in r
            r.update(audit(c,r))
        checked.append(r)
    accepted,rejected=resolve(contexts,checked)
    dump(HERE/'imported_ledger.json',checked)
    dump(HERE/'import_receipt.json',dict(scanner_version='4.5.5',scanner_sha256=SCANNER,
        ledger_sha256=sha(HERE/'imported_ledger.json'),accepted=len(accepted),quarantined=len(rejected),
        positives=sum(a!={'breathing':'none','accent':'none'} for a in accepted.values()),
        codex_before=checked[0]['before'],codex_after=checked[-1]['after'],
        reader_runs=0,network_used=False))
    subprocess.run(['bash',str(CQ/'AGGREGATE.sh')],check=True)
    print(json.dumps(load(HERE/'import_receipt.json'),indent=2))

if __name__=='__main__':
    {'build':build,'verify':verify,'run':run,'import':import_reads}[sys.argv[1]]()
