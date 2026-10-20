"""Validate saved R2C artifacts and write the reviewable inventory/report."""
import sys
sys.dont_write_bytecode=True
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image
from scripts.labelfix import r2_cards_prepare as p
from scripts.labelfix import r2_cards_resolve as r


def main():
    out=p.OUT
    roles=json.loads((out/'doc_roles.json').read_text())
    docs=roles['documents']
    assert sum(roles['role_counts'].values())==len(docs)
    # Verify the original reservation inputs have not drifted under a live
    # collector. No file locking or writes are performed in input directories.
    drift=[]
    for path,expected in roles['input_sha256'].items():
        if p.sha(Path(path))!=expected:
            drift.append(path)
    assert not drift,drift
    receipts={};allcrop={};allslots={};validations={};controlstates={}
    for deck,role in [('T2','supervision'),('T4','witness')]:
        base=out/'decks'/deck
        keys=r.read(base/'private/key.jsonl');public=r.read(base/'blind/cards.jsonl')
        reverse=r.read(base/'blind/cards_reverse.jsonl')
        assert reverse==list(reversed(public))
        assert len(keys)==len(public)==880
        assert len({k['card_id'] for k in keys})==880
        data=[k for k in keys if not k['control']];controls=[k for k in keys if k['control']]
        assert len(data)==800 and len(controls)==80
        assert all(docs[k['doc']]['role']==role for k in keys)
        pages=Counter(k['page'] for k in keys)
        assert max(pages.values())<=5
        slices=Counter(k['slice'] for k in data)
        perdoc=Counter((k['slice'],k['doc']) for k in data)
        assert all(n<=.1*slices[sl] for (sl,d),n in perdoc.items())
        if deck=='T4':
            assert len({k['doc'] for k in data})>=20
            assert sum(bool(k['paired_views']) for k in data)==50
            assert sum(len(k['paired_views']) for k in data)==150
        allcrop[deck]={k['crop_sha256'] for k in keys}
        allslots[deck]={(k['crop_sha256'],k['crop_letter_offset']+k['anchor_index']) for k in data}
        byid={k['card_id']:k for k in keys}
        for pub in public:
            key=byid[pub['card_id']]
            assert pub==key['public']
            assert pub['options']==p.options(key['mining_key'],key['anchor_index'],key['target_head'],p.SEED+key['card_id'])
            for field in ('word_image','line_image'):
                name=pub[field];assert name==p.sha(base/'blind'/name)+'.png'
                with Image.open(base/'blind'/name) as im:
                    assert not im.info
                    if field=='line_image':
                        assert list(im.size)==key['native_size']
                    else:
                        x0,y0,x1,y1=key['word_box'];scale=key['zoom_scale']
                        assert 1<=scale<=3
                        assert im.size==((x1-x0)*scale,(y1-y0)*scale)
            with Image.open(key['crop']) as im:
                original=im.convert('RGB');native=original.convert('L')
                assert p.sha(Path(key['crop']))==key['crop_sha256']
                x0,y0,x1,y1=key['word_box']
                with Image.open(base/'blind'/pub['line_image']) as full:
                    assert full.convert('RGB').tobytes()==original.tobytes()
                scale=key['zoom_scale']
                expected=original.crop(key['word_box']).resize(((x1-x0)*scale,(y1-y0)*scale),Image.Resampling.LANCZOS)
                with Image.open(base/'blind'/pub['word_image']) as zoom:
                    assert zoom.convert('RGB').tobytes()==expected.tobytes()
                a=p.np.asarray(native)<180
                assert a[:,x0:x1].any()
                assert not a[:,x0-1:x0+1].any() and not a[:,x1-1:x1+1].any()
                assert not a[0,x0:x1].any() and not a[-1,x0:x1].any()
            for view in pub.get('paired_views',[]):
                assert view['image']==p.sha(base/'blind'/view['image'])+'.png'
        cp=json.loads((base/'private/controls_proposed.json').read_text())
        assert len(cp['controls'])==80
        assert {c['card_id'] for c in cp['controls']}=={k['card_id'] for k in controls}
        for c in cp['controls']:
            assert len(c['expected_letter_heads'])==len(r.letters(c['expected_form']))
            assert [dict((h,c[h]) for h in r.HEADS) for c in c['expected_letter_heads']]==r.form_heads(c['expected_form'])
        controlstates[deck]=dict(proposed=80,lead_verified=sum(c['lead_verified'] for c in cp['controls']))
        validations[deck]=dict(cards=len(data),controls=len(controls),documents=len({k['doc'] for k in data}),
                              max_cards_page=max(pages.values()),slice_counts=slices,distinct_anchor_slots=len(allslots[deck]),
                              all_card_geometry_checks_passed=True)
        receipts[deck]=json.loads((base/'private/receipt.json').read_text())
    assert not (allcrop['T2']&allcrop['T4']), 'Cross-role crop leak'
    assert not (allslots['T2']&allslots['T4']), 'Cross-role target slot leak'
    qa=json.loads((out/'qa/manifest.json').read_text())
    assert all(v['count']==20 and p.sha(out/v['image'])==v['sha256'] for v in qa.values())
    leaks=p.leak_scan()
    coverage=json.loads((out/'geometry_coverage.json').read_text())
    attempted=sum(c.get('attempted_lines',0) for c in coverage.values())
    safe=sum(c.get('lines_with_safe_words',0) for c in coverage.values())
    words=sum(c.get('safe_words',0) for c in coverage.values())
    p.dump(out/'receipts/artifact_validation.json',dict(decks=validations,role_input_drift=drift,
            cross_role_crop_overlap=0,qa_sources=len(qa),qa_boxes=len(qa)*20,control_states=controlstates,
            coverage=dict(attempted_lines=attempted,lines_with_safe_words=safe,safe_words=words,
                          percent=100*safe/attempted),passed=True))
    # Check the frozen W1 provider/edition exclusion custody in addition to the
    # explicit per-line classes used by the reservation.
    ex=p.load(p.RUN/'exclusions_manifest.json');index=p.load(p.RUN/'exclusions_index.json')
    exreceipt=p.load(p.RUN/'exclusions_receipt.json')
    assert p.sha(p.RUN/'exclusions_manifest.json')==exreceipt['manifest_sha256']
    decisions=p.rows(p.RUN/'exclusion_decisions.jsonl')
    accepted={x['item'] for x in decisions if x['status']=='eligible'}
    wdocs={d for d,v in docs.items() if v['pool']=='W1'}
    assert wdocs<=accepted
    # Bind the decisions/edition-alias evidence without changing reservation.
    p.bind(p.RUN/'alias_resolution_evidence.jsonl')
    p.dump(out/'receipts/w1_exclusion_custody.json',dict(manifest_sha256=exreceipt['manifest_sha256'],
            eligible_w1_documents=len(wdocs),all_have_eligible_owner_decision=True,
            policy=exreceipt.get('policy'),input_sha256=p.INPUTS.copy()))
    tests=ET.parse(out/'receipts/tests.xml').getroot()
    suites=list(tests.iter('testsuite'))
    passed=sum(int(s.get('tests',0))-int(s.get('failures',0))-int(s.get('errors',0))-int(s.get('skipped',0)) for s in suites)
    assert all(int(s.get('failures',0))==int(s.get('errors',0))==0 for s in suites)
    report=['# R2C blind grader decks — 17 October 2026','',
            '**Prepared: T2 800 + 80 proposed controls; T4 800 + 80 proposed controls. No acquisition shortfalls.**',
            'Lead pixel verification of the 160 proposed controls and the geometry QA strips remains required before readers start. No reader was run; no printed truth or usable supervised targets are claimed yet.',
            '', '## Reservation and exclusions','',
            f'{len(docs)} eligible documents: validation {roles["role_counts"]["validation"]}, witness {roles["role_counts"]["witness"]}, calibration {roles["role_counts"]["calibration"]}, supervision {roles["role_counts"]["supervision"]}. Roles were persisted before geometry/mining; the input-hash recheck passed.',
            '',roles['rule'],'',
            'Collection-v2 source cells use wave:source and decade; missing years use unknown. Global largest-remainder quotas avoid reserving every singleton cell. C1 selection was absent here; the S8 copy was used after all nine available copies matched SHA-256 bd0f740258bcf64688323d3a79eb8f1ee78518bc7a8c2a491adc7766dd8adbc3.',
            '',roles['heldout_note'],
            '', 'Raw inputs: W1 25,920 rows; v2 train 214,436 rows. Eligible after all rules: W1 7,436 lines; v2 35,295 lines. Sequential exclusions are mutually exclusive and reconcile exactly; overlapping counts below show every independent rule, including zeros.',
            '', '| Rule | W1 excluded | v2 excluded |','|---|---:|---:|']
    reasons=sorted(set(k.split(':',1)[1] for k in roles['exclusion_counts_overlapping'])|{'line_admission_failed','stratum_not_c1_pass','C1_316','S8_DEV','audit100','heldout666','v2_dev_test'}|
                   {'release_'+k for k in json.loads((p.EX/'release_exclusions.json').read_text())['classes']})
    for reason in reasons:
        report.append(f'| {reason} | {roles["exclusion_counts_overlapping"].get("W1:"+reason,0):,} | {roles["exclusion_counts_overlapping"].get("v2:"+reason,0):,} |')
    report+=['','Sequential counts: `'+json.dumps(roles['exclusion_counts_sequential'],sort_keys=True)+'`.','',
             'Exclusions expand line IDs to their whole v2 documents (including namespaced/bare document aliases), and apply all release class files. The W1 owner exclusion manifest and saved eligible decisions were additionally checked for all W1 documents; that manifest carries provider/edition aliases. A renamed release class file is accepted only by its declared exact SHA-256. See doc_roles.json and receipts/w1_exclusion_custody.json.',
             '', 'Conservative scope: audit100 was excluded at whole-document level as well as by line, beyond the brief\'s minimum line exclusion. This stronger separation was fixed in the initial reservation; the sequential audit100 exclusion removes 5,224 otherwise surviving v2 lines. No slice needed backfill from those exposed documents.',
             '', 'The live owner release index gained a 1,681-line rotated-crop quality class during the final check. Its overlap with the eligible pool and with either deck is zero. Quality classes are applied at line level; evaluation cohorts also exclude documents. receipts/live_exclusion_refresh.json records the updated input custody and proves eligible line IDs and every frozen document role stayed unchanged.',
             '', '## Geometry and QA','',
             f'{safe:,}/{attempted:,} attempted supervision/witness lines have at least one safe word ({100*safe/attempted:.2f}%); {words:,} saved-geometry word candidates. The {42731-attempted:,} validation/calibration lines were reserved and not located. This is safe-word line coverage, not full-word or full-corpus OCR accuracy.',
             '', 'Provider token text anchors are joined to saved lines by case-preserving base letters and exact word count. Unsupported frames and mismatches are rejected. Discovery native_size can predate downscaling: the actual retained submitted raster determines the W1 frame. Parliament uses its saved normalized-vertices native-frame flag. No equal-width word estimates, recogniser spans, inference, teacher output, or spelling rules are used.',
             '', 'Missing disposable W1 PNGs were recreated inside this worktree by cropping retained page rasters; each reconstructed PNG matches the original crop SHA-256 byte for byte. Compressed Parliament responses use the saved t23-raw-dedup-1 representation bound to the original response hash and their own compressed-file hashes. Input files were read without locks or modifications.',
             '',f'QA: {len(qa)} source strips, 20 deterministically random word boxes each ({len(qa)*20} total), in qa/. Red boxes appear only in these private QA strips. Every selected card passed ink, clear side-boundary, unclipped top/bottom, crop hash, frame and scale checks.',
             '', '| Source | Eligible lines | Reserved | Attempted | Safe-word lines | No safe word / rejected | Words |','|---|---:|---:|---:|---:|---:|---:|']
    for source,c in coverage.items():
        report.append(f'| {source} | {c["eligible_lines"]:,} | {c.get("reserved_not_located",0):,} | {c.get("attempted_lines",0):,} | {c.get("lines_with_safe_words",0):,} | {c.get("attempted_lines",0)-c.get("lines_with_safe_words",0):,} | {c.get("safe_words",0):,} |')
    report+=['','Detailed rejection reasons per source are in geometry_coverage.json. A line can supply safe words while other words on it are refused.',
             '', 'Robustness acquisition uses neighbour_body_ink_xh >= 1.0, accent_ink_cut_fraction >= 0.05, or a token within half a crop height of either horizontal crop edge. These are selection thresholds only. Initial-diphthong breathings are classified as psili/dasia rather than crasis; final-accent mining includes the last vowel before terminal consonants.',
             '', '## Drawn cards, candidates and caps','',
             '| Deck / slice | Absent candidates | Marked candidates | Drawn absent | Drawn marked | Total | Shortfall |','|---|---:|---:|---:|---:|---:|---:|']
    for deck,rec in receipts.items():
        for sl,n in rec['drawn'].items():
            absent=rec['candidates'].get(('exact_names_absent' if sl=='exact_names' else sl)+':absent',0)
            marked=rec['candidates'].get(sl+':marked',0)
            da=rec['drawn_polarity'].get(sl+':False',0);dm=rec['drawn_polarity'].get(sl+':True',0)
            if sl=='random':
                da=dm='—'
            report.append(f'| {deck} / {sl} | {absent:,} | {marked:,} | {da} | {dm} | {n} | {rec["shortfalls"][sl]} |')
        report+=['',f'{deck}: {rec["documents"]} data documents; maximum {rec["max_cards_per_page"]} cards/page including controls. Maximum per-document slice counts: `{json.dumps(rec["max_document_per_slice"])}`. Cap rejections: `{json.dumps(rec["caps_hit"])}`. C1 error-line priority cards drawn: {rec["c1_priority_drawn"]}. Exact-name subtypes: `{json.dumps(rec["exact_name_subtypes"])}`.','']
    report+=['C1 priority uses marks=n verdicts joined through the owner key and exact crop raster equality; these are candidate error lines, not accepted printed labels or guaranteed error words. Existing C1 correction text is never shown. Candidate counts are overlapping anchor opportunities; drawn words are unique within each deck. Slice polarity is an acquisition key, not print truth.',
             '', 'T4 has 400 contrasts (100 per specified slice), 200 vowel-bearing words sampled by a uniform hash permutation subject to uniqueness/diversity caps, and 200 robustness words. Fifty robustness cards additionally show padding-only, ±1.5 degree skew, and expanded span-jitter views of the same source word. All 150 extra views retain the same witness group and add no denominator slots. Native line context remains unchanged. Sampling is constrained, so no unconstrained population inclusion probability is claimed.',
             '', '## Blinding, controls and handoff','',
             'Each card has an unboxed word zoom at an exact integer uniform scale of 1–3, plus the complete line at native pixels. HTML scrolls wide lines rather than scaling them. Public image names hash their PNG contents; public paths/manifests have opaque card IDs and no source, book, page, line, selection text, confidence, or private joins. Leak scans cover text, paths, image metadata and content-hash names and passed for both decks. Intrinsic printed text may identify a work; required native context is retained.',
             '', 'Options use base letters and punctuation only, adding alternatives for one anchor head. No provider marks are copied. Consequently other printed marks may be missing from every option: readers must then select literal transcription of the complete printed word. This deliberate limitation is explicit in each README. Literal transcription remains available for base-letter errors and misprints.',
             '', 'The complete expected control forms, complete proposed letter tuples and review images are together in each private/controls_proposed.json directory. Open private/controls_review.html for the native-pixel lead review gallery. They are PROPOSED from selection keys, not pixel-verified truth. All lead_verified flags remain false; the resolver refuses to consume real readers until every control is verified. The deck-level controls_proposed.json is an index to that private key. All 80 controls per deck are excluded from truth/inventory denominators.',
             '', 'Pass only decks/T2/blind/ or decks/T4/blind/ to readers. Reader 1 uses cards.jsonl / index.html; reader 2 independently uses cards_reverse.jsonl / reverse.html. Preserve all source/private directories outside reader access. Tranche 3 was not built; its documents remain reserved.',
             '', '## Resolution and usable inventory','',
             'r2_cards_resolve.py accepts two reader JSONL files and optional reader 3. It enforces assigned IDs/order, rejects inconsistent literal/head tuples, gates each batch at at most one control error, and omits every failed batch. Disagreements produce tiebreak/blind/cards.jsonl with re-randomised option identities and a separate private option map; controls are included for the third-reader gate. Third answers must use that new map. At least two matching votes are required. Ownership failures, undecided heads, absent votes and unresolved forms remain unknown.',
             '', 'Truth records complete printed forms and explicitly voted four-head targets. Omitted non-anchor targets remain unknown even if their transcription looks unmarked. Inventory counts distinct (crop SHA-256, crop-relative letter index), using the word offset so separate words on the same crop do not collapse. It reports complete targets, unknown targets and target-head absent/marked counts by deck and slice. Repeated views never multiply slots. No truth file is emitted for these ungraded real decks.',
             '', 'Example after control verification:','',
             '```sh',
             'PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/r2_cards_resolve.py --deck docs/records/labelfix/spellcheck/R2/decks/T2 --reader1 r1.jsonl --reader2 r2.jsonl --out docs/records/labelfix/spellcheck/R2/resolved/T2',
             '```','',
             '| Deck | Data cards prepared | Controls proposed | Actual readings | Tiebreak readings | Actual Opus tokens | Usable printed slots |',
             '|---|---:|---:|---:|---:|---:|---|',
             '| T2 | 800 | 80 | 0 | 0 | 0 | pending independent readers |',
             '| T4 | 800 | 80 | 0 | 0 | 0 | pending independent readers |','',
             'Initial forecast: 3,520 card readings including controls, plus disagreements. The 150 additional paired views add visual work but no independent source cards. The resolver sums reported input/output tokens and labels missing usage unknown; synthetic test usage is never reported as real Opus usage.',
             '', '## Validation and provenance','',
             f'{passed} tests passed (tests/test_r2_cards.py, tests/test_docai.py, tests/test_harvest_admission.py); none modified or weakened. Synthetic integration exercises agreement, strict reverse order, >1-control batch rejection, one allowed control error, unverified-key refusal, re-keyed tiebreak resolution, UNKNOWN preservation, explicit ownership masking, inconsistent tuple refusal, crop-relative distinct slot counts and exact saved crop reconstruction.',
             '', 'Artifact validation passed: 1,760 cards, every selected pixel/geometry/hash/scale check, role disjointness, zero cross-deck crop overlap, diversity caps, 50 repeated T4 witnesses, all QA strips and both leak scans. Receipts and copied S8 reference code are in receipts/. Those reference files are never imported; runtime code uses only standard library, Pillow and NumPy.',
             '', 'Observed checkout: opus/r2-cards at 339e221ba3baddc8e43f88647fb19ab17d635b9a (R2 brief), directly after plan 52f34de9. No Git writes, network, recogniser/reader/detector inference, Clariden, or writes/locks in any input worktree were performed. All generated files are inside this worktree.',
             '', 'Acquisition shortfalls: none. Readiness limitation: lead pixel verification of proposed controls and QA, followed by independent readers; usable truth counts remain pending.']
    (out/'R2C_REPORT.md').write_text('\n'.join(report)+'\n')
    p.dump(out/'receipts/opus_usage_pre_readers.json',dict(T2=dict(cards=800,controls=80,readings=0,tiebreaks=0,tokens=0),T4=dict(cards=800,controls=80,readings=0,tiebreaks=0,tokens=0)))
    p.dump(out/'receipts/validation_inputs.json',p.INPUTS)
    print(f'R2C READY: docs {len(docs)} (val {roles["role_counts"]["validation"]} / witness {roles["role_counts"]["witness"]} / calib {roles["role_counts"]["calibration"]} / supervision {roles["role_counts"]["supervision"]}); T2 800+80 controls; T4 800+80 controls; geometry coverage {safe}/{attempted} ({100*safe/attempted:.2f}%); shortfalls none; tests {passed} passed')


if __name__=='__main__':
    main()
