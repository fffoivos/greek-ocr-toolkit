"""Reachability census for the owner's design (lexicon proposes, ink decides, model only locates).

    python -m greekocr.labelfix.reach --seed 0 --seed 1 --out docs/labelfix/spellcheck

Text only (no crops, no ink): for every Google mark error the human text reveals on the three-way
Wikisource lines, the earliest stage of the owner's design that could reach it, and for every Google
word that is CORRECT, whether the same stages would propose a change (the load the ink must reject).

Stages, in order (the first that applies wins):
  guard         the word is excluded by policy (Latin/digits, all caps, hyphen line end, abbreviation,
                capitalised non-initial word)
  constraint    Google's form violates a hard orthographic constraint and the human form does not
  grave         Google writes an acute on the final syllable where the human writes a grave, and
                another word follows on the line (positional; deterministic)
  lex_unique    Google's form is unattested (< ATTESTED_MIN) and the human form is the ONLY attested
                one-cluster mark variant
  lex_compete   Google's form is unattested, the human form is one of several attested variants
  lex_miss      Google's form is unattested but the human form is not among the one-cluster proposals
                (two clusters differ, or the human form is unattested)
  real_word     Google's form is attested and so is the human form (needs the ink to contradict Google)
  human_unatt   Google's form is attested, the human form is not (out of reach of a lexicon design)
The model's reading is recorded only to split each class by "model also wrong".
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from .candidates import pair_tokens
from .constraints import violations
from .lexicon import ATTESTED_MIN, load_all
from .spellink import guard_reason, proposals
from .text import ACCENTS, clusters, lower_word, nfc, nfd, strip_marks, tokenize
from .validate import TOOLKIT, load_three_way

STAGES = ('human_error', 'guard', 'constraint', 'grave', 'grave_line_end', 'lex_unique', 'lex_compete', 'lex_miss',
          'real_word', 'human_unatt')
REACH = ('constraint', 'grave', 'grave_line_end', 'lex_unique', 'lex_compete', 'real_word')
HOLD = ('lex_unique',)
ACUTE, GRAVE = '́', '̀'


def final_acute_to_grave(g: str, h: str) -> bool:
    cg, ch = clusters(nfd(g)), clusters(nfd(h))
    if len(cg) != len(ch):
        return False
    diffs = [i for i, (a, b) in enumerate(zip(cg, ch)) if (a.base, a.marks) != (b.base, b.marks)]
    if len(diffs) != 1:
        return False
    i = diffs[0]
    bearers = [k for k, c in enumerate(cg) if any(m in ACCENTS for m in c.marks) or c.base.lower() in 'αεηιουω']
    return (bearers and i == bearers[-1] and cg[i].marks.replace(ACUTE, GRAVE) == ch[i].marks
            and ACUTE in cg[i].marks)


def final_grave_form(core: str) -> str:
    """The word with its final-syllable acute written grave (the form it takes before another word)."""
    cl = clusters(nfd(core))
    acc = [i for i, c in enumerate(cl) if ACUTE in c.marks]
    if len(acc) != 1 or _final_accent(core) != ACUTE:
        return nfd(core)
    i = acc[0]
    return ''.join(c.base + (c.marks.replace(ACUTE, GRAVE) if k == i else c.marks) for k, c in enumerate(cl))


def written_freq(core: str, lex) -> int:
    """N1: a final acute and a final grave are the same lexical form (position decides; the grave stage owns it)."""
    return max(lex.freq(core), lex.freq(final_grave_form(core)))


def only_grave_or_rho(a: str, b: str) -> bool:
    """N1/N2: the two forms differ only by final acute<->grave, or only by a breathing on an initial rho."""
    a, b = lower_word(nfd(a)), lower_word(nfd(b))
    if final_grave_form(a) == final_grave_form(b) or a.replace(GRAVE, ACUTE) == b.replace(GRAVE, ACUTE):
        return True
    if a[:1] == 'ρ' and b[:1] == 'ρ' and strip_rho(a) == strip_rho(b):
        return True
    return False


def strip_rho(w: str) -> str:
    return 'ρ' + w[1:].lstrip('\u0313\u0314')


def spell_props(core: str, lex, nxt):
    """spellink.proposals with N1 (acute/grave positional) and N2 (initial-rho breathing optional) applied."""
    if written_freq(core, lex) >= ATTESTED_MIN and not violations(core, nxt, hard_only=True):
        return [], 'attested'
    props, why = proposals(core, lex, nxt)
    props = [p for p in props if not only_grave_or_rho(core, p.form)]
    return props, why


def regimes(seed: int) -> dict:
    out = {}
    for line in open(TOOLKIT / f'docs/labelfix/validation_lines_s{seed}.jsonl', encoding='utf-8'):
        r = json.loads(line)
        out[r['line_id']] = r['regime']
    return out


def mark_kind(g: str, h: str) -> str:
    cg, ch = clusters(nfd(g)), clusters(nfd(h))
    if len(cg) != len(ch):
        return 'multi'
    diffs = [(a.marks, b.marks) for a, b in zip(cg, ch) if a.marks != b.marks]
    if len(diffs) != 1:
        return 'multi'
    a, b = diffs[0]
    ch_ = set(a) ^ set(b)
    names = {'\u0313': 'breathing', '\u0314': 'breathing', '\u0301': 'accent', '\u0300': 'accent', '\u0342': 'accent',
             '\u0345': 'subscript', '\u0308': 'dialytika'}
    return '+'.join(sorted({names.get(c, 'other') for c in ch_}))


def classify(g, h, gt, lex, is_last):
    nxt = gt[g.index + 1].core if g.index + 1 < len(gt) else None
    if violations(h.core, nxt, hard_only=True) and not violations(g.core, nxt, hard_only=True):
        return 'human_error', 'human form impossible', []
    if guard_reason(g, is_last):
        return 'guard', guard_reason(g, is_last), []
    if violations(g.core, nxt, hard_only=True) and not violations(h.core, nxt, hard_only=True):
        return 'constraint', '', []
    if final_acute_to_grave(g.core, h.core):
        if nxt is not None and not g.trail.strip():
            return 'grave', '', []
        if nxt is None and not g.trail.strip():
            return 'grave_line_end', 'word continues on the next line', []
        return 'real_word', 'acute->grave before punctuation', []
    written = written_freq(g.core, lex)
    props, why = spell_props(g.core, lex, nxt)
    forms = [lower_word(nfd(p.form)) for p in props]
    hl = lower_word(nfd(h.core))
    if written < ATTESTED_MIN:
        if hl in forms:
            return ('lex_unique' if len(forms) == 1 else 'lex_compete'), why, forms
        return 'lex_miss', why, forms
    if written_freq(h.core, lex) >= ATTESTED_MIN:
        return 'real_word', '', forms
    return 'human_unatt', '', forms


def census(seed: int, lexicons: dict) -> dict:
    reg = regimes(seed)
    errors, correct_load, hold_fp = [], Counter(), []
    n_correct = 0
    for l in load_three_way(seed):
        regime = reg.get(l['line_id'])
        if regime is None or regime == 'mono':
            continue
        lex = lexicons[regime]
        gt = tokenize(l['google'])
        hum = dict((g.index, h) for g, h in pair_tokens(l['google'], l['human']))
        mod = dict((g.index, m) for g, m in pair_tokens(l['google'], l['model']))
        for g in gt:
            if not g.core:
                continue
            h = hum.get(g.index)
            if h is None:
                continue
            is_last = g.index == len(gt) - 1
            if g.core == h.core:
                n_correct += 1
                nxt = gt[g.index + 1].core if g.index + 1 < len(gt) else None
                if guard_reason(g, is_last):
                    continue
                if written_freq(g.core, lex) < ATTESTED_MIN:
                    props, _ = spell_props(g.core, lex, nxt)
                    if props:
                        correct_load['lex_proposes_on_correct_word'] += 1
                        if len(props) == 1:
                            correct_load['lex_unique_on_correct_word'] += 1
                            hold_fp.append(dict(line_id=l["line_id"], word_index=g.index, google=nfc(g.core), proposal=nfc(props[0].form),
                                                count=props[0].count, google_count=lex.freq(g.core)))
                if final_acute_or_grave_line_end(g, gt, is_last):
                    correct_load['acute_final_line_end_correct'] += 1
                if acute_final_midline(g, gt):
                    correct_load['acute_final_midline_correct'] += 1
                if violations(g.core, nxt, hard_only=True):
                    correct_load['constraint_flags_correct_word'] += 1
                continue
            if strip_marks(nfd(g.core)) != strip_marks(nfd(h.core)):
                continue   # base-letter errors are not this tool's
            m = mod.get(g.index)
            stage, why, forms = classify(g, h, gt, lex, is_last)
            errors.append(dict(line_id=l['line_id'], doc=l['doc'], word_index=g.index, google=nfc(g.core),
                               human=nfc(h.core), model=nfc(m.core) if m else None,
                               model_right=bool(m is not None and m.core == h.core), stage=stage, why=why,
                               proposals=[nfc(f) for f in forms], regime=regime, kind=mark_kind(g.core, h.core),
                               google_count=lex.freq(g.core), human_count=lex.freq(h.core)))
    return dict(seed=seed, errors=errors, n_correct=n_correct, correct_load=dict(correct_load), hold_fp=hold_fp)


def _final_accent(core: str) -> str | None:
    cl = clusters(nfd(core))
    acc = [(i, m) for i, c in enumerate(cl) for m in c.marks if m in ACCENTS]
    if len(acc) != 1:
        return None
    i, m = acc[0]
    later = [c for c in cl[i + 1:] if c.base.lower() in 'αεηιουω']
    if later and not (len(later) == 1 and i + 1 < len(cl) and cl[i].base.lower() + later[0].base.lower() in
                      ('αι', 'ει', 'οι', 'υι', 'αυ', 'ευ', 'ηυ', 'ου')):
        return None
    return m


def final_acute_or_grave_line_end(g, gt, is_last) -> bool:
    """A correct Google word with a final-syllable ACUTE at the line end, no punctuation (where the grave rule
    would wrongly fire if the word does not continue / the print keeps the acute)."""
    return is_last and not g.trail.strip() and _final_accent(g.core) == ACUTE


def acute_final_midline(g, gt) -> bool:
    return g.index + 1 < len(gt) and not g.trail.strip() and _final_accent(g.core) == ACUTE


def table(res: dict) -> list[str]:
    errs = res['errors']
    by = defaultdict(Counter)
    kinds = defaultdict(Counter)
    for e in errs:
        kinds[e['stage']][e['kind']] += 1
        by[e['stage']]['model_right' if e['model_right'] else 'model_wrong'] += 1
    n = len(errs)
    he = sum(by['human_error'].values())
    nn = n - he
    out = [f"### Seed {res['seed']}: {n} Google mark errors (human differs from Google in marks only); "
           f"{he} are human-text errors, universe {nn}", '',
           '| stage | all | % of universe | model right | model also wrong | HOLD-reachable | mark kinds |',
           '|---|---:|---:|---:|---:|---:|---|']
    for s in STAGES:
        c = by[s]
        t = c['model_right'] + c['model_wrong']
        pc = '' if s == 'human_error' else f'{100 * t / max(1, nn):.1f}%'
        hold = t if s in HOLD else 0
        k = ', '.join(f'{a} {b}' for a, b in kinds[s].most_common())
        out.append(f"| {s} | {t} | {pc} | {c['model_right']} | {c['model_wrong']} | {hold} | {k} |")
    reach = sum(sum(by[s].values()) for s in REACH)
    mw = sum(1 for e in errs if not e['model_right'] and e['stage'] != 'human_error')
    mw_reach = sum(by[s]['model_wrong'] for s in REACH)
    hold = sum(sum(by[s].values()) for s in HOLD)
    cl = res['correct_load']
    out += ['', f"Reachable in principle ({' + '.join(REACH)}): {reach} of {nn} ({100 * reach / max(1, nn):.1f}%); "
            f"of the {mw} the model also gets wrong: {mw_reach} ({100 * mw_reach / max(1, mw):.1f}%).",
            f"Reachable when the image is ambiguous (HOLD: Google unattested, the human form the unique attested "
            f"one-cluster variant): {hold} ({100 * hold / max(1, nn):.1f}%).",
            f"Load on the {res['n_correct']} correct Google words: lexicon proposes on "
            f"{cl.get('lex_proposes_on_correct_word', 0)} (unique proposal, i.e. HOLD would fire wrongly: "
            f"{cl.get('lex_unique_on_correct_word', 0)}); hard constraints flag {cl.get('constraint_flags_correct_word', 0)}; "
            f"final acute kept correctly mid-line before a word: {cl.get('acute_final_midline_correct', 0)}, "
            f"at the line end without punctuation: {cl.get('acute_final_line_end_correct', 0)} "
            f"(the grave rule must not fire on these: acute-everywhere prints and words that end the sentence).",
            f"HOLD text-only precision on this set: {hold} right vs {cl.get('lex_unique_on_correct_word', 0)} wrong "
            f"= {100 * hold / max(1, hold + cl.get('lex_unique_on_correct_word', 0)):.1f}% before any ink.", '']
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed', type=int, action='append', default=None)
    ap.add_argument('--out', type=Path, default=TOOLKIT / 'docs/labelfix/spellcheck')
    ap.add_argument('--lexicons', type=Path, default=TOOLKIT / 'docs/labelfix/lexicons')
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    lexicons = load_all(a.lexicons)
    lines = ['# Reachability census (text only)', '', __doc__.split('\n\n', 1)[1], '']
    for seed in a.seed or [0, 1]:
        res = census(seed, lexicons)
        with open(a.out / f'reach_s{seed}.jsonl', 'w', encoding='utf-8') as fh:
            for e in res['errors']:
                fh.write(json.dumps(e, ensure_ascii=False) + '\n')
        with open(a.out / f'hold_fp_s{seed}.jsonl', 'w', encoding='utf-8') as fh:
            for e in res['hold_fp']:
                fh.write(json.dumps(e, ensure_ascii=False) + '\n')
        lines += table(res)
    (a.out / 'reach.md').write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
