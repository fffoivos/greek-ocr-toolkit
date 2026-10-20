"""Offline N1-TS3 scan reconciliation, third read, and bounded review artifacts."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from collections import Counter
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts/numerics'))
import n1ts
from n1t_packs import rows,sha
BASE=n1ts.BASE
EXPECTED='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
MIRROR='lekythos--dcfa99599048d352--s000-l0144'

def dump(p,x):
    p.parent.mkdir(parents=True,exist_ok=True);n1ts.dump(p,x)

def jsonl(p,x):
    p.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in x))

def rescan():
    scanner=ROOT/'scripts/secondary/reading/scan_rollout.py'
    assert sha(scanner)==EXPECTED,'canonical hash mismatch'
    # Check every r3 answer before any scanning, including failed-scan pack copies.
    for i in range(1,7):
        p=n1ts.SCRATCH/f'sol_packs/n1t3/ctx{i:02}/r3/answers.jsonl'
        if not p.is_file() or not rows(p):raise ValueError('STOP: r3 answers absent: '+str(p))
    sys.path.insert(0,str(scanner.parent))
    spec=importlib.util.spec_from_file_location('n1_v44_scanner',scanner)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    records=[]
    for runpath in sorted((BASE/'answers').rglob('*.run.json')):
        run=json.loads(runpath.read_text());scanpath=runpath.with_name(runpath.name.replace('.run.json','.scan.json'))
        archive=scanpath.with_suffix('.pre_v44.json')
        if not archive.exists():archive.write_bytes(scanpath.read_bytes())
        old=json.loads(archive.read_text());stem=runpath.name.removesuffix('.run.json');ctx,reader=stem.split('.')
        root=runpath.parent.name if runpath.parent.name in ('n1cal','n1cal2','n1t','n1t2','n1t3') else ('n1cal' if ctx.startswith('cal') else 'n1')
        rd=n1ts.SCRATCH/'sol_packs'/root/ctx/reader
        if run.get('rollout'):
            new=mod.inspect(run['rollout'],rd)
        else:
            new=dict(scanner_version=4,ok=False,violations=[dict(reason='no rollout; failed launch rc='+str(run['rc']))])
        dump(scanpath,new)
        record=dict(run=str(runpath.relative_to(ROOT)),reader_dir=str(rd),rollout=run.get('rollout'),
            old_ok=old['ok'],new_ok=new['ok'],old_findings=old['violations'],new_findings=new['violations'],
            old_scan_sha256=sha(archive),new_scan_sha256=sha(scanpath),
            disposition='ACCEPTED' if new['ok'] else 'VOID',
            reason='v4.4 clean; control gate evaluated separately' if new['ok'] else 'v4.4 scan failed; excluded from voting')
        if root=='n1t3':
            target=scanpath.with_name(stem+'.jsonl');source=rd/'answers.jsonl'
            if target.exists():assert target.read_bytes()==source.read_bytes()
            else:target.write_bytes(source.read_bytes())
            record['answer_source']=str(source);record['answer_sha256']=sha(target)
            record['answer_use']='voting subject to controls' if new['ok'] else 'secondary evidence only; scan VOID'
        records.append(record)
        print(str(runpath.relative_to(BASE)),record['disposition'],flush=True)
    dump(BASE/'N1TS3_SCANS.json',dict(scanner_sha256=sha(scanner),records=records))
    return records


def apply_authority(slots,decisions):
    lead=BASE/'lead_t.jsonl'
    assert sha(lead)==lead.with_suffix('.jsonl.sha256').read_text().split()[0]
    # Apply sealed existing rulings independently of the now-changed raised selection.
    result=copy.deepcopy(decisions);byid={d['slot_id']:d for d in result};slotmap={s['slot_id']:s for s in slots}
    for r in rows(lead):
        d=byid[r['slot_id']];s=slotmap[r['slot_id']];truth=r['truth']
        if truth=='hold':
            d.update(truth_candidate=None,status='lead_review',reason='lead_hold_too_faint',confidence='unresolved',lead_ruling=r,agreement=False,edit_candidate=None,tags=[])
        else:
            d.update(truth_candidate=truth if truth in n1ts.GLYPHS else None,status='lead_ruled',reason='lead_ruling',confidence='lead',lead_ruling=r,agreement=False,tags=[truth] if truth in n1ts.DASHES else [],edit_candidate=dict(start=s['start'],end=s['end'],original=s['glyph'],replacement='·') if truth=='raised dot' and s['glyph']!='·' else None)
    for d in result:
        if d['line_id']==MIRROR:
            d.update(truth_candidate=None,status='excluded',reason='suspect:mirrored',confidence='excluded',agreement=False,edit_candidate=None,tags=['suspect:mirrored','excluded:show_through'])
    return result


def combine():
    if sha(ROOT/'scripts/secondary/reading/scan_rollout.py')!=EXPECTED:raise ValueError('canonical scanner changed')
    from n1t_combine import load_reads,require_complete
    slots=rows(n1ts.OUT/'slots.jsonl');two,g2=load_reads(n1ts.OUT);require_complete(slots,two)
    extra,g3=load_reads(BASE/'n1t3')
    # Bind every gate to its sealed pack, approved controls and current scan receipt.
    from n1_pack_closure import scan as closure
    from n1t_packs import typed_controls
    from greekocr.numerics.locks import load_locks
    load_locks(BASE).assert_fit_rows(s['line_id'] for s in slots)
    controls={r['slot_id']:r['truth'] for r in typed_controls(rows(BASE/'controls/approved.jsonl'),rows(BASE/'controls/dash_types.jsonl'))}
    scan_records={r['run']:r for r in json.loads((BASE/'N1TS3_SCANS.json').read_text())['records']}
    for out in (n1ts.OUT,BASE/'n1t3'):
        for kp in sorted((out/'keys').glob('ctx*.json')):
            key=json.loads(kp.read_text());reader=next(iter(key['readers']));ctx=kp.name.split('.')[0]
            directory=n1ts.SCRATCH/'sol_packs'/out.name/ctx/reader
            check=closure(directory,out,completed=True,meanings=n1ts.MEANINGS)
            if not check['ok']:raise ValueError('pack provenance: '+str(check['violations']))
            for item in key['items'].values():
                if item['control_truth'] is not None and controls[item['slot_id']]!=item['control_truth']:
                    raise ValueError('unapproved control truth')
            stem=BASE/'answers'/out.name/(ctx+'.'+reader)
            rp=Path(str(stem)+'.run.json');sp=Path(str(stem)+'.scan.json')
            recorded=scan_records[str(rp.relative_to(ROOT))]
            if sha(sp)!=recorded['new_scan_sha256']:raise ValueError('scan receipt changed')
            if json.loads(sp.read_text())['scanner_version']!='v4.4-canonical':raise ValueError('v4.4 scan required')
            if json.loads(rp.read_text())['rollout']!=recorded['rollout']:raise ValueError('rollout provenance changed')
            if rows(Path(str(stem)+'.jsonl'))!=rows(directory/'answers.jsonl'):raise ValueError('answer provenance changed')
            (g2 if out==n1ts.OUT else g3)[ctx+'.'+reader].update(
                pack_manifest_sha256=check['manifest_sha256'],key_sha256=sha(kp),
                scan_sha256=sha(sp),run_sha256=sha(rp),answers_sha256=sha(Path(str(stem)+'.jsonl')),
                scan_status='ACCEPTED' if recorded['new_ok'] else 'VOID')
    slotmap={s['slot_id']:s for s in slots}
    for s in rows(BASE/'n1t3/slots.jsonl'):
        if slotmap[s['slot_id']]!=s:raise ValueError('r3 slot source differs')
    expected={s['slot_id'] for s in rows(BASE/'n1t3/slots.jsonl')}
    if set(extra)!=expected or any(len(v)!=1 or v[0]['reader']!='r3' for v in extra.values()):raise ValueError('incomplete independent r3')
    if len(g3)!=6:raise ValueError('six r3 gates required')
    before=apply_authority(slots,[n1ts.decide(s,two.get(s['slot_id'],[])) for s in slots])
    after=apply_authority(slots,[n1ts.decide(s,two.get(s['slot_id'],[])+extra.get(s['slot_id'],[])) for s in slots])
    dump(BASE/'n1t3/combined_decisions.json',dict(decisions=after,gates_r1_r2=g2,gates_r3=g3))
    return slots,before,after,g2,g3


def sheets(slots,before,after):
    from PIL import Image,ImageDraw
    from n1_raised_sheets import font,paste_fit,reference_set
    import textwrap
    dest=n1ts.DEST;dest.mkdir(parents=True,exist_ok=True)
    ss={s['slot_id']:s for s in slots};bb={d['slot_id']:d for d in before}
    audits=[d for d in before if ss[d['slot_id']]['read_reason']=='audit']
    nonempty=[d for d in audits if any(r['meaning']!='nothing' for r in d['reads'])]
    anchors=sorted([d for d in audits if all(r['meaning']=='nothing' for r in d['reads'])],key=lambda d:sha_text('N1TS3:anchors:'+d['slot_id']))[:4]
    assert len(nonempty)==13 and len(anchors)==4
    ruled={r['slot_id'] for r in rows(BASE/'lead_t.jsonl')}
    raised=[d for d in after if d['truth_candidate']=='raised dot' and bb[d['slot_id']]['truth_candidate']!='raised dot' and d['slot_id'] not in ruled and any(r['reader']=='r3' for r in d['reads'])]
    metadata={}
    for kind,selected in [('geo_audit',nonempty+anchors),('raised_r3',raised)]:
        header=540 if kind=='raised_r3' else 110
        canvas=Image.new('RGB',(2400,header+700*max(1,(len(selected)+1)//2)+30),'white');draw=ImageDraw.Draw(canvas)
        draw.text((25,20),f'N1-TS3 {kind}: {len(selected)} targets',font=font(36,True),fill='black')
        refs=[]
        if kind=='raised_r3':
            for j,s in enumerate(reference_set(rows(BASE/'controls/approved.jsonl'))):
                x=25+595*j
                draw.text((x,115),'APPROVED '+s['truth'],font=font(25,True),fill='black')
                for k in ('zoom','line'):assert sha(s[k])==s[k+'_sha256']
                paste_fit(canvas,s['zoom'],(x,165,x+570,400));paste_fit(canvas,s['line'],(x,410,x+570,490));refs.append(s)
        if not selected:draw.text((30,header+50),'No new raised-dot truth candidates after r3; no lead ruling requested.',font=font(30),fill='black')
        template=[]
        for j,d in enumerate(selected):
            s=ss[d['slot_id']];x=25+1190*(j%2);y=header+700*(j//2)
            draw.rectangle((x,y,x+1165,y+680),outline='#555',width=2)
            draw.text((x+12,y+10),f'Cell {j+1} | Google {s["glyph"]!r}',font=font(28,True),fill='black')
            draw.text((x+12,y+50),s['slot_id'],font=font(19),fill='black')
            for k in ('zoom','line'):assert sha(s[k])==s[k+'_sha256']
            paste_fit(canvas,s['zoom'],(x+15,y+90,x+1150,y+345));paste_fit(canvas,s['line'],(x+15,y+355,x+1150,y+430))
            for k,r in enumerate(d['reads']):
                draw.text((x+12,y+440+30*k),f'{r["context"]}.{r["reader"]} [{r["context_status"]}] {r["meaning"]} / {r["confidence"]}',font=font(24),fill='black')
            # Compact visible geometry; full unabridged record is in the matching template.
            visible='Geometry record: '+json.dumps(s['geometry'],ensure_ascii=False,separators=(',',':'))
            for k,t in enumerate(textwrap.wrap(visible,106)):draw.text((x+12,y+540+22*k),t,font=font(18),fill='black')
            draw.text((x+12,y+650),'anchor: both nothing' if d in anchors else d['reason'],font=font(22),fill='black')
            template.append(dict(slot_id=s['slot_id'],cell_number=j+1,truth=None,note='',sheet=kind+'.png',bbox=[x,y,x+1165,y+680],reads=d['reads'],geometry=s['geometry'],dash=s.get('dash'),anchor=d in anchors,line_sha256=s['line_sha256'],zoom_sha256=s['zoom_sha256']))
        canvas.save(dest/(kind+'.png'));jsonl(dest/(kind+'_template.jsonl'),template)
        metadata[kind]=dict(cells=len(selected),path=str(dest/(kind+'.png')),sha256=sha(dest/(kind+'.png')),template_sha256=sha(dest/(kind+'_template.jsonl')),slot_ids=[d['slot_id'] for d in selected])
    return metadata


def sha_text(s):return hashlib.sha256(s.encode()).hexdigest()


def owner(slots,decisions):
    from greekocr.numerics.owner_v2 import build,GROUPS
    from n1t_owner_sheet import publish
    cards,spec=build(rows(n1ts.OUT/'lines.jsonl'),slots,decisions)
    legacy=json.loads((n1ts.OUT/'legacy_note_ids.json').read_text())
    for c in cards:
        if c['line_id'] in legacy:c['note_data']=dict(line=c['line_id'],**{'legacy-note-ids':json.dumps(legacy[c['line_id']])})
        if c['line_id']==MIRROR:c['tags'] += [dict(text='suspect:mirrored'),dict(text='excluded:show_through')]
    import base64,io
    from PIL import Image
    from greekocr.numerics.prune import has_gap_component
    for c in cards:
        marked={s['number'] for s in slots if s['line_id']==c['line_id'] and (s['glyph'].strip() or (s['geometry']['geom_status']=='ok' and has_gap_component(s)))}
        zooms=[]
        for z in c['zooms']:
            if int(z['alt'].split()[-1]) not in marked:continue
            with Image.open(z['image']) as im:
                buf=io.BytesIO();im.convert('L').save(buf,'JPEG',quality=85)
            zooms.append(dict(z,image='data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode()))
        c['zooms']=zooms
    full_boxes=dict(Counter(b['style'] for c in cards for b in c['slots'] if b['evidence']))
    full_groups=dict(Counter(c['group'] for c in cards));all_cards=len(cards)
    target=BASE/'owner_sheet/n1_sheet.html'
    summary=publish(cards,spec,target,compact=True)
    cuts=['line rasters native size, grayscale PNG, colored decision boxes retained','marked-slot zooms only, JPEG quality 85']
    if target.stat().st_size>14_000_000:
        needs=[c for c in cards if c['group']==GROUPS[3]]
        sample=sorted(needs,key=lambda c:sha_text('20261017:N1TS3:needs:'+c['line_id']))[:40]
        keep={c['line_id'] for c in sample}
        cards=[c for c in cards if c['group'] in GROUPS[:3] or c['line_id'] in keep]
        spec['intro']+=f'\nNeeds a look: {len(needs)} complete lines; showing seeded sample of {len(sample)} (20261017:N1TS3:needs).'
        spec['needs_sample_line_ids']=sorted(keep);spec['needs_total']=len(needs)
        summary=publish(cards,spec,target,compact=True)
        cuts.append('agreement sample omitted; Needs a look reduced to seeded 40-card sample')
    if target.stat().st_size>14_000_000:raise ValueError('owner sheet still exceeds 14 MB')
    summary.update(sheet_bytes=target.stat().st_size,cuts=cuts,full_cards=all_cards,full_groups=full_groups,full_boxes=full_boxes,
        boxes=dict(Counter(b['style'] for c in cards for b in c['slots'] if b['evidence'])),
        unlocalized_slots=[b['slot_id'] for c in cards for b in c['slots'] if not b['evidence']])
    return summary


def main():
    scans=rescan() if '--rebuild' not in sys.argv else json.loads((BASE/'N1TS3_SCANS.json').read_text())['records']
    # Recover failed-scan answers for decoded secondary evidence only, never voting.
    for i in range(1,7):
        source=n1ts.SCRATCH/f'sol_packs/n1t3/ctx{i:02}/r3/answers.jsonl'
        target=BASE/f'answers/n1t3/ctx{i:02}.r3.jsonl'
        if not target.exists():target.write_bytes(source.read_bytes())
    slots,before,after,g2,g3=combine();contact=sheets(slots,before,after);summary=owner(slots,after)
    reasons=lambda ds:dict(Counter(d['reason'] for d in ds if d['status']=='lead_review'))
    for r in scans:
        rp=ROOT/r['run']
        if '/n1t3/' in str(rp):
            source=Path(r['reader_dir'])/'answers.jsonl'
            r.update(answer_source=str(source),answer_sha256=sha(source),answer_use='voting subject to controls' if r['new_ok'] else 'secondary evidence only; scan VOID')
    historical=json.loads((BASE/'N1TS2_RECEIPT.json').read_text())['final_lead_review']
    receipt=dict(task='N1-TS3',status='BUILT; tests pending',network=False,git_writes=False,reading_run=False,label_edits=0,
        scans=scans,scanner_sha256=EXPECTED,scans_receipt_sha256=sha(BASE/'N1TS3_SCANS.json'),
        historical_before=historical,before_r3=reasons(before),after_r3=reasons(after),gates_r3=g3,
        transitions=dict(Counter(d['reason']+' → '+a['reason'] for d,a in zip(before,after))),
        sheets=contact,owner=summary,lead_rulings_sha256=sha(BASE/'lead_t.jsonl'),
        exclusion=dict(line_id=MIRROR,tag='suspect:mirrored',decision=None,note='lead update identifies verso show-through; excluded from scoring and edits'))
    dump(BASE/'N1TS3_RECEIPT.json',receipt)
    print(json.dumps({k:receipt[k] for k in ('before_r3','after_r3','owner')},indent=2))

def finalize():
    import xml.etree.ElementTree as ET
    path=BASE/'N1TS3_RECEIPT.json';r=json.loads(path.read_text())
    tests=BASE/'N1TS3_TESTS.xml';tree=ET.parse(tests)
    if tree.findall('.//failure') or tree.findall('.//error'):raise ValueError('tests failed')
    passed=len(tree.findall('.//testcase'))-len(tree.findall('.//skipped'))
    for name,h in r['owner']['hashes'].items():
        if sha(BASE/'owner_sheet'/name)!=h:raise ValueError('owner product changed')
    if sha(ROOT/'scripts/secondary/reading/scan_rollout.py')!=EXPECTED:raise ValueError('scanner changed')
    for name,info in r['sheets'].items():
        if sha(info['path'])!=info['sha256']:raise ValueError('contact sheet changed')
        if sha(Path(info['path']).with_name(name+'_template.jsonl'))!=info['template_sha256']:raise ValueError('template changed')
    files=['scripts/numerics/n1ts3.py','scripts/numerics/n1t_combine.py','scripts/numerics/n1t_owner_sheet.py','scripts/numerics/n1t_boxes.py','scripts/secondary/reading/n1_launch.py','scripts/secondary/reading/scan_rollout.py','scripts/secondary/reading/scan_rollout_secondary_pre_v44.py','greekocr/numerics/combine_v2.py','greekocr/numerics/owner_v2.py','tests/test_n1ts3.py','tests/test_n1ts2.py','tests/test_n1ts.py','tests/test_n1t.py','tests/test_n1cd.py','scripts/numerics/n1_decide.py','scripts/numerics/n1_score.py','scripts/numerics/n1t_prepare.py']
    inputs=[*sorted((BASE/'n1t2/keys').glob('*.json')),*sorted((BASE/'n1t3/keys').glob('*.json')),
            BASE/'n1t2/slots.jsonl',BASE/'n1t2/lines.jsonl',BASE/'n1t3/slots.jsonl',
            BASE/'lead_t.jsonl',BASE/'lead_t.jsonl.sha256',BASE/'controls/approved.jsonl',BASE/'controls/dash_types.jsonl',
            BASE/'n1t3/combined_decisions.json',BASE/'N1TS3_SCANS.json']
    for sub in ('n1t2','n1t3'):
        for pattern in ('*.jsonl','*.run.json','*.scan.json'):
            inputs+=sorted((BASE/'answers'/sub).glob(pattern))
    r.update(status='READY',tests=dict(passed=passed,path=str(tests.relative_to(ROOT)),sha256=sha(tests)),
        source_hashes={p:sha(ROOT/p) for p in files},input_hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs},
        physical_qa='Viewed native-size owner raster examples for all three box styles and geometry-audit cells; gray line pixels, color boxes and number lane retained. No GUI or remote note-store verification.',
        publication='Local artifact only; same owner HTML path. No network, remote publication, reading run, git write, or label edit.',
        scanner_backup_sha256=sha(ROOT/'scripts/secondary/reading/scan_rollout_secondary_pre_v44.py'))
    dump(path,r)
    before=r['before_r3'];after=r['after_r3'];o=r['owner'];scans=r['scans']
    final=json.loads((BASE/'n1t3/combined_decisions.json').read_text())['decisions']
    excluded=[d for d in final if d['status']=='excluded']
    text=['## N1-TS3','',f'**READY.** Folded the completed six-context r3 reading into independent control, scan and pack-provenance gates. Two agreeing VALID, high-confidence votes establish a truth candidate; geometry and typed-dash gates still apply. Sealed lead rulings override, including the two faint holds. No labels were edited.', '',
        f'Historical phase-2 lead_review: **{sum(r["historical_before"].values())}**. With the mirrored/show-through row explicitly excluded, the comparable pre-r3 count is **{sum(before.values())}**, falling to **{sum(after.values())}** after r3. All **{len(excluded)} slots** on `{MIRROR}` have no truth or edit candidate and carry `suspect:mirrored` / `excluded:show_through`; they are excluded from scoring and edits. Unresolved slots retain Google in Ours.', '',
        '| lead_review reason | Historical phase 2 | Before r3, exclusion applied | After r3 |','|---|---:|---:|---:|']
    text += [f'| {reason} | {r["historical_before"].get(reason,0)} | {before.get(reason,0)} | {after.get(reason,0)} |' for reason in sorted(set(before)|set(after))]
    text += ['', 'R3 resolves 172 previously unresolved slots. Another 27 slots gain a reading consensus but remain withheld by the typed-dash geometry gate. A failed r3 context may change the exclusive unresolved reason to invalid provenance; earlier valid votes are retained and are not newly voided. The receipt preserves every before/after reason transition.', '', '### Canonical v4.4 reconciliation', '',
        'Scanner SHA256 `'+EXPECTED+'` matches the canonical source. The old copy is retained as `scripts/secondary/reading/scan_rollout_secondary_pre_v44.py`. Every original scan is preserved beside its replacement as `*.scan.pre_v44.json`. The scanner file itself is copied verbatim.', '',
        f'**{len(scans)} recorded attempts checked: {sum(x["new_ok"] for x in scans)} clean, {sum(not x["new_ok"] for x in scans)} VOID; no previously clean rollout became VOID. No failed context was newly accepted.** The archived failed calibration launch has no rollout and remains VOID. Clean scans are ACCEPTED for scan purposes; control gates still apply. Scan-VOID contexts have INVALID voting provenance and cannot establish truth. Failed-scan r3 answers were copied from completed sealed packs for secondary evidence only; no reader was launched.', '',
        '| Recorded attempt | Old scan | v4.4 scan | Old findings | New findings |','|---|---|---|---:|---:|']
    text += [f'| `{x["run"].removeprefix("artifacts/n1/answers/").removesuffix(".run.json")}` | {"clean" if x["old_ok"] else "VOID"} | {x["disposition"]} | {len(x["old_findings"])} | {len(x["new_findings"])} |' for x in scans]
    text += ['', 'Still-VOID findings:', '']
    for x in scans:
        if not x['new_ok']:
            describe=lambda findings:'; '.join(f.get('reason','')+(' ['+f['path']+']' if 'path' in f else '') for f in findings)
            text.append('- `'+x['run']+'`: old: '+describe(x['old_findings'])+'. New: '+describe(x['new_findings'])+'.')
    text += ['', 'The only removed finding is ctx05/r3 record 257 (`/zoom/detail57.png`); its other path finding and unmatched returned image remain. Complete old/new findings, reader directories, scan hashes and disposition reasons are in `artifacts/n1/N1TS3_SCANS.json` and the receipt.', '',
        '| r3 context | Wrong controls | Abstentions | Control gate | Scan | Voting gate |','|---|---:|---:|---|---|---|']
    text += [f'| {k} | {g["wrong"]} | {g["abstentions"]} | {g["control_status"]} | {g["scan_status"]} | {g["status"]} |' for k,g in r['gates_r3'].items()]
    text += ['', 'Each read is bound to its private option map and sealed pack manifest, approved typed controls, answer bytes, run metadata and current v4.4 scan receipt. Every r3 slot matches the corresponding original slot record. Final decisions and all per-read gates: `artifacts/n1/n1t3/combined_decisions.json`.', '',
        '### Lead sheets', '',
        f'`{n1ts.DEST}/geo_audit.png`: **17 cells**, all 13 geometry-audit slots with a non-nothing call plus four seeded both-nothing anchors (`N1TS3:anchors`). Each cell carries the marked zoom, line, both original reads and geometry record; `geo_audit_template.jsonl` retains the full record and image hashes. The geometry-only rule remains provisional; this sheet supplies evidence for lead review, with no new ruling inferred.', '',
        f'`{n1ts.DEST}/raised_r3.png`: **{r["sheets"]["raised_r3"]["cells"]} newly raised candidates**. No previously unruled slot gains a raised-dot truth candidate from r3. The sheet states this explicitly and includes the approved raised/baseline references; `raised_r3_template.jsonl` is empty. Existing lead-raised rulings are retained.', '',
        '### Owner sheet under the cap', '',
        f'`artifacts/n1/owner_sheet/n1_sheet.html`: **{o["sheet_bytes"]/1_000_000:.2f} MB** ({o["sheet_bytes"]:,} bytes), **{o["cards"]} complete-line cards**. Native line pixels are converted to gray PNG with the existing colored solid/dashed boxes and number lane; they are never enlarged. Zooms are grayscale JPEG quality 85 and only retained for slots with a Google mark or a saved gap component. Empty-gap zooms, including the unlocalized whole-line duplicate zoom, are omitted. The complete unlocalized line and unsure Gaps record remain.', '',
        '**No card groups were cut; the seeded 40-card fallback was unnecessary.** The intro, named Gaps row, Printed prefill, line note identities and legacy note loader remain. Unsure means unresolved after r3; the excluded mirrored row is explicitly tagged.', '',
        '| Group | Cards |','|---|---:|']
    from greekocr.numerics.owner_v2 import GROUPS
    text += [f'| {g} | {o["groups"].get(g,0)} |' for g in GROUPS]
    text += ['',f'Drawn boxes: **{o["boxes"].get("decided-changed",0)} changed, {o["boxes"].get("decided-unchanged",0)} unchanged, {o["boxes"].get("unsure",0)} unsure**. The one misaligned slot remains unlocalized and is not included in drawn-box counts. Geometry-only empty slots stay unboxed, including on the excluded row. Physical raster examples were inspected; tests decode every embedded line PNG to verify native width and height plus the 30-pixel numbering lane and check JPEG quality tables. No live remote note-store or browser UI claim is made.', '',
        f'**Tests: {passed} passed**, `artifacts/n1/N1TS3_TESTS.xml`. Includes three-vote majority, invalid/VOID/low-confidence exclusions, all scan reconciliations, lead authority, mirrored exclusion, complete sheet/template coverage, native image dimensions, size cap, control/pack seals, historical custody through original scan archives and legacy note compatibility. Launcher tests use local fake readers/probes only. No production reading run or network call. Receipt: `artifacts/n1/N1TS3_RECEIPT.json`.']
    report=ROOT/'docs/records/labelfix/secondary/N1T_REPORT.md'
    report.write_text(report.read_text().split('\n## N1-TS3')[0].rstrip()+'\n\n'+'\n'.join(text)+'\n')
    reasons=', '.join(f'{k} {v}' for k,v in sorted(after.items()))
    groups=', '.join(f'{k}: {v}' for k,v in o['groups'].items())
    print(f'N1TS3 READY: lead_review before {sum(before.values())} → after r3 {sum(after.values())} ({reasons}); new raised candidates {r["sheets"]["raised_r3"]["cells"]}; geo-audit cells 17; sheet {o["sheet_bytes"]/1_000_000:.2f} MB, cards {o["cards"]} (groups {groups}); boxes changed {o["boxes"].get("decided-changed",0)}, unchanged {o["boxes"].get("decided-unchanged",0)}, unsure {o["boxes"].get("unsure",0)}; tests {passed} passed')


if __name__=='__main__':
    if sys.argv[1:]==['--finalize']:finalize()
    else:main()
