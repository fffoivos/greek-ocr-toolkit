"""Offline N1-C geometry, candidate selection and lead-only contact sheets."""
import hashlib
import json
import random
import sys
from collections import Counter,defaultdict
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from greekocr.ops.data_root import input_path as _data_input
from greekocr.numerics.locks import load_locks
from greekocr.numerics.slots_geom import locate_slot
from greekocr.numerics.tokens import tokenize
from n1_render import cached_crop, render, SCRATCH
from n1_build_packs import rows, write_new
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'artifacts/n1'
RUN=Path.home()/'Projects/collect-v3-data/run'
ANCHORS=['elstat--c5f7ea1f26d39839--s000-l0367','elstat--ee37bc488988f1bd--s000-l0445','elstat--ee37bc488988f1bd--s000-l0457']
INPUTS={}


def sha(path): return hashlib.sha256(_data_input(Path(path)).read_bytes()).hexdigest()
def bind(path):
    path=Path(path)
    if str(path) not in INPUTS: INPUTS[str(path)]=sha(path)
    return path

def sheet(records,path):
    canvas=Image.new('RGB',(1600,350*((len(records)+1)//2)),'white');draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    for i,r in enumerate(records):
        x=(i%2)*800;y=(i//2)*350
        glyph=r['google_glyph'] if r['google_glyph'] else '(empty)'
        draw.text((x+10,y+8),f"Cell {r['cell_number']} | Google: {glyph}",font=font,fill='black')
        for name,box in [('zoom',(780,225)),('line',(780,80))]:
            with Image.open(r[name]) as im:
                im=im.convert('RGB');im.thumbnail(box,Image.Resampling.LANCZOS)
                canvas.paste(im,(x+10,y+(42 if name=='zoom' else 270)))
    canvas.save(path)


def main():
    locks=load_locks(OUT)
    for name in ['frame_step1.jsonl','n1_locked_eval_line_ids.txt','n1_reserved_doc_line_ids.txt','n1_reserved_docs.txt','locked_eval_docs.json']:
        bind(OUT/name)
    frame=[r for r in rows(OUT/'frame_step1.jsonl') if r['partition']=='step1'];assert len(frame)==600
    locks.assert_fit_rows(r['line_id'] for r in frame)
    try: locks.assert_fit_rows([next(iter(locks.reserved_line_ids))])
    except ValueError: refused=True
    else: raise AssertionError('reserved id accepted')
    w1=rows(bind(RUN/'W1/features.jsonl')); byid={r['id']:r for r in w1}
    devdocs={r['document'] for r in frame}
    excluded=set(json.loads((OUT/'locked_eval_docs.json').read_text())['excluded_c1_line_ids'])
    pools=defaultdict(list)
    for row in w1:
        doc=row['source']+':'+row['item'];year=row.get('year') or 0
        eligible=row['source']=='elstat' or row['source']=='gazette_modern' and 1982<=year<=1990
        if not eligible or doc in devdocs|locks.reserved_docs or row['id'] in excluded:continue
        for ti,token in enumerate(tokenize(row['label'])):
            for s in token.slots:
                if s.boundary:continue
                group=('thousands_dot' if s.glyph=='.' and 'thousands' in s.grammar_candidates else
                    'decimal_comma' if s.glyph==',' and 'decimal' in s.grammar_candidates else
                    'range_dash' if s.glyph=='-' and 'range' in s.grammar_candidates else
                    'inner_dash' if s.glyph=='-' and token.digit_count>=4 else
                    'empty' if s.glyph=='' else None)
                if group:
                    pools[group].append(dict(asdict(s),slot_id=f"{row['id']}:t{ti}:s{s.index}",line_id=row['id'],
                        token_start=token.start,token_end=token.end,document=doc,source=row['source'],control_group=group))
    print('pool sizes', {k:len(v) for k,v in pools.items()},flush=True)
    cache={}
    def process(slot):
        locks.assert_fit_rows([slot['line_id']])
        row=byid[slot['line_id']]; result=dict(slot_id=slot['slot_id'],line_id=row['id'],google_glyph=slot['glyph'],
             grammar=slot['grammar_candidates'],crop_sha256=row['crop_sha256'])
        recordpath=bind(RUN/'W1/pages'/(row['page_id']+'.json'))
        record=json.loads(recordpath.read_text()); response=bind(record['response'])
        if INPUTS[str(response)]!=record['response_sha256']:raise ValueError('response hash mismatch')
        if str(response) not in cache:cache[str(response)]=json.loads(response.read_text())['document']
        geom=locate_slot(row,slot,cache[str(response)]);result['geometry']=geom
        try:
            bind(row['crop_source_image']);crop=cached_crop(row)
        except (ValueError,OSError) as exc:
            result['crop_unavailable']=True;result['crop_error']=str(exc);return result
        result['crop_unavailable']=False
        if geom['geom_status']=='ok':result.update(render(crop,geom,SCRATCH/'n1_cache/rendered'))
        return result
    bedpath=OUT/'step1_geometry.jsonl'
    if bedpath.exists():
        bed=rows(bedpath)
        assert [r['slot_id'] for r in bed]==[s['slot_id'] for s in frame]
        # Recompute geometry under the current implementation, without reading pixels.
        changed=False
        for result,slot in zip(bed,frame):
            row=byid[slot['line_id']]
            record=json.loads((RUN/'W1/pages'/(row['page_id']+'.json')).read_text())
            path=record['response']
            if path not in cache: cache[path]=json.loads(Path(path).read_text())['document']
            current=locate_slot(row,slot,cache[path])
            changed |= current!=result['geometry']
            result['geometry']=current
        if changed: bedpath.write_text(''.join(json.dumps(r)+'\n' for r in bed))
        # Replay custody bindings for the already completed immutable geometry records.
        for slot in frame:
            row=byid[slot['line_id']]
            record=json.loads(bind(RUN/'W1/pages'/(row['page_id']+'.json')).read_text())
            bind(record['response']);bind(row['crop_source_image'])
    else:
        bed=[]
        for i,s in enumerate(frame):
            r=process(s);r['geometry_record_ref']='artifacts/n1/step1_geometry.jsonl#'+s['slot_id'];bed.append(r)
            if (i+1)%100==0: print('step1',i+1,Counter(x['geometry']['geom_status'] for x in bed),flush=True)
        write_new(bedpath,''.join(json.dumps(r)+'\n' for r in bed))
    rng=random.Random('20261017:N1C:ctrl');candidates=[]; rejected=[];used=set()
    for group,count in [('thousands_dot',24),('decimal_comma',24),('range_dash',24),('inner_dash',12),('empty',12)]:
        pool=sorted(pools[group],key=lambda s:s['slot_id']);rng.shuffle(pool);selected=[]
        for s in pool:
            if s['slot_id'] in used:continue
            r=process(s)
            if r['geometry']['geom_status']!='ok' or r['crop_unavailable']:
                rejected.append(dict(r))
            r.update(control_group=group,document=s['document'],cell_number=len(candidates)+len(selected)+1,
                geometry_record_ref='artifacts/n1/controls/candidates.jsonl#'+s['slot_id'])
            selected.append(r);used.add(s['slot_id'])
            if len(selected)==count:break
        if len(selected)!=count:print(f'POOL SHORTFALL {group}: {len(selected)}/{count}',flush=True)
        candidates+=selected
    sheets=SCRATCH/'n1_ctrl_sheets';sheets.mkdir(parents=True,exist_ok=True);paths=[]
    rendered=[r for r in candidates if 'line' in r and 'zoom' in r]
    for i in range(0,len(rendered),12):
        path=sheets/f'controls_{i//12+1:02d}.png';sheet(rendered[i:i+12],path);paths.append(str(path))
    anchors=[]
    for ident in ANCHORS:
        row=byid[ident]; slots=[]
        for ti,t in enumerate(tokenize(row['label'])):
            for s in t.slots:
                if not s.boundary and s.glyph.strip():slots.append(dict(asdict(s),slot_id=f'{ident}:t{ti}:s{s.index}',line_id=ident))
        for s in slots:
            try:
                r=process(s)
            except ValueError as exc:
                if ident not in locks.reserved_line_ids: raise
                r=dict(slot_id=s['slot_id'],line_id=ident,google_glyph=s['glyph'],blocked_reserved=True,reason=str(exc))
            r.update(reference_only=True,cell_number=len(anchors)+1);anchors.append(r)
    anchorpaths=[]
    rendered_anchors=[r for r in anchors if 'line' in r and 'zoom' in r]
    for i in range(0,len(rendered_anchors),12):
        path=sheets/f'c1_references_{i//12+1:02d}.png';sheet(rendered_anchors[i:i+12],path);anchorpaths.append(str(path))
    for candidate in candidates:
        for field in ('line','zoom','line_sha256','zoom_sha256'):candidate.setdefault(field,None)
    write_new(OUT/'controls/candidates.jsonl',''.join(json.dumps(r)+'\n' for r in candidates))
    write_new(OUT/'controls/rejected.jsonl',''.join(json.dumps(r)+'\n' for r in rejected))
    write_new(OUT/'controls/c1_references.jsonl',''.join(json.dumps(r)+'\n' for r in anchors))
    summary=dict(geometry_status_counts=dict(Counter(r['geometry']['geom_status'] for r in bed)),
        crop_unavailable=sum(r['crop_unavailable'] for r in bed),controls=len(candidates),sheets=paths,
        c1_sheets=anchorpaths,c1_slots=len(anchors),pool_sizes={k:len(v) for k,v in pools.items()},
        rejected_candidates=len(rejected),reserved_refusal=refused)
    write_new(OUT/'N1C_GENERATION.json',json.dumps(dict(inputs=INPUTS,summary=summary),indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
