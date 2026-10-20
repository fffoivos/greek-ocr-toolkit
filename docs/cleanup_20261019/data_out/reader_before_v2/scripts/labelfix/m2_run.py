"""M2: offline, CPU-only blind-crop inference. References never enter infer_line.

Run with PYTHONPATH=$PWD and the toolkit virtualenv. Cached alignments are
checkpoint/crop-bound; no existing alignment cache or production code is edited.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import time

os.environ.setdefault('HF_HUB_OFFLINE', '1')
os.environ.setdefault('TRANSFORMERS_OFFLINE', '1')
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

import numpy as np
from PIL import Image
import torch

from greekocr.labelfix.ctc_align import Alignment, Recognizer, make_strip
from greekocr.labelfix import ink, markshape, reading, case
from greekocr.labelfix.text import nfc
from scripts.labelfix.clariden.r1_common import HEADS, LETTERS, compose
from scripts.labelfix.clariden.r1_extract import extract_line
from scripts.labelfix.clariden.r1_model import MarkReader
from scripts.labelfix.clariden.r1_pixels import FONT_RULE
from scripts.labelfix.owner_reading import serialize

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT.parent/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/blind_checks_v1'
CACHE = ROOT/'.cache/labelfix/m2'
OUT = ROOT/'docs/labelfix/spellcheck'
CTC = ROOT.parent/'greek-page-ocr/out/e3b/jobA/runs/full_s0/best.pt'
R1 = ROOT/'artifacts/labelfix_r1/output_3678928/A/best.pt'
R1_COPY = ROOT.parent/'greek-ocr-toolkit-spellcheck-r1/artifacts/labelfix_r1/output_3678928/A/best.pt'
SHAPE = ROOT/'docs/labelfix/markshape_model_S4.json'
CASE = ROOT/'docs/labelfix/case_model_S5.json'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def rows(path):
    with (gzip.open if str(path).endswith('.gz') else open)(path, 'rt') as f:
        return [json.loads(s) for s in f if s.strip()]


def write_rows(path, records):
    with (gzip.open if str(path).endswith('.gz') else open)(path, 'wt') as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False)+'\n')


def inventory():
    result = []
    for phase in ('t4c', 'c0'):
        for path in sorted((BASE/phase).glob('*/cards.jsonl')):
            source = path.parent.name
            key = json.loads((path.parent.parent/(source+'_key.json')).read_text())
            verdicts = {r['card_id']: r for r in rows(path.parent.parent/(source+'_out.jsonl'))}
            cards = rows(path)
            assert len(cards) == len(verdicts)
            for card in cards:
                cid = card['card_id']
                result.append(dict(id=f'{phase}/{source}/{cid}', source=source, phase=phase,
                    card_id=cid, crop=str(path.parent/card['crop']), key=key[cid],
                    google_label=card['google_text'], verdict=verdicts[cid]))
    assert len(result) <= 10000
    assert len({r['id'] for r in result}) == len(result)
    return result


def kinds(parts):
    return {'breathing' if p in ('psili', 'dasia') else
            'accent' if p in ('acute', 'grave', 'circumflex') else p for p in parts}


def reader_predictions(model, samples, windows, batch_size=64):
    out = {}
    with torch.inference_mode():
        for i in range(0, len(samples), batch_size):
            ss = samples[i:i+batch_size]
            grey = torch.from_numpy(np.asarray(windows[i:i+batch_size])).float().div_(255)
            masks = torch.tensor([s[7][0] for s in ss], dtype=torch.float32)
            xx = torch.arange(128, dtype=torch.float32)[None, :]+.5
            mask = ((xx >= masks[:, 0, None]) & (xx < masks[:, 1, None])).float()[:, None, :].expand(-1, 64, -1)
            x = torch.stack((grey, mask), dim=1).contiguous(memory_format=torch.channels_last)
            letters = torch.tensor([s[4] for s in ss], dtype=torch.long)
            prob = [z.float().softmax(1) for z in model(x, letters)]
            values = torch.stack([z.argmax(1) for z in prob], 1).tolist()
            for j, (s, v) in enumerate(zip(ss, values)):
                cls = compose(v)
                out[s[3]] = dict(start=s[3], base=LETTERS[s[4]], factors=v, cls=cls,
                    parts=cls.split('+') if cls != 'none' else [],
                    mark_probabilities={choices[q]: float(prob[h][j, q])
                        for h, (choices, q) in enumerate(zip(HEADS.values(), v)) if q})
    return out


# Compatibility entry point; the policy and serializer live in one module.
from greekocr.labelfix.release_gate import compose as combine, compose_runtime


def infer_line(identifier, image, alignment, detector_model, reader_model, *, script_class=None):
    """Reference-free boundary: no Google label, verdict or printed pair accepted."""
    from greekocr.labelfix.toolkit_geometry import polytonic_scope
    if not polytonic_scope(script_class):
        return dict(id=identifier,status='skipped',skip_reason='monotonic_scope')
    text = alignment.prediction
    record = dict(id=identifier, recogniser_text=text, _line=0)
    ss, wide, _, losses, coverage, size = extract_line(record, alignment.to_record(), image, evaluation=True)
    pred = reader_predictions(reader_model, ss, wide)
    raw = reading.read_ink(ink.analyse(image), text, alignment, detector_model, filtered=False)
    runtime = dict(id=identifier, status='ok', recogniser_text=nfc(text), recogniser_nfd=text,
        recognition_confidence=alignment.confidence, image_width=image.width,
        recognition_evidence=alignment.recognition_evidence(raw.slots,image.width), detector=serialize(raw),
        r1_predictions=list(pred.values()), coverage=coverage, font_size=size, extraction_counts=dict(losses))
    runtime['modes']={mode:compose_runtime(runtime,mode) for mode in ('PRESENCE','FULL')}
    return runtime


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--batch-size', type=int, default=8)
    ap.add_argument('--launch-head', help='record the head observed when the task began, if the shared checkout advanced')
    ap.add_argument('--replay-detector', nargs='*', help='S7: replay detector only, with bound cached CTC and R1 outputs')
    ap.add_argument('--output-dir', type=Path)
    ap.add_argument('--script-classes', type=Path, help='independent line script-class manifest; no reference text')
    a = ap.parse_args()
    if a.replay_detector is not None:
        replay_detector(a.replay_detector,a.output_dir,a.script_classes)
        return
    torch.set_num_threads(a.threads)
    head_start = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    CACHE.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    inv = inventory()
    script_scope={r['id']:r['scripts'] for r in rows(a.script_classes)} if a.script_classes else {}
    # Snapshot protected source code and Git metadata without invoking mutating Git.
    protected = sorted((ROOT/'greekocr').rglob('*.py'))+sorted((ROOT/'scripts/labelfix/clariden').glob('*.py'))
    before = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    bindings = {str(p): sha(p) for p in (CTC, R1, R1_COPY, SHAPE, CASE)}
    assert bindings[str(R1)] == bindings[str(R1_COPY)]
    input_files = sorted({p for phase in ('t4c','c0') for p in (BASE/phase).glob('*_key.json')})
    input_files += sorted(p for phase in ('t4c','c0') for p in (BASE/phase).glob('*_out.jsonl'))
    input_files += sorted(p for phase in ('t4c','c0') for p in (BASE/phase).glob('*/cards.jsonl'))
    input_hashes = {str(p): sha(p) for p in input_files}
    valid = []
    crop_hashes = {}
    skipped = {}
    for r in inv:
        if r['key'].get('primary_class') == 'cyrillic':
            skipped[r['id']] = 'non_Greek_cyrillic_cohort'
            continue
        path = Path(r['crop'])
        try:
            with Image.open(path) as im:
                make_strip(im)
            crop_hashes[r['id']] = sha(path)
            valid.append(r)
        except (OSError, ValueError) as e:
            skipped[r['id']] = 'crop_problem:'+repr(e)
    cache_path = CACHE/'align_s0.jsonl'
    alignments = {}
    if cache_path.exists():
        for r in rows(cache_path):
            assert r['checkpoint_sha256'] == bindings[str(CTC)]
            assert r['crop_sha256'] == crop_hashes[r['id']]
            assert r['id'] not in alignments
            alignments[r['id']] = r['alignment']
    need = [r for r in valid if r['id'] not in alignments]
    need.sort(key=lambda r: Image.open(r['crop']).width/Image.open(r['crop']).height)
    if need:
        rec = Recognizer(CTC, device='cpu', threads=a.threads)
        with open(cache_path, 'a') as f:
            for i in range(0, len(need), a.batch_size):
                batch = need[i:i+a.batch_size]
                images = []
                for r in batch:
                    with Image.open(r['crop']) as im:
                        images.append(im.convert('L'))
                for r, al in zip(batch, rec.align_batch(images)):
                    # Read back the canonical, rounded cache representation even
                    # on the first run, so restart and initial results coincide.
                    ar = al.to_record()
                    alignments[r['id']] = ar
                    f.write(json.dumps(dict(id=r['id'], crop=r['crop'], crop_sha256=crop_hashes[r['id']],
                        checkpoint_sha256=bindings[str(CTC)], alignment=ar), ensure_ascii=False)+'\n')
                f.flush()
                print(f'CTC {min(i+a.batch_size,len(need))}/{len(need)} elapsed={time.monotonic()-started:.1f}s', flush=True)
        del rec
    model = MarkReader(embedding=True).to('cpu', memory_format=torch.channels_last)
    ck = torch.load(R1, map_location='cpu', weights_only=True)
    assert ck['arm'] == 'A'
    model.load_state_dict(ck['model'])
    model.eval()
    detector_model = markshape.load_model(SHAPE)
    case.configure_model(CASE)
    runtime_path = CACHE/'runtime.jsonl'
    # Runtime is cheap to replay from bound alignments; do not reuse unbound
    # composed results after any measurement-wrapper change.
    runtime = []
    with open(runtime_path, 'w') as f:
        for i, r in enumerate(inv):
            if r['id'] in skipped:
                result = dict(id=r['id'], status='skipped', skip_reason=skipped[r['id']])
            else:
                try:
                    with Image.open(r['crop']) as im:
                        result = infer_line(r['id'], im.convert('L'), Alignment.from_record(alignments[r['id']]), detector_model, model,
                                            script_class=script_scope.get(r['id']))
                except Exception as e:
                    raise RuntimeError('M2 inference failed: '+r['id']) from e
            runtime.append(result)
            f.write(json.dumps(result, ensure_ascii=False)+'\n')
            f.flush()
            if (i+1) % 10 == 0 or i+1 == len(inv):
                print(f'COMBINED {i+1}/{len(inv)} elapsed={time.monotonic()-started:.1f}s', flush=True)
    after = {str(p.relative_to(ROOT)): sha(p) for p in protected}
    assert before == after
    assert input_hashes == {str(p): sha(p) for p in input_files}
    assert bindings == {str(p): sha(p) for p in (CTC, R1, R1_COPY, SHAPE, CASE)}
    assert crop_hashes == {r['id']: sha(r['crop']) for r in valid}
    receipt = dict(schema='m2-runtime-v1', launch_head=a.launch_head or head_start, execution_start_head=head_start,
        completion_head=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        changes_since_launch=subprocess.check_output(['git','diff','--name-only',a.launch_head or head_start,head_start],cwd=ROOT,text=True).splitlines(),
        inventory_cards=len(inv), source_cohorts=len({r['source'] for r in inv}), inferred_lines=len(valid),
        skipped=dict(Counter(skipped.values())), newly_aligned_lines=len(need), cached_lines=len(alignments),
        device='cpu', threads=a.threads, ctc_batch_size=a.batch_size, network='OFF; no network API used',
        python=platform.python_version(), torch=torch.__version__, model_bindings=bindings, input_sha256=input_hashes,
        crop_sha256=crop_hashes, protected_source_sha256=before, protected_sources_unchanged=True,
        script_sha256=sha(Path(__file__)), alignment_sha256=sha(cache_path), runtime_sha256=sha(runtime_path),
        font_rule=FONT_RULE, k1_output='print (default)', k1_rules=sorted(reading.APPLIED_CONSTRAINT_RULES),
        r1_epoch=ck['epoch'], elapsed_seconds=time.monotonic()-started,
        reference_boundary='infer_line receives id, crop, recognizer alignment, detector model, R1 model only')
    (OUT/'M2_runtime_receipt.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('inventory_cards','inferred_lines','skipped','elapsed_seconds')}), flush=True)


def replay_detector(substitutions, output, script_classes):
    """Reference-free detector replay; cached R1 extraction/predictions stay fixed."""
    import socket
    from greekocr.labelfix.toolkit_geometry import polytonic_scope
    def forbidden(*args,**kwargs):raise RuntimeError('S7 is offline and cached-reader-only')
    socket.socket.connect=forbidden;socket.create_connection=forbidden
    Recognizer.__init__=forbidden;Recognizer.align_batch=forbidden
    started=time.monotonic()
    if output is None or script_classes is None:raise ValueError('S7 output and script-class manifest required')
    output.mkdir(parents=True,exist_ok=True)
    original=json.loads((OUT/'M2_runtime_receipt.json').read_text())
    from scripts.labelfix.owner_reading import SOURCES
    code=[ROOT/p for p in SOURCES]+[Path(__file__)]
    before={str(p):sha(p) for p in code}
    assert original['runtime_sha256']==sha(CACHE/'runtime.jsonl')
    assert original['alignment_sha256']==sha(CACHE/'align_s0.jsonl')
    for p,d in original['model_bindings'].items():assert sha(p)==d
    for p,d in original['input_sha256'].items():assert sha(p)==d
    old={r['id']:r for r in rows(CACHE/'runtime.jsonl')}
    als={r['id']:r for r in rows(CACHE/'align_s0.jsonl')}
    scope={r['id']:r for r in rows(script_classes)}
    sr=json.loads(script_classes.with_suffix('.receipt.json').read_text())
    assert sr['manifest_sha256']==sha(script_classes)
    for p,d in sr['source_sha256'].items():assert sha(p)==d
    inv=inventory();model=markshape.load_model(SHAPE);result=[]
    for item in inv:
        identifier=item['id'];prior=old[identifier]
        annotation=scope[identifier]
        if prior['status']!='ok':result.append(prior);continue
        if not polytonic_scope(annotation['scripts']):
            result.append(dict(id=identifier,status='skipped',skip_reason='monotonic_scope',script_scope=annotation));continue
        ar=als[identifier];assert ar['crop_sha256']==sha(item['crop'])
        assert original['crop_sha256'][identifier]==ar['crop_sha256']
        with Image.open(item['crop']) as image:
            alignment=Alignment.from_record(ar['alignment'])
            raw=reading.read_ink(ink.analyse(image),ar['alignment']['prediction'],alignment,model,
                                 filtered=False,substitutions=substitutions)
            score_evidence=alignment.recognition_evidence(raw.slots,image.width)
            image_width=image.width
        run={k:v for k,v in prior.items() if k not in ('detector','modes')}
        run.update(detector=serialize(raw),script_scope=annotation,image_width=image_width,
                   recognition_confidence=alignment.confidence,recognition_evidence=score_evidence)
        run['modes']={mode:compose_runtime(run,mode) for mode in ('PRESENCE','FULL')}
        result.append(run)
    write_rows(output/'runtime.jsonl',result)
    assert before=={str(p):sha(p) for p in code},'S7 replay source changed during inference'
    # Read-only scoring can reuse the existing alignment binding.
    receipt=dict(original,schema='s7-m2-cached-detector-v1',substitutions=list(substitutions),
        original_eligible_lines=473,scope_excluded_lines=sum(r.get('skip_reason')=='monotonic_scope' for r in result),
        inferred_lines=sum(r['status']=='ok' for r in result),ctc_forward_passes=0,r1_forward_passes=0,retraining=False,newly_aligned_lines=0,
        original_runtime_sha256=original['runtime_sha256'],script_sha256=sha(Path(__file__)),
        runtime_sha256=sha(output/'runtime.jsonl'),alignment_path=str(CACHE/'align_s0.jsonl'),
        script_classes_sha256=sha(script_classes),elapsed_seconds=time.monotonic()-started,
        protected_source_sha256=before)
    (output/'M2_runtime_receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('inferred_lines','scope_excluded_lines','ctc_forward_passes','r1_forward_passes','elapsed_seconds')},indent=2))


if __name__ == '__main__':main()
