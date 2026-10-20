"""SR1 offline migrations: small counterexamples plus frozen historical witnesses."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from PIL import Image
import pytest
from tests._paths import require_file
from greekocr.adjudicate.artifact_custody import copy_artifacts, verify
from greekocr.adjudicate.batch_check import batch_check
from greekocr.adjudicate.controls_review_sheets import controls_review_sheets
from greekocr.adjudicate.deal_batches import deal_batches
from greekocr.adjudicate.deck import build_deck
from greekocr.adjudicate.edit_evidence_crosstab import edit_evidence_crosstab
from greekocr.adjudicate.mark_profile import mark_views
from greekocr.adjudicate.owner_notes_export import owner_notes_export
from greekocr.adjudicate.page_specs import load_spec, render_spec
from greekocr.adjudicate.release_census import release_census, evidence_dump
from greekocr.adjudicate.score import named_slices, SLICE_REGISTRY
from greekocr.adjudicate.truth_overlay import add, symmetric_rescore
ROOT = Path(__file__).resolve().parents[2]
FIX = ROOT/'artifacts/cleanup_sr1'


def test_audit101_ink_and_boundary_bug():
    fixture = json.loads((FIX/'audit101.json').read_text())
    result = edit_evidence_crosstab(**fixture)
    assert len(result['changes'])==101
    assert result['above_additions_with_ink']==dict(right=38,total=38)
    # Mutation witness: <= selects the next base at precisely the edit offset.
    wrong = 0
    for r in fixture['records']:
        gates=sorted(r['gate_decisions'],key=lambda g:g['start'])
        for c in r['changes']:
            strict=max((g for g in gates if g['start']<c['start']),key=lambda g:g['start'])
            inclusive=max((g for g in gates if g['start']<=c['start']),key=lambda g:g['start'])
            wrong+=strict!=inclusive
    assert wrong>0


def test_edit_boundary_synthetic_and_unknown():
    record=dict(line_id='l',gate_decisions=[dict(start=0,base='α',evidence=dict(above=[1])),dict(start=1,base='β',evidence={})],changes=[dict(start=1,letter='α',**{'from':'','to':'\u0301'})])
    r=edit_evidence_crosstab([record],{'l':dict(verdicts=['unknown'])})
    assert r['changes'][0]['slot']==0 and r['changes'][0]['ink']
    assert r['above_additions_with_ink']==dict(right=0,total=1)
    record['changes'][0]['letter']='β'
    with pytest.raises(ValueError,match='base mismatch'):edit_evidence_crosstab([record],{'l':dict(ok=True)})


def census_fixture():
    selection={}
    records=[]
    for i,tier in enumerate(('agree','other','noink')):
        ident=f'l{i}'
        selection[ident]=dict(label='ά',wave=f'w{i%2}',crop='unused.png')
        records.append(dict(line_id=ident,status='hold',gate_decisions=[dict(start=0,base='α',r1_parts=['grave'],peer_prediction=dict(parts=['grave']),detector_parts=['grave'] if tier=='agree' else [],evidence=dict(above=[dict(bbox=[0,0,1,1])] if tier!='noink' else [],below=[]),hold_reasons=[])]))
    return records,selection


def test_census_tiers_wave_seed_and_alignment():
    records,selection=census_fixture()
    result=release_census(records,selection,sample_size=1)
    assert result['tiers']==dict(agree=1,other=1,noink=1)
    assert result['waves']=={'w0':dict(agree=1,noink=1),'w1':dict(other=1)}
    assert result==release_census(records,selection,sample_size=1)
    records[0]['gate_decisions'][0]['base']='β'
    assert release_census(records,selection)['aligned']==2
    with pytest.raises(ValueError):release_census(records,selection,sample_size=-1)


def test_census_does_not_count_disagreement_or_addition():
    records,selection=census_fixture()
    records[0]['gate_decisions'][0]['peer_prediction']['parts']=[]
    selection['l1']['label']='α'
    assert release_census(records,selection)['tiers']==dict(noink=1)
    assert evidence_dump(records,'l0')['slots']
    with pytest.raises(KeyError):evidence_dump(records,'absent')
    with pytest.raises(ValueError):evidence_dump(records+records,'l0')


@pytest.mark.parametrize('name,count',[('reader_errors_heldout',39),('accent_corrections_checked',100),('audit_words',100),('accent_substitutions',60)])
def test_data_page_specs(name,count):
    path=require_file(FIX/'specs'/f'{name}.json')
    assert len(load_spec(path)['lines'])==count
    html=render_spec(path)
    assert html.count('<div class="card"')==count
    assert '<textarea' in html


def test_page_spec_schema(tmp_path):
    p=tmp_path/'spec.json';p.write_text('{}')
    with pytest.raises(ValueError):load_spec(p)


@pytest.mark.parametrize('name,row',[('capital',dict(base='Ἀ')),('ALL-CAPS',dict(word='ΦΡΆΓΚΙΣΚΗ')),('numeral',dict(word='Αʹ')),('ο-monotonic',dict(base='ο',orthography='monotonic')),('subscript',dict(truth=[0,0,0,1])),('exact-name',dict(exact_name=True))])
def test_slices(name,row):
    assert named_slices([row])[name]==[row]
    assert named_slices([{}])[name]==[]
    with pytest.raises(TypeError):SLICE_REGISTRY[name]=lambda r:True


def test_slices_case_and_context_not_predictions():
    assert not named_slices([dict(base='α',word='Αθήνα',prediction=[1,1,0,0])])['ALL-CAPS']
    assert named_slices([dict(base='ο')])['ο-monotonic']
    assert named_slices([dict(base='η',truth=[0,0,0,0])])['subscript']
    assert named_slices([dict(truth=[0,2,0,0])])['exact-name']
    assert named_slices([dict(base='α',numeral=True)])['numeral']


def test_review_contact_sheets_and_limit(tmp_path):
    im=tmp_path/'word.png';Image.new('RGB',(200,50),'#dddddd').save(im)
    controls=[dict(id=f'c{i}',word_image=str(im),letter_image=str(im),expected_form='ἦγε',expected_tuple=[1,3,0,0]) for i in range(13)]
    out=tmp_path/'review'
    r=controls_review_sheets(controls,out)
    assert r['sheets']==2 and len(json.loads((out/'index.json').read_text()))==13
    assert Image.open(out/'controls_000.png').size==(1600,1920)
    assert Image.open(out/'controls_001.png').size==(1600,320)
    with pytest.raises(ValueError):controls_review_sheets(controls,tmp_path/'bad',per_sheet=13)


def make_deck(tmp_path,mark=False):
    image=tmp_path/'source.png';Image.new('RGB',(100,30),'white').save(image)
    record=dict(image=str(image),options=['α','ά'],profile='mark' if mark else 'word',bbox=[20,0,30,30])
    if mark:record.update(word_box=[10,0,70,30],letter_box=[20,0,30,30])
    return build_deck(dict(blind_dir=str(tmp_path/'source_deck/blind'),items=[record,record],controls=[dict(record,pixel_verified=True,known_answer='α')]))


def test_deal_reverse_hashes_isolation_and_batch_check(tmp_path):
    receipt=make_deck(tmp_path)
    deal=deal_batches(receipt['blind_dir'],tmp_path/'assignments',batch_size=3)
    r1,r2=deal['batches']
    assert r1['ids']==list(reversed(r2['ids']))
    assert all('key' not in p for p in r1['files'])
    keys=json.loads(Path(receipt['private_key']).read_text())
    key={k['id']:k for k in keys}
    cards=json.loads((tmp_path/'assignments'/r1['folder']/'items_blind.json').read_text())
    answers=[dict(id=c['id'],answer=next(k for k,v in c['options'].items() if v=='α'),confidence='high',note='') for c in cards]
    result=batch_check(tmp_path/'assignments'/r1['folder'],r1,answers,keys)
    assert result['status']=='BATCH_CHECK_PASSED' and result['truth_written'] is False
    bad=deepcopy(answers)
    control=next(i for i,a in enumerate(bad) if key[a['id']]['control'])
    bad[control]['answer']=next(k for k,v in cards[control]['options'].items() if v=='ά')
    assert batch_check(tmp_path/'assignments'/r1['folder'],r1,bad,keys)['status']=='CONTROLS_FAILED'
    with pytest.raises(ValueError,match='coverage/order'):batch_check(tmp_path/'assignments'/r1['folder'],r1,answers[::-1],keys)
    (tmp_path/'assignments'/r1['folder']/'README.md').write_text('tampered')
    with pytest.raises(ValueError,match='hash mismatch'):batch_check(tmp_path/'assignments'/r1['folder'],r1,answers,keys)


def test_deal_chunks_and_unsafe_paths(tmp_path):
    receipt=make_deck(tmp_path)
    out=tmp_path/'dealt'
    result=deal_batches(receipt['blind_dir'],out,batch_size=2)
    assert [len(b['ids']) for b in result['batches']]==[2,2,1,1]
    with pytest.raises(FileExistsError):deal_batches(receipt['blind_dir'],out)
    manifest=Path(receipt['blind_dir'])/'items_blind.json'
    cards=json.loads(manifest.read_text());cards[0]['img']='../private/items_key.json';manifest.write_text(json.dumps(cards))
    with pytest.raises(ValueError,match='unsafe'):deal_batches(receipt['blind_dir'],tmp_path/'unsafe')


def test_mark_native_views_and_deal(tmp_path):
    native=Image.fromarray(np.arange(100*30*3,dtype=np.uint8).reshape(30,100,3))
    result=mark_views(native,[10,0,70,30],[20,0,30,30])
    assert result['word'].size==(180,90) and result['letter'].size==(80,240)
    assert np.array_equal(np.array(result['letter'])[::8,::8],np.array(native)[:,20:30])
    receipt=make_deck(tmp_path,mark=True)
    cards=json.loads((Path(receipt['blind_dir'])/'items_blind.json').read_text())
    assert all('mark_img' in c for c in cards)
    assert Image.open(Path(receipt['blind_dir'])/cards[0]['mark_img']).size==(80,240)
    assert deal_batches(receipt['blind_dir'],tmp_path/'mark_deal')['batches'][0]['leak_scan']['passed']
    with pytest.raises(ValueError):mark_views(native,[0,0,101,30],[1,0,2,30])


def test_notes_join_and_explicit_sheet_conventions(tmp_path):
    cards=[dict(sheet=s,db_id='l:s1',evidence='card') for s in ('audit','reader')]
    sheets={'audit':dict(no_note_status='accepted',note_status='review'), 'reader':dict(no_note_status='unreviewed',note_status='review')}
    documents=[dict(sheet='reader',db_id='l:s1',note='this is circumflex actually',printed='ἦγε')]
    out=tmp_path/'notes.jsonl'
    assert owner_notes_export(documents,cards,sheets,out)['rows']==2
    rows=[json.loads(l) for l in out.read_text().splitlines()]
    assert [r['status'] for r in rows]==['accepted','review']
    assert rows[1]['card']==cards[1] and rows[1]['document']==documents[0]
    with pytest.raises(ValueError):owner_notes_export(documents*2,cards,sheets,tmp_path/'duplicate')
    with pytest.raises(ValueError):owner_notes_export(documents+[dict(sheet='audit',db_id='absent')],cards,sheets,tmp_path/'unknown')
    with pytest.raises(KeyError):owner_notes_export([],cards,{},tmp_path/'no_convention')


def overlay_input():
    parent=json.loads((FIX/'overlay/truth_overlay_v1.json').read_text())
    target=json.loads((FIX/'overlay/truth_overlay_v1_1.json').read_text())
    paths=[FIX/'overlay/evidence/tranche6'/name for name in ('answer_r1.json','answer_r2.json','answer_r3.json','letter.png')]
    return parent,target,paths


def test_overlay_v11_reproduction_and_symmetric_rescore():
    parent,target,paths=overlay_input()
    entry=target['entries'][0]
    receipt=add(parent,entry,version='v1.1',evidence_paths=paths,expected_parent='v1')
    assert receipt['overlay']==target
    assert len(receipt['evidence'])==4
    lines=[dict(print_slots=[dict(id=entry['id'],targets=[1,1,0,0],unknown=[])])]
    def score(lines,pred):return int(lines[0]['print_slots'][0]['targets']==pred[0])
    r=symmetric_rescore(lines,target,{'A':[[1,1,0,0]],'B':[[1,3,0,0]]},score)
    assert r['arms']['A']['score']==0 and r['arms']['B']['score']==1
    assert r['arms']['A']['truth_sha256']==r['arms']['B']['truth_sha256']
    assert lines[0]['print_slots'][0]['targets']==[1,1,0,0]
    with pytest.raises(ValueError):symmetric_rescore([],target,{'A':[],'B':[]},score)


@pytest.mark.parametrize('mutation',['parent','domain','unknown','previous','evidence'])
def test_overlay_rejects_invalid(mutation):
    parent,target,paths=overlay_input();entry=deepcopy(target['entries'][0])
    if mutation=='parent':parent['version']='wrong'
    elif mutation=='domain':entry['new_tuple'][1]=4
    elif mutation=='unknown':entry['unknown']=['breathing']
    elif mutation=='previous':entry['previous_tuple']=[0,0,0,0]
    else:paths=paths[:-1]
    with pytest.raises(ValueError):add(parent,entry,version='v1.1',evidence_paths=paths,expected_parent='v1')


def test_custody_hashes_tamper_and_symlink(tmp_path):
    source=tmp_path/'source';source.mkdir();(source/'a').write_bytes(b'witness')
    result=copy_artifacts(source,tmp_path/'copy',['a'])
    assert result['verification']['passed']
    (tmp_path/'copy/a').write_bytes(b'tampered')
    assert verify(tmp_path/'copy',result['manifest'])['mismatches']==['a']
    with pytest.raises(FileExistsError):copy_artifacts(source,tmp_path/'copy',['a'])
    with pytest.raises(ValueError):copy_artifacts(source,tmp_path/'escape',['../source/a'])
    (source/'link').symlink_to(source/'a')
    with pytest.raises(ValueError):copy_artifacts(source,tmp_path/'linked',['link'])


def test_cli_crosstab(tmp_path):
    out=tmp_path/'result.json'
    result=subprocess.run([sys.executable,'scripts/review/sr1.py','crosstab','--spec',str(FIX/'audit101.json'),'--output',str(out)],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    assert json.loads(out.read_text())['above_additions_with_ink']==dict(right=38,total=38)


def test_r2_patch_apply_and_actual_symmetric_instrument(tmp_path):
    """Apply the supplied patch to a hash-bound temp copy of the tracked source."""
    import hashlib
    import runpy
    source=ROOT/'scripts/labelfix/r2_score.py'
    receipt=json.loads((FIX/'r2_score_patch_receipt.json').read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest()==receipt['source_sha256']
    target=tmp_path/'scripts/labelfix/r2_score.py';target.parent.mkdir(parents=True)
    target.write_bytes(source.read_bytes())
    process=subprocess.run(['patch','-p1','-i',str(FIX/'r2_score_slices.patch')],cwd=tmp_path,capture_output=True,text=True)
    assert process.returncode==0,process.stderr
    instrument=runpy.run_path(str(target))
    line=dict(line_id='l',doc='d',print_slots=[dict(id='l:s0',base='η',targets=[1,1,0,0],unknown=[],word='ἤγε')])
    predictions=[dict(line_id='l',start=0,base='η',factors=[1,3,0,0])]
    scored,records=instrument['score']([line],predictions)
    assert set(scored['slices'])==set(SLICE_REGISTRY)
    assert scored['slices']['subscript']['states']['union_slots']==1
    assert scored['slices']['exact-name']['states']['union_slots']==1
    assert records[0]['word']=='ἤγε'
    overlay=dict(version='fixture',entries=[dict(id='l:s0',previous_tuple=[1,1,0,0],new_tuple=[1,3,0,0],unknown=[])])
    result=symmetric_rescore([line],overlay,{'A':predictions,'B':predictions},instrument['score'])
    assert result['arms']['A']['score']==result['arms']['B']['score']
    assert result['arms']['A']['score'][0]['micro']['composed_tuple']['accuracy_all']==1


def test_batch_check_cli_is_dry_and_returns_gate_failure(tmp_path):
    receipt=make_deck(tmp_path)
    dealt=deal_batches(receipt['blind_dir'],tmp_path/'assigned',batch_size=110)
    assignment=dealt['batches'][0]
    folder=tmp_path/'assigned'/assignment['folder']
    cards=json.loads((folder/'items_blind.json').read_text())
    keys=json.loads(Path(receipt['private_key']).read_text())
    answers=[dict(id=c['id'],answer='literal',printed='α',confidence='high',note='') for c in cards]
    spec=tmp_path/'check.json'
    spec.write_text(json.dumps(dict(folder=str(folder),assignment=assignment,answers=answers,keys=keys)))
    output=tmp_path/'check_result.json'
    proc=subprocess.run([sys.executable,'scripts/review/sr1.py','batch-check','--batch-check','--spec',str(spec),'--output',str(output)],cwd=ROOT,capture_output=True,text=True)
    assert proc.returncode==0,proc.stderr
    assert json.loads(output.read_text())['truth_written'] is False
    for answer in answers:answer['printed']='ά'
    spec.write_text(json.dumps(dict(folder=str(folder),assignment=assignment,answers=answers,keys=keys)))
    output=tmp_path/'failed.json'
    proc=subprocess.run([sys.executable,'scripts/review/sr1.py','batch-check','--batch-check','--spec',str(spec),'--output',str(output)],cwd=ROOT,capture_output=True,text=True)
    assert proc.returncode==1
    assert json.loads(output.read_text())['status']=='CONTROLS_FAILED'


def test_raw_artifact_db_dump_adapter(tmp_path):
    docs=[dict(id='l',data=dict(note='checked',printed='ἦγε'))]
    cards=[dict(sheet='s',db_id='l')]
    sheets={'s':dict(no_note_status='accepted',note_status='review')}
    path=tmp_path/'notes.jsonl'
    owner_notes_export(docs,cards,sheets,path)
    row=json.loads(path.read_text())
    assert row['document']['note']=='checked' and row['status']=='review'


def test_custody_extra_files_and_manifest_traversal(tmp_path):
    source=tmp_path/'s';source.mkdir();(source/'a').write_text('evidence')
    result=copy_artifacts(source,tmp_path/'out',['a'])
    (tmp_path/'out/extra').write_text('unexpected')
    assert verify(tmp_path/'out',result['manifest'])['mismatches']==['extra']
    with pytest.raises(ValueError):verify(tmp_path/'out',dict(files={'../a':'0'*64}))


def test_census_mixed_line_tier_line_counts():
    records,selection=census_fixture()
    record=records[0]
    other=deepcopy(records[1]['gate_decisions'][0]);other.update(start=2,base='ε')
    record['gate_decisions'].append(other)
    selection['l0']['label']='άέ'
    result=release_census([record],selection)
    assert result['tiers']==dict(agree=1,other=1)
    assert result['tier_lines']==dict(agree=1,other=1)
    assert result['sizes']==dict(other=1)


def test_overlay_evidence_directory_and_real_date_validation():
    parent,target,paths=overlay_input()
    entry=deepcopy(target['entries'][0]);entry['evidence']=entry['evidence'].replace('evidence/tranche6/','wrong/directory/')
    with pytest.raises(ValueError,match='evidence'):add(parent,entry,version='v1.1',evidence_paths=paths,expected_parent='v1')
    entry=deepcopy(target['entries'][0]);entry['date']='2026-99-99'
    with pytest.raises(ValueError,match='date'):add(parent,entry,version='v1.1',evidence_paths=paths,expected_parent='v1')
