"""Compare every round-3 check and validate all 54 delivered artifact sets.

The archived checks supply evaluation references, never detector inputs.
Writes a compact metric comparison plus exact nested-check differences.
"""
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

# These are our own fixed-scale contact sheets, not uploaded compressed input.
# Image.verify() validates their streams without allocating the full raster.
Image.MAX_IMAGE_PIXELS = 500_000_000

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'.astra/out'
OLD=ROOT/'.astra/previous_round3'


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(c,lines):
    checks=c['checks']
    res=[v['p90'] for l in lines if l['discounted'] is None
         for v in l['guide_residuals'].values() if v['p90'] is not None]
    d={k:c[k] for k in ('cut_ink_lines','foreign_ink_lines','rule_gutter_crossings',
       'boundary_overlaps','broken_line_pairs','strip_edge_touch_lines',
       'source_boundary_cut_lines','unassigned_body_components')}
    d.update(guide_p90_median=float(np.median(res)) if res else 0,
      borrowed_lines=checks['1_font_and_accent_lines']['borrowed_lines'],
      no_body_lines=len(checks['2_extra_lines']['no_body_lines']),
      close_pairs=len(checks['2_extra_lines']['close_pairs']),
      maximum_jump=checks['5_smoothness']['maximum'],
      unassigned_text_size_components=checks['7_missed_text']['unassigned_text_size_components'],
      unassigned_text_size_ink=checks['7_missed_text']['unassigned_text_size_ink'],
      graphic_lines=len(checks['8_nontext_ink']['candidate_lines_on_detected_graphics']),
      graphic_segments=len(checks['8_nontext_ink'].get('candidate_segments_on_detected_graphics',[])),
      review_crossings=len(checks['6_column_crossings'].get('review_crossing_lines',[])),
      seam_gaps=len(checks['10_existing_checks'].get('seam_gaps',[])),
      lost_assigned_ink_fraction=1-c['assigned_ink_retained_fraction'],
      invalid_boundaries=len(c['invalid_boundary_lines']))
    return d


def differences(a,b,path=''):
    if isinstance(a,dict) and isinstance(b,dict):
        out=[]
        for key in sorted(a.keys()|b.keys()):
            if key not in a or key not in b:out.append(dict(path=path+'/'+key,old=a.get(key),new=b.get(key)))
            else:out.extend(differences(a[key],b[key],path+'/'+key))
        return out
    if a==b:return []
    if isinstance(a,list) and isinstance(b,list):
        # Preserve exact mismatching check paths without duplicating megabytes
        # of per-pixel arrays. Bound checks files remain the source records.
        return [dict(path=path,old_count=len(a),new_count=len(b),
                     old_sha256=hashlib.sha256(json.dumps(a,sort_keys=True).encode()).hexdigest(),
                     new_sha256=hashlib.sha256(json.dumps(b,sort_keys=True).encode()).hexdigest())]
    return [dict(path=path,old=a,new=b)]


def case_image(number,panels):
    images=[]
    for key,box in panels:
        im=Image.open(OUT/f'{key}.lines.jpg').convert('RGB')
        if box:im=im.crop(box)
        im.thumbnail((1500,1750))
        images.append((key,im))
    canvas=Image.new('RGB',(sum(im.width for _,im in images),max(im.height for _,im in images)+55),'white')
    draw=ImageDraw.Draw(canvas);x=0
    for key,im in images:
        draw.text((x+8,8),f'Case {number} | NEW round-4 output | {key}',fill='black')
        draw.text((x+8,27),'Active pieces only. Discounted candidates remain in JSON.',fill='black')
        canvas.paste(im,(x,55));x+=im.width
    (OUT/'cases').mkdir(exist_ok=True)
    canvas.save(OUT/'cases'/f'case-{number}.jpg',quality=95)


def main():
    pages=sorted((ROOT/'.astra/pages').glob('*.png'));assert len(pages)==54
    tables={p.stem for p in (ROOT/'docs/tables/annotations').glob('*.json')}
    rows=[];failures=[]
    for page in pages:
        key=page.stem
        old=read(OLD/f'{key}.checks.json');new=read(OUT/f'{key}.checks.json')
        previous_lines=read(OLD/f'{key}.lines.json');lines=read(OUT/f'{key}.lines.json')
        segments=read(OUT/f'{key}.segments.json');cells=read(OUT/f'{key}.cells.json')
        # Repeat round 3's check-8 supplement and its manually supplied check-6
        # references. The reference is read from the baseline, not invented here.
        graphics=new['checks']['8_nontext_ink']['detected_graphics']
        hits=[i for i,s in enumerate(segments) if any(
            max(s['box'][0],g[0])<min(s['box'][2],g[2]) and
            max(s['box'][1],g[1])<min(s['box'][3],g[3]) for g in graphics)]
        new['checks']['8_nontext_ink'].update(candidate_segments_on_detected_graphics=hits,
          segment_measurement='Rough bounding-box intersection with detected graphic boxes; not semantic ground truth.')
        ref=old['checks']['6_column_crossings'].get('review_reference_x')
        if ref is not None:
            new['checks']['6_column_crossings'].update(review_reference_x=ref,
              review_reference=old['checks']['6_column_crossings']['review_reference'],
              review_crossing_lines=[i for i,l in enumerate(lines) if l['discounted'] is None and
                                    l['x0']<ref-.75*l['xheight'] and l['x1']>ref+.75*l['xheight']])
        new['review_supplement_sha256']=sha(Path(__file__))
        (OUT/f'{key}.checks.json').write_text(json.dumps(new,indent=2)+'\n')
        assert sha(page)==new['source_sha256']==old['source_sha256']
        w,h=Image.open(page).size
        for ext in ('lines.jpg','unrolled.jpg'):
            with Image.open(OUT/f'{key}.{ext}') as im:im.verify()
        seen=set()
        for c in cells['cells']:
            assert c['index'] not in seen;seen.add(c['index'])
            assert c['coord_origin']=='TOPLEFT'
            a,t,b,bot=c['box_pixels'];assert 0<=a<b<=w and 0<=t<bot<=h
            assert all(math.isfinite(v) for v in c['box_page'])
            assert np.allclose(c['box_page'],np.array(c['box_pixels'])/3)
            assert 0<=c['line_index']<len(lines) and lines[c['line_index']]['discounted'] is None
        assert len(cells['cells'])==new['active_lines']
        for line in lines:
            for curve in ('top','bottom','baseline','meanline','font_top','font_bottom','accent_top','accent_bottom'):
                assert len(line[curve])==line['x1']-line['x0'] and np.isfinite(line[curve]).all()
        before=metrics(old,previous_lines);after=metrics(new,lines)
        worse={k:dict(old=before[k],new=after[k]) for k in before if after[k]>before[k]+1e-10}
        row=dict(key=key,table_page=key in tables,
          active=dict(old=old['active_lines'],new=new['active_lines']),
          discounted=dict(old=old['discounted_lines'],new=new['discounted_lines']),
          metrics=dict(old=before,new=after),worse=worse,
          exact_lines_equal=previous_lines==lines,
          check_differences=differences(old['checks'],new['checks']),
          cells=len(cells['cells']),
          receipts={str(p.relative_to(ROOT)):sha(p) for p in [page,OLD/f'{key}.checks.json',OUT/f'{key}.checks.json',OUT/f'{key}.cells.json']})
        rows.append(row)
        if key not in tables and (worse or previous_lines!=lines):failures.append(key)
    records=[read(OUT/f'{p.stem}.checks.json') for p in pages]
    (OUT/'checks.json').write_text(json.dumps(records,indent=2)+'\n')
    result=dict(pages=54,non_table_pages=46,non_table_regressions=failures,
                any_worse_pages=[r['key'] for r in rows if r['worse']],rows=rows)
    (OUT/'regression.json').write_text(json.dumps(result,indent=2)+'\n')
    case_image(28,[('s2-831443dc5e6f1ccfbaf5-p00020',(40,920,3300,3810))])
    case_image(33,[('an-7a2b17a3fb0f-p000200',(690,135,3220,2130))])
    case_image(34,[('an-a3c2bdf81256-p000112',None),('s2-80513ae109b4f749ca58-p00003',None)])
    print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
    assert not failures,'Non-table regression: '+', '.join(failures)


if __name__=='__main__':main()
