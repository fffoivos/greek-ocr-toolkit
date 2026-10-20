"""K1 reading-only constraints: exceptions, evidence, abstention and receipts."""
from copy import deepcopy
import pytest
from greekocr.labelfix.reading import (LineReading, MARKS, apply_constraints,
    CONSTRAINT_RULES, APPLIED_CONSTRAINT_RULES)
from greekocr.labelfix.text import clusters,nfd


def reading(text,probabilities=None):
    inverse={v:k for k,v in MARKS.items()};slots=[]
    for c in clusters(nfd(text)):
        if not c.base.isalpha():continue
        i=len(slots)
        slots.append(dict(base=c.base,start=c.start,component_slot=i+1,
            parts=[inverse[m] for m in c.marks if m in inverse],
            naming=dict(probability=(probabilities or {}).get(i,.8)),
            evidence=dict(xh=10,body=[i*10,i*10+8],above=[dict(bbox=[i*10,0,i*10+5,5],area=15)],below=[])))
    return LineReading(text,slots,[])


def all_rules(text,**kw):return apply_constraints(reading(text,**kw),enabled_rules=None,output="normalised")


@pytest.mark.parametrize('before,after',[
    ('Ἐμπρ\u0342ός','Ἐμπρός'),('τρ\u0342ισκότειδο','τρισκότειδο'),
    ('πὄχεἵ','πὄχεί'),('πὄχει','πὄχει'),('βἳος','βιος'),
    ('βίος','βίος'),('αἶψα','αἶψα'),('αἲψα','αἰψα'),
    ('κἀγώ','κἀγώ'),('Τυῤῥηνῶν','Τυῤῥηνῶν'),
    ('ῥόδον','ῥόδον'),('ῤόδον','ρόδον'),('β\u0308','β'),
    ('ε\u0345','ε'),('ε\u0342','ε'),('ο\u0342','ο'),
    ('Α\u0308Β','Α\u0308Β'),('κἀγώ-Τυῤῥηνῶν','κἀγώ-Τυῤῥηνῶν'),
    ('ἄυλος','ἄυλος'),('οἶκος','οἶκος'),('λόγός μου','λόγός μου'),
    ('λόγός','λόγός'),
])
def test_letter_and_word_rules(before,after):
    r,removed=all_rules(before)
    assert nfd(r.text)==nfd(after)
    assert all({'rule','letter','slot','start','part','evidence'}<=set(x) for x in removed)


def test_filter_is_copy_and_retains_evidence():
    r=reading('Ἐμπρ\u0342ός');snapshot=deepcopy(r)
    result,removed=apply_constraints(r,enabled_rules=None,output="normalised")
    assert r==snapshot and removed
    for old,new in zip(r.slots,result.slots):
        assert old['evidence'] is new['evidence']
    assert result.removed_by_constraint==removed
    again,extra=apply_constraints(result,enabled_rules=None,output="normalised")
    assert again.text==result.text and not extra


def test_weak_accent_removed_and_alternative_recorded():
    r=reading('λόγός καλός',probabilities={1:.6,3:.95})
    after,removed=apply_constraints(r,enabled_rules=None,output="normalised")
    assert after.text=='λογός καλός'
    event=next(x for x in removed if x['rule']=='C3:two_accents')
    assert event['evidence']['probability']==.6
    assert len(event['alternatives'])==2


def test_tied_evidence_preserves_both_and_flags():
    r,removed=all_rules('λόγός καλός')
    assert r.text=='λόγός καλός' and not removed
    assert any(f['reason']=='evidence_tie' for f in r.constraint_flags)


def test_same_letter_fused_pair_uses_shared_support_and_abstains():
    r,removed=all_rules('α\u0313\u0314')
    assert not removed and len(r.slots[0]['parts'])==2
    assert r.constraint_flags[0]['rule']=='C2:two_breathings'


def test_per_blob_probability_resolves_same_letter_conflict():
    r=reading('α\u0313\u0314')
    r.slots[0]['evidence']['above'].append(dict(bbox=[6,0,9,5],area=10))
    r.slots[0]['naming']=dict(method='per_blob',per_blob=[
        dict(blob=0,parts=['psili'],probability=.6),dict(blob=1,parts=['dasia'],probability=.9)])
    after,removed=apply_constraints(r,enabled_rules=None,output="normalised")
    assert after.text=='ἁ' and removed[0]['part']=='psili'


def test_held_rule_is_flagged_without_deletion():
    r,removed=apply_constraints(reading('β\u0301'),enabled_rules=set())
    assert nfd(r.text)==nfd('β\u0301') and not removed
    assert any(f['reason']=='rule_held_back' for f in r.constraint_flags)


def test_default_policy_contains_only_qualified_rules():
    assert APPLIED_CONSTRAINT_RULES<=CONSTRAINT_RULES
    r,removed=apply_constraints(reading('ρ\u0342'),output='normalised')
    assert r.text=='ρ' and len(removed)==1


def test_punctuation_quote_apostrophe_and_original_slot_offsets_preserved():
    r,removed=all_rules('“β\u0301ίος,” δ’')
    assert r.text=='“βίος,” δ’'
    assert removed[0]['start']==1


def test_filter_selection_on_public_reader(monkeypatch):
    from greekocr.labelfix import reading as module
    def raw(*args,filtered=True,output="print"):
        r=reading('ρ\u0342')
        return apply_constraints(r,output=output)[0] if filtered else r
    monkeypatch.setattr(module,'read_ink',raw)
    from PIL import Image
    crop=Image.new('L',(20,20),255)
    monkeypatch.setattr(module.I,'analyse',lambda x:x)
    assert module.read_line(crop,'ρ',None,None,output='normalised')=='ρ'
    assert nfd(module.read_line(crop,'ρ',None,None))==nfd('ρ\u0342')
    assert nfd(module.read_line(crop,'ρ',None,None,filtered=False))==nfd('ρ\u0342')


def test_default_keeps_conflicting_print_rules_visible_as_flags():
    r,removed=apply_constraints(reading('πὄχεἵ πνίξει'))
    assert r.text=='πὄχεἵ πνίξει' and not removed
    assert {f['rule'] for f in r.constraint_flags} >= {
        'C1:breathing_after_consonant_start','C3:two_accents'}


def test_single_invalid_accent_records_keep_alternative():
    r,removed=all_rules('αἲψα')
    assert r.text=='αἰψα'
    assert removed[0]['alternative']['action']=='keep_mark'
    assert removed[0]['alternative']['part']=='grave'


@pytest.mark.parametrize('field,first,second',[
    ('blob_area',10,20),('distance_to_letter',5,1),
])
def test_secondary_evidence_order(field,first,second):
    r=reading('λόγός καλός')
    # Both accents have exactly the same classifier probability.
    for index,value in [(1,first),(3,second)]:
        ev=r.slots[index]['evidence']
        if field=='blob_area':ev['above'][0]['area']=value
        else:
            center=sum(ev['body'])/2
            ev['above'][0]['bbox']=[center+value-2.5,0,center+value+2.5,5]
    after,removed=apply_constraints(r,enabled_rules=None,output="normalised")
    assert after.text=='λογός καλός'
    assert removed[0]['evidence'][field]==first


def test_r1_reporting_filters_before_frozen_slot_scoring():
    from scripts.labelfix.clariden.r1_score import map_lines
    line=dict(line_id='l',doc='d',dev=False,recogniser_text='ρα',slots=[
        dict(slot=1,base='ρ',truth=[],bbox=[0,0,10,20]),
        dict(slot=2,base='α',truth=[],bbox=[10,0,20,20])],
        recogniser_slots=[dict(start=0,base='ρ',component_slot=1,locator_span=[0,10],
                              naming=dict(probability=.99)),
                          dict(start=1,base='α',component_slot=2,locator_span=[10,20])])
    original=deepcopy(line)
    meta={'l':dict(recogniser_text='ρα',coverage_by_start={0:dict(fused=False),1:dict(fused=False)})}
    pred={('l',0):dict(cls='circumflex')}
    mapped,counts=map_lines([line],meta,pred)
    assert mapped[0]['reading']=='ρα'
    assert mapped[0]['slots'][0]['detected']==[]
    assert counts['removed_by_constraint']==1
    assert mapped[0]['removed_by_constraint'][0]['evidence']['probability'] is None
    assert line==original
    raw,counts=map_lines([line],meta,pred,filtered=False)
    assert nfd(raw[0]['reading'])==nfd('ρ\u0342α')
    assert raw[0]['slots'][0]['detected']==[('accent','circumflex')]
    assert counts['removed_by_constraint']==0


def test_letter_mismatch_cannot_silently_reassign_a_mark():
    r=reading('α');r.slots[0]['base']='β'
    with pytest.raises(ValueError,match='letters and evidence slots differ'):
        apply_constraints(r)
