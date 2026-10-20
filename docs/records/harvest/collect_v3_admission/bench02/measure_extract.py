#!/usr/bin/env python3
"""Local 4,000-row sample only; hashes and both complete streams included in timing."""
import json
from pathlib import Path
import platform
import sys
import time
import bench02_draw as b

sample=Path.home()/'Projects/collect-v3-data/census02_sample'
decisions=[sample/f'decisions_{w}_2000.jsonl.gz' for w in ('W1','W2')]
diagnostics=[sample/f'evaluation_diagnostics_{w}_2000.jsonl.gz' for w in ('W1','W2')]
out=b.HERE/'dryrun_census02/tags.jsonl.gz'
start=time.perf_counter()
receipt=b.extract(decisions,diagnostics,out)
seconds=time.perf_counter()-start
n=receipt['decisions']; rate=(n+receipt['diagnostics'])/seconds
bytes_per_row=out.stat().st_size/n
projection=1186000/rate
result=dict(interpreter=sys.executable,version=platform.python_version(),seconds=seconds,
    decisions=n,diagnostics=receipt['diagnostics'],input_bytes=sum(p.stat().st_size for p in decisions+diagnostics),
    rate_input_rows_per_second=rate,rate_decision_diagnostic_pairs_per_second=n/seconds,
    projected_full_seconds=projection,time_limit_minutes=__import__('math').ceil(3*projection/900)*15,
    compressed_bytes=out.stat().st_size,compressed_bytes_per_row=bytes_per_row,
    projected_320479_MB=bytes_per_row*320479/1e6,
    caveat='Local compressed census02 sample, warm-cache possible; not measured Clariden throughput. Full inputs approx 9+7 GB; compression and storage can differ.')
assert result['time_limit_minutes']<=120
b.dump(b.HERE/'BENCH02E_measurements.json',result)
print(json.dumps(result,indent=2))
