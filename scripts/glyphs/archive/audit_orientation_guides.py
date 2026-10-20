"""Audit actual oriented delivery against part-2 lines and part-1 table ink.

Only byte-identical upright base fits are reused. Minority fits and changed
frames execute the production code. Timing here is delivery, not orientation.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
from greekocr.ops.data_root import input_path as _data_input
import greekocr.glyphs.oriented_page as oriented_module
from greekocr.glyphs.oriented_page import oriented_page
from greekocr.glyphs.orientation import Orientation,QuarterTurn,measure_orientation
from scripts.glyphs.archive.render_orientation_round4 import load_baseline,draw_words
from scripts.glyphs.archive.evaluate_orientation_guides import save,counts,time_summary,decision_row
from scripts.glyphs.archive.report_orientation_round4 import element_coverages
from scripts.glyphs.archive.evaluate_tables_round4 import geometry

OUT=ROOT/'.astra/out/orientation_eval'
OLD=ROOT/'.astra/previous_round4_part2'


def read(path):return json.loads(_data_input(path).read_text())
def sha(path):return hashlib.sha256(_data_input(path).read_bytes()).hexdigest()


def compact_word(w,image):
    corners=w.frame.rectangle(w.box);box=[*corners.min(0),*corners.max(0)]
    return dict(index=w.index,group_id=w.group_id,line_index=w.line_index,box_pixels=box,
                corners_pixels=corners.tolist(),box_page=(np.array(box)/3).tolist(),coord_origin='TOPLEFT',orientation_cw=w.orientation.orientation_cw,
                axis=w.orientation.axis,alternatives=w.orientation.alternatives,
                table_id=w.table_id,cell_id=w.cell_id,inherited_from=w.orientation.evidence.get('inherited_from'),
                geometry_orientation_cw=w.frame.orientation_cw,
                geometry_is_hypothesis=w.orientation.orientation_cw is None)


def audit(out):
    save(out/'delivery-source-hashes.json', {str(p.relative_to(ROOT)):sha(p) for p in
        [ROOT/'greekocr/glyphs/oriented_page.py', ROOT/'greekocr/glyphs/orientation.py',
         ROOT/'greekocr/glyphs/orientation_guides.py', ROOT/'greekocr/glyphs/orientation_regions.py', Path(__file__)]})
    pages=[];tables=[];rotated=[]
    original_fit=oriented_module._fit_group
    cache={};cache_stats=Counter()
    def cache_key(image,frame,regions):
        local=frame.image(image)
        mapped=[]
        for tid,box in regions:
            pts=frame.rectangle(box,inverse=False)
            mapped.append((tid,tuple(np.round(np.r_[pts.min(0),pts.max(0)],6))))
        return (local.size,hashlib.sha256(local.tobytes()).hexdigest(),tuple(mapped))
    def cached_fit(image,frame,decision,gid,regions,start,*,segmentation=None,pieces=None):
        key=cache_key(image,frame,regions)
        if key in cache:
            segmentation,pieces=cache[key];cache_stats['hits']+=1
        elif segmentation is not None:
            cache_stats['verified_part2_reuse']+=1
        else:
            cache_stats['fresh_fits']+=1
        result=original_fit(image,frame,decision,gid,regions,start,segmentation=segmentation,pieces=pieces)
        cache[key]=(result[1],result[2])
        return result
    oriented_module._fit_group=cached_fit
    for path in sorted((ROOT/'.astra/pages').glob('*.png')):
        cache.clear()
        print('START',path.stem,flush=True)
        key=path.stem;image=Image.open(path).convert('L');base,pieces=load_baseline(OLD,key)
        assert read(OLD/f'{key}.checks.json')['source_sha256']==sha(path)
        layout=read(ROOT/'.astra/layout'/f'{key}.json')
        regions=[(str(c['id']),[v*3 for v in c['box']]) for c in layout['retained']]
        cache[cache_key(image,QuarterTurn(*image.size,0),regions)]=(base,pieces)
        decision_path=out/'decisions'/f'{key}__cw0.json'
        record=read(decision_path)['whole'] if decision_path.exists() else measure_orientation(image,unit='page').to_record()
        dominant=Orientation(**{k:record[k] for k in Orientation.__dataclass_fields__})
        start=perf_counter();result=oriented_page(image,regions,dominant=dominant,use_osd=False,segmentation=base,pieces=pieces)
        seconds=perf_counter()-start
        words=[compact_word(w,image) for w in result.words]
        assert all(w['orientation_cw'] in (None,w['geometry_orientation_cw']) for w in words), 'accepted reading and crop frame disagree'
        oldlines=read(OLD/f'{key}.lines.json');newlines=[l.to_record() for l in result.segmentation.lines]
        same=oldlines==newlines
        row=dict(key=key,source_sha256=sha(path),lines_exact=same,base_fit_reused=result.segmentation is base,
                 old_lines=len(oldlines),new_lines=len(newlines),main=result.dominant.to_record(),
                 groups=result.groups,words=len(words),accepted=sum(w['orientation_cw'] is not None for w in words),
                 delivery_seconds=seconds,
                 table_pieces_before=sum(p.table_id is not None for p in pieces),
                 table_pieces_after=sum(w['table_id'] is not None for w in words))
        save(out/'delivery'/f'{key}.json',dict(**row,word_records=words))
        draw_words(image,dict(image_size=image.size,words=words),out/(key+'.words.jpg'))
        pages.append(row)
        annotation=ROOT/'docs/records/tables/annotations'/f'{key}.json'
        if annotation.exists():
            ann=read(annotation);gray=np.asarray(image);bg=ndi.maximum_filter(gray,size=max(3,round(.015*min(gray.shape))))
            ink=bg.astype(float)-gray>30
            oldcells=read(ROOT/'.astra/previous_round4_part1'/f'{key}.cells.json')['cells']
            previous=element_coverages(ann,oldcells,ink);current=element_coverages(ann,words,ink)
            before={(r['table'],r['cell'],r['element']):r['coverage'] for r in previous}
            losses=[dict(**r,old_coverage=before[(r['table'],r['cell'],r['element'])]) for r in current if r['coverage']<before[(r['table'],r['cell'],r['element'])]-1e-10]
            oldgeo=geometry(ann,oldcells,image);newgeo=geometry(ann,words,image)
            tab=dict(key=key,old_complete=sum(r['coverage']>=.98 for r in previous),
                     complete=sum(r['coverage']>=.98 for r in current),total=len(current),
                     old_crossings=len(oldgeo['crossing_pieces']),crossings=len(newgeo['crossing_pieces']),
                     losses=losses,passed=not losses and len(newgeo['crossing_pieces'])<=len(oldgeo['crossing_pieces']))
            tables.append(tab);save(out/'tables'/f'{key}.json',tab)
        # Run actual production delivery on each rotated raster. Reuse only
        # byte-identical normalized pixels and matching transformed table boxes.
        for a in (0,90,180,270):
            print('TURN',key,a,flush=True)
            measured=read(out/'decisions'/f'{key}__cw{a}.json')
            im_a=image.rotate(-a,expand=True);outer=QuarterTurn(*im_a.size,a)
            turn_started=perf_counter()
            if a==0:
                turned=result
            else:
                transformed=[]
                for tid,box in regions:
                    pts=outer.rectangle(box)
                    transformed.append((tid,[*pts.min(0),*pts.max(0)]))
                d=Orientation(**{k:measured['whole'][k] for k in Orientation.__dataclass_fields__})
                turned=oriented_page(im_a,transformed,dominant=d,use_osd=False)
            turn_seconds=seconds if a==0 else perf_counter()-turn_started
            records=[compact_word(w,im_a) for w in turned.words]
            assert all(w['orientation_cw'] in (None,w['geometry_orientation_cw']) for w in records)
            word_rows=[]
            for w in records:
                source_points=outer.points(w['corners_pixels']);sc=source_points.mean(0)
                truth=a
                if key=='s2-6419488b7f8e69fd20da-p00001':
                    truth=None
                    for box,angle in [([180,487,320,1907],270),([1270,3922,1530,4037],180),([1610,187,1810,297],0),([1710,390,2390,1180],270)]:
                        if box[0]<=sc[0]<=box[2] and box[1]<=sc[1]<=box[3]:truth=(angle+a)%360
                    if truth is None:continue
                known=w['orientation_cw']
                word_rows.append(dict(accepted=known is not None,correct=known==truth,error=known is not None and known!=truth,
                                      axis_correct=w['axis']==('vertical' if truth%180 else 'horizontal')))
            rotated.append(dict(key=key,applied_cw=a,delivery_seconds=turn_seconds,**counts(word_rows)))
            save(out/'words'/f'{key}__cw{a}.json',dict(image_size=im_a.size,groups=turned.groups,words=records))
        save(out/'delivery-summary.json',dict(pages=pages,tables=tables,rotated_words=rotated,
             fit_cache=dict(cache_stats),words_scope='Actual oriented_page delivery on all 216 rotated rasters, with exact normalized-pixel fit caching. Word/piece polarity truth by source orientation; case 35 only labelled ROIs. Not word-detection recall.'))
        print('AUDIT',key,'same',same,'words',len(words),'seconds',round(seconds,2),flush=True)
    composite_rows=[]
    cases=[c for c in read(out/'manifest.json')['cases'] if c['kind']=='composite']
    research=ROOT/'.astra/orientation_research'
    cases += [{**c,'id':'research__'+c['id'],'research':True,'path':str((research/c['path']).relative_to(ROOT))}
              for c in read(research/'testset/manifest.json')['cases'] if c['kind']=='composite']
    for case in cases:
        cache.clear();print('COMPOSITE',case['id'],flush=True)
        image=Image.open(ROOT/case['path']).convert('L')
        measured=read(out/'decisions'/(case['id']+'.json'))['whole']
        dominant=Orientation(**{k:measured[k] for k in Orientation.__dataclass_fields__})
        start=perf_counter();result=oriented_page(image,dominant=dominant,use_osd=False)
        elapsed=perf_counter()-start
        records=[compact_word(w,image) for w in result.words]
        assert all(w['orientation_cw'] in (None,w['geometry_orientation_cw']) for w in records)
        scored={'main':[],'minority':[]};roi=case['roi']
        for word in records:
            b=word['box_pixels'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2
            where='minority' if roi[0]<=cx<=roi[2] and roi[1]<=cy<=roi[3] else 'main'
            truth=case['roi_truth_cw'] if where=='minority' else case['truth_cw']
            angle=word['orientation_cw']
            scored[where].append(dict(accepted=angle is not None,correct=angle==truth,error=angle is not None and angle!=truth,
                                      axis_correct=word['axis']==('vertical' if truth%180 else 'horizontal')))
        row=dict(id=case['id'],research=case.get('research',False),roi_truth_cw=case['roi_truth_cw'],
                 numbers_only=case.get('numbers_only',False),delivery_seconds=elapsed,
                 main=counts(scored['main']),minority=counts(scored['minority']))
        composite_rows.append(row)
        save(out/'words'/(case['id']+'.json'),dict(**row,image_size=image.size,groups=result.groups,words=records))
        draw_words(image,dict(image_size=image.size,words=records),out/(case['id']+'.words.jpg'))
        summary=read(out/'delivery-summary.json');summary.update(composite_words=composite_rows,fit_cache=dict(cache_stats))
        save(out/'delivery-summary.json',summary)
    oriented_module._fit_group=original_fit
    return pages,tables


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=OUT)
    args=ap.parse_args();audit(args.out)
