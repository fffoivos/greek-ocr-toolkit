"""Validation of the correction rules on the three-way Wikisource lines (human / Google / model).

    python -m greekocr.labelfix.validate --seed 0 --seed 1 --out docs/labelfix

For every Greek line of the `wikisource_human` instrument we have the human transcription
(truth), Google's label (the training label) and the recogniser's reading; the crop is the
same. Candidates are generated exactly as for training labels and every accepted correction
is checked against the human text.

Book separation: thresholds (mark-shape, lexicon margins) were set while inspecting lines of
three books (DEV_BOOKS); the report shows the dev subset, the held-out books and both.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import time

from PIL import Image

from .candidates import LineContext, acute_house_style, line_candidates, pair_tokens
from .ctc_align import Alignment, Recognizer
from .ink import analyse
from .lexicon import choose_regime, load_all
from .rules import RULES, rule_for
from .constraints import violations
from .text import classify_diff, nfc, nfd, tokenize

HOME = Path.home()
PAGE_OCR = HOME / 'Projects' / 'greek-page-ocr'
PRED_DIR = PAGE_OCR / 'out' / 'e3b' / 'predictions'
CKPT = {0: PAGE_OCR / 'out/e3b/jobA/runs/full_s0/best.pt', 1: PAGE_OCR / 'out/e3b/jobA/runs/full_s1/best.pt'}
TOOLKIT = Path(__file__).resolve().parents[2]
TEST_JSONL = TOOLKIT / 'docs/harvest/collection/v2/import_real_v2_test.jsonl'
DEV_BOOKS = ('wikisource:8b6b0de9', 'wikisource:02a3a2a6', 'wikisource:2793d64c')
RULE_ORDER = list(RULES)


def lb95(k: int, n: int) -> float:
    """Exact one-sided 95 % lower confidence bound on a binomial proportion (Clopper-Pearson)."""
    if n == 0:
        return 0.0
    if k == 0:
        return 0.0
    from scipy.stats import beta
    return float(beta.ppf(0.05, k, n - k + 1))


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def load_three_way(seed: int) -> list[dict]:
    test = {}
    for line in open(TEST_JSONL, encoding='utf-8'):
        r = json.loads(line)
        test[r['id']] = r
    v2 = {}
    for line in open(PRED_DIR / f'full_s{seed}_v2_test.jsonl', encoding='utf-8'):
        r = json.loads(line)
        v2[r['line_id']] = r
    out = []
    for line in open(PRED_DIR / f'full_s{seed}_wikisource_human.jsonl', encoding='utf-8'):
        h = json.loads(line)
        if h['source_dataset'] != 'wikisource_el':
            continue
        k = h['line_id'][:-len('-human')]
        g, t = v2[k], test[k]
        out.append(dict(line_id=k, google=nfd(g['gt']), model=nfd(h['prediction']), model_v2=nfd(g['prediction']),
                        human=nfd(h['gt'].lstrip(':').strip()), crop=str(TOOLKIT / t['crop']), wave=t['wave'],
                        doc=t['doc'], script_class=g['script_class'], seed=seed, year=t.get('year')))
    return out


def alignments_for(lines: list[dict], seed: int, cache_dir: Path, threads: int = 4, log=print) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f'align_s{seed}.jsonl'
    have = {}
    if cache.exists():
        for line in open(cache, encoding='utf-8'):
            r = json.loads(line)
            have[r['crop']] = Alignment.from_record(r['alignment'])
    missing = sorted({l['crop'] for l in lines} - set(have))
    if missing:
        rec = Recognizer(CKPT[seed], threads=threads)
        log(f'[validate] seed {seed}: aligning {len(missing)} crops with {rec.ckpt_path}')
        new = rec.align_paths(missing, bs=16, log=log)
        with open(cache, 'a', encoding='utf-8') as fh:
            for crop, al in new.items():
                fh.write(json.dumps(dict(crop=crop, alignment=al.to_record()), ensure_ascii=False) + '\n')
        have.update(new)
    return have


def page_of(line_id: str) -> str:
    return line_id.rsplit('-l', 1)[0]


def truth_map(google: str, human: str) -> dict:
    """Google word index -> human token (or None) through the character alignment."""
    return {g.index: h for g, h in pair_tokens(google, human)}


def line_props(ink, width: int) -> dict:
    xh = ink.xh
    comps = ink.components
    return dict(clipped=bool(ink.ink[0].any() or ink.ink[-1].any()),
                specks=sum(1 for c in comps if c.role in ('punct', 'fragment') and c.area < 0.05 * xh * xh) >= 3,
                faint_ink=sum(1 for c in comps if c.darkness > ink.faint_cut and c.area >= 12) >= 3,
                neighbour_ink=any(c.role == 'neighbour' for c in comps),
                long=width > 1200)


def direction_of(d: dict) -> str:
    if d['kind'] == 'base':
        return 'base'
    g, m = nfd(d['google']), nfd(d['model'])
    ng, nm = sum(1 for c in g if ord(c) >= 0x300), sum(1 for c in m if ord(c) >= 0x300)
    return 'add' if nm > ng else 'remove' if nm < ng else 'change'


def evaluate_lines(lines: list[dict], lexicons: dict, aligns: dict, policy: str, log=print, shape_model=None) -> tuple[list, list]:
    """Returns (candidate records with truth, per-line records)."""
    # document-level regime: majority of the per-line choices
    per_line = {}
    for l in lines:
        toks = tokenize(l['google'])
        regime, _ = choose_regime(l['script_class'], [t.core for t in toks if t.core], lexicons, (l['google'], l['model']))
        per_line[l['line_id']] = regime
    votes = defaultdict(Counter)
    for l in lines:
        votes[l['doc']][per_line[l['line_id']]] += 1
    doc_regime = {d: c.most_common(1)[0][0] for d, c in votes.items()}
    pages = defaultdict(list)
    for l in lines:
        pages[page_of(l['line_id'])].append(l['google'])
    page_style = {p: acute_house_style(g) for p, g in pages.items()}
    cands, linerecs = [], []
    t0 = time.time()
    for n, l in enumerate(lines):
        im = Image.open(l['crop'])
        ink = analyse(im)
        al = aligns[l['crop']]
        style = page_style[page_of(l['line_id'])]
        ctx = LineContext(l['line_id'], l['google'], l['model'], l['script_class'], l['wave'], l['crop'], al, ink,
                          regime_override=doc_regime[l['doc']], acute_style=style[0], shape_model=shape_model,
                          extra=dict(doc=l['doc'], seed=l['seed'], dev=l['doc'] in DEV_BOOKS,
                                     page_acute_share=round(style[1], 2), page_accented_words=style[2]))
        props = line_props(ink, im.size[0])
        truth = truth_map(l['google'], l['human'])
        recs = line_candidates(ctx, lexicons, policy)
        for c in recs:
            h = truth.get(c['word_index'])
            c['human_token'] = h.text if h else None
            c['human_nfc'] = nfc(h.text) if h else None
            if h is None:
                outcome = 'unknown'
            elif h.core == c['model_core']:
                outcome = 'correct'            # correction equals the human text
            elif h.core == c['google_core']:
                outcome = 'google_right'       # correction would introduce an error
            else:
                outcome = 'both_wrong'         # human differs from both readings
            c['outcome'] = outcome
            c['stratum'] = ('model=human' if outcome == 'correct' else 'google=human' if outcome == 'google_right'
                            else 'all_different' if outcome == 'both_wrong' else 'unknown')
            c['direction'] = direction_of(c['diff'])
            if h is not None:
                c['edit_benefit'] = levenshtein(c['google_core'], h.core) - levenshtein(c['model_core'], h.core)
            else:
                c['edit_benefit'] = 0
            c['line_props'] = props
            c['n_words_bucket'] = '<=3' if c['n_words'] <= 3 else '4-7' if c['n_words'] <= 7 else '>=8'
            cands.append(c)
        # recoverable Google errors (truth universe for recall): Google token != human token, single allowed diff
        recoverable = []
        for g, h in pair_tokens(l['google'], l['human']):
            if h is None or g.core == h.core:
                continue
            d = classify_diff(g.core, h.core)
            if d is None:
                continue
            mt = {gg.index: mm for gg, mm in pair_tokens(l['google'], l['model'])}
            m = mt.get(g.index)
            recoverable.append(dict(word_index=g.index, rule=rule_for(d), google=nfc(g.core), human=nfc(h.core),
                                    model=nfc(m.core) if m else None, model_right=(m is not None and m.core == h.core)))
        census = []
        if doc_regime[l['doc']] != 'mono':
            gt_toks = tokenize(l['google'])
            mt = {g.index: m for g, m in pair_tokens(l['google'], l['model'])}
            for g in gt_toks:
                if not g.core:
                    continue
                nxt = gt_toks[g.index + 1].core if g.index + 1 < len(gt_toks) else None
                gv = violations(g.core, nxt)
                if not gv:
                    continue
                m = mt.get(g.index)
                h = truth.get(g.index)
                census.append(dict(word_index=g.index, google=nfc(g.core), violations=gv,
                                   model=nfc(m.core) if m else None,
                                   model_possible=(m is not None and not violations(m.core, nxt)),
                                   human=nfc(h.core) if h else None,
                                   human_possible=(h is not None and not violations(h.core, nxt)),
                                   google_eq_human=(h is not None and h.core == g.core),
                                   model_eq_human=(m is not None and h is not None and m.core == h.core)))
        linerecs.append(dict(line_id=l['line_id'], doc=l['doc'], seed=l['seed'], dev=l['doc'] in DEV_BOOKS,
                             constraint_census=census,
                             regime=doc_regime[l['doc']], google_eq_model=l['google'] == l['model'],
                             google_eq_human=l['google'] == l['human'], model_eq_human=l['model'] == l['human'],
                             n_words=len(tokenize(l['google'])), recoverable=recoverable, props=props,
                             n_candidates=len(recs), n_accepted=sum(1 for c in recs if c['decision']['accept'])))
        if log and n % 200 == 0:
            log(f'[validate] {n}/{len(lines)} lines ({time.time() - t0:.0f}s)')
    return cands, linerecs


# ----------------------------------------------------------------------------- reporting

def pct(k, n):
    return f'{100 * k / n:.1f}%' if n else '-'


def precision_row(cs: list) -> dict:
    acc = [c for c in cs if c['decision']['accept']]
    known = [c for c in acc if c['outcome'] != 'unknown']
    k = sum(1 for c in known if c['outcome'] == 'correct')
    fp = sum(1 for c in known if c['outcome'] == 'google_right')
    bw = sum(1 for c in known if c['outcome'] == 'both_wrong')
    benefit = sum(c['edit_benefit'] for c in known)
    return dict(candidates=len(cs), accepted=len(acc), known=len(known), correct=k, google_right=fp, both_wrong=bw,
                precision=(k / len(known)) if known else None, lb95=lb95(k, len(known)), net_benefit=benefit,
                abstained=sum(1 for c in cs if c['decision']['reason'].startswith('abstain')),
                rejected=sum(1 for c in cs if not c['decision']['accept'] and not c['decision']['reason'].startswith(('abstain', 'excluded'))),
                excluded=sum(1 for c in cs if c['decision']['reason'].startswith('excluded')))


def ablation_accept(c: dict, mode: str) -> bool:
    d = c['decision']
    if d['reason'].startswith('excluded'):
        return False
    if mode == 'model_only':
        return True
    if mode == 'model+lexicon':
        return d['lexicon_ok'] if d['lexicon_ok'] is not None else d['accept']
    if mode == 'model+ink':
        return d['ink_ok'] if d['ink_ok'] is not None else d['accept']
    return d['accept']


def ablation_row(cs: list, mode: str) -> dict:
    acc = [c for c in cs if ablation_accept(c, mode) and c['outcome'] != 'unknown']
    k = sum(1 for c in acc if c['outcome'] == 'correct')
    return dict(accepted=len(acc), correct=k, precision=(k / len(acc)) if acc else None, lb95=lb95(k, len(acc)),
                net_benefit=sum(c['edit_benefit'] for c in acc))


def fmt_row(r: dict) -> str:
    p = '-' if r['precision'] is None else f"{100 * r['precision']:.1f}%"
    return (f"{r['candidates']} | {r['excluded']} | {r['abstained']} | {r['rejected']} | {r['accepted']} | "
            f"{r['correct']} | {r['google_right']} | {r['both_wrong']} | {p} | {100 * r['lb95']:.1f}% | {r['net_benefit']:+d}")


HEADER = ('| rule | candidates | excluded | abstained | rejected | accepted | = human | Google right (FP) | human ≠ both | '
          'precision | LB95 | net edits |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|')


def by_rule_table(cs: list, title: str) -> list[str]:
    out = [f'### {title}', '', HEADER]
    for rule in RULE_ORDER + ['none']:
        sub = [c for c in cs if c['decision']['rule'] == rule]
        if not sub:
            continue
        out.append(f'| {rule} | ' + fmt_row(precision_row(sub)) + ' |')
    out.append(f'| **all** | ' + fmt_row(precision_row(cs)) + ' |')
    out.append('')
    return out


def group_table(cs: list, key, title: str, label: str) -> list[str]:
    out = [f'### {title}', '', f'| {label} | rule | accepted | = human | FP | precision | LB95 | net edits |',
           '|---|---|---:|---:|---:|---:|---:|---:|']
    groups = defaultdict(list)
    for c in cs:
        groups[key(c)].append(c)
    for g in sorted(groups, key=lambda v: str(v)):
        for rule in RULE_ORDER:
            sub = [c for c in groups[g] if c['decision']['rule'] == rule and c['decision']['accept']]
            if not sub:
                continue
            r = precision_row(sub)
            p = '-' if r['precision'] is None else f"{100 * r['precision']:.1f}%"
            out.append(f"| {g} | {rule} | {r['accepted']} | {r['correct']} | {r['google_right']} | {p} | {100 * r['lb95']:.1f}% | {r['net_benefit']:+d} |")
    out.append('')
    return out


def recall_table(cands: list, linerecs: list, title: str) -> list[str]:
    out = [f'### {title}', '', '| rule (Google→human diff) | recoverable Google errors | recovered (TP) | FP (accepted, ≠ human) | recall | precision |',
           '|---|---:|---:|---:|---:|---:|']
    universe = Counter()
    recovered = Counter()
    accepted_keys = {(c['line_id'], c['word_index']) for c in cands if c['decision']['accept'] and c['outcome'] == 'correct'}
    for l in linerecs:
        for r in l['recoverable']:
            universe[r['rule']] += 1
            if (l['line_id'], r['word_index']) in accepted_keys:
                recovered[r['rule']] += 1
    fps = Counter(c['decision']['rule'] for c in cands if c['decision']['accept'] and c['outcome'] == 'google_right')
    for rule in RULE_ORDER:
        if universe[rule] == 0 and fps[rule] == 0:
            continue
        tp = recovered[rule]
        out.append(f"| {rule} | {universe[rule]} | {tp} | {fps[rule]} | {pct(tp, universe[rule])} | {pct(tp, tp + fps[rule])} |")
    out.append(f"| **all** | {sum(universe.values())} | {sum(recovered.values())} | {sum(fps.values())} | "
               f"{pct(sum(recovered.values()), sum(universe.values()))} | {pct(sum(recovered.values()), sum(recovered.values()) + sum(fps.values()))} |")
    out.append('')
    return out


def verdicts(cs: list) -> dict:
    """Release-candidate test per rule: LB95 >= 99 %, positive net benefit, no regime with >= 2 FP."""
    out = {}
    for rule in RULE_ORDER:
        sub = [c for c in cs if c['decision']['rule'] == rule]
        if not sub:
            continue
        r = precision_row(sub)
        fp_by_regime = Counter(c['regime'] for c in sub if c['decision']['accept'] and c['outcome'] == 'google_right')
        systematic = [reg for reg, n in fp_by_regime.items() if n >= 2]
        ok = r['lb95'] >= 0.99 and r['net_benefit'] > 0 and not systematic
        out[rule] = dict(release_candidate=ok, lb95=r['lb95'], net_benefit=r['net_benefit'], accepted=r['accepted'],
                         systematic_failure_regimes=systematic)
    return out


def write_report(out: Path, results: dict, policies: tuple) -> dict:
    """results[(seed, policy)] = (cands, linerecs). Returns summary for REPORT.md."""
    L = ['# Validation on the three-way Wikisource lines', '',
         'Truth = the human Wikisource transcription; label = Google Document AI; reading = our recogniser '
         '(E3 `full` arm, seeds 0 and 1, same crops). A candidate is a Google word the model reads differently '
         'with a single allowed difference. `accepted` = the pipeline would rewrite the label. '
         'Outcome of an accepted correction: `= human` (correct), `Google right` (a false correction, the label '
         'was right), `human ≠ both` (the label was wrong but so is the correction).', '',
         'LB95 = exact one-sided 95 % lower confidence bound on precision (Clopper–Pearson; 90/100 → 83.6 %, '
         '99/100 → 95.3 %, 100/100 → 97.1 %). Net edits = Levenshtein edits removed minus edits introduced over '
         'accepted corrections (word cores, NFD codepoints). A rule is a **release candidate** only if '
         'LB95 ≥ 99 % AND net edits > 0 AND no regime has ≥ 2 false corrections; otherwise it is '
         '**proposal-only**.', '',
         f'Book separation: thresholds were set while inspecting lines of {len(DEV_BOOKS)} books (dev): '
         f'{", ".join(DEV_BOOKS)}. "held-out" = all other books.', '']
    summary = {}
    for (seed, policy), (cands, linerecs) in sorted(results.items()):
        L += [f'## Seed {seed}, lexicon policy `{policy}`', '']
        n_lines = len(linerecs)
        L += [f'Lines: {n_lines} (dev {sum(1 for l in linerecs if l["dev"])}, held-out {sum(1 for l in linerecs if not l["dev"])}); '
              f'Google = model on {sum(1 for l in linerecs if l["google_eq_model"])} lines (agreement control: of those, '
              f'{sum(1 for l in linerecs if l["google_eq_model"] and not l["google_eq_human"])} still differ from the human text '
              f'and are unreachable by this method); Google = human on {sum(1 for l in linerecs if l["google_eq_human"])}; '
              f'model = human on {sum(1 for l in linerecs if l["model_eq_human"])}.', '',
              f'Candidates: {len(cands)}; truth known for {sum(1 for c in cands if c["outcome"] != "unknown")} '
              f'(the human line could not be word-aligned for the rest).', '']
        for subset, name in ((lambda c: True, 'all books'), (lambda c: c['dev'], 'dev books'),
                             (lambda c: not c['dev'], 'held-out books')):
            cs = [c for c in cands if subset(c)]
            L += by_rule_table(cs, f'Per rule — {name}')
        held = [c for c in cands if not c['dev']]
        v = verdicts(held)
        L += ['### Release-candidate verdicts (held-out books)', '', '| rule | accepted | LB95 | net edits | systematic failure | verdict |',
              '|---|---:|---:|---:|---|---|']
        for rule, r in v.items():
            L.append(f"| {rule} | {r['accepted']} | {100 * r['lb95']:.1f}% | {r['net_benefit']:+d} | "
                     f"{', '.join(r['systematic_failure_regimes']) or 'none'} | "
                     f"{'RELEASE CANDIDATE' if r['release_candidate'] else 'proposal-only'} |")
        L.append('')
        summary[(seed, policy)] = dict(verdicts=v, all=precision_row(cands), held=precision_row(held),
                                       by_rule={r: precision_row([c for c in held if c['decision']['rule'] == r]) for r in RULE_ORDER},
                                       by_rule_all={r: precision_row([c for c in cands if c['decision']['rule'] == r]) for r in RULE_ORDER})
        # ablations
        L += ['### Ablations (all books; accepted = known-truth candidates passing the stage)', '',
              '| rule | stage | accepted | = human | precision | LB95 | net edits |', '|---|---|---:|---:|---:|---:|---:|']
        for rule in RULE_ORDER + ['all']:
            sub = cands if rule == 'all' else [c for c in cands if c['decision']['rule'] == rule]
            if not sub:
                continue
            for mode in ('model_only', 'model+lexicon', 'model+ink', 'full'):
                r = ablation_row(sub, mode)
                p = '-' if r['precision'] is None else f"{100 * r['precision']:.1f}%"
                L.append(f"| {rule} | {mode} | {r['accepted']} | {r['correct']} | {p} | {100 * r['lb95']:.1f}% | {r['net_benefit']:+d} |")
        L.append('')
        # agreement-rate table: lexicon alone / ink alone / both vs human, over mark candidates with both verdicts
        both = [c for c in cands if c['decision']['lexicon_ok'] is not None and c['decision']['ink_ok'] is not None
                and c['outcome'] in ('correct', 'google_right')]
        L += ['### Agreement with the human text (mark rules with both verdicts; outcome known as model-right or Google-right)', '',
              '| witness says "model" | n | model = human | Google = human | agreement |', '|---|---:|---:|---:|---:|']
        for name, sel in (('lexicon alone', lambda c: c['decision']['lexicon_ok']),
                          ('ink alone', lambda c: c['decision']['ink_ok']),
                          ('lexicon AND ink', lambda c: c['decision']['lexicon_ok'] and c['decision']['ink_ok']),
                          ('neither (lexicon no, ink no)', lambda c: not c['decision']['lexicon_ok'] and not c['decision']['ink_ok'])):
            s = [c for c in both if sel(c)]
            k = sum(1 for c in s if c['outcome'] == 'correct')
            L.append(f'| {name} | {len(s)} | {k} | {len(s) - k} | {pct(k, len(s))} |')
        L.append('')
        L += recall_table(cands, linerecs, 'Per-mark recovery (TP / FP / recall), all books')
        L += ['### Reader-agreement strata (all candidates, by rule)', '', '| rule | model = human | Google = human | all different | unknown | accepted: model = human | accepted: Google = human | accepted: all different |',
              '|---|---:|---:|---:|---:|---:|---:|---:|']
        for rule in RULE_ORDER:
            sub = [c for c in cands if c['decision']['rule'] == rule]
            if not sub:
                continue
            s = Counter(c['stratum'] for c in sub)
            a = Counter(c['stratum'] for c in sub if c['decision']['accept'])
            L.append(f"| {rule} | {s['model=human']} | {s['google=human']} | {s['all_different']} | {s['unknown']} | "
                     f"{a['model=human']} | {a['google=human']} | {a['all_different']} |")
        L.append('')
        L += group_table(cands, lambda c: c['direction'], 'Accepted corrections by direction', 'direction')
        L += group_table(cands, lambda c: c['regime'], 'Accepted corrections by regime', 'regime')
        L += group_table(cands, lambda c: c['doc'], 'Accepted corrections by book', 'book')
        L += group_table(cands, lambda c: c['n_words_bucket'], 'Accepted corrections by line length (words)', 'words')
        # abstention reasons
        L += ['### Abstention and rejection reasons (all candidates)', '', '| reason | n | of which model = human | Google = human |', '|---|---:|---:|---:|']
        reasons = Counter()
        mh = Counter()
        gh = Counter()
        for c in cands:
            if c['decision']['accept']:
                continue
            key = c['decision']['reason']
            key = key.split('(')[0]
            if key.startswith(('accepted;', 'rejected;')):
                parts = [p.split('(')[0] for p in c['decision']['reason'].split(';')[1:]]
                key = ' + '.join(p for p in parts if not p.startswith(('google_form_unattested', 'margin_ok', 'count_matches', 'mark_present', 'slope_agrees', 'below=', 'dots_match', 'model=')))
            reasons[key] += 1
            mh[key] += c['outcome'] == 'correct'
            gh[key] += c['outcome'] == 'google_right'
        for key, n in reasons.most_common():
            L.append(f'| {key} | {n} | {mh[key]} | {gh[key]} |')
        L.append('')
        # physical negative controls
        L += ['### Physical controls (candidates on lines with the property)', '',
              '| property | lines | candidates | accepted | = human | Google right (FP) |', '|---|---:|---:|---:|---:|---:|']
        for prop in ('clipped', 'specks', 'faint_ink', 'neighbour_ink', 'long'):
            nl = sum(1 for l in linerecs if l['props'][prop])
            sub = [c for c in cands if c['line_props'][prop]]
            acc = [c for c in sub if c['decision']['accept']]
            L.append(f"| {prop} | {nl} | {len(sub)} | {len(acc)} | {sum(1 for c in acc if c['outcome'] == 'correct')} | "
                     f"{sum(1 for c in acc if c['outcome'] == 'google_right')} |")
        L.append('')
        # pass 4: ink-decisive variant on lexicon-neutral candidates (separate column, never folded into accept)
        neutral = [c for c in cands if c['decision'].get('lexicon_neutral')]
        idc = [c for c in cands if c['decision'].get('ink_decisive')]
        L += ['### Ink-decisive variant (lexicon-neutral candidates; `markshape_model.json`, tau = 99 % held-out precision)', '',
              f'Lexicon-neutral mark candidates: {len(neutral)}; ink-decisive among them: {len(idc)}.', '',
              '| rule | lexicon-neutral | ink_decisive | = human | Google right (FP) | human ≠ both | precision | LB95 | net edits |',
              '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for rule in RULE_ORDER + ['all']:
            nn = neutral if rule == 'all' else [c for c in neutral if c['decision']['rule'] == rule]
            dd = idc if rule == 'all' else [c for c in idc if c['decision']['rule'] == rule]
            if not nn:
                continue
            k = sum(1 for c in dd if c['outcome'] == 'correct')
            fp = sum(1 for c in dd if c['outcome'] == 'google_right')
            bw = sum(1 for c in dd if c['outcome'] == 'both_wrong')
            known = k + fp + bw
            L.append(f"| {rule} | {len(nn)} | {len(dd)} | {k} | {fp} | {bw} | {pct(k, known)} | {100 * lb95(k, known):.1f}% | "
                     f"{sum(c['edit_benefit'] for c in dd):+d} |")
        # reasons why neutral candidates were not decisive
        why = Counter(c['decision']['ink_decisive_reason'].split('(')[0] for c in neutral if not c['decision']['ink_decisive'])
        L += ['', 'Why lexicon-neutral candidates were not ink-decisive: ' + ', '.join(f'{k} {n}' for k, n in why.most_common()) + '.', '']
        # recall with the variant
        acc_keys = {(c['line_id'], c['word_index']) for c in cands if c['decision']['accept'] and c['outcome'] == 'correct'}
        idc_keys = {(c['line_id'], c['word_index']) for c in idc if c['outcome'] == 'correct'}
        universe = [(l['line_id'], r) for l in linerecs for r in l['recoverable']]
        rec_base = sum(1 for lid, r in universe if (lid, r['word_index']) in acc_keys)
        rec_total = sum(1 for lid, r in universe if (lid, r['word_index']) in acc_keys | idc_keys)
        L += [f'Recall of the {len(universe)} recoverable Google mark errors: rules {rec_base} ({pct(rec_base, len(universe))}); '
              f'rules + ink_decisive {rec_total} ({pct(rec_total, len(universe))}).', '']
        # ceiling analysis
        cand_by_key = {(c['line_id'], c['word_index']): c for c in cands}
        ceil = Counter()
        for lid, r in universe:
            c = cand_by_key.get((lid, r['word_index']))
            if not r['model_right']:
                ceil['model wrong (unreachable without a better model)'] += 1
                continue
            if c is None:
                ceil['model right, not a candidate (pairing / multi-difference)'] += 1
                continue
            d = c['decision']
            if d['accept']:
                ceil['model right, accepted by the rules'] += 1
            elif d['reason'].startswith('excluded'):
                ceil['model right, excluded by a guard'] += 1
            elif d['reason'].startswith('abstain'):
                ceil['model right, abstained (ink unreadable / regime)'] += 1
            elif d.get('lexicon_neutral'):
                ceil['model right, lexicon neutral, ink decisive' if d.get('ink_decisive') else 'model right, lexicon neutral, ink not decisive'] += 1
            elif d['lexicon_ok'] is False:
                ceil['model right, lexicon contradicts'] += 1
            else:
                ceil['model right, ink conjunction fails'] += 1
        L += ['### Ceiling analysis of the recoverable Google mark errors', '', '| class | n | share |', '|---|---:|---:|']
        for k, n in ceil.most_common():
            L.append(f'| {k} | {n} | {pct(n, len(universe))} |')
        L.append('')
        summary[(seed, policy)]['ink_decisive'] = dict(neutral=len(neutral), decisive=len(idc),
                                                       correct=sum(1 for c in idc if c['outcome'] == 'correct'),
                                                       fp=sum(1 for c in idc if c['outcome'] == 'google_right'),
                                                       recall_rules=rec_base, recall_total=rec_total, universe=len(universe), ceiling=dict(ceil))
        # policy defaults 3a / 3b
        li = [c for c in cands if c.get('line_initial_allowed')]
        li_acc = [c for c in li if c['decision']['accept']]
        pages_flagged = {page_of(c['line_id']) for c in cands if c.get('acute_style')}
        sup = [c for c in cands if 'abstain:acute_house_style' in c['decision']['reason']]
        L += ['### Policy defaults (3a line-initial capitals, 3b acute house style)', '',
              f'3a: line-initial capitalised words admitted (lower-cased model form attested ≥ 50, not in the proper-name list): '
              f'{len(li)} candidates, {len(li_acc)} accepted, {sum(1 for c in li_acc if c["outcome"] == "correct")} = human, '
              f'{sum(1 for c in li_acc if c["outcome"] == "google_right")} Google right.', '',
              f'3b: pages flagged as acute-everywhere (share of word-final acute > 0.8 over ≥ 10 accented final syllables in the '
              f'Google text): {len(pages_flagged)} pages carrying {sum(1 for c in cands if c.get("acute_style"))} candidates; '
              f'final_grave corrections suppressed on them: {len(sup)} ({sum(1 for c in sup if c["outcome"] == "correct")} would have '
              f'matched the human text, {sum(1 for c in sup if c["outcome"] == "google_right")} would have been false).', '']
        # orthographic constraints
        cen = [x for l in linerecs for x in l['constraint_census']]
        n_words = sum(l['n_words'] for l in linerecs if l['regime'] != 'mono')
        con = [c for c in cands if c['decision']['rule'] == 'constraint']
        con_acc = [c for c in con if c['decision']['accept']]
        overlap = sum(1 for c in con_acc if c['decision']['lexicon_ok'])
        L += ['### Orthographic constraints (polytonic-regime lines; `constraints.py`)', '',
              f'Google words checked: {n_words}; violating a hard constraint: {len(cen)} '
              f'({pct(len(cen), n_words)}); of those, the human form is itself impossible (constraint too strict or '
              f'human error): {sum(1 for x in cen if x["human"] is not None and not x["human_possible"])}; Google = human '
              f'although "impossible": {sum(1 for x in cen if x["google_eq_human"])}; the model\'s form is possible: '
              f'{sum(1 for x in cen if x["model_possible"])}, of which model = human: '
              f'{sum(1 for x in cen if x["model_possible"] and x["model_eq_human"])}.', '',
              '| violation | Google words | model possible | model = human | Google = human |', '|---|---:|---:|---:|---:|']
        by_v = Counter()
        mp, mh, gh = Counter(), Counter(), Counter()
        for x in cen:
            for v in x['violations']:
                by_v[v] += 1
                mp[v] += x['model_possible']
                mh[v] += x['model_possible'] and x['model_eq_human']
                gh[v] += x['google_eq_human']
        for v, n in by_v.most_common():
            L.append(f'| {v} | {n} | {mp[v]} | {mh[v]} | {gh[v]} |')
        r = precision_row(con)
        p = '-' if r['precision'] is None else f"{100 * r['precision']:.1f}%"
        L += ['', f"Rule `constraint` (single allowed mark difference, Google impossible, model possible, ink agrees): "
              f"candidates {r['candidates']}, accepted {r['accepted']}, = human {r['correct']}, Google right {r['google_right']}, "
              f"human ≠ both {r['both_wrong']}, precision {p}, LB95 {100 * r['lb95']:.1f}%, net edits {r['net_benefit']:+d}; "
              f"overlap with the lexicon rules: {overlap} of the {len(con_acc)} accepted would also pass the lexicon "
              f"(the other {len(con_acc) - overlap} are corrections the lexicon alone could not make).", '']
        by_base = Counter(c['decision']['base_rule'] for c in con_acc)
        if by_base:
            L.append('Accepted by underlying mark category: ' + ', '.join(f'{k} {v}' for k, v in by_base.most_common()) + '.')
            L.append('')
        # false corrections listed
        fps = [c for c in cands if c['decision']['accept'] and c['outcome'] != 'correct']
        L += [f'### Accepted corrections that do not match the human text ({len(fps)})', '',
              '| rule | book | Google | proposed | human | crop |', '|---|---|---|---|---|---|']
        for c in fps:
            L.append(f"| {c['decision']['rule']} | {c['doc']} | {c['google_nfc']} | {c['corrected_nfc']} | {c['human_nfc']} | "
                     f"`{Path(c['crop_path']).relative_to(TOOLKIT)}` |")
        L.append('')
    L += ['## Typeface class', '', 'Not derivable: the prediction records carry `font_style_unknown` for every real line; '
          'the only per-line grouping available is the book (above). All lines are from the `wikisource` wave.', '']
    (out / 'validation_wikisource.md').write_text('\n'.join(L))
    return summary


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed', type=int, action='append', default=None)
    ap.add_argument('--policy', action='append', default=None)
    ap.add_argument('--out', type=Path, default=TOOLKIT / 'docs/labelfix')
    ap.add_argument('--cache-dir', type=Path, required=True)
    ap.add_argument('--lexicons', type=Path, default=TOOLKIT / 'docs/labelfix/lexicons')
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--limit', type=int, default=None)
    ap.add_argument('--shape-model', type=Path, default=TOOLKIT / 'docs/labelfix/markshape_model.json')
    a = ap.parse_args(argv)
    shape_model = None
    if a.shape_model and a.shape_model.exists():
        from .markshape import load_model
        shape_model = load_model(a.shape_model)
    seeds = a.seed or [0, 1]
    policies = tuple(a.policy or ('strict', 'ratio'))
    a.out.mkdir(parents=True, exist_ok=True)
    lexicons = load_all(a.lexicons)
    results = {}
    for seed in seeds:
        lines = load_three_way(seed)
        if a.limit:
            lines = lines[:a.limit]
        aligns = alignments_for(lines, seed, a.cache_dir, a.threads)
        for policy in policies:
            cands, linerecs = evaluate_lines(lines, lexicons, aligns, policy, shape_model=shape_model)
            results[(seed, policy)] = (cands, linerecs)
            with open(a.out / f'validation_candidates_s{seed}_{policy}.jsonl', 'w', encoding='utf-8') as fh:
                for c in cands:
                    fh.write(json.dumps(c, ensure_ascii=False) + '\n')
            with open(a.out / f'validation_lines_s{seed}.jsonl', 'w', encoding='utf-8') as fh:
                for l in linerecs:
                    fh.write(json.dumps(l, ensure_ascii=False) + '\n')
    summary = write_report(a.out, results, policies)
    (a.out / 'validation_summary.json').write_text(json.dumps({f'{k[0]}_{k[1]}': v for k, v in summary.items()}, indent=1, default=str))
    for k, v in summary.items():
        print(k, {r: (round(x['lb95'], 3), x['accepted'], x['net_benefit']) for r, x in v['verdicts'].items()})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
