"""Scorer and training finalizer fixtures; no real locked answers or train edit."""
import copy
import json
from pathlib import Path
import sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts/numerics'))
from test_n1r import rule,slot
from greekocr.numerics.ink_rule import decide
from greekocr.numerics.line_complete import enumerate_slots
from n1_gate import score,truth_from_reads
from n1_apply_train import apply_rows,run,label_sha,authorize_gate
from n1t_packs import rows


def votes(truth):
    return [dict(reader=r,meaning=truth,context_status='VALID',read_status='ok',confidence='high') for r in ('r1','r2')]


def decision(rule,sid='p',truth='raised dot',edit=True):
    d=decide(slot(),rule);d.update(slot_id=sid)
    if truth!='raised dot':d.update({'class':truth},edit=None)
    if not edit:d['edit']=None
    return d


def gate(rule):
    ds=[decision(rule),decision(rule,'h','hyphen')]
    return score(ds,['p','h'],{'p':votes('raised dot'),'h':votes('hyphen')})


def test_gate_pass_reports_recall_unsure(rule):
    g=gate(rule);assert g['passed'] and g['raised_precision']==1 and g['raised_recall']==1
    assert g['unsure_rate']==0 and g['false_range_edits']==0


def test_zero_predictions_is_not_success(rule):
    d=decision(rule,truth='unsure');g=score([d],['p'],{'p':votes('raised dot')})
    assert not g['passed'] and g['raised_precision'] is None and g['raised_recall']==0


def test_range_false_edit_fails(rule):
    ds=[decision(rule),decision(rule,'range')]
    g=score(ds,['p','range'],{'p':votes('raised dot'),'range':votes('hyphen')})
    assert not g['passed'] and g['false_range_edits']==1 and g['raised_precision']==.5


@pytest.mark.parametrize('truth',['hyphen','en dash','em dash','any dash'])
def test_all_range_types_count_false_edit(rule,truth):
    g=score([decision(rule)],['p'],{'p':votes('hyphen' if truth=='any dash' else truth)},
            [dict(slot_id='p',truth='any dash')] if truth=='any dash' else [])
    assert g['false_range_edits']==1 and g['hyphen_to_raised_false']==1 and not g['passed']


def test_baseline_false_positive_fails_without_range_edit(rule):
    g=score([decision(rule)],['p'],{'p':votes('baseline dot')})
    assert g['raised_precision']==0 and not g['passed'] and g['false_range_edits']==0


@pytest.mark.parametrize('bad',['VOID','INVALID','low'])
def test_invalid_votes_need_lead(rule,bad):
    rr=votes('raised dot')
    if bad=='low':rr[1]['confidence']='low'
    else:rr[1]['context_status']=bad
    g=score([decision(rule)],['p'],{'p':rr});assert not g['passed'] and g['unresolved']==['p']
    g=score([decision(rule)],['p'],{'p':rr},[dict(slot_id='p',truth='raised dot')]);assert g['passed']


def test_lead_overrides_agreement_and_hold(rule):
    for truth in ['baseline dot','hold']:
        g=score([decision(rule)],['p'],{'p':votes('raised dot')},[dict(slot_id='p',truth=truth)])
        assert not g['passed']


def test_unlocalized_reads_cannot_establish_truth(rule):
    g=score([decision(rule)],['p'],{'p':votes('raised dot')},unlocalized_ids=['p'])
    assert not g['passed'] and g['unresolved']==['p']
    g=score([decision(rule)],['p'],{'p':votes('raised dot')},[dict(slot_id='p',truth='raised dot')],unlocalized_ids=['p'])
    assert g['passed']


@pytest.mark.parametrize('case',['missing','duplicate','mixed_hash','extra_read'])
def test_bad_population_refused(rule,case):
    ds=[decision(rule)];reads={'p':votes('raised dot')}
    if case=='missing':reads['p']=reads['p'][:1]
    elif case=='duplicate':reads['p'][1]['reader']='r1'
    elif case=='extra_read':reads['other']=votes('nothing')
    else:
        ds.append(decision(rule,'other'));ds[-1]['rule_hash']='other'
    with pytest.raises(ValueError):score(ds,['p'],reads)


def train_fixture(tmp_path):
    from PIL import Image,ImageDraw
    from greekocr.numerics.ink_rule import sha
    p=tmp_path/'crop.png';im=Image.new('L',(70,35),255);draw=ImageDraw.Draw(im)
    draw.rectangle((4,5,13,24),fill=0);draw.rectangle((35,5,44,24),fill=0)
    draw.rectangle((22,14,24,16),fill=0);im.save(p)
    row=dict(id='row',label='1.2',crop=str(p),crop_sha256=sha(p),split='train')
    ss=enumerate_slots(dict(id='row',text=row['label']))
    for s in ss:
        s['geometry']=dict(geom_status='missing')
        if s['boundary'] is None:
            s['geometry']=dict(geom_status='ok',left_digit=[4,5,14,25],right_digit=[35,5,45,25],
                digit_top=5,baseline=25,digit_height=20,gap=[14,35],gap_width=21,gap_center=24.5,zoom_bbox=[0,0,55,32])
            s['digit_widths']=dict(status='ok',median_digit_width=10,widths=[10,10])
    return row,dict(line_id='row',crop_sha256=sha(p),parent_label_sha256=label_sha(row['label']),slots=ss)


def test_train_real_pixels_edit_and_complete_records(rule,tmp_path):
    row,side=train_fixture(tmp_path)
    result,ds=apply_rows([row],rule,gate(rule),tmp_path,{'row':side})
    assert result[0]['parent_label']=='1.2' and result[0]['label']=='1·2'
    assert len(ds)==3 and len(result[0]['edits'])==1
    assert all(d['rule_hash']==rule['rule_hash'] and d['crop_sha256']==row['crop_sha256'] for d in ds)


def test_train_missing_geometry_retains_every_slot(rule,tmp_path):
    row,_=train_fixture(tmp_path);result,ds=apply_rows([row],rule,gate(rule),tmp_path)
    assert result[0]['label']=='1.2' and len(ds)==3
    assert all(d['class']=='unsure' and d['tags']==['unsure'] and not d['edit'] for d in ds)


@pytest.mark.parametrize('field',['crop_sha256','parent_label_sha256','slots'])
def test_train_geometry_custody(rule,tmp_path,field):
    row,side=train_fixture(tmp_path);side[field]=[] if field=='slots' else 'bad'
    with pytest.raises(ValueError):apply_rows([row],rule,gate(rule),tmp_path,{'row':side})


@pytest.mark.parametrize('bad',['not_passed','rule_hash','precision','no_predictions','false_ranges','unresolved'])
def test_applier_fails_before_outputs(rule,tmp_path,bad):
    g=gate(rule)
    if bad=='not_passed':g['passed']=False
    if bad=='rule_hash':g['rule_hash']='other'
    if bad=='precision':g['raised_precision']=.98
    if bad=='no_predictions':g['raised_predicted']=0
    if bad=='false_ranges':g['false_range_edits']=1
    if bad=='unresolved':g['unresolved']=['p']
    output=tmp_path/'output.jsonl'
    with pytest.raises(ValueError,match='gate'):run(tmp_path/'absent-source',output,tmp_path/'absent-registry',rule,g,tmp_path)
    assert not output.exists()


def test_finalizer_manifest_and_lqb_preserve_parent(rule,tmp_path):
    row,side=train_fixture(tmp_path);source=tmp_path/'source.jsonl'
    source.write_text(json.dumps(row)+'\n'+json.dumps(dict(id='plain',label='abc',crop='unused',split='train'))+'\n')
    registry=tmp_path/'versions.json';registry.write_text(json.dumps(dict(schema='lqb-versions-v1',versions={'existing':{'keep':True}})))
    output=tmp_path/'n1_v1_train.jsonl'
    manifest=run(source,output,registry,rule,gate(rule),tmp_path,{'row':side})
    assert manifest['output']['rows']==2 and manifest['decisions']['slots']==3 and manifest['edits']==1
    results=rows(output);assert results[1]['label']=='abc' and results[0]['label']=='1·2'
    v=json.loads(registry.read_text())['versions']
    assert v['existing']=={'keep':True} and v['n1_v1_train']['parent']=='collection_v2_train'
    assert v['n1_v1_train']['sha256']==manifest['output']['sha256']
    with pytest.raises(ValueError,match='overwrite'):run(source,output,registry,rule,gate(rule),tmp_path,{'row':side})


@pytest.mark.parametrize('count,passes',[(100,True),(99,False)])
def test_precision_boundary_exactly_99_percent(rule,count,passes):
    ds=[decision(rule,str(i)) for i in range(count)]
    rr={str(i):votes('raised dot' if i else 'baseline dot') for i in range(count)}
    g=score(ds,list(rr),rr)
    assert g['passed'] is passes and g['false_range_edits']==0


def test_train_stroke_pixels_are_tag_only(rule,tmp_path):
    from PIL import Image,ImageDraw
    from greekocr.numerics.ink_rule import sha
    row,side=train_fixture(tmp_path)
    with Image.open(row['crop']) as image:
        im=image.copy();draw=ImageDraw.Draw(im);draw.rectangle((20,12,31,18),fill=255)
        draw.rectangle((20,14,29,15),fill=0);im.save(row['crop'])
    row['crop_sha256']=side['crop_sha256']=sha(row['crop'])
    result,ds=apply_rows([row],rule,gate(rule),tmp_path,{'row':side})
    assert result[0]['label']=='1.2' and not result[0]['edits']
    assert any(d['class']=='en dash' and d['tags']==['en dash'] for d in ds)


def test_train_parent_registration_conflict_precedes_output(rule,tmp_path):
    source=tmp_path/'source';source.write_text('')
    registry=tmp_path/'versions.json';registry.write_text(json.dumps(dict(versions={'collection_v2_train':dict(path='other',sha256='bad')})))
    output=tmp_path/'n1_v1_train.jsonl'
    with pytest.raises(ValueError,match='parent differs'):run(source,output,registry,rule,gate(rule),tmp_path)
    assert not output.exists()
