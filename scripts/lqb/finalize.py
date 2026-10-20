"""Write the v1.1 sample-aware report and receipt after offline validation."""
from collections import Counter
import json
from pathlib import Path
import re
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.labelfix.lqb import DEFAULT, ROOT, GROUPS, sha256, dump, intro_sentences, measurement_text


def main():
    def read(name):return json.loads((DEFAULT/name).read_text())
    m=read('truth_v1.manifest.json');s=read('score_v1.json');sheet=read('scoreboard_build.json');validation=read('validation/checks.json')
    assert s['truth_sha256']==m['sha256']==sha256(DEFAULT/'truth_v1.jsonl')
    changed=[p for p,h in m['inputs'].items() if sha256(p)!=h];assert not changed,changed
    tests=(DEFAULT/'tests_v1.txt').read_text();match=re.search(r'(\d+) passed',tests);assert match and 'failed' not in tests
    ntests=int(match[1])
    lines=['# Label Quality Scoreboard v1.1','',*intro_sentences(s),'',f"Frozen truth: {m['items']:,} scoped items; tiers {m['tiers']}; {m['conflicts']} conflicts. Truth SHA256 `{m['sha256']}`.",'',f"[Scoreboard](scoreboard.html): {sheet['cards']} cards, {sheet['bytes']/1e6:.2f} MB. [Scores](score_v1.json), [manifest](truth_v1.manifest.json), [receipt](LQB1_RECEIPT.json).",'', '## Sample contract','',
    '`uniform` means a seeded uniform draw from a stated population. `enriched` means selected faults, contrasts or controls. `decision_audit` means selected from a version’s decisions. `locked_stratum` identifies a frozen evaluation stratum. Only uniform and eligible locked-stratum rows print a POPULATION error rate. Mixed aggregates never print one. The selected i-a word scopes explicitly disable population rates despite their locked-stratum label. All other measurements describe errors on the sample; these are not errors per 100 lines.',
    '', 'Document bootstrap intervals resample documents intact, 4,000 replicates, seed 20261017; intervals on selected samples are descriptive and do not undo selection. Degenerate intervals do not prove population equality. Decision-precision intervals are Wilson diagnostics conditional on sampled decisions, not population-error estimates. Audit100 samples sf6 releases, so a Google row on it describes Google correctness conditional on sf6 selection, not Google release precision.',
    '', '## A+B scores by sample type','',
    'Only covered out-of-sample, non-regression items enter measurements. `n` is known opportunities (marks heads, N1 gaps, or letters), not full lines. In-sample/regression/uncovered counts remain separate in the JSON. Owner39 never enters a headline. Sample types are split before display; no selected audit is pooled into a population rate.',
    '', '| class | version | sample_type | measurement | in-sample items | regression items | uncovered |','|---|---|---|---|---:|---:|---:|']
    for cls in GROUPS:
        for name,v in s['versions'].items():
            r=v[cls+'|A+B']
            for typ,row in (r['by_sample_type'] or {'not measured':r}).items():
                lines.append(f"| {cls} | {name} | {typ} | {measurement_text(row)} | {row['in_sample']['items']} | {row['regression_only']['items']} | {row['uncovered']} |")
    lines+=['','## Paired comparisons','','B−A is reported in errors per opportunity on the common sample. Only eligible population pairs additionally carry per-100 rates in JSON. Both versions’ in-sample items and regression items are excluded.','', '| class | A → B | sample_type | common items | A errors → B errors | B−A on the sample | document 95% interval |','|---|---|---|---:|---|---|---|']
    for pair,values in s['paired'].items():
        for cls in GROUPS:
            p=values[cls+'|A+B'];ci=p['delta_ci95'];delta=p['delta_per_opportunity']
            lines.append(f"| {cls} | {pair} | {p['sample_type']} | {p['items']} | {p['a_errors']} → {p['b_errors']} | {delta:.6f} | [{ci[0]:.6f}, {ci[1]:.6f}] |" if ci else f"| {cls} | {pair} | {p['sample_type']} | 0 | — | not measured | — |")
    lines+=['','## Truth inventory','','| set | tier | sample_type | sample description |','|---|---|---|---|']
    for name,source in m['sources'].items():lines.append(f"| {name} | {source['tier']} | {source['sample_type']} | {source['sample_description']} |")
    lines+=['','## Letters evidence decision','',
    '**Added one tier-A letters truth set: `R0_ia_letters`, `sample_type=locked_stratum`.** It contains only 24 AGREED word-card scopes, 125 known printed letters on 23 distinct lines within the 133-line i-a cohort. There are zero certified complete lines. [R0 report, lines 3–16](../spellcheck/R0_REPORT.md#letter-errors-on-adjudicated-word-card-slots) states the coverage and disagreement enrichment. [R0c input contract](../../briefs/R0c_scoring.md) identifies completed R0b truth, 24 AGREED plus 3 excluded controls, private keys and raw answers. [R0 reader plan](../../briefs/R0_recogniser_audit.md) specifies two blind Opus readers against pixels. [Completed i-a verdicts](../spellcheck/R0_expected_truth_ia.json), [scope keys](../spellcheck/R0_adjudication_private/ia/items_key.json), and [per-word inventory](../spellcheck/R0_evidence/scoring/letter_units.jsonl) bind the retained literal forms. These existing adjudications are reused; no new reading occurred.',
    '', '**Edition-normalisation caveat:** aligned Wikisource text is a reference transcription, not automatic pixel truth. NFC/whitespace and formatting/variant cleanup are documented in [source READS, lines 11–15](../../harvest/wikisource/READS.md). The [i-a source records](../spellcheck/R0_locked_set.jsonl) explicitly label the human text “Wikisource reference; not yet pixel-adjudicated”. Literal R0 pixel rulings override that reference only within certified scopes. The remaining i-a line spans remain reference transcription, not pixel truth. i-a has 131/133 v2-val overlap and one book supplies 122/133 lines ([R0 report, lines 199–201](../spellcheck/R0_REPORT.md)); it is selection-exposed and cannot establish general letter accuracy.',
    '', '**i-b: reference transcription, not pixel truth.** The source registry has 1,246 harvest lines; the R0 locked subset has 400 lines. [R0 report, lines 216–255](../spellcheck/R0_REPORT.md) says print truth remains PENDING and two independent readers plus pixel tiebreak are required. [i-b expected truth](../spellcheck/R0_expected_truth_ib.json) remains unadjudicated. No i-b reference label enters truth. The [T7b source receipt](/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-sol-wsr0/docs/harvest/wikisource_r0/RECEIPT.md), lines 39–45 and 189–210, records finite preparer QA: 20 candidates inspected, 3 source/print discrepancies excluded and 17 retained examples with no discrepancy identified. It explicitly does not certify every glyph. This supplies extraction/source QA, not a tier-A/B adjudicated letter-scope inventory; those examples are not silently promoted.',
    '', '**Version coverage:** all 24 i-a scopes are absent from the registered W1 versions, so letters are not measured in this scoreboard. Truth availability does not authorize substituting the R0 recogniser stream for an LQB version. Reference scopes are anchored to base-letter spans in the frozen i-a Google text; the builder verifies the census and exact span, and the scorer maps those boundaries across version changes.',
    '', '## Retained safeguards and unresolved sources','',
    'Deduplication is `(line_id, slot, class)`; contradictory truth excludes the key. Equal truth unions provenance and contamination. Different sampling types merging on one key conservatively become enriched. Unknown/unreadable items remain absent. The owner ἤγε → ἦγε overlay is applied symmetrically before deduplication. RU1 review and original yer controls are in-sample for ru1_v1; RU1 audit is not. N1 truth excludes held/show-through cells and carries `n1_*` contamination. T2 is supervision, not an exclusion holdout. Exclusion ids are a handoff only; none were registered.',
    '', 'Google, W1, RU1 and masked-admission membership remain defined by [versions.json](versions.json). Masks are a sibling admission branch, not a new RU1 text repair. sf6 remains remote_unfetched; no network action was attempted. Marks use peer union alignment and known head opportunities; inserted letters have unknown marks. N1 uses digit-anchored gap classes. Letters ignore combining diacritics and count base-letter edits only in certified spans. All source hashes are bound in the manifest.']
    for issue in m['issues']:lines.append('\n- **'+issue['set']+'**: '+issue['reason']+'.')
    lines+=['','## Reproduction and receipt','', '```sh', 'export PYTHONDONTWRITEBYTECODE=1', 'export TMPDIR="$PWD/docs/records/labelfix/lqb/validation/tmp"','PY=../greek-ocr-toolkit-sol-collect/.venv/bin/python', '$PY -B scripts/lqb/build_truth.py > docs/records/labelfix/lqb/truth_build_v1.log', '$PY -B -m greekocr.labelfix.lqb trend --output docs/records/labelfix/lqb/score_v1.json', 'PYTHONPATH=../greek-ocr-toolkit-cleanup $PY -B scripts/lqb/build_scoreboard.py', '$PY -B -m pytest tests/test_lqb.py -q --basetemp=docs/records/labelfix/lqb/validation/pytest_tmp > docs/records/labelfix/lqb/tests_v1.txt', '$PY -B scripts/lqb/validate_scoreboard.py', '$PY -B scripts/lqb/finalize.py','```','',
    f"LQB1b tests: **{ntests} passed** ([log](tests_v1.txt)). Revalidated {len(m['inputs'])} input hashes and truth/score equality. Structural validation decoded all {validation['decoded_pngs']} embedded images, verified {sheet['cards']} cards and disabled remote notes. Visible browser layout was not reverified in LQB1b; structural checks do not establish visible correctness.",
    '', 'LQB1b: network OFF; zero new readers, recogniser/inference runs, .git writes, peer/collector writes or external publication. All temporary writes use this worktree, including TMPDIR and pytest basetemp. The predecessor LQB1 receipt documented system-temp deviations; they were not repeated in LQB1b.']
    # Preserve the separately validated LQB2 amendment when rebuilding v1 tables.
    report=DEFAULT/'SCORE_v1.md'
    previous=report.read_text() if report.exists() else ''
    amendment=previous.split('\n## LQB2\n',1)
    if len(amendment)==2:lines+=['','## LQB2',amendment[1].strip()]
    report.write_text('\n'.join(lines)+'\n')
    outputs=['truth_v1.jsonl','truth_v1.manifest.json','conflicts.jsonl','truth_v1_exclusion_ids.txt','versions.json','score_v1.json','SCORE_v1.md','scoreboard.html','scoreboard_build.json','scoreboard_cards.json','tests_v1.txt','truth_build_v1.log','validation/checks.json']
    code=[ROOT/'greekocr/labelfix/lqb.py',*sorted((ROOT/'scripts/lqb').glob('*.py')),ROOT/'tests/test_lqb.py']
    receipt=dict(schema='LQB1b-receipt-v1.1',status='ready_for_lead_review_with_explicit_source_gaps',network=False,new_readers=0,inference_runs=0,git_writes=False,peer_worktree_writes=False,collector_writes=False,temporary_write_deviations=[],temporary_root=str(DEFAULT/'validation/tmp'),remote_fetched=False,truth_items=m['items'],tiers=m['tiers'],exclusion_ids=m['exclusion_ids'],exclusions_registered=False,classes=m['classes'],conflicts=m['conflicts'],sample_type_counts=m['sample_type_counts'],letters_truth=m['letters_truth'],scoreboard=sheet,tests_passed=ntests,input_hashes_revalidated=len(m['inputs']),source_gaps=m['issues'],validation=validation,artifacts={n:dict(sha256=sha256(DEFAULT/n),bytes=(DEFAULT/n).stat().st_size) for n in outputs},code={str(p.relative_to(ROOT)):sha256(p) for p in code})
    dump(DEFAULT/'LQB1_RECEIPT.json',receipt)
    print(json.dumps(dict(samples=m['sample_type_counts'],letters=m['letters_truth'],MB=sheet['bytes']/1e6,tests=ntests)))

if __name__=='__main__':main()
