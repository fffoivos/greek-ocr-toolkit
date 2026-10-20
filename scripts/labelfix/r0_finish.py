"""Assemble the R0a handoff. No adjudication, tuning, network, or model forward."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
from collections import Counter,defaultdict
import base64
import html
import io
import json
import os
from pathlib import Path
import unicodedata as U
os.environ['PYTHONDONTWRITEBYTECODE']='1'
os.environ['GIT_OPTIONAL_LOCKS']='0'
from PIL import Image
from scripts.labelfix.r0_prepare import (ROOT,OUT,WORK,read,write,dump,sha,all_locked,
    bare,letters,QUOTES,SEED,CKPT,line_sources)
from greekocr.labelfix.ctc_align import Alignment
from greekocr.labelfix.sheet import load_alignments,crop_key
from greekocr.labelfix.candidates import align_chars
from greekocr.labelfix.text import nfd,nfc

def make_ledger():
    spans=read(WORK/'span_slots.jsonl.gz')
    cards=json.loads((OUT/'R0_adjudication_private/items_key.json').read_text())
    ledger=[]
    for r in spans:
        if r['outside_blob']:
            ledger.append(dict(type='ctc_span_centre_outside_assigned_blob',DATA_MODEL=None,
                classification_status='PENDING_R0c_CAUSAL_REVIEW',line_id=r['line_id'],slot=r['slot'],
                slot_coordinate='NFD_offset',
                observation_confirmed=True,recogniser_letter_error_confirmed=False,
                evidence=r,reason='Native CTC centre is outside the clean runtime-assigned component; glyph identity and label causation are not adjudicated.'))
    for r in read(WORK/'R1_unmapped_715.jsonl'):
        ledger.append(dict(type='R1_frozen_instrument_unmapped',DATA_MODEL=None,
            classification_status='MAPPING_AVAILABILITY_NOT_LETTER_ERROR',line_id=r['line_id'],slot=r['slot'],
            slot_coordinate='NFD_offset',
            observation_confirmed=True,recogniser_letter_error_confirmed=False,
            evidence=dict(reason=r['reason'],detail=r['mapping_detail'],frozen_overlap_count=r['frozen_overlap_count']),
            detail_file='R0_evidence/R1_unmapped_715.jsonl'))
    for c in cards:
        if c['control']:continue
        for kind in c['kinds']:
            ledger.append(dict(type=kind,DATA_MODEL=None,classification_status='PENDING_R0b_PRINT_TRUTH_AND_R0c',
                line_id=c['line_id'],slot=c.get('frozen_slot',c['start']),slot_coordinate='frozen_slot' if 'frozen_slot' in c else 'NFD_offset',
                card_id=c['id'],observation_confirmed=True,recogniser_letter_error_confirmed=False,
                evidence='Reference disagreement or detector punctuation proposal; see private key after blind reading.'))
    write(OUT/'R0_failures.jsonl',ledger)
    # These are truth-dependent result fields, never substitute zeros for rates.
    controls=[r for r in cards if r['control']]
    dump(OUT/'R0_result_placeholders.json',dict(phase='R0a',
        letter_truth=dict(source='Pending R0b pixel adjudication; Wikisource/M2 references and owner notes are not full-line truth',
                          full_lines=0,full_line_slots=0,
                          control_words=len(controls),control_word_letter_positions=sum(len(letters(r['known_answer'])) for r in controls)),
        letter_error_pct=None,letter_error_case_folded_pct=None,
        letter_errors_by_book=None,letter_errors_by_type={k:None for k in ('substitution','insertion','deletion','case','script_mixup')},
        case_recogniser_right_pct=None,case_extrapolated_count=None,
        apostrophe_print_positive_positions=None,apostrophe_recogniser_emitted_pct=None,apostrophe_google_present_pct=None,
        DATA_types=None,MODEL_types=None,
        instruction='R0c must fill these only after the independent readers and control checks. Never calculate letter accuracy against Google.'))
    examples=defaultdict(list)
    for r in ledger:
        if r['line_id'] not in examples[r['type']]:examples[r['type']].append(r['line_id'])
    dump(WORK/'failure_type_placeholders.json',dict(
        types=[dict(type=t,observations=sum(r['type']==t for r in ledger),
            confirmed_print_failure_count=None,DATA_MODEL=None,classification_status='PENDING_R0c',
            example_line_ids=examples[t][:3],evidence='R0_failures.jsonl; R0_cards; training_label_frequencies.json',
            training_arm=None) for t in sorted(examples)],
        caveat='Counts are observations/candidates, not confirmed recogniser errors. Some rare candidate types have fewer than three line ids; do not invent examples.'))
    return ledger

def make_punctuation_inventory():
    held=read(WORK/'continuity_666.jsonl');locked,_=all_locked()
    rows=[]
    for l in held+locked:
        for source in ('model','google','human'):
            if l.get(source) is None:continue
            for pos,ch in enumerate(nfd(l[source])):
                if ch in QUOTES+'…′″':
                    rows.append(dict(line_id=l['line_id'],source=source,NFD_offset=pos,symbol=ch,
                        codepoint=f'U+{ord(ch):04X}',print_truth=None,
                        source_status='reference/emission only; not pixel truth'))
    write(WORK/'punctuation_emissions.jsonl',rows)
    dump(WORK/'punctuation_summary.json',dict(
        raw_emission_counts={s:dict(Counter(r['symbol'] for r in rows if r['source']==s)) for s in ('model','google','human')},
        print_conditioned_recogniser_recall=None,print_conditioned_google_presence=None,
        status='PENDING_R0b',warning='Raw counts compare different reference coverage and are not punctuation accuracy or a truth-positive denominator.'))

def review_page(ledger):
    held=read(WORK/'continuity_666.jsonl');locked,la=all_locked()
    sources={l['line_id']:l for l in held+locked}
    for l in line_sources():
        if 'ξa' in nfc(l['model']):sources[l['line_id']]=l
    cache=load_alignments(ROOT/'.cache/labelfix/align_s0.jsonl')
    allspans=read(WORK/'span_slots.jsonl.gz');categories=defaultdict(list)
    for r in ledger:categories[r['type']].append(r['line_id'])
    for s in allspans:
        if s['status']!='clean_one_blob_one_character':categories[s['status']].append(s['line_id'])
        if s['script_class']=='Latin':categories['Latin'].append(s['line_id'])
    chosen=[]
    # Round robin avoids a page filled only with the most common category.
    pools={k:list(dict.fromkeys(v)) for k,v in categories.items()}
    for i in range(60):
        for k,pool in sorted(pools.items()):
            if i<len(pool) and pool[i] not in chosen:chosen.append(pool[i])
            if len(chosen)==60:break
        if len(chosen)==60:break
    parts=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>R0a recogniser position review</title><style>body{margin:20px;background:#f4f2ed;color:#211e18;font:16px system-ui}main{max-width:1200px;margin:auto}article{padding:15px;margin:20px 0;background:white;border:1px solid #ccc}.crop{overflow-x:auto;background:white}.crop svg{display:block;max-width:none}.text{font:22px Georgia;overflow-wrap:anywhere}small{overflow-wrap:anywhere}textarea{width:98%;height:64px}h1{font-size:28px}label{display:block;margin-top:10px}</style><main>
<h1>R0a recogniser position review</h1><p>Pre-adjudication preview, 60 lines. Thin boxes show native cached CTC character spans, including combining marks and spaces. Letter truth and DATA/MODEL decisions remain pending. Google is shown as a reference. Notes autosave locally; the track lead publishes the final R0c page.</p><button id="export">Export owner notes</button>''']
    selections=[]
    for lid in chosen:
        l=sources[lid];al=la.get(lid) or cache[crop_key(l['crop'])]
        with Image.open(l['crop']) as im:
            w,h=im.size;buf=io.BytesIO();im.save(buf,format='PNG');data=base64.b64encode(buf.getvalue()).decode()
        tags=[k for k,v in categories.items() if lid in v]
        selections.append(dict(line_id=lid,categories=tags,native_ctc_text=al.prediction,
            recorded_prediction_differs=al.prediction!=nfd(l['model'])))
        parts.append(f'<article data-line="{html.escape(lid)}"><h2>{html.escape(lid)}</h2><small>{html.escape(", ".join(tags))} · all results unadjudicated</small>')
        parts.append(f'<div class="crop"><svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Line crop and CTC character spans" width="{w}" height="{h+24}" viewBox="0 -24 {w} {h+24}"><image href="data:image/png;base64,{data}" x="0" y="0" width="{w}" height="{h}"/>')
        for s in al.spans:
            label='␠' if s.char.isspace() else '◌'+s.char if U.category(s.char).startswith('M') else s.char
            parts.append(f'<rect x="{s.x0:.2f}" y="0" width="{max(.1,s.x1-s.x0):.2f}" height="{h}" fill="none" stroke="#ba463f" stroke-width=".6"/><text x="{(s.x0+s.x1)/2:.2f}" y="-5" text-anchor="middle" font-size="13" fill="#702a25">{html.escape(label)}</text>')
        parts.append('</svg></div>')
        parts.append('<p>Google</p><div class="text">'+html.escape(nfc(l['google']))+'</div>')
        parts.append('<p>Our recogniser (native CTC)</p><div class="text">'+html.escape(nfc(al.prediction))+'</div>')
        if al.prediction!=nfd(l['model']):parts.append('<p>Stored instrument prediction</p><div class="text">'+html.escape(nfc(l['model']))+'</div>')
        parts.append(f'<label>Owner note<textarea data-id="{html.escape(lid)}" placeholder="Letters, case, apostrophe or span position"></textarea></label></article>')
    parts.append('''</main><script>const k='r0-owner-position-v1';const notes=JSON.parse(localStorage.getItem(k)||'{}');for(const t of document.querySelectorAll('textarea')){t.value=notes[t.dataset.id]||'';t.oninput=()=>{notes[t.dataset.id]=t.value;localStorage.setItem(k,JSON.stringify(notes))}}document.querySelector('#export').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(notes,null,2)],{type:'application/json'}));a.download='R0_owner_position_notes.json';a.click()};</script></html>''')
    (OUT/'R0_review_positions.html').write_text('\n'.join(parts))
    write(WORK/'review_selection_60.jsonl',selections)

def report():
    summary=json.loads((WORK/'span_summary.json').read_text())
    split=json.loads((OUT/'R0_newsource_split_receipt.json').read_text())
    fresh=json.loads((WORK/'fresh_pool_inventory.json').read_text())
    lock=json.loads((OUT/'R0_locked_set_receipt.json').read_text())
    card=json.loads((WORK/'cards_receipt.json').read_text())
    r1=json.loads((WORK/'R1_unmapped_summary.json').read_text())
    case=json.loads((WORK/'case_sampling_receipt.json').read_text())
    freq=json.loads((WORK/'training_label_frequencies.json').read_text())
    bind=json.loads((WORK/'input_binding.json').read_text())
    align=json.loads((WORK/'alignment_receipt.json').read_text())
    p=summary['pooled'];outside=p['outside_pct']
    notes=read(WORK/'owner_letter_punctuation_evidence.jsonl')
    controls=read(WORK/'controls_pixel_verified.jsonl')[:card['controls']]
    keys=json.loads((OUT/'R0_adjudication_private/items_key.json').read_text())
    held=read(WORK/'continuity_666.jsonl');heldids={r['line_id'] for r in held}
    covered={r['line_id'] for r in keys if not r['control'] and r['line_id'] in heldids}
    lines=['# R0 recogniser audit — R0a handoff', '',
        '**Letter truth first:** no full line in the 666-line continuity instrument or the 200-line new-source locked stratum has newly adjudicated complete print-letter truth in this phase (0 full lines / 0 full slots certified). Wikisource supplies human reference text for all 666 continuity lines; M2 supplies existing blind verdicts for the new-source lines, not complete transcriptions. Owner notes supply partial observations, not a replacement full-line transcription. No letter error rate is calculated against Google or any unadjudicated reference.', '',
        f"Planted controls have preparer-verified base letters and case for {len(controls)} isolated words ({sum(len(letters(r['correct'])) for r in controls)} letter positions); they are quality checks, not an accuracy sample. {len(covered)} of the 666 lines have at least one non-control adjudication card. Completing a word card does not certify the rest of its line. R0b can record a full-line letter transcription; R0c must report exactly which full lines/slots have truth, retaining the risk of shared errors in three-way agreement.", '',
        '**Status: R0a independent work ready; required Wikisource stratum (i) is pending a scope decision/additional books. Do not call the complete two-stratum audit READY.** R0b and R0c have not run. The expected truth, error rates, case winner/extrapolation, print-conditioned apostrophe rates and causal DATA/MODEL decisions remain null.', '',
        '## Fresh-book feasibility and frozen sets','',
        'The specified local harvest has 20 Greek books. The 14 continuity books and three detector DEV books exclude 17. The remaining three are original harvest `dev` books (distinct from the detector DEV books). No fourth or fifth fresh Greek book exists in this pool; ten additional fresh books are Russian and are ineligible. The referenced E3 human prediction file covers only the existing 17 Greek instrument books, so it cannot supply fresh-book recognitions.', '',
        '| Fresh Greek book | Harvest split | Human-aligned lines, before admission | Admitted polytonic candidate lines |',
        '|---|---|---:|---:|']
    for b in fresh['books']:lines.append(f"| {b['book']}: {b['title']} | {b['source_split']} | {b['human_aligned_lines']} | {b['eligible_lines']} |")
    lines += ['', 'Thus at most 235 human-aligned lines exist before admission/script checks, and 133 candidates remain after admission, one-to-one human alignment, existing crop and explicit polytonic-mark checks. Crops are whole admitted line crops; pixel completeness remains subject to adjudication. No selection depends on recogniser accuracy. The requested ≈300–500 lines / ≥5 books cannot be met offline. No candidate stratum was silently frozen or forwarded through CTC. `R0_locked_set.jsonl` is intentionally empty; its receipt says `PENDING_SCOPE_DECISION`. The question about accepting an undersized set remains unanswered.', '',
        f"Stratum (ii): **200 locked lines / {len(split['locked_sources'])} sources**, seeded {SEED}, from 409 eligible measured polytonic M2 cards; 200/409 is 48.9%, capped at the requested 200. **273 remaining measured cards form DEV** (including 40 modern-source cards and other cards without explicit polytonic evidence). The 40 unmeasured Cyrillic cards do not enter either list. All 473 measured cards are accounted for exactly once. The locked and DEV lists contain line ids; `R0_newsource_exclusion_ids.txt` contains the 200 frozen training exclusions. DEV and locked are a line split and share documents; document-disjointness between these two pools is not claimed.", '',
        'Selection requires a non-modern/non-Cyrillic source and a breathing, grave, circumflex or subscript in Google or recogniser text, and no Cyrillic codepoint. This script filter may enrich marked text and is not an unbiased source-population estimate. Mixed Greek/Latin cards are retained; monotonic-only cards are excluded from the lock.', '',
        '**Never tune:** the locked strata judge L1 and wave 1c from now on, never policy/checkpoint/threshold selection, never training. The 666 remain the continuity instrument. All M2 cards had already been used as S7 qualification targets; this freeze cannot undo that prior exposure.', '',
        '### Zero-intersection receipt','',
        'The L1 manifest was copied read-only from the specified worktree and checked byte-for-byte against commit `6b91ebaa`. For the 200 new-source locked rows, intersections against 666, detector DEV and L1 input are all **zero** for line ids, document ids and normalized document stems; exact crop hashes also have zero overlap with 666/DEV and the development remainder. Source cards, key line ids, Google labels and crop bytes were checked against the original blind-card files. Cross-stratum (i)/(ii) exclusion is **PENDING**, because stratum (i) does not yet exist; no vacuous zero is advertised as a completed receipt. Identifier checks cannot exclude undocumented copies of the same edition across archives.', '',
        '[Frozen split receipt](R0_newsource_split_receipt.json) · [Fresh pool inventory](R0_evidence/fresh_pool_inventory.json) · [L1 manifest copy](R0_evidence/L1_input_documents.txt) · [Input hashes](R0_evidence/input_binding.json)', '',
        '## Native CTC span placement, all alphabetic slots','',
        f"**{p['outside']} / {p['clean_slots']} clean slots = {outside:.4f}% outside their assigned blob** across {len(held)+align['locked_crops']} lines. Every emitted alphabetic slot is retained in the census: {p['all_alphabetic_slots']} total. Fused slots: {p['statuses'].get('fused_multi_character_blob',0)}; split slots: {p['statuses'].get('split_character_multi_blob',0)}; no letter blob: {p['statuses'].get('no_letter_blob',0)}. These are slot counts, not distinct blob counts.", '',
        'Method: run the unchanged native detector `ink.analyse`, `case.estimate_font`, `segmentation.recogniser_slots`, and `case.prepare` with the actual cached CTC prediction. A clean slot owns exactly one native connected component and no other character owns that component, with neither fusion, split-union nor unknown localisation. The reference is its native component bbox, not a CTC-derived partition. Outside means `(x0+x1)/2` is outside `[blob.x0, blob.x1)`. The assignment still uses the runtime overlap rule: it is not independent pixel truth for glyph identity. Do not interpret this geometry diagnostic as a letter error rate or a causal training-label verdict.', '',
        'Actual cached predictions are used for span measurement; **10 continuity lines differ from the stored instrument prediction**, including eight with different base letters. Their native spans are not transferred. The deck includes native-cache variant cards in addition to the stored-prediction cards; R0c must keep the two prediction streams distinct. [Exact drift receipt](R0_evidence/cached_prediction_drift_10.jsonl). Card locators alone may transfer spans to stored text, and their coordinate provenance is recorded. Nonalphabetic CTC atoms (combining marks, spaces, punctuation) are separately counted in the line census; the clean letter-blob denominator does not apply to them.', '',
        '| Script | All slots | Clean | Outside | Outside % |','|---|---:|---:|---:|---:|']
    for k,v in summary['by_script'].items():
        val='—' if v['outside_pct'] is None else f"{v['outside_pct']:.4f}"
        lines.append(f"| {k} | {v['all_alphabetic_slots']} | {v['clean_slots']} | {v['outside']} | {val} |")
    lines+=['','Greek script uses the recorded line class (`greek_mono` → modern, otherwise Greek polytonic/mixed); Latin is identified per emitted character. A polytonic-source card can contain a modern-class line, so book/source names alone are not script truth. Size is the runtime pixel x-height (including capital-run bands), with fixed <20, 20–34 and ≥35 px buckets.','',
        '| Pixel x-height | All slots | Clean | Outside | Outside % |','|---|---:|---:|---:|---:|']
    for k,v in summary['by_size'].items():lines.append(f"| {k} | {v['all_alphabetic_slots']} | {v['clean_slots']} | {v['outside']} | {v['outside_pct']:.4f} |")
    lines+=['','Script × size, per-book and per-stratum denominators are in [span_summary.json](R0_evidence/span_summary.json); every slot is in [span_slots.jsonl.gz](R0_evidence/span_slots.jsonl.gz), and nonletter atoms are in [span_line_census.jsonl](R0_evidence/span_line_census.jsonl).','',
        '## The original 715 R1 unmapped samples','',
        'Reproduced exactly: 11,329 scored samples, 10,614 mapped, 715 unmapped. Every unmapped frozen S4 recogniser slot has `localisation_unknown=True` and lacks `component_slot`. Of these, **698 share a primary blob with other recognised characters**, so the historical mapper rejects unique ownership; **17 have no overlapping primary letter blob**. The saved primary-owner lists give the reason for each individual sample. [Historical S4 mapping source](R0_evidence/historical_S4_reading.py.txt), read from commit `afe67823`, explicitly refuses `k is None or len(owners[k]) != 1`. These are original frozen-instrument mapping omissions, not 715 missing recogniser letters. The independent R1 extraction uses different component/window rules and can still admit a window. Its additional support partition is:', '',
        '| R1 support / frozen mapping | Count | Example line ids |','|---|---:|---|']
    for k,v in r1['mapping_details'].items():lines.append(f"| {k} | {v} | {', '.join(r1['detail_examples'][k])} |")
    lines += ['',f"Frozen evaluation bbox overlaps per unmapped CTC interval: {r1['frozen_overlap_counts']}. Overlap does not confer unique ownership. [All 715 individual reasons, owner starts and exact saved evidence](R0_evidence/R1_unmapped_715.jsonl) are preserved; neither fusion nor a nearest-blob fallback invents truth. The 698 shared-blob versus 17 no-primary distinction closes the historical mapping mechanism; judging whether each shared component really contains multiple printed letters still requires pixels.", '',
        '## Blind handoff and truth placeholders','',
        f"**{card['adjudication_cards']} adjudication cards + {card['controls']} planted controls = {card['blind_items']} cards ({100*card['control_fraction']:.2f}% controls)**. Every disagreement group is included, rather than sampled; character-aligned word groups retain joins, splits and reference insertions. Forms are NFD-mark-stripped, case kept, and contain at most three distinct candidates. Candidate order and complete item order are seeded/randomized; source names, original line ids, reference verdicts and control flags are absent from the blind file. Zooms are at most 3× native. Each item includes the full line.", '',
        '| Card kind (can share a card) | Count |','|---|---:|']
    for k,v in card['by_kind'].items():lines.append(f'| {k} | {v} |')
    lines += ['',f"The exact 753 S5 case-disagreement slots are retained as the population. The seeded sample contains **160 slots from all {len(case['sample_by_book'])} books with disagreements**. Population and sample counts per book are in [case_sampling_receipt.json](R0_evidence/case_sampling_receipt.json). R0c uses the stratified estimator `sum_h N_h × recogniser_right_h/n_h`; the winner percentage and extrapolated count are null now.", '',
        'R0b delivery: give each independent Opus reader only [R0_cards/](R0_cards/index.html), its images/README, and a fresh blank [R0_expected_truth.json](R0_expected_truth.json). Keep [items_key.json](R0_adjudication_private/items_key.json) and all other evidence private. The key is outside the blind directory and never embedded/fetched by its viewer. The preparer visually checked planted-control words; controls are excluded from accuracy. Readers must be able to reject all candidate forms, identify ambiguous print and record full-line transcription explicitly. The track lead validates controls privately and resolves reader disagreements. No adjudicator was run during R0a.', '',
        f"The owner evidence ledger retains {len(notes)} relevant note records (including repeated historical note sets), with original note source/line id. Notes such as misread rho, εις segmentation, eta classification and Latin-a output are partial or method-specific observations, not automatically recogniser identity failures. [Owner notes ledger](R0_evidence/owner_letter_punctuation_evidence.jsonl).", '',
        'Apostrophe/quote cards include textual disagreements, S4 apostrophe/opening-quote candidates and new-source detector candidates. Existing M2 blind pairs add candidate forms where an exact reference phrase can be located. Existing verdicts remain reference-only. Apostrophe versus breathing and Greek/Latin homoglyphs need explicit pixel/context judgment. The [punctuation inventory](R0_evidence/punctuation_emissions.jsonl) records raw emissions and source coverage; print-positive denominators and emitted/present rates remain null.', '',
        '## Training-label evidence and R0c DATA/MODEL boundary','',
        f"The exact local `import_real_v2_train.jsonl` contains {freq['lines']:,} rows; its hash and symbol-by-script frequencies are recorded. These are training-manifest labels, not a claim that every row was consumed unchanged by E3. Frequency alone does not establish correctness, elision semantics or causal model limitations.", '',
        '| Label symbol | Codepoint | Occurrences | Lines |','|---|---|---:|---:|']
    for r in freq['symbols']:
        if r['symbol'] in "'’ʼ᾽‘“”«»\"":lines.append(f"| {r['symbol']} | {r['codepoint']} | {r['occurrences']} | {r['lines']} |")
    lines += ['', 'The straight apostrophe and spacing koronis are present, while the right curly apostrophe is extremely rare. This rules out the broad unsupported assertion “training labels contain no apostrophes”; it does not prove whether Google dropped particular printed elisions. The codec also admits U+2019. R0c must join adjudicated print, Google labels, recogniser output and label/preprocessing evidence before selecting DATA (bad/missing labels or coverage) versus MODEL (correct labels but failed reading/position). Mixed or unresolved causes must remain explicit rather than forced into a wider-model recommendation.', '',
        '`R0_failures.jsonl` is a **candidate/geometry observation ledger** in R0a: one row per observed diagnostic or unresolved card kind, with line id, slot, evidence, `DATA_MODEL=null` and status. It does not label disagreement as confirmed failure. Confirmed letter substitution/insertion/deletion/case/script counts, ≥3 examples per supported final failure type, DATA/MODEL verdict and training-arm recommendation belong to R0c; [failure_type_placeholders.json](R0_evidence/failure_type_placeholders.json) and [R0_result_placeholders.json](R0_result_placeholders.json) make the missing fields explicit.', '',
        '## Review page and verification','',
        '[R0_review_positions.html](R0_review_positions.html) is a 60-line pre-adjudication position preview with full line, line id, Google, native recogniser text, a thin box/character label for every CTC atom and one autosaving/exportable note. The final failure-type selection remains R0c work; the track lead publishes it. No Firefox presentation was opened and nothing was published.', '',
        f"Execution: local Mac CPU, network off, **{align['total_R0_forward_crops']} new CTC crops**, 200 reused crop/checkpoint-bound M2 cached alignments, no CTC forward on the 666. Runtime/model assets are unchanged. Launch checkout `{bind['head']}` is two R0 brief commits after requested `fabcd6d4`; no detector/recogniser code was edited and no Git mutation command was used. Reproduction scripts are `scripts/labelfix/r0_prepare.py` and `scripts/labelfix/r0_finish.py`. All card PNGs decode, blind/key schemas and control counts validate, both viewers pass JavaScript syntax checks, and runtime/checkpoint/shared-cache hashes are unchanged. Nineteen representative card images were inspected, covering all card kinds and controls. Browser visual/interaction QA could not run: the in-app browser is unavailable and the browser inventory is empty. Final artifact/reference/hash checks are in [validation.json](R0_evidence/validation.json).", '',
        'R0a is stopped here. The unresolved fresh-book scope prevents the exact requested READY receipt. R0b must provide independent pixel judgments; R0c must score and classify.','']
    final=f"R0a PARTIAL READY: locked set (i) PENDING (0 lines / 0 books; 133 candidates / 3 books available), (ii) 200 new-source lines / {len(split['locked_sources'])} sources (dev pool 273); zero overlap (ii) with 666, DEV, L1 input; cross-stratum receipt PENDING; cards {card['adjudication_cards']} (+controls {card['controls']}); span placement outside-blob {outside:.4f}%; R0 RESULT (after R0c): letter truth PENDING (0 full lines certified in R0a); letter error PENDING (case-folded PENDING); spans outside blob {outside:.4f}% (by script/size in receipt); case disagreements recogniser right PENDING; apostrophes emitted PENDING; DATA types PENDING; MODEL types PENDING."
    lines.append(final)
    (OUT/'R0_REPORT.md').write_text('\n'.join(lines)+'\n')
    print(final,flush=True)

def verify():
    blind=json.loads((OUT/'R0_cards/items_blind.json').read_text())
    key=json.loads((OUT/'R0_adjudication_private/items_key.json').read_text())
    assert len(blind)==len(key) and len({r['id'] for r in blind})==len(blind)
    allowed={'id','img','line_img','A','B','C'}
    dims=[]
    for b,k in zip(blind,key):
        assert set(b)<=allowed and b['id']==k['id'] and all(k[x]==v for x,v in b.items())
        assert 2<=len([x for x in ('A','B','C') if x in b])<=3
        assert k['zoom_scale']<=3
        for field in ('img','line_img'):
            p=OUT/'R0_cards'/b[field];assert p.is_file()
            with Image.open(p) as im:im.verify()
        dims.append(dict(id=b['id'],zoom_scale=k['zoom_scale']))
    locked=read(OUT/'R0_newsource_locked.jsonl');dev=read(OUT/'R0_newsource_dev.jsonl')
    assert len(locked)==200 and len(dev)==273
    assert not {r['line_id'] for r in locked}&{r['line_id'] for r in dev}
    assert (OUT/'R0_newsource_exclusion_ids.txt').read_text().splitlines()==sorted(r['line_id'] for r in locked)
    native=read(WORK/'span_slots.jsonl.gz');assert all(r['native_ctc'] for r in native)
    bind=json.loads((WORK/'input_binding.json').read_text())
    changed=[p for p,h in bind['files'].items() if sha(ROOT/p)!=h]
    assert not changed,changed
    assert sha(CKPT[0])==bind['checkpoint_sha256']
    assert (_data_input(OUT/'R0_review_positions.html')).read_text().count('<article ')==60
    viewer=(OUT/'R0_cards/index.html').read_text()
    assert 'items_key' not in viewer and 'http://' not in viewer and 'https://' not in viewer
    assert all(set(x)=={'id','reader_1','reader_2','adjudicated'} for x in json.loads((OUT/'R0_expected_truth.json').read_text()))
    assert sum(r['control'] for r in key)/len(key)>=.08
    files=[p for p in OUT.glob('R0*') if p.is_file()]
    manifest={str(p.relative_to(OUT)):sha(p) for p in files}
    for p in (OUT/'R0_cards').rglob('*'):
        if p.is_file():manifest[str(p.relative_to(OUT))]=sha(p)
    manifest['R0_adjudication_private/items_key.json']=sha(OUT/'R0_adjudication_private/items_key.json')
    dump(WORK/'artifact_hashes.json',manifest)
    dump(WORK/'validation.json',dict(status='PASS_FOR_AVAILABLE_R0a_SCOPE',
        complete_two_stratum_R0a=False,fresh_wikisource_scope='PENDING',
        source_and_shared_cache_hashes_unchanged=True,checkpoint_unchanged=True,
        blind_schema_allowlist=True,blind_key_not_embedded_or_fetched=True,all_card_images_decodable=True,
        controls=sum(r['control'] for r in key),control_fraction=sum(r['control'] for r in key)/len(key),
        case_cards=sum('case_disagreement' in r['kinds'] for r in key),
        locked_dev_partition_exact=True,exclusion_ids_match=True,span_slots=len(native),native_ctc_only=True,
        review_lines=60,network_calls=0,new_ctc_forward_crops=0,git_mutation_commands=0,
        browser_visual_QA='Unavailable: CUA in-app browser not available and browser inventory is empty. Native card PNGs inspected separately; JSON/image/hash checks are not GUI proof.'))

def main():
    make_punctuation_inventory();ledger=make_ledger();review_page(ledger);report();verify()

if __name__=='__main__':main()
