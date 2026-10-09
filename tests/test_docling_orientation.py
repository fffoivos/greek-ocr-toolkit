"""Actual Docling frame types, adapter stage ordering and table mapping."""
from pathlib import Path
from types import SimpleNamespace as NS
import numpy as np
import pytest
from PIL import Image,ImageDraw

from docling_core.types.doc import BoundingBox,CoordOrigin,Size,DocItemLabel
from docling_core.types.doc.page import BoundingRectangle,TextCell
from docling.datamodel.base_models import Cluster,LayoutPrediction,Table,TableStructurePrediction
from docling.models.base_ocr_model import _empty_segmented_page
from greekocr.glyphs.orientation import Orientation,QuarterTurn
from greekocr.deploy.docling_plugin.orientation import NormalizedPageBackend,PageOrientationAdapter,OrientedTableAdapter


def bbox(v):
    return BoundingBox(l=v[0],t=v[1],r=v[2],b=v[3],coord_origin=CoordOrigin.TOPLEFT)


@pytest.mark.parametrize('angle',[0,90,180,270])
def test_backend_is_one_coherent_frame_at_every_scale(angle):
    im = Image.new('RGB',(200,300),'white');ImageDraw.Draw(im).rectangle((20,30,60,70),fill='black')
    size = Size(width=200,height=300);parsed=_empty_segmented_page(NS(size=size))
    parsed.textline_cells=[TextCell(index=0,text='λόγος',orig='λόγος',from_ocr=False,
        rect=BoundingRectangle.from_bounding_box(bbox((20,30,60,70))))];parsed.has_lines=True
    backend=NS(get_size=lambda:size,get_page_image=lambda scale=1:im.resize((round(200*scale),round(300*scale))),
               get_segmented_page=lambda:parsed,get_bitmap_rects=lambda scale=1:[bbox((0,0,200,300))])
    adapter=NormalizedPageBackend(backend,angle)
    for scale in (1,2,3):
        assert adapter.get_page_image(scale).size==tuple(round(v*scale) for v in adapter.frame.size)
    assert adapter.get_segmented_page().textline_cells[0].rect.angle_360==angle%360
    assert np.array_equal(adapter.get_page_image(),im.rotate(angle,expand=True))
    assert parsed.textline_cells[0].rect.angle_360==0


def test_preprocessing_receives_rotated_backend_and_cache_is_invalidated(monkeypatch):
    import greekocr.deploy.docling_plugin.orientation as mod
    im=Image.new('RGB',(200,300),'white');size=Size(width=200,height=300)
    backend=NS(is_valid=lambda:True,get_size=lambda:size,get_page_image=lambda scale:im.resize((round(200*scale),round(300*scale))))
    page=NS(page_no=1,_backend=backend,size=size,_image_cache={1:im},parsed_page='old')
    seen=[]
    def preprocessing(conv,pages):
        p=list(pages)[0];seen.append((p.size.width,p.size.height,p._image_cache,p.parsed_page));yield p
    monkeypatch.setattr(mod,'discover_directions',lambda im:[])
    adapter=PageOrientationAdapter(preprocessing,decide=lambda im:Orientation(axis='vertical',orientation_cw=90))
    list(adapter(NS(),[page]))
    assert seen==[(300,200,{},None)]
    list(adapter(NS(),[page]))
    assert page.size.width==300 and len(adapter.records)==1  # never double-rotate


def test_mixed_page_does_not_get_global_rotation(monkeypatch):
    import greekocr.deploy.docling_plugin.orientation as mod
    size=Size(width=200,height=300);image=Image.new('L',(200,300),255)
    backend=NS(is_valid=lambda:True,get_size=lambda:size,get_page_image=lambda scale:image)
    page=NS(page_no=1,_backend=backend)
    monkeypatch.setattr(mod,'discover_directions',lambda im:[dict(axis='horizontal',components=10),dict(axis='vertical',components=90)])
    adapter=PageOrientationAdapter(lambda c,p:iter(p),decide=lambda im:Orientation(axis='vertical',orientation_cw=90))
    list(adapter(NS(),[page]))
    assert page._backend is backend and adapter.records[0]['mixed'] and not adapter.records[0]['applied']


@pytest.mark.parametrize('angle',[0,90,180,270])
def test_table_adapter_rotates_pixels_tokens_and_inverse_maps_grid(angle):
    from docling_core.types.doc import TableCell
    im=Image.new('RGB',(200,300),'white');ImageDraw.Draw(im).rectangle((30,40,80,60),fill='black')
    source=im.rotate(-angle,expand=True);frame=QuarterTurn(*source.size,angle)
    corners=frame.rectangle((30,40,80,60));r=BoundingRectangle(**{f'r_{a}{i}':p[j] for i,p in enumerate(corners) for j,a in enumerate(('x','y'))},coord_origin=CoordOrigin.TOPLEFT)
    cell=TextCell(index=7,text='TOKEN',orig='TOKEN',from_ocr=True,rect=r)
    cluster=Cluster(id=4,label=DocItemLabel.TABLE,confidence=1,bbox=bbox([0,0,*source.size]),cells=[cell])
    page=NS(page_no=1,size=Size(width=source.width,height=source.height),predictions=NS(layout=LayoutPrediction(clusters=[cluster])),get_image=lambda scale:source)
    def predict(conv,pages):
        p=pages[0];assert np.array_equal(p.get_image(scale=1),im)
        c=p.predictions.layout.clusters[0]
        assert c.cells[0].index==7 and c.cells[0].rect.angle_360==0
        assert c.cells[0].rect.to_bounding_box()==bbox((30,40,80,60))
        assert not p._backend.get_segmented_page().word_cells
        tc=TableCell(text='TOKEN',bbox=bbox((20,30,90,70)),row_span=1,col_span=1,start_row_offset_idx=2,end_row_offset_idx=3,start_col_offset_idx=1,end_col_offset_idx=2,column_header=False,row_header=False,row_section=False)
        table=Table(id=4,page_no=1,cluster=c,label=c.label,num_rows=4,num_cols=3,table_cells=[tc],otsl_seq=[])
        return [TableStructurePrediction(table_map={4:table})]
    adapter=OrientedTableAdapter(NS(predict_tables=predict,enabled=True))
    output=adapter.predict_tables(NS(),[page])[0].table_map[4]
    assert output.orientation.value==f'rot_{(-angle)%360}'
    assert (output.table_cells[0].start_row_offset_idx,output.table_cells[0].start_col_offset_idx)==(2,1)
    expected=frame.rectangle((20,30,90,70))
    assert output.table_cells[0].bbox==bbox([*expected.min(0),*expected.max(0)])


def test_real_pipeline_wiring_uses_adapters_before_layout_and_at_tables():
    import inspect
    from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
    source=inspect.getsource(StandardPdfPipeline._create_run_ctx)
    # Installed 2.135's actual graph, not the unrelated listing order of stages.
    assert 'preprocess.add_output_queue(layout.input_queue)' in source
    assert 'layout.add_output_queue(ocr.input_queue)' in source
    assert 'layout_postprocess.add_output_queue(table.input_queue)' in source
    assert 'model=self.preprocessing_model' in source and 'model=self.table_model' in source


def test_actual_tableformer_control_under_all_quarter_turns(tmp_path):
    from scripts.glyphs.evaluate_orientation_round4 import tables,RESEARCH
    if not (RESEARCH/'testset/manifest.json').exists():
        pytest.skip('optional offline research fixture bundle is not installed')
    rows=tables(tmp_path)
    assert len(rows)==4 and all(r['passed'] for r in rows)
    assert [r['orientation'] for r in rows]==['rot_0','rot_270','rot_180','rot_90']


def test_both_real_pdf_backends_metadata_and_no_double_rotation(tmp_path):
    from scripts.glyphs.evaluate_orientation_round4 import metadata,RESEARCH
    if not (RESEARCH/'testset/manifest.json').exists():
        pytest.skip('optional offline research fixture bundle is not installed')
    rows=metadata(tmp_path)
    assert len(rows)==8 and all(r['passed'] and r['native_lines']==0 for r in rows)


def test_oriented_plugin_emits_ordered_words_with_independent_confidence(monkeypatch):
    from docling.datamodel.accelerator_options import AcceleratorOptions
    from docling_core.types.doc.page import TextDirection
    from greekocr.glyphs.oriented_page import OrientedWord,OrientedPage
    from greekocr.deploy.docling_plugin.model import GlossapiOcrModel
    from greekocr.deploy.docling_plugin.options import GlossapiOcrOptions
    import greekocr.glyphs.oriented_page as module
    im=Image.new('L',(300,400),255);size=Size(width=100,height=100)
    parsed=_empty_segmented_page(NS(size=size))
    backend=NS(get_segmented_page=lambda:parsed)
    page=NS(page_no=1,size=size,parsed_page=parsed,_backend=backend,get_image=lambda **kw:im,predictions=NS(layout=None))
    o=Orientation(axis='vertical',orientation_cw=270,axis_confidence=.9,polarity_confidence=.8,alternatives=[90,270])
    w=OrientedWord(0,'g',3,(20,30,80,50),QuarterTurn(*im.size,270),o,
                   dict(baseline=[[20,45],[80,45]]),Image.new('L',(100,40),255))
    monkeypatch.setattr(module,'oriented_page',lambda *a,**kw:OrientedPage([w],o,[],[],None,[]))
    opts=GlossapiOcrOptions(checkpoint=Path('unused'),codec=Path('unused'),recognition_mode='oriented',replace_policy='all')
    model=GlossapiOcrModel(enabled=True,artifacts_path=None,options=opts,accelerator_options=AcceleratorOptions(device='cpu'))
    monkeypatch.setattr(model,'_get_recognizer',lambda:NS(recognize=lambda strips:[('λόγος',.42)]))
    list(model(NS(input=NS(file=Path('scan.png'))),[page]))
    c=parsed.textline_cells[0];record=model.call_log[0]['words'][0]
    assert c.rect.angle_360==90 and c.text_direction==TextDirection.LEFT_TO_RIGHT
    assert c.confidence==record['recognition_confidence']==.42
    assert record['polarity_confidence']==.8 and record['axis_confidence']==.9
    assert np.allclose(c.rect.to_polygon(),w.frame.rectangle(w.box)/np.array([3,4]))
    points=np.c_[record['guides_local']['baseline'],np.ones(2)]
    assert np.allclose((points@np.array(record['local_to_page']).T)[:,:2],record['guides_page']['baseline'])
    assert np.allclose(np.array(record['guides_pixels']['baseline'])/np.array([3,4]),record['guides_page']['baseline'])
    assert not parsed.word_cells and not parsed.char_cells
    assert backend._greekocr_word_orientations=={0:270}
