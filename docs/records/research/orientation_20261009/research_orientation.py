"""Reproducible pixel-only orientation research; run stages in the foreground.

All angles are observed writing orientation CLOCKWISE from upright. Pillow's
positive rotate is CCW, so generation uses -angle and correction uses +angle.
No source PDF or OCR text layer is consulted. Writes stay beside this file.
"""
import os
os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['OMP_NUM_THREADS']='4'
os.environ['TOKENIZERS_PARALLELISM']='false'
from pathlib import Path
ROOT=Path(__file__).resolve().parent
os.environ['TMPDIR']=str(ROOT/'tmp')
(ROOT/'tmp').mkdir(exist_ok=True)
import argparse, csv, hashlib, io, json, math, subprocess, sys, time
from collections import Counter
from types import SimpleNamespace as NS
import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

REAL='s2-6419488b7f8e69fd20da-p00001'
SOURCES=[('an-d6fd2cf2f618-p000047',7,(75,330,1100,710)),
         ('s2-3229200bf47ca465a42d-p00004',14,(100,540,1320,990)),
         ('s2-49598b2e848ab1f0ee1e-p00001',13,(100,1090,1505,1530))]
def save(path,obj):
    path=ROOT/path; path.parent.mkdir(exist_ok=True,parents=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n')
def load(path): return json.loads((ROOT/path).read_text())
def thumb(im,limit=1800):
    im=im.copy(); im.thumbnail((limit,limit)); return im
def ink(im,limit=1800):
    g=np.array(thumb(im.convert('L'),limit))
    m=cv2.adaptiveThreshold(g,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,51,18)
    # Scale-independent long rule removal, retaining individual stems.
    k=max(80,round(min(g.shape)*.09))
    rules=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((1,k),np.uint8))|cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((k,1),np.uint8))
    m=m & ~rules
    return m
def generate():
    out=ROOT/'testset'; out.mkdir(exist_ok=True)
    cases=[]
    def add(id,im,**meta):
        p=out/(id+'.png'); im.save(p,dpi=(300,300))
        cases.append(dict(id=id,path=str(p.relative_to(ROOT)),size=list(im.size),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),**meta))
    for p in sorted((ROOT/'pages').glob('*.png')):
        im=Image.open(p).convert('RGB')
        # The real table's dominant writing is CCW90 = CW270; its headers mix.
        base=270 if p.stem==REAL else 0
        for a in (0,90,180,270):
            add(p.stem+f'__r{a}',im.rotate(-a,expand=True),unit='page',kind='whole',source=p.stem,applied_cw=a,truth_cw=(base+a)%360,mixed=(p.stem==REAL))
    for name in (SOURCES[0][0],SOURCES[1][0]):
        im=Image.open(ROOT/'pages'/f'{name}.png').convert('RGB')
        for a in (-5,-3,-1,1,3,5):
            add(name+f'__skew{a:+d}',im.rotate(-a,expand=True,resample=Image.Resampling.BICUBIC,fillcolor='white'),unit='page',kind='skew',source=name,truth_cw=0,skew_cw=a,mixed=False)
    templates=[]
    for si,(name,li,blockbox) in enumerate(SOURCES):
        im=Image.open(ROOT/'pages'/f'{name}.png').convert('RGB')
        line=load(f'round3/{name}.lines.json')[li]
        base=float(np.median(line['baseline']));xh=float(line['xheight'])
        linebox=(line['x0'],int(min(line['accent_top']))-3,line['x1'],int(max(line['font_bottom']))+3)
        lc=im.crop(linebox)
        templates.extend([(f'b{si}','block',im.crop(blockbox),name,list(blockbox)),(f'l{si}','line',lc,name,list(linebox))])
        m=ink(lc,10000)
        for j in range(m.shape[1]):
            top=max(0,int(min(line['accent_top'][j],line['font_top'][j]))-linebox[1]-2)
            bottom=min(m.shape[0],int(line['font_bottom'][j])-linebox[1]+3)
            m[:top,j]=0;m[bottom:,j]=0
        v=(m.sum(axis=0)>255).astype(np.uint8)
        v=cv2.morphologyEx(v[None,:],cv2.MORPH_CLOSE,np.ones((1,3),np.uint8))[0]
        z=np.r_[0,v==0,0].astype(int);starts=np.flatnonzero(np.diff(z)==1);ends=np.flatnonzero(np.diff(z)==-1)
        cuts=[0]+[int((a+b)//2) for a,b in zip(starts,ends) if b-a>=max(4,.4*xh) and a>0 and b<len(v)]+[len(v)]
        wi=0
        for a,b in zip(cuts,cuts[1:]):
            xs=np.flatnonzero(v[a:b]);
            if not len(xs):continue
            a1=a+int(xs[0]);b1=a+int(xs[-1])+1
            if not 3*xh<=b1-a1<=11*xh:continue
            a1=max(0,a1-3);b1=min(lc.width,b1+3)
            t=int(min(line['accent_top'][a1:b1]))-3;b=int(max(line['font_bottom'][a1:b1]))+3
            wordbox=[linebox[0]+a1,t,linebox[0]+b1,b]
            crop=im.crop(wordbox)
            templates.append((f'w{si}_{wi}','word',crop,name,wordbox));wi+=1
            if wi==4:break
        if si==2:
            # Manual complete-word spans checked on line_s2-495...png. The
            # automatically proposed last piece was a line-end fragment.
            templates=[t for t in templates if not t[0].startswith('w2_')]
            for wi,(a,b) in enumerate([(160,425),(495,735),(745,838),(860,1165)]):
                j0=max(0,a-line['x0']);j1=min(len(line['font_bottom']),b-line['x0'])
                t=int(min(line['accent_top'][j0:j1]))-4;bot=int(max(line['font_bottom'][j0:j1]))+4
                wordbox=[a,t,b,bot]
                templates.append((f'w2_{wi}','word',im.crop(wordbox),name,wordbox))
    for id,unit,im,name,box in templates:
        for a in (0,90,180,270):
            add(id+f'__r{a}',Image.new('RGB',(im.rotate(-a,expand=True).width+40,im.rotate(-a,expand=True).height+40),'white'),unit=unit,kind='crop',source=name,truth_cw=a,source_box=box,template=id)
            p=out/(id+f'__r{a}.png'); padded=Image.open(p);padded.paste(im.rotate(-a,expand=True),(20,20));padded.save(p,dpi=(300,300));cases[-1]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    # Two distinct upright bases; local units in a cleared side strip. Preserve
    # substantial upright content on the rest of the page, with explicit ROIs.
    for si in (0,1):
        name=SOURCES[si][0];baseim=Image.open(ROOT/'pages'/f'{name}.png').convert('RGB')
        for unit in ('block','line','word'):
            id,u,im,src,box=next(t for t in templates if t[1]==unit and t[0].startswith({'block':'b','line':'l','word':'w'}[unit]+str(si)))
            for a in (90,270):
                local=im.rotate(-a,expand=True);local.thumbnail((int(baseim.width*.30),int(baseim.height*.65)))
                page=baseim.copy();d=ImageDraw.Draw(page);strip=(0,0,int(baseim.width*.34),baseim.height);d.rectangle(strip,fill='white')
                xy=(15,round(baseim.height*.25));page.paste(local,xy)
                roi=[xy[0]-8,xy[1]-8,xy[0]+local.width+8,xy[1]+local.height+8]
                add(f'composite_{si}_{unit}_r{a}',page,unit='page',kind='composite',source=name,truth_cw=0,mixed=True,roi=roi,roi_truth_cw=a,roi_unit=unit,template=id,source_box=box)
    save('testset/manifest.json',dict(angle_convention='observed CW; correction Pillow +angle',real_manual_label=dict(dominant_cw=270,correction_cw=90,note='Main title/numbers upright after clockwise90; some table labels remain perpendicular; folio upright in source'),cases=cases))
    canvas=Image.new('RGB',(1000,math.ceil(len(templates)/3)*200),'white');d=ImageDraw.Draw(canvas)
    for i,(id,u,im,src,box) in enumerate(templates):
        im=thumb(im,310);im.thumbnail((310,165));xy=((i%3)*333,(i//3)*200);canvas.paste(im,(xy[0],xy[1]+25));d.text(xy,id+' '+u,fill='black')
    canvas.save(ROOT/'templates.png')
    print(Counter(c['kind'] for c in cases),Counter(c['unit'] for c in cases),flush=True)

def geometry(im):
    start=time.perf_counter();m=ink(im); f=m.astype(float)/255
    # Normalized projection concentration: independent of page aspect ratio.
    row=f.mean(1);col=f.mean(0)
    hs=float(np.var(row)/(np.mean(row)**2+1e-9));vs=float(np.var(col)/(np.mean(col)**2+1e-9))
    projection_axis=0 if hs>=vs else 90
    # Component-neighbour geometry avoids the page-column concentration that
    # confounds global projection profiles on sparse pages and narrow columns.
    n,l0,s0,c0=cv2.connectedComponentsWithStats(m,8);s0=s0[1:];c0=c0[1:]
    eligible=(s0[:,4]>=8)&(s0[:,2]>=2)&(s0[:,3]>=2)&(s0[:,2]<150)&(s0[:,3]<150)
    q=s0[eligible];cent0=c0[eligible];ch=float(np.median(np.maximum(q[:,2],q[:,3]))) if len(q) else 10.
    bodies=(np.maximum(q[:,2],q[:,3])>.65*ch)&(np.maximum(q[:,2],q[:,3])<2*ch)&(q[:,4]>.15*ch*ch)
    pts=cent0[bodies];horizontal=vertical=0.
    if len(pts)>=3:
        ds,js=cKDTree(pts).query(pts,k=min(12,len(pts)))
        for i,ids in enumerate(js):
            dd=pts[np.atleast_1d(ids)]-pts[i];dx=np.abs(dd[:,0]);dy=np.abs(dd[:,1])
            hx=dx[(dy<.35*ch)&(dx>.4*ch)&(dx<5*ch)]
            vy=dy[(dx<.35*ch)&(dy>.4*ch)&(dy<5*ch)]
            horizontal+=ch/float(hx.min()) if len(hx) else 0.
            vertical+=ch/float(vy.min()) if len(vy) else 0.
    component_axis=0 if horizontal>=vertical else 90
    axis=component_axis if len(pts)>=12 else projection_axis
    aligned=np.rot90(m,axis//90)
    n,labels,stats,cent=cv2.connectedComponentsWithStats(aligned,8)
    s=stats[1:];c=cent[1:]
    okay=(s[:,4]>=5)&(s[:,2]>=2)&(s[:,3]>=3)&(s[:,2]<aligned.shape[1]*.1)&(s[:,3]<aligned.shape[0]*.15)
    s=s[okay];c=c[okay]
    if len(s)<3:return dict(axis_cw=axis,projection_axis_cw=projection_axis,component_axis_cw=component_axis,pred_cw=None,seconds=time.perf_counter()-start,hs=hs,vs=vs,reason='too_few_components')
    h=float(np.median(s[:,3]));body=(s[:,3]>.65*h)&(s[:,3]<2*h)&(s[:,2]<2.5*h)&(s[:,4]>.12*h*h)
    bs=s[body];bc=c[body]; small=(s[:,3]<.55*h)&(s[:,4]<.30*h*h)
    up=down=0
    if len(bs):
        tree=cKDTree(bc)
        for q,ct in zip(s[small],c[small]):
            dist,ix=tree.query(ct,k=min(4,len(bs)))
            candidates=[]
            for j in np.atleast_1d(ix):
                b=bs[j];x,y=ct
                if b[0]-.2*h<=x<=b[0]+b[2]+.2*h:
                    gapabove=b[1]-(q[1]+q[3]);gapbelow=q[1]-(b[1]+b[3])
                    if -.1*h<=gapabove<=.7*h:candidates.append((abs(gapabove),1))
                    if -.1*h<=gapbelow<=.7*h:candidates.append((abs(gapbelow),-1))
            if candidates:
                sign=min(candidates)[1];up+=sign==1;down+=sign==-1
    # Baseline bottoms generally align more tightly than cap/ascender tops.
    differences=[]
    if len(bs)>3:
        tree=cKDTree(bc)
        ds,ids=tree.query(bc,k=min(8,len(bc)))
        for i,js in enumerate(ids):
            near=[j for j in np.atleast_1d(js) if abs(bc[j,1]-bc[i,1])<.45*h and abs(bc[j,0]-bc[i,0])<8*h]
            if len(near)>=3:
                tops=bs[near,1];bottoms=bs[near,1]+bs[near,3]
                differences.append((np.median(abs(tops-np.median(tops)))-np.median(abs(bottoms-np.median(bottoms))))/h)
    align=float(np.mean(differences)) if differences else 0.
    accent=(up-down)/max(1,up+down)
    polarity=accent+2*align
    pred=(axis+(180 if polarity<0 else 0))%360
    return dict(axis_cw=axis,projection_axis_cw=projection_axis,component_axis_cw=component_axis,component_votes=[horizontal,vertical],pred_cw=pred,seconds=time.perf_counter()-start,hs=hs,vs=vs,axis_margin=abs(horizontal-vertical)/max(horizontal,vertical,1e-9),accent_above=up,accent_below=down,alignment=align,polarity_score=polarity,body_components=len(bs))

def osd(im):
    start=time.perf_counter();p=ROOT/'tmp'/'osd.png';thumb(im,2000).save(p,dpi=(300,300))
    r=subprocess.run(['/opt/homebrew/bin/tesseract',str(p),'stdout','-l','osd','--psm','0'],capture_output=True,text=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
    import re
    ori=re.search(r'Orientation in degrees: (\d+)',r.stdout);conf=re.search(r'Orientation confidence: ([\d.]+)',r.stdout)
    return dict(pred_cw=int(ori.group(1)) if ori else None,confidence=float(conf.group(1)) if conf else None,seconds=time.perf_counter()-start,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)

VOTE_CACHE={}
def ocr_vote(im,unit):
    start=time.perf_counter();scores=[];details=[];inference_seconds=0.;cold_equivalent=0.
    for a in (0,90,180,270):
        p=ROOT/'tmp'/'vote.png';x=thumb(im.rotate(a,expand=True),2000)
        psm='8' if unit=='word' else '7' if unit=='line' else '6' if unit=='block' else '11'
        key=hashlib.sha256(x.tobytes()+str(x.size).encode()+psm.encode()).hexdigest()
        if key in VOTE_CACHE:
            detail=dict(VOTE_CACHE[key],angle=a,cached=True);scores.append(detail['score']);details.append(detail);cold_equivalent+=detail['neural_seconds'];continue
        x.save(p,dpi=(300,300));neural_start=time.perf_counter()
        r=subprocess.run(['/opt/homebrew/bin/tesseract',str(p),'stdout','-l','grc+ell','--psm',psm,'tsv'],capture_output=True,text=True,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
        neural_sec=time.perf_counter()-neural_start;inference_seconds+=neural_sec;cold_equivalent+=neural_sec
        words=[];score=0.
        for row in csv.DictReader(io.StringIO(r.stdout),delimiter='\t'):
            try:conf=float(row['conf'])
            except (ValueError,KeyError):continue
            txt=row.get('text','') or '';greek=sum(('\u0370'<=c<='\u03ff') or ('\u1f00'<=c<='\u1fff') for c in txt)
            if conf>=0 and txt.strip():
                score+=max(0,conf)*greek;words.append([txt,conf,greek])
        detail=dict(angle=a,score=score,words=words,returncode=r.returncode,stderr=r.stderr,neural_seconds=neural_sec,input_sha256=key,cached=False)
        VOTE_CACHE[key]=detail;scores.append(score);details.append(detail)
    ix=int(np.argmax(scores));ordered=sorted(scores,reverse=True);margin=(ordered[0]-ordered[1])/max(1,ordered[0])
    elapsed=time.perf_counter()-start
    return dict(pred_cw=ix*90 if max(scores)>0 else None,seconds=elapsed,uncached_equivalent_seconds=elapsed-inference_seconds+cold_equivalent,scores=scores,margin=margin,details=details)

def run_candidates(which):
    cases=load('testset/manifest.json')['cases'];out=ROOT/f'{which}.jsonl'
    with out.open('w') as f:
        for c in cases:
            im=Image.open(ROOT/c['path']).convert('RGB')
            units=[('full',im,c['unit'],c['truth_cw'])]
            if c['kind']=='composite':units.append(('roi',im.crop(c['roi']),c['roi_unit'],c['roi_truth_cw']))
            for scope,x,u,truth in units:
                r=(geometry(x) if which=='geometry' else osd(x) if which=='osd' else ocr_vote(x,u))
                rec=dict(id=c['id'],scope=scope,unit=u,kind=c['kind'],truth_cw=truth,correct=r['pred_cw']==truth,**r)
                if 'axis_cw' in r:
                    rec['axis_correct']=r['axis_cw']==truth%180
                    rec['projection_axis_correct']=r['projection_axis_cw']==truth%180
                    rec['component_axis_correct']=r['component_axis_cw']==truth%180
                f.write(json.dumps(rec,ensure_ascii=False)+'\n');f.flush()
                print(which,c['id'],scope,r['pred_cw'],truth,round(r['seconds'],3),flush=True)

def run_layout():
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from docling.datamodel.pipeline_options import LayoutObjectDetectionOptions, LayoutPostprocessorOptions
    from docling.models.stages.layout.layout_object_detection_model import LayoutObjectDetectionModel
    from docling.models.stages.layout.layout_postprocessing_model import LayoutPostprocessingModel
    from docling_core.types.doc import Size
    artifacts=ROOT/'artifacts';artifacts.mkdir(exist_ok=True)
    snap=Path('/Users/foivoskarounos-zamparloukos/.cache/huggingface/hub/models--docling-project--docling-layout-heron/snapshots/8f39ad3c0b4c58e9c2d2c84a38465abf757272d8')
    link=artifacts/'docling-project--docling-layout-heron'
    if not link.exists():link.symlink_to(snap,target_is_directory=True)
    start=time.perf_counter();model=LayoutObjectDetectionModel(artifacts,AcceleratorOptions(device='cpu',num_threads=4),LayoutObjectDetectionOptions());post=LayoutPostprocessingModel(options=LayoutPostprocessorOptions())
    save('layout_config.json',dict(snapshot=str(snap),load_seconds=time.perf_counter()-start,options=model.options.model_dump(mode='json'),scale='PNG/3, fresh forwards; no OCR cells'))
    with (ROOT/'layout.jsonl').open('w') as f:
        for c in load('testset/manifest.json')['cases']:
            if c['unit']!='page':continue
            im=Image.open(ROOT/c['path']).convert('RGB');size=Size(width=im.width/3,height=im.height/3)
            backend=NS(is_valid=lambda:True)
            page=NS(page_no=1,size=size,_backend=backend,cells=[],parsed_page=None,predictions=NS(layout=None),get_image=lambda scale:im.resize((round(size.width*scale),round(size.height*scale))))
            conv=NS(timings={},confidence=NS(pages={1:NS(layout_score=0.)}))
            start=time.perf_counter();raw=model.predict_layout(conv,[page])[0];seconds=time.perf_counter()-start
            rawdata=raw.model_dump(mode='json');final=post.postprocess_layout(conv,[page])[0]
            rec=dict(id=c['id'],kind=c['kind'],truth_cw=c['truth_cw'],seconds=seconds,raw=rawdata,retained=final.model_dump(mode='json'))
            f.write(json.dumps(rec)+'\n');f.flush();print('layout',c['id'],round(seconds,3),Counter(x.label.value for x in raw.clusters),flush=True)

def run_lines():
    sys.path.insert(0,'/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4')
    from greekocr.glyphs.page_text_lines import segment_page
    with (ROOT/'lines.jsonl').open('w') as f:
        for c in load('testset/manifest.json')['cases']:
            if c['kind']!='whole':continue
            im=Image.open(ROOT/c['path']).convert('L');start=time.perf_counter();p=segment_page(im);seconds=time.perf_counter()-start
            kept=[l for l in p.lines if l.discounted is None]
            lengths=np.array([l.x1-l.x0 for l in kept]);xh=np.array([l.xheight for l in kept])
            rec=dict(id=c['id'],truth_cw=c['truth_cw'],seconds=seconds,total=len(p.lines),kept=len(kept),median_length=float(np.median(lengths)) if len(kept) else None,median_xheight=float(np.median(xh)) if len(kept) else None,shorter_than_3xh=float(np.mean(lengths<3*xh)) if len(kept) else None,diagnostics=p.diagnostics)
            if c['source']==REAL or (c['source']==SOURCES[0][0] and c['applied_cw'] in (0,90,180)):
                view=thumb(im.convert('RGB'),1400);draw=ImageDraw.Draw(view);scale=view.width/im.width
                for line in kept:
                    draw.line([(round((line.x0+j)*scale),round(y*scale)) for j,y in enumerate(line.baseline)][::max(1,round(1/scale))],fill='red',width=1)
                view.save(ROOT/'testset'/f"{c['id']}_lines.jpg")
            f.write(json.dumps(rec,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n');f.flush();print('lines',c['id'],len(kept),round(seconds,3),flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stage',choices=['generate','geometry','osd','ocr_vote','layout','lines']);args=ap.parse_args()
    if args.stage=='generate':generate()
    elif args.stage=='layout':run_layout()
    elif args.stage=='lines':run_lines()
    else:run_candidates(args.stage)
