"""Completed-reader closure regression; all mutations stay in a temporary pack."""
import json, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import common_full as common


class CompletedReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='test-g5-', dir=common.scan_rollout.REPLAY_TMP)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.bed = self.root/'packs'
        self.folder = self.bed/'p2'
        self.answers = self.root/'answers'
        self.answers.mkdir()
        self.key = common.load(common.ROOT/'keys/p2_key.json')
        shutil.copytree(common.BED/'p2', self.folder)
        shutil.copyfile(common.BED/'MANIFEST.p2.json', self.bed/'MANIFEST.p2.json')
        shutil.copyfile(common.SR/'answers/grave_full/p2.jsonl', self.answers/'p2.jsonl')
        shutil.copyfile(self.answers/'p2.jsonl', self.folder/'answers.jsonl')
        zoom = self.folder/'zoom/nested'
        zoom.mkdir(parents=True, exist_ok=True)
        self.image = self.folder/next(r for r in common.load(self.bed/'MANIFEST.p2.json')['files'] if r.startswith('img/'))
        shutil.copyfile(self.image, zoom/'review.png')
        self.patch = patch.object(common, 'BED', self.bed)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def read(self):
        return common.read_contexts(self.key, 'p2', self.answers)

    def test_completed_reader(self):
        before = {str(p.relative_to(self.folder)): common.sha(p)
                  for p in self.folder.rglob('*') if p.is_file()}
        self.assertEqual(list(self.read()), list(self.key))
        after = {str(p.relative_to(self.folder)): common.sha(p)
                 for p in self.folder.rglob('*') if p.is_file()}
        self.assertEqual(before, after)

    def test_changed_original_rejected(self):
        self.image.write_bytes(self.image.read_bytes()+b'changed')
        with self.assertRaisesRegex(ValueError, 'original changed or missing'):
            self.read()

    def test_missing_original_rejected(self):
        self.image.unlink()
        with self.assertRaisesRegex(ValueError, 'original changed or missing'):
            self.read()

    def test_unallowed_file_rejected(self):
        (self.folder/'extra.txt').write_text('extra')
        with self.assertRaisesRegex(ValueError, 'unallowed added file'):
            self.read()

    def test_unallowed_directory_rejected(self):
        (self.folder/'extra').mkdir()
        with self.assertRaisesRegex(ValueError, 'unallowed added directory'):
            self.read()

    def test_zoom_symlink_rejected(self):
        (self.folder/'zoom/link.png').symlink_to(self.image)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.read()


if __name__ == '__main__':
    unittest.main(verbosity=2)
