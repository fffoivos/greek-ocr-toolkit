"""Offline table/OCR research. All outputs are written beside this script.

Runs the installed TableStructureModel.predict_tables, its actual layout cell
assignment, and ReadingOrderModel's TableItem builder. No input boxes.json is read.
The first forward pass for an image/mode is real; subsequent identical network
inputs reuse the exact tensors, while all matching/postprocessing runs afresh.
"""
import os
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

import argparse
import copy
import hashlib
import importlib.metadata
import json
import math
import time
from collections import Counter
from pathlib import Path
from types import SimpleNamespace as NS

import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw
from docling.datamodel.accelerator_options import AcceleratorOptions
from docling.datamodel.base_models import Cluster, LayoutPrediction
from docling.datamodel.pipeline_options import TableStructureOptions, TableFormerMode
from docling.models.base_ocr_model import _empty_segmented_page
from docling.models.stages.table_structure.table_structure_model import TableStructureModel
from docling.models.stages.reading_order.readingorder_model import ReadingOrderModel
from docling.utils.layout_postprocessor import LayoutPostprocessor
from docling_core.types.doc import BoundingBox, CoordOrigin, DocItemLabel, DoclingDocument, Size
from docling_core.types.doc.page import BoundingRectangle, TextCell

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'experiments'
MODEL_ROOT = Path('/Users/foivoskarounos-zamparloukos/.cache/huggingface/hub/models--docling-project--docling-models/snapshots/fc0f2d45e2218ea24bce5045f58a389aed16dc23/model_artifacts/tableformer')
# Manually chosen table regions from pixels, in ORIGINAL source PNG coordinates.
TABLES = {
    'an-7a2b17a3fb0f-p000200': (2090, 150, 3190, 2090),
    's2-200e977f2dab5291c42c-p00035': (565, 745, 2900, 3840),
    's2-831443dc5e6f1ccfbaf5-p00020': (55, 920, 3290, 3800),
}

def bb(vals):
    return BoundingBox(l=vals[0], t=vals[1], r=vals[2], b=vals[3], coord_origin=CoordOrigin.TOPLEFT)

def serial(obj):
    if hasattr(obj, 'model_dump'):
        return obj.model_dump(mode='json')
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    if isinstance(obj, (np.ndarray, torch.Tensor)):
        return obj.tolist()
    if isinstance(obj, Path):
        return str(obj)
    raise TypeError(type(obj).__name__)

def save(name, obj):
    OUT.mkdir(exist_ok=True)
    (OUT / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=serial) + '\n')

def label_cell(i, text, vals, **kwargs):
    return TextCell(index=i, text=text, orig=text, from_ocr=True, confidence=.9,
                    rect=BoundingRectangle.from_bounding_box(bb(vals)), **kwargs)

def ink_mask(image):
    gray = np.asarray(image.convert('L'))
    ink = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, 51, 18)
    # Remove long straight rules; split decisions must come from word gaps,
    # not the vertical/horizontal rule's black pixels.
    h = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((1, 160), np.uint8))
    v = cv2.morphologyEx(ink, cv2.MORPH_OPEN, np.ones((160, 1), np.uint8))
    return cv2.bitwise_and(ink, cv2.bitwise_not(cv2.bitwise_or(h, v)))

def spans_for_line(line, mask, kind):
    left, right = int(line['x0']), int(line['x1'])
    n = right - left
    if n <= 0:
        return []
    if kind == 'line':
        return [(left, right)]
    # Per-column ink within the supplied font/diacritic curves (not the PDF
    # text layer). Closing across 2 pixels avoids splitting a character.
    top = np.minimum(line['font_top'], line['accent_top'])
    bottom = np.maximum(line['font_bottom'], line['accent_bottom'])
    has_ink = np.zeros(n, dtype=np.uint8)
    for j, x in enumerate(range(left, right)):
        if 0 <= x < mask.shape[1]:
            a = max(0, int(math.floor(top[min(j, len(top)-1)])))
            b = min(mask.shape[0], int(math.ceil(bottom[min(j, len(bottom)-1)])))
            has_ink[j] = np.count_nonzero(mask[a:b, x]) >= 2
    has_ink = cv2.morphologyEx(has_ink[None, :], cv2.MORPH_CLOSE,
                             np.ones((1, 3), np.uint8))[0]
    gap = max(4, round(float(line['xheight']) * (.30 if kind == 'word' else 1.5)))
    cuts = [0]
    starts = np.flatnonzero(np.diff(np.r_[0, has_ink == 0, 0].astype(int)) == 1)
    ends = np.flatnonzero(np.diff(np.r_[0, has_ink == 0, 0].astype(int)) == -1)
    for a, b in zip(starts, ends):
        if b - a >= gap and a > 0 and b < n:
            cuts.append((int(a) + int(b)) // 2)
    cuts.append(n)
    spans = []
    for a, b in zip(cuts, cuts[1:]):
        occupied = np.flatnonzero(has_ink[a:b])
        if len(occupied):
            spans.append((left+a+int(occupied[0]), left+a+int(occupied[-1])+1))
    # Do not improve recall by throwing out the original line if projection
    # found no ink; retain it as one uncertain piece.
    return spans or [(left, right)]

def controlled_cells(name, image, kind):
    lines = json.loads((ROOT / 'round3' / (name + '.lines.json')).read_text())
    mask = ink_mask(image) if kind != 'line' else None
    cells, meta = [], []
    for li, line in enumerate(lines):
        for pi, (a, b) in enumerate(spans_for_line(line, mask, kind)):
            q0, q1 = a-int(line['x0']), b-int(line['x0'])
            top = max(0., min(line['top'][q0:q1]))
            bottom = min(float(image.height), max(line['bottom'][q0:q1]))
            vals = [max(0,a)/3, top/3, min(image.width,b)/3, bottom/3]
            if vals[2] <= vals[0] or vals[3] <= vals[1]:
                continue
            token = f'L{li:04d}P{pi:02d}'
            cells.append(label_cell(len(cells), token, vals))
            meta.append(dict(id=len(cells)-1, token=token, line=li, piece=pi,
                             source_box=[v*3 for v in vals], discounted=line['discounted']))
    return cells, meta

class StubBackend:
    """No PDF layer. Optional sentinel words prove backend-word precedence."""
    def __init__(self, image, size, words=None, rect_text=''):
        self.image = image
        self.segmented = _empty_segmented_page(NS(size=size))
        self.segmented.word_cells = words or []
        self.segmented.has_words = bool(words)
        self.rect_text = rect_text
        self.rect_calls = []
    def is_valid(self):
        return True
    def get_segmented_page(self):
        return self.segmented
    def get_text_in_rect(self, bbox):
        self.rect_calls.append(bbox.model_dump(mode='json'))
        return self.rect_text

def page_for(image, cells, region, words=None, rect_text=''):
    size = Size(width=image.width/3, height=image.height/3)
    backend = StubBackend(image, size, words, rect_text)
    cluster = Cluster(id=0, label=DocItemLabel.TABLE, confidence=1., bbox=bb([v/3 for v in region]), cells=[])
    page = NS(page_no=1, size=size, _backend=backend, cells=cells,
              predictions=NS(layout=LayoutPrediction(clusters=[cluster]), tablestructure=None),
              get_image=lambda scale: image.resize((round(size.width*scale), round(size.height*scale))))
    # Actual installed cell-to-layout matching, with a fixed manual table box.
    proc = LayoutPostprocessor.__new__(LayoutPostprocessor)
    proc.cells = cells
    proc._assign_cells_to_clusters([cluster])
    return page, cluster, backend

def build_model(mode):
    t = time.monotonic()
    model = TableStructureModel(enabled=True, artifacts_path=MODEL_ROOT,
        options=TableStructureOptions(mode=TableFormerMode(mode), do_cell_matching=True),
        accelerator_options=AcceleratorOptions(device='cpu', num_threads=4))
    print('MODEL', mode, 'loaded_s', round(time.monotonic()-t,3), flush=True)
    network = model.tf_predictor._model
    original = network.predict
    cache = {}
    forwards = []
    def cached_predict(image_batch, *args, **kwargs):
        key = hashlib.sha256(image_batch.detach().cpu().numpy().tobytes()).hexdigest()
        if key not in cache:
            t = time.monotonic()
            print('FORWARD', mode, key[:10], 'start', flush=True)
            cache[key] = copy.deepcopy(original(image_batch, *args, **kwargs))
            dt = time.monotonic()-t
            forwards.append(dict(key=key, seconds=dt))
            print('FORWARD', mode, key[:10], 'seconds', round(dt,3), flush=True)
        return copy.deepcopy(cache[key])
    network.predict = cached_predict
    original_multi = model.tf_predictor.multi_table_predict
    captured = []
    def capture(*args, **kwargs):
        out = original_multi(*args, **kwargs)
        captured[:] = copy.deepcopy(out)
        return out
    model.tf_predictor.multi_table_predict = capture
    return model, captured, forwards

def run_case(model, captured, name, image, cells, meta, region, kind, matching=True, words=None, rect_text=''):
    model.do_cell_matching = matching
    page, cluster, backend = page_for(image,cells,region,words,rect_text)
    t = time.monotonic()
    model.predict_tables(NS(timings={}), [page])
    table = page.predictions.tablestructure.table_map[0]
    # Exercise the exact final TableItem construction helper used by reading order.
    doc = DoclingDocument(name=name)
    doc.add_page(page_no=1, size=page.size)
    table_item = ReadingOrderModel.__new__(ReadingOrderModel)._add_table_element(table,doc)
    known = {c.text for c in cells}
    occurrences = Counter()
    landing = {}
    for ci, c in enumerate(table_item.data.table_cells):
        for token in c.text.split():
            if token in known:
                occurrences[token] += 1
                landing.setdefault(token,[]).append(dict(table_cell=ci, row=c.start_row_offset_idx,
                                                        col=c.start_col_offset_idx, text=c.text))
    assigned_inputs = {c.text for c in cluster.cells}
    metrics = dict(page=name, variant=kind, mode=model.mode.value, matching=matching,
        table_cells=len(table.table_cells), rows=table.num_rows, cols=table.num_cols,
        page_input_cells=len(cells), table_input_cells=len(cluster.cells),
        assigned=sum(occurrences[x]>0 for x in assigned_inputs),
        split=0, duplicated=sum(occurrences[x]>1 for x in assigned_inputs),
        lost=sum(occurrences[x]==0 for x in assigned_inputs),
        layout_excluded=len(cells)-len(cluster.cells),
        backend_text_calls=len(backend.rect_calls), elapsed_s=round(time.monotonic()-t,3))
    details = captured[0]['predict_details']
    metrics['structural_cells_before_postprocess'] = len(details.get('prediction_bboxes_page',[]))
    metrics['final_match_count'] = len(details.get('matches',{}))
    assert metrics['assigned']+metrics['lost']==metrics['table_input_cells']
    assert all(token in known or token == rect_text or token == 'BACKEND_WORD'
               for c in table.table_cells for token in c.text.split())
    stem = f'{name}.{model.mode.value}.{kind}.matching-{int(matching)}'
    save(stem+'.json', dict(metrics=metrics, region_source_pixels=region, source_scale=3,
          cells=meta, layout_assigned_ids=[c.index for c in cluster.cells], landing=landing,
          raw_tableformer=captured[0], table=table.model_dump(mode='json'),
          final_table_item=table_item.model_dump(mode='json'), backend_text_calls=backend.rect_calls))
    # Pixel-based overlay: blue predicted/final table boxes, orange OCR boxes.
    overlay = image.copy().convert('RGB')
    draw = ImageDraw.Draw(overlay)
    draw.rectangle(region,outline='red',width=5)
    for c in cluster.cells:
        draw.rectangle(tuple(v*3 for v in c.rect.to_bounding_box().as_tuple()),outline='orange',width=2)
    for ci,c in enumerate(table.table_cells):
        if c.bbox:
            box=tuple(v*3 for v in c.bbox.as_tuple())
            draw.rectangle(box,outline='blue',width=2)
            draw.text((box[0],box[1]),f'{ci}:{c.start_row_offset_idx},{c.start_col_offset_idx}',fill='blue')
    overlay.thumbnail((1400,1400))
    overlay.save(OUT/(stem+'.jpg'))
    print(json.dumps(metrics),flush=True)
    return metrics

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--page',choices=list(TABLES),action='append')
    ap.add_argument('--mode',choices=['accurate','fast'],default='accurate')
    ap.add_argument('--variants',default='line,wide,word')
    ap.add_argument('--controls',action='store_true')
    args=ap.parse_args()
    OUT.mkdir(exist_ok=True)
    model,captured,forwards=build_model(args.mode)
    summary=[]
    for name in args.page or TABLES:
        image=Image.open(ROOT/'pages'/(name+'.png')).convert('RGB')
        for kind in args.variants.split(','):
            cells,meta=controlled_cells(name,image,kind)
            summary.append(run_case(model,captured,name,image,cells,meta,TABLES[name],kind))
        if args.controls:
            cells,meta=controlled_cells(name,image,'line')
            summary.append(run_case(model,captured,name,image,cells,meta,TABLES[name],'line-image-backend',False))
            # Sentinel in a table row, pretending an old native word is retained.
            candidates=[c for c in cells if c.rect.to_bounding_box().intersection_over_self(bb([v/3 for v in TABLES[name]]))>.8]
            center=bb([v/3 for v in TABLES[name]])
            seed=min(candidates,key=lambda c: abs((c.rect.to_bounding_box().t+c.rect.to_bounding_box().b)/2-(center.t+center.b)/2)+abs((c.rect.to_bounding_box().l+c.rect.to_bounding_box().r)/2-(center.l+center.r)/2))
            sentinel=seed.model_copy(update=dict(index=99999,text='BACKEND_WORD',orig='BACKEND_WORD',from_ocr=False))
            summary.append(run_case(model,captured,name,image,cells,meta,TABLES[name],'line-backend-word',True,[sentinel]))
    save(f'summary-{args.mode}.json',dict(metrics=summary,forwards=forwards,
         versions={p:importlib.metadata.version(p) for p in ['docling','docling-core','docling-ibm-models']},
         model_root=MODEL_ROOT,environment=dict(HF_HUB_OFFLINE=os.environ['HF_HUB_OFFLINE'])))

if __name__=='__main__':
    main()
