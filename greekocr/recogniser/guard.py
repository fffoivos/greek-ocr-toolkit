"""Process-local replay guard; pinned callers keep their original guards."""
from collections.abc import Iterator

from contextlib import contextmanager
from unittest.mock import patch


__all__ = ['forbid_forward']


@contextmanager
def forbid_forward() -> Iterator[None]:
    from greekocr.labelfix.ctc_align import Recognizer
    from greekocr._vendor.bench.o4b_models import E1
    from greekocr._vendor.bench.e2_reader_parity import E1Reader
    from greekocr._vendor.pipeline.recognize import Recognizer as Vendor
    from greekocr.deploy.docling_plugin.recognizer.inference import Recognizer as Serve
    from .api import Recogniser
    from contextlib import ExitStack
    def forbidden(*args, **kwargs):
        raise RuntimeError('recogniser forward forbidden during replay')
    with ExitStack() as stack:
        for cls, methods in ((Recognizer, ('__init__', 'align_batch', 'align_paths')),
                (E1, ('read', 'logits')), (E1Reader, ('read',)),
                (Vendor, ('recognize',)), (Serve, ('recognize',)),
                (Recogniser, ('read', 'logits'))):
            for method in methods:
                stack.enter_context(patch.object(cls, method, forbidden))
        yield
