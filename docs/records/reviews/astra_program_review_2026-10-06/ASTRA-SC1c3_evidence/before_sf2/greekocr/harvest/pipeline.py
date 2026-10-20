"""Resumable page extraction and budget-aware stratified reader orchestration."""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib, importlib, json, math, sys, time
import numpy as np
import cv2
from PIL import Image
import pypdfium2 as pdfium
from .core import STACK_COMMIT, SCHEMA, GATE_REVISION, bbox, page_gate, crop_gate, body_font_gate, split_columns, tier, validate_record
from .readers import Readers, BudgetExceeded, atomic, read_jsonl

HOME=Path('/Users/foivoskarounos-zamparloukos/Projects')
DEFAULT_SOURCE=HOME/'greek-page-ocr'

def digest(path):
    with Path(path).open('rb') as stream: return hashlib.file_digest(stream,'sha256').hexdigest()

def append(path,row):
    with Path(path).open('a') as f: f.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n'); f.flush()

def inputs(source, anemi, proposal=None):
    """Only receipted pages in the exact middle:2 proposal manifest."""
    anemi=Path(anemi)
    manifest=json.loads((anemi/'wave_manifest.json').read_text())
    by_id={r['record_id']:r for r in manifest['records']}
    if proposal:
        expected={r['document_id'] for r in json.loads(Path(proposal).read_text())}
        if len(expected)!=150 or set(by_id)!=expected: raise ValueError('manifest must contain all 150 proposal books')
    pages=[]
    latest={(r['record_id'],r['volume_id'],r['page_index']):r for r in read_jsonl(anemi/'ledger.jsonl')}
    for rid,r in sorted(by_id.items()):
        total=sum(v['pages'] for v in r['volumes']); start=max(0,(total-2)//2); offset=0
        for v in r['volumes']:
            selected=[i for i in range(v['pages']) if start<=offset+i<min(total,start+2)]
            if v.get('selected_page_indices')!=selected: raise ValueError('manifest is not middle:2')
            offset+=v['pages']
            for pi in selected:
                receipt=latest.get((rid,v['volume_id'],pi),{})
                if receipt.get('state')!='saved': continue
                key=hashlib.sha256(rid.encode()).hexdigest()[:24]
                pdf=anemi/'records'/key/receipt['path']
                if not pdf.exists() or digest(pdf)!=receipt['sha256']: raise ValueError('Anemi receipt hash mismatch')
                pages.append(dict(id=f"anemi-{key}-v{v['volume_id'][:8]}-p{pi+1:06d}",
                    pdf=str(pdf.resolve()),pdf_page_index=0,page=pi+1,source='Anemi',book=rid,
                    year=r['year'],decade=r['year']//10*10,catalogue=r,rights=r['rights'],
                    source_url=receipt['url'],fetch_receipt=receipt))
    return pages

class FrozenStack:
    def __init__(self, export):
        export=Path(export).resolve(); info=json.loads((export/'EXPORT.json').read_text())
        if info['commit']!=STACK_COMMIT: raise ValueError('wrong stack export')
        sys.path.insert(0,str(export)); import onnxruntime as ort; ort.set_default_logger_severity(3)
        from prototypes.fast_lines.stack import Stack
        from prototypes.fast_lines.shared.geometry_bend import scout
        self.stack=Stack(); self.scout=scout; self.pm=None
        original=self.stack.detector.infer
        def infer(gray,*args,**kwargs):
            out=original(gray,*args,**kwargs)
            if self.pm is None: self.pm=out[0]
            return out
        self.stack.detector.infer=infer
        self.model_sha256=digest(export/'.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx')
        self.source_sha256=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((export/'prototypes/fast_lines').rglob('*.py')))).hexdigest()
    def run(self,path,gray):
        self.pm=None; result=self.stack(path); start=time.perf_counter()
        edge=result['page_field']['scout']; rules=result['geometry']['columns']['rules']
        fields=self.scout(self.pm,np.array([bbox(q['polygon']) for q in result['original']]).reshape(-1,4),gray.shape[::-1],edge,rules,gray=gray)
        bend=[dict(side=int(f.side),support_rows=len(f.support),height=float(f.height),pitch=float(f.pitch),bounds=np.asarray(f.bounds).tolist()) for f in fields]
        result['harvest_bend']=bend; result['stages']['harvest_bend_scout_s']=time.perf_counter()-start
        return result

def weak_layer(page,image,source):
    sys.path.insert(0,str(Path(source).resolve()))
    from bench.extract_lines import char_records, group_chars, union, valid_box, pixel_box, spatial_text
    result=[]
    with closing(page.get_textpage()) as tp:
        if not tp.count_chars(): return []
        for group in group_chars(char_records(tp)):
            visible=[c for c in group if valid_box(c) and not c['text'].isspace()]
            if visible:
                result.append(dict(text=spatial_text(group),bbox=list(pixel_box(union([c['box'] for c in visible]),page,image)),engine='InVision text layer; weak OCR vote'))
    return result

def match_layer(box,rows):
    area=max(1,(box[2]-box[0])*(box[3]-box[1])); candidates=[]
    for r in rows:
        b=r['bbox']; intersection=max(0,min(box[2],b[2])-max(box[0],b[0]))*max(0,min(box[3],b[3])-max(box[1],b[1]))
        if intersection/area>=.6: candidates.append(dict(r,overlap_crop_fraction=intersection/area))
    return max(candidates,key=lambda r:r['overlap_crop_fraction']) if candidates else None

def crop_features(im):
    a=np.asarray(im.convert('L')); dark=float(np.percentile(a,5)); paper=float(np.percentile(a,90))
    ink=(a<min(220,paper-35)).astype(np.uint8); n,labels,stats,centres=cv2.connectedComponentsWithStats(ink)
    bodies=[s for s in stats[1:] if s[4]>=5 and s[3]>=3 and s[2]<im.width*.2 and s[3]<im.height*.95]
    contrasts=[]
    for x,y,w,h,area in bodies:
        local=a[y:y+h,x:x+w]; contrasts.append(float(paper-np.percentile(local,10)))
    return dict(width=im.width,height=im.height,x_height_estimate=float(np.median([s[3] for s in bodies])) if bodies else None,
                faintness_proxy=paper-dark,darkest_percentile_contrast=paper-dark,ink_fraction=float(ink.mean()),
                component_contrast_p10=float(np.percentile(contrasts,10)) if contrasts else None,
                component_count=len(bodies),length_stratum='full_width' if im.width/max(1,im.height)>=12 else 'short',
                readability_stratum='faint' if paper-dark<70 else 'normal',chars_per_100px=None)

def polygon_crop(image, polygon, *, parent_polygon=None):
    box=bbox(polygon)
    x0,y0,x1,y1=max(0,math.floor(box[0])),max(0,math.floor(box[1])),min(image.width,math.ceil(box[2])),min(image.height,math.ceil(box[3]))
    if x1<=x0 or y1<=y0: raise ValueError('invalid polygon crop')
    if parent_polygon is not None:
        # Re-rasterising a clipped sloping edge can move it by one pixel. Cut
        # the original mask instead, preserving every original column pixel.
        parent_box=bbox(parent_polygon)
        px,py=max(0,math.floor(parent_box[0])),max(0,math.floor(parent_box[1]))
        return polygon_crop(image,parent_polygon).crop((x0-px,y0-py,x1-px,y1-py))
    raw=image.crop((x0,y0,x1,y1)); mask=np.zeros((raw.height,raw.width),np.uint8)
    cv2.fillPoly(mask,[np.rint(np.asarray(polygon)-[x0,y0]).astype(np.int32)],255)
    return Image.fromarray(np.where(mask,np.asarray(raw),255).astype(np.uint8))

def extract_page(inp,stack,big,source):
    pdf_sha=digest(inp['pdf']); start=time.perf_counter()
    page_dir=Path(big)/'pages'; page_dir.mkdir(parents=True,exist_ok=True)
    page_path=page_dir/(inp['id']+'.png')
    with pdfium.PdfDocument(inp['pdf']) as doc, closing(doc[inp['pdf_page_index']]) as page:
        bitmap=page.render(scale=200/72,grayscale=True)
        image=bitmap.to_pil().copy().convert('L'); bitmap.close()
        image.save(page_path,compress_level=1)
    render_s=time.perf_counter()-start; gray=np.asarray(image)
    t=time.perf_counter(); result=stack.run(page_path,gray); stack_s=time.perf_counter()-t
    t=time.perf_counter(); pg=page_gate(gray,result['items'],bend_fired=any(f['side']!=0 for f in result['harvest_bend']))
    items=split_columns(result['items'],pg,gray)
    gates_s=time.perf_counter()-t; boxes=[bbox(q['polygon']) for q in items]
    records=[];crop_s=0.; code_hash={p.name:digest(p) for p in sorted(Path(__file__).parent.glob('*.py'))}
    for i,(item,box) in enumerate(zip(items,boxes)):
        t=time.perf_counter(); gate=crop_gate(box,boxes,pg,image.size,item,long_complete=True)
        feat=dict(width=math.ceil(box[2])-math.floor(box[0]),height=math.ceil(box[3])-math.floor(box[1]),
            x_height_estimate=None,chars_per_100px=None,faintness_proxy=None,
            width_band_ratio=gate['width_band_ratio'],paragraph_position=gate['paragraph_position'])
        if gate['accepted']:
            feat.update(crop_features(polygon_crop(image,item['polygon'],parent_polygon=item.get('harvest_parent_polygon'))))
            feat['length_stratum']='long_complete_candidate'
        crop_s+=time.perf_counter()-t
        ident=inp['id']+f"-l{item['harvest_parent_index']+1:04d}"
        if 'harvest_column_piece' in item: ident+=f"-c{item['harvest_column_piece']+1}"
        record=dict(schema=SCHEMA,id=ident,page_id=inp['id'],source='Anemi',
            book=inp['book'],year=inp['year'],decade=inp['decade'],page=inp['page'],
            provenance=dict(pdf=inp['pdf'],pdf_sha256=pdf_sha,source_url=inp['source_url'],
                catalogue=inp['catalogue'],rights=inp['rights'],fetch_receipt=inp['fetch_receipt'],
                page_image=str(page_path.resolve()),dpi=200,render_scale=200/72,grayscale=True,
                stack_model_sha256=stack.model_sha256,stack_source_sha256=stack.source_sha256),
            harvest_code_sha256=code_hash,stack_commit=STACK_COMMIT,polygon=item['polygon'],bbox=box,
            stack_source_ids=item.get('source_ids'),stack_score=item.get('score'),page_class=pg['page_class'],
            gates=gate,page_gate_flags=pg['flags'],features=feat,straighten=None,raw_crop=None,
            straight_crop=None,text_layer=None,readers={},tier='unread' if gate['accepted'] else 'rejected',
            label=None,tags=[],sampled=False)
        if 'harvest_parent_polygon' in item:
            record['pre_split_polygon']=item['harvest_parent_polygon']
        records.append(validate_record(record))
    body_font_gate(records,pg)
    receipt=dict(**inp,stack_commit=STACK_COMMIT,page_gate=pg,bend_scout=result['harvest_bend'],
        lines_found=len(records),survived_gates=sum(r['gates']['accepted'] for r in records),
        stack_suppression_count=len(result.get('removed',[])),
        stack_suppression_reasons=dict(__import__('collections').Counter(q.get('removal','unknown') for q in result.get('removed',[]))),
        timing=dict(render_s=render_s,stack_s=stack_s,page_gates_s=gates_s,crop_s=crop_s,straighten_s=0.,
            total_cpu_s=time.perf_counter()-start,stack_stages=result['stages'],stack_timing=result['timing']))
    return receipt,records

def prepare(out,big,export,source,anemi,max_new_pages=None,proposal=None):
    out=Path(out); out.mkdir(parents=True,exist_ok=True);store=out/'pages';store.mkdir(exist_ok=True)
    selection=inputs(source,anemi,proposal);atomic(out/'input_pages.json',selection);stack=None;processed=0
    for inp in selection:
        path=store/(inp['id']+'.json')
        if path.exists(): continue
        if max_new_pages is not None and processed>=max_new_pages: break
        if stack is None: stack=FrozenStack(export)
        receipt,records=extract_page(inp,stack,big,source);atomic(path,dict(page=receipt,records=records));processed+=1
        print(f"HARVEST_PAGE Anemi page={inp['page']} found={len(records)} survived={receipt['survived_gates']} cpu_s={receipt['timing']['total_cpu_s']:.2f}",flush=True)
    return collect(out)

def collect(out):
    pages=[];records=[]
    for path in sorted((Path(out)/'pages').glob('*.json')):
        obj=json.loads(path.read_text()); pages.append(obj['page']); records.extend(obj['records'])
    atomic(Path(out)/'page_gates.json',pages)
    path=Path(out)/'records.jsonl'; temp=path.with_suffix('.jsonl.tmp')
    with temp.open('w') as f:
        for r in records: f.write(json.dumps(validate_record(r),ensure_ascii=False,allow_nan=False)+'\n')
    temp.replace(path); return pages,records

def balanced_sample(records,n,seed=13):
    # Equal allocation across source/decade/length/readability, then deterministic
    # pseudorandom order within each stratum. Inclusion probabilities recorded.
    groups=defaultdict(list)
    for r in records:
        key=(r['source'],str(r['decade']),r['features']['length_stratum'],r['features']['readability_stratum'])
        groups[key].append(r)
    for key,rows in groups.items(): rows.sort(key=lambda r:hashlib.sha256(f'{seed}:{r["id"]}'.encode()).hexdigest())
    chosen=[];keys=sorted(groups); index=0
    while len(chosen)<min(n,len(records)):
        for key in keys:
            if index<len(groups[key]) and len(chosen)<n: chosen.append(groups[key][index])
        index+=1
    counts=defaultdict(int)
    for r in chosen: counts[(r['source'],str(r['decade']),r['features']['length_stratum'],r['features']['readability_stratum'])]+=1
    for r in chosen:
        key=(r['source'],str(r['decade']),r['features']['length_stratum'],r['features']['readability_stratum'])
        r['sampling']=dict(stratum=list(key),population=len(groups[key]),selected=counts[key],inclusion_probability=counts[key]/len(groups[key]),seed=seed)
    return chosen

def assign(r,pair):
    r['readers']=pair
    if any(v['status']!='ok' or v['rejected'] for v in pair.values()):
        r.update(tier='rejected',label=None,tags=sorted(set(flag for v in pair.values() for flag in v['flags'])) or ['reader_service_error'])
    else:
        result=tier(pair['vision']['text'],pair['docai']['text'],(r.get('text_layer') or {}).get('text')); r.update(result)
        r['features']['chars_per_100px']=len(pair['vision']['text'])*100/max(1,r['features']['width'])

def persist(out,pages,records):
    grouped=defaultdict(list)
    for r in records: grouped[r['page_id']].append(validate_record(r))
    for page in pages:
        page['survived_gates']=sum(r['gates']['accepted'] for r in grouped[page['id']])
        atomic(Path(out)/'pages'/(page['id']+'.json'),dict(page=page,records=grouped[page['id']]))
    collect(out)

def sample_order(rows,seed=13):
    """Prefer complete, long rows; interleave both pages before hash-ranked fill."""
    groups=defaultdict(list)
    for r in rows: groups[r['page_id']].append(r)
    for group in groups.values():
        group.sort(key=lambda r:(r['gates']['paragraph_position']!='interior',
            -min(1.,r['features']['width_band_ratio']),
            hashlib.sha256(f'{seed}:{r["id"]}'.encode()).hexdigest()))
    ordered=[];keys=sorted(groups)
    for i in range(max((len(g) for g in groups.values()),default=0)):
        ordered.extend(groups[k][i] for k in keys if i<len(groups[k]))
    return ordered

def neighbour_ink(line):
    """Own accent-to-descender zone, anchored to the straightener's baseline.

    The body-band roles only seed guide fitting; they do not decide ownership.
    The centroid and extent tests are applied to every measured component.
    """
    from greekocr.glyphs.components import line_glyphs
    from greekocr.glyphs.page_font import DEFAULTS, fit_guides
    from greekocr.glyphs.page_text_lines import LineSegment
    from types import SimpleNamespace
    g=line_glyphs(line.image,xh_prior=line.xh,
                  focus=(line.baseline_row-2,line.baseline_row+2))
    base=g.band.bottom.copy();xh=float(line.xh)
    evidence=np.asarray([(c.x0,c.y0,c.x1,c.y1,c.area,c.index,c.darkness)
        for c in g.components if c.role not in ('neighbour','rule','large')],float).reshape(-1,7)
    guides=LineSegment(0,g.width,base,base-1.5*xh,base-xh,base+.5*xh,
        base-2.8*xh,base+1.3*xh,xh,support=g.band.n_support,
        component_ids=tuple(evidence[:,5].astype(int)))
    fit_guides(SimpleNamespace(components=evidence,labels=g.labels,xheight=xh),[guides])
    accent=guides.accent_top
    # A partly unsupported accent band must borrow the complete band. Mixing
    # a fused capital's top contact with an imputed accent bottom shrinks the
    # envelope onto the ascenders and excludes real clipped diacritics.
    borrowed_accent=bool({'accent_top','accent_bottom'}&set(guides.borrowed))
    if borrowed_accent: accent=guides.baseline+DEFAULTS['accent_top']*xh
    top=accent-.15*xh;bottom=guides.font_bottom+.15*xh
    owned={'above':[],'below':[]};components=[]
    for c in g.components:
        # True ink centroid, rather than the centre of a bounding rectangle.
        sub=g.labels[c.y0:c.y1,c.x0:c.x1]==c.index
        ys,xs=np.nonzero(sub)
        cx=float(xs.mean()+c.x0);cy=float(ys.mean()+c.y0)+.5
        x=int(np.clip(round(cx),0,g.width-1))
        overlap=max(0.,min(c.y1,bottom[x])-max(c.y0,top[x]))
        fraction=overlap/max(1,c.h)
        if (cy<top[x] or cy>bottom[x]) and fraction<=.25:
            side='above' if cy<top[x] else 'below';owned[side].append(c.index)
            pixel_x=xs+c.x0;pixel_y=ys+c.y0+.5
            # Extents decide ownership; contact requires retained ink inside
            # the fitted zone, not a fractional empty corner of its rectangle.
            touches=bool(np.any((pixel_y>=top[pixel_x])&(pixel_y<=bottom[pixel_x])))
            components.append(dict(index=c.index,side=side,centroid=[cx,cy],
                bbox=[c.x0,c.y0,c.x1,c.y1],overlap_fraction=float(fraction),touches_zone=touches))
    result={};masks=[]
    for side in ('above','below'):
        ids=owned[side]
        mask=np.isin(g.labels,ids) if ids else np.zeros_like(g.ink)
        masks.append(mask)
        rows=np.flatnonzero(mask.any(axis=1));cols=np.flatnonzero(mask.any(axis=0))
        result[side]=dict(height_fraction=len(rows)/g.height,
            x_span_fraction=float(cols[-1]-cols[0]+1)/g.width if cols.size else 0.,
            ink_pixels=int(mask.sum()),component_count=len(ids))
    mask=masks[0]|masks[1];rows=np.flatnonzero(mask.any(axis=1));cols=np.flatnonzero(mask.any(axis=0))
    hf=len(rows)/g.height;wf=float(cols[-1]-cols[0]+1)/g.width if cols.size else 0.
    touches=any(c['touches_zone'] for c in components)
    sample_x=np.unique(np.r_[np.arange(0,g.width,32),g.width-1]).astype(int)
    result.update(height_limit=.12,x_span_limit=.20,overlap_limit=.25,
        combined=dict(height_fraction=hf,x_span_fraction=wf,ink_pixels=int(mask.sum())),
        components=components,touches_zone=touches,
        own_zone=dict(sample_x=sample_x.tolist(),accent_top=accent[sample_x].tolist(),
            descender_bottom=guides.font_bottom[sample_x].tolist(),baseline=guides.baseline[sample_x].tolist(),x_height=xh,padding_xh=.15,
            borrowed_guides=list(guides.borrowed),borrowed_accent_band=borrowed_accent),
        rejected=bool((hf>=.12 and wf>=.20) or touches))
    return result

def inspect_straight_crop(raw):
    """Offline gate stage only: no filesystem writes, detector or readers."""
    from greekocr.glyphs.lines_api import separate_lines
    flags=[];line=None;metadata=None;sliver=None
    try:
        lines=separate_lines(raw,min_visible=0,tight=True,margin=.2)
        mains=[l for l in lines if l.side=='main']
        neighbours=[l for l in lines if l.side!='main' and l.visible>=.5]
        if len(mains)!=1:
            flags.append('straightener_multiple_bands' if lines else 'straightener_empty')
        else:
            line=mains[0]
            metadata=dict(x_height=float(line.xh),missing_fraction=float(line.missing.mean()),
                top_body_cut=float(line.top_cut.mean()),bottom_body_cut=float(line.bottom_cut.mean()),
                margin_xh=.2,tight=True,page_x_offset_in_crop=line.x0)
            sliver=neighbour_ink(line)
            if sliver['rejected']: flags.append('neighbour_sliver')
            if neighbours: flags.append('straightener_multiple_bands')
            if metadata['top_body_cut']>.08 or metadata['bottom_body_cut']>.08:
                flags.append('curled_or_clipped_body_edge')
    except Exception as e: flags.append('straightener_error_'+type(e).__name__)
    return dict(flags=flags,line=line,straighten=metadata,neighbour_sliver=sliver)

def straighten_candidate(r,big):
    t=time.perf_counter();directory=Path(big)/'crops'/r['page_id'];directory.mkdir(parents=True,exist_ok=True)
    with Image.open(r['provenance']['page_image']) as page:
        raw=polygon_crop(page,r['polygon'],parent_polygon=r.get('pre_split_polygon'))
    raw_path=directory/(r['id']+'.raw.png');raw.save(raw_path)
    r['raw_crop']=str(raw_path.resolve())
    inspected=inspect_straight_crop(raw)
    r['gates']['flags'].extend(inspected['flags'])
    r['gates']['neighbour_sliver']=inspected['neighbour_sliver']
    r['straighten']=inspected['straighten']
    line=inspected['line']
    if line is not None:
        path=directory/(r['id']+'.straight.png');line.image.save(path)
        r['straight_crop']=str(path.resolve())
        r['straighten']['page_x_offset']=math.floor(r['bbox'][0])+line.x0
        r['features']['x_height_estimate']=float(line.xh)
        r['features']['straight_width']=line.image.width;r['features']['straight_height']=line.image.height
    r['gates']['accepted']=not r['gates']['flags']
    if not r['gates']['accepted']: r.update(tier='rejected',label=None)
    r['straighten_s']=time.perf_counter()-t
    return r['gates']['accepted']

def sample(out,big,n=500):
    if not 1<=n<=500: raise ValueError('sample must be <=500 lines')
    out=Path(out);pages,records=collect(out)
    if len(pages)!=300 or len({p['book'] for p in pages})!=150:
        raise ValueError('sample waits for 300 pages / all 150 proposal books')
    if (out/'sampling.json').exists():
        frozen=json.loads((out/'sampling.json').read_text())
        if frozen['sample_max']!=n: raise ValueError('frozen sample cannot change during resume')
        return [r for r in records if r['sampled']]
    grouped=defaultdict(list)
    for r in records:
        if r['source']!='Anemi': raise ValueError('Vouli is excluded')
        if r['gates']['accepted']: grouped[r['book']].append(r)
    ordered={b:sample_order(rs) for b,rs in grouped.items()};cursor=defaultdict(int);selected=[];book_counts=defaultdict(int)
    books=sorted({p['book'] for p in pages},key=lambda b:(next(p['decade'] for p in pages if p['book']==b),b))
    def take(book):
        rows=ordered.get(book,[])
        while cursor[book]<len(rows):
            r=rows[cursor[book]];cursor[book]+=1
            if r.get('straighten') is None and not straighten_candidate(r,big): continue
            if not r['gates']['accepted']: continue
            r['sampled']=True;selected.append(r);book_counts[book]+=1;return True
        return False
    # Three rounds give every eligible book a row before any fourth allocation.
    for round_index in range(3):
        for book in books:
            if len(selected)<n: take(book)
    # A fourth row only for rich books, allocated round-robin across decades.
    rich=defaultdict(list)
    for b in books:
        if len(grouped[b])>=12 and book_counts[b]==3: rich[next(p['decade'] for p in pages if p['book']==b)].append(b)
    for bs in rich.values(): bs.sort(key=lambda b:(-len(grouped[b]),hashlib.sha256(('fourth:'+b).encode()).hexdigest()))
    for i in range(max((len(bs) for bs in rich.values()),default=0)):
        for decade in sorted(rich):
            if len(selected)<n and i<len(rich[decade]): take(rich[decade][i])
    for r in selected:
        r['sampling']=dict(rule='purposive long complete lines; three per book; rich-book fourth across decades',
            stratum=['Anemi',r['decade'],r['book']],population_candidates=len(grouped[r['book']]),
            selected_per_book=book_counts[r['book']],seed=13,inclusion_probability=None,
            note='ranked geometric quality, not a probability sample')
    for p in pages:
        p['timing']['straighten_s']=sum(r.get('straighten_s',0.) for r in records if r['page_id']==p['id'])
        p['timing']['total_cpu_s']+=p['timing']['straighten_s']
    persist(out,pages,records)
    atomic(out/'sampling.json',dict(rule='3 per book, up to 4 for >=12 candidate books; round-robin fourths by decade',
        sample_max=n,eligible_before_straightening=sum(len(rs) for rs in grouped.values()),selected=len(selected),
        target_books=150,represented_books=sum(bool(book_counts[b]) for b in books),book_counts={b:book_counts[b] for b in books},
        zero_books=[b for b in books if not book_counts[b]],decades=sorted({r['decade'] for r in selected}),
        ids=[r['id'] for r in selected],seed=13,montage=False,selection_frozen_before_calls=True))
    return selected

def label(out,cap=3):
    out=Path(out);pages,records=collect(out);sampling=json.loads((out/'sampling.json').read_text())
    by_id={r['id']:r for r in records};selected=[by_id[i] for i in sampling['ids']]
    if len(selected)>500 or any(r['source']!='Anemi' or not r['gates']['accepted'] or not r['sampled'] for r in selected):
        raise ValueError('sample contract violated')
    if any(r['gates'].get('gate_revision')!=GATE_REVISION or
           not isinstance(r['gates'].get('neighbour_sliver'),dict) for r in selected):
        raise ValueError(f'stored sample predates {GATE_REVISION} geometry; gate certification required before readers')
    readers=Readers(out/'google',cap);saved=out/'labels';saved.mkdir(exist_ok=True)
    todo=[]
    for r in selected:
        path=saved/(r['id']+'.json')
        if path.exists(): assign(r,json.loads(path.read_text()))
        else: todo.append(r)
    try:
        with ThreadPoolExecutor(max_workers=4) as pool:
            pending={};cursor=0;completed=0
            while cursor<len(todo) or pending:
                while cursor<len(todo) and len(pending)<4:
                    f=pool.submit(readers.single,todo[cursor]);pending[f]=todo[cursor];cursor+=1
                f=next(as_completed(pending));r=pending.pop(f);pair=f.result()
                atomic(saved/(r['id']+'.json'),pair);assign(r,pair);completed+=1
                if completed%25==0:
                    print(f"HARVEST_LABEL lines={completed}/{len(todo)} cost_usd={readers.budget.receipt()['cost_usd']:.3f}",flush=True)
    except BudgetExceeded: atomic(out/'stop.json',dict(reason='cost_or_call_cap',cost=readers.budget.receipt()))
    persist(out,pages,records);atomic(out/'cost_receipt.json',readers.budget.receipt())
    return selected
