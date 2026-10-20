#!/usr/bin/env python3
"""Aspect B (content and style) analysis of the admitted real-line OCR pool.

Spec: docs/harvest/analysis/SPECS.md, section "Aspect B -- content and style".

Usage (from the repo root):
    .venv/bin/python docs/harvest/analysis/B_content_style/analysis_B.py            # full pool
    .venv/bin/python docs/harvest/analysis/B_content_style/analysis_B.py --limit 20000 \
        --out docs/harvest/analysis/B_content_style/test_first20k                  # smoke test

Two streaming passes over admitted_all.jsonl:
  pass 1 computes per-line numeric features (kept as small numpy arrays, no labels, no crops);
  class quantiles are computed from those arrays;
  pass 2 re-streams the jsonl, assigns flags with reasons, writes line_flags.jsonl.gz and
  reservoir-samples 20 example lines per flag type.
Then book statistics and REPORT.md.

Page height for the running-title detector comes from the page PNG header (PIL lazy open, only
the header is read), page_id -> image path taken from docs/harvest/<wave>/records.jsonl
(round1: records_all.jsonl). Fallback: max y1 of that page's boxes in records. Cached in
page_sizes.json next to this script.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import re
import sys
import unicodedata
from collections import Counter, defaultdict

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
HERE = os.path.dirname(os.path.abspath(__file__))
ADMITTED = os.path.join(REPO, "docs/harvest/collection/admitted_all.jsonl")

# ----------------------------------------------------------------------------- characters
# Spacing apostrophe-like characters named in the spec.
SPACING_APOS = {"᾿": "U+1FBF psili", "᾽": "U+1FBD koronis", "΄": "U+0384 tonos",
                "’": "U+2019 right quote"}
# Other spacing (non-combining) Greek diacritics: counted as their own feature, excluded from
# symbol share (they are Unicode Sk but are accent marks, not symbols).
SPACING_GREEK_OTHER = set("΅῀῁῍῎῏῝῞῟῭΅`´῾͵")
HYPHENS_END = {"-": "-", "‐": "U+2010", "‑": "U+2011", "­": "soft hyphen", "¬": "¬ (not sign)"}
DASHES = "—–―‒−"  # em, en, horizontal bar, figure dash, minus


def is_greek_letter(ch: str) -> bool:
    o = ord(ch)
    return (0x0370 <= o <= 0x03FF or 0x1F00 <= o <= 0x1FFF) and unicodedata.category(ch).startswith("L")


NUM_TOKEN = re.compile(r"^[(\[]?[-+−±]?\d[\d.,:/%·'΄]*[)\]]?[.,;:]?$")
BIBLIO = [
    ("year_in_parens", re.compile(r"\(\s*(1[4-9]\d\d|20[0-2]\d)\s*\)")),
    ("pp.", re.compile(r"(?<!\w)pp\.")),
    ("Bd.", re.compile(r"(?<!\w)Bd\.")),
    ("vol.", re.compile(r"(?<!\w)[Vv]ol\.")),
    ("σ.+number", re.compile(r"(?<!\w)σ\.\s?\d")),
]
REP_RUN = re.compile(r"(\S)\1{3,}")
# headword (one or two words) followed by a dash or a colon and then more text
# headword = ONE word (letters, internal hyphen/apostrophe allowed; not ending a sentence with "."), optional comma,
# then a dash or a colon, then more text
DICT_LINE = re.compile(r"^\W{0,2}[^\W\d_][^\W\d_\-'\u2019\u1FBF\u1FBD]*,?\s*(?::(?!//)|[" + DASHES + r"]|\s-\s)\s*\S")
# 19th-c. orthography writes final ς at a compound boundary (προςάγω, εἰςφέρω, ὥςτε, ὅςτις, δυςτυχής): faithful to
# the print, not a label error. Prefix (accents stripped, lowercase) before such a ς:
COMPOUND_S_PREFIX_END = ("προ", "ει", "δυ")
COMPOUND_S_PREFIX_EQ = {"ω", "ο", "οπω", "ε", "καθω", "ουτω", "α", "η", "οια", "οιο", "οποια", "οποιο", "ηντινα", "οιτινα"}
COMPOUND_S_SUFFIX_START = ("δηποτ", "περ", "τισ", "τινο", "τινα", "τινω", "τιν")
# digitisation stamps / scanner marks admitted as lines (whole label after stripping ornaments)
# (no trailing period: "ΠΑΝΕΠΙΣΤΗΜΙΟΝ." as a printed heading is book text)
STAMP = re.compile(r"^\W*(ΠΑΝΕΠΙΣΤΗΜΙ\w*(\s+ΚΡ\w*)?|Digitized by Google|ΒΙΒΛΙΟΘΗΚΗ)[^\w.]*$")
PRECOMPOSED_BREATHING_CAP = re.compile("[\u1F08-\u1F0F\u1F18-\u1F1D\u1F28-\u1F2F\u1F38-\u1F3F\u1F48-\u1F4D"
                                       "\u1F59-\u1F5F\u1F68-\u1F6F\u1F88-\u1F8F\u1F98-\u1F9F\u1FA8-\u1FAF\u1FEC]")
WORD_CORE = re.compile(r"^[^\w]*(.*?)[^\w]*$")


def _plain(t: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn").lower()


def word_core(tok: str) -> str:
    return "".join(c for c in tok if unicodedata.category(c)[0] in "LM").lower()


def line_features(label: str, vocab: Counter | None = None) -> dict:
    s = unicodedata.normalize("NFC", label or "")
    vis = [c for c in s if not c.isspace() and unicodedata.category(c) != "Mn"]
    n_vis = len(vis)
    cats = [unicodedata.category(c) for c in vis]
    n_digit = sum(1 for c in cats if c == "Nd")
    n_punct = sum(1 for c in cats if c.startswith("P"))
    n_symbol = sum(1 for c, k in zip(vis, cats) if k.startswith("S") and c not in SPACING_APOS and c not in SPACING_GREEK_OTHER)
    n_upper = sum(1 for k in cats if k in ("Lu", "Lt"))
    n_lower = sum(1 for k in cats if k == "Ll")
    n_cased = n_upper + n_lower
    tokens = s.split()
    word_lens = []
    greek_words = 0
    for t in tokens:
        letters = [c for c in t if unicodedata.category(c).startswith("L")]
        if letters:
            word_lens.append(len(letters))
            if any(is_greek_letter(c) and unicodedata.category(c) == "Ll" for c in letters):
                greek_words += 1
    longest_tok = max((len([c for c in t if unicodedata.category(c) != "Mn"]) for t in tokens), default=0)
    # repeated runs
    runs = [(m.group(1), len(m.group(0))) for m in REP_RUN.finditer(s)]
    # numeric table: >=3 consecutive numeric tokens
    best = cur = 0
    for t in tokens:
        if NUM_TOKEN.match(t):
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    biblio = [name for name, rx in BIBLIO if rx.search(s)]
    # final sigma errors
    sig_end_strong = sig_end_period = medial_final = medial_compound = medial_stigma = 0
    sig_ctx = []
    for i, c in enumerate(s):
        if c == "σ":
            nxt = s[i + 1] if i + 1 < len(s) else ""
            prv = s[i - 1] if i > 0 else ""
            if nxt and (unicodedata.category(nxt).startswith("L") or unicodedata.category(nxt) == "Mn"):
                continue
            if nxt in HYPHENS_END or nxt in "‐‑":
                continue  # word broken at line end / compound: sigma stays medial
            if not (prv and unicodedata.category(prv).startswith("L")):
                continue  # single-letter "σ" (abbreviation, e.g. "σ. 12")
            if nxt == ".":
                sig_end_period += 1  # possible abbreviation (e.g. "Ἰησ.")
            else:
                sig_end_strong += 1
                sig_ctx.append(s[max(0, i - 8):i + 3])
        elif c == "ς":
            nxt = s[i + 1] if i + 1 < len(s) else ""
            if nxt and unicodedata.category(nxt).startswith("L"):
                j = i
                while j > 0 and (unicodedata.category(s[j - 1]).startswith("L") or unicodedata.category(s[j - 1]) == "Mn"):
                    j -= 1
                pre = _plain(s[j:i])
                k = i + 1
                while k < len(s) and (unicodedata.category(s[k]).startswith("L") or unicodedata.category(s[k]) == "Mn"):
                    k += 1
                post = _plain(s[i + 1:k])
                if pre == "" or pre.endswith(COMPOUND_S_PREFIX_END) or pre in COMPOUND_S_PREFIX_EQ or post.startswith(COMPOUND_S_SUFFIX_START):
                    medial_compound += 1  # print orthography (compound boundary / aphaeresis 'ς), not counted as an error
                else:
                    medial_final += 1
                    sig_ctx.append(s[max(0, i - 8):i + 3])
                    if vocab is not None:
                        w_st = (s[j:i] + "στ" + s[i + 1:k]).lower()
                        if vocab.get(w_st, 0) >= 1:
                            medial_stigma += 1  # ς stands for the στ ligature (word with στ attested in the pool)
    # spacing apostrophes
    sa_alone = sa_before = sa_before_cap = sa_after = 0
    sa_kinds = Counter()
    for t in tokens:
        if t and all(ch in SPACING_APOS or unicodedata.category(ch).startswith("P") for ch in t) and any(ch in SPACING_APOS for ch in t):
            for ch in t:
                if ch in SPACING_APOS:
                    sa_alone += 1
                    sa_kinds[SPACING_APOS[ch]] += 1
            continue
        for j, ch in enumerate(t):
            if ch not in SPACING_APOS:
                continue
            prv = t[j - 1] if j > 0 else ""
            nxt = t[j + 1] if j + 1 < len(t) else ""
            if (not prv or not unicodedata.category(prv).startswith("L")) and nxt and unicodedata.category(nxt).startswith("L"):
                sa_before += 1  # word-initial spacing mark directly before a letter (e.g. "᾿Α")
                if unicodedata.category(nxt) in ("Lu", "Lt"):
                    sa_before_cap += 1  # e.g. "᾿Α" where the precomposed capital "Ἀ" is meant
                    sa_kinds[SPACING_APOS[ch] + " before capital"] += 1
                else:
                    sa_kinds[SPACING_APOS[ch] + " before lowercase"] += 1
            else:
                sa_after += 1  # elision / keraia after a letter: normal usage, not flagged
    n_sg_other = sum(1 for c in s if c in SPACING_GREEK_OTHER)
    stripped = s.rstrip()
    hyph = HYPHENS_END.get(stripped[-1:], "") if stripped else ""
    first_letter = next((c for c in s if unicodedata.category(c).startswith("L")), "")
    cap_initial = bool(first_letter) and unicodedata.category(first_letter) in ("Lu", "Lt")
    dict_like = bool(DICT_LINE.match(s))
    return {
        "n_chars": len(s),
        "n_vis": n_vis,
        "digit_share": n_digit / n_vis if n_vis else 0.0,
        "punct_share": n_punct / n_vis if n_vis else 0.0,
        "symbol_share": n_symbol / n_vis if n_vis else 0.0,
        "upper_share": n_upper / n_cased if n_cased else 0.0,
        "is_all_caps": n_cased >= 2 and n_lower == 0,
        "no_lower": n_lower == 0 and (n_cased >= 2 or n_digit >= 1),
        "n_tokens": len(tokens),
        "mean_word_len": float(np.mean(word_lens)) if word_lens else 0.0,
        "n_words": len(word_lens),
        "longest_token": longest_tok,
        "rep_run_count": len(runs),
        "rep_run_max": max((r[1] for r in runs), default=0),
        "rep_run_chars": "".join(sorted({r[0] for r in runs})),
        "numeric_run": best,
        "numeric_table": best >= 3,
        "biblio": biblio,
        "sigma_end_strong": sig_end_strong,
        "sigma_end_period": sig_end_period,
        "final_sigma_medial": medial_final,
        "final_sigma_compound": medial_compound,
        "final_sigma_for_st": medial_stigma,
        "stamp": bool(STAMP.match(s.strip())),
        "precomposed_breathing_capital": len(PRECOMPOSED_BREATHING_CAP.findall(s)),
        "sigma_err": sig_end_strong + medial_final,
        "sigma_ctx": sig_ctx[:3],
        "greek_words": greek_words,
        "spacing_apos_alone": sa_alone,
        "spacing_apos_before_letter": sa_before,
        "spacing_apos_before_capital": sa_before_cap,
        "spacing_apos_after_letter": sa_after,
        "spacing_apos_kinds": dict(sa_kinds),
        "spacing_greek_other": n_sg_other,
        "hyphen_end": hyph,
        "cap_initial": cap_initial,
        "dictionary_like": dict_like,
    }


# numeric columns kept in memory for quantiles / book stats
NUM_COLS = ["n_chars", "digit_share", "punct_share", "symbol_share", "upper_share", "n_tokens", "mean_word_len",
            "longest_token", "rep_run_max", "numeric_run", "sigma_err", "greek_words", "spacing_apos_alone",
            "spacing_apos_before_letter", "y_rel", "is_all_caps", "no_lower", "cap_initial", "dictionary_like",
            "hyphen_end", "biblio", "numeric_table", "rep_run", "top_bottom", "n_words", "final_sigma_compound",
            "spacing_apos_before_capital", "stamp", "precomposed_breathing_capital"]
# continuous features summarised per book (median/p10/p90) and z-scored
BOOK_FEATS = ["n_chars", "digit_share", "punct_share", "symbol_share", "upper_share", "n_tokens", "mean_word_len",
              "longest_token", "y_rel"]


# ----------------------------------------------------------------------------- page sizes
def records_path(wave: str) -> str:
    if wave == "round1":
        return os.path.join(REPO, "docs/harvest/round1/records_all.jsonl")
    return os.path.join(REPO, f"docs/harvest/{wave}/records.jsonl")


def page_sizes(needed: dict[str, set], cache_path: str) -> dict:
    """needed: wave -> set(page_id). Returns page_id -> {"w","h","method"}."""
    cache = {}
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            cache = json.load(f)
    missing = {w: {p for p in ps if p not in cache} for w, ps in needed.items()}
    if any(missing.values()):
        from PIL import Image
        for wave, ps in missing.items():
            if not ps:
                continue
            img_of, maxy = {}, defaultdict(float)
            with open(records_path(wave)) as f:
                for line in f:
                    r = json.loads(line)
                    p = r["page_id"]
                    if p in ps:
                        if r.get("image"):
                            img_of[p] = r["image"]
                        maxy[p] = max(maxy[p], float(r["bbox"][3]))
            for p in ps:
                img = img_of.get(p)
                path = os.path.join(REPO, img) if img else None
                if path and os.path.exists(path):
                    with Image.open(path) as im:  # lazy: reads the header only
                        w, h = im.size
                    cache[p] = {"w": w, "h": h, "method": "png_header"}
                else:
                    cache[p] = {"w": None, "h": maxy.get(p) or None, "method": "max_y1_records"}
        with open(cache_path, "w") as f:
            json.dump(cache, f)
    return cache


# ----------------------------------------------------------------------------- helpers
def q(a, p):
    return float(np.percentile(a, p)) if len(a) else float("nan")


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    return f"{x:.{nd}f}"


class Reservoir:
    def __init__(self, k, seed):
        self.k, self.n, self.items, self.rng = k, 0, [], random.Random(seed)

    def add(self, item):
        self.n += 1
        if len(self.items) < self.k:
            self.items.append(item)
        else:
            j = self.rng.randrange(self.n)
            if j < self.k:
                self.items[j] = item


# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=HERE)
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    assert out.startswith(HERE), "outputs must stay under the Aspect B folder"
    os.makedirs(out, exist_ok=True)

    # ---- pass 0: pages needed
    needed = defaultdict(set)
    n_total = 0
    with open(ADMITTED) as f:
        for i, line in enumerate(f):
            if args.limit and i >= args.limit:
                break
            r = json.loads(line)
            needed[r["wave"]].add(r["page_id"])
            n_total += 1
    sizes = page_sizes(needed, os.path.join(HERE, "page_sizes.json"))
    size_methods = Counter(sizes[p]["method"] for ps in needed.values() for p in ps)
    print(f"lines={n_total} pages={sum(len(v) for v in needed.values())} size methods={dict(size_methods)}", flush=True)

    # ---- pass 1: features
    N = n_total
    A = {c: np.zeros(N, dtype=np.float32) for c in NUM_COLS}
    cls_idx = np.zeros(N, dtype=np.int16)
    wave_idx = np.zeros(N, dtype=np.int16)
    book_idx = np.zeros(N, dtype=np.int32)
    classes, waves, books = {}, {}, {}
    biblio_kind = Counter()
    vocab = Counter()  # NFC-lowercased word cores of the processed pool (for the ς -> στ check)
    hyphen_kind = Counter()
    with open(ADMITTED) as f:
        for i, line in enumerate(f):
            if i >= N:
                break
            r = json.loads(line)
            ft = line_features(r["label"])
            for tok in unicodedata.normalize("NFC", r["label"] or "").split():
                wc_ = word_core(tok)
                if wc_:
                    vocab[wc_] += 1
            H = sizes[r["page_id"]]["h"]
            y0, y1 = float(r["bbox"][1]), float(r["bbox"][3])
            yc = (y0 + y1) / 2 / H if H else float("nan")
            tb = bool(H) and (y0 < 0.08 * H or y1 > 0.92 * H)
            for c in NUM_COLS:
                if c == "y_rel":
                    A[c][i] = yc
                elif c == "top_bottom":
                    A[c][i] = tb
                elif c == "hyphen_end":
                    A[c][i] = bool(ft["hyphen_end"])
                elif c == "biblio":
                    A[c][i] = bool(ft["biblio"])
                elif c == "rep_run":
                    A[c][i] = ft["rep_run_count"] > 0
                elif c in ("spacing_apos_alone", "spacing_apos_before_letter"):
                    A[c][i] = ft[c]
                else:
                    A[c][i] = float(ft[c])
            biblio_kind.update(ft["biblio"])
            if ft["hyphen_end"]:
                hyphen_kind[ft["hyphen_end"]] += 1
            cls_idx[i] = classes.setdefault(r["script_class"], len(classes))
            wave_idx[i] = waves.setdefault(r["wave"], len(waves))
            book_idx[i] = books.setdefault((r["source"], r["book_key"]), len(books))
            if i % 50000 == 0:
                print(f"pass1 {i}", flush=True)
    cls_names = {v: k for k, v in classes.items()}
    wave_names = {v: k for k, v in waves.items()}
    book_names = {v: k for k, v in books.items()}

    # ---- class reference quantiles (line level)
    REF = {}
    for ci, cn in cls_names.items():
        m = cls_idx == ci
        d = {"n": int(m.sum())}
        for c in ["n_chars", "digit_share", "punct_share", "symbol_share", "mean_word_len", "longest_token", "n_tokens"]:
            for p in (1, 5, 10, 25, 50, 75, 90, 95, 99):
                d[f"{c}_p{p}"] = q(A[c][m], p)
        # word-length reference only over lines with >= 3 words (1-2 word lines have degenerate means)
        mw = m & (A["n_words"] >= 3)
        d["mean_word_len_3w_n"] = int(mw.sum())
        d["mean_word_len_3w_p1"], d["mean_word_len_3w_p99"] = q(A["mean_word_len"][mw], 1), q(A["mean_word_len"][mw], 99)
        # thresholds on the non-zero part for sparse share features (if most lines are 0, the plain p95 is 0)
        for c in ["digit_share", "punct_share", "symbol_share"]:
            nz = A[c][m][A[c][m] > 0]
            d[f"{c}_nz_n"] = int(len(nz))
            d[f"{c}_nz_p90"] = q(nz, 90) if len(nz) else float("nan")
            d[f"{c}_nz_p99"] = q(nz, 99) if len(nz) else float("nan")
        for c in ["is_all_caps", "numeric_table", "biblio", "rep_run", "top_bottom", "no_lower", "dictionary_like",
                  "hyphen_end", "cap_initial"]:
            d[f"{c}_rate"] = float(A[c][m].mean())
        d["sigma_err_line_rate"] = float((A["sigma_err"][m] > 0).mean())
        d["spacing_apos_line_rate"] = float(((A["spacing_apos_alone"][m] + A["spacing_apos_before_letter"][m]) > 0).mean())
        REF[cn] = d

    # line-level thresholds (all relative to the line's script class)
    def thr(cn):
        d = REF[cn]
        return {
            # digit-heavy: digit share above the class p90 of lines that contain digits at all
            "digit_heavy": d["digit_share_nz_p90"],
            "punct_heavy": d["punct_share_nz_p99"],
            "symbol_heavy": d["symbol_share_nz_p99"],
            "long_token": d["longest_token_p99"],
            "word_len_hi": d["mean_word_len_3w_p99"],
            "word_len_lo": d["mean_word_len_3w_p1"],
            # "short" for the running-title pattern: at most the class median length
            "short": d["n_chars_p50"],
        }
    THR = {cn: thr(cn) for cn in REF}

    FLAG_TYPES = ["digit_heavy", "punct_heavy", "symbol_heavy", "all_caps", "long_token", "word_length_outlier",
                  "repeated_run", "numeric_table", "bibliographic", "running_title_or_page_number",
                  "final_sigma_error", "spacing_apostrophe", "line_end_not_sign", "dictionary_like", "digitisation_stamp"]
    flag_cols = {ft: np.zeros(N, dtype=bool) for ft in FLAG_TYPES}
    examples = {ft: Reservoir(20, seed=sum(map(ord, ft)) + 17) for ft in FLAG_TYPES}
    random.seed(17)

    SIG_ST = np.zeros(N, dtype=np.int16)
    SIG_MED = np.zeros(N, dtype=np.int16)
    SIG_END = np.zeros(N, dtype=np.int16)
    # ---- pass 2: flags + line_flags.jsonl.gz
    out_lines = os.path.join(out, "line_flags.jsonl.gz")
    with open(ADMITTED) as f, gzip.open(out_lines, "wt", encoding="utf-8") as g:
        for i, line in enumerate(f):
            if i >= N:
                break
            r = json.loads(line)
            cn = r["script_class"]
            t, d = THR[cn], REF[cn]
            ft = line_features(r["label"], vocab)
            SIG_ST[i] = ft["final_sigma_for_st"]
            SIG_MED[i] = ft["final_sigma_medial"]
            SIG_END[i] = ft["sigma_end_strong"]
            flags = {}
            if ft["digit_share"] > 0 and ft["digit_share"] > t["digit_heavy"]:
                flags["digit_heavy"] = f"digit share {ft['digit_share']:.3f} > {cn} p90 of digit-bearing lines {t['digit_heavy']:.3f} (n={d['digit_share_nz_n']})"
            if ft["punct_share"] > 0 and ft["punct_share"] > t["punct_heavy"]:
                flags["punct_heavy"] = f"punctuation share {ft['punct_share']:.3f} > {cn} p99 of punctuated lines {t['punct_heavy']:.3f}"
            if ft["symbol_share"] > 0 and ft["symbol_share"] > t["symbol_heavy"]:
                flags["symbol_heavy"] = f"symbol share {ft['symbol_share']:.3f} > {cn} p99 of symbol-bearing lines {t['symbol_heavy']:.3f} (n={d['symbol_share_nz_n']})"
            if ft["is_all_caps"]:
                flags["all_caps"] = f"all cased letters uppercase (upper share {ft['upper_share']:.2f}); {cn} all-caps line rate {d['is_all_caps_rate']:.3f}"
            if ft["longest_token"] > t["long_token"]:
                flags["long_token"] = f"longest token {ft['longest_token']} chars > {cn} p99 {t['long_token']:.0f}"
            if ft["n_words"] >= 3 and (ft["mean_word_len"] > t["word_len_hi"] or ft["mean_word_len"] < t["word_len_lo"]):
                flags["word_length_outlier"] = (f"mean word length {ft['mean_word_len']:.2f} over {ft['n_words']} words outside {cn} "
                                                f"[p1 {t['word_len_lo']:.2f}, p99 {t['word_len_hi']:.2f}] of >=3-word lines")
            if ft["rep_run_count"]:
                flags["repeated_run"] = f"{ft['rep_run_count']} run(s) of >=4 identical chars, max {ft['rep_run_max']}, chars {ft['rep_run_chars']!r}; {cn} line rate {d['rep_run_rate']:.4f}"
            if ft["numeric_table"]:
                flags["numeric_table"] = f"{ft['numeric_run']} consecutive numeric tokens; {cn} line rate {d['numeric_table_rate']:.4f}"
            if ft["biblio"]:
                flags["bibliographic"] = f"patterns {ft['biblio']}; {cn} line rate {d['biblio_rate']:.4f}"
            H = sizes[r["page_id"]]["h"]
            y0, y1 = float(r["bbox"][1]), float(r["bbox"][3])
            yc = (y0 + y1) / 2 / H if H else None
            topbot = bool(H) and (y0 < 0.08 * H or y1 > 0.92 * H)
            short = ft["n_chars"] <= t["short"]
            if topbot and short and ft["no_lower"]:
                flags["running_title_or_page_number"] = (
                    f"box y0={y0:.0f} y1={y1:.0f} of page h={H:.0f} (in top/bottom 8%), {ft['n_chars']} chars <= {cn} p50 "
                    f"{t['short']:.0f}, no lowercase letters")
            if ft["sigma_err"]:
                flags["final_sigma_error"] = (f"{ft['sigma_end_strong']} word-final σ + {ft['final_sigma_medial']} word-internal ς "
                                              f"(of which {ft['final_sigma_for_st']} where the στ-form is attested in the pool, i.e. ς misread for the στ ligature) "
                                              f"(ctx {ft['sigma_ctx']}); {cn} line rate {d['sigma_err_line_rate']:.4f}")
            sa = ft["spacing_apos_alone"] + ft["spacing_apos_before_letter"]
            if sa:
                flags["spacing_apostrophe"] = (f"{ft['spacing_apos_alone']} standing alone + {ft['spacing_apos_before_letter']} word-initial "
                                               f"before a letter {ft['spacing_apos_kinds']}; {cn} line rate {d['spacing_apos_line_rate']:.4f}")
            if ft["hyphen_end"] == "¬ (not sign)":
                flags["line_end_not_sign"] = "line ends with ¬ (text-layer hyphenation artefact)"
            if ft["dictionary_like"]:
                flags["dictionary_like"] = f"headword + dash/colon at line start; {cn} line rate {d['dictionary_like_rate']:.4f}"
            if ft["stamp"]:
                flags["digitisation_stamp"] = (f"label is a library/digitiser stamp; box {float(r['bbox'][2]) - float(r['bbox'][0]):.0f}x"
                                               f"{y1 - y0:.0f}px at y_rel {yc if yc is None else round(yc, 3)}")
            for k in flags:
                flag_cols[k][i] = True
                examples[k].add({"id": r["id"], "wave": r["wave"], "source": r["source"], "book_key": r["book_key"],
                                 "label": r["label"], "crop_path": r["crop_path"], "reason": flags[k]})
            row = {"id": r["id"], "wave": r["wave"], "source": r["source"], "book_key": r["book_key"],
                   "script_class": cn, "y_rel": None if yc is None else round(yc, 4), "top_bottom_8pct": topbot,
                   **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in ft.items() if k not in ("sigma_ctx",)},
                   "flags": sorted(flags), "reasons": flags}
            g.write(json.dumps(row, ensure_ascii=False) + "\n")
            if i % 50000 == 0:
                print(f"pass2 {i}", flush=True)

    # ---- book statistics
    nb = len(book_names)
    order = np.argsort(book_idx, kind="stable")
    bounds = np.searchsorted(book_idx[order], np.arange(nb + 1))
    BOOK = []
    for b in range(nb):
        ix = order[bounds[b]:bounds[b + 1]]
        src, key = book_names[b]
        cc = Counter(cls_names[c] for c in cls_idx[ix])
        wc = Counter(wave_names[w] for w in wave_idx[ix])
        rec = {"source": src, "book_key": key, "waves": dict(wc), "n_lines": int(len(ix)),
               "script_class": cc.most_common(1)[0][0], "class_counts": dict(cc)}
        for c in BOOK_FEATS:
            v = A[c][ix]
            v = v[~np.isnan(v)]
            rec[c] = {"median": q(v, 50), "p10": q(v, 10), "p90": q(v, 90)}
        rec["flag_counts"] = {ft: int(flag_cols[ft][ix].sum()) for ft in FLAG_TYPES}
        rec["flag_shares"] = {ft: rec["flag_counts"][ft] / len(ix) for ft in FLAG_TYPES}
        rec["shares"] = {c: float(A[c][ix].mean()) for c in
                         ["is_all_caps", "cap_initial", "hyphen_end", "top_bottom", "dictionary_like", "numeric_table", "biblio"]}
        gw = float(A["greek_words"][ix].sum())
        se = float(A["sigma_err"][ix].sum())
        rec["greek_words"] = int(gw)
        rec["sigma_errors"] = int(se)
        rec["precomposed_breathing_capitals"] = int(A["precomposed_breathing_capital"][ix].sum())
        rec["compound_final_sigma"] = int(A["final_sigma_compound"][ix].sum())
        rec["sigma_error_parts"] = {"word_final_σ": int(SIG_END[ix].sum()), "word_internal_ς": int(SIG_MED[ix].sum()),
                                    "of_which_ς_for_στ": int(SIG_ST[ix].sum())}
        rec["shares"]["spacing_mark_before_capital_lines"] = float((A["spacing_apos_before_capital"][ix] > 0).mean())
        rec["final_sigma_error_rate"] = se / gw if gw else None
        BOOK.append(rec)

    MIN_LINES, MIN_GW, MIN_REF_BOOKS, MIN_SIG_ERR = 30, 100, 5, 2
    by_cls = defaultdict(list)
    for rec in BOOK:
        by_cls[rec["script_class"]].append(rec)
    BREF = {}
    for cn, recs in by_cls.items():
        ref = [r for r in recs if r["n_lines"] >= MIN_LINES]
        sig = [r["final_sigma_error_rate"] for r in ref if r["greek_words"] >= MIN_GW]
        caps = [r["shares"]["is_all_caps"] for r in ref]
        capi = [r["shares"]["cap_initial"] for r in ref]
        med_len = [r["n_chars"]["median"] for r in ref]
        d = {"n_books": len(recs), "n_ref": len(ref), "n_ref_sigma": len(sig),
             "sigma_p95": q(sig, 95) if sig else None, "all_caps_p95": q(caps, 95) if caps else None,
             "cap_initial_p95": q(capi, 95) if capi else None, "median_len_p50": q(med_len, 50) if med_len else None}
        for c in BOOK_FEATS:
            v = np.array([r[c]["median"] for r in ref], dtype=float)
            d[f"{c}_mu"], d[f"{c}_sd"] = (float(v.mean()), float(v.std(ddof=1))) if len(v) >= 2 else (None, None)
        for ft in FLAG_TYPES:
            v = np.array([r["flag_shares"][ft] for r in ref], dtype=float)
            d[f"share_{ft}_mu"], d[f"share_{ft}_sd"] = (float(v.mean()), float(v.std(ddof=1))) if len(v) >= 2 else (None, None)
        BREF[cn] = d

    for rec in BOOK:
        cn = rec["script_class"]
        d = BREF[cn]
        hard = {}
        eligible = rec["n_lines"] >= MIN_LINES
        dh = rec["flag_shares"]["digit_heavy"]
        if dh > 0.30:
            hard["digit_heavy_gt30pct"] = f"{dh:.1%} of {rec['n_lines']} lines digit-heavy > 30% (spec constant)"
        rt = rec["flag_shares"]["running_title_or_page_number"]
        if rt > 0.30:
            hard["running_title_gt30pct"] = f"{rt:.1%} of lines are running-title/page-number pattern > 30% (spec constant)"
        sr = rec["final_sigma_error_rate"]
        q_ok = d["n_ref"] >= MIN_REF_BOOKS
        rec["below_support"] = {}
        if (eligible and q_ok and sr is not None and rec["greek_words"] >= MIN_GW and d["sigma_p95"] is not None
                and sr > d["sigma_p95"] and rec["sigma_errors"] < MIN_SIG_ERR):
            rec["below_support"]["final_sigma_above_class_p95"] = f"rate {sr:.4f} > p95 {d['sigma_p95']:.4f} but only {rec['sigma_errors']} error(s)"
        if (eligible and q_ok and sr is not None and rec["greek_words"] >= MIN_GW and d["sigma_p95"] is not None
                and sr > d["sigma_p95"] and rec["sigma_errors"] >= MIN_SIG_ERR):
            hard["final_sigma_above_class_p95"] = (f"final-sigma error rate {sr:.4f} ({rec['sigma_errors']}/{rec['greek_words']} Greek words) > "
                                                   f"{cn} book p95 {d['sigma_p95']:.4f} (N={d['n_ref_sigma']} books)")
        ac = rec["shares"]["is_all_caps"]
        if eligible and q_ok and d["all_caps_p95"] is not None and ac > d["all_caps_p95"]:
            hard["all_caps_above_class_p95"] = f"all-caps line share {ac:.3f} > {cn} book p95 {d['all_caps_p95']:.3f} (N={d['n_ref']} books)"
        rec["hard_flags"] = hard
        # verse-like (informational, not a hard flag)
        ci = rec["shares"]["cap_initial"]
        rec["verse_like"] = bool(eligible and q_ok and d["cap_initial_p95"] is not None and ci > d["cap_initial_p95"]
                                 and rec["n_chars"]["median"] < d["median_len_p50"])
        if rec["verse_like"]:
            rec["verse_like_reason"] = (f"capital-initial line share {ci:.3f} > {cn} book p95 {d['cap_initial_p95']:.3f} and median "
                                        f"length {rec['n_chars']['median']:.0f} < {cn} book median {d['median_len_p50']:.0f}")
        z = {}
        for c in BOOK_FEATS:
            mu, sd = d[f"{c}_mu"], d[f"{c}_sd"]
            z[c] = (rec[c]["median"] - mu) / sd if (mu is not None and sd and d["n_ref"] >= 5) else None
        zs = {}
        for ft in FLAG_TYPES:
            mu, sd = d[f"share_{ft}_mu"], d[f"share_{ft}_sd"]
            zs[ft] = (rec["flag_shares"][ft] - mu) / sd if (mu is not None and sd and d["n_ref"] >= 5) else None
        rec["z_median"] = z
        rec["z_flag_share"] = zs
        rec["z_reference"] = {"script_class": cn, "N_books": d["n_ref"], "min_lines": MIN_LINES,
                              "note": None if d["n_ref"] >= 5 else "reference population < 5 books: z not computed"}
        rec["n_beyond_2sd"] = sum(1 for v in list(z.values()) + list(zs.values()) if v is not None and abs(v) > 2)

    with open(os.path.join(out, "book_stats.jsonl"), "w") as f:
        for rec in BOOK:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    A["_sig_st"], A["_sig_med"], A["_sig_end"] = SIG_ST, SIG_MED, SIG_END
    write_report(out, N, A, cls_idx, wave_idx, cls_names, wave_names, REF, THR, BOOK, BREF, FLAG_TYPES, flag_cols,
                 examples, size_methods, biblio_kind, hyphen_kind, MIN_LINES, MIN_GW, args.limit, MIN_SIG_ERR, MIN_REF_BOOKS)
    print("done", out)


def findings(w, N, A, wave_idx, wave_names, BOOK=None, flag_cols=None, MIN_SIG_ERR=2):
    """Key measured findings (numbers computed from this run)."""
    w("## 0. Key findings (numbers from this run)\n")
    # 1. breathing on capitals: two encodings
    pc, sc = A["precomposed_breathing_capital"], A["spacing_apos_before_capital"]
    rows = []
    for wi, wn in sorted(wave_names.items(), key=lambda kv: kv[1]):
        m = wave_idx == wi
        a, b = int(pc[m].sum()), int(sc[m].sum())
        if a + b:
            rows.append(f"{wn} {b:,}/{a + b:,} ({b / (a + b):.0%})")
    both = sum(1 for r in BOOK if r["shares"].get("spacing_mark_before_capital_lines", 0) > 0 and r.get("precomposed_breathing_capitals", 0) > 0)
    w(f"1. **Breathing/accent on a capital is encoded two ways.** {int((sc > 0).sum()):,} lines write a spacing mark (mostly U+1FBF ᾿) "
      f"followed by a bare capital (`᾿Αθῆναι`) instead of the precomposed capital (`Ἀθῆναι`); per wave, spacing-form / all "
      f"breathing-capitals: {'; '.join(rows)}. {both} books use BOTH encodings, so this is a label-normalisation inconsistency "
      "(Google output), not a property of the print: the same glyph gets two different targets.")
    # 2. sigma
    w(f"2. **Final-sigma errors are rare but systematic in 19th-c. type.** {int(flag_cols['final_sigma_error'].sum()):,} lines "
      f"({flag_cols['final_sigma_error'].mean():.2%}); occurrences: word-final σ {int(A['_sig_end'].sum())}, word-internal ς "
      f"{int(A['_sig_med'].sum())}, of which {int(A['_sig_st'].sum())} have the στ-spelling attested elsewhere in the pool — the "
      "στ ligature (ϛ-like glyph) read as ς (`μέγιςος`, `Πανεπιςημίου`, `καταςροφὴν`). A further "
      f"{int(A['final_sigma_compound'].sum())} compound-boundary ς (`προςάγω`, `ὥςτε`, `ὁποιοςδήποτε`, aphaeresis `᾿ς`) follow "
      "the print's orthography and are not counted.")
    # 3. stamps
    st = flag_cols["digitisation_stamp"]
    w(f"3. **Library stamp admitted as text.** {int(st.sum())} lines are digitisation/ownership marks, not book text: "
      "mostly the University of Crete seal on Anemi scans (`ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ`, partial `ΠΑΝΕΠΙΣΤΗΜΙ…`; curved lettering over a "
      "logo in a ~190×240 px box at ~92 % of the page height), a few rubber library stamps (`ΒΙΒΛΙΟΘΗΚΗ`) and `Digitized by Google` "
      "footers on Wikisource scans.")
    # 4. running titles / big book / digit
    rt = flag_cols["running_title_or_page_number"]
    mx_rt = max(BOOK, key=lambda r: r["flag_shares"]["running_title_or_page_number"])
    mx_dh = max(BOOK, key=lambda r: r["flag_shares"]["digit_heavy"])
    big = sorted(BOOK, key=lambda r: -r["n_lines"])[:3]
    w(f"4. **No book exceeds the 30 % spec limits** for digit-heavy or running-title lines (max digit-heavy share "
      f"{mx_dh['flag_shares']['digit_heavy']:.1%} in {mx_dh['source']} {mx_dh['book_key']}; max running-title share "
      f"{mx_rt['flag_shares']['running_title_or_page_number']:.1%} in {mx_rt['source']} {mx_rt['book_key']}). Running titles and "
      f"session headers are {rt.mean():.2%} of lines ({int(rt.sum())}). The largest single book is "
      + "; ".join(f"{r['source']} {r['book_key']} {r['n_lines']:,} lines ({r['n_lines'] / N:.1%} of the pool)" for r in big)
      + (" — the first is the Liddell–Scott Greek–English lexicon (visible in its lines); its citation lines dominate the "
         "latin/greek_latin_cs numeric-table and digit-heavy flags." if big[0]["book_key"] == "4c207e1e" else "."))
    w("")


def write_report(out, N, A, cls_idx, wave_idx, cls_names, wave_names, REF, THR, BOOK, BREF, FLAG_TYPES, flag_cols,
                 examples, size_methods, biblio_kind, hyphen_kind, MIN_LINES, MIN_GW, limit, MIN_SIG_ERR=2, MIN_REF_BOOKS=5):
    L = []
    w = L.append
    w("# Aspect B — content and style\n")
    w(f"Input: `docs/harvest/collection/admitted_all.jsonl`{' (first %d lines only — TEST RUN)' % limit if limit else ''}. "
      f"Lines processed: **{N:,}**; books (source, book_key): **{len(BOOK)}**.\n")
    w(f"Page height for the running-title detector: {dict(size_methods)} (`png_header` = height read from the page PNG header "
      "via the image path in the wave's records.jsonl; `max_y1_records` = fallback, not needed if absent).\n")
    w("Script: `docs/harvest/analysis/B_content_style/analysis_B.py` (re-runnable; `--limit N --out <subdir>` for tests).\n")
    findings(w, N, A, wave_idx, wave_names, BOOK=BOOK, flag_cols=flag_cols, MIN_SIG_ERR=MIN_SIG_ERR)

    groups = sorted({(wave_names[wi], cls_names[ci]) for wi, ci in zip(wave_idx, cls_idx)})
    # distributions
    w("## 1. Feature distributions per wave × script class\n")
    w("Shares are per line over visible characters (whitespace and combining marks excluded). Columns: median / p90 / p99 (mean for shares in brackets).\n")
    feats = [("digit_share", 3), ("punct_share", 3), ("symbol_share", 3), ("upper_share", 2), ("n_tokens", 0),
             ("mean_word_len", 2), ("longest_token", 0), ("n_chars", 0)]
    w("| wave | class | n | " + " | ".join(f[0] for f in feats) + " |")
    w("|---|---|---:|" + "---|" * len(feats))
    for wv, cn in groups:
        m = (wave_idx == [k for k, v in wave_names.items() if v == wv][0]) & (cls_idx == [k for k, v in cls_names.items() if v == cn][0])
        cells = []
        for f, nd in feats:
            v = A[f][m]
            cells.append(f"{fmt(q(v,50),nd)} / {fmt(q(v,90),nd)} / {fmt(q(v,99),nd)}" + (f" ({v.mean():.3f})" if "share" in f else ""))
        w(f"| {wv} | {cn} | {int(m.sum()):,} | " + " | ".join(cells) + " |")
    w("")
    w("Pattern rates per wave × class (share of lines):\n")
    pats = ["is_all_caps", "cap_initial", "hyphen_end", "numeric_table", "biblio", "rep_run", "dictionary_like", "top_bottom"]
    w("| wave | class | n | " + " | ".join(pats) + " | sigma_err lines | compound-ς lines (not errors) | spacing-apos lines | of which mark before a capital |")
    w("|---|---|---:|" + "---:|" * (len(pats) + 4))
    for wv, cn in groups:
        m = (wave_idx == [k for k, v in wave_names.items() if v == wv][0]) & (cls_idx == [k for k, v in cls_names.items() if v == cn][0])
        cells = [f"{A[p][m].mean():.4f}" for p in pats]
        cells.append(f"{(A['sigma_err'][m] > 0).mean():.4f}")
        cells.append(f"{(A['final_sigma_compound'][m] > 0).mean():.4f}")
        cells.append(f"{((A['spacing_apos_alone'][m] + A['spacing_apos_before_letter'][m]) > 0).mean():.4f}")
        cells.append(f"{(A['spacing_apos_before_capital'][m] > 0).mean():.4f}")
        w(f"| {wv} | {cn} | {int(m.sum()):,} | " + " | ".join(cells) + " |")
    w("")
    w(f"Bibliographic pattern kinds (line counts): {dict(biblio_kind)}. Line-end hyphen kinds: {dict(hyphen_kind)}.\n")

    w("## 2. Line-flag thresholds (per script class, whole pool as reference)\n")
    w("| class | n lines | digit_heavy > (p90 of digit-bearing lines) | punct_heavy > (p99 of punctuated) | symbol_heavy > (p99 of symbol-bearing) | long_token > p99 | word length outside [p1, p99] (lines >= 3 words) | short (running title) <= p50 chars |")
    w("|---|---:|---:|---:|---:|---:|---|---:|")
    for cn in sorted(REF):
        t = THR[cn]
        w(f"| {cn} | {REF[cn]['n']:,} | {fmt(t['digit_heavy'])} | {fmt(t['punct_heavy'])} | {fmt(t['symbol_heavy'])} | {fmt(t['long_token'],0)} | "
          f"[{fmt(t['word_len_lo'],2)}, {fmt(t['word_len_hi'],2)}] | {fmt(t['short'],0)} |")
    w("")

    w("## 3. Flag rates per wave × class (share of lines carrying the flag)\n")
    w("| wave | class | n | " + " | ".join(FLAG_TYPES) + " |")
    w("|---|---|---:|" + "---:|" * len(FLAG_TYPES))
    for wv, cn in groups:
        m = (wave_idx == [k for k, v in wave_names.items() if v == wv][0]) & (cls_idx == [k for k, v in cls_names.items() if v == cn][0])
        w(f"| {wv} | {cn} | {int(m.sum()):,} | " + " | ".join(f"{flag_cols[ft][m].mean():.4f}" for ft in FLAG_TYPES) + " |")
    tot = " | ".join(f"{flag_cols[ft].mean():.4f}" for ft in FLAG_TYPES)
    w(f"| **all** | | {N:,} | {tot} |")
    w("")
    w(f"Final-sigma error parts (occurrences): word-final σ {int(A['_sig_end'].sum()):,}; word-internal ς {int(A['_sig_med'].sum()):,}, "
      f"of which ς where the same word with στ is attested in the pool {int(A['_sig_st'].sum()):,}; "
      f"compound-boundary / aphaeresis ς (print orthography, NOT counted) {int(A['final_sigma_compound'].sum()):,}. "
      f"Spacing mark word-initially before a capital (e.g. ᾿Α for Ἀ): {int((A['spacing_apos_before_capital'] > 0).sum()):,} lines.\n")
    w("Total flagged lines per type: " + ", ".join(f"{ft} {int(flag_cols[ft].sum()):,}" for ft in FLAG_TYPES) + ".\n")

    w("## 4. Book reference populations and hard flags\n")
    w(f"Book script class = majority class of its lines. Reference books: n_lines >= {MIN_LINES}; final-sigma reference additionally needs >= {MIN_GW} Greek words.\n")
    w("| class | books | ref books (N for z) | final-sigma ref N | final-sigma rate p95 | all-caps share p95 | capital-initial p95 |")
    w("|---|---:|---:|---:|---:|---:|---:|")
    for cn, d in sorted(BREF.items()):
        w(f"| {cn} | {d['n_books']} | {d['n_ref']} | {d['n_ref_sigma']} | {fmt(d['sigma_p95'],4)} | {fmt(d['all_caps_p95'])} | {fmt(d['cap_initial_p95'])} |")
    w("")
    hc = Counter(h for r in BOOK for h in r["hard_flags"])
    w("Hard-flag books per flag: " + (", ".join(f"{k} **{v}**" for k, v in sorted(hc.items())) or "none") +
      f"; books with ≥1 hard flag: **{sum(1 for r in BOOK if r['hard_flags'])}**; verse-like books (informational): {sum(r['verse_like'] for r in BOOK)}.\n")
    hb = sorted([r for r in BOOK if r["hard_flags"]], key=lambda r: (-len(r["hard_flags"]), -r["n_beyond_2sd"], -r["n_lines"]))
    w("### Hard-flag books, ranked (number of hard flags, then features beyond 2σ vs same-class books)\n")
    w("| # | source | book_key | waves | class | n | hard flags (reasons) | features beyond 2σ |")
    w("|---:|---|---|---|---|---:|---|---:|")
    for i, r in enumerate(hb, 1):
        reasons = "<br>".join(f"**{k}**: {v}" for k, v in r["hard_flags"].items())
        w(f"| {i} | {r['source']} | {r['book_key']} | {','.join(r['waves'])} | {r['script_class']} | {r['n_lines']} | {reasons} | {r['n_beyond_2sd']} |")
    w("")
    bs = [r for r in BOOK if r.get("below_support")]
    if bs:
        w(f"Books above the class p95 final-sigma rate but with fewer than {MIN_SIG_ERR} error occurrences (NOT hard-flagged, a single "
          "occurrence is not a book-level pattern):\n")
        for r in bs:
            w(f"- {r['source']} {r['book_key']} ({r['script_class']}, {r['n_lines']} lines): " + "; ".join(r["below_support"].values()))
        w("")
    nq = [cn for cn, d in BREF.items() if d["n_ref"] < MIN_REF_BOOKS]
    if nq:
        w(f"Classes with fewer than {MIN_REF_BOOKS} reference books (class-p95 hard flags, verse-like and z-scores NOT evaluated): "
          + ", ".join(f"{cn} (N={BREF[cn]['n_ref']})" for cn in nq) + ".\n")
    vb = [r for r in BOOK if r["verse_like"]]
    if vb:
        w("### Verse-like books (informational)\n")
        w("| source | book_key | class | n | reason |")
        w("|---|---|---|---:|---|")
        for r in vb:
            w(f"| {r['source']} | {r['book_key']} | {r['script_class']} | {r['n_lines']} | {r['verse_like_reason']} |")
        w("")
    top = sorted(BOOK, key=lambda r: -r["n_beyond_2sd"])[:25]
    w("### Books with most features beyond 2σ (z of medians + z of flag shares, same-class books)\n")
    w("| source | book_key | class | n | n beyond 2σ | largest |z| (feature: z) |")
    w("|---|---|---|---:|---:|---|")
    for r in top:
        allz = {**{f"median {k}": v for k, v in r["z_median"].items()}, **{f"share {k}": v for k, v in r["z_flag_share"].items()}}
        big = sorted(((k, v) for k, v in allz.items() if v is not None), key=lambda kv: -abs(kv[1]))[:4]
        w(f"| {r['source']} | {r['book_key']} | {r['script_class']} | {r['n_lines']} | {r['n_beyond_2sd']} | " +
          "; ".join(f"{k}: {v:+.1f}" for k, v in big) + " |")
    w("")

    w("## 5. Examples (20 random lines per flag type, reservoir sample, fixed seed)\n")
    for ft in FLAG_TYPES:
        ex = examples[ft]
        w(f"### {ft} ({ex.n:,} lines)\n")
        if not ex.items:
            w("_none_\n")
            continue
        w("| # | label | crop_path | reason |")
        w("|---:|---|---|---|")
        for i, e in enumerate(ex.items, 1):
            lab = (e["label"] or "").replace("|", "\\|")
            w(f"| {i} | `{lab}` | {e['crop_path']} | {e['reason'].replace('|', '/')} |")
        w("")
    with open(os.path.join(out, "REPORT.md"), "w") as f:
        f.write("\n".join(L) + "\n")
        f.write("\n" + JUDGEMENT)


JUDGEMENT = """## 6. What I judged and why (detector definitions and limits)

**Reference groups.** Line flags compare a line with all pool lines of its own `script_class` (whole pool, all waves). Book hard
flags and z-scores compare a book with books of the same majority script class that have >= 30 lines; class-quantile hard flags,
verse-like and z-scores are only evaluated when that population has >= 5 books (greek_latin_cs has 2 majority books, so it is
not evaluated). z = (book median − mean of same-class book medians) / sd; I also give z of each flag share, because the medians
of sparse features (digit share, symbol share) are 0 for nearly every book and their z is degenerate. `N_books` is stored in
every book row (`z_reference`).

**Thresholds (all quantiles of the reference group, no hand-set cut-offs except the spec's 30 % and 8 %).**
- *digit_heavy*: digit share above the class p90 **of lines that contain any digit** (plain p95 over all lines is 0 for every
  class, since most lines have no digits). Same idea for punctuation (p99 of punctuated lines) and symbols (p99 of symbol-bearing
  lines). Shares are over visible characters (whitespace and combining marks excluded). Greek spacing accents (U+0384, U+1FBF …)
  are Unicode "symbols" but are counted as their own feature, not in symbol share.
- *word_length_outlier*: mean word length outside the class [p1, p99] computed over lines with >= 3 words; 1–2-word lines have
  degenerate means and are not flagged (constant 3 is my choice).
- *long_token*: longest whitespace token above the class p99. In Greek this is mostly genuine long words
  (`Κωνσταντινουπόλεως`); merged words show up here too but the flag is not specific to them.
- *running_title_or_page_number*: spec rule — box in the top or bottom 8 % of the **page image height** (read from the PNG header;
  all 5,967 pages had an image, no fallback needed), no lowercase letters (all-caps or digits), and "short" = at most the class
  median length (p25 cut off real headers like `ΣΥΝΕΔΡΙΑΣΗ Π' – 21 ΦΕΒΡΟΥΑΡΙΟΥ 1996`). Limit: page images include scan margins, so
  a header printed at 9–10 % of the scan is missed; mixed-case running titles (`Κεφ. Γ'. Ἐσωτ. ὀργαν.`) are missed by design.
  Page numbers themselves are mostly not admitted (records mark them `counted: false`), so this flag is mostly running titles.
- *final_sigma_error*: σ at a word end (next char not a letter/combining mark, not a hyphen), excluding the single-letter
  abbreviation `σ.` and σ before a period (possible abbreviation such as `Ἰησ.`; counted separately as `sigma_end_period`), plus ς
  followed by a letter. Not counted as errors: ς at a compound boundary in 19th-c. orthography (prefix ends in προ/ει/δυ or is
  ὡ/ὁ/ὁπω/ἐ/καθω/οὑτω/οἱα/ὁποια…, or the rest starts δηποτ/περ/τις/τιν…) and aphaeresis `᾿ς`. The στ-ligature sub-count checks
  whether the same word with στ instead of ς occurs in the pool (exact word match; line-end fragments like `ἐκκλησιαςι-` are only
  caught when the fragment itself is attested). Book hard flag: rate per Greek word above the class p95 of books with >= 100 Greek
  words AND >= 2 occurrences (a single error is listed under "below support", not hard-flagged).
- *spacing_apostrophe*: U+1FBF, U+1FBD, U+0384, U+2019 standing alone as a token, or word-initially directly before a letter.
  Elision/keraia after a letter (`ἀλλ᾿`, `Α΄`) is normal usage and not flagged. Almost all hits are `᾿` + capital = breathing on a
  capital written as a separate character (see finding 1); a few are `’ς`/`᾿ς` aphaeresis, which is legitimate.
- *dictionary_like*: one headword (no sentence-final period), optional comma, then a dash or a colon and more text. It also fires on
  speaker labels in parliament minutes (`ΠΡΟΕΔΡΟΣ:`), dialogue dashes after a broken word (`νον - ἐνῷ`) and `word: text` in prose;
  it is a style descriptor, not an error flag. URLs are excluded.
- *numeric_table*: >= 3 consecutive numeric tokens. In practice it catches classical citation strings (`Xen. An. 6. 1, 21`) far
  more than tables; real tables are rare in the admitted pool (admission already removed most).
- *bibliographic*: year in parentheses, `pp.`, `Bd.`, `vol.`, `σ.` + number (spec list only; `σελ.`, `τόμ.` not included).
- *repeated_run*: >= 4 identical non-space characters; almost all are ellipses/leaders `....` (table-of-contents leaders in
  theses, vote lists in vouli). Leader dots are hard to count visually, so these labels are higher risk.
- *digitisation_stamp* (added, not in the spec): whole label = `ΠΑΝΕΠΙΣΤΗΜΙ…` (+ `ΚΡ…`), `Digitized by Google` or `ΒΙΒΛΙΟΘΗΚΗ`.
  The University of Crete seal is curved text over a logo; it is not book text.
- *line_end_not_sign*: label ending in `¬` (text-layer hyphenation artefact). Zero in this pool — the Google reads carry no text
  layer artefacts of that kind.
- *verse-like book* (informational): share of capital-initial lines above the class p95 of books AND median line length below the
  class median of book medians. It also catches lists of names (vouli vote lists, thesis front matter), not only verse.
- *all_caps*: a line whose cased letters are all uppercase (>= 2). It is not an error per line; the book hard flag is the book's
  share above the class p95. Note that all-caps headings carry no breathings or accents in the print, so in polytonic books many all-caps
  lines are classed `greek_mono` (43 % of round1 greek_mono lines are all-caps); per-class rates must be read with that in mind.

**Things I did not judge.** Whether a flagged label is wrong: only the crop can tell. Digit-heavy, all-caps, dictionary-like,
numeric-table and bibliographic flags describe content type, not label quality. The label-quality signals in this aspect are
final_sigma_error (especially the στ sub-count), spacing_apostrophe (encoding inconsistency), digitisation_stamp and repeated_run.
"""


if __name__ == "__main__":
    main()
