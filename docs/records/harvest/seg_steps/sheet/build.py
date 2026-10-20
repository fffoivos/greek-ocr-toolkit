"""Offline owner sheet from immutable saved SEG results. No tool/reader imports.
Run: ../greek-ocr-toolkit-sol-recut/.venv/bin/python -B docs/harvest/seg_steps/sheet/build.py
"""
from __future__ import annotations
import base64, bisect, collections, datetime, hashlib, json, math, re, subprocess, sys
from pathlib import Path
from zoneinfo import ZoneInfo
sys.dont_write_bytecode = True
from PIL import Image
from vendor import owner_sheet

HERE = Path(__file__).resolve().parent
D = HERE.parent
ROOT = HERE.parents[3]
REVIEW = ROOT.parent / 'greek-ocr-toolkit-review'
BASE = ROOT.parent / 'greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1'
INPUTS = {}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
    p = Path(p); INPUTS[str(p)] = sha(p)
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def save(p, obj): p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
def stamp(m):
    t = m.get('updated', '')
    if not t: return 0
    dt = datetime.datetime.fromisoformat(t.replace('Z', '+00:00'))
    return (dt if dt.tzinfo else dt.replace(tzinfo=ZoneInfo('Europe/Athens'))).timestamp()
def fmt(x): return 'unavailable in saved verdict' if x is None else f'{x:.3f}'

def inv(frame):
    (a,b,c),(d,e,f),_ = frame['source_to_measurement']; det = a*e-b*d
    assert det
    return [[e/det,-b/det,(b*f-c*e)/det],[-d/det,a/det,(c*d-a*f)/det]]
def pt(M,x,y): return M[0][0]*x+M[0][1]*y+M[0][2], M[1][0]*x+M[1][1]*y+M[1][2]
def poly(M, points, cls, closed=False):
    return '<' + ('polygon' if closed else 'polyline') + f' class="{cls}" points="' + ' '.join('%.3f,%.3f'%pt(M,*p) for p in points) + '"/>'
def box(M,b,cls):
    x,y,X,Y = b
    return poly(M,[[x,y],[X,y],[X,Y],[x,Y]],cls,True)

def unrolled_outline(rf, base):
    """Display inverse of saved (s,n), following the saved sampled base polyline.
    No detector, fit or pixel measurement. Sampling is recorded in the receipt.
    """
    lengths = [0.]
    for a,b in zip(base,base[1:]): lengths.append(lengths[-1]+math.dist(a,b))
    def at(s,n):
        i = min(len(base)-2,max(0,bisect.bisect_right(lengths,s)-1))
        a,b = base[i:i+2]; length = lengths[i+1]-lengths[i]
        t=(s-lengths[i])/length; dx=(b[0]-a[0])/length; dy=(b[1]-a[1])/length
        return [a[0]+t*(b[0]-a[0])-n*dy,a[1]+t*(b[1]-a[1])+n*dx]
    s0,n0,s1,n1 = rf['sn_box']
    ticks = [s0]+[s for s in lengths if s0<s<s1]+[s1]
    return [at(s,n0) for s in ticks]+[at(s,n1) for s in reversed(ticks)]

def overlay(z,w,h,record):
    e=z['evidence']; M=inv(z['frame']); out=[]; main=None; kind='unavailable'
    for d in e.get('detected_rows',[]):
        if d['votes']<=0: continue
        c=d['curves']
        if d['side']=='main':
            main=c['base'];out.extend([poly(M,c['ascender'],'asc'),poly(M,c['base'],'base')])
        else:
            out.extend([poly(M,c['ascender'],'nasc'),poly(M,c['base'],'nbase')])
    for line in e['lines']:
        if line['side']!='main':
            for word in line['word_groups']: out.append(box(M,word['bbox'],'wwhole' if word['whole'] else 'wpart'))
    cut=e['gate'].get('main_cut') or {}
    for s in cut.get('cut_spans',[]):
        y=.5 if s['edge']=='top' else z['frame']['height']-.5
        out.append(poly(M,[[s['x0'],y],[s['x1'],y]],'cutspan' if s['min_visible']<.6 else 'cutspan2'))
    for c in cut.get('crossings',[]):
        if 'leaves' in c.get('meaning',''):
            x,y=pt(M,c['x'],.5 if c['edge']=='top' else z['frame']['height']-.5)
            out.append(f'<circle class="cross" cx="{x:.3f}" cy="{y:.3f}" r="5"/>')
    bx=e.get('box_evidence') or {}; rf=bx.get('row_frame') or {}
    if bx.get('bbox'): out.append(box(M,bx['bbox'],'tbox'))
    if rf.get('corners'):
        out.append(poly(M,rf['corners'],'rframe',True))
        kind='all-ink box' if rf.get('coordinates')=='processed_crop_all_components' else 'de-skewed box'
    elif rf.get('sn_box'):
        assert main and len(main)>1
        out.append(poly(M,unrolled_outline(rf,main),'rframe',True));kind='unrolled box (display outline from saved sampled base)'
    if kind=='unavailable' and record.get('small') and (record.get('geometry') or {}).get('all_box'):
        out.append(box(M,record['geometry']['all_box'],'rframe'))
        kind='all-ink box (saved diagnostic component bounds; verdict has no Stage-B box)'
    return f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none">'+''.join(out)+'</svg>',kind

def measurements(z):
    e=z['evidence'];b=e.get('box_evidence') or {};f=b.get('row_frame') or {};g=e['gate'];p=b.get('prediction') or {}
    a,h=f.get('length'),f.get('height'); small=f.get('coordinates')=='processed_crop_all_components'
    # S4 small passes width/height unchanged; normal rows use long/short.
    long,short=(a,h) if a is None or h is None else (max(a,h),min(a,h))
    expected=p.get('expected');ratio=(e['characters']+1)/(expected+1) if expected is not None and expected!=-1 else None
    pad=(e.get('padding_evidence') or {}).get('total_padding_line_heights')
    return (z['reason']+f' | box long side {fmt(long)} px / short side {fmt(short)} px'+
            (f' (saved predictor inputs: width {fmt(a)} / height {fmt(h)})' if small else '')+
            f' | OCR chars {e["characters"]}; expected {fmt(expected)}; ratio (chars+1)/(expected+1) {fmt(ratio)}'+
            f' | padding {fmt(pad)} box heights | gate {g["verdict"]}: {g["reason"]}; '+
            f'whole neighbour words {g["whole_words"]}, cut-off words {g["cutoff_words"]}, complete other rows {len(g["complete_rows"])}')
def inventory(e):
    bits=[]
    for l in e['lines']:
        tag='complete' if l['complete'] else f'{l["visible"]:.0%} visible'
        bits.append(f'{l["side"].upper()}: {l["bodies"]} letter bodies, {tag}, '+
                    (f'covers {l["coverage"]:.0%}' if l['side']=='main' else f'{l["whole_words"]} whole / {l["cutoff_words"]} cut-off words'))
    return ' | '.join(bits) or 'No rows detected'

STEP_NAMES={'s1':'s1 whole word','s2':'s2 turn','s3':'s3 curve','s4':'s4 small all-ink','s1–s3 unresolved':'s1–s3: combined change saved; individual flip attribution unavailable'}

def main():
    vendor={}
    for name in ('owner_sheet.py','owner_sheet.css','owner_sheet.js'):
        source=REVIEW/'greekocr/adjudicate'/name
        assert sha(source)==sha(HERE/'vendor'/name)
        vendor[name]=sha(source)
    main_rows=read(D/'s4/replay.jsonl');typo=read(D/'s4/typology_replay.jsonl')
    assert collections.Counter(r['cohort'] for r in main_rows)=={'segeval1':150,'calibration':888,'cells':250}
    assert sum(not r['manifest']['control'] for r in typo)==417
    pool={};candidates=collections.defaultdict(list);flips=collections.defaultdict(set)
    for i in range(1,5):
        for r in read(D/f's{i}/flips.jsonl'): flips[r['line_id']].add(f's{i}')
    for r in read(D/'s4/typology_flips.jsonl'):flips[r['line_id']].add('s4')
    for r in main_rows:
        lid=r['line_id'];old=r['baseline_08'];new=r['after']
        if lid in pool:
            assert pool[lid]['old']['verdict']==old['verdict'] and pool[lid]['new']['verdict']==new['verdict']
            assert pool[lid]['new']['binding']['crop_sha256']==new['binding']['crop_sha256']
            assert pool[lid]['new']['evidence']==new['evidence']
            pool[lid]['cohorts'].add(r['cohort'])
        else:pool[lid]=dict(old=old,new=new,record=r,cohorts={r['cohort']})
        rating=r.get('owner_rating') or {}
        if rating.get('decision') in ('KEEP','DROP'):
            candidates[lid].append(dict(owner_mark=rating['decision'],source='888 rating',sheet='888 rating',explicit=False,updated=rating.get('updated','')))
    for r in typo:
        if r['manifest']['control']: continue
        lid=r['line_id']
        if lid in pool:
            assert pool[lid]['new']['verdict']==r['versions']['s4']['verdict']
            assert pool[lid]['new']['binding']['crop_sha256']==r['versions']['s4']['binding']['crop_sha256']
            pool[lid]['cohorts'].add('typology')
        else:pool[lid]=dict(old=r['versions']['08'],new=r['versions']['s4'],record=r,cohorts={'typology'})
        if r['versions']['08']['verdict']!=r['versions']['s3']['verdict'] and lid not in {x['line_id'] for x in main_rows}:
            flips[lid].add('s1–s3 unresolved')
    for source,path in [('owner_marks_20261019',BASE/'owner_marks_20261019.jsonl'),('typology',BASE/'small_segments/owner_marks_smallseg.jsonl')]:
        entries=read(path)
        snapshot=read(D/('s4/owner_marks_snapshot.jsonl' if source=='owner_marks_20261019' else 's4/typology_owner_marks_snapshot.jsonl'))
        assert entries==snapshot, f'owner marks drift: {source}'
        for m in entries: candidates[m['line_id']].append(dict(m,source=source,explicit=True))
    judgments={lid:max(enumerate(ms),key=lambda it:(it[1]['explicit'],stamp(it[1]),it[0]))[1] for lid,ms in candidates.items()}
    changed={lid for lid,p in pool.items() if p['old']['verdict']!=p['new']['verdict']}
    proposals=collections.defaultdict(list)
    for r in read(D/'s5/changed_lines.jsonl') if (D/'s5/changed_lines.jsonl').exists() else []:proposals[r['line_id']].append(r)
    assert set(proposals)<=pool.keys()
    selected=changed|set(proposals);cards=[];manifest=[];counts=collections.Counter();missing_steps=[];crop_checks=[]
    for lid in selected:
        p=pool[lid];r=p['record'];old,new=p['old'],p['new'];j=judgments.get(lid)
        group='unjudged' if not j else ('newly_agree' if new['verdict']==j['owner_mark'] else 'disagree')
        if lid in changed:counts[group]+=1
        section='proposal' if lid in proposals else 'changed'
        steps=sorted(flips[lid]);unresolved='s1–s3 unresolved' in steps
        if unresolved: missing_steps.append(lid)
        if lid in changed:assert steps,lid
        crop=Path(r['row']['crop_path']);expected=r['row']['crop_sha256']
        assert sha(crop)==expected==old['binding']['crop_sha256']==new['binding']['crop_sha256'],lid
        with Image.open(crop) as im:w,h=im.size
        crop_checks.append(dict(line_id=lid,path=str(crop),sha256=expected))
        svg,box_kind=overlay(new,w,h,r)
        owner_text='No saved owner judgement' if not j else f'{j["owner_mark"]} ({j.get("sheet",j["source"])}, {j.get("updated") or "time not recorded"}; source: {j["source"]})'+(' | '+j['note'] if j.get('note') else '')
        rows=[dict(name='Google',text=r['row']['raw_text']),dict(name='Lines found',text=inventory(new['evidence'])),
              dict(name='Owner mark (sheet, time)',text=owner_text),
              dict(name='Changed by',text='; '.join(STEP_NAMES[s] for s in steps) or 'No verdict change in s1–s4'),
              dict(name='Final text box',text=box_kind)]
        if lid in proposals:
            rows.append(dict(name='Proposed band (not adopted)',text=' | '.join(f'{x["scheme"]} band {x["band"]}: current {x["current"]} → proposed {x["proposed"]}; ratio {x["r"]:.3f}; padding {x["padding"]:.3f}' for x in proposals[lid])))
        ans=r.get('reader_answer')
        rows.append(dict(name='Text vs crop',text=json.dumps(ans,ensure_ascii=False) if ans else 'No saved reader answer for this line; no new reading.'))
        rows.append(dict(name='Owner standard',text=('Saved owner mark: '+j['owner_mark'] if j else 'No saved owner judgement')+(' | saved reader state: '+str(r.get('owner_standard_state')) if r.get('owner_standard_state') else '')))
        version_rows=[dict(name='0.8',verdict=old['verdict'],text=measurements(old)),dict(name='0.9-s4',verdict=new['verdict'],text=measurements(new))]
        source=r['row'].get('source') or lid.split('--')[0]
        # Passing a data URI preserves the exact crop file bytes; the renderer otherwise re-encodes PNGs.
        uri='data:image/png;base64,'+base64.b64encode(crop.read_bytes()).decode()
        cards.append(dict(line_id=lid,image=uri,group=section+'_'+group,rows=rows,versions=version_rows,tool_verdict=new['verdict'],overlay_svg=svg,
                          tags=[dict(text=c) for c in sorted(p['cohorts'])]+[dict(text=source),dict(text=old['verdict']+' → '+new['verdict']),dict(text=f'{w}×{h} px')],
                          data={'crop-sha256':expected},_sort=(steps[0] if steps else 's5',source,lid)))
        manifest.append(dict(line_id=lid,group=group,section=section,cohorts=sorted(p['cohorts']),steps=steps,verdicts={'0.8':old['verdict'],'0.9-s4':new['verdict']},
                             owner_mark_source=j,owner_mark_candidates=candidates.get(lid,[]),changed_08_s4=lid in changed,proposed_band=proposals.get(lid,[]),crop_path=str(crop),crop_sha256=expected,box_overlay=box_kind))
    group_rank={f'{section}_{g}':i for i,(section,g) in enumerate((s,g) for s in ('changed','proposal') for g in ('disagree','newly_agree','unjudged'))}
    cards.sort(key=lambda c:(group_rank[c['group']],c['_sort'])); by_id={m['line_id']:m for m in manifest};manifest=[by_id[c['line_id']] for c in cards]
    report=D/'s4/REPORT.md';INPUTS[str(report)]=sha(report);text=report.read_text()
    scores=text[text.index('| Metric |'):text.index('\n\n| Set |')]
    # Typology intermediate s1/s2 measurements were never saved: do not invent scores.
    scores+='\n| Typology agreement /185 | 131 | not saved | not saved | 147 | 160 |'
    two=text[text.index('| Type |',text.index('### without_owner fit cells')):text.index('\n\n### all fit cells')]
    intro=('Every line whose verdict changed between 0.8 and the new tool (0.9-s4), in the 150, 888 and 250 sets and the 417 small crops. 279 cards. The last section shows the lines the proposed length band would change (not adopted).\n'
           'The five changes: (1) a neighbour word counts only if every letter is ≥95% visible; (2) crops taller than wide are turned 90° right; (3) curved lines are measured along their curve; (4) small crops (≤8 Google characters, at most 6× longer than tall) are measured from all their ink; (5) proposed length band 0.30–2.00 instead of 0.5–1.5, not adopted.\n'
           'Agreement with your judgements, 0.8 → new tool: your 235 marks 155 → 189; your 135 ratings 94 → 109; your 185 small-crop marks 131 → 160. On the 150: wrongly dropped 18 → 16, wrongly kept 14 → 15, undecided 11 → 0.\n'
           'Small crops, numeric only or all? Box from all ink helps both: numbers 111 → 127 of 144, letters 120 → 137 of 157. A separate expected length for numbers adds 5 more on numbers only (132). Mixed: 3 crops, indicative only.\n'
           'Your earlier mark on each line is shown as text ("Owner mark"); this sheet starts unmarked and never saves on load.\n'
           'Outer border = your mark (green KEEP, red DROP). Inner frame = new tool (green KEEP, red DROP, amber UNCERTAIN).\n'
           'Overlays (b): green = main line; orange dashed = other rows; red box = whole neighbour word; grey dashed = cut-off word; magenta = the box the tool measured.\n'
           'Keys: ↑ ↓ move · SPACE marks KEEP/DROP · b boxes · z zoom · Esc leaves the note.')
    groups=[]
    for section,heading in [('changed','Changed from 0.8 to 0.9-s4'),('proposal','Proposed band (not adopted)')]:
        for g,label in [('disagree','Now disagrees with the owner'),('newly_agree','Newly agrees with the owner'),('unjudged','Changed, no owner judgement')]:
            n=sum(c['group']==section+'_'+g for c in cards)
            if n:groups.append(dict(id=section+'_'+g,heading=f'{label} ({n})',section=section))
    spec=dict(title='SEG final sheet — 0.8 → 0.9-s4',sheet_prefix='seg09',variant='decision',intro=intro,groups=groups,
              sections=[dict(id='changed',heading='Changed from 0.8 to 0.9-s4'),dict(id='proposal',heading='Proposed band (not adopted)',header='Current and proposed verdicts are shown on every card. The inner frame remains 0.9-s4. Shared changed lines appear here once.')])
    output=HERE/'seg09_sheet.html';output.write_text(owner_sheet.render(cards,spec))
    assert len(cards)==len(selected)==len({c['line_id'] for c in cards})
    assert output.stat().st_size<16_000_000
    js=(HERE/'vendor/owner_sheet.js').read_text()
    checks=["el.querySelector('.note').value", "last: initial.get(el), edited: false",'if (!state.edited || !state.ready || !db) return;', 'if (snapshot === state.last) return;', 'if (state.edited) state.schedule();',"timeZone: 'Europe/Athens'"]
    assert all(s in js for s in checks) and js.count('.set(doc, {merge: true})')==1
    html=output.read_text();assert 'data-verdict=' not in html and html.count('class="card"')==len(cards)
    assert html.count('class="version"')==2*len(cards)
    assert set(re.findall(r'data-id="(seg09:[^"]+)"',html))=={'seg09:'+lid for lid in selected}
    runtime=subprocess.run(['node',str(REVIEW/'tests/adjudicate/owner_sheet_runtime.cjs'),str(HERE/'vendor/owner_sheet.js')],capture_output=True,text=True)
    (HERE/'runtime_check.log').write_text(runtime.stdout+runtime.stderr);assert runtime.returncode==0,runtime.stderr
    (HERE/'cards.jsonl').write_text(''.join(json.dumps(m,ensure_ascii=False)+'\n' for m in manifest))
    receipt=dict(created=datetime.datetime.now(ZoneInfo('Europe/Athens')).isoformat(),network='OFF',segmentation_runs=0,reader_runs=0,published=False,git_writes=False,
                 renderer_head='19347b5a8a89bdb36391c2baf03ace3a3b0a4c11',vendor_sha256=vendor,inputs_sha256=INPUTS,
                 cards=len(cards),changed_set=len(changed),groups=dict(counts),proposed_band=len(proposals),proposal_records=sum(map(len,proposals.values())),shared_changed_proposal=len(changed&set(proposals)),
                 html_bytes=output.stat().st_size,html_sha256=sha(output),crop_sha={'passed':len(crop_checks),'total':len(cards)},crop_checks=crop_checks,
                 no_load_write='ok',runtime_check='passed',screenshot='pending',unresolved_step_attribution=sorted(missing_steps),
                 limitations=['Individual s1/s2/s3 typology replay verdicts were not saved; combined 0.8-to-s3 changes are labelled unresolved.', 'Unrolled display outlines invert the saved sampled base polyline; full per-pixel bases were not saved.'],
                 checks=dict(card_set_equality=True,unique_database_ids=True,last_two_versions=True,empty_initial_owner_marks=True,html_under_16_MB=True,byte_exact_embedded_crops=True))
    save(HERE/'receipt.json',receipt)
    print(f'Built {len(cards)} cards; changed {len(changed)}; groups {dict(counts)}; proposals {len(proposals)}; HTML {output.stat().st_size/1e6:.3f} MB; crop SHA {len(cards)}/{len(cards)}; runtime passed')
if __name__=='__main__':main()
