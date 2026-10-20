"""Write the RU4E2 offline handoff from completed preparation evidence."""
from collections import Counter
import json
from pathlib import Path
import ru4e2 as n
m=n.m
A=n.ART

def main():
    build=json.loads((A/'build.json').read_text())
    books=m.rows(A/'census_by_book.jsonl')
    census=m.rows(A/'census_all_rows.jsonl')
    pp=m.rows(A/'candidate_positions.full.jsonl')
    wave=json.loads((A/'wave1c_comparison.json').read_text())
    old=json.loads((m.ART/'broader_lqb_check.json').read_text())
    failures=[]
    for name in old['failures']:
        if name=='test_v2_source_hashes_and_outputs':
            cause='Historical LQB3 receipt expects external release_exclusions.json SHA e9f975908d; current SHA is 573c8f3fec. The test calls relative_to(ROOT) on that changed external path and raises ValueError. Historical custody is unproven; no LQB runtime regression.'
            native='fails'
        elif name in ('test_union_marks_known_and_inserted_unknown','test_mark_heads_reported_separately'):
            cause='x86_64 Python/NumPy cannot load arm64 SciPy ndimage, reached through the existing union scorer and labelfix/ink.py. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure.'
            native='passes'
        else:
            cause='x86_64 Python/NumPy cannot load arm64 SciPy, reached through the existing external adjudicate/score.py scipy.stats import. Installed NumPy 1.24.3 is also below SciPy requirement >=1.26.4. Environment failure.'
            native='passes'
        failures.append(dict(test=name,cause=cause,native_environment=native,classification='other',fixed=False))
    m.dump(A/'lqb_failure_census.json',dict(original_failures=14,fixed=0,other=14,x86=dict(passed=69,failed=14),native=dict(passed=82,failed=1),failures=failures))
    line=(f"RU4E2 READY: cyrillic rows test {build['rows']['test']}/dev {build['rows']['dev']} in {len(books)} books (pre_reform {sum(b['orthography']=='pre_reform' for b in books)}); candidates {len(pp)} positions in {build['candidate_lines']} lines; matches wave1c slice {'yes' if wave['matches'] else 'no'}; contexts {len(build['contexts'])} ×2; est {build['budget']['points']} pts; LQB failures 14 (fixed 0, other 14)")
    text=['# RU4E2: complete Cyrillic census and offline reading preparation','',
      f"**{build['rows']['test']:,} test rows, {build['rows']['dev']:,} dev rows, {len(books)} books; {len(pp):,} candidate positions in {build['candidate_lines']:,} lines.** All 13 books meet the requested mechanical pre_reform rule. Wave-1c scored a subset, so exact equality is **no**. No readers, usage probes, network, browser, computer-use, real .git writes or other-worktree writes were performed.",'',
      '## Census','',
      'Every row in both imports was inspected. Selection is case-insensitive `script_class == cyrillic` OR at least three Unicode Cyrillic letters in the exact import `label`. These exact import labels supply the raw parent; no convention label stream, Unicode normalization or whitespace editing is used. `(source, doc)` is the book identity. There are 3,526 class-Cyrillic test rows plus 26 qualifying Latin-class rows, and 411 class-Cyrillic dev rows. Language is a metadata guess, not pixel evidence.','',
      'Orthography is `pre_reform` iff a book has >=5 final ъ or any ѣ/і/ѳ/ѵ (historical counts include uppercase via casefold). Final signs and candidates use the unchanged RU4E positional rule: lowercase sign, preceding Cyrillic letter, no following Cyrillic letter, `kind == final`; ASCII pre-hyphen positions are excluded. No Google ъ is a candidate. Offsets are zero-based Unicode code points in the untouched raw string.','',
      '| Book identity | Test | Dev | Language guess | Final ь | Final ъ | ѣ | і | ѳ | ѵ | Candidate lines |','|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|']
    for b in books:
        language=b['language_guess'];language=', '.join(language) if isinstance(language,list) else language
        h=b['historical'];lines=len({p['row_id'] for p in pp if p['book']==b['book']})
        text.append(f"| {b['book']} | {b['splits'].get('test',0)} | {b['splits'].get('dev',0)} | {language} | {b['final_soft']} | {b['final_hard']} | {h['ѣ']} | {h['і']} | {h['ѳ']} | {h['ѵ']} | {lines} |")
    text+=['','All entries have mechanical orthography class `pre_reform`. The Serbian dev book qualifies through seven і and has zero final signs. Wikisource 5a6a4fec qualifies through a single і despite zero final ъ; its 113 candidate positions are retained as instructed. Neither case establishes historical Russian spelling. The two Bulgarian archive volumes are retained; do not interpret every candidate as a proposed Russian hard-sign edit.','',
      'Exact rows, per-book counts, candidate offsets and candidate lines are in [census_all_rows.jsonl](../../../artifacts/ru1/ru4e2/census_all_rows.jsonl), [census_by_book.jsonl](../../../artifacts/ru1/ru4e2/census_by_book.jsonl), [candidate_positions.full.jsonl](../../../artifacts/ru1/ru4e2/candidate_positions.full.jsonl) and [candidate_lines.full.jsonl](../../../artifacts/ru1/ru4e2/candidate_lines.full.jsonl). Per-split/book counts are also saved.','',
      '## Wave-1c comparison','',
      f"Production readback root: `{n.WAVE}`. Its bound deployment manifest is `wave1c_prep/manifest_fix1.json`, SHA `{wave['manifest_sha256']}`. Scored populations are established from `wave1c/job01/predictions/ctrl_s0_v2_test.jsonl` and its full-coverage counterpart, then independently compared for all six production arms and both instruments. Each of the 12 prediction files matches its saved `predictions_sha256` receipt. The deployed raw test and dev snapshots are SHA-identical to the census imports.",'',
      '| Instrument | Cyrillic scored rows / unique IDs per arm | Census test rows | Missing census IDs | IDs outside census |','|---|---:|---:|---:|---:|',
      '| v2_test | 1,742 / 1,742 | 3,552 | 1,810 | 0 |','| v2_test_full_coverage | 3,510 / 3,510 | 3,552 | 42 | 0 |','',
      'Both instruments have identical Cyrillic ID sets across all six arms. The full-coverage Cyrillic slice omits all 26 Latin-class census rows and 16 class-Cyrillic rows. No omission cause is inferred merely from the IDs. Neither instrument equals even the 3,526 script-class-only test rows. Dev is preparation scope, not part of these scored TEST instruments. Exact missing IDs, prediction paths/hashes and receipt paths/hashes are in [wave1c_comparison.json](../../../artifacts/ru1/ru4e2/wave1c_comparison.json); receipt-hash verification is in [wave1c_receipt_validation.json](../../../artifacts/ru1/ru4e2/wave1c_receipt_validation.json). This is an ID-population comparison, not a claim that encoded scoring strings are byte-identical to raw imports.','',
      '## Packs, driver and finaliser','',
      f"Active pack root: `{n.PACK}`. This preserves the RU4E external-worktree closure guard while using the requested `sol_packs/ru4e/` suffix. Private keys and current evidence are under `artifacts/ru1/ru4e2/`; the original empty-scope RU4E artifacts are preserved. There are 16 contexts ×2, 1,359 candidate line items + 144 control line placements per round, 3,006 total reads, estimated **6.012 points** at 0.2 points / 100 reads. Probe and replacement-read costs are excluded. Controls come from the same 31 adjudicated lines / 65 positions. Each context contains 93 or 94 items, <=100; r2 reverses r1 exactly with fresh IDs. Closure passes on all 32 packs.",'',
      'Public copies contain the same native decoded mode, dimensions and pixel bytes as the original crops. PNG metadata is removed because the existing closure scanner rejects it. Each private candidate item retains original path/SHA, native pixel SHA/mode/size and the sanitized PNG SHA. Original files are unchanged. The initial metadata-bearing build was rejected before any reading; its log/keys and `/private/tmp/ru4e2/failed_metadata_packs/` are retained separately and are not driver inputs.','',
      'The shared RU4E builder gained explicit selected-ID and crop-preparation hooks; its nine-book default and all read/adjudication gates remain in place. RU4E2 imports its own SHA-bound helper copies from `scripts/secondary/ru4e2_bound/`, with both launcher and probe output roots rebound to RU4E2. Model remains gpt-6.1-sol / medium, network and external reader tools disabled. The driver probes before contexts, stops at >=70%, claims attempts exclusively and never reruns them.','',
      'Later explicit launch: `scripts/secondary/run_ru4e2_all.sh`. The completed preparation used only `scripts/secondary/run_ru4e2_all.sh --dry-run`, reporting 32 planned contexts and zero probes/reads. Offline finalisation is `scripts/secondary/ru4e2_finalize.sh`, currently **PENDING_READS**, with all 1,753 positions held. It retains canonical v4.4 scans, independent rollout/model/effort/coverage/control gates, VOID-to-r3 routing, audit 20 edit_hard + 10 keep_soft plus disagreements, and mandatory lead checks on every edit. The current empty lead template is not an adjudication result.','',
      'After readings and completed pixel checks, `scripts/secondary/ru4e2_finalize.sh --apply-lead /absolute/completed-lead.jsonl` uses the unchanged sparse-output protocol: `artifacts/ru1/ru1_v3_test_edits.jsonl`, manifest + SHA and LQB `ru1_v3_test_edits`, parent `google_raw_v2_import`, recorded split, holds and omitted-ID inheritance. Every applied edit must have two admitted independent hard calls and the lead pixel check; raw bytes may change only at the listed ь→ъ offsets. **No production edit file, manifest or LQB registration was issued.**','',
      '## The 14 LQB failures','',
      'The original command reproduces **69 passed, 14 failed** under x86_64 Python 3.11 / NumPy 1.24.3. A read-only use of the existing compatible arm64 environment at `~/Projects/greek-ocr-toolkit/.venv/bin/python` gives **82 passed, 1 failed** for the same 83 tests. No packages or environments were changed. No genuine regression in this worktree\'s LQB code was found, so **0 fixed, 14 other**, and LQB code/tests/historical receipts were left untouched.','',
      '| Test | Cause | Compatible environment |','|---|---|---|']
    for r in failures:text.append(f"| `{r['test']}` | {r['cause']} | {r['native_environment']} |")
    text+=['','The last failure must not be made green by updating historical expected hashes or relaxing custody. The four changed local sources are already allowed as superseded by that historical test; the external release-exclusions hash is the additional drift. Exact expected/current hashes are retained in [historical_input_drift.json](../../../artifacts/ru1/ru4e2/historical_input_drift.json). Full failure traces: [x86](../../../artifacts/ru1/ru4e2/lqb_x86_initial.txt), [compatible arm64](../../../artifacts/ru1/ru4e2/lqb_native_initial.txt). All 14 classified records: [lqb_failure_census.json](../../../artifacts/ru1/ru4e2/lqb_failure_census.json).','',
      '## Verification','',
      '**29 RU4E/RU4E2 tests passed**, including all 24 original fixtures, selection by OR rule, threshold/isolated-letter behavior, exact raw offsets, no whole-book scope expansion, metadata stripping with pixel identity, sampled-wave inequality, non-nine scope packing and dry-run isolation. **11 canonical scanner tests passed**. Driver dry-run, offline pending finalisation and shell syntax checks passed. These focused passes do not make the historical LQB suite green.','',
      'Commands used x86_64 Python 3.11 with `-B`, `pytest -q -p no:cacheprovider tests/test_ru4e.py tests/test_ru4e2.py`, scanner unittest discovery, and the two documented LQB interpreters with `tests/test_lqb.py tests/test_lqb3.py`. Preparation tests use synthetic fixtures; no real glyph reading was performed.','',line]
    report=m.WORK/'docs/records/labelfix/secondary/RU4E2_REPORT.md';report.write_text('\n'.join(text)+'\n')
    m.dump(A/'RU4E2_RECEIPT.json',dict(status='READY_FOR_READINGS',rows=build['rows'],books=len(books),pre_reform=13,
        candidate_positions=len(pp),candidate_lines=build['candidate_lines'],contexts_per_round=len(build['contexts']),
        budget=build['budget'],matches_wave1c=wave['matches'],lqb_failures=14,fixed=0,other=14,
        tests=dict(protocol=29,scanner=11,lqb_x86_pass=69,lqb_x86_fail=14,lqb_native_pass=82,lqb_native_fail=1),
        network=False,reader_runs=0,probes=0,git_writes=False,peer_writes=False,
        report=str(report),report_sha256=m.sha(report),last_line=line))
    print(line)

if __name__=='__main__':main()
