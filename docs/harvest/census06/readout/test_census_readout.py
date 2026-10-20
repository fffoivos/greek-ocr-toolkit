"""Offline export readout tests. No pipeline imports, readers, census or Slurm."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time

import pytest

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'greekocr').is_dir() and (p / 'docs').is_dir())

def historical(path):
    if not path.exists():
        pytest.skip('historical fixture absent from this checkout: ' + str(path))
    return path
MOCK = ROOT / 'docs/harvest/seg_census/mock_batch'
ATTEMPTS = [MOCK / 'mode-i-removed'] + [MOCK / 'W/filter_pipeline_20261018/census_04_seg08' / n
                                      for n in ('mode-i', 'mode-ii', 'smoke-mode-i', 'smoke-mode-ii')]
spec = importlib.util.spec_from_file_location('census_readout', str(HERE / 'census_readout.py'))
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


def dump(path, obj):
    path.write_text(reader.canonical(obj) + '\n')


def row(i, split='train', crop=None, edition=None):
    return dict(parent_id='p', id=str(i), split=split, source='s', primary_class='prose', script_class='greek',
                crop_sha256=crop or ('crop-' + str(i)), edition_id=edition or ('edition-' + str(i)))


def decision(r, disposition='ADMIT', reasons=None, stages=None):
    return dict(binding={k:r[k] for k in ('parent_id','id','split','crop_sha256')}, disposition=disposition,
                pipeline_version='0.3', final_text='text', reasons=[dict(reason=x) for x in (reasons or [])], stages=stages or [],
                routes={t:dict(status='not_run_due_to_prior_exclusion') for t in reader.TOOLS},
                toolchain_versions={'segmentation':'0.8'})


def make_run(path, n=10, corrupt=True):
    path.mkdir(); gen = path / 'generations/g1-test'; gen.mkdir(parents=True)
    db = sqlite3.connect(str(path / 'ledger.sqlite'))
    db.executescript('CREATE TABLE run(key TEXT PRIMARY KEY,value TEXT); CREATE TABLE observations(parent TEXT,id TEXT,split TEXT,source TEXT,role TEXT,script TEXT,edition TEXT,payload TEXT, PRIMARY KEY(parent,id));')
    binding = dict(config=dict(parents=[dict(id='p', rows=n)], final_policy={'heldout_editions':['protected']}))
    encoded = reader.canonical(binding); bound_sha = hashlib.sha256(encoded.encode()).hexdigest()
    db.execute('INSERT INTO run VALUES (?,?)', ('binding', encoded))
    gate_reasons = ['mixed_script_word','unexpected_script','short_line','single_character_cell','numeric_shape','cell_status_unresolved']
    strata = {}; totals = {}; admitted = []
    with (gen/'decisions.jsonl').open('w') as stream:
        for i in range(n):
            r = row(i, edition='protected' if corrupt and i==6 else None)
            db.execute('INSERT INTO observations VALUES (?,?,?,?,?,?,?,?)', ('p',str(i),'train','s','prose','greek',r['edition_id'],reader.canonical(r)))
            if corrupt and i == n-1: continue  # missing canonical inventory identity
            if corrupt and i < 6:
                reason = gate_reasons[i]; disp = 'HOLD' if i in (1,5) else 'DROP'
                stages = [dict(stage='content_gate', excluded=reason)]
                d = decision(r, disp, [reason], stages)
                if i == 0:
                    d['stages'].append(dict(stage='segmentation',result=dict(verdict='DROP',reason='length band low')))
                    d['routes']['numerics']['status'] = 'failed'
            elif corrupt and i == 7:
                d = decision(r, 'DROP', ['duplicate_training_observation']); d['pre_dedup_disposition']='ADMIT'
            elif corrupt and i == 8:
                d = decision(r, 'HOLD', ['correction_unresolved','correction_unresolved'])
                d['routes']['polytonic'] = dict(status='proposal_only', edits=[dict(start=0,end=1,text='x')])
            else:
                d = decision(r)
                admitted.append(dict(r, final_text=d['final_text'], decision=d))
            count = 2 if corrupt and i==0 else 1
            for _ in range(count):
                stream.write(reader.canonical(d)+'\n')
                disp = d['disposition']; totals[disp]=totals.get(disp,0)+1
                k=('p','train','s','prose','greek',disp); strata[k]=strata.get(k,0)+1
    db.commit(); db.close()
    (gen/'admitted_train.jsonl').write_text(''.join(reader.canonical(r)+'\n' for r in admitted))
    if corrupt:
        with (gen/'admitted_train.jsonl').open('a') as stream: stream.write(reader.canonical(row(7))+'\n')
    (gen/'admission_records.jsonl').write_text('')
    (gen/'evaluation_diagnostics.jsonl').write_text('')
    for t in ('polytonic','cyrillic','numerics','content_repair'):
        (gen/('pending_'+t+'.jsonl')).write_text(reader.canonical(row(8))+'\n' if corrupt and t=='polytonic' else '')
    by_stratum = [dict(zip(('parent','split','source','role','script','disposition','rows'),k+(v,))) for k,v in strata.items()]
    if corrupt: by_stratum[0]['rows'] += 1
    summary = dict(input_rows=n, dispositions=totals, by_stratum=by_stratum, complete=True, run_binding_sha256=bound_sha)
    dump(gen/'summary.json',summary)
    dump(path/'CURRENT.json',dict(status='completed',export_id='g1-test',generation=1,run_binding_sha256=bound_sha, summary_sha256=reader.sha(gen/'summary.json')))
    return path


@pytest.mark.parametrize('run', ATTEMPTS, ids=lambda p:p.name)
def test_real_mock(run, tmp_path):
    historical(run / 'CURRENT.json')
    before = {str(p):reader.sha(p) for p in run.rglob('*') if p.is_file()}
    result = reader.readout(run,tmp_path/'out')
    gen = Path(result['generation']); summary=json.loads((gen/'summary.json').read_text())
    assert result['rows'] == summary['input_rows']
    assert {k:v for k,v in result['dispositions'].items() if v} == {k:v for k,v in summary['dispositions'].items() if v}
    assert result['summary_reason_counts'] == summary['overlapping_reason_counts']
    assert result['route_status_counts'] == summary['route_status_counts']
    assert result['segmentation_availability'] == summary['segmentation_availability']
    assert all(v['status']=='PASS' for v in result['invariants'].values())
    assert result['complete']
    assert before == {str(p):reader.sha(p) for p in run.rglob('*') if p.is_file()}
    assert sorted(p.name for p in (tmp_path/'out').iterdir()) == ['READOUT.md','readout.json']
    # Compare exact strata including role and script, not just grand totals.
    assert sorted(result['tables']['by_stratum'],key=reader.canonical) == sorted(summary['by_stratum'],key=reader.canonical)


def test_synthetic(tmp_path):
    run=make_run(tmp_path/'run'); result=reader.readout(run,tmp_path/'out',expect_rows=11)
    p=result['problems']; inv=result['invariants']
    for name in ('duplicates','missing_rows','heldout_leaks','gate_segmentation_violations','gate_route_violations','admitted_train_violations'):
        assert p[name]['count']==(2 if name in ('gate_segmentation_violations','gate_route_violations') else 1), name
        assert inv[name]['status']=='FAIL'
    assert inv['summary_by_stratum']==dict(status='FAIL',count=1)
    assert inv['expect_rows']==dict(status='FAIL',count=1)
    assert inv['dispositions_sum']['status']=='PASS'  # duplicates still carry a valid written disposition
    assert not result['complete']
    assert result['gate']['DROP']==5 and result['gate']['HOLD']==2
    for reason in ('mixed_script_word','unexpected_script','short_line','single_character_cell','numeric_shape','cell_status_unresolved'):
        assert result['gate'][reason] == (2 if reason=='mixed_script_word' else 1)
    assert result['tables']['dedup_changes'][0]['rows']==1
    assert result['tables']['correction_edits'][0]['status']=='proposal_only'
    assert result['pending']['polytonic']==1
    assert result['tables']['pending_reasons'][0]['reason']=='correction_unresolved'
    assert sum(r['rows'] for r in result['tables']['all_reasons'] if r['reason']=='correction_unresolved')==1
    assert result['tables']['segmentation_reasons'][0]['reason']=='length band low'
    # Supplied baseline uses exactly the exported summary schema.
    baseline=Path(result['generation'])/'summary.json'
    result=reader.readout(run,tmp_path/'with-baseline',baseline=baseline)
    assert sum(r['delta'] for r in result['tables']['baseline'])==-1


def test_publication_pinning(tmp_path):
    run=make_run(tmp_path/'run',corrupt=False)
    (run/'summary.json').write_text('INVALID ROOT ALIAS')
    (run/'decisions.jsonl').write_text('INVALID ROOT ALIAS')
    result=reader.readout(run,tmp_path/'out')
    assert result['rows']==10
    with pytest.raises(ValueError,match='outside'):
        reader.readout(run,run/'bad-output')
    current=json.loads((run/'CURRENT.json').read_text()); current['status']='in_progress';dump(run/'CURRENT.json',current)
    with pytest.raises(ValueError,match='completed'):
        reader.readout(run,tmp_path/'bad')


def test_old_syntax_and_mac_python(tmp_path):
    ast.parse((HERE/'census_readout.py').read_text(),feature_version=(3,6))
    run=make_run(tmp_path/'run',corrupt=False)
    proc=subprocess.run(['/usr/bin/python3','-B',str(HERE/'census_readout.py'),'--run',str(run),'--out',str(tmp_path/'out')],capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr
    (tmp_path/'mac_python_receipt.json').write_text(json.dumps(dict(version=subprocess.check_output(['/usr/bin/python3','--version'],text=True).strip(),syntax='ast feature_version=(3, 6) PASS',stdout=proc.stdout),indent=2)+'\n')


def test_spooled_job(tmp_path):
    spool=tmp_path/'spool';spool.mkdir();job=spool/'slurm_script';shutil.copyfile(HERE/'readout.sbatch',job)
    unrelated=tmp_path/'unrelated';unrelated.mkdir();bin_dir=tmp_path/'bin';bin_dir.mkdir()
    srun=bin_dir/'srun'
    srun.write_text('''#!/usr/bin/env python3
import os,sys,json
args=sys.argv[1:]
while args and args[0].startswith('-'):
    value=args.pop(0)
    if value=='-A': args.pop(0)
with open(os.environ['MOCK_SRUN_LOG'],'a') as f: f.write(json.dumps(dict(cwd=os.getcwd(),argv=args))+'\\n')
os.execvpe(args[0],args,os.environ)
''');srun.chmod(0o755)
    out=tmp_path/'out';log=tmp_path/'srun.jsonl'
    env=dict(os.environ,PATH=str(bin_dir)+os.pathsep+os.environ['PATH'],CENSUS06_RUN=str(make_run(tmp_path/'spool-run',n=200,corrupt=False)),CENSUS06_READOUT_OUT=str(out),CENSUS06_BUNDLE=str(HERE),CENSUS06_PYTHON=sys.executable,SLURM_JOB_PARTITION='normal',MOCK_SRUN_LOG=str(log))
    decision_path=Path(env['CENSUS06_RUN'])/'generations/g1-test/decisions.jsonl'
    ds=[json.loads(line) for line in decision_path.read_text().splitlines()]
    for d in ds: d['pipeline_version']='0.3.3'
    decision_path.write_text(''.join(reader.canonical(d)+'\n' for d in ds))
    exports=list(reader.records(decision_path.parent/'admitted_train.jsonl'))
    for r,d in zip(exports,ds): r['decision']=d
    (decision_path.parent/'admitted_train.jsonl').write_text(''.join(reader.canonical(r)+'\n' for r in exports))
    proc=subprocess.run(['bash',str(job)],cwd=str(unrelated),env=env,capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr
    calls=[json.loads(line) for line in log.read_text().splitlines()]
    assert len(calls)==1 and calls[0]['cwd']==str(unrelated)
    assert str(HERE/'census_readout.py') in calls[0]['argv']
    assert json.loads((out/'readout.json').read_text())['rows']==200
    (tmp_path/'spool_receipt.json').write_text(json.dumps(dict(stdout=proc.stdout,calls=calls,spooled=True,sbatch_invoked=False),indent=2)+'\n')


def test_streaming_600k(tmp_path):
    run=make_run(tmp_path/'run',n=600000,corrupt=False)
    code='''import importlib.util,json,resource,sys,time
spec=importlib.util.spec_from_file_location('r',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
t=time.time();r=m.readout(sys.argv[2],sys.argv[3],expect_rows=600000)
peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(json.dumps(dict(rows=r['rows'],seconds=time.time()-t,peak_mb=peak/(1024*1024 if sys.platform=='darwin' else 1024),invariants=r['invariants'])))
'''
    proc=subprocess.run([sys.executable,'-B','-c',code,str(HERE/'census_readout.py'),str(run),str(tmp_path/'out')],capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr
    metrics=json.loads(proc.stdout);assert metrics['rows']==600000
    assert metrics['peak_mb']<1024
    assert all(v['status']=='PASS' for v in metrics['invariants'].values())
    (tmp_path/'streaming_receipt.json').write_text(json.dumps(metrics,indent=2)+'\n')


def test_local_census03_evidence():
    evidence=ROOT/'docs/harvest/seg_census/remote_evidence'
    validation=json.loads(historical(evidence/'validation.json').read_text())
    assert validation['rows']==592466 and len(validation['parents'])==5
    assert sum(validation['parents'].values())==592466
    handoff=(ROOT/'docs/harvest/seg_census/HANDOFF_SEGCENSUS1.md').read_text()
    assert "65,900 admissions" in handoff
    # The older equivalent counts are explicitly conditional predictions. They
    # must not be fed to --baseline as an executed census_03 summary.
    prepared=(evidence/'HANDOFF.md').read_text()
    assert '65,900 predicted train candidates' in prepared
    assert '| HOLD | 145,131 |' in prepared and '| DROP | 3,405 |' in prepared


def test_crop_protection(tmp_path):
    run=make_run(tmp_path/'run',corrupt=False)
    gen=run/'generations/g1-test'
    db=sqlite3.connect(str(run/'ledger.sqlite'))
    r=row(1,split='dev',crop='crop-0')
    db.execute('UPDATE observations SET split=?,payload=? WHERE id=?',('dev',reader.canonical(r),'1'))
    db.commit();db.close()
    decisions=list(reader.records(gen/'decisions.jsonl'))
    decisions[1]['binding']['split']='dev';decisions[1]['binding']['crop_sha256']='crop-0'
    exports=[r for r in reader.records(gen/'admitted_train.jsonl') if r['id']!='1']
    (gen/'admitted_train.jsonl').write_text(''.join(reader.canonical(r)+'\n' for r in exports))
    (gen/'decisions.jsonl').write_text(''.join(reader.canonical(d)+'\n' for d in decisions))
    summary=json.loads((gen/'summary.json').read_text());summary['by_stratum'][0]['rows']=9
    summary['by_stratum'].append(dict(summary['by_stratum'][0],split='dev',rows=1));dump(gen/'summary.json',summary)
    current=json.loads((run/'CURRENT.json').read_text());current['summary_sha256']=reader.sha(gen/'summary.json');dump(run/'CURRENT.json',current)
    result=reader.readout(run,tmp_path/'out')
    assert result['problems']['heldout_leaks']['count']==1
    assert result['problems']['heldout_leaks']['first20'][0]['crop'] is True
    assert result['problems']['heldout_leaks']['first20'][0]['edition'] is False
    assert result['invariants']['summary_by_stratum']['status']=='PASS'
    assert result['invariants']['heldout_leaks']['status']=='FAIL'


@pytest.mark.parametrize('fault', ['no_reason','pipeline_version_mismatch','dispositions_sum'])
def test_written_faults(tmp_path,fault):
    run=make_run(tmp_path/'run',corrupt=False);gen=run/'generations/g1-test'
    decisions=list(reader.records(gen/'decisions.jsonl'))
    if fault=='no_reason': decisions[1]['disposition']='HOLD'
    if fault=='pipeline_version_mismatch': decisions[1]['pipeline_version']='DIFFERENT'
    if fault=='dispositions_sum': decisions[1]['disposition']='INFRA_ERROR'
    (gen/'decisions.jsonl').write_text(''.join(reader.canonical(d)+'\n' for d in decisions))
    result=reader.readout(run,tmp_path/'out')
    assert result['invariants'][fault]==dict(status='FAIL',count=1)
    if fault=='pipeline_version_mismatch':
        assert result['pipeline_versions']=={'0.3':9,'DIFFERENT':1}

@pytest.mark.parametrize('version,expected,passes', [('0.3.2',None,True),('0.3.2','0.3.2',True),('0.3.2','0.3',False),(None,None,False),('',None,False)])
def test_pipeline_version_argument(tmp_path,version,expected,passes):
    run=make_run(tmp_path/'version-run',corrupt=False)
    path=run/'generations/g1-test/decisions.jsonl'
    ds=[json.loads(s) for s in path.read_text().splitlines()]
    for d in ds:
        if version is None: d.pop('pipeline_version')
        else: d['pipeline_version']=version
    path.write_text(''.join(reader.canonical(d)+'\n' for d in ds))
    exports=list(reader.records(run/'generations/g1-test/admitted_train.jsonl'))
    for r,d in zip(exports,ds): r['decision']=d
    (run/'generations/g1-test/admitted_train.jsonl').write_text(''.join(reader.canonical(r)+'\n' for r in exports))
    result=reader.readout(run,tmp_path/'version-out',expect_pipeline_version=expected)
    assert (result['invariants']['pipeline_version_mismatch']['status']=='PASS') is passes
    assert result['expected_pipeline_version']==expected


def republish(run, held=(), empty=False):
    gen=run/'generations/g1-test'
    db=sqlite3.connect(str(run/'ledger.sqlite'))
    binding=json.loads(db.execute("SELECT value FROM run WHERE key='binding'").fetchone()[0])
    binding['config']['final_policy']['heldout_crop_sha256']=list(held)
    encoded=reader.canonical(binding)
    db.execute("UPDATE run SET value=? WHERE key='binding'", (encoded,));db.commit();db.close()
    if empty: (gen/'admitted_train.jsonl').write_text('')
    summary=json.loads((gen/'summary.json').read_text())
    summary['run_binding_sha256']=hashlib.sha256(encoded.encode()).hexdigest()
    summary['outputs']={p.stem:dict(sha256=reader.sha(p)) for p in gen.glob('*.jsonl')}
    dump(gen/'summary.json',summary)
    current=json.loads((run/'CURRENT.json').read_text())
    current.update(run_binding_sha256=summary['run_binding_sha256'],summary_sha256=reader.sha(gen/'summary.json'))
    dump(run/'CURRENT.json',current)


def cli(run, out, n):
    proc=subprocess.run([sys.executable,'-B',str(HERE/'census_readout.py'),
                         '--run',str(run),'--out',str(out),'--expect-rows',str(n)],capture_output=True,text=True)
    return proc,json.loads((out/'readout.json').read_text())


@pytest.mark.parametrize('configured', [True,False])
def test_astra_config_only_crop(tmp_path,configured):
    run=make_run(tmp_path/'run',n=1,corrupt=False)
    republish(run,held=['crop-0'] if configured else [])
    proc,result=cli(run,tmp_path/'out',1)
    assert result['problems']['heldout_leaks']['count']==int(configured)
    assert result['invariants']['heldout_leaks']['status']==('FAIL' if configured else 'PASS')
    assert proc.returncode==(1 if configured else 0)
    if configured:
        assert result['problems']['heldout_leaks']['first20'][0]['edition'] is False


def test_astra_missing_export(tmp_path):
    run=make_run(tmp_path/'run',n=3,corrupt=False);republish(run,empty=True)
    proc,result=cli(run,tmp_path/'out',3)
    assert result['invariants']['admitted_train_equals_eligible']==dict(status='FAIL',count=3)
    assert result['invariants']['admitted_train_violations']['status']=='PASS'
    assert proc.returncode==1


@pytest.mark.parametrize('fault',['duplicate','row_content'])
def test_export_equality(tmp_path,fault):
    run=make_run(tmp_path/'run',n=1,corrupt=False)
    path=run/'generations/g1-test/admitted_train.jsonl'
    if fault=='duplicate': path.write_text(path.read_text()*2)
    else:
        r=json.loads(path.read_text());r['final_text']='changed';dump(path,r)
    republish(run)
    proc,result=cli(run,tmp_path/'out',1)
    assert result['invariants']['admitted_train_equals_eligible']['status']=='FAIL'
    assert proc.returncode==1


@pytest.mark.parametrize('name',['smoke-mode-i','smoke-mode-ii','full-mode-ii'])
def test_census05_mock(tmp_path,name):
    fixture=historical(HERE.parent/'mocks'/name/'readout.json')
    recorded=json.loads(fixture.read_text())
    run=historical(HERE.parent/'mock_batch/W/census_05_20261020/attempts'/name)
    proc,result=cli(run,tmp_path/'out',200)
    assert proc.returncode==0,proc.stdout+proc.stderr
    assert all(v['status']=='PASS' for v in result['invariants'].values())


@pytest.mark.parametrize('reason', ['sf7 hold', 'sf7 out_of_scope', '  unknown SF7 reason α  '])
@pytest.mark.parametrize('split,disp,role', [('train','ADMIT','prose'), ('dev','HOLD','table'), ('test','DROP','caption')])
def test_kept_unverified_exact_reason_counts(tmp_path, reason, split, disp, role):
    run=make_run(tmp_path/'run', n=1, corrupt=False); gen=run/'generations/g1-test'
    db=sqlite3.connect(str(run/'ledger.sqlite'))
    r=json.loads(db.execute('SELECT payload FROM observations').fetchone()[0])
    r.update(split=split, primary_class=role, raw_text='text')
    db.execute('UPDATE observations SET split=?,role=?,payload=?', (split,role,reader.canonical(r)))
    db.commit();db.close()
    d=decision(r,disp,[] if disp=='ADMIT' else ['segmentation'])
    d['routes']['polytonic']=dict(status='kept_unverified',edits=[],evidence=dict(kept_unverified=True,reason=reason))
    dump(gen/'decisions.jsonl',d)
    (gen/'admitted_train.jsonl').write_text(reader.canonical(dict(r,final_text='text',decision=d))+'\n' if disp=='ADMIT' and split=='train' else '')
    summary=json.loads((gen/'summary.json').read_text())
    summary.update(dispositions={disp:1},by_stratum=[dict(parent='p',split=split,source='s',role=role,script='greek',disposition=disp,rows=1)])
    dump(gen/'summary.json',summary);republish(run)
    result=reader.readout(run,tmp_path/'out',expect_rows=1)
    assert all(v['status']=='PASS' for v in result['invariants'].values())
    assert result['tables']['kept_unverified_reasons']==[dict(reason=reason,parent='p',split=split,disposition=disp,**{'class':role},rows=1)]
    assert result['tables']['kept_unverified_reason_totals']==[dict(reason=reason,rows=1)]
    assert result['tables']['polytonic_route_status_counts_by_parent']==[dict(parent='p',status='kept_unverified',rows=1)]
    assert reason in (tmp_path/'out/READOUT.md').read_text()
