"""Conditional grid, residual body, and paragraph-initial corrections."""
from time import perf_counter
from .type_context import recover as confirm,grid_view
from .type_lattice import blocks,gaps,inspect_slot
from .type_grid_edges import candidates
from .type_ink_motif_gate import inspect as motif
from .type_table_extent import analyze as table_extent
from ..layout_barriers.fast import run as separators
from .type_residual_recovery import recover as residual_recover
from .type_initials import complete as complete_initial
from .geometry import height_proxy


def recover(gray,items,detector,*,excluded_regions=(),grid_items=None,version=2,column_evidence=None):
    """After shared Q8/B/A: actual polygons own ink, quadrilaterals nominate grids.

    Existing R3 bracketed gaps and R4 phase/edge witnesses share one block scout.
    Excluded B footprints are propagated to all candidates. No separator here.
    """
    start=perf_counter();grid=grid_view(items) if grid_items is None else grid_items
    bb=blocks(grid,(gray.shape[1],gray.shape[0]));old=gaps(bb,items);new=candidates(bb,items,(gray.shape[1],gray.shape[0]),version=2)
    ss=[inspect_slot(gray,s,items,version=3) for s in old+new];evidence=dict(blocks=bb,slots=ss,raw_rows=[],route='heuristic')
    scout=perf_counter();veto=list(excluded_regions);motifs=[];table=None;new_supported=[]
    for i in range(len(old),len(ss)):
        s=ss[i]
        if not s['supported'] or s['owned_fraction']>=.25:continue
        dense=inspect_slot(gray,s,items,dense=True,version=3)
        if not dense['supported'] or dense['owned_fraction']>=.25:continue
        new_supported.append(i)
        h=s['height'];y=s['y'];x0=s['x0'];x1=s['x1'];a=y+s['slope']*(x0-s['xref']);b=y+s['slope']*(x1-s['xref'])
        q=dict(polygon=[[x0,a-.8*h],[x1,b-.8*h],[x1,b+.8*h],[x0,a+.8*h]])
        r,_=motif(gray,q,h);motifs.append(dict(slot=i,**r))
        if r['drop']:veto.append(q)
    if new_supported:
        table=table_extent(gray,items,route='explicit',version=6)
        veto.extend(r['bbox'] for r in table['regions'])
    result=confirm(gray,items,detector,excluded_regions=veto,grid_items=grid,lattice_evidence=evidence,version=4)
    residual=None;initials=[];initial_s=0.;extra_scout=0.
    if version>=2:
        residual=residual_recover(gray,result['items'],detector,excluded_regions=excluded_regions,
                                  version=11,column_evidence=column_evidence)
        result['items']=residual['items'];result['added']=result['added']+residual['added']
        extra_scout=residual['scout_s'];t=perf_counter()
        if result['added']:
            h=height_proxy(items,(gray.shape[1],gray.shape[0]))
            for i,q in enumerate(result['added']):
                after,receipt=complete_initial(gray,q,result['items'],h,excluded_regions=excluded_regions)
                initials.append(dict(addition=i,**receipt))
                if receipt['changed']:
                    result['items']=[after if z is q else z for z in result['items']]
                    result['added'][i]=after
        initial_s=perf_counter()-t
    end=perf_counter();result.update(seconds=end-start,scout_s=scout-start,correction_s=end-scout,
        new_added=[q for q in result['added'] if q.get('type_slot',len(old))>=len(old)],motifs=motifs,table_extents=table,new_slot_start=len(old),version=version,
        residual={k:v for k,v in residual.items() if k!='items'} if residual else None,initials=initials,initial_s=initial_s,
        round5_added_s=(residual['seconds'] if residual else 0.)+initial_s)
    result['scout_s']+=extra_scout;result['correction_s']-=extra_scout
    return result


def run(gray,items,detector,*,version=1):
    start=perf_counter();sep=separators(gray,items);t=perf_counter();r=recover(gray,sep['items'],detector,version=version)
    final=separators(gray,r['items']) if r['added'] else None
    r['items']=final['items'] if final else r['items'];r.update(type_s=perf_counter()-t,added_s=perf_counter()-start,separator=sep,final_separator=final)
    return r
