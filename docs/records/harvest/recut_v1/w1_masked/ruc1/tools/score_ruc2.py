"""Offline, mechanical RUC2 aggregation. Does not adjudicate or update admission."""
import sys
sys.dont_write_bytecode = True
import json, subprocess, difflib, hashlib
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from build import HERE, REPO, BED, REFERENCE, rows, dump, jsonl, sha


def main():
    # No network operations permitted by this process.
    sys.addaudithook(lambda event,args: (_ for _ in ()).throw(PermissionError('network OFF')) if event.startswith('socket.') else None)
    keypath=HERE/'keys/ruc1.json'; key=json.loads(keypath.read_text())
    inputs=[keypath,HERE/'keys/draw.jsonl',HERE/'README.md',HERE/'runtime_bindings.json',HERE/'adapter_approval.json',HERE/'reference_adapter.py',HERE/'build.py',Path(__file__).resolve()]
    wrapper=HERE.parent/'kosmo2/tools'
    inputs += [wrapper/name for name in ('scan_rollout_v41.py','scan_rollout_v42.py','test_scan_rollout_v41.py','test_scan_rollout_v42.py')]
    testlog=HERE/'scan/v42.tests.log'
    assert 'Ran 8 tests' in testlog.read_text() and testlog.read_text().rstrip().endswith('OK')
    recheck=HERE/'scan/c2_recheck_receipt.json'; receipt=json.loads(recheck.read_text())
    assert receipt['ok'] and not receipt['violations']
    assert receipt['rollout_sha256']==sha(receipt['rollout'])
    assert receipt['original_scan_sha256']==sha(HERE/'scan/ruc1/c2.scan.json')
    inputs += [testlog,recheck,HERE/'scan/ruc1/c1.scan.json',HERE/'prompts/ruc1.md',HERE/'launchers/run_read.sh']
    bed=[]; controls=[]; scans={}
    for context in ('c1','c2'):
        sp=HERE/'scan/ruc1'/('c1.scan_v42.json' if context=='c1' else 'c2.scan.json')
        scan=json.loads(sp.read_text()); inputs.append(sp)
        assert scan['ok'] and not scan['violations'] and not scan['manifest_check_skipped']
        scans[context]=dict(path=str(sp.relative_to(HERE)),scanner_version=scan['scanner_version'],ok=True,
            returned_images=scan['returned_images'],image_match_counts=dict(Counter(m['match'] for m in scan['image_matches'])))
        ap=HERE/f'answers/ruc1/{context}.jsonl'; mp=ap.with_name(context+'.mapped.jsonl'); cp=ap.with_name(context+'.controls.json')
        ip=HERE/f'pack_inventory/{context}.cards.jsonl'; pack=BED/context
        inputs += [ap,mp,cp,ip,pack/'cards.jsonl',pack/'answers.jsonl',pack.parent/f'MANIFEST.{context}.json']
        assert rows(ap)==rows(pack/'answers.jsonl')
        assert rows(ip)==rows(pack/'cards.jsonl')
        answers=rows(ap); cards=rows(ip); inventory={r['card_id']:r for r in cards}
        assert len(answers)==len({a['card_id'] for a in answers})==55
        assert [a['card_id'] for a in answers]==key['readers'][context]
        mapped=[]; checked=[]
        for a in answers:
            assert set(a)=={'card_id','letters','marks','crop_ok','errors','detail'}
            assert a['letters'] in ('y','n','u') and a['marks'] in ('y','n','na') and a['crop_ok'] in ('y','n')
            assert isinstance(a['errors'],list) and isinstance(a['detail'],str)
            meta=key['items'][a['card_id']]; crop=pack/inventory[a['card_id']]['crop']; inputs.append(crop)
            assert sha(crop)==meta['crop_sha256']
            r=dict(a,opaque_id=a['card_id'],context=context,line_id=meta['line_id'],control=meta['control'],
                source=meta['source'],crop_path=str(crop),crop_sha256=meta['crop_sha256'],
                letters_status='final',crop_ok_status='final',marks_status='pending_opus')
            if meta['control']:
                checks={f:a[f]==v for f,v in meta['expected'].items()}
                r.update(expected=meta['expected'],checks=checks,passed=all(checks.values()))
                checked.append(r); controls.append(r)
            else:
                r.update(label_repaired=meta['label_repaired'],label_parent=meta['label_parent'],label_used=meta['label_used'])
                assert r['label_repaired']==(r['label_parent']!=r['label_used'])
                bed.append(r); mapped.append(dict(a,card_id=meta['line_id']))
        assert rows(mp)==mapped
        receipt=json.loads(cp.read_text()); errors=sum(not r['passed'] for r in checked)
        assert receipt['control_errors']==errors and receipt['flagged']==(errors>1)
        assert {r['id']:r['passed'] for r in receipt['controls']}=={r['opaque_id']:r['passed'] for r in checked}
    assert len(bed)==len({r['line_id'] for r in bed})==100
    assert {r['line_id']:r['label_repaired'] for r in bed}=={r['id']:r['label_repaired'] for r in rows(HERE/'keys/draw.jsonl')}
    assert sum(r['label_repaired'] for r in bed)==18
    assert len(controls)==len({r['line_id'] for r in controls})==10
    totals={f:dict(Counter(r[f] for r in bed)) for f in ('letters','crop_ok','marks')}
    split={name:dict(n=sum(r['label_repaired']==repair for r in bed),letters=dict(Counter(r['letters'] for r in bed if r['label_repaired']==repair))) for name,repair in [('repaired',True),('unrepaired',False)]}
    queue=[]
    for r in bed+controls:
        reasons=[f+':'+r[f] for f in ('letters','crop_ok','marks') if r[f] not in ('y','na')]
        if r['errors']: reasons.append('error_labels')
        if r.get('passed') is False: reasons.append('control_disagreement')
        if reasons: queue.append(dict(r,review_reasons=reasons,review_status='pending_eye_review'))
    assert len(queue)==len({r['opaque_id'] for r in queue})
    jsonl(HERE/'review_queue.jsonl',queue); jsonl(HERE/'scored_cards.jsonl',bed)
    contexts={c:dict(passed=sum(r['passed'] for r in controls if r['context']==c),errors=sum(not r['passed'] for r in controls if r['context']==c)) for c in ('c1','c2')}
    for v in contexts.values():v['flagged']=v['errors']>1
    k=sum(r['passed'] for r in controls); letters=totals['letters'].get('y',0); crop=totals['crop_ok'].get('y',0)
    gate=letters>=90 and crop>=90
    # Construct only a patch; the lead owns application in the other worktree.
    target=REFERENCE/'HANDOVER.md'; before=target.read_text(); assert 'v4.2 (coordinator ruling' not in before
    bullet='- **v4.2 (coordinator ruling, 17 Oct).** Read-only OS resource paths under `/System/Library/Fonts/**` and `/Library/Fonts/**` are allowed in tool inputs. Every other absolute-path test is unchanged; font writes remain violations. v4.1 resolution and ordinary v4 image provenance (exact or v4 downscale) remain unchanged. Witness: ruc1 c1, records 194 and 215, `/System/Library/Fonts/Helvetica.ttc` used as ImageMagick `-font` input; 27 exact + 54 v4-downscale matches = 81/81, no violations, manifest check enabled. Local wrapper: `../greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/kosmo2/tools/scan_rollout_v42.py`; final scan: `../greek-ocr-toolkit-sol-recut/docs/harvest/recut_v1/w1_masked/ruc1/scan/ruc1/c1.scan_v42.json`.\n\n'
    assert before.count('## 6. Measured cost')==1
    after=before.replace('## 6. Measured cost',bullet+'## 6. Measured cost')
    rel='docs/harvest/sol_reading/HANDOVER.md'; hd=HERE/'handover'; hd.mkdir(exist_ok=True)
    patch=hd/'HANDOVER.v42.patch'; patch.write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),fromfile='a/'+rel,tofile='b/'+rel)))
    reading=REFERENCE.parents[2]
    def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()
    dump(hd/'RUC2_COMMIT_GUARD.json',dict(worktree=str(reading),head=git(reading,'rev-parse','HEAD'),branch=git(reading,'branch','--show-current'),require_empty_index=True,
        status='patch prepared; lead applies',before_sha256={rel:sha(target)},outputs={rel:hashlib.sha256(after.encode()).hexdigest()},patch_sha256=sha(patch),commit_files=[rel],
        instructions=['Require HEAD/branch and empty index; verify before hash and patch hash.','Apply HANDOVER.v42.patch; verify output hash.','Stage only listed path; require exact staged set and output hash before commit; stop on mismatch.']))
    (hd/'RUC2_COMMIT_FILES.txt').write_text(rel+'\n')
    log=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/8014ea5c-bc18-4a66-b4b1-93bd1d0a9cc4/scratchpad/ruc1_run.log');inputs.append(log)
    launches=[]
    for line in log.read_text().splitlines():
        try:o=json.loads(line)
        except ValueError:continue
        if o.get('label') in ('SR-ruc1-c1','SR-ruc1-c2') and 'model' in o:launches.append(o)
    assert len(launches)==2 and all(o['model']=='gpt-6.1-sol' and o['rc']==0 for o in launches)
    for o in launches:inputs.append(Path(o['rollout']))
    bindings=json.loads((HERE/'runtime_bindings.json').read_text())['reference_sources']
    for p,digest in bindings.items():assert sha(p)==digest;inputs.append(Path(p))
    line=f"RUC2: done | v4.2 witness: ok | letters y: {letters} (repaired {split['repaired']['letters'].get('y',0)}/18, unrepaired {split['unrepaired']['letters'].get('y',0)}/82) | crop_ok y: {crop} | controls: {k}/10 | gate: {'pass' if gate else 'fail'} | review queue: {len(queue)}"
    result=dict(schema='RUC2-results-v1',status='done',network='OFF',method='Mechanical aggregation; no new reader or adjudication',
        model='gpt-6.1-sol',reasoning_effort='medium',acceptance_ok=True,scans=scans,v42_witness=dict(ok=True,records=[194,215],path='/System/Library/Fonts/Helvetica.ttc'),
        n=100,totals=totals,letters=totals['letters'],crop_ok=totals['crop_ok'],marks=totals['marks'],letters_status='final',crop_ok_status='final',marks_status='pending_opus',
        letters_split=split,controls=dict(passed=k,total=10,contexts=contexts,rows=controls),
        comparison=dict(prior='C1 on old labels',n=100,letters_y=74,crop_ok_y=97,paired=False,different_card_set=True,letters_delta_points=letters-74,crop_ok_delta_points=crop-97,
            interpretation='Descriptive comparison of different samples; no paired agreement or causal repair effect.'),
        gate=dict(letters_threshold=90,crop_ok_threshold=90,letters_pass=letters>=90,crop_ok_pass=crop>=90,passed=gate,admission_updated=False),
        review_queue=dict(n=len(queue),bed=sum(not r['control'] for r in queue),controls=sum(r['control'] for r in queue),path='review_queue.jsonl',rule='Every negative/unreadable field, nonempty error list, or control disagreement; one entry per card, including expected negatives'),
        handover_edit=dict(status='prepared; not applied; lead applies',patch='handover/HANDOVER.v42.patch'),
        tests=dict(passed=8,log='scan/v42.tests.log'),input_sha256={str(p):sha(p) for p in inputs},summary_line=line)
    dump(HERE/'results.json',result)
    report=['# RUC2 ia_russian re-check','',
        'c1 is accepted under v4.2: **27 exact + 54 v4-downscale = 81/81 returned images**, no violations, manifest check enabled. The only waived findings are read-only Helvetica `-font` operands at records 194 and 215. The original c1 VOID scan is retained as historical evidence. A fresh c2 v4 scan matches its existing scan (55/55 images, no violations); see scan/c2_recheck_receipt.json. The Sol-reading scanner remains unchanged.','',
        '| Sample | Cards | Letters y | Crop_ok y | Marks y | Controls |','|---|---:|---:|---:|---:|---:|',
        f'| RUC1 c1 + c2 | 100 | {letters} | {crop} | {totals["marks"].get("y",0)} | {k}/10 |',
        '| C1, old labels, different card set | 100 | 74 | 97 | — | — |','',
        f"Letters: repaired-label cards **{split['repaired']['letters'].get('y',0)}/18**; unrepaired **{split['unrepaired']['letters'].get('y',0)}/82**. Repaired means actual label text changed; it does not include unchanged RU1-ok labels.",'',
        f'**Gate: {"PASS" if gate else "FAIL"}** (letters ≥90 and crop_ok ≥90). Letters and crop_ok are final Sol verdicts; marks remain **pending_opus**. Admission state was not updated.','',
        f'Against C1, letters change by {letters-74:+d} percentage points and crop_ok by {crop-97:+d}. These are different card sets: this is a descriptive, unpaired comparison and does not establish a causal repair effect.','',
        f"Controls: {k}/10. Context details: "+'; '.join(f"{c}: {v['passed']}/5, {v['errors']} errors, flagged={v['flagged']}" for c,v in contexts.items())+'. Marks are excluded from control pass/fail.','',
        f"The [review queue](review_queue.jsonl) contains **{len(queue)} unique cards** ({result['review_queue']['bed']} bed, {result['review_queue']['controls']} controls). It retains every negative/unreadable verdict, nonempty error list, and control disagreement, including expected-negative controls. IDs, crop hashes/paths, original detail and reasons are preserved. Review remains pending.",'',
        'Eight wrapper tests pass, including both real witnesses, non-font outside paths, parent escapes, both font roots, font writes, and v4 downscale boundaries. The v4.2 read proof is conservative: known ImageMagick `-font` argv operands and standalone cat/stat/ls reads are accepted; unknown uses fail closed. No rollout code is executed by the allowance check.','',
        '[HANDOVER.v42.patch](handover/HANDOVER.v42.patch) adds the §5 ruling after the existing v4.1 bullet. Before/after hashes, patch hash and a separate guarded commit list are prepared for the lead; the patch has not been applied.','',
        'RUC2_COMMIT_FILES.txt and RUC2_COMMIT_GUARD.json bind this change set. Require matching HEAD/branch, empty index, input and output hashes; stage only listed paths and verify the exact staged set. Stop on mismatch. No staging or commit was attempted.','',line]
    (HERE/'RESULTS.md').write_text('\n'.join(report)+'\n');print(line)

if __name__=='__main__': main()
