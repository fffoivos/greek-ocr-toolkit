"""Offline paper/noise hypothesis; no Stack import and no front-ink claim.

The mean remains the callers' engineering-window observation. The proposed
cutoff is a three-standard-deviation departure, estimated from adjacent bright
samples on THIS raster. It assumes locally stationary independent noise. The
native gallery tests that assumption, including its failure under resampling.
Do not promote this function merely because its masks look less fragmented.
"""
import argparse
import json
from pathlib import Path
from time import perf_counter

import cv2
import numpy as np

from ..shared import observations as obs
from ..shared.geometry import height_proxy, quantize
from ..layout_barriers.fast import scout, correct
from .r8_measurements import digest, dump


def observe(gray, width):
    """DN mean and local neighbour-difference variance, with explicit samples.

    For independent bright-half Gaussian samples, their conditional variance
    is sigma**2 * (1 - 2/pi). Correcting for that censoring is necessary;
    unconditioned Var(I[x]-I[x+1])/2 would underestimate scanner noise.
    A round-to-nearest DN has variance 1/12 under a uniform rounding phase;
    that is a quantization prior, not a measured scanner noise floor. The
    three-sigma tolerance is inherited from ink_faintness.components. It has
    a one-sided Gaussian tail of 0.00135 ONLY if the noise model is valid.
    """
    raw = gray.astype(np.float32)
    paper = cv2.boxFilter(gray, cv2.CV_32F, (width, width))
    bright = raw >= paper
    numerator = np.zeros(gray.shape, np.float32)
    count = np.zeros(gray.shape, np.float32)
    for axis in (0, 1):
        a = (slice(None, -1), slice(None)) if axis == 0 else (slice(None), slice(None, -1))
        b = (slice(1, None), slice(None)) if axis == 0 else (slice(None), slice(1, None))
        pairs = bright[a] & bright[b]
        numerator[a] += ((raw[b] - raw[a]) ** 2) * pairs
        count[a] += pairs
    summed = cv2.boxFilter(numerator, cv2.CV_32F, (width, width), normalize=False)
    samples = cv2.boxFilter(count, cv2.CV_32F, (width, width), normalize=False)
    variance = summed / np.maximum(2 * (1 - 2/np.pi) * samples, 1)
    # Unknown support is returned separately; no fallback empirical cutoff.
    known = samples > 0
    sigma = np.sqrt(np.maximum(variance, 1 / 12))
    tolerance = 3 * sigma * np.sqrt(1 - 1 / width**2)
    response = paper - raw
    return dict(paper=paper, sigma_dn=sigma, tolerance_dn=tolerance,
                samples=samples, bright=bright, response_dn=response,
                known=known, mask=(known & (response > tolerance)).astype(np.uint8))


def describe(e, crop):
    x, y, z, w = crop
    take = lambda k: e[k][y:w, x:z]
    return dict(paper_dn=np.percentile(take('paper'), [0, 50, 100]).tolist(),
                sigma_dn=np.percentile(take('sigma_dn'), [0, 50, 100]).tolist(),
                tolerance_dn=np.percentile(take('tolerance_dn'), [0, 50, 100]).tolist(),
                bright_sample_pixels=int(take('bright').sum()),
                unknown_pixels=int((~take('known')).sum()),
                ink_pixels=int(take('mask').sum()))


def panel(raw, e):
    image = cv2.cvtColor(raw, cv2.COLOR_GRAY2BGR)
    samples = image.copy(); samples[e['bright']] = (0, 180, 0)
    support = image.copy(); support[e['mask'] > 0] = (0, 0, 230)
    band = image.copy()
    changed = (e['mask'] > 0) != (e['response_dn'] > 255 * .08)
    band[changed] = (230, 0, 230)
    return np.hstack([image, samples, support, band])


def study(inputs, previous, out):
    inputs, previous, out = map(Path, (inputs, previous, out))
    out.mkdir(parents=True, exist_ok=True)
    original_ink = obs.ink
    receipts = []
    for row in json.loads(inputs.read_text())['pages']:
        name = row['page']; gray = cv2.imread(row['path'], 0)
        assert digest(row['path']) == row['sha256']
        assert digest(row['original_paddle']) == row['original_paddle_sha256']
        items = json.loads(Path(row['original_paddle']).read_text())['original']
        old = json.loads((previous / f'{name}.json').read_text())
        h = height_proxy(items, gray.shape[::-1]); width = quantize(4*h) | 1
        start = perf_counter(); native = observe(gray, width); native_s = perf_counter()-start
        probes = []
        for i, p in enumerate(old['probes']):
            x,y,z,w = p['bbox']; crop = gray[y:w, x:z]
            local = {k: v[y:w, x:z] for k,v in native.items()}
            view = panel(crop, local)
            cv2.imwrite(str(out / f'{name}-{i}.png'), view)
            # Complete operator arrays retained for reviewer pixel queries.
            np.savez_compressed(out / f'{name}-{i}.npz', **local)
            probes.append(dict(source=p['source'], bbox=p['bbox'], **describe(native,p['bbox']),
                old06_pixels=int((local['response_dn']>255*.06).sum()),
                old08_pixels=int((local['response_dn']>255*.08).sum()),
                image=f'{name}-{i}.png', samples=f'{name}-{i}.npz'))
        calls = []
        def proposed(image, k, *, method, threshold, arithmetic):
            if method != 'mean' or arithmetic != 'dn':
                return original_ink(image,k,method=method,threshold=threshold,arithmetic=arithmetic)
            start=perf_counter(); result=observe(image,k)
            calls.append(dict(shape=list(image.shape), width=k, old_threshold_dn=threshold,
                seconds=perf_counter()-start, **describe(result,[0,0,image.shape[1],image.shape[0]])))
            # Save reduced response for native-vs-reduced probe comparison.
            calls[-1]['_arrays']=result
            return result['mask']
        obs.ink = proposed
        try:
            witness, primitive = scout(gray,items)
            downstream = correct(gray,items,witness,primitive)
        finally:
            obs.ink = original_ink
        reduced = calls[0].pop('_arrays')
        rh,rw=reduced['mask'].shape
        scale=min(1.,12/h,1200/max(gray.shape))
        step=max(1,2**int(np.floor(np.log2(1/scale))))
        ch,cw=(gray.shape[0]//step)*step,(gray.shape[1]//step)*step
        sx=rw/cw;sy=rh/ch
        for i,p in enumerate(probes):
            a,b,c,d=p['bbox']; box=[int(a*sx),int(b*sy),max(int(c*sx),int(a*sx)+1),max(int(d*sy),int(b*sy)+1)]
            p['reduced']=describe(reduced,box)
            x,y,z,w=box
            mx=np.broadcast_to((np.arange(a,c,dtype=np.float32)+.5)*sx-.5,(d-b,c-a)).copy()
            my=np.broadcast_to(((np.arange(b,d,dtype=np.float32)+.5)*sy-.5)[:,None],(d-b,c-a)).copy()
            mask=cv2.remap(reduced['mask'],mx,my,cv2.INTER_NEAREST)
            p['reduced_native_disagreement_pixels']=int((mask!=native['mask'][b:d,a:c]).sum())
        record=dict(page=name,input_sha256=row['sha256'],engineering_height=h,native_window=width,
                    native_s=native_s,probes=probes,cheap_calls=calls,
                    old_scouts=old['scouts'],witness=witness,downstream=downstream,
                    independent_native_reference=str(previous/f'{name}.json'),
                    reference_sha256=digest(previous/f'{name}.json'))
        dump(out / f'{name}.json', record)
        receipts.append(dict(page=name,probes=len(probes),native_s=native_s,
            old_candidates=len(old['scouts'][0]['candidates']),new_candidates=len(witness['candidates']),
            new_cuts=len(downstream['changes'])))
        print(name,receipts[-1],flush=True)
    dump(out/'receipt.json',dict(inputs_sha256=digest(inputs),pages=receipts,
         scope='offline candidate only; no source/ownership authority; native observations bypass all scouts'))


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('inputs');p.add_argument('previous');p.add_argument('out')
    a=p.parse_args();cv2.setNumThreads(1);study(a.inputs,a.previous,a.out)
