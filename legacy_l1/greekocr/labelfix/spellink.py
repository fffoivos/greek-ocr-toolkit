"""Polytonic spell checker: deterministic/lexical proposals, ink decisions, CTC location only.

The old voter design in rules.py is deliberately untouched. ACCEPT and HOLD are separate
outputs. A recogniser reading never supplies a candidate or changes a lexical/ink gate.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from itertools import product

from .candidates import pair_tokens
from .constraints import ENCLITICS, normalise, syllables, violations
from .ctc_align import Alignment, transfer_alignment
from .ink import CropInk, dialytika_shape, mark_evidence, slope_sign
from .lexicon import ATTESTED_MIN, RATIO_MIN, Lexicon
from .markshape import features, mark_class
from .rules import has_subscript, marks_above
from .text import (ACUTE, GRAVE, Token, clusters, has_greek, has_latin_or_digit, hyphenated_line_end,
                   is_abbreviation, is_all_caps, is_capitalised, lexicon_key, lower_word, nfc, nfd, strip_marks, tokenize)


# Frozen from DEV_BOOKS only; see spellcheck/calibration.json.
TAU_CONTRADICT = 0.90


@dataclass
class Proposal:
    form: str
    count: int
    cluster_index: int
    google_marks: str
    marks: str
    mark_cls: str | None
    # D1 can repair more than one cluster. Every changed cluster must pass.
    changes: tuple = ()


def recase(form_lower: str, like: str) -> str:
    return form_lower[0].upper() + form_lower[1:] if like and like[0].isupper() and form_lower else form_lower


def final_accent_index(core: str) -> int | None:
    cs = clusters(nfd(core))
    ss = syllables(cs)
    accented = [i for i, c in enumerate(cs) if any(m in '́̀͂' for m in c.marks)]
    return accented[0] if len(accented) == 1 and ss and accented[0] in ss[-1] else None


def final_grave_form(core: str) -> str:
    core = nfd(core)
    i = final_accent_index(core)
    return ''.join(c.base + (c.marks.replace(ACUTE, GRAVE) if k == i else c.marks)
                   for k, c in enumerate(clusters(core)))


def written_freq(core: str, lex: Lexicon) -> int:
    """N1, local to this engine: acute/grave are positional spellings of one form."""
    return max(lex.freq(core), lex.freq(final_grave_form(core)))


def only_grave_or_rho(a: str, b: str) -> bool:
    a, b = lower_word(nfd(a)), lower_word(nfd(b))
    if final_grave_form(a) == final_grave_form(b):
        return True
    return bool(a.startswith('ρ') and b.startswith('ρ') and
                'ρ' + a[1:].lstrip('̓̔') == 'ρ' + b[1:].lstrip('̓̔'))


def _proposal(core, form, count, *, multi=False):
    a, b = clusters(lower_word(nfd(core))), clusters(lower_word(nfd(form)))
    if len(a) != len(b) or any(x.base != y.base for x, y in zip(a, b)):
        return None
    changes = tuple((i, x.marks, y.marks) for i, (x, y) in enumerate(zip(a, b)) if x.marks != y.marks)
    if not changes or (not multi and len(changes) != 1) or only_grave_or_rho(core, form):
        return None
    if any(mark_class(y) is None for _, _, y in changes):
        return None
    i, gm, pm = changes[0]
    return Proposal(recase(lower_word(nfd(form)), core), count, i, gm, pm, mark_class(pm), changes)


# Finite legal mark alphabet. Used only for deterministic minimum-edit constraint repairs.
MARK_SETS = tuple(normalise('α' + b + a + s)[1:] for b, a, s in
                  product(('', '̓', '̔', '̈'), ('', ACUTE, GRAVE, '͂'), ('', 'ͅ')))


def _mark_distance(a, b):
    # Multiset edit distance (one replacement costs one; duplicated erroneous marks count).
    from collections import Counter
    aa, bb = Counter(a), Counter(b)
    return max(sum((aa - bb).values()), sum((bb - aa).values()))


def constraint_fallback(core, next_core):
    """Unique constraint-valid minimum mark repair, without lexical or model guesses.

    Dynamic enumeration by total mark edit cost; stop as soon as a valid cost is found.
    Two valid minima suffice to prove non-uniqueness. No arbitrary repair is selected.
    """
    cs = clusters(core)
    choices = []
    for c in cs:
        opts = MARK_SETS if c.base.lower() in 'αεηιουωρ' else ('',)
        opts = set(opts) | {c.marks}
        choices.append(sorted(((_mark_distance(c.marks, x), x) for x in opts)))
    # Removing all marks and supplying an initial breathing bounds the minimum cost.
    bound = sum(len(c.marks) for c in cs) + 1
    for budget in range(1, bound + 1):
        found = []
        def visit(i, left, pieces):
            if len(found) > 1:
                return
            if i == len(cs):
                if left == 0:
                    form = ''.join(pieces)
                    if not violations(form, next_core, hard_only=True):
                        found.append(form)
                return
            for cost, marks in choices[i]:
                if cost > left:
                    break
                visit(i + 1, left - cost, pieces + [cs[i].base + marks])
        visit(0, budget, [])
        if found:
            if len(found) != 1:
                return []
            p = _proposal(core, found[0], 0, multi=True)
            return [p] if p else []
    return []


def alternatives(core, lex, next_core=None, *, multi=False):
    out = []
    for form, n in lex.variants(core).items():
        if n < ATTESTED_MIN or violations(form, next_core, hard_only=True):
            continue
        p = _proposal(core, form, n, multi=multi)
        if p:
            out.append(p)
    return sorted(out, key=lambda p: (-p.count, p.form))


def proposals(core: str, lex: Lexicon, next_core: str | None = None, *, policy='strict'):
    """D1/L1 lexical proposals, including N1/N2; never model-dependent."""
    core = nfd(core)
    if not core or not has_greek(core):
        return [], 'non_greek'
    impossible = bool(violations(core, next_core, hard_only=True))
    written = written_freq(core, lex)
    if impossible:
        out = alternatives(core, lex, next_core, multi=True)
        if out:
            return out, 'constraint_attested'
        fallback = constraint_fallback(core, next_core)
        return fallback, 'constraint_minimal' if fallback else 'constraint_no_unique_supported_minimal_repair'
    if written >= ATTESTED_MIN and policy == 'strict':
        return [], 'attested'
    out = alternatives(core, lex, next_core)
    if policy == 'ratio' and written >= ATTESTED_MIN:
        out = [p for p in out if p.count >= RATIO_MIN * written]
    if not out:
        return [], 'no_attested_one_cluster_variant'
    return out, 'unattested' if written < ATTESTED_MIN else 'ratio'


def guard_reason(tok: Token, is_last: bool, *, guard_names=True, guard_abbr=True):
    if has_latin_or_digit(tok.core):
        return 'latin_or_digit'
    if is_all_caps(tok.core):
        return 'all_caps'
    if hyphenated_line_end(tok, is_last):
        return 'hyphen_line_end'
    if guard_abbr and is_abbreviation(tok):
        return 'abbreviation'
    if guard_names and is_capitalised(tok.core) and tok.index > 0:
        return 'proper_name'
    return None


def locate(g: Token, m: Token | None, al: Alignment, cluster_index: int):
    """CTC locates, including proportional location when the model reads other letters."""
    if m is None:
        return None
    gcl, mcl = clusters(g.core), clusters(m.core)
    cw = al.char_width()
    if strip_marks(m.core) == strip_marks(g.core) and cluster_index < len(mcl):
        c = mcl[cluster_index]
        bi = m.core_start + c.start
        bx0, bx1 = al.window(bi, bi + 1)
        cx0, cx1 = al.window(bi, m.core_start + c.end)
        return 'model_marks', min(bx0, cx0) - cw, max(bx1, cx1) + cw, bx0, bx1
    w0, w1 = al.window(m.start, m.end)
    n = max(1, len(gcl))
    bx0, bx1 = w0 + (w1 - w0) * cluster_index / n, w0 + (w1 - w0) * (cluster_index + 1) / n
    return 'proportional', bx0 - cw, bx1 + cw, bx0, bx1


@dataclass
class Judgement:
    accept: bool
    reason: str
    chosen: Proposal | None = None
    evidence: dict | None = None
    shape: dict | None = None
    ev: object = field(default=None, repr=False)


def evidence_abstention(ev):
    if ev.body_source != 'letter' or ev.n_letters_in_span != 1:
        return 'localisation_uncertain'
    if ev.neighbour_marks:
        return 'neighbouring_marks'
    if any(b.faint for b in ev.above + ev.below):
        return 'faint_mark'
    if ev.clipped_top or ev.clipped_bottom:
        return 'clipped_band'
    return None


def above_count_matches(marks, ev):
    """Breathing + accent can be two blobs or one fused compound, never zero.

    Classification is still required by judge; count compatibility alone does
    not identify the breathing or accent. Dialytika always requires two dots.
    """
    expected = marks_above(marks)
    compound = any(m in marks for m in '̓̔') and any(m in marks for m in '́̀͂')
    return ev.n_above == expected or (compound and expected == 2 and ev.n_above == 1)


def contradiction(p, ev, shape, google_cls, tau_contradict):
    """Concrete HOLD veto. Unreadable evidence is an abstention, never a contradiction."""
    if ev is None:
        return 'abstains', 'no_evidence'
    why = evidence_abstention(ev)
    if why:
        return 'abstains', why
    wide = any(b.w > .5 * ev.xh and slope_sign(b) is None for b in ev.above)
    if wide:
        return 'abstains', 'merged_marks'
    if has_subscript(p.marks) and not ev.below:
        return 'contradicts', 'no_blob_below'
    if '̈' in p.marks and not dialytika_shape(ev):
        return 'contradicts', 'no_two_dots'
    if marks_above(p.marks) > marks_above(p.google_marks) and ev.n_above < marks_above(p.marks) and not above_count_matches(p.marks, ev):
        return 'contradicts', 'too_few_above_blobs'
    if shape and shape['pred'] == google_cls and shape['prob'] >= tau_contradict:
        return 'contradicts', 'classifier_reads_google'
    return 'abstains', 'image_ambiguous'


def judge(props, google_marks_cls, ink, loc, model, tau, *, ev=None, shape=None):
    if ev is None:
        _, x0, x1, bx0, bx1 = loc
        ev = mark_evidence(ink, x0, x1, core_x0=bx0, core_x1=bx1)
    rec = ev.to_record()
    # Record classifier even on abstentions, so every sheet caption remains diagnostic.
    if shape is None and model is not None:
        pred, prob, dist = model.predict(features(ev))
        shape = dict(pred=pred, prob=prob, tau=tau, google_prob=dist.get(google_marks_cls, 0.0))
    def result(ok, reason, p=None):
        return Judgement(ok, reason, p, rec, shape, ev)
    why = evidence_abstention(ev)
    if why:
        return result(False, 'abstain:' + why)
    if shape is None:
        return result(False, 'abstain:no_shape_model')
    pred, prob = shape['pred'], shape['prob']
    matching = [p for p in props if p.mark_cls == pred]
    if not matching:
        return result(False, 'shape_predicts_' + pred)
    p = matching[0]
    if prob < tau:
        return result(False, 'abstain:shape_below_tau', p)
    if pred == google_marks_cls:
        return result(False, 'shape_reads_google', p)
    wide = any(b.w > .5 * ev.xh and slope_sign(b) is None for b in ev.above)
    if not above_count_matches(p.marks, ev):
        return result(False, 'abstain:merged_marks' if wide else 'blob_count_mismatch', p)
    if bool(ev.below) != has_subscript(p.marks):
        return result(False, 'subscript_blob_mismatch', p)
    if '̈' in p.marks and not dialytika_shape(ev):
        return result(False, 'no_two_dots', p)
    if ('psili' in pred or 'dasia' in pred) and any(b.source == 'attached' for b in ev.above) and \
            (google_marks_cls or '').replace('psili', 'dasia') == pred.replace('psili', 'dasia'):
        return result(False, 'abstain:attached_breathing_kind', p)
    return result(True, 'classifier_and_physical_checks', p)


def dialytika_only(p):
    changes = p.changes or ((p.cluster_index, p.google_marks, p.marks),)
    return all(g.replace('̈', '') == m.replace('̈', '') for _, g, m in changes)


def grave_proposal(g, nxt, lex):
    # Before enclitics acute stays. Punctuation / line end are slope-only contexts.
    if nxt and lexicon_key(nxt) in ENCLITICS and not g.trail:
        return None
    form = final_grave_form(g.core)
    if form == g.core:
        return None
    i = final_accent_index(g.core)
    gm, pm = clusters(g.core)[i].marks, clusters(form)[i].marks
    return Proposal(form, written_freq(form, lex), i, gm, pm, mark_class(pm), ((i, gm, pm),))


def judge_grave(p, ev, shape, *, positional, book_style):
    rec = ev.to_record()
    why = evidence_abstention(ev)
    def result(ok, reason):
        return Judgement(ok, reason, p, rec, shape, ev)
    if book_style == 'acute':
        return result(False, 'abstain:book_prints_acute')
    if why:
        return result(False, 'abstain:' + why)
    if ev.n_above != marks_above(p.marks) or ev.n_above != 1:
        return result(False, 'abstain:grave_accent_not_isolated')
    if bool(ev.below) != has_subscript(p.marks):
        return result(False, 'subscript_blob_mismatch')
    slope = slope_sign(ev.above[0])
    if slope == 'grave':
        return result(True, 'decisive_grave_slope')
    if positional and book_style == 'grave' and slope != 'acute':
        return result(True, 'positional_grave;accent_present;not_acute_slope')
    return result(False, 'abstain:' + ('acute_slope' if slope == 'acute' else 'grave_slope_required'))


def spell_ink_line(line_id, google, model_text, al, ink, lex, shape_model, *, guard_names=True,
                   guard_abbr=True, extra=None, tau_contradict=TAU_CONTRADICT, book_style='unknown'):
    google, model_text = nfd(google), nfd(model_text)
    if al is not None and nfd(al.prediction) != model_text:
        al = transfer_alignment(model_text, al)
    gt, pairs, out = tokenize(google), {g.index: m for g, m in pair_tokens(google, model_text)}, []
    for g in gt:
        if not g.core:
            continue
        nxt = gt[g.index + 1].core if g.index + 1 < len(gt) else None
        guard = guard_reason(g, g.index == len(gt) - 1, guard_names=guard_names, guard_abbr=guard_abbr)
        if not has_greek(g.core) and not guard:
            guard = 'non_greek'
        m = pairs.get(g.index)
        cache = {}
        def evidence(i):
            if i not in cache:
                loc = locate(g, m, al, i) if al is not None else None
                if loc is None or ink is None:
                    cache[i] = (loc, None, None)
                else:
                    _, x0, x1, bx0, bx1 = loc
                    ev = mark_evidence(ink, x0, x1, core_x0=bx0, core_x1=bx1, base_letter=clusters(g.core)[i].base)
                    shape = None
                    if shape_model is not None:
                        pred, prob, dist = shape_model.predict(features(ev))
                        shape = dict(pred=pred, prob=prob, tau=shape_model.tau,
                                     google_prob=dist.get(mark_class(clusters(g.core)[i].marks), 0.0))
                    cache[i] = (loc, ev, shape)
            return cache[i]
        written = written_freq(g.core, lex)
        impossible = bool(violations(g.core, nxt, hard_only=True))
        dp = grave_proposal(g, nxt, lex)
        d2_attempt = None
        if dp and (g.trail or nxt is None) and not guard:
            loc, ev, shape = evidence(dp.cluster_index)
            gj = judge_grave(dp, ev, shape, positional=False, book_style=book_style) if ev is not None else None
            d2_attempt = gj.reason if gj else 'abstain:locator_unpaired'
            if gj is None or not gj.accept:
                dp = None
        if impossible:
            stage, (props, why) = 'D1', proposals(g.core, lex, nxt)
            ratio_props = props
        elif dp:
            stage, props, ratio_props, why = 'D2', [dp], [dp], 'final_acute'
        elif written < ATTESTED_MIN:
            stage, (props, why) = 'L1', proposals(g.core, lex, nxt)
            ratio_props = props
        else:
            stage, props, why = 'L2', alternatives(g.core, lex, nxt), 'attested_alternatives'
            # Mark-bearing means vowel/rho clusters, including unmarked vowels (των -> τῶν).
            # The classifier, never the recogniser's text, must supply the differing class.
            props = [p for p in props if clusters(g.core)[p.cluster_index].base.lower() in 'αεηιουωρ']
            ratio_props, _ = proposals(g.core, lex, nxt, policy='ratio')
        # Ratio policy is an additional L1 trigger, not an L2 confidence relaxation.
        all_props = {p.form: p for p in props + ratio_props}
        if guard_names and is_capitalised(g.core) and g.index == 0:
            if lex.name_count(g.core) >= 3:
                guard = 'known_name'
            all_props = {f: p for f, p in all_props.items() if p.count >= 50 and lex.name_count(f) < 3}
            props = [p for p in props if p.form in all_props]
            ratio_props = [p for p in ratio_props if p.form in all_props]
            if not all_props and not guard:
                guard = 'initial_capital_unattested_50'
        m = pairs.get(g.index)
        r = dict(line_id=line_id, word_index=g.index, n_words=len(gt), stage=stage, google_token=g.text,
                 google_core=g.core, google_nfc=nfc(g.text), written_count=written, lexicon_reason=why,
                 model_token=m.text if m else None, model_nfc=nfc(m.text) if m else None,
                 book_style=book_style, tau_contradict=tau_contradict, d2_attempt=d2_attempt,
                 proposals=[dict(form=nfc(p.form), count=p.count, cluster=p.cluster_index, cls=p.mark_cls,
                                 changes=p.changes) for p in props],
                 ratio_proposals=[nfc(p.form) for p in ratio_props], ratio_stage=stage,
                 decision=dict(accept=False, column=None, reason='no_proposal'), ratio_decision=None,
                 model_agrees=False, ink=None, shape=None, cluster_window=None, word_window=None)
        r.update(extra or {})
        if guard:
            r['decision']['reason'] = 'excluded:' + guard
            r['ratio_decision'] = dict(r['decision'])
            out.append(r)
            continue
        if not all_props:
            r['decision']['reason'] = why if why != 'attested_alternatives' else 'no_attested_mark_alternative'
            r['ratio_decision'] = dict(r['decision'])
            out.append(r)
            continue
        judged, traces = {}, {}
        hold_forbidden = set()
        for p in all_props.values():
            js, vetoes = [], []
            adds_final_grave = any(ACUTE in gm and GRAVE in pm and i == final_accent_index(g.core)
                                   for i,gm,pm in p.changes)
            slope_only_grave = adds_final_grave and (g.trail or nxt is None)
            if slope_only_grave or adds_final_grave and book_style == 'acute':
                hold_forbidden.add(p.form)
            for i, gm, pm in p.changes:
                loc, ev, shape = evidence(i)
                cp = replace(p, cluster_index=i, google_marks=gm, marks=pm, mark_cls=mark_class(pm))
                if ev is None:
                    j = Judgement(False, 'abstain:locator_unpaired' if loc is None else 'abstain:no_crop')
                elif stage == 'D2':
                    j = judge_grave(cp, ev, shape, positional=bool(nxt and not g.trail), book_style=book_style)
                else:
                    j = judge([cp], mark_class(gm), ink, loc, shape_model,
                              shape_model.tau if shape_model else 1.0, ev=ev, shape=shape)
                if adds_final_grave and book_style == 'acute':
                    j = replace(j, accept=False, reason='abstain:book_prints_acute')
                elif slope_only_grave and ACUTE in gm and GRAVE in pm and j.accept and not any(slope_sign(b) == 'grave' for b in ev.above):
                    j = replace(j, accept=False, reason='abstain:grave_slope_required')
                js.append(j)
                vetoes.append(contradiction(cp, ev, shape, mark_class(gm), tau_contradict))
            primary = next((j for j in js if not j.accept), js[0])
            judged[p.form] = (all(j.accept for j in js), primary, vetoes)
            traces[p.form] = [dict(cluster=i, accept=cj.accept, reason=cj.reason, ink=cj.evidence,
                                   shape=cj.shape, cluster_window=list(evidence(i)[0][3:]) if evidence(i)[0] else None)
                              for (i, _, _), cj in zip(p.changes, js)]
        def decide(ps, hold_stage):
            accepted = [p for p in ps if judged[p.form][0]]
            if len(accepted) == 1:
                p = accepted[0]
                return p, 'ACCEPT', judged[p.form][1].reason
            if len(accepted) > 1:
                return None, None, 'abstain:competing_ink_supported_proposals'
            if len(ps) == 1 and hold_stage in ('D1', 'L1') and not dialytika_only(ps[0]) and ps[0].form not in hold_forbidden:
                p = ps[0]
                _, j, vs = judged[p.form]
                if j.evidence is not None and not any(v == 'contradicts' for v, _ in vs):
                    return p, 'HOLD', 'ambiguous_image;' + j.reason
            return None, None, judged[ps[0].form][1].reason if ps else 'no_proposal'
        chosen, col, reason = decide(props, stage)
        rp, rc, rr = decide(ratio_props if stage == 'L2' else props, 'L1' if stage == 'L2' else stage)
        # Ratio includes ordinary L2 if its extra lexical trigger did not decide.
        if stage == 'L2' and rc is None:
            rp, rc, rr = chosen, col, reason
        elif stage == 'L2' and rc is not None:
            r['ratio_stage'] = 'L1'
        if r['ratio_stage'] == stage:
            r['ratio_proposals'] = [nfc(p.form) for p in props]
        r['ratio_decision'] = dict(accept=rc == 'ACCEPT', column=rc, proposal=nfc(rp.form) if rp else None, reason=rr)
        r['decision'] = dict(accept=col == 'ACCEPT', column=col, reason=reason,
                             proposal=nfc(chosen.form) if chosen else None)
        shown = chosen or (props[0] if props else next(iter(all_props.values())))
        _, j, vs = judged[shown.form]
        shown_checks = traces[shown.form]
        primary_check = next((ck for ck in shown_checks if not ck['accept']), shown_checks[0])
        loc, ev, shape = evidence(primary_check['cluster'])
        r.update(ink=j.evidence, shape=j.shape, locator=loc[0] if loc else 'unpaired',
                 ink_verdict='supports' if col == 'ACCEPT' else 'contradicts' if any(v == 'contradicts' for v, _ in vs) else 'abstains',
                 contradiction_reasons=[why for v, why in vs if v == 'contradicts'],
                 proposal_core=shown.form, corrected_token=g.lead + shown.form + g.trail,
                 corrected_nfc=nfc(g.lead + shown.form + g.trail),
                 model_agrees=bool(m and lower_word(m.core) == lower_word(shown.form)),
                 cluster_window=[loc[3], loc[4]] if loc else None,
                 word_window=list(al.window(m.start, m.end)) if al and m else None,
                 cluster_checks=[primary_check]+[ck for ck in shown_checks if ck is not primary_check],
                 proposal_checks={nfc(f):dict(accept=ok, reason=cj.reason,
                     contradictions=[why for v,why in cv if v=='contradicts'],
                     clusters=[dict(cluster=x['cluster'],accept=x['accept'],reason=x['reason']) for x in traces[f]])
                     for f,(ok,cj,cv) in judged.items()})
        out.append(r)
    return out
