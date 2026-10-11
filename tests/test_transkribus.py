"""T12 offline parsing, safety, queue and three-engine measurement contracts."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import unicodedata

from PIL import Image
import pytest

from greekocr.readers.services.transkribus import (
    CREDITS_URL, TOKEN_URL, CreditFloorError, TranskribusError, TranskribusReader,
    _reading, load_transkribus, parse_balance, parse_page, parse_result, parse_token, request_payload,
)
from prototypes.harvest import google_failed_lines as g
from prototypes.harvest.transkribus_failed_lines import agreement, three_way_metrics

FIXTURE=Path(__file__).parent/'data/transkribus'


def sample(name):
    return json.loads((FIXTURE/name).read_text())


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    import requests
    def forbidden(*args,**kwargs):pytest.fail('network is forbidden in T12 tests')
    monkeypatch.setattr(requests.sessions.Session,'request',forbidden)
    monkeypatch.setenv('TRANSKRIBUS_USERNAME','inert-test-identity')
    monkeypatch.setenv('TRANSKRIBUS_PASSWORD','inert-test-secret')


class MockSession:
    def __init__(self,balance=200,statuses=None,error=None):
        self.balance=balance
        self.calls=[]
        self.submits=0
        self.statuses=list(statuses or [])
        self.error=error

    def request(self,method,url,**kw):
        self.calls.append((method,url,kw))
        code=200
        raw={}
        text=''
        if url==TOKEN_URL:raw=sample('token.json')
        elif url==CREDITS_URL:raw=dict(overallBalance=self.balance)
        elif method=='POST':
            self.submits+=1
            if self.error:code=self.error
            else:
                self.balance-=.25
                raw=dict(processId=120+self.submits,status='CREATED')
        elif url.endswith('/page'):text=(FIXTURE/'page.xml').read_text()
        elif 'creditTransactions' in url:
            pid=int(url.split('/jobs/')[1].split('/')[0])
            raw=dict(trpCreditTransaction=[dict(jobId=pid,creditValue=-.25,costFactor=.25,nrOfPages=1.0)])
        else:
            raw=sample('response.json')
            raw['status']=self.statuses.pop(0) if self.statuses else 'FINISHED'
        return SimpleNamespace(status_code=code,json=lambda:deepcopy(raw),text=text)


@pytest.fixture
def setup(tmp_path):
    path=tmp_path/'crop.png'
    Image.new('L',(100,20),255).save(path)
    session=MockSession()
    reader=TranskribusReader(responses_dir=tmp_path/'responses',session=session,mode='single_line',sleep=lambda s:None)
    return reader,path,session


def test_token_sample_expiry_and_refresh_fields():
    a,r,deadline=parse_token(sample('token.json'),100)
    assert a=='synthetic-access-sample' and r=='synthetic-refresh-sample' and deadline==400


@pytest.mark.parametrize('expiry',[0,-1,float('inf'),float('nan')])
def test_invalid_token_expiry_rejected(expiry):
    with pytest.raises(TranskribusError):parse_token(dict(access_token='inert',expires_in=expiry),0)


def test_credit_sample_uses_overall_balance():
    assert parse_balance(sample('credits.json'))==200


@pytest.mark.parametrize('raw',[{},dict(overallBalance=-1),dict(overallBalance=float('nan'))])
def test_unknown_invalid_credit_balance_cannot_authorize_work(raw):
    with pytest.raises(TranskribusError):parse_balance(raw)


def test_page_lines_confidence_and_glyphs_preserve_codepoints():
    result=parse_page((FIXTURE/'page.xml').read_text())
    assert result['lines']==['ἅϗ','ȣ ϛ ϲ']
    assert result['line_confidences']==[.8,None]
    assert [r['confidence'] for r in result['symbol_confidences']]==[.7,.9]
    assert result['token_confidences'][0]['confidence']==.85
    reading=_reading(dict(page_xml=(FIXTURE/'page.xml').read_text()),{})
    assert reading.text==unicodedata.normalize('NFD','ἅϗ\nȣ ϛ ϲ')
    assert reading.raw_text=='ἅϗ\nȣ ϛ ϲ'
    assert reading.mean_symbol_conf==pytest.approx(.8) and reading.min_symbol_conf==.7


def test_json_sample_missing_char_confidence_stays_null():
    result=parse_result(sample('response.json'))
    assert result['lines']==['ἅϗ','ȣ ϛ ϲ'] and result['line_confidences']==[.8,None]
    reading=_reading(sample('response.json'),{})
    assert not reading.symbol_confidences and reading.mean_symbol_conf is None


def test_page_region_reading_order_and_primary_alternative():
    xml='<PcGts><Page><ReadingOrder><OrderedGroup><RegionRefIndexed regionRef="b" index="0"/><RegionRefIndexed regionRef="a" index="1"/></OrderedGroup></ReadingOrder><TextRegion id="a"><TextLine><TextEquiv><Unicode>A</Unicode></TextEquiv></TextLine></TextRegion><TextRegion id="b"><TextLine><TextEquiv><Unicode>B</Unicode></TextEquiv></TextLine></TextRegion></Page></PcGts>'
    assert parse_page(xml)['lines']==['B','A']


@pytest.mark.parametrize('xml',['<PcGts/>','<!DOCTYPE Page><Page/>','<PcGts><Page/><Page/></PcGts>'])
def test_malformed_or_multiple_pages_fail(xml):
    with pytest.raises(ValueError):parse_page(xml)


def test_default_and_single_line_payloads(setup):
    _,path,_=setup
    image=path.read_bytes()
    default=request_payload(image,148525,'default')
    single=request_payload(image,999,'single_line')
    assert 'content' not in default
    assert default['config']['lineDetection']=={'modelId':49272}
    assert single['config']['textRecognition']['htrId']==999
    line=single['content']['regions'][0]['lines'][0]
    assert line['coords']['points']=='0,0 99,0 99,19 0,19'
    assert line['baseline']['points']=='0,14 99,14'


def test_at_most_once_cache_and_no_auth_on_reuse(setup):
    reader,path,session=setup
    reading=reader.read(path)
    assert reading.raw_text=='ἅϗ\nȣ ϛ ϲ' and session.submits==1
    count=len(session.calls)
    assert reader.read(path).cached
    assert len(session.calls)==count
    envelope=json.loads(Path(reading.raw_json_path).read_text())
    assert envelope['credits_used']==.25 and envelope['credentials']=='environment credentials used'


def test_credential_variables_and_tokens_never_persisted(setup):
    reader,path,_=setup
    reader.read(path)
    for file in reader.output_dir.rglob('*'):
        if file.is_file():
            data=file.read_bytes()
            assert b'inert-test-secret' not in data and b'inert-test-identity' not in data
            assert b'synthetic-access-sample' not in data and b'synthetic-refresh-sample' not in data


def test_expiry_refresh_uses_refresh_grant(setup):
    reader,_,session=setup
    reader._access_token()
    reader._expires_at=0
    reader._access_token()
    token_calls=[kw['data'] for _,url,kw in session.calls if url==TOKEN_URL]
    assert token_calls[0]['grant_type']=='password'
    assert token_calls[1]['grant_type']=='refresh_token'
    assert 'username' not in token_calls[1] and 'password' not in token_calls[1]


def test_credit_floor_prevents_submission(setup):
    reader,path,session=setup
    session.balance=50.75
    with pytest.raises(CreditFloorError):reader.read(path)
    assert session.submits==0 and not list((reader.output_dir/'attempts').glob('*.json'))


@pytest.mark.parametrize('code',[402,429])
def test_insufficient_credits_stops_and_uncertain_attempt_is_not_retried(setup,code):
    reader,path,session=setup
    session.error=code
    with pytest.raises(CreditFloorError):reader.read(path)
    with pytest.raises(TranskribusError,match='uncertain prior'):reader.read(path)
    assert session.submits==1


def test_hash_or_binding_mismatch_cannot_resubmit(setup):
    reader,path,session=setup
    with pytest.raises(ValueError,match='crop changed'):reader.read(path,expected_sha256='bad')
    reader.read(path)
    reader.model_id=999
    with pytest.raises(ValueError,match='binding'):reader.read(path)
    assert session.submits==1


def test_cache_tampering_fails(setup):
    reader,path,session=setup
    reading=reader.read(path)
    target=Path(reading.raw_json_path)
    envelope=json.loads(target.read_text());envelope['response']['page_xml']+=' '
    target.write_text(json.dumps(envelope))
    with pytest.raises(ValueError,match='hash changed'):reader.read(path)
    assert session.submits==1


def test_failed_process_no_resubmit(setup):
    reader,path,session=setup
    session.statuses=['FAILED']
    with pytest.raises(TranskribusError,match='FAILED'):reader.read(path)
    with pytest.raises(TranskribusError,match='prior process failed'):reader.read(path)
    assert session.submits==1


def test_bounded_wait_preserves_process_for_unbilled_resume(setup):
    reader,path,session=setup
    now=[0.0]
    reader.clock=lambda:now[0]
    reader.sleep=lambda t:now.__setitem__(0,now[0]+t)
    reader.max_wait_s=3
    session.statuses=['RUNNING']*10
    with pytest.raises(TranskribusError,match='bounded'):reader.read(path)
    assert session.submits==1
    session.statuses=[]
    reader.read(path)
    assert session.submits==1


def test_queue_reserves_all_pending_charges_and_drains_accepted(setup,tmp_path):
    reader,path,session=setup
    session.balance=52
    other=tmp_path/'other.png';Image.new('L',(101,20),255).save(other)
    rows=[dict(crop_path=str(p),crop_sha256=g.sha256(p)) for p in (path,other)]
    results=[]
    with pytest.raises(CreditFloorError):
        for row,reading in reader.read_many(rows):results.append(reading)
    assert session.submits==1 and len(results)==1
    envelope=json.loads(Path(results[0].raw_json_path).read_text())
    assert envelope['credits_used']==.25 and envelope['credit_transactions'][0]['jobId']==121


def test_queue_duplicate_sha_is_one_charge(setup):
    reader,path,session=setup
    rows=[dict(crop_path=str(path),crop_sha256=g.sha256(path))]*2
    results=list(reader.read_many(rows))
    assert len(results)==2 and session.submits==1


def test_offline_rebuild_never_authenticates(setup):
    reader,path,session=setup
    row=dict(crop_path=str(path),crop_sha256=g.sha256(path))
    assert list(reader.read_many([row],offline=True))==[]
    assert not session.calls
    reader.read(path)
    count=len(session.calls)
    assert list(reader.read_many([row],offline=True))[0][1].cached
    assert len(session.calls)==count


def test_explicit_enable_and_engine_dispatch(monkeypatch,tmp_path):
    with pytest.raises(TranskribusError,match='explicitly enabled'):load_transkribus(responses_dir=tmp_path)
    import prototypes.harvest.transkribus_failed_lines as module
    calls=[]
    monkeypatch.setattr(module,'run_transkribus',lambda *args,**kw:calls.append((args,kw)) or dict(status='complete'))
    assert g.run(tmp_path,tmp_path,engine='transkribus',offline=True)['status']=='complete'
    assert calls[0][1]['offline']
    metrics=g.crop_metrics(dict(page_xml=(FIXTURE/'page.xml').read_text()),100,20,engine='transkribus')
    assert metrics['lines_returned']==2 and metrics['mean_symbol_confidence']==pytest.approx(.8)


def test_majority_nfd_and_line_breaks_are_separate():
    result=three_way_metrics(dict(docai='ἅ\n',vision='α\u0314\u0301',transkribus='ἅ'))
    assert not result['majority_raw'] and result['majority_nfd']
    assert result['unanimous_nfd_without_cr_lf'] and not result['unanimous_nfd']
    assert result['docai_vision_edits']==1
    assert result['docai_vision_cer']==.25


def test_cer_empty_denominators_and_raw_rare_glyph():
    result=three_way_metrics(dict(docai='',vision='',transkribus='ϗ'))
    assert result['majority_raw'] and not result['unanimous_raw']
    assert result['docai_transkribus_cer'] is None
    assert result['docai_vision_cer']==0 and result['docai_transkribus_reverse_cer']==1


def test_pooled_cer_and_common_cohort_exclude_missing_engine():
    full=dict(triple_available=True,**three_way_metrics(dict(docai='abc',vision='abd',transkribus='abd')))
    missing=dict(triple_available=False)
    result=agreement([full,missing])
    assert result['n_crops']==2 and result['n_triples']==1
    assert result['docai_vision']['pooled_cer']==pytest.approx(1/3)
    assert result['majority_raw']==1


def test_cli_accepts_transkribus_and_anemi_opt_in(monkeypatch):
    calls=[]
    monkeypatch.setattr(g,'run',lambda *a,**kw:calls.append(kw) or dict(status='complete'))
    previous=g.ALLOW_ANEMI
    try:
        assert g.main(['--engine','transkribus','--include-anemi','--offline'])==0
        assert calls[0]['engine']=='transkribus' and g.ALLOW_ANEMI
    finally:g.ALLOW_ANEMI=previous


@pytest.mark.parametrize('kwargs',[dict(max_wait_s=float('nan')),dict(max_page_credits=float('inf')),dict(http_timeout_s=0),dict(credit_floor=49)])
def test_invalid_limits_cannot_disable_bounded_wait_or_floor(tmp_path,kwargs):
    with pytest.raises(ValueError):TranskribusReader(responses_dir=tmp_path,**kwargs)


def test_bounded_runner_retry_preserves_original_and_reserves_unknown_charge(setup):
    from prototypes.harvest.transkribus_failed_lines import _prepare_bounded_retries
    reader,path,session=setup
    session.error=502
    with pytest.raises(TranskribusError):reader.read(path)
    row=dict(crop_id='s2-synthetic',page='s2-synthetic',crop_path=str(path),crop_sha256=g.sha256(path))
    attempt=reader.output_dir/'attempts'/(row['crop_sha256']+'.json')
    original=attempt.read_bytes()
    _prepare_bounded_retries([row,row],reader.output_dir,reader)
    assert not attempt.exists()
    assert (reader.output_dir/'prior_attempts'/attempt.name).read_bytes()==original
    assert reader.credit_floor==51 and session.submits==1
    session.error=None
    reader.read(path)
    assert session.submits==2
    # A second explicit recovery cannot erase/repeat the completed response.
    _prepare_bounded_retries([row],reader.output_dir,reader)
    assert session.submits==2


def test_retry_credit_shortfall_preserves_attempt(setup):
    from prototypes.harvest.transkribus_failed_lines import _prepare_bounded_retries
    reader,path,session=setup
    session.error=502
    with pytest.raises(TranskribusError):reader.read(path)
    session.balance=51.5
    row=dict(crop_id='s2-synthetic',page='s2-synthetic',crop_path=str(path),crop_sha256=g.sha256(path))
    with pytest.raises(ValueError,match='reservation'):_prepare_bounded_retries([row],reader.output_dir,reader)
    assert (reader.output_dir/'attempts'/(row['crop_sha256']+'.json')).exists()


def test_shared_cache_helper_routes_transkribus_and_offline_sha_reuse(setup):
    reader,path,session=setup
    row=dict(crop_id='s2-synthetic',page='s2-synthetic',crop_path=str(path),crop_sha256=g.sha256(path))
    first=g.cached_response(row,reader.output_dir,reader,engine='transkribus')
    assert first['binding']['engine']=='transkribus' and session.submits==1
    count=len(session.calls)
    second=g.cached_response(dict(row,crop_id='s2-identical'),reader.output_dir,reader,engine='transkribus',offline=True)
    assert first['response_sha256']==second['response_sha256'] and len(session.calls)==count
