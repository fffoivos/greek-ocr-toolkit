"""Worker contracts use fake DNS, credentials, disk and processes; never live HTTP."""
from collections import Counter,namedtuple
import json,os,shutil,subprocess,sys
from pathlib import Path
import pytest
from collect_v3.common import rows,read_json,write_json,sha,scrub
from collect_v3.config import config,SPECS
from collect_v3.egress import HOSTS,check_url
from collect_v3.offline import no_network
from worker.preflight import check,MIN_FREE_BYTES
from worker.control import launch,alive
from worker.sync import transfer,retained

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'docs/harvest/collect_v3'
Usage=namedtuple('Usage','total used free')


def fake_config(tmp_path):
    return config(output_root=str(tmp_path/'run'),cache=str(tmp_path/'run/cache'),limiter_root=str(tmp_path/'limiter'))


def flight(c,**kw):
    return check(c,system='Linux',machine='x86_64',version=(3,11,3),
                 disk=lambda p:Usage(80_000_000_000,1_000_000_000,79_000_000_000),resolver=lambda *a,**k:[True],**kw)


def test_rebalanced_plan_and_book_list():
    allrows=rows(ART/'W1_manifest.jsonl')+rows(ART/'W2_manifest.jsonl')
    assert len(allrows)==6850
    for source,total,items in [('bsb_poly1850',1000,25),('ia_poly1850',1600,40)]:
        pool=[r for r in allrows if r['source']==source]
        assert len(pool)==total and len({r['item'] for r in pool})>=items
        assert max(Counter(r['item'] for r in pool).values())<=40
        assert sum(r['tranche']=='W1' for r in pool)==total//5
    assert sum(r['projected_micro_usd'] for r in allrows)==10_275_000
    assert len([line for line in (ART/'ia_poly1850_books.md').read_text().splitlines() if line.startswith('| ')])==1+len({r['item'] for r in allrows if r['source']=='ia_poly1850'})
    receipt=read_json(ART/'plan_receipt.json')
    assert receipt['schema']=='collect-v3-plan-rev2.2'
    assert receipt['W1_projected_usd']<=2.15 and receipt['W2_projected_usd']<=8.30
    assert config()['mdz_daily_image_cap']==500
    assert config(mdz_daily_image_cap=123)['mdz_daily_image_cap']==123


def test_preflight_dns_exact_allowlist_and_credentials_private(tmp_path,monkeypatch,capsys):
    token='FAKE-WORKER-CREDENTIAL';monkeypatch.setenv('COLLECT_V3_ACCESS_TOKEN',token)
    monkeypatch.delenv('GOOGLE_APPLICATION_CREDENTIALS',raising=False)
    calls=[];c=fake_config(tmp_path)
    with no_network():
        result=check(c,system='Linux',machine='x86_64',version=(3,11,3),
                     disk=lambda p:Usage(80_000_000_000,1,MIN_FREE_BYTES),
                     resolver=lambda host,*a,**kw:calls.append(host) or [True])
    assert calls==list(HOSTS) and result['http_requests']==0 and result['limiter_writable']
    assert token not in json.dumps(result)+capsys.readouterr().out
    assert scrub(token)=='[REDACTED]'


@pytest.mark.parametrize('mode',['missing','both','disk','python','os','dns','limiter'])
def test_preflight_fails_closed(tmp_path,monkeypatch,mode):
    c=fake_config(tmp_path);monkeypatch.setenv('COLLECT_V3_ACCESS_TOKEN','FAKE')
    monkeypatch.delenv('GOOGLE_APPLICATION_CREDENTIALS',raising=False)
    kwargs=dict(system='Linux',machine='x86_64',version=(3,11,3),disk=lambda p:Usage(80_000_000_000,1,MIN_FREE_BYTES),resolver=lambda *a,**k:[True])
    if mode=='missing':monkeypatch.delenv('COLLECT_V3_ACCESS_TOKEN')
    elif mode=='both':monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS','PRIVATE_PATH')
    elif mode=='disk':kwargs['disk']=lambda p:Usage(80_000_000_000,1,MIN_FREE_BYTES-1)
    elif mode=='python':kwargs['version']=(3,11,4)
    elif mode=='os':kwargs['system']='Darwin'
    elif mode=='dns':kwargs['resolver']=lambda *a,**k:[]
    elif mode=='limiter':Path(c['limiter_root']).write_text('not a directory')
    with no_network(),pytest.raises((ValueError,OSError)):check(c,**kwargs)


def test_adc_path_and_content_never_printed(tmp_path,monkeypatch):
    credential=tmp_path/'private-owner-adc.json';credential.write_text('{"type":"authorized_user","refresh_token":"FAKE-REFRESH"}');credential.chmod(0o600)
    monkeypatch.delenv('COLLECT_V3_ACCESS_TOKEN',raising=False);monkeypatch.setenv('GOOGLE_APPLICATION_CREDENTIALS',str(credential))
    result=flight(fake_config(tmp_path))
    assert str(credential) not in json.dumps(result) and scrub(str(credential))=='[REDACTED]'
    credential.write_text('FAKE-INVALID-SECRET')
    with pytest.raises(ValueError) as error:flight(fake_config(tmp_path))
    assert str(credential) not in str(error.value) and 'FAKE' not in str(error.value)


@pytest.mark.parametrize('url',['http://archive.org/a','https://archive.org.evil.invalid/a','https://evil.invalid/a','https://archive.org:444/a','https://user:pass@archive.org/a'])
def test_egress_fails_before_connect(url):
    with no_network(),pytest.raises(ValueError):check_url(url)
    assert check_url('https://oauth2.googleapis.com/token')=='oauth2.googleapis.com'


def test_portable_fixtures_no_projects_tree(monkeypatch):
    from collect_v3.portable import load
    fixture_root=Path(os.environ.get('COLLECT_V3_FIXTURE_ROOT',ROOT/'worker/fixtures')).resolve()
    with no_network():fs,overrides,expected=load(fixture_root)
    assert len(fs)==30 and len(expected)==3643 and overrides
    assert all(Path(f['page']['image']).is_relative_to(fixture_root) for f in fs)


def test_w1_only_launcher_and_pid_reuse_guard(tmp_path):
    c=fake_config(tmp_path)
    with no_network(),pytest.raises(ValueError,match='W1 only'):launch(c,'W2')
    out=Path(c['output_root']);out.mkdir(parents=True)
    (out/'collector.pid').write_text(str(os.getpid()))
    write_json(out/'collector_identity.json',dict(pid=os.getpid(),start_ticks='wrong'))
    assert alive(out) is None


def test_launch_idempotent_and_no_second_spawn(tmp_path,monkeypatch):
    import worker.control as control
    c=fake_config(tmp_path);out=Path(c['output_root']);out.mkdir(parents=True)
    monkeypatch.setattr(control,'alive',lambda p:12345)
    monkeypatch.setattr(control.subprocess,'Popen',lambda *a,**kw:pytest.fail('duplicate launch'))
    assert launch(c)==dict(status='already_running',pid=12345)


def test_sync_dry_run_execute_checksums_and_no_caches(tmp_path,monkeypatch):
    from worker.prepare import prepare
    c=fake_config(tmp_path);out=prepare(c['output_root']);dest=tmp_path/'destination'
    for name in ('responses/hash.json','cache/pages/hash.jpg','cache/g1b/cache.npz','cache/http/disposable.body','W1/c1/cards/cards.jsonl','W1/c1/cards/crops/a.png','W1/crops/disposable.png','W1/pages/p.json','W1/features.jsonl'):
        p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
    from collect_v3.ledger import Ledger
    db=Ledger(out/'ledger.sqlite3',{'W1':2.15,'W2':8.3});db.reserve('hash','p','W1');db.complete('hash')
    write_json(Path(c['limiter_root'])/'mdz-image-daily.json',dict(starts=[1800000000],cap=500))
    result=transfer(c,str(dest))
    assert result['dry_run'] and not dest.exists()
    result=transfer(c,str(dest),True)
    assert result['post_sync_checksum_match']
    assert (dest/'responses/hash.json').exists() and (dest/'cache/pages/hash.jpg').exists()
    assert read_json(dest/'shared_limiter/mdz-image-daily.json')['starts']==[1800000000]
    assert (dest/'ledger.sqlite3').exists() and (dest/'W1/c1/cards/crops/a.png').exists()
    assert not (dest/'cache/g1b').exists() and not (dest/'cache/http').exists() and not (dest/'W1/crops').exists()
    assert not (dest/'W1/features.jsonl').exists()
    for line in (dest/'retained_SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1);assert sha(dest/name)==digest
    (dest/'cache/pages/hash.jpg').write_text('changed same length')
    transfer(c,str(dest),True)
    assert (dest/'cache/pages/hash.jpg').read_text()=='{}'
    db.close()


def test_retained_exception_and_symlink_guard(tmp_path):
    c=fake_config(tmp_path);out=Path(c['output_root']);pdf=out/'cache/http/exception.body';pdf.parent.mkdir(parents=True);pdf.write_bytes(b'%PDF')
    write_json(out/'W1/pages/p.json',dict(analysis_page=dict(source_pdf_retained=True,source_pdf_cache=str(pdf))))
    assert pdf in retained(out)
    link=out/'responses/link';link.parent.mkdir();link.symlink_to(pdf)
    with pytest.raises(ValueError,match='symlink'):retained(out)


def test_worker_shell_syntax():
    for script in (ROOT/'worker').glob('*.sh'):
        subprocess.run(['bash','-n',str(script)],check=True,capture_output=True)


def test_launch_command_resume_and_no_credential_serialization(tmp_path,monkeypatch):
    import worker.control as control
    import worker.preflight as preflight
    import worker.prepare as preparation
    c=fake_config(tmp_path);secret='FAKE-LAUNCH-TOKEN';monkeypatch.setenv('COLLECT_V3_ACCESS_TOKEN',secret)
    monkeypatch.setattr(preflight,'check',lambda *a,**k:{'status':'ok'})
    monkeypatch.setattr(preparation,'prepare',lambda out:Path(out))
    states=iter([None,99999,99999]);monkeypatch.setattr(control,'alive',lambda out:next(states))
    monkeypatch.setattr(control,'process_id',lambda pid:'fake-start-ticks')
    commands=[]
    class Child:pid=99999
    monkeypatch.setattr(control.subprocess,'Popen',lambda cmd,**kw:commands.append((cmd,kw)) or Child())
    with no_network():
        assert control.launch(c)['status']=='started'
        assert control.launch(c)['status']=='already_running'
    assert len(commands)==1
    cmd,kw=commands[0];assert cmd[cmd.index('--tranche')+1]=='W1'
    assert 'collect_v3/detach.py' in cmd[1] and kw['stdin']==subprocess.DEVNULL and kw['start_new_session']
    assert secret not in repr(commands) and secret not in (Path(c['output_root'])/'runtime_config.json').read_text()


def test_sync_refuses_active_worker(tmp_path,monkeypatch):
    import worker.control as control
    c=fake_config(tmp_path);Path(c['output_root']).mkdir(parents=True)
    monkeypatch.setattr(control,'alive',lambda out:99999)
    with no_network(),pytest.raises(ValueError,match='stop the collector'):transfer(c,str(tmp_path/'destination'),True)


def test_wheelhouse_missing_inputs_fail_before_install(tmp_path):
    from worker.wheels import verify
    with no_network(),pytest.raises(ValueError,match='missing pinned target wheels'):verify(tmp_path)


def test_guarded_recovery_patch_contains_new_files_and_excludes_ignored(tmp_path):
    from collect_v3.commit_helper import recovery_patch
    root=tmp_path/'source';root.mkdir()
    def git(*args):return subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True,text=True)
    git('init','-q');(root/'.gitignore').write_text('ignored/\n');(root/'source.py').write_text('before\n')
    git('add','.gitignore','source.py');git('-c','user.name=Fixture','-c','user.email=fixture@invalid','commit','-qm','fixture')
    (root/'source.py').write_text('after\n');(root/'new.py').write_text('new\n')
    (root/'ignored').mkdir();(root/'ignored/secret.txt').write_text('DO-NOT-INCLUDE')
    patch=tmp_path/'recovery.patch'
    recovery_patch(['source.py','new.py','ignored/secret.txt'],patch,root=root,base='HEAD')
    assert 'DO-NOT-INCLUDE' not in patch.read_text() and 'new.py' in patch.read_text()
    git('apply','--reverse','--check',str(patch))
    assert not git('diff','--cached','--name-only').stdout


def test_finalize_rebuild_tolerates_textless_response(tmp_path,monkeypatch):
    import collect_v3.storage as storage
    response=tmp_path/'r.json';write_json(response,{'document':{'pages':[{}]}})
    monkeypatch.setattr(storage,'verify_page',lambda record:None)
    record=dict(analysis_page={'id':'p'},image=str(tmp_path/'i.png'),response=str(response),tranche='W1')
    assert storage.page_rows(record,tmp_path/'cache',tmp_path)==[]
    assert storage.textless({'document':{'text':'α','pages':[{'lines':[]}]}}) and not storage.textless({'document':{'text':'α','pages':[{'lines':[{}]}]}})


def test_pre_read_rejections_are_excluded_not_braked_and_skipped_on_resume(tmp_path):
    from collect_v3.offline import fixtures,prepare_mock
    from collect_v3.runner import run
    projects=Path(os.environ.get('COLLECT_V3_PROJECTS_ROOT',str(ROOT.parent)))
    fs,overrides,_=fixtures(projects);manifest,http,reader,routes=prepare_mock(tmp_path,fs)
    calls=[]
    def fetch(draw):
        calls.append(draw['id']);raise ValueError('blank page gate')
    routes.fetch=fetch
    c=config(output_root=str(tmp_path),cache=str(tmp_path/'cache'),storage_diet=False);sources=sorted({f['source'] for f in fs})
    with no_network():run(c,'W1',sources,http=http,reader=reader,routes=routes)
    assert len(calls)==len(manifest)>=10
    state=read_json(tmp_path/'W1/state.json');assert set(state['pages'].values())=={'excluded'} and state['status']=='completed_selected_sources'
    assert all(read_json(tmp_path/'W1/pages'/(d['id']+'.json'))['reason']=='blank page gate' for d in manifest)
    with no_network():run(c,'W1',sources,http=http,reader=reader,routes=routes)
    assert len(calls)==len(manifest)


def test_other_value_errors_still_feed_the_brake(tmp_path):
    from collect_v3.offline import fixtures,prepare_mock
    from collect_v3.runner import run
    from collect_v3.transport import NetworkFailure
    projects=Path(os.environ.get('COLLECT_V3_PROJECTS_ROOT',str(ROOT.parent)))
    fs,overrides,_=fixtures(projects);manifest,http,reader,routes=prepare_mock(tmp_path,fs)
    def fetch(draw):raise NetworkFailure('network failure after 3 retries: TimeoutError')
    routes.fetch=fetch
    c=config(output_root=str(tmp_path),cache=str(tmp_path/'cache'),storage_diet=False)
    with no_network(),pytest.raises(RuntimeError,match='failure brake'):run(c,'W1',sorted({f['source'] for f in fs}),http=http,reader=reader,routes=routes)


def test_owner_go_caps_w2_spend(tmp_path):
    from collect_v3.runner import tranche_caps
    c=config(output_root=str(tmp_path),cache=str(tmp_path/'cache'))
    assert tranche_caps(c,tmp_path,'W2')['W2']==c['caps_usd']['W2']
    write_json(tmp_path/'W2_owner_go.json',{'sources':['nlg'],'cap_usd':3.8})
    assert tranche_caps(c,tmp_path,'W2')['W2']==min(3.8,c['caps_usd']['W2'])
    assert tranche_caps(c,tmp_path,'W1')['W1']==c['caps_usd']['W1']


def test_w2_gate_may_only_be_extended(tmp_path):
    from collect_v3.runner import gate_extension_ok
    old_gate={'tranche':'W1','sources':{'nlg':{'passed':True,'classes':{'poly1850':True}}}}
    write_json(tmp_path/'c1_gate.json',old_gate);h=sha(tmp_path/'c1_gate.json')
    (tmp_path/'W2/gate_snapshots').mkdir(parents=True);write_json(tmp_path/'W2/gate_snapshots'/(h+'.json'),old_gate)
    old={'manifest_sha256':'m','gate_sha256':h}
    write_json(tmp_path/'c1_gate.json',dict(old_gate,sources=dict(old_gate['sources'],gazette_modern={'passed':True,'classes':{'modern_scanned':True}})))
    assert gate_extension_ok(tmp_path,old,{'manifest_sha256':'m','gate_sha256':sha(tmp_path/'c1_gate.json')})
    assert not gate_extension_ok(tmp_path,old,{'manifest_sha256':'other','gate_sha256':sha(tmp_path/'c1_gate.json')})
    write_json(tmp_path/'c1_gate.json',{'tranche':'W1','sources':{'nlg':{'passed':True,'classes':{'poly1850':False}}}})
    assert not gate_extension_ok(tmp_path,old,{'manifest_sha256':'m','gate_sha256':sha(tmp_path/'c1_gate.json')})
    assert not gate_extension_ok(tmp_path,{'manifest_sha256':'m','gate_sha256':'0'*64},{'manifest_sha256':'m','gate_sha256':'1'*64})


def test_owner_go_entries_sum_caps(tmp_path):
    from collect_v3.runner import tranche_caps,go_entries
    c=config(output_root=str(tmp_path),cache=str(tmp_path/'cache'))
    write_json(tmp_path/'W2_owner_go.json',{'entries':[{'sources':['nlg'],'cap_usd':3.8},{'sources':['gazette_modern'],'cap_usd':1.44}]})
    assert len(go_entries(tmp_path))==2 and abs(tranche_caps(c,tmp_path,'W2')['W2']-min(5.24,c['caps_usd']['W2']))<1e-9


def test_daily_limit_defers_one_source_and_others_continue(tmp_path):
    from collect_v3.offline import fixtures,prepare_mock
    from collect_v3.runner import run
    from collect_v3.transport import DailyLimit
    projects=Path(os.environ.get('COLLECT_V3_PROJECTS_ROOT',str(ROOT.parent)))
    fs,overrides,_=fixtures(projects);manifest,http,reader,routes=prepare_mock(tmp_path,fs)
    sources=sorted({f['source'] for f in fs});capped=sources[0];calls=[]
    def fetch(draw):
        calls.append(draw['source'])
        if draw['source']==capped:raise DailyLimit('MDZ Image API rolling 24h cap reached; resume later')
        raise ValueError('blank page gate')
    routes.fetch=fetch
    c=config(output_root=str(tmp_path),cache=str(tmp_path/'cache'),storage_diet=False)
    with no_network():run(c,'W1',sources,http=http,reader=reader,routes=routes)
    state=read_json(tmp_path/'W1/state.json')
    assert state['status']=='deferred_daily_limit' and capped in state['deferred_sources'] and calls.count(capped)==1
    assert all(state['pages'].get(d['id']) is None for d in manifest if d['source']==capped)
    assert all(state['pages'][d['id']]=='excluded' for d in manifest if d['source']!=capped)
    assert len(sources)>1
