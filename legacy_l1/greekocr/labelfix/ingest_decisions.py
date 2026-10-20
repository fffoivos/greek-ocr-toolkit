"""Ingest the owner's deck decisions (`labelfix_decisions*.json` from the deck's download button).

    python -m greekocr.labelfix.ingest_decisions --deck docs/labelfix/review_deck \
        [--decisions ~/Downloads/labelfix_decisions.json] --out docs/labelfix

Without `--decisions` the newest `~/Downloads/labelfix_decisions*.json` is used. The file is
copied to `<out>/owner_decisions_<date>.json` and `<out>/owner_review_summary.md` is written:
per rule, cards shown / y / n / u; precision (with the exact 95 % lower bound) on the cards
that showed the correction; false-yes rate on negative controls; agreement on positive controls;
u-rate; and the five most common patterns among the `u` cards.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import datetime as dt
import glob
import json
import os
from pathlib import Path
import shutil

from .text import classify_diff, nfc, nfd, split_token
from .validate import lb95

DOWNLOADS = Path.home() / 'Downloads'


def find_decisions(decisions_dir: Path | None = None) -> Path | None:
    """Newest downloaded decisions file (the server-captured jsonl is read separately)."""
    files = sorted(glob.glob(str(DOWNLOADS / 'labelfix_decisions*.json')), key=os.path.getmtime)
    return Path(files[-1]) if files else None


def load_decisions(src: Path | None, decisions_dir: Path | None) -> tuple[list, list[str]]:
    """Merge every source: server-captured jsonl (newest record per card wins), Firefox pulls and
    downloaded json in `decisions_dir`, and the explicit/downloaded file. Later sources override."""
    merged: dict = {}
    used = []
    if decisions_dir and Path(decisions_dir).exists():
        from .deck_serve import read_decisions
        rows = read_decisions(decisions_dir)
        if rows:
            used.append(f'{decisions_dir}/*.jsonl ({len(rows)} records)')
        for r in rows:
            merged[r['id']] = r
        for path in sorted(glob.glob(str(Path(decisions_dir) / '*.json')), key=os.path.getmtime):
            rows = json.loads(Path(path).read_text())
            used.append(f'{path} ({len(rows)})')
            for r in rows:
                if r.get('decision') and r['id'] not in merged:
                    merged[r['id']] = r
    if src is not None and Path(src).exists():
        rows = json.loads(Path(src).read_text())
        used.append(f'{src} ({len(rows)})')
        for r in rows:
            if r.get('decision'):
                merged[r['id']] = r
    return list(merged.values()), used


def load_deck(deck_dir: Path) -> dict:
    data = json.loads((Path(deck_dir) / 'deck_data.js').read_text().split('=', 1)[1].rstrip(';\n'))
    return {c['id']: c for b in data['batches'] for c in b['cards']}


def pattern(card: dict) -> str:
    """What kind of change the card asked about: mark categories and the two cluster readings."""
    _, g, _ = split_token(nfd(card['google']))
    _, m, _ = split_token(nfd(card['model']))
    d = classify_diff(g, m)
    if d is None:
        return f"{card['rule']}: {card['google']} vs {card['model']}"
    cats = '+'.join(sorted(d.categories)) if d.categories else d.kind
    return f"{card['rule']}: {cats} {nfc(d.google)}→{nfc(d.model)}"


def summarise(cards: dict, decisions: list) -> tuple[dict, list[str]]:
    per = defaultdict(lambda: dict(shown=0, y=0, n=0, u=0, corr_y=0, corr_n=0, corr_u=0, label_y=0, label_n=0, label_u=0,
                                   neg_y=0, neg_n=0, neg_u=0, pos_y=0, pos_n=0, pos_u=0))
    u_patterns = Counter()
    unknown = 0
    for d in decisions:
        c = cards.get(d.get('id'))
        if c is None:
            unknown += 1
            continue
        if d.get('line_id') not in (None, c['line_id']) or d.get('word_index') not in (None, c['word_index']):
            unknown += 1
            continue
        v = d.get('decision')
        if v not in ('y', 'n', 'u'):
            continue
        r = per[c['rule']]
        r['shown'] += 1
        r[v] += 1
        kind = c['kind']
        if kind == 'neg':
            r['neg_' + v] += 1
        elif kind == 'pos':
            r['pos_' + v] += 1
        elif c['shown_is_model']:
            r['corr_' + v] += 1
        else:
            r['label_' + v] += 1
        if v == 'u':
            u_patterns[pattern(c)] += 1
    lines = ['# Owner review of the label-correction deck', '',
             f'Decisions ingested: {sum(r["shown"] for r in per.values())} (ignored: {unknown} with an unknown or mismatching card id).', '',
             '| rule | cards answered | y | n | u | u-rate | correction cards (y / n / u) | precision | LB95 | label-shown (y / n / u) | negative controls false-yes / n / u | positive controls y / n / u |',
             '|---|---:|---:|---:|---:|---:|---|---:|---:|---|---|---|']
    for rule, r in per.items():
        k, n = r['corr_y'], r['corr_y'] + r['corr_n']
        prec = f'{100 * k / n:.1f}%' if n else '-'
        lines.append(f"| {rule} | {r['shown']} | {r['y']} | {r['n']} | {r['u']} | {100 * r['u'] / r['shown']:.0f}% | "
                     f"{r['corr_y']} / {r['corr_n']} / {r['corr_u']} | {prec} | {100 * lb95(k, n):.1f}% | "
                     f"{r['label_y']} / {r['label_n']} / {r['label_u']} | {r['neg_y']} / {r['neg_n']} / {r['neg_u']} | "
                     f"{r['pos_y']} / {r['pos_n']} / {r['pos_u']} |")
    lines += ['', 'Precision = y / (y + n) on cards that showed the proposed correction (u excluded); LB95 = exact one-sided '
              '95 % lower bound. A "y" on a label-shown card means the existing label was judged right. Negative controls '
              'show a reading the human transcription contradicts, so a "y" there is a false yes.', '',
              '## Most common patterns among `u` (uncertain / neither) cards', '']
    if u_patterns:
        lines.append('| pattern | u cards |')
        lines.append('|---|---:|')
        for pat, n in u_patterns.most_common(5):
            lines.append(f'| {pat} | {n} |')
    else:
        lines.append('No `u` decisions.')
    lines.append('')
    return dict(per), lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--deck', type=Path, required=True)
    ap.add_argument('--decisions', type=Path, default=None)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--date', default=dt.date.today().strftime('%Y%m%d'))
    ap.add_argument('--decisions-dir', type=Path, default=None, help='server-captured jsonl dir (default <out>/decisions)')
    a = ap.parse_args(argv)
    ddir = a.decisions_dir or (a.out / 'decisions')
    src = a.decisions or find_decisions()
    decisions, used = load_decisions(src, ddir)
    if not decisions:
        print(f'OWNER_REVIEW: pending (no decisions in {ddir}, no labelfix_decisions*.json in ~/Downloads)')
        return 3
    cards = load_deck(a.deck)
    a.out.mkdir(parents=True, exist_ok=True)
    copy = a.out / f'owner_decisions_{a.date}.json'
    copy.write_text(json.dumps(decisions, ensure_ascii=False, indent=1))
    per, lines = summarise(cards, decisions)
    lines.insert(2, 'Sources: ' + '; '.join(used) + '.')
    (a.out / 'owner_review_summary.md').write_text('\n'.join(lines))
    print(f'OWNER_REVIEW: present ({len(decisions)} decisions from {len(used)} source(s) -> {copy}); rules: '
          + ', '.join(f"{r} {v['shown']}" for r, v in per.items()))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
