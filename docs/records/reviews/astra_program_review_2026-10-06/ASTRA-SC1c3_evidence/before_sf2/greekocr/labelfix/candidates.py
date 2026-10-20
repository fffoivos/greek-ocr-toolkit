"""Google-vs-model word pairing and evidence gathering -> candidate records.

For a line: Google's label (NFD), the recogniser's prediction with its CTC alignment, the
crop's ink analysis and the three lexicons. Words are paired through a character-level
alignment of the two readings (unit-cost Levenshtein path, as bench/e1_readout.alignment),
so lines whose word counts differ still pair the words they share. Only one-to-one pairs
whose aligned model text is a single token are candidates.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import unicodedata as ud

from .constraints import violations
from .ctc_align import Alignment
from .ink import CropInk, dialytika_shape, mark_evidence, slope_sign
from .lexicon import REGIMES, choose_regime
from .rules import Candidate, Decision, InkSummary, decide, line_initial_allowed
from .text import (ACUTE, GRAVE, Token, accent_of, classify_diff, clusters, hyphenated_line_end, is_abbreviation,
                   is_capitalised, lower_word, nfc, nfd, tokenize)


def align_chars(ref: str, hyp: str) -> list[tuple[int | None, int | None]]:
    """Unit-cost alignment path as (ref_index | None, hyp_index | None) pairs."""
    n, m = len(ref), len(hyp)
    prefix = 0
    while prefix < min(n, m) and ref[prefix] == hyp[prefix]:
        prefix += 1
    suffix = 0
    while suffix < min(n, m) - prefix and ref[n - suffix - 1] == hyp[m - suffix - 1]:
        suffix += 1
    before = [(i, i) for i in range(prefix)]
    after = [(n - suffix + k, m - suffix + k) for k in range(suffix)]
    r, h = ref[prefix:n - suffix], hyp[prefix:m - suffix]
    dp = [list(range(len(h) + 1))] + [[i] + [0] * len(h) for i in range(1, len(r) + 1)]
    for i, a in enumerate(r, 1):
        for j, b in enumerate(h, 1):
            dp[i][j] = min(dp[i - 1][j - 1] + (a != b), dp[i - 1][j] + 1, dp[i][j - 1] + 1)
    i, j, path = len(r), len(h), []
    while i or j:
        if i and j and dp[i][j] == dp[i - 1][j - 1] + (r[i - 1] != h[j - 1]):
            path.append((prefix + i - 1, prefix + j - 1)); i -= 1; j -= 1
        elif i and dp[i][j] == dp[i - 1][j] + 1:
            path.append((prefix + i - 1, None)); i -= 1
        else:
            path.append((None, prefix + j - 1)); j -= 1
    return before + list(reversed(path)) + after


def pair_tokens(google: str, model: str) -> list[tuple[Token, Token | None]]:
    """Pair each Google token with the single model token its characters align to (or None)."""
    gt, mt = tokenize(google), tokenize(model)
    if len(gt) == len(mt):
        return list(zip(gt, mt))
    path = align_chars(nfd(google), nfd(model))
    owner = {}
    for t in mt:
        for k in range(t.start, t.end):
            owner[k] = t.index
    pairs = []
    for g in gt:
        hits = {owner[j] for i, j in path if i is not None and g.start <= i < g.end and j is not None and j in owner}
        if len(hits) == 1:
            m = mt[next(iter(hits))]
            # the model token must align to this Google token only
            back = {i for i, j in path if j is not None and m.start <= j < m.end and i is not None}
            if back and all(g.start <= i < g.end for i in back):
                pairs.append((g, m))
                continue
        pairs.append((g, None))
    return pairs


@dataclass
class LineContext:
    line_id: str
    google: str
    model: str
    script_class: str = ''
    wave: str = ''
    crop_path: str = ''
    alignment: Alignment | None = None
    ink: CropInk | None = None
    regime_override: str | None = None   # e.g. the document's majority regime
    acute_style: bool = False            # page-level: acute printed on every final syllable (policy 3b)
    shape_model: object = None           # markshape model (pass 4); None = no ink_decisive column
    extra: dict = field(default_factory=dict)


def line_candidates(ctx: LineContext, lexicons: dict, policy: str = 'strict') -> list[dict]:
    google, model = nfd(ctx.google), nfd(ctx.model)
    if ctx.alignment is not None and nfd(ctx.alignment.prediction) != model:
        from .ctc_align import transfer_alignment
        ctx.alignment = transfer_alignment(model, ctx.alignment)
    pairs = pair_tokens(google, model)
    gt = [g for g, _ in pairs]
    disputed = {g.index for g, m in pairs if m is None or g.core != m.core}
    undisputed = [g.core for g in gt if g.index not in disputed and g.core]
    regime, cover = choose_regime(ctx.script_class, undisputed, lexicons, (google, model))
    if ctx.regime_override:
        regime = ctx.regime_override
    lex = lexicons[regime]
    # regime uncertainty: the two polytonic lexicons attest the line about equally, or the line
    # has too few attested words to tell (quotations / mixed orthography on one page)
    ranked = sorted(cover.values(), reverse=True) + [0, 0]
    regime_uncertain = len(undisputed) >= 2 and (ranked[0] == 0 or (ranked[0] - ranked[1]) < max(1, 0.2 * len(undisputed)))
    if ctx.regime_override:
        regime_uncertain = False
    out = []
    for g, m in pairs:
        if m is None or g.core == m.core:
            continue
        diff = classify_diff(g.core, m.core)
        if diff is None:
            continue
        next_core = gt[g.index + 1].core if g.index + 1 < len(gt) else None
        g_viol = violations(g.core, next_core, hard_only=True) if regime != 'mono' and diff.kind == 'marks' else []
        m_viol = violations(m.core, next_core, hard_only=True) if regime != 'mono' and diff.kind == 'marks' else []
        g_variants = lex.variants(g.core)
        g_key_freq = max([n for f, n in g_variants.items() if f != lower_word(g.core)] or [0])
        cand = Candidate(g.core, m.core, diff, g.trail, g.lead, is_abbreviation(g),
                         hyphenated_line_end(g, g.index == len(gt) - 1), regime, regime_uncertain,
                         lex.freq(m.core), lex.freq(g.core), g_key_freq, g_viol, m_viol,
                         line_initial=(g.index == 0), model_lower_freq=lex.freq(m.core),
                         name_count=lex.name_count(m.core), acute_style=ctx.acute_style)
        ev_rec = None
        cl_window = None
        word_window = None
        if ctx.alignment is not None and ctx.ink is not None and diff.kind == 'marks':
            al = ctx.alignment
            mcl = clusters(m.core)[diff.cluster_index]
            base_i = m.core_start + mcl.start
            cw = al.char_width()
            bx0, bx1 = al.window(base_i, base_i + 1)
            cx0, cx1 = al.window(base_i, m.core_start + mcl.end)
            x0, x1 = min(bx0, cx0) - 1.0 * cw, max(bx1, cx1) + 1.0 * cw
            ev = mark_evidence(ctx.ink, x0, x1, core_x0=bx0, core_x1=bx1)
            obl = [slope_sign(b) for b in ev.above]
            merged = any(b.w > 0.5 * ev.xh and slope_sign(b) is None for b in ev.above)   # wide enough for two fused marks
            if ctx.shape_model is not None and ev.body_source == 'letter' and ev.n_letters_in_span == 1:
                from .markshape import features, mark_class
                pred, prob, dist = ctx.shape_model.predict(features(ev))
                cand.shape_pred, cand.shape_prob, cand.shape_tau = pred, prob, ctx.shape_model.tau
                mcls = mark_class(mcl.marks)
                gcls = mark_class(clusters(g.core)[diff.cluster_index].marks)
                cand.shape_model_prob = dist.get(mcls, 0.0) if mcls else 0.0
                cand.shape_google_prob = dist.get(gcls, 0.0) if gcls else 0.0
            cand.ink = InkSummary(True, ev.n_above, len(ev.below), [s for s in obl if s], dialytika_shape(ev),
                                  sum(1 for s in obl if s is None),
                                  localised=(ev.body_source == 'letter' and ev.n_letters_in_span == 1),
                                  neighbour_marks=ev.neighbour_marks,
                                  faint=any(b.faint for b in ev.above + ev.below),
                                  clipped_top=ev.clipped_top, clipped_bottom=ev.clipped_bottom, merged=merged,
                                  wide_blob=any(b.w > 0.45 * ev.xh for b in ev.above),
                                  attached=any(b.source == 'attached' for b in ev.above))
            ev_rec = ev.to_record()
            cl_window = [round(bx0, 1), round(bx1, 1)]
            word_window = [round(v, 1) for v in al.window(m.start, m.end)]
        elif ctx.alignment is not None:
            al = ctx.alignment
            mcl = clusters(m.core)[diff.cluster_index]
            base_i = m.core_start + mcl.start
            cl_window = [round(v, 1) for v in al.window(base_i, base_i + 1)]
            word_window = [round(v, 1) for v in al.window(m.start, m.end)]
        dec = decide(cand, policy)
        corrected = g.lead + m.core + g.trail
        rec = dict(line_id=ctx.line_id, wave=ctx.wave, crop_path=ctx.crop_path, script_class=ctx.script_class,
                   word_index=g.index, n_words=len(gt),
                   google_token=g.text, model_token=m.text, google_core=g.core, model_core=m.core,
                   google_nfc=nfc(g.text), model_nfc=nfc(m.text), corrected_token=corrected,
                   corrected_nfc=nfc(corrected),
                   diff=dict(kind=diff.kind, cluster_index=diff.cluster_index, google=nfc(diff.google),
                             model=nfc(diff.model), categories=sorted(diff.categories), final=diff.final_position),
                   regime=regime, regime_coverage=cover, regime_uncertain=regime_uncertain,
                   model_freq=cand.model_freq, google_freq=cand.google_freq, google_key_freq=g_key_freq,
                   constraints=dict(google=g_viol, model=m_viol),
                   line_initial=(g.index == 0), name_count=cand.name_count, acute_style=ctx.acute_style,
                   shape=dict(pred=cand.shape_pred, prob=round(cand.shape_prob, 4), model_prob=round(cand.shape_model_prob, 4),
                              google_prob=round(cand.shape_google_prob, 4), tau=cand.shape_tau) if cand.shape_pred else None,
                   line_initial_allowed=line_initial_allowed(cand) and (is_capitalised(g.core) or is_capitalised(m.core)),
                   variants={nfc(k): v for k, v in sorted(lex.variants(g.core).items(), key=lambda kv: -kv[1])[:8]},
                   ink=ev_rec, cluster_window=cl_window, word_window=word_window,
                   decision=dec.to_record())
        rec.update(ctx.extra)
        out.append(rec)
    return out


def acute_house_style(google_lines: list[str], min_words: int = 10, threshold: float = 0.8) -> tuple[bool, float, int]:
    """Policy 3b detector on a page's Google text: among words whose final syllable carries an acute
    or a grave and that are followed by another word on the same line (no trailing punctuation),
    the share of acute. Classical polytonic prints a grave there; a share above `threshold` on at
    least `min_words` words means the print uses acute everywhere."""
    acute = grave = 0
    for line in google_lines:
        toks = tokenize(line)
        for t in toks[:-1]:
            if t.trail or not t.core:
                continue
            cl = clusters(t.core)
            bearers = [c for c in cl if c.base in 'αεηιουωΑΕΗΙΟΥΩ']
            if not bearers:
                continue
            a = accent_of(bearers[-1].marks)
            if a == ACUTE:
                acute += 1
            elif a == GRAVE:
                grave += 1
    n = acute + grave
    share = acute / n if n else 0.0
    return (n >= min_words and share > threshold), share, n


def corrected_line(google: str, accepted: list[dict]) -> str:
    """Apply accepted candidates (by word_index) to Google's line."""
    toks = tokenize(google)
    by_index = {c['word_index']: c for c in accepted if c['decision']['accept']}
    pieces = []
    line = nfd(google)
    pos = 0
    for t in toks:
        pieces.append(line[pos:t.start])
        pieces.append(by_index[t.index]['corrected_token'] if t.index in by_index else t.text)
        pos = t.end
    pieces.append(line[pos:])
    return ''.join(pieces)
