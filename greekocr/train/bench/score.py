#!/usr/bin/env python3
"""Score only a hash-sealed, owner-verified reference; never native candidate labels.

Prediction rows: {id, hyp} (no embedded reference trusted). A companion .seal.json
must bind reference bytes, verified status, count and every crop's SHA256.
"""
from __future__ import annotations
import argparse
import json
import platform
import time
import unicodedata as ud
from collections import defaultdict
from pathlib import Path
from greekocr.train.bench.common import read_rows, sha256, write_json, script
from greekocr.train.cer import levenshtein

METRIC_VERSION='o1-metrics/v1'
MODES=('nfc_char','nfd_atom','diacritic_insensitive')


def normalize(text, mode):
    if mode=='nfc_char': return ud.normalize('NFC',text)
    if mode=='nfd_atom':
        # Expand precomposed characters individually. Already emitted atoms keep order,
        # including erroneous cross-ccc/equal-ccc ordering, as train/grade_t1.py requires.
        return ''.join(ud.normalize('NFD',c) for c in text)
    if mode=='diacritic_insensitive':
        return ''.join(c for c in ud.normalize('NFD',text) if not ud.category(c).startswith('M'))
    raise ValueError(mode)


def alignment(ref, hyp):
    """Levenshtein alignment; fixed tie-break substitution, deletion, insertion."""
    n,m=len(ref),len(hyp)
    d=[list(range(m+1))]+[[i]+[0]*m for i in range(1,n+1)]
    for i in range(1,n+1):
        for j in range(1,m+1):
            d[i][j]=min(d[i-1][j-1]+(ref[i-1]!=hyp[j-1]),d[i-1][j]+1,d[i][j-1]+1)
    pairs=[]; i,j=n,m
    while i or j:
        if i and j and d[i][j]==d[i-1][j-1]+(ref[i-1]!=hyp[j-1]):
            pairs.append((ref[i-1],hyp[j-1]));i-=1;j-=1
        elif i and d[i][j]==d[i-1][j]+1:
            pairs.append((ref[i-1],None));i-=1
        else:
            pairs.append((None,hyp[j-1]));j-=1
    return pairs[::-1]


def aggregate(pairs):
    out={'lines':len(pairs),'cer':{}}
    for mode in MODES:
        edits=length=0
        for r,h in pairs:
            ref,hyp=normalize(r['text'],mode),normalize(h,mode)
            edits+=levenshtein(ref,hyp);length+=len(ref)
        out['cer'][mode]={'edits':edits,'reference_units':length,'rate':edits/length if length else None}
    word_edits=words=exact=confused=script_pairs=ref_letters=0
    for r,h in pairs:
        ref,hyp=normalize(r['text'],'nfc_char'),normalize(h,'nfc_char')
        word_edits+=levenshtein(ref.split(),hyp.split());words+=len(ref.split());exact+=ref==hyp
        for a,b in alignment(ref,hyp):
            sa,sb=script(a) if a else None,script(b) if b else None
            if sa: ref_letters+=1
            if sa and sb:
                script_pairs+=1
                confused+=sa!=sb
    out.update(wer={'edits':word_edits,'reference_words':words,'rate':word_edits/words if words else None},
               exact_line_rate=exact/len(pairs) if pairs else None,exact_lines=exact,
               script_confusion={'cross_script_substitutions':confused,'aligned_letter_pairs':script_pairs,
                                 'reference_letters':ref_letters,'rate':confused/script_pairs if script_pairs else None})
    return out


def load_sealed(path):
    path=Path(path); seal_path=path.with_suffix('.seal.json')
    if not seal_path.exists(): raise ValueError('reference is unsealed: missing .seal.json')
    seal=json.loads(seal_path.read_text())
    if seal.get('sealed') is not True or not seal.get('verified_by'):
        raise ValueError('reference is unsealed: missing owner verification')
    if seal.get('reference_sha256')!=sha256(path): raise ValueError('sealed reference hash mismatch')
    rows=list(read_rows(path))
    if not rows or seal.get('lines')!=len(rows): raise ValueError('sealed reference line count mismatch')
    if len({r['id'] for r in rows})!=len(rows): raise ValueError('duplicate reference IDs')
    for r in rows:
        if r.get('status')!='verified' or not isinstance(r.get('text'),str) or not r['text'].strip():
            raise ValueError('reference includes unverified or empty text')
        if not r.get('doc') or not isinstance(r.get('strata'),list): raise ValueError('missing reference provenance/strata')
        crop=Path(r['crop_path'])
        if not crop.is_absolute(): crop=path.parent/crop
        expected=seal.get('crop_sha256',{}).get(r['id'])
        if not expected or sha256(crop)!=expected: raise ValueError('sealed crop hash mismatch: '+r['id'])
    return rows,seal


def score_files(predictions, reference, output, checkpoint, decoder, runtime):
    start=time.perf_counter(); refs,seal=load_sealed(reference)
    preds=list(read_rows(predictions))
    if len({p['id'] for p in preds})!=len(preds):raise ValueError('duplicate prediction IDs')
    byid={p['id']:p for p in preds}
    if set(byid)!={r['id'] for r in refs}:raise ValueError('prediction IDs must match entire sealed reference')
    for p in preds:
        if p.get('error') or not isinstance(p.get('hyp'),str):raise ValueError('failed or invalid prediction: '+p['id'])
    groups=defaultdict(list);groups['overall']=[(r,byid[r['id']]['hyp']) for r in refs]
    for r,h in groups['overall']:
        for s in r['strata']:groups[s].append((r,h))
    results={s:aggregate(rs) for s,rs in groups.items()}
    output=Path(output);write_json(output,results)
    manifest=dict(dataset_hash=sha256(reference),seal_sha256=sha256(Path(reference).with_suffix('.seal.json')),
                  predictions_hash=sha256(predictions),checkpoint_id=checkpoint,decoder=decoder,
                  metric_version=METRIC_VERSION,runtime=runtime,scoring_runtime=dict(python=platform.python_version(),
                  platform=platform.platform(),seconds=time.perf_counter()-start),coverage=dict(reference_lines=len(refs),
                  predictions=len(preds),scored=len(refs)),normalization=dict(nfc_char='whole-string NFC; literal whitespace/case',
                  nfd_atom='per-codepoint canonical decomposition; emitted atom order preserved, no folds',
                  diacritic_insensitive='whole-string NFD, remove all Unicode M categories, case retained'),
                  wer='NFC whitespace tokens; corpus edits/reference words',
                  script_confusion='NFC minimum-edit aligned letter pairs; tie break diag/del/ins; Common/Inherited and indels excluded from denominator')
    write_json(output.with_suffix('.manifest.json'),manifest)
    return results


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('predictions',type=Path);ap.add_argument('reference',type=Path)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--checkpoint',required=True);ap.add_argument('--decoder',required=True)
    ap.add_argument('--runtime',type=Path,required=True,help='Inference runtime JSON receipt')
    a=ap.parse_args()
    try: score_files(a.predictions,a.reference,a.out,a.checkpoint,a.decoder,json.loads(a.runtime.read_text()))
    except (ValueError,KeyError,FileNotFoundError) as e:ap.exit(2,str(e)+'\n')

if __name__=='__main__':main()
