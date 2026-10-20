"""Physical counterexamples and input contracts for round4 diagnostics."""
import cv2,numpy as np
from ..shared.ink_observability import measure
from ..shared.ink_stamp_field import render as polar
from ..shared.ink_image_structure import render as structure


def test_noise_is_measured_on_raw_residuals_not_truncated_bright_pixels():
    rng=np.random.default_rng(40);g=np.uint8(np.clip(235+rng.normal(0,2,(110,100)),0,255))
    r=measure(g,[20,20,72,92],60,version=3)
    assert 1.7<r['noise_dn']<2.4
    assert r['faintness']=='noise-limited candidate'
    assert r['readability']=='unknown'


def test_fading_changes_noise_observability_even_with_unchanged_shape():
    ink=np.zeros((110,100),float);ink[25:85,25:35]=1;ink[25:35,25:65]=1
    noise=np.random.default_rng(40).normal(0,2,ink.shape)
    strong=np.uint8(np.clip(235-180*ink+noise,0,255));faint=np.uint8(np.clip(235-1.8*ink+noise,0,255))
    a=measure(strong,[20,20,72,92],60,version=3);b=measure(faint,[20,20,72,92],60,version=3)
    assert a['core_snr']>40 and b['core_snr']<4
    assert a['topology_stable'] and not b['topology_stable']
    assert a['cause']==b['cause']


def test_empty_threshold_masks_are_not_stable_resolved_topology():
    r=measure(np.full((100,100),235,np.uint8),[25,25,75,75],50,version=3)
    assert not r['topology_stable'] and r['core_snr']<4


def test_ring_requires_radial_stroke_not_an_arbitrary_fitted_ellipse():
    g=np.full((180,180),235,np.uint8);cv2.circle(g,(90,90),60,80,3)
    ring=dict(center=[90,90],diameters=[120,120],angle=0)
    r=polar(g,ring,20,version=4)
    near=[q for q in r['rings'] if abs(q['radius_factor']-1)<.06]
    assert near and max(q['support'] for q in near)>.8
    noise=np.uint8(np.clip(235+np.random.default_rng(3).normal(0,8,g.shape),0,255))
    r=polar(noise,ring,20,version=4)
    assert max(r['profile'])<.3


def test_sparse_spokes_remain_a_proxy_not_an_exclusion():
    g=np.full((180,180),235,np.uint8);cv2.circle(g,(90,90),60,80,3)
    ring=dict(center=[90,90],diameters=[120,120],angle=0)
    r=polar(g,ring,20,route='heuristic',version=4)
    assert r['rings'] and r['safe_exclusions']==[]


def test_long_stroke_rendering_is_scale_relative():
    g=np.full((100,200),235,np.uint8);cv2.line(g,(30,50),(170,50),20,3)
    a=structure(g,20,version=2);b=structure(g,100,version=2)
    assert a['segments'] and not b['segments']
    assert a['safe_exclusions']==[]
