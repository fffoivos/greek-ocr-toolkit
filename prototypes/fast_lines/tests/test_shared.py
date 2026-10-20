import json
from pathlib import Path
import cv2,numpy as np,pytest
from prototypes.fast_lines.shared import geometry as g
from prototypes.fast_lines.shared.contracts import RegionRequest,merge_requests,deduplicate,rect
from prototypes.fast_lines.shared.detector import preprocess,postprocess,DEFAULT
from prototypes.fast_lines.shared.image_evidence import ImageEvidence,stroke_features
from prototypes.fast_lines.shared.manifest import load
from prototypes.fast_lines.shared.references import import_ours
from prototypes.fast_lines.shared.review import overlay,write_result,detector_record
from prototypes.fast_lines.shared.timing import Registry
from prototypes.fast_lines.shared.scheduler import scout
from prototypes.fast_lines.shared.perturbations import variants

def test_scope_rejects_unapproved_directory(tmp_path):
    p=tmp_path/'m.json'; p.write_text(json.dumps({'pages':[{'path':'.astra/elsewhere/x.png'}]}))
    with pytest.raises(ValueError): load(p)

def test_preprocess_size_and_channels():
    x,s=preprocess(np.full((320,640),255,np.uint8)); assert x.shape==(1,3,320,640)
    assert np.allclose(x[0,:,0,0],(1-np.array([.485,.456,.406]))/[.229,.224,.225])

def test_detector_transform_and_genealogy():
    p=np.zeros((80,100),np.float32); p[20:30,15:80]=.9
    a,trace=postprocess(p,(1000,800),genealogy=True)
    assert len(a)==1 and a[0]['baseline'] is None and trace[0]['reason']=='accepted candidate'
    assert np.asarray(a[0]['polygon'])[:,0].max()>790

def test_contrast_and_lazy_stroke():
    im=np.full((80,180),230,np.uint8); im[20:40,40:48]=80
    e=ImageEvidence(im,20); assert 'paper' not in e.__dict__
    assert e.contrast[25,44]>.5 and e.persistence[25,44]==3
    assert e.stroke['distance'].max()>0

def test_holes_and_endpoints():
    im=np.zeros((30,30),np.uint8); cv2.rectangle(im,(5,5),(24,24),1,2)
    s=stroke_features(im); assert s['holes']==1 and s['skeleton'].sum()>0

def test_geometry_scale_and_path():
    item={'polygon':rect([10,20,80,40])}; a=np.zeros((100,100),np.float32); a[30,:]=1
    strip,x,y,o=g.sample_strip(a,item,(100,100),10)
    path=g.continuous_path(strip); assert np.max(abs(o[path]))<1
    assert g.mask([item],(10,10),(100,100)).sum()>0

def test_robust_fit():
    x=np.linspace(0,1,40); y=3+2*x; y[3]=100
    c=g.robust_fit(x,y); assert np.allclose(c,[3,2],atol=.01)

def test_requests_transitive_merge():
    rs=[RegionRequest(str(i),b,'missing',[str(i)]) for i,b in enumerate([[0,0,2,2],[4,0,6,2],[1,0,5,2]])]
    out=merge_requests(rs); assert len(out)==1 and out[0]['bbox']==[0,0,6,2]

def test_dedup():
    q={'polygon':rect([0,0,10,10])}; keep,conf=deduplicate([q],[q]); assert len(keep)==1 and len(conf)==1

def test_reference_filters_discounts(tmp_path):
    p=tmp_path/'o.json'; q=dict(x0=0,x1=10,top=[1,1],bottom=[3,3],baseline=[2,2])
    p.write_text(json.dumps([q,dict(q,discounted=True)])); assert len(import_ours(p))==1

def test_discounted_never_drawn():
    im=np.full((30,30),255,np.uint8); q={'polygon':rect([2,2,20,20]),'discounted':True}
    assert np.array_equal(overlay(im,[q]),overlay(im))

def test_all_detector_exports_clip_without_mutating_candidates():
    q=dict(polygon=rect([-3,-4,120,90]),baseline=None,score=None)
    data=detector_record(dict(page='synthetic',image_size=[100,80]),[q,dict(q,discounted=True)],.1)
    assert len(data['items'])==1 and g.bbox(data['items'][0])==[0,0,100,80]
    assert g.bbox(q)==[-3,-4,120,90]

def test_registry_reuse_and_failure(tmp_path):
    r=Registry(tmp_path)
    with r.claim('a','b',{},'s') as event: assert event is not None
    with r.claim('a','b',{},'s') as event: assert event is None
    with r.claim('a','b',{},'s',repeat=1) as event: assert event is not None

def test_empty_output_wakes_scout():
    s=scout(np.full((100,100),255,np.uint8),np.zeros((32,32),np.float32),[])
    assert s['trigger'] and 'empty detector' in s['reasons']

def test_perturbations_are_reproducible():
    im=np.full((40,100),255,np.uint8); im[15:25,10:90]=0
    a,b=variants(im,10),variants(im,10)
    assert set(a)=={'control','fade','blur','break_strokes','thicken','curl','shift'}
    assert all(np.array_equal(a[k][0],b[k][0]) for k in a)
    assert np.array_equal(a['control'][0],im) and a['curl'][1].max()>0

def test_blur_and_thickening_store_actual_pixel_changes():
    im=np.full((80,160),255,np.uint8); im[25:50,40:60]=0
    for name in ('blur','thicken'):
        altered,change=variants(im,25)[name]
        assert np.array_equal(change,abs(altered.astype(np.int16)-im.astype(np.int16)))
        assert np.count_nonzero(change)>0
