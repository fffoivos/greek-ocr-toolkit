import pytest
from scripts.labelfix.r2_finalize_manifest import quarantine, unique, diversity, modification, leakage_check, unique_alignment

def row(i, doc='d', **kw):
    return dict(slot_id=['a'*64,i],targets=[0,1,0,0],unknown=[],doc=doc,page=str(i),card_id=str(i),slice='capitals',**kw)

def test_unknown_quarantines_whole_tuple():
    r=row(0);r['targets'][1]=None;r['unknown']=['accent']
    assert quarantine(r)
    assert not quarantine(row(1))

def test_duplicate_key_once_and_conflicting_tuple_stops():
    assert len(unique([row(0),row(0)]))==1
    r=row(0);r['targets'][1]=2
    with pytest.raises(ValueError,match='conflicting'): unique([row(0),r])

def test_document_cap_uses_retained_slice_denominator():
    rows=[row(i,'dominant') for i in range(50)] + [row(100+j*10+i,str(j)) for j in range(10) for i in range(5)]
    kept,excluded=diversity(rows)
    from collections import Counter
    assert kept and excluded
    assert max(Counter(r['doc'] for r in kept).values()) <= len(kept)/10
    assert len(kept)+len(excluded)==len(rows)
    assert diversity(rows[::-1])==diversity(rows)

def test_page_cap():
    rows=[dict(row(i,str(i%10)),page='same') for i in range(100)]
    kept,excluded=diversity(rows)
    assert len(kept)==50
    assert len(excluded)==50

def test_replacement_not_append():
    r=modification(row(0,pool='native'),{('a'*64,0)})
    assert r['replaces']==r['slot_id'] and 'pool' not in r
    assert 'replaces' not in modification(row(1),{('a'*64,0)})

def test_leakage_stop():
    roles={'d':{'role':'supervision'},'v':{'role':'validation'}}
    assert leakage_check([row(0)],roles,set())==0
    with pytest.raises(ValueError,match='STOP'): leakage_check([row(0,'v')],roles,set())
    with pytest.raises(ValueError,match='STOP'): leakage_check([row(0)],roles,{'d'})

def test_nfd_alignment_preserves_case_and_rejects_ambiguous_repeats():
    assert unique_alignment('αβγ','αβγ')=={0:0,1:1,2:2}
    assert unique_alignment('αα','α')=={}
    assert unique_alignment('Α','α')=={}

def test_slice_membership_uses_printed_base():
    from scripts.labelfix.r2_finalize_manifest import slice_compatible
    assert slice_compatible('capitals','Α')
    assert not slice_compatible('capitals','α')
    assert slice_compatible('subscript','η')
    assert not slice_compatible('subscript','ε')

def test_no_majority_remains_unresolved_and_unknown_is_preserved():
    from scripts.labelfix.r2_cards_resolve import resolve_card, HEADS
    key=dict(card_id='x',slice='capitals',crop_sha256='a'*64,word_index=0,anchor_index=0,target_head='breathing')
    def vote(form, breathing):
        return dict(form=form,ownership_ok=True,readability='readable',anchor_index=0,heads={0:dict(breathing=breathing,accent='none',diaeresis='none',subscript='none')})
    assert resolve_card(key,[vote('Α','none'),vote('Ἀ','psili'),vote('Ἁ','dasia')])['status']=='unresolved'
    r=resolve_card(key,[vote('Α','unknown'),vote('Α','unknown'),vote('Ἀ','psili')])
    assert r['status']=='unresolved'
    assert r['letter_heads'][0]['breathing']=='unknown'
