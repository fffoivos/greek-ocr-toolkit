"""Shared C1/held-out extraction: font-size plausible CTC spans, including fused ink."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import math
import multiprocessing as mp
from pathlib import Path
import time
import numpy as np
from PIL import Image

from scripts.labelfix.clariden.r1_common import (HEADS, INDEX_DTYPE, LETTERS, agreement_targets,
    check_disjointness, clusters, compose, crop_key, crop_path, document_split, nfd, rows,
    sha256, transfer_record, write_json, write_rows)
from scripts.labelfix.clariden.r1_pixels import FONT_RULE, threshold_image, font_size, plausible_span, fused_slots


WINDOW_CONTRACT=dict(schema='r1-trained-full-height-v1',padding_invariant=False,
    qualification='unqualified_for_padding_invariance',source_validity_mask=False)


def window_geometry(span, font_height, left=1.5):
    x0, x1 = math.floor(span[0]-left*font_height), math.ceil(span[1]+.75*font_height)
    if x1 <= x0:
        raise ValueError('empty window')
    return x0, x1, [(span[0]-x0)*128/(x1-x0), (span[1]-x0)*128/(x1-x0)]


def window(image, span, font_height, left=1.5):
    x0,x1,mask = window_geometry(span, font_height, left)
    canvas = Image.new('L',(x1-x0,image.height),255)
    lo,hi = max(0,x0),min(image.width,x1)
    if hi > lo:
        canvas.paste(image.crop((lo,0,hi,image.height)), (lo-x0,0))
    return np.asarray(canvas.resize((128,64), Image.Resampling.BILINEAR)), mask


def extract_line(record, alignment, image, validation=False, evaluation=False):
    """The same pixel/slot extraction for training, mock and held-out."""
    text = nfd(record.get('recogniser_text', alignment['prediction']))
    alignment,transferred=transfer_record(text,alignment)
    cs = clusters(text); spans = alignment['spans']
    if len(spans) != len(text):
        raise ValueError('alignment/codepoint count differs')
    letters=[(c.base,c.start,spans[c.start][3:5]) for c in cs if c.base.isalpha()]
    binary,threshold=threshold_image(image)
    size=font_size(binary,letters)
    fused=fused_slots(binary,letters,size['pixel_height'])
    targets = {} if evaluation else agreement_targets(record['label'],text)
    losses = Counter(); samples=[]; wide=[]; narrow=[]; coverage=[]
    losses['transferred_alignment_lines']+=int(transferred)
    for c in cs:
        if c.base not in LETTERS:
            continue
        losses['vowel_rho_slots'] += 1
        reason = None
        if alignment.get('confidence',0) < .5:
            reason = 'line_confidence_below_0.5'
        span = spans[c.start][3:5]
        if reason is None:
            ok, reason = plausible_span(span,size)
            if ok: reason = None
        if reason is None and not evaluation:
            if c.start not in targets:
                reason = 'non_agreement_word'
            elif targets[c.start] is None:
                reason = 'unsupported_marks'
        if reason:
            losses[reason] += 1
        else:
            losses['scored'] += 1
            x,m = window(image,span,size['pixel_height']); nx,nm = window(image,span,size['pixel_height'],.75)
            wide.append(x); narrow.append(nx)
            samples.append((0,len(samples),record['_line'],c.start,LETTERS.index(c.base),int(validation),
                            [-1]*4 if evaluation else targets[c.start], [m,nm]))
        diagnostic=fused.get(c.start,dict(fused=False,component_bbox=None,component_owners=[]))
        losses['fused_vowel_rho_slots']+=int(diagnostic['fused'])
        losses['fused_scored']+=int(diagnostic['fused'] and reason is None)
        uncertainty=[]
        if size['pixel_measurements']==0:uncertainty.append('no_pixel_evidence')
        if span[0]<0 or span[1]>image.width:uncertainty.append('out_of_image_span')
        coverage.append(dict(evidence_state='UNKNOWN' if uncertainty else 'unadjudicated',uncertainty=uncertainty,window_contract=WINDOW_CONTRACT,start=c.start,base=c.base,span=list(span),scored=reason is None,reason=reason,**diagnostic))
    return samples,wide,narrow,losses,coverage,dict(size,threshold=threshold,alignment_transferred=transferred)


def extract_chunk(task):
    number, records, settings = task
    out, root, layout, evaluation, val_docs = settings
    samples=[]; wide=[]; narrow=[]; losses=Counter(); line_metadata=[]; errors=[]
    for r,al in records:
        try:
            with Image.open(crop_path(r['crop'], root, layout)) as im:
                ss,xx,nn,ll,coverage,size = extract_line(r,al,im.convert('L'),r['doc'] in val_docs,evaluation)
            for s in ss:
                samples.append((number,len(samples),*s[2:]))
            wide.extend(xx); narrow.extend(nn); losses.update(ll)
            line_metadata.append(dict(line=r['_line'],id=r['id'],doc=r['doc'],crop=r['crop'],
                                      recogniser_text=nfd(r.get('recogniser_text',al['prediction'])),coverage=coverage,font_size=size))
            losses['decoded_lines'] += 1
        except Exception as e:
            errors.append(dict(id=r['id'],error=repr(e)))
    prefix = Path(out)/f'shard-{number:05d}'
    np.save(str(prefix)+'-wide.npy',np.asarray(wide,dtype=np.uint8).reshape(-1,64,128),allow_pickle=False)
    np.save(str(prefix)+'-narrow.npy',np.asarray(narrow,dtype=np.uint8).reshape(-1,64,128),allow_pickle=False)
    index = np.array(samples,dtype=INDEX_DTYPE)
    np.save(str(prefix)+'-index.npy',index,allow_pickle=False)
    write_rows(str(prefix)+'-lines.jsonl.gz',line_metadata)
    return number,losses,errors


def extract(selection, alignments, out, crop_root, layout='toolkit', mode='c1', workers=1,
            exclusions=None, split_path=None, full_selection=None):
    out=Path(out); out.mkdir(parents=True,exist_ok=False); started=time.monotonic()
    records = list(rows(selection)); evaluation=mode != 'c1'
    disjoint={}; split={}
    if not evaluation:
        full = list(rows(full_selection or selection))
        exc=json.loads(Path(exclusions).read_text())
        if sha256(full_selection or selection) != exc['selection_sha256']:
            raise ValueError('C1 source selection does not match exclusion binding')
        if len(full) != 91469:
            raise ValueError('full C1 selection must contain 91469 lines')
        allowed={r['id']:r for r in full}
        if any(r != allowed.get(r['id']) for r in records):
            raise ValueError('extraction row outside frozen C1')
        disjoint=check_disjointness(full,exc)
        split=document_split(full)
        if split_path and split != json.loads(Path(split_path).read_text()):
            raise ValueError('document split changed')
        print('DISJOINTNESS '+json.dumps(disjoint),flush=True)
        write_json(out/'document_split.json',split)
    bycrop={crop_key(r['crop']):dict(r,_line=i) for i,r in enumerate(records)}
    if len(bycrop) != len(records): raise ValueError('duplicate crop')
    settings=(str(out),str(crop_root),layout,evaluation,set(split.get('validation',[])))
    seen=set()
    def tasks():
        batch=[]; number=0
        for ar in rows(alignments):
            key=crop_key(ar['crop'])
            if key not in bycrop: continue
            if key in seen: raise ValueError('duplicate alignment '+key)
            seen.add(key);batch.append((bycrop[key],ar['alignment']))
            if len(batch)==512:
                yield number,batch,settings;number+=1;batch=[]
        if batch: yield number,batch,settings
    losses=Counter();errors=[];numbers=[]
    if workers>1:
        with mp.get_context('spawn').Pool(workers) as pool:
            for number,ls,es in pool.imap_unordered(extract_chunk,tasks(),chunksize=1):
                numbers.append(number);losses.update(ls);errors.extend(es)
    else:
        for number,ls,es in map(extract_chunk,tasks()):
            numbers.append(number);losses.update(ls);errors.extend(es)
    if set(bycrop)-seen:
        errors.extend(dict(crop=k,error='missing cached alignment') for k in sorted(set(bycrop)-seen))
    indices=[np.load(out/f'shard-{n:05d}-index.npy',allow_pickle=False) for n in sorted(numbers)]
    index=np.concatenate(indices) if indices else np.empty(0,dtype=INDEX_DTYPE)
    np.save(out/'index.npy',index,allow_pickle=False)
    lines=[l for n in sorted(numbers) for l in rows(out/f'shard-{n:05d}-lines.jsonl.gz')]
    write_rows(out/'lines.jsonl.gz',sorted(lines,key=lambda l:l['line']))
    hist={name:dict(Counter(choices[int(v)] for v in index['target'][:,j])) for j,(name,choices) in enumerate(HEADS.items())} if not evaluation else {}
    composed=dict(Counter(compose(y) for y in index['target'])) if not evaluation else {}
    payload=[p for p in out.iterdir() if p.is_file()]
    receipt=dict(schema='r1-extraction-v2',complete=not errors,mode=mode,requested_lines=len(records),
        font_rule=FONT_RULE,counts=dict(losses), errors=errors, samples=len(index), validation_samples=int(index['validation'].sum()),
        coverage=len(index)/losses['vowel_rho_slots'] if losses['vowel_rho_slots'] else 0,
        font_size_summary={k:dict(zip(('min','median','max'),map(float,np.quantile([l['font_size'][k] for l in lines],[0,.5,1])))) for k in ('pixel_height','median_ctc_width')} if lines else {},
        class_histogram=hist,composed_histogram=composed,disjointness=disjoint,document_split=split,
        source_sha256={str(p):sha256(p) for p in [selection,alignments]+([exclusions,full_selection or selection] if not evaluation else [])},
        sha256={p.name:sha256(p) for p in payload},elapsed_seconds=time.monotonic()-started,
        storage='uint8 grey per view; span masks generated from float intervals; two views for exact arm C geometry',
        stored_bytes=sum(p.stat().st_size for p in payload),no_ink_import=True,no_ctc_forward=True)
    write_json(out/'extraction_receipt.json',receipt)
    print('EXTRACTION '+json.dumps({k:v for k,v in receipt.items() if k not in ('sha256','source_sha256','document_split')}),flush=True)
    if errors: raise ValueError(f'{len(errors)} extraction failures; see receipt')
    return receipt


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ('selection','alignments','out','crop-root'):
        ap.add_argument('--'+name,type=Path,required=True)
    ap.add_argument('--mode',choices=['c1','heldout','owner'],default='c1')
    ap.add_argument('--layout',choices=['toolkit','e3'],default='toolkit')
    ap.add_argument('--workers',type=int,default=1)
    ap.add_argument('--exclusions',type=Path);ap.add_argument('--split-path',type=Path)
    ap.add_argument('--full-selection',type=Path)
    a=ap.parse_args()
    extract(a.selection,a.alignments,a.out,a.crop_root,a.layout,a.mode,a.workers,a.exclusions,a.split_path,a.full_selection)


if __name__=='__main__': main()
