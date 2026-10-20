"""SF4 conservative clipping, full runtime custody and punctuation integration."""
from copy import deepcopy
import hashlib
import html
import json
from pathlib import Path

import pytest

from greekocr.labelfix import reading as R
from greekocr.labelfix.release_gate import bind_runtime, compose_runtime, deserialize, serialize
from greekocr.labelfix.text import ELISION, clusters, is_letter, nfd
from tests.labelfix.test_sf4_review import clean


@pytest.mark.parametrize('base', ['Α','Ι','Υ','Β','Ρ','ι','β'])
@pytest.mark.parametrize('physical', ['case_class','slot_case','band_source','height_band','pixel_class','raw_pixel_class','frozen_pixel_class','geometry_capital','all_caps'])
@pytest.mark.parametrize('direction', ['top','bottom'])
def test_either_capital_signal_blocks_clipping_relaxation(base,physical,direction):
    rt=clean(base);s=rt['detector']['slots'][0]
    s['evidence'].update(meanline=100,xh=1,**{'clipped_'+direction:True})
    if physical=='case_class':s['evidence']['case_class']='capital'
    elif physical=='slot_case':s['case_class']='capital'
    elif physical=='band_source':s['evidence']['band_source']='capital_height'
    elif physical=='height_band':s['height_band']={'source':'capital_run'}
    else:s[physical]=True if physical in ('geometry_capital','all_caps') else 'capital'
    assert 'detector_clipped_'+direction in compose_runtime(rt,'ENSEMBLE_AB')['hold_slots'][0]['reasons']


@pytest.mark.parametrize('base',['Α','Ι','Υ','Β'])
def test_recogniser_capital_cannot_be_overruled_by_lowercase_pixels(base):
    rt=clean(base);s=rt['detector']['slots'][0]
    s.update(case_class='lowercase_body',height_band={'source':'pixel_lowercase_bodies'})
    s['evidence'].update(case_class='lowercase_body',meanline=100,xh=1,clipped_top=True)
    assert 'detector_clipped_top' in compose_runtime(rt,'ENSEMBLE_AB')['hold_slots'][0]['reasons']


@pytest.mark.parametrize('mode',['PRESENCE','FULL','ENSEMBLE_AB','ENSEMBLE_AE'])
@pytest.mark.parametrize('arm',['B','E'])
def test_full_owner_runtime_parity_with_differing_diagnostic_predictions(monkeypatch,mode,arm):
    from scripts.labelfix import owner_pages_build_combined as p
    rt=clean('ι');rt['detector']['slots'][0]['evidence']['clipped_bottom']=True
    rt['peer_predictions'][arm][0]['parts']=['subscript']
    rt=bind_runtime(rt)
    monkeypatch.setattr(p,'LINE_TEXT',{'synthetic':rt['recogniser_text']})
    monkeypatch.setattr(p,'RUNTIMES',{'synthetic':rt})
    actual,_=p.combine('synthetic',deserialize(rt['detector']),mode)
    expected=compose_runtime(rt,mode)
    assert serialize(actual)=={k:v for k,v in expected.items() if k not in ('mode','release_policy','hold_slots')}
    assert actual.slots[0]['hold']
    assert 'detector_clipped_bottom' in actual.slots[0]['hold_reasons']


@pytest.mark.parametrize('field',['recogniser_text','detector','r1_predictions','coverage','peer_predictions','peer_coverage','k1_flags'])
def test_every_relevance_input_is_bound(field):
    rt=bind_runtime(clean())
    if field=='recogniser_text':rt[field]='η'
    elif field=='detector':rt[field]['slots'][0]['evidence']['clipped_bottom']=True
    elif field=='r1_predictions':rt[field][0]['parts']=['subscript']
    elif field=='coverage':rt[field][0]['uncertainty']=['out_of_image_span']
    elif field=='peer_predictions':rt[field]['E'][0]['parts']=['subscript']
    elif field=='peer_coverage':rt[field]['E'][0]['scored']=False
    else:rt[field]=[{'reason':'clipped_top'}]
    with pytest.raises(ValueError,match='binding'):compose_runtime(rt,'ENSEMBLE_AB')


def test_owner_loader_binds_all_peers_and_detects_dropped_or_changed_E(tmp_path):
    from scripts.labelfix.owner_pages_build_combined import load_runtimes,digest
    path=tmp_path/'runtime.jsonl';rt=clean()
    path.write_text(json.dumps(rt)+'\n');cfg={'runtime':{str(path):digest(path)}}
    assert load_runtimes([str(path)],cfg)['synthetic']==bind_runtime(rt)
    rt['peer_predictions'].pop('E');path.write_text(json.dumps(rt)+'\n')
    with pytest.raises(ValueError,match='hash'):load_runtimes([str(path)],cfg)
    cfg['runtime'][str(path)]=digest(path)
    with pytest.raises(ValueError,match='diagnostic E'):load_runtimes([str(path)],cfg)


@pytest.mark.parametrize('alias',list(ELISION))
@pytest.mark.parametrize('context',['final','prefix','internal','closing'])
def test_all_aliases_through_slotting_rendering_composition_and_K1(alias,context):
    from types import SimpleNamespace as NS
    from greekocr.labelfix.ctc_align import Alignment,CharSpan
    from greekocr.labelfix.segmentation import recogniser_slots
    from scripts.labelfix.owner_reading import reading_html
    text={'final':'δ'+alias+' α','prefix':alias+'δ','internal':'δ'+alias+'α','closing':'δ.'+alias}[context]
    text=nfd(text)
    ink=NS(components=[],xh=20,font_width=16,width=len(text)*10,band=lambda x:(10,30))
    al=Alignment(text,[CharSpan(c,i,i,i+1,i*10,(i+1)*10) for i,c in enumerate(text)])
    slots=recogniser_slots(ink,text,al)
    expected_starts=[c.start for c in clusters(text) if is_letter(c.base)]
    assert [s['start'] for s in slots]==expected_starts
    # Replace unresolved synthetic localisation with explicit clean test evidence.
    for s in slots:
        s.update(localisation_unknown=False,segmentation_uncertain=False,parts=[],unnamed=[],evidence={})
    if context=='final':
        assert slots[0]['word_final'];slots[0]['apostrophe']=True
    cov=[dict(start=s['start'],base=s['base'],scored=True,evidence_state='unadjudicated',uncertainty=[]) for s in slots]
    pred=[dict(start=s['start'],base=s['base'],parts=[]) for s in slots]
    rt=dict(recogniser_text=text,detector=serialize(R.LineReading(text,slots,[])),
            r1_predictions=pred,coverage=cov,peer_predictions={'B':deepcopy(pred),'E':deepcopy(pred)},
            peer_coverage={'B':deepcopy(cov),'E':deepcopy(cov)})
    actual=compose_runtime(rt,'ENSEMBLE_AB')
    wanted='δ’ α' if context=='final' else text
    assert actual['text']==wanted and not actual['hold_slots']
    assert [s['start'] for s in actual['slots']]==expected_starts
    assert R.render_reading(text,slots)==wanted
    assert R.apply_constraints(deserialize(actual))[0].text==wanted
    assert html.unescape(reading_html(actual))==wanted


@pytest.mark.parametrize('binding_case',['valid','missing','wrong_page','wrong_notes','changed_page','changed_notes'])
def test_notes_binding_before_any_approval_output(tmp_path,monkeypatch,binding_case):
    from scripts.labelfix import owner_implicit_changes as m
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    paths={};hashes={}
    for name,text in [('old','ά'),('new','α')]:
        page=tmp_path/(name+'.html');page.write_text(text);hashes[name]=digest(page)
        side=tmp_path/(name+'.json');side.write_text(json.dumps(dict(page_sha256=hashes[name],lines={
            'x':dict(reading=text,line_reading=dict(slots=[dict(display_slot=1,bbox=[1,1,3,3])]))})))
        paths[name]=(page,side)
    notes=tmp_path/'notes.jsonl';notes.write_text('{"line_id":"x","note":""}\n')
    binding=dict(reviewed_page=str(paths['old'][0]),reviewed_page_sha256=hashes['old'],notes_sha256={str(notes):digest(notes)})
    if binding_case=='wrong_page':binding['reviewed_page_sha256']=hashes['new']
    if binding_case=='wrong_notes':binding['notes_sha256'][str(notes)]='0'*64
    if binding_case=='changed_page':paths['old'][0].write_text('changed')
    if binding_case=='changed_notes':notes.write_text('{"line_id":"x","note":"changed"}\n')
    bp=tmp_path/'binding.json';bp.write_text(json.dumps(binding));out=tmp_path/'out.json'
    argv=['owner_implicit_changes','--notes',str(notes),'--out',str(out),
          '--reviewed-page-sha256',hashes['old'],'--new-page-sha256',hashes['new']]
    for name,(page,side) in paths.items():argv+=['--'+name+'-page',str(page),'--'+name+'-boxes',str(side)]
    if binding_case!='missing':argv+=['--review-binding',str(bp)]
    monkeypatch.setattr('sys.argv',argv)
    if binding_case=='valid':
        m.main();data=json.loads(out.read_text())
        assert data['notes_sha256']==binding['notes_sha256']
        assert data['review_binding_sha256']==digest(bp)
        assert data['changes'][0]['kind']=='REGRESSION? (reviewed snapshot approval)'
    else:
        with pytest.raises(ValueError):m.main()
        assert not out.exists()


def test_actual_owner_cli_keeps_diagnostic_E_in_bound_runtime(tmp_path,monkeypatch):
    import subprocess
    from PIL import Image
    from greekocr.labelfix.ctc_align import Alignment
    from scripts.labelfix import owner_pages_build_combined as p
    from scripts.labelfix import owner_reading as owner
    rt=clean('ι');rt['detector']['slots'][0]['evidence']['clipped_bottom']=True
    rt['peer_predictions']['E'][0]['parts']=['subscript']
    runtime=tmp_path/'runtime.jsonl';runtime.write_text(json.dumps(rt)+'\n')
    crop=tmp_path/'synthetic.png';Image.new('L',(48,40),255).save(crop)
    checkpoint=tmp_path/'checkpoint';checkpoint.write_bytes(b'synthetic checkpoint identity')
    lines=tmp_path/'lines.jsonl';lines.write_text('{"line_id":"synthetic"}\n')
    truth=tmp_path/'truth.json';truth.write_text('{}')
    (tmp_path/'full_s0_v2_test.jsonl').write_text('{"line_id":"synthetic","gt":"ι"}\n')
    (tmp_path/'full_s0_wikisource_human.jsonl').write_text('')
    config=dict(schema='sf1-reading-v1',detector_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        source_sha256={x:owner.digest(owner.ROOT/x) for x in owner.SOURCES},
        shape_model=dict(path=owner.DEFAULT_SHAPE,sha256=owner.digest(owner.DEFAULT_SHAPE)),
        case_model=dict(path='docs/records/labelfix/case_model_S5.json',sha256=owner.digest('docs/records/labelfix/case_model_S5.json')),
        constraint_policy=owner.policy(),r1_checkpoint=dict(path=str(checkpoint),sha256=owner.digest(checkpoint)),
        release_mode='ENSEMBLE_AB',runtime={str(runtime):owner.digest(runtime)})
    cp=tmp_path/'config.json';cp.write_text(json.dumps(config))
    monkeypatch.setattr(p,'P',str(tmp_path)+'/')
    monkeypatch.setattr(p,'load_three_way',lambda split:[dict(line_id='synthetic',model='ι',google='ι',human='ι',crop=str(crop))])
    monkeypatch.setattr(p,'load_alignments',lambda path:{p.crop_key(str(crop)):Alignment('ι',[])})
    monkeypatch.setattr(p,'RUNTIMES',{})
    # A saved page must not refit the detector or run a reader.
    monkeypatch.setattr(owner.I,'analyse',lambda im:pytest.fail('saved page invoked detector'))
    out=tmp_path/'page.html';boxes=tmp_path/'boxes.json'
    monkeypatch.setattr('sys.argv',['owner_pages_build_combined','--out',str(out),'--boxes-out',str(boxes),
        '--reading-config',str(cp),'--runtime',str(runtime),'--gate-mode','ENSEMBLE_AB',
        '--lines',str(lines),'--print-truth',str(truth),'--notes',str(tmp_path/'missing_notes.jsonl')])
    p.main()
    side=json.loads(boxes.read_text());record=side['lines']['synthetic']['line_reading']
    expected=compose_runtime(rt,'ENSEMBLE_AB')
    assert record['evidence_sha256']==expected['evidence_sha256']
    assert all(record['slots'][i]['hold_reasons']==s['hold_reasons'] for i,s in enumerate(expected['slots']))
    assert 'detector_clipped_bottom' in record['slots'][0]['hold_reasons']
    assert side['page_sha256']==owner.digest(out)
