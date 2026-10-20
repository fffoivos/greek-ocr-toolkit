"""Review-only regression witnesses. Expected failures at 63119b84; no inference.

All pixels here are synthetic arrays. The repository is never modified.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np
import pytest

from greekocr.labelfix import ink as I
from greekocr.labelfix.reading import LineReading
from greekocr.labelfix.release_gate import compose_runtime, deserialize, serialize
from scripts.labelfix.clariden.l1_common import overlay


def clean(base='ι'):
    coverage = [dict(start=0, base=base, scored=True,
                     evidence_state='unadjudicated', uncertainty=[])]
    prediction = [dict(start=0, base=base, parts=[])]
    slot = dict(start=0, end=1, base=base, parts=[], unnamed=[],
                localisation_unknown=False, segmentation_uncertain=False,
                word_final=False, evidence=dict(meanline=30, xh=20,
                                               clipped_top=False, clipped_bottom=False))
    return dict(id='synthetic', recogniser_text=base,
                detector=serialize(LineReading(base, [slot], [])),
                r1_predictions=prediction, coverage=coverage,
                peer_predictions={a:deepcopy(prediction) for a in ('B','E')},
                peer_coverage={a:deepcopy(coverage) for a in ('B','E')})


def capital_diaeresis(base='Ι'):
    # Source dots originally extend two rows above this cropped view. Two
    # retained dot fragments touch row zero over the capital's body, not left
    # of it. Evidence is produced by the real deterministic geometry helper.
    lab = np.zeros((40, 48), int)
    lab[8:29, 19:23] = 1
    lab[0:3, 18:21] = 2
    lab[0:3, 24:27] = 3
    components = []
    for k in (1, 2, 3):
        ys, xs = np.where(lab == k)
        x0, x1, y0, y1 = int(xs.min()), int(xs.max()+1), int(ys.min()), int(ys.max()+1)
        components.append(NS(index=k, x0=x0, x1=x1, y0=y0, y1=y1,
                             w=x1-x0, h=y1-y0, cx=(x0+x1)/2, cy=(y0+y1)/2,
                             role='letter' if k == 1 else 'mark', darkness=20.,
                             area=int((lab == k).sum())))
    ink = I.CropInk(np.where(lab > 0, 20., 255.), lab > 0, lab, 20.,
                   np.full(48, 8.), np.full(48, 28.), components, 255., 48, 40, 20.)
    ink.case_info = {1:dict(case_class='capital')}
    region = dict(component=components[0], component_ids=[1],
                  region_bounds=[19,23], case_class='capital')
    ev = I.mark_evidence(ink, 19, 23, base_letter=base,
                         certified_body=(19,23), letter_region=region)
    r = clean(base)
    r['recogniser_text'] = base + '\u0308'
    r['detector']['slots'][0].update(parts=['dialytika'], evidence=ev.to_record())
    return r


@pytest.mark.parametrize('base', ['Ι','Υ'])
def test_clipped_capital_overhead_diaeresis_must_hold(base):
    r = capital_diaeresis(base)
    ev = r['detector']['slots'][0]['evidence']
    assert ev['clipped_top'] and len(ev['above']) == 2
    assert all(b['touches_border'] for b in ev['above'])
    result = overlay(dict(id='synthetic', label=r['recogniser_text'], script_class='greek_poly'),
                     r, 'ensemble_ab', dict(detector='s6', r1_sha256='A', policy_sha256='test'))
    assert result['status'] == 'hold', result


def test_owner_page_must_match_runtime_for_diagnostic_E_below_evidence(monkeypatch):
    from scripts.labelfix import owner_pages_build_combined as p
    r = clean('ι')
    r['detector']['slots'][0]['evidence']['clipped_bottom'] = True
    r['peer_predictions']['E'][0]['parts'] = ['subscript']
    monkeypatch.setattr(p, 'LINE_TEXT', {'synthetic':r['recogniser_text']})
    monkeypatch.setattr(p, 'R1', {('synthetic',0):r['r1_predictions'][0]})
    monkeypatch.setattr(p, 'COVERAGE', {'synthetic':r['coverage']})
    expected = compose_runtime(r, 'ENSEMBLE_AB')
    actual, _ = p.combine('synthetic', deserialize(r['detector']), 'ENSEMBLE_AB',
                           peer_predictions={0:r['peer_predictions']['B'][0]},
                           peer_coverage=r['peer_coverage']['B'])
    assert expected['hold_slots'][0]['reasons'] == ['detector_clipped_bottom']
    assert actual.slots[0]['label_status'] == expected['slots'][0]['label_status']


def test_implicit_changes_must_require_notes_to_page_binding(tmp_path, monkeypatch):
    from scripts.labelfix import owner_implicit_changes as mod
    paths = {}
    digests = {}
    for name, text in [('old','ά'), ('new','α')]:
        page = tmp_path/(name+'.html'); page.write_text(text)
        digests[name] = hashlib.sha256(page.read_bytes()).hexdigest()
        side = tmp_path/(name+'.json')
        side.write_text(json.dumps(dict(page_sha256=digests[name], lines={
            'synthetic':dict(reading=text, line_reading=dict(slots=[
                dict(display_slot=1, bbox=[1,1,3,3])]))})))
        paths[name] = (page, side)
    notes = tmp_path/'unbound_notes.jsonl'
    notes.write_text('{"line_id":"synthetic","note":""}\n')
    argv = ['owner_implicit_changes']
    for name in ('old','new'):
        argv += ['--'+name+'-page',str(paths[name][0]),'--'+name+'-boxes',str(paths[name][1])]
    argv += ['--reviewed-page-sha256',digests['old'],'--new-page-sha256',digests['new'],
             '--notes',str(notes),'--out',str(tmp_path/'result.json')]
    monkeypatch.setattr('sys.argv', argv)
    with pytest.raises(ValueError, match='binding'):
        mod.main()


def test_modifier_apostrophe_alias_composes_without_slot_mismatch():
    # U+02BC is isalpha(), so recogniser_slots creates a slot for it. SF3's
    # elision renderer drops that codepoint but leaves its slot behind.
    r = clean('δ')
    r['recogniser_text'] = 'δʼ'
    r['detector']['slots'][0].update(apostrophe=True, word_final=True)
    r['detector']['slots'].append(dict(start=1,end=2,base='ʼ',parts=[],unnamed=[],
        localisation_unknown=False,segmentation_uncertain=False,word_final=False,
        evidence=dict(clipped_top=False,clipped_bottom=False)))
    result = compose_runtime(r,'ENSEMBLE_AB')
    assert result['text'] == 'δ’'
