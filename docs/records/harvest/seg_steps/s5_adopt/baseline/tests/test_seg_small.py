"""Owner S4 boundaries and component/turn contract, with no extra tool rule."""
from pathlib import Path
import importlib.util,hashlib,json
import pytest
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('small_crop',R/'greekocr/harvest/filtering_assets/crop-tools.py');crop=importlib.util.module_from_spec(spec);spec.loader.exec_module(crop)
@pytest.mark.parametrize('chars,w,h,expected',[(8,600,100,True),(9,600,100,False),(8,601,100,False),(8,100,600,True)])
def test_definition(chars,w,h,expected):assert crop.is_small_segment(chars,w,h)==expected

def test_all_components_including_diacritic_and_isolated_speck():
 cs=[dict(index=1,bbox=[10,10,20,25],role='letter'),dict(index=2,bbox=[12,4,15,6],role='mark'),dict(index=3,bbox=[35,30,36,31],role='speck')]
 f=crop.small_segment_features(40,35,cs)
 assert f['candidate_text_box']==dict(bbox=[10,4,36,31],width=26,height=27)
 assert f['row_frame_text_box']['length']==26
 assert f['row_frame_text_box']['height']==27

@pytest.mark.parametrize('turned',[False,True])
def test_processed_box_and_padding(turned,tmp_path):
 from greekocr.harvest.line_pipeline_native import NativeSegmenter
 im=Image.new('L',(80,40),255);d=ImageDraw.Draw(im)
 d.rectangle((10,12,18,27),fill=0);d.rectangle((26,12,35,27),fill=0);d.rectangle((12,4,14,6),fill=0);d.rectangle((63,32,65,34),fill=0)
 if turned:im=im.transpose(Image.Transpose.ROTATE_90)
 p=tmp_path/'small.png';im.save(p)
 w=NativeSegmenter({'segmentation':{'version':'0.9-s4'}},R/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
 cs=[];orig=w.crop_tools.line_inventory
 def capture(g,lines,components,angle):cs.extend(components);return orig(g,lines,components,angle)
 w.crop_tools.line_inventory=capture
 try:z=w(dict(id='synthetic',parent_id='test',split='unassigned',crop_path=str(p),crop_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),raw_text='ab',script_class='pooled'))
 finally:w.close()
 box=[min(c['bbox'][0] for c in cs),min(c['bbox'][1] for c in cs),max(c['bbox'][2] for c in cs),max(c['bbox'][3] for c in cs)]
 assert z['evidence']['box_evidence']['bbox']==box==[10,4,66,35]
 assert z['frame']['normalization_cw']==(270 if turned else 0)
 p=z['evidence']['padding_evidence'];assert p['upright_box_height']==p['row_frame_height']==31
 assert p['total_padding_line_heights']==(40-31)/31

@pytest.mark.parametrize('whole,complete,verdict',[(0,False,'PASS'),(3,False,'DROP'),(0,True,'DROP')])
def test_missing_main_never_bypasses_positive_gate_drop(whole,complete,verdict):
 from greekocr.harvest.line_pipeline_native import NativeSegmenter
 w=NativeSegmenter({'segmentation':{'version':'0.9-s4'}},R/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
 try:
  z=w.service.call(dict(operation='decide',policy_sha256=w.policy_sha,evidence=dict(small_segment=True,gate_only=True,lines=[dict(index=1,side='above',votes=6,whole_words=whole,cutoff_words=0,complete=complete)])))
  assert z['verdict']==verdict
 finally:w.close()

@pytest.mark.parametrize('turned',[False,True])
def test_non_small_native_result_is_byte_identical_to_s3(turned,tmp_path):
 # Fresh old/current native runs, independently of the saved population readback.
 spec=importlib.util.spec_from_file_location('s4_test_replay',R/'docs/harvest/seg_steps/s4/replay.py')
 replay=importlib.util.module_from_spec(spec);spec.loader.exec_module(replay)
 im=Image.new('L',(80,40),255);pen=ImageDraw.Draw(im)
 for x in (10,26,42,58):pen.rectangle((x,12,x+7,27),fill=0)
 if turned:im=im.transpose(Image.Transpose.ROTATE_90)
 path=tmp_path/'non-small.png';im.save(path)
 row=dict(id='non-small',parent_id='test',split='unassigned',crop_path=str(path),crop_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw_text='abcdefghi',script_class='pooled')
 old,new=replay.worker('s3'),replay.worker()
 try:a,b=old(row),new(row)
 finally:old.close();new.close()
 assert replay.canonical(replay.norm(a))==replay.canonical(replay.norm(b))
 assert replay.canonical(a['evidence'])==replay.canonical(b['evidence'])
