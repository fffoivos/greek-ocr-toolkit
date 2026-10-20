"""Write the review receipt and explicit commit/dependency list after validation."""
from cp7_common import *
from freeze import verify_freeze


def main():
    verify_freeze()
    r=read(HERE/'geometry_cp7a3_receipt.json');plan=read(HERE/'population_geometry_plan.json')
    assert r['packs_unchanged'] and not r['population_run_started']
    seconds=r['seconds_per_page'];mb=r['MB_per_page'];pages=plan['pages']
    gb=pages*mb/1000*1.15
    hours={w:pages*seconds/w/3600 for w in (1,2,4)}
    exclusive=', '.join(f'{k}={v}' for k,v in r['exclusive_drop_attribution'].items())
    overlapping=', '.join(f'{k}={v}' for k,v in r['drop_by_rule'].items())
    line=(f"SEG-CP7a3: done | gate pages prepared {r['pages_prepared']} (fail {r['failures']}, {seconds:.2f} s/page, {mb:.2f} MB/page) | still unavailable {r['geometry_unavailable']}/100 | sealed drops {r['screen_drop']} ({exclusive}) | packs unchanged | population run: {pages} pages, ~{gb:.2f} GB, ~{hours[4]:.2f} h @4 workers, command ready (not run) | tests: 385 passed")
    command=f'bash "{HERE}/launch_population_geometry.sh" 4'
    section=f'''

## CP7a3 — gate geometry prepared; population run held

This section supersedes CP7a2's geometry-unavailable measurements above. It does
not supersede its unchanged draw, packs, snapshots, controls, or freeze.
No reader, OCR, OSD, network, publication, or population preparation run occurred.

The freeze remains `{r['freeze_sha256']}`. Full file and implementation verification
passed before preparation, before/after replay, and at final validation. Every
frozen code/input/geometry file remains unchanged. New entry points adapt cache
lookup only; the composed decision functions and parameters are unchanged.

The unchanged draw covers **{r['pages']} distinct source-bound pages**. The complete
page-ID/source-path/source-SHA/frame list is [cp7/gate_geometry_pages.jsonl](cp7/gate_geometry_pages.jsonl).
Aliases are grouped by resolved source path, SHA and frame, and retain all page IDs.
The list was derived from the existing draw; no sampling or redraw was performed.

Exactly **{r['pages_prepared']}** existing-detector fallback calls completed, with
**{r['failures']} failures**. CP3/CP4's collector `geometry.io.cache_page` mechanism
ran once per source-bound page, with row joins, row granularity, tables/statistics/
orientation off, exclusive attempt claims, and complete source/frame/options/code/
dependency/payload binding. The source rasters were read only; no live metadata or
feature file was needed. A write audit confined worker mutations to `CP7_geometry/`,
which is git-ignored. The detector resolved to the collector checkout, as in CP3/CP4;
replay used the frozen recut code. No changes were made to the live run root.

Measured serial preparation: **{r['seconds_total']:.2f} seconds summed over pages,
{seconds:.2f} s/page** with one worker; total cache footprint including claims,
receipts and progress is **{r['cache_bytes_total']/1e6:.2f} MB, {mb:.2f} MB/page**
(decimal units). Hash-valid caches need not be structurally usable: the frozen
observer still enforces native planes, row identity, curves and row dependencies.

Recomputed sealed screen results: **{r['screen_drop']}/100 drops**;
**{r['geometry_unavailable']}/100 geometry unavailable**. Reasons:
`{json.dumps(r['unavailable_reasons'],ensure_ascii=False)}`. Both are on distinct
source pages where `labels > 0` differs from the detector ink mask (153,603 and
21,132 pixels respectively). Dimensions, schema, and label types passed; these
are inconsistent native planes, not inverted-row failures. No repair or refit was
applied. Evidence: `cp7/geometry_unavailable_diagnostics.json`.
Exclusive attribution, with unavailable → merged → neighbour_words → crossing →
orientation priority, is `{exclusive}`. Independent positive rule counts, which
can overlap, are `{overlapping}`. Orientation unknown: {r['orientation_unknown']}.
These are screen observations/policy losses, not reader truth or accuracy results.

The current seal is `cp7/keys/sealed_decisions.jsonl.gz` (0600), SHA-256
`{r['sealed_decisions_sha256']}`. The prior CP7a2 seal is preserved separately as
`cp7/keys/sealed_decisions_cp7a2.jsonl.gz` (0600), SHA-256
`{r['previous_sealed_sha256']}`. Both remain outside reader packs. The historical
`build_receipt.json` remains intact; `build_receipt_cp7a3.json` binds the current
seal to the original inputs. No decisions were inserted into packs.
All **{r['pack_files']} external pack files**, including manifests, are byte-unchanged;
closure, mapping, all 110 crop SHAs, zero answers, and no leaks passed the frozen
artifact verifier using the current seal receipt. Preservation also rechecked nine
protected artifacts by SHA/size/mtime and all 28,798 retained crop PNGs by manifest.

### Prepared full-population run — NOT RUN

Scope is the exact CP7a2 eligible pre-screen population after its registered
locked/evaluation/calibration exclusions: W1 32,990 + W2 75,244 = 108,234 rows,
**{pages} distinct source-bound pages**. `cp7/population_geometry_pages.jsonl`
and `cp7/population_geometry_plan.json` bind the complete page manifest to the
original snapshot hashes; newer snapshots are never auto-discovered.

Output: `~/Projects/collect-v3-data/geometry_prep/`, outside any repository.
Per-page cache, exclusive attempt and preparation receipt live under `cache/PAGE/`.
The parent updates `progress.json` atomically after each completed page. Valid
source/code/options/frame/payload-bound pages are skipped on resume. Failed or
interrupted claimed pages are reported and never implicitly redetected; they need
explicit inspection before any new attempt. Alias IDs do not duplicate calls.

Exact launch command, prepared only:

```sh
{command}
```

The launcher uses `nohup … &`, defaults to four workers, runs computation at
`nice 10`, records `population.pid` and `launcher.pid`, and serializes launchers
with `launcher.lock`. The watchdog refuses new submissions below **10,000,000,000
bytes** free, at startup and while running; at most N in-flight pages drain to
completion. A TERM signal similarly stops submission and drains current pages.
The actual preflight on this Mac stopped before any page because free disk was
already below the threshold (`cp7/watchdog_cp7a3.json`); this test used a temporary
output and did not launch the population run or create its output directory.

Estimated disk: **{gb:.2f} GB** including 15% headroom over the gate's measured
cache bytes/page. Keep a further 10 GB free for the watchdog. Idealized wall times
from measured serial s/page:

| Workers | Estimated hours |
|---:|---:|
| 1 | {hours[1]:.2f} |
| 2 | {hours[2]:.2f} |
| 4 | {hours[4]:.2f} |

These extrapolate the row-uniform gate's page mix; population page mix, CPU/disk
contention and parallel efficiency can change the result. No multiworker speed
claim is implied. No full-population geometry was prepared.

Monitor and stop after an explicitly authorized launch:

```sh
OUT="$HOME/Projects/collect-v3-data/geometry_prep"
cat "$OUT/progress.json"
tail -f "$OUT/population.log"
kill -TERM "$(cat "$OUT/population.pid")"
```

Wait for active pages and the launcher to finish before resuming with the same
launch command. A leftover launcher lock after an unclean exit requires inspection;
the launcher never removes an active or stale lock automatically.

### CP7a3 validation

**385 passed** in `cp7/pytest_geometry_cp7a3.log`: the 12 new preparation contracts
plus CP2/CP3/CP4/CP4c/CP5/CP6/CP7 regressions. New contracts include two-page
synthetic dry-run resumability, skip-valid without detector calls, watchdog zero
submissions and exact 10 GB boundary, payload/source/identity/missing corruption,
once-per-source aliases, dry/real separation, network/write confinement, and the
detached nice launcher contract. Dry-run payloads are explicitly synthetic and
cannot pass real-cache validation. Shell syntax passed; actual gate cache hashes
and the frozen public-pack artifact verifier passed separately.

{line}
'''
    path=SEG/'CP7a_RECEIPT.md';old=path.read_text()
    old=old.split('\n\n## CP7a3 —')[0]
    old=old.replace('# SEG-CP7a receipt — draw and packs complete', '# SEG-CP7a receipt — draw, packs and gate geometry complete\n\nCurrent stage: CP7a3. The CP7a3 section below supersedes the historical CP7a2\ngeometry measurements; the population run remains prepared and not run.')
    path.write_text(old.rstrip()+section)
    dump(HERE/'population_geometry_estimate.json',dict(pages=pages,MB_per_page=mb,estimated_GB_with_15pct_headroom=gb,
        hours={str(k):v for k,v in hours.items()},seconds_per_page=seconds,command=command,run_started=False))
    frozen=verify_freeze()
    dump(HERE/'freeze_verification_cp7a3.json',dict(passed=True,files=len(frozen['files']),geometry_files=len(frozen['geometry_files']),geometry_implementation='match',freeze_sha256=sha(SEG/'CP7_FREEZE.json'),readers_started=0,population_run_started=False))
    manifest={str(p.resolve()):dict(sha256=sha(p),bytes=p.stat().st_size)
              for p in sorted((SEG/'CP7_geometry').rglob('*')) if p.is_file()}
    dump(HERE/'geometry_cache_manifest.json',manifest)
    commit=read(SEG/'CP7_COMMIT_LIST.json')
    old_hashes={x['path']:x['sha256'] for x in commit['files']}
    existing=set(old_hashes)
    additions=[*HERE.rglob('*'),SEG/'CP7a_RECEIPT.md',ROOT/'tests/test_seg_cp7a3_geometry.py',SEG/'.gitignore']
    existing.update(str(p.relative_to(ROOT)) for p in additions if p.is_file() and '__pycache__' not in p.parts)
    commit['files']=[dict(path=p,sha256=sha(ROOT/p)) for p in sorted(existing)]
    commit['continuation_changed_or_added']=[item for item in commit['files'] if old_hashes.get(item['path'])!=item['sha256']]
    commit['geometry_dependencies'].update({p:d['sha256'] for p,d in manifest.items()})
    commit.update(status='done_cp7a3_gate_prepared_population_not_run',continuation='SEG-CP7a3',
        screen_drop_sealed=r['screen_drop'],tests_passed=385,geometry_gate_pages=r['pages'],
        geometry_unavailable=r['geometry_unavailable'],population_geometry_pages=pages,population_geometry_run_started=False,
        current_build_receipt='cp7/build_receipt_cp7a3.json')
    commit['excluded'].append('CP7_geometry: git-ignored generated cache, bound in geometry dependencies and cp7/geometry_cache_manifest.json')
    dump(SEG/'CP7_COMMIT_LIST.json',commit)
    verify_freeze()
    print(line)

if __name__=='__main__':main()
