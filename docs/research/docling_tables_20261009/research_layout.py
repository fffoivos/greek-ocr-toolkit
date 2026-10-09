"""Offline Heron + complete layout postprocessing, varied injected OCR cells.

Every case executes a fresh neural forward on the same full-page image. No PDF
text or boxes.json is opened. Output boxes are logical page units (= PNG / 3).
"""
import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import copy
import csv
import hashlib
import json
import time
from collections import Counter
from pathlib import Path
from types import SimpleNamespace as NS

from PIL import Image, ImageDraw
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.pipeline_options import LayoutObjectDetectionOptions, LayoutPostprocessorOptions
from docling.models.stages.layout.layout_object_detection_model import LayoutObjectDetectionModel
from docling.models.stages.layout.layout_postprocessing_model import LayoutPostprocessingModel
from docling_core.types.doc import DocItemLabel, Size

from research_tables import ROOT, OUT, TABLES, StubBackend, bb, controlled_cells, label_cell, save

SNAPSHOT = Path('/Users/foivoskarounos-zamparloukos/.cache/huggingface/hub/models--docling-project--docling-layout-heron/snapshots/8f39ad3c0b4c58e9c2d2c84a38465abf757272d8')

def box(c):
    b = c.bbox
    return [b.l, b.t, b.r, b.b]

def table_records(prediction):
    return [dict(id=c.id, label=c.label.value, box=box(c), confidence=c.confidence,
                 text_cells=len(c.cells), tokens=[x.text for x in c.cells],
                 children=[x.id for x in c.children])
            for c in prediction.clusters if c.label in (DocItemLabel.TABLE, DocItemLabel.DOCUMENT_INDEX)]

def table_identity(records):
    return [{k:r[k] for k in ('id','label','box','confidence')} for r in records]

def run(model, post, name, image, variant, cells, metadata, control=None):
    size = Size(width=image.width/3, height=image.height/3)
    backend = StubBackend(image, size)
    backend.segmented.textline_cells = cells
    backend.segmented.has_lines = bool(cells)
    page = NS(page_no=1, size=size, _backend=backend, cells=cells,
              parsed_page=backend.segmented, predictions=NS(layout=None),
              get_image=lambda scale: image.resize((round(size.width*scale), round(size.height*scale))))
    conv = NS(timings={}, confidence=NS(pages={1:NS(layout_score=0.)}))
    started = time.monotonic()
    model.predict_layout(conv, [page])
    neural_seconds = time.monotonic()-started
    raw = copy.deepcopy(page.predictions.layout)
    raw_json = raw.model_dump(mode='json')
    processed = post.postprocess_layout(conv, [page])[0]
    raw_tables, final_tables = table_records(raw), table_records(processed)
    all_table_tokens = set(t for x in final_tables for t in x['tokens'])
    counts = Counter(c.label.value for c in processed.clusters)
    metrics = dict(page=name, variant=variant, input_cells=len(cells),
        raw_tables=len(raw_tables), final_tables=len(final_tables),
        table_text_cells=sum(x['text_cells'] for x in final_tables),
        unique_table_tokens=len(all_table_tokens),
        excluded_from_tables=len(set(x.text for x in cells)-all_table_tokens),
        final_clusters=len(processed.clusters), final_text_clusters=counts.get('text',0),
        layout_page_score=conv.confidence.pages[1].layout_score,
        neural_seconds=round(neural_seconds,4), elapsed_seconds=round(time.monotonic()-started,4),
        raw_sha256=hashlib.sha256(json.dumps(raw_json,sort_keys=True).encode()).hexdigest())
    detail = dict(metrics=metrics, raw_tables=raw_tables, final_tables=final_tables,
                  raw_prediction=raw_json, final_prediction=processed.model_dump(mode='json'),
                  input_metadata=metadata, control=control, final_label_counts=dict(counts))
    save(f'{name}.layout.{variant}.json',detail)
    print(json.dumps(dict(metrics=metrics, tables=table_identity(final_tables)),ensure_ascii=False),flush=True)
    if variant == 'line':
        thumb=image.copy(); thumb.thumbnail((1400,1400)); draw=ImageDraw.Draw(thumb)
        for t in final_tables:
            coords=[x*3*thumb.width/image.width for x in t['box']]
            draw.rectangle(coords,outline='red',width=3)
            draw.text((coords[0]+3,coords[1]+3),f"T{t['id']} {t['confidence']:.6f}",fill='red')
        thumb.save(OUT/f'{name}.layout.tables.jpg')
    return detail

def main():
    OUT.mkdir(exist_ok=True)
    artifacts=OUT/'layout-artifacts'; artifacts.mkdir(exist_ok=True)
    link=artifacts/'docling-project--docling-layout-heron'
    if not link.exists():
        link.symlink_to(SNAPSHOT,target_is_directory=True)
    assert SNAPSHOT.is_dir()
    options=LayoutObjectDetectionOptions()
    post_options=LayoutPostprocessorOptions()
    start=time.monotonic()
    model=LayoutObjectDetectionModel(artifacts_path=artifacts,
        accelerator_options=AcceleratorOptions(device='cpu',num_threads=4),options=options)
    post=LayoutPostprocessingModel(options=post_options)
    print('HERON_LOADED_SECONDS',round(time.monotonic()-start,3),flush=True)
    cases=[]
    for name, region in TABLES.items():
        image=Image.open(ROOT/'pages'/f'{name}.png').convert('RGB')
        line_cells,line_meta=controlled_cells(name,image,'line')
        base=run(model,post,name,image,'line',copy.deepcopy(line_cells),line_meta)
        cases.append(base)
        for variant in ('wide','word'):
            cells,meta=controlled_cells(name,image,variant)
            cases.append(run(model,post,name,image,variant,cells,meta))
        l,t,r,b=[x/3 for x in region]
        missing_box=bb([l,t,l+.35*(r-l),b])
        kept=[i for i,c in enumerate(line_cells) if c.rect.to_bounding_box().intersection_area_with(missing_box)==0]
        cases.append(run(model,post,name,image,'missing_left_35pct',
            copy.deepcopy([line_cells[i] for i in kept]),[line_meta[i] for i in kept],
            control=dict(removed=len(line_cells)-len(kept),missing_box=[missing_box.l,missing_box.t,missing_box.r,missing_box.b],
                         rule='Remove every line intersecting the left 35% of the manual table region')))
        cases.append(run(model,post,name,image,'no_cells',[],[]))
        low=copy.deepcopy(line_cells)
        for c in low: c.confidence=0.
        cases.append(run(model,post,name,image,'confidence_zero',low,line_meta))
        kept=[i for i,m in enumerate(line_meta) if m['discounted'] is None]
        cases.append(run(model,post,name,image,'discounted_omitted',
            copy.deepcopy([line_cells[i] for i in kept]),[line_meta[i] for i in kept],
            control=dict(removed=len(line_cells)-len(kept))))
        largest=max(base['final_tables'],key=lambda x:(x['box'][2]-x['box'][0])*(x['box'][3]-x['box'][1]))
        l,t,r,b=largest['box']; w,h=r-l,b-t
        # Both stress boxes stay inside the page; the crossing is the TABLE
        # border, not the image border. On the spread the upper margin is small.
        d=min(.10*h,.80*t)
        for variant,vals in [
            ('border_crossing_only',[l+.30*w,t-d,l+.70*w,t+d]),
            ('fused_table_and_outside_only',[l+.30*w,t-d,l+.70*w,t+2*d])]:
            assert 0 <= vals[0] < vals[2] <= image.width/3
            assert 0 <= vals[1] < vals[3] <= image.height/3
            cell=label_cell(10000,variant.upper(),vals)
            cases.append(run(model,post,name,image,variant,[cell],
                [dict(token=cell.text,source_box=[v*3 for v in vals])],
                control=dict(synthetic=True,description='One deliberately crossing box; the page pixels are unchanged')))
        page_cases=[x for x in cases if x['metrics']['page']==name]
        for case in page_cases:
            case['metrics']['raw_identical_to_line']=case['raw_prediction']==base['raw_prediction']
            case['metrics']['tables_identical_to_line']=table_identity(case['final_tables'])==table_identity(base['final_tables'])
            assert case['metrics']['raw_identical_to_line']
            assert case['metrics']['tables_identical_to_line']
    summary=dict(model_snapshot=str(SNAPSHOT), image_scale=1, source_to_page_scale=3,
        options=options.model_dump(mode='json'),post_options=post_options.model_dump(mode='json'),
        cases=[{k:x[k] for k in ('metrics','raw_tables','final_tables','control','final_label_counts')} for x in cases],
        all_raw_identical=True,all_table_identities_identical=True,
        source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__)]})
    save('layout-summary.json',summary)
    with (OUT/'layout-summary.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=list(cases[0]['metrics']))
        writer.writeheader(); writer.writerows(x['metrics'] for x in cases)

if __name__=='__main__': main()
