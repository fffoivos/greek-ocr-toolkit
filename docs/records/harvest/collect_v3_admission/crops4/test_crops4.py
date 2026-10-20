"""Local only: real bound W2 pixels, temporary mock census and cluster roots."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

B = Path(__file__).resolve().parent
P = Path.home() / 'Projects'
CODE = Path(os.environ.get('CROPS4_TEST_CODE', P / 'greek-ocr-toolkit-main-next/docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut'))
spec = importlib.util.spec_from_file_location('crops4', B / 'materialise_crops.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def seal(package):
    names = sorted(p.name for p in package.iterdir() if p.is_file() and p.name not in {'DEPLOY_SHA256SUMS', 'TEST_RESULTS.json', 'TESTS.log', 'COMMIT_LIST.json', 'COMMIT_LIST.md'})
    (package / 'DEPLOY_SHA256SUMS').write_text(''.join(m.sha(package / n) + '  ' + n + '\n' for n in names))


class Crops4(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='crops4-mock-')
        cls.root = Path(cls.tmp.name)
        cls.package = cls.root / 'package'; cls.package.mkdir()
        for name in ('materialise_crops.py', 'VERIFY.sh', 'crops4.sbatch', 'binding_checks.sh'):
            shutil.copy2(B / name, cls.package / name)
        seal(cls.package)
        cls.census = cls.root / 'census_05'
        cls.gen = cls.census / 'generations/g1'; cls.gen.mkdir(parents=True)
        cache = cls.root / 'pages'; cache.mkdir()
        cls.real = []; per_source = {}
        for r in m.lines(P / 'collect-v3-data/snapshots/W2_features_20261018_0524.jsonl'):
            source = Path(r['crop_source_image'])
            if not source.is_file() or per_source.get(r['source'], 0) >= 4:
                continue
            per_source[r['source']] = per_source.get(r['source'], 0) + 1
            dest = cache / source.name
            if not dest.exists():
                shutil.copyfile(source, dest)
            row = {k: r[k] for k in ('id', 'source', 'crop_bbox', 'crop_sha256', 'crop_source_sha256')}
            row.update(parent_id='collect-v3-W2-' + r['source'], split='train', crop_source_image=str(dest))
            cls.real.append(row)
            if len(cls.real) == 20:
                break
        assert len(cls.real) == 20
        cls.rows = copy.deepcopy(cls.real)
        # 480 explicit aliases exercise a 500-row gate without claiming 500 independent originals.
        for i in range(480):
            row = dict(cls.real[i % 20], id='mock-alias-%04d' % i)
            cls.rows.append(row)
        cls.held = [dict(cls.real[0], id='held-dev', split='dev'), dict(cls.real[1], id='held-test', split='test')]
        cls.publish()
        cls.projects = cls.root / 'prepared/projects'; cls.projects.mkdir(parents=True)
        (cls.projects / 'greek-ocr-toolkit-sol-recut').symlink_to(CODE, target_is_directory=True)
        (cls.projects / 'SHA256SUMS').write_text(m.sha(CODE / 'greekocr/harvest/line_pipeline_native.py') + '  greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_native.py\n')
        cls.stub = cls.root / 'bin'; cls.stub.mkdir()
        srun = cls.stub / 'srun'
        srun.write_text('#!/bin/bash\nset -eu\n[[ "$1" == -A && "$2" == a0140 ]]\nshift 2\nwhile [[ "$1" == --* ]]; do shift; done\nexec "$@"\n')
        srun.chmod(0o755)
        cls.env = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE='1', CODEC_PRELOAD='',
                       RECONSTRUCTION_SHA256=m.sha(CODE / 'greekocr/harvest/line_pipeline_native.py'),
                       PATH=str(cls.stub) + os.pathsep + os.environ['PATH'], LD_PRELOAD='')
        cls.work = cls.root / 'W'
        cls.smoke = cls.work / 'crops4_attempts/smoke'
        start = time.monotonic()
        cls.run_cli('--mode', 'smoke', '--attempt', str(cls.smoke), check=True)
        cls.smoke_seconds = time.monotonic() - start
        cls.smoke_receipt = cls.smoke / 'upload_receipt.json'
        cls.full = cls.work / 'crops4_attempts/full'
        cls.run_cli('--mode', 'full', '--attempt', str(cls.full), '--smoke-receipt', str(cls.smoke_receipt), check=True)

    @classmethod
    def publish(cls):
        values = {'admitted_train': [dict(r, decision=dict(binding=m.identity(r), admitted=True)) for r in cls.rows],
                  'decisions': [dict(binding=m.identity(r), admitted=True) for r in cls.rows + cls.held],
                  'evaluation_diagnostics': [dict(row=r, decision=dict(binding=m.identity(r), admitted=True)) for r in cls.held]}
        outputs = {}
        for name, rows in values.items():
            path = cls.gen / (name + '.jsonl')
            path.write_text(''.join(json.dumps(r) + '\n' for r in rows))
            outputs[name] = dict(path=str(path), sha256=m.sha(path))
        summary = cls.gen / 'summary.json'
        summary.write_text(json.dumps(dict(complete=True, outputs=outputs)))
        (cls.census / 'CURRENT.json').write_text(json.dumps(dict(status='completed', export_id='g1', summary_sha256=m.sha(summary))))

    @classmethod
    def run_cli(cls, *args, check=False, package=None):
        command = [sys.executable, '-B', str((package or cls.package) / 'materialise_crops.py'),
                   '--census-attempt', str(cls.census), '--census-code', str(CODE),
                   '--work-root', str(cls.work), '--attempt', str(cls.work / 'crops4_attempts/default'), '--workers', '8', *args]
        return subprocess.run(command, env=cls.env, text=True, capture_output=True, check=check)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_01_twenty_real_originals_byte_exact(self):
        for row in self.real:
            path = self.work / ('collection_w2_originals/' + row['source'] + '/' + row['id'] + '.png')
            self.assertEqual(m.sha(path), row['crop_sha256'])
        r = json.loads((self.full / 'upload_receipt.json').read_text())
        self.assertEqual((r['byte_exact'], r['mismatches'], r['failures']), (500, 0, 0))
        self.assertEqual(r['context']['reconstruction_sha256'], m.sha(CODE / 'greekocr/harvest/line_pipeline_native.py'))

    def test_02_smoke_isolation_and_sorted_selection(self):
        self.assertFalse((self.smoke / 'collection_w2_originals').exists())
        rows = list(m.lines(self.smoke / 'crops_manifest.jsonl'))
        self.assertEqual({r['row_id'] for r in rows}, {r['id'] for r in sorted(self.rows, key=lambda r:r['id'])[:500]})
        self.assertTrue(all((self.smoke / 'smoke' / r['relative_path']).is_file() for r in rows))

    def test_03_idempotence(self):
        self.run_cli('--mode', 'full', '--attempt', str(self.full), '--smoke-receipt', str(self.smoke_receipt), check=True)
        r = json.loads((self.full / 'upload_receipt.json').read_text())
        self.assertEqual((r['written'], r['skipped_valid']), (0, 500))

    def test_04_corrupt_existing_never_overwritten(self):
        row = self.real[0]
        path = self.work / ('collection_w2_originals/' + row['source'] + '/' + row['id'] + '.png')
        good = path.read_bytes(); path.write_bytes(b'corrupt')
        try:
            self.assertNotEqual(self.run_cli('--mode', 'full', '--attempt', str(self.full), '--smoke-receipt', str(self.smoke_receipt)).returncode, 0)
            self.assertEqual(path.read_bytes(), b'corrupt')
            r = json.loads((self.full / 'upload_receipt.json').read_text())
            self.assertEqual((r['status'], r['mismatches']), ('failed', 1))
        finally:
            path.write_bytes(good)

    def verify(self, package=None):
        return subprocess.run(['bash', str((package or self.package) / 'VERIFY.sh'), '--census-attempt', str(self.census),
            '--census-code', str(CODE), '--work-root', str(self.work), '--attempt', str(self.full), '--include-heldout'],
            env=self.env, text=True, capture_output=True)

    def test_05_verify_ok_and_heldout(self):
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'VERIFY_OK 502 ' + str(len({r['crop_source_image'] for r in self.rows})) + '\n')

    def test_06_verify_deploy_drift(self):
        bad = self.root / 'drift'; shutil.copytree(self.package, bad)
        with (bad / 'materialise_crops.py').open('a') as f: f.write('\n# drift\n')
        self.assertNotEqual(self.verify(bad).returncode, 0)

    def test_07_verify_missing_page(self):
        page = Path(self.real[0]['crop_source_image']); moved = page.with_suffix('.missing'); page.rename(moved)
        try:
            result = self.verify()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('missing pages', result.stderr)
        finally:
            moved.rename(page)

    def test_08_checksums_command(self):
        self.assertEqual(m.checksum_check(self.work, self.full / 'crops_sha256.txt'), 0)

    def test_09_full_gate_rejects_missing_or_tampered_smoke(self):
        self.assertNotEqual(self.run_cli('--mode', 'full').returncode, 0)
        r = json.loads(self.smoke_receipt.read_text()); r['byte_exact'] = 499
        bad = self.root / 'bad_receipt.json'; bad.write_text(json.dumps(r))
        self.assertNotEqual(self.run_cli('--mode', 'full', '--smoke-receipt', str(bad)).returncode, 0)
        r = next(m.lines(self.smoke / 'crops_manifest.jsonl'))
        path = self.smoke / 'smoke' / r['relative_path']; good = path.read_bytes(); path.write_bytes(b'drift')
        try:
            self.assertNotEqual(self.run_cli('--mode', 'full', '--smoke-receipt', str(self.smoke_receipt)).returncode, 0)
        finally:
            path.write_bytes(good)

    def test_10_census_hash_drift(self):
        path = self.gen / 'admitted_train.jsonl'; good = path.read_bytes(); path.write_bytes(good + b'\n')
        try:
            self.assertNotEqual(self.verify().returncode, 0)
        finally:
            path.write_bytes(good)

    def test_11_cluster_script_smoke_and_full_heldout(self):
        env = dict(self.env, W=str(self.work), CENSUS_ATTEMPT=str(self.census), CENSUS_PROJECTS=str(self.projects),
                   PROJECTS_SHA256=m.sha(self.projects / 'SHA256SUMS'), INCLUDE_HELDOUT='1', SLURM_CPUS_PER_TASK='8',
                   ATTEMPT='sbatch_smoke', MODE='smoke')
        def run():
            result = subprocess.run(['bash', str(self.package / 'crops4.sbatch')], env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        run()
        env.update(ATTEMPT='sbatch_full', MODE='full', SMOKE_RECEIPT=str(self.work / 'crops4_attempts/sbatch_smoke/upload_receipt.json'))
        run()
        r = json.loads((self.work / 'crops4_attempts/sbatch_full/upload_receipt.json').read_text())
        self.assertEqual((r['selected'], r['train_selected'], r['heldout_selected'], r['byte_exact']), (502, 500, 2, 502))
        self.assertEqual((self.work / 'crops4_attempts/sbatch_full/verify.log').read_text().split()[0], 'VERIFY_OK')

    def test_12_twenty_row_only_mock(self):
        # Separate measured run with exactly 20 originals and no gate aliases.
        old_rows = self.rows
        try:
            type(self).rows = self.real
            self.publish()
            attempt = self.work / 'crops4_attempts/real20'
            result = self.run_cli('--mode', 'smoke', '--attempt', str(attempt), check=True)
            receipt = json.loads((attempt / 'upload_receipt.json').read_text())
            self.assertEqual((receipt['selected'], receipt['byte_exact']), (20, 20))
            report = dict(tests=12, independent_originals=20, byte_exact=20, smoke_gate_rows=500,
                smoke_gate_aliases=480, smoke_seconds=self.smoke_seconds, real20_seconds=receipt['seconds'],
                projected_w2_3x_seconds=self.smoke_seconds / 500 * 219381 * 3,
                projected_w1w2_3x_seconds=self.smoke_seconds / 500 * 320479 * 3,
                reconstruction_module=m.MODULE, reconstruction_function=m.FUNCTION,
                reconstruction_sha256=m.sha(CODE / 'greekocr/harvest/line_pipeline_native.py'),
                interpreter=sys.executable, cpus=8, time_limit='01:30 (production default; local rate is not sizing evidence)',
                note='Local filesystem and alias smoke rate; Clariden filesystem throughput remains unmeasured.')
            (B / 'TEST_RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')
        finally:
            type(self).rows = old_rows
            self.publish()


    def test_13_independent_500_rate(self):
        old_rows = self.rows
        cache = self.root / 'pages'
        sample = []; per_source = {}
        for r in m.lines(P / 'collect-v3-data/snapshots/W2_features_20261018_0524.jsonl'):
            source = Path(r['crop_source_image'])
            if not source.is_file() or per_source.get(r['source'], 0) >= 100:
                continue
            per_source[r['source']] = per_source.get(r['source'], 0) + 1
            dest = cache / source.name
            if not dest.exists(): shutil.copyfile(source, dest)
            row = {k: r[k] for k in ('id', 'source', 'crop_bbox', 'crop_sha256', 'crop_source_sha256')}
            row.update(parent_id='collect-v3-W2-' + r['source'], split='train', crop_source_image=str(dest))
            sample.append(row)
            if len(sample) == 500: break
        self.assertEqual(len(sample), 500)
        try:
            type(self).rows = sample; self.publish()
            attempt = self.work / 'crops4_attempts/rate500'
            started = time.monotonic()
            self.run_cli('--mode', 'smoke', '--attempt', str(attempt), check=True)
            elapsed = time.monotonic() - started
            receipt = json.loads((attempt / 'upload_receipt.json').read_text())
            self.assertEqual((receipt['selected'], receipt['byte_exact']), (500, 500))
            report = json.loads((B / 'TEST_RESULTS.json').read_text())
            report.update(tests=23, rate_sample_independent_originals=500, rate_seconds=elapsed,
                rate_pages=receipt['pages'], rate_bytes=receipt['bytes'],
                projected_w2_3x_seconds=elapsed / 500 * 219381 * 3,
                projected_w1w2_3x_seconds=elapsed / 500 * 320479 * 3,
                note='Rate uses 500 independent original bindings, 100 per source for first five sources; local filesystem, not a Clariden throughput qualification.')
            self.assertLess(report['projected_w1w2_3x_seconds'], 1800)
            (B / 'TEST_RESULTS.json').write_text(json.dumps(report, indent=2) + '\n')
        finally:
            type(self).rows = old_rows; self.publish()

    def test_14_w1_and_all_selection(self):
        old_rows = self.rows
        try:
            type(self).rows = self.rows + [dict(self.real[0], parent_id='collect-v3-W1-mock')]
            self.publish()
            for tranche, count in [('W1', 1), ('all', 501), ('W2', 500)]:
                result = self.run_cli('--verify-only', '--tranche', tranche, check=True)
                self.assertEqual(result.stdout.split()[:2], ['VERIFY_OK', str(count)])
        finally:
            type(self).rows = old_rows; self.publish()

    def census05_env(self, attempt):
        code_root = self.root / 'census05_code'
        projects = code_root / 'docs/harvest/census05/package/projects'
        code = projects / 'greek-ocr-toolkit-pipe032'
        if not code.exists():
            shutil.copytree(CODE / 'greekocr', code / 'greekocr', ignore=shutil.ignore_patterns('__pycache__'))
        module = code / 'greekocr/harvest/line_pipeline_native.py'
        sums = self.root / 'census05_DEPLOY_SHA256SUMS'
        sums.write_text(m.sha(module) + '  ' + str(module.relative_to(code_root)) + '\n')
        return dict(self.env, W=str(self.work), CENSUS_ATTEMPT=str(self.census), CENSUS_PROJECTS=str(projects),
                    CENSUS_CODE=str(code), PROJECTS_SUMS=str(sums), PROJECTS_SUMS_ROOT=str(code_root),
                    PROJECTS_SHA256=m.sha(sums), ATTEMPT=attempt, MODE='smoke', INCLUDE_HELDOUT='1')

    def test_15_census05_layout_end_to_end(self):
        env = self.census05_env('census05_layout')
        result = subprocess.run(['bash', str(self.package / 'crops4.sbatch')], env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        attempt = self.work / 'crops4_attempts/census05_layout'
        receipt = json.loads((attempt / 'upload_receipt.json').read_text())
        self.assertEqual((receipt['selected'], receipt['byte_exact']), (500, 500))
        self.assertEqual(receipt['context']['reconstruction_sha256'], m.sha(Path(env['CENSUS_CODE']) / 'greekocr/harvest/line_pipeline_native.py'))
        self.assertTrue((attempt / 'verify.log').read_text().startswith('VERIFY_OK'))

    def test_16_unlisted_code_fails_before_materialising(self):
        env = self.census05_env('census05_unlisted')
        other = Path(env['CENSUS_PROJECTS']) / 'unlisted-code'
        shutil.copytree(Path(env['CENSUS_CODE']), other)
        env['CENSUS_CODE'] = str(other)
        result = subprocess.run(['bash', str(self.package / 'crops4.sbatch')], env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('reconstruction module not in PROJECTS_SUMS', (self.work / 'crops4_attempts/census05_unlisted/prepared-check.log').read_text())
        attempt = self.work / 'crops4_attempts/census05_unlisted'
        self.assertFalse((attempt / 'verify.log').exists())
        self.assertFalse((attempt / 'materialise.log').exists())
        self.assertFalse((attempt / 'upload_receipt.json').exists())

    def census06_env(self, attempt):
        env = self.census05_env(attempt)
        old = Path(env['PROJECTS_SUMS_ROOT'])
        manifest = Path(env['PROJECTS_SUMS']).read_text().replace('/census05/', '/census06/')
        # Repository-relative layout stays pipe032, as required by CENSUS06.
        root = self.root / 'census_06_20261020/code' / hashlib.sha256(manifest.encode()).hexdigest()[:16]
        if not root.exists():
            shutil.copytree(Path(env['CENSUS_CODE']), root / str(Path(env['CENSUS_CODE']).relative_to(old)).replace('/census05/', '/census06/'))
        sums = root / 'DEPLOY_SHA256SUMS'; sums.write_text(manifest)
        census = self.root / 'census_06_20261020/attempts/full-split-002'
        shutil.copytree(self.census, census, dirs_exist_ok=True)
        env.update(CENSUS_ATTEMPT=str(census), CENSUS_MANIFEST=str(sums),
                   PROJECTS_SUMS_ROOT=str(root), PROJECTS_SHA256=m.sha(sums),
                   CENSUS_PROJECTS=str(root / str(Path(env['CENSUS_PROJECTS']).relative_to(old)).replace('/census05/', '/census06/')),
                   CENSUS_CODE=str(root / str(Path(env['CENSUS_CODE']).relative_to(old)).replace('/census05/', '/census06/')))
        env.pop('PROJECTS_SUMS')
        return env

    def batch(self, env):
        return subprocess.run(['bash', str(self.package / 'crops4.sbatch')], env=env, capture_output=True, text=True)

    def rejected_before_materialising(self, env, message):
        result = self.batch(env)
        self.assertNotEqual(result.returncode, 0)
        attempt = self.work / 'crops4_attempts' / env['ATTEMPT']
        self.assertIn(message, (attempt / 'prepared-check.log').read_text())
        for name in ('verify.log', 'materialise.log', 'upload_receipt.json'):
            self.assertFalse((attempt / name).exists())

    def test_17_census06_submit_time_manifest(self):
        env = self.census06_env('c06_smoke')
        result = self.batch(env)
        self.assertEqual(result.returncode, 0, result.stderr)
        receipt = json.loads((self.work / 'crops4_attempts/c06_smoke/upload_receipt.json').read_text())
        self.assertEqual((receipt['status'], receipt['selected'], receipt['byte_exact']), ('ok', 500, 500))
        self.assertEqual(receipt['context']['inputs']['CURRENT.json'], m.sha(Path(env['CENSUS_ATTEMPT']) / 'CURRENT.json'))
        env.update(MODE='full', TRANCHE='all', ATTEMPT='c06_bad_old_smoke', SMOKE_RECEIPT=str(self.smoke_receipt))
        self.assertNotEqual(self.batch(env).returncode, 0)
        self.assertIn('smoke gate failed', (self.work / 'crops4_attempts/c06_bad_old_smoke/materialise.log').read_text())

    def test_18_manifest_sha_mismatch(self):
        env = self.census06_env('bad_manifest_sha'); env['PROJECTS_SHA256'] = '0' * 64
        self.rejected_before_materialising(env, 'manifest sha mismatch')

    def test_19_manifest_code_dir_mismatch(self):
        env = self.census06_env('bad_code_dir')
        env['PROJECTS_SUMS_ROOT'] = str(Path(env['PROJECTS_SUMS_ROOT']).parent)
        self.rejected_before_materialising(env, 'manifest/code-dir name mismatch')

    def test_20_wrong_reconstruction_sha(self):
        env = self.census06_env('wrong_reconstruction'); env.pop('RECONSTRUCTION_SHA256')
        # The real mock module differs from the production default: do not weaken the default.
        self.rejected_before_materialising(env, 'reconstruction sha mismatch')

    def test_21_all_existing_and_new_per_tranche(self):
        # Seed all census05-scope heldout files independently of test order.
        self.run_cli('--mode', 'smoke', '--include-heldout', '--attempt', str(self.work / 'crops4_attempts/seed_smoke'), check=True)
        self.run_cli('--mode', 'full', '--include-heldout', '--smoke-receipt', str(self.work / 'crops4_attempts/seed_smoke/upload_receipt.json'), check=True)
        old_rows = self.rows
        try:
            type(self).rows = self.rows + [dict(self.real[0], id='c06-new-w1', parent_id='collect-v3-W1-mock'),
                                         dict(self.real[1], id='c06-new-w2')]
            self.publish()
            env = self.census06_env('all_smoke'); self.assertEqual(self.batch(env).returncode, 0)
            env.update(MODE='full', TRANCHE='all', ATTEMPT='all_full',
                       SMOKE_RECEIPT=str(self.work / 'crops4_attempts/all_smoke/upload_receipt.json'))
            existing = {p: (p.read_bytes(), p.stat().st_ino, p.stat().st_mtime_ns)
                        for p in self.work.glob('collection_w*_originals/*/*.png')}
            result = self.batch(env); self.assertEqual(result.returncode, 0, result.stderr)
            receipt_path = self.work / 'crops4_attempts/all_full/upload_receipt.json'
            r = json.loads(receipt_path.read_text())
            self.assertEqual((r['written'], r['skipped_valid']), (2, 502))
            self.assertEqual((r['per_tranche']['W1']['written'], r['per_tranche']['W2']['written']), (1, 1))
            env['ATTEMPT'] = 'all_repeat'; self.assertEqual(self.batch(env).returncode, 0)
            r = json.loads((self.work / 'crops4_attempts/all_repeat/upload_receipt.json').read_text())
            self.assertEqual((r['written'], r['skipped_valid']), (0, 504))
            self.assertEqual((r['per_tranche']['W1']['skipped_valid'], r['per_tranche']['W2']['skipped_valid']), (1, 503))
            for p, state in existing.items():
                self.assertEqual((p.read_bytes(), p.stat().st_ino, p.stat().st_mtime_ns), state)
        finally:
            type(self).rows = old_rows; self.publish()

    def test_22_batch_mismatch_untouched_nonzero(self):
        env = self.census06_env('mismatch_smoke'); self.assertEqual(self.batch(env).returncode, 0)
        env.update(MODE='full', TRANCHE='all', ATTEMPT='mismatch_full',
                   SMOKE_RECEIPT=str(self.work / 'crops4_attempts/mismatch_smoke/upload_receipt.json'))
        row = self.real[0]
        path = self.work / ('collection_w2_originals/' + row['source'] + '/' + row['id'] + '.png')
        good = path.read_bytes(); path.write_bytes(b'pre-existing conflict')
        state = (path.read_bytes(), path.stat().st_ino, path.stat().st_mtime_ns)
        try:
            result = self.batch(env); self.assertNotEqual(result.returncode, 0)
            self.assertEqual((path.read_bytes(), path.stat().st_ino, path.stat().st_mtime_ns), state)
            r = json.loads((self.work / 'crops4_attempts/mismatch_full/upload_receipt.json').read_text())
            self.assertEqual((r['status'], r['mismatches']), ('failed', 1))
        finally:
            path.write_bytes(good)

    def test_23_light_verify_without_census(self):
        result = subprocess.run(['bash', str(self.package / 'VERIFY.sh'), '--deploy-only'],
                                env=self.env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('VERIFY_DEPLOY_OK crops4 package', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
