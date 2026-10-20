"""T16 offline contracts; never import or call a network reader."""
import importlib.util
from pathlib import Path
import hashlib
import pytest
from greekocr.harvest.round1 import (allocate, positions, replacement_candidates,
    substitution_fingerprints, book_signals, pair_page_lines, quintile,
    type_reasons, mixed_block, title_flag)


@pytest.mark.parametrize('vision,docai,flag',[
    ('καὶ ὁ λόγος','κ\u0300 ὁ λόγος','kai_k_mark'),
    ('καὶ τὸ φῶς','κὶ τὸ φῶς','kai_k_mark'),
    ('οὐκ ἔστι','ȣκ ἔστι','ou_8_ligature'),
    ('τοῦ οὐρανοῦ','τοῦ 8ρανοῦ','ou_8_ligature'),
    ('ἐστί λέξις','ἐςτί λέξις','final_sigma_mid_word'),
    ('ὁ καλός','ὁ καlός','latin_inside_greek'),
    ('στ λέξις','ϛ λέξις','stigma_koppa'),
    ('ϙ λέξις','κ λέξις','stigma_koppa'),
])
def test_fingerprint_positive(vision,docai,flag):
    assert flag in substitution_fingerprints(vision,docai)


@pytest.mark.parametrize('vision,docai',[
    ('καὶ ὁ λόγος','καὶ ὁ λόγος'),('οὐκ 8','οὐκ 8'),
    ('οὐκ 8','οὐκ 9'),('λόγος 8','λόγος 8'),
    ('καὶ κρῖμα','και κριμα'),('A ὁ λόγος','A ὁ λόγος'),
])
def test_fingerprint_not_independent_tokens_or_accents(vision,docai):
    assert substitution_fingerprints(vision,docai)==[]


def test_signal_denominator_includes_unpaired_and_symbol_weighting():
    pairs=[dict(vision='λόγος',docai='λόγος',paired=True),dict(vision='',docai='φῶς',paired=False)]
    s=book_signals(pairs,[.2,.8,.8],['ὁ λόγος ἐστὶ τὸ φῶς']*2)
    assert s['letters_agree_rate']==.5
    assert s['docai_mean_symbol_confidence']==pytest.approx(.6)
    assert s['paired_lines']==1 and s['lines']==2


def test_one_line_votes_once_per_fingerprint():
    s=book_signals([dict(vision='καὶ καὶ',docai='κὶ κὶ',paired=True)],[.9],[])
    assert s['fingerprint_line_counts']=={'kai_k_mark':1}
    assert s['fingerprint_line_shares']=={'kai_k_mark':1.0}


def test_language_block_minimum_and_foreign_share():
    assert not mixed_block('A καὶ')
    assert mixed_block('This is a complete foreign language paragraph')
    assert mixed_block('Αυτό είναι ελληνικό κείμενο with many English words')
    assert not mixed_block('Αυτό είναι ένα πλήρες ελληνικό κείμενο')


def test_quintile_interpolation_and_ties():
    assert quintile([0,1,2,3,4,5])==1
    assert quintile([0,1,2,3])==pytest.approx(.6)
    s=book_signals([dict(vision='α',docai='α',paired=True)],[.9],[])
    assert type_reasons(s,.9,0)==['docai_mean_symbol_confidence=0.900000 <= bottom-quintile 0.900000']


def test_fingerprint_strictly_above_five_percent_and_missing_fail_closed():
    s=book_signals([dict(vision='α',docai='α',paired=True)],[.9],[])
    s['fingerprint_line_shares']={'kai_k_mark':.05}
    assert not type_reasons(s,.8,.8)
    s['fingerprint_line_shares']['kai_k_mark']=.05001
    assert 'kai_k_mark' in type_reasons(s,.8,.8)[0]
    empty=book_signals([],[],[])
    assert len(type_reasons(empty,.8,.8))==2


def test_page_pairing_keeps_unmatched_and_refuses_merged_geometry():
    d=[dict(text='αβγ',bbox=[0,0,100,10]),dict(text='δεζ',bbox=[0,10,100,20])]
    v=[dict(text='αβγ δεζ',bbox=[0,0,100,20])]
    pairs=pair_page_lines(v,d)
    assert len(pairs)==2 and all(not p['paired'] for p in pairs)
    v=[dict(text='αβγ',bbox=[0,0,100,10])]
    pairs=pair_page_lines(v,d)
    assert [p['paired'] for p in pairs]==[True,False]


def books(count,decade=1900,decision='IN',offset=0):
    return [dict(book=f'{decade}-{i+offset}',decade=decade,decision=decision) for i in range(count)]


def test_allocation_equal_decade_targets_and_hard_caps():
    bs=books(20,1900)+books(2,1930)
    a,p=allocate(bs)
    assert p['targets'][1900]==p['targets'][1930]
    assert sum(a.values())<=2000 and max(a.values())<=16
    assert p['actual'][1930]==32
    assert p['actual'][1900]-p['targets'][1900] in (0,-1)
    assert p['actual'][1930]<p['targets'][1930]


def test_reduced_books_receive_half_and_out_books_zero():
    bs=books(10,1900)+books(1,1930)+books(1,1930,'REDUCED',1)+books(1,1900,'OUT_TYPE',99)
    a,p=allocate(bs)
    assert a['1930-0']==16 and a['1930-1']==8
    assert '1900-99' not in a


def test_budget_2000_is_never_exceeded_and_dense_fairness():
    a,p=allocate(books(180),budget=2000)
    assert sum(a.values())==2000
    assert max(a.values())-min(a.values())<=1


def test_explicit_redistribution_never_breaks_caps():
    bs=books(20,1900)+books(2,1930)
    a,p=allocate(bs,redistribute=True)
    assert sum(a.values())==352 and max(a.values())<=16
    assert p['policy']=='redistributed'


def test_empty_allocation():
    assert allocate([])==({}, {})


@pytest.mark.parametrize('total,count',[(50,16),(100,13),(2000,16)])
def test_positions_spread_seeded_bounded_exclude_pilot(total,count):
    pilot=[total//2,total//2+1]
    p=positions(total,count,pilot,book='book')
    assert p==positions(total,count,pilot,book='book')
    values=[v['page'] for v in p]
    assert len(set(values))==count and values==sorted(values)
    assert not set(values)&set(pilot)
    assert min(values)>=.08*total and max(values)<=.95*total
    assert p[0]['anchor']==__import__('math').ceil(.08*total)
    assert p[-1]['anchor']==__import__('math').floor(.95*total)
    assert all(0<=v['random_offset']<=2 for v in p)
    assert all(abs((b['anchor']-a['anchor'])-(.87*total/(count-1)))<=2 for a,b in zip(p,p[1:]))


def test_position_collisions_report_exclusion_adjustment():
    p=positions(20,14,[10,11],book='tiny')
    assert len(set(x['page'] for x in p))==14
    assert any(x['exclusion_adjustment'] for x in p)
    with pytest.raises(ValueError):positions(20,19,[10,11])


@pytest.mark.parametrize('excluded,reserved,expected',[
    ([],[],[20,21,22]),([21],[],[20,22]),([21,22],[],[20]),
    ([],[21],[20,22]),([], [21,22],[20]),
])
def test_replacements_are_only_next_two_physical_neighbours(excluded,reserved,expected):
    assert replacement_candidates(20,100,excluded,reserved)==expected


def test_replacements_do_not_cross_95_percent_boundary():
    assert replacement_candidates(94,100)==[94,95]
    assert replacement_candidates(95,100)==[95]


def test_title_flags_are_visible_review_hints():
    assert title_flag('Εκκλησιαστική Ιστορία')=='ecclesiastical/liturgical'
    assert title_flag('Ομήρου Ιλιάς')=='older-style/classical edition'
    assert title_flag('Γαλάτη : Νέον όργανον')==''


def driver():
    p=Path(__file__).resolve().parents[1]/'scripts/harvest/round1.py'
    spec=importlib.util.spec_from_file_location('t16_driver_test',p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod


def test_quality_guard_is_separate_and_reports_faintness_proxy():
    m=driver();limits=dict(ink_min=.05,ink_max=.5,component_min=30,faint_suppression_max=.125)
    features=dict(darkest_percentile_contrast=40,faintness_proxy=40,ink_fraction=.03,component_contrast_p10=20)
    flags,ratio=m.quality_flags(features,{'relative faintness':20},20,limits)
    assert set(flags)=={'bad_darkest_percentile_contrast','bad_faintness_proxy','bad_ink_fraction','faint_components','faint_or_show_through_dominated'}
    assert ratio==.5


def test_frozen_gate_matches_original_pilot_sha():
    m=driver()
    assert hashlib.sha256((m.OUT/'pilot_core.py').read_bytes()).hexdigest()==m.GATE_SHA
    assert callable(m.load_gate().page_gate)


def test_multivolume_global_to_local_positions():
    m=driver();b=dict(catalogue=dict(volumes=[dict(volume_id='a',pages=10),dict(volume_id='b',pages=20)]))
    assert m.locate(b,10)==(b['catalogue']['volumes'][0],10)
    assert m.locate(b,11)==(b['catalogue']['volumes'][1],1)
    assert m.locate(b,30)==(b['catalogue']['volumes'][1],20)
    with pytest.raises(ValueError):m.locate(b,31)


def test_fetcher_explicit_selection_validation_and_middle_compatibility():
    m=driver().fetch_module();r=dict(volumes=[dict(volume_id='a',pages=10,selected_page_indices=[0,2,9])])
    assert m.selected_indices(r,'explicit')=={'a':[0,2,9]}
    assert m.selected_indices(r,'middle:2')=={'a':[4,5]}
    r['volumes'][0]['selected_page_indices']=[2,2]
    with pytest.raises(ValueError):m.selected_indices(r,'explicit')


def fake_fetch_setup(monkeypatch,tmp_path):
    import io,copy
    from PIL import Image
    m=driver().fetch_module();stream=io.BytesIO();Image.new('RGB',(60,90),'white').save(stream,format='PDF');body=stream.getvalue()
    class HTTP:
        transferred=0
        ledger=tmp_path/'unused-ledger.jsonl'
        calls=[]
        def safe(self,value):return value
        def get(self,url,limit):
            self.calls.append(url);self.transferred+=len(body)
            return dict(url=url,status=200,bytes=len(body),sha256=hashlib.sha256(body).hexdigest(),fetched_at='2026-10-14T00:00:00+00:00',truncated=False),body
    client=HTTP();url=m.BASE+'/metadata/test/book.pdf'
    volume=dict(volume_id='volume',pages=10,source_pdf_url=url,viewer_url=m.BASE+'/php/pdf_pager.php?rec=test&do=book.pdf',viewer_rec_id='test',selected_page_indices=[1])
    record=dict(record_id='test',rank=1,pages=10,volumes=[volume])
    monkeypatch.setattr(m,'viewer_descriptor',lambda http,v:dict(endpoint=m.BASE+'/php/pdf_split.php',filename='/var/www/anemi-portal/metadata/test/book.pdf',source_pdf_url=url))
    def run(r):return m.fetch_wave([r],wave=1,max_pages=10,max_bytes=1_000_000,dest=tmp_path/'dest',http_root=tmp_path/'http',http_factory=lambda **kwargs:client,login=lambda h:True,emit=lambda s:None,page_range='explicit')
    return m,record,client,run


def test_fetcher_resumes_and_unions_only_explicit_new_pages(monkeypatch,tmp_path):
    import copy,json
    m,r,client,run=fake_fetch_setup(monkeypatch,tmp_path)
    assert run(r)['pages']==1
    expanded=copy.deepcopy(r);expanded['volumes'][0]['selected_page_indices']=[3]
    result=run(expanded)
    assert result['pages']==1 and result['skipped_pages']==1
    manifest=json.loads((tmp_path/'dest/wave_manifest.json').read_text())
    assert manifest['records'][0]['volumes'][0]['selected_page_indices']==[1,3]
    assert run(expanded)['pages']==0 and len(client.calls)==2


def test_fetcher_rejects_metadata_drift_on_resume(monkeypatch,tmp_path):
    import copy
    m,r,client,run=fake_fetch_setup(monkeypatch,tmp_path)
    run(r);changed=copy.deepcopy(r);changed['volumes'][0]['pages']=11
    with pytest.raises(m.ProbeError):run(changed)
    assert len(client.calls)==1


def test_fetcher_refetches_corrupt_saved_pdf(monkeypatch,tmp_path):
    m,r,client,run=fake_fetch_setup(monkeypatch,tmp_path)
    run(r)
    page=tmp_path/'dest/records'/m.record_key('test')/'volume/page-000002.pdf'
    page.write_bytes(b'corrupt')
    result=run(r)
    assert result['pages']==1 and result['skipped_pages']==0
    assert page.read_bytes().startswith(b'%PDF-')


def test_retained_unplanned_pdf_is_gated_manifested_and_not_accepted(monkeypatch,tmp_path):
    import json,datetime
    fm,r,client,fetch=fake_fetch_setup(monkeypatch,tmp_path);fetch(r)
    m=driver();monkeypatch.setattr(m,'ROOT',tmp_path);monkeypatch.setattr(m,'BIG',tmp_path/'dest');monkeypatch.setattr(m,'OUT',tmp_path/'report');monkeypatch.setattr(m,'fetch_module',lambda:fm)
    (m.BIG/'images').mkdir();m.OUT.mkdir()
    calls=[]
    def gate(pdf,image,stack,gate,limits):
        calls.append(pdf);image.write_bytes(b'rendered-for-test')
        return dict(accepted=True,flags=[],seconds=.01)
    monkeypatch.setattr(m,'gate_pdf',gate)
    b=dict(book='test',key=fm.record_key('test'),catalogue=r,decade=1900,decision='IN',allocation=1)
    data=dict(books=[b],quality_limits={},allocation_policy={});m.atomic(m.OUT/'selection.json',data)
    results={}
    assert m.gate_unaccounted(data,results,None,None)==1
    assert m.gate_unaccounted(data,results,None,None)==0
    assert len(calls)==1
    state=dict(complete=False,fetch_seconds=1,started_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    m.report(data,results,[],state)
    manifest=m.read(m.OUT/'manifest.json');summary=m.read(m.OUT/'summary.json')
    assert len(manifest['pages'])==1
    assert manifest['pages'][0]['gate']['accepted']
    assert not manifest['pages'][0]['harvest_accepted']
    assert manifest['pages'][0]['selection_disposition']=='superseded_page_plan'
    assert summary['pages_fetched']==summary['pages_gated']==1
    assert summary['pages_accepted']==0 and summary['pages_not_selected']==1
