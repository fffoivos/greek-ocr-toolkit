"""Render orientation outputs, preserving the part-two horizontal audit schema.

Existing line/cell files describe the compatibility detector. New words and
parametric guides describe the explicit oriented mode, never relabel legacy
horizontal pseudo-lines as corrected output. No source text layer is read.
"""
from __future__ import annotations
import argparse
import copy
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace

import numpy as np
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from greekocr.glyphs.orientation import measure_orientation, discover_directions, QuarterTurn
from greekocr.glyphs.oriented_page import oriented_page
from greekocr.glyphs.page_text_lines import LineSegment,CURVES
from greekocr.glyphs.table_lines import TextPiece


def save(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=lambda x:x.item() if isinstance(x,np.generic) else str(x))+'\n')


def load_baseline(directory,key):
    lines=[]
    for r in json.loads((directory/f'{key}.lines.json').read_text()):
        q=dict(r)
        for k in CURVES:q[k]=np.asarray(q[k],float)
        lines.append(LineSegment(**q))
    cells=json.loads((directory/f'{key}.cells.json').read_text())['cells']
    pieces=[TextPiece(tuple(c['box_pixels']),c['line_index'],lines[c['line_index']],c['table_id'],c['cell_id']) for c in cells]
    return SimpleNamespace(lines=lines,diagnostics=json.loads((directory/f'{key}.checks.json').read_text())),pieces


def draw_words(image,records,path, *, proposals=None):
    image=image.convert('RGB');image.thumbnail((1600,1800));d=ImageDraw.Draw(image)
    source_size=records.get('image_size',image.size);sx,sy=image.width/source_size[0],image.height/source_size[1]
    colors={0:(10,130,55),90:(20,90,220),180:(185,40,180),270:(220,65,20),None:(130,130,130)}
    for w in records['words']:
        points=[(p[0]*sx,p[1]*sy) for p in w['corners_pixels']]
        color=colors[w['orientation_cw']]
        d.line(points+[points[0]],fill=color,width=1)
        # Ordered bottom edge shows reading direction even at 180 degrees.
        a,b=points[:2];mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
        d.line((a,b),fill=color,width=2)
        delta=np.asarray(b)-np.asarray(a);n=np.linalg.norm(delta)
        if n>5:
            u=delta/n;v=np.array([-u[1],u[0]])
            tip=np.asarray(b)
            d.polygon([tuple(tip),tuple(tip-4*u+2*v),tuple(tip-4*u-2*v)],fill=color)
    image.save(path,quality=92)


def recognize_words(result,recognizer):
    from greekocr.glyphs.orientation import _recognition_strip
    strips=[]
    for w in result.words:
        strip=_recognition_strip(w.crop)
        if strip is None:raise ValueError(f'invalid word {w.index}')
        strips.append(strip)
    predictions=recognizer.recognize(strips)
    if len(predictions)!=len(result.words):raise ValueError('word prediction count mismatch')
    for w,(text,confidence) in zip(result.words,predictions):
        w.text,w.recognition_confidence=text,confidence


def source_records(result,image,outer):
    """Reuse only byte-identical normalized tensors; undo their outer frame."""
    records=[]
    for word in result.words:
        r=word.to_record(outer.size)
        corners=outer.points(r['corners_pixels'],inverse=True)
        r['corners_pixels']=corners.tolist();r['corners_page']=(corners/3).tolist()
        r['box_pixels']=[*corners.min(0),*corners.max(0)]
        r['box_page']=(np.array(r['box_pixels'])/3).tolist()
        r['guides_pixels']={k:outer.points(v,inverse=True).tolist() for k,v in r['guides_pixels'].items()}
        r['guides_page']={k:(np.array(v)/3).tolist() for k,v in r['guides_pixels'].items()}
        r['local_to_pixels']=(np.linalg.inv(outer.matrix)@np.array(r['local_to_pixels'])).tolist()
        r['local_to_page']=(np.diag([1/3,1/3,1.])@np.array(r['local_to_pixels'])).tolist()
        r['geometry_orientation_cw']=(r['geometry_orientation_cw']+outer.orientation_cw)%360
        if r['orientation_cw'] is not None:r['orientation_cw']=(r['orientation_cw']+outer.orientation_cw)%360
        r['alternatives']=[(a+outer.orientation_cw)%360 for a in r['alternatives']]
        if outer.orientation_cw%180 and r['axis']!='unknown':r['axis']='vertical' if r['axis']=='horizontal' else 'horizontal'
        r['evidence']={**r['evidence'],'evidence_frame':'normalized_raster','outer_orientation_cw':outer.orientation_cw}
        records.append(r)
    return records


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pages',type=Path,default=ROOT/'.astra/pages')
    ap.add_argument('--out',type=Path,default=ROOT/'.astra/out')
    ap.add_argument('--baseline',type=Path,default=ROOT/'.astra/previous_round4_part2')
    ap.add_argument('--layout',type=Path,default=ROOT/'.astra/layout')
    ap.add_argument('--checkpoint',type=Path,required=True)
    ap.add_argument('--codec',type=Path,default=ROOT/'greekocr/deploy/docling_plugin/recognizer/v1.json')
    ap.add_argument('--keys',nargs='*')
    ap.add_argument('--rotated',action='store_true')
    ap.add_argument('--receipt-name',default='orientation-render-receipt.json')
    args=ap.parse_args();args.out.mkdir(exist_ok=True,parents=True)
    import torch
    from greekocr.deploy.docling_plugin.recognizer.inference import Recognizer
    torch.set_num_threads(4)
    recognizer=Recognizer(str(args.checkpoint),str(args.codec))
    receipt=dict(checkpoint=str(args.checkpoint),checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),
                 codec_sha256=hashlib.sha256(args.codec.read_bytes()).hexdigest(),baseline_commit='f611ee2',
                 mode='oriented (opt-in; compatibility detector unchanged)',pages=[])
    paths=sorted(args.pages.glob('*.png'))
    if args.rotated:
        research=ROOT/'.astra/orientation_research'
        paths=[research/c['path'] for c in json.loads((research/'testset/manifest.json').read_text())['cases'] if c['kind']=='whole']
    cache={}
    for path in paths:
        key=path.stem
        if args.keys and key not in args.keys:continue
        start=time.monotonic();print('START',key,flush=True)
        image=Image.open(path).convert('L')
        dominant=measure_orientation(image,use_osd=True,unit='page')
        base=pieces=None;regions=[]
        if not args.rotated:
            base,pieces=load_baseline(args.baseline,key)
            layout=json.loads((args.layout/f'{key}.json').read_text())
            regions=[(str(c['id']),[v*3 for v in c['box']]) for c in layout['retained']]
        outer=None;cache_hit=False;digest=None
        if args.rotated:
            angle=dominant.orientation_cw
            if angle is None:angle=90 if dominant.axis=='vertical' else 0
            outer=QuarterTurn(*image.size,angle);normalized=outer.image(image)
            digest=hashlib.sha256(normalized.tobytes()+str(normalized.size).encode()).hexdigest()
            # Identical pixels do not imply the same accepted/unknown prior.
            # That distinction changes local inheritance and must be in the key.
            cache_key=(digest,dominant.orientation_cw is not None)
            cache_hit=cache_key in cache
            local_decision=replace(dominant,axis='horizontal' if dominant.axis!='unknown' else 'unknown',
                orientation_cw=0 if dominant.orientation_cw is not None else None,
                alternatives=[(v-angle)%360 for v in dominant.alternatives])
            if not cache_hit:
                cache[cache_key]=oriented_page(normalized,recognizer=recognizer,dominant=local_decision)
                recognize_words(cache[cache_key],recognizer)
            result=copy.deepcopy(cache[cache_key])
            result.dominant=local_decision
            result.groups[0].update(local_decision.to_record())
            for word in result.words:
                if word.orientation.evidence.get('inherited_from')=='page':
                    word.orientation=replace(local_decision,evidence={**local_decision.evidence,'inherited_from':'page','source':'line/block-neighbours'})
                elif word.orientation.evidence.get('polarity_source')=='block-neighbours':
                    word.orientation.polarity_confidence=local_decision.polarity_confidence
        else:
            result=oriented_page(image,regions,recognizer=recognizer,dominant=dominant,segmentation=base,pieces=pieces)
            recognize_words(result,recognizer)
        groups=copy.deepcopy(result.groups)
        if outer:
            for g in groups:
                g['frame']=(np.array(g['frame'])@outer.matrix).tolist()
                p=outer.rectangle(g['box']);g['box']=[*p.min(0),*p.max(0)]
                if g['orientation_cw'] is not None:g['orientation_cw']=(g['orientation_cw']+outer.orientation_cw)%360
                g['alternatives']=[(v+outer.orientation_cw)%360 for v in g['alternatives']]
                if outer.orientation_cw%180 and g['axis']!='unknown':g['axis']='vertical' if g['axis']=='horizontal' else 'horizontal'
        records=dict(schema='greekocr-oriented-words-v1',key=key,image_size=list(image.size),page_size=[v/3 for v in image.size],
                     page_units='PNG pixels / 3; plugin uses actual render-to-page ratios',
                     source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                     recognition_performed=True,dominant=dominant.to_record(),groups=groups,
                     proposals=result.proposals,proposals_frame='normalized_raster' if outer else 'current_page',
                     normalized_raster_sha256=digest,identical_raster_cache_hit=cache_hit,
                     words=source_records(result,image,outer) if outer else [w.to_record(image.size,[v/3 for v in image.size]) for w in result.words])
        save(args.out/f'{key}.words.json',records)
        draw_words(image,records,args.out/f'{key}.orientation.jpg')
        lines=[l.to_record() for l in result.segmentation.lines]
        save(args.out/f'{key}.oriented.lines.json',dict(frame=groups[0],lines=lines))
        save(args.out/f'{key}.oriented.checks.json',result.segmentation.diagnostics)
        if args.rotated:
            # Same part-two fields, with explicit local frame and orientation.
            save(args.out/f'{key}.lines.json',lines)
            save(args.out/f'{key}.checks.json',dict(key=key,frame=groups[0],**result.segmentation.diagnostics))
            save(args.out/f'{key}.cells.json',dict(image_size=list(image.size),page_size=[v/3 for v in image.size],cells=records['words']))
            save(args.out/f'{key}.segments.json',[dict(line_id=f'{key}-s{i:05d}',box=list(p.box)) for i,p in enumerate(result.pieces)])
        else:
            cells=json.loads((args.out/f'{key}.cells.json').read_text())
            cells['orientation_output']=f'{key}.words.json'
            cells['orientation_mode']='compatibility cells retained; oriented words are separate opt-in output'
            save(args.out/f'{key}.cells.json',cells)
        row=dict(key=key,words=len(result.words),accepted=sum(w.orientation.orientation_cw is not None for w in result.words),
                 seconds=round(time.monotonic()-start,3),dominant=result.dominant.to_record(),groups=len(result.groups))
        receipt['pages'].append(row);save(args.out/args.receipt_name,receipt)
        print('END',key,row['words'],row['accepted'],row['seconds'],flush=True)


if __name__=='__main__':main()
