#!/usr/bin/env python3
"""SR-G1 tests. ALL answers generated here are SYNTHETIC, never reader results."""
import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import build_grave as b
from score_grave import score, annotate_key, touches_punctuation, load_answers


class SyntheticScoring(unittest.TestCase):
    def setUp(self):
        self.key = {
            'k0000000001': dict(stratum='s1', line_id='l1', **{'class': 'positive'}, truth_accent='grave'),
            'k0000000002': dict(stratum='s1', line_id='l1', **{'class': 'positive'}, truth_accent='grave'),
            'k0000000003': dict(stratum='s2', line_id='l2', **{'class': 'negative'}, truth_accent='acute'),
            'k0000000004': dict(stratum='s2', line_id='l3', **{'class': 'control'}, truth_accent='circumflex'),
            'k0000000005': dict(stratum='s1', line_id='l4', **{'class': 'control'}, truth_accent='none'),
        }
        for i, m in enumerate(self.key.values()):
            m['touches_punct'] = i % 2 == 0
        self.answers = [dict(item_id=i, accent=m['truth_accent'], confidence='high', note='') for i, m in self.key.items()]

    def test_synthetic_perfect(self):
        r = score(self.answers, self.key)
        self.assertEqual(r['overall']['accuracy'], 1)
        self.assertEqual(r['overall']['control_passes'], 2)
        self.assertEqual(r['positive_lines']['n'], 1)
        self.assertEqual(r['positive_lines']['detected'], 1)
        self.assertEqual(r['negative_false_alarms']['rate'], 0)

    def test_synthetic_all_acute_misses_graves(self):
        for a in self.answers:
            a['accent'] = 'acute'
        r = score(self.answers, self.key)
        self.assertEqual(r['positive_lines']['detected'], 0)
        self.assertEqual(r['per_class']['positive']['confusion_matrix']['grave']['acute'], 2)
        self.assertEqual(r['overall']['correct'], 1)

    def test_synthetic_all_grave_false_alarm(self):
        for a in self.answers:
            a['accent'] = 'grave'
        r = score(self.answers, self.key)
        self.assertEqual(r['negative_false_alarms']['rate'], 1)
        self.assertEqual(r['overall']['control_passes'], 0)

    def test_synthetic_unreadable_in_accuracy_denominator(self):
        for a in self.answers:
            a['accent'] = 'unreadable'
        r = score(self.answers, self.key)
        self.assertEqual(r['overall']['unreadable'], 5)
        self.assertEqual(r['overall']['accuracy'], 0)
        self.assertEqual(r['positive_lines']['detected'], 0)

    def test_synthetic_line_any_grave(self):
        self.answers[0]['accent'] = 'acute'
        r = score(self.answers, self.key)
        self.assertEqual(r['positive_lines']['detected'], 1)
        self.assertEqual(r['per_class']['positive']['accuracy'], .5)

    def test_synthetic_missing(self):
        with self.assertRaises(ValueError):
            score(self.answers[:-1], self.key)

    def test_synthetic_extra(self):
        with self.assertRaises(ValueError):
            score(self.answers+self.answers[:1], self.key)

    def test_synthetic_reordered(self):
        with self.assertRaises(ValueError):
            score(list(reversed(self.answers)), self.key)

    def test_synthetic_duplicate(self):
        self.answers[1]['item_id'] = self.answers[0]['item_id']
        with self.assertRaises(ValueError):
            score(self.answers, self.key)

    def test_synthetic_invalid_accent(self):
        for invalid in ('GRAVE', 'unknown', None, [], 1):
            with self.subTest(invalid=invalid):
                aa = copy.deepcopy(self.answers)
                aa[0]['accent'] = invalid
                with self.assertRaises(ValueError):
                    score(aa, self.key)

    def test_synthetic_extra_field(self):
        self.answers[0]['truth'] = 'grave'
        with self.assertRaises(ValueError):
            score(self.answers, self.key)


    def test_prompt_schema_required_fields(self):
        for field in ('item_id', 'accent', 'confidence', 'note'):
            aa = copy.deepcopy(self.answers)
            del aa[0][field]
            with self.subTest(field=field), self.assertRaises(ValueError):
                score(aa, self.key)

    def test_confidence_and_note_types(self):
        for field, values in (('confidence', ('HIGH', '', None, [], 1)),
                              ('note', (None, [], {}, 1, True))):
            for value in values:
                aa = copy.deepcopy(self.answers)
                aa[0][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    score(aa, self.key)
        self.answers[0].update(confidence='low', note='uncertain stroke')
        r = score(self.answers, self.key)
        self.assertEqual(r['per_class']['positive']['low_confidence'],
                         dict(count=1, total=2, rate=.5))

    def test_duplicate_json_fields_rejected(self):
        with tempfile.TemporaryDirectory(dir=b.ROOT/'keys') as folder:
            path = Path(folder)/'duplicate.jsonl'
            path.write_text('{"item_id":"x","accent":"grave","accent":"acute","confidence":"high","note":""}\n')
            with self.assertRaises(ValueError):
                load_answers(path)

    def test_punctuation_split_all_metrics_and_intersections(self):
        self.answers[0].update(accent='acute', confidence='low', note='direction')
        self.answers[2].update(accent='grave', confidence='low')
        self.answers[3]['accent'] = 'unreadable'
        r = score(self.answers, self.key)
        yes, no = (r['touches_punct'][v] for v in ('true', 'false'))
        self.assertEqual((yes['overall']['n'], no['overall']['n']), (3, 2))
        self.assertEqual(yes['per_class']['positive']['grave_recall']['count'], 0)
        self.assertEqual(no['per_class']['positive']['grave_recall']['count'], 1)
        self.assertEqual(yes['per_stratum']['s2']['negative_false_alarms']['answered_grave'], 1)
        self.assertEqual(no['per_stratum_class']['s2']['control']['unreadable'], 1)
        self.assertIsNone(yes['per_stratum_class']['s2']['positive']['grave_recall']['rate'])
        self.assertEqual(yes['overall']['low_confidence']['count'], 2)
        self.assertEqual(len(r['wrong_items']), 3)
        for group in [r, yes, no]:
            for view in [group['per_class'], group['per_stratum']]:
                self.assertEqual(sum(x['n'] for x in view.values()), group['overall']['n'])
                self.assertEqual(sum(x['correct'] for x in view.values()), group['overall']['correct'])
                self.assertEqual(sum(x['unreadable'] for x in view.values()), group['overall']['unreadable'])
            self.assertEqual(sum(x['n'] for cc in group['per_stratum_class'].values() for x in cc.values()), group['overall']['n'])
        for truth in r['overall']['confusion_matrix']:
            for answer in r['overall']['confusion_matrix'][truth]:
                self.assertEqual(r['overall']['confusion_matrix'][truth][answer],
                                 yes['overall']['confusion_matrix'][truth][answer]+no['overall']['confusion_matrix'][truth][answer])

    def test_requires_boolean_punctuation_flag(self):
        for value in (None, 0, 1, 'false'):
            kk = copy.deepcopy(self.key)
            kk[next(iter(kk))]['touches_punct'] = value
            with self.assertRaises(ValueError):
                score(self.answers, kk)


class SourcePunctuation(unittest.TestCase):
    def test_following_punctuation(self):
        for punct in ',.;·:!?»)…':
            with self.subTest(punct=punct):
                self.assertTrue(touches_punctuation('τὸ καλό'+punct+' μετά', 2, 'καλὸ'))
        self.assertTrue(touches_punctuation('«καλό...»', 1, 'καλό'))
        self.assertTrue(touches_punctuation('καλο\u0301,', 1, 'καλό'))

    def test_line_end_hyphens(self):
        for hyphen in '-‐‑':
            self.assertTrue(touches_punctuation('τὸ παρά'+hyphen+'  ', 2, 'παρά'))
            self.assertTrue(touches_punctuation('τὸ παρά '+hyphen+'  ', 2, 'παρά'))
        self.assertFalse(touches_punctuation('παρά- μετά', 1, 'παρά'))

    def test_no_touch_or_unrelated_punctuation(self):
        for text in ('καλό', 'καλό μετά,', 'καλό , μετά', '(καλό', 'καλό λόγο-'):
            self.assertFalse(touches_punctuation(text, 1, 'καλό'))
        self.assertFalse(touches_punctuation('καλό, καλό', 2, 'καλό'))
        self.assertTrue(touches_punctuation('καλό, καλό', 1, 'καλό'))

    def test_bad_word_alignment(self):
        for index, word in ((0, 'καλό'), (2, 'καλό'), (1, 'λάθος')):
            with self.assertRaises(ValueError):
                touches_punctuation('καλό', index, word)

    def test_source_binding_and_stale_flag(self):
        with tempfile.TemporaryDirectory(dir=b.ROOT/'keys') as folder:
            source = Path(folder)/'s_key.json'
            source.write_text(json.dumps({'c1': dict(line_id='l1', literal_label='καλό,')}))
            key = {'i1': dict(stratum='s', card_id='c1', line_id='l1', word_index=1, printed_word='καλὸ')}
            annotated = annotate_key(key, folder)
            self.assertTrue(annotated['i1']['touches_punct'])
            self.assertEqual(annotated['i1']['c1_line_text'], 'καλό,')
            annotated['i1']['touches_punct'] = False
            with self.assertRaises(ValueError):
                annotate_key(annotated, folder)
            key['i1']['line_id'] = 'wrong'
            with self.assertRaises(ValueError):
                annotate_key(key, folder)


class SyntheticPixelsAndClosure(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='SYNTHETIC-', dir=b.ROOT/'keys')
        self.path = Path(self.temp.name)
        (self.path/'img').mkdir()
        self.image = b.encode(Image.new('RGB', (10, 8), 'white'))
        self.rel = 'img/'+hashlib.sha256(self.image).hexdigest()+'.png'
        (self.path/self.rel).write_bytes(self.image)
        self.item = dict(item_id='k0000000001', word_image=self.rel, letter_image=self.rel,
                         word_bare='νερο', anchor_index=3, anchor_base='ο')
        self.key = {self.item['item_id']: dict(line_id='private-line', stratum='private-stratum')}
        self.write()

    def tearDown(self):
        self.temp.cleanup()

    def write(self):
        (self.path/'items.jsonl').write_text(json.dumps(self.item, ensure_ascii=False)+'\n')

    def test_synthetic_closed_pack(self):
        self.assertTrue(b.scan(self.path, self.key)['ok'])

    def test_synthetic_extra_file(self):
        (self.path/'secret.json').write_text('{}')
        with self.assertRaises(ValueError):
            b.scan(self.path, self.key)

    def test_synthetic_extra_field(self):
        self.item['truth'] = 'grave'
        self.write()
        with self.assertRaises(ValueError):
            b.scan(self.path, self.key)

    def test_synthetic_bad_hash(self):
        (self.path/self.rel).write_bytes(b.encode(Image.new('RGB', (10, 8), 'black')))
        with self.assertRaises(ValueError):
            b.scan(self.path, self.key)

    def test_synthetic_traversal(self):
        self.item['word_image'] = '../private.png'
        self.write()
        with self.assertRaises(ValueError):
            b.scan(self.path, self.key)

    def test_synthetic_unreferenced_image(self):
        (self.path/'img/extra.png').write_bytes(self.image)
        with self.assertRaises(ValueError):
            b.scan(self.path, self.key)

    def test_synthetic_png_metadata(self):
        from PIL.PngImagePlugin import PngInfo
        metadata = PngInfo()
        metadata.add_text('label', 'grave')
        p = self.path/'img/metadata.png'
        Image.new('RGB', (2, 2)).save(p, pnginfo=metadata)
        with self.assertRaises(ValueError):
            b.png_clean(p)

    def test_synthetic_renderer_native_pixels(self):
        line = Image.new('RGB', (100, 20))
        for x in range(100):
            for y in range(20):
                line.putpixel((x, y), (x, y, (x+y) % 256))
        w, l, wb, lb = b.render(line, [20, 3, 60, 14], [40, 4, 50, 14])
        self.assertEqual(wb, [14, 0, 66, 20])
        self.assertEqual(lb, [34, 0, 56, 20])
        self.assertEqual(w.size, (156, 60))
        self.assertEqual(l.size, (176, 160))
        self.assertEqual(l.tobytes(), line.crop(lb).resize(l.size, Image.Resampling.NEAREST).tobytes())
        self.assertEqual(w.tobytes(), line.crop(wb).resize(w.size, Image.Resampling.LANCZOS).tobytes())

    def test_synthetic_bare_and_letter_anchor(self):
        self.assertEqual(b.bare('«ἂνθρωπός,»'), 'ανθρωπος')
        self.assertEqual(b.vowel_indices('«ἂνθρωπός,»'), [0, 4, 6])

    def test_synthetic_nfd_pair_filter(self):
        results = {s: {'mark_errors': []} for s in b.STRATA}
        results[b.STRATA[0]]['mark_errors'] = [dict(card_id='c001', line_id='l1',
            detail='νερὸ → νερό; νερό → νερὸ; τὸ → το; καὶ → καί; χιοῦμορ → χιούμορ')]
        pp = b.positive_pairs(results)
        self.assertEqual([p['printed'] for p in pp], ['νερὸ', 'καὶ'])
        self.assertEqual([p['anchor_index'] for p in pp], [3, 2])


class BuiltPackValidation(unittest.TestCase):
    def test_built_pack_and_labelled_synthetic_answers(self):
        key = annotate_key(json.loads((b.ROOT/'keys/key.json').read_text()))
        self.assertEqual(len(key), 58)
        # The completed reader workspace legitimately also has answers.jsonl/zoom.
        # Check original public payload closure in a private copy, plus manifest
        # equality; do not modify the reader workspace or relax scan().
        manifest = json.loads((b.BED/'MANIFEST.r1.json').read_text())
        with tempfile.TemporaryDirectory(prefix='SYNTHETIC-PAYLOAD-', dir=b.ROOT/'keys') as folder:
            payload = Path(folder)
            shutil.copyfile(b.PACK/'items.jsonl', payload/'items.jsonl')
            shutil.copytree(b.PACK/'img', payload/'img')
            receipt = b.scan(payload, key)
            self.assertTrue(receipt['ok'])
            self.assertEqual(receipt['files'], manifest['files'])
        fixtures = b.ROOT/'keys/synthetic'
        fixtures.mkdir(exist_ok=True)
        reports = {'label': 'SYNTHETIC ANSWERS ONLY; not Sol observations', 'scenarios': {}}
        for scenario in ('perfect', 'all_acute', 'all_grave', 'all_unreadable'):
            aa = [dict(item_id=i, accent=m['truth_accent'] if scenario == 'perfect' else scenario.removeprefix('all_'), confidence='high', note='') for i, m in key.items()]
            (fixtures/(scenario+'.SYNTHETIC.jsonl')).write_text(''.join(json.dumps(a)+'\n' for a in aa))
            report = score(aa, key)
            reports['scenarios'][scenario] = report
            if scenario == 'perfect':
                self.assertEqual(report['overall']['accuracy'], 1)
                self.assertEqual(report['positive_lines']['detected'], 26)
                self.assertEqual(report['overall']['control_passes'], 6)
            if scenario == 'all_acute':
                self.assertEqual(report['positive_lines']['detected'], 0)
            if scenario == 'all_grave':
                self.assertEqual(report['negative_false_alarms']['rate'], 1)
            if scenario == 'all_unreadable':
                self.assertEqual(report['overall']['unreadable'], 58)
        b.dump(fixtures/'SYNTHETIC_REPORTS.json', reports)
        self.assertEqual({m['line_id'] for m in key.values() if m['class'] == 'positive'} &
                         {m['line_id'] for m in key.values() if m['class'] != 'positive'}, set())
        for s, expected in zip(b.STRATA, (9, 11, 6)):
            self.assertEqual(sum(m['stratum'] == s and m['class'] == 'negative' for m in key.values()), expected)
        for m in key.values():
            self.assertFalse(m['geometry']['approx_letter_box'])
            if m['class'] != 'positive':
                self.assertTrue(all(v['letters'] == v['marks'] == 'y' for v in m['c1_verdicts']))


if __name__ == '__main__':
    result = unittest.main(exit=False, verbosity=2).result
    report = dict(label='SYNTHETIC TESTS; not reader results', total=result.testsRun,
                  passed=result.testsRun-len(result.errors)-len(result.failures),
                  failures=len(result.failures), errors=len(result.errors))
    b.dump(b.ROOT/'keys/SYNTHETIC_TEST_RESULTS.json', report)
    raise SystemExit(not result.wasSuccessful())
