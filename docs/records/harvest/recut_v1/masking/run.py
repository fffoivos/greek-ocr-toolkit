"""F2-only offline T6a2 binding, development, freeze and paired CPU readout."""
from __future__ import annotations
import argparse,gzip,hashlib,io,json,socket,sys,time,unicodedata,warnings
from collections import defaultdict,Counter
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(OUT.parent))
import run_f2 as prior
from greekocr.glyphs.foreign_ink import PARAMETERS,prepare_mask_page,mask_foreign_ink,mask_detected_line
from greekocr.pages import process_page
from greekocr.pages.lines import CURVES
from probe import match,runtime_fit

warnings.filterwarnings('ignore',category=np.exceptions.RankWarning)
SOURCES=prior.SOURCES

def source_hashes():
    files=['greekocr/glyphs/foreign_ink.py','greekocr/glyphs/recut.py','greekocr/glyphs/lines_api.py',
           'greekocr/glyphs/components.py','greekocr/pages/lines.py','greekocr/pages/pixels.py',
           'greekocr/pages/font.py','greekocr/pages/api.py','greekocr/pages/tables.py']
    return {p:prior.file_sha256(ROOT/p) for p in files}


def runtime_lines(native,page_id):
    path=OUT/'runtime'/f'{page_id}.json.gz';path.parent.mkdir(parents=True,exist_ok=True)
    binding=dict(source_raster_sha256=hashlib.sha256(np.asarray(native).tobytes()).hexdigest(),source_hashes=source_hashes())
    if path.exists():
        value=json.loads(gzip.decompress(path.read_bytes()))
        assert value['binding']==binding,'stale runtime observation'
        return value['lines']
    start=time.monotonic();result=process_page(native)
    # to_record rounds guides to .001 px: explicitly retain all full-precision curves.
    lines=[]
    for line in result.segmentation.lines:
        if line.discounted is not None:continue
        record=line.to_record()
        record.update({key:getattr(line,key).tolist() for key in CURVES})
        lines.append(record)
    value=dict(binding=binding,lines=lines,seconds=time.monotonic()-start,
               detected_without_google=True,utc=datetime.now(timezone.utc).isoformat())
    path.write_bytes(gzip.compress(json.dumps(value,separators=(',',':')).encode(),mtime=0))
    return lines


def measure(r,prepared,original,result):
    old=original[r['id']];row_id=old['ownership'].get('row_id')
    own=prepared.get(row_id) if old['ownership']['ownership_status']=='owned' else None
    box=tuple(r['crop_bbox']);x0,y0,x1,y1=box
    own_pixels=own_loss=foreign_before=foreign_after=body_before=body_after=0
    for other in prepared.values():
        before=prior.OWN.box_hits(other,box)
        if not before.any():continue
        yy,xx=other['_y'][before],other['_x'][before]
        lost=result.mask[yy-y0,xx-x0]
        if own is not None and other['row_id']==row_id:
            own_pixels+=int(before.sum());own_loss+=int(lost.sum())
        elif own is not None:
            foreign_before+=int(before.sum());foreign_after+=int((~lost).sum())
            index=xx-other['x0']
            body=(yy>=other['meanline'][index])&(yy<other['baseline'][index])
            body_before+=int(body.sum());body_after+=int((body&~lost).sum())
    return dict(id=r['id'],page_id=r['page_id'],stratum=r['stratum'],dev=r['dev'],
        original_page=r['crop_page_path'],old_box=list(box),google_text=r['label_after_conventions'],
        geometry_clean=r['geometry_positive'] is False and not r['screen_reject'],
        cached_owner_row=row_id if own is not None else None,
        own_pixels=own_pixels if own is not None else None,own_pixels_lost=own_loss if own is not None else None,
        foreign_pixels_before=foreign_before if own is not None else None,
        foreign_pixels_after=foreign_after if own is not None else None,
        neighbour_body_pixels_before=body_before if own is not None else None,
        neighbour_body_pixels_after=body_after if own is not None else None,**result.record)


def save_pair(native,result,record,feature):
    directory=OUT/'f2'/record['stratum']
    for arm,image in [('original',native.crop(tuple(record['old_box']))),('masked',result.image)]:
        dest=directory/arm/f"{record['id']}.png";dest.parent.mkdir(parents=True,exist_ok=True)
        image.save(dest,compress_level=3)
        record[f'{arm}_path']=str(dest.relative_to(OUT));record[f'{arm}_sha256']=prior.file_sha256(dest)
    assert record['original_sha256']==feature['crop_sha256'],'original crop custody'
    if not record['changed']:assert record['original_sha256']==record['masked_sha256']


def summaries(records):
    out={}
    for source in (*SOURCES,'overall'):
        rr=[r for r in records if source=='overall' or r['stratum']==source]
        n=[r for r in rr if r['dev'] and r['dev']['crop_ok']=='n']
        y=[r for r in rr if r['dev'] and r['dev']['crop_ok']=='y']
        out[source]=dict(lines=len(rr),changed=sum(r['changed'] for r in rr),
            crop_n=len(n),crop_y=len(y),changed_y=sum(r['changed'] for r in y),
            own_y_pixels=sum(r['own_pixels'] or 0 for r in y),
            own_y_lost=sum(r['own_pixels_lost'] or 0 for r in y),
            y_with_own_loss=sum(bool(r['own_pixels_lost']) for r in y),
            unmeasurable_y=sum(r['own_pixels'] is None for r in y),
            n_foreign_before=sum(r['foreign_pixels_before'] or 0 for r in n),
            n_foreign_after=sum(r['foreign_pixels_after'] or 0 for r in n),
            n_body_before=sum(r['neighbour_body_pixels_before'] or 0 for r in n),
            n_body_after=sum(r['neighbour_body_pixels_after'] or 0 for r in n),
            masked_pixels=sum(r['masked_pixel_count'] for r in rr),
            masked_components=sum(r['masked_component_count'] for r in rr),
            empty_ring_abstentions=sum(r['empty_ring_abstentions'] for r in rr),
            unmatched=sum(r.get('runtime_index') is None for r in rr),
            ring_median_median=np.median([np.mean(r['ring_median']) for r in rr if r['ring_median'] is not None]).item()
                if any(r['ring_median'] is not None for r in rr) else None,
            ring_spread_median=np.median([np.mean(r['ring_spread']) for r in rr if r['ring_spread'] is not None]).item()
                if any(r['ring_spread'] is not None for r in rr) else None)
    return out


def develop_or_materialize(dev_only):
    rr,inputs=prior.bind();assert len(rr)==5770
    if dev_only:rr=[r for r in rr if r['dev']]
    else:
        frozen=prior.read_json(OUT/'params.json')
        assert frozen['inputs']==inputs and frozen['source_hashes']==source_hashes()
        assert frozen['params']==PARAMETERS
    groups=defaultdict(list)
    for r in rr:groups[r['page_id']].append(r)
    records=[];provenance=[];start=time.monotonic()
    for i,group in enumerate(groups.values(),1):
        native,prepared,original,_,_,prov=prior.page_bundle(group)
        lines=runtime_lines(native,group[0]['page_id']);fits=[runtime_fit(l) for l in lines]
        page=prepare_mask_page(native)
        for r in group:
            index=match(r['crop_bbox'],fits)
            if index is None:
                # No target was detected: explicit conservative identity, no invented curve.
                from greekocr.glyphs.foreign_ink import MaskedCrop
                x0,y0,x1,y1=r['crop_bbox'];m=np.zeros((y1-y0,x1-x0),bool)
                result=MaskedCrop(native.crop(tuple(r['crop_bbox'])),m,dict(crop_box=r['crop_bbox'],
                    masked_pixel_count=0,proposed_masked_pixel_count=0,masked_component_count=0,
                    ring_median=None,ring_spread=None,fills=[],empty_ring_abstentions=0,
                    mask_sha256=hashlib.sha256(m.tobytes()).hexdigest(),changed=False,native_changed_pixels=0))
            else:
                result=mask_foreign_ink(page,lines[index],lines,r['crop_bbox'])
                if dev_only:
                    eq=mask_detected_line(page,lines[index],lines,r['crop_bbox'])
                    assert np.array_equal(result.mask,eq.mask)
                    assert np.array_equal(np.asarray(result.image),np.asarray(eq.image))
            record=measure(r,prepared,original,result);record['runtime_index']=index
            record['runtime_curves_path']=f"runtime/{r['page_id']}.json.gz"
            save_pair(native,result,record,r)
            records.append(record)
        provenance.append(prov)
        print('DEV' if dev_only else 'MATERIALIZE',i,'/',len(groups),'rows',len(records),'seconds',round(time.monotonic()-start,1),flush=True)
    stage='dev' if dev_only else 'f2'
    prior.write_rows(OUT/stage/'records.jsonl',records);prior.write_rows(OUT/stage/'provenance.jsonl',provenance)
    prior.write_json(OUT/stage/'summary.json',summaries(records))
    if dev_only:
        params_sha=hashlib.sha256(json.dumps(PARAMETERS,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        frozen=dict(params=PARAMETERS,params_sha256=params_sha,frozen_utc=datetime.now(timezone.utc).isoformat(),
            inputs=inputs,source_hashes=source_hashes(),dev_lines=160,network='OFF',
            selection='No tunable _voronoi_keep tolerances; fixed existing rule; no grid or model-based choice',
            dev_safety_pass=summaries(records)['overall']['own_y_lost']==0,
            harm_inference_started=False)
        assert not (OUT/'params.json').exists(),'do not overwrite frozen parameters'
        prior.write_json(OUT/'params.json',frozen);print('FROZEN',params_sha,flush=True)
    else:
        dev={r['id']:r for r in prior.rows(OUT/'dev/records.jsonl')}
        for r in records:
            if r['id'] in dev:
                assert r['mask_sha256']==dev[r['id']]['mask_sha256']
                assert r['masked_sha256']==dev[r['id']]['masked_sha256']
        for source in SOURCES:
            prior.write_rows(OUT/'f2'/source/'records.jsonl',[r for r in records if r['stratum']==source])


def sheets():
    records=prior.rows(OUT/'dev/records.jsonl');font=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',14)
    for source in SOURCES:
        rr=sorted([r for r in records if r['stratum']==source],key=lambda r:r['dev']['card_id'])
        directory=OUT/'dev/review'/source;directory.mkdir(parents=True,exist_ok=True)
        for start in range(0,len(rr),5):
            sheet=Image.new('RGB',(1900,900),'#e3e3e3');draw=ImageDraw.Draw(sheet)
            for j,r in enumerate(rr[start:start+5]):
                y=j*180
                draw.text((8,y+2),f"{r['dev']['card_id']} crop={r['dev']['crop_ok']} changed={r['changed']} OWN LOSS={r['own_pixels_lost']}/{r['own_pixels']} foreign={r['foreign_pixels_before']}->{r['foreign_pixels_after']} masked={r['masked_pixel_count']}",font=font,fill='black')
                draw.text((8,y+21),'Target: '+r['google_text'][:205],font=font,fill='#333333')
                for arm,offset in [('original',42),('masked',111)]:
                    image=Image.open(OUT/r[f'{arm}_path']).convert('RGB')
                    scale=min(2.,1850/image.width,64/image.height)
                    image=image.resize((max(1,round(image.width*scale)),max(1,round(image.height*scale))))
                    sheet.paste(image,(35,y+offset));draw.text((5,y+offset+18),arm[0].upper(),font=font,fill='black')
            sheet.save(directory/f'sheet{start//5+1:02d}.png')


def harm():
    import torch
    sys.path.insert(0,str(prior.OCR));sys.path.insert(0,str(prior.OCR/'train'))
    from eval_cer import evaluate,load_checkpoint
    from data import collate_strips
    from cer import load_codec
    from bench.o4b_models import strip
    from model import amp_dtype_for
    from ckpt_io import load_safetensors
    from torch.utils.data import DataLoader
    torch.set_num_threads(4);torch.set_num_interop_threads(1);torch.manual_seed(20261017)
    device=torch.device('cpu');checkpoint=prior.OCR/'out/e4/wave1a/job01/runs/ctrl_s0/best.pt'
    weights=checkpoint.with_suffix('.safetensors');codec_path=prior.OCR/'codec/v1.json'
    expected=next(r for r in prior.read_json(prior.OCR/'out/e4/wave1a_readback/sha256_comparison.json')['files']
                  if r['path']=='out/e4/wave1a/job01/runs/ctrl_s0/best.pt')
    assert prior.file_sha256(checkpoint)==expected['remote_sha256']==expected['local_sha256']
    assert expected['remote_sha256'].startswith('e20cd6cd'),'wrong E4 ctrl_s0 checkpoint'
    codec=load_codec(str(codec_path));model,meta=load_checkpoint(str(weights),codec,device)
    safe_sd,_=load_safetensors(str(weights))
    with torch.serialization.safe_globals([np._core.multiarray._reconstruct,np.ndarray,np.dtype,type(np.dtype(np.uint32))]):
        full=torch.load(checkpoint,map_location='cpu',weights_only=True)
    assert safe_sd.keys()==full['model'].keys() and all(torch.equal(safe_sd[k],full['model'][k]) for k in safe_sd)
    del full,safe_sd
    records=prior.rows(OUT/'f2/records.jsonl');frozen=prior.read_json(OUT/'params.json')
    assert len(records)==5770 and frozen['source_hashes']==source_hashes()
    binding=dict(device='cpu',threads=4,batch_size=16,seed=20261017,model_sha256=prior.file_sha256(checkpoint),
        weights_sha256=prior.file_sha256(weights),safetensors_tensor_equality_to_verified_pt=True,
        codec_sha256=prior.file_sha256(codec_path),checkpoint_metadata=meta,
        evaluator_sha256=prior.file_sha256(prior.OCR/'train/eval_cer.py'),
        preprocessing_sha256=prior.file_sha256(prior.OCR/'bench/o4b_models.py'),
        collator_sha256=prior.file_sha256(prior.OCR/'train/data.py'),
        records_sha256=prior.file_sha256(OUT/'f2/records.jsonl'),params_sha256=frozen['params_sha256'],
        frozen_utc=frozen['frozen_utc'],started_utc=datetime.now(timezone.utc).isoformat(),
        unique_f2_lines=len(records),network='OFF; socket connections forbidden',metric='strict NFD codepoint corpus CER',
        adapter='unchanged evaluate core + o4b_models.strip + collate_strips; raw uint8 48-pixel strips',
        evaluate_run_not_used='requires CUDA training runtime equality; this is a CPU readout')
    prior.write_json(OUT/'harm/binding.json',binding)
    mapping={ch:i for i,ch in enumerate(codec.atom_by_id) if i}
    for arm in ('original','masked'):
        path=OUT/'harm'/f'{arm}.jsonl';assert not path.exists(),'do not reuse unverified predictions'
        samples=[]
        for r in records:
            crop_path=OUT/r[f'{arm}_path'];assert prior.file_sha256(crop_path)==r[f'{arm}_sha256']
            with Image.open(crop_path) as image:arr=np.clip(np.rint(strip(image)*255),0,255).astype(np.uint8)
            text=unicodedata.normalize('NFD',r['google_text']);assert not (set(text)-mapping.keys())
            samples.append(dict(image=arr,width=arr.shape[1],label=np.array([mapping[c] for c in text],dtype=np.int64),script_class=r['stratum'],id=r['id']))
        order=sorted(range(len(samples)),key=lambda i:samples[i]['width'])
        stream=path.open('w');counter=iter(order);start=time.monotonic();count=0
        def collect(ref,hyp,edits):
            nonlocal count
            r=records[next(counter)];stream.write(json.dumps(dict(id=r['id'],stratum=r['stratum'],ref=ref,prediction=hyp,edits=edits,ref_len=len(ref)),ensure_ascii=False)+'\n')
            count+=1
            if count%100==0:
                stream.flush();print('HARM',arm,count,'/',len(records),'seconds',round(time.monotonic()-start,1),flush=True)
        loader=DataLoader([samples[i] for i in order],batch_size=16,shuffle=False,collate_fn=collate_strips,num_workers=0)
        result=evaluate(model,loader,codec,device,amp_dtype=amp_dtype_for(device),per_script=True,line_callback=collect)
        stream.close();assert result['n_lines']==len(records)
        prior.write_json(OUT/'harm'/f'{arm}.receipt.json',dict(binding=binding,result=result,predictions_sha256=prior.file_sha256(path),seconds=time.monotonic()-start))
        print('HARM complete',arm,result['cer'],flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['dev','materialize','sheets','harm']);args=parser.parse_args()
    {'dev':lambda:develop_or_materialize(True),'materialize':lambda:develop_or_materialize(False),'sheets':sheets,'harm':harm}[args.stage]()
