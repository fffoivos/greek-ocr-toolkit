"""Pixel writing direction, independent of layout and of horizontal line fitting.

Angles are observed CLOCKWISE quarter turns. Unknown is a real result, not 0.
Confidence values are evidence margins, not calibrated probabilities. Distances
are expressed in component heights or image fractions. No PDF text is read.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from typing import Protocol, Sequence

import cv2
import numpy as np
from PIL import Image, ImageOps
from scipy.spatial import cKDTree

__all__ = ['Orientation', 'QuarterTurn', 'measure_orientation', 'recognizer_polarity',
           'discover_directions', 'canonical_word_crop']


class _Recognizer(Protocol):
    def recognize(self, strips: list[np.ndarray]) -> list[tuple[str, float]]: ...


@dataclass
class QuarterTurn:
    """Exact boundary-coordinate transform from a source crop to upright pixels."""
    width: float
    height: float
    orientation_cw: int = 0
    offset: tuple[float, float] = (0., 0.)

    def __post_init__(self):
        if self.orientation_cw not in (0, 90, 180, 270):
            raise ValueError('orientation must be a clockwise quarter turn')
        if not np.isfinite([self.width, self.height, *self.offset]).all() or min(self.width, self.height) <= 0:
            raise ValueError('frame dimensions must be finite and positive')

    @property
    def matrix(self):
        """Source/page to normalized crop, homogeneous TOPLEFT coordinates."""
        w, h = self.width, self.height
        m = {0: [[1,0,0],[0,1,0],[0,0,1]],
             90: [[0,1,0],[-1,0,w],[0,0,1]],
             180: [[-1,0,w],[0,-1,h],[0,0,1]],
             270: [[0,-1,h],[1,0,0],[0,0,1]]}[self.orientation_cw]
        return np.asarray(m, float) @ np.array([[1,0,-self.offset[0]],[0,1,-self.offset[1]],[0,0,1]])

    @property
    def size(self):
        return (self.height, self.width) if self.orientation_cw % 180 else (self.width, self.height)

    def points(self, points: Sequence[Sequence[float]] | np.ndarray, *, inverse: bool = False) -> np.ndarray:
        """Map N corners or guide samples; never reduce an oriented quad to AABB."""
        a = np.asarray(points, float).reshape(-1, 2)
        m = np.linalg.inv(self.matrix) if inverse else self.matrix
        return (np.c_[a, np.ones(len(a))] @ m.T)[:, :2]

    def image(self, image: Image.Image) -> Image.Image:
        """Normalize pixels with exact transposition (no quarter-turn resampling)."""
        return image.rotate(self.orientation_cw, expand=True)

    def rectangle(self, box: Sequence[float], *, inverse: bool = True) -> np.ndarray:
        """Ordered BL, BR, TR, TL corners, mapped from an upright text box."""
        l, t, r, b = box
        return self.points([(l,b),(r,b),(r,t),(l,t)], inverse=inverse)


@dataclass
class Orientation:
    """Axis, polarity, residual skew and their independent evidence."""
    axis: str = 'unknown'
    orientation_cw: int | None = None
    axis_confidence: float = 0.
    polarity_confidence: float = 0.
    residual_skew_cw: float | None = None
    alternatives: list[int] = field(default_factory=lambda: [0,90,180,270])
    evidence: dict = field(default_factory=dict)

    def to_record(self) -> dict:
        """JSON-ready record; None serializes as explicit unknown (null)."""
        return asdict(self)


def _pixels(image, limit=1800):
    im = image.convert('L').copy()
    im.thumbnail((limit, limit))  # computation budget, not a geometric threshold
    g = np.asarray(im)
    # Estimate scale before adaptive thresholding, invariant to quarter turns.
    _, rough = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    _, _, s, _ = cv2.connectedComponentsWithStats(rough, 8)
    s = s[1:]
    dims = np.max(s[:,2:4],axis=1)
    good = s[(s[:,4] > .000001*g.size) & (dims < .25*max(g.shape)) &
             (np.min(s[:,2:4],axis=1) > .15*np.maximum(1,dims))]
    if len(good):
        order = np.argsort(np.max(good[:,2:4],axis=1))
        # Dust can outnumber letters by orders of magnitude. Weight by ink
        # support, with square root limiting influence from touching glyphs.
        weights = np.sqrt(good[order,4]); cumulative = np.cumsum(weights)
        xh = float(np.max(good[order[np.searchsorted(cumulative,cumulative[-1]/2)],2:4]))
    else:
        xh = min(g.shape)/20
    xh = max(1., xh)
    window = max(3, round(3*xh)) | 1
    m = cv2.adaptiveThreshold(g,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,window,18)
    k = max(1, round(max(8*xh, .09*min(g.shape))))
    rules = (cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((1,k),np.uint8)) |
             cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((k,1),np.uint8)))
    return im, m & ~rules, rules, xh


def _components(mask):
    _, labels, stats, centres = cv2.connectedComponentsWithStats(mask, 8)
    s, c = stats[1:], centres[1:]
    # Relative to the image diagonal, then re-estimate the typical body size.
    span = max(mask.shape)
    good = (s[:,4] >= .000002*mask.size) & (np.min(s[:,2:4],axis=1) >= .0008*span)
    good &= np.max(s[:,2:4],axis=1) < .085*span
    s, c = s[good], c[good]
    ch = float(np.median(np.max(s[:,2:4],axis=1))) if len(s) else 1.
    body = (np.max(s[:,2:4],axis=1) > .65*ch) & (np.max(s[:,2:4],axis=1) < 2*ch) & (s[:,4] > .15*ch*ch)
    return s, c, ch, body


def _votes(pts, ch):
    votes = np.zeros((len(pts),2)); slopes = [[], []]
    if len(pts) < 3:
        return votes, slopes
    _, js = cKDTree(pts).query(pts,k=min(12,len(pts)))
    for i, ids in enumerate(js):
        dd = pts[np.atleast_1d(ids)]-pts[i]
        dx, dy = abs(dd[:,0]), abs(dd[:,1])
        for axis, (along, across) in enumerate(((dx,dy),(dy,dx))):
            candidates = np.flatnonzero((across < .35*ch) & (along > .4*ch) & (along < 5*ch))
            if len(candidates):
                k = candidates[np.argmin(along[candidates])]
                votes[i,axis] = ch/along[k]
                slopes[axis].append(float(dd[k,1-axis]/dd[k,axis]))
    return votes, slopes


def _polarity(mask, axis):
    aligned = np.rot90(mask, axis//90)
    _, _, stats, centres = cv2.connectedComponentsWithStats(aligned, 8)
    s, c = stats[1:], centres[1:]
    valid = (s[:,4] > .000001*aligned.size) & (s[:,2] < .1*aligned.shape[1]) & (s[:,3] < .15*aligned.shape[0])
    s, c = s[valid], c[valid]
    if len(s) < 3:
        return dict(score=0., bodies=0, marks=0)
    h = float(np.median(s[:,3])); body = (s[:,3] > .65*h) & (s[:,3] < 2*h) & (s[:,2] < 2.5*h) & (s[:,4] > .12*h*h)
    bs, bc = s[body], c[body]
    small = (s[:,3] < .55*h) & (s[:,4] < .30*h*h)
    up = down = 0; differences = []
    if len(bs):
        tree = cKDTree(bc)
        for q, ct in zip(s[small], c[small]):
            _, ids = tree.query(ct, k=min(4,len(bs))); signs = []
            for j in np.atleast_1d(ids):
                b = bs[j]
                if b[0]-.2*h <= ct[0] <= b[0]+b[2]+.2*h:
                    for gap, sign in ((b[1]-(q[1]+q[3]),1),(q[1]-(b[1]+b[3]),-1)):
                        if -.1*h <= gap <= .7*h:
                            signs.append((abs(gap),sign))
            if signs:
                sign = min(signs)[1]; up += sign == 1; down += sign == -1
        _, ids = tree.query(bc,k=min(8,len(bc)))
        for i, js in enumerate(ids):
            near = [j for j in np.atleast_1d(js) if abs(bc[j,1]-bc[i,1]) < .45*h and abs(bc[j,0]-bc[i,0]) < 8*h]
            if len(near) >= 3:
                tops, bots = bs[near,1], bs[near,1]+bs[near,3]
                differences.append((np.median(abs(tops-np.median(tops)))-np.median(abs(bots-np.median(bots))))/h)
    alignment = float(np.mean(differences)) if differences else 0.
    return dict(score=(up-down)/max(1,up+down)+2*alignment, bodies=len(bs), marks=up+down,
                accent_above=up, accent_below=down, alignment=alignment)


def _osd(image):
    executable = shutil.which('tesseract')
    if not executable:
        return dict(available=False)
    with tempfile.TemporaryDirectory(prefix='greekocr-orientation-') as tmp:
        im = image.copy(); im.thumbnail((2000,2000)); path = os.path.join(tmp,'input.png')
        im.save(path,dpi=(300,300))
        try:
            r = subprocess.run([executable,path,'stdout','-l','osd','--psm','0'],capture_output=True,text=True,
                               timeout=20,env={**os.environ,'OMP_THREAD_LIMIT':'1'})
        except subprocess.TimeoutExpired:
            return dict(available=True,reason='timeout')
    angle = re.search(r'Orientation in degrees: (\d+)',r.stdout)
    conf = re.search(r'Orientation confidence: ([\d.]+)',r.stdout)
    return dict(available=True,angle=int(angle[1]) if angle else None,
                confidence=float(conf[1]) if conf else 0.,returncode=r.returncode)


def measure_orientation(image: Image.Image, *, use_osd: bool = False, unit: str = 'block') -> Orientation:
    """Measure a region; short words require recognizer evidence for polarity."""
    _, mask, _, _ = _pixels(image)
    s, c, h, body = _components(mask)
    pts = c[body]; votes, slopes = _votes(pts,h)
    totals = votes.sum(axis=0)
    f = mask.astype(float)/255
    concentrations = [float(np.var(f.mean(a))/(np.mean(f)**2+1e-9)) for a in (1,0)]
    axis = int(np.argmax(totals if len(pts) >= 12 else concentrations))
    margin = float(abs(totals[0]-totals[1])/max(float(totals.max()),1e-9))
    if len(pts) < 12:
        margin = float(abs(concentrations[0]-concentrations[1])/max(*concentrations,1e-9))
    result = Orientation(axis='horizontal' if axis == 0 else 'vertical',axis_confidence=margin,
                         alternatives=[axis*90,axis*90+180])
    result.evidence = dict(component_votes=totals.tolist(),body_count=len(pts),xheight=h*image.width/mask.shape[1],
                           projection_concentration=concentrations,source='component-neighbours')
    if unit in ('word','line') and mask.any():
        # A short chain's overall ink extent is stronger than a few accidental
        # mark-to-stem neighbours. This is used only for an already isolated word.
        tight = canonical_word_crop(image)
        ratio = max(tight.size)/max(1,min(tight.size))
        if ratio >= 1.5:
            axis = int(tight.height > tight.width)
            result.axis = 'horizontal' if axis == 0 else 'vertical'
            result.axis_confidence = 1-1/ratio
            result.alternatives = [axis*90,axis*90+180]
            result.evidence['axis_source'] = 'isolated-ink-chain-extent'
            margin = result.axis_confidence
    corroborated = int(np.argmax(concentrations)) == axis and len(pts) >= 12
    if not mask.any() or (margin < .08 and not corroborated):
        result.axis = 'unknown'; result.alternatives = [0,90,180,270]
        return result
    if slopes[axis]:
        skew = math.degrees(math.atan(float(np.median(slopes[axis]))))
        result.residual_skew_cw = skew if axis == 0 else -skew
    polarity = _polarity(mask, axis*90)
    result.evidence['asymmetry'] = polarity
    prior = (axis*90 + (180 if polarity['score'] < 0 else 0)) % 360
    # Many letters and detached marks are required. A single accent is not a vote.
    strong = polarity['bodies'] >= 24 and polarity['marks'] >= 5 and abs(polarity['score']) >= .35
    if strong and unit != 'word':
        result.orientation_cw = prior
        result.polarity_confidence = min(1., abs(polarity['score']))
        result.evidence['polarity_source'] = 'block-asymmetry'
    if use_osd and len(pts) >= 24:
        osd = _osd(image); result.evidence['osd'] = osd
        candidate = osd.get('angle')
        if candidate in result.alternatives and osd.get('confidence',0) >= 6:
            if strong and prior != candidate:
                result.orientation_cw = None; result.polarity_confidence = 0.
                result.evidence['polarity_source'] = 'conflicting-block-evidence'
            else:
                result.orientation_cw = candidate
                result.polarity_confidence = min(1., osd['confidence']/20)
                result.evidence['polarity_source'] = 'osd-block'
        elif candidate is not None and (candidate not in result.alternatives or (strong and candidate != prior)):
            result.orientation_cw = None; result.polarity_confidence = 0.
            result.evidence['polarity_source'] = 'weak-or-conflicting-osd'
    return result


def canonical_word_crop(image: Image.Image) -> Image.Image:
    """Remove arbitrary margins, keep all significant ink, add 0.1 body heights.

    Applied identically to standalone words, pasted ROIs and production crops.
    Contrast is normalized from measured paper and ink; padding is white.
    """
    im = image.convert('L'); g = np.asarray(im)
    # Remove a uniform light external canvas BEFORE estimating the scan's paper
    # and ink. Otherwise Otsu can classify an entire grey-paper paste as ink.
    span = float(g.max())-float(g.min())
    yy,xx = np.nonzero(g < float(g.max())-.05*span)
    if len(xx):
        im = im.crop((int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1))
        g = np.asarray(im)
    _, mask = cv2.threshold(g,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    _, labels, s, _ = cv2.connectedComponentsWithStats(mask,8)
    if len(s) <= 1:
        return im
    q = s[1:]; area = q[:,4]
    keep = np.flatnonzero(area >= max(1.,.006*float(area.max())))+1
    ys, xs = np.nonzero(np.isin(labels,keep))
    if not len(xs):
        return im
    x0,y0,x1,y1 = int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1
    h = float(np.median(np.max(q[keep-1,2:4],axis=1)))
    paper = float(np.percentile(g,90))
    dark = float(np.percentile(g[mask > 0],10))
    normalized = np.clip((g.astype(float)-dark)/max(1.,paper-dark)*255,0,255).astype('uint8')
    pad = max(1,round(.1*h))  # recognizer's documented training ink-height policy
    return ImageOps.expand(Image.fromarray(normalized).crop((x0,y0,x1,y1)),border=pad,fill=255)


def _recognition_strip(crop):
    """The same tensor contract for isolated marks, digits and ordinary words."""
    from greekocr.deploy.docling_plugin.recognizer.strips import extract_strip
    if crop.height < 4:
        crop = crop.resize((max(1,round(crop.width*4/crop.height)),4),Image.Resampling.LANCZOS)
    g = np.asarray(crop,dtype=np.float32)/255
    minimum = math.ceil(g.shape[0]/6)
    if g.shape[1] < minimum:
        pad = minimum-g.shape[1]
        g = np.pad(g,((0,0),(pad//2,pad-pad//2)),constant_values=1.)
    return extract_strip(g,(0,0,g.shape[1],g.shape[0]))


def recognizer_polarity(image: Image.Image, orientation: Orientation, recognizer: _Recognizer, *, margin: float = .12) -> Orientation:
    """Compare axis-consistent readings with our recognizer; retain both on doubt."""
    from greekocr.deploy.docling_plugin.recognizer.strips import extract_strip
    from dataclasses import replace
    out = replace(orientation,evidence=dict(orientation.evidence))
    if out.axis == 'unknown':
        return out
    angles = [0,180] if out.axis == 'horizontal' else [90,270]
    strips = []
    for angle in angles:
        crop = canonical_word_crop(image.rotate(angle,expand=True))
        strip = _recognition_strip(crop)
        if strip is None:
            out.evidence['polarity_source'] = 'invalid-recognition-crop'
            return out
        strips.append(strip)
    predictions = recognizer.recognize(strips)
    if len(predictions) != 2:
        raise ValueError('polarity recognizer must return two readings')
    scores = []; readings = []
    for angle,(text,confidence) in zip(angles,predictions):
        letters = [c for c in unicodedata.normalize('NFC',text) if c.isalpha()]
        greek = sum('GREEK' in unicodedata.name(c,'') for c in letters)
        # Ignore CTC blank confidence: only a meaningful Greek reading can win.
        meaningful = greek >= 3 and greek/max(1,len(letters)) >= .7 and len(set(letters)) >= 2
        score = float(confidence)*greek if meaningful else 0.
        scores.append(score); readings.append(dict(orientation_cw=angle,text=text,recognition_confidence=float(confidence),score=score))
    best = int(np.argmax(scores)); gap = (scores[best]-scores[1-best])/max(scores[best],1e-9)
    out.evidence.update(readings=readings,crop_policy='contrast+ink-envelope+0.1-body-height',polarity_source='recognizer-two-hypotheses')
    out.polarity_confidence = gap
    # More hallucinated letters cannot defeat a clearer shorter reading.
    conf_gap = readings[best]['recognition_confidence']-readings[1-best]['recognition_confidence']
    out.orientation_cw = angles[best] if scores[best] > 0 and gap >= margin and conf_gap >= .03 else None
    out.evidence['recognition_confidence_gap'] = conf_gap
    return out


def discover_directions(image: Image.Image) -> list[dict]:
    """Propose local chains in BOTH axes before fitting any horizontal lines.

    Components vote independently; only mutually consistent neighbours join.
    A rule between component centres blocks a join. The returned regions are
    proposals, with evidence, not certified word truth.
    """
    small, mask, rules, _ = _pixels(image,2000)
    stats, centres, ch, body = _components(mask)
    stats, centres = stats[body], centres[body]
    votes, _ = _votes(centres,ch)
    if len(centres) < 3:
        return []
    assignment = np.argmax(votes,axis=1)
    strength = np.max(votes,axis=1)/np.maximum(.01,np.min(votes,axis=1))
    parent = list(range(len(centres)))
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i,j in sorted(cKDTree(centres).query_pairs(3*ch)):
        axis = assignment[i]
        if axis != assignment[j] or min(strength[i],strength[j]) < 1.4:
            continue
        delta = abs(centres[i]-centres[j])
        if delta[1-axis] > .65*ch or delta[axis] > 3*ch:
            continue
        points = np.rint(np.linspace(centres[i],centres[j],max(2,round(delta.max())))).astype(int)
        if rules[points[:,1],points[:,0]].any():
            continue
        parent[root(j)] = root(i)
    groups = {}
    for i in range(len(centres)):
        groups.setdefault(root(i),[]).append(i)
    out = []; sx, sy = image.width/small.width, image.height/small.height
    for members in groups.values():
        if len(members) < 3:
            continue
        q = stats[members]; axis = int(assignment[members[0]])
        lo = q[:,:2].min(0); hi = (q[:,:2]+q[:,2:4]).max(0)
        if hi[axis]-lo[axis] < 2*(hi[1-axis]-lo[1-axis]):
            continue
        # Include detached accents at a scale-relative margin.
        lo = np.maximum(0,lo-.35*ch); hi = np.minimum([small.width,small.height],hi+.35*ch)
        box = [float(lo[0]*sx),float(lo[1]*sy),float(hi[0]*sx),float(hi[1]*sy)]
        out.append(dict(box=box,axis='horizontal' if axis==0 else 'vertical',components=len(members),
                        axis_confidence=float(np.median(1-1/strength[members])),xheight=ch*(sx+sy)/2))
    return sorted(out,key=lambda q:(q['box'][1],q['box'][0],q['axis']))
