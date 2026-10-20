#!/usr/bin/env python3
"""Bounded local synthetic benchmark, no production processing."""
import json
import resource
import tempfile
import time
from pathlib import Path
from test_release_v3 import Fixture
import build_release_v3 as b
with tempfile.TemporaryDirectory() as d:
    f=Fixture(d,n=1500)
    total=sum((f.root/n).stat().st_size for n in ('admitted_train','admission_records'))
    start=time.perf_counter();r=f.run();elapsed=time.perf_counter()-start
    result=dict(synthetic=True,input_bytes=total,rows=len(f.rows),seconds=elapsed,bytes_per_second=total/elapsed,
                maxrss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,platform='macOS arm64; maxrss bytes',
                production_input_bytes=7870677512+10412166460,large_input_hash_passes=2,
                note='1500 padded 20KB-evidence rows plus five edge cases; includes image hashing, output writes and input rehash; no production data transformed')
    b.write_json(Path(__file__).with_name('THROUGHPUT.json'),result)
    print(json.dumps(result,indent=2))
