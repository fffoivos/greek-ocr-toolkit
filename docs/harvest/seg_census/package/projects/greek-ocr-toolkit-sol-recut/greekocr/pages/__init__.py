"""Page analysis: ``process_page`` and ``process_book`` share ``PageOptions``.

See docs/PAGES_GUIDE.md. Low-level Q1/Q2 functions remain available in the
stage modules and through their original greekocr.glyphs import paths.
"""
from .api import process_book, process_page
from .options import OutputOptions, PageOptions
from .records import BookResult, PageResult

__all__ = ['process_page', 'process_book', 'PageOptions', 'OutputOptions', 'PageResult', 'BookResult']
