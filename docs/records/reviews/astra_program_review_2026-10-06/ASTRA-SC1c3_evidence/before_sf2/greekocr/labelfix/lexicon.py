"""Per-regime word-frequency lexicons from proofread human text.

Three orthographic regimes:

    ancient  scholarly polytonic editions (First1KGreek, classical literature corpus)
    poly19   19th-20th c. polytonic katharevousa/demotic (Gutenberg el, Wikisource el)
    mono     monotonic modern Greek (Wikipedia/finewiki, EUR-Lex, Europarl)

What the builder admits: whitespace tokens of born-digital, human-typed text, punctuation
stripped at the edges, NFD, with their marks. All-caps words are dropped (in polytonic
print they carry no accents and would attest mark-less forms); initial capitals are
lower-cased. Tokens with Latin letters or digits are dropped. Nothing produced by Google
Document AI or by our recogniser is ever admitted. Lines that share a 4-word shingle with
an evaluation line (human transcription or Google label of a held-out test crop) are
excluded so the validation is not read back from the lexicon.

Storage: `<regime>.tsv.gz` with `form<TAB>count`, forms NFD lower-case.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import gzip
import json
from pathlib import Path
import time
from typing import Iterable, Iterator

from .text import (has_greek, has_latin_or_digit, is_all_caps, is_capitalised, lexicon_key, lower_word, nfd,
                   split_token, strip_marks)

REGIMES = ('ancient', 'poly19', 'mono')
ATTESTED_MIN = 5          # rule 1: the model's form must reach this count
RATIO_MIN = 20            # rule 1: Google's form at least this much rarer (marks)
RATIO_MIN_BASE = 50       # rule 3: base-letter changes need this margin

# Source catalogue: regime -> list of (name, path relative to the greek-page-ocr data/raw dir,
# human-provenance evidence). Only born-digital, human-typed or human-proofread text.
SOURCES = {
    'ancient': [
        ('first1k_greek', 'corpus_v4/nc_1000_prwta_xronia_ellhnikhs.jsonl',
         'OpenGreekAndLatin First1KGreek TEI editions (scholarly, corrected); CC-BY-SA-4.0'),
        ('klasikh_arx_ell_grammateia', 'corpus_v4/nc_klasikh_arx_ell_grammateia.jsonl',
         'classical Greek literature editions, born-digital; CC-BY-SA-4.0'),
        ('perseus_greeklit_tei', 'TEI:perseus_greeklit_lines.jsonl',
         'Perseus canonical-greekLit TEI body text @ 0189b9c8 (choice->sic/orig); CC-BY-SA-4.0'),
        ('first1k_greek_tei', 'TEI:first1k_greek_lines.jsonl',
         'First1KGreek TEI body text @ 03776b39 (choice->sic/orig); CC-BY-SA-4.0'),
    ],
    'poly19': [
        ('wikisource_el', 'wikisource_el_lines.jsonl',
         'Greek Wikisource human transcriptions (dump); CC-BY-SA'),
    ],
    'mono': [
        ('gutenberg_el', 'gutenberg_el_lines.jsonl',
         'Project Gutenberg Greek ebooks, Distributed Proofreaders human-keyed; PD-US; the copies on disk are '
         'monotonic transcriptions (0 lines with a polytonic-only mark), so they attest the monotonic regime'),
        ('finewiki_el', 'corpus_v4/nc_HuggingFaceFW__finewiki.jsonl',
         'Greek Wikipedia (finewiki), born-digital; CC-BY-SA-4.0'),
        ('eurlex_el', 'corpus_v4/nc_eurlex-greek-legislation.jsonl',
         'EUR-Lex Greek legislation, born-digital; EUPL-1.2'),
        ('europarl_el', 'corpus_v4/nc_ellinika_dedomena_europaikou_koinovouliou.jsonl',
         'European Parliament Greek data, born-digital'),
    ],
}
EXCLUDED_SOURCES = [
    ('estianews', 'house style prints acute for grave (no varia): would attest the wrong final-syllable accent'),
    ('parliament_dl', 'provenance=ocr'),
    ('openbook_gr', 'provenance=ocr (OCR-mixed)'),
    ('Ekklisiastika_Keimena', 'liturgical register with many all-caps rubrics and doc greek_badness ~29; not needed'),
    ('Wikisource_Greek_texts (nanochat copy)', 'same source as wikisource_el_lines; avoid double counting'),
    ('Sxolika_vivlia / greek_legal_code / HPLT / greek_phd', 'provenance uncertain or web-crawled; not proofread'),
    ('perseus_greeklit', 'listed in data/sources.json but not on disk'),
    ('wikinews_el', 'listed in data/sources.json but not on disk'),
]


POLY_ONLY = frozenset('\u0313\u0314\u0300\u0342\u0345')   # breathing, varia, perispomeni, ypogegrammeni


def line_regime_ok(text: str, regime: str) -> bool:
    """Regime purity: polytonic regimes admit only lines carrying a polytonic-only mark; the
    monotonic regime admits only lines without one. Keeps monotonic Wikisource texts out of
    poly19 (and vice versa) so 'both forms attested' means attested in the SAME regime."""
    poly = any(c in POLY_ONLY for c in text)
    return poly if regime in ('ancient', 'poly19') else not poly


def admissible_tokens(text: str) -> Iterator[str]:
    for raw in nfd(text).split():
        _, core, _ = split_token(raw)
        if not core or not has_greek(core) or has_latin_or_digit(core):
            continue
        if is_all_caps(core):
            continue
        yield lower_word(core)


def shingles(text: str, n: int = 4) -> set[tuple[str, ...]]:
    words = [strip_marks(w).lower() for w in nfd(text).split()]
    words = [w.strip('.,;:·!?"\'«»()[]{}—–-') for w in words]
    words = [w for w in words if w]
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def capitalised_mid_sentence(text: str) -> Iterator[str]:
    """Lower-cased cores of capitalised words that are not sentence-initial (proper-name evidence)."""
    prev_trail = None
    for k, raw in enumerate(nfd(text).split()):
        lead, core, trail = split_token(raw)
        if (k > 0 and prev_trail is not None and not any(c in SENTENCE_END for c in prev_trail)
                and not lead and core and has_greek(core) and not has_latin_or_digit(core) and is_capitalised(core)):
            yield lower_word(core)
        prev_trail = trail


def lookup_variants(core: str) -> list[str]:
    """Inflection-aware lookup forms: as written, grave->acute, and with an enclitic-induced second
    accent (the accent on the last mark-bearing cluster of a two-accent word) removed."""
    base = lower_word(nfd(core))
    out = [base]
    acute = base.replace('\u0300', '\u0301')
    if acute != base:
        out.append(acute)
    accents = [i for i, c in enumerate(base) if c in ('\u0301', '\u0300', '\u0342')]
    if len(accents) == 2:
        stripped = base[:accents[-1]] + base[accents[-1] + 1:]
        out.append(stripped)
        out.append(stripped.replace('\u0300', '\u0301'))
    return list(dict.fromkeys(out))


@dataclass
class Lexicon:
    regime: str
    counts: dict = field(default_factory=dict)             # NFD lower form -> count
    by_key: dict = field(default_factory=lambda: defaultdict(dict))  # mark-stripped key -> {form: count}
    names: dict = field(default_factory=dict)              # lower form -> count as a capitalised mid-sentence word
    meta: dict = field(default_factory=dict)

    def add(self, form: str, n: int = 1) -> None:
        self.counts[form] = self.counts.get(form, 0) + n

    def finalize(self) -> None:
        self.by_key = defaultdict(dict)
        for form, n in self.counts.items():
            self.by_key[lexicon_key(form)][form] = n

    def freq(self, core: str) -> int:
        """Max count over the lookup variants (as written, grave->acute, enclitic accent removed)."""
        return max(self.counts.get(v, 0) for v in lookup_variants(core))

    def freq_exact(self, core: str) -> int:
        return self.counts.get(lower_word(nfd(core)), 0)

    def name_count(self, core: str) -> int:
        return self.names.get(lower_word(nfd(core)), 0)

    def attested(self, core: str, minimum: int = ATTESTED_MIN) -> bool:
        return self.freq(core) >= minimum

    def variants(self, core: str) -> dict:
        """All attested marked forms sharing the mark-stripped key of `core`."""
        return dict(self.by_key.get(lexicon_key(nfd(core)), {}))

    def coverage(self, cores: Iterable[str]) -> int:
        return sum(1 for c in cores if self.freq(c) >= 1)

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, 'wt', encoding='utf-8') as fh:
            for form, n in sorted(self.counts.items(), key=lambda kv: (-kv[1], kv[0])):
                fh.write(f'{form}\t{n}\n')
        path.with_suffix('.meta.json').write_text(json.dumps(self.meta, ensure_ascii=False, indent=1))
        with gzip.open(path.with_suffix('.names.tsv.gz'), 'wt', encoding='utf-8') as fh:
            for form, n in sorted(self.names.items(), key=lambda kv: (-kv[1], kv[0])):
                if n >= 2:
                    fh.write(f'{form}\t{n}\n')

    @classmethod
    def load(cls, path: Path, regime: str | None = None, min_count: int = 1) -> 'Lexicon':
        path = Path(path)
        lex = cls(regime or path.name.split('.')[0])
        with gzip.open(path, 'rt', encoding='utf-8') as fh:
            for line in fh:
                form, n = line.rstrip('\n').split('\t')
                n = int(n)
                if n >= min_count:
                    lex.counts[form] = n
        meta = path.with_suffix('.meta.json')
        if meta.exists():
            lex.meta = json.loads(meta.read_text())
        names = path.with_suffix('.names.tsv.gz')
        if names.exists():
            with gzip.open(names, 'rt', encoding='utf-8') as fh:
                for line in fh:
                    form, n = line.rstrip('\n').split('\t')
                    lex.names[form] = int(n)
        lex.finalize()
        return lex


def load_all(directory: Path, min_count: int = 1) -> dict:
    return {r: Lexicon.load(Path(directory) / f'{r}.tsv.gz', r, min_count) for r in REGIMES}


def doc_excluded(doc_id: str, exclude_docs: set | None) -> bool:
    """Document-level exclusion: the source document id (a Wikisource article URL for the dump)
    contains the stem of a held-out work's title."""
    if not exclude_docs or not doc_id:
        return False
    from urllib.parse import unquote
    key = lexicon_key(unquote(doc_id).replace('_', ' '))
    return any(stem in key for stem in exclude_docs)


# Held-out works that also exist as ancient editions: Apollonius Rhodius, Argonautica (tlg0001.tlg001)
# and Aesop's fables (tlg0096) are in the Wikisource human set; excluded from the TEI sources by id.
HELD_OUT_ANCIENT_IDS = ('tlg0001.tlg001', 'tlg0096')

SENTENCE_END = '.;!?·:'
DOC_OVERLAP_MIN = 20      # a whole source document is held out when at least this many of its lines AND
DOC_OVERLAP_SHARE = 0.3   # at least this share of its lines share a 4-gram with an evaluation line
                          # (an absolute threshold alone removed whole Europarl sessions on generic phrases)


def build_regime(regime: str, raw_dir: Path, *, exclude_shingles: set | None = None,
                 exclude_docs: set | None = None, tei_dir: Path | None = None,
                 max_lines_per_source: int | None = None, log=print) -> Lexicon:
    lex = Lexicon(regime)
    sources_meta = []
    exclude_docs = set(exclude_docs or ()) | set(HELD_OUT_ANCIENT_IDS)
    for name, rel, evidence in SOURCES[regime]:
        overlap_docs: set = set()
        if rel.startswith('TEI:'):
            if tei_dir is None or not (Path(tei_dir) / rel[4:]).exists():
                log(f'[lexicon:{regime}] {name}: TEI lines not available, skipped')
                continue
            path = Path(tei_dir) / rel[4:]
        else:
            path = Path(raw_dir) / rel
        t0 = time.time()
        n_lines = n_used = n_excluded = n_tokens = n_regime = n_doc = 0
        if exclude_shingles:
            # pass 1: a whole source document is held out when DOC_OVERLAP_MIN of its lines share a
            # 4-gram with an evaluation line (the eval set covers many pages of each held-out work,
            # and titles differ across namespaces/languages, so id/title matching is not enough)
            per_doc: dict = {}
            doc_lines: dict = {}
            with open(path, encoding='utf-8') as fh:
                for k, line in enumerate(fh):
                    if max_lines_per_source and k >= max_lines_per_source:
                        break
                    try:
                        rec = json.loads(line)
                    except ValueError:
                        continue
                    d = rec.get('source_doc_id', '')
                    doc_lines[d] = doc_lines.get(d, 0) + 1
                    if shingles(rec.get('text', '')) & exclude_shingles:
                        per_doc[d] = per_doc.get(d, 0) + 1
            overlap_docs = {d for d, n in per_doc.items() if n >= DOC_OVERLAP_MIN and n >= DOC_OVERLAP_SHARE * doc_lines[d]}
        with open(path, encoding='utf-8') as fh:
            for line in fh:
                if max_lines_per_source and n_lines >= max_lines_per_source:
                    break
                n_lines += 1
                try:
                    rec = json.loads(line)
                    text = rec['text']
                except (ValueError, KeyError):
                    continue
                if doc_excluded(rec.get('source_doc_id', ''), exclude_docs) or rec.get('source_doc_id', '') in overlap_docs:
                    n_doc += 1
                    continue
                if not line_regime_ok(nfd(text), regime):
                    n_regime += 1
                    continue
                if exclude_shingles and (shingles(text) & exclude_shingles):
                    n_excluded += 1
                    continue
                n_used += 1
                for tok in admissible_tokens(text):
                    lex.add(tok)
                    n_tokens += 1
                for name_key in capitalised_mid_sentence(text):
                    lex.names[name_key] = lex.names.get(name_key, 0) + 1
        sources_meta.append(dict(name=name, path=str(path), evidence=evidence, lines_read=n_lines,
                                 lines_used=n_used, lines_excluded_overlap=n_excluded,
                                 lines_excluded_regime=n_regime, lines_excluded_doc=n_doc,
                                 docs_excluded_by_overlap=len(overlap_docs), tokens=n_tokens,
                                 seconds=round(time.time() - t0, 1)))
        log(f'[lexicon:{regime}] {name}: lines={n_lines} used={n_used} excluded_overlap={n_excluded} '
            f'excluded_regime={n_regime} excluded_doc={n_doc} tokens={n_tokens} '
            f'({time.time() - t0:.0f}s)')
    lex.meta = dict(regime=regime, sources=sources_meta, forms=len(lex.counts),
                    tokens=sum(lex.counts.values()), forms_ge5=sum(1 for n in lex.counts.values() if n >= 5),
                    names=len(lex.names), names_ge3=sum(1 for n in lex.names.values() if n >= 3))
    lex.finalize()
    return lex


def choose_regime(script_class: str, cores: list[str], lexicons: dict, texts: Iterable[str] = ()) -> tuple[str, dict]:
    """Regime for a line.

    A polytonic-only mark in either reading (`texts`) proves a polytonic regime: ancient or
    poly19, whichever lexicon attests more of the undisputed word cores (ties -> poly19, the
    harvest is mostly 19th-20th c. print). Otherwise `greek_mono` -> mono; otherwise coverage
    decides. The script class alone is not trusted: it is derived from Google's label, and a
    polytonic line whose marks Google dropped is classed greek_mono.
    """
    cover = {r: lexicons[r].coverage(cores) for r in REGIMES if r in lexicons}
    poly = any(c in POLY_ONLY for t in texts for c in nfd(t))
    a, b, m = cover.get('ancient', 0), cover.get('poly19', 0), cover.get('mono', 0)
    if poly:
        return ('ancient' if a > b else 'poly19'), cover
    if script_class == 'greek_mono':
        return 'mono', cover
    best = max(cover.values()) if cover else 0
    if m >= best and m > 0:
        return 'mono', cover
    return ('ancient' if a > b else 'poly19'), cover
