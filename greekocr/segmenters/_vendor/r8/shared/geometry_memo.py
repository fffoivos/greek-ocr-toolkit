"""Call-local memoization of immutable polygon geometry, never page decisions.

Stack operators replace polygons when they edit geometry; they do not mutate
vertices in place. Hold each polygon reference until this call ends, preventing
object-id reuse. No image, ownership, exclusion, or confidence is cached here.
Standalone geometry calls keep their original uncached behavior.
"""
from contextvars import ContextVar
from functools import wraps

_current=ContextVar('fast_lines_geometry_memo',default=None)


def entry(polygon):
    memo=_current.get()
    if memo is None:return None
    key=id(polygon)
    if key not in memo:memo[key]=(polygon,{})
    return memo[key][1]


def page_geometry(function):
    @wraps(function)
    def call(*args,**kwargs):
        token=_current.set({})
        try:return function(*args,**kwargs)
        finally:_current.reset(token)
    return call
