"""Conditional spatial front/back ownership; unknown always means preserve.

Adapted from stopped 8e5c522; conditional suppression after feature review.
Same-page strong-print component exemplars are compared with ordinary/reflected
candidate components. Faintness nominates work but never authorizes a removal.
Runtime inputs contain no page identifiers, cohorts or old-model answers.
"""
from time import perf_counter
import numpy as np
from .contracts import bbox
from .geometry import height_proxy
from .ink_photometry import tone,sample_boxes,glyphs,match_glyphs,glyph_pixels,glyph_atlas


def analyze(gray, items, regions=None, *, detail=False, route='explicit',height=None,tone_samples=None,glyph_samples=(),glyph_output=None):
    """Assess full-page rectangles; default existing Paddle envelopes.

    Return regions with ownership front/back/unknown, reasons, spatial witnesses,
    suppress_indices indexing the requested regions, and charged fresh seconds.
    No region outside a supported candidate is suppressed. One call batches ROIs.
    Front is an ordinary-shape hypothesis, not proof for missing-line recovery.
    A region needs its own glyph witnesses; nearby rows cannot certify its source.
    Optional glyph_samples/output transport native anchor pixels/fixed tiles;
    the actual census, height selection and requested-region decisions are fresh.
    """
    if route not in ('explicit','sampled','dense'):
        raise ValueError('route must be explicit, sampled or dense')
    t=perf_counter();height=height_proxy(items,(gray.shape[1],gray.shape[0])) if height is None else float(height)
    if not np.isfinite(height) or height<=0:raise ValueError('height must be a positive finite bbox-height proxy')
    boxes=[bbox(q) for q in items]
    samples=sample_boxes(gray,boxes,tone_samples);sampled=samples[2]
    tones=sampled[:,1]
    high=float(np.percentile(tones,80)) if len(tones) else 0.
    requested=boxes if regions is None else [list(b) for b in regions]
    requested_samples=sampled if regions is None else sample_boxes(gray,requested,samples)[2]
    ts=requested_samples[:,1]
    anchors=[i for i,b in enumerate(boxes) if tones[i]>.85*high and b[2]-b[0]>8*height]
    anchors=sorted(anchors,key=lambda i:-tones[i])[:(6 if route=='sampled' else 12)]
    cores=requested_samples[:,0]
    anchor_core=float(np.median(sampled[anchors,0])) if anchors else 0.
    weak=[i for i,b in enumerate(requested) if ts[i]<.72*high and cores[i]<.5*anchor_core]
    suspects=[i for i in weak if requested[i][2]-requested[i][0]>2*height]
    scout_s=perf_counter()-t
    atlas=[]
    if suspects and len(anchors)>=3 and high>.08:
        for i in anchors:
            pixels=glyph_pixels(gray,boxes[i],prepared=glyph_samples)
            if glyph_output is not None:glyph_output.append(pixels)
            for g in glyphs(gray,boxes[i],height,limit=48 if route=='sampled' else (256 if route=='dense' else 64),pixels=pixels):
                g['line']=i;atlas.append(g)
    observation=glyph_atlas(atlas) if atlas else None
    rows=[]
    for i,b in enumerate(requested):
        r=dict(bbox=b,ownership='unknown',reason='no independent handedness evidence',
               relative_tone=float(ts[i]/max(high,1e-6)),relative_core=float(cores[i]/max(anchor_core,1e-6)),front_votes=0,back_votes=0)
        if i in suspects and observation:
            matches=match_glyphs(glyphs(gray,b,height,limit=24 if route=='sampled' else (256 if route=='dense' else 64)),observation)
            f=[m for m in matches if m['direct']>=.80 and m['margin']<=-.08]
            back=[m for m in matches if m['reflected']>=.80 and m['margin']>=.08]
            r.update(front_votes=len(f),back_votes=len(back))
            if len(back)>=4 and len(back)>=2*len(f):
                r.update(ownership='back',reason='multiple asymmetric glyph cores favour reflection of strong-print exemplars')
            elif len(f)>=4 and len(f)>=2*len(back):
                r.update(ownership='front',reason='multiple asymmetric glyph cores favour ordinary strong-print exemplars')
            if detail:
                r['matches']=matches
                r['witnesses']=[dict(m,exemplar=list(observation.exemplars[m['reflected_id'] if m['margin']>0 else m['direct_id']].bbox)) for m in back+f]
        rows.append(r)
    return dict(version='B5',route=route,regions=rows,suppress_indices=[i for i,r in enumerate(rows) if r['ownership']=='back'],
                anchors=anchors,atlas_glyphs=len(observation) if observation else 0,suspects=suspects,weak_indices=weak,height=height,
                image_size=[gray.shape[1],gray.shape[0]],scout_s=scout_s,seconds=perf_counter()-t)
