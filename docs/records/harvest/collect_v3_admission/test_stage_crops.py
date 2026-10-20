"""Offline integration checks against the staged cohort; uses only its bound inputs."""
import hashlib
import io
import json
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

from stage_crops import INTERPRETER, sha

BASE = Path(__file__).resolve().parent


def inventory():
    paths = list((BASE / 'crops').rglob('*')) + [BASE / name for name in
             ('crops_manifest.jsonl', 'crops_failures.jsonl', 'crops_receipt.json')]
    result = {}
    for path in paths:
        stat = path.stat()
        result[str(path)] = (stat.st_ino, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns,
                             sha(path) if path.is_file() else None)
    return result


class StagedCrops(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.receipt = json.loads((BASE / 'crops_receipt.json').read_text())
        cls.manifest = [json.loads(line) for line in (BASE / 'crops_manifest.jsonl').read_text().splitlines()]
        cls.retained = cls.manifest
        cls.manifest = [r for r in cls.retained if r['admitted']]
        cls.admitted = {r['row_id']: r for r in
                        map(json.loads, Path(cls.receipt['admitted_file']).read_text().splitlines())}

    def test_01_paths_and_all_hashes(self):
        self.assertEqual(self.receipt['failures'], 0)
        self.assertEqual((BASE / 'crops_failures.jsonl').read_bytes(), b'')
        self.assertEqual(len(self.manifest), len(self.admitted))
        self.assertEqual({r['row_id'] for r in self.manifest}, set(self.admitted))
        self.assertEqual(len(list((BASE / 'crops').rglob('*.png'))), len(self.retained))
        total = 0
        for row in self.manifest:
            admitted = self.admitted[row['row_id']]
            self.assertEqual(row['path'], f"crops/{admitted['source']}/{row['row_id']}.png")
            self.assertEqual(row['class'], admitted['primary_class'])
            path = BASE / row['path']
            self.assertEqual(sha(path), admitted['crop_sha256'])
            self.assertEqual(row['sha256'], admitted['crop_sha256'])
            self.assertEqual(path.stat().st_size, row['bytes'])
            total += row['bytes']
        self.assertEqual(sum(r['bytes'] for r in self.retained), self.receipt['total_bytes'])
        self.assertEqual(self.receipt['withdrawn_count'], sum(not r['admitted'] for r in self.retained))
        for row in self.retained:
            self.assertEqual(sha(BASE / row['path']), row['sha256'])
            self.assertEqual(row['admitted'], row['row_id'] in self.admitted)

    def test_02_sample_50_byte_identity(self):
        from PIL import Image
        sample = random.Random(20261018).sample(self.manifest, 50)
        ids = {r['row_id'] for r in sample}
        features = {}
        with Path(self.receipt['features_file']).open() as stream:
            for line in stream:
                row = json.loads(line)
                key = row.get('row_id', row.get('id'))
                if key in ids:
                    features[key] = row
        self.assertEqual(set(features), ids)
        for row in sample:
            feature = features[row['row_id']]
            self.assertEqual(sha(feature['crop_source_image']), feature['crop_source_sha256'])
            with Image.open(feature['crop_source_image']) as image:
                crop = image.convert('L').crop(feature['crop_bbox'])
                buffer = io.BytesIO()
                crop.save(buffer, format='PNG', compress_level=3)
            self.assertEqual(hashlib.sha256(buffer.getvalue()).hexdigest(), feature['crop_sha256'])
            self.assertEqual(buffer.getvalue(), (BASE / row['path']).read_bytes())

    def test_03_full_second_run_changes_nothing(self):
        before = inventory()
        subprocess.run([str(INTERPRETER), str(BASE / 'stage_crops.py'),
                        '--admitted', self.receipt['admitted_file'],
                        '--features', self.receipt['features_file'],
                        '--out', str(BASE / 'crops')], check=True)
        self.assertEqual(inventory(), before)

    def test_04_missing_and_mismatched_sources_record_failures(self):
        row = self.manifest[0]
        with Path(self.receipt['features_file']).open() as stream:
            feature = next(json.loads(line) for line in stream
                           if json.loads(line).get('id') == row['row_id'])
        for source, digest in [('/nonexistent/CROPS1-source.png', feature['crop_source_sha256']),
                               (feature['crop_source_image'], '0' * 64)]:
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                admitted = root / 'admitted.jsonl'
                features = root / 'input/features.jsonl'
                features.parent.mkdir()
                admitted.write_text(json.dumps(self.admitted[row['row_id']]) + '\n')
                features.write_text(json.dumps(dict(feature, crop_source_image=source,
                                                   crop_source_sha256=digest)) + '\n')
                result = subprocess.run([str(INTERPRETER), str(BASE / 'stage_crops.py'),
                                         '--admitted', str(admitted), '--features', str(features),
                                         '--out', str(root / 'output/crops')], capture_output=True)
                self.assertEqual(result.returncode, 1, result.stderr)
                failure = json.loads((root / 'output/crops_failures.jsonl').read_text())
                self.assertEqual(failure['row_id'], row['row_id'])
                self.assertIn('source', failure['reason'].lower())
                self.assertEqual(list((root / 'output/crops').rglob('*.png')), [])


if __name__ == '__main__':
    unittest.main(verbosity=2)
