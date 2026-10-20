"""Wait for complete native observations, then gate, publish, stage and verify."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from prepare_w1 import BASE, ROOT, offline
sys.addaudithook(offline)
PYTHON=Path.home()/'Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python'
assert os.path.samefile(sys.executable,PYTHON)


def call(*args,log=None):
    if log:
        with (BASE/log).open('w') as stream:
            subprocess.run([str(PYTHON),*map(str,args)],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
    else:
        subprocess.run([str(PYTHON),*map(str,args)],cwd=ROOT,check=True)


def main():
    before=json.loads((BASE/'w1_before.json').read_text());groups={}
    for line in Path(before['receipt']['input_path']).read_text().splitlines():
        r=json.loads(line);groups.setdefault(r['page_id'],[]).append(r)
    started=time.monotonic()
    while True:
        call(BASE/'merge_cache.py')
        complete=0
        for page,records in groups.items():
            path=BASE/'cache'/f'{page}.json'
            if path.exists():
                measurements=json.loads(path.read_text())['measurements']
                complete+=all(measurements.get(r['row_id'],{}).get('crop_box')==r['crop_bbox'] for r in records)
        print(f'W1 native measurements complete: {complete}/{len(groups)} pages',flush=True)
        if complete==len(groups):break
        assert time.monotonic()-started<14400, 'measurement wait exceeded four hours; no publication'
        time.sleep(30)
    call(BASE/'reissue.py',log='reissue.log')
    call(BASE.parent/'stage_crops.py','--admitted',BASE.parent/'w1_originals_v3_admitted.jsonl',
         '--features',Path.home()/'Projects/collect-v3-data/run/W1/features.jsonl',
         '--out',BASE.parent/'crops',log='stage.log')
    call(BASE/'verify.py',log='verify.log')
    tests=['tests/test_neighbour_words.py','tests/test_harvest_admission.py','tests/test_adm5b_schema.py',
           'tests/test_adm5c_variants.py','tests/test_round1_admission_outputs.py',
           'docs/harvest/recut_v1/masking/tests/test_foreign_ink.py',
           'docs/harvest/collect_v3_admission/test_stage_crops.py']
    call('-m','pytest','-q',*tests,log='tests_final.log')
    log=(BASE/'tests_final.log').read_text();count=int(re.search(r'(\d+) passed',log).group(1))
    (BASE/'TESTS.json').write_text(json.dumps(dict(passed=count,interpreter=str(PYTHON),tests=tests),indent=2)+'\n')
    call(BASE/'report.py')
    print(f'NW1b publication, staging, physical verification and {count} tests complete',flush=True)


if __name__=='__main__':main()
