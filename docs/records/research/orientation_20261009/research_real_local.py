"""Manually image-labelled, mixed-orientation crops on the real table page."""
from research_orientation import *
from research_rapid import MODEL,load_classifier,forward
ANNOTATIONS=[dict(id='real_title',unit='line',box=[180,487,320,1907],truth_cw=270,reading='Περιληπτικὴ σημείωσις ...'),
             dict(id='real_header',unit='word',box=[1270,3922,1530,4037],truth_cw=180,reading='Καπνοῦ'),
             dict(id='real_folio',unit='word',box=[1610,187,1810,297],truth_cw=0,reading='88 —',note='Digits can be 180-degree ambiguous; do not infer letter orientation from this alone')]
def main():
    im=Image.open(ROOT/'pages'/f'{REAL}.png').convert('RGB');out=[]
    sess=load_classifier()
    for ann in ANNOTATIONS:
        crop=im.crop(ann['box']);crop.save(ROOT/(ann['id']+'.png'))
        geo=geometry(crop);axis=geo['axis_cw'];start=time.perf_counter();g=np.asarray(crop.rotate(axis,expand=True))[:,:,::-1];h,w=g.shape[:2];neww=min(192,math.ceil(48*w/h));v=cv2.resize(g,(neww,48)).astype('float32').transpose(2,0,1)/127.5-1;ten=np.zeros((1,3,48,192),dtype='float32');ten[0,:,:,:neww]=v;pr=forward(sess,ten)
        rapid=dict(pred_cw=(axis+int(np.argmax(pr))*180)%360,confidence=float(np.max(pr)),seconds=time.perf_counter()-start+geo['seconds'])
        out.append(dict(annotation=ann,geometry=geo,osd=osd(crop),ocr_vote=ocr_vote(crop,ann['unit']),rapid=rapid))
    save('real_local_results.json',dict(source=REAL,cases=out))
    print([(x['annotation']['id'],x['annotation']['truth_cw'],[(d,x[d]['pred_cw']) for d in ['geometry','osd','ocr_vote','rapid']]) for x in out],flush=True)
if __name__=='__main__':main()
