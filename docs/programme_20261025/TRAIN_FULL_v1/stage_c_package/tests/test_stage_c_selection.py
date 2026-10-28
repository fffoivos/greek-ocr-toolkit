"""Regression for Astra H1: observe the loader that actually drives best.pt."""
from pathlib import Path
from types import SimpleNamespace
import sys
import pytest
PKG=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PKG))
from common import atomic,bound,digest,read,spec
from test_package import mock_runtime


def distinct_runtime(tmp_path):
    from prepare import write_pool
    import run
    path=mock_runtime(tmp_path)
    rt=read(path)
    rows=run.load_pools(rt,{'seal04_dev'})['seal04_dev'][:3]
    # Legacy validation is 8 different line IDs; seal04 dev is 3.
    rt['pools']['seal04_dev']=write_pool(tmp_path/'distinct_seal04',rows)
    atomic(path,rt)
    return path


def test_stage_c_best_loader_provenance_and_all_reporting_panels(tmp_path,monkeypatch):
    import run
    import mock_worker
    import stage_c
    from train import train as trainer
    import s1_segment
    monkeypatch.setattr(s1_segment,'Segment',s1_segment.Segment)
    monkeypatch.setattr(run,'install',mock_worker.mock_install)
    path=distinct_runtime(tmp_path)
    config=stage_c.make_run(path,'w1-h13',fixture=True)
    config['parameters']['epochs']=8
    config.update(total_updates=32,target_drawn_lines=config['parameters']['epoch_rows']*8,cer_steps=[8,16,24,32])
    seen=[]
    import eval_cer
    def epoch_eval(model,loader,*args,**kwargs):
        ids=[r['line_id'] for r in loader.dataset.rows]
        assert ids==['seal04_dev0','seal04_dev1','seal04_dev2']
        assert all(r['split']=='val' for r in loader.dataset.rows)
        seen.append(ids)
        return dict(cer=len(seen)*.01,blank_rate=0.)
    monkeypatch.setattr(eval_cer,'evaluate',epoch_eval)
    for k in ('S1_DEADLINE_EPOCH','TF_C_STOP','S1_FORCE_SPLIT_EPOCH','S1_FORCE_SPLIT_STEP'):
        monkeypatch.delenv(k,raising=False)
    output=tmp_path/'full'
    assert stage_c.execute(config,output,fixture=True)==0
    import torch
    state=torch.load(output/'segment.pt',map_location='cpu',weights_only=False)
    assert len(seen)==8 and state['global_step']==32
    assert state['best']==dict(metric=.01,epoch=1) and state['bad_epochs']==7
    best=torch.load(output/'best.pt',map_location='cpu',weights_only=False)
    assert best['epoch']==1
    rt=read(path)
    assert state['receipt']['validation']==rt['pools']['seal04_dev']
    assert state['receipt']['epochs']['1']['val']['rows']==3
    selection=read(output/'SELECTION_POOL.json')
    assert selection['rows']==3 and selection['name']=='seal04_dev'
    assert len(list(output.glob('SELECTION_EVAL_*.json')))==8
    complete=stage_c.complete(output,config)
    for item in complete['evaluations']+complete['loss_evaluations']:
        assert set(read(bound(item))['instruments'])==set(stage_c.PANELS)
    assert (output/'last.pt').exists()


def test_same_stage_b_view_full_reporting_and_full_pass_enforcement(tmp_path,monkeypatch):
    import run
    from train import train as trainer
    import s1_segment
    monkeypatch.setattr(s1_segment,'Segment',s1_segment.Segment)
    path=distinct_runtime(tmp_path)
    b,rt=run.install(path,study=True)
    b_selection=b.full_selection.copy()
    b_rows=b.shared_validation(None,None)
    c,rt=run.install(path,selection_pool='seal04_dev')
    assert c.full_selection==b_selection and c.shared_validation(None,None)==b_rows
    assert {'seal04_test','harvest_test'}<=set(c.full_pools)
    # Exercise the actual provenance branch with production-mode full-pass policy.
    rt['mock']=False;rt['train_rows']=8
    mix=c.validate(path)
    real=c.full_pools['real'];syn=c.full_pools['synthetic']
    rows=[dict(r,_component=ci,_pool_index=i) for ci,pool in enumerate((real,syn)) for i,r in enumerate(pool)]
    args=SimpleNamespace(full_smoke=False)
    c.training_provenance(args,mix,{1:{'train':rows}})
    rows[0]=dict(rows[1])
    with pytest.raises(ValueError,match='exactly one pass'):
        c.training_provenance(args,mix,{1:{'train':rows}})
