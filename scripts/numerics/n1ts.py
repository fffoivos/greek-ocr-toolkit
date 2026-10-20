"""Offline N1-TS phase 1 and explicitly authorized phase 2. Never starts readers."""
import argparse
from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys
import textwrap

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.numerics.combine_v2 import decide, GLYPHS, DASHES, MEANINGS
from greekocr.numerics.locks import load_locks
from n1t_combine import load_reads, require_complete
from n1t_packs import rows, sha, typed_controls
from n1_render import SCRATCH
from n1_raised_sheets import reference_set, paste_fit, font

BASE = ROOT/'artifacts/n1'
OUT = BASE/'n1t2'
DEST = SCRATCH/'n1_review/t_lead'
SEED = '20261017:N1TS:review'


def dump(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def selections(decisions):
    raised = [d for d in decisions if d['truth_candidate']=='raised dot' or
              any(r['meaning']=='raised dot' for r in d['reads'])]
    review = [d for d in decisions if d['status']=='lead_review']
    rank = lambda d: hashlib.sha256((SEED+':'+d['slot_id']).encode()).hexdigest()
    return sorted(raised, key=lambda d:d['slot_id']), sorted(review, key=rank)


def combine(out=OUT):
    slots=rows(out/'slots.jsonl');reads,gates=load_reads(out)
    require_complete(slots,reads)
    if len(gates)!=28: raise ValueError('exactly 14 contexts x 2 required')
    decisions=[decide(s,reads.get(s['slot_id'],[])) for s in slots]
    blocked=[f'ctx{i:02}' for i in range(1,15) if all(
        gates[f'ctx{i:02}.{r}']['control_status']=='VOID' for r in ('r1','r2'))]
    return slots, decisions, gates, blocked


def render_sheets(slots, decisions, dest=DEST):
    from PIL import Image, ImageDraw
    dest.mkdir(parents=True,exist_ok=True)
    byid={s['slot_id']:s for s in slots}
    raised,review=selections(decisions)
    refs=reference_set(rows(BASE/'controls/approved.jsonl'))
    sheets=[];locations={}
    for kind,selected,per_page in [('raised',raised,8),('review',review[:120],12)]:
        for off in range(0,len(selected),per_page):
            chunk=selected[off:off+per_page];num=off//per_page+1
            header=540 if kind=='raised' else 120
            canvas=Image.new('RGB',(2400,header+640*((len(chunk)+1)//2)+30),'white');draw=ImageDraw.Draw(canvas)
            draw.text((30,18),f'N1-TS {kind} / sheet {num} / lead printed-glyph check',font=font(36,True),fill='black')
            draw.text((30,65),'All reads retained; INVALID/VOID reads do not establish truth. Fill lead_t_template.jsonl.',font=font(25),fill='black')
            refinfo=[]
            if kind=='raised':
                for j,s in enumerate(refs):
                    for k in ('line','zoom'):
                        if sha(s[k])!=s[k+'_sha256']:raise ValueError('reference image changed')
                    x=25+595*j
                    draw.rectangle((x,112,x+580,512),outline='#777',width=2)
                    draw.text((x+10,122),f'APPROVED {s["truth"]}',font=font(25,True),fill='black')
                    paste_fit(canvas,s['zoom'],(x+10,163,x+570,405))
                    paste_fit(canvas,s['line'],(x+10,412,x+570,490))
                    refinfo.append(dict(slot_id=s['slot_id'],truth=s['truth'],zoom_sha256=s['zoom_sha256'],line_sha256=s['line_sha256']))
            cells=[];name=f'{kind}_{num:02}.png'
            for j,d in enumerate(chunk):
                s=byid[d['slot_id']];x=25+1190*(j%2);y=header+640*(j//2)
                for k in ('line','zoom'):
                    if sha(s[k])!=s[k+'_sha256']:raise ValueError('slot image changed')
                draw.rectangle((x,y,x+1165,y+620),outline='#555',width=2)
                draw.text((x+12,y+10),f'{kind} cell {off+j+1} | Google {json.dumps(s["glyph"],ensure_ascii=False)}',font=font(28,True),fill='black')
                for k,t in enumerate(textwrap.wrap(s['slot_id'],88)):
                    draw.text((x+12,y+48+24*k),t,font=font(21),fill='black')
                paste_fit(canvas,s['zoom'],(x+15,y+100,x+1150,y+365))
                paste_fit(canvas,s['line'],(x+15,y+375,x+1150,y+450))
                for k,r in enumerate(d['reads']):
                    draw.text((x+12,y+460+32*k),f'{r["context"]}.{r["reader"]} [{r["context_status"]}] {r["meaning"]} / {r["confidence"]}',font=font(25),fill='black')
                dash=s.get('dash',{});ratio=dash.get('dash_len_ratio')
                draw.text((x+12,y+530),f'Geometry: {dash.get("geometric_type") or "none"}; dash_len_ratio: {ratio if ratio is not None else "unavailable"}',font=font(25),fill='black')
                draw.text((x+12,y+566),d['reason'],font=font(23),fill='black')
                cell=dict(slot_id=s['slot_id'],cell_number=off+j+1,bbox=[x,y,x+1165,y+620],
                    google_glyph=s['glyph'],reads=d['reads'],dash=dash,reason=d['reason'],
                    line_sha256=s['line_sha256'],zoom_sha256=s['zoom_sha256'])
                cells.append(cell);locations.setdefault(s['slot_id'],[]).append(dict(sheet=name,cell=off+j+1))
            path=dest/name;canvas.save(path)
            sheets.append(dict(file=name,sha256=sha(path),set=kind,cells=cells,references=refinfo,total_cells=len(cells)+len(refinfo)))
    remainder=review[120:]
    index=dict(seed=SEED,raised_cells=len(raised),review_cells=min(120,len(review)),review_total=len(review),
        deferred_by_reason=dict(Counter(d['reason'] for d in remainder)),
        deferred_slots=[dict(slot_id=d['slot_id'],reason=d['reason']) for d in remainder],
        reference_note='Approved controls from multiple documents; no same-document match asserted.',
        sheets=sheets,template_meanings=list(MEANINGS)+['keep Google'])
    dump(dest/'sheets_index.json',index)
    template=[]
    required={x['slot_id'] for x in raised+review}
    for d in decisions:
        if d['slot_id'] in required:
            template.append(dict(slot_id=d['slot_id'],truth=None,note='',reason=d['reason'],
                google_glyph=byid[d['slot_id']]['glyph'],truth_candidate=d['truth_candidate'],
                reads=d['reads'],sheets=locations.get(d['slot_id'],[])))
    target=BASE/'lead_t_template.jsonl'
    if not target.exists():target.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in template))
    elif [r['slot_id'] for r in rows(target)]!=[r['slot_id'] for r in template]:
        raise ValueError('existing lead template differs; refusing overwrite')
    return index


def apply_lead(slots, decisions, rulings, blocked=(), partial=False):
    if blocked:raise ValueError('re-read required for both-VOID contexts: '+', '.join(blocked))
    raised,review=selections(decisions);required={d['slot_id'] for d in raised+review}
    byid={r['slot_id']:r for r in rulings}
    if len(byid)!=len(rulings) or (not set(byid)<=required) or (not partial and set(byid)!=required):
        raise ValueError('exact complete lead ruling coverage required')
    if partial and set(byid)!={d['slot_id'] for d in raised}:
        raise ValueError('partial rulings must cover exactly the raised set')
    slotmap={s['slot_id']:s for s in slots};result=copy.deepcopy(decisions)
    for d in result:
        if d['slot_id'] not in byid:continue
        r=byid[d['slot_id']];truth=r.get('truth')
        if truth not in (*MEANINGS,'keep Google','hold'):raise ValueError('unfilled/invalid lead ruling: '+d['slot_id'])
        if truth=='hold':
            d.update(truth_candidate=None,status='lead_review',reason='lead_hold_too_faint',
                     confidence='unresolved',lead_ruling=r,agreement=False,edit_candidate=None,tags=[])
            continue
        d.update(truth_candidate=truth if truth in GLYPHS else None,status='lead_ruled',
            reason='lead_ruling',confidence='lead',lead_ruling=r,agreement=False,tags=[truth] if truth in DASHES else [])
        s=slotmap[d['slot_id']]
        d['edit_candidate']=dict(start=s['start'],end=s['end'],original=s['glyph'],replacement='·') if (
            truth=='raised dot' and s['glyph']!='·') else None
        d.update(edit=None,apply_edit=False)
    return result


def phase1():
    calibration=json.loads((BASE/'N1CAL2S_RECEIPT.json').read_text())
    if calibration['status']!='PASS' or calibration['score']['correct']!=81:raise ValueError('calibration not PASS 81/82')
    slots,decisions,gates,blocked=combine()
    locks=load_locks(BASE);locks.assert_fit_rows(s['line_id'] for s in slots)
    controls=typed_controls(rows(BASE/'controls/approved.jsonl'),rows(BASE/'controls/dash_types.jsonl'))
    for kp in (OUT/'keys').glob('ctx*.json'):
        truth={r['slot_id']:r['truth'] for r in controls}
        for item in json.loads(kp.read_text())['items'].values():
            if item['control_truth'] is not None and truth[item['slot_id']]!=item['control_truth']:raise ValueError('control seal mismatch')
    dump(OUT/'decisions.json',dict(decisions=decisions,gates=gates,blocked_contexts=blocked))
    index=render_sheets(slots,decisions)
    decided=[d for d in decisions if d['status']=='truth_candidate'];byid={d['slot_id']:d for d in decisions}
    matrix=Counter((s['glyph'],byid[s['slot_id']]['truth_candidate']) for s in slots if byid[s['slot_id']]['status']=='truth_candidate')
    audit=[dict(slot_id=s['slot_id'],reads=byid[s['slot_id']]['reads'],
        raw_agree=all(r['meaning']=='nothing' for r in byid[s['slot_id']]['reads']),
        decided_nothing=byid[s['slot_id']]['truth_candidate']=='nothing') for s in slots if s['read_reason']=='audit']
    summary=dict(slots=len(slots),decided=len(decided),read_decided=sum(bool(d['reads']) for d in decided),
        geometry_only=sum(not d['reads'] for d in decided),lead_review=len(decisions)-len(decided),
        reasons=dict(Counter(d['reason'] for d in decisions if d['status']=='lead_review')),
        meanings=dict(Counter(d['truth_candidate'] for d in decided)),gates=gates,blocked_contexts=blocked,
        google_ours=[dict(google=g,ours=o,count=n) for (g,o),n in sorted(matrix.items())],
        geometry_audit=audit,audit_agree=sum(a['raw_agree'] for a in audit),audit_decided=sum(a['decided_nothing'] for a in audit),
        raised_cells=index['raised_cells'],review_cells=index['review_cells'],sheets=len(index['sheets']),
        deferred_by_reason=index['deferred_by_reason'],owner_sheet_sha256=sha(_data_input(BASE/'owner_sheet/n1_sheet.html')),
        owner_products={p.name:sha(p) for p in (BASE/'owner_sheet').glob('*') if p.is_file()},
        source_hashes={str(p.relative_to(ROOT)):sha(p) for p in [OUT/'slots.jsonl',OUT/'lines.jsonl',OUT/'decisions.json',BASE/'controls/approved.jsonl',BASE/'controls/dash_types.jsonl',*sorted((BASE/'answers/n1t2').glob('*.jsonl')),*sorted((BASE/'answers/n1t2').glob('*.run.json')),*sorted((BASE/'answers/n1t2').glob('*.scan.json')),*sorted((OUT/'keys').glob('*.json'))]})
    dump(BASE/'N1TS_PHASE1.json',summary)
    report_phase1(summary)
    print(json.dumps({k:v for k,v in summary.items() if k not in ('geometry_audit','gates','google_ours','source_hashes')},ensure_ascii=False,indent=2))
    return summary


def report_phase1(s):
    text=['## N1-TS phase 1','', 'Calibration v2 PASS (81/82). No reading run or network use. Two high-confidence VALID votes required; VOID votes are secondary only. Control `unreadable` (u) abstains except on unsure-dash controls, where only a dash type is accepted. No label edits applied.', '',
        '| Context | r1 wrong | u | control gate | usable | r2 wrong | u | control gate | usable |','|---|---:|---:|---|---|---:|---:|---|---|']
    for i in range(1,15):
        c=f'ctx{i:02}';a,b=(s['gates'][f'{c}.{r}'] for r in ('r1','r2'))
        text.append(f'| {c} | {a["wrong"]} | {a["abstentions"]} | {a["control_status"]} | {a["status"]} | {b["wrong"]} | {b["abstentions"]} | {b["control_status"]} | {b["status"]} |')
    text+=['','ctx01.r1 has 0 wrong controls but failed the recorded v4 scan: an absolute-path write to `/tmp/ocr_write_placeholder`. It is INVALID for voting. Its canonical answer copy was recovered from the existing completed pack; see `artifacts/n1/n1t2/answer_recovery.json`. The failed scan was preserved.', '',
        'Both-VOID re-read contexts: '+(', '.join(s['blocked_contexts']) or 'none')+'.', '',
        f'Decisions: {s["decided"]}/{s["slots"]} ({s["read_decided"]} read; {s["geometry_only"]} nothing by geometry); lead_review {s["lead_review"]}. Reasons use exclusive precedence: geometry unavailable, dash mismatch, invalid provenance, VOID, unreadable/other, low confidence; two usable conflicting votes are disagreement.', '',
        '| lead_review reason | slots |','|---|---:|']
    text += [f'| {r} | {n} |' for r,n in sorted(s['reasons'].items())]
    text+=['', 'Decided meanings: '+json.dumps(s['meanings'],ensure_ascii=False)+'.','','Google × ours over ALL decided slots (geometry-only included; dash types are named tags):','','| Google | Ours | slots |','|---|---|---:|']
    text += [f'| {json.dumps(x["google"],ensure_ascii=False)} | {x["ours"]} | {x["count"]} |' for x in s['google_ours']]
    text+=['',f'Geometry-only audit: both raw reads say nothing on {s["audit_agree"]}/30; {s["audit_decided"]}/30 also qualify as decided nothing after gates/confidence. These are evidence about the pruned population, not validation of every geometry-only slot. Full slot-level audit in `artifacts/n1/N1TS_PHASE1.json`.', '',
        f'Lead sheets: {s["raised_cells"]} raised cells; {s["review_cells"]} seeded review cells; {s["sheets"]} sheets. Raised pages carry 8 targets + 4 approved references; review pages have at most 12 targets. Seed `'+SEED+'`. Deferred review counts: '+json.dumps(s['deferred_by_reason'])+'. Every deferred slot/reason is in `sheets_index.json`; the template includes them with an empty sheets list. They still require rulings before phase 2.', '',
        f'Sheets: `{DEST}`. Index: `sheets_index.json`. Lead input: `artifacts/n1/lead_t_template.jsonl` (set truth to a sep2 meaning or `keep Google`; null is pending). A slot appearing in both sets has one ruling. All raised reads are included even from VOID/INVALID contexts.', '',
        'Phase 2 is implemented but NOT RUN. After the lead fills every required ruling and says go, run `n1ts.py --phase 2 --lead-approved`. This revalidates source hashes, complete readings, decisions, controls and both-VOID blocks, applies rulings, builds owner sheet v2 and writes a summary. Dash label outcomes stay tag-only; only exact Google -/. → · in grammar-thousands slots can be edit candidates. Current owner sheet is preserved.']
    path=ROOT/'docs/records/labelfix/secondary/N1T_REPORT.md';old=path.read_text();old=old.split('\n## N1-TS phase 1')[0]
    path.write_text(old.rstrip()+'\n\n'+'\n'.join(text)+'\n')


def phase2(approved=False):
    if not approved:raise ValueError('phase 2 requires lead go and --lead-approved')
    receipt=json.loads((BASE/'N1TS_PHASE1.json').read_text())
    for p,h in receipt['source_hashes'].items():
        if sha(ROOT/p)!=h:raise ValueError('phase 1 source changed: '+p)
    slots,decisions,gates,blocked=combine()
    if gates!=receipt['gates']:raise ValueError('phase 1 gates changed')
    recorded=json.loads((OUT/'decisions.json').read_text())
    if recorded['decisions']!=decisions:raise ValueError('phase 1 decisions changed')
    load_locks(BASE).assert_fit_rows(s['line_id'] for s in slots)
    lead=BASE/'lead_t.jsonl'
    partial=lead.exists()
    if not partial: lead=BASE/'lead_t_template.jsonl'
    if partial and (lead.with_suffix('.jsonl.sha256')).read_text().split()[0]!=sha(lead):
        raise ValueError('lead ruling seal mismatch')
    final=apply_lead(slots,decisions,rows(lead),blocked,partial=partial)
    from greekocr.numerics.owner_v2 import build
    cards,spec=build(rows(OUT/'lines.jsonl'),slots,final)
    legacy_path=OUT/'legacy_note_ids.json'
    if legacy_path.exists():
        legacy=json.loads(legacy_path.read_text())
        for c in cards:
            if c['line_id'] in legacy:
                c['note_data']=dict(line=c['line_id'],**{'legacy-note-ids':json.dumps(legacy[c['line_id']])})
    from n1t_owner_sheet import publish
    summary=publish(cards,spec,BASE/'owner_sheet/n1_sheet.html')
    summary.update(lead_rulings=sum(d['status']=='lead_ruled' for d in final),
        label_edits_applied=0,edit_candidates=sum(d['edit_candidate'] is not None for d in final),
        lead_template_sha256=sha(BASE/'lead_t_template.jsonl'),lead_rulings_sha256=sha(lead),
        unresolved=sum(d['truth_candidate'] is None for d in final),
        boxes=dict(Counter(s['style'] for c in cards for s in c['slots'] if s['evidence'])),
        unlocalized_slots=[s['slot_id'] for c in cards for s in c['slots'] if not s['evidence']],
        sheet_bytes=(_data_input(BASE/'owner_sheet/n1_sheet.html')).stat().st_size)
    dump(OUT/'lead_decisions.json',dict(decisions=final,gates=gates))
    dump(BASE/'N1TS_PHASE2.json',summary)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--phase',choices=['1','2'],default='1');p.add_argument('--lead-approved',action='store_true');a=p.parse_args()
    if a.phase=='1':phase1()
    else:print(json.dumps(phase2(a.lead_approved),ensure_ascii=False,indent=2))
