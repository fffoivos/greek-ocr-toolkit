"""Regenerate machine-readable summaries from the measured result files."""
from research_orientation import *
import importlib.metadata as md,platform
def version(p):
    try:return md.version(p)
    except md.PackageNotFoundError:return 'not installed'
def filehash(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def rows(file):return [json.loads(l) for l in (ROOT/file).read_text().splitlines()]
def group_label(r):
    if r['scope']=='roi':return 'composite ROI '+r['unit']
    return {'whole':'whole page','skew':'skew control','composite':'composite dominant','crop':r['unit']}[r['kind']]
def main():
    cases=load('testset/manifest.json')['cases'];assert len(cases)==136
    result=[]
    for file in ['geometry','osd','ocr_vote','constrained_vote','rapid']:
        rs=rows(file+'.jsonl');assert len(rs)==148,(file,len(rs))
        for mode in (['full','axis','projection'] if file=='geometry' else ['full']):
            groups={}
            for r in rs:groups.setdefault((group_label(r),r['truth_cw']),[]).append(r)
            for (unit,angle),rr in sorted(groups.items()):
                key={'full':'correct','axis':'axis_correct','projection':'projection_axis_correct'}[mode] if file=='geometry' else 'correct'
                times=[r.get('uncached_equivalent_seconds',r['seconds']) if file=='ocr_vote' else r['seconds'] for r in rr]
                result.append(dict(detector=file+(' '+mode if file=='geometry' else ''),unit=unit,rotation_cw=angle,n=len(rr),correct=sum(r[key] for r in rr),abstain=sum(r['pred_cw'] is None for r in rr) if mode=='full' else 0,accuracy=sum(r[key] for r in rr)/len(rr),mean_seconds=float(np.mean(times)),mean_actual_seconds=float(np.mean([r['seconds'] for r in rr]))))
    save('results_summary.json',dict(rows=result))
    with (ROOT/'results_summary.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(result[0]));w.writeheader();w.writerows(result)
    # Page-layout diagnosis: count detections, not an OCR accuracy metric.
    layout=rows('layout.jsonl');assert len(layout)==64
    save('layout_summary.json',dict(cases=[dict(id=r['id'],kind=r['kind'],truth_cw=r['truth_cw'],seconds=r['seconds'],raw_clusters=len(r['raw']['clusters']),raw_labels=dict(Counter(c['label'] for c in r['raw']['clusters'])),retained_tables=[c for c in r['retained']['clusters'] if c['label']=='table']) for r in layout]))
    lines=rows('lines.jsonl');assert len(lines)==40
    sums=[]
    for a in (0,90,180,270):
        rr=[r for r in lines if r['truth_cw']==a]
        sums.append(dict(rotation_cw=a,n=len(rr),mean_seconds=float(np.mean([r['seconds'] for r in rr])),mean_kept=float(np.mean([r['kept'] for r in rr])),median_page_median_length=float(np.median([r['median_length'] for r in rr])),median_page_median_xheight=float(np.median([r['median_xheight'] for r in rr])),mean_page_fraction_short=float(np.mean([r['shorter_than_3xh'] for r in rr]))))
    save('lines_summary.json',dict(rows=sums,cases=lines))
    source=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/lib/python3.11/site-packages')
    selections={
      'docling/pipeline/standard_pdf_pipeline.py':[(787,794)],
      'docling/document_converter.py':[(271,277)],
      'docling/models/stages/ocr/auto_ocr_model.py':[(65,80),(121,139),(152,165),(175,189)],
      'docling/backend/image_backend.py':[(56,69)],
      'docling/backend/pypdfium2_backend.py':[(164,204),(650,665)],
      'docling/backend/docling_parse_backend.py':[(246,261),(291,301),(364,367)],
      'docling_parse/pdf_parser.py':[(398,428),(1264,1279)],
      'docling/datamodel/pipeline_options.py':[(151,174),(425,449),(614,665),(1691,1720),(2153,2161)],
      'docling/models/stages/layout/layout_object_detection_model.py':[(95,115),(149,185)],
      'docling/models/inference_engines/object_detection/transformers_engine.py':[(220,244)],
      'docling/utils/layout_postprocessor.py':[(129,147),(660,688)],
      'docling/models/stages/ocr/tesseract_ocr_cli_model.py':[(74,76),(262,284),(351,374),(409,423)],
      'docling/models/stages/ocr/tesseract_ocr_model.py':[(193,220)],
      'docling/models/stages/ocr/tesseract_utils.py':[(119,163)],
      'docling/utils/orientation.py':[(12,70)],
      'docling_core/types/doc/page.py':[(109,161),(169,211),(273,309),(1254,1278)],
      'docling/models/stages/table_structure/table_structure_model.py':[(213,273),(294,322)],
      'docling/datamodel/base_models.py':[(436,441)],
      'docling/models/stages/reading_order/readingorder_model.py':[(97,112),(256,273)],
      'docling_core/types/doc/items/table/table_data.py':[(90,111),(295,315),(388,407)],
      'docling/models/stages/ocr/rapid_ocr_model.py':[(764,798)],
      'rapidocr/config.yaml':[(161,168)],
      'rapidocr/ch_ppocr_cls/main.py':[(36,44),(77,110)]}
    evidence=[]
    for name,ranges in selections.items():
        p=source/name;text=p.read_text().splitlines()
        evidence.append(dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),excerpts=[dict(start=a,end=b,text='\n'.join(f'{i+1}: {text[i]}' for i in range(a-1,min(b,len(text))))) for a,b in ranges]))
    worktree=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-astra-lines4')
    for name,ranges in {'greekocr/glyphs/page_text_lines.py':[(27,42),(143,172),(927,966)],'greekocr/glyphs/pixel_segments.py':[(1,5),(350,390)]}.items():
        p=worktree/name;text=p.read_text().splitlines();evidence.append(dict(file=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),excerpts=[dict(start=a,end=b,text='\n'.join(f'{i+1}: {text[i]}' for i in range(a-1,min(b,len(text))))) for a,b in ranges]))
    save('source_evidence.json',evidence)
    model_files=[]
    for root in [Path(load('table_results.json')['snapshot']),Path(load('layout_config.json')['snapshot'])]:
        for p in root.rglob('*'):
            if p.is_file() and p.suffix in ('.json','.safetensors','.pt','.bin'):model_files.append(dict(file=str(p),bytes=p.stat().st_size,sha256=filehash(p)))
    save('model_files.json',model_files)
    save('run_manifest.json',dict(python=sys.executable,date='2026-10-09',platform=platform.platform(),machine=platform.machine(),packages={p:version(p) for p in ['docling','docling-core','docling-ibm-models','docling-parse','torch','transformers','opencv-python','opencv-python-headless','onnxruntime','rapidocr']},env=dict(HF_HUB_OFFLINE=os.environ['HF_HUB_OFFLINE'],TRANSFORMERS_OFFLINE=os.environ['TRANSFORMERS_OFFLINE'],PYTHONDONTWRITEBYTECODE=os.environ['PYTHONDONTWRITEBYTECODE']),input_pages={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'pages').glob('*.png')},scripts={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},table=load('table_results.json')['snapshot'],layout=load('layout_config.json')['snapshot'],rapid=load('rapid_config.json'),ocr_vote_cache=dict(actual_tesseract_forwards=sum(not d['cached'] for r in rows('ocr_vote.jsonl') for d in r['details']),logical_hypothesis_evaluations=148*4)))
    print('All primary result cardinalities validated',flush=True)
if __name__=='__main__':main()
