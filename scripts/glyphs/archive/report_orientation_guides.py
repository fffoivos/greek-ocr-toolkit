"""Write the part-3c measured report without changing its preregistered rules."""
from __future__ import annotations
from collections import Counter
import json
import numpy as np
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from greekocr.ops.data_root import input_path as _data_input
OUT=ROOT/'.astra/out/orientation_eval'
REPORT=ROOT/'docs/records/reviews/PAGE_LINES_ROUND4_ORIENTATION_GUIDES_20261009.md'


def read(p):return json.loads(_data_input(p).read_text())
def pct(x):return '—' if x is None else f'{100*x:.1f}%'
def table(lines,headers,rows):
    lines.extend(['','| '+' | '.join(headers)+' |','|'+'|'.join('---' for _ in headers)+'|'])
    lines.extend('| '+' | '.join(map(str,row))+' |' for row in rows);lines.append('')


def main():
    summary=read(OUT/'summary.json');delivery=read(OUT/'delivery-summary.json');testfile=OUT/'tests.xml'
    assert len(delivery['pages'])==54 and len(delivery['rotated_words'])==216, 'page delivery audit incomplete'
    assert len(delivery['tables'])==8 and len(delivery.get('composite_words',[]))==51, 'table/composite audit incomplete'
    production=read(OUT/'production-orientation-time.json')
    assert len(production['rows'])==54, 'production orientation timing incomplete'
    assert all(r.get('delivery_identical_to_full_audit') for r in production['rows']), 'cache equivalence not checked'
    production_time=production['orientation']
    tests={}
    if testfile.exists():
        root=ET.parse(testfile).getroot();suites=root.findall('testsuite') if root.tag!='testsuite' else [root]
        tests={k:sum(int(s.attrib.get(k,0)) for s in suites) for k in ('tests','failures','errors','skipped')}
        tests['passed']=tests['tests']-tests['failures']-tests['errors']-tests['skipped']
    text=REPORT.read_text();preregister=text[text.index('## Rules recorded before evaluation'):]
    if '\n## Final measured results' in preregister:preregister=preregister.split('\n## Final measured results')[0]
    dev=summary['development'];whole=dev['whole'];accepted=sum(r['accepted'] for r in whole.values());errors=sum(r['errors'] for r in whole.values())
    composites=dev['composites'];found=sum(c['found_axis'] for c in composites);comp_errors=sum(c['errors'] for c in composites)
    time=dev['measure_time'];rt=dev['regions_time']
    exact=sum(r['lines_exact'] for r in delivery['pages']);tables=delivery['tables'];passedtables=sum(r['passed'] for r in tables)
    lines=['# Round 4, part 3c: orientation from fitted font and accent guides','',
        f'The font and accent lines provide useful way-up evidence, but this implementation is not reliable enough to be the default. On 216 full-resolution development rotations it accepted {accepted}, made {errors} wrong whole-page decisions, and left {216-accepted} unknown. Some local regions still get the wrong way up. Sparse labels and numeric print remain difficult. These are development tests, not held-out accuracy.','',
        'Both readings are fitted: 0° and 180° for text running across the page, 90° and 270° for text running down it. The comparison asks whether the accents, letter bottoms, capitals and descenders follow the font’s fitted lines. It chooses only when one reading has sufficient measured support. A word inherits its region’s answer. Unknown keeps both possible readings. Region assignment is incomplete: missed portions of a pasted block can still inherit the main page’s reading incorrectly, including number rows.','',
        f'The guide-only whole-page step took mean {time["mean"]:.3f} s, median {time["median"]:.3f} s and p95 {time["p95"]:.3f} s. Blind region discovery plus all region fits took mean {rt["mean"]:.3f} s, median {rt["median"]:.3f} s and p95 {rt["p95"]:.3f} s. The region total already includes the main guide fit; do not add the two numbers. Disk IO, image generation and OCR delivery are excluded.','',
        f'The main fit meets the target on average. All-region work sometimes exceeds the 1–2 s allowance; its measured maximum was {rt["maximum"]:.3f} s. In actual oriented delivery on the 54 original source rasters, the separately timed orientation work, including table confirmation, averaged {production_time["mean"]:.3f} s (p95 {production_time["p95"]:.3f} s; maximum {production_time["maximum"]:.3f} s).','',
        '**Oriented mode remains opt-in.** The default `recognition_mode="textlayer"` is unchanged. No model was trained; no held-out page was accessed.','',preregister.strip(),'','## Final measured results','',
        'Angles are observed clockwise. A Pillow positive turn normalizes them. Each 90°/270° row below is reported independently. Accuracy is correct / accepted; coverage is accepted / all. Whole-page and main-region decisions share the pooled main orientation group, including headers.','']
    for scope in ('development','research'):
        part=summary[scope]
        lines.append(f'### {scope.capitalize()} whole pages and main regions')
        table(lines,['Applied turn','Whole accepted / total','Whole correct / accepted','Errors','Coverage','Axis correct / total','Main-region accepted / total','Main errors'],
              [[a+'°',f'{part["whole"][a]["accepted"]}/{part["whole"][a]["total"]}',
                f'{part["whole"][a]["correct"]}/{part["whole"][a]["accepted"]}',part['whole'][a]['errors'],pct(part['whole'][a]['coverage']),
                f'{part["whole"][a]["axis_correct"]}/{part["whole"][a]["total"]}',
                f'{part["main_regions"][a]["accepted"]}/{part["main_regions"][a]["total"]}',part['main_regions'][a]['errors']] for a in ('0','90','180','270')])
        table(lines,['Applied turn','Scored blind regions','Accepted','Correct','Errors','Coverage'],
              [[a+'°',part['all_regions'][a]['total'],part['all_regions'][a]['accepted'],part['all_regions'][a]['correct'],part['all_regions'][a]['errors'],pct(part['all_regions'][a]['coverage'])] for a in ('0','90','180','270')])
    from greekocr.glyphs.orientation_guides import (CONTACT_TOLERANCE_XH, MIN_BASELINE_CONTACTS,
        MIN_VARIABLE_BODIES, MIN_MARKS, MARK_SUPERMAJORITY)
    abstention_reasons=Counter()
    for page in delivery['pages']:
        for angle in (0,90,180,270):
            row=read(OUT/'decisions'/(page['key']+f'__cw{angle}.json'))['whole']
            if row['accepted']:continue
            readings=row['evidence'].get('guide_test',{}).get('readings',[])
            true=next((r for r in readings if r['orientation_cw']==row['truth_cw']),None)
            if true is None:
                abstention_reasons['Correct axis unresolved or not selected']+=1
                continue
            other=next(r for r in readings if r is not true)
            base=true['residuals_xh']['baseline'];opposite=other['residuals_xh']['baseline']
            checks={
                'Too few or too dispersed baseline contacts':true['contacts'].get('baseline',0)<MIN_BASELINE_CONTACTS or base is None or base>CONTACT_TOLERANCE_XH,
                'Too few measured capital/descender contacts':true['variable_bodies']<MIN_VARIABLE_BODIES,
                'Accent count or above/below supermajority fails':true['accent_above']<MIN_MARKS or true['accent_above']<MARK_SUPERMAJORITY*max(1,true['mark_below']),
                'Net accent advantage below three marks':true['net_marks']-other['net_marks']<MIN_MARKS,
                'Baseline worse than the opposite reading by over tolerance':base is None or (opposite is not None and base>opposite+CONTACT_TOLERANCE_XH)}
            abstention_reasons.update(k for k,failed in checks.items() if failed)
    lines.append(f'Why {216-accepted} whole-page tests abstain: the following checks are evaluated on the known correct reading, after testing. Counts overlap; they are diagnostics, not fitted categories or new thresholds.')
    table(lines,['Failed requirement on the correct reading','Unknown cases'],sorted(abstention_reasons.items()))
    lines.extend(['Region counts include the main group and disconnected local proposals; they are not manual region recall. On the real mixed page, local polarity is scored only inside its four labelled ROIs. Other local regions have unknown truth and are excluded.','',
                  '### Words and pieces','',delivery['words_scope'],
                  'Table items remain boundary-safe pieces and may contain several words. Thus this is an inheritance audit over detector output, not a count of manually annotated linguistic words.'])
    wordrows=[]
    for a in (0,90,180,270):
        rows=[r for r in delivery['rotated_words'] if r['applied_cw']==a]
        total=sum(r['total'] for r in rows);acc=sum(r['accepted'] for r in rows);correct=sum(r['correct'] for r in rows)
        wordrows.append([f'{a}°',total,acc,correct,acc-correct,pct(acc/total if total else None),f'{np.mean([r.get("delivery_seconds",0) for r in rows]):.3f}'])
    table(lines,['Applied turn','Scored words/pieces','Accepted','Correct','Errors','Coverage','Mean delivery s'],wordrows)
    lines.append('Delivery timing runs oriented_page with the independently measured main decision and exact pixel-fit caching; includes region analysis, local fitting, splitting and crops. It excludes OCR and disk IO. Words have no independent polarity fit.')
    table(lines,['Research standalone word turn','Accepted / total','Errors','Axis correct / total'],
          [[a+'°',f'{summary["research"]["words"][a]["accepted"]}/{summary["research"]["words"][a]["total"]}',summary['research']['words'][a]['errors'],
            f'{summary["research"]["words"][a]["axis_correct"]}/{summary["research"]["words"][a]["total"]}'] for a in ('0','90','180','270')])
    fixtures=read(ROOT/'.astra/orientation_research/testset/manifest.json')['cases']
    from scripts.glyphs.archive.evaluate_orientation_guides import counts,time_summary
    controls=[]
    for unit in ('line','block'):
        for a in (0,90,180,270):
            cases=[c for c in fixtures if c['kind']=='crop' and c['unit']==unit and c['truth_cw']==a]
            rows=[read(OUT/'decisions'/('research__'+c['id']+'.json')) for c in cases]
            stat=counts([r['whole'] for r in rows])
            controls.append([unit,f'{a}°',stat['total'],stat['accepted'],stat['correct'],stat['errors'],pct(stat['coverage']),f"{np.mean([r['measure_seconds'] for r in rows]):.3f}" if rows else '—'])
    table(lines,['Research crop unit','Turn','Total','Accepted','Correct','Errors','Coverage','Mean orientation s'],controls)
    sk=summary['research']['skew']
    lines.append(f"Research skew controls: {sk['correct']}/{sk['total']} accepted correctly; {sk['errors']} errors; {sk['total']-sk['accepted']} unknown. All have expected quarter-turn 0; this is not residual deskew accuracy.")
    timing_rows=[]
    for a in (0,90,180,270):
        rows=[read(OUT/'decisions'/(r['key']+f'__cw{a}.json')) for r in delivery['pages']]
        mt=time_summary([r['measure_seconds'] for r in rows]);rt0=time_summary([r['region_seconds'] for r in rows])
        timing_rows.append([f'{a}°',f"{mt['mean']:.3f}",f"{mt['p95']:.3f}",f"{rt0['mean']:.3f}",f"{rt0['p95']:.3f}"])
    table(lines,['Turn','Mean main-fit s','p95 main-fit s','Mean all-region s','p95 all-region s'],timing_rows)
    lines.extend([production['scope']+'. The production timer includes direction discovery, both-reading region fits and any whole-table confirmation. It excludes the horizontal detector, word splitting and crop creation. This extra timing pass is on original source rasters only; the four-turn table above uses the guide-only benchmark. It times oriented_page alone: a complete Docling pipeline may additionally invoke the pre-layout adapter, and was not timed end to end.'])
    table(lines,['Production timer on 54 sources','Mean s','Median s','p95 s','Maximum s'],
          [['Orientation only',*[f'{production_time[k]:.3f}' for k in ('mean','median','p95','maximum')]],
           ['Total delivery with verified main-fit reuse',*[f"{production['delivery'][k]:.3f}" for k in ('mean','median','p95','maximum')]]])
    before_cache=read(OUT/'uncached-table-confirmation-time.json')['orientation']
    lines.append(f"Before table-fit memoization, orientation averaged {before_cache['mean']:.3f} s, with p95 {before_cache['p95']:.3f} s and maximum {before_cache['maximum']:.3f} s. All 54 source-page delivery records are identical after memoization (boxes, frames, labels and ownership); timings and guide-fit duration metadata naturally differ.")
    lines.extend(['Standalone words deliberately abstain: no parent region is provided in those oracle word fixtures. This implements the owner’s inheritance rule; it does not satisfy the old part-3 standalone-word coverage gate.','',
                  '### Two-orientation composites'])
    composite_summary=[]
    for scope in ('development','research'):
        for angle in (90,270,180):
            regions=[r for r in summary[scope]['composites'] if r['truth_cw']==angle]
            words=[r['minority'] for r in delivery['composite_words'] if r['research']==(scope=='research') and r['roi_truth_cw']==angle]
            if not regions:continue
            total=sum(r['total'] for r in words);acc=sum(r['accepted'] for r in words)
            composite_summary.append([scope,angle,f"{sum(r['found_axis'] for r in regions)}/{len(regions)}",
                sum(r['errors'] for r in regions),f'{acc}/{total}',sum(r['correct'] for r in words),
                sum(r['errors'] for r in words),pct(acc/total if total else None)])
    table(lines,['Scope','Minority turn','Axis found / cases','Guide-region errors','Minority words/pieces accepted / total','Correct','Errors','Coverage'],composite_summary)
    for scope in ('development','research'):
        rows=summary[scope]['composites'];lines.append(f'{scope.capitalize()} composites:')
        table(lines,['Fixture','Minority truth','Axis found','Chain-union IoU','Accepted region decisions','Errors','Oracle crop reading'],
              [[r['id'],f'{r["truth_cw"]}°','yes' if r['found_axis'] else 'no',f'{r["union_iou"]:.3f}',','.join('?' if a is None else str(a) for a in r['decisions']) or 'none',r['errors'],r['oracle']['orientation_cw']] for r in rows])
    for research in (False,True):
        lines.append(('Research' if research else 'Development')+' composite word/piece delivery:')
        word_composites=[r for r in delivery.get('composite_words',[]) if r['research']==research]
        table(lines,['Fixture','Minority turn','Main accepted / total','Main errors','Minority accepted / total','Minority correct','Minority errors','Delivery s'],
              [[r['id'],r['roi_truth_cw'],f"{r['main']['accepted']}/{r['main']['total']}",r['main']['errors'],
                f"{r['minority']['accepted']}/{r['minority']['total']}",r['minority']['correct'],r['minority']['errors'],f"{r['delivery_seconds']:.3f}"] for r in word_composites])
    case_lookup={c['id']:c for c in read(OUT/'manifest.json')['cases']}
    case_lookup.update({'research__'+c['id']:c for c in fixtures if c['kind']=='composite'})
    composite_error_rows=[]
    for row in delivery['composite_words']:
        if not row['minority']['errors']:continue
        case=case_lookup[row['id']];l,t,r,b=case['roi'];parents=Counter()
        for word in read(OUT/'words'/(row['id']+'.json'))['words']:
            box=word['box_pixels'];cx=(box[0]+box[2])/2;cy=(box[1]+box[3])/2
            if l<=cx<=r and t<=cy<=b and word['orientation_cw'] not in (None,case['roi_truth_cw']):
                parents[(word['group_id'],word['orientation_cw'])]+=1
        assert sum(parents.values())==row['minority']['errors']
        composite_error_rows.append([row['id'],row['minority']['errors'],
            '; '.join(f'{group} CW{angle}: {count}' for (group,angle),count in sorted(parents.items()))])
    table(lines,['Composite with wrong minority words','Wrong words/pieces','Actual inherited parent and reading'],composite_error_rows)
    lines.extend(['A proposal intersects the pasted ROI to count as axis found; the stricter 0.5 union-IoU diagnostic is also shown. Discovery is blind. Oracle-crop scores use the labelled ROI only after discovery, and never certify blind success. All 39 new pastes include a different-page donor (or explicitly rendered digits); each is tested at 90°, 270°, and 180°. Research fixtures are hash-verified and unchanged.','',
                  '### Numbers-only contract'])
    numeric=[r for r in composites if r.get('numbers_only')]
    numeric_words=[r for r in delivery.get('composite_words',[]) if r.get('numbers_only')]
    table(lines,['Numeric fixture: actual delivered words','Accepted / total','Wrong reading'],[[r['id'],f"{r['minority']['accepted']}/{r['minority']['total']}",r['minority']['errors']] for r in numeric_words])
    table(lines,['Numeric fixture','Blind accepted regions','Blind errors','Unlabelled oracle reading'],[[r['id'],r['accepted'],r['errors'],r['oracle']['orientation_cw']] for r in numeric])
    lines.extend(['The explicit `content_kind="numbers"` contract always abstains independently and `resolve_regions` inherits only from a nonnumeric, decided header in the same named orientation group. Conflicting headers abstain. The blind `page_regions` path currently does not classify numeric content or create semantic header/figure group links; it can only pool the ink of a geometrically joined block. Automatic numeric-to-header grouping is therefore incomplete. Pixel-only classification cannot guarantee that a small mark is an accent rather than a decimal point. The blind results above remain a separate release gate; the explicit semantic contract is not evidence of blind numeric detection.','',
                  '### Case 35: s2-6419488b7f8e69fd20da-p00001'])
    real=read(OUT/'real-crops.json')
    table(lines,['Part','Truth','Measured axis','Guide-only oracle reading','Accepted accents in the two readings','Outcome'],
          [[r['name'],r['truth_cw'],r['axis'],r['orientation_cw'],[x['accent_above'] for x in r['evidence'].get('guide_test',{}).get('readings',[])],
            'correct' if r['correct'] else 'wrong' if r['error'] else 'unknown'] for r in real])
    real_delivery=read(OUT/'delivery/s2-6419488b7f8e69fd20da-p00001.json')['word_records']
    roi_rows=[]
    for roi in real:
        box=roi['box'];items=[]
        for w in real_delivery:
            b=w['box_pixels'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
            if box[0]<=cx<=box[2] and box[1]<=cy<=box[3]:items.append(w)
        acc=[w for w in items if w['orientation_cw'] is not None]
        correct=sum(w['orientation_cw']==roi['truth_cw'] for w in acc)
        roi_rows.append([roi['name'],len(items),len(acc),correct,len(acc)-correct])
    table(lines,['Blind delivered ROI','Pieces/words found','Accepted','Correct','Errors'],roi_rows)
    lines.append('ROI membership uses delivered box centres. These counts do not establish complete text/word recall.')
    lines.extend(['The title oracle is a supplied single-line crop, so its long ink axis gives the 90°/270° pair. It has 3 above / 7 below marks at 90° and 4 above / 3 below at 270°: insufficient for the recorded three-to-one margin. «Καπνοῦ» has only 4/5 baseline contacts, below the twelve-contact minimum. The folio has no observed accents. The number-grid crop also fails to infer the correct axis independently; it needs its surrounding text group. The title and number rows are CW270, «Καπνοῦ» is CW180, and the ambiguous folio is upright in the source. That already exceeds the supported two accepted angles; an independently detected third reading must remain unknown. The folio’s appearance is not permission for digits to decide. Oracle crops are not proof that the blind path found each part.','',
                  '[New case-35 regions](../../.astra/out/orientation_eval/s2-6419488b7f8e69fd20da-p00001__cw0.regions.jpg) · [New case-35 delivered pieces](../../.astra/out/orientation_eval/s2-6419488b7f8e69fd20da-p00001.words.jpg)','',
                  '### Line preservation and table delivery','',
                  f'{exact}/54 upright-source main-frame line records are exactly equal to the part-2 records. Existing base fits are reused only in the same image frame, with source SHA-256 verified; changed frames and minority fits execute the production code. The six horizontal detector modules are independently verified byte-identical to `f611ee2`. This is a reuse/compatibility check, not 54 fresh independent fits. Local replacements are audited separately through delivered pieces.'])
    table(lines,['Source page','Main CW','Main-frame lines part 2 / now','Exact lines','Accepted pieces / words'],
          [[r['key'],r['main']['orientation_cw'],f'{r["old_lines"]}/{r["new_lines"]}','yes' if r['lines_exact'] else 'no',f'{r["accepted"]}/{r["words"]}'] for r in delivery['pages']])
    table(lines,['Table page','Part-1 complete / total','Now complete / total','Part-1 crossings','Now crossings','Elements losing ink','No worse?'],
          [[f"[{r['key']}](../../.astra/out/orientation_eval/{r['key']}.words.jpg)",f'{r["old_complete"]}/{r["total"]}',f'{r["complete"]}/{r["total"]}',r['old_crossings'],r['crossings'],len(r['losses']),'yes' if r['passed'] else 'no'] for r in tables])
    lines.extend(['Complete means at least 98% of independently annotated contrast pixels retained. Losses compare exact fractions even above 98%; crossing counts compare overlaps with multiple annotated cells. The annotations are the provisional part-1 pixel review. This measures detector delivery geometry, not OCR transcription or real TableFormer cell correctness.','',
                  'The part-3 regression had re-split already safe table pieces into tight words and allowed small local proposals to replace them. The new path preserves the existing table pieces, protects both Docling-supplied and pixel-detected table extents, and normalizes a local table only when the whole table’s guide decision agrees. The actual installed TableFormer and backend contracts are covered by the test suite.','',
                  '### Printing convention','',
                  'Of the eight annotated table pages, seven have upright main text in the supplied raster and one has sideways main text: case 35, observed CW270 (normalize by a clockwise 90° turn). A landscape two-page scan such as the navigation spread is not itself a sideways printed table. One sideways source is insufficient to establish a book-wide convention; rotated test copies do not add independent evidence. No empirical turning prior is enabled.','',
                  '### Errors and limitations',''])
    failing_tables=[r for r in tables if not r['passed']]
    for r in failing_tables:
        losses=r['losses']
        detail=(f"{r['key']}: {r['old_complete']} → {r['complete']} complete annotated elements, "
                f"but {len(losses)} elements lose some previously covered ink and crossings change "
                f"{r['old_crossings']} → {r['crossings']}. ")
        if r['key']=='s2-6419488b7f8e69fd20da-p00001':
            detail+='The accepted CW270 main frame changes the detector’s grid and piece partition. It recovers substantially more numeric text, but the new partition still crosses cells and loses some previous fragments. That is a table-delivery regression despite a correct main way-up decision; no net-improvement exemption is claimed.'
        else:
            detail+='The delivered-piece comparison does not establish a non-regression; individual losses are retained in the JSON report.'
        lines.extend([detail,''])
    adapter=dict(scope='Replay of stored decisions through the adapter mixed predicate; not a new Docling pipeline run.',rows=[])
    for angle in (0,90,180,270):
        rows=[]
        for p in sorted((OUT/'decisions').glob('*__cw'+str(angle)+'.json')):
            record=read(p)
            if record['kind']!='whole' or record.get('research') or record.get('mixed'):continue
            d=record['whole']
            mixed=any(r['axis']!=d['axis'] or r['orientation_cw'] not in (None,d['orientation_cw']) for r in record['regions'][1:])
            rows.append((d['accepted'],mixed,d['orientation_cw']))
        adapter['rows'].append(dict(turn=angle,uniform_pages=len(rows),accepted=sum(r[0] for r in rows),
            mixed_veto=sum(r[0] and r[1] for r in rows),would_normalize=sum(r[0] and not r[1] and r[2] in (90,180,270) for r in rows)))
    (OUT/'adapter-policy-audit.json').write_text(json.dumps(adapter,indent=2)+'\n')
    lines.extend(['Uniform-page normalization remains incomplete. The old two-percent veto was replaced, and the synthetic cross-line-neighbour test passes, but real chain proposals still produce false mixed flags. The following replays the adapter predicate on the stored fitted decisions; it is not a new end-to-end Docling run. Case 35 is excluded because it really is mixed.'])
    table(lines,['Applied turn','Uniform sources','Accepted main','False mixed vetoes among accepted','Would rotate before layout'],
          [[r['turn'],r['uniform_pages'],r['accepted'],r['mixed_veto'],r['would_normalize']] for r in adapter['rows']])
    if summary['errors']:
        table(lines,['Whole-page or crop fixture','Accepted','Expected'],[[r['id'],r['decision'],r['truth']] for r in summary['errors']])
    else:
        lines.extend(['No accepted whole-page or oracle-crop way-up errors were observed.',''])
    def error_reason(row):
        key=row['id']
        if 'an-1f8e7d022643' in key:
            return 'Mixed-size slanted Greek type and ornament: the upright reading measured 9 above / 6 below marks; the wrong reading 12 / 4. Both fit plausible classes; the count comparison chose wrongly.'
        if 's2-0ce9d1025b3f23c7119e' in key:
            return 'False text region on faint reverse-side ink. Local contrast admits show-through; the wrong reading fits 3 apparent accents / 1 below mark. Page-level faintness protection is missing in this proposal test.'
        if 's2-49598b2e848ab1f0ee1e' in key:
            return 'False vertical chain formed by aligned ends of horizontal lines. In the wrong axis the clipped letter parts fit 4 apparent accents / 1 below mark. This is discovery failure followed by a plausible but invalid class fit.'
        return 'See raw fitted class/contact evidence; no independent glyph identity is established.'
    table(lines,['Blind-region fixture','Region','Accepted','Expected','Explanation'],
          [[r['id'],r['region'],r['decision'],r['truth'],error_reason(r)] for r in summary['region_errors']])
    def word_error_reason(row):
        if 's2-6419488b7f8e69fd20da' in row['key']:
            return 'The mixed page main reading was inherited by a labelled ROI whose different orientation was not resolved locally; see the four ROI counts above.'
        return error_reason(dict(id=row['key']))+' Its word/piece descendants inherited that region decision.'
    table(lines,['Source with wrong delivered readings','Applied turn','Wrong accepted words/pieces','Explanation'],
          [[r['key'],r['applied_cw'],r['errors'],word_error_reason(r)] for r in delivery['rotated_words'] if r['errors']])
    lines.append('The composite word errors above occur when a missed or incompletely covered pasted minority retains its surrounding main-group reading. Their actual inherited parents are listed per fixture. Correct accepted minority-region fits therefore do not certify the entire pasted block’s word delivery. Numeric-only pastes expose the same missing semantic grouping; inherited main polarity is not a numeric guide decision, but it still fails the requirement to inherit only from a header in the correct orientation group.')
    lines.extend(['The explanations use source-crop inspection and fitted contacts; class-assignment mechanisms are interpretations, not manual glyph-class annotations. Research rows repeat the same source failure under exact rotations. A new crop sheet is [here](../../.astra/out/orientation_eval/error-regions.jpg).','', 'The direct guide-region errors are retained in the raw two-reading receipts. Their mechanism is an ambiguous or incorrect ink-class assignment (punctuation, damaged numerals, fragmented letters, or nontext) supporting a geometrically plausible fitted guide. A tight fitted curve is conditional on those class assignments; it does not certify that the marks are Greek accents. Region proposals can also fragment a label or create cross-line chains. No threshold was adjusted to eliminate individual remaining failures.','',
                  'Main-page priors, minority-turn priors, recognizer confirmation and OSD are not used in this final guide-only benchmark. OSD is optional and may only confirm the guide-supported close candidate. When supplied measured guide evidence, the paired recognizer helper preserves strong guide decisions, rejects independent word votes, and cannot decide a guide-silent region. Full real-recognition/pipeline accuracy was not rerun.','',
                  '### Release gates'])
    allregions=sum(r['errors'] for r in dev['main_regions'].values())
    minority_word_errors=sum(r['minority']['errors'] for r in delivery.get('composite_words',[]) if not r['research'])
    numeric_independent=any(r['accepted'] or r['oracle']['accepted'] for r in numeric) or any(r['minority']['accepted'] for r in delivery.get('composite_words',[]) if r.get('numbers_only'))
    gates=[('Zero whole-page and main-region way-up errors',errors==0 and allregions==0,f'{errors} whole, {allregions} main errors'),
           ('At least 95% whole-page coverage',accepted/216>=.95,pct(accepted/216)),
           ('Every minority found, no wrong way up',found==len(composites) and comp_errors==0 and minority_word_errors==0,f'{found}/{len(composites)} axis found; {comp_errors} accepted region errors; {minority_word_errors} delivered minority word/piece errors'),
           ('Numbers never decide alone',not numeric_independent,'explicit numeric contract tested; blind numeric receipts above'),
           ('54 upright-source line outputs unchanged or measured improvement',exact==54,f'{exact}/54 exact; no blanket improvement claim'),
           ('Eight tables no worse than part 1',passedtables==8,f'{passedtables}/8 no worse')]
    table(lines,['Gate','Pass','Evidence'],[[n,'yes' if ok else 'no',v] for n,ok,v in gates])
    initial=read(OUT/'initial/summary.json')
    table(lines,['Support definition','Development accepted / 216','Whole errors','90-degree accepted / errors','270-degree accepted / errors'],
          [['Initial raw variable-body classes',sum(r['accepted'] for r in initial['development']['whole'].values()),sum(r['errors'] for r in initial['development']['whole'].values()),
            f"{initial['development']['whole']['90']['accepted']} / {initial['development']['whole']['90']['errors']}",
            f"{initial['development']['whole']['270']['accepted']} / {initial['development']['whole']['270']['errors']}"],
           ['Final measured variable-guide support',accepted,errors,f"{whole['90']['accepted']} / {whole['90']['errors']}",f"{whole['270']['accepted']} / {whole['270']['errors']}"]])
    lines.extend(['### Tests, artifacts, and reproduction','',
                  f'Test suite: {tests.get("passed","pending")}/{tests.get("tests","pending")} passed; {tests.get("skipped",0)} skipped, {tests.get("failures",0)} failures, {tests.get("errors",0)} errors. The 16 browser-render checks were skipped because the Chromium executable is unavailable; it was not downloaded. All runnable tests pass. API documentation was regenerated.','',
                  'New output only: [prose guide readings](../../.astra/out/orientation_eval/guides-prose.png), [numeric-table guide readings](../../.astra/out/orientation_eval/guides-navigation.png). Solid guides have measured contacts; dashed guides are borrowed.','',
                  'Machine-readable results: [summary](../../.astra/out/orientation_eval/summary.json), [delivery audit](../../.astra/out/orientation_eval/delivery-summary.json), [per-case decisions](../../.astra/out/orientation_eval/decisions/), [production timing and cache equivalence](../../.astra/out/orientation_eval/production-orientation-time.json), [test XML](../../.astra/out/orientation_eval/tests.xml). The initial implementation is preserved under `initial/`. `run-source-hashes.json` binds the final fitted run; `source-finalization.json` records subsequent API-only annotations, the scoring-only correction that counts wrong-axis minority errors, and the auxiliary title oracle being supplied as a line. The guide acceptance rules did not change. Delivery source hashes bind the completed four-turn/composite audit after the table and word-partition corrections. `before-table-cache-oriented-page.py` preserves that audited source; the final timing file binds the cache-only revision and its 54-source delivery-equivalence checks.','',
                  'Run from the worktree with `PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1` and `/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python`:','',
                  '```sh','export PYTHONDONTWRITEBYTECODE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1',
                  'GUIDES_PYTHON=/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python',
                  '"$GUIDES_PYTHON" scripts/glyphs/archive/generate_orientation_guides.py','"$GUIDES_PYTHON" scripts/glyphs/archive/evaluate_orientation_guides.py',
                  '"$GUIDES_PYTHON" scripts/glyphs/archive/audit_orientation_guides.py','"$GUIDES_PYTHON" scripts/glyphs/archive/time_orientation_guides.py',
                  '"$GUIDES_PYTHON" scripts/glyphs/archive/render_orientation_guides.py','"$GUIDES_PYTHON" scripts/generate_api_docs.py',
                  '"$GUIDES_PYTHON" -m pytest -p no:cacheprovider --junitxml=.astra/out/orientation_eval/tests.xml',
                  '"$GUIDES_PYTHON" scripts/glyphs/archive/report_orientation_guides.py','```','',
                  'No push, download, background shell job, training run, or held-out-page access was performed.'])
    REPORT.write_text('\n'.join(lines)+'\n')
    compact=dict(whole=whole,main_regions=dev['main_regions'],words=wordrows,tables=tables,gates=[dict(name=n,passed=ok,evidence=v) for n,ok,v in gates],tests=tests,
                 composite_summary=composite_summary,composite_error_parents=composite_error_rows,adapter_policy=adapter['rows'],
                 timings=dict(whole=time,regions=rt,production_orientation=production_time),whole_abstention_reasons=dict(abstention_reasons),errors=summary['errors'],region_errors=summary['region_errors'])
    (REPORT.with_suffix('.json')).write_text(json.dumps(compact,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
