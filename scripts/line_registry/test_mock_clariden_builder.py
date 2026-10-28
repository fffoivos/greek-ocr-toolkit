"""Contract tests for the planned execution boundary, using the real book metadata."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mock_clariden_builder import credential_free, database_transport, run, sha, shards, validate
from prepare_one_book_mock import prepare


class BuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.book = Path(os.environ.get('RUNNER4_ONE_BOOK_ROOT','/private/tmp/runner4-book-registry-dryrun-20261023'))
        if not (cls.book/'manifest.json').is_file():
            raise unittest.SkipTest('prepare the real one-book offline probe first')
        cls.temp = tempfile.TemporaryDirectory(prefix='runner4-builder-tests-')
        cls.root = Path(cls.temp.name)
        cls.inputs = cls.root/'inputs'
        prepare(cls.book, cls.inputs)
        cls.config = cls.inputs/'INPUTS.json'

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_credentials_rejected_before_any_work(self):
        with patch.dict(os.environ, {'HF_TOKEN':'test-fixture'}):
            with self.assertRaisesRegex(ValueError,'authentication variables absent'):
                credential_free()

    def test_interrupt_resume_equals_clean_and_output_tamper_rejected(self):
        resumed = self.root/'resumed'; clean = self.root/'clean'
        stopped = run(self.config, resumed, stop_after=2)
        self.assertTrue(stopped['interrupted'])
        self.assertFalse((resumed/'MOCK_COMPLETE.json').exists())
        result = run(self.config, resumed)
        self.assertEqual(result['batches_reused'],2)
        baseline = run(self.config, clean)
        self.assertEqual(result['manifest_sha256'],baseline['manifest_sha256'])
        self.assertEqual(result['checks']['row_box_page_book_joins'],1429)
        self.assertEqual(result['checks']['used_joins'],1066)
        self.assertEqual(result['feature_replay']['variants'],2000)
        self.assertFalse(result['publishable'])
        self.assertEqual(result['payload_fixture_rows'],dict(crops=1,training=1,synthetic=1,references=4))
        p = next((resumed/'batches').rglob('rows-*.parquet'))
        with p.open('r+b') as f:
            f.seek(20); f.write(b'changed')
        with self.assertRaisesRegex(ValueError,'artifact hash mismatch'):
            run(self.config,resumed)

    def test_source_tamper_rejected(self):
        p = self.inputs/'Scripts-14.0.0.txt'; original = p.read_bytes()
        try:
            p.write_bytes(original+b'\n')
            with self.assertRaisesRegex(ValueError,'artifact hash mismatch'):
                run(self.config,self.root/'bad-source')
        finally:
            p.write_bytes(original)

    def test_broken_real_join_rejected(self):
        tables = {n:pq.read_table(self.inputs/(n+'.parquet')) for n in ('pages','boxes','rows','row_features')}
        records = tables['rows'].to_pylist();records[0]['box_id']='missing'
        tables['rows']=pa.Table.from_pylist(records,schema=tables['rows'].schema)
        with self.assertRaisesRegex(ValueError,'join failed'):
            validate(tables)

    def test_closed_shard_cap_preserves_binary_payloads(self):
        dest = self.root/'cap';dest.mkdir()
        payloads = [hashlib.shake_256(str(i).encode()).digest(1500) for i in range(30)]
        table = pa.table({'id':list(range(30)),'image_png':payloads})
        files = shards(table,dest,'part',12000)
        self.assertGreater(len(files),1)
        self.assertTrue(all(p.stat().st_size<=12000 for p in files))
        self.assertEqual(pa.concat_tables([pq.read_table(p) for p in files]).to_pylist(),table.to_pylist())

    def test_sqlite_transport_reassembles_with_full_hash_and_integrity(self):
        dest=self.root/'db';dest.mkdir();p=dest/'registry.sqlite'
        db=sqlite3.connect(p);db.execute('CREATE TABLE t (a TEXT)')
        db.executemany('INSERT INTO t VALUES (?)',[('row'+str(i),) for i in range(1000)])
        db.commit();db.close()
        parts,record=database_transport(p,dest,4096)
        self.assertGreater(len(parts),1)
        rebuilt=dest/'reassembled.sqlite';rebuilt.write_bytes(b''.join(x.read_bytes() for x in parts))
        self.assertEqual(sha(rebuilt),record['sha256'])
        db=sqlite3.connect(rebuilt)
        self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertEqual(db.execute('SELECT count(*) FROM t').fetchone()[0],1000)
        db.close()


if __name__=='__main__':
    unittest.main()
