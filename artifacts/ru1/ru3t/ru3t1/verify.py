"""Offline before/after proof; never calls a reader, probe, or finalizer on production."""
import contextlib, difflib, hashlib, importlib.util, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'scripts/secondary'),str(ROOT/'tests'),str(ROOT/'src'),str(ROOT)]
import ru2t, ru3t, ru2t_coverage, ru3t_driver
spec=importlib.util.spec_from_file_location('bound_coverage',OUT/'ru2t_coverage.bound.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
assert hashlib.sha256((OUT/'ru2t_coverage.bound.py').read_bytes()).hexdigest()=='52456823837e636f8d2f440ccd095352413435d111231f44c2923e6b1f060730'
def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
if sys.argv[1]=='tests':
    results={}
    for label,fn in [('before',old.coverage),('after',ru2t_coverage.coverage)]:
        ru2t.coverage=ru3t.coverage=fn
        suite=unittest.TestLoader().loadTestsFromNames(['test_ru2t','test_ru3t'])
        with (OUT/f'tests_{label}.txt').open('w') as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
        results[label]=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),ok=result.wasSuccessful())
    dump('tests.json',results)
    print(json.dumps(results));assert all(r['ok'] for r in results.values())
elif sys.argv[1]=='contexts':
    info=json.loads((ru3t.ART/'build.json').read_text());pack=Path(info['pack']);summary={}
    for ctx,r in ru3t_driver.plan(info):
        stem=ru3t.reader_stem(ctx,r);runpath=ru3t.ART/f'answers/{stem}.run.json'
        if not runpath.exists():continue
        run=json.loads(runpath.read_text());assert run['rc']==0
        rollout=Path(run['rollout']);rd=pack/ctx/r
        scan=ru3t.scan_rollout.inspect(rollout,rd)
        dump(stem+'.scan.json',scan)
        items=list(ru3t.rows(rd/'items.jsonl'))
        a=old.coverage(scan,rollout,rd,items);b=ru2t_coverage.coverage(scan,rollout,rd,items)
        dump(stem+'.before.json',a);dump(stem+'.after.json',b)
        assert a==b,(ctx,r)
        summary[ctx+'/'+r]=dict(identical=True,scan_ok=scan['ok'],rollout_sha256=ru3t.sha(rollout),run_sha256=ru3t.sha(runpath),items_sha256=ru3t.sha(rd/'items.jsonl'),**{k:b[k] for k in ['direct','derived','unviewed','assigned_crops']},coverage_sha256=ru3t.sha(OUT/(stem+'.after.json')))
        print(ctx+'/'+r,summary[ctx+'/'+r],flush=True)
    assert len(summary)==14
    dump('coverage_proof.json',summary)
