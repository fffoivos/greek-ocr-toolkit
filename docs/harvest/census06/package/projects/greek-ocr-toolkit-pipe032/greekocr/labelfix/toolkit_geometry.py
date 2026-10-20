"""Independently selectable S7 geometry candidates. No reference text enters here.

Physical pieces are never manufactured from a recognizer character count.
Unresolved groups retain every recognizer slot and their shared parent labels.
"""
from dataclasses import dataclass, replace
from types import SimpleNamespace
import numpy as np

from greekocr.glyphs.letters import letter_boxes
from greekocr.glyphs.baseline import text_lines, skew_line
from greekocr.pages import font
from . import ink as I
from .ctc_align import transfer_alignment
from .text import clusters, nfd, tokenize


@dataclass(frozen=True)
class SharedGuides:
    mean: np.ndarray
    base: np.ndarray
    ascender: np.ndarray
    descender: np.ndarray
    provenance: dict
    decision: dict
    classes: dict

    def record(self):
        return dict(mean=self.mean.tolist(), base=self.base.tolist(),
                    ascender=self.ascender.tolist(), descender=self.descender.tolist(),
                    provenance=self.provenance, decision=self.decision, classes=self.classes)


def glyph_view(ink):
    g = ink.glyphs
    return replace(g, band=replace(g.band, top=ink.top, bottom=ink.bottom, xh=ink.xh))


def shared_guides(ink, *, apply=False):
    """Keep the toolkit curvature; qualify S6's body-height correction per line."""
    g = ink.glyphs
    fit = ink.font_fit
    use_body = fit['source'] == 'pixel_lowercase_bodies' and fit['n'] >= 4
    xh = ink.xh if use_body else float(g.band.xh)
    # S6's body contacts qualify the vertical gauge/height, not a straightening.
    shift = float(np.median(ink.bottom-g.band.bottom)) if use_body else 0.
    base = g.band.bottom.copy()+shift
    mean = base-xh
    view = replace(g, band=replace(g.band, top=mean, bottom=base, xh=xh))
    four = text_lines(view, max_per_side=0)[0]
    rows = np.array([[c.x0,c.y0,c.x1,c.y1,c.area,c.index,0] for c in g.components], float).reshape(-1,7)
    page = SimpleNamespace(components=rows, labels=g.labels, xheight=xh)
    line = SimpleNamespace(component_ids=[c.index for c in g.components if c.role != 'neighbour'],
                           xheight=xh, baseline=base, x0=0, x1=g.width)
    counts, points = font.evidence(page, line)
    asc = four.ascender.copy()
    desc = four.descender.copy()
    provenance = dict(mean='measured' if use_body or g.band.n_support else 'fallback',
                      base='measured' if g.band.n_support else 'fallback',
                      ascender='fallback', descender='fallback')
    for name, key in [('ascender','font_top'), ('descender','font_bottom')]:
        pts = points[key]
        if len(pts) >= 3:
            offset = float(np.median([y-base[min(g.width-1,max(0,round(x)))] for x,y in pts]))
            if name == 'ascender' and -2.2*xh <= offset <= -1.05*xh:
                asc=base+offset; provenance[name]='measured'
            elif name == 'descender' and .08*xh <= offset <= 1.2*xh:
                desc=base+offset; provenance[name]='measured'
    decision = dict(winner='S6_body_repair' if use_body else 'toolkit',
                    toolkit_xh=float(g.band.xh), selected_xh=float(xh),
                    body_support=fit.get('n',0), baseline_shift=shift,
                    toolkit_degree=g.band.degree,
                    all_capital_evidence=not np.isclose(line.xheight,xh),
                    capital_evidence_xh=float(line.xheight))
    guides=SharedGuides(mean,base,asc,desc,provenance,decision,counts)
    if apply:
        ink.xh=xh; ink.top=mean; ink.bottom=base; ink.shared_guides=guides
    return guides


def physical_slots(ink, text, alignment):
    from .segmentation import _region
    text=nfd(text); alignment=transfer_alignment(text,alignment)
    boxes=letter_boxes(glyph_view(ink))
    tokens=tokenize(text); slots=[]; owners={}
    for cl in clusters(text):
        if not cl.base.isalpha(): continue
        sp=alignment.span(cl.start)
        overlap=[I._overlap(sp.x0,sp.x1,b.x0,b.x1)/np.sqrt(max(b.w,.35*ink.xh)) for b in boxes]
        k=max(range(len(boxes)),key=lambda i:overlap[i]) if boxes else None
        if k is not None and overlap[k]<=0: k=None
        s=dict(base=cl.base,start=cl.start,end=cl.end,locator_span=[sp.x0,sp.x1],
               primary=k,indices=[],component_ids=[],component=None,
               word_final=any(cl.end==t.core_end for t in tokens),
               word_index=next((t.index for t in tokens if t.core_start<=cl.start<t.core_end),-1),
               fused=False,split_union=False,localisation_unknown=False,
               segmentation_source='toolkit_middle_pieces')
        slots.append(s)
        if k is not None: owners.setdefault(k,[]).append(s)
    ink.physical_letters=[dict(x0=b.x0,y0=b.y0,x1=b.x1,y1=b.y1,
                              parents=list(b.components),pieces=b.pieces,merged=b.merged,resolved=b.resolved,
                              recognizer_starts=[s['start'] for s in owners.get(i,[])]) for i,b in enumerate(boxes)]
    ink.physical_mapping=dict(physical_groups=len(boxes),recognizer_letters=len(slots),
        count_disagreement=len(boxes)!=len(slots),
        unassigned_physical=[i for i in range(len(boxes)) if i not in owners],
        shared_physical=[i for i,ss in owners.items() if len(ss)>1],
        unresolved_physical=[i for i,b in enumerate(boxes) if not b.resolved])
    ink.physical_mapping['ambiguous']=bool(ink.physical_mapping['count_disagreement'] or
        ink.physical_mapping['unassigned_physical'] or ink.physical_mapping['shared_physical'] or
        ink.physical_mapping['unresolved_physical'])
    lookup={c.index:c for c in ink.components}
    for k,ss in owners.items():
        b=boxes[k]; ambiguous=len(ss)!=1 or not b.resolved
        for s in ss:
            c=_region(ink,[lookup[i] for i in b.components],b.x0,b.x1)
            # The toolkit also bounds this group's vertical custody to its
            # own line. Do not re-expand a parent label into a neighbouring row.
            if c is not None:
                y0=max(c.y0,b.y0);y1=min(c.y1,b.y1)
                mask=I.component_mask(ink,c)[y0-c.y0:y1-c.y0].copy()
                mask.setflags(write=False)
                c=SimpleNamespace(**{**vars(c),'y0':y0,'y1':y1,'h':y1-y0,'mask':mask})
            s.update(component=c,component_ids=list(b.components),indices=[],
                     region_bounds=[b.x0,b.x1],fused=b.merged>1 or len(ss)>1,
                     fusion_size=max(b.merged,len(ss)),split_union=len(b.components)>1,
                     segmentation_uncertain=ambiguous,localisation_unknown=ambiguous,
                     physical_resolved=b.resolved,physical_piece_count=b.pieces,
                     physical_recognizer_count=len(ss),
                     ambiguity='physical_recognizer_count' if len(ss)!=1 else 'unresolved_bridge' if not b.resolved else None)
    for s in slots:
        if s['component'] is not None: continue
        a,b=s['locator_span']; left=max(0,min(ink.width-1,int(a)));right=min(ink.width,max(left+1,int(b)))
        top,base=ink.band((left+right)/2)
        s.update(component=SimpleNamespace(index=-s['start']-1,x0=left,x1=right,y0=int(top),y1=int(base),
                                          cx=(left+right)/2,w=right-left,h=base-top,role='letter'),
                 region_bounds=[left,right],localisation_unknown=True,segmentation_uncertain=True,
                 physical_resolved=False,physical_piece_count=0,physical_recognizer_count=1,
                 ambiguity='no_physical_piece')
    return slots


def capital_features(ink, slots):
    """Geometric pixel vote, independent of recognizer case and frozen model weights."""
    guides=ink.shared_guides
    for s in slots:
        c=s['component']; x=min(ink.width-1,max(0,int(c.cx)))
        mask=I.component_mask(ink,c)
        cut=int(np.clip(np.floor(guides.mean[x])-c.y0,0,mask.shape[0]))
        upper=mask[:cut];lower=mask[cut:]
        uw=int(upper.any(axis=0).sum()) if upper.size else 0
        lw=int(lower.any(axis=0).sum()) if lower.size else 0
        cap=(abs(c.y0-guides.ascender[x])<=.18*ink.xh and
             abs(c.y1-guides.base[x])<=.18*ink.xh and c.w>=.5*ink.xh and uw>=.6*max(lw,1))
        s['toolkit_capital_features']=dict(ascender_distance=(c.y0-guides.ascender[x])/ink.xh,
            baseline_distance=(c.y1-guides.base[x])/ink.xh,upper_width=uw,body_width=lw,
            all_capital_evidence=guides.decision['all_capital_evidence'],tall_body_count=guides.classes['tall_body'],vote=bool(cap))
        # Reuse S6's existing supporting-probability gate. A tall lowercase
        # ascender reaching the same guide is not by itself a capital.
        if cap and (s.get('capital_probability',0.)>=.4 or guides.decision['all_capital_evidence']):
            s.update(pixel_class='capital',case_class='capital',geometry_capital=True)
        if c.index in ink.case_info:
            ink.case_info[c.index].update({k:s[k] for k in ('pixel_class','case_class','geometry_capital')})


def observation(ink, slot):
    """Directional coverage: missing pixels are UNSEEN, never negative evidence.

    Extent uses the same S6 font scale for S3 alone. Toolkit cut spans also
    catch body exits; validity masks can represent padding inside the raster.
    """
    a,b=slot['region_bounds'];a=max(0,a);b=min(ink.width,b)
    if b<=a:return dict(above='UNSEEN',below='UNSEEN',directions=['unlocated'])
    top=ink.top[a:b]; base=ink.bottom[a:b]; xh=ink.xh
    valid=getattr(ink,'valid_mask',None)
    invalid_upper=invalid_lower=False
    if valid is not None:
        yy=np.arange(ink.height)[:,None]
        invalid=~valid[:,a:b]
        invalid_upper=bool(((yy<top[None,:]) & (yy>=top[None,:]-.9*xh) & invalid).any())
        invalid_lower=bool(((yy>=base[None,:]) & (yy<base[None,:]+.9*xh) & invalid).any())
    directions=[]
    masks=getattr(ink,'cut_masks',{})
    for edge in ('top','bottom','left','right'):
        m=np.asarray(masks.get(edge,False))
        hit=bool(m) if m.ndim==0 else bool(m[a:b].any()) if m.ndim==1 else bool(m[:,a:b].any())
        if hit:directions.append(edge)
    if (top-.9*xh<0).any() or ink.ink[0,a:b].any() or invalid_upper:directions.append('top')
    if (base+.9*xh>ink.height).any() or ink.ink[-1,a:b].any() or invalid_lower:directions.append('bottom')
    for span in ink.toolkit_cuts:
        if span.x0<b and a<span.x1:directions.append(span.edge)
    directions=sorted(set(directions))
    return dict(above='UNSEEN' if set(directions)&{'top','left','right'} else 'OBSERVED',
                below='UNSEEN' if set(directions)&{'bottom','left','right'} else 'OBSERVED',directions=directions)


def prepare_cuts(ink):
    ink.toolkit_cuts=skew_line(glyph_view(ink),boxes=[]).cut_spans


def polytonic_scope(script_class):
    """A line's independent script annotation gates the polytonic checker.

    Unknown and mixed annotations stay eligible. Never infer monotonic from
    the absence of a detected breathing, a source name, or reference text.
    """
    classes={script_class} if isinstance(script_class,str) else set(script_class or ())
    return not ('greek_monotonic' in classes and 'greek_polytonic' not in classes)
