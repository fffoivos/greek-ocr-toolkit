"""Pixel case evidence. No reference text enters runtime classification.

The recogniser is a case prior, and its disagreement with pixels is retained.
Models are trained only on C1 agreeing letters, never evaluation books.
"""
from functools import lru_cache
from pathlib import Path
import numpy as np
from scipy import ndimage as ndi
from .ink import component_mask

ASCENDERS='βδζθλξϑ'
DESCENDERS='γημρφχψ'

def label(base):
    if base.isupper():return 'capital'
    if base in DESCENDERS:return 'lowercase_descender'
    if base in ASCENDERS:return 'lowercase_ascender'
    return 'lowercase_body'

def features(ink,c):
    xh=max(ink.xh,1);top,base=ink.band(c.cx)
    mask=component_mask(ink,c)
    h,w=mask.shape
    if not h or not w:return [0.]*78
    gy=np.minimum(np.arange(h)*8//h,7);gx=np.minimum(np.arange(w)*8//w,7)
    grid=np.zeros((8,8));cnt=np.zeros((8,8))
    np.add.at(grid,(gy[:,None],gx[None,:]),mask)
    np.add.at(cnt,(gy[:,None],gx[None,:]),1)
    ys,xs=np.nonzero(mask)
    stroke=2*ndi.distance_transform_edt(mask).max()/xh
    f=[c.h/xh,c.w/xh,(top-c.y0)/xh,(c.y1-base)/xh,c.w/max(c.h,1),
       mask.mean(),stroke,float(mask[:max(1,h//3)].mean()),float(mask[-max(1,h//3):].mean()),
       float(mask[:, :max(1,w//3)].mean()),float(mask[:,-max(1,w//3):].mean()),
       float(xs.std()/max(w,1)) if len(xs) else 0,float(ys.std()/max(h,1)) if len(ys) else 0,
       float(ndi.label(~np.pad(mask,1))[1]-1)]
    return f+(grid/np.maximum(cnt,1)).ravel().tolist()

MODEL_PATH=Path(__file__).resolve().parents[2]/"docs/records/labelfix/case_model_S5.json"

def configure_model(path):
    global MODEL_PATH
    MODEL_PATH=Path(path)
    model.cache_clear()

@lru_cache(maxsize=1)
def model():
    from .markshape import load_model
    p=MODEL_PATH
    return load_model(p) if p.exists() else None

def classify(ink,c,recogniser_base=None):
    m=model();f=features(ink,c)
    if m is None:
        raise FileNotFoundError('required case_model_S5.json is missing; case inference is unqualified')
    pixel,_,probs=m.predict(f);p=probs.get('capital',0.)
    raw_pixel=pixel
    frozen=getattr(ink,'frozen_case',{}).get(c.index,{})
    if frozen.get('bbox')!=[c.x0,c.y0,c.x1,c.y1]:frozen={}
    # The S5 classifier was fitted in the original glyph-band coordinates.
    # Keep that pixel view alongside the corrected font view; neither uses a
    # recogniser label. A normalization repair must not discard its cap vote.
    frozen_cap=frozen.get('raw_pixel_class')=='capital'
    if frozen_cap:
        pixel='capital';p=max(p,frozen['capital_probability'])
    # An attached mark on a narrow lowercase stem can look like a capital to
    # the fixed S5 model. It cannot supply a capital's full upper body width.
    top,baseline=ink.band(c.cx)
    cut=max(c.y0,min(c.y1,int(np.floor(top))))
    mask=component_mask(ink,c)
    upper_mask=mask[:max(0,cut-c.y0)]
    upper_width=int(np.count_nonzero(upper_mask.any(axis=0))) if upper_mask.size else 0
    lower_width=int(np.count_nonzero(mask[max(0,cut-c.y0):].any(axis=0))) if mask.size else 0
    geometry_cap=(1.25<=c.h/max(ink.xh,1)<=1.9 and abs(c.y1-baseline)<=.18*ink.xh
                  and c.w>=.5*ink.xh and upper_width>=.6*max(lower_width,1))
    if geometry_cap and p>=.4:
        pixel='capital'
    elif pixel=='capital' and not frozen_cap and c.w<.85*ink.xh and upper_width<.6*max(lower_width,1):
        pixel=max((k for k in probs if k!='capital'),key=lambda k:probs[k],default='lowercase_body')
    upper=bool(recogniser_base and recogniser_base.isupper())
    # Recognition is bounded by pixel height. Narrow lowercase mark bearers
    # are ambiguous with serif capitals plus joined accents: retain their
    # lowercase search, and expose the conflicting pixel-only decision.
    cap=(pixel=='capital' and (p>=.75 or geometry_cap)) or (upper and (p>=.25 or c.h>=.9*ink.xh and abs(f[3])<=.35))
    if recogniser_base and recogniser_base in 'αεηιουωρ' and c.w<.85*ink.xh:
        cap=False
    cls='capital' if cap else max((k for k in probs if k!='capital'),key=lambda k:probs[k],default='lowercase_body')
    return dict(case_source="case_model_S5",case_class=cls,pixel_class=pixel,raw_pixel_class=raw_pixel,
                frozen_pixel_class=frozen.get('raw_pixel_class',raw_pixel),geometry_capital=geometry_cap,capital_probability=round(p,5),
                recogniser_upper=upper if recogniser_base else None,
                case_disagreement=(pixel=='capital')!=upper if recogniser_base else None,
                all_caps=False)

def estimate_font(ink):
    """Pixel-only lowercase body fit, robust to capitals, ascenders and accents.

    Refit both boundaries: reusing a descender-biased baseline while changing
    only height slices *inside* a body. No CTC case or text is used by this fit.
    """
    if getattr(ink,'font_fit',None) is not None:return
    raw={c.index:classify(ink,c) for c in ink.components if c.role in ('letter','large')}
    ink.frozen_case={c.index:dict(raw[c.index],bbox=[c.x0,c.y0,c.x1,c.y1]) for c in ink.components if c.index in raw}
    bodies=[c for c in ink.components if raw.get(c.index,{}).get('raw_pixel_class')=='lowercase_body'
            and .65*ink.xh<=c.h<=1.15*ink.xh and .35*ink.xh<=c.w<=1.4*ink.xh]
    ink.font_width=float(np.median([c.w for c in bodies])) if bodies else .85*ink.xh
    if len(bodies)<4:
        ink.font_fit=dict(source='frozen_line_fallback',n=len(bodies),xh=ink.xh)
        return
    xs=np.array([c.cx for c in bodies]);ys=np.array([c.y1 for c in bodies],float)
    keep=np.ones(len(xs),bool)
    for _ in range(3):
        fit=np.polyfit(xs[keep],ys[keep],1) if np.ptp(xs[keep]) else np.array([0.,np.median(ys[keep])])
        residual=ys-np.polyval(fit,xs)
        med=np.median(residual[keep]);mad=np.median(abs(residual[keep]-med))
        new=abs(residual-med)<=max(2.,3*mad)
        if new.sum()<4:break
        keep=new
    height=float(np.median([c.h for c,k in zip(bodies,keep) if k]))
    ink.bottom=np.polyval(fit,np.arange(ink.width))
    ink.xh=height;ink.top=ink.bottom-height
    ink.font_fit=dict(source='pixel_lowercase_bodies',n=int(keep.sum()),xh=height,baseline_fit=fit.tolist())


def prepare(ink,slots):
    """Classify components/regions and assign the line font or a capital-run height."""
    estimate_font(ink)
    bases={i:s['base'] for s in slots if not s.get('fused') for i in s.get('component_ids',[])}
    owned={i for s in slots for i in s.get('component_ids',[])}
    ink.case_info={c.index:classify(ink,c,bases.get(c.index)) for c in ink.components if c.role in ('letter','large') or c.index in owned}
    ink.word_bands={}
    bodies=[c for c in ink.components if ink.case_info.get(c.index,{}).get('case_class')=='lowercase_body'
            and .65*ink.xh<=c.h<=1.15*ink.xh and abs(c.y1-ink.band(c.cx)[1])<=.2*ink.xh]
    for word in sorted({s.get('word_index',-1) for s in slots}):
        ss=[s for s in slots if s.get('word_index',-1)==word and s.get('component') is not None]
        ids={i for s in ss for i in s['component_ids']}
        cs=[c for c in ink.components if c.index in ids]
        if not cs:continue
        caps=[c for c in cs if ink.case_info[c.index]['case_class']=='capital']
        allcaps=len(cs)>=2 and len(caps)/len(cs)>=.8
        if allcaps:
            height=float(np.median([c.h for c in caps]));source='capital_run'
            for c in cs:ink.case_info[c.index]['all_caps']=True
        else:
            local=[c.h for c in bodies if c.index in ids]
            # S5's word-height substitution moved otherwise valid mark zones.
            # Keep the robust line font, even when local bodies are available.
            height=ink.xh
            source='word_lowercase_bodies' if len(local)>=2 else ink.font_fit['source']
        for c in cs:ink.word_bands[c.index]=dict(xh=height,source=source,old_xh=ink.xh)
    for s in slots:
        if s.get('component') is not None:
            c=s['component']
            info=classify(ink,c,s['base']) if s.get('fused') or s.get('split_union') or c.index not in ink.case_info else ink.case_info[c.index]
            s.update(info);s['height_band']=ink.word_bands.get(c.index,{})
