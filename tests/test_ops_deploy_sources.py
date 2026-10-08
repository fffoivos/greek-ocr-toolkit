import io
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
import pytest
from greekocr.ops import file_sha256, verify_files, write_receipt, require_env, Observation, watch, bounded_ssh, rate_limited_client
from greekocr.deploy import plugin_options
from greekocr.deploy.node_envs import environment_recipes, environment_plan, write_environment_script, KRAKEN_WHEEL_SHA256
from greekocr.deploy.pods import PodClient, pod_client, select_offer, create_pod, ensure_pod, terminate_pod, pod_status
from greekocr.real.sources import parse_source, discovery_command, run_discovery, http_client, refetch_pdf_cache, stage_parliament


def test_receipts_bind_files_and_atomic_publish(tmp_path):
    file=tmp_path/'input';file.write_bytes(b'recorded fixture');binding={str(file):file_sha256(file)}
    verify_files(binding);out=tmp_path/'nested/receipt.json';write_receipt(out,dict(inputs=binding))
    assert json.loads(out.read_text())['inputs']==binding and not out.with_name('receipt.json.tmp').exists()
    file.write_bytes(b'changed')
    with pytest.raises(ValueError,match='changed'):verify_files(binding)


def test_secrets_missing_and_values_never_in_error():
    assert require_env(['TOKEN'],env={'TOKEN':'fixture-secret'})=={'TOKEN':'fixture-secret'}
    with pytest.raises(ValueError,match='TOKEN') as exc:require_env(['TOKEN'],env={})
    assert 'fixture-secret' not in str(exc.value)
    with pytest.raises(ValueError):require_env(['TOKEN'],env={'TOKEN':''})

@pytest.mark.parametrize('terminal',['DONE','FAILED','STALL','TIMEOUT','LOST'])
def test_every_watch_terminal_emits_line(terminal):
    now=[0.0];lines=[]
    def sleep(t):now[0]+=t
    def probe():
        if terminal=='LOST':raise OSError('recorded SSH failure')
        return Observation(alive=True,log_bytes=int(now[0]) if terminal=='TIMEOUT' else 0,
                           done=terminal=='DONE',failed=terminal=='FAILED')
    result=watch('fixture',probe,max_seconds=3,stall_seconds=1,poll_seconds=.5,lost_after=2,
                 emit=lines.append,clock=lambda:now[0],sleep=sleep)
    assert result.state==terminal and lines[0]=='START fixture' and lines[-1].startswith(terminal)


def test_dead_process_never_succeeds_and_bounds_required():
    lines=[];assert watch('dead',lambda:Observation(False,0),emit=lines.append).state=='FAILED'
    for kw in ({'max_seconds':0},{'stall_seconds':float('inf')},{'poll_seconds':0},{'lost_after':0}):
        with pytest.raises(ValueError):watch('bad',lambda:Observation(True,0),**kw)


def test_bounded_ssh_no_shell_interpolation(monkeypatch):
    calls=[]
    monkeypatch.setattr(subprocess,'run',lambda cmd,**kwargs:calls.append((cmd,kwargs)) or subprocess.CompletedProcess(cmd,0,'ok',''))
    assert bounded_ssh('worker',['printf','literal $(not executed)'],timeout=9).stdout=='ok'
    command,kwargs=calls[0]
    assert 'ConnectTimeout=15' in command and 'ServerAliveCountMax=3' in command
    assert command[-1]=="printf 'literal $(not executed)'" and kwargs['timeout']==9 and not kwargs.get('shell')
    with pytest.raises(ValueError):bounded_ssh('-oBad',[])


def test_node_environment_pins_and_plans(tmp_path):
    recipes=environment_recipes();assert set(recipes)=={'ocr','cllg-gpu','e2ws','kraken'}
    assert all(r.python=='3.11' for r in recipes.values())
    for name in ('cllg-gpu','kraken'):
        with pytest.raises(ValueError,match='wheelhouse'):environment_plan(name,tmp_path/name)
        plan=environment_plan(name,tmp_path/name,wheelhouse=tmp_path/'wheels')
        assert KRAKEN_WHEEL_SHA256 in plan[2] and 'hashlib' in plan[2][2]
        assert any('safetensors==0.7.0' in cmd for cmd in plan)
    with pytest.raises(ValueError,match='requirements'):environment_plan('e2ws',tmp_path/'e2ws')
    plan=environment_plan('e2ws',tmp_path/'e2ws',paddle_requirements=tmp_path/'requirements.txt')
    assert any('paddlepaddle==3.1.0' in cmd for cmd in plan)
    script=write_environment_script('ocr',tmp_path/'path with spaces',tmp_path/'env.sh')
    text=script.read_text();assert 'cu126' in text and 'Linux' in text and 'pip check' in text and 'INSTALLED.txt' in text


def offer(gpu='A100_80GB',provider='massedcompute',price=2):
    return dict(gpuType=gpu,provider=provider,cloudId='cloud',stockStatus='available',prices={'onDemand':price},images=['cpu','cuda-fixture'])


def test_pod_offer_priority_not_global_cheapest():
    a=offer(price=3);b=offer(price=2);cheap=offer('A6000_48GB',price=.1)
    assert select_offer([a,cheap,b]) is b
    assert select_offer([dict(a,stockStatus='unavailable'),cheap]) is cheap
    with pytest.raises(ValueError):select_offer([])


def test_create_and_terminate_with_mock_transport():
    calls=[]
    def request(method,path,body):
        calls.append((method,path,body))
        if 'availability' in path:return {'data':[offer()]}
        if 'ssh_keys' in path:return {'data':[dict(id='key-id',publicKey='ssh-fixture')]}
        if method=='POST':return dict(id='pod-1',status='PROVISIONING')
        if method=='DELETE':return dict(status='DELETING')
        return dict(id='pod-1',status='ACTIVE')
    client=PodClient(request)
    result=create_pod(client,name='reviewable-fixture',public_key='ssh-fixture')
    assert result['pod_id']=='pod-1'
    payload=next(body for method,path,body in calls if method=='POST')
    assert payload['pod']['gpuCount']==1 and payload['pod']['sshKeyId']=='key-id' and payload['pod']['image']=='cuda-fixture'
    assert not payload['pod']['autoRestart'] and payload['provider']['type']=='massedcompute'
    assert pod_status(client,'pod-1')['status']=='ACTIVE'
    assert terminate_pod(client,'pod-1')['status']=='DELETING'
    assert calls[-1][0]=='DELETE' and calls[-1][1].endswith('pod-1')

@pytest.mark.parametrize('outcome',['ACTIVE','ERROR','TIMEOUT','LOST'])
def test_pod_reuse_receipts_and_liveness(tmp_path,outcome):
    path=tmp_path/'state.json';write_receipt(path,dict(pod_id='existing',offer=offer()))
    calls=[];now=[0.0];lines=[]
    def request(method,url,body):
        calls.append((method,url));assert method=='GET' and 'existing' in url
        if len(calls)==1:return dict(id='existing',status='ACTIVE')
        if outcome=='LOST':raise OSError('recorded failure')
        return dict(id='existing',status='PROVISIONING' if outcome=='TIMEOUT' else outcome,ip='fixture-ip' if outcome=='ACTIVE' else None)
    def sleep(t):now[0]+=t
    kwargs=dict(timeout=1,poll_seconds=.5,clock=lambda:now[0],sleep=sleep,emit=lines.append)
    if outcome=='ACTIVE':assert ensure_pod(PodClient(request),path,**kwargs)['pod']['status']=='ACTIVE'
    else:
        with pytest.raises({'ERROR':RuntimeError,'TIMEOUT':TimeoutError,'LOST':OSError}[outcome]):ensure_pod(PodClient(request),path,**kwargs)
    terminal={'ACTIVE':'DONE','ERROR':'FAILED','TIMEOUT':'TIMEOUT','LOST':'LOST'}[outcome]
    assert lines[-1].startswith(terminal)
    assert 'fixture-secret' not in path.read_text()


def test_pod_client_env_secret_is_only_in_transport_headers(monkeypatch):
    calls=[]
    class Response(io.BytesIO):pass
    def urlopen(req,timeout):calls.append((req,timeout));return Response(b'{"status":"ACTIVE"}')
    monkeypatch.setattr(__import__('urllib.request',fromlist=['urlopen']),'urlopen',urlopen)
    client=pod_client(env={'PRIME_INTELLECT_CONTROL_KEY':'fixture-secret'},timeout=7)
    assert 'fixture-secret' not in repr(client)
    assert pod_status(client,'pod')['status']=='ACTIVE'
    assert calls[0][0].get_header('Authorization')=='Bearer fixture-secret' and calls[0][1]==7
    with pytest.raises(ValueError,match='PRIME_INTELLECT'):pod_client(env={})


def test_docling_options_public_factory(tmp_path):
    options=plugin_options('checkpoint','codec',replace_policy='all')
    assert options.kind=='glossapi' and options.device=='cpu'
    with pytest.raises(ValueError,match='routing_sidecar'):plugin_options('checkpoint','codec')


def test_source_parsers_recorded_fixtures():
    root=Path(__file__).parent/'fixtures/o4c'
    parliament=parse_source('parliament',json.loads((root/'parliament_item.json').read_text()))
    assert parliament['year']==1850 and parliament['pages']==9 and parliament['rights']['compatible']
    archive=parse_source('archive',json.loads((root/'archive_greek_metadata.json').read_text()),identifier='b28038630')
    assert archive['pages']==1806 and archive['text_layer']['status']=='declared'
    media=parse_source('wikimedia',{'title':'File:Unverified.djvu'})
    assert not media['rights']['compatible']
    with pytest.raises(ValueError):parse_source('anemi',{})


def test_discovery_command_bound_root_and_timeout(monkeypatch,tmp_path):
    calls=[];command=discovery_command('parliament',tmp_path/'rows.jsonl')
    assert '--offline' in command and command[2]=='greekocr.real.sources._runner'
    monkeypatch.setattr(subprocess,'run',lambda cmd,**kwargs:calls.append((cmd,kwargs)) or subprocess.CompletedProcess(cmd,0,'fixture',''))
    assert run_discovery('archive',tmp_path/'rows.jsonl',timeout=7).stdout=='fixture'
    assert calls[0][1]['timeout']==12 and calls[0][0][calls[0][0].index('--timeout')+1]=='7'
    with pytest.raises(ValueError):discovery_command('unknown','out')


def test_rate_clients_use_explicit_root_offline(tmp_path):
    client=http_client('archive',tmp_path/'archive');assert client.offline and client.root==tmp_path/'archive'
    client=rate_limited_client('anemi',tmp_path/'anemi');assert client.offline and client.interval==2 and client.budget==1500000000
    with pytest.raises(ValueError):http_client('archive',tmp_path/'bad',interval=.1)
    with pytest.raises(ValueError):http_client('anemi',tmp_path/'bad',interval=1)


def test_refetch_stages_unchanged_script_verifies_bytes(tmp_path,monkeypatch):
    data=b'recorded fixture PDF';out=tmp_path/'pdfs';out.mkdir()
    file=out/'original';file.write_bytes(data);digest=file_sha256(file)
    manifest=tmp_path/'manifest.jsonl';manifest.write_text(json.dumps(dict(pdf_cache_sha256=digest,download_url='https://example.org/fixture'))+'\n')
    def run(cmd,**kwargs):
        script=Path(cmd[1]);assert script.name=='parliament_pdf_cache.py'
        evidence=script.parents[2]/'docs/evidence/s17/pdf_cache_refetch.jsonl'
        assert evidence.read_bytes()==manifest.read_bytes() and kwargs['timeout']==8
        (out/(digest+'.pdf')).write_bytes(data)
    monkeypatch.setattr(subprocess,'run',run)
    receipts=refetch_pdf_cache(manifest,out,timeout=8)
    assert receipts[0]['sha256']==digest and receipts[0]['bytes']==len(data)


def test_ranked_stage_retains_md5_flags(tmp_path,monkeypatch):
    out=tmp_path/'stage';out.mkdir();record=dict(document_id='book',rank=1,files=[dict(md5_matches_manifest=False,sha256='fixture')])
    (out/'receipts.jsonl').write_text(json.dumps(record)+'\n');calls=[]
    monkeypatch.setattr(subprocess,'run',lambda cmd,**kwargs:calls.append((cmd,kwargs)))
    assert stage_parliament(tmp_path,out)==[record]
    assert Path(calls[0][0][1]).name=='fetch_parliament_s2.py'


def test_discovery_runner_relocates_only_resources(tmp_path,monkeypatch):
    import sys
    from greekocr.real.sources import _runner
    root=tmp_path/'evidence/o4c';out=root/'archive.jsonl'
    monkeypatch.setattr(sys,'argv',['runner','archive','--evidence-root',str(root),'--timeout','3','--',
      '--out',str(out),'--offline','--max-pages','1'])
    def run(command,**kwargs):
        script=Path(command[1]);assert script.name=='o4c_discover_archive.py'
        staged=script.parents[2]
        assert (staged/'docs/evidence/o4c').resolve()==root.resolve() and kwargs['timeout']==3
        originals=Path(__file__).parents[1]/'greekocr/_vendor/source_clis/scripts/fetch'
        assert script.read_bytes()==(originals/script.name).read_bytes()
        assert '--offline' in command
        return subprocess.CompletedProcess(command,0)
    monkeypatch.setattr(subprocess,'run',run)
    assert _runner.main()==0
