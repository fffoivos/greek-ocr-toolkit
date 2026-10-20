"""ASTRA-SC1 executable counterexamples; no network, recognition or training."""
from copy import deepcopy
import json
from pathlib import Path
from tests._paths import require_file
from types import SimpleNamespace
import numpy as np
import pytest
from PIL import Image, ImageDraw
from greekocr.labelfix import ink as I, case
from greekocr.labelfix.reading import LineReading, apply_constraints
from greekocr.labelfix.segmentation import _region
from scripts.labelfix.box_regression import diff_line, slot_of

ROOT=Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0,str(ROOT/"scripts/labelfix"))

def crop(labels):
    h,w=labels.shape
    return I.CropInk(np.where(labels>0,20.,255.),labels>0,labels,20.,np.full(w,12.),np.full(w,18.),[],255.,w,h,20.)

def test_supported_printed_misprint_is_flagged_and_hold():
    s=dict(base='ε',start=0,parts=['circumflex'],naming={'probability':1.},
           evidence=dict(xh=20,body=[10,25],above=[dict(bbox=[12,4,22,10],area=50)]))
    rd,removed=apply_constraints(LineReading('ε\u0342',[s],[]))
    assert rd.text=='ε\u0342' and not removed
    assert rd.slots[0]['hold'] and rd.slots[0]['label_status']=='HOLD'
    assert any(f['rule']=='C4:circumflex_on_short_vowel' and f['evidence']['blob_area']==50 for f in rd.constraint_flags)
    norm,removed=apply_constraints(LineReading('ε\u0342',[s],[]),output='normalised')
    assert norm.text=='ε' and len(removed)==1

def test_clipping_preserves_source_pixels_and_never_grows():
    lab=np.zeros((20,20),int)
    lab[2:12,2]=1;lab[2,2:14]=1;lab[11,2:14]=1;lab[4:10,4:12]=2
    ci=crop(lab);b=I._blob(lab==1,0,0,'attached',ci);q=I.zone_blob(ci,b,upper=10)
    assert q is not None and q.area<=b.area
    assert q.pixel_keys()<=b.pixel_keys() and q.source_ids==(1,)
    assert all(lab[y,x]==1 for y,x in q.pixel_keys())

def test_union_case_occupancy_uses_all_parents():
    lab=np.zeros((30,40),int);lab[5:25,5:10]=1;lab[5:25,15:20]=2
    ci=crop(lab);c=_region(ci,[SimpleNamespace(index=1),SimpleNamespace(index=2)],5,20)
    assert case.features(ci,c)[5]==pytest.approx(2/3)
    assert c.component_ids==(1,2)

@pytest.mark.parametrize('marks',['\u0301\u0300','\u0304','\u0306','\u0307'])
def test_unsupported_print_truth_unknown(marks):
    from scripts.labelfix.s6_validate import char_truth
    reasons={}
    t=char_truth(dict(line_id='probe',google='α',model='α',human='α'),{'probe|0':{'printed':'α'+marks}},reasons=reasons)
    assert t=={0:None}
    assert reasons[0]['reason']=='unsupported_printed_marks'

def test_box_matching_order_independent_and_global():
    old=dict(reading='',letters=[[0,10],[5,15]],boxes=[dict(kind='above',bbox=[0,0,10,10]),dict(kind='above',bbox=[5,0,15,10])])
    new=dict(reading='',letters=old['letters'],boxes=[dict(kind='above',bbox=[2,0,12,10]),dict(kind='above',bbox=[-3,0,7,10])])
    rev=deepcopy(old);rev['boxes'].reverse()
    for v in (old,rev):
        d=diff_line(v,new,.3)
        assert len(d['lost'])==len(d['added'])==0 and len(d['moved'])==2
    assert slot_of([100,0,110,10],[[0,10]]) is None

def note_pair():
    old=dict(slots=[dict(slot=1,truth=None,detected=[])],recogniser_slots=[dict(start=0,component_slot=1,parts=['acute'],evidence={'above':[{'bbox':[0,0,3,3]}]})])
    new=deepcopy(old);new['recogniser_slots'][0]['parts']=[]
    return old,new

def test_approved_unknown_name_loss_fails():
    from scripts.labelfix.s6_notes import clause
    old,new=note_pair()
    assert not clause(new,old,'no_regression',None,None)[0]

@pytest.mark.parametrize('kind',['no_top','no_subscript','mark','fusion','named'])
def test_missing_note_target_unresolved(kind):
    from scripts.labelfix.s6_notes import clause
    old,new=note_pair();ok,why=clause(new,old,kind,999,1)
    assert not ok and why.get('unresolved')

def test_slot_clause_parser_excludes_counts_dates_and_neighbours():
    from scripts.labelfix.owner_implicit_changes import mentioned_slots
    assert mentioned_slots('2 marks at 7; slot 12; 15-16; 2026 pixels')=={7,12,15,16}

def test_r1_blank_and_padding_are_explicit_unqualified_evidence():
    from scripts.labelfix.clariden.r1_extract import window,extract_line,WINDOW_CONTRACT
    a=Image.new('L',(80,40),255);b=Image.new('L',(80,80),255)
    for im in (a,b):ImageDraw.Draw(im).rectangle((20,10,29,29),fill=0)
    wa,_=window(a,[20,30],20);wb,_=window(b,[20,30],20)
    # Keep the trained view unchanged in SF1; its limitation is machine-readable.
    assert not np.array_equal(wa,wb) and WINDOW_CONTRACT['padding_invariant'] is False
    al=dict(prediction='α',spans=[['α',0,1,20.,30.]],confidence=.9)
    ss,_,_,_,coverage,size=extract_line(dict(_line=0,recogniser_text='α'),al,Image.new('L',(80,40),255),evaluation=True)
    assert len(ss)==1 and size['pixel_measurements']==0
    assert coverage[0]['evidence_state']=='UNKNOWN' and 'no_pixel_evidence' in coverage[0]['uncertainty']

def test_saved_r1_baselines_have_correct_labels():
    p=ROOT/'docs/records/labelfix/spellcheck/clariden/R1_result_3678928/metrics.json'
    m=json.loads(p.read_text())
    for name,expected in [('S4',(3726,261,327)),('S5',(3714,249,339)),('S6',(3731,245,322))]:
        t=m['reference'][name]['all_unscored_none']['total']
        assert tuple(t[k] for k in ('tp','fp','fn'))==expected
    assert set(m['policies'])=={'raw','filtered'}

def test_model_assets_distinct_and_disjointness_bound():
    import hashlib
    root=ROOT/'docs/records/labelfix'
    assert hashlib.sha256((root/'markshape_model.json').read_bytes()).hexdigest()!=hashlib.sha256((root/'markshape_model_S4.json').read_bytes()).hexdigest()
    d=json.loads((ROOT/'artifacts/labelfix_r1/binding/disjointness.json').read_text())
    assert len(d)==7 and all(x['document_count']==x['line_count']==0 for x in d.values())

def test_pixel_union_conserved_when_deduplicating_native_proposals():
    from greekocr.labelfix.reading import read_ink
    from greekocr.labelfix.ctc_align import Alignment
    from greekocr.labelfix.markshape import load_model
    c=json.loads((ROOT/'tests/data/labelfix_s6/cases.json').read_text())[0]
    with Image.open(ROOT/'tests/data/labelfix_s6'/f"{c['line_id']}.png") as im:ci=I.analyse(im)
    rd=read_ink(ci,c['recogniser_text'],Alignment.from_record(c['alignment']),load_model(ROOT/'docs/records/labelfix/markshape_model_S4.json'))
    seen=set()
    for s in rd.slots:
        for b in s.get('evidence',I.MarkEvidence()).above:
            assert not seen & b.pixel_keys()
            seen.update(b.pixel_keys())
            assert all(ci.ink[y,x] and ci.labels[y,x] in b.source_ids for y,x in b.pixel_keys())

def test_blob_mask_serialization_is_lossless():
    lab=np.zeros((20,20),int);lab[2:8,3:5]=1;lab[6:8,3:9]=1
    ci=crop(lab);b=I._blob(lab==1,0,0,'attached',ci);r=b.to_record()
    pixels={(y+b.y0,x+b.x0) for y,a,z in r['pixel_runs'] for x in range(a,z)}
    assert pixels==b.pixel_keys() and len(pixels)==b.area

@pytest.mark.parametrize('module',['owner_pages_build','owner_pages_build_combined'])
def test_owner_page_same_serialized_reading_and_reference_parity(module,tmp_path):
    require_file('docs/records/labelfix/spellcheck/S6_lines.jsonl.gz')
    import importlib
    from greekocr.labelfix.ctc_align import Alignment
    from greekocr.labelfix.markshape import load_model
    m=importlib.import_module('scripts.labelfix.'+module)
    c=json.loads((ROOT/'tests/data/labelfix_s6/cases.json').read_text())[0]
    line=dict(model=c['recogniser_text'],line_id=c['line_id'],google='CHANGED',human='CHANGED')
    args=(ROOT/'tests/data/labelfix_s6'/f"{c['line_id']}.png",load_model(ROOT/'docs/records/labelfix/markshape_model_S4.json'),line,Alignment.from_record(c['alignment']))
    with pytest.raises(ValueError,match='configuration'):m.detect_s4(*args)
    from scripts.labelfix.owner_reading import load_configuration,policy,digest,SOURCES,DEFAULT_SHAPE
    import subprocess
    config_data=dict(schema='sf1-reading-v1',detector_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        source_sha256={p:digest(ROOT/p) for p in SOURCES},shape_model=dict(path=DEFAULT_SHAPE,sha256=digest(ROOT/DEFAULT_SHAPE)),
        case_model=dict(path='docs/records/labelfix/case_model_S5.json',sha256=digest(ROOT/'docs/records/labelfix/case_model_S5.json')),
        r1_checkpoint=None,constraint_policy=policy())
    path=tmp_path/'reading.json';path.write_text(json.dumps(config_data));config=load_configuration(path)
    first=m.detect_s4(*args,config=config)
    line.update(google='DIFFERENT',human='DIFFERENT',printed='NO INFERENCE')
    second=m.detect_s4(*args,config=config)
    assert first==second
    assert first[1]==first[3]['line_reading']['text']==first[3]['reading']
    from scripts.labelfix.clariden.r1_common import rows
    saved=next(r for r in rows(ROOT/'docs/records/labelfix/spellcheck/S6_lines.jsonl.gz') if r['line_id']==c['line_id'])
    assert first[3]['raw_line_reading']['text']==saved['reading']
    assert all(b['display_slot'] in {s['display_slot'] for s in first[3]['line_reading']['slots']} for b in first[3]['boxes'] if b['kind']!='quote')
    assert not hasattr(m,'ours_line') and not hasattr(m,'reconstructed')


def test_flagged_page_letter_dotted_and_keeps_mark():
    from scripts.labelfix.owner_reading import reading_html
    rec=dict(text='ε\u0342',slots=[dict(hold=True)])
    text=reading_html(rec)
    assert 'class="un"' in text and 'impossible by rule' in text and 'ε\u0342' in text


def test_missing_case_model_fails_closed(monkeypatch):
    monkeypatch.setattr(case,'model',lambda:None)
    lab=np.zeros((20,20),int);lab[4:15,5:10]=1
    c=_region(crop(lab),[SimpleNamespace(index=1)],5,10)
    with pytest.raises(FileNotFoundError,match='case_model'):case.classify(crop(lab),c)


def test_heuristic_mark_confidence_has_own_provenance():
    from greekocr.labelfix.markshape import name_marks
    class Rejected:
        def predict(self,features):return 'none',.99,{'none':.99}
    b=I.Blob(5,2,9,10,15,'attached',-60.,2.)
    ev=I.MarkEvidence(above=[b],xh=20.,body=(4,15))
    n=name_marks(ev,Rejected())
    assert n.parts==('acute',) and n.probability is None
    assert n.per_blob[0]['method']=='heuristic_unqualified' and n.per_blob[0]['probability'] is None
    assert n.per_blob[0]['rejected_model_probability']==.99


def test_baseline_name_hash_and_expected_totals_bound():
    require_file('docs/records/labelfix/spellcheck/S6_lines.jsonl.gz')
    from scripts.labelfix.clariden.r1_score import load_baselines
    root=ROOT/'docs/records/labelfix/spellcheck';manifest=json.loads((root/'SF1_baselines.json').read_text())
    with pytest.raises(ValueError,match='baseline hash mismatch'):
        load_baselines(['S5='+str(root/'S6_lines.jsonl.gz')],manifest)
    fake=deepcopy(manifest);fake['S4']['expected_totals']['tp']+=1
    with pytest.raises(ValueError,match='expected totals'):
        load_baselines(['S4='+str(root/'S4_lines.jsonl.gz')],fake)


def test_r1_support_cannot_borrow_s4_detector_pixels():
    from scripts.labelfix.clariden.r1_score import map_lines
    from greekocr.labelfix.reading import _mark_support
    line=dict(line_id='l',doc='d',dev=False,recogniser_text='α',slots=[dict(slot=1,base='α',truth=[],bbox=[0,0,10,20])],
        recogniser_slots=[dict(start=0,base='α',component_slot=1,locator_span=[0,10],
            evidence=dict(xh=10,body=[0,10],above=[dict(bbox=[0,0,5,5],area=25)]),naming=dict(probability=.99))])
    meta={'l':dict(recogniser_text='α',coverage_by_start={0:dict(fused=False)})}
    mapped,_=map_lines([line],meta,{('l',0):dict(cls='acute')},filtered=False)
    s=mapped[0]['recogniser_slots'][0];support=_mark_support(s,'acute')
    assert support['probability'] is None and support['blob_area'] is None and support['rank']==[0.,0.,0.]
    assert s['detector_evidence']['above'][0]['area']==25


def test_box_missing_lines_and_separate_slot_namespaces():
    from scripts.labelfix.box_regression import compare_pages
    old=dict(reading='a',boxes=[],letters=[[0,10]],letter_zones=[dict(display_slot=1,mark_zone=[0,0,10,10])])
    new=dict(reading='a',boxes=[dict(kind='above',bbox=[22,0,28,5])],letters=[[0,10],[20,30]],letter_zones=[dict(display_slot=1,mark_zone=[0,0,10,10]),dict(display_slot=2,mark_zone=[20,0,30,10])])
    d=diff_line(old,new,.3)
    assert d['added'][0]['new_slot']==2 and d['added'][0]['namespace']=='new'
    d=compare_pages({'lost':old},{'added':new},.3)
    assert d['lost']['line_status']=='missing_new' and d['added']['line_status']=='missing_old'


def test_implicit_missing_targets_and_no_neighbour_widening():
    from scripts.labelfix.owner_implicit_changes import compare
    old={'l':dict(reading='αβ',line_reading=dict(slots=[dict(display_slot=7,bbox=[1,2,3,4]),dict(display_slot=8,bbox=[4,2,6,4])]))}
    new={'l':dict(reading='αβ\u0301')}
    d=compare(old,new,[dict(line_id='l',note='mark at 7')])
    assert d[0]['old_slot']==8 and d[0]['kind'].startswith('REGRESSION')
    assert compare(old,{},[dict(line_id='l',note='')])[0]['kind']=='unresolved'


def test_r1_missing_target_and_unknown_approved_name_loss():
    from scripts.labelfix.clariden.r1_owner import clause
    old,new=note_pair()
    old['prediction_line_present']=new['prediction_line_present']=True
    assert not clause(dict(kind='mark',slots=[999],value=1),new,old)['fixed']
    assert clause(dict(kind='mark',slots=[999],value=1),new,old)['unresolved']=='missing target slot'
    assert not clause(dict(kind='no_regression',slots=[]),new,old)['fixed']


def test_historical_validators_explicit_raw_and_rendered_parts():
    import ast
    for name in ('s4_validate','s5_validate','s6_validate'):
        text=(ROOT/f'scripts/labelfix/{name}.py').read_text();tree=ast.parse(text)
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='read_ink']
        assert calls and all(any(k.arg=='filtered' and isinstance(k.value,ast.Constant) and k.value.value is False for k in c.keywords) for c in calls)
        assert 'mark_set(names.cls)' not in text

@pytest.mark.parametrize('module',['s4_validate','s5_validate','s6_validate'])
def test_historical_runtime_guard_prevents_overwrite(module):
    import importlib
    with pytest.raises(RuntimeError,match='Historical validator is pinned'):
        importlib.import_module('scripts.labelfix.'+module).main()


def test_per_column_zone_only_intersects_original_pixels():
    lab=np.zeros((20,20),int);lab[2:12,2:14]=1
    ci=crop(lab);b=I._blob(lab==1,0,0,'attached',ci)
    upper=np.arange(20)/2+3
    q=I.zone_blob(ci,b,upper=upper)
    assert q.pixel_keys()<=b.pixel_keys() and q.area<b.area
    assert all(y<int(np.floor(upper[x])) for y,x in q.pixel_keys())


def test_prediction_receipt_binds_extraction_index_and_checkpoint(tmp_path):
    from scripts.labelfix.clariden.r1_score import prediction_map,sha256
    extraction=tmp_path/'extraction';extraction.mkdir()
    (extraction/'index.npy').write_bytes(b'index')
    (extraction/'extraction_receipt.json').write_text(json.dumps(dict(sha256={'index.npy':sha256(extraction/'index.npy')})))
    checkpoint=tmp_path/'best.pt';checkpoint.write_bytes(b'checkpoint')
    p=tmp_path/'predictions.jsonl'
    p.write_text(json.dumps(dict(line_id='l',start=0,base='α',factors=[0,0,0,0],cls='none'))+'\n')
    receipt=dict(prediction_sha256=sha256(p),samples=1,extraction_receipt_sha256=sha256(extraction/'extraction_receipt.json'),input_index_sha256=sha256(extraction/'index.npy'),checkpoint_sha256=sha256(checkpoint))
    p.with_suffix('.receipt.json').write_text(json.dumps(receipt))
    meta={'l':dict(coverage_by_start={0:dict(base='α')},coverage=[dict(start=0,scored=True)])}
    assert prediction_map(p,meta,extraction=extraction,checkpoint=checkpoint)[('l',0)]['cls']=='none'
    checkpoint.write_bytes(b'other-checkpoint')
    with pytest.raises(ValueError,match='checkpoint_sha256 binding mismatch'):
        prediction_map(p,meta,extraction=extraction,checkpoint=checkpoint)


def test_box_owner_requires_full_two_dimensional_legal_zone():
    assert slot_of([1,50,3,60],[[0,10]]) is None
    zone=[dict(display_slot=7,mark_zone=[0,0,10,10])]
    assert slot_of([1,1,3,5],zone)==7
    assert slot_of([-1,1,3,5],zone) is None
    assert slot_of([1,1,3,5],zone+zone) is None


def test_combined_reader_flags_do_not_rank_with_detector_support():
    from greekocr.labelfix.reading import _mark_support
    s=dict(mark_support_source='reader',reader_evidence={},mark_probabilities={},
        evidence=dict(xh=10,body=[0,10],above=[dict(bbox=[1,1,5,5],area=100)]),naming=dict(probability=1.))
    support=_mark_support(s,'acute')
    assert support['probability'] is None and support['blob_area'] is None


def test_virtual_union_mark_shape_consumers_keep_every_parent():
    lab=np.zeros((35,30),int);lab[2:30,5:8]=1;lab[2:30,14:17]=2
    ci=crop(lab);c=_region(ci,[SimpleNamespace(index=1),SimpleNamespace(index=2)],5,17)
    blobs,_=I.vowel_marks(ci,c,12)
    assert len(blobs)==2 and {b.source_ids for b in blobs}=={(1,),(2,)}
    assert set().union(*(b.pixel_keys() for b in blobs))<={(y,x) for y,x in zip(*np.nonzero(lab))}


@pytest.mark.skip(reason="historical binding; green at opus/spellcheck@50b825a9e; see docs/cleanup_20261019/TEST_RECORDS.md")
def test_rescoring_receipt_and_current_note_sets_bound():
    from scripts.labelfix.clariden.r1_common import sha256
    root=ROOT/'docs/records/labelfix/spellcheck/clariden/R1_result_3678928'
    receipt=json.loads((root/'score_receipt.json').read_text())
    assert receipt['metrics_sha256']==sha256(root/'metrics.json')
    assert receipt['result_sha256']==sha256(root/'RESULT.md')
    assert {'baselines','extraction','predictions','scorer_sha256','constraint_policy','reader_support_sha256','checkpoints'}<=set(receipt)
    assert all(sha256(ROOT/p)==digest for p,digest in receipt['scorer_sha256'].items())
    m=json.loads((root/'metrics.json').read_text())
    for policy in ('raw','filtered'):
        data=m['policies'][policy]
        assert set(data['reference'])=={'S4','S5','S6'}
        counts=data['arms']['A']['owner_counts']
        assert counts['review_v16_49']['n']==49 and counts['examples_v10_57']['n']==57
        assert counts['examples_v10_57']['missing_prediction_lines']==1
    assert (root/'metrics_superseded.json').exists() and (root/'RESULT_superseded.md').exists()


def test_raw_r1_reading_flags_reach_label_slot():
    from scripts.labelfix.clariden.r1_score import map_lines
    line=dict(line_id='l',doc='d',dev=False,recogniser_text='ε',slots=[dict(slot=1,base='ε',truth=[],bbox=[0,0,10,20])],
        recogniser_slots=[dict(start=0,base='ε',component_slot=1,locator_span=[0,10])])
    meta={'l':dict(recogniser_text='ε',coverage_by_start={0:dict(fused=False)})}
    mapped,counts=map_lines([line],meta,{('l',0):dict(cls='circumflex')},filtered=False)
    assert mapped[0]['reading']=='ε\u0342' and not counts['removed_by_constraint']
    assert mapped[0]['slots'][0]['hold'] and mapped[0]['slots'][0]['label_status']=='HOLD'


def test_new_slot_numbers_never_alias_reviewed_old_notes():
    from scripts.labelfix.box_regression import review_scope
    old=dict(letter_zones=[dict(display_slot=9,mark_zone=[20,0,30,10])])
    change=dict(slot=7,new_slot=7,namespace='new',bbox=[22,1,28,5])
    assert review_scope(change,'added',old,{7},'reviewed with note')=='implicitly approved'
    assert change['reviewed_old_slot']==9
    assert review_scope(dict(change,bbox=[200,1,210,5]),'added',old,{7},'reviewed with note')=='unresolved reviewed owner'
