"""R2 recipe identity, union denominators, overlays, exports and continuity."""
import importlib.util
import json
from pathlib import Path
from tests._paths import require_file
import numpy as np
import pytest
import torch
from scripts.labelfix.clariden import r1_train as train
from scripts.labelfix.clariden.r1_common import HEADS, SEED, rows, sha256, write_rows, write_json
from scripts.labelfix.clariden.r2_manifest import ManifestPool, inventory_ids
from scripts.labelfix.clariden.r2_mock import prepare
from scripts.labelfix.clariden.r2_teacher import full_predictions
from scripts.labelfix.r2_score import score, apply_overlay, paired, truth_lines, continuity

FIX=Path('tests/labelfix/fixtures/r2')


def legacy(filename='r1_train_job_3678928.py'):
    spec=importlib.util.spec_from_file_location('r1_3678928',FIX/filename);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod


@pytest.fixture
def mock_pool(tmp_path):
    # Fixture preparation uses paths only for hashing, never loads these models.
    cfg=prepare(tmp_path/'inputs',FIX/'r1_train_3678928.py',FIX/'r1_train_3678928.py')
    return cfg


def test_seed_default_identity_first_200_batches_and_initial_weights():
    old=legacy();y=np.tile([[0,0,0,0],[1,1,0,0],[2,3,0,1],[0,1,1,0]],(800,1))
    aa=list(old.ArmBatches(y,16,'A',SEED+1));bb=list(train.ArmBatches(y,16,'A',SEED+1))
    assert len(aa)==200 and aa==bb
    torch.manual_seed(SEED);a=old.MarkReader(True).state_dict()
    torch.manual_seed(SEED);b=train.MarkReader(True).state_dict()
    assert all(torch.equal(a[k],b[k]) for k in a)
    assert list(legacy('r1_train_3678928.py').ArmBatches(y,16,'A',SEED+1))==aa
    assert list(train.ArmBatches(y,16,'A',SEED+2))!=aa


def test_old_manifest_exact_dataset_sampler_loss_and_training(mock_pool,tmp_path):
    cfg=mock_pool;old=legacy();ds=train.Shards(cfg['data'],'A','train')
    path=Path(cfg['data']).parent/'old_only.jsonl';pool=ManifestPool(ds,path,cfg['inventory'])
    assert pool.identity and np.array_equal(ds.index,pool.index)
    for i in range(len(ds)):
        assert all(np.array_equal(a,b) for a,b in zip(ds[i],pool[i]))
    common=dict(data=cfg['data'],heldout=cfg['heldout'],arm='A',device='cpu',epochs=15,batch_size=16,workers=0,steps=2,threads=2)
    old.train(out=tmp_path/'legacy',**common)
    train.train(out=tmp_path/'default',**common)
    train.train(out=tmp_path/'manifest',manifest=path,inventory=cfg['inventory'],**common)
    checkpoints=[torch.load(tmp_path/p/'best.pt',weights_only=True)['model'] for p in ('legacy','default','manifest')]
    assert all(torch.equal(checkpoints[0][k],c[k]) for c in checkpoints[1:] for k in checkpoints[0])
    logs=[(tmp_path/p/'train_log.csv').read_text().splitlines()[1].split(',')[2:6] for p in ('legacy','default','manifest')]
    assert logs[0]==logs[1]==logs[2]


def test_manifest_replacement_removal_quarantine_duplicate(mock_pool,tmp_path):
    cfg=mock_pool;ds=train.Shards(cfg['data'],'A','train');p=Path(cfg['manifest']);r=list(rows(p))[0]
    pool=ManifestPool(ds,p,cfg['inventory'])
    assert len(pool)==len(ds) and list(pool.index[0]['target'])==[0,1,0,0]
    write_rows(tmp_path/'dupe.jsonl',[r,r])
    with pytest.raises(ValueError,match='more than once'): ManifestPool(ds,tmp_path/'dupe.jsonl',cfg['inventory'])
    write_rows(tmp_path/'remove.jsonl',[dict(slot_id=r['slot_id'],removes=r['slot_id'])])
    assert len(ManifestPool(ds,tmp_path/'remove.jsonl',cfg['inventory']))==len(ds)-1
    write_rows(tmp_path/'unknown.jsonl',[dict(r,unknown=['breathing'],targets=[None,1,0,0])])
    q=ManifestPool(ds,tmp_path/'unknown.jsonl',cfg['inventory']);assert len(q)==len(ds)-1 and len(q.quarantined)==1
    write_rows(tmp_path/'badweight.jsonl',[dict(r,loss_weight=.5)])
    with pytest.raises(ValueError,match='weight mismatch'): ManifestPool(ds,tmp_path/'badweight.jsonl',cfg['inventory'])


def test_teacher_full_softmax_fields(mock_pool):
    ds=train.Shards(mock_pool['data'],'A');s=ds.index[0];sample=(0,0,0,int(s['start']),int(s['letter']),0,s['target'],s['mask'])
    torch.manual_seed(SEED);m=train.MarkReader(True).eval()
    result=full_predictions(m,[sample],[ds[0][0]],'cpu')[0]
    assert set(result['heads'])==set(HEADS)
    for name,choices in HEADS.items():
        h=result['heads'][name];assert set(h['probabilities'])==set(choices)
        assert sum(h['probabilities'].values())==pytest.approx(1)
        pp=sorted(h['probabilities'].values());assert h['margin']==pytest.approx(pp[-1]-pp[-2])


def line(slots):return dict(line_id='l',doc='d',source='s',print_slots=slots)
def slot(base,y,id='l:s1'):return dict(id=id,base=base,targets=y,unknown=[])
def pred(base,y,start=0):return dict(line_id='l',base=base,factors=y,start=start)


def test_union_missing_print_positive_and_inserted_prediction():
    lines=[line([slot('α',[0,1,0,0])])]
    s,r=score(lines,[pred('ε',[1,0,0,0])]);a=s['micro']['atomic']
    assert a['fn']==1 and a['fp']==0 and a['tp']==0
    assert len(r)==2
    assert s['micro']['heads']['accent']['values']['acute']['positive_opportunities']==1
    assert s['micro']['heads']['breathing']['values']['psili']['false_additions_per_1000_negative']==0
    assert s['micro']['composed_tuple']['all_denominator']==1
    assert r[1]['truth']==[None]*4 and r[1]['unknown']==list(HEADS)


def test_case_preserving_and_mark_blind_names():
    s,_=score([line([slot('Α',[0,1,0,0])])],[pred('α',[0,1,0,0])])
    assert s['micro']['atomic']['fn']==1 and s['micro']['atomic']['fp']==0
    s,_=score([line([slot('α',[0,3,0,0])])],[pred('α',[0,1,0,0])])
    assert s['micro']['heads']['accent']['confusion']['circumflex']['acute']==1


def test_inserted_marked_slot_is_unknown_diagnostic_only():
    ll=[line([slot('α',[0,1,0,0])])]
    pp=[pred('α',[0,1,0,0])]
    before,old=score(ll,pp)
    after,new=score(ll,pp+[pred('ε',[1,2,1,1],1)])
    a=after['micro'];b=before['micro']
    assert a['atomic']==b['atomic'] and a['atomic']['precision']==a['atomic']['recall']==1
    assert a['composed_tuple']==b['composed_tuple']
    assert a['dialytika_compound_confusion']==b['dialytika_compound_confusion']
    assert a['inserted_slots']==1
    counts=dict(total=1,by_head={name:1 for name in HEADS})
    assert a['inserted_slots_marked']==dict(counts,by_letter={'ε':counts})
    for name in HEADS:
        assert a['heads'][name]['confusion']==b['heads'][name]['confusion']
        assert a['heads'][name]['unknown']==1
    assert paired(old,new,100)['counts']=={}
    assert paired(old,new,100)['weighted_accuracy_delta']==0


def test_deleted_truth_positive_still_scores_false_negative():
    s,r=score([line([slot('α',[1,1,1,1])])],[])
    assert s['micro']['atomic']['fn']==4 and s['micro']['atomic']['fp']==0
    assert s['micro']['composed_tuple']['all_denominator']==1
    assert s['micro']['composed_tuple']['all_correct']==0
    assert not r[0]['unknown'] and r[0]['unmatched_print']
    assert s['micro']['inserted_slots']==0


def test_overlay_symmetry_and_partial_tuple():
    ll=[line([slot('η',[1,1,0,0],'384c3f89-p000059-l0013:s33')])]
    ov=json.loads(Path('docs/records/labelfix/spellcheck/R2/truth_overlay_v1.json').read_text())
    revised,version=apply_overlay(ll,ov);assert ll[0]['print_slots'][0]['targets']==[1,1,0,0]
    p=[pred('η',[2,3,0,0])];a,ar=score(revised,p);b,br=score(revised,p)
    assert a==b and a['micro']['heads']['accent']['values']['circumflex']['tp']==1
    assert a['micro']['heads']['breathing']['unknown']==1
    assert a['micro']['composed_tuple']['all_denominator']==0
    assert paired(ar,br,100)['counts']=={}


def test_paired_document_weights():
    ll=[line([slot('α',[0,1,0,0])])];ll[0]['inclusion_weight']=3
    _,a=score(ll,[pred('α',[0,0,0,0])]);_,b=score(ll,[pred('α',[0,1,0,0])])
    p=paired(a,b,100);assert p['counts']['old_wrong_new_right']==1
    assert p['weighted_accuracy_delta']==1 and p['document_cluster_95_interval']==[1,1]


def test_r1_published_continuity_exact():
    """Small frozen prediction/metadata fixture; no crops/model inference."""
    require_file('docs/records/labelfix/spellcheck/S4_lines.jsonl.gz')
    from scripts.labelfix.clariden.r1_score import metadata, prediction_map
    lines=[l for l in rows('docs/records/labelfix/spellcheck/S4_lines.jsonl.gz') if not l['dev']]
    md=list(rows(FIX/'heldout_lines.jsonl.gz'))
    meta={l['id']:dict(l,coverage_by_start={c['start']:c for c in l['coverage']}) for l in md}
    predictions=list(rows(FIX/'A_predictions.jsonl.gz'))
    actual=continuity(lines,meta,predictions)['summary']
    expected=json.loads(Path('docs/records/labelfix/spellcheck/clariden/R1_result_3678928/metrics.json').read_text())['policies']['raw']['arms']['A']
    for k in ('all_unscored_none','scored','fused_all_unscored_none','fused_scored','per_class','per_book'):
        assert actual[k]==expected[k]
    assert actual['all_unscored_none']['by_kind']['apostrophe']['fn']==206


def test_pipeline_same_frozen_policy_for_both_checkpoints():
    from tests.labelfix.test_sf6 import rich
    from scripts.labelfix.r2_score import pipeline
    rt=rich('ά');rt['id']='l'
    ll=[line([slot('α',[0,1,0,0])])];ll[0]['google']='α'
    pp=[pred('α',[0,1,0,0])];pp[0].update(cls='acute',mark_probabilities={'acute':.999})
    # FULL accepts only with the same frozen detector/observation evidence.
    a=pipeline(ll,pp,{'l':rt},'FULL');b=pipeline(ll,pp,{'l':rt},'FULL')
    assert a==b and a['policy']['sha256']
    assert a['counts']['lines']==1
    assert a['counts'].get('addition_incorrect',0)==0
    assert a['counts']['addition_correct']==1


def test_manifest_new_native_slot_window_pool(mock_pool,tmp_path):
    import shutil
    cfg=mock_pool;old=train.Shards(cfg['data'],'A','train')
    extra=tmp_path/'extra';shutil.copytree(cfg['data'],extra)
    ix=np.load(extra/'index.npy')[:1];ix['validation']=0;np.save(extra/'index.npy',ix)
    md=list(rows(extra/'lines.jsonl.gz'))[:1];md[0].update(id='native-l',doc='native:d',crop='native-crop')
    write_rows(extra/'lines.jsonl.gz',md)
    receipt=json.loads((extra/'extraction_receipt.json').read_text());receipt['sha256']={p.name:sha256(p) for p in extra.iterdir() if p.is_file() and p.name!='extraction_receipt.json'}
    write_json(extra/'extraction_receipt.json',receipt)
    inventory=list(rows(cfg['inventory']))+[dict(crop='native-crop',sha256='f'*64)]
    ip=tmp_path/'inventory.jsonl';write_rows(ip,inventory)
    r=dict(slot_id=['f'*64,0],line_id='native-l',doc='native:d',source='native',provenance='native_print',targets=[2,3,0,1],loss_weight=1,pool=str(extra))
    mp=tmp_path/'native.jsonl';write_rows(mp,[r])
    pool=ManifestPool(old,mp,ip,lambda p:train.Shards(p,'A','train'))
    assert len(pool)==len(old)+1 and list(pool[-1][2])==[2,3,0,1]
    assert pool[-1][0].shape==(64,128)


def test_fixture_hash_binding_and_teacher_checkpoint_provenance():
    binding=json.loads((FIX/'binding.json').read_text())
    assert all(sha256(FIX/p)==h for p,h in binding['sha256'].items())
    receipt=json.loads(Path('docs/records/labelfix/spellcheck/clariden/R1_result_3678928/score_receipt.json').read_text())
    # Historical prediction export is independently bound by its R1 receipt.
    assert receipt['checkpoints']['A']=='719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636'


def test_stage_binding_and_no_manifest_skip_contract(mock_pool,tmp_path):
    from scripts.labelfix.clariden.r2_run import validate
    cfg=mock_pool
    # The mock fixture uses a stand-in checkpoint hash for unit-only construction;
    # validation must reject it rather than passing a nominal stage receipt.
    with pytest.raises(ValueError,match='not frozen R1-A'):validate(cfg,True)


def test_teacher_export_real_mock_receipt():
    root=Path('artifacts/labelfix_r2/mock_run_v2/B')
    # Integration evidence is generated through the exact sbatch entry point.
    if not root.exists(): pytest.skip('bounded integration mock not generated')
    receipt=json.loads((root/'teacher_receipt.json').read_text());assert receipt['lines']==2
    assert receipt['binding']['teacher_sha256']=='719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636'
    for role in ('train','validation_reserve'):
        export=list(rows(root/f'chunk-000000-{role}.jsonl.gz'));assert export
        for r in export:
            assert set(r['heads'])==set(HEADS)
            assert set(r['crop_validity']) >= {'clipped_top','clipped_bottom','window_outside_image','span_plausible'}
            assert r['input_hashes']['crop']==r['slot_id'][0]



def test_manifest_does_not_change_frozen_class_weights(mock_pool,tmp_path):
    cfg=mock_pool
    train.train(cfg['data'],cfg['heldout'],tmp_path/'weighted','A',device='cpu',epochs=15,batch_size=16,workers=0,steps=1,threads=2,manifest=cfg['manifest'],inventory=cfg['inventory'])
    log=json.loads((tmp_path/'weighted/exposure_epoch_01.json').read_text())
    expected=train.class_weights(train.Shards(cfg['data'],'A','train').index['target'],'A','cpu')
    assert log['class_weights']=={h:w.tolist() for h,w in zip(HEADS,expected)}
    assert sum(p['draws'] for p in log['provenance'].values())==16
    assert log['unique_counts']['native_print']==1



def test_teacher_nested_validity_states_reach_scorer():
    p=pred('α',[0,1,0,0]);p.update(coverage=dict(scored=False,fused=True,evidence_state='UNKNOWN',uncertainty=['out_of_image_span']),crop_validity=dict(clipped_top=True,clipped_bottom=False))
    result,_=score([line([slot('α',[0,1,0,0])])],[p])
    states=result['micro']['states']
    assert states['fused']==1 and states['clipped']==1 and states['localisation']==1 and states['coverage']==0
