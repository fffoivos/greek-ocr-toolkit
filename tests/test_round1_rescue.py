"""T18 allocation/accepted-union contracts; all tests use the offline fixture."""
import copy
import json
import math
from pathlib import Path
from greekocr.ops.data_root import input_path as _data_input
from tests._paths import require_file

import pytest

from greekocr.harvest.round1 import positions, replacement_candidates
from greekocr.harvest.round1_rescue import rescue_selection, combined_manifest, look_relative


def inputs(decades=(1860, 1870, 1890, 1900, 1910, 1920)):
    books = [dict(book=f'book-{d}', key=f'{d}abcdef', year=d+2, decade=d,
                  pages=200, pilot_pages=[100, 101], decision='OUT_TYPE',
                  title='Ιστορία / βιβλίο', allocation=0, positions=[]) for d in decades]
    selection = dict(books=books, seed=20261014, quality_limits={'ink_min': .01},
                     pilot_gate_sha256='sha', pilot_gate_commit='gate', stack_commit='stack')
    rescues = dict(rescued=[{k: b[k] for k in ('key', 'year', 'decade')} for b in books],
                   stay_out=[], pending_owner_look_1880s=[], owner_decision='owner approved')
    return selection, rescues


@pytest.mark.parametrize('decade,expected', [(1860,16),(1870,16),(1880,13),(1890,13),
                                           (1900,13),(1910,13),(1920,13),(1930,13)])
def test_rescue_allocation_is_explicit_not_decade_rebalanced(decade, expected):
    selection, rescues = inputs((decade,))
    result = rescue_selection(selection, rescues)
    assert result['books'][0]['allocation'] == expected
    assert result['books'][0]['decision'] == 'RESCUED'
    assert result['books'][0]['prior_decision'] == 'OUT_TYPE'
    assert selection['books'][0]['allocation'] == 0


def test_rescue_positions_exactly_reuse_t16_and_bound_replacements():
    selection, rescues = inputs()
    result = rescue_selection(selection, rescues)
    for b in result['books']:
        pp = positions(b['pages'], b['allocation'], b['pilot_pages'], book=b['book'], seed=selection['seed'])
        assert [{k:v for k,v in p.items() if k!='candidates'} for p in b['positions']] == pp
        values = [p['page'] for p in b['positions']]
        assert not set(values) & set(b['pilot_pages'])
        assert min(values) >= math.ceil(.08*b['pages'])
        assert max(values) <= math.floor(.95*b['pages'])
        for p in b['positions']:
            assert p['candidates'] == replacement_candidates(p['page'], b['pages'], b['pilot_pages'],
                                                             [v for v in values if v!=p['page']])
            assert len(p['candidates']) <= 3
            assert all(p['page'] <= v <= p['page']+2 for v in p['candidates'])


@pytest.mark.parametrize('group', ['stay_out', 'pending_owner_look_1880s'])
def test_excluded_owner_groups_are_never_allocated(group):
    selection, rescues = inputs()
    rescues[group] = [rescues['rescued'].pop()]
    result = rescue_selection(selection, rescues)
    assert rescues[group][0]['key'] not in {b['key'] for b in result['books']}
    rescues['rescued'].append(rescues[group][0])
    with pytest.raises(ValueError, match='excluded'):
        rescue_selection(selection, rescues)


def test_duplicate_unknown_scan_and_changed_metadata_fail_closed():
    selection, rescues = inputs((1860,))
    duplicate = copy.deepcopy(rescues); duplicate['rescued'] *= 2
    with pytest.raises(ValueError, match='duplicate'): rescue_selection(selection, duplicate)
    unknown = copy.deepcopy(rescues); unknown['rescued'][0]['key'] = 'unknown'
    with pytest.raises(KeyError): rescue_selection(selection, unknown)
    changed = copy.deepcopy(rescues); changed['rescued'][0]['year'] += 1
    with pytest.raises(ValueError, match='metadata'): rescue_selection(selection, changed)
    selection['books'][0]['decision'] = 'OUT_SCAN'
    with pytest.raises(ValueError, match='strange-type'): rescue_selection(selection, rescues)


def page(book, number, accepted=True, gate=True):
    return dict(book=book, page=number, selected=True, harvest_accepted=accepted,
                gate=dict(accepted=gate), pdf_sha256=f'{book}-{number}', replacement=False,
                replacement_chain=[dict(page=number, state='accepted' if accepted else 'rejected')])


def test_combined_manifest_is_one_accepted_list_preserving_source_rows():
    t16 = dict(pages=[page('old',1),page('old',2,False),page('old',3,False,False)])
    rescue = dict(pages=[page('rescued',4),page('rescued',5,False,False)])
    before = copy.deepcopy((t16,rescue))
    result = combined_manifest(t16,rescue)
    assert isinstance(result,list) and len(result)==2
    assert result == [dict(t16['pages'][0],origin='t16'), dict(rescue['pages'][0],origin='rescue')]
    assert (t16,rescue)==before
    result[0]['gate']['accepted']=False
    assert t16['pages'][0]['gate']['accepted']  # no aliasing


@pytest.mark.parametrize('field', ['gate', 'selected'])
def test_combined_refuses_inconsistent_accepted_flags(field):
    p = page('book',1)
    if field=='gate': p['gate']['accepted']=False
    else: p['selected']=False
    with pytest.raises(ValueError,match='physical gate or selection'):
        combined_manifest(dict(pages=[p]),dict(pages=[]))


def test_combined_refuses_duplicates_even_across_origins():
    p=page('book',1)
    with pytest.raises(ValueError,match='duplicate'):
        combined_manifest(dict(pages=[p]),dict(pages=[p]))
    with pytest.raises(ValueError,match='duplicate'):
        combined_manifest(dict(pages=[p,p]),dict(pages=[]))


def test_rescue_finder_names_are_safe_bounded_and_mark_replacements():
    b=dict(year=1873,decade=1870,key='abcdef123456',title='  ../Λόγος / περί: "γλώσσης"  '*5)
    p=dict(page=43,replacement=True)
    relative=Path(look_relative(b,p))
    assert relative.parts[:2]==('accepted','1870s')
    assert relative.parts[2].startswith('RESCUED_1873_')
    assert relative.parts[2].endswith('_abcdef')
    assert relative.name=='p0043_REPL.png'
    assert len(relative.parts[2])<=len('RESCUED_1873_')+40+len('_abcdef')
    assert '..' not in relative.parts
    p['replacement']=False
    assert Path(look_relative(b,p)).name=='p0043.png'


def test_rescue_names_preserve_original_finder_punctuation():
    b=dict(year=1867,decade=1860,key='96bb71abcdef',
           title='Ο Λύχνος επί την λυχνία /  [Εις των μη διδακτόρων Καθηγητών].')
    assert Path(look_relative(b,dict(page=24,replacement=False))).parent.name == (
        'RESCUED_1867_Ο Λύχνος επί την λυχνία [Εις των μη διδα_96bb71')


def test_live_owner_input_is_exactly_51_books_693_slots_and_no_pending():
    require_file('docs/records/harvest/round1/selection.json')
    base=Path(__file__).resolve().parents[1]/'docs/records/harvest/round1'
    selection=json.loads((_data_input(base/'selection.json')).read_text())
    rescues=json.loads((_data_input(base/'rescues.json')).read_text())
    result=rescue_selection(selection,rescues)
    assert len(result['books'])==51
    assert sum(b['allocation'] for b in result['books'])==693
    assert sum(b['allocation']==16 for b in result['books'])==10
    assert all(b['decade']!=1880 for b in result['books'])
    assert result['quality_limits']==selection['quality_limits']
    assert result['pilot_gate_sha256']==selection['pilot_gate_sha256']
