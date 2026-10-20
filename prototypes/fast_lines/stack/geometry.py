"""Thin composition of shared geometry operators with the stack source ledger."""
from time import perf_counter
from collections import Counter
from ..shared.geometry_scout import sparse_fast as sparse
from ..shared.geometry_context import correct_geometry
from ..shared.geometry_feature_rules import refine, split_items
from ..shared.geometry_fragment_correct import run as join_fragments
from ..shared.geometry_columns import analyze as column_evidence, apply as column_split


def run(gray, pm, original, current, witness, primitive, *, forbidden_regions=()):
    start=perf_counter()
    s=sparse(pm,original,(gray.shape[1],gray.shape[0]),3)
    scout_s=perf_counter()-start
    # Shared context accepts intact original sources. Separated pieces stay in
    # the output, but cannot stand in for their original contour or own lost ink.
    counts=Counter(i for q in current for i in q['source_ids'])
    intact=[q['source_ids'][0] for q in current if len(q['source_ids'])==1
            and counts[q['source_ids'][0]]==1
            and q['polygon']==original[q['source_ids'][0]]['polygon']]
    a=correct_geometry(gray,pm,original,retained_source_indices=intact,
                       rule_witness=witness,geometry_scout=s)
    replacements={q['source_ids'][0]:q for q in a['items']}
    out=[replacements[q['source_ids'][0]] if q['source_ids'][0] in replacements else q for q in current]
    audits={q['line']:q['retention'] for q in a['geometry_decisions'] if q['decision']=='native geometry'}
    changes=[dict(q,source=q['line'],retention=audits[q['line']]) for q in a['geometry_changes']]
    t=perf_counter();curved=None
    if witness['candidates']:
        # Ownership sees removed original crossings too: deletion cannot certify a rule.
        curved=refine(gray,original,witness,primitive,apply=False,ownership=True,wide_paper=True)
        split=split_items(gray,out,curved['rules'],witness['height']) if curved['rules'] else dict(items=out,changes=[],decisions=[])
        curved.update(applied=split['changes'],applied_decisions=split['decisions']);out=split['items']
    curved_s=perf_counter()-t
    t=perf_counter()
    columns=column_evidence(gray,original,witness,primitive,retained_source_indices=set(counts))
    extra=column_split(out,columns);out=extra['items'];columns['changes']=extra['changes'];column_s=perf_counter()-t
    fragments=join_fragments(gray,original,out,forbidden_regions=forbidden_regions)
    return dict(items=fragments['items'],changes=changes,decisions=a['geometry_decisions'],
                map_bands=a.get('map_bands'),
                witness=s,curved=curved,columns=columns,column_s=column_s,fragments={k:v for k,v in fragments.items() if k!='items'},
                joined_reduction=len(out)-len(fragments['items']),
                scout_s=scout_s,geometry_s=a['geometry_s'],curved_s=curved_s,
                fragment_s=fragments['seconds'],seconds=perf_counter()-start)
