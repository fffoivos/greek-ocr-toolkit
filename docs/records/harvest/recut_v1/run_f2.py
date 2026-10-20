"""Offline F2-only T6a development, freeze, native recuts, and paired readout.

Run from worktree root with PYTHONDONTWRITEBYTECODE=1 .venv/bin/python ...
Network connections are forbidden within this process. No W1 path is accessed.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import time
import unicodedata

import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PROJECTS = ROOT.parent
F2 = PROJECTS/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest'
FEATURES = F2/'screen_v1/features.jsonl'
BLIND = F2/'blind_checks_v1/v2'
OCR = PROJECTS/'greek-page-ocr'
SOURCES = ('gazette_modern', 'lekythos_poly1900', 'kosmopolis_poly1900', 'ia_greek_latin')
sys.path.insert(0, str(ROOT))
from greekocr.glyphs.vertical_recut import TightenParams, band_from_record, tighten_box
from greekocr.ops.receipts import file_sha256


def no_network(*args, **kwargs):
    raise RuntimeError('T6a network OFF: socket connections forbidden')


socket.create_connection = no_network
socket.socket.connect = no_network
socket.socket.connect_ex = no_network


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ASSEMBLY = load_module('t6a_assembly', F2/'screen_v1/assembly_fix.py')
OWN = load_module('t6a_ownership', F2/'sample_v1/gr/reference/greekocr/labelfix/geometry/ownership.py')


def rows(path):
    with Path(path).open() as stream:
        return [json.loads(s) for s in stream if s.strip()]


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def write_rows(path, values):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w') as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False, allow_nan=False)+'\n')


def stratum(r):
    if not r['fixed_usable'] or r['text_exclusions']:
        return None
    if r['source'] == 'government-gazette' and r['primary_class'] == 'modern_scanned' and int(str(r.get('year') or 0)[:4]) >= 1982:
        return SOURCES[0]
    if r['source'] == 'lekythos' and r['primary_class'] == 'poly1900':
        return SOURCES[1]
    if r['source'] == 'kosmopolis' and r['primary_class'] == 'poly1900':
        return SOURCES[2]
    if r['track'] == 'ia' and r['source'] == 'greek_latin' and r['primary_class'] == 'mixed_greek_latin':
        return SOURCES[3]
    return None


def bind():
    rr = [dict(r, stratum=stratum(r)) for r in rows(FEATURES) if stratum(r)]
    assert len(rr) <= 10000
    cards = {}
    inputs = {str(FEATURES): file_sha256(FEATURES)}
    for source in SOURCES:
        kp, vp = BLIND/f'{source}_key.json', BLIND/f'{source}_out.jsonl'
        for path in (kp, vp, BLIND/source/'cards.jsonl'):
            # Bind to the requested development revision, not an unpinned live edit.
            relative = path.relative_to(F2.parents[1])
            expected = subprocess.check_output(['git', 'show', '2f34ed52:'+str(relative)], cwd=ROOT)
            assert hashlib.sha256(expected).hexdigest() == file_sha256(path), str(path)
            inputs[str(path)] = file_sha256(path)
        key = read_json(kp)
        for verdict in rows(vp):
            ident = key[verdict['card_id']]['line_id']
            cards[ident] = dict(verdict, stratum=source)
    assert len(cards) == 160 and set(cards) <= {r['id'] for r in rr}
    for r in rr:
        r['dev'] = cards.get(r['id'])
    return rr, inputs


def page_bundle(group):
    first = group[0]
    base = Path(first['crop_page_path']).parents[2]
    page_id = first['page_id']
    metadata = read_json(base/'receipts/pages'/f'{page_id}.json')
    cache = base/'cache/g1b'/page_id
    receipt = read_json(cache/'receipt.json')
    paths = {Path(first['crop_page_path']): receipt['source_sha256'],
             cache/'detector.json.gz': receipt['geometry_sha256'],
             cache/'ink.png': receipt['mask_sha256'],
             cache/'labels.npz': receipt['labels_sha256']}
    assert metadata['image_sha256'] == receipt['source_sha256']
    for path, digest in paths.items():
        assert file_sha256(path) == digest, 'cache custody: '+str(path)
    data = json.loads(gzip.decompress((cache/'detector.json.gz').read_bytes()))
    with Image.open(cache/'ink.png') as image:
        ink = np.asarray(image).astype(bool)
    with np.load(cache/'labels.npz') as archive:
        labels = archive['labels']
    prepared = {r['row_id']: OWN.prepare_row(r, ink, labels) for r in data['rows']}
    native = Image.open(first['crop_page_path']).copy()
    parsed = read_json(base/'google/parsed/docai'/f"{metadata['image_sha256']}.json")
    raw_path = Path(parsed['raw_json_path'])
    # Some historical path roots moved; use only an existing bound response.
    if not raw_path.exists():
        candidates = list((base/'google').rglob(raw_path.name))
        assert len(candidates) == 1, str(raw_path)
        raw_path = candidates[0]
    raw_bytes = raw_path.read_bytes()
    provider_receipt = read_json(raw_path.parent/'cache.json')
    assert hashlib.sha256(raw_bytes).hexdigest() == provider_receipt['raw_sha256']
    raw = json.loads(raw_bytes)
    tokens, _, _ = ASSEMBLY.page_tokens(raw['document'], native.size)
    membership = defaultdict(set)
    for i, line in enumerate(raw['document']['pages'][0]['lines']):
        ss = ASSEMBLY.spans(line)
        for t in tokens:
            if t['spans'] and all(any(a <= x < y <= b for a,b in ss) for x,y in t['spans']):
                membership[i].add(t['token_id'])
    original = {r['id']: r for r in rows(base/'bulk/lines'/f'{page_id}.jsonl')}
    provenance = dict(page_id=page_id, source=str(Path(first['crop_page_path'])),
                      source_sha256=receipt['source_sha256'], cache=str(cache),
                      cache_receipt_sha256=file_sha256(cache/'receipt.json'),
                      detector_sha256=receipt['detector_sha256'],
                      raw_response=str(raw_path), raw_sha256=provider_receipt['raw_sha256'],
                      geometry_sha256=receipt['geometry_sha256'],
                      labels_sha256=receipt['labels_sha256'], mask_sha256=receipt['mask_sha256'])
    return native, prepared, original, tokens, membership, provenance


def recut_one(r, prepared, original, tokens, membership, params):
    old = original[r['id']]
    assert old['crop_bbox'] == r['crop_bbox']
    row_id = old['ownership'].get('row_id')
    row = prepared.get(row_id) if old['ownership']['ownership_status'] == 'owned' else None
    band = band_from_record(row) if row else None
    own_tokens = membership[r['docai_line_index']]
    neighbours = [t['bbox'] for t in tokens if t['token_id'] not in own_tokens and t['bbox'] is not None]
    coordinates = (row['_y'], row['_x']) if row else None
    result = tighten_box(r['crop_bbox'], band, neighbours, params=params, own_pixels=coordinates)
    # Independent native mask accounting; foreign text bodies are separate from specks/rules.
    own_before = result.own_pixels
    own_lost = result.proposed_own_pixels_lost if result.changed else 0
    foreign_before = foreign_after = bodies_before = bodies_after = 0
    x0,y0,x1,y1 = result.old_box
    for other in prepared.values():
        if row is None or other['row_id'] == row_id:
            continue
        before = OWN.box_hits(other, result.old_box)
        after = OWN.box_hits(other, result.new_box)
        foreign_before += int(before.sum()); foreign_after += int(after.sum())
        if before.any():
            yy, xx = other['_y'], other['_x']-other['x0']
            body = (yy >= other['meanline'][xx]) & (yy < other['baseline'][xx])
            bodies_before += int((before & body).sum()); bodies_after += int((after & body).sum())
    record = dict(asdict(result), id=r['id'], page_id=r['page_id'], stratum=r['stratum'],
                  google_text=r['label_after_conventions'], original_page=r['crop_page_path'],
                  dev=r['dev'], screen_merged=bool(r['screen_reject']),
                  geometry_clean=r['geometry_positive'] is False and not r['screen_reject'],
                  guide_source=band.source if band else None, row_id=row_id,
                  before_height_xh=(y1-y0)/result.xheight if result.xheight else None,
                  after_height_xh=(result.new_box[3]-result.new_box[1])/result.xheight if result.xheight else None,
                  changed=result.changed, own_pixels_lost=own_lost,
                  foreign_pixels_before=foreign_before, foreign_pixels_after=foreign_after,
                  neighbour_body_pixels_before=bodies_before, neighbour_body_pixels_after=bodies_after)
    return record


def dev_summary(records):
    out = {}
    for source in (*SOURCES, 'overall'):
        rr = [r for r in records if source == 'overall' or r['stratum'] == source]
        n = [r for r in rr if r['dev']['crop_ok']=='n']
        y = [r for r in rr if r['dev']['crop_ok']=='y']
        out[source] = dict(lines=len(rr), changed=sum(r['changed'] for r in rr),
            before_median_xh=float(np.median([r['before_height_xh'] for r in rr if r['before_height_xh'] is not None])),
            after_median_xh=float(np.median([r['after_height_xh'] for r in rr if r['after_height_xh'] is not None])),
            crop_n=len(n), crop_n_body_present_before=sum(r['neighbour_body_pixels_before']>0 for r in n),
            crop_n_body_removed=sum(r['neighbour_body_pixels_before']>0 and r['neighbour_body_pixels_after']==0 for r in n),
            crop_n_body_pixels_before=sum(r['neighbour_body_pixels_before'] for r in n),
            crop_n_body_pixels_after=sum(r['neighbour_body_pixels_after'] for r in n),
            crop_y=len(y), crop_y_own_pixels=sum(r['own_pixels'] or 0 for r in y),
            crop_y_own_pixels_lost=sum(r['own_pixels_lost'] or 0 for r in y),
            proposal_own_pixels_lost=sum(r['proposed_own_pixels_lost'] or 0 for r in rr),
            own_guard_refusals=sum(r['status']=='own_ink_guard' for r in rr),
            statuses=dict(Counter(r['status'] for r in rr)))
    return out


def develop():
    rr, inputs = bind()
    groups = defaultdict(list)
    for r in rr:
        if r['dev']:
            groups[r['page_id']].append(r)
    candidates = {(t,b): [] for t in (.1,.2,.3) for b in (.1,.2,.3)}
    provenance = []
    for i, group in enumerate(groups.values(),1):
        native, prepared, original, tokens, membership, prov = page_bundle(group)
        provenance.append(prov)
        for (top,bottom), records in candidates.items():
            params = TightenParams(top,bottom)
            records.extend(recut_one(r,prepared,original,tokens,membership,params) for r in group)
        print('DEV page', i, '/', len(groups), flush=True)
    summaries = {f'{t:.1f}/{b:.1f}': dev_summary(v) for (t,b),v in candidates.items()}
    # Choose only from physical development evidence, before any model inference.
    # Maximise n-card neighbour body removal, then minimise residual body pixels,
    # then prefer larger margins (conservative preservation) on tied evidence.
    best = max(candidates, key=lambda k: (summaries[f'{k[0]:.1f}/{k[1]:.1f}']['overall']['crop_n_body_removed'],
        -summaries[f'{k[0]:.1f}/{k[1]:.1f}']['overall']['crop_n_body_pixels_after'], sum(k), k[0]))
    params = TightenParams(*best)
    write_json(OUT/'dev/grid.json', summaries)
    write_rows(OUT/'dev/records.jsonl', candidates[best])
    write_rows(OUT/'dev/provenance.jsonl', provenance)
    frozen = dict(schema='t6a-frozen-1', frozen_utc=datetime.now(timezone.utc).isoformat(),
        params=asdict(params), params_sha256=params.sha256,
        canonical_utf8=params.canonical().decode(), dev_only=True,
        selection='n-card body removal count; fewer residual neighbour-body pixels; larger margin sum/top',
        inputs=inputs, grid_sha256=file_sha256(OUT/'dev/grid.json'),
        dev_records_sha256=file_sha256(OUT/'dev/records.jsonl'),
        cutter_sha256=file_sha256(ROOT/'greekocr/glyphs/vertical_recut.py'),
        w1_qualification='deferred to T6b; W1 not accessed', harm_inference_started=False)
    assert not (OUT/'params.json').exists(), 'do not overwrite a freeze'
    write_json(OUT/'params.json', frozen)
    print('FROZEN', params.sha256, best, flush=True)


def materialize():
    frozen = read_json(OUT/'params.json'); params = TightenParams(**frozen['params'])
    assert params.sha256 == frozen['params_sha256']
    assert frozen['cutter_sha256'] == file_sha256(ROOT/'greekocr/glyphs/vertical_recut.py')
    rr, inputs = bind()
    assert inputs == frozen['inputs']
    groups = defaultdict(list)
    for r in rr:
        groups[r['page_id']].append(r)
    records, provenance = [], []
    for i, group in enumerate(groups.values(),1):
        native, prepared, original, tokens, membership, prov = page_bundle(group)
        provenance.append(prov)
        for r in group:
            record = recut_one(r,prepared,original,tokens,membership,params)
            directory = OUT/'f2'/r['stratum']
            dest = directory/'recut'/f"{r['id']}.png"
            dest.parent.mkdir(parents=True, exist_ok=True)
            buffer = io.BytesIO()
            native.crop(tuple(record['old_box'])).save(buffer,format='PNG',compress_level=3)
            assert hashlib.sha256(buffer.getvalue()).hexdigest() == r['crop_sha256'], 'original crop custody: '+r['id']
            native.crop(tuple(record['new_box'])).save(dest,compress_level=3)
            record.update(recut_path=str(dest.relative_to(OUT)), recut_sha256=file_sha256(dest),
                          original_crop_sha256=r['crop_sha256'])
            records.append(record)
        print('RECUT page',i,'/',len(groups),'rows',len(records),flush=True)
    write_rows(OUT/'f2/records.jsonl', records)
    write_rows(OUT/'f2/provenance.jsonl', provenance)
    for source in SOURCES:
        write_rows(OUT/'f2'/source/'records.jsonl',[r for r in records if r['stratum']==source])
    print('RECUT complete',len(records),flush=True)


def make_sheets():
    records = rows(OUT/'dev/records.jsonl')
    all_records = {r['id']:r for r in rows(OUT/'f2/records.jsonl')}
    font = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 13)
    for source in SOURCES:
        rr = sorted([r for r in records if r['stratum']==source], key=lambda r:r['dev']['card_id'])
        directory = OUT/'dev/review'/source; directory.mkdir(parents=True,exist_ok=True)
        for start in range(0,len(rr),5):
            sheet = Image.new('RGB',(1600,125*5),'#e3e3e3'); draw=ImageDraw.Draw(sheet)
            for j,r in enumerate(rr[start:start+5]):
                full=all_records[r['id']]; old=Image.open(r['original_page']).crop(tuple(r['old_box']))
                new=Image.open(OUT/full['recut_path']);scale=min(1.5,1550/max(old.width,1),42/max(old.height,1))
                a=old.resize((max(1,round(old.width*scale)),max(1,round(old.height*scale))))
                b=new.resize((max(1,round(new.width*scale)),max(1,round(new.height*scale))))
                y=125*j
                draw.text((6,y+2),f"{r['dev']['card_id']} crop={r['dev']['crop_ok']} {r['status']} own proposal lost={r['proposed_own_pixels_lost']} neighbour body {r['neighbour_body_pixels_before']}->{r['neighbour_body_pixels_after']}",font=font,fill='black')
                sheet.paste(a,(25,y+24));sheet.paste(b,(25,y+78))
                draw.text((1,y+35),'A',font=font,fill='black');draw.text((1,y+89),'B',font=font,fill='black')
            sheet.save(directory/f'sheet{start//5+1:02d}.png')


def evaluate_harm():
    import torch
    sys.path.insert(0,str(OCR));sys.path.insert(0,str(OCR/'train'))
    from eval_cer import evaluate, load_checkpoint
    from data import collate_strips
    from cer import load_codec
    from bench.o4b_models import strip
    from model import amp_dtype_for
    from torch.utils.data import DataLoader
    torch.set_num_threads(4)
    torch.set_num_interop_threads(1)
    torch.manual_seed(20261017)
    device=torch.device('cpu')
    checkpoint=OCR/'out/e4/wave1a/job01/runs/ctrl_s0/best.pt'
    weights=checkpoint.with_suffix('.safetensors')
    readback=read_json(OCR/'out/e4/wave1a_readback/sha256_comparison.json')
    expected=next(r for r in readback['files'] if r['path']=='out/e4/wave1a/job01/runs/ctrl_s0/best.pt')
    assert file_sha256(checkpoint)==expected['remote_sha256']==expected['local_sha256']
    codec_path=OCR/'codec/v1.json';codec=load_codec(str(codec_path))
    model,meta=load_checkpoint(str(weights),codec,device)
    assert meta.get('codec_sha256') in (None,'',file_sha256(codec_path))
    # Bind the local safetensors to the sha-verified full checkpoint's model tensors.
    # weights_only=True cannot execute arbitrary pickle; safe NumPy RNG metadata allowlist only.
    from ckpt_io import load_safetensors
    safe_sd,_=load_safetensors(str(weights))
    with torch.serialization.safe_globals([np.core.multiarray._reconstruct,np.ndarray,np.dtype,
                                          type(np.dtype(np.uint32))]):
        full=torch.load(checkpoint,map_location='cpu',weights_only=True)
    assert safe_sd.keys()==full['model'].keys()
    assert all(torch.equal(safe_sd[k],full['model'][k]) for k in safe_sd)
    del full,safe_sd
    records=rows(OUT/'f2/records.jsonl')
    frozen=read_json(OUT/'params.json')
    assert frozen['cutter_sha256']==file_sha256(ROOT/'greekocr/glyphs/vertical_recut.py')
    binding=dict(device='cpu',threads=4,seed=20261017,model_sha256=file_sha256(checkpoint),
        weights_sha256=file_sha256(weights), safetensors_tensor_equality_to_verified_pt=True,
        codec_sha256=file_sha256(codec_path), checkpoint_metadata=meta,
        evaluator_sha256=file_sha256(OCR/'train/eval_cer.py'),
        preprocessing_sha256=file_sha256(OCR/'bench/o4b_models.py'),
        collator_sha256=file_sha256(OCR/'train/data.py'),
        params_sha256=frozen['params_sha256'], frozen_utc=frozen['frozen_utc'],
        started_utc=datetime.now(timezone.utc).isoformat(), network='socket connections forbidden',
        unique_f2_lines=len(records), paired_arm_observations=2*len(records),
        metric='strict NFD codepoint corpus CER; Google post-fix labels',
        adapter='unchanged train.eval_cer.evaluate + o4b_models.strip + data.collate_strips; raw strips converted to uint8',
        full_evaluate_run_not_used='requires CUDA training runtime equality; CPU readout uses its unchanged evaluator core')
    write_json(OUT/'harm/binding.json',binding)
    mapping={ch:i for i,ch in enumerate(codec.atom_by_id) if i}
    for arm in ('original','recut'):
        predictions=OUT/'harm'/f'{arm}.jsonl'
        # Resume complete arms only if bound data and model match.
        if predictions.exists() and len(rows(predictions))==len(records):
            print('HARM cached',arm,flush=True);continue
        samples=[]
        last_page_path, last_image = None, None
        for r in records:
            if arm=='original':
                if last_page_path != r['original_page']:
                    with Image.open(r['original_page']) as image: last_image=image.copy()
                    last_page_path=r['original_page']
                crop=last_image.crop(tuple(r['old_box']))
            else:
                assert file_sha256(OUT/r['recut_path'])==r['recut_sha256']
                crop=Image.open(OUT/r['recut_path'])
            arr=np.clip(np.rint(strip(crop)*255),0,255).astype(np.uint8)
            text=unicodedata.normalize('NFD',r['google_text'])
            unknown=set(text)-mapping.keys()
            assert not unknown,(r['id'],unknown)
            samples.append(dict(image=arr,width=arr.shape[1],label=np.array([mapping[c] for c in text],dtype=np.int64),script_class=r['stratum'],id=r['id']))
        # Width-bucket sorting changes neither the pairs nor the exact scorer inputs.
        order=sorted(range(len(samples)),key=lambda i:samples[i]['width'])
        stream=predictions.open('w');counter=iter(order);start=time.monotonic();count=0
        def collect(ref,hyp,edits):
            nonlocal count
            index=next(counter);r=records[index]
            stream.write(json.dumps(dict(id=r['id'],stratum=r['stratum'],ref=ref,prediction=hyp,edits=edits,ref_len=len(ref)),ensure_ascii=False)+'\n')
            count+=1
            if count%100==0:
                stream.flush();print('HARM',arm,count,'/',len(records),'seconds',round(time.monotonic()-start,1),flush=True)
        loader=DataLoader([samples[i] for i in order],batch_size=16,shuffle=False,collate_fn=collate_strips,num_workers=0)
        result=evaluate(model,loader,codec,device,amp_dtype=amp_dtype_for(device),per_script=True,line_callback=collect)
        stream.close()
        assert result['n_lines']==len(records)
        write_json(OUT/'harm'/f'{arm}.receipt.json',dict(binding=binding,result=result,predictions_sha256=file_sha256(predictions),seconds=time.monotonic()-start))
        print('HARM complete',arm,result['cer'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['develop','materialize','sheets','harm'])
    stage=parser.parse_args().stage
    {'develop':develop,'materialize':materialize,'sheets':make_sheets,'harm':evaluate_harm}[stage]()
