"""Read-only L1-v0 window audit; optional byte-exact repair into a NEW tree."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
import numpy as np
from scripts.labelfix.clariden.r1_common import LETTERS, rows, sha256, write_json


def checked(path, digest):
    path=Path(path)
    if sha256(path)!=digest:raise ValueError('hash mismatch: '+str(path))
    return path


def shard_inputs(data, number):
    prefix=Path(data)/f'shard-{number:05d}'
    return {k:Path(str(prefix)+suffix) for k,suffix in
            [('receipt','-receipt.json'),('detector','-detector.jsonl.gz'),
             ('samples','-samples.json'),('wide','-wide.npy')]}


def repair_windows(data, number, historical, binding_dir, crop_root, layout, out):
    """Use unchanged L1 extract_line, original crops and original cached spans.

    A repair must reproduce the historical samples, coverage AND wide hash.
    Never write into L1-v0, even when a historical file is missing.
    """
    from PIL import Image
    from scripts.labelfix.clariden.r1_extract import extract_line
    from scripts.labelfix.clariden.r1_common import crop_key,crop_path
    paths=shard_inputs(data,number)
    recs=list(rows(paths['detector'])); wanted={r['id']:i for i,r in enumerate(recs)}
    selection={r['crop']:r for r in rows(Path(binding_dir)/'selection.jsonl') if r['id'] in wanted}
    top=json.loads((Path(data)/'detector_receipt.json').read_text())
    alignments={}
    for name,digest in top['alignment_sha256'].items():
        checked(name,digest)
        for row in rows(name):
            key=crop_key(row['crop'])
            if key in selection:
                if key in alignments:raise ValueError('duplicate repair alignment')
                alignments[key]=row['alignment']
    win=[]; samples=[]
    byid={r['id']:r for r in selection.values()}
    for i,r in enumerate(recs):
        source=byid[r['id']]; ar=alignments[source['crop']]
        with Image.open(crop_path(source['crop'],crop_root,layout)) as image:
            ss,wide,_,_,cov,size=extract_line(dict(id=r['id'],recogniser_text=ar['prediction'],_line=i),ar,image.convert('L'),evaluation=True)
        if cov!=r['coverage'] or size!=r['font_size']:raise ValueError('repair extraction differs')
        samples.extend(dict(line=i,start=s[3],letter=s[4],mask=s[7][0]) for s in ss);win.extend(wide)
    if samples!=json.loads(paths['samples'].read_text()):raise ValueError('repair samples differ')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    dest=out/paths['wide'].name
    np.save(dest,np.asarray(win,dtype=np.uint8).reshape(-1,64,128),allow_pickle=False)
    checked(dest,historical['sha256'][dest.name])
    return dest


def audit_shard(task):
    data,entry,repair,options=task
    paths=shard_inputs(data,entry['shard']); checked(paths['receipt'],options['receipt_hashes'][entry['shard']])
    receipt=json.loads(paths['receipt'].read_text())
    if not receipt.get('complete') or receipt!=entry:raise ValueError('inconsistent detector shard receipt')
    missing=[]
    for name,digest in receipt['sha256'].items():
        p=Path(data)/name
        if not p.exists() and name==paths['wide'].name:missing.append(name)
        else:checked(p,digest)
    wide=paths['wide']
    if missing and repair:
        wide=repair_windows(data,entry['shard'],receipt,options['binding_dir'],options['crop_root'],options['layout'],options['repair_out'])
    samples=json.loads(paths['samples'].read_text()); records=list(rows(paths['detector']))
    if len(records)!=entry['lines'] or len(samples)!=entry['windows']:raise ValueError('shard count mismatch')
    actual=[(s['line'],s['start'],LETTERS[s['letter']]) for s in samples]
    expected=[(i,c['start'],c['base']) for i,r in enumerate(records) for c in r['coverage'] if c['scored']]
    if len(actual)!=len(set(actual)) or actual!=expected:raise ValueError('windows do not cover every scored A slot')
    if wide.exists():
        a=np.load(wide,mmap_mode='r',allow_pickle=False)
        if a.dtype!=np.uint8 or a.shape!=(len(samples),64,128):raise ValueError('wide shape/dtype mismatch')
    if any(not (0<=s['line']<len(records) and len(s['mask'])==2 and s['mask'][1]>s['mask'][0]) for s in samples):
        raise ValueError('invalid sample line or span mask')
    return dict(shard=entry['shard'],lines=len(records),windows=len(samples),ids=[r['id'] for r in records],
                missing=missing,repaired=bool(missing and repair),wide=str(wide),receipt_sha256=sha256(paths['receipt']))


def audit(data, selection, out, *, workers=8, repair=False, binding_dir=None,crop_root=None,layout='e3'):
    started=time.monotonic();data=Path(data);out=Path(out)
    top=json.loads((data/'detector_receipt.json').read_text())
    if not top.get('complete') or top['selection_sha256']!=sha256(selection):raise ValueError('detector selection not bound')
    run_path=data.parent/'run_receipt.json';run=json.loads(run_path.read_text())
    if not run.get('complete'):raise ValueError('incomplete L1-v0')
    checked(data/'detector_receipt.json',run['step_receipts']['detector/detector_receipt.json'])
    hashes={e['shard']:run['step_receipts'][f'detector/shard-{e["shard"]:05d}-receipt.json'] for e in top['shards']}
    options=dict(receipt_hashes=hashes,binding_dir=binding_dir,crop_root=crop_root,layout=layout,repair_out=str(out.parent/'repaired_windows'))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results=list(pool.map(audit_shard,[(str(data),e,repair,options) for e in top['shards']]))
    ids=[i for r in results for i in r.pop('ids')];selected=[r['id'] for r in rows(selection)]
    if len(ids)!=len(set(ids)) or set(ids)!=set(selected):raise ValueError('window line identity differs from selection')
    missing=sum(bool(r['missing']) for r in results)
    result=dict(schema='l1e-window-audit-v1',complete=not missing or repair,lines=len(ids),windows=sum(r['windows'] for r in results),
        shards=len(results),missing_shards=missing,repaired_shards=sum(r['repaired'] for r in results),all_A_scored_windows_accounted=True,
        detector_receipt_sha256=sha256(data/'detector_receipt.json'),run_receipt_sha256=sha256(run_path),
        selection_sha256=sha256(selection),elapsed_seconds=time.monotonic()-started,entries=results)
    out.parent.mkdir(parents=True,exist_ok=True);write_json(out,result)
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for k in ('data','selection','out'):ap.add_argument('--'+k,type=Path,required=True)
    ap.add_argument('--workers',type=int,default=8)
    a=ap.parse_args();r=audit(a.data,a.selection,a.out,workers=a.workers)
    print(json.dumps({k:v for k,v in r.items() if k!='entries'}))
    if not r['complete']:raise SystemExit('missing windows; job must repair before inference')


if __name__=='__main__':main()
