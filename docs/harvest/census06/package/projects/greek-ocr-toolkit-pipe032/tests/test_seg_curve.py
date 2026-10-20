"""Owner S3 curve-frame measurement checks; all fixtures are local."""
import importlib.util
from pathlib import Path
from tests._paths import SEG_STEPS
import numpy as np
import pytest
from PIL import Image

R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('s3_crop_tools',R/'greekocr/harvest/filtering_assets/crop-tools.py')
crop=importlib.util.module_from_spec(spec);spec.loader.exec_module(crop)
spec=importlib.util.spec_from_file_location('s2_crop_tools',SEG_STEPS / 's3/baseline/greekocr/harvest/filtering_assets/crop-tools.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)

@pytest.mark.parametrize('angle',[0,1.2,-3])
def test_straight_curve_is_digit_exact(angle):
 w,h=350,80
 yy,xx=np.indices((h,w));base=48+np.tan(np.radians(angle))*(np.arange(w)-w/2)
 ink=(xx>=13)&(xx<337)&(yy>=base[None,:]-18)&(yy<base[None,:])
 ys,xs=np.nonzero(ink);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 args=dict(width=w,height=h,components=[dict(index=1,bbox=box,role='letter',area=int(ink.sum()))],
  ink_box=box,ink_pixels=int(ink.sum()),xheight=18,xheight_source='test',support_count=20,chars=50,
  labels=ink.astype(int),angle_deg=angle)
 assert crop.features_from_observation(**args,base_curve=base,base_is_straight=True)==old.features_from_observation(**args)


def test_circular_arc_analytic_length():
 radius=1000.;mid=300.;x=np.arange(601,dtype=float)
 base=np.sqrt(radius**2-(x-mid)**2)
 theta=np.linspace(-.24,.24,481)
 px=mid+radius*np.sin(theta);py=radius*np.cos(theta)
 s,n,half,amb=crop.curve_coordinates(px,py,base)
 assert abs((s[-1]-s[0])-radius*(theta[-1]-theta[0]))<1
 assert np.max(np.abs(n))<1
 assert amb==0


def test_curved_ink_pixel_cell_box():
 w,h=400,140;radius=700.;x=np.arange(w,dtype=float)
 base=105-radius+np.sqrt(radius**2-(x-200)**2)
 yy,xx=np.indices((h,w));ink=(xx>25)&(xx<375)&(yy>=base[None,:]-20)&(yy<base[None,:])
 ys,xs=np.nonzero(ink);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 args=dict(width=w,height=h,components=[dict(index=1,bbox=box,role='letter',area=int(ink.sum()))],
  ink_box=box,ink_pixels=int(ink.sum()),xheight=20,xheight_source='test',support_count=20,chars=50,
  labels=ink.astype(int),angle_deg=0)
 rf=crop.features_from_observation(**args,base_curve=base,base_is_straight=False)['row_frame_text_box']
 assert rf['height']<box[3]-box[1]
 assert rf['coordinates']=='base_curve_arc_length_and_normal'
 s,n,half,amb=crop.curve_coordinates(xs+.5,ys+.5,base)
 assert rf['sn_box']==[float((s-half).min()),float((n-half).min()),float((s+half).max()),float((n+half).max())]


def test_ambiguous_foot_uses_first_in_curve_order():
 # V with two distinct, equally near feet from (1,1).
 s,n,half,amb=crop.curve_coordinates(np.array([1.]),np.array([1.]),np.array([0.,2.,0.]))
 assert amb==1
 assert s[0]==pytest.approx(3/np.sqrt(5))
 assert n[0]<0

@pytest.mark.parametrize('turned',[False,True])
@pytest.mark.parametrize('degree',[1,2])
def test_horizontal_and_s2_turned_crops_reach_curve_measurement(turned,degree,monkeypatch,tmp_path):
 from greekocr.harvest.line_pipeline_native import NativeSegmenter
 from greekocr.glyphs.orientation import QuarterTurn
 import greekocr.glyphs.components as components
 import greekocr.glyphs.baseline as baseline
 from types import SimpleNamespace
 w,h=160,60;x=np.arange(w,dtype=float);base=40+.001*(x-80)**2
 yy,xx=np.indices((h,w));ink=(xx>15)&(xx<145)&(yy>=base[None,:]-12)&(yy<base[None,:])
 ys,xs=np.nonzero(ink);box=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
 g=SimpleNamespace(width=w,height=h,ink=ink,labels=ink.astype(int),letter_w=8.,
  band=components.Band(base-12,base,12.,20,tuple((float(i),float(base[i]),'bottom') for i in range(20,141,6)),degree=degree,xh_source='test',curve_is_straight=False),
  components=[SimpleNamespace(index=1,x0=box[0],y0=box[1],x1=box[2],y1=box[3],role='letter',area=int(ink.sum()),touches=[],w=box[2]-box[0],h=box[3]-box[1],cx=(box[0]+box[2])/2)])
 line=SimpleNamespace(side='main',visible=1.,votes=20.,x0=20,x1=140,ascender=base-18,mean=base-12,base=base,descender=base+3)
 seen=[]
 def detect(image):
  seen.append(image.size);return g
 monkeypatch.setattr(components,'line_glyphs',detect);monkeypatch.setattr(baseline,'text_lines',lambda g:[line])
 image=Image.fromarray(np.where(ink,0,255).astype(np.uint8))
 if turned:image=image.transpose(Image.Transpose.ROTATE_90)
 path=tmp_path/'curve.png';image.save(path)
 import hashlib
 row=dict(id='synthetic',parent_id='test',split='unassigned',crop_path=str(path),crop_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),raw_text='abcdefghi',script_class='pooled')
 worker=NativeSegmenter({'segmentation':{'version':'0.9-s3'}},R/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict')
 try:answer=worker(row)
 finally:worker.close()
 assert seen==[(w,h)]
 assert answer['frame']['normalization_cw']==(270 if turned else 0)
 rf=answer['evidence']['box_evidence']['row_frame']
 assert rf['coordinates']=='base_curve_arc_length_and_normal'
 assert answer['evidence']['padding_evidence']['row_frame_height']==rf['height']


def test_circular_arc_pixel_cell_length_within_one_pixel():
 radius=1000.;mid=300.;base=1100.-np.sqrt(radius**2-(np.arange(601)-mid)**2)
 labels=np.zeros((180,601),dtype=int)
 xx=np.arange(100,501);yy=np.rint(base[xx]-.5).astype(int);labels[yy,xx]=1
 box,amb=crop.curve_tight_box([dict(index=1)],labels,base)
 analytic=radius*(np.arcsin((501.-mid)/radius)-np.arcsin((100.-mid)/radius))
 assert abs((box[2]-box[0])-analytic)<1
 assert amb==0
