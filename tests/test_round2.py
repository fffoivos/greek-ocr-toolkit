"""Offline T22 contracts: new-book selection, bounded slots, hold-outs and reads."""
from collections import Counter
import json
from pathlib import Path

from PIL import Image
import pytest

from scripts.harvest import round2 as r
from scripts.harvest import round2_outputs as o
from greekocr.harvest.readers import BudgetExceeded


def row(**kwargs):
    return dict(document_id='new',title='Ιστορία της Ελλάδος',year=1901,pages=100,
        download_url='https://anemi.lib.uoc.gr/book.pdf',language=['gre'],catalogue_materials=['010'],**kwargs)


@pytest.mark.parametrize('field,value,reason',[
    ('year',1859,'year'),('year',1936,'year'),('pages',59,'pdf_or_pages'),
    ('download_url',None,'pdf_or_pages'),('language',['fre'],'language'),
    ('catalogue_materials',['020'],'not_monograph'),
    ('title','Histoire de la Grece','plainly_foreign_title'),
    ('title','Geschichte von Griechenland','plainly_foreign_title'),
    ('title','Storia della Grecia','plainly_foreign_title'),
    ('title','History of Greece','plainly_foreign_title'),
    ('title','Λεξικόν της ελληνικής γλώσσης','wave5_dictionary_grammar'),
    ('title','Γραμματική της αρχαίας ελληνικής','wave5_dictionary_grammar'),
    ('title','Συνώνυμα και συγγενικά','wave5_dictionary_grammar'),
    ('title','Πασχαλινή επετηρίς','wave5_periodical'),
])
def test_selection_filters(field,value,reason):
    candidate=row();candidate[field]=value
    assert r.eligible(candidate,set())==(False,reason)


def test_every_round1_and_early_book_excluded_even_if_otherwise_valid():
    for ident in ('round1','early'):
        candidate=row();candidate['document_id']=ident
        assert r.eligible(candidate,{'round1','early'})==(False,'previous_book')
    assert r.eligible(row(),{'round1','early'})==(True,None)


@pytest.mark.parametrize('year',[1860,1935])
def test_inclusive_year_and_page_boundaries(year):
    candidate=row();candidate.update(year=year,pages=60)
    assert r.eligible(candidate,set())[0]


def candidates():
    return [dict(book=f'{d}-{i}',key=f'{d:04d}{i:020d}',title='Ιστορία',year=d+i%10,decade=d,
                 place_hints=['Athens'] if i%2 else ['Corfu'],publishers=[])
            for d in r.DECADES for i in range(20)]


def test_seeded_draw_exact_50_six_or_seven_every_decade_order_independent():
    a,q=r.draw_books(candidates(),Counter(Athens=8,Corfu=1),Counter())
    b,_=r.draw_books(candidates()[::-1],Counter(Athens=8,Corfu=1),Counter())
    assert a==b and len(a)==len({x['book'] for x in a})==50
    assert Counter(x['decade'] for x in a)==q
    assert sorted(q.values())==[6]*6+[7]*2
    assert r.draw_books(candidates(),Counter(),Counter(),seed=20263)[0]!=a


def test_diversity_weights_prefer_known_rare_place_and_unknown_has_no_bonus():
    a,_=r.draw_books(candidates(),Counter(Athens=8,Corfu=1),Counter())
    weights={b['place_hints'][0]:b['draw_weight'] for b in a}
    assert weights['Corfu']>weights['Athens']>1


def test_holdout_frozen_eight_books_one_per_decade_six_test_two_dev():
    books,_=r.draw_books(candidates(),Counter(),Counter())
    held=r.select_holdout(books)
    assert held==r.select_holdout(books[::-1])
    assert len(held)==8 and Counter(b['split'] for b in held)=={'test':6,'dev':2}
    assert Counter(b['decade'] for b in held)=={d:1 for d in r.DECADES}


def test_replacement_neighbours_stop_at_plus_two_and_95_percent():
    assert r.replacement_candidates(90,100)==[90,91,92]
    assert r.replacement_candidates(94,100)==[94,95]
    assert r.replacement_candidates(90,100,reserved={91})==[90,92]


def test_slot_replay_stops_at_first_accept_and_tracks_failed_fetch():
    book=dict(book='new',key='newkey',positions=[dict(page=10,candidates=[10,11,12])])
    gates={'newkey:11':dict(harvest_accepted=False,gate={'flags':['table']}),
           'newkey:12':dict(harvest_accepted=True,gate={'flags':[]})}
    slots,_=r.replay_slots([book],gates,{'newkey:10':dict()})
    assert slots[0]['accepted_page']==12
    assert [c['state'] for c in slots[0]['chain']]==['fetch_failed','rejected','accepted']


def binding():
    return dict(project='test',location='eu',processor='test',version='test',user_project='test',
        options=dict(ocrConfig=dict(enableSymbol=True,hints=dict(languageHints=['el']))))


def reader(root):
    return r.Round2Readers(dict(binding=binding(),cap_usd=1.5,max_calls=650),root=root)


def test_no_vision_adapter_or_calls(tmp_path):
    instance=reader(tmp_path)
    assert not hasattr(instance,'vision')
    with pytest.raises(ValueError,match='forbids'):
        instance.call('vision','unused')


def test_success_cached_at_most_once_and_budget_unchanged(tmp_path,monkeypatch):
    instance=reader(tmp_path);path=tmp_path/'page.png';Image.new('L',(20,20),255).save(path)
    digest=r.sha(path);result=dict(status='ok',binding=binding(),image_sha256=digest)
    r.atomic(tmp_path/'parsed/docai'/(digest+'.json'),result)
    monkeypatch.setattr(instance.docai,'read',lambda *a:pytest.fail('no provider request'))
    assert instance.call('docai',path)==instance.call('docai',path)==result
    assert instance.budget.receipt()['calls_reserved']==0


def test_interrupted_reserved_attempt_never_retried(tmp_path,monkeypatch):
    instance=reader(tmp_path);path=tmp_path/'page.png';Image.new('L',(20,20),255).save(path)
    instance.budget.reserve('docai',r.sha(path))
    monkeypatch.setattr(instance.docai,'read',lambda *a:pytest.fail('no retry'))
    result=instance.call('docai',path)
    assert result['error_class']=='InterruptedReservedAttempt'
    assert instance.call('docai',path)==result
    assert instance.budget.receipt()['calls_reserved']==1


def test_provider_attempt_without_parsed_cache_never_retried(tmp_path,monkeypatch):
    instance=reader(tmp_path);path=tmp_path/'page.png';Image.new('L',(20,20),255).save(path)
    r.atomic(tmp_path/'docai/notused.json',{})
    (tmp_path/'docai/ledger.jsonl').write_text(json.dumps(dict(crop_sha256=r.sha(path)))+'\n')
    monkeypatch.setattr(instance.docai,'read',lambda *a:pytest.fail('no retry'))
    with pytest.raises(RuntimeError,match='no re-read'): instance.call('docai',path)
    assert instance.budget.receipt()['calls_reserved']==0


def test_previous_read_scope_includes_pages_without_line_records(tmp_path,monkeypatch):
    for i,name in enumerate(('round1/reads_d1/plan.json','round1/reads_rest/plan.json','vouli/plan.json')):
        path=tmp_path/'docs/records/harvest'/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(dict(pages=[dict(image_sha256=f'hash-{i}')])) )
    monkeypatch.setattr(r,'REPO',tmp_path)
    assert r.previous_page_hashes()=={'hash-0','hash-1','hash-2'}


def test_round2_spend_cap_survives_more_than_planned_calls(tmp_path):
    instance=r.Round2Readers(dict(binding=binding(),cap_usd=1.5,max_calls=2000),root=tmp_path)
    for i in range(1000): instance.budget.reserve('docai',str(i))
    assert instance.budget.receipt()['cost_usd']==1.5
    with pytest.raises(BudgetExceeded): instance.budget.reserve('docai','over')


def line(ident,text,book='new'):
    return dict(id=ident,page_id='page',book_key=book,year=1901,decade=1900,
        docai_text=text,confidence=.99,bbox=[0,0,100,20],flags=[],licence='anemi-research-internal',
        source_url='https://anemi.lib.uoc.gr/book',attribution='Anemi')


def test_o5_checks_round1_vouli_and_new_holdouts():
    texts=['Ἑλληνικὴ ἱστορία πρώτη','Ἑλληνικὴ ἱστορία δεύτερη','Ἑλληνικὴ ἱστορία τρίτη']
    records=[line(str(i),t) for i,t in enumerate(texts)]+[line('hold',texts[2],book='held')]
    old=[dict(id='old1',source='anemi_round1',split='test',label=texts[0]),
         dict(id='old2',source='vouli_parliament_1850s',split='dev',label=texts[1])]
    kept,rejected,quality,before,exclusions=o.admit_records(records,[dict(book_key='held',split='test')],old)
    assert [r['id'] for r in kept]==['hold']
    assert len(rejected)==3 and all(r['reasons']==['label_in_holdout'] for r in rejected)


def test_bad_page_dropped_after_read_and_visibly_marked():
    records=[line(str(i),'Ἑλληνικὴ ἱστορία') for i in range(3)]
    for row in records[:2]: row['confidence']=.1
    kept,rejected,quality,*_=o.admit_records(records,[],[])
    assert not kept and all('bad_page' in r['reasons'] for r in rejected)
    image=Image.new('L',(800,200),255)
    canvas,layout=o.render_compiled(image,[],quality['page'])
    assert layout['bad_page'] is True
    assert canvas.crop((40,0,840,35)).getextrema()!=((255,255),)*3


def test_compiled_path_and_crop_id_use_required_six_characters():
    page=dict(decade=1900,year=1901,title='Ιστορία της Ελλάδος',key='abcdef123456',page=7)
    assert str(o.compiled_path(page))=='1900s/1901_Ιστορία της Ελλάδος_abcdef/p0007.jpg'


def test_live_frozen_selection_has_no_previously_fetched_books():
    selection=json.loads((r.OUT/'selection.json').read_text())
    ids={b['book'] for b in selection['books']}
    assert not ids&set(selection['excluded_round1'])
    assert not ids&set(selection['excluded_early'])
    assert len(ids)==50 and sum(len(b['positions']) for b in selection['books'])==650
