"""Record positions for bounded commits. JSONL resumes with seek, not reparsing."""
import gzip
import json
from pathlib import Path

import pyarrow.parquet as pq

from .common import records


def positioned_records(path, source, ordinal=0, byte_offset=0):
    p = Path(path)
    if p.name.endswith(('.jsonl', '.jsonl.gz', '.ndjson')):
        opener = gzip.open if p.suffix == '.gz' else open
        with opener(p, 'rb') as stream:
            stream.seek(byte_offset)
            for raw in stream:
                if raw.strip():
                    yield ordinal, json.loads(raw), stream.tell()
                    ordinal += 1
    elif p.suffix == '.parquet':
        pf = pq.ParquetFile(p)
        skip, base = ordinal, 0
        for rg in range(pf.num_row_groups):
            count = pf.metadata.row_group(rg).num_rows
            if skip >= count:
                skip -= count
                base += count
                continue
            for batch in pf.iter_batches(row_groups=[rg], batch_size=256,
                                          columns=source.get('columns'), use_threads=False):
                size = batch.num_rows
                if skip >= size:
                    skip -= size
                    base += size
                    continue
                for i, row in enumerate(batch.to_pylist()):
                    if i >= skip:
                        yield base + i, row, 0
                skip = 0
                base += size
    else:
        for n, row in enumerate(records(p, source)):
            if n >= ordinal:
                yield n, row, 0
