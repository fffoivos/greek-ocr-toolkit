"""One raster-to-lines API over the three existing segmenter generations.

Imports are lazy; discovery never loads weights or downloads assets.
"""
from .api import available, get
from .types import Segmenter, SegmenterInfo, SegmentationResult, Line

__all__ = ['available', 'get', 'Segmenter', 'SegmenterInfo', 'SegmentationResult', 'Line', 'drop_binding_and_ornaments']


def drop_binding_and_ornaments(*args, **kwargs):
    """Lazy entry point; see greekocr.segmenters.filters."""
    from .filters import drop_binding_and_ornaments as apply
    return apply(*args, **kwargs)
