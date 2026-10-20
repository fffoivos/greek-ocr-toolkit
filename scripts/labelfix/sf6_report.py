"""Render the SF6 release gate report from the offline replay receipts."""
from collections import Counter
import json
from pathlib import Path
import re

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.r1_common import rows
from scripts.labelfix.sf6_measure import EV,DOC,CLASSES,KERAIA


def table(headers,values):
    def cell(x):return str(x).replace('|','\\|').replace('\n',' ')
    return ['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |',
            *['| '+' | '.join(cell(x) for x in row)+' |' for row in values]]


def vector(counts):return '/'.join(str(counts.get(k,0)) for k in CLASSES)
def arrow(a,b):return f'{a} → {b}'


def main():
    h=json.loads((EV/'heldout/metrics.json').read_text())
    dev=json.loads((EV/'m2_dev/metrics.json').read_text())
    w=list(rows(EV/'witness_results.jsonl.gz'));wm=json.loads((EV/'witness_metrics.json').read_text())
    log=(EV/'tests_after.log').read_text();passed=int(re.findall(r'(\d+) passed',log)[-1])
    priorlog=(EV/'witness_tests_before.log').read_text()
    failed=int(re.findall(r'(\d+) failed',priorlog)[-1])
    errors=int(re.findall(r'(\d+) error',log)[-1]) if re.findall(r'(\d+) error',log) else 0
    all_records=[*w,*rows(EV/'heldout/release_labels.jsonl.gz'),*rows(EV/'m2_dev/release_labels.jsonl.gz')]
    # A line appearing in SF5 and L1A is one witness, not two independent cases.
    unique={(r['mode'],r['id']):r for r in all_records}
    singles=set();punct={}
    for (mode,lid),r in unique.items():
        if r['before']['status']=='hold':continue
        bad=[c for c in r['checks'] if not c['allowed']]
        assert r['after']['status']=='hold' or not bad
        for c in bad:
            if sum(c['signals'].values())==1:singles.add((mode,lid,c['start'],c['character']))
        if r['after']['status']=='hold':
            cats={c['category'] for c in bad}&{'apostrophe','quote','keraia'}
            if cats:punct[mode,lid]=cats
    pc=Counter(c for cats in punct.values() for c in cats)
    ab=h['marks']['after']['ENSEMBLE_AB'];held=h['release_counts']['after']['ENSEMBLE_AB']['hold']
    L=['# SF6 — two positive absence signals for Google-character deletion','',
       f'Policy **`{gate.POLICY}`**. The keraia witness is **HOLD**; **{wm["quote_held"]}/{wm["quote_total"]} reviewer quote probes HOLD**. A release with an uncertified deletion becomes a whole-line HOLD. Insertions, SF5 text proposals, reader naming, agreement, observation predicates and K1 are unchanged.', '',
       f'**All-green acceptance is not met:** {passed} labelfix tests pass, with {errors} environment setup error(s). The unchanged capture test cannot bind its loopback socket in this sandbox (`PermissionError: [Errno 1] Operation not permitted`). The SF5 baseline has the same setup error with 847 passes. No test is skipped, deselected or weakened to hide it. '+('**census witnesses pending**.' if not (EV/'census_inputs.jsonl.gz').exists() else '**30 seeded census witnesses included**.'),'',
       'Launch HEAD `f267dfaa` on `opus/spellcheck`; frozen production sources are read directly from `05f2dafb` and verified byte-identical to launch. Network OFF; Mac CPU; saved evidence only; detector/R1/CTC inference 0; no `.git` or other-worktree writes. The aborted first evidence directory was renamed to `SF6_evidence_aborted_run1/` and none of its files were reused.', '',
       '## The one rule and the evidence contract','',
       'Every removed or replaced NFD character is checked at its original letter boundary. Canonical Unicode equivalence is unchanged. SF5 word-final elision aliases remain one atom, including next to real mark edits; other replacements count as deletions. Repeated signs keep their multiplicity. A spacing breathing attached as a combining mark still deletes the old spacing character, so SF6 can HOLD an otherwise valid SF5 atomic proposal.', '',
       'Combining/spacing marks require **reader AND detector**, or **reader AND recogniser text**. The coordinator’s **A∧B counts as one reader** in every mode, including PRESENCE/FULL; AE also retains its E check. Agreement is not independent print evidence. Apostrophes, quotes and numeral keraia require **detector AND recogniser text**; R1 supplies no punctuation absence signal. Other characters require a supported reader absence and a second source; no such reader head exists in the retained evidence, so these deletions HOLD.', '',
       'A reader absence needs a supported head, saved predictions from both A and B, scored coverage with a finite in-image span, a known evidence state, an empty uncertainty list, and no applicable slot/observation veto. Missing or conflicting B is not a reader absence, even if A and the detector agree. Detector absence needs an actually scored head, explicit `OBSERVED` coverage of the relevant region, a valid window, resolved localisation and segmentation, no unnamed or uncertain ink and no relevant clipping. Empty candidate lists without that evidence are UNKNOWN. The current apostrophe detector only scores word-final δ/τ/ρ/θ/π; an empty Ι, κ or μ slot is not a negative punctuation observation. Quote absence additionally needs the leading-left region observed. Keraia has no scored absence head in these saved records.', '',
       'Recogniser-text absence needs aligned letter context, a finite saved `recognition_confidence` in [0,1], a located in-image span, and no applicable uncertainty/clipping. An unscored string is not a positive absence. Its score is now included in the content-bound evidence envelope because SF6 consumes it. No missing confidence, coverage or observation state is filled in. This is evidence plumbing for the deletion rule, not a new source decision.', '',
       'Production changes: `release_gate.py` adds the deletion inventory/guard, policy id and score binding; `l1_common.overlay` records each decision and adds the whole-line HOLD before release. Existing composer functions and the SF5 text policy are byte/AST unchanged. All no-HOLD outputs retain their exact SF5 label and status. The verification checks this worktree and branch’s Git metadata separately from the shared common directory: concurrent other-worktree/branch changes and `info/refs` drift are recorded explicitly, not reported as globally unchanged. [Verification receipt](SF6_evidence/verification.json).', '',
       '## Held-out 666 — SF5 → SF6','',
       'The original instrument has 80 Google combining-mark errors, 10,046 known and 300 unknown-truth mapped/scored slots per mode. Frozen slot decisions remain identical (81,700 records). The table applies only SF6’s additional whole-line veto to those original slot scores; a failing deletion can therefore HOLD other slots on that same line. These are scores with the new release veto applied, not newly inferred reader scores. The original SF5 slot rows are the left side of each arrow. Existing SF5 line vetoes are not retroactively added to that historical slot instrument.', '',
       'The local 666-line artifact lacks full extraction coverage. Its certified frozen decisions are retained, but unavailable raw coverage is never used as positive reader absence. This is a saved-decision replay, not full runtime recomposition. Before applying SF6, all 2,664 SF5 effective line labels and statuses reproduce exactly.', '']
    rr=[]
    for mode in gate.MODES:
        a=h['marks']['before'][mode];b=h['marks']['after'][mode]
        rr.append([mode,'mark',*[arrow(a[k],b[k]) for k in ('corrected','wrong','missed','HOLD','new','lines_held')]])
        a=h['elision']['before'][mode];b=h['elision']['after'][mode]
        rr.append([mode,'elision kept/deleted/added',arrow('/'.join(str(a[k]) for k in ('kept','deleted','added')),'/'.join(str(b[k]) for k in ('kept','deleted','added'))),'—','—','—','—','—'])
        d=h['deletions'][mode]
        rr.append([mode,'deletion mark/apostrophe/quote/keraia/other',arrow(vector(d['before']),vector(d['after'])),'—','—','—','—','new HOLD '+vector(d['held'])])
    L+=table(['Mode','Row','Corrected /80, elision K/D/A or deleted characters','Wrong','Missed','HOLD errors','New','Instrument lines held /666'],rr)
    L+=['','The deletion row counts Google NFD characters removed from **released** labels, by source character class; it is not print-truth scoring. New HOLD vectors count lines, and classes can overlap. The elision row scores effective labels, retaining original Google on HOLD. Print truth covers 213 printed elisions and 5 certified absent sites on '+str(h['truth']['lines'])+'/666 lines, with 0 complete lines certified: pixel-adjudicated Wikisource text when supported by R0, otherwise the R0 adjudication. Ten quote scopes and one unresolved scope are excluded. The exact coverage and source counts are preserved in [held-out metrics](SF6_evidence/heldout/metrics.json).', '',
          'Actual whole-line release statuses, including the original Google guards:', '']
    L+=table(['Mode','Corrected lines','Unchanged lines','Held lines'],[
        [mode,*[arrow(h['release_counts']['before'][mode].get(k,0),h['release_counts']['after'][mode].get(k,0)) for k in ('corrected','unchanged','hold')]] for mode in gate.MODES])
    L+=['','Every changed mark outcome is listed below. The source parts and physical records did not change; only the SF6 whole-line veto changed the score. [Full per-slot events, including reasons](SF6_evidence/heldout/per_slot_changes.jsonl), [original slot identity proof](SF6_evidence/heldout/per_slot_proof.jsonl.gz), [line proposals, labels and absence checks](SF6_evidence/heldout/release_labels.jsonl.gz).', '']
    changes=list(rows(EV/'heldout/per_slot_changes.jsonl'))
    L+=table(['Line ID','Mode','Physical slot / recogniser start','SF5 → SF6'],[
        [r['id'],r['mode'],f"{r['before']['slot']} / {r['before']['start']}",arrow(r['before']['outcome'],r['after']['outcome'])]
        for r in changes if r['before']['outcome']!=r['after']['outcome']])
    L+=['','## M2 DEV — SF5 → SF6','',
        'Only the 273-card DEV allowlist is decoded from the cache; 0 locked stratum (ii) records are decoded or composed. There are 43 enumerated Google mark-error pairs and 212 marks-correct reference cards. B/E are missing in this cache; ensemble HOLDs remain. Complete saved runtime is replayed. Original slot decisions remain identical; the table adds only SF6’s whole-line veto, even on lines that already had a different SF5 line HOLD. That explains why slot scores can decrease while the final release counts stay unchanged.', '']
    rr=[]
    for mode in gate.MODES:
        a=dev['marks']['before']['modes'][mode];b=dev['marks']['after']['modes'][mode]
        rr.append([mode,'mark',*[arrow(a['errors'].get(k,0),b['errors'].get(k,0)) for k in ('corrected','missed','HOLD')],arrow(a['accepted_changed_slots'],b['accepted_changed_slots']),arrow(a['lines_with_HOLD'],b['lines_with_HOLD'])])
        rr.append([mode,'elision kept/deleted/added','UNKNOWN → UNKNOWN (0 certified scopes)','—','—','—','—'])
        d=dev['deletions'][mode]
        rr.append([mode,'deletion mark/apostrophe/quote/keraia/other',arrow(vector(d['before']),vector(d['after'])),'—','—','—','new HOLD '+vector(d['held'])])
    L+=table(['Mode','Row','Corrected /43, elision K/D/A or deleted characters','Missed','HOLD errors','Changed control slots','Instrument lines held /273'],rr)
    L+=['','DEV elision truth is UNKNOWN: 0 certified positive or negative sites, 0/273 lines with punctuation truth, human fields all null. No elision-accuracy claim is made. [DEV metrics](SF6_evidence/m2_dev/metrics.json), [allowlist/input receipt](SF6_evidence/m2_dev/receipt.json).', '']
    L+=table(['Mode','Corrected lines','Unchanged lines','Held lines'],[
        [mode,*[arrow(dev['release_counts']['before'][mode].get(k,0),dev['release_counts']['after'][mode].get(k,0)) for k in ('corrected','unchanged','hold')]] for mode in gate.MODES])
    L+=['','Changed DEV mark-pair outcomes, by mapped slot group (all are the new whole-line veto):','']
    changes=list(rows(EV/'m2_dev/per_slot_changes.jsonl'));rr=[]
    for r in changes:
        a=r['before'];b=r['after']
        for mode in gate.MODES:
            x=a['modes'][mode];y=b['modes'][mode]
            if x['outcome']!=y['outcome']:
                rr.append([a['id'],mode,a.get('google_nfd_letter_offsets'),arrow(x['outcome'],y['outcome'])])
    L+=table(['Card','Mode','Google NFD letter offsets','SF5 → SF6'],rr)
    L+=['','The complete per-slot control changes are linked separately: [DEV per-slot changes](SF6_evidence/m2_dev/control_slot_changes.jsonl).','',
        '## Punctuation-deletion HOLDs by class','',
        'Each cell is **newly held / all held with an uncertified attempted deletion**. The latter includes lines already held under SF5. Counts are lines per mode/cohort; classes can overlap. Punctuation uses detector AND recogniser text throughout, never R1 A+B.','']
    rr=[]
    for cohort,summary in [('held-out',h['deletions']),('M2 DEV',dev['deletions']),*[(k,v) for k,v in sorted(wm['cohorts'].items())]]:
        for mode in gate.MODES:
            if cohort in ('sf5','l1a','census') and mode!='ENSEMBLE_AB':continue
            d=summary[mode];a=d['punctuation_held'];b=d['punctuation_all_held']
            rr.append([cohort,mode,*[f'{a.get(k,0)} / {b.get(k,0)}' for k in ('apostrophe','quote','keraia','union')]])
    L+=table(['Cohort','Mode','Apostrophe','Quote','Keraia','Distinct punctuation lines'],rr)
    L+=['',f'Across all measured released SF5 line/mode identities, deduplicating overlapping witness cohorts: **{len(singles)} single-certified-source deletions released → 0**; **{len(punct)} newly held punctuation line/mode identities** (apostrophe {pc["apostrophe"]}, quote {pc["quote"]}, keraia {pc["keraia"]}). This includes all four held-out/DEV modes and all 64 synthetic reviewer probes; it is not a full-production prevalence estimate. Missing-evidence deletions are also held and are counted separately from single-certified-source cases in the machine-readable metrics.', '',
        '## SF5 and L1A regression witnesses','',
        'All 56 SF5 witnesses and all 48 L1A audit lines are listed individually. Ten SF5 lines and seven L1A lines change from release to HOLD; every other label/status is exact SF5 parity. Cohorts overlap on the six original L1A defect witnesses. Both known reader naming errors now HOLD: their saved wrong mark predictions remain unchanged. The two spacing-breathing proposals also HOLD because attachment replaces Google’s spacing character and the reader does not say that breathing is absent. [Full original/recogniser/before/after labels and source checks](SF6_evidence/witness_results.jsonl.gz), [source custody and all 48 L1A slot-parity checks](SF6_evidence/witness_inputs_receipt.json).','']
    for cohort,title in [('sf5','56 SF5 lines'),('l1a','48 L1A audit lines')]:
        L+=['### '+title,'']
        L+=table(['Line ID','SF5','SF6','Deleted characters requiring HOLD'],[
            [r['id'],r['before']['status'],r['after']['status'],', '.join(f"U+{ord(c['character']):04X} {c['category']}" for c in r['checks'] if not c['allowed']) or '—']
            for r in w if r['cohort']==cohort])
        L+=['']
    quotes=[r for r in all_records if r.get('cohort')!='quote_probe' and any(c['category']=='quote' for c in r['checks'])]
    L+=['Reviewer probe coverage: 64/64 cases HOLD across PRESENCE/FULL/AB/AE, each reproduced from the reviewer’s saved original/recogniser/mode case before applying SF6. The probe runtimes are synthetic fixtures; no invented observation is treated as scored production evidence. Additional saved quote-deletion lines are listed below (including previously held lines).','']
    L+=table(['Line ID','Mode','SF5 → SF6'],[[lid,mode,arrow(r['before']['status'],r['after']['status'])] for (mode,lid),r in sorted({(r['mode'],r['id']):r for r in quotes}.items())])
    L+=['','## Tests and reproduction','',
       f'- New SF6 suite: **{failed} failures on the frozen 05f2dafb implementation**, with the same witnesses passing on SF6. [Failing-before log](SF6_evidence/witness_tests_before.log), [SF5 + SF6 witness suite](SF6_evidence/witness_tests_after.log).',
       '- SF5 tests retain their exact composer assertions and positive controls. Only explicit deletion-release expectations change to exact HOLD checks, including unchanged effective Google bytes, no changes, and the SF6 reason. No general “either release or HOLD” assertion was substituted.',
       f'- Full labelfix suite: **{passed} passed, {errors} environment setup error(s), 0 assertion failures**. [Full result](SF6_evidence/tests_after.log), [SF5 baseline](SF6_evidence/tests_before.log). The capture test was not modified.',
       '- Coverage includes both valid two-source mark pairs, valid detector+recogniser punctuation, one-source and missing/unscored/clipped/uncertain controls, A/B-as-one, replacement deletions, multiplicity, explicit numeral signs, insertion parity, elision aliases, confidence binding and deterministic census selection.', '',
       '```sh',
       'export PYTHONPATH="$PWD" PYTHONDONTWRITEBYTECODE=1',
       'PY=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python',
       '$PY scripts/labelfix/sf6_measure.py all',
       'SF6_TEST_BASELINE=1 $PY -m pytest tests/labelfix/test_sf6.py -q -p no:cacheprovider',
       '$PY -m pytest tests/labelfix -q -p no:cacheprovider',
       '$PY scripts/labelfix/sf6_report.py',
       '$PY scripts/labelfix/sf6_verify.py',
       '# One-command census addition once the pulled evidence lands:',
       '$PY scripts/labelfix/sf6_measure.py --add-census /path/to/deletion_census.jsonl.gz',
       '```','',
       'The census addition samples 30 distinct released-deletion lines with seed 6 from sorted IDs, writes source/hash custody, adds repository regression cases, replays both pools, runs all labelfix tests and refreshes this report and verification. It accepts JSON/JSONL runtime rows or L1R2’s aggregate `CHANGES.json`; the latter samples its AB deletion-example ID pool, not the full population. Aggregate IDs require a `deletion_witness_inputs.jsonl.gz` sidecar (record+runtime), or a full `overlay_ensemble_ab.jsonl.gz` with edit evidence and Google’s original labels available locally. Missing evidence writes a pending receipt and fails loudly; no source is reconstructed from guesses. The test harness validates both formats with independent 40-row fixtures. '+('**census witnesses pending**. The read-only L1R2 report was checked at the end of this run: jobs prepared, no production job submitted and no pulled production census available; mock census counts are not substituted.' if not (EV/'census_inputs.jsonl.gz').exists() else 'The pulled census and selected IDs are bound in `census_receipt.json`.'),'',
       f'SF6 RESULT: policy sf6-release-v1; keraia witness HOLD yes; quote witnesses HOLD {wm["quote_held"]}/{wm["quote_total"]}; held-out AB corrected {ab["corrected"]}, wrong {ab["wrong"]}, new {ab["new"]}, lines held {held}; single-source deletions released {len(singles)}→0; punctuation-deletion HOLDs {len(punct)} (apostrophe/quote/keraia {pc["apostrophe"]}/{pc["quote"]}/{pc["keraia"]}); tests {passed} passed']
    (DOC/'SF6_REPORT.md').write_text('\n'.join(L)+'\n')
    print('wrote',DOC/'SF6_REPORT.md')


if __name__=='__main__':main()
