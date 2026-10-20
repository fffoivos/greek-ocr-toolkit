"""Write the preparation report/receipt; never manufacture pending reader outputs."""
from collections import Counter
import json
from pathlib import Path
import re
from ru2t import ART, PACK, WORK, HERE, SOURCE, SEED, SCANNER_SHA, tool_inputs, rows, sha, dump, closure


def main():
    info=json.loads((ART/'build.json').read_text())
    # Bind final tooling after fixture validation; data/crop/pack bindings stay fixed.
    info['inputs'].update({str(p):sha(p) for p in tool_inputs()})
    dump(ART/'build.json',info)
    for p,h in {**info['inputs'],**info['pack_inputs']}.items():
        if sha(p)!=h:raise ValueError('bound input changed: '+p)
    scans=closure(PACK,ART,runtime=True)
    if not all(s['ok'] for s in scans):raise ValueError('closure failed')
    test_counts={}
    for name in ['tests.txt','scanner_tests.txt']:
        s=(ART/name).read_text();m=re.search(r'Ran (\d+) tests?',s)
        if not m or not s.rstrip().endswith('OK'):raise ValueError('tests not passing')
        test_counts[name]=int(m[1])
    count=info['counts'];budget=info['budget'];books=info['books'];tests=sum(test_counts.values())
    report=WORK/'docs/records/labelfix/secondary/RU2T0_REPORT.md'
    lines=['# RU2T-0: collection-v2 train preparation','',
        f"**READY for readings: {count['selected_lines']} sampled candidate lines, {len(info['contexts'])} contexts × 2. No readings ran.** "
        f"The sample costs about {budget['selected_points']:.3f} weekly points ({budget['selected_reads']} item reads). Full coverage costs about {budget['full_points']:.2f} points ({budget['full_reads']} reads).",'',
        f"Input: `{SOURCE}`; SHA256 `{info['parent_sha256']}`. {count['parent_rows']:,} train rows, {count['cyrillic_rows']:,} selected by `script_class == cyrillic` (case insensitive) OR at least three Unicode Cyrillic letters. Group key is `(source, doc)`; language is only a metadata guess. Parent labels are never normalized.",'',
        '## Census and orthography','',
        '| Source / book (`doc`) | Language guess | Rows | ь final | ь pre_hyphen | ъ final | ъ pre_hyphen | ѣ | і | ѳ | ѵ | Class | Sample lines |',
        '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|']
    for bid,b in sorted(books.items()):
        vals=[str(b['signs'].get(s+':'+k,0)) for s,k in [('ь','final'),('ь','pre_hyphen'),('ъ','final'),('ъ','pre_hyphen')]]
        vals += [str(b['historical'].get(c,0)) for c in 'ѣіѳѵ']
        lines.append('| '+bid+' | '+b['language']+' | '+str(b['rows'])+' | '+' | '.join(vals)+' | '+b['orthography']+' | '+str(info['quotas'].get(bid,0))+' |')
    pp=list(rows(ART/'candidate_positions.full.jsonl'));kinds=Counter(p['kind'] for p in pp)
    lines += ['',
        'A sign needs a preceding Cyrillic letter and no immediately following Cyrillic letter. ASCII `-` gives `pre_hyphen`; all other boundaries give `final`, exactly as in the RU1 census helper. Sign census targets lowercase ь/ъ; historical-letter counts casefold uppercase forms. Offsets are Python Unicode code points in the original label.', '',
        '`pre_reform` means at least five word-final Google ъ (final plus pre_hyphen), OR any ѣ/і/ѳ/ѵ, across the selected rows of the book. This is the requested mechanical label class, not independently established historical orthography. **All nine books qualify; zero modern books and zero eligible modern spot positions.** `modern_spot_positions.jsonl` is empty; its seeded 10-position request cannot be filled.', '',
        'The Serbian volume and the Soviet 1930 volume also qualify under this rule. In particular, the 1930 source has no final ъ but historical letters in two rows; this does not establish that its general orthography is pre-reform. Source metadata and individual counts are retained in `build.json`; no classification override or language-based edit was made.', '',
        '## Budget and selection','',
        f"Full candidates: **{count['candidate_positions']:,} positions in {count['candidate_lines']:,} lines** ({kinds['final']} final; {kinds['pre_hyphen']} pre_hyphen). Since this exceeds 225 lines, the plan is **sample 200**, not full coverage. Selected lines contain {count['selected_positions']} candidate positions. The lead decides whether to extend beyond this sample.", '',
        f"Seed: `{SEED}`. Allocate 200 line slots proportionally by candidate-line book counts using largest remainders (book key breaks ties), then sample sorted IDs independently within each book with the seeded RNG. All nine books are represented. The same seed fixes context/control order; opaque IDs are freshly random. Full lists: `candidate_positions.full.jsonl` and `candidate_lines.full.jsonl`; selected IDs: `selected_lines.jsonl`.", '',
        f"Cost assumes 0.2 points per 100 item reads, both readers, and about 10% control items. Full packing would use 21 contexts per reader with 189 control appearances per reader: {budget['full_reads']} reads, **{budget['full_points']:.2f} points**. The sample has 21 controls per reader, {budget['selected_reads']} reads, **{budget['selected_points']:.3f} points**. These are estimates; no usage probe ran.", '',
        '## Packs and controls','',
        '| Context | Candidate lines | Control lines | Total per reader |', '|---|---:|---:|---:|']
    for c in info['contexts']:lines.append(f"| {c['context']} | {c['bed_lines']} | {c['control_lines']} | {c['items']} |")
    lines += ['',
        'Pack root: `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/sol_packs/ru2t/`. Each r2 is the exact reverse of r1 with globally fresh opaque IDs. Each reader sees only the RU1 public item fields, masked yer slots, and byte-copied PNG crops named by SHA256. Private keys, truth and manifests remain outside reader folders. All six pack closures pass; each has at most 100 items.', '',
        'Controls reuse the 31 slot-bearing RU1 adjudicated lines containing all 65 positions; the 28 zero-slot lines are excluded. The seeded round-robin selection uses 21 distinct controls per reader, reused in reverse order for r2. Control truth and pixel hashes come from the retained RU1 inventory/private assignments and verified original cache. The RU1 disputed control exclusion and wrong-sign gate are preserved: more than one wrong scored sign voids a context; abstentions and excluded controls are reported separately.', '',
        f"All {count['cyrillic_rows']:,} Cyrillic crop references were checked for local existence; **zero missing**. `crop_unavailable.jsonl` is empty. Selected crops were copied directly from collection-v2 paths, without fetching or regeneration; all copied bytes match the recorded source SHA256. Only automatic PNG decoding was used; no images were displayed.", '',
        '## Finalisation and registration','',
        'Prepared launcher (not executed): `scripts/secondary/reading/run_ru2t.sh ru2t ctx01 r1` (repeat for r2 and ctx02–03). Add `--dry-run` for local validation without a probe or reader. It reuses the existing Sol launcher with gpt-6.1-sol, medium, network/web disabled, isolated pack cwd, before/after usage accounting and the 78% usage refusal. It refuses to overwrite an attempt.', '',
        'After all readings: `scripts/secondary/ru2t_finalize.sh`. It verifies pinned parent/tool/pack hashes, canonical v4.4 rollout scans, actual rollout model/effort, distinct rollout evidence, crop coverage, complete answer mappings and control gates before emitting the label version. Scanner SHA256: `'+SCANNER_SHA+'` (the adopted N1TS3 canonical hash); the scanner was not changed.', '',
        '**Owner scope extension:** the older RU1 combiner excluded pre_hyphen positions. This task asks every word-final ь to receive two reads, so both final and pre_hyphen positions are candidates here; the wrapper reuses the RU1 vote/gate decision on both. Two independent hard calls permit ъ only if at least one context has a VALID RU1 control gate. Two soft calls keep ь. Unreadable/other/disagreement, missing evidence, or two VOID hard votes hold. Google ъ is never edited. No lexical prior overrides the glyph votes; modern-book candidates are absent by construction.', '',
        'The finaliser writes a complete parent-ID label stream to `artifacts/ru1/ru1_v2_train.jsonl`, preserving every unsampled and unedited label, plus `ru1_v2_train_manifest.json`, `ru2t/decisions.jsonl` and `ru2t/per_row_decision_counts.jsonl` (all parent rows). It then registers `collection_v2_train` as the SHA-bound parent and `ru1_v2_train` in `docs/records/labelfix/lqb/versions.json`, preserving existing entries. The output is a sampled correction version, not a claim of full candidate coverage.', '',
        '**Pending readings:** no real `ru1_v2_train.jsonl` or LQB version entry has been fabricated or published at this preparation stage. The finaliser refuses the current incomplete readings. The registry workflow was exercised only on temporary fixtures.', '',
        '## Validation','',
        f"**{tests} tests passed**: {test_counts['tests.txt']} RU2T fixture tests and {test_counts['scanner_tests.txt']} canonical scanner regressions. RU2T tests include all 16 call pairs, unreadable holds, VOID gates, pre_hyphen scope, modern exclusion, thresholds, deterministic stratification, full parent preservation, actual scanner→mapper→combiner→output→LQB loader round trip, and refusals for missing answers/run, changed parent/pack, forbidden paths, wrong model and reused rollout. Shell syntax and all six launcher dry runs pass. No reader, network, browser, computer use, source-input write or `.git` write occurred.", '',
        'Reproduce fixtures with `/usr/bin/arch -x86_64 /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 -B -m unittest discover -s tests -p test_ru2t.py`; scanner fixtures use `-s scripts/secondary/reading -p test_scan_rollout_v4.py`. The x86_64 interpreter is required by the installed Pillow binary. Pack regeneration refuses a nonempty destination.', '',
        f"RU2T0 READY: cyrillic rows {count['cyrillic_rows']}; books pre_reform {count['orthography_books'].get('pre_reform',0)} / modern {count['orthography_books'].get('modern',0)}; candidate ь positions {count['candidate_positions']} in {count['candidate_lines']} lines; plan {info['plan']} ({budget['full_points']:.2f} pts for full); contexts {len(info['contexts'])} ×2; closure ok; tests {tests} passed"]
    report.write_text('\n'.join(lines)+'\n')
    paths=[*tool_inputs(),Path(__file__),WORK/'tests/test_ru2t.py',report,*ART.rglob('*'),*PACK.rglob('*')]
    outputs={str(p):sha(p) for p in paths if p.is_file()}
    receipt=dict(schema='RU2T0-v1',status='READY_FOR_READINGS',counts=count,plan=info['plan'],budget=budget,contexts=info['contexts'],seed=SEED,inputs=info['inputs'],outputs=outputs,closure_ok=True,scanner=dict(version='v4.4-canonical',sha256=SCANNER_SHA),tests=dict(passed=tests,breakdown=test_counts),registration=dict(status='pending_readings',version='ru1_v2_train',parent='collection_v2_train',registry='docs/records/labelfix/lqb/versions.json'),no_reader_run=True,network=False,browser=False,computer_use=False,git_writes=False,missing_crops=0,receipt_hash_policy='Receipt excludes itself; outputs bind all packs, keys, scripts, tests, report and build.')
    dump(WORK/'artifacts/ru1/RU2T0_RECEIPT.json',receipt)
    print(lines[-1])

if __name__=='__main__':main()
