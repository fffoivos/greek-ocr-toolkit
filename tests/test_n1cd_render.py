"""N1-Cd builder integration under the prescribed x86 image interpreter."""
import json
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/numerics'))
from n1_build_packs import build
from greekocr.numerics.locks import Locks
from test_n1_packs_render import fixture


def test_seven_contexts_seeded_class_rotation_and_raised_reuse(tmp_path):
    _,_,base=fixture(tmp_path)
    records={f's{i}':dict(base['s0'],slot_id=f's{i}',line_id=f'line{i}') for i in range(578)}
    bed=[dict(slot_id=f's{i}') for i in range(558)]
    classes=['raised dot','comma','baseline dot','hyphen or dash','nothing']
    controls=[dict(slot_id=f's{i}',truth=classes[(i-558)//4]) for i in range(558,578)]
    locks=Locks(frozenset(),frozenset(),frozenset())
    from collections import Counter
    keys=[]
    for run in ('a','b'):
        result=build(bed,controls,records,tmp_path/run/'packs',tmp_path/run/'private',locks)
        assert len(result)==7 and all(r['controls']==9 and r['items']<=100 for r in result)
        keys.append([json.loads((tmp_path/run/'private/keys'/f'ctx{i:02}.json').read_text()) for i in range(1,8)])
        for i in range(1,8):
            assert (tmp_path/'a/packs'/f'ctx{i:02}/r1/items.jsonl').read_bytes()==(tmp_path/run/'packs'/f'ctx{i:02}/r1/items.jsonl').read_bytes()
    assert keys[0]==keys[1]
    seen=[]; raised=[]; truth_counts=Counter()
    for key in keys[0]:
        items=list(key['items'].values()); assert len({r['slot_id'] for r in items})==len(items)
        seen.extend(r['slot_id'] for r in items if r['control_truth'] is None)
        cc=[r for r in items if r['control_truth'] is not None]
        truth_counts.update(r['control_truth'] for r in cc)
        rr=[r['slot_id'] for r in cc if r['control_truth']=='raised dot']; assert len(rr)==1
        raised.extend(rr)
    assert len(seen)==len(set(seen))==558
    assert sorted(Counter(raised).values())==[1,2,2,2]
    assert set(truth_counts[c] for c in classes[1:])=={14}


def test_bed_refuses_without_raised_control(tmp_path):
    _,_,records=fixture(tmp_path)
    with pytest.raises(ValueError,match='raised-dot'):
        build([dict(slot_id='s0')],[dict(slot_id='s30',truth='comma'),dict(slot_id='s31',truth='comma')],records,
              tmp_path/'packs',tmp_path/'private',Locks(frozenset(),frozenset(),frozenset()),require_raised=True)
