"""Attest and time the actual epoch loader feeding best.pt; no metric changes."""
from contextlib import contextmanager
from pathlib import Path
import time
from common import atomic, digest


@contextmanager
def instrument(trainer, selection, output):
    import eval_cer
    original = eval_cer.evaluate

    def measured(model, loader, *args, **kwargs):
        rows = loader.dataset.rows
        identity = digest([(r['line_id'], r['label_ids']) for r in rows])
        if len(rows) != selection['rows'] or identity != selection['identity_sha256']:
            raise ValueError('best.pt selection loader differs from attested seal04 dev')
        tick = time.monotonic()
        result = original(model, loader, *args, **kwargs)
        seconds = time.monotonic() - tick
        atomic(Path(output)/('SELECTION_EVAL_%d.json' % time.time_ns()),
            dict(selection=selection, seconds=seconds, result=result,
                 purpose='epoch CER used by best.pt/best metric/bad_epochs; no test panels'))
        return result

    eval_cer.evaluate = measured
    try:
        yield
    finally:
        eval_cer.evaluate = original
