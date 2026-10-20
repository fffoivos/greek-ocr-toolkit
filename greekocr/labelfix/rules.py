"""The rule engine: pure functions over a candidate's evidence. No I/O, no model, no pixels.

A candidate is a word position where the recogniser's reading differs from Google's.
`decide` returns the rule it falls under and whether the correction is accepted, with the
reason for every rejection, and keeps the lexicon and ink verdicts separately so the
validation can report lexicon-alone / ink-alone / both agreement rates.

Rules (owner brief, 16 Oct 2026):
  breathing, accent, subscript, dialytika, marks_multi   mark changes on ONE vowel cluster:
      lexicon (model form attested >= 5; Google's form unattested, or under the `ratio`
      policy >= 20x rarer) AND ink agreement in the vowel's window.
  final_grave    acute <-> grave on the final syllable: the lexicon is position-blind (both forms
                 are attested), so the ONLY evidence is the ink: exactly one oblique mark whose slope
                 agrees with the model's reading. No positional exception: without a readable slope
                 the rule abstains.
  base_sub       one base-letter substitution from the confusion list: lexicon margin >= 50x.
  final_sigma    sigma <-> final sigma at the word end: lexicon margin >= 50x.
  constraint     Google's form breaks a hard orthographic constraint (constraints.py) and the model's
                 form breaks none: the lexicon is not required, the ink conjunction for the mark is.

Outcomes are `accepted`, `rejected` (evidence contradicts the model), `abstain:*` (evidence
unreadable: regime uncertain, vowel not localised, neighbouring marks, faint / merged / clipped
ink, no discriminative mark shape) or `excluded:*` (guards).

Guards (never corrected): proper names (capitalised), abbreviations (trailing '.', <= 3
letters), words with Latin letters or digits, hyphenated line ends, all-caps words for mark
rules (print without accents), and anything that is not a single allowed difference.

The `both attested -> leave` principle (rule 5) is the default policy `strict`: a Google form
with count >= ATTESTED_MIN is left alone even if the model's form is far commoner. Policy
`ratio` is the literal rule 1 (>= 20x rarer suffices) and is reported for comparison only.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .lexicon import ATTESTED_MIN, POLY_ONLY, RATIO_MIN, RATIO_MIN_BASE
from .text import (ACUTE, GRAVE, CIRCUMFLEX, BREATHINGS, ACCENTS, DIALYTIKA, SUBSCRIPT, Diff, accent_of,
                   classify_diff, has_greek, has_latin_or_digit, is_all_caps, is_capitalised)

RULES = ('breathing', 'accent', 'subscript', 'dialytika', 'marks_multi', 'final_grave', 'base_sub', 'final_sigma', 'constraint')
MARK_RULES = ('breathing', 'accent', 'subscript', 'dialytika', 'marks_multi')
POLICIES = ('strict', 'ratio')


@dataclass
class InkSummary:
    """What the rule engine needs from `ink.MarkEvidence` (kept plain so tests need no pixels)."""
    available: bool = False
    n_above: int = 0
    n_below: int = 0
    obliques: list = field(default_factory=list)   # 'acute' | 'grave' per oblique blob above
    dialytika_shape: bool = False
    n_flat: int = 0                                 # blobs above that are not oblique
    localised: bool = True      # exactly one letter under the CTC span, body snapped to a letter component
    neighbour_marks: int = 0    # mark blobs in the search window that belong to other letters
    faint: bool = False         # any counted blob is faint
    clipped_top: bool = False   # ink touches the crop's top edge in the window
    clipped_bottom: bool = False
    merged: bool = False        # a single blob wide enough to be two fused marks
    wide_blob: bool = False     # any blob above wider than 0.45 x-height (not a lone breathing/acute)
    attached: bool = False      # any counted blob above was sliced off a letter (fused mark): its shape is truncated


@dataclass
class Candidate:
    google_core: str
    model_core: str
    diff: Diff | None = None
    trailing_punct: str = ''
    leading_punct: str = ''
    is_abbreviation: bool = False
    hyphen_line_end: bool = False
    regime: str = ''
    regime_uncertain: bool = False
    model_freq: int = 0
    google_freq: int = 0
    google_key_freq: int = 0    # best count of any OTHER marked form of Google's letters (mark-stripped key)
    google_violations: list = field(default_factory=list)   # orthographic constraints Google's form breaks
    model_violations: list = field(default_factory=list)    # ... the model's form breaks
    line_initial: bool = False          # first word of the line
    model_lower_freq: int = 0           # count of the lower-cased model form (for line-initial capitals)
    name_count: int = 0                 # how often the lower-cased form is a capitalised mid-sentence word
    acute_style: bool = False           # the page prints acute on every final syllable (no grave)
    shape_pred: str | None = None       # mark-shape classifier: predicted mark class at the vowel
    shape_prob: float = 0.0             # ... its probability
    shape_model_prob: float = 0.0       # probability of the model's mark class
    shape_google_prob: float = 0.0      # probability of Google's mark class
    shape_tau: float = 1.0              # calibrated threshold (99 % precision on held-out books)
    ink: InkSummary = field(default_factory=InkSummary)


@dataclass
class Decision:
    rule: str
    accept: bool
    reason: str
    lexicon_ok: bool | None = None   # None = not consulted for this rule
    ink_ok: bool | None = None
    policy: str = 'strict'
    base_rule: str = ''              # for rule 'constraint': the mark category the ink verdict used
    lexicon_neutral: bool = False    # both forms attested, or both unattested
    ink_decisive: bool = False       # pass-4 variant: lexicon neutral AND the mark-shape classifier is decisive
    ink_decisive_reason: str = ''

    def to_record(self) -> dict:
        return dict(rule=self.rule, accept=self.accept, reason=self.reason, lexicon_ok=self.lexicon_ok,
                    ink_ok=self.ink_ok, policy=self.policy, base_rule=self.base_rule or self.rule,
                    lexicon_neutral=self.lexicon_neutral, ink_decisive=self.ink_decisive,
                    ink_decisive_reason=self.ink_decisive_reason)


def marks_above(cluster: str) -> int:
    """Expected number of ink blobs above the vowel: breathing 1, accent 1, dialytika 2 (two dots)."""
    return sum(2 if c in DIALYTIKA else 1 for c in cluster if c in BREATHINGS or c in ACCENTS or c in DIALYTIKA)


def has_subscript(cluster: str) -> bool:
    return any(c in SUBSCRIPT for c in cluster)


def rule_for(diff: Diff) -> str:
    if diff.kind == 'base':
        return 'final_sigma' if 'final_sigma' in diff.categories else 'base_sub'
    cats = diff.categories
    if cats == frozenset({'accent'}) and diff.final_position:
        ga, ma = accent_of(diff.google), accent_of(diff.model)
        if {ga, ma} == {ACUTE, GRAVE}:
            return 'final_grave'
    if len(cats) == 1:
        return next(iter(cats))
    return 'marks_multi'


LINE_INITIAL_MIN_FREQ = 50   # policy 3a: a line-initial capitalised word may be corrected when its lower-cased
NAME_LIST_MIN = 3            # model form is attested >= 50 and is not a proper name (>= 3 mid-sentence capitals)


def line_initial_allowed(cand: Candidate) -> bool:
    return cand.line_initial and cand.model_lower_freq >= LINE_INITIAL_MIN_FREQ and cand.name_count < NAME_LIST_MIN


def guard(cand: Candidate) -> str | None:
    g, m = cand.google_core, cand.model_core
    if not has_greek(g) or not has_greek(m):
        return 'non_greek'
    if has_latin_or_digit(g) or has_latin_or_digit(m):
        return 'latin_or_digit'
    if cand.is_abbreviation:
        return 'abbreviation'
    if (is_capitalised(g) or is_capitalised(m)) and not line_initial_allowed(cand):
        return 'proper_name'
    if cand.hyphen_line_end:
        return 'hyphen_line_end'
    return None


def lexicon_verdict(cand: Candidate, rule: str, policy: str) -> tuple[bool, str]:
    mf, gf = cand.model_freq, cand.google_freq
    ratio = RATIO_MIN_BASE if rule in ('base_sub', 'final_sigma') else RATIO_MIN
    if mf < ATTESTED_MIN:
        return False, f'model_form_unattested({mf}<{ATTESTED_MIN})'
    if gf == 0:
        return True, f'google_form_unattested;model={mf}'
    if policy == 'strict' and gf >= ATTESTED_MIN:
        return False, f'both_attested(google={gf},model={mf})'
    if mf < ratio * gf:
        return False, f'margin_below_{ratio}x(google={gf},model={mf})'
    return True, f'margin_ok(google={gf},model={mf},>={ratio}x)'


def ink_verdict(cand: Candidate, rule: str) -> tuple[bool, str]:
    ink = cand.ink
    if not ink.available:
        return False, 'abstain:no_ink'
    d = cand.diff
    g_above, m_above = marks_above(d.google), marks_above(d.model)
    g_sub, m_sub = has_subscript(d.google), has_subscript(d.model)
    # abstentions: the ink cannot be read with confidence at this vowel
    if not ink.localised:
        return False, 'abstain:localisation_uncertain'
    if ink.neighbour_marks and (m_above != g_above or m_sub != g_sub):
        return False, f'abstain:neighbouring_marks({ink.neighbour_marks})'
    if ink.faint:
        return False, 'abstain:faint_mark'
    if ink.merged and ink.n_above != m_above:
        return False, 'abstain:merged_marks'
    if m_above < g_above and ink.wide_blob:
        # a mark removal supported only by a blob count: a wide blob can be two fused marks
        return False, 'abstain:removal_with_wide_blob'
    if ink.clipped_top and m_above < g_above:
        return False, 'abstain:clipped_top_no_false_absence'
    if ink.clipped_top and m_above > g_above and ink.n_above < m_above:
        return False, 'abstain:clipped_top'
    if ink.clipped_bottom and m_sub != g_sub:
        return False, 'abstain:clipped_bottom'
    if rule == 'final_grave':
        if cand.trailing_punct:
            return False, 'abstain:final_grave_before_punctuation'
        if cand.acute_style and accent_of(d.model) == GRAVE:
            # policy 3b: the page prints acute everywhere; follow the print, never normalise to grave
            return False, 'abstain:acute_house_style'
        if len(ink.obliques) != 1 or ink.n_above > 2:
            return False, f'abstain:needs_one_oblique(obliques={len(ink.obliques)},above={ink.n_above})'
        want = 'grave' if accent_of(d.model) == GRAVE else 'acute'
        if ink.obliques[0] != want:
            return False, f'slope_disagrees(ink={ink.obliques[0]},model={want})'
        return True, f'slope_agrees({want})'
    if rule == 'subscript':
        if ink.n_above != m_above:
            return False, f'above_count(ink={ink.n_above},model={m_above})'
        if m_sub and ink.n_below < 1:
            return False, 'no_blob_below'
        if not m_sub and ink.n_below >= 1:
            return False, 'blob_below_but_model_has_none'
        return True, f'below={ink.n_below}'
    if rule == 'dialytika':
        has_d = any(c in DIALYTIKA for c in d.model)
        if ink.n_above != m_above:
            return False, f'above_count(ink={ink.n_above},model={m_above})'
        if has_d and not ink.dialytika_shape:
            return False, 'no_two_dots'
        if not has_d and ink.dialytika_shape:
            return False, 'two_dots_but_model_has_none'
        return True, 'dots_match'
    # breathing / accent / marks_multi: count agreement, and the single-oblique shape where it applies
    if ink.n_above != m_above:
        return False, f'above_count(ink={ink.n_above},model={m_above},google={g_above})'
    if m_sub != g_sub and ink.n_below < 1 and m_sub:
        return False, 'no_blob_below'
    ma, ga = accent_of(d.model), accent_of(d.google)
    if rule in ('accent', 'marks_multi') and ma is not None and ma != ga:
        # the accent itself changes: its shape must be discriminative (slope for acute/grave,
        # a non-oblique blob for the circumflex); otherwise abstain
        if ma in (ACUTE, GRAVE):
            want = 'acute' if ma == ACUTE else 'grave'
            if len(ink.obliques) != 1:
                return False, f'abstain:needs_one_oblique(obliques={len(ink.obliques)},above={ink.n_above})'
            if ink.obliques[0] != want:
                return False, f'slope_disagrees(ink={ink.obliques[0]},model={want})'
        elif ma == CIRCUMFLEX:
            if ink.obliques:
                return False, 'oblique_but_model_has_circumflex'
            if ink.n_flat < 1:
                return False, 'abstain:no_flat_blob_for_circumflex'
    if g_above == 0 and m_above >= 1:
        return True, f'mark_present(above={ink.n_above})'
    return True, f'count_matches(above={ink.n_above})'


def lexicon_neutral(cand: Candidate) -> bool:
    """The spell checker neither supports nor contradicts the model: both forms attested (>= ATTESTED_MIN)
    or both unattested (< ATTESTED_MIN)."""
    mf, gf = cand.model_freq, cand.google_freq
    return (mf >= ATTESTED_MIN and gf >= ATTESTED_MIN) or (mf < ATTESTED_MIN and gf < ATTESTED_MIN)


def ink_decisive_verdict(cand: Candidate, rule: str) -> tuple[bool, str]:
    """Pass-4 variant for lexicon-neutral mark candidates: the ordinary ink conjunction must hold AND the
    mark-shape classifier must give the model's mark class p >= tau while not predicting Google's."""
    if cand.shape_pred is None:
        return False, 'no_shape_model'
    ok, why = ink_verdict(cand, rule if rule in MARK_RULES else 'accent')
    if not ok:
        return False, 'ink_conjunction:' + why
    from .markshape import mark_class
    mc, gc = mark_class(''.join(c for c in cand.diff.model if __import__('unicodedata').category(c).startswith('M'))), mark_class(''.join(c for c in cand.diff.google if __import__('unicodedata').category(c).startswith('M')))
    if mc is None:
        return False, 'model_marks_outside_scheme'
    if cand.ink.attached and ('psili' in (mc or '') or 'dasia' in (mc or '') or 'psili' in (gc or '') or 'dasia' in (gc or '')):
        # a breathing fused to its vowel is cut at the mean line: the hook that tells rough from smooth is lost
        return False, 'attached_breathing_not_decisive'
    if cand.shape_pred != mc:
        return False, f'shape_predicts_{cand.shape_pred}(p={cand.shape_prob:.3f})'
    if cand.shape_prob < cand.shape_tau:
        return False, f'shape_below_tau(p={cand.shape_prob:.3f}<{cand.shape_tau})'
    if gc == cand.shape_pred:
        return False, 'shape_does_not_discriminate'
    return True, f'shape={mc}(p={cand.shape_prob:.3f}>={cand.shape_tau};google_p={cand.shape_google_prob:.3f})'


def _with_variant(dec: 'Decision', cand: Candidate, rule: str) -> 'Decision':
    """Attach the lexicon-neutral flag and the ink-decisive verdict (mark rules only, never changes accept)."""
    if cand.diff is not None and cand.diff.kind == 'marks' and rule in MARK_RULES + ('final_grave', 'constraint'):
        dec.lexicon_neutral = lexicon_neutral(cand)
        if dec.lexicon_neutral and not dec.accept and not dec.reason.startswith(('excluded', 'abstain')):
            ok, why = ink_decisive_verdict(cand, rule)
            dec.ink_decisive, dec.ink_decisive_reason = ok, why
    return dec


def decide(cand: Candidate, policy: str = 'strict') -> Decision:
    return _with_variant(_decide(cand, policy), cand, (cand.diff and rule_for(cand.diff)) or 'none')


def _decide(cand: Candidate, policy: str = 'strict') -> Decision:
    if policy not in POLICIES:
        raise ValueError(policy)
    d = cand.diff if cand.diff is not None else classify_diff(cand.google_core, cand.model_core)
    cand.diff = d
    if d is None:
        return Decision('none', False, 'excluded:no_single_allowed_difference', policy=policy)
    why = guard(cand)
    rule = rule_for(d)
    if why:
        return Decision(rule, False, 'excluded:' + why, policy=policy)
    if rule in MARK_RULES + ('final_grave',) and (is_all_caps(cand.google_core) or is_all_caps(cand.model_core)):
        return Decision(rule, False, 'excluded:all_caps_marks', policy=policy)
    if cand.regime_uncertain:
        return Decision(rule, False, 'abstain:regime_uncertain', policy=policy)
    if cand.regime == 'mono' and d.kind == 'marks' and any(c in POLY_ONLY for c in d.model):
        return Decision(rule, False, 'rejected:polytonic_mark_in_monotonic_regime', policy=policy)
    if rule == 'final_grave':
        ok, why = ink_verdict(cand, rule)
        return Decision(rule, ok, why, None, ok, policy)
    lex_ok, lex_why = lexicon_verdict(cand, rule, policy)
    if d.kind == 'marks' and cand.google_violations and not cand.model_violations and cand.regime != 'mono':
        # rule `constraint`: Google's form is impossible under the hard orthographic constraints and
        # the model's form is possible -> no lexicon needed; the ink conjunction for the mark still is
        ink_ok, ink_why = ink_verdict(cand, rule if rule in MARK_RULES else 'accent')
        reason = ('accepted;' if ink_ok else 'rejected;') + 'violates:' + '+'.join(cand.google_violations) + ';' + ink_why
        return Decision('constraint', ink_ok, reason, lex_ok, ink_ok, policy, base_rule=rule)
    if rule in ('base_sub', 'final_sigma'):
        if lex_ok and cand.google_key_freq >= ATTESTED_MIN:
            # Google's letters spell an attested word under other marks: the disagreement may be a
            # mark error that a base-letter change would turn into a different word; no ink is
            # consulted for base letters, so abstain
            return Decision(rule, False, f'abstain:google_letters_attested_with_other_marks({cand.google_key_freq})',
                            lex_ok, None, policy)
        return Decision(rule, lex_ok, lex_why, lex_ok, None, policy)
    ink_ok, ink_why = ink_verdict(cand, rule)
    accept = lex_ok and ink_ok
    reason = ('accepted;' if accept else 'rejected;') + lex_why + ';' + ink_why
    return Decision(rule, accept, reason, lex_ok, ink_ok, policy)


def apply_correction(google_token_text: str, lead: str, core: str, trail: str, model_core: str) -> str:
    """The corrected token: Google's punctuation around the model's core."""
    return lead + model_core + trail
