"""Offline N1-G audit, review sheets and explicitly authorized finalization."""
import argparse
from collections import Counter, defaultdict
import html
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT/'scripts/numerics'), str(ROOT/'scripts/secondary/reading'), str(ROOT/'scripts/secondary')]
from greekocr.numerics.ink_rule import sha, load_rule, decide, CLASSES, DASHES
from greekocr.numerics.combine_v2 import MEANINGS, decode_and_gate
from n1t_packs import rows
from n1_gate import score, truth_from_reads
from n1_render import SCRATCH
BASE = ROOT/'artifacts/n1'
OUT = BASE/'n1e'
DEST = SCRATCH/'n1_review/gate'
RULE = BASE/'n1r/rule.json'


def write(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def jsonl(path, values):
    Path(path).write_text(''.join(json.dumps(v, ensure_ascii=False)+'\n' for v in values))


def item_coverage(scan, rollout, directory, items):
    from ru2t_coverage import coverage
    # Either sealed, target-marked line or sealed target zoom establishes a view.
    # Supply both as origins while preserving the public schema for literal replay.
    aliases = [dict(i, crop=i[k]) for i in items for k in ('line', 'zoom')]
    cov = coverage(scan, rollout, directory, aliases)
    direct = set(cov['direct_crops']); derived = set(cov['derived_crops'])
    kinds = {i['item_id']: 'direct' if {i['line'],i['zoom']} & direct else
             'derived' if {i['line'],i['zoom']} & derived else 'unviewed' for i in items}
    return dict(counts={k:sum(v==k for v in kinds.values()) for k in ('direct','derived','unviewed')},
                items=kinds, image_coverage=cov)


def audit(out=OUT, rulepath=RULE, refresh=False):
    from n1_pack_closure import scan as closure
    from n1t_packs import typed_controls
    import scan_rollout
    if sha(ROOT/'scripts/secondary/reading/scan_rollout.py') != 'dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547':
        raise ValueError('canonical scanner changed')
    rule = load_rule(rulepath)
    if rule['config']['implementation_sha256'] != sha(ROOT/'greekocr/numerics/ink_rule.py'):
        raise ValueError('frozen implementation changed')
    receipt = BASE/'N1R_RECEIPT.json'
    sealed = json.loads(receipt.read_text())
    for p, digest in sealed['outputs'].items():
        actual = sha(p)
        if Path(p) in {ROOT/'scripts/numerics/n1_gate.py', ROOT/'scripts/numerics/n1_apply_train.py'}:
            # Authorized N1-G gate plumbing revisions, with byte-exact N1R predecessors.
            actual = sha(BASE/'n1g/predecessor'/Path(p).name)
        if Path(p) == ROOT/'docs/labelfix/secondary/N1R_REPORT.md':
            original = Path(p).read_text().split('\n## N1-G locked evaluation')[0]
            actual = hashlib.sha256(original.encode()).hexdigest()
        if actual != digest: raise ValueError('N1R sealed output changed: '+p)
    build = json.loads((out/'build.json').read_text())
    if build['rule_hash'] != rule['rule_hash']: raise ValueError('rule mismatch')
    for p, digest in build['inputs'].items():
        if sha(p) != digest: raise ValueError('locked input changed: '+p)
    slots = rows(out/'slots.jsonl'); lines = {r['line_id']:r['text'] for r in rows(out/'lines.jsonl')}
    decisions = rows(out/'rule_decisions.jsonl')
    if decisions != [decide(s,rule,lines[s['line_id']]) for s in slots]: raise ValueError('decision replay differs')
    approved = {c['slot_id']:c['truth'] for c in typed_controls(rows(BASE/'controls/approved.jsonl'),rows(BASE/'controls/dash_types.jsonl'))}
    reads = defaultdict(list); contexts = {}; evidence = {}
    for kp in sorted((out/'keys').glob('ctx*.json')):
        key = json.loads(kp.read_text()); reader = next(iter(key['readers'])); ctx = kp.name.split('.')[0]
        name = ctx+'.'+reader; rd = Path(build['pack_root'])/ctx/reader
        check = closure(rd,out,completed=True,meanings=MEANINGS)
        if not check['ok']: raise ValueError('pack custody: '+str(check['violations']))
        for item in key['items'].values():
            if item['control_truth'] is not None and approved[item['slot_id']] != item['control_truth']:
                raise ValueError('unapproved control')
        stem = BASE/'answers'/out.name/name
        ap = Path(str(stem)+'.jsonl'); sp = Path(str(stem)+'.scan.json'); rp = Path(str(stem)+'.run.json')
        run = json.loads(rp.read_text()); oldscan = json.loads(sp.read_text()); rollout = Path(run['rollout'])
        if rows(ap) != rows(rd/'answers.jsonl'): raise ValueError('answer custody differs')
        # Keep original launcher scans intact; new scans have a separate N1-G namespace.
        target = out/'gate_scans'/(name+'.json')
        if refresh:
            scan = scan_rollout.inspect(rollout,rd); write(target,scan)
        else:
            scan = json.loads(target.read_text())
        if scan.get('scanner_version') != 'v4.4-canonical' or scan.get('rollout_sha256') != sha(rollout):
            raise ValueError('canonical scan/rollout custody')
        if oldscan.get('scanner_version') != 'v4.4-canonical': raise ValueError('launcher scan version')
        cov = item_coverage(scan,rollout,rd,rows(rd/'items.jsonl'))
        gate, decoded = decode_and_gate(key,rows(ap))
        gate['control_status'] = gate['status']
        provenance = scan['ok'] and run['rc']==0 and run['model']=='gpt-6.1-sol'
        if not provenance: gate['status']='VOID'
        # Coverage loss is item-local, including controls, never context-wide.
        # An unseen control cannot supply a correct control answer.
        unseen_controls = [d for d in decoded if d['control'] and cov['items'][d['item_id']]=='unviewed']
        gate['unviewed_controls'] = len(unseen_controls)
        gate.update(scan_ok=scan['ok'],coverage=cov,scan_sha256=sha(target),pack_manifest_sha256=check['manifest_sha256'])
        contexts[name]=gate
        for d in decoded:
            if not d['control']:
                reads[d['slot_id']].append(dict(reader=reader,context=ctx,item_id=d['item_id'],meaning=d['meaning'],
                    confidence=d['confidence'],context_status=gate['status'],
                    read_status='unviewed' if cov['items'][d['item_id']]=='unviewed' else 'ok'))
        for p in (kp,ap,sp,rp,target,rollout): evidence[str(p)]=sha(p)
        print(name,gate['status'],gate['wrong'],cov['counts'],flush=True)
    selected = rows(out/'read_set.jsonl')
    if set(reads)!={s['slot_id'] for s in selected}: raise ValueError('read population differs')
    for votes in reads.values():
        if len(votes)!=2 or {v['reader'] for v in votes}!={'r1','r2'}: raise ValueError('incomplete reads')
    return dict(rule=rule,decisions=decisions,slots=selected,reads=dict(reads),contexts=contexts,evidence=evidence,
                prepared_receipt_sha256=sha(receipt))


def assemble(data, lead=(), final=False):
    excluded = sorted(s['slot_id'] for s in data['slots'] if s.get('render_scope')=='whole_line_unlocalized')
    ids = [s['slot_id'] for s in data['slots'] if s['slot_id'] not in excluded]
    eligible_lead = [r for r in lead if r['slot_id'] not in excluded]
    g = score(data['decisions'],ids,{s:data['reads'][s] for s in ids},eligible_lead)
    truth, unresolved = truth_from_reads(ids,data['reads'],eligible_lead)
    byid={d['slot_id']:d for d in data['decisions']}
    candidates=[]
    for s in data['slots']:
        sid=s['slot_id']; t=truth.get(sid)
        candidates.append(dict(slot_id=sid,truth_candidate=t,status='excluded_unlocalized' if sid in excluded else
                               'truth_candidate' if t else 'lead_review',reads=data['reads'][sid],
                               google_glyph=s['google_glyph'],rule_class=byid[sid]['class']))
    review = review_ids(candidates)
    g.update(phase='FINAL' if final else 'PROVISIONAL',excluded_unlocalized=excluded,
             excluded_unlocalized_count=len(excluded),lead_required_ids=sorted(review),
             false_positive_ids=sorted(s for s,t in truth.items() if byid[s]['class']=='raised dot' and t!='raised dot'),
             gate_scope='n1_locked_eval_alt; unlocalized slots excluded',contexts=data['contexts'],
             evidence=data['evidence'],prepared_receipt_sha256=data['prepared_receipt_sha256'])
    if not final: g['passed']=False
    return g,candidates


def review_ids(candidates):
    return {c['slot_id'] for c in candidates if c['rule_class']=='raised dot' or c['truth_candidate']=='raised dot' or
            (c['status'] in ('lead_review','excluded_unlocalized') and c['google_glyph'] in ('-','.'))}


def validate_lead(template, lead):
    expected={r['slot_id'] for r in template}
    if len(lead)!=len(expected) or {r['slot_id'] for r in lead}!=expected:
        raise ValueError('exact complete lead template required')
    if any(r.get('truth') not in (*CLASSES,'any dash','hold') for r in lead):
        raise ValueError('blank/invalid lead truth')


def final_gate(data, template, lead):
    _, initial_candidates = assemble(data)
    if {r['slot_id'] for r in template} != review_ids(initial_candidates):
        raise ValueError('lead template does not cover the required review union')
    validate_lead(template,lead)
    g,_ = assemble(data,lead,final=True)
    # Only explicitly requested review cells require lead closure. Remaining
    # unresolved, non-editing slots remain outside truth and are reported.
    required=({r['slot_id'] for r in template} | {d['slot_id'] for d in data['decisions'] if d['class']=='raised dot'}) - set(g['excluded_unlocalized'])
    noncritical=set(g['unresolved'])-required
    g['unadjudicated_noncritical_ids']=sorted(noncritical)
    g['unresolved']=sorted(set(g['unresolved']) & required)
    g['passed']=bool(not g['unresolved'] and g['raised_predicted']>0 and g['raised_truth']>0 and
                     g['raised_precision']>=.99 and g['false_range_edits']==0)
    g['failing_slots']=sorted(set(g['false_positive_ids'])|set(g['false_range_edit_ids'])|set(g['unresolved']))
    return g


def reference_pair():
    truth=rows(BASE/'n1r/truth.jsonl')
    # Existing high-confidence development truth; neither reference is locked truth.
    doc='elstat:GRESYE_01_0001_00046'
    pair=[next(r for r in truth if r['document']==doc and r['truth']==t) for t in ('raised dot','baseline dot')]
    for r in pair:
        for k in ('line','zoom'):
            if sha(r[k]) != r[k+'_sha256']: raise ValueError('reference pixels changed')
    return pair


def sheets(data,candidates,dest=DEST):
    from PIL import Image,ImageDraw
    from n1_raised_sheets import font,paste_fit
    import textwrap
    dest.mkdir(parents=True,exist_ok=True)
    selected=review_ids(candidates); sm={s['slot_id']:s for s in data['slots']}; cm={c['slot_id']:c for c in candidates}
    ordered=sorted(selected,key=lambda sid:(sm[sid]['document'],sid)); refs=reference_pair(); index=[]; template=[]
    for offset in range(0,len(ordered),10):
        chunk=ordered[offset:offset+10]; num=offset//10+1
        canvas=Image.new('RGB',(2400,3900),'white'); draw=ImageDraw.Draw(canvas)
        draw.text((30,15),f'N1-G lead review {num} / {len(chunk)} targets + 2 references',font=font(34,True),fill='black')
        draw.text((30,65),'References share one development document; target documents are named per cell.',font=font(25),fill='black')
        for j,r in enumerate(refs):
            x=30+1180*j
            draw.text((x,110),'REFERENCE: '+r['truth']+' / '+r['document'],font=font(23,True),fill='black')
            paste_fit(canvas,r['zoom'],(x,150,x+1140,370));paste_fit(canvas,r['line'],(x,380,x+1140,450))
        cells=[]
        for j,sid in enumerate(chunk):
            s=sm[sid]; c=cm[sid]; n=offset+j+1; x=30+(j%2)*1180;y=490+(j//2)*675
            for k in ('line','zoom'):
                if sha(s[k])!=s[k+'_sha256']:raise ValueError('target pixels changed')
            draw.rectangle((x,y,x+1140,y+650),outline='gray',width=2)
            lines=[f'Cell {n} / Google {json.dumps(s["google_glyph"])} / RULE {c["rule_class"]}',sid,s['document'],
                   'Candidate: '+str(c['truth_candidate'])+' / '+c['status']]
            for k,line in enumerate(lines):draw.text((x+10,y+10+30*k),line,font=font(22,k==0),fill='black')
            paste_fit(canvas,s['zoom'],(x+10,y+145,x+1130,y+385));paste_fit(canvas,s['line'],(x+10,y+400,x+1130,y+480))
            for k,v in enumerate(c['reads']):
                draw.text((x+10,y+490+30*k),f'{v["context"]}.{v["reader"]} {v["context_status"]}: {v["meaning"]} / {v["confidence"]} / {v["read_status"]}',font=font(22),fill='black')
            if c['status']=='excluded_unlocalized':draw.text((x+10,y+555),'UNLOCALIZED: whole line; excluded from gate',font=font(23,True),fill='red')
            draw.text((x+10,y+605),'Lead truth: ____________________',font=font(25),fill='black')
            cell=dict(cell_number=n,slot_id=sid,sheet=f'gate_{num:02}.png',bbox=[x,y,x+1140,y+650],
                      excluded_unlocalized=c['status']=='excluded_unlocalized',truth=None)
            template.append(cell);cells.append(cell)
        path=dest/f'gate_{num:02}.png';canvas.save(path)
        index.append(dict(file=path.name,sha256=sha(path),target_cells=len(chunk),total_cells=len(chunk)+2,
                          references=[{k:r[k] for k in ('slot_id','truth','document','line_sha256','zoom_sha256','truth_source')} for r in refs],cells=cells))
    # Never overwrite a lead's work on a rebuild.
    tp=dest/'gate_lead_template.jsonl'
    if not tp.exists():jsonl(tp,template)
    elif [{k:r[k] for k in ('cell_number','slot_id','sheet')} for r in rows(tp)] != [{k:r[k] for k in ('cell_number','slot_id','sheet')} for r in template]:
        raise ValueError('existing template has different population')
    write(dest/'sheets_index.json',dict(target_cells=len(template),sheets=index,max_total_cells=12,
        reference_document=refs[0]['document'],reference_source_sha256=sha(BASE/'n1r/truth.jsonl')))
    links=''.join(f'<p><a href="{r["file"]}">{r["file"]}</a> ({r["target_cells"]} targets)</p>' for r in index)
    (dest/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>N1-G lead review</title><h1>N1-G lead review</h1><p>Fill truth in gate_lead_template.jsonl; preserve slot IDs. Unlocalized cells remain excluded. Allowed: '+html.escape(', '.join((*CLASSES,'any dash','hold')))+'.</p>'+links)
    return template,index


def phase1(refresh=False):
    data=audit(refresh=refresh);g,candidates=assemble(data)
    template,index=sheets(data,candidates)
    for name,values in [('gate_candidates.jsonl',candidates),('gate_unlocalized.jsonl',[s for s in data['slots'] if s.get('render_scope')=='whole_line_unlocalized'])]:jsonl(OUT/name,values)
    write(OUT/'gate_provisional.json',g)
    void=[k for k,v in data['contexts'].items() if v['status']=='VOID']
    valid={r:sum(v['status']=='VALID' for k,v in data['contexts'].items() if k.endswith('.'+r)) for r in ('r1','r2')}
    counts=Counter(c['status'] for c in candidates);raised=sum(d['class']=='raised dot' for d in data['decisions'])
    precision='undefined' if g['raised_precision'] is None else f'{g["raised_precision"]:.2%}'
    last=f'N1G PHASE1 READY: contexts VALID r1 {valid["r1"]}/10 r2 {valid["r2"]}/10; truth slots {counts["truth_candidate"]}, lead_review {counts["lead_review"]}; rule-raised {raised}; provisional precision {precision} ({g["raised_tp"]}/{g["raised_predicted"]}), range false edits {g["false_range_edits"]}; lead cells {len(template)} on {len(index)} sheets'
    receipt=dict(schema='n1g-receipt-v1',phase='PHASE1 READY',rule_hash=data['rule']['rule_hash'],contexts_valid=valid,
        void_contexts=void,counts=dict(counts),rule_raised=raised,provisional_gate=g,
        lead_cells=len(template),lead_sheets=len(index),lead_template=str(DEST/'gate_lead_template.jsonl'),
        lead_template_sha256=sha(DEST/'gate_lead_template.jsonl'),sheets_index_sha256=sha(DEST/'sheets_index.json'),
        evidence=data['evidence'],phase2_executed=False,training_written=False,lqb_registered=False,
        implementation_hashes={str(p):sha(p) for p in (ROOT/'scripts/numerics/n1g.py',ROOT/'scripts/numerics/n1_gate.py',ROOT/'scripts/numerics/n1_apply_train.py',ROOT/'scripts/secondary/ru2t_coverage.py',ROOT/'tests/test_n1g.py',BASE/'n1g/predecessor/n1_gate.py',BASE/'n1g/predecessor/n1_apply_train.py')},
        last_line=last,restrictions=dict(network='OFF',new_readings=False,browser=False,computer_use=False,git_writes=False))
    import xml.etree.ElementTree as ET
    testpath=BASE/'N1G_TESTS.xml'
    if testpath.exists():
        cases=ET.parse(testpath).findall('.//testcase')
        receipt['tests']=dict(path=str(testpath),sha256=sha(testpath),
            passed=sum(not c.findall('failure') and not c.findall('error') for c in cases),
            failed=sum(bool(c.findall('failure') or c.findall('error')) for c in cases))
    receipt['artifacts']={str(p):sha(p) for p in (OUT/'gate_candidates.jsonl',OUT/'gate_unlocalized.jsonl',OUT/'gate_provisional.json')}
    write(BASE/'N1G_RECEIPT.json',receipt)
    report=ROOT/'docs/labelfix/secondary/N1R_REPORT.md'
    text=report.read_text().split('\n## N1-G locked evaluation')[0]
    text+='\n## N1-G locked evaluation — Phase 1\n\n'
    text+=f'**PROVISIONAL; no release authorization.** Frozen rule `{data["rule"]["rule_hash"]}` replayed exactly. All 20 canonical v4.4 scans and sealed pack closures pass. VOID contexts: {", ".join(void)}. Control threshold is >1 wrong; approved unsure dash controls accept any dash type. All context/item coverage details are in `artifacts/n1/n1e/gate_provisional.json`; coverage accepts direct views or literal-command traced derivatives and drops only unviewed item votes.\n\n'
    text+=f'Two valid high-confidence agreeing reads establish {counts["truth_candidate"]} truth candidates; {counts["lead_review"]} localized slots need lead review. The 36 unlocalized slots are listed in `artifacts/n1/n1e/gate_unlocalized.jsonl` and excluded throughout, including after lead rulings. Truth candidates do not need agreement with the rule or dash geometry.\n\n'
    text+=f'Provisional precision: {precision} ({g["raised_tp"]}/{g["raised_predicted"]}); true-range false edits: {g["false_range_edits"]}; recall: {g["raised_recall"]} ({g["raised_tp"]}/{g["raised_truth"]}); selected-truth unsure rate: {g["unsure_rate"]}; all-enumerated unsure rate: {g["all_slot_unsure_rate"]}. Recall describes adjudicated selected slots, not population recall. False-positive IDs and the full confusion matrix are in the provisional JSON.\n\n'
    text+=f'Lead review: {len(template)} target cells on {len(index)} sheets (at most 10 targets + 2 references). Sheets and `gate_lead_template.jsonl`: `{DEST}`. Raised and baseline references at the top of every sheet share development document `elstat:GRESYE_01_0001_00046`; target documents are separately identified. References are previously established development truth, not new readings. The template truth fields are blank.\n\n'
    text+='The frozen classifier and rule are unchanged. The two N1R-sealed gate/applier support scripts were revised for N1-G; byte-exact predecessors, verified against the original N1R receipt hashes, are retained in `artifacts/n1/n1g/predecessor/`. The original report prefix is likewise verified against its N1R seal before this section is updated. Current gate code is bound by the N1-G receipt.\n\n'
    text+='Phase 2 is implemented in `scripts/numerics/n1g.py phase2 --lead PATH --lead-go`; invoke only after the lead fills every template row and explicitly says go. It revalidates preparation, scans, answer custody and coverage, applies lead overrides, excludes unlocalized cells, and requires every requested localized review cell to resolve. Other non-editing unresolved slots are reported and excluded from metrics. A non-vacuous ≥99% precision and zero range edits are required. Failure writes failing slot IDs and stops before training or LQB writes. Success invokes `n1_apply_train.py`, writes the overlay/manifest/detached SHA, registers it, then re-scores using the LQB scorer. Per N1-G, the independently adjudicated locked gate is now the publication criterion; it supersedes the earlier undefined held-out-development precision prerequisite. The original development results remain unchanged and are not used to tune this rule. No Phase 2 action has run.\n\n'
    if 'tests' in receipt:
        text+=f'Validation: **{receipt["tests"]["passed"]} passed, {receipt["tests"]["failed"]} failed** in `artifacts/n1/N1G_TESTS.xml`. Tests exercise control thresholds, any-dash controls, direct/derived/unviewed coverage, VOID/single/disagreement exclusion, permanent unlocalized exclusion, exact lead coverage, lead overrides and holds, pass/fail publication branches, real-pixel fixture application, manifest/registry custody, and sheet selection/reference bounds. Phase 2 publication tests use temporary fixtures and mocked dispatch; no real train overlay or registry write occurred.\n'
    report.write_text(text)
    receipt['report_sha256']=sha(report)
    write(BASE/'N1G_RECEIPT.json',receipt)
    print(last)
    return receipt


def phase2(leadpath,go=False):
    if not go:raise ValueError('lead go is required before phase 2')
    receipt=json.loads((BASE/'N1G_RECEIPT.json').read_text())
    for p,digest in receipt.get('implementation_hashes',{}).items():
        if sha(p)!=digest:raise ValueError('gate implementation changed: '+p)
    data=audit();lead=rows(leadpath)
    if data['evidence'] != receipt['evidence']:raise ValueError('Phase 1 evidence changed')
    # The sealed sheet index binds the original required population even when the template is filled in place.
    ip=DEST/'sheets_index.json'
    if sha(ip)!=receipt['sheets_index_sha256']:raise ValueError('review sheets index changed')
    ix=json.loads(ip.read_text());sealed=[c for sh in ix['sheets'] for c in sh['cells']]
    for sh in ix['sheets']:
        if sha(DEST/sh['file'])!=sh['sha256']:raise ValueError('review sheet changed')
    g=final_gate(data,sealed,lead);g['lead_sha256']=sha(leadpath)
    write(OUT/'gate_final.json',g)
    receipt.update(phase='FINAL PASS' if g['passed'] else 'FINAL FAIL',phase2_executed=True,final_gate=g)
    write(BASE/'N1G_RECEIPT.json',receipt)
    report=ROOT/'docs/labelfix/secondary/N1R_REPORT.md'
    with report.open('a') as f:f.write('\n### N1-G final gate\n\n'+receipt['phase']+'; failing slots: '+json.dumps(g['failing_slots'])+'\n')
    if not g['passed']:return g
    # This subprocess repeats all real custody/gate checks before touching training.
    try:
        subprocess.run([sys.executable,'-B',str(ROOT/'scripts/numerics/n1_apply_train.py'),'--lead',str(leadpath),'--lead-go'],check=True)
    except subprocess.CalledProcessError as exc:
        receipt.update(training_application_status='FAILED',training_application_returncode=exc.returncode)
        write(BASE/'N1G_RECEIPT.json',receipt)
        with report.open('a') as f:f.write('\nTraining application stopped with return code '+str(exc.returncode)+'; see command stderr.\n')
        raise
    output=BASE/'n1_v1_train.jsonl'
    output.with_suffix('.jsonl.sha256').write_text(sha(output)+'  '+output.name+'\n')
    from greekocr.labelfix.lqb import run
    registry=json.loads((ROOT/'docs/labelfix/lqb/versions.json').read_text())
    truth=ROOT/'docs/labelfix/lqb/truth_v1_1.jsonl'
    result=run(truth,registry,['google_raw','collection_v2_train','n1_v1_train'])
    write(BASE/'n1_v1_train_lqb_score.json',result)
    receipt.update(training_written=True,lqb_registered=True,train_sha256=sha(output),lqb_score_sha256=sha(BASE/'n1_v1_train_lqb_score.json'))
    write(BASE/'N1G_RECEIPT.json',receipt)
    return g


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('phase',choices=['phase1','phase2']);p.add_argument('--refresh-scans',action='store_true');p.add_argument('--lead',type=Path);p.add_argument('--lead-go',action='store_true');a=p.parse_args()
    if a.phase=='phase1':phase1(a.refresh_scans)
    else:
        if not a.lead:p.error('--lead required')
        result=phase2(a.lead,a.lead_go)
        return 0 if result['passed'] else 2
    return 0
if __name__=='__main__':sys.exit(main())
