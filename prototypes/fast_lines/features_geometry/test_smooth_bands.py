"""New export's original-pixel contract, reusing the write-once native fixtures."""
import numpy as np
from ..shared import geometry_bands as bands,geometry_rows as rows
from .test_whole_children import actual


def test_smooth_B_refuses_partial_omitted_apostrophe_without_new_attachment():
    gray,item,record,pieces,ctx=actual()
    polygons,receipt=rows.whole_children(gray,item,record,pieces,ctx,smooth_exports=True)
    assert not polygons
    assert receipt['first_failure']=='actual page raster changes rectified whole membership'
    delta=receipt['native_page_delta']
    assert not delta['lost']
    # This source-bound whole mark is not in the accepted member population.
    # Padding must not turn 46/59 pixels into a newly accepted B child.
    mark=next(q for q in delta['added'] if q['component']==32)
    assert mark['pixels']==46 and mark['total']==59


def test_declared_crop_edges_change_no_legacy_native_mask():
    gray,item,record,pieces,ctx=actual()
    polygons,receipt=rows.whole_children(gray,item,record,pieces,ctx)
    assert polygons and receipt['page_membership']['members']
    for p in polygons:
        assert np.array_equal(bands.crop_mask(gray.shape,dict(polygon=p)),rows._filled(gray.shape,p))
