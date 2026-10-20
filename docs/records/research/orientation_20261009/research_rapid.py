"""Cached RapidOCR 0/180 classifier + independently measured ink text axis.

Direct ONNX inference replicates rapidocr/ch_ppocr_cls/main.py:83-110 and avoids
any automatic model download. The classifier itself is binary, not four-way.
"""
from research_orientation import *
MODEL=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/lib/python3.11/site-packages/rapidocr/models/ch_ppocr_mobile_v2.0_cls_mobile.onnx')
def load_classifier():
    # onnxruntime is absent in the requested Python; OpenCV DNN is installed.
    cv2.setNumThreads(1)
    net=cv2.dnn.readNetFromONNX(str(MODEL));net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV);net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    return net
def forward(session,tensor):
    session.setInput(tensor);return session.forward()[0]
def main():
    start=time.perf_counter();session=load_classifier();loadsec=time.perf_counter()-start
    save('rapid_config.json',dict(model=str(MODEL),sha256=hashlib.sha256(MODEL.read_bytes()).hexdigest(),engine='OpenCV DNN CPU; onnxruntime unavailable',input_shape=[1,3,48,192],load_seconds=loadsec,labels=['0','180'],preprocess='BGR, aspect-preserving resize to H48,W<=192, right zero pad; /127.5-1',axis='geometry.jsonl axis_cw; classifier has no 90/270 classes'))
    axisrecords={(r['id'],r['scope']):r for r in [json.loads(l) for l in (ROOT/'geometry.jsonl').read_text().splitlines()]}
    with (ROOT/'rapid.jsonl').open('w') as f:
        for c in load('testset/manifest.json')['cases']:
            im=Image.open(ROOT/c['path']).convert('RGB');units=[('full',im,c['unit'],c['truth_cw'])]
            if c['kind']=='composite':units.append(('roi',im.crop(c['roi']),c['roi_unit'],c['roi_truth_cw']))
            for scope,x,unit,truth in units:
                start=time.perf_counter();axis=axisrecords[c['id'],scope]['axis_cw'];g=np.asarray(x.rotate(axis,expand=True))[:,:,::-1];h,w=g.shape[:2];neww=min(192,math.ceil(48*w/h));resized=cv2.resize(g,(neww,48)).astype('float32').transpose(2,0,1)/127.5-1
                tensor=np.zeros((1,3,48,192),dtype='float32');tensor[0,:,:,:neww]=resized
                probs=forward(session,tensor);pol=int(np.argmax(probs))*180;pred=(axis+pol)%360
                sec=time.perf_counter()-start;axis_sec=axisrecords[c['id'],scope]['seconds']
                rec=dict(id=c['id'],scope=scope,unit=unit,kind=c['kind'],truth_cw=truth,pred_cw=pred,correct=pred==truth,confidence=float(np.max(probs)),probs=probs.tolist(),axis_cw=axis,seconds=sec+axis_sec,classifier_seconds=sec)
                f.write(json.dumps(rec)+'\n');f.flush();print(c['id'],scope,pred,truth,sec,flush=True)
if __name__=='__main__':main()
