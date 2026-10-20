#!/usr/bin/env python3
"""Aspect A — language and script analysis of the admitted real-line pool.

Re-runnable:  .venv/bin/python docs/harvest/analysis/A_language_script/analysis_A.py [--limit N] [--out DIR]
Streams docs/harvest/collection/admitted_all.jsonl twice (pass 1: reference
distributions + book majorities; pass 2: features again, flags, outputs).
Nothing outside the output folder is written. No network.
"""
from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import unicodedata as ud
from array import array
from collections import Counter, defaultdict
from functools import lru_cache

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
INPUT = os.path.join(REPO, "docs/harvest/collection/admitted_all.jsonl")
SEED = 20261015

# ----------------------------------------------------------------- scripts
OTHER_SCRIPT_WORDS = (
    "ARMENIAN", "HEBREW", "ARABIC", "SYRIAC", "COPTIC", "GEORGIAN", "DEVANAGARI", "BENGALI",
    "CJK", "IDEOGRAPHIC", "HIRAGANA", "KATAKANA", "HANGUL", "THAI", "ETHIOPIC", "RUNIC",
    "GOTHIC", "OLD ITALIC", "CHEROKEE", "CANADIAN", "MONGOLIAN", "TIBETAN", "GLAGOLITIC",
    "TIFINAGH", "SAMARITAN", "THAANA", "NKO", "LAO", "KHMER", "MYANMAR", "TAMIL", "TELUGU",
    "KANNADA", "MALAYALAM", "GUJARATI", "GURMUKHI", "ORIYA", "SINHALA", "PHOENICIAN",
    "LINEAR B", "CYPRIOT", "OGHAM", "BOPOMOFO", "YI ", "VAI ", "OSAGE", "ADLAM",
)
ROMAN = frozenset("IVXLCDMΙΧ")
# letters of script Y that look like letters of the line's majority script X (homoglyph-only words, soft flag)
LOOKALIKE = {("latin", "cyrillic"): set("ABCEHKMOPTXYaceopxyIiJjSs"),
             ("latin", "greek"): set("ABEHIKMNOPTXYZovu"),
             ("greek", "latin"): set("ΑΒΕΖΗΙΚΜΝΟΡΤΥΧο"),
             ("greek", "cyrillic"): set("ΑΒΕΗΚΜΟΡΤΧοα"),
             ("cyrillic", "greek"): set("АВЕНКМОРТХаоеру"),
             ("cyrillic", "latin"): set("АВСЕНКМОРТХУаеорсху")}  # admission exempts IVXLC + Greek Ι/Χ; D/M added for numerals
CLASS_EXPECTED = {
    "greek_poly": {"greek"}, "greek_mono": {"greek"},
    "greek_latin_cs": {"greek", "latin"},
    "latin": {"latin", "greek"},          # Latin-majority lines routinely quote Greek words
    "cyrillic": {"cyrillic", "latin"},    # Latin binomials / citations inside Cyrillic text
}


@lru_cache(maxsize=16384)
def char_script(ch: str):
    """('letter'|'mark'|'sym', script) for letters and script-named non-letters; None otherwise."""
    cat = ud.category(ch)
    name = ud.name(ch, "")
    kind = "letter" if cat.startswith("L") else ("mark" if cat.startswith("M") else "sym")
    for s in ("GREEK", "LATIN", "CYRILLIC"):
        if s in name:
            return kind, s.lower()
    if kind == "letter":
        return kind, "other"
    for w in OTHER_SCRIPT_WORDS:
        if w in name:
            return kind, "other"
    return None


@lru_cache(maxsize=16384)
def letter_script(ch: str):
    r = char_script(ch)
    return r[1] if r and r[0] == "letter" else None


def split_words(text: str) -> list[str]:
    """Space, = - / and Unicode punctuation delimit; combining marks stay attached (spec)."""
    out, cur = [], []
    for ch in text:
        if ch.isspace() or ch in "=-/" or ud.category(ch).startswith("P"):
            if cur:
                out.append("".join(cur)); cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return out


def strip_marks(s: str) -> str:
    return "".join(c for c in ud.normalize("NFD", s) if not ud.category(c).startswith("M"))


# ----------------------------------------------------------------- language lists
LATIN_FW = {
    "la": "et in est non ad cum ut sed quod qui quae quam ex e de per ab a sunt enim autem vel atque nec neque aut esse "
          "hoc haec etiam ac eius sive seu apud inter quoque tamen ergo igitur nisi sub pro super post ante quid quibus "
          "sibi se id ita sic ubi unde nam iam tam dum si erat fuit omnia omnes ipse illa ille".split(),
    "fr": "le la les de des du et est un une en que qui dans pour par sur au aux avec ce cette ces il elle ils ne pas plus "
          "son sa ses se sont été être mais ou où comme nous vous leur leurs à très tout tous y on".split(),
    "de": "der die das und ist nicht mit von den dem des ein eine einer eines einem zu auf im für sich auch als bei aus "
          "nach wie oder wird werden sind war wurde zur zum über durch an es er sie wir dass daß noch nur so ich man "
          "um vom diese dieser dieses".split(),
    "en": "the and of to is in that it for was on with as by be at this which from or are an were his her their have "
          "has had not but he she they we been its will would there these those also into a".split(),
    "it": "il lo la le gli di del della dello dei degli delle e è che non un una uno per con da dal dalla nel nella "
          "sul sulla al alla sono come più anche questo questa ma ed si ha".split(),
}
LATIN_ELISION = {"fr": ("l'", "d'", "qu'", "n'", "s'", "c'", "j'", "l’", "d’", "qu’", "n’", "s’", "c’", "j’"),
                 "it": ("dell'", "all'", "nell'", "sull'", "dall'", "un'", "dell’", "all’", "nell’", "sull’", "dall’", "un’")}
LATIN_CUE = {"fr": set("éèêçùûôîœëï"), "de": set("äöüß"), "it": set("ìò"), "la": set("æ")}

CYR_FW = {
    "ru": "и в во не на что с со по к ко как это он она оно они его ее её их для от из же бы был была было были так но "
          "или все всё при о об до также который которая которое которые которых только уже когда если чтобы этого "
          "этот эта эти тоже ни ли у будет есть нет мы вы я".split(),
    "bg": "и на в във за да се от с със не по са е ще като че това тази този тия които който която което към при или "
          "но до ги му ѝ той тя те им след още също бил била било били ни ли си беше бяха бъде из нѣ ся".split(),
    # Serbian: only words absent from the ru/bg lists, so shared words never tip a line to sr
    "sr": "је од што као ће су који која које али кад још бити био смо сте тај овај ова ово њега њих међу".split(),
}
CYR_CUE = {"ru": set("ыэ"), "sr": set("јљњћђџ"), "bg": set("ѫѭ")}
CYR_CUE_WEIGHT = {"ru": 1.0, "sr": 2.0, "bg": 1.0}
CYR_NORM = str.maketrans({"ѣ": "е", "і": "и", "ѳ": "ф", "ѵ": "и"})

LATIN_FW_SETS = {k: set(v) for k, v in LATIN_FW.items()}
CYR_FW_SETS = {k: set(v) for k, v in CYR_FW.items()}

# Greek register cues (matched on lower-cased, accent/breathing-stripped words; final ς kept as σ-normalised)
K_WORDS = {"εν", "εισ", "υπο", "δια", "ινα", "ητοι", "ουχι", "ουδε", "μηδε", "τω", "τοισ", "ταισ"}
D_WORDS = {"σε", "στον", "στην", "στη", "στο", "στα", "στουσ", "στισ", "για"}
DROP_N = set("βγδζθλμνρσςφχ")   # demotic drops article -ν before these (unless γκ/μπ/ντ/τσ/τζ)
KEEP_CLUSTERS = ("γκ", "μπ", "ντ", "τσ", "τζ")
POLY_MARKS = {"̓", "̔", "͂", "ͅ", "̀"}  # psili, dasia, perispomeni, ypogegrammeni, varia
TONOS_MARKS = {"́", "̈"}                                # acute/tonos, diaeresis


def guess_latin(words_raw: list[str], text_lower: str):
    score = Counter()
    for w in words_raw:
        wl = w.lower()
        for lang, s in LATIN_FW_SETS.items():
            if wl in s:
                score[lang] += 1
    for lang, pref in LATIN_ELISION.items():
        for p in pref:
            score[lang] += text_lower.count(" " + p) + (1 if text_lower.startswith(p) else 0)
    for lang, cues in LATIN_CUE.items():
        hit = len(cues & set(text_lower))
        if hit:
            score[lang] += 0.5 * hit
    return pick(score)


def guess_cyr(words_raw: list[str], text_lower: str):
    score = Counter()
    final_hard = False
    for w in words_raw:
        wl0 = w.lower().translate(CYR_NORM)
        wl = wl0
        if len(wl) > 1 and wl.endswith("ъ"):
            wl = wl[:-1]
            final_hard = True
        for lang, s in CYR_FW_SETS.items():
            if wl in s:
                score[lang] += 1
        if "ъ" in wl:  # word-internal ъ after removing the pre-reform final hard sign → Bulgarian cue
            score["bg"] += 0.5
        if len(wl0) >= 5 and (wl0.endswith("тѣ") or wl0.endswith("ътъ") or wl0.endswith("ятъ")):
            score["bg"] += 0.5          # postposed article (pre-1945 spelling): -тѣ, -ътъ, -ятъ
        if len(wl0) >= 5 and (wl0.endswith("ся") or wl0.endswith("сь") or wl0.endswith("аго") or wl0.endswith("яго")):
            score["ru"] += 0.5          # fused reflexive -ся/-сь, pre-reform adjective -аго/-яго
    for lang, cues in CYR_CUE.items():
        hit = len(cues & set(text_lower))
        if hit:
            score[lang] += CYR_CUE_WEIGHT[lang] * hit
    if final_hard:                       # Serbian Cyrillic has no ъ at all
        score.pop("sr", None)
    return pick(score)


def pick(score: Counter):
    if not score:
        return "unknown"
    best = score.most_common()
    if best[0][1] < 1 or (len(best) > 1 and best[1][1] == best[0][1]):
        return "unknown"
    return best[0][0]


# ----------------------------------------------------------------- features
def features(label: str, cls: str, book_script: str | None):
    # Script classification runs on the raw label (as admission does): NFC would turn e.g. U+0374 GREEK NUMERAL
    # SIGN into U+02B9 MODIFIER LETTER PRIME and invent an 'other' letter.
    text = label
    counts = Counter()
    for ch in text:
        s = letter_script(ch)
        if s:
            counts[s] += 1
    n_letters = sum(counts.values())
    shares = {s: round(counts[s] / n_letters, 4) if n_letters else 0.0 for s in ("greek", "latin", "cyrillic", "other")}
    majority = max(("greek", "latin", "cyrillic"), key=lambda s: counts[s]) if n_letters else None

    words = split_words(text)
    mixed = []
    script_words = defaultdict(list)
    wscripts = []
    for w in words:
        scripts = {letter_script(c) for c in w if letter_script(c)}
        wscripts.append(scripts)
        if len(scripts) >= 2 and not set(w) <= ROMAN:
            mixed.append(w)
        if len(scripts) == 1:
            script_words[next(iter(scripts))].append(w)

    # Residue (see REPORT section 7):
    #  other_script      letters of any non-Greek/Latin/Cyrillic script, or marks/symbols whose name names one;
    #  unexpected_*      letters (or script-named combining marks) of a script outside the class's expected set
    #                    (+ the book's majority script);
    #  isolated_*        an expected minority script present in the line ONLY as single-letter tokens.
    #  *_ref_letter      the single letter sits in/next to a number (Stephanus '591 B', '44D', 'σ. 100');
    #  *_standalone      a single letter with no number next to it (homoglyph suspect);
    #  *_word            a whole word of >=2 letters.
    # Roman-numeral tokens (only I V X L C D M / Greek Ι Χ) are excluded and counted apart.
    expected = set(CLASS_EXPECTED.get(cls, {"greek", "latin", "cyrillic"}))
    if book_script:
        expected.add(book_script)
    residue, kinds, roman_tokens = [], [], []
    has_digit = [any(ud.category(c) == "Nd" for c in w) for w in words]

    def ctx(i):
        nl = sum(1 for c in words[i] if letter_script(c))
        if has_digit[i]:
            return "alnum"
        if nl >= 2:
            return "word"
        near = has_digit[i] or (i > 0 and has_digit[i - 1]) or (i + 1 < len(words) and has_digit[i + 1])
        if near:
            return "ref_letter"
        lets = [c for c in words[i] if letter_script(c)]
        look = LOOKALIKE.get((letter_script(lets[0]), majority), set()) if lets else set()
        return "standalone_lookalike" if lets and lets[0] in look else "standalone"

    minority_single = {}
    for sc, ws in script_words.items():
        if sc != majority and sc != "other":
            minority_single[sc] = all(sum(1 for c in w if letter_script(c)) == 1 for w in ws if not set(w) <= ROMAN)
    for i, w in enumerate(words):
        if not wscripts[i]:
            continue
        if set(w) <= ROMAN and wscripts[i] != {majority}:
            roman_tokens.append(w)
            continue
        for ch in w:
            s = letter_script(ch)
            if not s:
                continue
            if s == "other":
                residue.append(ch); kinds.append("other_script")
            elif s not in expected:
                residue.append(ch); kinds.append("unexpected_" + ctx(i))
            elif s != majority and minority_single.get(s):
                residue.append(ch); kinds.append("isolated_" + ctx(i))
    for ch in text:
        r = char_script(ch)
        if r and r[0] != "letter" and (r[1] == "other" or (r[0] == "mark" and r[1] not in expected)):
            residue.append(ch); kinds.append("other_script" if r[1] == "other" else "unexpected_mark")
    residue_chars = sorted(set(residue))
    residue_kinds = sorted(set(kinds))
    homoglyph_words = []
    for i, w in enumerate(words):
        sc = wscripts[i]
        if len(sc) != 1 or majority in sc or has_digit[i] or set(w) <= ROMAN:
            continue
        y = next(iter(sc))
        lets = [c for c in w if letter_script(c)]
        look = LOOKALIKE.get((y, majority))
        if look and len(lets) >= 2 and all(c in look for c in lets):
            homoglyph_words.append(w)

    # language guess
    tl = ud.normalize("NFC", text).lower()
    if not n_letters:
        lang = "unknown"
    elif majority == "greek":
        lang = "el"
    elif majority == "latin":
        lang = guess_latin(script_words.get("latin", []), " " + tl)
    else:
        lang = guess_cyr(script_words.get("cyrillic", []), tl)

    # Greek diacritics (after NFD)
    greek_letters = poly = 0
    marked_letters = tonos_only_letters = 0
    cur_greek, cur_marks = False, set()

    def close():
        nonlocal marked_letters, tonos_only_letters
        if cur_greek and cur_marks:
            marked_letters += 1
            if cur_marks <= TONOS_MARKS:
                tonos_only_letters += 1

    for ch in ud.normalize("NFD", text):
        if ud.category(ch).startswith("M"):
            if cur_greek:
                cur_marks.add(ch)
                if ch in POLY_MARKS:
                    poly += 1
        else:
            close()
            cur_greek = letter_script(ch) == "greek"
            cur_marks = set()
            if cur_greek:
                greek_letters += 1
    close()
    mark_density = round(poly / greek_letters, 4) if greek_letters else None
    tonos_only = round(tonos_only_letters / marked_letters, 4) if marked_letters else None

    # register cues
    kat = dem = None
    kcues, dcues = [], []
    gw = [strip_marks(w).lower().replace("ς", "σ") for w in script_words.get("greek", [])]
    if lang == "el" and gw:
        for i, w in enumerate(gw):
            if w in K_WORDS:
                kcues.append(w)
            elif w in D_WORDS:
                dcues.append(w)
            elif len(w) >= 5 and w.endswith("εωσ"):
                kcues.append("-εως")
            elif len(w) >= 5 and (w.endswith("ουσι") or w.endswith("ουσιν")):
                kcues.append("-ουσι(ν)")
            elif len(w) >= 5 and w.endswith("ουν"):
                dcues.append("-ουν")
            if w in ("την", "τη") and i + 1 < len(gw):
                nxt = gw[i + 1]
                if nxt and nxt[0] in DROP_N and not nxt.startswith(KEEP_CLUSTERS):
                    (kcues if w == "την" else dcues).append(w + "+C")
        kat = round(len(kcues) / len(gw), 4)
        dem = round(len(dcues) / len(gw), 4)
    return {
        "shares": shares, "n_letters": n_letters, "majority_script": majority,
        "residue": residue_chars, "residue_names": [ud.name(c, f"U+{ord(c):04X}") for c in residue_chars],
        "residue_kinds": residue_kinds, "homoglyph_words": homoglyph_words,
        "roman_tokens": roman_tokens, "mixed_words": mixed, "lang_guess": lang,
        "greek_letters": greek_letters, "mark_density": mark_density, "tonos_only": tonos_only,
        "katharevousa_score": kat, "demotic_score": dem, "k_cues": kcues, "d_cues": dcues,
        "n_greek_words": len(gw),
    }


# ----------------------------------------------------------------- helpers
def q(arr, p):
    return float(np.quantile(arr, p)) if len(arr) else None


def fmt(x, nd=4):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{x:.{nd}f}" if isinstance(x, float) else str(x))


def stream(path, limit):
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit and i >= limit:
                break
            yield json.loads(line)


KIND_ORDER = ["other_script", "unexpected_word", "unexpected_mark", "unexpected_standalone_lookalike",
              "isolated_standalone_lookalike", "unexpected_standalone", "isolated_word", "isolated_standalone", "unexpected_alnum", "isolated_alnum", "unexpected_ref_letter", "isolated_ref_letter"]
EXPLAINED = ("_ref_letter", "_alnum")

BOOK_FEATS = ("greek_share", "latin_share", "cyrillic_share", "mark_density", "tonos_only",
              "katharevousa_score", "demotic_score")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    args = ap.parse_args()
    out = args.out
    os.makedirs(out, exist_ok=True)

    # ---------------- pass 1: book script majority (letters), book class, then features → references
    book_letters = defaultdict(Counter)
    book_class = defaultdict(Counter)
    book_wave = {}
    for r in stream(INPUT, args.limit):
        k = (r["source"], r["book_key"])
        book_wave.setdefault(k, Counter())[r["wave"]] += 1
        book_class[k][r["script_class"]] += 1
        for ch in r["label"]:
            s = letter_script(ch)
            if s:
                book_letters[k][s] += 1
    book_script = {k: c.most_common(1)[0][0] for k, c in book_letters.items()}
    book_major_class = {k: c.most_common(1)[0][0] for k, c in book_class.items()}

    cls_vals = defaultdict(lambda: defaultdict(lambda: array("d")))
    book_lang = defaultdict(Counter)
    for r in stream(INPUT, args.limit):
        k = (r["source"], r["book_key"])
        f = features(r["label"], r["script_class"], book_script[k])
        c = r["script_class"]
        for s in ("greek", "latin", "cyrillic"):
            cls_vals[c][s + "_share"].append(f["shares"][s])
        for name in ("mark_density", "tonos_only"):
            if f[name] is not None:
                cls_vals[c][name].append(f[name])
        book_lang[k][f["lang_guess"]] += 1

    def majority_lang(cnt: Counter):
        known = Counter({l: n for l, n in cnt.items() if l != "unknown"})
        if not known:
            return "unknown", 0.0
        l, n = known.most_common(1)[0]
        return l, n / sum(known.values())

    book_major_lang = {k: majority_lang(c) for k, c in book_lang.items()}
    # line-level class quantiles
    cls_q = {c: {name: {p: q(np.frombuffer(a, dtype="d"), p) for p in (0.01, 0.05, 0.5, 0.95, 0.99)}
                 for name, a in d.items()} for c, d in cls_vals.items()}
    del cls_vals

    # ---------------- pass 2: flags + outputs
    rng = random.Random(SEED)
    examples = defaultdict(list)         # flag -> reservoir of 20
    ex_seen = Counter()
    flag_counts = defaultdict(Counter)   # (wave, class) -> flag counts
    group_n = Counter()
    lang_by_group = defaultdict(Counter)
    dist = defaultdict(lambda: defaultdict(lambda: array("d")))  # (wave,class) -> feat -> values
    residue_char_counts = Counter()
    roman_counts = Counter()
    kcue_counts, dcue_counts = Counter(), Counter()
    per_book = defaultdict(lambda: {"feat": defaultdict(lambda: array("d")), "flags": Counter(), "n": 0,
                                    "lang": Counter(), "k": 0, "d": 0, "gw": 0, "class": Counter(),
                                    "residue_kinds": Counter(), "year": Counter()})
    residue_kind_by_group = defaultdict(Counter)
    residue_matrix, lang_ne_matrix = Counter(), Counter()
    n_lines = 0
    lf_path = os.path.join(out, "line_flags.jsonl.gz")
    with gzip.open(lf_path, "wt", encoding="utf-8", compresslevel=6) as lf:
        for r in stream(INPUT, args.limit):
            n_lines += 1
            k = (r["source"], r["book_key"])
            c, w = r["script_class"], r["wave"]
            f = features(r["label"], c, book_script[k])
            flags = []
            primary = None
            if f["residue"]:
                primary = min(f["residue_kinds"], key=KIND_ORDER.index)
                flags.append({"flag": "other_script_residue", "hard": True, "kind": primary, "kinds": f["residue_kinds"],
                              "reason": f"residue [{', '.join(f['residue_kinds'])}] chars {''.join(f['residue'])!r} ({'; '.join(f['residue_names'])}) in a "
                                        f"{c} line (expected scripts {sorted(CLASS_EXPECTED[c] | {book_script[k]})}; "
                                        f"letter shares G/L/C={f['shares']['greek']}/{f['shares']['latin']}/{f['shares']['cyrillic']}); "
                                        f"class reference: residue should be 0"})
            if f["homoglyph_words"]:
                flags.append({"flag": "homoglyph_word", "hard": False,
                              "reason": f"word(s) {f['homoglyph_words'][:5]} written only with letters that look like "
                                        f"{f['majority_script']} letters, in a {f['majority_script']}-majority {c} line "
                                        f"(class rate in REPORT §4)"})
            if f["mixed_words"]:
                flags.append({"flag": "mixed_word", "hard": True,
                              "reason": f"{len(f['mixed_words'])} mixed-script word(s) {f['mixed_words'][:5]}; admission requires 0"})
            ml, mshare = book_major_lang[k]
            if w != "mixed" and f["lang_guess"] not in ("unknown", ml) and ml != "unknown":
                flags.append({"flag": "lang_ne_book", "hard": True,
                              "reason": f"line language {f['lang_guess']} ≠ book majority {ml} "
                                        f"({mshare:.1%} of the book's {sum(book_lang[k].values())} lines with a guessed language)"})
            cq = cls_q.get(c, {})
            md = f["mark_density"]
            if c == "greek_poly" and md is not None and "mark_density" in cq:
                lo, hi = cq["mark_density"][0.01], cq["mark_density"][0.99]
                if md < lo:
                    flags.append({"flag": "mark_density_low", "hard": False,
                                  "reason": f"polytonic mark density {md:.4f} < greek_poly line p1 {lo:.4f}"})
                elif md > hi:
                    flags.append({"flag": "mark_density_high", "hard": False,
                                  "reason": f"polytonic mark density {md:.4f} > greek_poly line p99 {hi:.4f}"})
            if c == "greek_mono" and md:
                flags.append({"flag": "mono_with_poly_marks", "hard": False,
                              "reason": f"greek_mono line has mark density {md:.4f} (class p99 {cq['mark_density'][0.99]:.4f})"})
            # minority-script share outlier within the class
            dom = {"greek_poly": "greek", "greek_mono": "greek", "greek_latin_cs": "greek",
                   "latin": "latin", "cyrillic": "cyrillic"}[c]
            minority = round(1 - f["shares"][dom], 4)
            dom_q = cq.get(dom + "_share")
            if dom_q is not None and f["shares"][dom] < dom_q[0.01] and dom_q[0.01] < 1.0:
                flags.append({"flag": "script_share_outlier", "hard": False,
                              "reason": f"{dom} letter share {f['shares'][dom]:.4f} (minority {minority:.4f}) < {c} line p1 {dom_q[0.01]:.4f}"})
            row = {"id": r["id"], "source_key": f"{r['source']}/{r['book_key']}", "source": r["source"],
                   "book_key": r["book_key"], "wave": w, "script_class": c,
                   "features": {"script_shares": f["shares"], "n_letters": f["n_letters"],
                                "residue_chars": f["residue"], "residue_names": f["residue_names"],
                                "roman_tokens": f["roman_tokens"], "mixed_words": f["mixed_words"],
                                "homoglyph_words": f["homoglyph_words"],
                                "lang_guess": f["lang_guess"], "mark_density": md, "tonos_only": f["tonos_only"],
                                "katharevousa_score": f["katharevousa_score"], "demotic_score": f["demotic_score"],
                                "k_cues": f["k_cues"], "d_cues": f["d_cues"]},
                   "flags": flags}
            lf.write(json.dumps(row, ensure_ascii=False) + "\n")

            g = (w, c)
            group_n[g] += 1
            lang_by_group[g][f["lang_guess"]] += 1
            for s in ("greek", "latin", "cyrillic"):
                dist[g][s + "_share"].append(f["shares"][s])
            for name in ("mark_density", "tonos_only", "katharevousa_score", "demotic_score"):
                if f[name] is not None:
                    dist[g][name].append(f[name])
            for ch in f["residue"]:
                residue_char_counts[ch] += 1
            for t in f["roman_tokens"]:
                roman_counts[t] += 1
            kcue_counts.update(f["k_cues"]); dcue_counts.update(f["d_cues"])
            b = per_book[k]
            b["n"] += 1; b["class"][c] += 1; b["year"][r.get("year")] += 1
            b["lang"][f["lang_guess"]] += 1
            for s in ("greek", "latin", "cyrillic"):
                b["feat"][s + "_share"].append(f["shares"][s])
            if f["lang_guess"] == "el":
                for name in ("mark_density", "tonos_only", "katharevousa_score", "demotic_score"):
                    if f[name] is not None:
                        b["feat"][name].append(f[name])
                b["k"] += len(f["k_cues"]); b["d"] += len(f["d_cues"]); b["gw"] += f["n_greek_words"]
            if primary:
                b["residue_kinds"][primary] += 1
                residue_kind_by_group[g][primary] += 1
                rs = "+".join(sorted({letter_script(ch) or (char_script(ch) or ("", "other"))[1] for ch in f["residue"]}))
                residue_matrix[("explained" if primary.endswith(EXPLAINED) else "unexplained",
                                f["majority_script"], rs)] += 1
            for fl in flags:
                if fl["flag"] == "lang_ne_book":
                    lang_ne_matrix[(c, f["lang_guess"])] += 1
            for fl in flags:
                flag_counts[g][fl["flag"]] += 1
                b["flags"][fl["flag"]] += 1
                ekey = fl["flag"] + (":" + fl["kind"] if "kind" in fl else "")
                ex_seen[ekey] += 1
                item = {"id": r["id"], "source": r["source"], "book_key": r["book_key"], "label": r["label"],
                        "crop_path": r["crop_path"], "reason": fl["reason"]}
                res = examples[ekey]
                if len(res) < 20:
                    res.append(item)
                else:
                    j = rng.randrange(ex_seen[ekey])
                    if j < 20:
                        res[j] = item

    # ---------------- book stats
    def book_summary(k, b):
        s = {}
        for name in BOOK_FEATS:
            a = np.frombuffer(b["feat"][name], dtype="d") if name in b["feat"] else np.array([])
            s[name] = {"median": q(a, .5), "p10": q(a, .1), "p90": q(a, .9),
                       "mean": float(a.mean()) if len(a) else None, "n": int(len(a))}
        return s

    books = {}
    for k, b in per_book.items():
        ml, mshare = book_major_lang[k]
        foreign = sum(n for l, n in b["lang"].items() if l not in ("unknown", ml))
        books[k] = {"source": k[0], "book_key": k[1],
                    "wave": book_wave[k].most_common(1)[0][0], "n_lines": b["n"],
                    "year": b["year"].most_common(1)[0][0],
                    "majority_script_class": book_major_class[k], "script_class_counts": dict(b["class"]),
                    "majority_script": book_script[k], "majority_language": ml,
                    "majority_language_share": round(mshare, 4), "language_counts": dict(b["lang"]),
                    "other_language_lines": foreign, "other_language_share": round(foreign / b["n"], 4),
                    "register_k_cues": b["k"], "register_d_cues": b["d"], "greek_words": b["gw"],
                    "register_k_share": round(b["k"] / (b["k"] + b["d"]), 4) if (b["k"] + b["d"]) else None,
                    "features": book_summary(k, b), "flag_counts": dict(b["flags"]),
                    "residue_lines": b["flags"].get("other_script_residue", 0),
                    "residue_kind_counts": dict(b["residue_kinds"]),
                    "residue_lines_unexplained": sum(n for kd, n in b["residue_kinds"].items() if not kd.endswith(EXPLAINED))}
    # z-scores against books of the same majority script class
    # script shares are ~1.0 / 0.0 at the median for nearly every book, so they are z-scored by their MEAN;
    # sparse register rates likewise get a mean in addition to the median.
    ZFEATS = [(n, "median") for n in ("mark_density", "tonos_only", "katharevousa_score", "demotic_score")] + \
             [(n, "mean") for n in ("greek_share", "latin_share", "cyrillic_share", "katharevousa_score", "demotic_score")]
    ref = defaultdict(lambda: defaultdict(list))
    for k, bs in books.items():
        c = bs["majority_script_class"]
        for n, st in ZFEATS:
            v = bs["features"][n][st]
            if v is not None:
                ref[c][f"{n}_{st}"].append(v)
        ref[c]["other_language_share"].append(bs["other_language_share"])
        ref[c]["residue_line_share"].append(bs["residue_lines"] / bs["n_lines"])
        if bs["register_k_share"] is not None:
            ref[c]["register_k_share"].append(bs["register_k_share"])
    ref_stats = {c: {n: (float(np.mean(v)), float(np.std(v)), len(v), q(np.array(v), .05), q(np.array(v), .95))
                     for n, v in d.items()} for c, d in ref.items()}

    hard_counts = Counter()
    for k, bs in books.items():
        c = bs["majority_script_class"]
        z = {}
        vals = {f"{n}_{st}": bs["features"][n][st] for n, st in ZFEATS}
        vals["other_language_share"] = bs["other_language_share"]
        vals["residue_line_share"] = bs["residue_lines"] / bs["n_lines"]
        vals["register_k_share"] = bs["register_k_share"]
        for n, v in vals.items():
            if v is None or n not in ref_stats[c]:
                continue
            mu, sd, N, _, _ = ref_stats[c][n]
            z[n] = {"z": round((v - mu) / sd, 3) if sd > 0 else None, "value": round(v, 4), "ref_mean": round(mu, 4),
                    "ref_sd": round(sd, 4), "ref_N": N}
        bs["zscores"] = z
        bs["zscore_reference"] = f"books whose majority script_class is {c} (N={len(ref[c]['greek_share_mean'])})"
        bs["n_features_beyond_2sd"] = sum(1 for v in z.values() if v["z"] is not None and abs(v["z"]) > 2)
        hard = []
        if bs["residue_lines"]:
            hard.append({"flag": "other_script_residue", "explained_only": bs["residue_lines_unexplained"] == 0,
                         "reason": f"{bs['residue_lines']} of {bs['n_lines']} lines carry other-script residue "
                                   f"(by primary kind {bs['residue_kind_counts']}; {bs['residue_lines_unexplained']} not explained by "
                                   f"a number-adjacent reference letter or a letter+digit token) "
                                   f"({bs['residue_lines'] / bs['n_lines']:.2%}; same-class book p95 "
                                   f"{ref_stats[c]['residue_line_share'][4]:.2%})"})
        if bs["flag_counts"].get("mixed_word"):
            hard.append({"flag": "mixed_word", "reason": f"{bs['flag_counts']['mixed_word']} lines with mixed-script words (admission requires 0)"})
        if c == "greek_poly":
            md = bs["features"]["mark_density"]["median"]
            p5 = ref_stats[c]["mark_density_median"][3]
            if md is not None and md < p5:
                hard.append({"flag": "poly_mark_density_low",
                             "reason": f"median polytonic mark density {md:.4f} < p5 {p5:.4f} of greek_poly-class book medians "
                                       f"(N={ref_stats[c]['mark_density_median'][2]})"})
        if bs["wave"] != "mixed" and bs["majority_language"] != "unknown":
            share = bs["other_language_share"]
            if share > 0.02:
                tag = "greek_book_other_lang_gt2pct" if bs["majority_language"] == "el" else "book_other_lang_gt2pct"
                others = {l: n for l, n in bs["language_counts"].items() if l not in ("unknown", bs["majority_language"])}
                hard.append({"flag": tag,
                             "reason": f"{share:.2%} of lines guessed as another language than {bs['majority_language']} {others} > 2% "
                                       f"(same-class book p95 {ref_stats[c]['other_language_share'][4]:.2%})"})
        bs["hard_flags"] = hard
        for h in hard:
            hard_counts[h["flag"]] += 1

    with open(os.path.join(out, "book_stats.jsonl"), "w", encoding="utf-8") as fo:
        for k in sorted(books, key=lambda k: (-len(books[k]["hard_flags"]), -books[k]["n_features_beyond_2sd"], k)):
            fo.write(json.dumps(books[k], ensure_ascii=False) + "\n")

    # ---------------- report
    write_report(out, n_lines, books, group_n, residue_kind_by_group, residue_matrix, lang_ne_matrix, lang_by_group, dist, flag_counts, examples, hard_counts,
                 residue_char_counts, roman_counts, kcue_counts, dcue_counts, cls_q, ref_stats, ref)
    print(json.dumps({"lines": n_lines, "books": len(books), "hard_flag_books": dict(hard_counts),
                      "flag_lines": dict(ex_seen)}, ensure_ascii=False))


def write_report(out, n_lines, books, group_n, residue_kind_by_group, residue_matrix, lang_ne_matrix, lang_by_group, dist, flag_counts, examples, hard_counts,
                 residue_char_counts, roman_counts, kcue_counts, dcue_counts, cls_q, ref_stats, ref):
    L = []
    P = L.append
    P("# Aspect A — language and script (analysis of the admitted pool)\n")
    P(f"Generated by `analysis_A.py` (same folder). Input `docs/harvest/collection/admitted_all.jsonl`, {n_lines:,} lines, "
      f"{len(books)} source keys (source, book_key). Line flags in `line_flags.jsonl.gz`, per-book statistics in `book_stats.jsonl`.\n")
    groups = sorted(group_n)
    waves = sorted({g[0] for g in groups})
    classes = ["greek_poly", "greek_mono", "greek_latin_cs", "latin", "cyrillic"]

    # ---- key findings (numbers computed from this run)
    tot_res = sum(residue_matrix.values())
    unexpl = sum(n for (e, _, _), n in residue_matrix.items() if e == "unexplained")
    cyr_in_g = sum(n for (e, ms, rs), n in residue_matrix.items() if ms in ("greek", "latin") and "cyrillic" in rs and e == "unexplained")
    lat_in_g = sum(n for (e, ms, rs), n in residue_matrix.items() if ms == "greek" and rs == "latin" and e == "unexplained")
    lne = sum(lang_ne_matrix.values())
    lne_latin = sum(n for (cc, _), n in lang_ne_matrix.items() if cc == "latin")
    gb = [b for b in books.values() if any(h["flag"] == "greek_book_other_lang_gt2pct" for h in b["hard_flags"])]
    pl = [b for b in books.values() if any(h["flag"] == "poly_mark_density_low" for h in b["hard_flags"])]
    era = [b for b in books.values() if b["year"] and b["year"] < 1950 and b["majority_script_class"] == "greek_mono"]
    top5 = sorted((b["other_language_share"] for b in gb), reverse=True)[:5]
    era_oa = sum(1 for b in era if b["source"].startswith("openarchives"))
    P("## 0. Key findings\n")
    P(f"1. **Other-script residue is rare but real**: {tot_res} lines ({tot_res / n_lines:.2%}); {tot_res - unexpl} are explained "
      f"(a Latin letter inside/next to a number: formulas, units, Stephanus sections), {unexpl} are not. Of the unexplained: "
      f"{lat_in_g} Latin letters/words in Greek-majority lines (maths variables, acronyms, and look-alike capitals such as `A-` for `Ἀ-`), "
      f"{cyr_in_g} lines with Cyrillic letters in Greek- or Latin-majority text (DocAI reading Greek/Latin capitals as Cyrillic: `ВЕ`, `ОПР`, `По`, `Аг.`, `сатра-`) — "
      f"these are label errors the admission filter cannot see because each foreign token is a whole word in one script.")
    P(f"2. **Language mismatch is mostly genuine foreign-language text, concentrated in a few books**: {lne} lines differ from their "
      f"book's majority language (mixed wave exempt); {lne_latin} of them are Latin-script lines (fr/en/it/la/de quotations, "
      f"bibliography, bilingual editions) inside Greek books. {len(gb)} Greek books exceed 2 %; the top five are bilingual "
      f"({top5[-1]:.0%}–{top5[0]:.0%} other-language lines). Cyrillic books mostly trip the 2 % rule through ru/bg confusion of the function-word detector, "
      f"not through real mixing.")
    P(f"3. **Polytonic labelling consistency**: {len(pl)} polytonic-class books have a median mark density below the class p5; "
      f"their labels mix monotonic tonos with partial breathings (e.g. `σὖν`, `τῆς᾿ ενδόξου`, `ήσαν` in polytonic text) — Google "
      f"dropped or misplaced breathings, so these labels teach an inconsistent target. Separately, {len(era)} books with a recorded "
      f"year before 1950 have a monotonic majority (table in §5); {era_oa} are OpenArchives items whose metadata year is implausible "
      f"(e.g. NB-IoT text dated 1916), i.e. a year-metadata problem, not a script problem; the others are listed in §5 "
      f"(e.g. an 1852 parliament volume whose monotonic lines are member-name lists with capitals lacking breathings).\n")
    P("## 1. Lines per wave and script class\n")
    P("| wave | " + " | ".join(classes) + " | total |")
    P("|---|" + "---:|" * (len(classes) + 1))
    for w in waves:
        row = [group_n.get((w, c), 0) for c in classes]
        P(f"| {w} | " + " | ".join(f"{x:,}" for x in row) + f" | {sum(row):,} |")
    P("")

    P("## 2. Language guess per wave and script class\n")
    langs = ["el", "la", "fr", "de", "en", "it", "ru", "bg", "sr", "unknown"]
    P("| wave | class | n | " + " | ".join(langs) + " |")
    P("|---|---|---:|" + "---:|" * len(langs))
    for g in groups:
        cnt = lang_by_group[g]
        P(f"| {g[0]} | {g[1]} | {group_n[g]:,} | " + " | ".join(str(cnt.get(l, 0)) if cnt.get(l) else "" for l in langs) + " |")
    P("")

    def dist_table(feat, title, only=None, note=""):
        P(f"### {title}\n")
        if note:
            P(note + "\n")
        P("| wave | class | n | mean | p1 | p5 | p10 | median | p90 | p95 | p99 |")
        P("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
        for g in groups:
            if only and g[1] not in only:
                continue
            a = np.frombuffer(dist[g][feat], dtype="d") if feat in dist[g] else np.array([])
            if not len(a):
                continue
            P(f"| {g[0]} | {g[1]} | {len(a):,} | {a.mean():.4f} | " + " | ".join(f"{q(a, p):.4f}" for p in (.01, .05, .1, .5, .9, .95, .99)) + " |")
        P("")

    P("## 3. Feature distributions (line level)\n")
    dist_table("greek_share", "Greek letter share")
    dist_table("latin_share", "Latin letter share")
    dist_table("cyrillic_share", "Cyrillic letter share", only={"cyrillic", "latin"})
    dist_table("mark_density", "Polytonic mark density (Greek lines)", only={"greek_poly", "greek_mono", "greek_latin_cs"},
               note="Combining psili, dasia, perispomeni, ypogegrammeni and varia per Greek letter after NFD.")
    dist_table("tonos_only", "Tonos-only share (Greek lines)", only={"greek_poly", "greek_mono", "greek_latin_cs"},
               note="Among Greek letters carrying any mark, the share whose marks are only acute/tonos and/or diaeresis. "
                    "In polytonic text an oxia alone also counts (NFD makes it identical to tonos), so values near 0.4–0.6 are normal there.")
    dist_table("katharevousa_score", "Katharevousa cue rate (cues per Greek word, el lines)", only={"greek_poly", "greek_mono", "greek_latin_cs"})
    dist_table("demotic_score", "Demotic cue rate (cues per Greek word, el lines)", only={"greek_poly", "greek_mono", "greek_latin_cs"})

    P("### Line-level class reference quantiles used for flags\n")
    P("| class | feature | p1 | p5 | median | p95 | p99 |")
    P("|---|---|---:|---:|---:|---:|---:|")
    for c in classes:
        for feat, qs in sorted(cls_q.get(c, {}).items()):
            P(f"| {c} | {feat} | " + " | ".join(fmt(qs[p]) for p in (.01, .05, .5, .95, .99)) + " |")
    P("")

    P("## 4. Flag rates per wave and class (lines)\n")
    fl_names = ["other_script_residue", "mixed_word", "lang_ne_book", "homoglyph_word", "mark_density_low",
                "mark_density_high", "mono_with_poly_marks", "script_share_outlier"]
    P("| wave | class | n | " + " | ".join(fl_names) + " |")
    P("|---|---|---:|" + "---:|" * len(fl_names))
    tot = Counter()
    for g in groups:
        fc = flag_counts[g]
        tot.update(fc)
        P(f"| {g[0]} | {g[1]} | {group_n[g]:,} | " + " | ".join(
            f"{fc.get(f, 0)} ({fc.get(f, 0) / group_n[g]:.2%})" if fc.get(f) else "" for f in fl_names) + " |")
    P(f"| **all** | | {n_lines:,} | " + " | ".join(f"{tot.get(f, 0)} ({tot.get(f, 0) / n_lines:.2%})" for f in fl_names) + " |")
    P("\nHard line flags: other_script_residue, mixed_word, lang_ne_book (lang_ne_book is not raised in the mixed wave). "
      "The others are soft outlier flags against the line's script class.\n")

    P("### Residue lines by primary kind (most severe kind on the line)\n")
    P("| wave | class | " + " | ".join(KIND_ORDER) + " |")
    P("|---|---|" + "---:|" * len(KIND_ORDER))
    for g in groups:
        rk = residue_kind_by_group.get(g)
        if rk:
            P(f"| {g[0]} | {g[1]} | " + " | ".join(str(rk.get(kd, "")) for kd in KIND_ORDER) + " |")
    P("")
    P("### Residue lines by line majority script × residue script\n")
    P("`explained` = primary kind is `*_alnum` or `*_ref_letter` (letters in/next to numbers: formulas, units, Stephanus sections).\n")
    P("| explained? | line majority script | residue script(s) | lines |")
    P("|---|---|---|---:|")
    for (e, ms, rs), n in sorted(residue_matrix.items(), key=lambda x: -x[1]):
        P(f"| {e} | {ms} | {rs} | {n} |")
    P("")
    P("### lang_ne_book lines by line class × guessed language\n")
    P("| line class | guessed language | lines |")
    P("|---|---|---:|")
    for (cc, lg), n in sorted(lang_ne_matrix.items(), key=lambda x: -x[1]):
        P(f"| {cc} | {lg} | {n} |")
    P("")
    P("### Residue characters (lines containing each)\n")
    P("| char | code | name | lines |")
    P("|---|---|---|---:|")
    for ch, n in residue_char_counts.most_common(40):
        P(f"| {ch} | U+{ord(ch):04X} | {ud.name(ch, '?')} | {n} |")
    P("")
    P("Standalone Roman-numeral tokens in a minority script (excluded from residue): " +
      ", ".join(f"`{t}` {n}" for t, n in roman_counts.most_common(15)) + "\n")
    P("Register cue frequencies — katharevousa: " + ", ".join(f"`{t}` {n:,}" for t, n in kcue_counts.most_common()) +
      "; demotic: " + ", ".join(f"`{t}` {n:,}" for t, n in dcue_counts.most_common()) + "\n")

    P("## 5. Books\n")
    by_cls = Counter(b["majority_script_class"] for b in books.values())
    P("Book reference populations (books grouped by the majority script_class of their lines): " +
      ", ".join(f"{c} N={n}" for c, n in by_cls.most_common()) + ".\n")
    P("| book-level hard flag | books |")
    P("|---|---:|")
    for h in ("other_script_residue", "mixed_word", "poly_mark_density_low", "greek_book_other_lang_gt2pct", "book_other_lang_gt2pct"):
        P(f"| {h} | {hard_counts.get(h, 0)} |")
    P("")
    P("Book reference quantiles (same-class book populations):\n")
    P("| class | statistic | N | mean | sd | p5 | p95 |")
    P("|---|---|---:|---:|---:|---:|---:|")
    for c in classes:
        for n, (mu, sd, N, p5, p95) in sorted(ref_stats.get(c, {}).items()):
            P(f"| {c} | {n} | {N} | {mu:.4f} | {sd:.4f} | {fmt(p5)} | {fmt(p95)} |")
    P("")
    P("### Hard-flag books, ranked (number of hard flags, then share of residue + other-language lines)\n")
    P("| # | source | book_key | wave | class | n | maj. lang | other-lang | residue lines | register K-share | hard flags |")
    P("|---:|---|---|---|---|---:|---|---:|---:|---:|---|")
    hb = [b for b in books.values() if b["hard_flags"]]
    hb.sort(key=lambda b: (-len(b["hard_flags"]), -(b["residue_lines"] + b["other_language_lines"]) / b["n_lines"]))
    for i, b in enumerate(hb, 1):
        P(f"| {i} | {b['source']} | {b['book_key']} | {b['wave']} | {b['majority_script_class']} | {b['n_lines']} | "
          f"{b['majority_language']} ({b['majority_language_share']:.0%}) | {b['other_language_share']:.1%} | {b['residue_lines']} | "
          f"{fmt(b['register_k_share'], 2)} | " + "; ".join(h["flag"] for h in b["hard_flags"]) + " |")
    P("")
    P("### Era vs script: books with recorded year < 1950 but a greek_mono majority\n")
    P("| source | book_key | year | n | class counts | register K-share |")
    P("|---|---|---:|---:|---|---:|")
    for b in sorted(era, key=lambda b: b["year"]):
        P(f"| {b['source']} | {b['book_key']} | {b['year']} | {b['n_lines']} | {b['script_class_counts']} | {fmt(b['register_k_share'], 2)} |")
    P("")
    P("### Books most often beyond 2σ of their class (top 25 by count of |z|>2 features)\n")
    P("| source | book_key | class | n | features with |z|>2 |")
    P("|---|---|---|---:|---|")
    for b in sorted(books.values(), key=lambda b: -b["n_features_beyond_2sd"])[:25]:
        if not b["n_features_beyond_2sd"]:
            break
        zz = ", ".join(f"{n} z={v['z']:+.1f} ({v['value']})" for n, v in b["zscores"].items() if v["z"] is not None and abs(v["z"]) > 2)
        P(f"| {b['source']} | {b['book_key']} | {b['majority_script_class']} | {b['n_lines']} | {zz} |")
    P("")

    P("## 6. Example lines per flag type (≤20 random, seed 20261015)\n")
    for fl in sorted(examples):
        P(f"### {fl}\n")
        P("| # | label | crop_path | reason |")
        P("|---:|---|---|---|")
        for i, e in enumerate(examples[fl], 1):
            lab = e["label"].replace("|", "\\|")
            rea = e["reason"].replace("|", "\\|")
            P(f"| {i} | {lab} | `{e['crop_path']}` | {rea} |")
        P("")
    P(JUDGED)
    with open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def _lists_md():
    s = []
    for lang, ws in LATIN_FW.items():
        s.append(f"- {lang}: " + " ".join(ws))
    s.append("- elision prefixes: fr " + " ".join(LATIN_ELISION["fr"][:7]) + "; it " + " ".join(LATIN_ELISION["it"][:6]))
    s.append("- letter cues (+0.5 per distinct letter): " + "; ".join(f"{k} {''.join(sorted(v))}" for k, v in LATIN_CUE.items()))
    for lang, ws in CYR_FW.items():
        s.append(f"- {lang}: " + " ".join(ws))
    s.append("- Cyrillic letter cues (+1 per distinct letter): " + "; ".join(f"{k} {''.join(sorted(v))}" for k, v in CYR_CUE.items())
             + "; word-internal ъ (after dropping a pre-reform word-final ъ) +0.5 bg")
    s.append("- Greek katharevousa words: " + " ".join(sorted(K_WORDS)) + "; endings -εως (word ≥5 letters), -ουσι(ν) (≥5); "
             "`την` before a consonant where demotic drops -ν (β γ δ ζ θ λ μ ν ρ σ φ χ, not γκ μπ ντ τσ τζ)")
    s.append("- Greek demotic words: " + " ".join(sorted(D_WORDS)) + "; ending -ουν (≥5); `τη` before such a consonant")
    return "\n".join(s)


JUDGED = None  # filled below (needs the lists)

JUDGED_TEMPLATE = """## 7. What I judged and why (detector definitions and limits)

- **Source key** = (source, book_key). Every wave carries a per-document `book_key`, so no other field was needed. One source key = one book/volume/document.
- **Script of a letter** = Unicode name contains GREEK / LATIN / CYRILLIC (the same rule as admission); any other letter is `other`.
  Script letter shares are computed over letters only (digits/punctuation excluded), after NFC.
- **Mixed-script words**: split on whitespace, `= - /` and every Unicode punctuation character; words whose letters come from ≥2 scripts,
  Roman-numeral words (only I V X L C D M and Greek Ι Χ) excluded. Admission already rejects these, so the expected count is 0.
- **Other-script residue** (hard line flag). Three sources: (1) any `other`-script letter, or a combining mark / symbol whose Unicode name
  names another script (Armenian, Hebrew, Coptic, …); (2) letters (or script-named combining marks) of a script outside the line class's expected set —
  greek_poly/greek_mono: Greek; greek_latin_cs: Greek+Latin; latin: Latin+Greek; cyrillic: Cyrillic+Latin — always plus the book's majority script
  (so English headwords in a Cyrillic dictionary are not residue); (3) a minority script present in the line ONLY as single-letter tokens (homoglyph suspects such as a
  Latin `O` or `x` standing alone in Greek text). Tokens made only of Roman-numeral letters (I V X L C D M, Greek Ι Χ) are excluded everywhere and counted separately.
  Each residue line gets a kind by context of the offending token: `*_alnum` (letters inside a token with digits: `44D`, `H2O`, `CO2`),
  `*_ref_letter` (a single letter next to a number: Stephanus/Bekker sections `591 B`, `σ. 100`), `*_standalone_lookalike` (a single letter with no number
  that has a look-alike in the line's majority script — the homoglyph-error suspects, e.g. Latin `A-` for `Ἀ-`, Latin `e` for Cyrillic `е`),
  `*_standalone` (a single letter without such a look-alike, e.g. the Greek article `ὁ` heading an English dictionary gloss, `q. v.`), `*_word` (a whole foreign-script word, e.g. Cyrillic `ВЕ` in Greek text), `other_script`, `unexpected_mark`.
  `*_alnum` and `*_ref_letter` are usually correct transcriptions of real Latin letters; the book hard flag keeps them (spec) but states how many residue lines
  are NOT of these explained kinds (`residue_lines_unexplained`, `explained_only`).
- **homoglyph_word** (soft, my addition): a word of ≥2 letters, in a script other than the line's majority script, whose letters ALL have look-alikes in the
  majority script (e.g. Latin `Ha`/`ce` in a Cyrillic line = `На`/`се`; Latin `TOD` in a Greek line). Genuine acronyms (`IBM`, `MOT`) also match, so it is soft.
  Limit: (3) also catches genuine one-letter Latin initials in a Greek line when no full Latin word sits on the same line (e.g. "ὁ κ. P. Smith" is fine because of
  "Smith", but "ὁ P." alone is flagged); legitimate single-letter section markers are flagged too — they are listed in the examples so the adjudicator can judge.
- **Language guess**: majority (plurality) letter script decides the family. Greek-majority → `el` (spec). Latin-majority → la/fr/de/en/it by counting
  function-word hits (ambiguous words such as `in`, `et`, `la` score for every language that has them), elision prefixes and accented-letter cues;
  Cyrillic-majority → ru/bg/sr likewise, after normalising pre-reform ѣ→е, і→и, ѳ→ф, ѵ→и and dropping a word-final ъ. The top score must be ≥1 and unique,
  otherwise `unknown`. Cyrillic tie-breakers on top of the function words: ы/э +1 ru; ј љ њ ћ ђ џ +2 sr each; ѫ ѭ +1 bg; word-internal ъ +0.5 bg;
  words (≥5 letters) ending -тѣ/-ътъ/-ятъ (postposed article) +0.5 bg; ending -ся/-сь/-аго/-яго +0.5 ru; a word-final ъ (pre-reform spelling) removes sr
  (Serbian Cyrillic has no ъ). The Serbian list holds only words absent from the ru/bg lists. Short Latin/Cyrillic lines without function words (names, citations, binomials, dictionary headwords) are therefore `unknown`, and
  `unknown` is never counted as a language mismatch. Ukrainian, Church Slavonic, Spanish etc. are not in the label set: they fall into the nearest
  listed language or `unknown` (a Ukrainian line usually scores as ru or bg).
- **lang_ne_book** (hard line flag): line language (not unknown) ≠ the book's majority language among lines with a guessed language; not raised in the
  mixed wave (spec). Greek books with >2 % of lines in another language get the book hard flag `greek_book_other_lang_gt2pct` (mixed wave exempt,
  since mixed-language books were collected on purpose); I applied the same 2 % rule to non-Greek books as `book_other_lang_gt2pct` — an extension of the spec,
  reported separately because Cyrillic ru/bg/sr discrimination by function words is noisy on single lines.
- **Mark density**: combining psili U+0313, dasia U+0314, perispomeni U+0342, ypogegrammeni U+0345 and varia U+0300 per Greek letter after NFD. Spacing
  breathings (U+1FBF, U+1FBD, U+1FFE before capitals) are not counted (they do not decompose under NFD); this slightly lowers density in all-caps-heavy lines.
  `mark_density_low/high` (soft) compare a greek_poly line with the greek_poly line p1/p99. `mono_with_poly_marks` checks greek_mono lines (should be impossible
  by the admission classifier; expected 0).
- **Book-level `poly_mark_density_low`**: the book's majority script class is greek_poly and its median mark density over its `el` lines is below p5 of
  the greek_poly book medians (so ~5 % of polytonic books are flagged by construction; the reason states the value and p5).
- **Tonos-only share**: among Greek letters with any mark, the share whose marks are only acute/tonos and/or diaeresis.
- **Register cues** (katharevousa vs demotic), counted on lower-cased words with all marks removed and ς→σ, as cues per Greek word in `el` lines; book-level
  `register_k_share` = K cues / (K + D cues). Cue words are frequent but crude: `υπο`, `δια`, `για` and `-ουν` occur in both registers, and the `την`+consonant cue
  only says the text keeps the final ν. Use it as a book-level tendency, never on single lines; no line flag is raised on register.
- **Z-scores**: each book's statistic against the mean and population SD of books of the same majority script_class (`ref_N` stored with every z):
  medians of mark density, tonos-only share and the register rates; MEANS of the script letter shares (their medians are 1.0/0.0 for almost every book)
  and of the register rates; plus other-language share, residue-line share and register K-share. z is null when the reference SD is 0. Small populations (greek_latin_cs, latin) give unstable z-scores.
- **Script-share outlier** (soft): the line's dominant-script share below its class p1 (only when p1 < 1).

### Function-word and cue lists used (in full)

{lists}
"""
JUDGED = JUDGED_TEMPLATE.format(lists=_lists_md())

if __name__ == "__main__":
    main()
