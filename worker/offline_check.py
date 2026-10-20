#!/usr/bin/env python3
"""All collector tests and T4b parity in a fresh, network-denied workspace."""
import os,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from collect_v3.common import read_json,write_json,sha
from collect_v3.offline import no_network
from worker.runtime import ROOT

def main():
    fixtures=Path(os.environ.get('COLLECT_V3_FIXTURE_ROOT',ROOT/'worker/fixtures')).resolve()
    from collect_v3.portable import verify
    verify(fixtures)
    os.environ['COLLECT_V3_FIXTURE_ROOT']=str(fixtures)
    os.environ['PYTHONDONTWRITEBYTECODE']='1';os.environ['OMP_THREAD_LIMIT']='1';os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    validation=ROOT/'worker/validation';validation.mkdir(parents=True,exist_ok=True)
    out=Path(tempfile.mkdtemp(prefix='check-',dir=validation))
    from worker.prepare import prepare
    prepare(out)
    def tests_runner(replay_root):
        env={**os.environ,'COLLECT_V3_TEST_OUTPUT':str(out/'tests'),'PYTHONPATH':str(ROOT),
             'COLLECT_V3_REPLAY_ROOT':str(replay_root)}
        # The subprocess entrypoint blocks sockets and DNS before pytest is imported.
        cmd=[sys.executable,'-m','worker.test_offline',str(ROOT/'collect_v3/tests')]
        with (out/'tests.log').open('w') as log:
            result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
        if result.returncode:raise RuntimeError('offline tests failed; log: '+str(out/'tests.log'))
    from collect_v3.verify_offline import verify as dry_run
    with no_network():
        proof=dry_run(ROOT.parent,out,out/'replay',out/'tests',tests_runner=tests_runner)
    summary=dict(status='ok',tests=proof['tests'],parity=proof['parity'],network=False,provider_calls=0,actual_spend_usd=0,validation_root=str(out),fixture_manifest_sha256=sha(ROOT/'worker/fixture_manifest.json'))
    write_json(validation/'latest.json',summary)
    print(f"offline tests={proof['tests']['passed']} parity={proof['parity']['status']} comparisons={proof['parity']['field_comparisons']} spend=0")
    return 0

if __name__=='__main__':sys.exit(main())
