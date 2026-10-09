"""Fixed research fixtures: measured gates, with failures and abstentions retained.

Run offline in the foreground. --require-gate returns nonzero for any unmet
requirement. Oracle crop tests and blind discovery are deliberately separate.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace as NS

import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from greekocr.glyphs.orientation import measure_orientation,recognizer_polarity,discover_directions,QuarterTurn

RESEARCH=ROOT/'.astra/orientation_research'


def save(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n')


def fixture_cases():
    cases=json.loads((RESEARCH/'testset/manifest.json').read_text())['cases']
    for c in cases:
        assert hashlib.sha256((RESEARCH/c['path']).read_bytes()).hexdigest()==c['sha256'],f"modified fixture {c['id']}"
    return cases


def decisions(cases,recognizer,out):
    rows=[]
    for c in cases:
        if c['kind'] not in ('whole','skew') and c['unit']!='word' and not(c['kind']=='composite' and c['roi_unit']=='word'):
            continue
        im=Image.open(RESEARCH/c['path']);truth=c['truth_cw'];unit=c['unit'];category=c['kind']
        if c['kind']=='composite':
            im=im.crop(c['roi']);truth=c['roi_truth_cw'];unit='word';category='pasted-word'
        if unit=='word' and category!='pasted-word':category='word'
        o=measure_orientation(im,use_osd=unit=='page',unit=unit)
        if unit=='word':o=recognizer_polarity(im,o,recognizer)
        rows.append(dict(id=c['id'],category=category,truth_cw=truth,
                         axis_correct=o.axis==('vertical' if truth%180 else 'horizontal'),
                         correct=o.orientation_cw==truth,accepted=o.orientation_cw is not None,**o.to_record()))
    save(out/'decisions.json',rows)
    return rows


def blind(cases,out):
    rows=[]
    for c in cases:
        if c['kind']!='composite':continue
        im=Image.open(RESEARCH/c['path']);proposals=discover_directions(im)
        # No truth/ROI enters proposal generation. Scoring starts here.
        shape=(im.height,im.width);truth=np.zeros(shape,bool);cover=np.zeros(shape,bool)
        l,t,r,b=c['roi'];truth[t:b,l:r]=True;outside=0
        for p in proposals:
            if p['axis']!='vertical':continue
            a,y,z,bot=[round(v) for v in p['box']]
            if max(a,l)>=min(z,r) or max(y,t)>=min(bot,b):outside+=1;continue
            cover[y:bot,a:z]=True
        iou=float((cover&truth).sum()/max(1,(cover|truth).sum()))
        # Image ink diagnostic, explicitly not manual word precision/recall.
        from greekocr.glyphs.orientation import _pixels
        small,ink,_,_=_pixels(im,2000);sx,sy=small.width/im.width,small.height/im.height
        ink_cover=np.asarray(Image.fromarray(cover).resize(small.size,Image.Resampling.NEAREST))
        roi=np.asarray(Image.fromarray(truth).resize(small.size,Image.Resampling.NEAREST))
        coverage=float(((ink>0)&roi&ink_cover).sum()/max(1,((ink>0)&roi).sum()))
        rows.append(dict(id=c['id'],unit=c['roi_unit'],union_iou=iou,threshold_ink_coverage=coverage,
                         outside_vertical_proposals=outside,proposals=proposals,passed=iou>=.5 and coverage>=.95))
        view=im.convert('RGB');view.thumbnail((1000,1200));draw=ImageDraw.Draw(view);scale=view.width/im.width
        for p in proposals:
            if p['axis']=='vertical':draw.rectangle([v*scale for v in p['box']],outline='red',width=1)
        draw.rectangle([v*scale for v in c['roi']],outline='blue',width=2)
        view.save(out/(c['id']+'.jpg'))
    save(out/'blind.json',rows);return rows


def real(recognizer,out):
    key='s2-6419488b7f8e69fd20da-p00001';im=Image.open(ROOT/'.astra/pages'/f'{key}.png')
    rows=[]
    # Fixed image-labelled research annotations, only in the evaluator.
    for name,box,truth,unit in [('title',[180,487,320,1907],270,'line'),
                               ('header',[1270,3922,1530,4037],180,'word'),
                               ('folio',[1610,187,1810,297],0,'word')]:
        crop=im.crop(box);o=measure_orientation(crop,use_osd=True,unit=unit)
        if o.orientation_cw is None:o=recognizer_polarity(crop,o,recognizer)
        rows.append(dict(id=name,box=box,truth_cw=truth,correct=o.orientation_cw==truth,
                         passed=o.orientation_cw==truth or (name=='folio' and o.orientation_cw is None),**o.to_record()))
    save(out/'real-crops.json',rows);return rows


def grid_fixture():
    """Exact construction from Sol's research_docling.py, extended to four turns."""
    grid=Image.new('RGB',(1140,820),'white');d=ImageDraw.Draw(grid);tokens=[]
    for rr in range(4):
        for cc in range(3):
            word=Image.open(RESEARCH/'testset'/f'w{rr%3}_{cc%4}__r0.png').convert('RGB');word.thumbnail((230,110))
            x=40+cc*350+30;y=40+rr*180+35;grid.paste(word,(x,y));tokens.append((f'R{rr}C{cc}',[x,y,x+word.width,y+word.height]))
    for x in (40,390,740,1090):d.line([(x,40),(x,760)],fill='black',width=3)
    for y in (40,220,400,580,760):d.line([(40,y),(1090,y)],fill='black',width=3)
    return grid,tokens


def tables(out):
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from docling.datamodel.pipeline_options import TableStructureOptions,TableFormerMode
    from docling.datamodel.base_models import Cluster,LayoutPrediction
    from docling.models.stages.table_structure.table_structure_model import TableStructureModel
    from docling.models.base_ocr_model import _empty_segmented_page
    from docling_core.types.doc import BoundingBox,CoordOrigin,DocItemLabel,Size
    from docling_core.types.doc.page import BoundingRectangle,TextCell
    from greekocr.deploy.docling_plugin.orientation import OrientedTableAdapter
    modelroot=Path.home()/'.cache/huggingface/hub/models--docling-project--docling-models/snapshots/fc0f2d45e2218ea24bce5045f58a389aed16dc23/model_artifacts/tableformer'
    model=TableStructureModel(enabled=True,artifacts_path=modelroot,options=TableStructureOptions(mode=TableFormerMode.ACCURATE,do_cell_matching=True),accelerator_options=AcceleratorOptions(device='cpu',num_threads=4))
    adapter=OrientedTableAdapter(model);grid,base=grid_fixture();rows=[]
    for a in (0,90,180,270):
        im=grid.rotate(-a,expand=True);frame=QuarterTurn(im.width,im.height,a)
        cells=[]
        for i,(text,box) in enumerate(base):
            points=frame.rectangle(box)/3
            rect=BoundingRectangle(**{f'r_{axis}{k}':p[j] for k,p in enumerate(points) for j,axis in enumerate(('x','y'))},coord_origin=CoordOrigin.TOPLEFT)
            cells.append(TextCell(index=i,text=text,orig=text,from_ocr=True,confidence=1,rect=rect))
        p=frame.rectangle([35,35,1095,765])/3;l,t=p.min(0);r,b=p.max(0)
        box=BoundingBox(l=l,t=t,r=r,b=b,coord_origin=CoordOrigin.TOPLEFT)
        cluster=Cluster(id=0,label=DocItemLabel.TABLE,confidence=1,bbox=box,cells=cells)
        size=Size(width=im.width/3,height=im.height/3);sp=_empty_segmented_page(NS(size=size))
        page=NS(page_no=1,size=size,_backend=NS(is_valid=lambda:True,get_segmented_page=lambda:sp),
                predictions=NS(layout=LayoutPrediction(clusters=[cluster]),tablestructure=None),
                get_image=lambda scale:im.resize((round(size.width*scale),round(size.height*scale))))
        table=adapter.predict_tables(NS(timings={}),[page])[0].table_map[0]
        assignments={}
        for c in table.table_cells:
            for token in c.text.split():assignments.setdefault(token,[]).append([c.start_row_offset_idx,c.start_col_offset_idx])
        correct=sum(assignments.get(f'R{r}C{c}')==[[r,c]] for r in range(4) for c in range(3))
        row=dict(applied_cw=a,rows=table.num_rows,columns=table.num_cols,correct=correct,total=12,
                 orientation=table.orientation.value,passed=correct==12 and (table.num_rows,table.num_cols)==(4,3),
                 assignments=assignments,table=table.model_dump(mode='json'))
        rows.append(row);print('GRID',a,correct,table.num_rows,table.num_cols,flush=True)
    save(out/'table-grid.json',rows);return rows


def metadata(out):
    import pypdfium2 as pdfium
    from docling.datamodel.document import InputDocument
    from docling.datamodel.base_models import InputFormat
    from docling.backend.docling_parse_backend import ThreadedDoclingParseDocumentBackend
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    from greekocr.deploy.docling_plugin.orientation import NormalizedPageBackend
    im=Image.open(RESEARCH/'testset/an-d6fd2cf2f618-p000047__r0.png').convert('RGB');im.thumbnail((600,900))
    im.save(out/'metadata-base.pdf',resolution=72);rows=[];originals={}
    for a in (0,90,180,270):
        doc=pdfium.PdfDocument(out/'metadata-base.pdf');p=doc[0];p.set_rotation(a);path=out/f'metadata-{a}.pdf';doc.save(path);p.close();doc.close()
        for cls in (ThreadedDoclingParseDocumentBackend,PyPdfiumDocumentBackend):
            inp=InputDocument(path_or_stream=path,format=InputFormat.PDF,backend=cls);backend=inp._backend
            page=next(backend.iter_pages()) if cls==ThreadedDoclingParseDocumentBackend else backend.load_page(0)
            image=page.get_page_image(scale=1.);size=page.get_size()
            if a==0:originals[cls.__name__]=image
            expected=originals[cls.__name__].rotate(-a,expand=True)
            mae=float(np.mean(abs(np.asarray(image,dtype=float)-np.asarray(expected,dtype=float))))
            # Correct exactly once from the ALREADY metadata-rotated render.
            corrected=NormalizedPageBackend(page,a).get_page_image(scale=1.)
            error=float(np.mean(abs(np.asarray(corrected,dtype=float)-np.asarray(originals[cls.__name__],dtype=float))))
            rows.append(dict(backend=cls.__name__,rotate=a,mae=mae,corrected_mae=error,
                             native_lines=len(page.get_segmented_page().textline_cells),
                             passed=image.size==expected.size and mae<1 and error<1))
            backend.unload()
    save(out/'metadata.json',rows);return rows


def fitter(cases,out):
    from greekocr.glyphs.page_text_lines import segment_page,CURVES
    cache={};rows=[]
    for c in cases:
        if c['kind']!='whole':continue
        image=Image.open(RESEARCH/c['path']).convert('L');frame=QuarterTurn(*image.size,c['truth_cw'])
        normalized=frame.image(image)
        base=next(x for x in cases if x['kind']=='whole' and x['source']==c['source'] and x['applied_cw']==0)
        baseline_image=Image.open(RESEARCH/base['path']).convert('L').rotate(base['truth_cw'],expand=True)
        exact_pixels=np.array_equal(normalized,baseline_image)
        digest=hashlib.sha256(normalized.tobytes()+str(normalized.size).encode()).hexdigest()
        # Reuse fits only for byte-identical normalized raster tensors.
        fresh=digest not in cache
        if fresh:
            print('FITTER',c['id'],flush=True);cache[digest]=segment_page(normalized)
        result=cache[digest];error=0.
        for l in result.lines:
            if l.discounted is not None:continue
            xs=np.arange(l.x0,l.x1)
            for k in CURVES:
                points=np.c_[xs,getattr(l,k)];mapped=frame.points(points,inverse=True)
                error=max(error,float(abs(frame.points(mapped)-points).max()))
        rows.append(dict(id=c['id'],truth_normalization_only=True,normalized_sha256=digest,
                         fresh_fit=fresh,exact_normalized_pixels=exact_pixels,max_guide_roundtrip_pixels=error,
                         lines=sum(l.discounted is None for l in result.lines),passed=exact_pixels and error<=1))
    save(out/'fitter.json',rows);return rows


def gates(out):
    load=lambda name:json.loads((out/name).read_text()) if (out/name).exists() else []
    decisions=load('decisions.json');whole=[r for r in decisions if r['category']=='whole'];skew=[r for r in decisions if r['category']=='skew']
    words=[r for r in decisions if r['category']=='word'];pasted=[r for r in decisions if r['category']=='pasted-word']
    summary=[]
    def add(name,passed,numbers):summary.append(dict(gate=name,passed=bool(passed),numbers=numbers))
    meta=load('metadata.json');add('offline/frame metadata',len(meta)==8 and all(r['passed'] for r in meta),dict(passed=sum(r['passed'] for r in meta),total=8))
    axis=sum(r['axis_correct'] for r in whole);errors=sum(r['accepted'] and not r['correct'] for r in whole)
    add('whole-page direction',len(whole)==40 and axis==40 and errors==0,dict(axis_correct=axis,total=40,accepted=sum(r['accepted'] for r in whole),polarity_errors=errors))
    add('skew controls',len(skew)==12 and all(r['correct'] for r in skew),dict(correct=sum(r['correct'] for r in skew),axis_correct=sum(r['axis_correct'] for r in skew),total=12))
    add('word orientation',sum(r['correct'] for r in words)>=46 and len(pasted)==4 and all(not r['accepted'] or r['correct'] for r in pasted),dict(correct=sum(r['correct'] for r in words),accepted=sum(r['accepted'] for r in words),total=48,errors=sum(r['accepted'] and not r['correct'] for r in words),pasted_correct=sum(r['correct'] for r in pasted),pasted_abstain=sum(not r['accepted'] for r in pasted)))
    blindrows=load('blind.json');add('blind mixed discovery',len(blindrows)==12 and all(r['passed'] for r in blindrows),dict(passed=sum(r['passed'] for r in blindrows),total=12,outside_vertical_proposals=sum(r['outside_vertical_proposals'] for r in blindrows),manual_word_annotations=False))
    realrows=load('real-crops.json');add('real mixed page',False,dict(crops_passed=sum(r['passed'] for r in realrows),crops_total=3,blind_full_page_coverage_certified=False))
    fit=load('fitter.json');add('existing line fitter',len(fit)==40 and all(r['passed'] for r in fit),dict(passed=sum(r['passed'] for r in fit),total=40,fresh_fits=sum(r['fresh_fit'] for r in fit),scope='truth-normalized fitter and inverse geometry; not polarity accuracy'))
    grid=load('table-grid.json');add('table grid',len(grid)==4 and all(r['passed'] for r in grid),dict(passed=sum(r['passed'] for r in grid),total=4,logical_labels=sum(r['correct'] for r in grid)))
    stage=load('pipeline.json');uniform=load('uniform-pipeline/pipeline.json')
    normalized=bool(uniform) and any(r['applied'] for r in uniform.get('normalization',[]))
    add('pipeline stage ordering',bool(stage) and stage.get('passed',False) and normalized,
        dict(mixed_page_pipeline=stage,uniform_page_pipeline=uniform,automatic_uniform_normalization_verified=normalized))
    save(out/'gates.json',dict(passed=all(r['passed'] for r in summary),gates=summary))
    return summary


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--checkpoint',type=Path)
    ap.add_argument('--codec',type=Path,default=ROOT/'greekocr/deploy/docling_plugin/recognizer/v1.json')
    ap.add_argument('--out',type=Path,default=ROOT/'.astra/out/orientation-acceptance')
    ap.add_argument('--stages',nargs='+',default=['decisions','blind','real','tables','metadata','fitter'])
    ap.add_argument('--require-gate',action='store_true');args=ap.parse_args();args.out.mkdir(exist_ok=True,parents=True)
    import torch;torch.set_num_threads(4)
    cases=fixture_cases();recognizer=None
    if set(args.stages)&{'decisions','real'}:
        from greekocr.deploy.docling_plugin.recognizer.inference import Recognizer
        if args.checkpoint is None:ap.error('--checkpoint is required for our recognizer polarity tests')
        recognizer=Recognizer(str(args.checkpoint),str(args.codec))
    for name in args.stages:
        print('STAGE',name,flush=True)
        if name=='decisions':decisions(cases,recognizer,args.out)
        elif name=='blind':blind(cases,args.out)
        elif name=='real':real(recognizer,args.out)
        elif name=='tables':tables(args.out)
        elif name=='metadata':metadata(args.out)
        elif name=='fitter':fitter(cases,args.out)
        elif name!='gates':ap.error(f'unknown stage {name}')
    summary=gates(args.out)
    print(json.dumps(summary,indent=2))
    if args.require_gate and not all(r['passed'] for r in summary):raise SystemExit(1)


if __name__=='__main__':main()
