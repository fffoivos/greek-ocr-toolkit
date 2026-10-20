"""Record SEG10 scope, exact diffs, artifact fingerprints and review report."""
from pathlib import Path
from datetime import datetime, timezone
import difflib, hashlib, importlib.util, json, os, re, shlex, subprocess

ROOT=Path(__file__).resolve().parents[5];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
dump=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT,env=env,text=True)


def run():
    s=read(OUT/'summary.json');init=read(OUT/'initial.json');view=Path(read(OUT/'view_receipt.json')['view'])
    current_head=git('rev-parse','HEAD').strip()
    coordinator_changes=git('diff','--name-only',init['head']+'..'+current_head).splitlines()
    assert not any(p.startswith(('greekocr/','scripts/','tests/','docs/records/harvest/seg_steps/')) for p in coordinator_changes)
    assert git('branch','--show-current').strip()=='cleanup/20261019'
    assert 'CLEAN4T' in git('log','--format=%s',init['head'])
    protected={}
    for rel,before in init['protected'].items():
        p=ROOT/rel
        now={str(q.relative_to(p)):[q.stat().st_size,q.stat().st_mtime_ns,q.stat().st_ctime_ns] for q in p.rglob('*') if q.is_file()} if p.exists() else None
        assert now==before,rel
        protected[rel]=dict(unchanged=True,files=None if before is None else len(before))
    vp=ROOT/'docs/harvest/line_pipeline/tool_versions.json';v=read(vp)
    spec=importlib.util.spec_from_file_location('seg10_build',ROOT/'scripts/harvest/build_filter_versions.py')
    build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
    assert build.build()==v
    for name,t in v['tools'].items():
        assert t['iteration_count']==len(t['documented_iterations'])
        if name=='segmentation':assert t['iteration_count']==8+int(t['version'].split('-s')[1])
        else:assert t['version']=='0.'+str(t['iteration_count'])
        for key,h in t['components'].items():assert sha(ROOT.parent/key)==h,key
        assert hashlib.sha256(json.dumps(t['components'],sort_keys=True,separators=(',',':')).encode()).hexdigest()==t['digest']
    assert s['replay']['measurement_differences']==0 and s['acceptance']['differences']==0
    unchanged_assets=['greekocr/harvest/filtering_assets/service.mjs','greekocr/harvest/filtering_assets/crop-tools.py','greekocr/harvest/line_pipeline_native.py','greekocr/glyphs/components.py','greekocr/harvest/filtering_assets/font-models.json']
    for rel in unchanged_assets:assert subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT,env=env)==(ROOT/rel).read_bytes()
    names=['test_content_gate.py','test_line_pipeline.py','test_seg_gate.py','test_seg_deskew.py','test_seg_curve.py','test_seg_small.py','test_integration_fixes.py']
    test_hashes={}
    for name in names:
        assert (ROOT/'tests'/name).read_bytes()==(view/'tests'/name).read_bytes(),name
        test_hashes['tests/'+name]=sha(ROOT/'tests'/name)
    command=[str(ROOT.parent/'greek-ocr-toolkit-sol-recut/.venv/bin/python'),'-B','-m','pytest','-q','-p','no:cacheprovider',*[str(view/'tests'/n) for n in names]]
    (OUT/'tests_command.txt').write_text('PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. '+shlex.join(command)+'\n')
    assert (OUT/'tests.log').read_text().splitlines()[-1]==s['tests']['verbatim']
    dump(OUT/'tests_receipt.json',dict(command=command,cwd=str(ROOT),env=dict(PYTHONPATH='.',PYTHONDONTWRITEBYTECODE='1'),
        interpreter=str(ROOT.parent/'greek-ocr-toolkit-sol-recut/.venv/bin/python'),tested_files_sha256=test_hashes,
        tested_copies_identical=True,passed=248,failed=0,verbatim=s['tests']['verbatim'],
        initial_run='tests_initial.log: 9 failed, 239 passed; missing view fixtures (4), old version/hash expectations (3), new fixture construction error (2); all corrected without changing tool rules'))
    allowed=['docs/B_training_data/c_pipeline/README.md','docs/harvest/line_pipeline/tool_versions.json',
        'greekocr/harvest/filtering_assets/segmentation-policy.js','greekocr/harvest/line_pipeline.py',
        'greekocr/harvest/line_pipeline_census.py','scripts/harvest/build_filter_versions.py',
        'tests/test_content_gate.py','tests/test_seg_gate.py','tests/test_seg_small.py']
    assert sorted(git('diff','--name-only').splitlines())==sorted(allowed)
    assert not git('diff','--cached','--name-only').strip()
    git('diff','--check')
    diff=git('diff','--no-ext-diff','--',*allowed)
    rel='tests/test_integration_fixes.py'
    diff+=''.join(difflib.unified_diff([], (ROOT/rel).read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+rel))
    (OUT/'scope_guard.diff').write_text(diff)
    testdiff=git('diff','--no-ext-diff','--','tests/test_content_gate.py','tests/test_seg_gate.py','tests/test_seg_small.py')
    (OUT/'test_changes.diff').write_text(testdiff)
    changed=[*allowed,rel]
    dump(OUT/'scope_guard.json',dict(head=init['head'],current_head=current_head,coordinator_changes=coordinator_changes,clean_start=True,branch='cleanup/20261019',changed_files={p:sha(ROOT/p) for p in changed},
        diffs='scope_guard.diff',protected=protected,unchanged_native_assets={p:sha(ROOT/p) for p in unchanged_assets},
        output_directory=str(OUT.relative_to(ROOT)),git_writes=0,git_write_evidence='no mutating git command; .git read-only in session sandbox; coordinator advanced HEAD separately; empty staged diff',
        other_untracked=git('ls-files','--others','--exclude-standard').splitlines()))
    old,new=s['policy_sha256']['old'],s['policy_sha256']['new']
    scores=s['scores'];u=scores['unfiltered'];g=scores['gate_0.3_removed']
    err=lambda q:'/'.join(str(q[k]) for k in ('FP','FN','UNC'))
    agree=lambda q:f"{q['agreement']}/{q['n']}"
    ready=(f"SEG10 READY: fixes ported numeric-adjacency ok heldout-union ok (hunks identical yes); policy sha {old[:8]} → {new[:8]}; segmentation 0.9-s5; pipeline 0.3.1; changed owner-judged lines 59 (= s5 yes); "
        f"150 FP/FN/UNC {err(u['s4']['segeval1'])} → {err(u['s5']['segeval1'])}; 888 {agree(u['s4']['rated'])} → {agree(u['s5']['rated'])}; marks {agree(u['s4']['marks'])} → {agree(u['s5']['marks'])}; "
        f"typology {agree(u['s4']['typology'])} → {agree(u['s5']['typology'])}; tests 248 passed 0 failed")
    (OUT/'ready_line.txt').write_text(ready+'\n')
    lines=['# SEG10 — integration fixes ported; segmentation 0.9-s5 adopted','',
        'Completed the two exact census_03 integration ports and the single inclusive length-band adoption. Native replay: **1,705/1,705** match the saved S4 measurements and new-band native decisions; **zero measurement differences**. Exact changed owner-judged IDs: **59 before gate exclusions, 38 after**, both equal the saved s5 sets. Specified suite: **248 passed in 4.21s**, zero failures. The lead/coordinator commits; no commit was made.','',
        '## Authority and boundaries','',
        '**Coordinator decision, not an owner ruling.** The task supplies this provenance: the coordinator adopted 0.30–2.00 under the owner\'s end-to-end mandate (“you don\'t have to wait for me, resolve these end to end”), recorded it in the coordinator ledger on **19 Oct 2026 at 21:34**, and reported it to the owner in writing: “frozen the configuration at 0.9-s4 measurement, gate 0.3, band 0.30–2.00, one band for everything”. No objection since was reported in the task. This run does not claim an independent ledger/message readback. The provenance is also in the manifest and pipeline README.','',
        'One band applies to numeric/non-numeric and small/non-small rows. Mode 2, padding 1.5, the S4 small path, gate, detector, predictor and geometry remain unchanged. The band was fitted on owner marks; finite-set improvements do not establish independent census generalization.','',
        f"Start: clean `cleanup/20261019` at `{init['head']}` (CLEAN4L); CLEAN4T `{git('log','--all','--grep=CLEAN4T','--format=%h','-1').strip()}` is committed in its ancestry. `git status --porcelain` was empty. Network OFF; no readers, corpus census, deployment or `.git` writes. Only tiny mock census plumbing ran inside the requested tests. Protected package and remote evidence file sizes/mtimes/ctimes are unchanged; absent historical census03_baseline paths were not recreated.",'',
        f"Coordinator commits advanced HEAD during the run to `{current_head}`; their changed files are `{coordinator_changes}`. They contain no SEG10 source, test or replay changes. This task issued no mutating git command.",'',
        '## Exact integration ports','',
        '`automatic_result()` now identifies digit/separator/digit adjacency with the supplied regex. Candidate rows `1.234`, `12 - 3`, `4·5` produce no automatic verified-negative; `Α.Β. 12`, `12.`, `-5` produce `verified_no_change`. Census deduplication unions configured held-out crop hashes into the existing observed held-out set and retains the existing `heldout_crop_identity` rule. The mock fixtures prove config-only protection with zero dev/test observations, observed protection, and an unaffected train row.','',
        '[port_check.json](port_check.json): both complete hunks, including all added bytes and context, equal the archived diff after normalizing line offsets. Full hunk diff:','',
        '```diff',(OUT/'integration_hunks.diff').read_text().rstrip(),'```','',
        '## Policy and versions','',
        f"Old policy SHA256: `{old}`. New: `{new}`. `service.mjs` hashes these exact policy bytes; the service itself is unchanged. Only `lower=.5,upper=1.5` → `lower=.30,upper=2.00` changes in both `boxLengthJudgement` and `combinedBoxJudgement`.",'',
        '| Tool | Version | Iteration count | Recorded change |','| --- | --- | --- | --- |',
        '| Segmentation | 0.9-s4 → 0.9-s5 | 12 → 13 | length band 0.30–2.00 (coordinator decision under the owner\'s end-to-end mandate, 19 Oct 21:34; fitted on owner marks, s5) |',
        '| Numerics | 0.2 → 0.3 | 2 → 3 | Exact numeric-adjacency automatic-negative fix |',
        '| Census | 0.5 → 0.6 | 5 → 6 | Configured held-out crop union |',
        '| Pipeline | 0.3 → 0.3.1 | patch ID | Both integration fixes and policy adoption |','',
        'Ownership: `Pipeline` calls `automatic_result(row, tool, ..., self.versions[tool]["version"], self.versions[tool]["digest"], ...)`; the changed branch emits a **numerics** result, so its iteration is numerics. The manifest previously listed only its legacy N1 artifact; its owning integration component `line_pipeline.py` is now also fingerprinted there. Shared component hashes refresh for other tools without inventing unrelated generations.','',
        'The 0.n tools still have n documented iterations; segmentation preserves the established eight base iterations plus s1–s5 convention (13 total). `iteration_count == len(documented_iterations)` is verified for every tool. `build_filter_versions.py` regenerated the manifest normally: **no fallback**. All component hashes and digests revalidate; an in-memory fresh build equals the saved JSON. Local component keys now name this main-next checkout rather than the manifest\'s former segcensus prefix.','',
        '## Native replay and acceptance','',
        'The unchanged S4 worker factory, S2 source-context handling, S1 network audit hook and 120-second per-row timeout processed the original 150+888+250 crops and 417 non-control typology crops. Saved input rows and crop SHA256s were checked. Each fresh S5 result equals the native service applied to its saved S4 evidence, ignoring only elapsed seconds, version label and policy fingerprint. All other evidence, frame, warnings, binding and decisions match. Runtime: **64.11113916710019 s**. No detector or predictor fit was run.','',
        'There are **111 cohort-entry verdict flips** (overlap between panels is retained), all caused by a length-band change and carrying `length:` reasons. Three additional rows stay DROP but advance from length to the unchanged padding reason; they are listed with saved ratios in [reason_only.jsonl](reason_only.jsonl).','',
        'Among **533 unique owner-judged IDs**, the changed set equals the 59 `scheme=overall` IDs in `s5/changed_lines.jsonl` exactly; its numeric-scheme rows are duplicates/subsets. Removing content-gate 0.3 failures leaves exactly the same **38 IDs** as the gate re-report. [owner_judged_flips.jsonl](owner_judged_flips.jsonl) records them. [acceptance_differences.jsonl](acceptance_differences.jsonl) and [measurement_differences.jsonl](measurement_differences.jsonl) are empty. **No differing lines; no tuning.**','',
        'Scores retain S4 definitions: 150 FP=DROP/fine, FN=KEEP/faulty, UNC=every uncertain; 888 agreement uses explicit ratings only; owner marks use latest timestamp then file order; typology excludes the 20 controls and scores its 185 explicit marks. Content gate 0.3 removes saved failing rows, as in gate_rereport; it does not change segmentation verdicts.','',
        '| Metric | Unfiltered s4 → s5 | Gate 0.3 failures removed: s4 → s5 |','| --- | --- | --- |',
        f"| 150 FP/FN/UNC | {err(u['s4']['segeval1'])} → {err(u['s5']['segeval1'])} (n=150) | {err(g['s4']['segeval1'])} → {err(g['s5']['segeval1'])} (n=137) |",
        *[f"| {label} agreement | {agree(u['s4'][key])} → {agree(u['s5'][key])} | {agree(g['s4'][key])} → {agree(g['s5'][key])} |" for label,key in [('888 rated','rated'),('Owner marks','marks'),('Typology marked','typology')]],
        '| 250 cells KEEP/DROP/UNC | 230/15/5 → 242/3/5 | 205/3/5 → 205/3/5 (n=213) |','',
        'Cohort denominators before → after gate: 150→137, 888→819, 250→213, 417→284. Scored denominators: 135→91 ratings, 235→191 marks, 185→176 typology marks. Full confusion matrices are in [summary.json](summary.json).','',
        '| Overall band objective | S4 0.50–1.50 fd/fk | S5 0.30–2.00 fd/fk |','| --- | --- | --- |',
        '| Before content gate (500 population; 490 objective) | 59/16 | 10/24 |',
        '| Gate failures removed (420 population; 412 objective) | 38/16 | 5/20 |','',
        'All four values exactly equal the s5/gate_rereport fixed-band figures. As before, owner-DROP notes that length cannot assess are outside the objective (10 before /8 after), but remain in the population and changed-ID check. This is why these objective errors differ from the separate panels\' confusion counts. Wider bounds reduce false drops while some false keeps increase; the recorded band is adopted without tuning.','',
        '## Tests and layout compatibility','',
        '`tests/test_content_gate.py`, `test_line_pipeline.py`, `test_seg_{gate,deskew,curve,small}.py`, and `test_integration_fixes.py`: **`248 passed in 4.21s`**, **0 failed**. New mode-2 boundary tests exercise regular and small branches: 0.30/2.00 KEEP; 0.2999/2.0001 DROP.','',
        'The existing band expectation changes only its default endpoints. Two identity assertions also need the authorized version/fingerprint changes: the clear-row fixture retains exact output equality after its expected pipeline stamp changes to 0.3.1; the non-small geometry comparison explicitly verifies differing policy hashes and compares every remaining normalized field/evidence byte. The historic fixtures were not rewritten. All test diffs:','',
        '```diff',testdiff.rstrip(),'```','',
        'CLEAN3 moved saved replay JSONL inputs into `../greek-ocr-data`; CLEAN4L moved historical scripts under `docs/records`. Existing tests still reference the old paths and historical scripts calculate the root at their original depth. [prepare_view.py](prepare_view.py) creates a temporary layout view under `/private/tmp`, verifies mirrored file SHA256s against CLEAN3 receipts, links current production assets, and copies the four historical replay scripts and seven tests byte for byte at their original depth. It also copies the unchanged gate03 analysis script for its original root calculation. Source/archives are not restored or edited. [view_receipt.json](view_receipt.json) records the exact paths and verified hashes. This is the only replay/test layout fallback; manifest regeneration had none.','',
        'The initial suite result was `9 failed, 239 passed in 4.39s`: four missing compatibility-view fixtures, three old version/hash expectations, and two new test-fixture construction errors. All were corrected; [tests_initial.log](tests_initial.log) is preserved. No test was skipped or marked expected-failure.','',
        'Exact executed command: [tests_command.txt](tests_command.txt). Reproduce with the sol-recut interpreter and `PYTHONPATH=.`:','',
        '```sh','PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/records/harvest/seg_steps/s5_adopt/run_tests.py',
        'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/records/harvest/seg_steps/s5_adopt/replay.py',
        'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. ../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/records/harvest/seg_steps/s5_adopt/summarize.py','```','',
        '## Scope and receipts','',
        '[scope_guard.json](scope_guard.json) lists changed files, SHA256s and protected-tree verification. [scope_guard.diff](scope_guard.diff) contains every production, manifest, README and test change, including the new integration tests. [receipt.json](receipt.json) fingerprints all generated artifacts, source inputs, interpreter and replay bindings. [replay.jsonl](replay.jsonl) retains all 1,705 before/after native results; [flips.jsonl](flips.jsonl) lists every cohort-entry verdict flip. No other tool rules changed.','',ready]
    (OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
    inputs=['docs/records/harvest/seg_census/remote_evidence/integration_fixes.diff','docs/records/harvest/seg_census/remote_evidence/source_diff_validation.json','docs/records/harvest/seg_census/remote_evidence/HANDOFF.md',
        'docs/records/harvest/seg_steps/s5/BAND_PROPOSAL.md','docs/records/harvest/seg_steps/s5/changed_lines.jsonl','docs/records/harvest/seg_steps/s5/band_population.jsonl',
        'docs/records/harvest/seg_steps/gate_rereport/REPORT.md','docs/records/harvest/seg_steps/gate_rereport/finite_summary.json',
        'docs/records/harvest/seg_steps/s4/replay.py','docs/records/harvest/seg_steps/s4/validate_report.py','docs/records/harvest/seg_steps/s4/tests_command.txt',
        'docs/records/harvest/seg_steps/s4/owner_marks_snapshot.jsonl','docs/records/harvest/seg_steps/s4/typology_owner_marks_snapshot.jsonl']
    dump(OUT/'receipt.json',dict(schema='seg10-adoption-receipt-v1',created_utc=datetime.now(timezone.utc).isoformat(),head=init['head'],
        branch='cleanup/20261019',current_head=current_head,coordinator_changes=coordinator_changes,clean_start=True,network='OFF',readers=0,corpus_census=0,git_writes=0,
        policy_sha256=s['policy_sha256'],manifest_sha256=sha(vp),manifest_fallback=None,manifest_build_equals_saved=True,manifest_iterations_valid=True,
        protected=protected,test_result=s['tests'],inputs_sha256={p:sha(ROOT/p) for p in inputs},
        interpreter=dict(path=command[0],resolved=str(Path(command[0]).resolve()),sha256=sha(Path(command[0]).resolve())),
        artifacts={str(p.relative_to(OUT)):dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='receipt.json'},
        last_line=ready))
    print(ready)


if __name__=='__main__':run()
