"""Frozen T4b pixel and token features; extracted without calibration runner."""
import statistics
import numpy as np
from scipy.ndimage import gaussian_filter1d,label as connected_labels,find_objects
from scipy.signal import find_peaks
def pixel_features(crop, fallback_xheight):
    a = np.asarray(crop.convert('L'))
    # Fixed robust dark-ink threshold; no OCR and no additional page segmentation.
    lo, hi = np.percentile(a, [5, 90])
    threshold = min(200., (float(lo)+float(hi))/2)
    ink = a < threshold
    # Estimate body height solely from this existing crop, never G1b's row
    # detector or measurements outside the crop. Accent/noise components and
    # very wide/tall rules are excluded by fixed, unsupervised shape criteria.
    labels, _ = connected_labels(ink)
    heights = []
    for obj in find_objects(labels):
        if obj is None:
            continue
        h, w = obj[0].stop-obj[0].start, obj[1].stop-obj[1].start
        if max(3., a.shape[0]*.12) <= h <= a.shape[0]*.90 and .12 <= w/h <= 3. and w <= max(6., a.shape[1]*.25):
            heights.append(h)
    xheight = float(statistics.median(heights)) if len(heights)>=3 else max(1.,float(fallback_xheight))
    xheight_method = 'crop_component_median_body_height_proxy' if len(heights)>=3 else 'google_token_height_half_fallback'
    ym = ink.sum(axis=1).astype(float)
    xm = ink.sum(axis=0).astype(float)
    nonzero = np.flatnonzero(xm > 0)
    width = int(nonzero[-1]-nonzero[0]+1) if len(nonzero) else 0
    smoothed = gaussian_filter1d(ym, max(.6, xheight*.12))
    peaks, props = find_peaks(np.pad(smoothed, 1), distance=max(2, xheight*.7),
                             prominence=max(2., smoothed.max()*.18), height=max(2., smoothed.max()*.20))
    peaks = peaks-1
    # Internal low-ink run with >=10% ink on either side. Margins never count.
    gap = 0
    cum = np.cumsum(xm)
    if len(nonzero) and cum[-1] > 0:
        low = xm <= max(0., float(np.median(xm[xm > 0]))*.08)
        start = None
        for i in range(int(nonzero[0]), int(nonzero[-1])+2):
            if i < len(low) and low[i]:
                if start is None:
                    start = i
            elif start is not None:
                if cum[max(0, start-1)] >= cum[-1]*.10 and cum[-1]-cum[min(i, len(cum)-1)] >= cum[-1]*.10:
                    gap = max(gap, i-start)
                start = None
    return dict(xheight=xheight, xheight_method=xheight_method, body_component_count=len(heights),
                ink_width=width, ink_pixels=int(ink.sum()), projection_peaks=int(len(peaks)),
                projection_peak_y=peaks.tolist(), internal_gap_xh=gap/max(1., xheight),
                crop_height_xh=a.shape[0]/max(1., xheight))

def token_features(tokens, xheight):
    tt = [t for t in tokens if t['bbox'] and any(c.isalnum() for c in t['text'])]
    yy = sorted((t['bbox'][1]+t['bbox'][3])/2 for t in tt)
    centers = []
    for y in yy:
        if not centers or y-statistics.median(centers[-1]) > .75*xheight:
            centers.append([y])
        else:
            centers[-1].append(y)
    return dict(token_count=len(tt), token_row_clusters=len(centers),
                token_y_spread_xh=float(np.percentile(yy, 90)-np.percentile(yy, 10))/max(1., xheight) if yy else 0.)

def branch(r, b):
    return all(r[k] > v for k, v in b.items())

def reject(r, model):
    return any(branch(r, b) for b in model['branches'])
