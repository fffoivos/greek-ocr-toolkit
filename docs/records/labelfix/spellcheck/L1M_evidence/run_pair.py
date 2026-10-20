"""L1M paired CPU audit; frozen imports, fixed readers, no release/code edits.

Run from this checkout with the original toolkit's existing Python environment:
  PYTHONDONTWRITEBYTECODE=1 .../greek-ocr-toolkit/.venv/bin/python .../run_pair.py
Use --sample vouli to append that stratum when sourcing is complete.
"""
import argparse
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
WORK=HERE.parents[3]
FROZEN=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-spellcheck')
HARVEST=Path('/Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/docs/harvest')
SOURCING=Path('/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/v2_masked')
sys.path.insert(0,str(FROZEN))
import numpy as np
import scipy
from PIL import Image
from greekocr.labelfix import reading, ink, release_gate as gate, case, markshape
from greekocr.labelfix.ctc_align import Alignment
from scripts.labelfix.clariden.l1_common import overlay

METRICS=('localisation_unknown','segmentation_uncertain','clipped_top','clipped_bottom','unnamed')
MODES=('ENSEMBLE_AB','PRESENCE')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def writejson(path,data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')


def dumpgz(path,data):
    with gzip.open(path,'wt') as f:
        for row in data:f.write(json.dumps(row,ensure_ascii=False)+'\n')


def selected_sources(ids):
    result={}
    for line in (HARVEST/'collection/v2/import_real_v2_train.jsonl').open():
        r=json.loads(line)
        if r['id'] in ids:result[r['id']]=r
    assert set(result)==set(ids)
    return result


def ensure_alignments(sources):
    path=HERE/'c1_selected_alignments.jsonl.gz'
    found={}
    if path.exists():
        found={r['id']:r for r in map(json.loads,gzip.open(path,'rt'))}
    wanted=set(sources)-set(found)
    if wanted:
        lookup={r['crop']:k for k,r in sources.items() if k in wanted}
        for line in gzip.open(WORK/'.cache/labelfix/clariden/C1_alignments.jsonl.gz','rt'):
            crop=json.JSONDecoder().raw_decode(line[line.index(':')+1:].lstrip())[0]
            if crop in lookup:
                key=lookup[crop];found[key]=dict(id=key,**json.loads(line))
        dumpgz(path,[found[k] for k in sorted(found)])
    return found


def source_binding():
    assert gate.POLICY=='sf4-release-v1'
    head=subprocess.check_output(['git','--no-optional-locks','rev-parse','HEAD'],cwd=FROZEN,text=True).strip()
    assert head=='c6064650fa5451cbc3bd13197d7a31c0d3bbf33d',head
    paths={Path(m.__file__).resolve() for m in list(sys.modules.values())
           if getattr(m,'__file__',None) and str(Path(m.__file__).resolve()).startswith(str(FROZEN)+'/')
           and str(m.__file__).endswith('.py')}
    for asset in ('docs/labelfix/markshape_model_S4.json','docs/labelfix/case_model_S5.json'):
        paths.add(FROZEN/asset)
    hashes={}
    for p in sorted(paths):
        relative=str(p.relative_to(FROZEN))
        committed=subprocess.check_output(['git','--no-optional-locks','show',head+':'+relative],cwd=FROZEN)
        assert committed==p.read_bytes(),('frozen source differs from commit',relative)
        hashes[relative]=sha(p)
    return dict(commit=head,root=str(FROZEN),policy=gate.policy_binding(),sources=hashes,
        python=sys.version,executable=sys.executable,numpy=np.__version__,scipy=scipy.__version__)


def slotmetrics(serial):
    c=Counter({k:0 for k in METRICS}); c.update(slots=len(serial['slots']))
    hist=Counter()
    for s in serial['slots']:
        for k in METRICS:
            c[k]+=int(bool(s.get('evidence',{}).get(k))) if k.startswith('clipped_') else int(bool(s.get(k)))
        hist[len(s.get('component_ids',[]))]+=1
        c['component_assignments']+=len(s.get('component_ids',[]))
        c['unnamed_blobs']+=len(s.get('unnamed',[]))
    return dict(c,components_per_letter_histogram=dict(sorted(hist.items())))


def decision_projection(result):
    return dict(text=result['text'],hold_slots=result['hold_slots'])


def borders(line_id, sourcing, ci, masked_ci, before, after, original, masked):
    """Every raw clipping flag -> exact edge pixels, native connected blobs.

    No ownership is inferred from removal or survival. Sourcing supplies no
    pixel ownership/curve maps in this handoff, so attribution is undecidable.
    """
    flags=[]; blobs={}; amap={s['start']:s for s in after['slots']}
    for s in before['slots']:
        ev=s.get('evidence',{})
        if not ev:continue
        b0,b1=ev['body']
        # Exact clipping predicate in frozen ink.mark_evidence: uses crop xh,
        # calculated before the optional word/capital evidence-band override.
        lo=max(0,int(math.floor(b0-.1*ci.xh)))
        hi=min(ci.width,int(math.ceil(b1+.2*ci.xh)))
        for direction,y in [('top',0),('bottom',ci.height-1)]:
            if not ev.get('clipped_'+direction):continue
            xs=np.flatnonzero(ci.ink[y,lo:hi])+lo
            assert len(xs),(line_id,s['start'],direction,'clipping window reconstruction')
            ids=sorted(set(int(v) for v in ci.labels[y,xs]))
            ids=[v for v in ids if v>0]
            keys=[]
            for label in ids:
                key=f'{direction}:{label}';keys.append(key)
                if key not in blobs:
                    yy,xx=np.nonzero(ci.labels==label)
                    edge_xs=xx[yy==y]
                    gone=~masked_ci.ink[yy,xx]
                    blobs[key]=dict(id=line_id,key=key,edge=direction,label=label,
                        bbox=[int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1],
                        pixels=len(xx),edge_x=edge_xs.tolist(),native_pixels=list(zip(xx.tolist(),yy.tolist())),
                        pixels_no_longer_ink=int(gone.sum()),edge_pixels_no_longer_ink=int((~masked_ci.ink[y,edge_xs]).sum()),
                        attribution='undecidable',attribution_basis='no saved pixel ownership or Voronoi curves in sourcing handoff')
            flags.append(dict(id=line_id,start=s['start'],base=s['base'],edge=direction,
                window=[lo,hi],border_ink_x=xs.tolist(),blob_keys=keys,
                attribution='undecidable',persists=bool(amap.get(s['start'],{}).get('evidence',{}).get('clipped_'+direction)),
                audit_status=sourcing['audit_status']))
    old={(f['start'],f['edge']) for f in flags}
    new=[dict(start=s['start'],base=s['base'],edge=d,attribution='undecidable')
         for s in after['slots'] for d in ('top','bottom')
         if s.get('evidence',{}).get('clipped_'+d) and (s['start'],d) not in old]
    return flags,list(blobs.values()),new


def run(sample, refresh=False):
    started=time.monotonic()
    root=SOURCING/('l1e_sample_vouli' if sample=='vouli' else 'l1e_sample_r3')
    receipt_path=root/'receipt.json'
    if not receipt_path.exists():
        print('vouli pending: sourcing receipt absent' if sample=='vouli' else 'STOP: sourcing receipt absent')
        return False
    receipt=json.loads(receipt_path.read_text())
    expected=60 if sample=='vouli' else 200
    if receipt.get('status')!='completed' or receipt.get('completed_pages')!=receipt.get('selected_pages'):
        if sample=='vouli':
            print('vouli pending: sourcing receipt incomplete');return False
        raise ValueError('STOP: incomplete 200-line sourcing receipt')
    suffix='_vouli' if sample=='vouli' else ''
    ids=(HERE.parent/f'L1M_masking_sample_ids{suffix}.txt').read_text().split()
    assert len(ids)==len(set(ids))==expected
    staging={r['id']:r for r in map(json.loads,(root/'lines.jsonl').open())}
    assert set(staging)==set(ids)
    assert sha(root/'lines.jsonl')==receipt['lines_sha256']
    sources=selected_sources(ids)
    alignments=ensure_alignments(sources)
    # Fetch is stdlib only; explicitly load the evidence helper from this folder.
    sys.path.insert(0,str(HERE))
    from fetch_selected import fetch
    remote_path=fetch(sample)
    remote=json.loads(gzip.decompress(remote_path.read_bytes()))
    for key,r in remote['alignments'].items():alignments[key]=dict(id=key,**r)
    assert all(k in alignments for k in ids)
    case.configure_model(FROZEN/'docs/labelfix/case_model_S5.json')
    model=markshape.load_model(FROZEN/'docs/labelfix/markshape_model_S4.json')
    initial_binding=source_binding()
    out=HERE/sample;out.mkdir(exist_ok=True)
    if (out/'receipt.json').exists() and not refresh:
        print('Existing completed sample; use --refresh for an intentional rerun');return True
    (out/'pixels').mkdir(exist_ok=True)
    binding=dict(detector='s6',r1_sha256='719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636',
                 policy_sha256=initial_binding['policy']['sha256'])
    results=[];details=[];slotrows=[];blobrows=[];flagrows=[]
    for i,key in enumerate(ids,1):
        sr=staging[key];runtime=remote['runtime'][key];al=Alignment.from_record(alignments[key]['alignment'])
        assert runtime['recogniser_nfd']==al.prediction,(key,'recogniser/alignment differs')
        assert runtime['historical_A_verified']
        p=Path(sr['original_path']);q=root/sr['masked_path']
        assert sha(p)==sr['original_crop_sha256'] and sha(q)==sr['masked_sha256']
        with Image.open(p) as im:original=np.array(im.convert('L'))
        with Image.open(q) as im:masked=np.array(im.convert('L'))
        assert original.shape==masked.shape
        if sr['match_status']!='ok':assert np.array_equal(original,masked)
        images=[original,masked];cis=[];serials=[];modes={};overlays={};counts={};fixed_digests=[]
        for name,arr in zip(('original','masked'),images):
            ci=ink.analyse(Image.fromarray(arr));cis.append(ci)
            raw=reading.read_ink(ci,al.prediction,al,model,filtered=False)
            serial=gate.serialize(raw);serials.append(serial)
            rr={k:deepcopy(v) for k,v in runtime.items() if k not in ('evidence_sha256','modes','historical_A_verified')}
            rr['detector']=serial
            # Fixed readers include predictions, all peer coverage, and saved context/K1 inputs.
            fixed={k:rr.get(k) for k in ('recogniser_text','recogniser_nfd','r1_predictions','coverage','peer_predictions','peer_coverage','k1_flags')}
            fixed_digests.append(hashlib.sha256(json.dumps(fixed,sort_keys=True,ensure_ascii=False).encode()).hexdigest())
            modes[name]={mode:gate.compose_runtime(rr,mode) for mode in MODES}
            overlays[name]={mode:overlay(sources[key],rr,mode,binding) for mode in MODES}
            counts[name]=slotmetrics(serial)
        assert fixed_digests[0]==fixed_digests[1]
        flags,blobs,new_flags=borders(key,sr,*cis,*serials,original,masked)
        flagrows.extend(flags);blobrows.extend(blobs)
        saved_modes={mode:gate.compose_runtime(runtime,mode) for mode in MODES}
        parity={mode:decision_projection(saved_modes[mode])==decision_projection(modes['original'][mode]) for mode in MODES}
        oldslots={s['start']:s for s in serials[0]['slots']};newslots={s['start']:s for s in serials[1]['slots']}
        newloc=[start for start,s in newslots.items() if s.get('localisation_unknown') and not oldslots.get(start,{}).get('localisation_unknown')]
        foreign=sr.get('foreign_pixels_removed')
        group='matching_failed' if sr['match_status']!='ok' else 'unknown' if foreign is None else 'none' if foreign==0 else 'small' if foreign<=100 else 'large'
        record=dict(id=key,wave=sr['wave'],sample=sample,source=sr,foreign_group=group,
            counts=counts,status={name:{mode:overlays[name][mode]['status'] for mode in MODES} for name in ('original','masked')},
            reasons={name:{mode:dict(Counter(h['detail'] for h in overlays[name][mode]['hold_slots'])) for mode in MODES} for name in ('original','masked')},
            reason_sets={name:{mode:sorted({h['detail'] for h in overlays[name][mode]['hold_slots']}) for mode in MODES} for name in ('original','masked')},
            saved_original_gate_parity=parity,fixed_reader_sha256=fixed_digests[0],
            new_localisation_starts=newloc,new_clipping_flags=new_flags,
            binary_ink_pixels=[int(ci.ink.sum()) for ci in cis],
            changed_pixels=int((original!=masked).sum()))
        results.append(record)
        details.append(dict(id=key,detector=dict(zip(('original','masked'),serials)),modes=modes,overlays=overlays))
        for name,serial in zip(('original','masked'),serials):
            for s in serial['slots']:
                slotrows.append(dict(id=key,wave=sr['wave'],variant=name,start=s['start'],base=s['base'],
                    component_ids=s.get('component_ids',[]),bbox=s.get('bbox'),n_components=len(s.get('component_ids',[])),
                    **{k:bool(s.get('evidence',{}).get(k)) if k.startswith('clipped_') else bool(s.get(k)) for k in METRICS}))
        np.savez_compressed(out/'pixels'/f'{key}.npz',original_ink=cis[0].ink,masked_ink=cis[1].ink,
            original_labels=cis[0].labels,masked_labels=cis[1].labels,changed_pixels=original!=masked)
        if i%20==0:print(f'{sample}: {i}/{len(ids)} paired lines; {time.monotonic()-started:.1f}s',flush=True)
    dumpgz(out/'lines.jsonl.gz',results);dumpgz(out/'details.jsonl.gz',details)
    dumpgz(out/'slots.jsonl.gz',slotrows);dumpgz(out/'border_flags.jsonl.gz',flagrows);dumpgz(out/'border_blobs.jsonl.gz',blobrows)
    writejson(out/'source_selected.json',sources)
    # Re-hash imported frozen sources and original crop bytes after all processing.
    final_binding=source_binding()
    assert all(final_binding['sources'][p]==digest for p,digest in initial_binding['sources'].items())
    assert all(sha(Path(staging[k]['original_path']))==staging[k]['original_crop_sha256'] for k in ids)
    writejson(out/'receipt.json',dict(schema='l1m-paired-v1',complete=True,lines=len(ids),sample=sample,
        seconds=time.monotonic()-started,source_binding=final_binding,remote=sha(remote_path),
        staging_root=str(root),staging_receipt_sha256=sha(receipt_path),staging_lines_sha256=sha(root/'lines.jsonl'),
        sample_ids_sha256=sha(HERE.parent/f'L1M_masking_sample_ids{suffix}.txt'),
        outputs={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='receipt.json'},
        own_foreign_pixel_masks_available=False,ownership_limitation='Summaries and fill component IDs only; all blob attributions undecidable.',
        frozen_sources_unchanged=True,original_crops_unchanged=True,reader_runs=0,workers=1,threads=1,
        network='Clariden selected evidence only',git_writes=0))
    return True


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--sample',choices=['200','vouli'],default='200');ap.add_argument('--refresh',action='store_true')
    args=ap.parse_args()
    if run(args.sample,args.refresh):
        subprocess.run([sys.executable,str(HERE/'build_report.py')],check=True)
