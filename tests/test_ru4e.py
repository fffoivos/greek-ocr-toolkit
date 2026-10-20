"""Offline synthetic fixtures. Never invokes Codex, probes, or real glyph reads."""
import base64
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts/secondary'))
import ru4e as m
from PIL import Image, ImageOps


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ru4e-fixture-')
        self.root = Path(self.tmp.name)
        self.art, self.pack = self.root/'art', self.root/'packs'
        self.sources = {s: self.root/(s+'.jsonl') for s in ('test', 'dev')}
        self.books = self.root/'books.json'
        m.dump(self.books, dict(books={f'fixture:book{i}': {} for i in range(9)}))
        self.data = []
        for n, split in enumerate(self.sources):
            image = self.root/(split+'.png')
            Image.new('RGB', (19+n, 7+n), 'white').save(image)
            row = dict(id='fixture-'+split+'-line', source='fixture', doc=f'book{n}',
                       label='  конь, домъ конь-\tпуть.\u0301 ', crop=str(image))
            m.jsonl(self.sources[split], [row])
            self.data.append(dict(row, ru4e_split=split))
        image = self.root/'control.png'
        Image.new('RGB', (14, 6), 'black').save(image)
        masked, slots = m.mask('конь домъ конь домъ')
        for slot in slots:
            slot.update(prior='unknown', control_truth=slot['google'])
        self.pool = [dict(control=True, row_id='control-private-row', source_id='control-private-row',
                          slots=slots, book='control:book', masked_text=masked,
                          image=str(image), source_crop_sha256=m.sha(image))]
        self.info = m.build(self.sources, self.books, self.art, self.pack, self.pool)
        self.registry = self.root/'versions.json'
        m.dump(self.registry, dict(versions={'untouched': {'value': 42},
               'google_raw_v2_import': dict(path=str(self.sources['test']), sha256=m.sha(self.sources['test']),
                                           text_field='label', id_field='id', parent=None)}))
        self.output = self.root/'ru1_v3_test_edits.jsonl'

    def tearDown(self):
        self.tmp.cleanup()

    def reader(self, reader, art=None, pack=None, ctx='ctx01', call='ъ', void=False):
        art, pack = art or self.art, pack or self.pack
        rd = pack/ctx/reader
        key = json.loads((art/f'keys/{m.stem(ctx, reader)}.json').read_text())
        records = [dict(type='turn_context', payload=dict(model='gpt-6.1-sol', effort='medium',
                                                        unique=str(art)+reader))]
        answers = []
        for j, item in enumerate(m.rows(rd/'items.jsonl')):
            meta = key['items'][item['item_id']]
            calls = {str(n): ('other' if void else slot['control_truth']) if meta['control'] else call
                     for n, slot in enumerate(meta['slots'], 1)}
            answers.append(dict(item_id=item['item_id'], slots=calls,
                                confidence={k: 'high' for k in calls}, unmarked_final_hard_signs=[],
                                pre1918='unclear', note='synthetic'))
            records.extend([
                dict(payload=dict(type='function_call', name='view_image', call_id=f'v{j}',
                                  arguments=json.dumps(dict(path=item['crop'])))),
                dict(payload=dict(type='function_call_output', call_id=f'v{j}', output=[
                    dict(type='input_image', image_url='data:image/png;base64,'+
                         base64.b64encode((rd/item['crop']).read_bytes()).decode())]))])
        m.jsonl(rd/'answers.jsonl', answers)
        rollout = art/(m.stem(ctx, reader)+'.rollout.jsonl')
        m.jsonl(rollout, records)
        m.dump(art/f'answers/{m.stem(ctx, reader)}.run.json',
               dict(rc=0, model='gpt-6.1-sol', rollout=str(rollout)))

    def finish(self, lead=None):
        return m.finalize(self.art, self.pack, lead, self.registry, self.output)

    def both(self):
        self.reader('r1')
        self.reader('r2')

    def lead(self):
        entries = m.rows(self.art/'lead/template.jsonl')
        for e in entries:
            e.update(call='ъ' if e['proposed'] == 'edit_hard' else 'ь',
                     pixel_checked=True, reviewer='synthetic-lead', note='fixture pixels')
        path = self.root/'lead-completed.jsonl'
        m.jsonl(path, entries)
        return path

    def test_exact_census_scope(self):
        pp = m.rows(self.art/'candidate_positions.full.jsonl')
        self.assertEqual(len(pp), 4)
        self.assertEqual({p['kind'] for p in pp}, {'final'})
        self.assertEqual({p['google'] for p in pp}, {'ь'})
        self.assertEqual(self.info['rows'], dict(test=1, dev=1))
        self.assertEqual(len(self.info['counts']), 18)

    def test_reverse_fresh_ids_and_controls_budget(self):
        r1, r2 = [m.rows(self.pack/f'ctx01/{r}/items.jsonl') for r in ('r1', 'r2')]
        strip = lambda seq: [{k: v for k, v in i.items() if k != 'item_id'} for i in seq]
        self.assertEqual(strip(r1), strip(reversed(r2)))
        self.assertFalse({i['item_id'] for i in r1} & {i['item_id'] for i in r2})
        self.assertEqual(self.info['budget']['item_reads'], 6)
        self.assertEqual(self.info['budget']['points'], .012)
        self.assertLessEqual(len(r1), 100)
        self.assertTrue(all(r['ok'] for r in m.closure(self.pack, self.art, True)))

    def test_no_reads_pending_no_output(self):
        self.assertEqual(self.finish()['status'], 'PENDING_READS')
        self.assertFalse(self.output.exists())
        with self.assertRaisesRegex(ValueError, 'PENDING_READS'):
            self.finish(self.root/'missing-lead')

    def test_full_roundtrip_raw_overlay_split_and_lqb(self):
        self.both()
        report = self.finish()
        self.assertEqual(report['counts'], {'edit_hard': 4})
        self.assertEqual(report['lead']['audit_edit_hard'], 4)
        self.assertFalse(self.output.exists())
        result = self.finish(self.lead())
        out = m.rows(self.output)
        self.assertEqual({r['split'] for r in out}, {'test', 'dev'})
        self.assertEqual(out[0]['label'], '  конъ, домъ конь-\tпутъ.\u0301 ')
        self.assertEqual(out[0]['label_parent'].encode(), self.data[0]['label'].encode())
        self.assertEqual(result['counts']['edits'], 4)
        self.assertTrue(out[0]['edits'][0]['reads'][0]['evidence'])
        self.assertTrue(out[0]['edits'][0]['lead']['pixel_checked'])
        self.assertTrue(self.output.with_suffix('.sha256').exists())
        from greekocr.labelfix.lqb import load_version
        reg = json.loads(self.registry.read_text())
        self.assertEqual(reg['versions']['untouched'], {'value': 42})
        self.assertEqual(load_version('ru1_v3_test_edits', reg), {r['id']: r['label'] for r in out})
        with self.assertRaisesRegex(ValueError, 'overwrite'):
            self.finish(self.lead())

    def test_keep_omitted_and_hold_included(self):
        self.reader('r1', call='ь')
        self.reader('r2', call='ь')
        report = self.finish()
        self.assertEqual(report['counts'], {'keep_soft': 4})
        result = self.finish(self.lead())
        self.assertEqual(result['output']['rows'], 0)
        from greekocr.labelfix.lqb import load_version
        reg = json.loads(self.registry.read_text())
        self.assertEqual(load_version('ru1_v3_test_edits', reg), {r['id']: r['label'] for r in self.data})

    def test_disagreement_cannot_be_promoted(self):
        self.reader('r1', call='ъ')
        self.reader('r2', call='ь')
        self.assertEqual(self.finish()['lead']['genuine_disagreements'], 4)
        path = self.lead()
        checks = m.rows(path)
        checks[0]['call'] = 'ъ'
        m.jsonl(path, checks)
        with self.assertRaisesRegex(ValueError, 'cannot create edit'):
            self.finish(path)
        for e in checks:
            e['call'] = 'hold'
        m.jsonl(path, checks)
        result = self.finish(path)
        self.assertEqual(result['counts']['hold_rows'], 2)
        self.assertTrue(all(r['label'] == r['label_parent'] for r in m.rows(self.output)))

    def test_all_edits_need_pixels(self):
        self.both()
        self.finish()
        path = self.lead()
        checks = m.rows(path)
        checks[0]['pixel_checked'] = False
        m.jsonl(path, checks)
        with self.assertRaisesRegex(ValueError, 'pixel check'):
            self.finish(path)
        self.assertFalse(self.output.exists())

    def test_void_builds_r3_and_admits_fresh_evidence(self):
        self.reader('r1')
        self.reader('r2', void=True)
        report = self.finish()
        self.assertEqual(report['contexts']['ctx01/r2']['status'], 'VOID')
        self.assertEqual(report['status'], 'PENDING_READS')
        repl = report['replacements'][0]
        self.assertEqual(len(report['replacements']), 1)
        self.assertEqual(self.finish()['replacements'], report['replacements'])
        self.reader('r3', Path(repl['art']), Path(repl['pack']))
        self.assertEqual(self.finish()['counts'], {'edit_hard': 4})
        self.finish(self.lead())
        self.assertEqual(len(m.rows(self.output)), 2)

    def test_both_void_get_independent_replacements(self):
        self.reader('r1', void=True)
        self.reader('r2', void=True)
        report = self.finish()
        self.assertEqual(len(report['replacements']), 2)
        ids = []
        for repl in report['replacements']:
            ids.append({i['item_id'] for i in m.rows(Path(repl['pack'])/'ctx01/r3/items.jsonl')})
            self.reader('r3', Path(repl['art']), Path(repl['pack']))
        self.assertFalse(ids[0] & ids[1])
        self.assertEqual(self.finish()['counts'], {'edit_hard': 4})

    def test_failed_model_is_not_admitted(self):
        self.both()
        p = self.art/'ctx01.r2.rollout.jsonl'
        records = m.rows(p)
        records[0]['payload']['model'] = 'wrong'
        m.jsonl(p, records)
        report = self.finish()
        self.assertEqual(report['contexts']['ctx01/r2']['status'], 'FAILED')
        self.assertEqual(report['status'], 'PENDING_READS')

    def test_reused_rollout_is_not_admitted(self):
        self.both()
        (self.art/'answers/ctx01.r2.run.json').write_bytes((self.art/'answers/ctx01.run.json').read_bytes())
        self.assertEqual(self.finish()['contexts']['ctx01/r2']['status'], 'FAILED')

    def test_forbidden_read_is_not_admitted(self):
        self.both()
        p = self.art/'ctx01.r2.rollout.jsonl'
        records = m.rows(p)
        records.append(dict(payload=dict(type='function_call', name='exec_command',
                       arguments=json.dumps(dict(cmd='cat ../keys/private.json')))))
        m.jsonl(p, records)
        self.assertEqual(self.finish()['contexts']['ctx01/r2']['status'], 'FAILED')

    def test_derived_and_unviewed_coverage(self):
        self.both()
        rd = self.pack/'ctx01/r2'
        items = m.rows(rd/'items.jsonl')
        key = json.loads((self.art/'keys/ctx01.r2.json').read_text())
        n = next(j for j, i in enumerate(items) if not key['items'][i['item_id']]['control'])
        item = items[n]
        p = self.art/'ctx01.r2.rollout.jsonl'
        records = m.rows(p)
        del records[1+2*n:3+2*n]
        m.jsonl(p, records)
        self.assertEqual(self.finish()['coverage']['ctx01/r2']['unviewed'], 1)
        zoom = rd/'zoom/montage.png'
        zoom.parent.mkdir()
        with Image.open(rd/item['crop']) as im:
            tile = ImageOps.expand(im, border=3, fill='black')
            montage = Image.new('RGB', (tile.width*2, tile.height), 'gray')
            montage.paste(tile, (0, 0)); montage.paste(tile, (tile.width, 0)); montage.save(zoom)
        command = 'magick '+item['crop']+' -bordercolor black -border 3x3 '+item['crop']+' -bordercolor black -border 3x3 +append zoom/montage.png'
        records.extend([
            dict(payload=dict(type='function_call', name='exec_command', arguments=json.dumps(dict(cmd=command)))),
            dict(payload=dict(type='function_call', name='view_image', call_id='montage', arguments=json.dumps(dict(path='zoom/montage.png')))),
            dict(payload=dict(type='function_call_output', call_id='montage', output=[dict(type='input_image', image_url='data:image/png;base64,'+base64.b64encode(zoom.read_bytes()).decode())]))])
        m.jsonl(p, records)
        report = self.finish()
        self.assertEqual(report['coverage']['ctx01/r2']['derived'], 1)
        self.assertEqual(report['counts'], {'edit_hard': 4})

    def test_parent_and_pack_tamper(self):
        p = self.pack/'ctx01/r1/items.jsonl'
        original = p.read_bytes()
        p.write_text('{}\n')
        with self.assertRaisesRegex(ValueError, 'bound input'):
            self.finish()
        p.write_bytes(original)
        self.sources['test'].write_text(self.sources['test'].read_text()+'\n')
        with self.assertRaisesRegex(ValueError, 'bound input'):
            self.finish()

    def test_empty_scope_is_explicit(self):
        sources = {s: self.root/(s+'-empty.jsonl') for s in self.sources}
        for p in sources.values():
            m.jsonl(p, [dict(id='unrelated', source='other', doc='x', label='конь')])
        art, pack = self.root/'empty-art', self.root/'empty-pack'
        info = m.build(sources, self.books, art, pack, self.pool)
        self.assertEqual(info['status'], 'EMPTY_SCOPE')
        self.assertEqual(info['budget']['points'], 0)
        self.assertEqual(m.finalize(art, pack)['status'], 'EMPTY_SCOPE')
        with self.assertRaisesRegex(ValueError, 'EMPTY_SCOPE'):
            m.finalize(art, pack, self.root/'none')

    def test_large_pack_and_20_10_audit(self):
        sources = {s: self.root/(s+'-large.jsonl') for s in self.sources}
        data = [dict(self.data[0], id=f'large-fixture-line-{n:04}', label='конь') for n in range(120)]
        m.jsonl(sources['test'], data)
        m.jsonl(sources['dev'], [])
        art, pack = self.root/'large-art', self.root/'large-pack'
        info = m.build(sources, self.books, art, pack, self.pool)
        self.assertEqual(len(info['contexts']), 2)
        self.assertTrue(all(c['items'] <= 100 for c in info['contexts']))
        pp = m.rows(art/'candidate_positions.full.jsonl')
        ds = [dict(p, decision='edit_hard' if n < 80 else 'keep_soft', reason='fixture') for n, p in enumerate(pp)]
        entries, audit = m.lead_sheets(art, pack, ds)
        self.assertEqual((audit['edit_checks'], audit['audit_edit_hard'], audit['audit_keep_soft']), (80, 20, 10))
        self.assertEqual(len(entries), 90)
        self.assertEqual(entries, m.lead_sheets(art, pack, ds)[0])

    def test_parent_split_hash_and_foreign_id_rejected_by_lqb(self):
        self.both()
        self.finish()
        self.finish(self.lead())
        from greekocr.labelfix.lqb import load_version
        reg = json.loads(self.registry.read_text())
        bad = copy.deepcopy(reg)
        bad['versions']['google_raw_v2_import']['splits']['dev']['sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'parent split sha256'):
            load_version('ru1_v3_test_edits', bad)
        out = m.rows(self.output)
        out.append(dict(id='foreign-id', label='x', split='test'))
        m.jsonl(self.output, out)
        reg['versions']['ru1_v3_test_edits']['sha256'] = m.sha(self.output)
        with self.assertRaisesRegex(ValueError, 'outside parent splits'):
            load_version('ru1_v3_test_edits', reg)


class DriverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ru4e-driver-')
        self.art, self.pack = Path(self.tmp.name)/'art', Path(self.tmp.name)/'pack'
        self.art.mkdir()
        self.info = dict(status='READY_FOR_READINGS', contexts=[dict(context='ctx01'), dict(context='ctx02')])
        self.patcher = patch.object(m, 'validate', return_value=self.info)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tmp.cleanup()

    def test_dry_run_no_probe_or_read(self):
        def fail(*a, **kw):
            self.fail('live call')
        result = m.drive(self.art, self.pack, True, fail, fail)
        self.assertEqual(result['contexts'], 4)
        self.assertEqual(result['probes'], 0)

    def test_exact_70_stops_before_claim(self):
        def fail(*a, **kw):
            self.fail('reader launched')
        result = m.drive(self.art, self.pack, False, fail, lambda *a, **kw: 'primary=70%/10080m')
        self.assertEqual(result['status'], 'STOPPED_AT_70')
        self.assertFalse((self.art/'answers').exists())

    def test_failed_attempts_never_rerun(self):
        calls = []
        def run(cmd, **kw):
            calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 1, '', 'synthetic failure')
        probe = lambda *a, **kw: 'primary=69%/10080m'
        m.drive(self.art, self.pack, False, run, probe)
        m.drive(self.art, self.pack, False, run, probe)
        self.assertEqual(len(calls), 4)
        self.assertTrue(all('ru4e_bound/run_read.sh' in c[1] for c in calls))

    def test_bad_probe_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'weekly'):
            m.drive(self.art, self.pack, False, lambda *a, **kw: self.fail('launch'),
                    lambda *a, **kw: 'NONE')

    def test_in_repo_and_symlink_guard(self):
        repo = Path(self.tmp.name)/'guard-repo'
        repo.mkdir(); (repo/'.git').mkdir()
        with self.assertRaisesRegex(ValueError, 'outside every git'):
            m.external(repo/'no-packs')
        alias = Path(self.tmp.name)/'alias'
        alias.symlink_to(repo, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'outside every git'):
            m.external(alias/'no-packs')


class MatrixTests(unittest.TestCase):
    def test_all_call_pairs(self):
        for a in ('ъ', 'ь', 'u', 'other'):
            for b in ('ъ', 'ь', 'u', 'other'):
                votes = [dict(logical_reader=r, call=c, gate_status='VALID')
                         for r, c in zip(('r1', 'r2'), (a, b))]
                self.assertEqual(m.combine({}, votes)['decision'],
                                 'edit_hard' if a == b == 'ъ' else 'keep_soft' if a == b == 'ь' else 'hold')

    def test_void_and_duplicate_role_cannot_edit(self):
        votes = [dict(logical_reader=r, call='ъ', gate_status=g)
                 for r, g in [('r1', 'VALID'), ('r2', 'VOID')]]
        self.assertEqual(m.combine({}, votes)['decision'], 'hold')
        votes[1].update(logical_reader='r1', gate_status='VALID')
        self.assertEqual(m.combine({}, votes)['decision'], 'hold')


if __name__ == '__main__':
    unittest.main()
