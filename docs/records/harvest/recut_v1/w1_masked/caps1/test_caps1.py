"""Offline CAPS1 contract tests; synthetic answers are never reader results."""
from __future__ import annotations

import base64
from collections import Counter
import io
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile
import unittest

from PIL import Image

import build as b
import prepare_launchers as launchers
import reference_adapter as adapter


class Caps1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = json.loads((b.HERE / 'keys/caps1.json').read_text())
        cls.receipt = json.loads((b.HERE / 'build_receipt.json').read_text())
        cls.pool = b.rows(b.HERE / 'keys/pool.jsonl')
        cls.draw = b.rows(b.HERE / 'keys/draw.jsonl')
        cls.controls = json.loads((b.HERE / 'keys/control_truth.json').read_text())
        cls.cards = {c: b.rows(b.BED / c / 'cards.jsonl') for c in ('c1', 'c2')}
        (b.HERE / 'test_tmp').mkdir(exist_ok=True)

    def test_pool_from_features_and_all_release_exclusion_classes(self):
        cfg = json.loads((b.EXCLUSIONS / 'release_exclusions.json').read_text())
        excluded = set()
        for meta in cfg['classes'].values():
            excluded.update(s.strip() for s in (b.EXCLUSIONS / meta['file']).read_text().splitlines()
                            if s.strip() and not s.startswith('#'))
        expected = []
        for row in b.rows_stream(b.W1 / 'features.jsonl'):
            if row.get('primary_class') == 'headings_caps' and row.get('candidate_usable') is True and row['id'] not in excluded:
                expected.append(b.pool_record(row))
        self.assertEqual(self.pool, sorted(expected, key=lambda r: r['id']))
        self.assertEqual(len(self.pool), 2211)
        self.assertEqual(Counter(r['source'] for r in self.pool), self.receipt['pool_per_source'])
        self.assertEqual(sum(r['crop_tight_page'] for r in self.pool), 2070)
        self.assertEqual(sum(r['usable_final'] for r in self.pool), 141)

    def test_pool_filter_retains_held_rows_and_requires_true_boolean(self):
        rows = [dict(id=str(i), primary_class=c, candidate_usable=u, usable_final=False,
                     crop_tight_page=True, source='arbitrary') for i, c, u in (
            (0, 'headings_caps', True), (1, 'headings_caps', True),
            (2, 'poly1850', True), (3, 'headings_caps', False), (4, 'headings_caps', 'true'))]
        self.assertEqual([r['id'] for r in b.filter_pool(rows, {'1'})], ['0'])

    def test_seeded_uniform_draw_over_id_order(self):
        expected = random.Random('caps1:headings_caps').sample([r['id'] for r in self.pool], 100)
        self.assertEqual([r['id'] for r in self.draw], expected)
        self.assertEqual(len(set(expected)), 100)
        self.assertEqual([r['id'] for r in b.draw(list(reversed(self.pool)))], expected)
        self.assertEqual(Counter(r['source'] for r in self.draw), self.receipt['draw_per_source'])

    def test_context_seed_order_and_disjoint_coverage(self):
        all_ids = []
        for index, context in enumerate(('c1', 'c2')):
            line_ids = [r['id'] for r in self.draw[index * 50:(index + 1) * 50]]
            line_ids += [r['line_id'] for r in self.controls[index * 5:(index + 1) * 5]]
            random.Random(b.order_seed(context)).shuffle(line_ids)
            expected = ['k' + b.hashlib.sha256((b.SEED + ':' + context + ':' + i).encode()).hexdigest()[:10] for i in line_ids]
            self.assertEqual([r['card_id'] for r in self.cards[context]], expected)
            self.assertEqual(self.key['readers'][context], expected)
            self.assertTrue(all(re.fullmatch(r'k[0-9a-f]{10}', i) for i in expected))
            all_ids += expected
        self.assertEqual(len(set(all_ids)), 110)

    def test_original_crop_hashes_and_copy_properties(self):
        for record in json.loads((b.HERE / 'keys/crop_custody.json').read_text()):
            source, dest = Path(record['source']), Path(record['destination'])
            self.assertEqual(b.sha(source), record['expected_sha256'])
            self.assertEqual(b.sha(dest), record['expected_sha256'])
            self.assertEqual(dest.name, record['expected_sha256'] + '.png')
            self.assertFalse(source.samefile(dest))
            self.assertFalse(dest.is_symlink())
            self.assertEqual(dest.stat().st_nlink, 1)
            with Image.open(dest) as im:
                im.load()
                self.assertEqual((im.format, im.mode, im.info), ('PNG', 'L', {}))

    def test_controls_match_c1_references_and_seed(self):
        ref = {v['card_id']: v for p in sorted(b.VERDICTS.glob('bsb_poly1850__poly1850__*.jsonl')) for v in b.rows(p)}
        public = {c['card_id']: c for c in b.rows(b.C1 / 'cards.jsonl')}
        good = [cid for cid in sorted(public) if ref[cid]['letters'] == ref[cid]['crop_ok'] == 'y']
        bad = [cid for cid in sorted(public) if (ref[cid]['letters'] == 'n' or ref[cid]['crop_ok'] == 'n') and ref[cid]['detail'].strip()]
        rng = random.Random(b.SEED + ':controls')
        positives = rng.sample(good, 7)
        continuation = random.Random(); continuation.setstate(rng.getstate())
        while True:
            candidate = continuation.choice(good)
            if candidate not in positives and ref[candidate]['detail'] == '':
                break
        selected = positives + rng.sample(bad, 3)
        rng.shuffle(selected)
        selected[selected.index('c058')] = candidate
        self.assertEqual(candidate, 'c066')
        self.assertEqual(b.sha(b.SWAP_SHEET), self.receipt['control_swap_sheet']['sha256'])
        baseline = json.loads((b.HERE / 'control_swap.json').read_text())
        self.assertEqual({str(p.relative_to(b.BED / 'c1')): b.sha(p) for p in (b.BED / 'c1').rglob('*') if p.is_file()}, baseline['c1_original_files'])
        self.assertEqual([c['source_card']['card_id'] for c in self.controls], selected)
        for context in ('c1', 'c2'):
            items = [self.key['items'][r['card_id']] for r in self.cards[context]]
            self.assertEqual(sum(m['control'] for m in items), 5)
            self.assertEqual(sum(not m['control'] for m in items), 50)
        self.assertEqual(sum(c['reference_verdict']['letters'] == c['reference_verdict']['crop_ok'] == 'y' for c in self.controls), 7)
        for c in self.controls:
            self.assertEqual(c['reference_verdict'], ref[c['source_card']['card_id']])
            self.assertNotEqual(c['primary_class'], 'headings_caps')
        self.assertNotIn(b.PACK_ROOT.resolve(), b.SHEET.resolve().parents)
        self.assertEqual(b.sha(b.SHEET), self.receipt['control_sheet']['sha256'])

    def test_pack_closure(self):
        for context in ('c1', 'c2'):
            result = adapter.closure(b.BED / context, compatible=True)
            self.assertTrue(result['ok'], result['violations'])
            self.assertEqual(result['items'], 55)
            self.assertEqual({p.name for p in (b.BED / context).iterdir()}, {'cards.jsonl', 'crops'})

    def test_prompt_byte_identical(self):
        self.assertEqual((b.HERE / 'prompts/caps1.md').read_bytes(), (b.REFERENCE / 'prompts/bsb.md').read_bytes())
        self.assertEqual(b.sha(b.HERE / 'prompts/caps1.md'), self.receipt['prompt_sha256'])
        self.assertNotIn(b'{{READER2_CLAUSE}}', (b.HERE / 'prompts/caps1.md').read_bytes())

    def test_launchers_only_have_declared_path_substitutions(self):
        for name in launchers.NAMES:
            private, public = b.HERE / 'launchers' / name, b.PACK_ROOT / 'launchers' / name
            self.assertEqual(private.read_text(), launchers.configured(name))
            self.assertEqual(private.read_bytes(), public.read_bytes())
            subprocess.run(['bash', '-n', str(public)], check=True, capture_output=True)
        read = (b.HERE / 'launchers/run_read.sh').read_text()
        for setting in ('MODEL=gpt-6.1-sol', 'model_reasoning_effort=$EFFORT', 'approval_policy=never',
                        'project_doc_max_bytes=0', 'features.multi_agent=false', 'features.remote_plugin=false',
                        'features.apps=false', 'sandbox_workspace_write.network_access=false', 'web_search="disabled"',
                        '--sandbox workspace-write', '-C "$RD"'):
            self.assertIn(setting, read)

    def test_input_bindings_unchanged(self):
        bindings = dict(self.receipt['inputs'])
        bindings.update(json.loads((b.HERE / 'runtime_bindings.json').read_text())['reference_sources'])
        for path, digest in bindings.items():
            self.assertEqual(b.sha(path), digest, path)

    def fake_answers(self):
        records = []
        for card in self.cards['c1']:
            meta = self.key['items'][card['card_id']]
            records.append(dict(card_id=card['card_id'], letters=meta.get('expected', {}).get('letters', 'u'),
                                crop_ok=meta.get('expected', {}).get('crop_ok', 'u'), marks='n', errors=[], detail='synthetic test only'))
        return records

    def test_mapper_removes_controls_and_ignores_marks(self):
        mapper = adapter.load_reference('map_answers')
        mapped, controls = mapper.map_records('bsb', 'c1', self.fake_answers(), self.key, self.cards['c1'])
        self.assertEqual(len(mapped), 50)
        self.assertEqual(len(controls['controls']), 5)
        self.assertEqual(controls['control_errors'], 0)
        self.assertFalse(controls['flagged'])
        self.assertEqual({r['card_id'] for r in mapped}, {m['line_id'] for m in self.key['items'].values() if not m['control'] and m['line_id'] in {self.key['items'][c['card_id']]['line_id'] for c in self.cards['c1']}})

    def test_mapper_rejects_bad_order_and_flags_two_control_errors(self):
        mapper = adapter.load_reference('map_answers')
        answers = self.fake_answers()
        with self.assertRaises(ValueError):
            mapper.map_records('bsb', 'c1', list(reversed(answers)), self.key, self.cards['c1'])
        wrong = 0
        for row in answers:
            if self.key['items'][row['card_id']]['control'] and wrong < 2:
                row['letters'] = 'n' if row['letters'] == 'y' else 'y'
                wrong += 1
        _, result = mapper.map_records('bsb', 'c1', answers, self.key, self.cards['c1'])
        self.assertEqual(result['control_errors'], 2)
        self.assertTrue(result['flagged'])

    def fixture(self, temporary):
        directory = Path(temporary) / 'c1'
        (directory / 'crops').mkdir(parents=True)
        card = self.cards['c1'][0]
        shutil.copyfile(b.BED / 'c1' / card['crop'], directory / card['crop'])
        b.jsonl(directory / 'cards.jsonl', [card])
        b.dump(directory.parent / 'MANIFEST.c1.json', dict(files={name: b.sha(directory / name) for name in ('cards.jsonl', card['crop'])}))
        scanner = adapter.load_reference('scan_rollout', adapter.ROLLOUT_SUBSTITUTIONS)
        scanner.CAPS_REPLAY = b.HERE / 'tools/replay_literal.py'
        scanner.REPLAY_TMP = Path(temporary) / 'replay'
        scanner.REPLAY_TMP.mkdir()
        return directory, scanner, card

    def test_v4_scans_sibling_paths_and_rejects_foreign_pixels(self):
        with tempfile.TemporaryDirectory(dir=b.HERE / 'test_tmp') as temporary:
            directory, scanner, card = self.fixture(temporary)
            clean = Path(temporary) / 'clean.jsonl'
            image = base64.b64encode((directory / card['crop']).read_bytes()).decode()
            b.jsonl(clean, [dict(payload=dict(type='function_call_output', output=[dict(type='input_image', image_url='data:image/png;base64,' + image)]))])
            self.assertTrue(scanner.inspect(clean, directory)['ok'])
            # The inherited integrity contract permits only reader outputs.
            (directory / 'answers.jsonl').write_text('')
            (directory / 'zoom').mkdir()
            (directory / 'zoom' / 'note.txt').write_text('permitted zoom output')
            self.assertEqual(scanner.integrity(directory, False), ([], False))
            extra = directory / 'extra.txt'; extra.write_text('unexpected')
            self.assertTrue(scanner.integrity(directory, False)[0])
            extra.unlink()
            original = (directory / card['crop']).read_bytes()
            (directory / card['crop']).write_bytes(original + b'tampered')
            self.assertTrue(scanner.integrity(directory, False)[0])
            (directory / card['crop']).write_bytes(original)
            self.assertEqual(scanner.integrity(directory, False), ([], False))
            foreign = io.BytesIO(); Image.new('RGB', (19, 19), 'magenta').save(foreign, format='PNG')
            dirty = Path(temporary) / 'dirty.jsonl'
            b.jsonl(dirty, [dict(payload=dict(type='function_call', name='exec_command', arguments=json.dumps(dict(cmd='cat ../c2/cards.jsonl')))),
                          dict(payload=dict(type='function_call_output', output=[dict(type='input_image', image_url='data:image/png;base64,' + base64.b64encode(foreign.getvalue()).decode())]))])
            result = scanner.inspect(dirty, directory)
            self.assertFalse(result['ok'])
            reasons = [v['reason'] for v in result['violations']]
            self.assertIn('other reader folder', reasons)
            self.assertTrue(any('image provenance' in r for r in reasons))
            self.assertTrue(any('forbidden literal' in r for r in reasons))

    def test_v4_replays_overwritten_zoom_from_cards_and_crops(self):
        with tempfile.TemporaryDirectory(dir=b.HERE / 'test_tmp') as temporary:
            directory, scanner, card = self.fixture(temporary)
            (directory / 'zoom').mkdir()
            command = 'magick ' + card['crop'] + ' -resize 200% zoom/test.png'
            subprocess.run(command.split(), cwd=directory, check=True, capture_output=True)
            observed = (directory / 'zoom/test.png').read_bytes()
            subprocess.run(['magick', card['crop'], '-resize', '300%', 'zoom/test.png'], cwd=directory, check=True, capture_output=True)
            literal = "mkdir -p zoom\npython3 - <<'PY'\nimport subprocess\nsubprocess.run(" + repr(command.split()) + ", check=True)\nPY"
            match, receipt = scanner.reproduce(observed, directory, 'zoom/test.png', [(1, literal)])
            self.assertIsNotNone(match, receipt)
            self.assertTrue(receipt['pixels_exact'])
            self.assertEqual(receipt['original_files'], 2)


if __name__ == '__main__':
    import time
    import xml.etree.ElementTree as ET
    b.io_guard()
    start = time.monotonic()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Caps1Tests)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    text = stream.getvalue()
    (b.HERE / 'tests.log').write_text(text)
    root = ET.Element('testsuite', tests=str(result.testsRun), failures=str(len(result.failures)),
                      errors=str(len(result.errors)), skipped=str(len(result.skipped)), time=str(round(time.monotonic() - start, 3)))
    ET.ElementTree(root).write(b.HERE / 'tests.xml', encoding='unicode')
    print(text, end='')
    raise SystemExit(0 if result.wasSuccessful() else 1)
