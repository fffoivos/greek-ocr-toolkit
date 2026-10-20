"""Collect unambiguous vowel samples from the three-way lines, fit and calibrate the mark-shape classifier.

    python -m greekocr.labelfix.markshape_train --cache-dir <scratch> --out docs/labelfix

Writes `markshape_samples.jsonl.gz` (features + class + book), `markshape_model.json` (weights, tau)
and `markshape_report.md` (held-out accuracy, per-class recall/precision, confusion, threshold).
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import gzip
import json
from pathlib import Path

import numpy as np
from PIL import Image

from .candidates import pair_tokens
from .ink import analyse, mark_evidence
from .markshape import FEATURES, SoftmaxModel, calibrate, features, fit, fit_mlp, mark_class
from .text import VOWELS, clusters, nfd
from .validate import DEV_BOOKS, TOOLKIT, alignments_for, load_three_way


def collect(lines: list[dict], aligns: dict, log=print) -> list[dict]:
    out = []
    for n, l in enumerate(lines):
        al = aligns.get(l['crop'])
        if al is None or nfd(al.prediction) != l['model']:
            from .ctc_align import transfer_alignment
            if al is None:
                continue
            al = transfer_alignment(l['model'], al)
        ink = analyse(Image.open(l['crop']))
        gm = {g.index: m for g, m in pair_tokens(l['google'], l['model'])}
        gh = {g.index: h for g, h in pair_tokens(l['google'], l['human'])}
        for g, m in gm.items():
            h = gh.get(g)
            if m is None or h is None:
                continue
            gt = [t for t in __import__('greekocr.labelfix.text', fromlist=['tokenize']).tokenize(l['google']) if t.index == g][0]
            if not (gt.core and gt.core == m.core == h.core):
                continue
            cw = al.char_width()
            for cl in clusters(m.core):
                if cl.base not in VOWELS:
                    continue
                label = mark_class(cl.marks)
                if label is None:
                    continue
                bi = m.core_start + cl.start
                bx0, bx1 = al.window(bi, bi + 1)
                cx0, cx1 = al.window(bi, m.core_start + cl.end)
                ev = mark_evidence(ink, min(bx0, cx0) - cw, max(bx1, cx1) + cw, core_x0=bx0, core_x1=bx1)
                if ev.body_source != 'letter' or ev.n_letters_in_span != 1:
                    continue   # the classifier is only ever asked about well-localised vowels
                out.append(dict(line_id=l['line_id'], doc=l['doc'], dev=l['doc'] in DEV_BOOKS, word=m.core, base=cl.base,
                                label=label, x=features(ev)))
        if log and n % 300 == 0:
            log(f'[markshape] {n}/{len(lines)} lines, {len(out)} samples')
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, default=TOOLKIT / 'docs/labelfix')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--min-class', type=int, default=15, help='classes rarer than this are dropped from the scheme')
    a = ap.parse_args(argv)
    lines = load_three_way(a.seed)
    aligns = alignments_for(lines, a.seed, a.cache_dir)
    samples = collect(lines, aligns)
    counts = Counter(s['label'] for s in samples)
    classes = sorted(c for c, n in counts.items() if n >= a.min_class)
    samples = [s for s in samples if s['label'] in classes]
    with gzip.open(a.out / 'markshape_samples.jsonl.gz', 'wt', encoding='utf-8') as fh:
        for s in samples:
            fh.write(json.dumps(s, ensure_ascii=False) + '\n')
    dev = [s for s in samples if s['dev']]
    held = [s for s in samples if not s['dev']]
    Xd, yd = [s['x'] for s in dev], [s['label'] for s in dev]
    Xh, yh = [s['x'] for s in held], [s['label'] for s in held]
    lin = fit(Xd, yd, classes)
    cal_lin = calibrate(lin, Xh, yh)
    mlp = fit_mlp(Xd, yd, classes)
    cal_mlp = calibrate(mlp, Xh, yh)
    model, cal = (mlp, cal_mlp) if cal_mlp['accuracy'] >= cal_lin['accuracy'] else (lin, cal_lin)
    cal_dev = calibrate(model, Xd, yd)
    model.tau = cal['threshold']['tau'] if cal['threshold'] else 1.0
    model.meta = dict(n_dev=len(dev), n_held=len(held), classes=classes, counts=dict(counts), dev_books=list(DEV_BOOKS),
                      held_out=cal, dev_fit=dict(accuracy=cal_dev['accuracy']),
                      softmax_held_out=dict(accuracy=cal_lin['accuracy'], threshold=cal_lin['threshold']),
                      mlp_held_out=dict(accuracy=cal_mlp['accuracy'], threshold=cal_mlp['threshold']),
                      chosen='mlp' if model is mlp else 'softmax')
    model.save(a.out / 'markshape_model.json')
    # confusion on held-out
    P = model.probs([s['x'] for s in held])
    pred = [classes[i] for i in P.argmax(axis=1)]
    conf = Counter((s['label'], p) for s, p in zip(held, pred))
    L = ['# Mark-shape classifier (ink-decisive variant)', '',
         f'Samples: vowels of words where Google = human = model on the three-way lines (seed {a.seed} alignments), '
         f'well-localised only: {len(samples)} ({len(dev)} dev-book, {len(held)} held-out-book); classes with ≥ {a.min_class} '
         f'samples: {len(classes)}.', '',
         f'{len(FEATURES)} features (counts, sizes, slope, elongation, hook, skew, position + two 8×8 shape thumbnails). '
         f'Softmax regression: held-out accuracy {100 * cal_lin["accuracy"]:.1f} %; one-hidden-layer MLP (96 tanh units, Adam, '
         f'class-balanced): held-out accuracy {100 * cal_mlp["accuracy"]:.1f} %. Chosen: **{model.meta["chosen"]}** '
         f'(dev-fit accuracy {100 * cal_dev["accuracy"]:.1f} %, **held-out accuracy {100 * cal["accuracy"]:.1f} %**).', '']
    t = cal['threshold']
    if t:
        L.append(f'**Confidence threshold tau = {t["tau"]}**: on held-out samples, predictions with p ≥ tau are {100 * t["precision"]:.2f} % '
                 f'correct and cover {100 * t["coverage"]:.1f} % of the samples ({t["n"]}).')
    else:
        L.append('No threshold reaches 99 % precision on the held-out samples.')
    L += ['', '| tau | held-out predictions with p ≥ tau | precision |', '|---|---:|---:|']
    for r in cal['curve']:
        L.append(f"| {r['tau']} | {r['n']} | {'-' if r['precision'] is None else f'{100 * r[chr(112)+chr(114)+chr(101)+chr(99)+chr(105)+chr(115)+chr(105)+chr(111)+chr(110)]:.2f}%'} |")
    L += ['', 'Mark-vs-mark only (truth and prediction both carry a mark; the mark ↔ none confusions are the extractor losing a blob, '
          'which the removal abstentions guard separately):', '', '| tau | n | precision |', '|---|---:|---:|']
    for r in cal['marks_only']:
        L.append(f"| {r['tau']} | {r['n']} | {'-' if r['precision'] is None else f'{100 * r[chr(112)+chr(114)+chr(101)+chr(99)+chr(105)+chr(115)+chr(105)+chr(111)+chr(110)]:.2f}%'} |")
    L += ['', '| class | samples (all) | held-out n | recall (argmax) | precision at tau | n at tau |', '|---|---:|---:|---:|---:|---:|']
    for c in classes:
        pc = cal['per_class'].get(c)
        if pc:
            prec = '-' if pc['precision_at_tau'] is None else f'{100 * pc["precision_at_tau"]:.1f}%'
            L.append(f'| {c} | {counts[c]} | {pc["n"]} | {100 * pc["recall"]:.1f}% | {prec} | {pc["n_at_tau"]} |')
    L += ['', '## Held-out confusion (truth → predicted, counts ≥ 2)', '', '| truth | predicted | n |', '|---|---|---:|']
    for (tr, pr), n in sorted(conf.items(), key=lambda kv: -kv[1]):
        if tr != pr and n >= 2:
            L.append(f'| {tr} | {pr} | {n} |')
    L.append('')
    (a.out / 'markshape_report.md').write_text('\n'.join(L))
    print(json.dumps(dict(samples=len(samples), classes=classes, held_out=cal['accuracy'], threshold=t)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
