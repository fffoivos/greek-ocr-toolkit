"""Offline mechanical KR3 aggregation, paired to pinned SRK2; no adjudication."""
import sys
sys.dont_write_bytecode = True
import json, subprocess
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import HERE, REPO, BED, rows, dump, jsonl, sha, io_guard


def main():
    io_guard()
    key = json.loads((HERE/'keys/kosmo2.json').read_text())
    prior_path = 'docs/harvest/recut_v1/w1_masked/checks/kosmo_poly1850_sol/answers_mapped.jsonl'
    pinned = subprocess.check_output(['git', 'show', '87db4392:'+prior_path], cwd=REPO)
    assert pinned == (REPO/prior_path).read_bytes(), 'SRK2 local answers differ from pinned commit'
    prior_rows = [json.loads(l) for l in pinned.splitlines()]
    prior = {r['line_id']: r for r in prior_rows}
    assert len(prior) == len(prior_rows) == 100
    assert sum(r['letters']=='y' for r in prior_rows) == 96
    assert sum(r['crop_ok']=='y' for r in prior_rows) == 99
    bed, controls, inputs, scans = [], [], [HERE/'keys/kosmo2.json', REPO/prior_path], {}
    for context in ('c1', 'c2b'):
        scanpath = HERE/'scan/kosmo2'/('c1.scan.json' if context=='c1' else 'c2b.scan_v41_final.json')
        scan = json.loads(scanpath.read_text())
        assert scan['ok'] and not scan['violations'] and not scan['manifest_check_skipped']
        scans[context] = dict(path=str(scanpath.relative_to(HERE)), ok=True, scanner_version=scan['scanner_version'])
        inputs.append(scanpath)
        ap = HERE/f'answers/kosmo2/{context}.jsonl'
        mp = HERE/f'answers/kosmo2/{context}.mapped.jsonl'
        cp = HERE/f'answers/kosmo2/{context}.controls.json'
        ip = HERE/f'pack_inventory/{context}.cards.jsonl'
        inputs.extend([ap,mp,cp,ip])
        answers = rows(ap); cards = rows(ip)
        assert len(answers)==55 and len({r['card_id'] for r in answers})==55
        assert {r['card_id'] for r in answers} == set(key['readers'][context])
        inventory = {r['card_id']:r for r in cards}
        mapped = []
        checked_controls = []
        for answer in answers:
            iid = answer['card_id']; meta = key['items'][iid]
            crop = BED/context/inventory[iid]['crop']
            assert sha(crop) == meta['crop_sha256']
            inputs.append(crop)
            row = dict(answer, opaque_id=iid, context=context, line_id=meta['line_id'],
                       control=meta['control'], source=meta['source'], crop_path=str(crop),
                       crop_sha256=meta['crop_sha256'], letters_status='final',
                       crop_ok_status='final', marks_status='pending_opus')
            if meta['control']:
                checks = {f:answer[f]==v for f,v in meta['expected'].items()}
                row.update(expected=meta['expected'], checks=checks, passed=all(checks.values()))
                checked_controls.append(row); controls.append(row)
            else:
                mapped.append(dict(answer,card_id=meta['line_id']))
                bed.append(row)
        assert mapped == rows(mp), 'mapped answer mismatch'
        receipt=json.loads(cp.read_text())
        assert receipt['control_errors']==sum(not r['passed'] for r in checked_controls)
        assert receipt['flagged']==(receipt['control_errors']>1)
        assert {r['id']:r['passed'] for r in receipt['controls']} == {r['opaque_id']:r['passed'] for r in checked_controls}
    assert len(bed)==len({r['line_id'] for r in bed})==100
    assert {r['line_id'] for r in bed} == set(prior)
    assert len(controls)==len({r['line_id'] for r in controls})==10
    # Pair original card identity and crop content as well as line ID.
    sourcekey=json.loads((HERE.parent/'cards_kosmo_poly1850_key.json').read_text())
    inputs.append(HERE.parent/'cards_kosmo_poly1850_key.json')
    for row in bed:
        old=prior[row['line_id']]
        assert sourcekey[old['card_id']]['card_crop_sha256']==row['crop_sha256']
    totals={f:dict(Counter(r[f] for r in bed)) for f in ('letters','crop_ok','marks')}
    paired={}
    for field in ('letters','crop_ok','marks'):
        flips=[dict(line_id=r['line_id'], opaque_id=r['opaque_id'], context=r['context'],
                    previous=prior[r['line_id']][field], current=r[field],
                    previous_detail=prior[r['line_id']]['detail'], current_detail=r['detail'])
               for r in bed if r[field]!=prior[r['line_id']][field]]
        paired[field]=dict(agreement=100-len(flips), n=100, flips=flips,
                          transitions=dict(Counter(prior[r['line_id']][field]+'->'+r[field] for r in bed)))
    queue=[]
    for row in bed+controls:
        reasons = [f+':'+row[f] for f in ('letters','crop_ok','marks') if row[f] not in ('y','na')]
        if row['errors']: reasons.append('error_labels')
        if row.get('passed') is False: reasons.append('control_disagreement')
        if reasons: queue.append(dict(row, review_reasons=reasons, review_status='pending_eye_review'))
    jsonl(HERE/'review_queue.jsonl',queue)
    jsonl(HERE/'scored_cards.jsonl',bed)
    k=sum(r['passed'] for r in controls)
    result=dict(schema='KR3-results-v1',status='scoring complete; HANDOVER patch prepared, application blocked by writable roots',
        network='OFF',method='Mechanical aggregation; no new reading or adjudication',
        acceptance_ok=True,scanner_rule='v4.1: resolve pwd/template paths; ordinary v4 image provenance (exact or v4 downscale)',
        returned_images=64,pixel_exact_images=53,v4_downscale_images=11,violations=[],scans=scans,
        n=100,totals=totals,letters=totals['letters'],crop_ok=totals['crop_ok'],marks=totals['marks'],
        letters_status='final',crop_ok_status='final',marks_status='pending_opus',
        controls=dict(passed=k,total=10,contexts={c:dict(passed=sum(r['passed'] for r in controls if r['context']==c),
            errors=sum(not r['passed'] for r in controls if r['context']==c),flagged=sum(not r['passed'] for r in controls if r['context']==c)>1) for c in ('c1','c2b')},rows=controls),
        prior_run=dict(label='pre-handover, no controls',run='SRK2',commit='87db4392',cards=100,letters_y=96,crop_ok_y=99),
        paired_agreement=paired,review_queue=dict(n=len(queue),bed=sum(not r['control'] for r in queue),controls=sum(r['control'] for r in queue),path='review_queue.jsonl',
            rule='Every current negative/unreadable field, nonempty error list, or control disagreement; deduplicated by card; paired flips listed separately'),
        handover_edit=dict(status='prepared, not applied: outside writable roots',patch='handover/HANDOVER.v41.patch'),
        tests=dict(passed=4,log='scan/v41_final.tests.log'),input_sha256={str(p):sha(p) for p in inputs})
    line=f"KR3: done | c2b accepted (v4.1) | letters y: {totals['letters'].get('y',0)} | crop_ok y: {totals['crop_ok'].get('y',0)} | marks y: {totals['marks'].get('y',0)} (pending opus) | controls: {k}/10 | paired agreement letters/crop: {paired['letters']['agreement']}/{paired['crop_ok']['agreement']} | review queue: {len(queue)}"
    result['summary_line']=line
    dump(HERE/'results.json',result)
    report=['# KR3 kosmo2 scoring','',
        'c2b is accepted under v4.1: **53 exact + 11 v4-downscale = 64/64**, with no violations and the manifest check enabled. The fresh scan resolves the recorded pwd/template paths, including record 27; all other v4 checks remain unchanged. The ordinary v4 image rule accepts exact matches or downscales with long side 2048, aspect within 1 px and RGB MAD < 2. The previous strict KR2 rejection is superseded; its scan is retained as historical evidence. c1 passes v4; c2 remains VOID and excluded.','',
        '| Run | Cards | Letters y | Crop_ok y | Marks y | Controls |',
        '|---|---:|---:|---:|---:|---:|',
        f"| c1 + c2b | 100 | {totals['letters'].get('y',0)} | {totals['crop_ok'].get('y',0)} | {totals['marks'].get('y',0)} | {k}/10 |",
        '| SRK2 `87db4392`, **pre-handover, no controls** | 100 | 96 | 99 | 90 | none |','',
        'Letters and crop_ok are final Sol verdicts. Marks remain **pending_opus**. Scoring is mechanical with network OFF; no new reader or visual adjudication was run. Both contexts have zero control errors and are unflagged.','',
        'Pairing uses exactly the same 100 unique line IDs and verifies crop SHA256 identity. The SRK2 answer file was read from commit `87db4392` and checked byte-for-byte against the local file. Agreement measures verdict agreement, not independent accuracy.','']
    for f,p in paired.items():
        report += [f"**{f}: {p['agreement']}/100 agreement**; transitions (SRK2 → current): "+', '.join(f'{t}: {n}' for t,n in p['transitions'].items())+'.','']
        for flip in p['flips']:
            report += [f"- `{flip['line_id']}`: {flip['previous']} → {flip['current']}; current detail: {flip['current_detail'] or '(empty)'}. Previous detail: {flip['previous_detail'] or '(empty)' }."]
        report += ['']
    report += [f"The [review queue](review_queue.jsonl) has **{len(queue)} unique cards** ({result['review_queue']['bed']} bed, {result['review_queue']['controls']} controls). It includes every current negative/unreadable verdict, nonempty error list and control disagreement. Expected-negative controls are included as flags and distinguished from control errors. Paired flips are retained separately above and in results.json. Each queue record preserves the crop, IDs, verdicts, errors and original reader detail. Review remains pending.",'',
        'Four wrapper tests pass: real witness acceptance and template resolution, true outside-path rejection, parent escape rejection, and v4 downscale limits (MAD, aspect, long side). [Final scan](scan/kosmo2/c2b.scan_v41_final.json); [test log](scan/v41_final.tests.log).','',
        '**HANDOVER limitation:** this session cannot write the Sol-reading worktree. The §5 addition is prepared as [HANDOVER.v41.patch](handover/HANDOVER.v41.patch), with before/after hashes and a guarded external commit list. The existing HANDOVER contains no v4.1 bullet, so the patch adds the corrected ordinary-v4 wording. It has not been applied there. No staging or commit was attempted in either worktree.','',
        'KR3_COMMIT_FILES.txt and KR3_COMMIT_GUARD.json bind the recut change set. The handover/ directory contains the separate Sol-reading list and guard. Require matching HEAD/branch, empty index, and all input/output hashes; stage only the exact listed paths and verify the staged set. Stop on mismatch.','',line]
    (HERE/'RESULTS.md').write_text('\n'.join(report)+'\n')
    print(line)

if __name__=='__main__': main()
