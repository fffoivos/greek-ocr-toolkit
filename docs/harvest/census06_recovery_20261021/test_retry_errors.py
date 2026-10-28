"""Exercise the external adapter against the actual committed census04/census."""
import importlib.util,json,os,pathlib,sqlite3,sys
import pytest
HERE=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path(os.environ['CENSUS_RETRY_TEST_CODE']).resolve()
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE))
from greekocr.harvest import line_pipeline_census04 as real
import retry_errors as driver
spec=importlib.util.spec_from_file_location('sealed_test_fixtures',ROOT/'tests/test_line_pipeline.py')
f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)

def fixture(tmp_path):
    rows=[dict(f.row('1234'),id=str(i),crop_sha256=f.digest(str(i)),primary_class='numerics_tables',script_class='nonletter') for i in range(4)]
    config=f.census_config(tmp_path,rows);out=tmp_path/'attempt'
    def observe(row):
        if row['id']=='3':raise TimeoutError('transient fixture')
        return f.segment(row,{'0':'KEEP','1':'DROP','2':'UNCERTAIN'}[row['id']])
    first=real.run(config,out,execute=True,segmenter_factory=lambda:observe)
    assert first['dispositions']['INFRA_ERROR']==1
    return config,out,driver.snapshot(out)

def test_real_census04_retry_only_errors_generation_and_publication(tmp_path):
    config,out,before=fixture(tmp_path)
    checked=driver.preflight(config,out,real,before['binding_sha256'])
    calls=[]
    def healthy(row):calls.append(row['id']);return f.segment(row)
    receipt=driver.retry(config,out,real,checked,segmenter_factory=lambda:healthy)
    assert receipt['status']=='PASS',receipt
    assert calls==['3'] # ADMIT, DROP and HOLD never re-evaluated.
    assert all(receipt['checks'].values())
    assert receipt['after_generation']==receipt['before_generation']+1
    current=json.loads((out/'CURRENT.json').read_text())
    assert current['status']=='completed' and current['generation']==receipt['after_generation']
    assert json.loads((out/'summary.json').read_text())['complete']

def test_read_only_preflight_does_not_change_attempt(tmp_path):
    config,out,before=fixture(tmp_path)
    paths={p:p.read_bytes() for p in out.rglob('*') if p.is_file() and p.suffix not in ['-shm','-wal']}
    driver.preflight(config,out,real,before['binding_sha256'])
    assert all(p.read_bytes()==raw for p,raw in paths.items())
    assert driver.snapshot(out)==before

def test_different_config_binding_and_unprocessed_are_rejected(tmp_path):
    config,out,before=fixture(tmp_path)
    with pytest.raises(ValueError,match='unexpected ledger binding'):driver.preflight(config,out,real,'0'*64)
    changed=dict(config,row_timeout_seconds=121)
    with pytest.raises(ValueError,match='configuration differs'):driver.preflight(changed,out,real,before['binding_sha256'])
    db=sqlite3.connect(out/'ledger.sqlite');db.execute("DELETE FROM decisions WHERE id='0'");db.commit();db.close()
    with pytest.raises(ValueError,match='UNPROCESSED'):driver.preflight(config,out,real,before['binding_sha256'])

def test_still_failing_retry_is_hold(tmp_path):
    config,out,before=fixture(tmp_path)
    def broken(row):raise TimeoutError('still failing')
    receipt=driver.retry(config,out,real,before,segmenter_factory=lambda:broken)
    assert receipt['status']=='HOLD' and not receipt['checks']['infra_error_zero']

def test_original_job_must_end(monkeypatch):
    monkeypatch.setattr(driver.subprocess,'check_output',lambda *a,**k:'3711087|RUNNING\n')
    with pytest.raises(ValueError,match='remains in queue'):driver.check_ended('3711087')

@pytest.mark.parametrize('queue',['','3712311|RUNNING\n'])
def test_original_expired_from_live_queue_requires_terminal_accounting(monkeypatch,queue):
    calls=[]
    def output(argv,**kwargs):
        calls.append(argv)
        if argv[0]=='squeue':
            assert '-j' not in argv # A finished ID may make squeue -j fail.
            return queue
        return '3711087|TIMEOUT|0:0\n'
    monkeypatch.setattr(driver.subprocess,'check_output',output)
    assert driver.check_ended('3711087')==['3711087','TIMEOUT','0:0']
    assert [argv[0] for argv in calls]==['squeue','sacct']

@pytest.mark.parametrize('accounting',['','3711087|RUNNING|0:0\n'])
def test_absent_from_queue_is_insufficient_without_terminal_accounting(monkeypatch,accounting):
    monkeypatch.setattr(driver.subprocess,'check_output',lambda argv,**kwargs:'' if argv[0]=='squeue' else accounting)
    with pytest.raises(ValueError,match='not confirmed terminal'):driver.check_ended('3711087')

def test_scheduler_query_failure_still_fails_closed(monkeypatch):
    def unavailable(argv,**kwargs):
        raise driver.subprocess.CalledProcessError(1,argv)
    monkeypatch.setattr(driver.subprocess,'check_output',unavailable)
    with pytest.raises(driver.subprocess.CalledProcessError):driver.check_ended('3711087')

def test_other_decision_mutation_is_detected(tmp_path):
    config,out,before=fixture(tmp_path)
    receipt=driver.retry(config,out,real,before,segmenter_factory=lambda:f.segment)
    assert receipt['status']=='PASS'
    db=sqlite3.connect(out/'ledger.sqlite');db.execute("UPDATE decisions SET payload=payload||' ' WHERE id='0'");db.commit();db.close()
    result=json.loads((out/'summary.json').read_text())
    receipt=driver.compare(out,before,result)
    assert receipt['status']=='HOLD' and not receipt['checks']['former_nonerrors_byte_unchanged']

def test_cli_explicit_and_default_test_only_never_execute(tmp_path):
    import subprocess
    config,out,before=fixture(tmp_path)
    path=tmp_path/'config.json';path.write_text(json.dumps(config))
    for flag in [[],['--test-only']]:
        command=[sys.executable,'-B',str(HERE/'retry_errors.py'),'--code-root',str(ROOT),'--config',str(path),'--attempt',str(out),'--original-job','NOT_A_REAL_JOB','--expect-binding-sha256',before['binding_sha256']]+flag
        r=subprocess.run(command,capture_output=True,text=True)
        assert r.returncode==0,r.stderr
        report=json.loads(r.stdout)
        assert report['status']=='TEST_ONLY_PASS' and report['processing_started'] is False
        assert report['execute_kwargs']==dict(execute=True,retry_errors=True,retry_holds=False)
        assert driver.snapshot(out)==before
