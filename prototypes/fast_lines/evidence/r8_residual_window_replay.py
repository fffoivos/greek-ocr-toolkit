"""Offline, fixed-request interventions through the real v11 recovery consumer.

Run serially with --source selecting an archived baseline or rejected trial.
The requests are experiments only; no saved localization is used by runtime.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--reverse', action='store_true')
    args = parser.parse_args()
    source = args.source.resolve()
    sys.path.insert(0, str(source))
    import cv2
    import numpy as np
    from prototypes.fast_lines.shared import detector, type_residual_recovery as rr

    def sha(path):
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()

    def clean(value):
        if isinstance(value, np.ndarray): return value.tolist()
        if isinstance(value, np.generic): return value.item()
        if isinstance(value, dict): return {k: clean(v) for k,v in value.items()}
        if isinstance(value, (list, tuple)): return [clean(v) for v in value]
        return value

    def write(path, value):
        path.write_text(json.dumps(clean(value), ensure_ascii=False, indent=2))

    inputs = json.loads((args.evidence/'target-input.json').read_text())
    census = json.loads((args.evidence/'residual-input.json').read_text())
    assert sha(inputs['path']) == inputs['sha256']
    manifest = json.loads((args.evidence.parent/'R8-01b/inputs-208.json').read_text())
    assert inputs in manifest['pages'], 'only the pinned development input is allowed'
    identity = {str(p.relative_to(source)): sha(p)
                for p in sorted((source/'prototypes/fast_lines').rglob('*.py'))
                if '/evidence/' not in str(p) and not p.name.startswith('test_')}
    args.out.mkdir(parents=True, exist_ok=False)
    write(args.out/'source.json', identity)
    detector.MODEL = Path('/Users/foivoskarounos-zamparloukos/Projects/'
        'greek-ocr-toolkit-astra-lines4/.astra/fast_lines/onnx/PP-OCRv6_small_det.onnx')
    start = perf_counter(); model = detector.Detector(); startup = perf_counter()-start
    start = perf_counter(); gray = cv2.imread(inputs['path'], 0); decode = perf_counter()-start
    windows = [(0,2576,3080), (1,2583,3079)]
    records = []
    for window,top,bottom in windows[::-1] if args.reverse else windows:
        calls = []
        class Recording:
            def infer(self, crop, side=960):
                started = perf_counter(); pm,meta = model.infer(crop,side)
                calls.append(dict(seconds=perf_counter()-started, meta=meta,
                                  shape=crop.shape, side=side, pixels=crop.size))
                return pm,meta
        original = rr.requests
        rr.requests = lambda *_: [dict(id='window-intervention',
            bbox=[0,top,gray.shape[1],bottom],derivation=[],dependencies=[])]
        try:
            result = rr.recover(gray,detector=Recording(),**census)
        finally:
            rr.requests = original
        assert len(calls)==1
        calls[0]['input_sha256']=hashlib.sha256(gray[top:bottom].tobytes()).hexdigest()
        write(args.out/f'{window}.json',result)
        records.append(dict(window=window, seconds=result['seconds'],
            scout_s=result['scout_s'], correction_s=result['correction_s'],
            inference=calls, added=len(result['added']),
            natural_heights=[q['height'] for q in result['calls']]))
    assert all(sha(source/p)==h for p,h in identity.items())
    write(args.out/'receipt.json',dict(source=str(source), source_sha256=sha(args.out/'source.json'),
        input=inputs, census_sha256=sha(args.evidence/'residual-input.json'),
        script_sha256=sha(__file__), model_sha256=sha(detector.MODEL),
        opencv=cv2.__version__, opencv_threads=cv2.getNumThreads(),
        onnx='CPU sequential intra/inter 1', startup_s=startup, decode_s=decode,
        records=records, timing='Recovery includes real regional inference and all native preparation; '
        'source/input hashing and serialization are outside its clock. '
        'No full-page correction timing or speed claim. Startup/decode separate.'))


if __name__ == '__main__':
    main()
