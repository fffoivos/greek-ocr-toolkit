"""A04: local pitch alternatives and shared smooth displacement, no image resampling."""
import numpy as np
from ..shared.geometry import sample_strip,peak_track,robust_fit,ribbon,line_axis,comparison,pitch_candidates
from ..shared.contracts import bbox,result

def run(ctx,phase=3):
    layout=ctx.get('layout_barriers'); blocks=layout.get('blocks',[[0,0,*ctx.size]])
    anchors=[]; grids=[]; fields=[]; output=list(ctx.items); paths=[]; comparisons=[]; ref={r['id']:r for r in ctx.reference.get('lines',[])}
    for bid,b in enumerate(blocks):
        members=[i for i,q in enumerate(ctx.items) if b[0]<=(bbox(q)[0]+bbox(q)[2])/2<b[2]]
        strip=ctx.ev.crop(ctx.ev.contrast,b); pitch=pitch_candidates(strip.mean(1),ctx.ev.body) if strip.size else []
        centres=[(bbox(ctx.items[i])[1]+bbox(ctx.items[i])[3])/2 for i in members]
        grids.append(dict(block=bid,pitch_candidates=pitch,members=members,centres=centres,phases=[[(y*ctx.ev.sy)%p['pitch'] for y in centres] for p in pitch],ownership='unknown; dominant grid is not front'))
        local=[]
        for i in members:
            q=ctx.items[i]; box=bbox(q)
            if box[2]-box[0]<8*ctx.height: continue
            s,x,y,o=sample_strip(ctx.pm,q,ctx.size,ctx.height,nx=17,ny=31,extend=0)
            dy,support=peak_track(s,o); ok=support>.3
            if ok.sum()<8: continue
            xn=(x-b[0])/max(b[2]-b[0],1); residual=dy/ctx.height
            coef=robust_fit(xn[ok],residual[ok],degree=2)
            local.append((i,coef,x,y,dy,support))
            anchors.append(dict(line=i,block=bid,points=np.c_[x,y+dy].tolist(),support=support.tolist(),affine=line_axis(q).tolist()))
        if len(local)<4 or layout.get('table'):
            fields.append(dict(block=bid,status='underconstrained or protected table')); continue
        coef=np.median(np.stack([l[1] for l in local]),axis=0)
        residuals=[float(np.median(abs(l[4]/ctx.height-np.polynomial.polynomial.polyval((l[2]-b[0])/max(b[2]-b[0],1),coef)))) for l in local]
        fields.append(dict(block=bid,bbox=b,coef=coef.tolist(),height=ctx.height,residuals_h=residuals,status='shared candidate',anchor_lines=[l[0] for l in local]))
        if phase==1: continue
        for l,res in zip(local,residuals):
            i,_,x,y,dy,support=l; corr=np.polynomial.polynomial.polyval((x-b[0])/max(b[2]-b[0],1),coef)*ctx.height
            if res>.35: continue
            if max(abs(corr))<.2*ctx.height: continue
            p=np.c_[x,y+corr].tolist(); paths.append(p); box=bbox(ctx.items[i])
            output[i]=dict(ctx.items[i],polygon=ribbon(x,y+corr,box[3]-box[1]),baseline=None,centreline=p,source_ids=[i],provenance='shared block field, physical leaf unverified')
            if i in ref: comparisons.append(dict(line=i,**comparison(p,ref[i]['path'],ctx.height)))
    return result(output,anchors=anchors,grids=grids,fields=fields,paths=paths,comparisons=comparisons,
                  regions=[dict(bbox=f['bbox']) for f in fields if 'bbox' in f],status='provisional block fields; leaf identity unresolved')
