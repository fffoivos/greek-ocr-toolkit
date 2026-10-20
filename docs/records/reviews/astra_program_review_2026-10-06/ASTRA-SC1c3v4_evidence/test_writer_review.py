"""SF6c writer-to-overlay certification checks. All inference is mocked."""
from copy import deepcopy

import pytest
from PIL import Image
from greekocr.labelfix import ink, reading, release_gate as gate
from greekocr.labelfix.ctc_align import Alignment, CharSpan, recognition_fields
from scripts.labelfix import m2_run
from scripts.labelfix.clariden import l1_common, l1_detect, l1e_measure, r1_extract
from scripts.labelfix.clariden.r1_common import rows
from tests.labelfix.test_sf6 import rich, overlay


@pytest.mark.parametrize('writer',['m2','l1'])
@pytest.mark.parametrize('case',['missing','zero','floor','legacy_high','regional_low','scored'])
def test_real_writer_evidence_controls_punctuation_release(tmp_path,monkeypatch,writer,case):
    # Only detector/extraction/model work is mocked. Serialization, regional
    # evidence production and the release overlay execute the real code.
    raw=reading.LineReading('δ',rich('δ')['detector']['slots'],[])
    monkeypatch.setattr(reading,'read_ink',lambda *a,**k:deepcopy(raw))
    monkeypatch.setattr(ink,'analyse',lambda image:None)
    extraction=([],[],[],{},[],{})
    monkeypatch.setattr(r1_extract,'extract_line',lambda *a,**k:extraction)
    monkeypatch.setattr(m2_run,'extract_line',lambda *a,**k:extraction)
    monkeypatch.setattr(m2_run,'reader_predictions',lambda *a,**k:{})
    score={'missing':None,'zero':0.,'floor':.5}.get(case,.9)
    frames=None if case in ('missing','legacy_high') else [.9]*10
    if case=='regional_low':frames[2]=.2
    alignment=Alignment('δ',[CharSpan('δ',0,1,2,10.,18.)],10,1.,40,score,frames)
    if writer=='m2':
        runtime=m2_run.infer_line('x',Image.new('L',(40,20)),alignment,None,None,script_class='greek_poly')
    else:
        image=tmp_path/'line.png';Image.new('L',(40,20)).save(image)
        monkeypatch.setattr(l1_detect,'crop_path',lambda *a:image)
        monkeypatch.setattr(l1_detect,'_STATE',((str(tmp_path),str(tmp_path),'toolkit',False),None))
        l1_detect.chunk((0,[(dict(id='x',crop=str(image)),alignment.to_record())]))
        runtime=next(rows(tmp_path/'shard-00000-detector.jsonl.gz'))
    assert runtime['image_width']==40 and runtime['recognition_confidence']==score
    for mode in gate.MODES:
        result=overlay((gate,l1_common),"δ'",runtime,mode)
        if case=='scored':
            assert (result['status'],result['label'])==('corrected','δ')
            assert result['deletion_checks'][0]['signals']==dict(reader=False,detector=True,recogniser=True)
        else:
            assert result['status']=='hold' and result['changes']==[] and 'label' not in result
            assert result['deletion_checks'][0]['signals']['recogniser'] is False


@pytest.mark.parametrize('case',['missing','zero','legacy_high','scored'])
def test_saved_l1e_and_copy_fields_do_not_upgrade_missing_evidence(case):
    rt=rich('δ')
    if case!='scored':
        rt.pop('recognition_evidence')
        if case=='missing':rt.pop('recognition_confidence')
        elif case=='zero':rt['recognition_confidence']=0.
    meta=dict(rt,font_size={})
    line=dict(line_id='x',recogniser_text='δ',reading='δ',recogniser_slots=rt['detector']['slots'])
    runtime=l1e_measure.saved_runtime(line,meta,{a:[] for a in ('A','B','E')})
    copied=recognition_fields(rt)
    assert runtime['recognition_confidence']==rt.get('recognition_confidence')
    assert runtime['recognition_evidence']==copied['recognition_evidence']
    if case!='scored':
        assert runtime['recognition_evidence']['scored'] is False
        assert runtime['recognition_evidence']['regions']==[]
    for mode in gate.MODES:
        out=overlay((gate,l1_common),"δ'",runtime,mode)
        assert out['status']==('corrected' if case=='scored' else 'hold')
