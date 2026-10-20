"""Tiny deterministic probes of the INSTALLED matcher; no neural inference.
The 2x2 grid is controlled, not model quality or human annotation.
"""
import os
os.environ['HF_HUB_OFFLINE']='1'
import copy
from types import SimpleNamespace as NS
from research_tables import bb, label_cell, save, serial
from docling_ibm_models.tableformer.data_management.tf_cell_matcher import CellMatcher
from docling_ibm_models.tableformer.data_management.matching_post_processor import MatchingPostProcessor
from docling_ibm_models.tableformer.data_management.tf_predictor import TFPredictor
from docling_core.types.doc import TableCell
from docling_core.types.doc.page import TextCellUnit, BoundingRectangle, TextDirection
from docling.backend.docling_parse_backend import ThreadedDoclingParsePageBackend
from docling.models.stages.table_structure.table_structure_model_v2 import TableStructureModelV2

CONFIG={'predict':{'pdf_cell_iou_thres':.05}}
GRID=[dict(cell_id=i,row_id=i//2,column_id=i%2,label='body',cell_class=2,bbox=b)
      for i,b in enumerate([[10,10,90,40],[110,10,190,40],[10,60,90,90],[110,60,190,90]])]
ANCHORS=[dict(id=i,text=f'A{i}',bbox=b) for i,b in enumerate(
    [[20,15,40,35],[120,15,140,35],[20,65,40,85],[120,65,140,85]])]

def match_probe(name, tokens, postprocess=True):
    cm=CellMatcher(CONFIG)
    pp=MatchingPostProcessor(CONFIG)
    grid=copy.deepcopy(GRID)
    raw,_=cm._intersection_over_pdf_match(grid,tokens)
    details=dict(table_cells=grid,pdf_cells=copy.deepcopy(tokens),matches=copy.deepcopy(raw),
                 table_bbox=[0,0,200,100],page_height=100,page_width=200)
    if postprocess:
        details=pp.process(details)
    tf=TFPredictor.__new__(TFPredictor)
    responses=tf._merge_tf_output(tf._generate_tf_response(details['table_cells'],details['matches']),details['pdf_cells'])
    cells=[TableCell.model_validate(copy.deepcopy(r)) for r in responses]
    landing={}
    for t in tokens:
        landing[t['text']]=[dict(row=c.start_row_offset_idx,col=c.start_col_offset_idx,text=c.text)
                           for c in cells if t['text'] in c.text]
    result=dict(name=name,postprocess=postprocess,tokens=tokens,initial_matches=raw,
                final_matches=details['matches'],table_cells=[c.model_dump(mode='json') for c in cells],landing=landing)
    print(name,landing,flush=True)
    return result

def main():
    cases=[]
    cases.append(match_probe('within-one-cell-line',ANCHORS+[dict(id=4,text='WORD_ONE WORD_TWO',bbox=[45,15,80,35])]))
    cases.append(match_probe('within-one-cell-two-words',ANCHORS+[dict(id=4,text='WORD_ONE',bbox=[45,15,59,35]),dict(id=5,text='WORD_TWO',bbox=[64,15,80,35])]))
    cases.append(match_probe('cross-column',ANCHORS+[dict(id=4,text='LEFT_CONTENT RIGHT_CONTENT',bbox=[70,15,150,35])]))
    cases.append(match_probe('cross-row-rule',ANCHORS+[dict(id=4,text='TOP_CONTENT BOTTOM_CONTENT',bbox=[20,25,40,80])]))
    cases.append(match_probe('partial-overlap',ANCHORS+[dict(id=4,text='PARTIAL',bbox=[180,15,230,35])]))
    cases.append(match_probe('no-overlap-row-band',ANCHORS+[dict(id=4,text='ROW_ORPHAN',bbox=[210,15,230,35])]))
    cases.append(match_probe('no-overlap-column-band',ANCHORS+[dict(id=4,text='COL_ORPHAN',bbox=[20,110,40,130])]))
    cases.append(match_probe('no-overlap-either-band',ANCHORS+[dict(id=4,text='LOST_ORPHAN',bbox=[210,110,230,130])]))
    cases.append(match_probe('cross-column-postprocessor-disabled',ANCHORS+[dict(id=4,text='LEFT_CONTENT RIGHT_CONTENT',bbox=[70,15,150,35])],False))
    # Actual backend text extraction helper: cached segmented lines may be OCR
    # if page.parsed_page aliases the cached object; PDFium differs (see source).
    backend=ThreadedDoclingParsePageBackend.__new__(ThreadedDoclingParsePageBackend)
    backend._result=NS(success=True)
    backend._seg_page=NS(textline_cells=[label_cell(0,'FUSED_BACKEND',[70,15,150,35])])
    backend_reads={name:backend.get_text_in_rect(bb(b)) for name,b in {
        'left':[10,10,90,40], 'right':[110,10,190,40],
        'overlapping-left':[10,10,130,40], 'overlapping-right':[90,10,190,40]}.items()}
    # V2 matching is a different algorithm: >.3 overlap, independently per
    # predicted cell, so crossing text CAN appear in two cells. No V2 weights.
    v2=TableStructureModelV2.__new__(TableStructureModelV2)
    v2_texts=v2._match_texts([bb([10,10,90,40]),bb([110,10,190,40])],
                           [label_cell(0,'V2_FUSED',[30,15,170,35])],.3)
    # Oriented quadrilateral is reduced to its axis-aligned envelope.
    skew=BoundingRectangle(r_x0=10,r_y0=30,r_x1=90,r_y1=40,r_x2=90,r_y2=20,r_x3=10,r_y3=10,
                           coord_origin='TOPLEFT')
    save('micro-probes.json',dict(cases=cases,backend_reads=backend_reads,
                                  v2_texts=v2_texts,skew_envelope=skew.to_bounding_box().model_dump(mode='json')))
    print('backend_reads',backend_reads,'v2_texts',v2_texts,'skew',skew.to_bounding_box(),flush=True)

if __name__=='__main__':
    main()
