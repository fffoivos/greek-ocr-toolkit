"""Offline 200-real-row batch harness. srun and native I/O are test doubles.

Real shell scripts, config preparation, row adapters, correction import/validation,
composition, admission, durable publication, and output-root behavior execute.
Reader outcomes are explicitly synthetic no-change fixtures, not qualifications.
"""
from copy import deepcopy
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

D = Path(__file__).resolve().parent
PROJECTS = D/'package/projects'
sys.path.insert(0, str(PROJECTS/'greek-ocr-toolkit-pipe032'))
from greekocr.harvest import line_pipeline_census as census
from greekocr.harvest import line_pipeline_census04 as c4
from greekocr.harvest.line_pipeline import canonical, digest, identity


def jsonl(path, rows):
    path.write_text(''.join(canonical(r)+'\n' for r in rows))
    return str(path)


def build(root):
    records = [json.loads(s) for s in gzip.open(D/'mock_slice_inputs.jsonl.gz', 'rt')]
    assert len(records) == 200
    versions_path = PROJECTS/'greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json'
    versions = json.loads(versions_path.read_text())['tools']
    groups, metadata, observations, frozen = {}, dict(books={}), {}, []
    fixture_groups = {}
    for saved in records:
        r = deepcopy(saved['row'])
        original_parent=r['parent_id']
        index=fixture_groups.get(original_parent,0);fixture_groups[original_parent]=index+1
        # Mock-only parent groups preserve all 200 real raw rows under smoke's
        # unchanged 40-row cap. Production parent config is never changed.
        if index>=40: r['parent_id']=original_parent+'-mock-shard-'+str(index//40)
        if saved['cohort'] == 'calibration':
            r.update(split='train', source='bsb_poly1850')
            r['book_id'] = 'calibration:'+r['id'].split('-p')[0]
            r['page_id'] = r['id'].rsplit('-l', 1)[0]
            r['edition_id'] = 'fixture:'+r['book_id']
            fmt = 'canonical'
        elif r['parent_id'].startswith('collection-v2'):
            r['label'] = r['raw_text']
            r['book_id'] = r['doc']
            fmt = 'collection-v2'
        else:
            r['old_label'] = r['raw_text']
            r['book_id'] = r['page_id'].rsplit('--s', 1)[0]
            fmt = 'collect-v3-features'
        metadata['books'][r['book_id']] = dict(edition_id='fixture:'+r['book_id'], provenance='mock declaration; not a release',
            languages=['Greek', 'Latin', 'Russian'], scripts=['greek', 'latin', 'cyrillic'],
            orthography='polytonic', orthographies=dict(cyrillic='historical_russian'), latin_policy='allowed')
        groups.setdefault((r['parent_id'], fmt), []).append(r)
        answer = deepcopy(saved['segmentation'])
        answer['binding'] = identity(r)
        observations[canonical([r['parent_id'], r['id']])] = answer
        old = deepcopy(saved['frozen_05']); old['binding'] = identity(r)
        frozen.append(dict(binding=identity(r), raw_text_sha256=digest(r['raw_text']), stages=[dict(stage='segmentation', result=old)]))
    parents, corrections, assignments = [], [], []
    source_rows = {}
    for (parent_id, fmt), rows in groups.items():
        path = root/(parent_id+'.jsonl')
        parent = dict(id=parent_id, format=fmt, path=jsonl(path, rows), rows=len(rows), sha256=census.file_sha(path))
        if fmt == 'collection-v2': parent['split'] = parent_id.rsplit('-',1)[1]
        parents.append(parent)
        source_rows[parent_id] = rows
        for r in rows:
            row = census.canonicalize(r, parent, metadata)
            if fmt == 'collect-v3-features':
                # One row intentionally absent: it must keep the unassigned hold.
                if not assignments or len(assignments) != 3:
                    book_hash = int(digest(row['book_id'])[:8], 16)
                    split = 'dev' if book_hash % 7 == 0 else 'test' if book_hash % 7 == 1 else 'train'
                    assignments.append(dict(parent_id=parent_id, row_id=r['id'], edition_id=row['edition_id'], split=split))
                else:
                    # Use a sentinel so exactly one row, not the remaining cohort, is omitted.
                    assignments.append(dict(_omit=True))
            for tool in ('polytonic', 'cyrillic', 'numerics', 'content_repair'):
                record = dict(tool=tool, tool_version=versions[tool]['version'], tool_digest=versions[tool]['digest'],
                    binding=identity(row), raw_text_sha256=digest(row['raw_text']), status='verified_no_change', edits=[],
                    evidence=dict(offline_mock=True, source='synthetic saved reader result; no accuracy claim'))
                corrections.append((parent_id, tool, record))
    assignments = [r for r in assignments if not r.get('_omit')]
    releases = []
    for parent in parents:
        for tool in ('polytonic', 'cyrillic', 'numerics', 'content_repair'):
            path = root/(parent['id']+'-'+tool+'.jsonl')
            jsonl(path, [r for p, t, r in corrections if p == parent['id'] and t == tool])
            releases.append(dict(tool=tool, parent_id=parent['id'], path=str(path), sha256=census.file_sha(path),
                format='line-tool-result-v1', status='released', parent_manifest_sha256=parent['sha256']))
    meta = root/'metadata.json'; meta.write_text(canonical(metadata))
    old = root/'frozen05.jsonl'; jsonl(old, frozen)
    split = root/'split.jsonl'; jsonl(split, assignments)
    jsonl(root/'observations.jsonl', [dict(key=k, result=v) for k, v in observations.items()])
    config = dict(routes_out_of_scope=['polytonic'], component_roots={p.name:str(p) for p in PROJECTS.iterdir() if p.is_dir()}, versions=str(versions_path), codec=str(PROJECTS/'greek-ocr-toolkit-pipe032/greekocr/_vendor/codec/v2.json'), metadata=str(meta), parents=parents, corrections=releases,
        final_policy={}, native_workers=2, native_prefetch_factor=2,
        frozen_05=dict(path=str(old), sha256=census.file_sha(old)))
    path = root/'source_config.json'; path.write_text(canonical(config))
    return path, split


def native_factory():
    records = {r['key']: r['result'] for r in map(json.loads, Path(os.environ['MOCK_OBSERVATIONS']).read_text().splitlines())}
    def observe(row):
        saved = deepcopy(records[canonical([row['parent_id'], row['id']])])
        assert saved['raw_text_sha256'] == digest(row['raw_text'])
        assert saved['binding']['crop_sha256'] == row['crop_sha256']
        saved['binding'] = identity(row)
        return saved
    return observe


def execute_mock_native():
    # Same CLI parser, run implementation and batch argv; only native I/O is mocked.
    c4.main(segmenter_factory=native_factory)


def main():
    root = D/'mock_batch'
    if root.exists():
        shutil.rmtree(root)
    root.mkdir()
    source, split = build(root)
    spool = root/'slurm-spool'; spool.mkdir()
    for script in (D/'jobs').glob('*.sbatch'): shutil.copyfile(script, spool/script.name)
    bin_dir = root/'bin'; bin_dir.mkdir()
    srun = bin_dir/'srun'
    srun.write_text('''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
args=sys.argv[1:]
while args and args[0].startswith('-'):
    key=args.pop(0)
    if key=='-A':args.pop(0)
with open(os.environ['MOCK_SRUN_LOG'],'a') as f:f.write(json.dumps(dict(cwd=os.getcwd(),argv=args))+'\\n')
if '-m' in args and args[args.index('-m')+1]=='greekocr.harvest.line_pipeline_census04':
    i=args.index('-m');args=args[:i]+[os.environ['MOCK_BATCH_SCRIPT'],'--native']+args[i+2:]
os.execvpe(args[0],args,os.environ)
''')
    srun.chmod(0o755)
    env = dict(os.environ, PATH=str(bin_dir)+os.pathsep+os.environ['PATH'],
        W=str(root/'W'), CENSUS05_BUNDLE=str(D), CENSUS05_PYTHON=sys.executable, CENSUS05_CONFIG=str(source),
        SLURM_JOB_PARTITION='normal', CENSUS05_EXPECT_ROWS='200', MOCK_SRUN_LOG=str(root/'srun.jsonl'),
        MOCK_OBSERVATIONS=str(root/'observations.jsonl'), MOCK_BATCH_SCRIPT=str(Path(__file__).resolve()))
    results = {}
    for smoke in ('1','0'):
        for mode in ('mode-i','mode-ii'):
            tag=('smoke' if smoke=='1' else 'full')+'-'+mode
            current=dict(env,E4_SMOKE=smoke,CENSUS05_ATTEMPT=tag)
            if mode=='mode-ii': current.update(CENSUS05_SPLIT_FILE=str(split),CENSUS05_SPLIT_SHA256=census.file_sha(split))
            with (root/(tag+'.log')).open('w') as log:
                proc=subprocess.run(['bash',str(spool/'census.sbatch')],cwd='/private/tmp',env=current,stdout=log,stderr=subprocess.STDOUT)
            if smoke=='0' and mode=='mode-i':
                assert proc.returncode!=0
                assert 'full mode requires' in (root/(tag+'.log')).read_text()
                results[tag]=dict(refused=True,exit_code=proc.returncode);continue
            assert proc.returncode==0,(tag,proc.returncode)
            out=root/'W/census_05_20261020/attempts'/tag
            ds=[json.loads(line) for line in (out/'decisions.jsonl').read_text().splitlines()]
            assert len(ds)==200 and not any(d['disposition']=='INFRA_ERROR' for d in ds)
            assert all(d['diagnostics']['frozen_05']['available'] for d in ds)
            result=dict(rows=len(ds),complete=json.loads((out/'summary.json').read_text())['complete'],dispositions={k:sum(d['disposition']==k for d in ds) for k in ('ADMIT','DROP','HOLD')},output_root=str(out),actual_batch_script=True,slurm_spooled_script=True,unrelated_submit_cwd=True)
            with (root/(tag+'-readout.log')).open('w') as log:
                proc=subprocess.run(['bash',str(spool/'readout.sbatch')],cwd='/private/tmp',env=current,stdout=log,stderr=subprocess.STDOUT)
            assert proc.returncode==0,(tag,'readout',proc.returncode)
            report=json.loads(Path(str(out)+'.readout/readout.json').read_text())
            assert all(v['status']=='PASS' for v in report['invariants'].values())
            result.update(readout_last_line=Path(str(out)+'.readout/READOUT.md').read_text().strip().splitlines()[-1],readout_invariants=report['invariants'])
            results[tag]=result
    for kind in ('regression','parity'):
        current=dict(env,E4_SMOKE='1',CENSUS05_ATTEMPT='validation',CENSUS05_PREDICTOR=str(D.parents[2].parent/'greek-ocr-toolkit-main-next/scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'))
        with (root/(kind+'.log')).open('w') as log:
            subprocess.run(['bash',str(spool/(kind+'.sbatch'))],cwd='/private/tmp',env=current,stdout=log,stderr=subprocess.STDOUT,check=True)
    results['validation_jobs']=['regression','parity']
    calls = [json.loads(s) for s in (root/'srun.jsonl').read_text().splitlines()]
    assert all('/census_05_20261020/attempts/' in r['cwd'] or '/package/projects/greek-ocr-toolkit-pipe032' in r['cwd'] or r['cwd']=='/private/tmp' for r in calls)
    results['srun_calls'] = len(calls)
    results['native_mock'] = 'attempt-3 hash-verified native 0.13 measurements; corrections synthetic no-change fixtures; no reader'
    (D/'mock_batch_results.json').write_text(json.dumps(results, indent=2)+'\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--native':
        sys.argv.pop(1);execute_mock_native()
    else:
        main()
