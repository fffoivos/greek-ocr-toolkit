"""BENCH02E transport, readout and mocked Slurm integration regressions."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
import bench02_draw as b
from test_bench02_draw import SAMPLE, decision


class Bench02ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old=types.ModuleType('bench02d_reference')
        cls.old.__file__=str(b.HERE/'bench02_draw.py')
        source=subprocess.check_output(['git','show','9834244c7:docs/harvest/collect_v3_admission/bench02/bench02_draw.py'],cwd=b.HERE).decode()
        exec(compile(source,'BENCH02D_reference','exec'),cls.old.__dict__)

    def sample(self):
        files=[SAMPLE/f'decisions_{w}_2000.jsonl.gz' for w in ('W1','W2')]
        if not all(p.exists() for p in files): self.fail('required local sample absent')
        features={b.key(r['decision']):r['row'] for w in ('W1','W2') for r in b.rows(SAMPLE/f'evaluation_diagnostics_{w}_2000.jsonl.gz')}
        return [(d,features[b.key(d)]) for p in files for d in b.rows(p)]

    def test_slim_export_has_no_text_or_long_strings(self):
        def check(value,name=''):
            if isinstance(value,dict):
                self.assertNotIn('final_text',value)
                for k,v in value.items(): check(v,k)
            elif isinstance(value,list):
                for v in value: check(v,name)
            elif isinstance(value,str) and not (name.endswith('_id') or 'sha' in name): self.assertLessEqual(len(value),64,(name,value))
        for d,f in self.sample():
            r=b.slim(d,f);check(r)
            self.assertNotIn('final_inventory',r);self.assertNotIn('expectations',r)
            self.assertIn('split',r)
        d=decision();d['final_text']='Secret sentence. '*100
        d['final_inventory']['mixed_words']=['SecretΑβγ']
        r=b.slim(d,dict(leader_runs=['secret'*30],crop_bbox=[1,2,3,4],series='unused'))
        check(r);self.assertTrue(r['text_facets']['mixed_words'])
        self.assertEqual(True,r['evidence']['leader_runs'])
        self.assertNotIn('crop_bbox',r['evidence']);self.assertNotIn('series',r['evidence'])

    def test_classifier_matches_pinned_bench02d_sample(self):
        self.assertEqual(self.old.PRECEDENCE,b.PRECEDENCE);self.assertEqual(self.old.QUOTAS,b.QUOTAS)
        for d,f in self.sample():
            old=self.old.tag(self.old.slim(d,f));new=b.tag(b.slim(d,f))
            # BENCH02F intentionally changes cell/short, gate inventory,
            # punctuation and degraded evidence. Preserve every other tag.
            changed={'numeric_cells','cell_flag','short','punctuation_heavy','degraded','leaders_dashes'}
            if 'final_inventory' not in d: changed.update(('monotonic','polytonic','latin','greek_latin','historical_russian','modern_cyrillic','cyrillic_language'))
            for k,v in old['tags'].items():
                if k not in changed:self.assertEqual(v,new['tags'][k],(b.key(d),k))
            self.assertEqual(old['source'],new['source'])
            self.assertEqual(old['font_size'],new['font_size'])

    def test_draw_identical_slim_and_full_sample_with_nonempty_supply(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td)
            def write(name,rr):
                p=td/name;p.write_text(''.join(b.canonical(r)+'\n' for r in rr));return p
            pairs=self.sample();slim=[b.slim(d,f) for d,f in pairs]
            # Full and slim forms share the census_05 adapter, as required by F.
            full=[dict(r,final_text=d['final_text'],final_inventory=d.get('final_inventory',d.get('raw_inventory',{})),expectations=d.get('expectations',{})) for r,(d,f) in zip(slim,pairs)]
            for r in full:r.pop('text_facets')
            # Exercise selection beyond the original empty draw: fixture-only admission/splits.
            # Text and classifier evidence are the real unchanged 4,000-row sample.
            for r in full+slim:r['admitted']=True
            split=write('split.jsonl',[dict(parent_id=r['parent_id'],row_id=r['row_id'],edition_id=f'e{i}',split=('test','dev')[i%2]) for i,r in enumerate(slim)])
            ed=write('ed.jsonl',[dict(edition_id=f'e{i}',member_documents=[]) for i in range(len(slim))])
            fs=[write(f'W{i}.jsonl',[]) for i in (1,2)];v2=[write(f'v{i}.jsonl',[]) for i in range(3)]
            manifest=td/'ex.json';manifest.write_text('{"classes":{}}')
            paths=[write('full.jsonl',full),write('slim.jsonl',slim)]
            for i,tags in enumerate(paths):b.draw(tags,split,[ed],fs,v2,manifest,td/str(i))
            self.assertEqual((td/'0/candidates.jsonl').read_bytes(),(td/'1/candidates.jsonl').read_bytes())
            candidates=list(b.rows(td/'1/candidates.jsonl'));self.assertGreater(len(candidates),0)
            for r in candidates:
                self.assertEqual({'parent_id','row_id','split','source','edition_id','class','tags','rank'},set(r))
            self.assertEqual(self.old.PRECEDENCE,b.PRECEDENCE)
            self.assertEqual(self.old.QUOTAS,b.QUOTAS)

    def test_readout_exact_candidate_keys_and_authoritative_fields(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td);ds=[decision('a'),decision('b'),decision('a','collect-v3-W2-x')]
            for i,d in enumerate(ds): d.update(raw_text_sha256=str(i)*64,edits=[dict(kind='test',index=i)])
            def write(name,rr):(td/name).write_text(''.join(b.canonical(r)+'\n' for r in rr))
            write('decisions.jsonl',list(reversed(ds)))
            write('evaluation_diagnostics.jsonl',[dict(decision=d,row=dict(parent_id=b.key(d)[0],id=b.key(d)[1],crop_sha256='a'*64,crop_source_image=f'/page/{i}.png',crop_bbox=[i,0,20,30])) for i,d in enumerate(ds)])
            wanted=[ds[2],ds[0]]
            write('candidates.jsonl',[dict(parent_id=b.key(d)[0],row_id=b.key(d)[1]) for d in wanted])
            self.assertEqual(2,b.readout(td/'candidates.jsonl',td,td))
            result=list(b.rows(td/'candidates_readout.jsonl'))
            self.assertEqual([b.key(d) for d in wanted],[b.key(r) for r in result])
            for r,d in zip(result,wanted):
                for k in ('final_text','raw_text_sha256','edits'):self.assertEqual(d[k],r[k])
                self.assertEqual('a'*64,r['crop_sha256']);self.assertIn('crop_bbox',r);self.assertIn('crop_source_image',r)
            write('candidates.jsonl',[dict(parent_id='missing',row_id='a')])
            with self.assertRaises(ValueError):b.readout(td/'candidates.jsonl',td,td)

    def test_output_dir_guard(self):
        with self.assertRaises(ValueError):b.output('/tmp/forbidden',Path('relative'))
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td);root=td/'explicit';root.mkdir()
            escape=root/'escape';escape.symlink_to(td,target_is_directory=True)
            with self.assertRaises(ValueError):b.output(escape/'bad',root)
            self.assertEqual(root/'ok',b.output(root/'ok',root))
        with self.assertRaises(Exception):b.absolute_dir('relative')

    def test_sbatch_and_wrapper_mock_run(self):
        with tempfile.TemporaryDirectory(dir=b.HERE) as td:
            td=Path(td)
            stubs={
                'mkdir':'#!/bin/bash\nexit 0\n',
                'sbatch':'#!/bin/bash\nprintf "SBATCH:%s\\n" "$@"\nwhile [[ "$1" == --* ]]; do shift; done\nbash "$@"\n',
                'srun':'#!/bin/bash\nprintf "SRUN:%s\\n" "$@"\n'}
            for name,source in stubs.items():
                p=td/name;p.write_text(source);p.chmod(0o755)
            env=dict(os.environ,PATH=str(td)+':'+os.environ['PATH'],SLURM_JOB_PARTITION='normal')
            for mode in ('extract','readout'):
                text=(b.HERE/f'{mode}.sbatch').read_text()
                for value in ('#SBATCH --partition=normal','#SBATCH --nodes=1','#SBATCH --time=01:00:00'):self.assertIn(value,text)
                self.assertNotIn('--mem',text);self.assertNotIn('xfer',text)
                self.assertNotIn('#SBATCH --output=',text)
                args=['bash',str(b.HERE/'submit_job.sh'),mode,'/scratch/census','/iopsstor/scratch/test/out']
                if mode=='readout':args+=['/scratch/candidates.jsonl']
                out=subprocess.check_output(args,env=env,cwd=td,text=True)
                self.assertIn(f'SBATCH:--output=/iopsstor/scratch/test/out/{mode}-%j.log',out)
                self.assertIn('SRUN:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/venv_l1/bin/python',out)
                self.assertIn('SRUN:--output-dir\nSRUN:/iopsstor/scratch/test/out',out)
                self.assertIn('SRUN:'+str(b.HERE/'bench02_draw.py'),out)
            bad=subprocess.run(['bash',str(b.HERE/'submit_job.sh'),'extract','/census','relative'],env=env,capture_output=True)
            self.assertNotEqual(0,bad.returncode)

if __name__=='__main__':unittest.main()
