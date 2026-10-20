"""Finish mechanical pack preparation from the verified W2 snapshot. Never runs a reader."""
import subprocess,xml.etree.ElementTree as ET
from build import *
PYTHON=COLLECTOR/'.venv/bin/python'
def run(script,*args):
 result=subprocess.run([str(PYTHON),'-B',str(HERE/script),*args],cwd=REPO)
 if result.returncode:raise RuntimeError(script+' failed: '+str(result.returncode))
def readme(receipt,n):
 strata=receipt['strata'];short=', '.join(k.removeprefix('w2c1_')+'='+str(v['pool']) for k,v in strata.items())
 table='\n'.join('| '+v['source']+' | '+v['primary_class']+' | '+str(v['w2_rows'])+' | '+str(v['pool'])+' | '+str(v['draw'])+' |' for v in strata.values())
 text="""# W2C1b: W2 snapshot stratum packs

Prepared and validated; no readers started and no admission verdicts produced.

Input: `__METHOD__`, at
`~/Projects/collect-v3-data/snapshots/W2_features_20261018_0524.jsonl`.
The complete 219,381-row snapshot is SHA-256 verified before sampling:
`4954a94cc3c051aeb36e367101bc3448233448422bb05834d3276e090de987b4`.
No replay is used. Live run features files are never read; preparation rejects
those reads and network sockets. No live locks or writes are taken.

| Source | Class | W2 rows before filters | Eligible pool | Draw |
|---|---|---:|---:|---:|
__TABLE__

BSB W2 is partial: 298 pages at snapshot time. All eight pools have at least
100 rows; each uniform draw contains exactly 100. Gazette additionally requires
`gazette_stratum == "measured_1986_1990"`; counts before filters include all
Gazette modern_scanned rows, and the eligible pool applies this field gate.

Pools require W2, the specified source/class, candidate_usable true,
screen_merged false, and absence from every registered release exclusion class.
Rotated crops are excluded when height > width with at least four non-space
label characters. SEG screens are being qualified separately under CP7; these
letters and crop_ok checks do not wait for SEG. No new SEG filters are added.

Original crops are copied. Missing crops are regenerated from retained source
rasters only through `collect_v3.storage.ensure_crop`, using exclusively
`~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python`, into this task's
`cache/`, outside the live run. Every source and copied crop matches the
snapshot crop SHA-256; custody is recorded in `keys/crop_custody.json`.

Seed: `w2c1:<source>:<class>`, uniform sampling over rows sorted by id; context
order adds `:order:c1` or `:order:c2`. Eight beds, two disjoint contexts each,
50 bed cards + five approved CAPS1/CAPS1b controls per context. All 10 lead
controls are reused per bed. Fresh opaque ids and public closure are verified.
Keys, truth, pool/draw inventories and custody stay here, outside PACK_ROOT.
PACK_ROOT: `__PACK__`.

`prompts/bsb.md` is copied verbatim from Sol-reading; only its reader-2 template
placeholder is rendered empty for independent one-reader contexts.
Canonical scanner: `tools/scan_rollout.py`, SHA-256 `__SHA__`, invoked directly
without scanner wrappers. Every prepared and executed run receipt records this
hash. Canonical replay helper is unchanged; closure uses the CAPS1 grayscale
and disjoint-context adapter. Manifests live beside the reader directories.

The lead can run `bash __HERE__/launch_all.sh` after reviewing READY.json.
It runs all 16 contexts sequentially and logs to `run.log`. Before every
context, `launchers/limit_probe.sh` must yield exactly one weekly 10080-minute
bucket. Use >=78%, missing or ambiguous readings stop with exit 8; the bed
launcher probes before and after as well. `launch_lines.txt` has the 16 public
launch lines. Preparation and tests never call the real probe or reader.

Reader settings: gpt-6.1-sol, medium, network OFF, web disabled,
apps/plugins/multi-agent OFF. Receipts retain rollout, usage, limit readings,
scanner hash and audit/map return codes. More than one control error flags a
context. Letters and crop_ok are the final Sol dimensions; marks remain pending
Opus for grave-heavy strata. No check scores or admission outcomes are claimed.

Validation: __N__ tests passed, zero skipped. Coverage includes exact pool
filters, eight seeds/order, crop SHA equality, all 16 context closures, scanner
hash/direct invocation, prompt/settings, snapshot SHA/count verification and
rejection of corrupt bindings, and shell stop-rule execution with fake probes
and readers. See `tests.log`, `tests.xml`, `closure.json`, `build_receipt.json`,
`runtime_bindings.json`, and `READY.json`. The real launcher has not been run.

W2C1b: done | strata: 8 | pools: __SHORT__ | contexts: 16 | READY.json written | canonical scanner sha ok | launch_all ready | tests: __N__ passed
"""
 for old,new in {'__METHOD__':receipt['pool_method'],'__TABLE__':table,'__PACK__':str(PACK_ROOT),'__SHA__':CANONICAL,'__HERE__':str(HERE),'__N__':str(n),'__SHORT__':short}.items():text=text.replace(old,new)
 (HERE/'README.md').write_text(text)
def finalize():
 if '--wait' in sys.argv:raise ValueError('--wait replay mode retired; use snapshot')
 if (HERE/'READY.json').exists():raise RuntimeError('Refuse overwrite validated READY.json')
 run('build.py');run('prepare.py');run('closure.py')
 for source,cls in STRATA:
  bed=bedname(source,cls)
  for ctx in ('c1','c2'):
   dump(HERE/'receipts'/bed/(ctx+'.json'),dict(bed=bed,context=ctx,status='prepared; reader not started',canonical_scanner_sha256=CANONICAL,model='gpt-6.1-sol',effort='medium',network='OFF'))
 with (HERE/'tests.log').open('w') as log:
  result=subprocess.run([str(PYTHON),'-B','-m','pytest','-q',str(HERE/'test_w2c1.py'),'--junitxml='+str(HERE/'tests.xml')],cwd=REPO,stdout=log,stderr=subprocess.STDOUT)
 if result.returncode:raise RuntimeError('tests failed; see tests.log')
 suites=ET.parse(HERE/'tests.xml').getroot();n=sum(int(s.attrib.get('tests',0)) for s in suites.findall('testsuite'));assert n>=50
 dump(HERE/'READY.json',dict(status='prepared and validated; readers not started',tests_passed=n,contexts=16,strata=8,snapshot_path=str(SNAPSHOT),snapshot_sha256=SNAPSHOT_SHA,snapshot_rows=SNAPSHOT_ROWS,readers_started=0,canonical_scanner_sha256=CANONICAL,closure_sha256=sha(HERE/'closure.json'),build_receipt_sha256=sha(HERE/'build_receipt.json')))
 readme(json.loads((HERE/'build_receipt.json').read_text()),n);print('W2C1b ready',flush=True)
if __name__=='__main__':
 try:finalize()
 except Exception as exc:dump(HERE/'preparation_failed.json',dict(error=str(exc)));raise
