"""Build the three regime lexicons and write docs/records/labelfix/lexicon_report.md.

    python -m greekocr.labelfix.build_lexicon --raw-dir ~/Projects/greek-page-ocr/data/raw \
        --out docs/records/labelfix/lexicons --exclude-eval docs/records/harvest/collection/v2/import_real_v2_test.jsonl \
        --exclude-human ~/Projects/greek-page-ocr/out/e3b/predictions/full_s0_wikisource_human.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from .lexicon import EXCLUDED_SOURCES, REGIMES, SOURCES, build_regime, shingles
from .text import lexicon_key

DEFAULT_CAPS = {'ancient': 400_000, 'poly19': None, 'mono': 400_000}


def work_stems(exclude_eval: list[Path]) -> set:
    """Title stems of held-out Wikisource works, from the eval records' source_url
    (…/wiki/Σελίδα:<title>.djvu/<page>): mark-stripped, lower-cased, >= 12 characters."""
    from urllib.parse import unquote
    stems = set()
    for path in exclude_eval:
        for line in open(path, encoding='utf-8'):
            r = json.loads(line)
            url = r.get('source_url') or ''
            if 'wikisource' not in url or '/wiki/' not in url:
                continue
            title = unquote(url.split('/wiki/', 1)[1]).split(':', 1)[-1]
            for ext in ('.djvu', '.pdf'):
                title = title.split(ext)[0]
            stem = lexicon_key(title.replace('_', ' ')).strip()
            if len(stem) >= 12:
                stems.add(stem)
    return stems


def eval_shingles(exclude_eval: list[Path], exclude_human: list[Path]) -> tuple[set, dict]:
    out: set = set()
    counts = {}
    for path in exclude_eval:
        n = 0
        for line in open(path, encoding='utf-8'):
            r = json.loads(line)
            out |= shingles(r['label'])
            n += 1
        counts[str(path)] = n
    for path in exclude_human:
        n = 0
        for line in open(path, encoding='utf-8'):
            r = json.loads(line)
            out |= shingles(r['gt'].lstrip(':'))
            n += 1
        counts[str(path)] = n
    return out, counts


def write_report(out_dir: Path, lexicons: dict, shingle_counts: dict, n_shingles: int, caps: dict,
                 stems: set = frozenset()) -> None:
    lines = ['# Lexicon report (labelfix)', '',
             'Built by `python -m greekocr.labelfix.build_lexicon`. Forms are NFD, lower-cased, edge punctuation',
             'stripped; all-caps words dropped; tokens with Latin letters or digits dropped. Only born-digital,',
             'human-typed or human-proofread text; no Google Document AI output and no recogniser output.',
             'Regime purity: polytonic regimes admit only lines that carry a polytonic-only mark (breathing,',
             'varia, perispomeni, ypogegrammeni); the monotonic regime admits only lines without one.', '',
             '## Held-out exclusion', '',
             f'Lines of a source that share a 4-word shingle with an evaluation line are excluded: {n_shingles} shingles',
             'from:', '']
    for p, n in shingle_counts.items():
        lines.append(f'- `{p}`: {n} lines')
    lines += ['', f'Whole works are excluded by title stem ({len(stems)} stems from the eval records\' Wikisource URLs):', '']
    lines += [f'- {s}' for s in sorted(stems)]
    lines += ['', '## Regimes and sources', '']
    lines.append('| regime | source | evidence of human provenance | lines read | lines used | excluded (held-out work) | excluded (eval overlap) | excluded (other regime) | tokens | cap |')
    lines.append('|---|---|---|---:|---:|---:|---:|---:|---:|---|')
    for r in REGIMES:
        lex = lexicons[r]
        for s in lex.meta['sources']:
            lines.append(f"| {r} | {s['name']} | {s['evidence']} | {s['lines_read']} | {s['lines_used']} | "
                         f"{s['lines_excluded_doc']} | {s['lines_excluded_overlap']} | {s['lines_excluded_regime']} | "
                         f"{s['tokens']} | {caps[r] or 'none'} |")
    lines += ['', '| regime | distinct forms | forms with count >= 5 | tokens | proper-name keys (>= 3 mid-sentence capitalised) |', '|---|---:|---:|---:|---:|']
    for r in REGIMES:
        m = lexicons[r].meta
        lines.append(f"| {r} | {m['forms']} | {m['forms_ge5']} | {m['tokens']} | {m.get('names_ge3', 0)} |")
    lines += ['', 'Lookup is inflection-aware: a form counts if it, its grave->acute variant, or (for two-accent words) the',
              'form without the enclitic-induced second accent is attested. Held-out ancient works excluded from the TEI',
              f'sources by id: {", ".join(__import__("greekocr.labelfix.lexicon", fromlist=["HELD_OUT_ANCIENT_IDS"]).HELD_OUT_ANCIENT_IDS)}.']
    lines += ['', '## Sources considered and excluded', '']
    for name, why in EXCLUDED_SOURCES:
        lines.append(f'- {name}: {why}')
    lines += ['', 'Source files live under `~/Projects/greek-page-ocr/data/raw/` (see `data/sources.json` there).', '']
    (out_dir.parent / 'lexicon_report.md').write_text('\n'.join(lines))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--exclude-eval', type=Path, nargs='*', default=[])
    ap.add_argument('--exclude-human', type=Path, nargs='*', default=[])
    ap.add_argument('--regimes', nargs='*', default=list(REGIMES))
    ap.add_argument('--cap', type=int, default=None, help='override the per-source line cap for every regime')
    ap.add_argument('--tei-dir', type=Path, default=None, help='directory with TEI-extracted *_lines.jsonl (tei_extract.py)')
    a = ap.parse_args(argv)
    caps = dict(DEFAULT_CAPS)
    if a.cap is not None:
        caps = {r: a.cap for r in REGIMES}
    t0 = time.time()
    excl, counts = eval_shingles(a.exclude_eval, a.exclude_human)
    stems = work_stems(a.exclude_eval)
    print(f'[lexicon] exclusion shingles: {len(excl)} from {sum(counts.values())} eval lines; '
          f'{len(stems)} held-out work stems ({time.time()-t0:.0f}s)', flush=True)
    a.out.mkdir(parents=True, exist_ok=True)
    lexicons = {}
    for r in a.regimes:
        lex = build_regime(r, a.raw_dir, exclude_shingles=excl, exclude_docs=stems, tei_dir=a.tei_dir, max_lines_per_source=caps[r],
                           log=lambda s: print(s, flush=True))
        lex.meta['held_out_work_stems'] = sorted(stems)
        lex.meta['cap_lines_per_source'] = caps[r]
        lex.meta['exclusion_shingles'] = len(excl)
        lex.save(a.out / f'{r}.tsv.gz')
        lexicons[r] = lex
        print(f'[lexicon] {r}: forms={lex.meta["forms"]} ge5={lex.meta["forms_ge5"]} tokens={lex.meta["tokens"]}', flush=True)
    if set(a.regimes) == set(REGIMES):
        write_report(a.out, lexicons, counts, len(excl), caps, stems)
    print(f'[lexicon] done in {time.time()-t0:.0f}s', flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
