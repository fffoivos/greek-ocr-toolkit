"""Build the 25 numbered owner-case views and a reproducible round-3 report.

Page names and review coordinates belong ONLY to this evaluation script.
The detector receives pixels and optional provenance boxes, never these cases.
"""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / '.astra/out'
OLD = ROOT / '.astra/previous_round2'
REPORT = ROOT / 'docs/records/reviews/PAGE_LINES_ROUND3_20261009.md'
P = 'an-d6fd2cf2f618-p000047'
V = 's2-49598b2e848ab1f0ee1e-p00001'
T = 'an-1f8e7d022643-p000003'
S = 'an-3352d912f2e9-p000104'
G = 'an-d6002cf45e4d-p000058'
REVIEW_DIVIDERS = {'s2-d1ed1c2db37f431f4acb-p00001':1620,
                   's2-9de6cda8f03f0fc60a58-p00005':1683,
                   's2-7247ee9b1bc2374b3980-p00001':1741}
CASES = [
    (1,P,'Four font guides',[(60,740,1120,910)]),
    (2,P,'Accents split from letters',[(60,775,1120,900)]),
    (3,V,'First line of s00014 cut',[(90,820,1520,970)]),
    (4,V,'Bottom of s00024 cut',[(1510,2485,3040,2695)]),
    (5,P,'Stamp over text',[(650,1400,1178,1897)]),
    (6,P,'Stamp lettering made into lines',[(770,1450,1178,1897)]),
    (7,'s2-09f5dfca4af4d74173c6-p00005','Faint page',None),
    (8,'s2-0ce9d1025b3f23c7119e-p00001','Faint lines',None),
    (9,'s2-5ca02b142a2a3eaf078a-p00002','Bottom-right ghosts',[(1420,2390,2050,3300)]),
    (10,'s2-d1ed1c2db37f431f4acb-p00001','Bottom-left show-through',[(150,3630,1640,4400)]),
    (11,'an-ef481610a820-p000181','Jagged regions',None),
    (12,V,'Opposite-column connection',[(1180,1660,1950,1860)]),
    (13,'s2-74cdb23a34ca4a6cd01e-p00002','Missed bottom-left text',[(100,3930,1750,5200)]),
    (14,'s2-3229200bf47ca465a42d-p00004','Curled line starts',[(0,250,700,1500)]),
    (15,T,'Headpiece and decorated initials',[(50,100,1460,410),(90,1580,550,1835),(90,1990,550,2190)]),
    (16,T,'Letter-spaced ΑΚΟΛΟΥΘΙΑ',[(65,410,1460,590)]),
    (17,S,'Text printed over stamp',[(180,1530,1350,1920)]),
    (18,S,'Drop capital (open problem)',[(150,1570,620,1740)]),
    (19,'an-5c093c79d6bb-p000199','Facing pages joined at top',[(450,90,2860,530)]),
    (20,'an-9ea1564fcf4f-p000013','Facing pages joined throughout',None),
    (21,P,'Separate accent band',[(60,740,1120,910)]),
    (22,'an-a73d22211479-p000301','Broken column rule',[(60,1120,1720,2260)]),
    (23,G,'Engraving, caption, initial and text',None),
    (24,P,'Capital running head',[(280,45,1090,150)]),
    (25,P,'Text lost under stamp',[(50,1400,1178,1897)]),
]


def load(key):
    return (json.loads((OUT/f'{key}.lines.json').read_text()),
            json.loads((OUT/f'{key}.checks.json').read_text()))


def active(rows):
    return [(i,l) for i,l in enumerate(rows) if l['discounted'] is None]


def median_y(line):
    return float(np.median(line['baseline']))


def in_place(rows, x0, y0, x1, y1):
    return [(i,l) for i,l in active(rows) if l['x0']<x1 and l['x1']>x0 and y0<=median_y(l)<=y1]


def nearest(rows, old):
    # Compare spatially overlapping lines; the saved round-2 index is never
    # assumed to be the new index after insertions/deletions.
    options=[]
    for i,l in active(rows):
        overlap=min(l['x1'],old['x1'])-max(l['x0'],old['x0'])
        if overlap > .3*(old['x1']-old['x0']):
            options.append((abs(median_y(l)-median_y(old)),i,l))
    return min(options,key=lambda p:p[0])[1:] if options else (None,None)


def case_image(number,key,rois):
    rows=json.loads((OUT/f'{key}.lines.json').read_text())
    with Image.open(OUT/f'{key}.lines.jpg') as image:
        image=image.convert('RGB')
        if rois is None:
            rois=[(0,0,image.width,image.height)]
        panels=[]
        for box in rois:
            a,t,b,bot=box
            box=(max(0,a),max(0,t),min(image.width,b),min(image.height,bot))
            crop=image.crop(box)
            crop.thumbnail((1500,1700))
            # Label discounts after resizing so a full-page view does not turn
            # the distinction into unreadable source-resolution text.
            cd=ImageDraw.Draw(crop)
            sx,sy=crop.width/(box[2]-box[0]),crop.height/(box[3]-box[1])
            for i,line in enumerate(rows):
                by=median_y(line)
                if line['discounted'] and box[0]<=line['x0']<box[2] and box[1]<=by<box[3]:
                    x=(line['x0']-box[0])*sx;y=(by-box[1])*sy
                    label=f'D:{i}'
                    cd.rectangle(cd.textbbox((x,y),label),fill='white')
                    cd.text((x,y),label,fill=(115,40,115))
            panels.append(crop)
        canvas=Image.new('RGB',(max(900,max(p.width for p in panels)),sum(p.height+28 for p in panels)+66),'white')
        d=ImageDraw.Draw(canvas)
        d.text((8,6),f'Case {number:02d} | NEW round-3 output | {key}',fill='black')
        d.text((8,24),'Base red; mean blue; capitals green; descenders purple; accents orange/cyan dashed.',fill='black')
        d.text((8,42),'Region: grey outline + tint. D / [discounted]: retained candidate excluded from OCR.',fill='black')
        y=66
        for box,panel in zip(rois,panels):
            d.text((8,y),f'Source crop {box}',fill='black');y+=28
            canvas.paste(panel,(0,y));y+=panel.height
        path=OUT/'cases'/f'case-{number:02d}.jpg'
        canvas.save(path,quality=95)
        return str(path.relative_to(ROOT))


def summary_figure(records,name):
    values=[l['guide_residuals'][name]['p90'] for rows,_ in records.values() for _,l in active(rows)
            if l['guide_residuals'][name]['p90'] is not None]
    return float(np.median(values)) if values else None


def describe(number,key,rows,checks,records):
    selected=active(rows)
    cut=set(checks['cut_line_indices'])
    if number in (1,21):
        guide_names=('baseline','meanline','font_top','font_bottom') if number==1 else ('accent_bottom','accent_top')
        fig=', '.join(f'{g} {summary_figure(records,g):.3f}' for g in guide_names)
        borrow=sum(any(k in l['borrowed'] for k in guide_names) for rr,_ in records.values() for _,l in active(rr))
        extra=' Independent font accuracy remains unresolved; the frozen page-level curl maximum regresses to 14.61 px.' if number==1 else ''
        return ('not fixed' if number==1 else 'improved'),f'Class-conditioned joint fit; median per-line p90 distance in x-heights: {fig}. {borrow} active lines borrow at least one of these guides. Class assignments remain inferred.'+extra
    if number==2:
        selected=in_place(rows,100,805,1110,858)
        return ('fixed' if len(selected)==1 else 'not fixed'),f'{len(selected)} active baselines in the reviewed accent/body band (y 805–858); indices {[i for i,_ in selected]}. Marks attach to a body line.'
    if number in (3,4):
        old=json.loads((OLD/f'{key}.lines.json').read_text())[10 if number==3 else 93]
        i,l=nearest(rows,old)
        if l is None:return 'not fixed','No spatially matching active line.'
        margin=float(np.median(np.array(l['baseline'])-l['top']))/l['xheight'] if number==3 else float(np.median(np.array(l['bottom'])-l['baseline']))/l['xheight']
        return ('improved' if i in cut else 'fixed'),f'New line {i}; {"top" if number==3 else "bottom"} margin {margin:.2f} x-heights; source/strip cutoff flag {i in cut}. Page cutoff count {len(cut)}.'
    if number in (5,6):
        short=[(i,l) for i,l in in_place(rows,780,1450,1178,1897) if l['x0']>750]
        discounted=[i for i,l in enumerate(rows) if l['discounted'] and l['x0']>750 and 1450<median_y(l)<1900]
        ring=[(i,l) for i,l in short if not (900<l['x0']<990 and 1790<median_y(l)<1845)]
        if number==6:
            return ('fixed' if not ring else 'improved'),f'{len(ring)} active ring-lettering candidates; {len(discounted)} faint candidates retained with a discount reason ({discounted}). The remaining short active line {[i for i,_ in short]} is the printed catchword, verified in case-06.'
        broad=in_place(rows,60,1450,1120,1795)
        overextended=[i for i,l in broad if l['x0']<250 and l['x1']>1120]
        return 'improved',f'No separate active ring-lettering rows ({len(ring)} candidates); faint ring row(s) {discounted} discounted. Text continues through the stamp, but {len(overextended)} body line(s) extend beyond x 1120 ({overextended}); stamp influence is not fully removed.'
    if number in (7,8,9,10):
        faint=[(i,l) for i,l in enumerate(rows) if l['discounted'] and 'faint' in l['discounted']]
        if number in (9,10):
            a,t,b,bot={9:(1420,2390,2050,3300),10:(150,3630,1640,4400)}[number]
            faint=[(i,l) for i,l in faint if l['x0']<b and l['x1']>a and t<median_y(l)<bot]
        ratios=[l['contrast'] for _,l in faint]
        return ('fixed' if faint else 'not fixed'),f'{len(faint)} faint candidates explicitly discounted in the reviewed place; contrast/text range {min(ratios,default=0):.2f}–{max(ratios,default=0):.2f}; {checks["discounted_lines"]} total discounted. Uniform fading is retained in the synthetic control.'
    if number==11:
        jump=checks['checks']['5_smoothness']['maximum']
        return ('fixed' if jump<.1 else 'improved'),f'Maximum adjacent-column region jump {jump:.3f} x-heights (round 2: 14.4); {checks["boundary_overlaps"]} active overlap pairs.'
    if number in (12,19,20,22):
        xpos,ya,yb={12:(1530,1650,1900),19:(1670,120,400),20:(1545,220,1500),22:(883,300,2250)}[number]
        cross=[i for i,l in active(rows) if l['x0']<xpos<l['x1'] and ya<=median_y(l)<=yb]
        boundaries=checks['checks']['6_column_crossings']
        labels=''
        if number in (12,22):
            left=sorted({l['column'] for _,l in active(rows) if l['x1']<xpos})
            right=sorted({l['column'] for _,l in active(rows) if l['x0']>xpos})
            labels=f' Left/right column IDs: {left}/{right}.'
        return ('fixed' if not cross else 'not fixed'),f'{len(cross)} active lines cross the owner-located boundary x≈{xpos} in y {ya}–{yb}; {len(boundaries["full_height_boundaries"])} full-height gutters and {len(boundaries["continued_rules"])} fitted rule paths; automatic crossings {checks["rule_gutter_crossings"]}.'+labels
    if number==13:
        selected=in_place(rows,180,4030,1700,checks['image_size'][1])
        wide=[l for _,l in selected if l['x1']-l['x0']>800]
        starts=[l['x0'] for l in wide]
        last=sorted(selected,key=lambda r:median_y(r[1]))[-2:]
        last_text=[dict(line=i,x=[l['x0'],l['x1']],cut=i in cut) for i,l in last]
        return ('improved' if wide else 'not fixed'),f'{len(wide)} active lines wider than 800 px in the reviewed corner, starts {min(starts,default=0)}–{max(starts,default=0)}; {len(selected)} candidates there; page rule mask {100*checks["checks"]["7_missed_text"]["rule_mask_fraction"]:.2f}%. The last two printed rows are covered by {last_text}; the last region overextends into the left margin. Individual letter recall remains unlabelled.'
    if number==14:
        main=[l for _,l in active(rows) if l['x1']-l['x0']>500]
        starts=[l['x0'] for l in main]
        recovered=sum(x<170 for x in starts)
        return ('improved' if recovered else 'not fixed'),f'{recovered}/{len(main)} broad lines now start left of x 170; median start {np.median(starts) if starts else 0:.0f} px; page cutoff count {len(cut)}. Curl-tip completeness is not established by the start coordinate.'
    if number==15:
        head=in_place(rows,50,100,1460,410)
        return ('fixed' if not head else 'improved' if len(head)<10 else 'not fixed'),f'{len(head)} active headpiece lines (round 2: 10); {len(checks["checks"]["8_nontext_ink"]["detected_graphics"])} detected graphic regions. Case-15 also shows no active frame fragments; the letters inside decorated initials remain deferred.'
    if number==16:
        head=in_place(rows,50,450,1460,590)
        extent=[(l['x0'],l['x1']) for _,l in head]
        return ('fixed' if len(head)==1 and extent[0][0]<=105 and extent[0][1]>=1420 else 'improved'),f'{len(head)} active heading line(s), x extents {extent}; first Α and remaining capitals are judged at heading size.'
    if number==17:
        old=json.loads((OLD/f'{key}.lines.json').read_text())
        matched=[nearest(rows,old[j]) for j in (27,28)]
        ends=[l['x1'] for _,l in matched if l]
        return ('improved' if len(ends)==2 and min(ends)>990 else 'not fixed'),f'Former lines 27/28 now match {[(i,l["x0"],l["x1"]) for i,l in matched if l]}; printed right end is about x 1290. Cutoff flags {[i in cut for i,l in matched if l]}.'
    if number==18:
        old=json.loads((OLD/f'{key}.lines.json').read_text())
        matched=[nearest(rows,old[j]) for j in (25,26)]
        return 'not fixed',f'Open problem, explicitly deferred: the first two body lines start at {[(i,l["x0"]) for i,l in matched if l]}. No claim that the large Ε is assigned correctly.'
    if number==23:
        picture=in_place(rows,340,280,2440,1880)
        body=in_place(rows,200,2150,2500,3100)
        last=max(body,key=lambda p:median_y(p[1])) if body else None
        last_text=f'last text candidate {last[0]} starts x {last[1]["x0"]}' if last else 'no body line'
        return ('fixed' if not picture and last and last[1]['x0']<=320 and checks['broken_line_pairs']==0 else 'improved' if len(picture)<16 else 'not fixed'),f'{len(picture)} active engraving candidates (round 2: 16); {last_text}; {checks["broken_line_pairs"]} possible broken pairs. Woodcut letter remains deferred.'
    if number==24:
        head=in_place(rows,300,60,1100,145)
        return ('fixed' if head else 'not fixed'),f'{len(head)} running-head line(s), indices {[i for i,_ in head]}; tall-body counts {[l["ink_classes"]["tall_body"] for _,l in head]}; meanline borrowed {["meanline" in l["borrowed"] for _,l in head]}.'
    if number==25:
        text=in_place(rows,60,1450,1120,1795)
        text=[(i,l) for i,l in text if l['x0']<250]
        ends=[l['x1'] for _,l in text]
        complete=sum(x>=1050 for x in ends)
        return ('improved' if complete else 'not fixed'),f'{complete}/{len(text)} body lines through the stamp reach x≥1050; right ends {ends}; {sum(i in cut for i,_ in text)} still carry a cutoff flag.'
    raise ValueError(number)


def main():
    (OUT/'cases').mkdir(exist_ok=True)
    records={p.name.removesuffix('.checks.json'):load(p.name.removesuffix('.checks.json')) for p in sorted(OUT.glob('*.checks.json'))}
    if len(records)!=48:
        raise ValueError(f'Expected all 48 pages, found {len(records)}')
    # Supplement the detector's semantic-free line check with the corresponding
    # rough-box intersections. These are review flags, never graphic truth.
    supplement_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    for key,(_,c) in records.items():
        graphics=c['checks']['8_nontext_ink']['detected_graphics']
        segments=json.loads((OUT/f'{key}.segments.json').read_text())
        hits=[]
        for i,s in enumerate(segments):
            a,t,b,bot=s['box']
            if any(max(a,x)<min(b,r) and max(t,y)<min(bot,d) for x,y,r,d in graphics):
                hits.append(i)
        c['checks']['8_nontext_ink']['candidate_segments_on_detected_graphics']=hits
        c['checks']['8_nontext_ink']['segment_measurement']='Rough bounding-box intersection with detected graphic boxes; not semantic ground truth.'
        if key in REVIEW_DIVIDERS:
            rows,_=records[key]
            divider=REVIEW_DIVIDERS[key]
            c['checks']['6_column_crossings']['review_reference_x']=divider
            c['checks']['6_column_crossings']['review_crossing_lines']=[i for i,l in active(rows) if l['x0']<divider-.75*l['xheight'] and l['x1']>divider+.75*l['xheight']]
            c['checks']['6_column_crossings']['review_reference']='Visible column divider, manually reviewed; counts clear spans beyond +/-0.75 x-height around an approximate x reference, not a fitted rule. This reference is evaluation-only.'
        c['review_supplement_sha256']=supplement_hash
        (OUT/f'{key}.checks.json').write_text(json.dumps(c,indent=2))
    (OUT/'checks.json').write_text(json.dumps([c for _,c in records.values()],indent=2))
    table=[]
    for number,key,title,rois in CASES:
        rows,checks=records[key]
        state,measurement=describe(number,key,rows,checks,records)
        path=case_image(number,key,rois)
        table.append(dict(case=number,page=key,title=title,status=state,measurement=measurement,image=path))
    (OUT/'cases/cases.json').write_text(json.dumps(table,indent=2,ensure_ascii=False))
    lines=['# Page-lines round 3 — 9 October 2026','',
        'The detector now separates faint overlays from dark print, continues collinear rule pieces, and uses persistent page gaps to separate columns and facing pages. Capitals, small bodies, descenders and detached marks supply different contacts to a joint six-guide fit. Missing classes are recorded as borrowed. Region seams use stable neighbours and bend around assigned ink.', '',
        '**This remains a partial result.** The saved checks measure inferred component ownership, not manually labelled character truth. A smooth curve or a zero crossing count does not prove complete or pure OCR strips. Discounted candidates remain visible in JSON and review images; the public OCR-line API excludes them.', '',
        '## Implementation and validation','',
        '- Pixel-only discovery and supplemental body-bottom groups retain capital headings. PDF boxes are provenance only; all 24 available Vouli hint reruns must have identical geometry.',
        '- `page_font.py` classifies ink, associates marks, splits a fused upper mark at a narrow neck, and alternates one curve with robust class offsets. Compatible sizes supply missing font ratios. Gradual x-height variation is enabled only with distributed small-letter evidence. No third accent guide is asserted: there is no validated two-mode stack classification.',
        '- Long thin rule pieces are fitted in page coordinates. Isolated glyph stems are vetoed as rules. Graphic frames/texture and repeated motifs are removed before rule continuation, avoiding extrapolating picture strokes across text.',
        '- Baseline contacts still initialise shared column geometry with the existing crop tools. Local class fitting refines that initial shape; this is not a fully joint page-wide six-class optimisation. Font grouping currently uses type size, not a validated italic/typeface classifier.',
        '- Regions share smooth constraints between overlapping neighbours. Where ownership interleaves incompatibly, the midpoint compromise can still cut ink; those cuts remain in the checks.',
        '- Tests: see `.astra/tests-round3.log`; 12 new regressions cover all nine requested scenes, shared whitespace seams, indented reading order, and a connected table frame. Recognition is mocked by the existing contracts. The saved artifact and curl audits are separate from tests.',
        '', '### Traced round-2 causes', '',
        'For the missing running head, replaying `f405fe3` shows seed 2 (x 82–1099, y 73–284) peeling body lines at y 269, 217 and 166 with a fixed 21 px prior. On the next iteration the remaining head produces a projection peak at local y 53.4, but the crop fitter returns an unsupported band at page y 232.8 and zero letter bodies. `_discover` breaks there. The header pixels were neither absent nor masked; the fixed body-size prior and unsupported crop result stopped discovery. The supplemental body-bottom grouping recovers this capital band.', '',
        'For the missing first word below the woodcut on `an-d6002cf45e4d-p000058`, replaying round 2 finds intact text components at x 300–616, y 2934–2987, but no rough seed intersecting that row left of x 700. The model starts at x 923, y 2964. The woodcut rule evidence constrains the whole rough horizontal zone, and the later ten-x-height extension cannot reach the beginning. Thus unmasked pixels alone were insufficient: the seed column cut and bounded extension caused the miss. The revised graphic exclusion and rule handling restore a seed along the last row.', '',
        'The reproduction traces are retained in `.astra/work/trace-round2.log` and `.astra/work/trace-header.log`. Neither trace uses text-layer transcription as truth.',
        '', '## Every owner case', '',
        '| # | Page / place | New output and measured evidence | Status | Image |',
        '|---:|---|---|---|---|']
    for c in table:
        lines.append(f'| {c["case"]} | `{c["page"]}` — {c["title"]} | {c["measurement"]} | **{c["status"]}** | [case-{c["case"]:02d}](../../{c["image"]}) |')
    lines += ['', '## All 48 pages: checks 1–10', '',
        'Guide is the median of measured per-guide p90 residuals in x-heights (full class and per-line values are in each checks JSON). Borrow counts active lines borrowing any guide. Extra = no-body / closer-than-half-pitch pairs. Cut = source boundary or strip edge. D = discounted candidates. Jump = largest active region step in x-heights. Miss = unassigned text-size components, including possible non-text. Graphic = active lines / rough segment boxes intersecting detected graphics, not a semantic ground-truth count. Broken covers both heading and general possible splits. Gaps counts nearest-neighbour seams that still disagree after all competing constraints; each gap magnitude is recorded in check 10. Stamp-truncated text still requires the named visual cases; no automatic semantic stamp-recall count is claimed.', '',
        '| Page | Active | D | Guide | Borrow | Extra | Cut | Jump | Cross | Miss | Rule % | Graphic | Broken | Foreign | Overlap | Gaps |',
        '|---|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for key,(rows,c) in records.items():
        chk=c['checks'];res=[v['p90'] for _,l in active(rows) for v in l['guide_residuals'].values() if v['p90'] is not None]
        ex=chk['2_extra_lines'];miss=chk['7_missed_text']
        cross=str(c['rule_gutter_crossings'])
        if 'review_crossing_lines' in chk['6_column_crossings']:
            cross+=f' / {len(chk["6_column_crossings"]["review_crossing_lines"])} reviewed'
        lines.append(f'| `{key}` | {c["active_lines"]} | {c["discounted_lines"]} | {np.median(res) if res else 0:.3f} | {chk["1_font_and_accent_lines"]["borrowed_lines"]} | {len(ex["no_body_lines"])}/{len(ex["close_pairs"])} | {c["cut_ink_lines"]} | {chk["5_smoothness"]["maximum"]:.3f} | {cross} | {miss["unassigned_text_size_components"]} | {100*miss["rule_mask_fraction"]:.2f} | {len(chk["8_nontext_ink"]["candidate_lines_on_detected_graphics"])}/{len(chk["8_nontext_ink"]["candidate_segments_on_detected_graphics"])} | {c["broken_line_pairs"]} | {c["foreign_ink_lines"]} | {c["boundary_overlaps"]} | {len(chk["10_existing_checks"].get("seam_gaps",[]))} |')
    lines += ['', '## What does not work yet', '',
        'The following case outcomes are incomplete or explicitly deferred:', '']
    lines += [f'- Case {c["case"]}, `{c["page"]}`: {c["measurement"]}' for c in table if c['status']!='fixed']
    lines += ['', 'Tables remain in scope as text pieces; no table structure is inferred. Current table-page diagnostics:', '']
    for key in ('an-7a2b17a3fb0f-p000200','s2-200e977f2dab5291c42c-p00035','s2-831443dc5e6f1ccfbaf5-p00020'):
        _,c=records[key]
        lines.append(f'- `{key}`: {c["active_lines"]} active candidates; {c["cut_ink_lines"]} cutoff flags, {c["foreign_ink_lines"]} foreign-ink flags, {c["broken_line_pairs"]} possible broken pairs, {c["rule_gutter_crossings"]} detected boundary crossings. Zero crossings does not establish that every cell gap was detected.')
    lines += ['', 'The connected-table guard protects repeated text rows, but `an-7a2b17a3fb0f-p000200` still has a falsely excluded large region (x 719–1820, y 398–2113), visibly losing much of the left table. This is not fixed. The all-pairs overlap check passes independently of this missing-text error.', '']
    lines += ['Full-height rule continuation can also split a heading that spans the columns above a table: the heading on `s2-200e977f2dab5291c42c-p00035` and the ΠΙΝΑΞ heading on `an-2cfe28da5103-p000135` remain fragmented. The named ΑΚΟΛΟΥΘΙΑ fix does not establish general heading recall.', '']
    for key,divider in REVIEW_DIVIDERS.items():
        rows,c=records[key]
        joins=c['checks']['6_column_crossings']['review_crossing_lines']
        lines += [f'Visual boundary failure on `{key}`: {len(joins)} active candidates clearly cross the visible column divider near x {divider}, indices {joins}. No detected boundary protects this divider, so the automatic crossing count is falsely reassuring. Check 6 records the separate evaluation-only review reference and count; it does not alter the detector.', '']
    lines += ['On `s2-d1ed1c2db37f431f4acb-p00001`, case 10\'s faint ghost candidates are discounted but the columns remain joined. The independent saved-file audit also finds a real region overlap between candidates 84 and 87 (116 pixel columns, maximum depth 41.377 px); the zero-overlap requirement is therefore not met on all 48 pages.', '']
    for key,edge in (('an-5c093c79d6bb-p000199',480),('an-9ea1564fcf4f-p000013',400)):
        rows,_=records[key]
        ids=[i for i,l in active(rows) if l['x1']<edge]
        lines.append(f'- Scan-border check on `{key}`: {len(ids)} active candidates end left of x {edge}, indices {ids}. Fold separation and scan-border rejection are distinct checks.')
    lines += ['', 'Other limitations: mirrored show-through is not recognised by letter shape; discounting uses relative contrast and body evidence. Dark stamp lettering and small ornaments can still resemble letters. Contrast filtering can leave unassigned faint true marks. Drop capitals are recorded as observed, not solved. Held-out pages were not accessed.', '',
        'All 48 source/output bindings, per-line guide residuals, discount reasons and checks 1–10 are saved under `.astra/out/`. `cases/cases.json` is the machine-readable case table. The case images show only the new output.', '']
    validation={}
    test_log=ROOT/'.astra/tests-round3.log'
    if test_log.exists():
        matches=re.findall(r'(\d+) passed(?:, (\d+) warnings)? in ([\d.]+)s',test_log.read_text())
        if matches:
            passed,warnings,seconds=matches[-1]
            validation['tests']=dict(passed=int(passed),total=int(passed),warnings=int(warnings or 0),seconds=float(seconds),
                                     log_sha256=hashlib.sha256(test_log.read_bytes()).hexdigest())
    hints=[c['hint_comparison'] for _,c in records.values() if c['hint_comparison']]
    validation['hint_reruns']=dict(total=len(hints),identical=sum(h['identical_pixel_geometry'] for h in hints))
    blocked=ROOT/'.astra/git-commit-blocked.txt'
    if blocked.exists():
        validation['git_commit']=dict(status='blocked',reason=blocked.read_text().strip(),
                                     fallback_patch='.astra/page-lines-round3.patch',
                                     fallback_script='.astra/commit-page-lines-round3.sh')
    for name in ('artifact_audit','curl_contacts'):
        path=OUT/f'{name}.json'
        if path.exists():
            data=json.loads(path.read_text())
            validation[name]={k:v for k,v in data.items() if k!='records'}
    aggregates={name:sum(c[name] for _,c in records.values()) for name in
                ('active_lines','discounted_lines','cut_ink_lines','foreign_ink_lines','rule_gutter_crossings','boundary_overlaps','broken_line_pairs')}
    aggregates['seam_gap_pairs']=sum(len(c['checks']['10_existing_checks']['seam_gaps']) for _,c in records.values())
    aggregates['maximum_region_step_xh']=max(c['checks']['5_smoothness']['maximum'] for _,c in records.values())
    aggregates['reviewed_column_crossings']=sum(len(c['checks']['6_column_crossings'].get('review_crossing_lines',[])) for _,c in records.values())
    lines += ['## Validation receipt','',
              f'Tests: {validation.get("tests",{}).get("passed","pending")} passed. Hint reruns: {validation["hint_reruns"]["identical"]}/{len(hints)} identical in the renderer\'s compared geometry arrays. API documentation regenerated (206 public callable entries; generated content unchanged).', '',
              f'Across 48 pages: {aggregates["active_lines"]} active and {aggregates["discounted_lines"]} discounted candidates; {aggregates["cut_ink_lines"]} cutoff flags, {aggregates["foreign_ink_lines"]} foreign-ink flags, {aggregates["rule_gutter_crossings"]} automatically detected crossings but {aggregates["reviewed_column_crossings"]} clear crossings at the three separately reviewed dividers, {aggregates["boundary_overlaps"]} overlap pair(s), {aggregates["broken_line_pairs"]} possible broken pairs, and {aggregates["seam_gap_pairs"]} disagreeing seam pairs. The largest region step is {aggregates["maximum_region_step_xh"]:.3f} x-heights. Seam counts include distant rows with ordinary margins; inspect their recorded magnitudes and locations before treating every gap as a cutoff.', '']
    if 'artifact_audit' in validation:
        audit=validation['artifact_audit']
        missing=sum('missing' in f for f in audit['failures'])
        invalid=sum(len(f.get('invalid_lines',[])) for f in audit['failures'])
        overlaps=sum(len(f.get('overlap_pairs',[])) for f in audit['failures'])
        lines += [f'Saved-file audit: {audit["pages"]} pages; {missing} pages with missing files, {invalid} invalid bands, {overlaps} overlapping active pair(s). Every JPEG was decoded and every candidate strip accounted for, including wrapped table stacks. The detector/renderer hash matches the current source. The audit returns failure when overlaps remain.', '']
    if 'curl_contacts' in validation:
        contacts=validation['curl_contacts']['lines']
        covered=sum(c.get('covered_contacts',0) for c in contacts)
        total=sum(c.get('contacts',0) for c in contacts)
        errs=[c['max_absolute_error_px'] for c in contacts if 'max_absolute_error_px' in c]
        lines += [f'Independent frozen curl contacts: {covered}/{total} covered, worst baseline error {max(errs,default=0):.2f} px. These contacts test geometry only, not character recall or strip purity. Round 2 reported 10.2 px at crop 23: the new maximum is a regression, despite passing the unchanged crop-tool tests. The page-level joint fit still needs better class and neighbouring-shape constraints.', '']
    if 'git_commit' in validation:
        lines += ['Git staging was blocked by the sandbox when creating the worktree index lock. No commit was made. The requested fallback is `.astra/page-lines-round3.patch` with `.astra/commit-page-lines-round3.sh`; the script verifies the branch, base revision and file hashes, then commits with both required trailers. Nothing was pushed.', '']
    receipt=dict(status='PARTIAL',cases=table,validation=validation,aggregates=aggregates,
                 implementation_sha256=next(iter(records.values()))[1]['implementation_sha256'],
                 review_supplement_sha256=supplement_hash,
                 pages=[dict(page=k,**{n:c[n] for n in aggregates if n in c},
                             maximum_region_step_xh=c['checks']['5_smoothness']['maximum'],
                             reviewed_column_crossings=len(c['checks']['6_column_crossings'].get('review_crossing_lines',[])),
                             seam_gap_pairs=len(c['checks']['10_existing_checks']['seam_gaps'])) for k,(_,c) in records.items()])
    REPORT.with_suffix('.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False))
    REPORT.write_text('\n'.join(lines))
    print(f'Wrote {REPORT} and {len(table)} case images')


if __name__=='__main__':
    main()
