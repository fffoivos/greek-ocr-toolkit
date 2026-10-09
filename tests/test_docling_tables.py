"""Table pieces, page-space delivery and real installed V1 matching contracts."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace as NS
import numpy as np
import pytest
from PIL import Image,ImageDraw,ImageFont

from greekocr.glyphs.table_lines import table_text_pieces, recognition_pieces
from greekocr.glyphs.page_text_lines import segment_page

FONT=Path(__file__).parent/'fixtures/fonts/GFSDidot-Regular.ttf'


def scene(ruled):
 im=Image.new('L',(800,500),255);d=ImageDraw.Draw(im);font=ImageFont.truetype(str(FONT),28)
 truth=[]
 for y in (190,250,310,370):
  for x in (50,440):
   text='123,45 λόγος'
   d.text((x,y),text,font=font,fill=20)
   truth.append(d.textbbox((x,y),text,font=font))
 if ruled:d.line((400,170,400,425),fill=20,width=2)
 return im,truth


@pytest.mark.parametrize('ruled',[True,False],ids=['ruled-boundary','unruled-gutter'])
def test_pieces_split_entries_and_recover_both_sides(ruled):
 im,truth=scene(ruled)
 pieces=table_text_pieces(im,(30,170,780,430))
 assert pieces and all(not (p.box[0]<400<p.box[2]) for p in pieces)
 for a,t,b,bot in truth:
  cover=np.zeros((bot-t,b-a),bool)
  for p in pieces:
   x0,y0,x1,y1=p.box
   cover[max(0,y0-t):max(0,min(bot,y1)-t),max(0,x0-a):max(0,min(b,x1)-a)]=True
  ink=np.asarray(im)[t:bot,a:b]<128
  assert (ink&cover).sum()/ink.sum()>.97


def test_later_boundary_does_not_cut_full_width_prose():
 im,_=scene(True);d=ImageDraw.Draw(im);font=ImageFont.truetype(str(FONT),28)
 for y in (25,70,115):d.text((50,y),'λόγος καὶ ἀνθρώπων λόγος καὶ ἀνθρώπων λόγος',font=font,fill=20)
 base=segment_page(im)
 pieces,_,_=recognition_pieces(im,base.lines,[('local',(30,170,780,430))])
 prose=[p for p in pieces if p.box[3]<170]
 assert len(prose)==3
 assert all(p.box[0]<400<p.box[2] for p in prose)
 assert all(not (p.box[0]<400<p.box[2]) for p in pieces if p.table_id)


def test_frame_touching_digits_survive():
 im,_=scene(True);d=ImageDraw.Draw(im)
 d.rectangle((30,170,780,430),outline=20,width=2)
 # Connect the left frame to the first body in every row.
 for y in (210,270,330,390):d.line((30,y,57,y),fill=20,width=2)
 pieces=table_text_pieces(im,(25,165,785,435))
 assert sum(p.box[0]<200 for p in pieces)>=4
 assert all(p.box[2]-p.box[0]<400 for p in pieces)


def cell(text,box=(10,10,40,30),ocr=False):
 from docling_core.types.doc import BoundingBox,CoordOrigin
 from docling_core.types.doc.page import TextCell,BoundingRectangle
 return TextCell(index=0,text=text,orig=text,from_ocr=ocr,rect=BoundingRectangle.from_bounding_box(
  BoundingBox(l=box[0],t=box[1],r=box[2],b=box[3],coord_origin=CoordOrigin.TOPLEFT)))


@pytest.mark.parametrize('aliased',[True,False])
def test_stale_native_and_ocr_words_and_chars_cleared_in_backend(aliased):
 from docling.models.base_ocr_model import _empty_segmented_page
 from docling_core.types.doc import Size,BoundingBox
 from docling_core.types.doc.page import TextCellUnit
 from greekocr.deploy.docling_plugin.model import GlossapiOcrModel
 parsed=_empty_segmented_page(NS(size=Size(width=100,height=100)))
 backend=parsed if aliased else deepcopy(parsed)
 for p in (parsed,backend):
  p.textline_cells=[cell('OLD_LINE')];p.has_lines=True
  p.word_cells=[cell('OLD_NATIVE'),cell('OLD_OCR',ocr=True)];p.has_words=True
  p.char_cells=[cell('OLD_CHAR',ocr=True)];p.has_chars=True
 page=NS(parsed_page=parsed,_backend=NS(get_segmented_page=lambda:backend))
 ours=[cell('FRESH',ocr=True)]
 GlossapiOcrModel._install(ours,page)
 for p in (parsed,backend):
  assert p.textline_cells==ours
  assert not p.word_cells and not p.char_cells and not p.has_words and not p.has_chars
  assert not p.get_cells_in_bbox(TextCellUnit.WORD,BoundingBox(l=0,t=0,r=100,b=100))


def test_ocr_mode_and_recognition_mode_are_independent():
 from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
 from docling.datamodel.pipeline_options import OcrMode
 o=GlossapiOcrOptions(checkpoint=Path('unused'),codec=Path('unused'),replace_policy='all',
                     mode=OcrMode.FULL_PAGE,recognition_mode='detector')
 assert o.mode==OcrMode.FULL_PAGE and o.recognition_mode=='detector'
 with pytest.raises(ValueError):GlossapiOcrOptions(checkpoint=Path('unused'),codec=Path('unused'),replace_policy='all',mode='detector')


def test_plugin_uses_actual_xy_render_ratios_and_separate_piece_recognition(monkeypatch):
 from docling.datamodel.accelerator_options import AcceleratorOptions
 from docling.datamodel.base_models import Cluster,LayoutPrediction
 from docling_core.types.doc import Size,BoundingBox,CoordOrigin,DocItemLabel
 from docling.models.base_ocr_model import _empty_segmented_page
 from greekocr.deploy.docling_plugin.model import GlossapiOcrModel
 from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
 im,_=scene(True);size=Size(width=400,height=250)
 parsed=_empty_segmented_page(NS(size=size))
 page=NS(page_no=1,size=size,parsed_page=parsed,get_image=lambda **kw:im,
         predictions=NS(layout=LayoutPrediction(clusters=[Cluster(id=3,label=DocItemLabel.TABLE,confidence=.9,
          bbox=BoundingBox(l=15,t=85,r=390,b=215,coord_origin=CoordOrigin.TOPLEFT),cells=[])])))
 o=GlossapiOcrOptions(checkpoint=Path('unused'),codec=Path('unused'),replace_policy='all',recognition_mode='detector',crop_scale=3)
 model=GlossapiOcrModel(enabled=True,artifacts_path=None,options=o,accelerator_options=AcceleratorOptions(device='cpu'))
 seen=[]
 def recognise(strips):
  seen.extend(strips);return [(f'PIECE{i}',.9) for i in range(len(strips))]
 monkeypatch.setattr(model,'_get_recognizer',lambda:NS(recognize=recognise))
 list(model(NS(input=NS(file=Path('scan.png'))),[page]))
 assert len(parsed.textline_cells)==len(seen)>8
 for c in parsed.textline_cells:
  b=c.rect.to_bounding_box()
  assert b.coord_origin==CoordOrigin.TOPLEFT and 0<=b.l<b.r<=400 and 0<=b.t<b.b<=250
  assert not b.l<200<b.r
 assert {c.text for c in parsed.textline_cells}=={f'PIECE{i}' for i in range(len(seen))}


def test_installed_tableformer_labels_and_fused_negative_control():
 # Same controlled 2x2 methodology as .astra/docling_research/probe_matching.py.
 # Uses the installed matcher, postprocessor and TableCell serializer, not mocks.
 from docling_ibm_models.tableformer.data_management.tf_cell_matcher import CellMatcher
 from docling_ibm_models.tableformer.data_management.matching_post_processor import MatchingPostProcessor
 from docling_ibm_models.tableformer.data_management.tf_predictor import TFPredictor
 from docling_core.types.doc import TableCell
 config={'predict':{'pdf_cell_iou_thres':.05}}
 grid=[dict(cell_id=i,row_id=i//2,column_id=i%2,label='body',cell_class=2,bbox=b) for i,b in enumerate(
  [[10,10,90,40],[110,10,190,40],[10,60,90,90],[110,60,190,90]])]
 anchors=[dict(id=i,text=f'LABEL{i}',bbox=b) for i,b in enumerate(
  [[20,15,40,35],[120,15,140,35],[20,65,40,85],[120,65,140,85]])]
 def run(tokens):
  raw,_=CellMatcher(config)._intersection_over_pdf_match(deepcopy(grid),tokens)
  details=MatchingPostProcessor(config).process(dict(table_cells=deepcopy(grid),pdf_cells=deepcopy(tokens),
   matches=raw,table_bbox=[0,0,200,100],page_height=100,page_width=200))
  tf=TFPredictor.__new__(TFPredictor)
  out=tf._merge_tf_output(tf._generate_tf_response(details['table_cells'],details['matches']),details['pdf_cells'])
  return [TableCell.model_validate(deepcopy(r)) for r in out]
 correct=run(anchors)
 for i in range(4):
  owners=[c for c in correct if f'LABEL{i}' in c.text.split()]
  assert len(owners)==1 and (owners[0].start_row_offset_idx,owners[0].start_col_offset_idx)==divmod(i,2)
 fused=run(anchors+[dict(id=4,text='LEFT_CONTENT RIGHT_CONTENT',bbox=[70,15,150,35])])
 owners=[c for c in fused if 'LEFT_CONTENT' in c.text]
 assert len(owners)==1 and 'RIGHT_CONTENT' in owners[0].text
 # Survival of both words is a FAILURE of the intended separate ownership.
 assert owners[0].start_col_offset_idx==1


def test_narrow_repeated_gutter_splits_below_word_gap_threshold():
 im=Image.new('L',(190,280),255);d=ImageDraw.Draw(im)
 for y in (30,90,150,210):
  for x in (20,34,48,67,81,95):
   d.rectangle((x,y,x+10,y+20),outline=20,width=3)
 pieces=table_text_pieces(im,(5,10,170,255))
 assert len(pieces)>=8
 assert all(not p.box[0]<63<p.box[2] for p in pieces)


def test_table_border_clipping_preserves_scalar_neighbour_metadata():
 from greekocr.glyphs.table_lines import detector_pieces
 im,_=scene(False)
 lines=segment_page(im).lines
 for line in lines:line.neighbours['page_edge']=True
 pieces=detector_pieces(im,lines,[('partial',(100,170,350,430))])
 outside=[p for p in pieces if not p.table_id]
 assert outside and all(p.line.neighbours['page_edge'] is True for p in outside)
 assert all(len(p.line.top)==p.line.x1-p.line.x0 for p in pieces)


def test_sentence_between_table_blocks_is_refitted_without_divider():
 im=Image.new('L',(800,760),255);d=ImageDraw.Draw(im);font=ImageFont.truetype(str(FONT),28)
 for top in (20,470):
  for y in (top+20,top+80,top+140):
   for x in (40,450):d.text((x,y),'λόγος 123,45',font=font,fill=20)
  d.line((400,top,400,top+210),fill=20,width=2)
 d.text((40,340),'λόγος καὶ ἀνθρώπων λόγος καὶ ἀνθρώπων λόγος',font=font,fill=20)
 lines=segment_page(im).lines
 pieces,_,_=recognition_pieces(im,lines,[('one',(20,10,780,260)),('two',(20,460,780,710))])
 middle=[p for p in pieces if 300<p.box[1]<400]
 assert len(middle)==1 and middle[0].box[0]<400<middle[0].box[2]
