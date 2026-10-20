"""Recheck all owner cases and compare the 54 outputs to round-four part one.

Review coordinates and page identities are evaluation-only, never detector input.
Run after render_page_line_segments.py --layout .astra/layout.
"""
from pathlib import Path
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from scripts.glyphs.archive.audit_tables_round4 import metrics, differences
from scripts.glyphs.archive.review_page_lines_round3 import CASES, in_place, active, median_y, nearest

OUT = ROOT/'.astra/out'
OLD = ROOT/'.astra/previous_round4_part1'
REPORT = ROOT/'docs/records/reviews/PAGE_LINES_ROUND4_NONTABLE_20261009.md'
Image.MAX_IMAGE_PIXELS = 500_000_000


def read(p):
    return json.loads(p.read_text())


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def crossed(rows, x, slope=0., yref=0., top=0., bottom=1e9):
    return [i for i,l in active(rows) if top <= median_y(l) <= bottom
            and l['x0'] < x+slope*(median_y(l)-yref)-.75*l['xheight']
            and l['x1'] > x+slope*(median_y(l)-yref)+.75*l['xheight']]


DIVIDERS = {
    's2-0ce9d1025b3f23c7119e-p00001': (1715.,0.,0.),
    's2-9de6cda8f03f0fc60a58-p00005': (1676.,53/3600,300.),
    's2-d1ed1c2db37f431f4acb-p00001': (1578.,27/3600,300.),
}
R3 = [
    (26,'s2-0ce9d1025b3f23c7119e-p00001','Joined columns and faint halves',None),
    (27,'s2-93f8070059f938bda524-p00001','Good reference to preserve',None),
    (29,'s2-9de6cda8f03f0fc60a58-p00005','Joined across the slanted solid rule',None),
    (30,'s2-d1ed1c2db37f431f4acb-p00001','Joined across the differently slanted rule',None),
    (31,'s2-3229200bf47ca465a42d-p00004','Missing first characters, old lines 32–46',[(55,1520,660,2390)]),
    (32,'an-1436ae03653f-p000163','Ornamental border, old s00039',[(340,3450,2050,3590)]),
]


def case_image(round_, number, key, rois):
    im=Image.open(OUT/f'{key}.lines.jpg').convert('RGB')
    if rois is None:
        rois=[(0,0,*im.size)]
    if round_==2 and number==14:
        rois=[(55,350,600,1100),(55,1520,660,2390)]
    panels=[]
    for a,t,b,bot in rois:
        crop=im.crop((max(0,a),max(0,t),min(im.width,b),min(im.height,bot)))
        crop.thumbnail((1650,1900));panels.append(crop)
    canvas=Image.new('RGB',(max(950,max(p.width for p in panels)),sum(p.height for p in panels)+65),'white')
    d=ImageDraw.Draw(canvas)
    d.text((8,8),f'Round {round_}, case {number:02d} | NEW part-2 output | {key}',fill='black')
    d.text((8,26),'Active lines only. Red baseline; blue mean; green capitals; purple descenders.',fill='black')
    d.text((8,44),'Orange/cyan dashed: accent bottom/top. Tint/grey: extraction region.',fill='black')
    y=65
    for panel in panels:
        canvas.paste(panel,(0,y));y+=panel.height
    name=f'r{round_}-case-{number:02d}.jpg'
    canvas.save(OUT/'cases'/name,quality=95)
    return name


def audit():
    pages=sorted((ROOT/'.astra/pages').glob('*.png'))
    assert len(pages)==54
    tables={p.stem for p in (ROOT/'docs/records/tables/annotations').glob('*.json')}
    rows=[];records={}
    for p in pages:
        key=p.stem;lines=read(OUT/f'{key}.lines.json');oldlines=read(OLD/f'{key}.lines.json')
        c=read(OUT/f'{key}.checks.json');old=read(OLD/f'{key}.checks.json')
        assert c['source_sha256']==old['source_sha256']==sha(p)
        segments=read(OUT/f'{key}.segments.json');cells=read(OUT/f'{key}.cells.json')
        graphics=c['checks']['8_nontext_ink']['detected_graphics']
        c['checks']['8_nontext_ink']['candidate_segments_on_detected_graphics']=[i for i,s in enumerate(segments)
            if any(max(s['box'][0],g[0])<min(s['box'][2],g[2]) and max(s['box'][1],g[1])<min(s['box'][3],g[3]) for g in graphics)]
        ref=old['checks']['6_column_crossings'].get('review_reference_x')
        if ref is not None:
            c['checks']['6_column_crossings'].update(review_reference_x=ref,
                review_reference=old['checks']['6_column_crossings']['review_reference'],
                review_crossing_lines=crossed(lines,ref))
        if key in DIVIDERS:
            c['checks']['6_column_crossings']['owner_slanted_reference']=dict(
                parameters=DIVIDERS[key],old_lines=crossed(oldlines,*DIVIDERS[key]),new_lines=crossed(lines,*DIVIDERS[key]))
        c['nontable_review_sha256']=sha(Path(__file__))
        (OUT/f'{key}.checks.json').write_text(json.dumps(c,indent=2)+'\n')
        w,h=c['image_size']
        for ext in ('lines.jpg','unrolled.jpg'):
            with Image.open(OUT/f'{key}.{ext}') as im: im.verify()
        assert len(cells['cells'])==c['active_lines']
        for piece in cells['cells']:
            a,t,b,bot=piece['box_pixels']
            assert 0<=a<b<=w and 0<=t<bot<=h and piece['coord_origin']=='TOPLEFT'
            assert np.allclose(piece['box_page'],np.array(piece['box_pixels'])/3)
            assert lines[piece['line_index']]['discounted'] is None
        for l in lines:
            for curve in ('baseline','meanline','font_top','font_bottom','accent_top','accent_bottom','top','bottom'):
                assert len(l[curve])==l['x1']-l['x0'] and np.isfinite(l[curve]).all()
        before=metrics(old,oldlines);after=metrics(c,lines)
        worse={k:dict(old=before[k],new=after[k]) for k in before if after[k]>before[k]+1e-10}
        row=dict(key=key,table_page=key in tables,old=before,new=after,worse=worse,
                 active=[old['active_lines'],c['active_lines']],discounted=[old['discounted_lines'],c['discounted_lines']],
                 exact_lines_equal=oldlines==lines,check_differences=differences(old['checks'],c['checks']),
                 hashes={ext:sha(OUT/f'{key}.{ext}') for ext in ('checks.json','lines.json','cells.json','lines.jpg','unrolled.jpg')})
        rows.append(row);records[key]=(lines,c,oldlines,old)
    result=dict(pages=54,baseline_commit='376ab5d',rows=rows,any_worse_pages=[r['key'] for r in rows if r['worse']])
    assert len({c['implementation_sha256'] for _,c,_,_ in records.values()})==1, 'Mixed detector revisions'
    reference=next(r for r in rows if r['key']=='s2-93f8070059f938bda524-p00001')
    assert reference['exact_lines_equal'] and not reference['worse'], 'Case 27 reference changed'
    (OUT/'regression-nontable.json').write_text(json.dumps(result,indent=2)+'\n')
    (OUT/'checks.json').write_text(json.dumps([r[1] for r in records.values()],indent=2)+'\n')
    return result,records


def describe(round_,n,key,records):
    lines,c,oldlines,old=records[key];same=lines==oldlines
    cuts=set(c['cut_line_indices']);sel=active(lines)
    if round_==3:
        if n in (26,29,30):
            before=crossed(oldlines,*DIVIDERS[key]);after=crossed(lines,*DIVIDERS[key])
            status='fixed' if not after else 'improved' if len(after)<len(before) else 'not fixed'
            faint=[l for l in lines if l['discounted'] and 'faint' in l['discounted']]
            extra='Crossings use the review’s slanted path, separately from detected boundaries.'
            if n==26:
                prefix=[(i,l) for i,l in active(lines) if l['x0']<800 and 320<median_y(l)<390]
                tail=[(i,l) for i,l in enumerate(lines) if l['discounted'] and 700<l['x0']<1000 and 320<median_y(l)<390]
                extra=f'Αριθ. 302 prefix: {[(i,l["x0"],l["x1"],l["contrast"]) for i,l in prefix]}; separately discounted tail: {[(i,l["x0"],l["x1"],l["contrast"]) for i,l in tail]}. Tuple = index/start/end/relative contrast. Faint-letter purity elsewhere remains unlabelled.'
            if n==29:
                body_before=crossed(oldlines,*DIVIDERS[key],top=250)
                body_after=crossed(lines,*DIVIDERS[key],top=250)
                if not body_after:
                    status='fixed'
                extra+=f' Body-only joins below y 250: {len(body_before)} → {len(body_after)}. The centred page number 485 above the rule is an intentional crossing of the extrapolated reference, verified on the image.'
            return status,f'Owner-position crossings {len(before)} → {len(after)} (indices {after}); automatic crossings {c["rule_gutter_crossings"]}; active {old["active_lines"]} → {c["active_lines"]}; {len(faint)} faint candidates discounted. '+extra
        if n==27:
            wide=max(l['x1']-l['x0'] for _,l in sel)
            return ('unchanged' if same else 'improved'),f'Exact line records equal to part 1: {same}; {c["active_lines"]} active / {c["discounted_lines"]} discounted; widest active {wide} px; cuts {c["cut_ink_lines"]}; foreign {c["foreign_ink_lines"]}; crossings/overlaps/broken {c["rule_gutter_crossings"]}/{c["boundary_overlaps"]}/{c["broken_line_pairs"]}.'
        if n==31:
            matching=[(j,*nearest(lines,oldlines[j])) for j in range(32,min(47,len(oldlines))) if oldlines[j]['discounted'] is None]
            starts=[l['x0'] for _,_,l in matching if l]
            pairs=[f'{j}→{i}: {l["x0"]}' for j,i,l in matching if l]
            return 'improved',f'Old row → new row: start x = {", ".join(pairs)}. {sum(85<=x<=105 for x in starts)}/{len(starts)} start in the review’s approximate first-letter range (85–100 px, allowing 5 px). Page cuts {old["cut_ink_lines"]} → {c["cut_ink_lines"]}. Old row 46 was already discounted at the bottom edge. Start position alone does not certify curl fit or every glyph.'
        if n==32:
            hits=in_place(lines,373,3490,2030,3580)
            before=in_place(oldlines,373,3490,2030,3580)
            rejected=[i for i,l in enumerate(lines) if l['discounted'] and l['x1']>373 and l['x0']<2030 and 3490<median_y(l)<3580]
            return ('fixed' if not hits else 'improved' if len(hits)<len(before) else 'not fixed'),f'Active border candidates {len(before)} → {len(hits)} (indices {[i for i,_ in hits]}); discounted candidates {rejected}, reasons {[lines[i]["discounted"] for i in rejected]}. The long reviewed band is removed; any remaining short edge fragment is still a failure. Discounted candidates have no cells or drawn guides.'
    if n in (1,21):
        guides=('baseline','meanline','font_top','font_bottom') if n==1 else ('accent_bottom','accent_top')
        parts=[]
        for g in guides:
            values=[l['guide_residuals'][g]['p90'] for rr,_,_,_ in records.values() for _,l in active(rr) if l['guide_residuals'][g]['p90'] is not None]
            parts.append(f'{g} {np.median(values):.3f}')
        borrowed=sum(any(g in l['borrowed'] for g in guides) for rr,_,_,_ in records.values() for _,l in active(rr))
        return ('not fixed' if n==1 else 'unchanged'),f'All 54 pages: median class-contact p90 residuals (x-heights): {", ".join(parts)}; {borrowed} active lines borrow one of these guides. Six guides share one fitted shape and gradual scale; class truth and page-wide joint optimisation remain unvalidated.'
    if n==2:
        hits=in_place(lines,100,805,1110,858)
        return ('unchanged' if same else 'fixed' if len(hits)==1 else 'not fixed'),f'{len(hits)} active baselines in y 805–858: {[i for i,_ in hits]}. Accent marks are assigned to bodies; no independent accent-row crop is intended.'
    if n in (3,4):
        x,y=(800,901) if n==3 else (2200,2573)
        i,l=min(((i,l) for i,l in sel if l['x0']<x<l['x1']),key=lambda z:abs(median_y(z[1])-y))
        margin=np.median(np.array(l['baseline'])-l['top'])/l['xheight'] if n==3 else np.median(np.array(l['bottom'])-l['baseline'])/l['xheight']
        return ('not fixed' if i in cuts else 'unchanged' if same else 'fixed'),f'New line {i}, baseline y {median_y(l):.1f}; {"top" if n==3 else "bottom"} margin {margin:.2f} x-heights; cutoff flag {i in cuts}; page cut flags {old["cut_ink_lines"]} → {c["cut_ink_lines"]}.'
    if n in (5,6):
        short=[(i,l) for i,l in in_place(lines,780,1450,1178,1897) if l['x0']>750]
        ring=[i for i,l in short if not (900<l['x0']<990 and 1790<median_y(l)<1845)]
        faint=[i for i,l in enumerate(lines) if l['discounted'] and l['x0']>750 and 1450<median_y(l)<1900]
        text=[l for _,l in in_place(lines,60,1450,1120,1795) if l['x0']<250]
        return ('unchanged' if same else 'improved'),f'{len(ring)} active ring-lettering candidates; {len(faint)} discounted short candidates; short active IDs {[i for i,_ in short]}. '+(f'{sum(l["x1"]>1120 for l in text)} text lines overextend beyond x 1120; stamp influence remains.' if n==5 else 'The candidate near y 1820 is the printed catchword; rotation-based stamp classification is deferred.')
    if n in (7,8,9,10):
        bounds={7:(0,0,*c['image_size']),8:(0,0,*c['image_size']),9:(1420,2390,2050,3300),10:(150,3630,1640,4400)}[n]
        a,t,b,bot=bounds
        faint=[l for l in lines if l['discounted'] and 'faint' in l['discounted'] and l['x0']<b and l['x1']>a and t<median_y(l)<bot]
        ratios=[l['contrast'] for l in faint]
        extra=f' Column crossings {len(crossed(oldlines,*DIVIDERS[key]))} → {len(crossed(lines,*DIVIDERS[key]))}.' if key in DIVIDERS else ''
        if n==10:
            residual=in_place(lines,150,4190,1640,4240)
            extra+=f' Visual review still finds a false line on the bottom printed rule: {[(i,round(median_y(l),1)) for i,l in residual]} (index, baseline y); its crop includes show-through.'
        return ('unchanged' if same else 'improved'),f'{len(faint)} faint candidates discounted in the named place; relative contrast {min(ratios,default=0):.2f}–{max(ratios,default=0):.2f}; {c["discounted_lines"]} total discounts.'+extra+' Faint letters inside active crops are not independently labelled.'
    if n==11:
        jump=c['checks']['5_smoothness']['maximum']
        return ('unchanged' if same else 'fixed' if jump<.1 else 'improved'),f'Maximum boundary step {jump:.4f} x-heights; {c["boundary_overlaps"]} overlaps (owner round 2 maximum 14.4).'
    if n in (12,19,20,22):
        x,t,bot={12:(1530,1650,1900),19:(1670,120,400),20:(1545,220,1500),22:(883,300,2250)}[n]
        hits=crossed(lines,x,top=t,bottom=bot)
        return ('not fixed' if hits else 'unchanged' if same else 'fixed'),f'{len(hits)} active crossings at reviewed x≈{x}, y {t}–{bot}; indices {hits}; automatic page crossings {c["rule_gutter_crossings"]}; broken pairs {c["broken_line_pairs"]}.'
    if n==13:
        hits=in_place(lines,180,4030,1700,c['image_size'][1]);wide=[l for _,l in hits if l['x1']-l['x0']>800]
        starts=[l['x0'] for l in wide]
        before=[l for _,l in in_place(oldlines,180,4030,1700,c['image_size'][1]) if l['x1']-l['x0']>800]
        return ('unchanged' if [(l['x0'],l['x1']) for l in before]==[(l['x0'],l['x1']) for l in wide] else 'improved'),f'{len(before)} → {len(wide)} broad rows below y 4030; starts {min(starts,default=0)}–{max(starts,default=0)} px; {len(hits)} active candidates there; page rule mask {100*c["checks"]["7_missed_text"]["rule_mask_fraction"]:.2f}%. Individual first/last letters remain unlabelled.'
    if n==14:
        starts=[l['x0'] for _,l in sel if l['x1']-l['x0']>500]
        return 'improved',f'{sum(x<170 for x in starts)}/{len(starts)} broad lines start left of x 170; median start {np.median(starts):.1f} px. See round-3 case 31 for every bottom-row match and the remaining curl error.'
    if n==15:
        hits=in_place(lines,50,100,1460,410)
        return ('unchanged' if same else 'fixed' if not hits else 'not fixed'),f'{len(hits)} active headpiece rows (round 2: 10); IDs {[i for i,_ in hits]}; {len(c["checks"]["8_nontext_ink"]["detected_graphics"])} detected graphics. Decorated/drop initials remain deferred.'
    if n==16:
        hits=in_place(lines,50,450,1460,590)
        return ('unchanged' if same else 'fixed' if len(hits)==1 else 'not fixed'),f'{len(hits)} active ΑΚΟΛΟΥΘΙΑ heading rows; extents {[(l["x0"],l["x1"]) for _,l in hits]}; the first Α must remain with the rest.'
    if n in (17,25):
        hits=[(i,l) for i,l in in_place(lines,60,1450 if n==25 else 1650,1350,1795 if n==25 else 1900) if l['x0']<350]
        ends=[l['x1'] for _,l in hits]
        return ('unchanged' if same else 'not fixed'),f'Text rows in stamp area: {[(i,l["x0"],l["x1"]) for i,l in hits]}; {sum(i in cuts for i,_ in hits)} cut flags. Printed ends are approximately x {1095 if n==25 else 1290}; endpoint coverage is not proof of letter completeness. '+('Ends extend farther into the stamp than part 1 (up to x 1343, previously 1328); this is not certified text recovery.' if n==17 else '')
    if n==18:
        hits=in_place(lines,150,1600,620,1740)
        return 'not fixed',f'Open problem, deliberately deferred: the two-line Ε is not assigned as a drop capital. The {len(hits)} active paragraph rows here start at {[(i,l["x0"]) for i,l in hits]} (index, x pixels), to its right. No drop-capital code change; the current crop is included for review.'
    if n==23:
        hits=in_place(lines,340,280,2440,1880);body=in_place(lines,200,2150,2500,3100)
        last=max(body,key=lambda z:median_y(z[1])) if body else None
        before=in_place(oldlines,340,280,2440,1880)
        oldbody=in_place(oldlines,200,2150,2500,3100)
        oldlast=max(oldbody,key=lambda z:median_y(z[1])) if oldbody else None
        unchanged=len(before)==len(hits) and oldlast and last and oldlast[1]['x0']==last[1]['x0']
        return ('unchanged' if unchanged else 'improved'),f'{len(before)} → {len(hits)} active engraving candidates; last body row {last[0] if last else None}, start x {last[1]["x0"] if last else None}; {c["broken_line_pairs"]} broken pairs. The woodcut initial remains deferred.'
    if n==24:
        hits=in_place(lines,300,60,1100,145)
        return ('unchanged' if same else 'fixed' if hits else 'not fixed'),f'{len(hits)} running-head rows, IDs {[i for i,_ in hits]}; tall-body counts {[l["ink_classes"]["tall_body"] for _,l in hits]}; mean guide borrowed {["meanline" in l["borrowed"] for _,l in hits]}.'
    raise ValueError(n)


def main():
    audit_result,records=audit();(OUT/'cases').mkdir(exist_ok=True)
    cases=[]
    for round_,entries in ((3,R3),(2,CASES)):
        for n,key,title,rois in entries:
            status,measurement=describe(round_,n,key,records)
            cases.append(dict(round=round_,case=n,page=key,title=title,status=status,measurement=measurement,
                              image=case_image(round_,n,key,rois)))
    (OUT/'cases-nontable.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2)+'\n')
    lines=['# Page lines round 4, part 2: ordinary pages — 9 October 2026','',
      'Column stops now use direct slanted-stroke evidence and narrower persistent gutters. Continued strokes are checked before extending through letter bodies. A coherent faint tail is separated from a dark prefix before contrast scoring; uniformly faded text and isolated light letters are retained. Unsupported ornament bands are discounted before OCR delivery and rendering. The existing four font guides and two accent guides retain their joint per-line shape fit. OpenCV, already used by the table path, is now declared as a core dependency for slanted-stroke detection.','',
      '**Partial result.** The report distinguishes changed measurements from complete glyph recovery. Orientation and drop capitals are deferred. No held-out page was accessed. The 54 source PNGs and part-1 JSON/image outputs were preserved with hashes in `.astra/previous_round4_part1/receipt.json` before this run.','',
      '## Every requested case','',
      '“Unchanged” means the named issue was re-measured on the new output; it does not assert that all ink on that page is correct. Fixed refers to the named test, not whole-page OCR quality. Coordinates are review coordinates, used only by this evaluation script. Owner-position crossings require more than 0.75 x-heights on each side of the reference at the median baseline; both old and new outputs use this same test, so counts can differ from the original review’s fixed-pixel tolerance.','',
      '| Case | Page and exact place | New result and measurement | Status | New image |',
      '|---|---|---|---|---|']
    for r in cases:
        page=(f'all 54 pages; example `{r["page"]}`' if r['round']==2 and r['case'] in (1,21) else f'`{r["page"]}`')
        lines.append(f'| R{r["round"]}-{r["case"]:02d} | {page} — {r["title"]} | {r["measurement"]} | **{r["status"]}** | [view](../../.astra/out/cases/{r["image"]}) |')
    lines += ['', '## All 54 pages against part 1','',
      'Each vector is part 1 → part 2. G = median per-guide p90 residual / borrowed lines. E = no-body / close pairs. C = cut flags. D = discounts (not a badness score). J = maximum boundary step in x-heights. X = detected / fixed-position review crossings; the separate slanted review checks are in the cases above and checks JSON. M = unassigned text-size components / pixels, including possible non-text. N = graphic line / rough-segment intersections. B = broken pairs. F/O/S = foreign ink / overlaps / seam gaps. These checks use inferred components, not independent character labels. Every increase, including a changed denominator or numerical guide residual, is flagged.','',
      '| Page | G | E | C | D | J | X | M | N | B | F/O/S | Any worse? |',
      '|---|---|---|---|---|---|---|---|---|---|---|---|']
    groups=[('guide_p90_median','borrowed_lines'),('no_body_lines','close_pairs'),('cut_ink_lines',),(),('maximum_jump',),('rule_gutter_crossings','review_crossings'),('unassigned_text_size_components','unassigned_text_size_ink'),('graphic_lines','graphic_segments'),('broken_line_pairs',),('foreign_ink_lines','boundary_overlaps','seam_gaps')]
    def fmt(v): return f'{v:.4f}' if isinstance(v,float) else str(v)
    for r in audit_result['rows']:
        values=[]
        for group in groups:
            values.append('→'.join('/'.join(fmt(r[side][k]) for k in group) for side in ('old','new')) if group else '→'.join(map(str,r['discounted'])))
        lines.append('| `'+r['key']+'` | '+' | '.join(values)+' | '+('**YES**' if r['worse'] else 'No')+' |')
    lines += ['', '### Every worsened measurement','']
    def precise(v): return f'{v:.10g}' if isinstance(v,float) else str(v)
    for r in audit_result['rows']:
        if r['worse']:
            lines.append(f'- `{r["key"]}`: '+', '.join(f'{k} {precise(v["old"])}→{precise(v["new"])}' for k,v in r['worse'].items())+'.')
    lines += ['', '## Table preservation','',
      'See [table-preservation.json](../../.astra/out/table-preservation.json) for all eight pages: current piece geometry against part 1, element-by-element coverage, crossing pieces, and fresh model forwards. The offline acceptance harness and actual DocumentConverter label-injection pipeline were rerun. Recognition remains substituted with labels.','']
    preservation=OUT/'table-preservation.json'
    if preservation.exists():
        tr=read(preservation)
        lines += [f'Part-1 acceptance preservation: **{sum(r["passed"] for r in tr["rows"])}/8 pass**. This preserves the existing partial table result; it does not turn the part-1 failures into passes.','',
                  '| Page | Complete elements | Crossing pieces | Final missing labels | Wrong owners | Preserved? |',
                  '|---|---|---|---|---|---|']
        for r in tr['rows']:
            arrow=lambda v:'→'.join(map(str,v))
            lines.append(f'| `{r["key"]}` | {arrow(list(r["complete_elements"].values()))} | {arrow(r["crossing_pieces"])} | {arrow(r["final_missing"])} | {arrow(r["final_wrong"])} | {r["passed"]} |')
    lines += ['',
      '## What does not work yet','',
      '- Guide residuals measure inferred classes. They do not certify correct small-letter, capital, accent or descender labels. The fit is joint per line, regularised by neighbouring baseline geometry; it is not a fully joint six-class page-wide optimisation.',
      '- Contrast splitting handles coherent spatial changes, including a dark prefix followed by a faint tail. Faint ink interleaved or superimposed with foreground letters and stamp removal remain unresolved; no independent semantic purity count is claimed.',
      '- Curl recovery can retain more first-letter ink while still misfitting a first-letter baseline or retaining margin ink. Inspect the named line matches and images; endpoint changes alone are not an acceptance gate.',
      f'- Boundary cuts, foreign ink, unassigned text-size components and possible broken rows remain. {len(audit_result["any_worse_pages"])}/54 pages have at least one worse measurement; all are listed above. Case 10 still includes a false crop on the bottom printed rule, with show-through inside it.',
      '- Ornament rejection is conservative morphology and support analysis. Repeated shapes resembling actual letters cannot be identified reliably without further evidence.',
      '- The overall-review question about per-letter ink states remains open: line JSON contains component class counts, not per-letter intact/merged/broken/faint records.',
      '- Part-1 table failures remain open. Orientation and drop-capital handling were not implemented. No character recognition, CER or held-out generalisation test was run.','',
      '## Validation and reproduction','']
    test=OUT/'tests-nontable.xml'
    if test.exists():
        suites=ET.parse(test).getroot();total=sum(int(s.attrib.get('tests',0)) for s in suites.iter('testsuite'))
        skipped=sum(int(s.attrib.get('skipped',0)) for s in suites.iter('testsuite'))
        failed=sum(int(s.attrib.get('failures',0))+int(s.attrib.get('errors',0)) for s in suites.iter('testsuite'))
        lines.append(f'Full suite: **{total-skipped-failed} passed, {skipped} skipped, {failed} failed; {total} collected**. [Log](../../.astra/out/tests-nontable.log).')
    lines += ['', 'Nine new parametrised synthetic checks cover ±0.5°/±1° rules with level neighbouring rows, a faint half opposite dark text, a dark prefix with a faint tail in the same column, curled starts beside a binding shadow, repeated solid non-letter shapes with real-text controls, and false continuation through separated letter stems. All artifact sets are checked for finite curves, page-unit boxes, valid image streams and exclusion of discounted candidates from cells. The renderer skips discounts for both overlays and strips.','',
      'Use `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python` from this worktree, with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1`:','',
      '```sh','python scripts/generate_api_docs.py','python -m pytest -p no:cacheprovider --junitxml=.astra/out/tests-nontable.xml',
      'python scripts/glyphs/render_page_line_segments.py --layout .astra/layout',
      'python scripts/glyphs/archive/evaluate_tables_round4.py',
      'python scripts/glyphs/archive/integrate_docling_tables_round4.py',
      'python scripts/glyphs/archive/score_tables_round4.py',
      'python scripts/glyphs/archive/check_tables_part2.py',
      'python scripts/glyphs/archive/review_page_lines_round4_nontable.py','```','',
      'API regeneration produced 211 public entries and no API diff. No public signature changed. Foreground execution only; no push or model download. Machine-readable results: [case records](../../.astra/out/cases-nontable.json), [all-page regression](../../.astra/out/regression-nontable.json).','',
      '## Commit handoff','',
      'No commit was made: the sandbox refused creation of the worktree `index.lock` during `git add` (`Operation not permitted`). The requested fallback is [the patch](../../.astra/page-lines-round4-nontable.patch) and [the commit script](../../.astra/commit-page-lines-round4-nontable.sh). The patch is replayed against HEAD files in a temporary directory and checked byte-for-byte. The script verifies branch `astra/page-lines-4`, base `376ab5d`, an empty index, file hashes and reverse patch applicability before committing the explicit file list with the requested Co-Authored-By and Claude-Session footers. It does not push. [Validation receipt](../../.astra/round4-nontable-patch-validation.json).']
    REPORT.write_text('\n'.join(lines)+'\n')
    durable=dict(status='PARTIAL',baseline_commit='376ab5d',cases=cases,
                 pages=[{k:v for k,v in r.items() if k!='check_differences'} for r in audit_result['rows']],
                 table_preservation=read(preservation) if preservation.exists() else None,
                 tests=dict(total=total,passed=total-skipped-failed,skipped=skipped,failed=failed) if test.exists() else None)
    REPORT.with_suffix('.json').write_text(json.dumps(durable,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),pages=54,worse_pages=audit_result['any_worse_pages']),indent=2))


if __name__=='__main__':
    main()
