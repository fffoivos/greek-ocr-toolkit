"""Replay only the six requested cycle-3 verification findings; no inference."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.l1_common import overlay
from scripts.labelfix.clariden.r1_common import rows, sha256
from scripts.labelfix import owner_pages_build_combined as page
from scripts.labelfix.box_regression import diff_line
from tests.labelfix.test_sf2 import raw, coverage
from test_c3_scope import clean

ROOT=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
OUT=Path(__file__).resolve().parent
BINDING=dict(detector='s6',r1_sha256='A',policy_sha256='verification-only')


def write(name, value):
    (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def capitals():
    path=OUT/'capital_diaeresis_witnesses.json'
    previous=json.loads(path.read_text());result={}
    for base,witness in previous.items():
        runtime=witness['runtime']
        decision=gate.compose_runtime(runtime,'ENSEMBLE_AB')
        value=overlay(dict(id='synthetic',label=runtime['recogniser_text'],script_class='greek_poly'),
                      runtime,'ensemble_ab',BINDING)
        assert decision['hold_slots'][0]['reasons']==['detector_clipped_top']
        assert value['status']=='hold' and 'label' not in value
        result[base]=dict(original=runtime['recogniser_text'],previous_status=witness['overlay']['status'],
            current_status=value['status'],released_label_present='label' in value,
            hold_slots=decision['hold_slots'],evidence_sha256=decision['evidence_sha256'])
    return dict(saved_input_sha256=sha256(path),cases=result)


def ensemble_page():
    r=clean('ι');r['detector']['slots'][0]['evidence']['clipped_bottom']=True
    r['peer_predictions']['E'][0]['parts']=['subscript']
    page.LINE_TEXT={'synthetic':r['recogniser_text']}
    page.R1={('synthetic',0):r['r1_predictions'][0]};page.COVERAGE={'synthetic':r['coverage']}
    expected=gate.compose_runtime(r,'ENSEMBLE_AB')
    legacy,_=page.combine('synthetic',gate.deserialize(r['detector']),'ENSEMBLE_AB',
        peer_predictions={0:r['peer_predictions']['B'][0]},peer_coverage=r['peer_coverage']['B'])
    bound=gate.bind_runtime(r)
    current,_=page.combine('synthetic',gate.deserialize(r['detector']),'ENSEMBLE_AB',runtime=bound)
    serial=gate.serialize(current)
    assert serial['slots']==expected['slots'] and serial['text']==expected['text']
    assert serial['evidence_sha256']==expected['evidence_sha256']
    assert legacy.slots[0]['hold'] and expected['hold_slots'][0]['reasons']==['detector_clipped_bottom']
    return dict(runtime_status=expected['slots'][0]['label_status'],runtime_reasons=expected['slots'][0]['hold_reasons'],
        complete_page_status=current.slots[0]['label_status'],complete_page_reasons=current.slots[0]['hold_reasons'],
        exact_text_slot_digest_parity=True,evidence_sha256=serial['evidence_sha256'],
        legacy_partial_status=legacy.slots[0]['label_status'],legacy_partial_reasons=legacy.slots[0]['hold_reasons'])


def alias():
    r=clean('δ');r['recogniser_text']='δʼ'
    r['detector']['slots'][0].update(apostrophe=True,word_final=True)
    r['detector']['slots'].append(dict(start=1,end=2,base='ʼ',parts=[],unnamed=[],
        localisation_unknown=False,segmentation_uncertain=False,word_final=False,
        evidence=dict(clipped_top=False,clipped_bottom=False)))
    result=gate.compose_runtime(r,'ENSEMBLE_AB')
    assert result['text']=='δ’' and not result['hold_slots']
    return dict(input=r['recogniser_text'],output=result['text'],hold_slots=result['hold_slots'],
                letter_slots=len(result['slots']),retained_legacy_punctuation=result['geometry']['elision_alias_slots'])


def notes_binding():
    # Exact unbound-notes CLI fixture from the original cycle-3 witness.
    from scripts.labelfix import owner_implicit_changes as mod
    fixture=OUT/'notes_binding_fixture';fixture.mkdir(exist_ok=True)
    paths={};digests={}
    for name,text in [('old','ά'),('new','α')]:
        html=fixture/(name+'.html');html.write_text(text)
        digests[name]=sha256(html)
        side=fixture/(name+'.json')
        side.write_text(json.dumps(dict(page_sha256=digests[name],lines={
            'synthetic':dict(reading=text,line_reading=dict(slots=[
                dict(display_slot=1,bbox=[1,1,3,3])]))})))
        paths[name]=(html,side)
    notes=fixture/'unbound_notes.jsonl'
    notes.write_text('{"line_id":"synthetic","note":""}\n')
    argv=['owner_implicit_changes']
    for name in ('old','new'):
        argv+=['--'+name+'-page',str(paths[name][0]),'--'+name+'-boxes',str(paths[name][1])]
    output=fixture/'result.json'
    assert not output.exists()
    argv+=['--reviewed-page-sha256',digests['old'],'--new-page-sha256',digests['new'],
           '--notes',str(notes),'--out',str(output)]
    saved_argv=sys.argv
    try:
        sys.argv=argv
        try:
            mod.main()
        except ValueError as error:
            message=str(error)
            assert 'binding' in message
        else:
            raise AssertionError('Unbound notes were accepted')
    finally:
        sys.argv=saved_argv
    assert not output.exists()
    return dict(exception='ValueError',message=message,approval_output_created=False,
                fixture='notes_binding_fixture')


def old_uncertainty_and_boxes():
    results={}
    for name,raw_reading,cov in [
        ('r1_unknown',raw(),[dict(start=0,scored=True,evidence_state='UNKNOWN',uncertainty=['no_pixel_evidence'],reason=None)]),
        ('r1_outside',raw(),[dict(start=0,scored=True,evidence_state='UNKNOWN',uncertainty=['out_of_image_span'],reason=None)]),
        ('segmentation_uncertain',raw(segmentation_uncertain=True),[]),
        ('clipped_detector',raw(evidence=dict(above=[],below=[],clipped_top=True,clipped_bottom=True)),[]),
    ]:
        runtime=dict(recogniser_text='ά',detector=gate.serialize(raw_reading),
                     r1_predictions=[dict(start=0,parts=[],mark_probabilities={})],coverage=cov)
        results[name]={}
        for mode in ('PRESENCE','FULL'):
            composed=gate.compose_runtime(runtime,mode)
            value=overlay(dict(id='synthetic',label='ά',script_class='greek_poly'),runtime,mode.lower(),BINDING)
            assert composed['hold_slots'] and value['status']=='hold' and 'label' not in value
            results[name][mode]=dict(text=composed['text'],hold_slots=composed['hold_slots'],overlay_status=value['status'])
    # Exact cycle-2 identical-rectangle/different-owner counterexample.
    old=dict(reading='αα',boxes=[dict(kind='above',bbox=[5,2,8,5],display_slot=1)],
             letter_zones=[dict(display_slot=1,mark_zone=[0,0,10,10])])
    new=deepcopy(old);new['boxes'][0]['display_slot']=2;new['letter_zones'][0]['display_slot']=2
    delta=diff_line(old,new,.3)
    assert len(delta['owner_changed'])==1 and not delta['lost'] and not delta['added']
    results['unchanged_box_changed_owner']=delta
    return results


def owner92():
    # Same saved records as cycle 3; only the adapter envelope changes for SF4.
    base=Path('/tmp/SF2-verified-20261017/owner')
    conf=json.loads((base/'combined_config.json').read_text())
    side=json.loads((base/'combined_boxes.json').read_text())
    assert side['page_sha256']==sha256(base/'combined.html')
    predictions={}
    for path,digest in conf['r1_predictions'].items():
        path=ROOT/path;assert sha256(path)==digest
        for r in rows(path):predictions[r['line_id'],r['start']]=r
    for path,digest in conf['r1_coverage'].items():assert sha256(path)==digest
    cov={r['line_id']:r['coverage'] for r in rows(base/'coverage.jsonl')}
    page.LINE_TEXT={r['line_id']:r['recogniser_text'] for r in rows(base/'S6_scoring_lines.jsonl')}
    outputs={}
    for lid,s in side['lines'].items():
        runtime=gate.bind_runtime(dict(recogniser_text=page.LINE_TEXT[lid],detector=s['raw_line_reading'],
            r1_predictions=[dict(p,start=start) for (key,start),p in predictions.items() if key==lid],coverage=cov[lid]))
        # This historical A-only PRESENCE fixture contains no B/E predictions.
        # None are invented; the separate ensemble witness has the real peers.
        expected=gate.compose_runtime(runtime,'PRESENCE')
        actual,_=page.combine(lid,gate.deserialize(runtime['detector']),'PRESENCE',runtime=runtime)
        actual=gate.serialize(actual)
        assert actual['text']==expected['text'] and actual['slots']==expected['slots']
        assert actual['evidence_sha256']==expected['evidence_sha256']
        outputs[lid]=expected
    prior=ROOT/'docs/reviews/astra_program_review_2026-10-06/ASTRA-SC1c2_evidence/cn1_unheld_coverage.json'
    checked=[]
    for kind,values in json.loads(prior.read_text()).items():
        if not isinstance(values,list):continue
        for lid,start,_ in values:
            slot=next(s for s in outputs[lid]['slots'] if s['start']==start)
            assert slot['hold']
            checked.append(dict(kind=kind,line_id=lid,start=start,reasons=slot['hold_reasons']))
    quotes={lid:outputs[lid]['text'] for lid in ('384c3f89-p000030-l0010','384c3f89-p000030-l0029')}
    assert all(text.startswith('“') for text in quotes.values())
    return dict(exact_text_slot_digest_parity_lines=len(outputs),held_former_coverage_witnesses=checked,
                restored_quote_outputs=quotes,native_crops_decoded=0)


if __name__=='__main__':
    results=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                 policy=gate.policy_binding(),scope='Only C3-B01/M01/N01 and C2-N02/B01/M02 witnesses',
                 network=False,ctc_forward_passes=0,r1_forward_passes=0,native_crops_decoded=0)
    for name,fn in [('capital_saved',capitals),('ensemble_page',ensemble_page),('modifier_alias',alias),
                    ('notes_binding',notes_binding),
                    ('cycle2_uncertainty_boxes',old_uncertainty_and_boxes),('owner92',owner92)]:
        result=fn();write(name+'.json',result);results[name]=dict(output=name+'.json',sha256=sha256(OUT/(name+'.json')))
        print(name+' verified',flush=True)
    write('scoped_replay_receipt.json',results)
