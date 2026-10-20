"""T6f mock adapter: execute the frozen T6c2 worker with the T6b guard.

The worker, matcher, diagnostics and masker are imported unchanged. Only input
paths, unrelated evaluation pins and receipt provenance are adapted. The guard
calls T6b.guard_measure with the owner's explicit original-crop <128 mask.
"""
from __future__ import annotations
import os
import sys
sys.dont_write_bytecode = True
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[name] = '1'
os.environ['HF_HUB_OFFLINE'] = os.environ['TRANSFORMERS_OFFLINE'] = '1'

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import socket

TREE = '63c640a3aa4abe08d200258cf24d235dfa4a1625'
PARAM = '801d517e2ac5b64b62c16868a4b1374fe15d9364af38a674ce8e9eac65e1cfe8'
LIBRARY = 'f203504a8703561569486450d7e725fe7b399cd4c8fbf581b79cd249e3c5aeb5'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--code', type=Path, required=True)
    p.add_argument('--harvest', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--worker', type=int, required=True)
    a = p.parse_args()
    root = a.code.resolve()
    sys.path.insert(0, str(root))
    folder = root / 'docs/harvest/recut_v1'
    t6c2 = load('t6f_frozen_t6c2', folder/'v2_test/run.py')
    t6b = load('t6f_frozen_t6b', folder/'w1_masked/run.py')
    t6c2.HARVEST = a.harvest
    t6c2.io_guard(a.out.resolve())
    import numpy as np
    import cv2
    cv2.setNumThreads(0)
    import greekocr.glyphs.foreign_ink as foreign
    from PIL import Image

    def binding():
        parameters = json.loads((folder/'masking/params.json').read_text())
        assert parameters['params_sha256'] == PARAM
        actual = hashlib.sha256(json.dumps(parameters['params'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        assert actual == PARAM and foreign.PARAMETERS == parameters['params']
        for name, expected in parameters['source_hashes'].items():
            assert t6c2.sha(root/name) == expected, name
        assert t6c2.sha(root/'greekocr/glyphs/foreign_ink.py') == LIBRARY
        return dict(code_tree_sha=TREE,params_sha256=PARAM,library_sha256=LIBRARY,
                    t6c2_worker_sha256=t6c2.sha(t6c2.__file__),t6b_guard_source_sha256=t6c2.sha(t6b.__file__),
                    adapter_sha256=t6c2.sha(__file__),host=socket.gethostname())
    t6c2.frozen = binding
    # Keep the actual priority visible, including a sandbox-denied Mac nice call.
    t6c2.low_priority = lambda: os.getpriority(os.PRIO_PROCESS,0)
    original_mask = foreign.mask_foreign_ink

    def guarded_mask(page, line, neighbours, box):
        result = original_mask(page,line,neighbours,box)
        original = page.image.crop(tuple(box))
        changed = np.asarray(original) != np.asarray(result.image)
        if changed.ndim == 3:
            changed = np.any(changed,axis=2)
        counts = t6b.guard_measure(np.asarray(original.convert('L')) < 128, changed)
        guard = counts['own_ink_masked_fraction'] > .30
        result.record.update(counts, wrong_line_risk=guard,
                             would_be_masked_pixel_count=result.record['masked_pixel_count'],
                             would_be_masked_component_count=result.record['masked_component_count'])
        if guard:
            result.image = original
            result.mask = np.zeros_like(result.mask)
            result.record.update(masked_pixel_count=0,masked_component_count=0,
                                 changed=False,native_changed_pixels=0)
        return result
    foreign.mask_foreign_ink = guarded_mask
    t6c2.worker(a.out,a.worker)
    selection = json.loads((a.out/'selection.json').read_text())[a.worker]
    name = selection['wave']+'--'+selection['page_id']
    path = a.out/'page-lines'/(name+'.jsonl')
    records = list(t6c2.rows(path))
    lookup = {r['id']:r for r in selection['lines']}
    for r in records:
        unmatched = r['match_status'] == 'unmatched'
        if unmatched:
            original = Path(r['original_path'])
            destination = a.out/'crops'/selection['wave']/selection['doc']/Path(original).name
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_bytes(original.read_bytes())
            r.update(masked_path=str(destination.relative_to(a.out)),masked_sha256=t6c2.sha(destination))
            with Image.open(original) as im:
                counts = t6b.guard_measure(np.asarray(im.convert('L'))<128,np.zeros((im.height,im.width),dtype=bool))
            r.update(counts,wrong_line_risk=False)
        guarded = r.get('wrong_line_risk',False)
        r.update(split=lookup[r['id']]['split'],host=socket.gethostname(),code_tree_sha=TREE,
                 params_sha256=PARAM,original_sha256=r['stored_crop_sha256'],output_sha256=r['masked_sha256'],
                 guard_status='unmatched_original' if unmatched else 'guarded_original' if guarded else 'masked')
        if unmatched or guarded:
            assert r['output_sha256'] == r['original_sha256']
    # The original page receipt binds the original frozen-worker record file.
    t6c2.write_rows(a.out/'page-lines'/(name+'.guarded.jsonl'),records)


if __name__ == '__main__':
    main()
