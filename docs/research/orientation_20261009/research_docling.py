"""Offline TableFormer and backend coordinate probes. No PDF text as truth."""
from research_orientation import *
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import Cluster,LayoutPrediction
from docling.datamodel.pipeline_options import TableStructureOptions,TableFormerMode
from docling.models.base_ocr_model import _empty_segmented_page
from docling.models.stages.table_structure.table_structure_model import TableStructureModel
from docling_core.types.doc import BoundingBox,CoordOrigin,DocItemLabel,Size
from docling_core.types.doc.page import BoundingRectangle,TextCell
def bb(v):return BoundingBox(l=v[0],t=v[1],r=v[2],b=v[3],coord_origin=CoordOrigin.TOPLEFT)
def rect(v):return BoundingRectangle.from_bounding_box(bb(v))
def cw_points(points,a,w,h):
    if a==0:return points
    if a==90:return [[h-y,x] for x,y in points]
    if a==180:return [[w-x,h-y] for x,y in points]
    if a==270:return [[y,w-x] for x,y in points]
def oriented(v,a,w,h):
    r=rect(v);ps=cw_points(r.to_polygon(),a,w,h)
    return BoundingRectangle(**{f'r_{axis}{i}':p[j]/3 for i,p in enumerate(ps) for j,axis in enumerate(('x','y'))},coord_origin=CoordOrigin.TOPLEFT)
def tables():
    out=[]
    inputs=[]
    for name,region in [('s2-200e977f2dab5291c42c-p00035',[565,745,2900,3840]),(REAL,[365,340,2690,4530])]:
        im=Image.open(ROOT/'pages'/f'{name}.png').convert('RGB')
        ls=load(f'round3/{name}.lines.json');cells=[]
        for i,l in enumerate(ls):
            v=[l['x0'],min(l['top']),l['x1'],max(l['bottom'])]
            if region[0]<=v[0] and v[2]<=region[2] and region[1]<=v[1] and v[3]<=region[3]:cells.append((f'L{i:04}',v))
        for a in (0,90):inputs.append((name+f'__r{a}',im.rotate(-a,expand=True),[min(p[0] for p in cw_points(rect(region).to_polygon(),a,*im.size)),min(p[1] for p in cw_points(rect(region).to_polygon(),a,*im.size)),max(p[0] for p in cw_points(rect(region).to_polygon(),a,*im.size)),max(p[1] for p in cw_points(rect(region).to_polygon(),a,*im.size))],[(txt,oriented(v,a,*im.size)) for txt,v in cells],None))
    # Known logical 4x3 grid. Every label is inside one cell. Greek pixel word
    # snippets, not font-generated approximations. Extra header, no PDF layer.
    grid=Image.new('RGB',(1140,820),'white');d=ImageDraw.Draw(grid);basecells=[]
    for rr in range(4):
        for cc in range(3):
            word=Image.open(ROOT/'testset'/f'w{rr%3}_{cc%4}__r0.png').convert('RGB');word.thumbnail((230,110))
            x=40+cc*350+30;y=40+rr*180+35;grid.paste(word,(x,y));basecells.append((f'R{rr}C{cc}',[x,y,x+word.width,y+word.height]))
    for x in (40,390,740,1090):d.line([(x,40),(x,760)],fill='black',width=3)
    for y in (40,220,400,580,760):d.line([(40,y),(1090,y)],fill='black',width=3)
    for a in (0,90):
        im=grid.rotate(-a,expand=True);im.save(ROOT/f'grid_r{a}.png')
        ps=cw_points(rect([35,35,1095,765]).to_polygon(),a,*grid.size);region=[min(p[0] for p in ps),min(p[1] for p in ps),max(p[0] for p in ps),max(p[1] for p in ps)]
        inputs.append((f'grid__r{a}',im,region,[(txt,oriented(v,a,*grid.size)) for txt,v in basecells],dict(rows=4,cols=3)))
    modelroot=Path('/Users/foivoskarounos-zamparloukos/.cache/huggingface/hub/models--docling-project--docling-models/snapshots/fc0f2d45e2218ea24bce5045f58a389aed16dc23/model_artifacts/tableformer')
    for mode in ('accurate','fast'):
        start=time.perf_counter();model=TableStructureModel(enabled=True,artifacts_path=modelroot,options=TableStructureOptions(mode=TableFormerMode(mode),do_cell_matching=True),accelerator_options=AcceleratorOptions(device='cpu',num_threads=4));print('table_load',mode,time.perf_counter()-start,flush=True)
        for name,im,region,tokens,truth in inputs:
            size=Size(width=im.width/3,height=im.height/3);sp=_empty_segmented_page(NS(size=size))
            cells=[TextCell(index=i,text=t,orig=t,from_ocr=True,confidence=1.,rect=r) for i,(t,r) in enumerate(tokens)]
            cluster=Cluster(id=0,label=DocItemLabel.TABLE,confidence=1.,bbox=bb([v/3 for v in region]),cells=cells)
            backend=NS(is_valid=lambda:True,get_segmented_page=lambda:sp)
            page=NS(page_no=1,size=size,_backend=backend,predictions=NS(layout=LayoutPrediction(clusters=[cluster]),tablestructure=None),get_image=lambda scale:im.resize((round(size.width*scale),round(size.height*scale))))
            conv=NS(timings={});start=time.perf_counter();pred=model.predict_tables(conv,[page])[0];sec=time.perf_counter()-start;tbl=pred.table_map[0]
            assignments={}
            for cell in tbl.table_cells:
                for token in cell.text.split():assignments.setdefault(token,[]).append([cell.start_row_offset_idx,cell.start_col_offset_idx])
            correct=None
            if truth:
                correct=sum(assignments.get(f'R{rr}C{cc}')==[[rr,cc]] for rr in range(4) for cc in range(3))
            rec=dict(id=name,mode=mode,seconds=sec,num_rows=tbl.num_rows,num_cols=tbl.num_cols,orientation=tbl.orientation.value,input_tokens=len(cells),assigned_tokens=sum(t in assignments for t,r in tokens),logical_grid_correct=correct,logical_grid_total=12 if truth else None,assignments=assignments,table=tbl.model_dump(mode='json'),tokens=[c.model_dump(mode='json') for c in cells])
            out.append(rec);save('table_results.json',dict(snapshot=str(modelroot),cases=out));print('table',name,mode,tbl.num_rows,tbl.num_cols,len(tbl.table_cells),rec['assigned_tokens'],correct,round(sec,3),flush=True)

def backend_probe():
    import pypdfium2 as pdfium
    from docling.datamodel.document import InputDocument
    from docling.datamodel.base_models import InputFormat
    from docling.backend.docling_parse_backend import ThreadedDoclingParseDocumentBackend
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    from docling.datamodel.backend_options import ThreadedDoclingParseBackendOptions
    im=Image.open(ROOT/'pages'/f'{SOURCES[0][0]}.png').convert('RGB');im.thumbnail((600,900));im.save(ROOT/'tmp'/'base.pdf',resolution=72.)
    results=[];renders={}
    for angle in (0,90,180,270):
        writer=pdfium.PdfDocument(ROOT/'tmp'/'base.pdf');p=writer[0];p.set_rotation(angle);path=ROOT/'tmp'/f'rotate_{angle}.pdf'
        writer.save(path);p.close();writer.close()
        for cls in (ThreadedDoclingParseDocumentBackend,PyPdfiumDocumentBackend):
            doc=InputDocument(path_or_stream=path,format=InputFormat.PDF,backend=cls)
            backend=doc._backend
            pb=next(backend.iter_pages()) if cls==ThreadedDoclingParseDocumentBackend else backend.load_page(0)
            image=pb.get_page_image(scale=1.);size=pb.get_size();sp=pb.get_segmented_page();key=cls.__name__
            image.save(ROOT/'tmp'/f'{key}_{angle}.png')
            if angle==0:renders[key]=image
            expected=renders[key].rotate(-angle,expand=True);equal_size=image.size==expected.size
            mae=float(np.mean(abs(np.asarray(image.convert('L'),dtype=float)-np.asarray(expected.convert('L'),dtype=float)))) if equal_size else None
            results.append(dict(backend=key,pdf_rotate=angle,render_size=list(image.size),page_size=size.model_dump(),mae_to_rotate0=mae,native_text_cells=len(sp.textline_cells) if sp else None))
            backend.unload()
    # Round-trip corners use the installed OCR mapping helper, with offsets.
    from docling.models.stages.ocr.tesseract_utils import parse_tesseract_orientation,tesseract_box_to_bounding_rectangle
    roundtrips=[]
    for a in (0,90,180,270):
        r=tesseract_box_to_bounding_rectangle(bb([20,30,100,50]),original_offset=bb([11,13,211,313]),scale=2.,orientation=parse_tesseract_orientation(str(a)),im_size=(200,300))
        roundtrips.append(dict(osd_cw=a,rect=r.model_dump(mode='json'),angle_ccw=r.angle_360,aabb=r.to_bounding_box().model_dump(mode='json')))
    save('backend_results.json',dict(pdf_tests=results,cell_mapping=roundtrips))
    print(json.dumps(results),flush=True)
if __name__=='__main__':
    if sys.argv[1]=='tables':tables()
    elif sys.argv[1]=='backend':backend_probe()
