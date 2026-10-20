"""Candidate run on a sample of training (or test) lines: model forward -> ink -> candidates.

    python -m greekocr.labelfix.sample --records docs/records/harvest/collection/v2/import_real_v2_train.jsonl \
        --n 5000 --out docs/records/labelfix/candidates_train_sample.jsonl --cache-dir <scratch>

Every candidate (accepted, abstained, rejected, excluded) is written with its evidence; the
summary (`.md` next to the output) counts candidates per rule per wave and projects accepted
corrections to the full training set.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import random
import time

from PIL import Image

from .candidates import LineContext, acute_house_style, line_candidates
from .ctc_align import Alignment, Recognizer
from .ink import analyse
from .lexicon import choose_regime, load_all
from .rules import RULES
from .text import nfd, tokenize
from .validate import CKPT, TOOLKIT, line_props, page_of

TRAIN_ROWS_AFTER_CODEC = 207_851   # E3 results: collection v2 train rows after codec


def load_records(path: Path, admitted_only: bool = True) -> list[dict]:
    out = []
    for line in open(path, encoding='utf-8'):
        r = json.loads(line)
        if admitted_only and r.get('admitted') is False:
            continue
        out.append(r)
    return out


def align_records(recs: list[dict], seed: int, cache_dir: Path, name: str, threads: int, log=print) -> dict:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = cache_dir / f'align_{name}_s{seed}.jsonl'
    have = {}
    if cache.exists():
        for line in open(cache, encoding='utf-8'):
            r = json.loads(line)
            have[r['crop']] = Alignment.from_record(r['alignment'])
    crops = [str(TOOLKIT / r['crop']) for r in recs]
    missing = sorted(set(crops) - set(have))
    if missing:
        rec = Recognizer(CKPT[seed], threads=threads)
        log(f'[sample] aligning {len(missing)} crops ({rec.ckpt_path})')
        new = rec.align_paths(missing, bs=16, log=log)
        with open(cache, 'a', encoding='utf-8') as fh:
            for crop, al in new.items():
                fh.write(json.dumps(dict(crop=crop, alignment=al.to_record()), ensure_ascii=False) + '\n')
        have.update(new)
    return have


def run(recs: list[dict], lexicons: dict, aligns: dict, policy: str = 'strict', log=print, shape_model=None) -> tuple[list, dict]:
    per_line = {}
    for r in recs:
        crop = str(TOOLKIT / r['crop'])
        if crop not in aligns:
            continue
        toks = tokenize(nfd(r['label']))
        regime, _ = choose_regime(r.get('script_class', ''), [t.core for t in toks if t.core], lexicons,
                                  (r['label'], aligns[crop].prediction))
        per_line[r['id']] = regime
    votes = defaultdict(Counter)
    for r in recs:
        if r['id'] in per_line:
            votes[r['doc']][per_line[r['id']]] += 1
    doc_regime = {d: c.most_common(1)[0][0] for d, c in votes.items()}
    pages = defaultdict(list)
    for r in recs:
        pages[page_of(r['id'])].append(nfd(r['label']))
    page_style = {p: acute_house_style(g) for p, g in pages.items()}
    cands = []
    stats = dict(lines=0, lines_with_candidates=0, lines_google_eq_model=0, skipped=0,
                 pages_acute_style=sum(1 for v in page_style.values() if v[0]), pages=len(page_style))
    t0 = time.time()
    for n, r in enumerate(recs):
        crop = str(TOOLKIT / r['crop'])
        if crop not in aligns:
            stats['skipped'] += 1
            continue
        al = aligns[crop]
        im = Image.open(crop)
        ink = analyse(im)
        style = page_style[page_of(r['id'])]
        ctx = LineContext(r['id'], r['label'], al.prediction, r.get('script_class', ''), r['wave'], crop, al, ink,
                          regime_override=doc_regime[r['doc']], acute_style=style[0], shape_model=shape_model,
                          extra=dict(doc=r['doc'], year=r.get('year'), split=r.get('split'), seed=0,
                                     page_acute_share=round(style[1], 2), page_accented_words=style[2]))
        stats['lines'] += 1
        if nfd(r['label']) == nfd(al.prediction):
            stats['lines_google_eq_model'] += 1
        props = line_props(ink, im.size[0])
        recs_out = line_candidates(ctx, lexicons, policy)
        for c in recs_out:
            c['line_props'] = props
            c['n_words_bucket'] = '<=3' if c['n_words'] <= 3 else '4-7' if c['n_words'] <= 7 else '>=8'
        if recs_out:
            stats['lines_with_candidates'] += 1
        cands.extend(recs_out)
        if log and n % 500 == 0:
            log(f'[sample] {n}/{len(recs)} lines, {len(cands)} candidates ({time.time() - t0:.0f}s)')
    return cands, stats


def summary_md(cands: list, stats: dict, sampled_by_wave: Counter, train_by_wave: Counter, n_train: int) -> str:
    L = ['# Candidate run on a training sample', '',
         f"Sampled lines: {stats['lines']} (random, seed 20261016, admitted rows of `import_real_v2_train.jsonl`); "
         f"Google = model on {stats['lines_google_eq_model']} lines; lines with at least one candidate: "
         f"{stats['lines_with_candidates']}; candidates: {len(cands)}; accepted: "
         f"{sum(1 for c in cands if c['decision']['accept'])}.", '',
         '## Candidates per rule per wave', '',
         '| rule | wave | sampled lines | candidates | accepted | abstained | rejected | excluded | accepted per 1000 lines | projected accepted in train wave |',
         '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    by = defaultdict(list)
    for c in cands:
        by[(c['decision']['rule'], c['wave'])].append(c)
    waves = sorted(sampled_by_wave)
    total_proj = Counter()
    for rule in list(RULES) + ['none']:
        for w in waves:
            cs = by.get((rule, w), [])
            if not cs:
                continue
            acc = sum(1 for c in cs if c['decision']['accept'])
            abst = sum(1 for c in cs if c['decision']['reason'].startswith('abstain'))
            exc = sum(1 for c in cs if c['decision']['reason'].startswith('excluded'))
            rej = len(cs) - acc - abst - exc
            rate = acc / sampled_by_wave[w] if sampled_by_wave[w] else 0
            proj = rate * train_by_wave[w]
            total_proj[rule] += proj
            L.append(f'| {rule} | {w} | {sampled_by_wave[w]} | {len(cs)} | {acc} | {abst} | {rej} | {exc} | '
                     f'{1000 * rate:.1f} | {proj:.0f} |')
    L += ['', '## Projection to the training set', '',
          f'Train records: {n_train} admitted rows (207,851 after codec per E3_RESULTS; the projection uses per-wave rates × '
          f'admitted rows per wave, then scales by {TRAIN_ROWS_AFTER_CODEC}/{n_train}).', '',
          '| rule | accepted in sample | projected accepted (full train) |', '|---|---:|---:|']
    scale = TRAIN_ROWS_AFTER_CODEC / max(1, n_train)
    for rule in RULES:
        acc = sum(1 for c in cands if c['decision']['rule'] == rule and c['decision']['accept'])
        L.append(f'| {rule} | {acc} | {total_proj[rule] * scale:.0f} |')
    acc_all = sum(1 for c in cands if c['decision']['accept'])
    L.append(f'| **all** | {acc_all} | {sum(total_proj.values()) * scale:.0f} |')
    li = [c for c in cands if c.get('line_initial_allowed')]
    L += ['', '## Policy defaults', '',
          f"3a line-initial capitalised words admitted: {len(li)} candidates, {sum(1 for c in li if c['decision']['accept'])} accepted. "
          f"3b acute-everywhere pages: {stats.get('pages_acute_style', 0)} of {stats.get('pages', 0)} sampled pages (note: a sampled page "
          f"usually has few lines, so the ≥ 10 accented-word floor rarely triggers here); final_grave suppressed on them: "
          f"{sum(1 for c in cands if 'abstain:acute_house_style' in c['decision']['reason'])}.", '']
    idc = [c for c in cands if c['decision'].get('ink_decisive')]
    L += ['', f"Ink-decisive variant (lexicon-neutral + mark-shape classifier at tau): {len(idc)} candidates "
          f"({', '.join(f'{k} {v}' for k, v in Counter(c['decision']['rule'] for c in idc).most_common())}); not folded into accepted.", '']
    L += ['', '## Outcomes by rule (all waves)', '', '| rule | candidates | accepted | abstained | rejected | excluded |', '|---|---:|---:|---:|---:|---:|']
    for rule in list(RULES) + ['none']:
        cs = [c for c in cands if c['decision']['rule'] == rule]
        if not cs:
            continue
        acc = sum(1 for c in cs if c['decision']['accept'])
        abst = sum(1 for c in cs if c['decision']['reason'].startswith('abstain'))
        exc = sum(1 for c in cs if c['decision']['reason'].startswith('excluded'))
        L.append(f'| {rule} | {len(cs)} | {acc} | {abst} | {len(cs) - acc - abst - exc} | {exc} |')
    L += ['', '## Abstention / rejection reasons', '', '| reason | n |', '|---|---:|']
    reasons = Counter()
    for c in cands:
        if c['decision']['accept']:
            continue
        key = c['decision']['reason']
        if key.startswith(('accepted;', 'rejected;')):
            parts = [p.split('(')[0] for p in key.split(';')[1:]]
            key = ' + '.join(p for p in parts if not p.startswith(('google_form_unattested', 'margin_ok', 'count_matches',
                                                                   'mark_present', 'slope_agrees', 'below=', 'dots_match', 'model=')))
        reasons[key.split('(')[0]] += 1
    for k, n in reasons.most_common():
        L.append(f'| {k} | {n} |')
    L.append('')
    return '\n'.join(L)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--records', type=Path, required=True)
    ap.add_argument('--n', type=int, default=5000)
    ap.add_argument('--seed', type=int, default=20261016)
    ap.add_argument('--ids', type=Path, default=None, help='file of line ids to use instead of a random sample')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--cache-dir', type=Path, required=True)
    ap.add_argument('--name', default='train')
    ap.add_argument('--lexicons', type=Path, default=TOOLKIT / 'docs/records/labelfix/lexicons')
    ap.add_argument('--policy', default='strict')
    ap.add_argument('--threads', type=int, default=4)
    ap.add_argument('--shape-model', type=Path, default=TOOLKIT / 'docs/records/labelfix/markshape_model.json')
    a = ap.parse_args(argv)
    shape_model = None
    if a.shape_model and a.shape_model.exists():
        from .markshape import load_model
        shape_model = load_model(a.shape_model)
    recs = load_records(a.records)
    train_by_wave = Counter(r['wave'] for r in recs)
    if a.ids:
        want = set(a.ids.read_text().split())
        chosen = [r for r in recs if r['id'] in want]
    else:
        chosen = random.Random(a.seed).sample(recs, a.n)
    lexicons = load_all(a.lexicons)
    aligns = align_records(chosen, 0, a.cache_dir, a.name, a.threads)
    cands, stats = run(chosen, lexicons, aligns, a.policy, shape_model=shape_model)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, 'w', encoding='utf-8') as fh:
        for c in cands:
            fh.write(json.dumps(c, ensure_ascii=False) + '\n')
    sampled_by_wave = Counter(r['wave'] for r in chosen)
    a.out.with_suffix('.md').write_text(summary_md(cands, stats, sampled_by_wave, train_by_wave, len(recs)))
    print(json.dumps(stats), 'accepted', sum(1 for c in cands if c['decision']['accept']))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
