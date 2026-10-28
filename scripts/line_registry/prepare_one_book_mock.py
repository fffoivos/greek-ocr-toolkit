"""Prepare ONLY the offline mock bundle; payload fixtures are not training data."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import zlib

import pyarrow as pa
import pyarrow.parquet as pq

from mock_clariden_builder import REPO, TABLES, canonical, credential_free, info, sha, write_json


def prepare(book_root, output):
    credential_free()
    output.mkdir(parents=True, exist_ok=True)
    for n in TABLES:
        shutil.copyfile(book_root/(n+'.parquet'), output/(n+'.parquet'))
    shutil.copyfile(book_root/'Scripts-14.0.0.txt', output/'Scripts-14.0.0.txt')
    registry = REPO/'docs/programme_20261019/registry/book_registry'
    for n in ('book_registry.parquet', 'row_instruments.parquet'):
        shutil.copyfile(registry/n, output/n)
    # Valid 1x1 PNG, fixture only. No real crop/synthetic/reference bytes are
    # available for this book on the Mac. Never label these as recovered bytes.
    def chunk(kind, data):
        return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data))
    png = b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',1,1,8,0,0,0,0))+chunk(b'IDAT',zlib.compress(b'\x00\x00'))+chunk(b'IEND',b'')
    row = pq.read_table(output/'rows.parquet').to_pylist()[0]
    for lane in ('crops', 'training', 'synthetic', 'references'):
        records = []
        for variant in (['seal04_raw','seal04_corrected','v2_test_raw','v2_test_corrected'] if lane=='references' else [lane]):
            records.append(dict(payload_id='MOCK:'+variant, mock_fixture=True,
                origin='mock_fixture_not_training_data', row_key=row['row_key'] if lane!='synthetic' else None,
                image_png=png, image_sha256=hashlib.sha256(png).hexdigest(),
                label_raw=row['label_raw'], label_corrected=row['label_corrected'],
                label_variant=variant, licence='unknown_fixture', factory_build_id='MOCK',
                font=None, generator_config_sha256=None, seed=None, text_source=None,
                provenance_completeness='mock_fixture; historical fields deliberately unknown',
                historical_unknown_fields=['font','generator_config_sha256','seed','text_source']))
        pq.write_table(pa.Table.from_pylist(records), output/(lane+'.parquet'), compression='zstd')
    inputs = [info(p,output) for p in sorted(output.iterdir()) if p.is_file() and p.suffix in ('.parquet','.txt')]
    config = dict(schema='runner4-clariden-mock-input-v1', mode='mock_one_book_not_publishable',
        source_one_book_manifest=dict(path=str(book_root/'manifest.json'), sha256=sha(book_root/'manifest.json')),
        source_scope='40 real harvested page observations and 1429 real census rows; all payload lanes are explicit fixtures',
        page_batch_size=5, shard_cap_bytes=1_000_000_000, inputs=inputs)
    write_json(output/'INPUTS.json',config)
    return dict(root=str(output),inputs=len(inputs),bytes=sum(r['bytes'] for r in inputs),config_sha256=sha(output/'INPUTS.json'))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--book-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();print(canonical(prepare(a.book_root,a.output)))
