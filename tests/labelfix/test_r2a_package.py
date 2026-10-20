"""R2a package admission, extraction identity, DEV exclusions and receipts."""
import json
from pathlib import Path
from tests._paths import require_file
import numpy as np
import pytest
from scripts.labelfix.clariden import r2a_run as job
from scripts.labelfix.clariden.r2a_mock import prepare
from scripts.labelfix.clariden.r1_common import rows,sha256,write_rows,write_json,verify_receipt

@pytest.fixture
def cfg(tmp_path):return prepare(tmp_path/'inputs')

def test_overlay_all_new_and_replace_assertion(cfg,tmp_path):
    checked=job.validate(cfg,True)
    assert checked['new_identities']==4 and checked['replaced']==0
    out=tmp_path/'B/native';out.parent.mkdir()
    job.extract_cohort(cfg['native'],cfg['native_alignments'],out,True)
    result=job.overlay_pool(cfg,out)
    assert result['training_slots']==result['old_slots']+4
    assert result['replacement_assertion']=='pass'
    assert result['unique_counts']==dict(old=24,native_print=4)

def test_duplicate_overlay_rejected(cfg):
    rr=list(rows(cfg['manifest']));write_rows(cfg['manifest'],rr+[rr[0]])
    cfg['sha256'][cfg['manifest']]=sha256(cfg['manifest']);cfg['expected_slots']=5
    with pytest.raises(ValueError,match='duplicate overlay'):job.validate(cfg,True)

def test_existing_identity_not_silently_appended(cfg):
    rr=list(rows(cfg['manifest']));old=list(rows(Path(cfg['data']).parent/'old_only.jsonl'))[0]
    rr[0]['slot_id']=old['slot_id'];write_rows(cfg['manifest'],rr);cfg['sha256'][cfg['manifest']]=sha256(cfg['manifest'])
    with pytest.raises(ValueError,match='all-new'):job.validate(cfg,True)

def test_training_witness_document_leakage(cfg):
    rr=list(rows(cfg['witness']));rr[0]['doc']='native:0';write_rows(cfg['witness'],rr);cfg['sha256'][cfg['witness']]=sha256(cfg['witness'])
    with pytest.raises(ValueError,match='leakage'):job.validate(cfg,True)

def test_saved_alignment_text_mismatch_stops(cfg,tmp_path):
    ar=list(rows(cfg['dev_alignments']));ar[0]['alignment']['prediction']='ε'*8;write_rows(cfg['dev_alignments'],ar)
    with pytest.raises(ValueError,match='text mismatch'):job.extract_cohort(cfg['dev'],cfg['dev_alignments'],tmp_path/'extract',True)

def test_extraction_receipt_source_and_native_bytes(cfg,tmp_path):
    out=tmp_path/'extract';job.extract_cohort(cfg['dev'],cfg['dev_alignments'],out,True)
    receipt=verify_receipt(out);metadata=list(rows(out/'lines.jsonl.gz'))
    assert receipt['complete'] and receipt['no_ctc_forward'] and receipt['requested_lines']==1
    assert metadata[0]['source']=='dev' and len(np.load(out/'index.npy'))==8
    assert {'index.npy','lines.jsonl.gz','shard-00000-wide.npy','shard-00000-narrow.npy'}<=set(receipt['sha256'])

def test_dev_controls_unknown_and_weights(cfg,tmp_path):
    out=tmp_path/'extract';job.extract_cohort(cfg['dev'],cfg['dev_alignments'],out,True)
    pred=[dict(line_id='dev-0',start=i,base='α',factors=[0,0,0,0]) for i in range(8)]
    score,ledger,states=job.dev_score(cfg,list(rows(out/'lines.jsonl.gz')),pred)
    assert len(states)==4 and len(ledger)==4
    assert {r['line_id'] for r in ledger}=={'d0','d1'}
    assert all(r['inclusion_weight']==2 for r in ledger)
    assert len([r for r in states if r['control']])==1

def test_witness_ambiguous_alignment_unknown_preserved(cfg,tmp_path):
    out=tmp_path/'extract';job.extract_cohort(cfg['witness'],cfg['witness_alignments'],out,True)
    mm=list(rows(out/'lines.jsonl.gz'));mm[0]['recogniser_text']='α'*7
    ledger=job.witness_ledger(cfg,mm,[])
    assert len(ledger)==8 and all(r['status']=='alignment_unknown' for r in ledger)
    assert all(r['prediction'] is None for r in ledger)

def test_unique_alignment_case_preserving():
    assert job.unique_alignment('Αα','Αα')=={0:0,1:1}
    assert job.unique_alignment('αα','α')=={}
    assert job.unique_alignment('Α','α')=={}

def test_production_refuses_without_allocation(cfg,tmp_path,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    with pytest.raises(ValueError,match='existing Slurm'):job.run(Path(cfg['data']).parent.parent/'config.json',tmp_path/'run',False)

def test_target_witness_pairing_preserves_unknown_and_positives():
    old=[];new=[]
    for i in range(8):
        row=dict(card_id=str(i),letter_index=0,doc=f'd{i}',slice='subscript',control=False,anchor=True,target_head='subscript',truth=[0,0,0,int(i==7)],prediction=[0,0,0,1])
        old.append(row);new.append(dict(row,prediction=[0,0,0,int(i==7)]))
    old.append(dict(old[0],card_id='unknown',prediction=None));new.append(dict(new[0],card_id='unknown'))
    result=job.witness_comparison(old,new,100)
    assert result['counts']['unknown']==1
    assert result['net_fewer_wrong']==7 and result['false_addition_reduction']==1
    assert result['benefit_gate']['positive_regressions']==0
    assert result['net_fewer_wrong_document_ci95'][0]>0

def test_exact_sbatch_entrypoint_receipts(tmp_path):
    import os,subprocess,sys
    target=tmp_path/'e2e'
    subprocess.run([sys.executable,'-B','-m','scripts.labelfix.clariden.r2a_mock','--out',str(target)],
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(Path.cwd())},check=True,capture_output=True)
    root=target/'run';receipt=json.loads((root/'run_receipt.json').read_text())
    assert receipt['complete'] and receipt['mock'] and not receipt['submitted']
    assert receipt['stages']==list('ABCD')
    for name in 'ABCD':
        stage=json.loads((root/f'stage_{name}.json').read_text())
        assert {'binding','complete','elapsed_seconds','result','sha256','stage'}<=stage.keys()
        assert stage['binding']==receipt['binding'] and stage['complete']
        for p,h in stage['sha256'].items():assert sha256(root/p)==h
    scored=json.loads((root/'D/scoring_receipt.json').read_text())
    assert len(scored['arms'])==6 and scored['dev_items']==4 and scored['witness_cards']==1
    for arm in scored['arms'].values():
        for cohort in ('heldout','witness','dev'):
            assert {'prediction_sha256','checkpoint_sha256','extraction_receipt_sha256'}<=arm[cohort].keys()


def test_real_v2_keeps_width_gate_and_custody():
    from collections import Counter
    root=Path(__file__).resolve().parents[2]
    v1=root/'artifacts/r2a_manifest/r2a_slots.jsonl'
    v2=root/'artifacts/r2a_manifest/r2a_slots_v2.jsonl'
    original=list(rows(v1));active=list(rows(v2))
    rejected=('82e8f64cbca6e513163d4452641a51a215a0e744b8c4a338a6dc0fdf7ec740e8',46)
    assert sha256(v1)=='3dda20644c17b44e1a1c9f69781a9f1dd18657f6dc8b8b7e9cd14d8dd30a7667'
    assert active==[r for r in original if tuple(r['slot_id'])!=rejected]
    assert Counter(r['polarity'] for r in active)==dict(negative=1149,positive=423)
    quarantined=list(rows(root/'artifacts/r2a_manifest/quarantined.jsonl'))
    assert len(quarantined)==259
    assert [(r['reason'],r['polarity']) for r in quarantined if tuple(r.get('slot_id',[]))==rejected]==[('frozen_extractor_width_gate','negative')]
    cfg=json.loads((root/'config/r2a_job.json').read_text())
    receipt=json.loads((root/'artifacts/r2a_manifest/receipt.json').read_text())
    assert cfg['expected_slots']==receipt['slots']==len(active)==1572
    assert cfg['manifest']=='artifacts/r2a_manifest/r2a_slots_v2.jsonl'
    assert cfg['sha256'][cfg['manifest']]==receipt['manifest_v2_sha256']==sha256(v2)
    assert not cfg['readiness']['native_width_decision_pending']
    sentence=receipt['coordinator_accepted_deviation']
    assert sentence==cfg['coordinator_accepted_deviation']
    assert sentence in (root/'scripts/labelfix/r2_readback_verify.py').read_text()


def test_quarantined_real_slot_still_fails_frozen_extractor():
    require_file('artifacts/labelfix_r2a/inputs/native_alignments.jsonl.gz')
    from PIL import Image
    from scripts.labelfix.clariden.r1_extract import extract_line
    from scripts.labelfix.clariden.r2a_prepare import ROOT
    cfg=json.loads(Path('config/r2a_job.json').read_text())
    line=next(r for r in rows(cfg['native']) if r['crop_sha256']=='82e8f64cbca6e513163d4452641a51a215a0e744b8c4a338a6dc0fdf7ec740e8')
    alignment=next(r['alignment'] for r in rows(cfg['native_alignments']) if r['crop']==line['crop'])
    with Image.open(require_file(Path(line['crop']).relative_to(ROOT))) as im:
        _,_,_,_,coverage,_=extract_line(dict(line,_line=0),alignment,im,evaluation=True)
    rejected=next(r for r in coverage if r['start']==46)
    assert not rejected['scored'] and rejected['reason']=='width_outside_0.2_2.0_median_ctc'


def duplicate_old(cfg):
    from scripts.labelfix.clariden.r1_train import Shards
    old=Shards(cfg['data'],'A','train')
    old.index=np.concatenate([old.index,old.index[:1]])
    return old


def test_empty_manifest_duplicate_old_seed_equivalence(cfg,tmp_path):
    from scripts.labelfix.clariden.r2_manifest import ManifestPool
    from scripts.labelfix.clariden.r1_train import ArmBatches
    old=duplicate_old(cfg);empty=tmp_path/'empty.jsonl';write_rows(empty,[])
    pool=ManifestPool(old,empty,cfg['inventory'])
    assert pool.identity and np.array_equal(pool.index,old.index)
    assert pool.binding['old_rows']==25 and pool.binding['old_unique_keys']==24
    assert pool.binding['old_duplicate_rows']==2 and pool.binding['old_duplicate_groups']==dict(a=0,b=1,c=0,d=0)
    seed=20261017
    a=list(ArmBatches(old.index['target'],16,'A',seed));b=list(ArmBatches(pool.index['target'],16,'A',seed))
    assert a==b
    for batch in a:
        for i in batch:
            assert all(np.array_equal(x,y) for x,y in zip(old[i],pool[i]))
    assert np.all(pool.loss_weights==1)


@pytest.mark.parametrize('operation',['same_key','replaces','removes'])
def test_duplicate_old_replacement_ambiguity_stops(cfg,tmp_path,operation):
    from scripts.labelfix.clariden.r2_manifest import ManifestPool,inventory_ids
    old=duplicate_old(cfg);meta=inventory_ids(old,cfg['inventory'])[0]
    row=dict(meta,role='train',provenance='native_print',targets=[0,1,0,0],loss_weight=1)
    if operation!='same_key':
        row[operation]=meta['slot_id'];row['slot_id']=['f'*64,0]
    p=tmp_path/'ambiguous.jsonl';write_rows(p,[row])
    with pytest.raises(ValueError,match='ambiguous old identity for replacement'):ManifestPool(old,p,cfg['inventory'])


def test_dry_run_ab_stops_before_training(cfg,tmp_path,monkeypatch):
    monkeypatch.delenv('SLURM_JOB_ID',raising=False)
    out=tmp_path/'dryrun';job.run(Path(cfg['native']).parent/'config.json',out,mock=True,dry_run_ab=True)
    assert (out/'B/overlay_receipt.json').exists()
    assert json.loads((out/'dryrun_receipt.json').read_text())['full_overlay']
    assert not (out/'C').exists() and not (out/'D').exists()


def test_new_overlay_preserves_duplicate_old_rows(cfg,tmp_path):
    from scripts.labelfix.clariden.r2_manifest import ManifestPool
    from scripts.labelfix.clariden.r1_train import Shards
    old=duplicate_old(cfg);out=tmp_path/'native'
    job.extract_cohort(cfg['native'],cfg['native_alignments'],out,True)
    pool=ManifestPool(old,cfg['manifest'],cfg['inventory'],lambda p:Shards(p,'A','train'),native_pool=out)
    assert len(pool)==len(old)+4
    assert np.array_equal(pool.index[:len(old)],old.index)
    assert [e['index'] for e in pool.entries[:len(old)]]==list(range(len(old)))
    assert pool.binding['overlay_hits_on_duplicated_keys']==0
    assert np.all(pool.loss_weights[:len(old)]==1)
