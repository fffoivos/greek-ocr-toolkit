"""Pixel evidence for structure stops, independent of frozen line geometry.

The dimensionless rules are specified in PAGE_LINES_Q1B_BOUNDARIES.md before
the development-page audit. Detector masks are proposals, never evidence.
"""
from __future__ import annotations

from copy import deepcopy

import numpy as np
from scipy import ndimage as ndi

from .components import binarise, to_gray
from .pixel_segments import _runs


def _at(boundary, ys):
    return np.interp(ys, *np.asarray(boundary['path']).T[::-1])


class BoundaryEvidence:
    """One original-image mask and line-local spacing measurements per page."""

    def __init__(self, page, lines):
        gray = to_gray(page)
        self.gray = np.rint(gray).astype(np.uint8)
        self.ink = binarise(gray, window=max(15, round(.04 * min(gray.shape))) | 1)
        self.lines = lines
        self.profiles = {}
        self.validated_rules = []
        self.xheight = float(np.median([l['xheight'] for l in lines
            if l.get('discounted') is None])) if any(
                l.get('discounted') is None for l in lines) else min(gray.shape) / 100

    def band(self, line, *, body=False):
        """Original ink at pixel centres inside this record's own curved band."""
        h, w = self.ink.shape
        a, b = max(0, line['x0']), min(w, line['x1'])
        sl = slice(a-line['x0'], b-line['x0'])
        xh = line['xheight']
        top = np.asarray(line['meanline'] if body else line['top'])[sl]
        bottom = np.asarray(line['baseline'] if body else line['bottom'])[sl]
        if body:
            top, bottom = top-.2*xh, bottom+.2*xh
        t, bot = max(0, int(np.floor(top.min()))), min(h, int(np.ceil(bottom.max()))+1)
        ys = np.arange(t, bot)[:, None]
        mask = self.ink[t:bot, a:b] & (ys >= top) & (ys < bottom)
        return a, t, mask

    def profile(self, i):
        if i not in self.profiles:
            line = self.lines[i]
            a, _, band = self.band(line, body=True)
            occupied = band.sum(axis=0) >= max(1, .1*line['xheight'])
            runs = [(a+s, a+e) for s, e in _runs(occupied)]
            gaps = [(left[1], right[0]) for left, right in zip(runs, runs[1:])]
            self.profiles[i] = (runs, gaps)
        return self.profiles[i]

    def gutter(self, boundary):
        top, bottom = boundary['path'][0][1], boundary['path'][-1][1]
        sides = [[], []]
        participants = []
        gaps = [[], []]
        rows = []
        for i, line in enumerate(self.lines):
            if line.get('discounted') is not None:
                continue
            y = float(np.median(line['baseline']))
            if not top <= y < bottom:
                continue
            centre, xh = float(_at(boundary, y)), line['xheight']
            if line['x1'] < centre-12*xh or line['x0'] > centre+12*xh:
                continue
            runs, spaces = self.profile(i)
            if not runs:
                continue
            participants.append(dict(line_index=i, xheight=xh))
            support = []
            for side in (0, 1):
                own = [(a,b) for a,b in runs if
                       (b <= centre and b >= centre-12*xh if side == 0 else
                        a >= centre and a <= centre+12*xh)]
                wide = bool(own and own[-1][1]-own[0][0] >= 3*xh)
                support.append(wide)
                if wide:
                    sides[side].append((y, xh, i))
                # Candidate gap never contributes to ordinary spacing.
                gaps[side].extend((b-a)/xh for a,b in spaces if
                    (b < centre and b >= centre-12*xh if side == 0 else
                     a > centre and a <= centre+12*xh))
            rows.append((y, xh, support, runs))
        # Delivered table fragments can end at a word gap. Include facing
        # fragments on the same baseline when measuring ordinary spacing;
        # otherwise splitting would erase word spaces from the distribution.
        interpiece_samples = [0,0]
        for y,xh,_,runs in rows:
            facing = [(other_runs[0][0]-runs[-1][1],other_xh)
                      for other_y,other_xh,_,other_runs in rows
                      if abs(other_y-y)<=.6*min(xh,other_xh) and other_runs[0][0]>runs[-1][1]]
            if not facing:
                continue
            gap,peer_xh = min(facing)
            a,b = runs[-1][1],runs[-1][1]+gap
            centre = float(_at(boundary,y))
            side = 0 if b<centre else 1 if a>centre else None
            if side is not None:
                gaps[side].append(gap/max(xh,peer_xh))
                interpiece_samples[side] += 1
        max_xh = max((p['xheight'] for p in participants), default=self.xheight)
        width = float(boundary.get('width', 0))
        spacing = []
        for values in gaps:
            q = np.percentile(values, [25, 50, 75, 90]) if values else [None]*4
            spacing.append(dict(samples=len(values), letter_q25_xh=q[0], median_xh=q[1],
                                word_q75_xh=q[2], q90_xh=q[3]))
        # Merge observations of one printed baseline, not table pieces.
        grouped = []
        for y, xh, support, runs in sorted(rows):
            if not grouped or y-grouped[-1][0] > .6*min(xh, grouped[-1][1]):
                grouped.append([y, xh, support.copy()])
            else:
                grouped[-1][2] = [a or b for a,b in zip(grouped[-1][2], support)]
        counts = [sum(row[2][s] for row in grouped) for s in (0,1)]
        # Adjacent columns need not share a baseline phase. Measure leading
        # independently on each side before comparing their occupied spans.
        pitches = []
        side_baselines = []
        for side in (0,1):
            values = [row[0] for row in grouped if row[2][side]]
            side_baselines.append(values)
            if len(values)>1:
                pitches.append(float(np.median(np.diff(values))))
        reach = .5*min(pitches) if pitches else max_xh
        both = sum(all(any(abs(row[0]-y)<=reach for y in values)
                       for values in side_baselines) for row in grouped)
        spans = [max((r[0] for r in side), default=0)-min((r[0] for r in side), default=0)
                 for side in sides]
        shared_span = (min(max((r[0] for r in side), default=0) for side in sides) -
                       max(min((r[0] for r in side), default=0) for side in sides))
        # A size-specific test uses that size's measured spacing. The largest
        # participating size also imposes the absolute x-height floor.
        required = float(max([1.5*max_xh] + [1.5*s['q90_xh']*max_xh for s in spacing if s['samples']]))
        # Check the proposed whitespace against original letter-band ink.
        # The detector's rectangle alone cannot prove a white gap. For columns
        # with staggered baselines, use the nearest rows within half a leading.
        observed_gaps = []
        for y,_,support in grouped:
            centre = float(_at(boundary,y))
            local_runs = [run for ry,_,_,runs in rows if abs(ry-y)<=reach for run in runs]
            left = [b for a,b in local_runs if b<=centre]
            right = [a for a,b in local_runs if a>=centre]
            spans_centre = any(a<centre<b for a,b in local_runs)
            observed_gaps.append(0. if spans_centre or not left or not right else min(right)-max(left))
        white_rows = sum(width >= required for width in observed_gaps)
        checks = dict(spacing_observed=all(s['samples'] >= 3 for s in spacing),
            wide_at_local_scale=width >= required,
            separate_blocks=min(counts) >= 3,
            persistent=shared_span >= 6*max_xh,
            bilateral_support=both/max(1,len(grouped)) >= .6,
            original_whitespace=white_rows/max(1,len(grouped)) >= .6)
        checks = {key:bool(value) for key,value in checks.items()}
        return dict(method='line-local-spacing-v1', accepted=all(checks.values()), checks=checks,
            width_px=width, local_xheight_max_px=max_xh, width_xh=width/max_xh,
            required_width_px=required, spacing_sides=spacing, side_row_counts=counts,
            side_span_xh=[s/max_xh for s in spans], shared_span_xh=shared_span/max_xh,
            occupied_rows=len(grouped), bilateral_rows=both, participants=participants,
            observed_gap_widths_px=observed_gaps, white_rows=white_rows,
            baseline_matching_reach_px=reach, interpiece_spacing_samples=interpiece_samples)

    def rule(self, boundary):
        h, w = self.ink.shape
        top, bottom = boundary['path'][0][1], boundary['path'][-1][1]
        nearby = [l['xheight'] for l in self.lines if l.get('discounted') is None and
            max(l['baseline']) >= top and min(l['meanline']) <= bottom and
            l['x0'] <= _at(boundary, np.median(l['baseline']))+12*l['xheight'] and
            l['x1'] >= _at(boundary, np.median(l['baseline']))-12*l['xheight']]
        xh = float(np.median(nearby)) if nearby else self.xheight
        yy = np.arange(max(0, int(np.ceil(top))), min(h, int(np.floor(bottom))+1))
        xx = _at(boundary, yy)
        radius = max(1, int(np.ceil(.8*xh)))
        offsets = np.arange(-radius, radius+1)
        ix = np.rint(xx[:,None]+offsets).astype(int)
        sample = self.ink[yy[:,None], np.clip(ix,0,w-1)] & (ix>=0) & (ix<w)
        centres = np.full(len(yy), np.nan)
        thickness = np.full(len(yy), np.nan)
        for j, row in enumerate(sample):
            options = [(a,b) for a,b in _runs(row) if a>0 and b<len(row) and
                       abs((a+b-1)/2-radius) <= .3*xh and b-a <= .35*xh]
            if not options:
                continue
            a,b = min(options, key=lambda ab:abs((ab[0]+ab[1]-1)/2-radius))
            c = (a+b-1)/2
            flanks = np.rint([c-.5*xh,c+.5*xh]).astype(int)
            if np.any(flanks<0) or np.any(flanks>=len(row)) or row[flanks].any():
                continue
            centres[j] = xx[j]+c-radius
            thickness[j] = b-a
        valid = np.isfinite(centres)
        if valid.sum() >= 2:
            slope, intercept = np.polyfit(yy[valid], centres[valid], 1)
            residual = abs(centres-(slope*yy+intercept))
            valid &= residual <= .15*xh
        else:
            slope, intercept = 0., float(xx[0]) if len(xx) else 0.
            residual = np.full(len(yy), np.nan)
            valid[:] = False
        # Stroke continuity and stroke shape are different measurements.
        # At a table junction the rule is still ink even though its horizontal
        # run touches letters or a crossing rule. Fit/measure thickness only
        # on isolated rows, then test continuity on the fitted narrow path.
        raw = np.zeros(len(yy),bool)
        if valid.any():
            ink_radius = float(np.median(thickness[valid]))/2 + .05*xh
            for offset in np.arange(-int(np.ceil(ink_radius)),int(np.ceil(ink_radius))+1):
                at = np.rint(slope*yy+intercept+offset).astype(int)
                ok = (at>=0)&(at<w)
                raw[ok] |= self.ink[yy[ok],at[ok]]
        occupied = np.flatnonzero(raw)
        if len(occupied):
            lo, hi = occupied[0], occupied[-1]+1
        else:
            lo, hi = 0, 0
        support = raw[lo:hi]
        dashes = np.array([b-a for a,b in _runs(support)], dtype=float)
        breaks = np.array([b-a for a,b in _runs(~support)], dtype=float)
        fraction = float(support.mean()) if len(support) else 0.
        def cv(values):
            return float(values.std()/values.mean()) if len(values) else 0.
        thin_fraction = float(valid.sum()/max(1,raw.sum()))
        continuous = fraction >= .85
        dashed = bool(fraction >= .5 and len(dashes) >= 3 and dashes.min() >= xh and
                      len(breaks) and breaks.max() <= 2*xh and cv(dashes) <= .5 and cv(breaks) <= .5)
        checks = dict(long_enough=(hi-lo) >= 8*xh, sustained_straight_thin_ink=continuous or dashed,
                      isolated_thin_support=thin_fraction>=.5,
                      no_long_unprinted_gap=not len(breaks) or breaks.max()<=2*xh)
        checks = {key:bool(value) for key,value in checks.items()}
        evidence = dict(method='original-thin-stroke-v1', accepted=all(checks.values()), checks=checks,
            xheight_px=xh, support_fraction=fraction, supported_rows=int(valid.sum()),
            thin_support_fraction=thin_fraction, original_ink_rows=int(raw.sum()),
            sampled_rows=len(yy), extent_xh=(hi-lo)/xh,
            thickness_q90_xh=float(np.nanpercentile(thickness[valid],90)/xh) if valid.any() else None,
            residual_q90_xh=float(np.nanpercentile(residual[valid],90)/xh) if valid.any() else None,
            dash_lengths_xh=(dashes/xh).tolist(), gap_lengths_xh=(breaks/xh).tolist(),
            style='continuous' if continuous else 'dashed' if dashed else 'unsupported')
        if evidence['accepted']:
            new_top, new_bottom = int(yy[lo]), int(yy[hi-1])
            evidence['validated_path'] = [[float(slope*new_top+intercept),new_top],
                                          [float(slope*new_bottom+intercept),new_bottom]]
        return evidence

    def validate(self, boundaries):
        kept, rejected = [], []
        for candidate in boundaries:
            boundary = deepcopy(candidate)
            if boundary['kind'] == 'fold':
                evidence = dict(method='spread-fold', accepted=True, source=boundary.get('source'))
            elif boundary['kind'] == 'gutter':
                evidence = self.gutter(boundary)
            elif boundary['kind'] == 'rule':
                evidence = self.rule(boundary)
            else:
                raise ValueError(f"unsupported boundary kind: {boundary['kind']}")
            boundary['evidence'] = evidence
            if evidence['accepted']:
                if 'validated_path' in evidence:
                    boundary['proposal_path'] = boundary['path']
                    boundary['path'] = evidence['validated_path']
                kept.append(boundary)
            else:
                boundary['rejection_reasons'] = [k for k,v in evidence['checks'].items() if not v]
                rejected.append(boundary)
        self.validated_rules = [b for b in kept if b['kind']=='rule']
        return kept, rejected

    def crossing(self, line_index, boundary):
        """Text-band evidence, excluding the rule stroke and outer ribbon slack."""
        line = self.lines[line_index]
        a,t,mask = self.band(line, body=True)
        h,w = self.ink.shape
        xh = line['xheight']
        # Context outside the body band distinguishes a tall rule remnant
        # from a glyph cropped to one x-height. Strip verified neighbouring
        # rules too: a double border's second stroke is not the piece's text.
        ca,cb = max(0,a-int(xh)),min(w,a+mask.shape[1]+int(xh))
        ct,cbot = max(0,t-int(2*xh)),min(h,t+mask.shape[0]+int(2*xh))
        context = self.ink[ct:cbot,ca:cb].copy()
        # Identify long original strokes before carving fitted rule paths.
        # Carving can otherwise turn the edge of a slanted/heavy rule into
        # several short fragments that look like separate letter components.
        original_labels,_ = ndi.label(context,structure=np.ones((3,3)))
        original_sizes = np.bincount(original_labels.ravel())
        rejected_components = []
        remove = np.zeros(len(original_sizes),bool)
        for k,sl in enumerate(ndi.find_objects(original_labels),1):
            if sl is None:
                continue
            ys,xs = sl
            hh,ww = ys.stop-ys.start,xs.stop-xs.start
            if (hh>=3*xh and hh>=8*ww) or (ww>=3*xh and ww>=8*hh):
                remove[k] = True
                rejected_components.append(dict(box=[ca+xs.start,ct+ys.start,ca+xs.stop,ct+ys.stop],
                    area=int(original_sizes[k]),reason='original elongated rule component'))
        context &= ~remove[original_labels]
        cy,cx = np.arange(ct,cbot)[:,None],np.arange(ca,cb)[None,:]
        for rule in self.validated_rules:
            rt,rb = rule['path'][0][1],rule['path'][-1][1]
            if rb<ct or rt>=cbot:
                continue
            e = rule['evidence']
            radius = .5*e['thickness_q90_xh']*e['xheight_px']+.05*xh
            context &= ~((cy>=rt)&(cy<=rb)&(abs(cx-_at(rule,cy))<=radius))
        labels,n = ndi.label(context,structure=np.ones((3,3)))
        sizes = np.bincount(labels.ravel(),minlength=n+1)
        keep = sizes >= .04*xh*xh
        keep[0] = False
        for k,sl in enumerate(ndi.find_objects(labels),1):
            if sl is None:
                continue
            ys,xs = sl
            hh,ww = ys.stop-ys.start,xs.stop-xs.start
            rule_remnant = (hh>=3*xh and ww<=.5*xh) or (ww>=3*xh and hh<=.25*xh)
            outside_text_scale = hh>3.5*xh or ww>12*xh
            if rule_remnant or outside_text_scale:
                keep[k] = False
                rejected_components.append(dict(box=[ca+xs.start,ct+ys.start,ca+xs.stop,ct+ys.stop],
                    area=int(sizes[k]),reason='long thin rule remnant' if rule_remnant else 'outside text-component scale'))
        text_mask = keep[labels][t-ct:t-ct+mask.shape[0],a-ca:a-ca+mask.shape[1]]
        mask &= text_mask
        # The permissive binariser intentionally retains faint connected
        # regions. Background texture is not positive text-crossing evidence:
        # require the line's own foreground contrast after removing rules.
        gray_band = self.gray[t:t+mask.shape[0],a:a+mask.shape[1]]
        paper = float(np.percentile(self.gray[ct:cbot,ca:cb],90))
        foreground = float(np.percentile(gray_band[mask],10)) if mask.any() else paper
        contrast_threshold = (paper+foreground)/2
        mask &= gray_band<=contrast_threshold
        yy, xx = np.nonzero(mask)
        yy, xx = yy+t, xx+a
        inside = (yy >= boundary['path'][0][1]) & (yy <= boundary['path'][-1][1])
        distance = xx-_at(boundary, yy)
        margin = .35*line['xheight'] if boundary['kind']=='rule' else 0.
        # Restrict to adjoining text, not unrelated ink at the far end of a line.
        left = inside & (distance < -margin) & (distance >= -3*line['xheight'])
        right = inside & (distance > margin) & (distance <= 3*line['xheight'])
        counts = [int(left.sum()),int(right.sum())]
        rows = [np.unique(yy[side]) for side in (left,right)]
        overlap = len(np.intersect1d(*rows))
        threshold = .04*line['xheight']**2
        real = min(counts) >= threshold and overlap >= .2*line['xheight']
        return dict(classification='real crossing' if real else 'unresolved envelope overlap',
            line_index=line_index, boundary_id=boundary['id'], boundary_kind=boundary['kind'],
            own_ink_pixels_sides=counts, common_ink_rows=overlap,
            required_ink_pixels_per_side=threshold, required_common_rows=.2*line['xheight'],
            xheight_px=line['xheight'], rule_exclusion_margin_px=margin,
            excluded_rule_components=rejected_components,
            foreground_contrast=dict(paper=paper,ink_q10=foreground,threshold=contrast_threshold),
            line_extent=[line['x0'],min(line['top']),line['x1'],max(line['bottom'])],
            boundary_path=boundary['path'])
