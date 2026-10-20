"""Correct physical ownership hypotheses from an explicitly offline adapter.

The live i2 consumer failed final raster qualification and is not installed.
These tests validate its compatible inputs, not a default font/crop gain.
"""
from pathlib import Path
import json
import cv2
import numpy as np
import pytest
from ..shared import geometry_rows as rows
from ..evidence.r8_font_guides import measure,choose


def actual(index):
    meta=json.loads(Path(__file__).with_name('font_guides_native.json').read_text())
    case=meta['cases'][index];z=np.load(Path(__file__).with_name('font_guides_native.npz'))
    k=case['fixture'];gray=z[f'gray{k}'];item=dict(polygon=z[f'polygon{k}'].tolist())
    ctx={};record=rows.native(gray,item,float(z[f'height{k}']),prepared=ctx)
    return ctx,record


@pytest.mark.parametrize('index,mark,body,track',[(0,147,77,3),(14,159,80,0),(17,95,50,3)])
def test_conditional_fit_proposes_correct_lower_body_without_class_qualification(index,mark,body,track):
    ctx,record=actual(index);guides=measure(ctx,record)
    legacy=rows.mark_bodies(*ctx['centres'][mark],ctx['body_boxes'],ctx['height'])
    candidates,receipt=choose(ctx,guides,mark,legacy_bodies=legacy)
    assert candidates==[body] and receipt['owner']['track']==track
    guide=next(g for g in guides if g['track']==track)
    assert guide['status']!='unknown' and not {'baseline','meanline'} & set(guide['borrowed'])
    assert guide['contact_component_ids']['baseline'] and guide['contact_component_ids']['meanline']
    assert receipt['owner']['donors']  # observed numeric contacts, not class truth
    assert mark not in guide['component_ids']  # disputed mark cannot fit itself
    assert all(guide['finite_x'][0]<=(ctx['stats'][k,0]+ctx['stats'][k,2]/2)<guide['finite_x'][1]
               for k in guide['component_ids'])  # no silently clamped outside classes


def test_adapter_uses_native_pixels_and_labels_without_reprocessing(monkeypatch):
    ctx,record=actual(14)
    def repeated(*args,**kwargs):raise AssertionError('same-native remap/threshold/CC must not repeat')
    monkeypatch.setattr(cv2,'connectedComponentsWithStats',repeated)
    monkeypatch.setattr(cv2,'GaussianBlur',repeated)
    monkeypatch.setattr(rows,'strip',repeated)
    guides=measure(ctx,record)
    guide=next(g for g in guides if g['track']==0)
    assert all(q['native_labels'] for q in guide['contact_component_ids']['meanline'])


@pytest.mark.parametrize('index,marks',[(3,[83,84,86]),(9,[66]),(1,[81])])
def test_specks_and_unsupported_competing_classes_remain_unknown(index,marks):
    ctx,record=actual(index);guides=measure(ctx,record)
    for mark in marks:
        legacy=rows.mark_bodies(*ctx['centres'][mark],ctx['body_boxes'],ctx['height'])
        candidates,receipt=choose(ctx,guides,mark,legacy_bodies=legacy)
        assert candidates is None and not receipt['accepted']


@pytest.mark.xfail(strict=True,reason='FONT: original fused-neck evidence labels a real letter apex/stem as an accent contact')
@pytest.mark.parametrize('index,track,label',[(14,0,162),(17,0,32),(17,3,102)])
def test_letter_apex_stem_is_not_an_upper_mark_class_contact(index,track,label):
    ctx,record=actual(index);guides=measure(ctx,record)
    guide=next(g for g in guides if g['track']==track)
    # Unresized original/native pixels and source-bound contact panels identify
    # these as letter strokes. The failed assertion tests the actual reusable
    # evidence calculation; no synthetic always-false expression is used.
    assert label in guide['component_ids']
    assert not any(label in q['native_labels'] for q in guide['contact_component_ids']['accent_top'])
