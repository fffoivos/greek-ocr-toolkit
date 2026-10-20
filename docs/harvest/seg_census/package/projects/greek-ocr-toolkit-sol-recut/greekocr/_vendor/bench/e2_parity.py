"""Native vs converted ORIGINAL-vocabulary endpoints/logits on exactly 100 crops."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import torch
from PIL import Image
from greekocr._vendor.bench.common import read_rows, sha256
from greekocr._vendor.bench.e1_common import atomic_json, read_json
from greekocr._vendor.bench.e2_teachers import hook
from greekocr._vendor.bench.e2_models import build_donor, preprocess


def greedy(array):
    ids=np.asarray(array).argmax(-1).reshape(-1).tolist()
    return [i for j,i in enumerate(ids) if i and (not j or i!=ids[j-1])]


def compare(native,converted):
    result={}
    for name in ('backbone','neck','logits'):
        a=np.asarray(native[name]);b=np.asarray(converted[name])
        if a.shape!=b.shape: raise ValueError('parity shape mismatch: '+name)
        if not np.isfinite(a).all() or not np.isfinite(b).all(): raise ValueError('nonfinite parity endpoint')
        diff=np.abs(a-b); away=np.abs(a)>1e-3
        absolute=float(diff.max(initial=0));relative=float((diff[away]/np.abs(a[away])).max(initial=0))
        scale=float(max(1.0,np.abs(a).max(initial=0)));normalised=absolute/scale
        result[name]=dict(shape=list(a.shape),max_abs=absolute,max_relative_away_from_zero=relative,
                          ref_max_abs=scale,max_abs_over_ref_max=normalised,
                          rule='max_abs/max(1,max|ref|) <= 1e-4 and identical greedy decode')
        # 8 Oct 2026 (coordinator, disclosed): the earlier rule (abs<=1e-4 or element-wise relative<=1e-3) failed on
        # 2.9e-4 absolute noise over activations of magnitude 64 (4.5 ppm, correlation 1.000000); FP32 conv accumulation
        # order differs between Paddle and Torch. Scale-normalised tolerance; raw numbers stay in the receipt.
        if normalised>1e-4: raise ValueError(f'parity tolerance failed: {name} abs={absolute},ref_max={scale},normalised={normalised}')
    if greedy(native['logits'])!=greedy(converted['logits']): raise ValueError('greedy sequence differs')
    return result


def preprocessing_check(native, rows, spec, out):
    """Independent upstream image path on 20 crops, before all model endpoints."""
    binding = getattr(native, 'binding', {})
    source = binding.get('preprocessing_source')
    if not callable(getattr(native, 'preprocess', None)) or not source:
        raise ValueError('native preprocessing hook/source required; no shared-tensor-only qualification')
    if (Path(source).resolve() == Path(__file__).with_name('e2_models.py').resolve()
            or sha256(source) != binding.get('preprocessing_source_sha256')):
        raise ValueError('native preprocessing must bind donor source bytes')
    # Include each edge kind in this smaller preflight, irrespective of row order.
    selected = []
    for kind in ('short','very_long','blank','padded'):
        selected.append(next(r for r in rows if r['parity_kind']==kind))
    selected.extend(r for r in rows if r not in selected)
    checks=[]
    for i,r in enumerate(selected[:20]):
        path=Path(r['crop_path'])
        with Image.open(path) as im: ours=preprocess(im,spec['preprocess']).numpy()
        ref=native.preprocess(path)
        if isinstance(ref,torch.Tensor): ref=ref.detach().cpu().numpy()
        else: ref=np.asarray(ref)
        if ref.dtype != np.float32 or ours.dtype != np.float32:
            raise ValueError('native preprocessing tensors must be FP32')
        if ref.shape != ours.shape or ref.ndim != 4:
            raise ValueError('native preprocessing shape mismatch: '+str(path))
        if not np.isfinite(ref).all() or not np.isfinite(ours).all():
            raise ValueError('nonfinite native preprocessing tensor')
        error=float(np.abs(ref-ours).max(initial=0))
        np.savez_compressed(out/f'preprocess_{i:03d}.npz',native=ref,ours=ours)
        if error>1e-6: raise ValueError(f'native preprocessing tolerance failed: {path}: {error}')
        checks.append(dict(crop_path=str(path),parity_kind=r['parity_kind'],shape=list(ref.shape),max_abs=error))
    return dict(passed=True,crops=20,criterion='independent native preprocessing; FP32, same shape, max abs <=1e-6',
                source=source,source_sha256=sha256(source),checks=checks)


def parity(spec,converted,crops,out):
    rows=list(read_rows(crops))
    if len(rows)!=100: raise ValueError('parity requires exactly 100 crops')
    if len({str(Path(r['crop_path']).resolve()) for r in rows})!=100: raise ValueError('parity crops must be distinct')
    if not {'short','very_long','blank','padded'} <= {r.get('parity_kind') for r in rows}:
        raise ValueError('100 crops must include short, very_long, blank and padded cases')
    if not spec.get('native_factory'): raise ValueError('node-only: native inference/logits hook unavailable')
    native,bound=hook(spec['native_factory'],spec)
    ck=torch.load(converted,map_location='cpu',weights_only=True)
    if ck['source_sha256']!=sha256(spec['checkpoint']): raise ValueError('parity donor source mismatch')
    if bound['adapter_sha256'] == sha256(__file__): raise ValueError('native reference must use upstream inference')
    out=Path(out);out.mkdir(parents=True,exist_ok=True);checks=[];inputs={}
    native_preprocessing=preprocessing_check(native,rows,spec,out)
    model=build_donor(ck['family'],ck['config'],ck['n_classes']).eval().cpu()
    model.load_state_dict(ck['model'],strict=True)
    for i,r in enumerate(rows):
        path=Path(r['crop_path']);inputs[str(path.resolve())]=sha256(path)
        with Image.open(path) as im:x=preprocess(im,spec['preprocess'])
        with torch.inference_mode():
            ref=native.endpoints(x)
            actual=model.endpoints(x)
        arrays=lambda endpoints:{k:(v.detach().cpu().numpy() if isinstance(v,torch.Tensor) else np.asarray(v)) for k,v in endpoints.items()}
        ref,actual=arrays(ref),arrays(actual)
        if any(v.dtype != np.float32 for values in (ref,actual) for v in values.values()):
            raise ValueError('parity endpoints must actually be FP32')
        np.savez_compressed(out/f'{i:03d}.npz',**{'native_'+k:v for k,v in ref.items()},**{'converted_'+k:v for k,v in actual.items()})
        checks.append(dict(crop_path=str(path),parity_kind=r['parity_kind'],checks=compare(ref,actual)))
    report=dict(passed=True,crops=100,fp32=True,classifier='original, before head swap',
        criterion='max abs / max(1, max|native|) <= 1e-4 per endpoint (scale-normalised, 8 Oct 2026); identical CTC greedy; raw abs/relative kept per endpoint',
        converted_sha256=sha256(converted),checkpoint_sha256=sha256(spec['checkpoint']),
        preprocessing=spec['preprocess'],native_adapter=bound,inputs=inputs,checks=checks,
        native_preprocessing=native_preprocessing,
        native_binding=getattr(native,'binding',None),
        endpoint_files={p.name:sha256(p) for p in sorted(out.glob('*.npz'))})
    atomic_json(out/'parity.json',report);return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--spec',type=Path,required=True)
    p.add_argument('--converted',type=Path,required=True);p.add_argument('--crops',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();parity(read_json(a.spec),a.converted,a.crops,a.out)


if __name__=='__main__': main()
