"""Offline CP7b scoring; no measurement. Copy CP7b_RECEIPT.staged.md to ../CP7b_RECEIPT.md after running (frozen guard confines writes to cp7)."""
import gzip
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from cp7_common import HERE, SEG, ROOT, PACK_ROOT, BEDS, SCANNER, sha, read, rows, dump, jsonl, offline_guard
from freeze import verify_freeze
from runtime import map_records, RUBRIC

FREEZE = '9212fe491a37e3992d245aec0d8a47a7e9437e8e6ef3a7aa6a1025ac825fa22e'
SCREENS = ('union', 'merged', 'neighbour_words', 'orientation', 'geometry_unavailable', 'crossing')

def truth(answer):
    return any(answer[f] == 'yes' for f in RUBRIC)

def flags(answer):
    return bool(answer.get('flags') or answer.get('flag') or answer['errors'] or answer['detail'] or
                any(answer[f] in ('n', 'u') for f in ('letters', 'marks', 'crop_ok')))

def matrix(pairs):
    out = dict(TP=0, FP=0, FN=0, TN=0)
    for predicted, actual in pairs:
        out[('T' if predicted == actual else 'F') + ('P' if predicted else 'N')] += 1
    out['precision'] = out['TP'] / (out['TP'] + out['FP']) if out['TP'] + out['FP'] else None
    out['recall'] = out['TP'] / (out['TP'] + out['FN']) if out['TP'] + out['FN'] else None
    return out

def predictions(seal):
    return dict(union=seal['screen_drop'], merged=seal['merged'] is True,
                neighbour_words=seal['neighbour_words'] is True,
                orientation=seal['orientation'] is True,
                geometry_unavailable=seal['geometry_unavailable'], crossing=seal['crossing']['drop'] is True)

def validate():
    offline_guard()
    verify_freeze()
    assert sha(SEG/'CP7_FREEZE.json') == FREEZE
    build = read(HERE/'build_receipt_cp7a3.json')
    assert sha(HERE/'keys/sealed_decisions.jsonl.gz') == build['sealed_decisions_sha256']
    assert sha(HERE/'keys/draw.jsonl') == build['draw_sha256']
    assert sha(HERE/'tools/scan_rollout.py') == SCANNER
    preservation = read(HERE/'pack_preservation_cp7a3.json')
    assert preservation['unchanged']
    assert all(sha(p) == digest for p, digest in preservation['files'].items())
    seals = [json.loads(line) for line in gzip.open(HERE/'keys/sealed_decisions.jsonl.gz', 'rt')]
    by = {s['row_id']: s for s in seals}
    assert len(by) == len(seals) == 100
    assert set(by) == {r['id'] for r in rows(HERE/'keys/draw.jsonl')}
    approved = {c['source_card']['card_id']: c for c in read(ROOT/'docs/harvest/recut_v1/w1_masked/caps1/keys/control_truth.json')}
    log = (HERE/'run.log').read_text()
    logged_runs = [json.loads(line) for line in log.splitlines() if line.startswith('{"label":')]
    records, controls, custody = [], [], []
    for bed in BEDS:
        key = read(HERE/'keys'/f'{bed}.json')
        directory = PACK_ROOT/bed/'r1'
        manifest = read(directory.parent/'MANIFEST.r1.json')['files']
        assert all(sha(directory/p) == digest for p, digest in manifest.items())
        cards = rows(directory/'cards.jsonl')
        mapped, control = map_records(rows(HERE/'answers'/bed/'r1.jsonl'), cards, key)
        assert mapped == rows(HERE/'answers'/bed/'r1.mapped.jsonl')
        assert control == rows(HERE/'answers'/bed/'r1.controls.jsonl')
        assert rows(directory/'answers.jsonl') == rows(HERE/'answers'/bed/'r1.jsonl')
        receipt = read(HERE/'receipts'/f'{bed}.json')
        scan = read(HERE/'scan'/bed/'r1.scan.json')
        assert scan['ok'] and not scan['violations'] and not scan['manifest_check_skipped']
        assert sha(scan['rollout']) == scan['rollout_sha256']
        assert receipt['run'] == next(r for r in logged_runs if r['label'] == receipt['run']['label'])
        assert receipt['run']['usage'] == scan['total_token_usage']
        assert receipt['run']['rollout'] == scan['rollout']
        assert receipt['run']['rc'] == receipt['scanner_rc'] == receipt['mapping_rc'] == 0
        assert receipt['run']['model'] == 'gpt-6.1-sol'
        assert receipt['freeze_sha256'] == FREEZE and receipt['canonical_scanner_sha256'] == SCANNER
        assert receipt['limit_before'] in log and receipt['limit_after'] in log
        valid = True
        for a in control:
            meta = key['items'][a['card_id']]
            reference = approved[meta['control_public_id']]['reference_verdict']
            assert reference == meta['reference_verdict']
            expected = {f: reference[f] for f in ('letters', 'marks', 'crop_ok')}
            passed = all(a[f] == v for f, v in expected.items())
            valid &= passed
            controls.append(dict(context=bed, row_id=a['line_id'], card_id=a['card_id'],
                                 control_id=meta['control_public_id'], expected=expected,
                                 actual={f:a[f] for f in expected}, passed=passed))
        custody.append(dict(context=bed, valid=valid, mapped=len(mapped), controls=len(control),
                            manifest_files=len(manifest), scan_ok=True, violations=0,
                            run_matches_log=True, rollout_sha256=scan['rollout_sha256']))
        card_by = {c['card_id']: c for c in cards}
        for a in mapped:
            s = by[a['line_id']]
            crop = directory/card_by[a['card_id']]['crop']
            assert sha(crop) == s['crop_sha256'] == key['items'][a['card_id']]['crop_sha256']
            local_crop = HERE/'crops'/crop.name
            assert local_crop.read_bytes() == crop.read_bytes()
            pred = predictions(s)
            assert pred['union'] is s['composed']['drop']
            assert pred['union'] == any(pred[f] for f in SCREENS if f != 'union')
            actual = truth(a)
            mismatch = {f: ('FP' if pred[f] else 'FN') for f in SCREENS if pred[f] != actual}
            records.append(dict(context=bed, context_valid=valid, row_id=a['line_id'], card_id=a['card_id'],
                crop_path=str(crop), crop_copy=str(local_crop.relative_to(ROOT)), crop_sha256=sha(crop),
                reader=a, truth='DROP' if actual else 'KEEP', predictions=pred,
                mismatches=mismatch, flag=flags(a), unreadable=any(a[f]=='u' for f in ('letters','marks','crop_ok')),
                sealed=s))
    assert len(records) == len({r['row_id'] for r in records}) == 100 and len(controls) == 10
    return records, controls, custody

def summarize(records, controls, custody):
    valid = [r for r in records if r['context_valid']]
    matrices = {f:matrix([(r['predictions'][f], r['truth']=='DROP') for r in valid]) for f in SCREENS}
    rotated = [r for r in valid if r['reader']['rotated']=='yes']
    missed = [r['row_id'] for r in rotated if not r['predictions']['union']]
    unknown = [r for r in valid if r['sealed']['orientation_unknown']]
    unavailable = [r for r in valid if r['sealed']['geometry_unavailable']]
    adjudicate = [r for r in records if r['mismatches'] or r['flag'] or r['unreadable']]
    return dict(controls_passed=sum(c['passed'] for c in controls), mapped=len(records), custody=custody,
        void_contexts=[c['context'] for c in custody if not c['valid']], scored=len(valid),
        reader_drop=sum(r['truth']=='DROP' for r in valid), matrices=matrices,
        rotated=dict(total=len(rotated), admitted=len(missed), rate=len(missed)/len(rotated) if rotated else None, row_ids=missed),
        orientation_unknown=dict(total=len(unknown), reader_drop=sum(r['truth']=='DROP' for r in unknown), row_ids=[r['row_id'] for r in unknown]),
        geometry_unavailable=dict(total=len(unavailable), reader_drop=sum(r['truth']=='DROP' for r in unavailable), row_ids=[r['row_id'] for r in unavailable]),
        adjudication_ids=[r['row_id'] for r in adjudicate], adjudication_count=len(adjudicate),
        flag_count=sum(r['flag'] for r in records), unreadable_count=sum(r['unreadable'] for r in records))

def compact_evidence(s):
    structural = s['structural']
    groups=[]
    for row in structural.get('rows', []):
        groups.append({k:row.get(k) for k in ('row_id','column_id','xheight','profile_runs','profile_gaps','directional_missing')} |
                      dict(groups=[{k:g.get(k) for k in ('box','body_count','width_xh','complete','resolved','positive','unresolved')} for g in row.get('groups',[])]))
    inclusion=structural.get('row_inclusion', {})
    o=s['orientation_observation'];d=o.get('decision',{})
    return dict(structural_status=structural.get('status'), structural_reason=structural.get('reason'),
        target_row_id=structural.get('target_row_id'), neighbour_rows=groups,
        row_inclusion={k:v for k,v in inclusion.items() if k!='rows'},
        row_inclusion_rows=[{k:r.get(k) for k in ('row_id','column_id','xheight','assigned_pixels','supported')} | dict(runs=[{k:run.get(k) for k in ('x0','x1','body_cut_fraction','body_pixels','body_extent_px','complete')} for run in r.get('runs',[]) if run.get('body_pixels',0) or run.get('complete')]) for r in inclusion.get('rows',[]) if r.get('assigned_pixels',0) or any(run.get('body_pixels',0) or run.get('complete') for run in r.get('runs',[]))],
        omitted_zero_ink_rows=sum(not (r.get('assigned_pixels',0) or any(run.get('body_pixels',0) or run.get('complete') for run in r.get('runs',[]))) for r in inclusion.get('rows',[])), crossing=s['crossing'],
        axis=dict(status=o.get('status'),reason=o.get('reason'),decision_source=o.get('decision_source'),
                  source=o.get('source'),axis=d.get('axis'),orientation_cw=d.get('orientation_cw'),
                  axis_confidence=d.get('axis_confidence'),polarity_confidence=d.get('polarity_confidence'),
                  regional=o.get('regional'),regional_evidence=o.get('regional_evidence')))

def number(x):
    return 'undefined' if x is None else f'{x:.4f}'

def final_line(s, tests):
    m=s['matrices']['union'];r=s['rotated'];u=s['orientation_unknown'];g=s['geometry_unavailable']
    return (f"SEG-CP7b: done | controls {s['controls_passed']}/10 | mapped 100/100 | union TP {m['TP']} FP {m['FP']} FN {m['FN']} TN {m['TN']} (P {number(m['precision'])} R {number(m['recall'])}) | rotated-miss {r['admitted']}/{r['total']} | unknown-axis {u['total']} (reader drop {u['reader_drop']}) | geometry_unavailable {g['total']} (reader drop {g['reader_drop']}) | to adjudicate {s['adjudication_count']} | tests: {tests} passed")

def write_outputs(records, controls, s, tests):
    (HERE/'scored_cp7b.jsonl.gz').write_bytes(gzip.compress(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records).encode(),mtime=0))
    dump(HERE/'controls_cp7b.json',controls)
    dump(HERE/'score_summary_cp7b.json',s)
    sheet=['# CP7b adjudication sheet','',
        'Reader labels are provisional owner-standard truth; the lead has not yet adjudicated pixels. No new reading was performed for CP7b.', '',
        'Includes every FP/FN for union **or any standalone screen**, plus any letters/marks/crop_ok n/u, errors, nonempty detail, explicit flag, or unreadable. Controls are reported separately; none missed. Unknown-axis and unavailable-geometry rows are listed in the receipt even when they need no adjudication.', '',
        'Crop paths below point to the original CP7a public packs; repository copies were checked byte-identical. Full sealed evidence is retained in `scored_cp7b.jsonl.gz`. Contact sheets are previews; use original crops for the lead pixel check.', '']
    selected=[r for r in records if r['row_id'] in s['adjudication_ids']]
    font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',14)
    sheets=[]
    for start in range(0,len(selected),30):
        batch=selected[start:start+30]; width=1500; cellw=750; cellh=240
        canvas=Image.new('RGB',(width,cellh*((len(batch)+1)//2)), 'white'); draw=ImageDraw.Draw(canvas)
        for i,r in enumerate(batch):
            x=(i%2)*cellw;y=(i//2)*cellh
            draw.rectangle((x,y,x+cellw-1,y+cellh-1),outline='#999999')
            draw.text((x+8,y+6),r['row_id'],font=font,fill='black')
            draw.text((x+8,y+28),f"{r['card_id']} truth {r['truth']} union {'DROP' if r['predictions']['union'] else 'KEEP'}",font=font,fill='black')
            with Image.open(r['crop_path']) as im:
                preview=im.convert('RGB');preview.thumbnail((cellw-16,cellh-62),Image.Resampling.LANCZOS)
                canvas.paste(preview,(x+8,y+54))
        name='ADJUDICATION_SHEET.png' if start==0 else f'ADJUDICATION_SHEET_{start//30+1:02d}.png'
        canvas.save(HERE/name);sheets.append(dict(path=name,rows=[r['row_id'] for r in batch],size=list(canvas.size)))
    dump(HERE/'contact_sheets_cp7b.json',sheets)
    for r in selected:
        sheet += [f"## {r['row_id']}",'',f"Card `{r['card_id']}`; context `{r['context']}`; reader truth **{r['truth']}**.",'',
            f"Crop: `{r['crop_path']}`",'',f"Byte-identical repository crop: `{r['crop_copy']}`; SHA-256 `{r['crop_sha256']}`.",'',
            'Triggers: '+json.dumps(dict(mismatches=r['mismatches'],flag=r['flag'],unreadable=r['unreadable']))+'.','',
            'Reader answers and one-line reasons:','', '```json',json.dumps(r['reader'],ensure_ascii=False,indent=2),'```','',
            'Sealed screen decisions (null remains unknown/unavailable):','', '```json',json.dumps({k:r['sealed'][k] for k in ('merged','neighbour_words','orientation','orientation_unknown','geometry_unavailable','screen_drop','composed')},indent=2),'```','',
            'Measured evidence (neighbour runs, row inclusion, crossing, axis; zero-ink rows/runs and native component IDs omitted here, retained in the sealed record):','', '```json',json.dumps(compact_evidence(r['sealed']),ensure_ascii=False,indent=2),'```','',
            'Lead pixel adjudication: **pending**.','']
    (HERE/'ADJUDICATION_SHEET.md').write_text('\n'.join(sheet))
    receipt=['# SEG-CP7b receipt','',
        f"Freeze verified before scoring and again after output: `{FREEZE}`. Current CP7a3 seal: `{sha(HERE/'keys/sealed_decisions.jsonl.gz')}`. Network OFF; no reader launched, OCR, new crop reading, threshold changes, geometry preparation, or staged replay.",'',
        'Both original pack manifests and CP7a3 pack-preservation hashes match. Raw answers remap exactly to the 100 mapped rows and 10 controls; each original pack crop and repository copy matches the sealed crop SHA. Scan reports are ok with zero violations; their rollout hashes, usage and receipts match the logged runs.', '',
        'Context A provenance: its lead-written receipt exactly matches the successful run JSON, 50/5 mapping and before/after limit snapshots in `cp7/run.log`. The log subsequently records a preflight FileNotFoundError for CP5_verification.json before B starts. That file now matches the freeze byte-for-byte. The receipt is consistent with the logged run, but the run log itself does not record the restoration action or receipt creation. No claim of contemporaneous automated A-receipt creation is made.', '',
        'The pre-reader CP7a3 verifier was attempted and stops at pack-directory closure because reader answers and zoom files now exist; its later pre-reader no-answers assertion is also obsolete. CP7b directly verifies the original manifest entries and preservation hashes without removing reader products. No frozen verifier was edited.', '',
        f"Controls: **{s['controls_passed']}/10 passed**, including letters, marks and crop_ok against lead-approved caps1 control_truth.json reference values; no context voided. The key's explicit required fields letters/crop_ok also all pass. Reasons/error wording is descriptive, not an additional control target.",'',
        '| Context | Control | Expected letters/marks/crop | Reader letters/marks/crop | Pass |','|---|---|---|---|---|']
    for c in controls:
        receipt.append(f"| {c['context']} | {c['control_id']} | {'/'.join(c['expected'].values())} | {'/'.join(c['actual'].values())} | {c['passed']} |")
    receipt += ['', 'Truth is DROP iff any of neighbour_whole_word, multi_line, rotated, horizontally_missegmented is yes; otherwise KEEP. All 100 are scored; '+str(s['reader_drop'])+' reader DROP, '+str(100-s['reader_drop'])+' reader KEEP. Flags do not silently change this truth.', '',
        'A positive prediction means the screen drops. FP = screen DROP / reader KEEP; FN = screen KEEP / reader DROP. Standalone null merged/neighbour/orientation values do not trigger that screen and are counted as non-drops; geometry-unavailable is scored separately as the fail-closed policy. Orientation uses the final sealed decision, including regional inheritance; unknown admits for orientation only. Union is screen_drop/composed.drop, excluding the separate text admission rules. Crossing is included as an additional composed constituent.', '',
        '| Screen | TP | FP | FN | TN | Precision | Recall |','|---|---:|---:|---:|---:|---:|---:|']
    for name,m in s['matrices'].items():
        receipt.append(f"| {name} | {m['TP']} | {m['FP']} | {m['FN']} | {m['TN']} | {number(m['precision'])} | {'recall undefined' if m['recall'] is None else number(m['recall'])} |")
    rotated=s['rotated']
    receipt += ['',f"Rotated-miss rate: **{rotated['admitted']}/{rotated['total']} ({number(rotated['rate'])})**, denominator = reader rotated=yes, numerator = composed screen admits. This is segmentation admission; admission_drop also includes independent text rules and is not this metric.",'',
        'Orientation provenance: '+json.dumps({v:sum(r['sealed']['orientation_observation'].get('decision_source','not_recorded')==v for r in records) for v in sorted({r['sealed']['orientation_observation'].get('decision_source','not_recorded') for r in records})})+'.','']
    for field,title in [('orientation_unknown','Unknown-axis rows'),('geometry_unavailable','Geometry unavailable: fail-closed cost')]:
        group=s[field]
        receipt += [f'## {title}','',f"{group['total']} rows; reader DROP {group['reader_drop']}, KEEP {group['total']-group['reader_drop']}.",'',
            '| Row id | Reader truth | Reader rotated | Union | Sealed reason |','|---|---|---|---|---|']
        for r in records:
            if r['row_id'] not in group['row_ids']:continue
            reason=r['sealed']['orientation_observation'].get('reason') if field=='orientation_unknown' else r['sealed']['structural'].get('reason')
            receipt.append(f"| {r['row_id']} | {r['truth']} | {r['reader']['rotated']} | {'DROP' if r['predictions']['union'] else 'KEEP'} | {reason} |")
        receipt += ['']
    receipt += [f"Adjudication: **{s['adjudication_count']} unique fresh rows**; {s['flag_count']} flagged, {s['unreadable_count']} unreadable. Includes standalone disagreements as well as union disagreements. See `cp7/ADJUDICATION_SHEET.md` and contact sheets (at most 30 crops each). Labels remain reader truth pending the lead's pixel check.",'',
        f"Validation: {tests} tests passed (see `cp7/pytest_cp7b.log`); input/output SHA manifest in `CP7b_COMMIT_LIST.json`. The full-population geometry and staged replay remain held for the owner.",'',final_line(s,tests)]
    (HERE/'CP7b_RECEIPT.staged.md').write_text('\n'.join(receipt)+'\n')

def main():
    records,controls,custody=validate()
    summary=summarize(records,controls,custody)
    assert not summary['void_contexts'], 'Control miss voids context: '+str(summary['void_contexts'])
    write_outputs(records,controls,summary,int(sys.argv[1]) if len(sys.argv)>1 else 0)
    verify_freeze()
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
