"""Reusable tone and glyph-shape operators, adapted from stopped 8e5c522.

No ownership labels here. Components are observed fragments, not known characters."""
import cv2
import numpy as np
from dataclasses import dataclass
from numbers import Integral, Real
from typing import NamedTuple
from .geometry import roi, quantize
from .image_evidence import components


def percentiles8(patch, qs):
    """Exact NumPy linear percentiles for a nonempty uint8 sampled patch."""
    counts=np.bincount(patch.ravel(),minlength=256).cumsum()
    ranks=np.asarray(qs,dtype=float)*(patch.size-1)/100
    lo=np.floor(ranks).astype(int);hi=np.ceil(ranks).astype(int)
    a=np.searchsorted(counts,lo,side='right');b=np.searchsorted(counts,hi,side='right')
    return a+(b-a)*(ranks-lo)


def tones(gray, box, lows=(2,10)):
    x0,y0,x1,y1=roi(box,gray.shape)
    patch=gray[y0:y1:max(1,(y1-y0)//24),x0:x1:max(1,(x1-x0)//192)]
    if not patch.size: return np.zeros(len(lows))
    values=percentiles8(patch,[*lows,90]);hi=values[-1]
    return (hi-values[:-1])/max(hi,1)


def sample_boxes(gray, boxes, prepared=None):
    """Sample both tone percentiles once per exact native sampling rectangle.

    A prepared tuple is (immutable image, integer bounds, two tone values).
    It lives only within one compose call. A changed image or rectangle is
    sampled afresh; changed censuses still rebuild anchors and classification.
    Returned values are owned, so consumers cannot mutate the producer.
    """
    bounds=np.asarray([roi(b,gray.shape) for b in boxes],int).reshape(-1,4)
    previous=(prepared is not None and prepared[0] is gray)
    if previous and np.array_equal(bounds,prepared[1]):
        return (gray,bounds,prepared[2].copy())
    values=np.empty((len(bounds),2))
    for i,b in enumerate(bounds):
        match=np.flatnonzero(np.all(prepared[1]==b,axis=1)) if previous else []
        values[i]=prepared[2][match[0]] if len(match) else tones(gray,b)
    return (gray,bounds,values)


def tone(gray, box, low=10):
    return float(tones(gray,box,(low,))[0])


def glyph_pixels(gray, box, threshold=.70, prepared=()):
    """Native labels before height/area/limit selection, not a glyph census.

    An observation is (immutable gray, exact clipped ROI, threshold, labels,
    stats, normalized components). The operator is native percentile90/10 threshold and CC8, no halo or
    transform. Only these height-independent pixels are shared within compose;
    anchors, glyph filters and source votes remain caller-owned. The fixed
    22x22 shape normalization can be reused for the identical native component;
    each consumer receives owned copies, never mutable shared line metadata.
    Arrays are read-only and never carry a line/source owner. Gray must remain
    immutable for the observation's invocation-local lifetime.
    """
    bounds=tuple(roi(box,gray.shape))
    for p in prepared:
        if p[0] is gray and p[1]==bounds and p[2]==threshold:return p
    x0,y0,x1,y1=bounds;raw=gray[y0:y1,x0:x1]
    labels=stats=None
    if raw.size:
        paper,core=percentiles8(raw,[90,10]);depth=float(paper-core)
        if depth>=1:
            binary=(raw < paper-threshold*depth).astype(np.uint8)
            labels,stats,_=components(binary)
            labels.flags.writeable=False;stats.flags.writeable=False
    return gray,bounds,threshold,labels,stats,{}


def normalized_glyph(labels,j,x,y,w,h):
    """Fixed tile/vector observation; no engineering height or owner input."""
    patch=(labels[y:y+h,x:x+w]==j+1).astype(np.float32)
    scale=18/max(h,w);sw,sh=quantize(w*scale),quantize(h*scale)
    patch=cv2.resize(patch,(sw,sh),interpolation=cv2.INTER_AREA)
    tile=np.zeros((22,22),np.float32);tx=(22-sw)//2;ty=(22-sh)//2
    tile[ty:ty+sh,tx:tx+sw]=patch
    tile=cv2.GaussianBlur(tile,(3,3),.6)
    v=tile.ravel();v=v-v.mean();v=v/max(np.linalg.norm(v),1e-6)
    tile.flags.writeable=False;v.flags.writeable=False
    return tile,v


def glyphs(gray, box, height, threshold=.70, limit=64, *, pixels=None):
    x0,y0,x1,y1=roi(box,gray.shape)
    pixels=glyph_pixels(gray,box,threshold) if pixels is None else pixels
    if pixels[0] is not gray or pixels[1]!=(x0,y0,x1,y1) or pixels[2]!=threshold:
        raise ValueError('glyph pixels require the same immutable image, native ROI and threshold')
    labels,stats,normalized=pixels[3:]
    if labels is None:return []
    found=[]
    for j,(x,y,w,h,area) in enumerate(stats):
        if not (.35*height<h<1.8*height and .12*height<w<1.6*height): continue
        if area < .055*height*height or x==0 or y==0 or x+w>=x1-x0 or y+h>=y1-y0: continue
        if j not in normalized:normalized[j]=normalized_glyph(labels,j,x,y,w,h)
        tile,v=normalized[j]
        found.append(dict(bbox=[int(x+x0),int(y+y0),int(x+x0+w),int(y+y0+h)], vector=v.copy(), tile=tile.copy(),
                          aspect=float(w/h), height=float(h)))
    if len(found)>limit:
        found=[found[i] for i in np.linspace(0,len(found)-1,limit).astype(int)]
    return found


class GlyphExemplar(NamedTuple):
    bbox: tuple
    line: int | None


@dataclass(frozen=True, slots=True, init=False)
class GlyphAtlas:
    vectors: np.ndarray
    aspects: np.ndarray
    exemplars: tuple[GlyphExemplar, ...]

    def __init__(self, *args, **kwargs):
        raise TypeError('use glyph_atlas(selected_glyphs), not independent atlas parts')

    @classmethod
    def _observe(cls, glyphs):
        # One ordered census supplies every part. There is no arrays/metadata
        # assembler, including through dataclasses.replace.
        census=tuple(glyphs)
        vectors=np.array([g['vector'] for g in census],np.float32)
        aspects=np.array([g['aspect'] for g in census],np.float64)
        exemplars=tuple(GlyphExemplar(tuple(g['bbox']),g.get('line')) for g in census)
        n=len(census)
        if vectors.shape!=((n,484) if n else (0,)) or aspects.shape!=(n,):
            raise ValueError('atlas requires one 484-vector and scalar aspect per exemplar')
        if any(len(e.bbox)!=4 or not all(isinstance(v,Real) for v in e.bbox)
               or (e.line is not None and not isinstance(e.line,Integral)) for e in exemplars):
            raise ValueError('atlas exemplar requires four native coordinates and integer line or None')
        # A read-only owned base prevents ordinary setflags(write=True) on the
        # exposed view. This is an API contract, not an introspection boundary.
        vectors.flags.writeable=False;aspects.flags.writeable=False
        value=object.__new__(cls)
        object.__setattr__(value,'vectors',vectors.view())
        object.__setattr__(value,'aspects',aspects.view())
        object.__setattr__(value,'exemplars',exemplars)
        return value

    def __len__(self):
        return len(self.exemplars)


def glyph_atlas(atlas):
    """One owned observation of this selected ordered glyph census.

    Scored arrays and native exemplar metadata have the same order and lifetime.
    Source records may subsequently change; a new census needs a new snapshot.
    This value carries no row-ownership or source decision.
    """
    return GlyphAtlas._observe(atlas)


def match_glyphs(query, atlas: GlyphAtlas):
    if not isinstance(atlas,GlyphAtlas):raise TypeError('matcher requires glyph_atlas observation')
    if not query or not atlas: return []
    a,aspects=atlas.vectors,atlas.aspects
    q=np.array([g['vector'] for g in query],np.float32)
    qr=q.reshape(-1,22,22)[:,:,::-1].reshape(-1,484).copy()
    # OpenCV GEMM obeys cv2's thread setting, avoiding an unbounded BLAS pool.
    direct=cv2.gemm(q,a,1,None,0,flags=cv2.GEMM_2_T)
    reflected=cv2.gemm(qr,a,1,None,0,flags=cv2.GEMM_2_T)
    # Compare shapes at compatible aspect ratio; do not stretch one glyph to another.
    compatible=np.abs(np.log(np.array([g['aspect'] for g in query])[:,None]/aspects[None,:]))<.22
    direct[~compatible]=-1;reflected[~compatible]=-1
    di=direct.argmax(1);ri=reflected.argmax(1)
    return [dict(bbox=g['bbox'],direct=float(direct[i,di[i]]),reflected=float(reflected[i,ri[i]]),
                 margin=float(reflected[i,ri[i]]-direct[i,di[i]]),direct_id=int(di[i]),reflected_id=int(ri[i])) for i,g in enumerate(query)]


def motif(gray, box, height):
    x0,y0,x1,y1=roi(box,gray.shape)
    raw=gray[y0:y1,x0:x1]
    if not raw.size or raw.shape[1]<4*height: return dict(repeat=0.,lag_h=0.)
    s=min(1.,12/height)
    patch=cv2.resize(raw,None,fx=s,fy=s,interpolation=cv2.INTER_AREA).astype(np.float32)
    patch=patch.mean(0); patch=patch-patch.mean()
    values=[]
    for lag in range(quantize(.35*height*s),min(quantize(4*height*s),len(patch)//4)):
        a,b=patch[:-lag],patch[lag:]
        v=float(a@b/max(np.linalg.norm(a)*np.linalg.norm(b),1e-6))
        values.append((v,lag))
    if not values: return dict(repeat=0.,lag_h=0.)
    v,lag=max(values)
    return dict(repeat=v,lag_h=lag/(height*s),lag=lag/s,bbox=list(box))
