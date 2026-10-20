"""Post-read r2 scoring. No readers, geometry preparation or threshold changes."""
import gzip
from r2_common import *
from runtime_r2 import map_records
from score_cp7b import matrix, flags, compact_evidence
from PIL import Image, ImageDraw, ImageFont
SCREENS=('union','merged','neighbour_words','orientation','crossing')
TRUTH_FIELDS=('neighbour_whole_word','multi_line','rotated','horizontally_missegmented')

def truth(answer):
    return any(answer[f]=='yes' for f in TRUTH_FIELDS)

def predictions(s):
    p={f:s[f] is True for f in ('merged','neighbour_words','orientation')}
    p['crossing']=s['crossing']['drop'] is True
    p['union']=any(p.values())
    return p

def actual_for(screen,a):
    # Every screen is audited against owner DROP-truth, as in CP7b.
    return truth(a)

def mismatches(s,a):
    # A policy-only loss must not become a measured FP or FN.
    if s['geometry_unavailable']:return {}
    return {f:('FP' if p else 'FN') for f,p in predictions(s).items() if p!=actual_for(f,a)}

def validate():
    guard()
    verify()
    freeze_sha = sha(FREEZE)
    build = read(R2/'build_receipt.json')
    assert sha(R2/'keys/sealed_decisions.jsonl.gz') == build['sealed_decisions_sha256']
    assert sha(R2/'keys/draw.jsonl') == build['draw_sha256']
    assert sha(BASE/'tools/scan_rollout.py') == SCANNER
    seals = [json.loads(line) for line in gzip.open(R2/'keys/sealed_decisions.jsonl.gz', 'rt')]
    by = {s['row_id']: s for s in seals}
    assert len(by) == len(seals) == 100
    assert set(by) == {r['id'] for r in rows(R2/'keys/draw.jsonl')}
    approved = {c['source_card']['card_id']: c for c in read(ROOT/'docs/harvest/recut_v1/w1_masked/caps1/keys/control_truth.json')}
    log = (BASE/'run_r2.log').read_text()
    logged_runs = [json.loads(line) for line in log.splitlines() if line.startswith('{"label":')]
    records, controls, custody = [], [], []
    for bed in BEDS_R2:
        key = read(R2/'keys'/f'{bed}.json')
        directory = PACK_ROOT/bed/'r1'
        manifest = read(directory.parent/'MANIFEST.r1.json')['files']
        assert all(sha(directory/p) == digest for p, digest in manifest.items())
        cards = rows(directory/'cards.jsonl')
        mapped, control = map_records(rows(R2/'answers'/bed/'r1.jsonl'), cards, key)
        assert mapped == rows(R2/'answers'/bed/'r1.mapped.jsonl')
        assert control == rows(R2/'answers'/bed/'r1.controls.jsonl')
        assert rows(directory/'answers.jsonl') == rows(R2/'answers'/bed/'r1.jsonl')
        receipt = read(R2/'receipts'/f'{bed}.json')
        scan = read(R2/'scan'/bed/'r1.scan.json')
        assert scan['ok'] and not scan['violations'] and not scan['manifest_check_skipped']
        assert sha(scan['rollout']) == scan['rollout_sha256']
        assert receipt['run'] == next(r for r in logged_runs if r['label'] == receipt['run']['label'])
        assert receipt['run']['usage'] == scan['total_token_usage']
        assert receipt['run']['rollout'] == scan['rollout']
        assert receipt['run']['rc'] == receipt['scanner_rc'] == receipt['mapping_rc'] == 0
        assert receipt['run']['model'] == 'gpt-6.1-sol'
        assert receipt['freeze_sha256'] == freeze_sha and receipt['canonical_scanner_sha256'] == SCANNER
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
            local_crop = R2/'crops'/crop.name
            assert local_crop.read_bytes() == crop.read_bytes()
            pred = predictions(s)
            assert s['screen_drop'] is s['composed']['drop']
            assert s['screen_drop'] == any((s['geometry_unavailable'], pred['union']))
            actual = truth(a)
            mismatch = mismatches(s, a)
            records.append(dict(context=bed, context_valid=valid, row_id=a['line_id'], card_id=a['card_id'],
                crop_path=str(crop), crop_copy=str(local_crop.relative_to(ROOT)), crop_sha256=sha(crop),
                reader=a, truth='DROP' if actual else 'KEEP', predictions=pred,
                mismatches=mismatch, flag=flags(a), unreadable=any(a[f]=='u' for f in ('letters','marks','crop_ok')),
                sealed=s))
    assert len(records) == len({r['row_id'] for r in records}) == 100 and len(controls) == 10
    return records, controls, custody

def summarize(records,controls,custody):
    valid=[r for r in records if r['context_valid']]
    measured=[r for r in valid if not r['sealed']['geometry_unavailable']]
    matrices={f:matrix([(r['predictions'][f],actual_for(f,r['reader'])) for r in measured]) for f in SCREENS}
    policy=[r for r in valid if r['sealed']['geometry_unavailable']]
    clips=[r for r in valid if r['reader']['end_clip']=='yes']
    diagnostic=[r for r in valid if r['sealed']['edge_clip_candidate'] is not None]
    adjudicate=[r for r in records if r['mismatches'] or r['flag'] or r['unreadable'] or r['reader']['end_clip']=='yes']
    passed=sum(c['passed'] for c in controls)
    scans_ok=len(custody)==2 and all(c['scan_ok'] for c in custody)
    return dict(gate_pass=all(m['FP']==m['FN']==0 for m in matrices.values()) and passed==10 and len(records)==100 and len(valid)==100 and scans_ok,
        controls_passed=passed,mapped=len(records),scored=len(valid),scans_ok=scans_ok,custody=custody,
        matrices=matrices,screen_denominator=len(measured),matrix_truth='owner DROP union for every screen; geometry-unavailable rows excluded as policy',
        composed_with_policy=matrix([(r['sealed']['screen_drop'] is True,truth(r['reader'])) for r in valid]),
        geometry_unavailable=dict(total=len(policy),reader_drop=sum(truth(r['reader']) for r in policy),row_ids=[r['row_id'] for r in policy],classification='policy, not screen error'),
        orientation_unknown=sum(r['sealed']['orientation_unknown'] for r in valid),
        end_clip=dict(total=len(clips),denominator=len(valid),rate=len(clips)/len(valid) if valid else None,known_class=True),
        edge_clip_candidate=dict(measured=len(diagnostic),unavailable=len(valid)-len(diagnostic),agreement=matrix([(r['sealed']['edge_clip_candidate'],r['reader']['end_clip']=='yes') for r in diagnostic]),gating=False,interpretation='lower bound'),
        adjudication_ids=[r['row_id'] for r in adjudicate])

def write_outputs(records,controls,summary):
    dump(R2/'score_summary.json',summary);dump(R2/'controls.json',controls)
    (R2/'scored.jsonl.gz').write_bytes(gzip.compress(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records).encode(),mtime=0))
    selected=[r for r in records if r['row_id'] in summary['adjudication_ids']]
    sheet=['# CP7 r2 adjudication','', 'Reader truth awaits lead pixel adjudication. End-clips are a known admitted class. Policy losses are separate from screen errors.','']
    font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',14);contacts=[]
    for start in range(0,len(selected),30):
        batch=selected[start:start+30];canvas=Image.new('RGB',(1500,240*((len(batch)+1)//2)),'white');d=ImageDraw.Draw(canvas)
        for i,r in enumerate(batch):
            x=i%2*750;y=i//2*240
            d.text((x+8,y+6),r['row_id'],font=font,fill='black')
            d.text((x+8,y+28),r['card_id']+' '+r['truth'],font=font,fill='black')
            with Image.open(r['crop_path']) as im:
                im=im.convert('RGB');im.thumbnail((734,178));canvas.paste(im,(x+8,y+54))
        name=f'ADJUDICATION_{start//30+1:02d}.png';canvas.save(R2/name)
        contacts.append(dict(path=name,rows=[r['row_id'] for r in batch],size=list(canvas.size)))
    for r in selected:
        sheet.extend([f"## {r['row_id']}",'',f"Crop: `{r['crop_path']}`; SHA `{r['crop_sha256']}`",'', '```json',json.dumps(dict(reader=r['reader'],mismatches=r['mismatches'],evidence=compact_evidence(r['sealed']),edge_clip=r['sealed']['edge_clip_diagnostic']),ensure_ascii=False,indent=2),'```','', 'Lead pixel adjudication: pending.',''])
    (R2/'ADJUDICATION_SHEET.md').write_text('\n'.join(sheet)+'\n');dump(R2/'contact_sheets.json',contacts)

def main():
    records,controls,custody=validate()
    summary=summarize(records,controls,custody)
    write_outputs(records,controls,summary);verify()
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
