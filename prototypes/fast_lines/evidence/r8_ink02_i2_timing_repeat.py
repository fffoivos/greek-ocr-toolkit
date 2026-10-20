"""One fixed outlier resolution, declared after primary before repeat clocks."""
import json,sys
from pathlib import Path
from . import r8_ink02 as runner
from .r8_ink02_i2 import O,I,dump
c=json.loads((I/'INK02_COHORT.json').read_text());raw=json.loads((O/'TIMING_RAW.json').read_text());selected=set()
for page in {r['page'] for r in raw}:
 rs=[r for r in raw if r['page']==page]
 if all(r['arms']['C']['stages']['ink_s']>r['arms']['B']['stages']['ink_s'] for r in rs) or all(r['arms']['C']['timing']['correction_s']>r['arms']['B']['timing']['correction_s'] for r in rs):selected.add(page)
controls=[r['page'] for r in c['pages'] if ('0ce9' in r['page'] or '93f8' in r['page'] or ('8314' in r['page'] and 'same-book-zero-atlas' in r['roles']))]
selected.update(controls);assert len(selected)==8
plan=dict(rule='all four primary deltas positive in ink or correction; include0ce9/93f8 and8314 same-book atlas0',pages=sorted(selected),primary_sha256=runner.sha(O/'TIMING_RAW.json'),repetitions_per_order=2,orders=['BC','CB'],later_repeats_authorized=False,detector_guard_fraction=.05,source=runner.sources(runner.ROOT),purpose='investigate repeatability, not replace primary or rerun until pass')
dump(O/'TIMING_REPEAT_PLAN.json',plan);c['pages']=[r for r in c['pages'] if r['page'] in selected];runner.OUT=O/'timing_repeat';runner.load=lambda:c
runner.timing(Path(sys.argv[1]))
