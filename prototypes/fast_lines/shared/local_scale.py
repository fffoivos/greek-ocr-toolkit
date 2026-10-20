"""Measured local contact extents, with their physical interpretation explicit.

A component's vertical extent includes any joined accent/ascender/descender. It
is not a measured x-height. A compatible lower-contact chain supplies local
sampling scale, not a semantic baseline. Region and ink-calibration pools do
not establish compatible typography. These distinctions survive every caller.

The estimators here are lifted from type_residual.render, page_field.render and
ink_faintness.reference. No histogram mode, new classifier or fallback scale is
introduced. Unknown measurements stay None; engineering fallbacks are callers'
responsibility pending the ink/row migrations.
"""
import numpy as np


def component_extent(boxes, *, compatibility, evidence_version='native.v1'):
    bounds=np.asarray(boxes,float).reshape(-1,4)
    extents=bounds[:,3]-bounds[:,1]
    return dict(value_px=float(np.median(extents)) if len(extents) else None,
                range_px=[float(extents.min()),float(extents.max())] if len(extents) else None,
                support=len(extents),units='native pixels',quantity='connected-ink vertical extent',
                compatibility=compatibility,body_height_px=None,
                uncertain=True,reason='glyph classes and semantic body contacts are not established',
                evidence_version=evidence_version)


def contact_band(top,bottom,step,*,top_support,bottom_support,engineering_prior):
    """Existing strip-contact measurement, not a confidence promotion.

    Even repeated contacts can belong to capitals or a neighbouring row. The
    legacy profile's `uncertain=False` is deliberately not copied as a physical
    guarantee. Saved native-vs-font comparisons document those counterexamples.
    """
    return dict(value_px=float((bottom-top)*step),quantity='strip top-to-bottom contact separation',
                units='native pixels',top_px=float(top*step),bottom_px=float(bottom*step),
                top_support=int(top_support),bottom_support=int(bottom_support),
                body_height_px=None,uncertain=True,
                reason='contact population needs row and glyph-class attribution',
                engineering_prior_px=float(engineering_prior))
