"""Statistical pairing and selective readback regressions."""
import json
import numpy as np
import pytest
from scripts.labelfix.r2_readback_verify import verify, sha
from scripts.labelfix.r2a_digest import pool, counts_by_doc, holm, paired_slots


def slot(pred,ident='s',unknown=None):
    return dict(id=ident,line_id='line',doc='document',truth=[0,1,0,0],prediction=pred,
                unknown=unknown or [],inclusion_weight=1.,base='α')


def test_pool_keeps_seed_observations_and_shared_document_cluster():
    data={a:{'heldout':[slot([0,1,0,0])]} for a in ['a','b','c']}
    pooled=pool('heldout',['a','b','c'],data)
    assert len({r['id'] for r in pooled})==3
    v=counts_by_doc(pooled,pooled,1,1)
    assert v.shape==(1,6) and v.tolist()==[[3,0,0,3,0,0]]


def test_exact_name_substitution_is_fp_and_fn_and_unknown_is_excluded():
    a=[slot([0,1,0,0]),slot([0,1,0,0],'unknown',['accent'])]
    b=[slot([0,3,0,0]),slot([0,3,0,0],'unknown',['accent'])]
    assert counts_by_doc(a,b,1,1).tolist()==[[1,0,0,0,0,1]]
    assert counts_by_doc(a,b,1,3).tolist()==[[0,0,0,0,1,0]]
    changed=paired_slots(a,b)
    assert changed[0]['head_regressions']==['accent']
    assert changed[1]['head_regressions']==[]


def test_holm_stops_after_failed_step_and_uses_simultaneous_failure_bound():
    def t(p,delta=0):return dict(p_noninfer=p,delta_pp=delta,margin_pp=-.2,_errors=np.array([-.1,0,.1]),ci95_pp=[delta-.1,delta+.1])
    tests=holm([t(.001),t(.03),t(.04)])
    assert [t['verdict'] for t in tests]==['PASS','INCONCLUSIVE','INCONCLUSIVE']
    assert holm([t(.9,-1)])[0]['verdict']=='FAIL'


def test_selective_readback_records_excluded_arrays_but_requires_selected(tmp_path):
    root=tmp_path/'out';root.mkdir()
    p=root/'score.json';p.write_text('{}')
    stage=root/'stage_D.json';stage.write_text(json.dumps(dict(complete=True,sha256={'score.json':sha(p),'B/shard.npy':'not-pulled'})))
    env=tmp_path/'envelope';env.write_text(f'{sha(stage)}  stage_D.json\n')
    r=verify(root,env,'start',selection=['score.json','stage_D.json'])
    assert r['sha256_verified']==2 and r['intentionally_not_pulled']==['B/shard.npy']
    with pytest.raises(ValueError,match='VERIFICATION FAILED'):
        verify(root,env,'start',selection=['score.json','stage_D.json','absent.log'])


def test_done_hash_conflicts_fail_closed(tmp_path):
    root=tmp_path/'out';seed=root/'C/20261016';seed.mkdir(parents=True)
    (seed/'DONE').write_text(json.dumps(dict(best_sha256='one',predictions_sha256='two')))
    (root/'stage_C.json').write_text(json.dumps(dict(complete=True,sha256={'C/20261016/best.pt':'different'})))
    with pytest.raises(ValueError,match='conflicting receipt hashes'):
        verify(root,tmp_path/'unused','start')
