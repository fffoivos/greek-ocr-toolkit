"""Offline continuation of N1-C; never builds packs or classifies ink."""
from greekocr.ops.data_root import input_path as _data_input
import hashlib
import json
import platform
import random
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/n1'
SCRATCH = Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad')
COLLECT = Path.home() / 'Projects/greek-ocr-toolkit-sol-collect'
COLLECT_PY = COLLECT / '.venv/bin/python'
RUN = Path.home() / 'Projects/collect-v3-data/run'
GROUPS = [('thousands_dot',24),('decimal_comma',24),('range_dash',24),('inner_dash',12),('empty',12)]

def sha(path):
    return hashlib.sha256(_data_input(Path(path)).read_bytes()).hexdigest()

def rows(path):
    return [json.loads(s) for s in _data_input(Path(path)).read_text().splitlines() if s.strip()]

def write(path, value, jsonl=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    # All persistent products are new; restart must use a fresh reviewed output.
    with path.open('x') as f:
        f.write(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in value) if jsonl else json.dumps(value,indent=2,ensure_ascii=False)+'\n')

def interpreter():
    import PIL
    import zlib
    return dict(executable=sys.executable, version=sys.version, machine=platform.machine(), pillow=PIL.__version__,zlib=zlib.ZLIB_VERSION,flags=str(sys.flags))

def regenerate(request, result):
    """Runs only in collector Python; the original row is never passed to ensure_crop."""
    sys.path.insert(0,str(COLLECT))
    from collect_v3.storage import ensure_crop
    records=[]
    for row in rows(request):
        copied=dict(row,crop=str(SCRATCH/'n1_cache/crops'/(row['crop_sha256']+'.png')))
        try:
            crop=ensure_crop(copied)
            if sha(crop)!=row['crop_sha256']: raise ValueError('crop hash mismatch after ensure_crop')
            records.append(dict(line_id=row['id'],crop=str(crop),crop_sha256=sha(crop),crop_unavailable=False))
        except (ValueError,OSError) as exc:
            records.append(dict(line_id=row['id'],crop_unavailable=True,crop_error=str(exc)))
    write(result,dict(interpreter=interpreter(),records=records))

def sheet(records,path,reference=False):
    """Make the zoom fill its large panel even when its native 3x size is small."""
    from PIL import Image,ImageDraw,ImageFont
    banner=45 if reference else 0
    canvas=Image.new('RGB',(1600,350*((len(records)+1)//2)+banner),'white')
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    if reference:draw.text((10,5),'C1 reference',font=font,fill='black')
    for i,r in enumerate(records):
        x=(i%2)*800;y=(i//2)*350+banner
        draw.text((x+10,y+8),f"Cell {r['cell_number']} | Google: {r['google_glyph'] or '(empty)'}",font=font,fill='black')
        for name,width,height,offset in [('zoom',780,225,42),('line',780,80,270)]:
            with Image.open(r[name]) as opened:
                im=opened.convert('RGB')
                scale=min(width/im.width,height/im.height)
                if name=='line':scale=min(1,scale)
                im=im.resize((max(1,round(im.width*scale)),max(1,round(im.height*scale))),Image.Resampling.LANCZOS)
                canvas.paste(im,(x+10,y+offset))
    canvas.save(path)

def main():
    sys.path[:0]=[str(ROOT),str(Path(__file__).parent)]
    from greekocr.numerics.locks import load_locks
    from greekocr.numerics.slots_geom import locate_slot
    from greekocr.numerics.tokens import tokenize
    from n1_render import render
    from PIL import Image,ImageDraw,ImageFont
    locks=load_locks(OUT)
    inputs={}
    def bind(path):
        path=Path(path);inputs[str(path)]=sha(path);return path
    for p in OUT.glob('n1_*txt'):bind(p)
    for p in ['frame_step1.jsonl','locked_eval_docs.json','step1_geometry.jsonl','controls/candidates.jsonl','controls/c1_references.jsonl']:
        bind(OUT/p)
    frame=[r for r in rows(OUT/'frame_step1.jsonl') if r['partition']=='step1']
    assert len(frame)==600
    locks.assert_fit_rows(s['line_id'] for s in frame)
    try:locks.assert_fit_rows(['elstat--c5f7ea1f26d39839--s000-l0367'])
    except ValueError:reserved_refused=True
    else:raise AssertionError('reserved C1 accepted')
    w1=rows(bind(RUN/'W1/features.jsonl'));byid={r['id']:r for r in w1}
    devdocs={s['document'] for s in frame}
    excluded=set(json.loads((OUT/'locked_eval_docs.json').read_text())['excluded_c1_line_ids'])
    pools=defaultdict(list);all_ranges=[];slotmap={s['slot_id']:s for s in frame}
    for row in w1:
        doc=row['source']+':'+row['item'];year=row.get('year') or 0
        if doc in devdocs|locks.reserved_docs or row['id'] in excluded:continue
        eligible=row['source']=='elstat' or row['source']=='gazette_modern' and 1982<=year<=1990
        for ti,t in enumerate(tokenize(row['label'])):
            for s in t.slots:
                if s.boundary:continue
                group=('thousands_dot' if s.glyph=='.' and 'thousands' in s.grammar_candidates else
                    'decimal_comma' if s.glyph==',' and 'decimal' in s.grammar_candidates else
                    'range_dash' if s.glyph=='-' and 'range' in s.grammar_candidates else
                    'inner_dash' if s.glyph=='-' and t.digit_count>=4 else
                    'empty' if s.glyph=='' else None)
                if not group or not (eligible or group=='range_dash'):continue
                slot=dict(asdict(s),slot_id=f"{row['id']}:t{ti}:s{s.index}",line_id=row['id'],token_start=t.start,token_end=t.end,document=doc,source=row['source'],control_group=group)
                slotmap[slot['slot_id']]=slot
                if eligible:pools[group].append(slot)
                if group=='range_dash':all_ranges.append(slot)
    docs={}
    def geometry(slot):
        locks.assert_fit_rows([slot['line_id']])
        row=byid[slot['line_id']]
        record=json.loads(bind(RUN/'W1/pages'/(row['page_id']+'.json')).read_text())
        resp=Path(record['response'])
        if str(resp) not in docs:
            assert sha(bind(resp))==record['response_sha256']
            docs[str(resp)]=json.loads(resp.read_text())['document']
        return locate_slot(row,slot,docs[str(resp)])
    dropped=[];bed=[]
    for s,old in zip(frame,rows(OUT/'step1_geometry.jsonl')):
        assert s['slot_id']==old['slot_id']
        geom=geometry(s);assert geom==old['geometry']
        if geom['geom_status']=='ok':bed.append((s,geom))
        else:dropped.append(dict(slot_id=s['slot_id'],line_id=s['line_id'],**geom))
    assert len(bed)==558 and len(dropped)==42
    old=rows(OUT/'controls/candidates.jsonl');oldids={r['slot_id'] for r in old}
    rejected=[];chosen=[];rng=random.Random('20261017:N1C:ctrl');pool_sizes={k:len(v) for k,v in pools.items()}
    # Replay the entire original category stream, including shuffle consumption.
    for group,target in GROUPS:
        pool=sorted(pools[group],key=lambda s:s['slot_id']);rng.shuffle(pool)
        retained=[]
        for r in old:
            if r['control_group']!=group:continue
            s=slotmap[r['slot_id']];g=geometry(s)
            if g['geom_status']=='ok':retained.append((s,g,'v1_retained'))
            else:rejected.append(dict(slot_id=s['slot_id'],line_id=s['line_id'],control_group=group,stage='v1',**g))
        for s in pool:
            if len(retained)>=target:break
            if s['slot_id'] in oldids:continue
            g=geometry(s)
            if g['geom_status']=='ok':retained.append((s,g,'same_pool_replacement'))
            else:rejected.append(dict(slot_id=s['slot_id'],line_id=s['line_id'],control_group=group,stage='replacement',**g))
        if group=='range_dash' and len(retained)<target:
            extra=sorted([s for s in all_ranges if s['slot_id'] not in {p['slot_id'] for p in pool}],key=lambda s:s['slot_id'])
            random.Random('20261017:N1C:ctrl:range').shuffle(extra)
            for s in extra:
                if len(retained)>=target:break
                g=geometry(s)
                if g['geom_status']=='ok':retained.append((s,g,'other_W1_range'))
                else:rejected.append(dict(slot_id=s['slot_id'],line_id=s['line_id'],control_group=group,stage='range_extension',**g))
        chosen+=retained
    refs=[]
    for oldref in rows(OUT/'controls/c1_references.jsonl'):
        if oldref.get('blocked_reserved'):continue
        ident=oldref['line_id'];row=byid[ident]
        for ti,t in enumerate(tokenize(row['label'])):
            for s in t.slots:
                sid=f'{ident}:t{ti}:s{s.index}'
                if sid!=oldref['slot_id']:continue
                slot=dict(asdict(s),slot_id=sid,line_id=ident)
                g=geometry(slot);assert g['geom_status']=='ok';refs.append((slot,g))
    assert len(refs)==4
    # Regenerate even the dropped v1 controls, to account for all original candidates.
    ids={s['line_id'] for s,g in bed+refs}|{s['line_id'] for s,g,_ in chosen}|{r['line_id'] for r in old}
    requests=[]
    for ident in sorted(ids):
        locks.assert_fit_rows([ident]);row=byid[ident];bind(row['crop_source_image']);requests.append(row)
    request=SCRATCH/'n1_cache/n1cb_crop_requests.jsonl';result=SCRATCH/'n1_cache/n1cb_crop_results.json'
    write(request,requests,True)
    print('Regenerating',len(requests),'unique line crops',flush=True)
    subprocess.run(['/usr/bin/arch','-arm64',str(COLLECT_PY),'-B',str(Path(__file__).resolve()),'--regenerate',str(request),str(result)],check=True)
    cropresults=json.loads(result.read_text());crops={r['line_id']:r for r in cropresults['records']}
    def process(s,g,recordfile):
        locks.assert_fit_rows([s['line_id']]);c=crops[s['line_id']]
        r=dict(slot_id=s['slot_id'],line_id=s['line_id'],google_glyph=s['glyph'],grammar=s['grammar_candidates'],geometry=g,
            crop_sha256=byid[s['line_id']]['crop_sha256'],crop_unavailable=c['crop_unavailable'],geometry_record_ref=f'artifacts/n1/{recordfile}#'+s['slot_id'])
        if c['crop_unavailable']:r['crop_error']=c['crop_error']
        else:
            assert sha(c['crop'])==r['crop_sha256']
            r.update(render(c['crop'],g,SCRATCH/'n1_cache/rendered_cb'))
        for key in ['line','zoom','line_sha256','zoom_sha256']:r.setdefault(key,None)
        return r
    rendered_bed=[]
    for s,g in bed:
        rendered_bed.append(process(s,g,'step1_rendered_v2.jsonl'))
        if len(rendered_bed)%100==0:print('Rendered step1',len(rendered_bed),flush=True)
    controls=[]
    for s,g,origin in chosen:
        r=process(s,g,'controls/candidates_v2.jsonl');r.update(control_group=s['control_group'],document=s['document'],source=s['source'],selection_origin=origin,cell_number=len(controls)+1);controls.append(r)
    references=[]
    for s,g in refs:
        r=process(s,g,'controls/c1_references_v2.jsonl');r.update(reference_only=True,cell_number=len(references)+1);references.append(r)
    sheets=SCRATCH/'n1_ctrl_sheets';sheets.mkdir(parents=True,exist_ok=True)
    paths=[];index=[]
    available=[r for r in controls if r['line'] and r['zoom']]
    for i in range(0,len(available),12):
        batch=available[i:i+12];path=sheets/f'n1cb_controls_{i//12+1:02d}.png';assert not path.exists();sheet(batch,path);paths.append(str(path))
        index.extend(dict(sheet=str(path),cell_number=r['cell_number'],slot_id=r['slot_id'],reference_only=False) for r in batch)
    c1path=sheets/'n1cb_c1_reference.png'
    assert all(r['line'] for r in references) and not c1path.exists()
    sheet(references,c1path,reference=True)
    index.extend(dict(sheet=str(c1path),cell_number=r['cell_number'],slot_id=r['slot_id'],reference_only=True) for r in references)
    write(sheets/'sheets_index.json',index)
    products={'step1_rendered_v2.jsonl':rendered_bed,'step1_dropped_misaligned_v2.jsonl':dropped,'controls/candidates_v2.jsonl':controls,'controls/rejected_v2.jsonl':rejected,'controls/c1_references_v2.jsonl':references,
        'controls/crop_checks_v2.jsonl':cropresults['records']}
    for name,value in products.items():write(OUT/name,value,True)
    summary=dict(step1_rendered=sum(bool(r['line']) for r in rendered_bed),step1_crop_unavailable=sum(r['crop_unavailable'] for r in rendered_bed),dropped_misaligned=len(dropped),dropped_reasons=dict(Counter(r['reason'] for r in dropped)),
        control_candidates=len(controls),control_counts=dict(Counter(r['control_group'] for r in controls)),control_rendered=len(available),control_crop_unavailable=sum(r['crop_unavailable'] for r in controls),
        original_controls_misaligned=sum(r['stage']=='v1' for r in rejected),control_origins=dict(Counter(r['selection_origin'] for r in controls)),pool_sizes=pool_sizes,all_W1_range_pool=len(all_ranges),sheets=paths,c1_sheet=str(c1path),c1_slots=len(references),reserved_refused=reserved_refused)
    outputs={str(OUT/name):sha(OUT/name) for name in products}
    for p in paths+[str(c1path),str(sheets/'sheets_index.json'),str(request),str(result)]:outputs[p]=sha(p)
    for r in rendered_bed+controls+references:
        for k in ['line','zoom']:
            if r[k]:outputs[r[k]]=r[k+'_sha256']
    write(OUT/'N1Cb_GENERATION.json',dict(inputs=inputs,outputs=outputs,summary=summary,interpreters=dict(collector=cropresults['interpreter'],renderer=interpreter()),constraints=dict(network=False,git_writes=False,reader_run=False,real_packs=False,calibration_pack=False,glyph_classification=False)))
    print(json.dumps(summary,indent=2),flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--regenerate':
        if platform.machine()!='arm64':
            import os
            os.execv('/usr/bin/arch',['/usr/bin/arch','-arm64',str(COLLECT_PY),'-B',str(Path(__file__).resolve()),*sys.argv[1:]])
        regenerate(sys.argv[2],sys.argv[3])
    else:main()
