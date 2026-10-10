"""S1: isolated content-pinned Paddle DB adapter, single-thread CPU ONNX."""
from time import perf_counter
import cv2, numpy as np, onnxruntime as ort
from .paddle_db import DBPostProcess, DetResizeForTest, NormalizeImage
from .manifest import MODEL

DEFAULT=dict(thresh=.2,box_thresh=.45,unclip_ratio=1.4,box_type='quad',max_candidates=3000)
VARIANTS={'quad':DEFAULT,'poly':dict(DEFAULT,box_type='poly')}
for name,k,v in [('threshold_low','thresh',.1),('threshold_high','thresh',.3),
                 ('score_low','box_thresh',.35),('score_high','box_thresh',.55),
                 ('expansion_low','unclip_ratio',1.),('expansion_high','unclip_ratio',1.8)]:
    VARIANTS[name]=dict(VARIANTS['poly'],**{k:v})

def preprocess(gray,long_side=960):
    rgb=cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB) if gray.ndim==2 else cv2.cvtColor(gray,cv2.COLOR_BGR2RGB)
    resized,shape=DetResizeForTest(limit_side_len=long_side,limit_type='max')([rgb])
    arr=NormalizeImage(order='hwc')(resized)[0]
    return np.ascontiguousarray(arr.transpose(2,0,1)[None],np.float32),shape[0]

class Detector:
    def __init__(self):
        t=perf_counter(); opts=ort.SessionOptions(); opts.intra_op_num_threads=1; opts.inter_op_num_threads=1
        opts.execution_mode=ort.ExecutionMode.ORT_SEQUENTIAL
        self.session=ort.InferenceSession(str(MODEL),sess_options=opts,providers=['CPUExecutionProvider'])
        self.name=self.session.get_inputs()[0].name; self.startup_s=perf_counter()-t
    def infer(self,gray,long_side=960):
        t=perf_counter(); x,shape=preprocess(gray,long_side); pre=perf_counter()-t
        t=perf_counter(); pm=self.session.run(None,{self.name:x})[0][0,0]; infer=perf_counter()-t
        return pm,dict(preprocess_s=pre,inference_s=infer,tensor=list(x.shape),map_shape=list(pm.shape),shape=shape.tolist())

def postprocess(pm,size,config=None,genealogy=False):
    c=dict(DEFAULT if config is None else config); db=DBPostProcess(**c)
    w,h=size; segmentation=(pm>c['thresh']).astype(np.uint8)
    fn=db.polygons_from_bitmap if c['box_type']=='poly' else db.boxes_from_bitmap
    boxes,scores=fn(pm,segmentation,w,h,c['box_thresh'],c['unclip_ratio'])
    items=[dict(polygon=np.asarray(b,float).tolist(),baseline=None,score=float(s),score_source='PP-OCRv6 small DB map') for b,s in zip(boxes,scores)]
    if not genealogy: return items
    contours,_=cv2.findContours(segmentation,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    records=[]
    for i,contour in enumerate(contours[:c['max_candidates']]):
        q,short=db.get_mini_boxes(contour); q=np.asarray(q,np.float32)
        if c['box_type']=='poly':
            q=cv2.approxPolyDP(contour,.002*cv2.arcLength(contour,True),True).reshape(-1,2).astype(np.float32)
        score=db.box_score_fast(pm,q)
        reason='accepted candidate'
        if c['box_type']=='quad' and short<db.min_size: reason='map short side'
        elif len(q)<4: reason='fewer than four contour vertices'
        elif score<c['box_thresh']: reason='score'
        else:
            expanded=db.unclip(q,c['unclip_ratio'])
            if len(expanded)==0: reason='empty expansion'
            elif c['box_type']=='poly' and len(expanded)>1: reason='multiple expansion paths'
            elif db.get_mini_boxes(np.asarray(expanded).reshape(-1,1,2).astype(np.float32))[1]<db.min_size+2: reason='expanded map short side'
        records.append(dict(id=i,contour=(contour.reshape(-1,2)*[w/pm.shape[1],h/pm.shape[0]]).tolist(),score=float(score),reason=reason,discounted=reason!='accepted candidate'))
    return items,records
