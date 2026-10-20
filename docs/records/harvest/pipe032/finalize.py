"""Verify manifest, scope and immutable functions; write report and file receipts."""
from pathlib import Path
from datetime import datetime, timezone
import ast, difflib, hashlib, importlib.util, json, os, re, shlex, subprocess
ROOT=Path(__file__).resolve().parents[4];OUT=ROOT/'docs/records/harvest/pipe032'
ENV=dict(os.environ,GIT_OPTIONAL_LOCKS='0',PYTHONDONTWRITEBYTECODE='1')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,env=ENV,text=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def source(p, name):
    s=Path(p).read_text();tree=ast.parse(s)
    n=next(n for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and n.name==name)
    return ast.get_source_segment(s,n),[n.lineno,n.end_lineno]
def fingerprint(p):return dict(path=str(p.relative_to(ROOT)),bytes=p.stat().st_size,sha256=sha(p))

def main():
    from greekocr.harvest.line_pipeline_census import verify_versions
    vp=ROOT/'docs/harvest/line_pipeline/tool_versions.json'
    before=read(OUT/'baseline/tool_versions.json');after=read(vp)
    subprocess.run([os.sys.executable,'-B',str(ROOT/'scripts/harvest/build_filter_versions.py')],env=ENV,cwd=ROOT,check=True,stdout=(OUT/'version_build.log').open('w'))
    assert read(vp)==after
    spec=importlib.util.spec_from_file_location('pipe032_builder',ROOT/'scripts/harvest/build_filter_versions.py');build=importlib.util.module_from_spec(spec);spec.loader.exec_module(build)
    assert build.build()==after
    verify_versions(after['tools'])  # Direct, unchanged runtime verifier, no native worker.
    scans=[]
    for name,t in after['tools'].items():
        old=before['tools'][name]
        valid=lambda x:x['version']=='0.'+str(x['iteration_count']) and x['iteration_count']==len(x['documented_iterations'])
        scans.append(dict(tool=name,before_version=old['version'],after_version=t['version'],before_iterations=old['iteration_count'],after_iterations=t['iteration_count'],before='PASS' if valid(old) else 'FAIL',after='PASS' if valid(t) else 'FAIL'))
        assert valid(t)
    assert [r['tool'] for r in scans if r['before']=='FAIL']==['segmentation']
    dump(OUT/'version_verification.json',dict(verifier='greekocr.harvest.line_pipeline_census.verify_versions',direct_result='PASS',build_equals_saved=True,additional_label_accepted=after['tools']['segmentation']['label']=='0.9-s5',tools=scans))
    dump(OUT/'version-build-fallbacks.json',[])
    (OUT/'version_verifier.log').write_text('verify_versions(regenerated_manifest["tools"]): PASS; all component hashes and digests checked\n'+'\n'.join(f"{r['tool']}: {r['before_version']} ({r['before']}) -> {r['after_version']} ({r['after']}); iterations {r['before_iterations']} -> {r['after_iterations']}" for r in scans)+'\n')
    allowed=['docs/harvest/line_pipeline/README.md','docs/harvest/line_pipeline/tool_versions.json','greekocr/harvest/line_pipeline.py','greekocr/harvest/line_pipeline_census.py','scripts/harvest/build_filter_versions.py','tests/test_content_gate.py']
    assert sorted(git('diff','--name-only').splitlines())==sorted(allowed)
    assert not git('diff','--cached','--name-only').strip()
    untracked=git('ls-files','--others','--exclude-standard').splitlines()
    assert all(p=='tests/test_routes_out_of_scope.py' or p.startswith('docs/records/harvest/pipe032/') for p in untracked)
    git('diff','--check')
    immutable={}
    for rel,names in [('greekocr/harvest/line_pipeline.py',['routes','automatic_result','validate_result','preserve_holds','final_eligibility','finish','content_gate_exclusion','short_line_exclusion','merge_edits']),('greekocr/harvest/line_pipeline_census.py',['deduplicate','verify_versions'])]:
        for name in names:
            a,_=source(OUT/'baseline'/Path(rel).name,name);b,lines=source(ROOT/rel,name);assert a==b,(rel,name)
            immutable[rel+'::'+name]=dict(unchanged=True,sha256=hashlib.sha256(b.encode()).hexdigest(),lines=lines)
    for rel in ['greekocr/harvest/line_pipeline_native.py','greekocr/harvest/filtering_assets/segmentation-policy.js','greekocr/harvest/filtering_assets/crop-tools.py','greekocr/harvest/line_pipeline_sources.py']:
        assert git('show','HEAD:'+rel)==(ROOT/rel).read_text();immutable[rel]=dict(unchanged=True,sha256=sha(ROOT/rel))
    for f in (OUT/'baseline').iterdir():
        rel=next((r for r in allowed if Path(r).name==f.name),None)
        assert rel and git('show','HEAD:'+rel)==f.read_text(),f
    patch=git('diff','--no-ext-diff','--',*allowed)
    new='tests/test_routes_out_of_scope.py'
    patch+=''.join(difflib.unified_diff([], (ROOT/new).read_text().splitlines(True),fromfile='/dev/null',tofile='b/'+new))
    (OUT/'scope_guard.diff').write_text(patch)
    dump(OUT/'scope_guard.json',dict(allowed_source_changes=allowed+[new],actual_tracked_changes=git('diff','--name-only').splitlines(),new_test=new,output_root='docs/records/harvest/pipe032/',outside_scope_changes=[],index_changes=[],immutable=immutable,patch_sha256=sha(OUT/'scope_guard.diff')))
    native=read(OUT/'native_replay_receipt.json');mock=read(OUT/'mock_receipt.json')
    assert native['matching']=={'segeval1':150,'calibration':888} and not native['differences']
    assert all(not s['empty_config_differences'] and not s['movers'] for s in mock['summary'].values())
    log=(OUT/'tests.log').read_text();verbatim=log.strip().splitlines()[-1]
    match=re.fullmatch(r'(\d+) passed in [\d.]+s',verbatim);assert match,log
    passed=int(match[1]);assert passed==260
    view=Path(read(OUT/'view_receipt.json')['view'])
    names=['test_content_gate.py','test_line_pipeline.py','test_seg_gate.py','test_seg_deskew.py','test_seg_curve.py','test_seg_small.py','test_integration_fixes.py','test_routes_out_of_scope.py']
    source_copies={}
    for name in names:
        assert (view/'tests'/name).read_bytes()==(ROOT/'tests'/name).read_bytes();source_copies['tests/'+name]=sha(ROOT/'tests'/name)
    for rel in ['greekocr/harvest/line_pipeline.py','greekocr/harvest/line_pipeline_census.py']:
        assert (view/rel).read_bytes()==(ROOT/rel).read_bytes();source_copies[rel]=sha(ROOT/rel)
    interpreter=ROOT.parent/'greek-ocr-toolkit-sol-recut/.venv/bin/python'
    cmd=[str(interpreter),'-B','-m','pytest','-q','-p','no:cacheprovider',*['tests/'+n for n in names]]
    (OUT/'tests_command.txt').write_text('cd '+shlex.quote(str(view))+'\nPYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. '+shlex.join(cmd)+'\n')
    dump(OUT/'tests_receipt.json',dict(command=cmd,cwd=str(view),verbatim=verbatim,passed=passed,failed=0,errors=0,skipped=0,source_copies_sha256=source_copies,interpreter=dict(path=str(interpreter),sha256=sha(interpreter)),current_equivalent='S4 five-file command expanded to S5 seven files plus the PIPE032 route tests'))
    head=git('rev-parse','HEAD').strip();assert head=='4bf2e4cf37e69eb4a073308e8809ce4189c7182c'
    table=['| Tool | Version before → after | Iterations before → after | Invariant before → after |','|---|---|---|---|']
    for r in scans:table.append(f"| {r['tool']} | {r['before_version']} → {r['after_version']} | {r['before_iterations']} → {r['after_iterations']} | {r['before']} → {r['after']} |")
    mt=['| Mock split mode | ADMIT / HOLD / DROP before | After polytonic out | Empty-config differing rows | Movers |','|---|---|---|---:|---:|']
    for mode,s in mock['summary'].items():
        fmt=lambda x:'/'.join(str(x[k]) for k in ('ADMIT','HOLD','DROP'))
        mt.append(f"| {mode} | {fmt(s['before'])} | {fmt(s['after'])} | {len(s['empty_config_differences'])} | {len(s['movers'])} |")
    ready=f'PIPE032 READY: routes_out_of_scope ok; in-scope missing still HOLD ok; admission field ok; empty-config regression 150/888 150/888 mock 200 identical yes; polytonic-out mock ADMIT/HOLD/DROP 106/46/48 → 106/46/48; segmentation version 0.13 (label 0.9-s5) verifier ok; pipeline 0.3.2; versions moved composer 0.2→0.3, census 0.6→0.7, segmentation 0.9-s5→0.13; fallbacks 0; suite {passed} passed 0 failed 0 errors'
    report=['# PIPE032 — pipeline 0.3.2','',
      'Implemented declared correction scope; all requested checks pass. Changes remain uncommitted for the coordinator. No live census, reader, network, Slurm, deployment or Git-metadata write was issued.','',
      '## Launch and scope','',
      f'The provided writable checkout is `{ROOT}`, branch `cleanup/pipe032`, launch HEAD `{head}`. Its initial `git status --porcelain` was empty. The requested main-next tree was also clean on `cleanup/20261019` at `1c5038626f202503e980d72b9cbdf562b7d5f3c6`; PIPE032 is its direct child with only the task brief added. Work stayed in the writable isolated checkout. No branch switch or commit was performed.','',
      'Read the requested routing/result/final-eligibility code, census binding/dedup/exports/verifier, builder/manifest/README, and segcensus HANDOFF_CENSUS05 blocking findings plus audit_runtime_contracts.py. Segcensus evidence was read only. The separate standing N1 version/digest incompatibility remains outside this task; passing this manifest verifier does not certify those ledgers or a census05 package.','',
      '## Changes','',
      '- Config `routes_out_of_scope` defaults to `[]`, validates against `TOOLS`, rejects `content_repair`, and is materialized in the config before the run binding hash. Pipeline receives a copied list beside its existing policy. Invalid scope fails even before reporting-only preflight or output creation.',
      '- Needed out-of-scope tools return the exact requested `not_applied_out_of_scope` route record before any corrector/ledger lookup or automatic result. The status is outside `SUCCESS`, exempt only from unresolved-route HOLD, supplies no edits, skips candidate recheck, and is excluded from content-repair resolvers. In-scope missing/sparse results still HOLD. Gate/segmentation exclusions still retain prior-exclusion route records.',
      '- Admission records always contain `corrections_not_applied`: sorted routed tool names, otherwise `[]`. The embedded decision supplies their `not_applied_out_of_scope` status. Summary `corrections_not_applied` maps each configured tool to counts by final disposition, including post-dedup changes. Compatibility admission `pipeline_version` now uses `PIPELINE_VERSION` instead of stale `0.3`.',
      '- Manifest and requested README identify polytonic-out census05 as the **20 October coordinator decision under the owner\'s end-to-end mandate, never an owner ruling**; SF7 remains candidate_pre_audit and enters when its audit passes. Default scope remains empty.',
      '- Segmentation becomes `0.13`, with extra display field `label="0.9-s5"`; no restrictive manifest property schema exists in the consumers, and the unchanged verifier accepts this field. Thirteen existing iterations remain thirteen. No segmentation method, thresholds or runtime verifier changed.',
      '- Composer owns this orchestration change (its manifest components include `line_pipeline.py`); it adds iteration 3. Census adds iteration 7 for scope binding/admission exports/counts. Other versions do not move; shared-file component digests regenerate as required.',
      '- README version/integration notes are synchronized with this HEAD. The sole existing-test edit updates the explicit pipeline-version expectation from 0.3.1 to 0.3.2; assertions and fixtures otherwise remain unchanged.','',
      '## Final eligibility and preserved rules','',
      '`greekocr/harvest/line_pipeline.py:337–380` is byte-identical to launch. Its signature reads row, composed text/inventory, expectations, codec and final policy; its body has no routes, polytonic-result or release-scope lookup. The unchanged call at lines 510–512 passes those same arguments. Scope only changes which correction obligations are scheduled/recorded at lines 446–477. Final eligibility reads nothing new.','',
      '`scope_guard.json` verifies unchanged function bytes for routes, automatic_result, validate_result, preserve_holds, final_eligibility, finish, the gate/length rules, merge_edits, deduplicate and verify_versions. Segmentation/native assets and source adapters also remain unchanged.','',
      '## Versions and direct verifier','',*table,'',
      'Pipeline constant: **0.3.1 → 0.3.2**. `build_filter_versions.py` ran normally; a fresh in-memory build equals saved JSON. `version-build-fallbacks.json` is `[]`. Direct `verify_versions(after["tools"])` succeeds for all tools, checking version/history, every component file hash, and every component digest. See `version_verification.json`, `version_build.log` and `version_verifier.log`.','',
      '## Tests and native replay','',
      f'Verbatim final suite count: **`{verbatim}`** — **0 failed / 0 errors / 0 skipped**. The S4 command\'s current equivalent includes the seven S5 integration files plus `tests/test_routes_out_of_scope.py` (12 PIPE032 cases). Exact command, cwd, copied-file hashes and interpreter are in `tests_command.txt` and `tests_receipt.json`.',
      '',
      'The suite uses a temporary view because this isolated worktree lacks the ignored CLEAN4L alias file, predictor and some relocated evidence. Production/test Python copies are byte-identical; missing support/evidence is linked from existing local custody. `prepare_view.py` and `view_receipt.json` identify the view and supplements. No source or fixture from another worktree was modified. The initial collection failure and initial monotonic fixture mistake were fixed before the final full passing run; no tool rule was relaxed.','',
      f'Fresh native replay: **150/150 segeval1 + 888/888 calibration** verdicts and reasons equal the exact saved S5 `after` results, in {native["elapsed_seconds"]:.3f}s. Every crop SHA was rechecked; calibration uses the unchanged saved-context workflow. Differing rows: **none (`[]`)**. `native_replay.jsonl`, script/log and receipt retain every comparison and source/predictor hashes. This verifies native parity under the segmentation version relabel; no reader was run.','',
      '## Whole-pipeline mock','',*mt,'',
      'These are fresh 0.3.1 versus 0.3.2 runs of the unchanged relocated census04 `mock_batch.py::build` 200-real-row slice and census04 split/diagnostic wrapper, with native observations injected and synthetic qualified no-change corrections preserved. Both modes execute registration, correction imports/validation, routing/composition, final checks, dedup and durable export. No shell job, srun or live census executes. Native saved observation version metadata is relabeled to the bound version; verdicts and evidence are unchanged.','',
      'To isolate behavior, both sides use the exact original 0.3.1 manifest/correction binding. Every complete decision is equal after removing only `pipeline_version` and `run_binding_sha256`, whose changes are intentional; no reason, route, text, edit, stage or diagnostic field is removed. All raw decisions are saved as mode-*-{before,empty,polytonic-out}.jsonl. The regenerated production manifest is independently accepted by the direct verifier.','',
      'Empty-config differing rows, mode-i: `[]`; mode-ii: `[]`. Polytonic-out movers, mode-i: `[]`; mode-ii: `[]`. The harness supplies qualified synthetic polytonic no-change records for every row, so disabling those records cannot recover missing-SF7 HOLDs in this fixture. Every-mover requirement is satisfied with zero movers; no population recovery is inferred. The focused cases separately prove polytonic-only unresolved HOLD → ADMIT and polytonic+missing-numerics remains HOLD. The mode-ii counts are used in the readiness line.','',
      '| Mode | Routed out-of-scope polytonic ADMIT / HOLD / DROP |','|---|---|',
      *[f"| {mode} | {s['scope_counts']['polytonic'].get('ADMIT',0)}/{s['scope_counts']['polytonic'].get('HOLD',0)}/{s['scope_counts']['polytonic'].get('DROP',0)} |" for mode,s in mock['summary'].items()],
      '',
      'The archived original mock result (73/87/40 mode-i; 133/14/53 mode-ii, expressed ADMIT/HOLD/DROP) used an older package. It is not the 0.3.1 control: the control above runs launch 0.3.1 source with the current gate/final rules and its original manifest.','',
      '## Scope guard and receipt','',
      'Source changes (complete diffs in `scope_guard.diff`):','',*[f'- `{p}`' for p in allowed+[new]],'',
      'All additional artifacts are inside `docs/records/harvest/pipe032/`. `scope_guard.json` records the allowed/actual change set, empty index changes and unchanged function hashes. `receipt.json` records path, bytes and SHA256 for source/output artifacts and read-only input evidence; producing state is uncommitted on the launch commit, awaiting coordinator commit. No file exceeds 5,000,000 bytes.','',ready]
    (OUT/'REPORT.md').write_text('\n'.join(report)+'\n')
    inputs=[]
    for p in [ROOT/'AGENTS.md',ROOT.parent/'greek-ocr-toolkit-segcensus/docs/harvest/census05/HANDOFF_CENSUS05.md',ROOT.parent/'greek-ocr-toolkit-segcensus/docs/harvest/census05/audit_runtime_contracts.py',ROOT.parent/'greek-ocr-toolkit-main-next/docs/records/harvest/seg_steps/s4/tests_command.txt']:
        inputs.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p)))
    files=[fingerprint(ROOT/p) for p in allowed+[new]]+[fingerprint(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='receipt.json']
    assert all(f['bytes']<=5000000 for f in files)
    dump(OUT/'receipt.json',dict(schema='pipe032-receipt-v1',created_utc=datetime.now(timezone.utc).isoformat(),source_commit=head,producing_state='uncommitted working tree; coordinator commits',producing_commit=None,branch=git('branch','--show-current').strip(),initial_porcelain='',patch_sha256=sha(OUT/'scope_guard.diff'),network=False,reader_runs=0,live_census_runs=0,slurm=0,git_mutations=[],inputs=inputs,files=files,receipt_self_hash_excluded=True))
    print(ready)
if __name__=='__main__':main()
