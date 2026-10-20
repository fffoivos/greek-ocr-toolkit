"""Render the RB8 handoff and an exact path list; no git calls."""
import json,pathlib
BASE=pathlib.Path(__file__).resolve().parent;ROOT=BASE.parents[1];OUT=BASE/'output_3702849'
r=json.loads((OUT/'READBACK_RECEIPT.json').read_text());remote=json.loads((OUT/'remote_sha_verification.json').read_text());stays=json.loads((OUT/'REMOTE_ONLY_SHA256.json').read_text());s=r['splits'];train=r['train_comparison'];runtime=r['runtime']
size=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file());lines=[]
def add(t=''):lines.append(t)
add('# RB8 — TR2 job 3702849 test/dev readback')
add();add('20 October 2026. **Readback passed; candidate status unchanged.** `ssh clariden true` exited 0, with no certificate refresh. Slurm job and all recorded steps are `COMPLETED`, exit `0:0`. The complete job log is retained locally. No submission, resubmission, job-output modification, audit acceptance, label binding, or `.git` write was performed. Network use was limited to Clariden.')
add();add('The release ID is `sf7_rc1_test_edits_A`, parent `google_raw_v2_import`, variant A, source job `3702849`. Both release receipts remain `candidate_pre_audit`, `bound: false`. This is integrity/readback evidence, not an accuracy audit.')
add();add('| Split | Selected lines | Released rows | Edits | Composer corrected | Unchanged | HOLD | Composer-only rows omitted |')
add('|---|---:|---:|---:|---:|---:|---:|---:|')
for split,v in s.items():
 c=v['composer_counts'];add(f"| {split} | {v['selection_lines']:,} | {v['rows']} | {v['edits']} | {c['corrected']} | {c['unchanged']:,} | {c['hold']:,} | {v['normalization_only']} |")
add();add('There are 377 distinct row byte patches for 392 logical edits: multiple mark edits can share a grapheme patch. Each row reconstructs forward and backward against its raw-parent UTF-8 bytes. Every edit has nonempty byte patches, valid parent spans, source/policy provenance, and an independent reversible application. All 36,730 selected labels equal their matching raw-parent labels. Full overlay coverage equals the exact TR1 selected ID inventories, controls equal corrected ∪ unchanged, and test/dev IDs are disjoint; no duplicate or unselected IDs occur. Separate score receipts report 28,620/28,620 and 8,110/8,110 alignment identity matches, with zero mismatches; their score-file hashes were verified remotely.')
add();add('**Receipt terminology caveat:** all 11 test + 4 dev IDs in the upstream `normalization_only` fields actually differ by one composer-only insertion of U+201C (`“`). They are not Unicode-normalization-only changes. Independent comparison records each ID and difference in the readback receipt. They are excluded from the edits-only files, exactly as the existing converter emitted them. The upstream receipts and package were preserved; this terminology discrepancy is left visible for the audit.')
add();add('## Edits by kind and head')
add();add('“Insert” below corresponds to receipt kind `addition`, “delete” to `deletion`, and “substitute” to `substitution`. Quote-alias consumption is reported separately, rather than counted as a diacritic deletion.')
add();add('| Split | Head | Insert | Delete | Substitute | Quote-alias consume |')
add('|---|---|---:|---:|---:|---:|')
for split,v in s.items():
 for h in ('accent','breathing','dialytika','subscript','quote_alias'):
  c=v['edits_by_head'].get(h,{});add(f"| {split} | {h} | {c.get('addition',0)} | {c.get('deletion',0)} | {c.get('substitution',0)} | {c.get('quote_alias_consume',0)} |")
add();add('Totals: test 68 insertions, 0 diacritic deletions, 271 substitutions, 2 quote-alias consumptions; dev 11 insertions, 0 deletions, 40 substitutions.')
add();add('## Rate comparison and runtime')
add();add('| Release | Selected lines | Edited rows | Edits | Edits / selected line | Edits / 1,000 selected lines | Relative to train |')
add('|---|---:|---:|---:|---:|---:|---:|')
t=train['edits_per_selected_line'];add(f'| Train RB7 | 124,669 | 605 | 665 | {t:.8f} | {t*1000:.4f} | 1.000× |')
for split,v in s.items():
 rate=v['edits_per_selected_line'];add(f"| {split} | {v['selection_lines']:,} | {v['rows']} | {v['edits']} | {rate:.8f} | {rate*1000:.4f} | {rate/t:.3f}× |")
rate=392/36730;add(f'| Test + dev | 36,730 | 359 | 392 | {rate:.8f} | {rate*1000:.4f} | {rate/t:.3f}× |')
add();add('The denominator is the full selected population, including HOLD. These rates describe emitted candidate edits, not accuracy or a like-for-like precision comparison across populations.')
add();add(f"Slurm allocation: **29m32s (1,772 s), four GPUs, {runtime['allocated_gpu_hours']:.6f} allocated GPU-h**. Pipeline receipt: {runtime['pipeline_seconds']:.3f} s (29m21.07s). Against the 40-minute / 2.666667 GPU-h forecast, allocation elapsed was **10m28s shorter (26.17% below forecast)**, saving 0.697778 allocated GPU-h. Requested limit was 60 minutes. GPU-h measures reserved GPUs × allocation elapsed, not measured GPU utilisation; queue delay is excluded. [Slurm state](../../../artifacts/sf7_rc1_test/output_3702849/job_state.txt).")
add();add('## Identity and SHA verification')
add();add('| Binding | SHA-256 |')
add('|---|---|')
for k,v in [('Policy digest',r['policy_digest']),('Preregistration',r['preregistration_sha256']),('Test parent',s['test']['parent_sha256']),('Dev parent',s['dev']['parent_sha256']),('Test selection',s['test']['selection_sha256']),('Dev selection',s['dev']['selection_sha256'])]:add(f'| {k} | `{v}` |')
add();add(f"All **{len(remote['files']):,} remote files** ({sum(v['bytes'] for v in remote['files'].values()):,} bytes) were SHA-256 hashed; {remote['receipt_bound_files']:,} distinct files match existing job-receipt references through {len(remote['checks']):,} checks. Scalar metadata links and alignment-binding content were checked separately. The two recompose configs also match their SF7 receipt hashes. The remaining 22 files are metadata/receipt roots or summaries for which the job publishes no hash in another receipt; their captured hashes are retained without inventing an original receipt binding. Both raw-parent hashes, exact TR1 inventories, selection hashes, release hashes, policy-source hashes and preregistration were checked against the package. Local config hash equals the remote config hash. Each downloaded original output and the job log matches its remote SHA. The terminal log receipt equals `receipt.json`.")
add();add('The independent local verifier uses the TR2 `readback_dryrun.py` forward/reverse method at full population scale, with RB7 provenance and untouched-byte checks. Compact witnesses were streamed directly from raw parents, selections, overlays and controls on Clariden; full raw files and overlays were not downloaded. The extractor and witness hash are retained for reproducibility. No inference or training ran on the Mac.')
add();add('## Retained files and lead handoff')
add();add(f"The local output directory contains **{size:,} bytes ({size/1e6:.2f} MB)**, below the 200 MB total limit. It contains both edits-only releases, all job receipts and small stage summaries, the complete log, Slurm state, compact readback witnesses, verification evidence and the RB7-schema [READBACK_RECEIPT.json](../../../artifacts/sf7_rc1_test/output_3702849/READBACK_RECEIPT.json).")
add();add(f"**{len(stays):,} files / {sum(v['bytes'] for v in stays.values()):,} bytes stay remote**, including raw production arrays, detector window arrays, alignment/frame scores, combined A/B/E runtime, shard overlays and full overlays/controls. Every retained-remote output path, size and SHA is listed in [REMOTE_ONLY_SHA256.json](../../../artifacts/sf7_rc1_test/output_3702849/REMOTE_ONLY_SHA256.json), relative to `{remote['run']}`. Raw parents, checkpoints and crops also remain remote as package inputs; their bindings are in the package and verification checks. These inputs are not part of the output-tree byte total.")
add();add('The exact lead commit list is [LEAD_COMMIT_PATHS.txt](../../../artifacts/sf7_rc1_test/LEAD_COMMIT_PATHS.txt). It includes this report, the five readback/retrieval/verification scripts plus report generator, both releases, receipts, small summaries and all evidence files. Some artifact paths may be ignored by repository rules; the lead should use the exact list when staging. No staging or commit was attempted. Re-run local readback with:')
add();add('```bash\npython3 -B artifacts/sf7_rc1_test/validate_rb8.py\n```')
add();add('RB8 DONE: job 3702849 COMPLETED; test rows 308 edits 341; dev rows 51 edits 51; readback ok')
report=ROOT/'docs/labelfix/spellcheck/SF7_TEST_READBACK.md';report.write_text('\n'.join(lines)+'\n')
lead=BASE/'LEAD_COMMIT_PATHS.txt';paths=sorted({str(p.relative_to(ROOT)) for p in BASE.rglob('*') if p.is_file()}|{str(report.relative_to(ROOT)),str(lead.relative_to(ROOT))});lead.write_text('\n'.join(paths)+'\n')
print('Report written;',len(paths),'lead paths;',size,'output bytes')
