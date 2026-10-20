"""Offline replacement isolation, cache binding, and no-read driver checks."""
import json
from pathlib import Path
import sys
from unittest.mock import patch

import pytest
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
import ru4ef1 as f
m=f.m


@pytest.fixture
def packs(tmp_path):
    f.n.configure()
    image=tmp_path/'native.png';Image.new('L',(20,10),123).save(image)
    source=tmp_path/'source.jsonl'
    m.jsonl(source,[dict(id='row',source='fixture',doc='book',label='конь домъ',crop=str(image))])
    books=tmp_path/'books.json';m.dump(books,dict(books={'fixture:book':{}}))
    masked,slots=m.mask('конь домъ')
    for s in slots:s.update(control_truth=s['google'])
    pool=[dict(control=True,row_id='control',source_id='control',book='fixture:control',
        slots=slots,masked_text=masked,image=str(image),source_crop_sha256=m.sha(image))]
    art,pack=tmp_path/'art',tmp_path/'packs'
    m.build({'test':source},books,art,pack,pool,selected_ids={'row'})
    return art,pack


def test_independent_r3_r4_fresh_ids_and_repeatable_routing(packs):
    art,pack=packs
    r3=f.replacement(art,pack,'ctx01','r1','r3')
    r4=f.replacement(art,pack,'ctx01','r2','r4')
    assert r3['logical_reader']=='r1' and r4['logical_reader']=='r2'
    assert r3['reader']=='r3' and r4['reader']=='r4'
    original={i['item_id'] for role in ('r1','r2') for i in m.rows(pack/'ctx01'/role/'items.jsonl')}
    fresh=[{i['item_id'] for i in m.rows(Path(r['pack'])/'ctx01'/r['reader']/'items.jsonl')} for r in (r3,r4)]
    assert not fresh[0]&fresh[1] and not original&set.union(*fresh)
    assert f.replacement(art,pack,'ctx01','r2','r4')==r4
    item=Path(r4['pack'])/'ctx01/r4/items.jsonl'
    item.write_text(item.read_text()+'\n')
    with pytest.raises(ValueError,match='binding changed'):
        f.replacement(art,pack,'ctx01','r2','r4')


def test_r4_closure_rejects_extra_pack_entry(packs):
    art,pack=packs;r=f.replacement(art,pack,'ctx01','r2','r4')
    rp,ra=Path(r['pack']),Path(r['art'])
    assert f.closure(rp,ra,runtime=True,replacement=True)[0]['ok']
    (rp/'ctx01/private.txt').write_text('extra')
    with pytest.raises(ValueError,match='closure'):
        f.closure(rp,ra,runtime=True,replacement=True)


def test_failed_collection_cache_invalidates_on_runtime_change(packs,tmp_path):
    art,pack=packs;roll=tmp_path/'rollout.jsonl';roll.write_text('{}\n')
    m.dump(art/'answers/ctx01.run.json',dict(rollout=str(roll)))
    with patch.object(f,'ORIGINAL_COLLECT',side_effect=ValueError('invalid scan')) as collect:
        task=(str(art),str(pack),'ctx01','r1')
        assert f.precollect(task)[1]['error']=='invalid scan'
        f.precollect(task);assert collect.call_count==1
        (pack/'ctx01/r1/answers.jsonl').write_text('{}\n')
        f.precollect(task);assert collect.call_count==2


def test_replacement_driver_dry_run_never_probes_or_reads(packs):
    art,pack=packs
    replacements=[f.replacement(art,pack,'ctx01','r1','r3'),f.replacement(art,pack,'ctx01','r2','r4')]
    m.jsonl(art/'r3_to_run.jsonl',replacements)
    with patch.object(f,'ART',art),patch.object(f,'PACK',pack),patch.object(m,'tasks',m.tasks),patch.object(m,'closure',m.closure),patch.object(m.subprocess,'check_output',side_effect=AssertionError('probe forbidden')),patch.object(m.subprocess,'run',side_effect=AssertionError('reader forbidden')):
        f.drive(True)
    assert not list(art.glob('**/*.attempt.json'))


def test_invalid_originals_route_and_later_admit_r3_and_r4(packs,tmp_path,monkeypatch):
    art,pack=packs
    class InlinePool:
        def __init__(self,**kwargs):pass
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def map(self,fn,tasks):return map(fn,tasks)
    for role in ('r1','r2'):
        rollout=tmp_path/(role+'.jsonl');rollout.write_text(json.dumps(dict(role=role)))
        m.dump(art/'answers'/(m.stem('ctx01',role)+'.run.json'),dict(rollout=str(rollout)))
    monkeypatch.setattr(f,'ART',art);monkeypatch.setattr(f,'PACK',pack)
    monkeypatch.setattr(f,'ProcessPoolExecutor',InlinePool)
    monkeypatch.setattr(f,'precollect',lambda t:(t[2]+'/'+t[3],dict(error='invalid canonical scan')))
    monkeypatch.setattr(f,'sheets',lambda ds,report:dict(path='fixture',audit_cells=30))
    for name in ('collect','closure','replacement'):monkeypatch.setattr(m,name,getattr(m,name))
    f.finalize(1)
    report=json.loads((art/'finalize.json').read_text())
    assert report['counts']=={'hold':1}
    assert [r['reader'] for r in report['replacements']]==['r3','r4']
    assert report['replacement_budget']['items']==4
    for repl in report['replacements']:
        a=Path(repl['art']);r=repl['reader']
        rollout=a/'rollout.jsonl';rollout.write_text(json.dumps(dict(role=r)))
        m.dump(a/'answers'/(m.stem('ctx01',r)+'.run.json'),dict(rollout=str(rollout)))
    position=m.rows(art/'candidate_positions.full.jsonl')[0]
    monkeypatch.setattr(f,'ORIGINAL_COLLECT',lambda *args:([dict(position,call='ъ',confidence='high',item_id='fixture')],dict(status='VALID'),{},{}))
    f.finalize(1)
    report=json.loads((art/'finalize.json').read_text())
    assert report['counts']=={'edit_hard':1}
    assert report['status']=='AWAITING_LEAD'
    assert report['contexts']['ctx01/r1/r3']['status']=='VALID'
    assert report['contexts']['ctx01/r2/r4']['status']=='VALID'
    assert not list(tmp_path.rglob('ru1_v3_test_edits.jsonl'))
