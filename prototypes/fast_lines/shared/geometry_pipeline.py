"""Round-four geometry stack: one Q8 scout, equivalent sparse scout, curl joins."""
from time import perf_counter
from .geometry_scout import sparse_fast
from .geometry_context import correct_geometry
from .geometry_feature_rules import refine,split_items
from .geometry_fragment_correct import run as join_fragments
from ..layout_barriers.fast import scout,correct


def run(gray,pm,items):
    start=perf_counter();size=(gray.shape[1],gray.shape[0]);witness,primitive=scout(gray,items)
    sparse=sparse_fast(pm,items,size,3);scout_s=perf_counter()-start
    a=correct_geometry(gray,pm,items,rule_witness=witness,geometry_scout=sparse)
    t=perf_counter();base=correct(gray,a['items'],witness,primitive) if witness['candidates'] else dict(items=a['items'],changes=[])
    curved=None
    if witness['candidates']:
        curved=refine(gray,items,witness,primitive,apply=False,ownership=True,wide_paper=True)
        if curved['rules']:base['items']=split_items(gray,base['items'],curved['rules'],sparse['height'])['items']
    separator_s=perf_counter()-t;prior=base['items'];result=join_fragments(gray,items,prior)
    return dict(items=result['items'],prior=prior,joins=result['joins'],decisions=result['decisions'],
        geometry_changes=a['geometry_changes'],separator_changes=base['changes'],curved=curved,
        scout_s=scout_s,geometry_s=a['geometry_s'],separator_s=separator_s,
        fragment_s=result['seconds'],added_s=perf_counter()-start)
