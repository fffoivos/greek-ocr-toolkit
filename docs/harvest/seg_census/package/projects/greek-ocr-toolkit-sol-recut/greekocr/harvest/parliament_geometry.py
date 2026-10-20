"""T23 native geometry for DocAI's large-image integer/normalized disagreement.

Use provider normalized vertices in the explicitly reported native pixel frame
when integer vertices disagree. No inferred scale, text matching, new read, or
raw-response mutation. Recorded transform cases retain the original T15 path.
"""
from __future__ import annotations

import copy
import math

from .page_reads import _response_geometry as original_geometry


def response_geometry(engine,raw,native_size):
    if engine!='docai':return original_geometry(engine,raw,native_size)
    page=raw['document']['pages'][0]
    dimension=page.get('dimension',{})
    returned=(dimension.get('width'),dimension.get('height'))
    if page.get('transforms') or returned!=tuple(native_size):
        return original_geometry(engine,raw,native_size)
    discrepancy=0
    for node in page.get('lines',[]):
        polygon=node.get('layout',{}).get('boundingPoly',{})
        integers=polygon.get('vertices',[]);normalized=polygon.get('normalizedVertices',[])
        if len(integers)==len(normalized) and integers:
            discrepancy=max(discrepancy,max(abs(a.get(axis,0)-b.get(axis,0)*native_size[j])
                for a,b in zip(integers,normalized) for j,axis in enumerate(('x','y'))))
    if discrepancy<=1.5:
        result=original_geometry(engine,raw,native_size)
        result['coordinate_frame']['vertex_source']='provider_integer_vertices'
        result['coordinate_frame']['integer_normalized_max_difference_px']=discrepancy
        return result
    if dimension.get('unit')!='pixels':raise ValueError('normalized native frame is not reported in pixels')
    if (page.get('image',{}).get('width'),page.get('image',{}).get('height'))!=tuple(native_size):
        raise ValueError('normalized frame does not match returned native image dimensions')
    converted=copy.deepcopy(raw);converted_page=converted['document']['pages'][0]
    for kind in ('lines','paragraphs','symbols'):
        for node in converted_page.get(kind,[]):
            polygon=node.get('layout',{}).get('boundingPoly',{})
            if not polygon:continue
            normalized=polygon.get('normalizedVertices',[])
            if not normalized:raise ValueError('conflicting integer frame without normalized vertices')
            vertices=[dict(x=v.get('x',0)*native_size[0],y=v.get('y',0)*native_size[1]) for v in normalized]
            if not all(math.isfinite(v[axis]) for v in vertices for axis in ('x','y')):
                raise ValueError('nonfinite normalized vertex')
            polygon['vertices']=vertices;polygon.pop('normalizedVertices',None)
    result=original_geometry(engine,converted,native_size)
    result['coordinate_frame'].update(vertex_source='provider_normalized_vertices',
        integer_normalized_max_difference_px=discrepancy,raw_response_unchanged=True,
        normalized_reference_size=list(native_size))
    return result
