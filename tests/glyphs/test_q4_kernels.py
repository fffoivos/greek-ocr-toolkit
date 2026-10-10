"""Differential checks for replacements of Q3b's numerical/library operations."""
import numpy as np
import pytest
from scipy import ndimage as ndi

from greekocr.glyphs.components import _hole_sizes, _xheight, _ransac_line
from greekocr.pages.pixels import _rect_morphology
from greekocr.pages.statistics import _curve


@pytest.mark.parametrize('shape', [(1, 1), (2, 1), (1, 2), (3, 4), (4, 3), (7, 7), (18, 1), (1, 18)])
def test_rect_morphology_matches_scipy_border_and_even_origins(shape):
    rng = np.random.default_rng(82)
    for size in ((1, 1), (5, 8), (31, 29)):
        for density in (0., .2, .6, 1.):
            mask = rng.random(size) < density
            for closing, reference in ((False, ndi.binary_opening), (True, ndi.binary_closing)):
                np.testing.assert_array_equal(_rect_morphology(mask, shape, closing=closing),
                                              reference(mask, structure=np.ones(shape)))


def test_holes_match_scipy_with_diagonal_contacts_and_border_ink():
    rng = np.random.default_rng(93)
    for shape in ((1, 1), (3, 3), (12, 13), (33, 20)):
        for density in (0., .2, .5, .8, 1.):
            for _ in range(5):
                mask = rng.random(shape) < density
                holes = ndi.binary_fill_holes(mask) & ~mask
                labels, _ = ndi.label(holes)
                expected = np.bincount(labels.ravel())[1:]
                np.testing.assert_array_equal(np.sort(_hole_sizes(mask)), np.sort(expected))


def test_size_mode_preserves_closed_interval_endpoints():
    rng = np.random.default_rng(12)
    for size in (0, 1, 13, 400):
        hs = np.sort(rng.integers(3, 100, size=size).astype(float))
        if size:
            counts = [np.sum((hs >= v*.88) & (hs <= v*1.12)) for v in hs]
            expected = float(np.median(hs[np.asarray(counts) >= .9*max(counts)]))
        else:
            expected = 0.
        assert _xheight(hs) == expected


def test_ransac_preserves_rng_candidates_and_first_winner():
    rng = np.random.default_rng(27)
    for n in (0, 1, 2, 7, 31, 80):
        for _ in range(10):
            xs = rng.integers(0, 800, size=n).astype(float)
            ys = .05*xs + rng.integers(-20, 20, size=n)
            gen = np.random.default_rng(4)
            expected = np.ones(n, bool)
            if n >= 3:
                best_n = -1
                for i,j in gen.integers(0,n,size=(min(200,n*n),2)):
                    if xs[i] == xs[j]: continue
                    slope=(ys[j]-ys[i])/(xs[j]-xs[i])
                    if abs(slope) > .2: continue
                    inliers=abs(ys-(ys[i]+slope*(xs-xs[i]))) <= 3.2
                    if inliers.sum() > best_n:
                        best_n,expected=int(inliers.sum()),inliers
            np.testing.assert_array_equal(_ransac_line(xs,ys,3.2,np.random.default_rng(4)),expected)


def test_unit_grid_interpolation_is_bit_exact_including_extrapolation():
    rng = np.random.default_rng(1)
    for n in (1, 2, 100):
        values=rng.normal(size=n).tolist()
        line=dict(x0=12,x1=12+n,baseline=values)
        for x in np.r_[np.arange(10,15+n,.5),rng.uniform(0,200,100)]:
            assert _curve(line,'baseline',x).hex() == float(np.interp(x,np.arange(12,12+n),values)).hex()


def test_peeling_descriptor_cache_matches_uncached_measurement():
    from greekocr.glyphs.components import _line_glyphs as line_glyphs
    gray=np.full((90,180),235.)
    for y in (12,52):
        for x in range(8,160,24):
            gray[y:y+20,x:x+13]=40
            gray[y+4:y+16,x+4:x+9]=235
    cache={}
    for step in range(2):
        before=line_glyphs(gray,xh_prior=20,focus=(20,40))
        after=line_glyphs(gray,xh_prior=20,focus=(20,40),_component_cache=cache)
        assert before.components == after.components
        assert before.band.support == after.band.support
        for field in ('gray','ink','labels','dt'):
            np.testing.assert_array_equal(getattr(before,field),getattr(after,field))
        np.testing.assert_array_equal(before.band.bottom,after.band.bottom)
        gray[:40]=235
    assert cache


def test_descriptor_cache_preserves_translated_bounds_and_border_contacts():
    from greekocr.glyphs.components import _line_glyphs
    cache = {}
    for offset, shape in ((0, (40, 60)), (7, (58, 82)), (12, (70, 93))):
        gray = np.full(shape, 235.)
        gray[offset:offset+20, offset:offset+13] = 40
        gray[offset+4:offset+16, offset+4:offset+9] = 235
        kwargs = dict(xh_prior=20, focus=(offset+10, offset+30), _geometry_only=True)
        expected = _line_glyphs(gray, **kwargs)
        actual = _line_glyphs(gray, _component_cache=cache, **kwargs)
        assert expected.components == actual.components
        np.testing.assert_array_equal(expected.band.bottom, actual.band.bottom)


def test_grouped_percentiles_and_median_preserve_exact_values():
    from greekocr.pages.statistics import _distribution, _median
    rng = np.random.default_rng(64)
    for size in (0, 1, 2, 3, 20, 301):
        values = rng.normal(size=size).tolist() + [None, np.nan, np.inf]
        a = np.asarray([v for v in values if v is not None and np.isfinite(v)], float)
        actual = _distribution(values)
        assert _median(values) == actual['median']
        if len(a):
            for key, value in (('median', np.median(a)), ('p10', np.percentile(a, 10)),
                               ('p90', np.percentile(a, 90)), ('mean', a.mean()), ('std', a.std())):
                assert actual[key].hex() == float(value).hex()


def test_proven_peel_masks_match_binarise_after_arbitrary_whitening():
    from greekocr.glyphs.components import _stable_peel_ink, binarise
    rng = np.random.default_rng(512)
    accepted = rejected = 0
    for shape in ((31, 1), (32, 39), (63, 120)):
        for paper in (210., 235.3, 255.):
            for density in (.03, .2, .85):
                for ink_level in (0., 80., 180., 208.):
                    mask = rng.random(shape) < density
                    gray = np.where(mask, ink_level, paper)
                    if not _stable_peel_ink(gray, paper):
                        rejected += 1
                        continue
                    accepted += 1
                    for _ in range(6):
                        np.testing.assert_array_equal(binarise(gray), gray < paper)
                        gray[rng.random(shape) < .3] = paper
    assert accepted > 10 and rejected > 10


def test_discovery_geometry_does_not_depend_on_hole_or_stroke_measurements():
    from greekocr.glyphs.components import _line_glyphs as line_glyphs
    from greekocr.glyphs.baseline import text_lines
    gray=np.full((90,240),235.)
    for x in range(10,220,24):
        gray[20:44,x:x+15]=40
        gray[24:40,x+4:x+10]=235
        gray[12:15,x+6:x+9]=40
    complete=line_glyphs(gray,xh_prior=24,focus=(30,50))
    geometry=line_glyphs(gray,xh_prior=24,focus=(30,50),_geometry_only=True)
    assert complete.band.support == geometry.band.support
    np.testing.assert_array_equal(complete.band.bottom,geometry.band.bottom)
    for a,b in zip(complete.components,geometry.components):
        for field in ('index','x0','x1','y0','y1','area','darkness','fill','touches','role','rel_h','rel_w','rel_cy'):
            assert getattr(a,field) == getattr(b,field)
    for name in ('ascender','mean','base','descender'):
        np.testing.assert_array_equal(getattr(text_lines(complete)[0],name),getattr(text_lines(geometry)[0],name))


def test_diagnostic_broad_phase_never_drops_an_original_positive_pair():
    from types import SimpleNamespace
    from greekocr.pages.lines import (_diagnostic_pairs, GEOMETRY_COMPARISON_EPSILON_PX,
                                      JOIN_MAX_GAP_XH, JOIN_BASELINE_SLACK_XH)
    rng=np.random.default_rng(15)
    lines=[]
    for _ in range(80):
        left=int(rng.integers(0,180)); width=int(rng.integers(2,90))
        base=rng.uniform(0,120)+rng.normal(size=width)
        lines.append(SimpleNamespace(x0=left,x1=left+width,baseline=base,
            top=base-rng.uniform(5,20),bottom=base+rng.uniform(2,10),xheight=float(rng.uniform(6,15)),discounted=None))
    pairs=_diagnostic_pairs(lines)
    for i,a in enumerate(lines):
        assert pairs[i].tolist() == sorted(pairs[i].tolist())
        for j in range(i+1,len(lines)):
            b=lines[j]; lo,hi=max(a.x0,b.x0),min(a.x1,b.x1)
            if hi>lo:
                ai,bi=slice(lo-a.x0,hi-a.x0),slice(lo-b.x0,hi-b.x0)
                positive=np.any(np.minimum(a.bottom[ai],b.bottom[bi])-np.maximum(a.top[ai],b.top[bi]) > GEOMETRY_COMPARISON_EPSILON_PX)
            else:
                left,right=(a,b) if a.x0<b.x0 else (b,a)
                positive=(right.x0-left.x1 <= JOIN_MAX_GAP_XH*max(left.xheight,right.xheight)
                          and abs(left.baseline[-1]-right.baseline[0]) <= JOIN_BASELINE_SLACK_XH*min(left.xheight,right.xheight))
            if positive: assert j in pairs[i]


def test_run_edges_preserve_half_open_endpoints_and_numeric_fallback():
    from greekocr.pages.pixels import _runs
    rng=np.random.default_rng(2)
    for n in (0,1,2,30,200):
        for density in (0.,.2,.8,1.):
            for mask in (rng.random(n)<density,rng.integers(-2,4,n)):
                edges=np.diff(np.r_[False,mask,False].astype(np.int8))
                expected=[(int(a),int(b)) for a,b in zip(np.flatnonzero(edges==1),np.flatnonzero(edges==-1))]
                assert _runs(mask)==expected
