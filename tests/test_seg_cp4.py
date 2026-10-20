"""CP4 mechanics. Rectangles are body analogues, never semantic word truth."""
import json
from pathlib import Path
from tests._paths import run_record

import numpy as np
import pytest
from greekocr.harvest.neighbour_words import neighbour_word_evidence, row_word_evidence, WORD_PROXY
from greekocr.harvest.row_inclusion import supported_rows
from test_seg_cp3 import planted
from test_seg_cp2 import cached


def observe(p,box,target='own'):
    before=p['labels'].copy(); ink=p['ink'].copy()
    result=neighbour_word_evidence(p,box,target_row_id=target)
    assert np.array_equal(before,p['labels']) and np.array_equal(ink,p['ink'])
    assert result['decision_status']=='unqualified_cp4'
    return result


def short_page(n):
    p=planted([('own','c',5,125,55,0),('other','c',10,10+12*n,20,0)])
    r=p['rows'][1]
    p['labels'][np.isin(p['labels'],r['component_ids'])]=0
    for j,cid in enumerate(r['component_ids']): p['labels'][20:30,10+8*j:16+8*j]=cid
    p['ink'][:]=p['labels']>0
    raw={k:v for k,v in r.items() if not k.startswith('_')}
    p['rows'][1]=p['ownership'].prepare_row(raw,p['ink'],p['labels'])
    return p


@pytest.mark.parametrize('n',range(1,10))
def test_complete_short_body_runs(n):
    p=short_page(n)
    r=observe(p,[0,10,160,70])
    assert r['neighbour_drop'] is True and r['union_drop'] is True
    assert [g['body_count'] for row in r['rows'] for g in row['groups']]==[n]
    assert all(cid>0 for row in r['rows'] for g in row['groups'] for l in g['letters'] for cid in l['native_component_ids'])


@pytest.mark.parametrize('edge',['top','bottom'])
@pytest.mark.parametrize('fraction',[.5,.6])
def test_edge_halves_and_sixty_percent(edge,fraction):
    p=short_page(9)
    if edge=='top': box=[0,30-int(10*fraction),160,70]
    else:
        p=planted([('own','c',5,125,20,0),('other','c',10,118,55,0)])
        box=[0,10,160,55+int(10*fraction)]
    r=observe(p,box)
    assert r['neighbour_drop'] is False and r['union_drop'] is False


def test_clean_control_and_missing_neighbour():
    p=short_page(4)
    assert observe(p,[0,50,160,70])['neighbour_drop'] is False
    p=planted([('own','c',5,125,55,0)])
    r=observe(p,[0,50,160,70])
    assert r['status']=='unresolved' and r['union_drop'] is None


def test_separated_partial_word_cannot_become_complete_substring():
    p=short_page(4)
    # Mechanical gaps are .6 xh, hence four independent groups. Use smaller
    # within-word gaps below the existing .35 xh scale for a single group.
    labels=p['labels']
    r=p['rows'][1]
    # Put the same four native bodies at 2 px within-word gaps.
    labels[np.isin(labels,r['component_ids'])]=0
    for j,cid in enumerate(r['component_ids']): labels[20:30,10+8*j:16+8*j]=cid
    p['ink'][:]=labels>0
    raw={k:v for k,v in r.items() if not k.startswith('_')}
    p['rows'][1]=p['ownership'].prepare_row(raw,p['ink'],labels)
    m=observe(p,[12,10,160,70])
    assert m['neighbour_drop'] is False and m['union_drop'] is False
    assert not m['row_inclusion']['merged']
    assert m['rows'][0]['groups'][0]['body_count']==4


def test_sloping_local_complete_word():
    p=planted([('own','c',10,140,55,0),('other','c',10,140,20,.5)])
    r=observe(p,[0,10,160,65])
    assert r['neighbour_drop'] is True
    assert any(not g['complete'] for row in r['rows'] for g in row['groups'])


def test_cross_column_does_not_supply_neighbour():
    p=planted([('own','c0',5,65,55,0),('other','c1',90,145,20,0)])
    r=observe(p,[0,10,160,70])
    assert r['neighbour_drop'] is None and r['union_drop'] is None


def test_ambiguous_target_is_not_silently_picked():
    p=short_page(4)
    r=neighbour_word_evidence(p,[0,10,160,70])
    assert r['reason']=='ambiguous_target' and r['neighbour_drop'] is None and r['union_drop'] is True


def test_mixed_font_sizes_use_neighbour_height():
    p=short_page(4)
    p['rows'][0]['xheight']=30.
    # Row-local evidence independent of the target's font size.
    r=p['rows'][1]; support=supported_rows(p,[0,10,160,70])['rows'][1]
    m=row_word_evidence(p,r,[0,10,160,70],support)
    assert m['xheight']==10 and all(g['positive'] for g in m['groups'])
    assert all(l['body_height_xh']==1 for g in m['groups'] for l in g['letters'])


def test_joined_unresolved_letters_are_explicit():
    p=short_page(4); r=p['rows'][1]
    p['labels'][np.isin(p['labels'],r['component_ids'])]=0
    p['labels'][20:30,10:17]=r['component_ids'][0]
    p['labels'][20:30,24:31]=r['component_ids'][1]
    p['labels'][20:30,38:66]=r['component_ids'][2]
    p['ink'][:]=p['labels']>0
    raw={k:v for k,v in r.items() if not k.startswith('_')}
    p['rows'][1]=p['ownership'].prepare_row(raw,p['ink'],p['labels'])
    m=observe(p,[36,10,70,70])
    assert m['status']=='unresolved' and m['neighbour_drop'] is None
    assert any(not l['resolved'] for row in m['rows'] for g in row['groups'] for l in g['letters'])


@pytest.mark.parametrize('kind',['marks','noise','rule'])
def test_cc_inflation_never_supplies_bodies(kind):
    p=short_page(9); r=p['rows'][1]
    p['labels'][np.isin(p['labels'],r['component_ids'])]=0
    for j,cid in enumerate(r['component_ids']):
        if kind=='marks': p['labels'][17:19,10+12*j:13+12*j]=cid
        elif kind=='noise': p['labels'][24:25,10+12*j:11+12*j]=cid
        else: p['labels'][24:25,10:118]=r['component_ids'][0]
    p['ink'][:]=p['labels']>0
    raw={k:v for k,v in r.items() if not k.startswith('_')}
    p['rows'][1]=p['ownership'].prepare_row(raw,p['ink'],p['labels'])
    m=observe(p,[0,10,160,70])
    assert m['neighbour_drop'] is False and m['union_drop'] is False


def test_no_component_count_completeness_claim():
    assert WORD_PROXY['min_bodies']==1
    with pytest.raises(ValueError,match='invalid_word_proxy'):
        p=short_page(4); r=p['rows'][1]
        row_word_evidence(p,r,[0,10,160,70],{'excluded_component_ids':[]},
                          params=dict(WORD_PROXY,min_bodies=10))


def test_recorded_native_one_letter_words():
    # Real scan + existing recorded Google word geometry, not bars or a new
    # reader. First three unambiguous one-letter tokens in fixed page order.
    from greekocr.harvest.geometry_observations import load_cached_page, sha
    seg=Path(__file__).parents[1]/'docs/records/harvest/collect_v3_admission/seg'
    fixture=json.loads((seg/'CP4_one_letter_words.json').read_text())
    assert sha(fixture['source'])==fixture['source_sha256']
    assert sha(fixture['response'])==fixture['response_sha256']
    page=load_cached_page(fixture['source'],fixture['cache'],fixture['source_sha256'])
    results=[]
    for word in fixture['words']:
        r=next(r for r in page['rows'] if r['row_id']==word['geometry_row_id'])
        box=word['crop_box']; support=supported_rows(page,box)
        rs=next(s for s in support['rows'] if s['row_id']==r['row_id'])
        record={**{k:fixture[k] for k in ('source','source_sha256','response','response_sha256')},**word}
        observed=row_word_evidence(page,r,box,rs,recorded_word=record)
        assert observed==word['evidence']
        positive=any(g['positive'] for g in observed['groups'])
        unresolved=any(g['unresolved'] for g in observed['groups'])
        assert positive or unresolved  # never claim a verified absence
        results.append(positive)
    assert results==[True,True,True]


def test_separated_fragment_only_runs_do_not_accumulate():
    p=short_page(9);r=p['rows'][1]
    p['labels'][np.isin(p['labels'],r['component_ids'])]=0
    for j,cid in enumerate(r['component_ids']):
        p['labels'][23:27,10+12*j:16+12*j]=cid
    p['ink'][:]=p['labels']>0
    raw={k:v for k,v in r.items() if not k.startswith('_')}
    p['rows'][1]=p['ownership'].prepare_row(raw,p['ink'],p['labels'])
    m=observe(p,[0,10,160,70])
    assert m['neighbour_drop'] is not True and m['union_drop'] is not True


def test_resolved_joined_letters_keep_native_parent():
    p=short_page(4);r=p['rows'][1];ids=r['component_ids']
    p['labels'][np.isin(p['labels'],ids)]=0
    p['labels'][20:30,10:16]=ids[0]
    p['labels'][20:30,20:26]=ids[1]
    p['labels'][20:30,40:46]=ids[2]
    p['labels'][20:30,48:54]=ids[2]
    p['labels'][24:25,46:48]=ids[2]
    p['ink'][:]=p['labels']>0
    raw={k:v for k,v in r.items() if not k.startswith('_')}
    p['rows'][1]=p['ownership'].prepare_row(raw,p['ink'],p['labels'])
    m=observe(p,[38,10,56,70])
    letters=[l for row in m['rows'] for group in row['groups'] for l in group['letters']]
    assert m['neighbour_drop'] is True and m['union_drop'] is True
    assert len(letters)==2 and all(l['merged']>1 and l['resolved'] and l['native_component_ids']==[ids[2]] for l in letters)


@pytest.mark.parametrize('case',['head','scope'])
def test_commit_guard_rejects_changes(case,monkeypatch):
    import runpy
    guard=run_record(str(Path(__file__).parents[1]/'docs/records/harvest/collect_v3_admission/seg/guard_cp4_commit.py'))
    monkeypatch.setattr(guard['subprocess'],'check_output',lambda *a,**kw:'current\n')
    manifest=dict(base_HEAD='old' if case=='head' else 'current',files=[],read_only_dependencies=[])
    with pytest.raises(ValueError,match='base HEAD moved' if case=='head' else 'exact review scope'):
        guard['verify'](manifest)


def test_cached_foreign_measurement_preserves_core(cached):
    from greekocr.harvest import geometry_observations as g
    from greekocr.glyphs import foreign_ink
    from test_seg_cp2 import load
    page=load(cached);own=page['rows'][1]; others=[page['rows'][0],page['rows'][2]]
    box=[0,0,100,90]
    expected=foreign_ink._foreign_mask(page['ink'],foreign_ink._centre_fit(own),
        [foreign_ink._centre_fit(r) for r in others],tuple(box))
    before=page['ink'].copy(),page['labels'].copy()
    result=g.measure_foreign(page,own,others,box)
    assert np.array_equal(result['mask'],expected)
    assert np.array_equal(page['ink'],before[0]) and np.array_equal(page['labels'],before[1])


@pytest.mark.parametrize('outside_row',[False,True])
def test_connected_top_stroke_full_native_extent(outside_row):
    p=short_page(1);r=p['rows'][1];cid=r['component_ids'][0]
    end=26 if outside_row else 21
    p['labels'][16:20,10:end]=cid
    p['ink'][:]=p['labels']>0
    p['rows'][1]=p['ownership'].prepare_row(
        {k:v for k,v in r.items() if not k.startswith('_')},p['ink'],p['labels'])
    m=observe(p,[10,10,16,70])
    assert m['neighbour_drop'] is False and m['union_drop'] is False
    letter=m['rows'][0]['groups'][0]['letters'][0]
    assert letter['box']==[10,16,end,30]
    assert not letter['extent_complete'] and not letter['complete']


def test_shared_parent_split_conserves_full_native_ink():
    p=short_page(4);r=p['rows'][1];ids=r['component_ids']
    p['labels'][np.isin(p['labels'],ids)]=0
    for cid,x in zip(ids[:2],[10,20]):p['labels'][20:30,x:x+6]=cid
    p['labels'][20:30,40:46]=ids[2];p['labels'][20:30,48:54]=ids[2]
    p['labels'][24:25,46:48]=ids[2]
    p['labels'][17:20,51:58]=ids[2]
    p['ink'][:]=p['labels']>0
    p['rows'][1]=p['ownership'].prepare_row({k:v for k,v in r.items() if not k.startswith('_')},p['ink'],p['labels'])
    m=observe(p,[38,10,56,70])
    letters=[l for row in m['rows'] for g in row['groups'] for l in g['letters']]
    assert len(letters)==2 and all(l['shared_parent_split'] for l in letters)
    assert sum(l['assigned_native_pixels'] for l in letters)==int((p['labels']==ids[2]).sum())
    assert max(l['box'][2] for l in letters)==58
    assert m['union_drop'] is False


def test_recorded_word_cannot_override_binding_or_clipping():
    from greekocr.harvest.geometry_observations import load_cached_page
    seg=Path(__file__).parents[1]/'docs/records/harvest/collect_v3_admission/seg'
    f=json.loads((seg/'CP4_one_letter_words.json').read_text())
    p=load_cached_page(f['source'],f['cache'],f['source_sha256'])
    w=f['words'][0];row=next(r for r in p['rows'] if r['row_id']==w['geometry_row_id'])
    record={**{k:f[k] for k in ('source','source_sha256','response','response_sha256')},**w}
    support=dict(excluded_component_ids=[])
    with pytest.raises(ValueError,match='binding_mismatch'):
        row_word_evidence(p,row,w['crop_box'],support,recorded_word=dict(record,source_sha256='bad'))
    with pytest.raises(ValueError,match='geometry_mismatch'):
        row_word_evidence(p,row,w['crop_box'],support,recorded_word=dict(record,recorded_box=[0,0,1,1]))
    clipped=[960,97,976,142]
    m=row_word_evidence(p,row,clipped,support,recorded_word=record)
    assert not any(g['positive'] for g in m['groups'])


def test_fallback_claim_is_once_per_bound_source(tmp_path):
    import runpy
    script=Path(__file__).parents[1]/'docs/records/harvest/collect_v3_admission/seg/prepare_cp4_geometry.py'
    claim=run_record(str(script))['claim_attempt']
    m=dict(id='page-a',image=str(tmp_path/'source.png'),image_sha256='source-hash')
    assert claim(tmp_path,m,'detector',dict(frame=0))
    assert not claim(tmp_path,dict(m,id='alias'),'detector',dict(frame=0))
    with pytest.raises(ValueError,match='attempt_identity_changed'):
        claim(tmp_path,m,'changed-detector',{})
    # A changed source under an already claimed page ID also cannot overwrite.
    with pytest.raises(FileExistsError):
        claim(tmp_path,dict(m,image_sha256='changed-source'),'detector',{})
