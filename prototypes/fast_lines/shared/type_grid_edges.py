"""One-pitch continuation witnesses outside well-observed type-grid blocks.

An edge is weaker than a bracketed slot. It must retain original ink confirmation
and independent ownership/table/regional-detector checks before any correction.
"""
from time import perf_counter
import numpy as np
from .contracts import bbox
from .type_lattice import blocks,gaps,raw_rows,inspect_slot


def candidates(bb,items,size,*,version=1):
    bounds=np.asarray([bbox(q) for q in items],float).reshape(-1,4);out=[]
    for b in bb:
        h=b['height'];p=b['pitch'];ys=np.asarray(b['centres'])
        if len(ys)<4:continue
        if version>=2:
            for k,(a,d) in enumerate(zip(ys[:-1],ys[1:])):
                n=int(round((d-a)/p))
                # Preserve the round3 bracketed witness. Here render the
                # intervals its global phase residual could not describe.
                if n<2 or n>4 or abs((d-a)-n*p)<=.4*h:continue
                for j in range(1,n):
                    y=float(a+j*(d-a)/n)
                    owned=np.flatnonzero((bounds[:,0]<b['x1'])&(bounds[:,2]>b['x0'])&(abs((bounds[:,1]+bounds[:,3])/2-y)<.65*h))
                    if len(owned):continue
                    out.append(dict(block=b['id'],y=y,height=h,pitch=p,slope=b['slope'],x0=b['x0'],x1=b['x1'],xref=b['xref'],
                        neighbours=[b['members'][k],b['members'][k+1]],status='interior phase uncertainty',edge=0,phase_residual_h=float(((d-a)-n*p)/h)))
        for direction in [-1,1]:
            edge=ys[:4] if direction<0 else ys[-4:]
            if np.max(abs(np.diff(edge)-p))>.4*h:continue
            y=float(edge[0]-p if direction<0 else edge[-1]+p)
            if not h<y<size[1]-h:continue
            owned=np.flatnonzero((bounds[:,0]<b['x1'])&(bounds[:,2]>b['x0'])&(abs((bounds[:,1]+bounds[:,3])/2-y)<.65*h))
            if len(owned):continue
            neighbour=b['members'][0 if direction<0 else -1]
            out.append(dict(block=b['id'],y=y,height=h,pitch=p,slope=b['slope'],x0=b['x0'],x1=b['x1'],xref=b['xref'],
                neighbours=[neighbour],status='one-pitch edge continuation',edge=direction))
    return out


def analyze(gray,items,*,route='heuristic',version=1):
    start=perf_counter();bb=blocks(items,(gray.shape[1],gray.shape[0]));ss=candidates(bb,items,(gray.shape[1],gray.shape[0]),version=version)
    evidence=[inspect_slot(gray,s,items,dense=route=='slow',version=3) for s in ss]
    rows=[]
    if route!='heuristic':
        for b in bb:
            z=dict(b,y0=max(0,b['y0']-1.5*b['pitch']),y1=min(gray.shape[0],b['y1']+1.5*b['pitch']))
            rows.append(dict(block=b['id'],**raw_rows(gray,z,samples=None if route=='slow' else 12)))
    return dict(blocks=bb,slots=evidence,raw_rows=rows,seconds=perf_counter()-start,route=route,
                caveat='unbracketed edge is only a nomination; density and pitch never certify front text')
