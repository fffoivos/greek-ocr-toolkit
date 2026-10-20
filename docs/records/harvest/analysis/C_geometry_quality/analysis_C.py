#!/usr/bin/env python3
"""Aspect C — length, geometry and label-quality proxies for the admitted real-line pool.

Follows docs/harvest/analysis/SPECS.md ("Aspect C" + general rules).

Run from the repo root:
    .venv/bin/python docs/harvest/analysis/C_geometry_quality/analysis_C.py            # full pool
    .venv/bin/python docs/harvest/analysis/C_geometry_quality/analysis_C.py --limit 20000 --out <dir>

Streams the pool jsonl and the per-wave records.jsonl; never opens crops (crop width/height come from the pool);
page heights come from PNG headers only (PIL lazy open, no pixel decode).
"""
import argparse
import collections
import gzip
import json
import math
import os
import random
import re
import sys
import unicodedata
from array import array

import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
POOL = os.path.join(ROOT, "docs/harvest/collection/admitted_all.jsonl")
HARVEST = os.path.join(ROOT, "docs/harvest")
WIKI_TRANS = os.path.join(HARVEST, "wikisource/cleaned_transcriptions")
HERE = os.path.dirname(os.path.abspath(__file__))

MIN_REF_BOOKS = 10          # book-level quantile hard flags need >= 10 same-class reference books (greek_latin_cs has 2)
MIN_BOOK_LINES = 20          # books with fewer lines are excluded from book reference populations / hard flags
HEIGHT_HI, HEIGHT_LO, HEIGHT_BOOK_SHARE = 1.7, 0.5, 0.10   # spec constants
N_EXAMPLES = 20
SEED = 20261015

HYPHENS = ("-", "‐", "‑", "¬", "⸗")
try:
    import regex as _re2
    STRIP_RE = _re2.compile(r"^[^\p{L}\p{M}]+|[^\p{L}\p{M}]+$")
    LETTER_RE = _re2.compile(r"\p{L}")
    DIGIT_RE = _re2.compile(r"\p{N}")
except ImportError:  # pragma: no cover
    STRIP_RE = re.compile(r"^[\W\d_]+|[\W\d_]+$")
    LETTER_RE = re.compile(r"[^\W\d_]")
    DIGIT_RE = re.compile(r"\d")


def records_path(wave):
    if wave == "round1":
        return os.path.join(HARVEST, "round1/records_all.jsonl")
    return os.path.join(HARVEST, wave, "records.jsonl")


def ends_hyphen(text):
    return bool(text) and text.rstrip().endswith(HYPHENS)


def tokens(label, drop_first, drop_last):
    """NFC-lowercased word tokens; edge punctuation stripped; tokens with digits or <2 letters skipped;
    line-final hyphen fragment and (if the previous line ended in a hyphen) the line-initial continuation dropped."""
    parts = unicodedata.normalize("NFC", label).split()
    if drop_last and parts:
        parts = parts[:-1]
    if drop_first and parts:
        parts = parts[1:]
    out = []
    for p in parts:
        w = STRIP_RE.sub("", p)
        if not w or DIGIT_RE.search(w):
            continue
        if len(LETTER_RE.findall(w)) < 2:
            continue
        out.append(unicodedata.normalize("NFC", w.lower()))
    return out


def q(arr, p):
    arr = arr[~np.isnan(arr)]
    return float(np.percentile(arr, p)) if arr.size else float("nan")


def fmt(x, nd=3):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(float(x), nd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=HERE)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    log = lambda *a: print(*a, file=sys.stderr, flush=True)

    # ---------------- pass 1 over the pool: metadata ----------------
    ids, wave_i, book_i, cls_i, page_keys = [], array("i"), array("i"), array("i"), []
    label_len, crop_w, crop_h, conf_mean = array("d"), array("d"), array("d"), array("d")
    nonspace_len = array("i")
    pool_bbox = []
    waves, classes, books = {}, {}, {}
    pages_needed = collections.defaultdict(set)
    with open(POOL, encoding="utf-8") as fh:
        for n, line in enumerate(fh):
            if args.limit and n >= args.limit:
                break
            r = json.loads(line)
            w = waves.setdefault(r["wave"], len(waves))
            c = classes.setdefault(r["script_class"], len(classes))
            b = books.setdefault((r["source"], r["book_key"]), len(books))
            ids.append(r["id"]); wave_i.append(w); cls_i.append(c); book_i.append(b)
            page_keys.append(r["page_id"])
            lab = unicodedata.normalize("NFC", r["label"])
            label_len.append(len(lab)); nonspace_len.append(len("".join(lab.split())))
            crop_w.append(r["crop_width"]); crop_h.append(r["crop_height"])
            conf_mean.append(r["confidence"] if r["confidence"] is not None else float("nan"))
            pool_bbox.append(r["bbox"])
            pages_needed[r["wave"]].add(r["page_id"])
    N = len(ids)
    wave_names = {v: k for k, v in waves.items()}
    class_names = {v: k for k, v in classes.items()}
    book_names = {v: k for k, v in books.items()}
    log(f"pool lines={N} books={len(books)} waves={sorted(waves)}")
    want = {(wave_names[wave_i[i]], ids[i]): i for i in range(N)}

    # ---------------- records pass: page context ----------------
    sym_count = array("d", [float("nan")]) * N
    conf_min = array("d", [float("nan")]) * N
    prev_hyph = bytearray(N)
    rec_bbox = [None] * N
    page_ctx = {}    # (wave, page_id) -> dict
    pid_re = re.compile(r'"page_id":\s*"([^"]+)"')
    diag = collections.Counter()
    for wave in sorted(pages_needed):
        need = pages_needed[wave]
        path = records_path(wave)
        per_page = {}
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                m = pid_re.search(line, 0, 400)
                if not m or m.group(1) not in need:
                    continue
                r = json.loads(line)
                pid = r["page_id"]
                st = per_page.get(pid)
                if st is None:
                    st = per_page[pid] = {"lines": [], "image": r.get("image")}
                bb = r["bbox"]
                text = r.get("label") or r.get("docai_text") or ""
                st["lines"].append((r.get("line_number") or 0, bool(r.get("counted")), bb, ends_hyphen(r.get("docai_text") or text), r["id"]))
                i = want.get((wave, r["id"]))
                if i is not None:
                    sc = r.get("symbol_count")
                    sym_count[i] = float(sc) if sc is not None else float("nan")
                    mc = r.get("min_confidence")
                    conf_min[i] = float(mc) if mc is not None else float("nan")
                    rec_bbox[i] = bb
                    diag[f"{wave}:matched"] += 1
        for pid, st in per_page.items():
            ls = sorted(st["lines"], key=lambda t: t[0])
            counted = [t for t in ls if t[1]] or ls
            hs = [t[2][3] - t[2][1] for t in counted]
            x0 = min(t[2][0] for t in counted); x1 = max(t[2][2] for t in counted)
            ymax = max(t[2][3] for t in ls)
            ph = None
            img = st["image"]
            if img and os.path.exists(os.path.join(ROOT, img)):
                try:
                    with Image.open(os.path.join(ROOT, img)) as im:
                        ph = im.size[1]
                except Exception:
                    ph = None
            if ph is None:
                diag[f"{wave}:page_height_fallback"] += 1
                ph = ymax
            page_ctx[(wave, pid)] = (float(np.median(hs)), float(x1 - x0), float(ph), len(counted))
            prev = False
            for t in ls:
                i = want.get((wave, t[4]))
                if i is not None:
                    prev_hyph[i] = 1 if prev else 0
                prev = t[3]
        log(f"records {wave}: pages={len(per_page)}/{len(need)} matched={diag[wave + ':matched']}")
    diag_missing = collections.Counter(wave_names[wave_i[i]] for i in range(N) if rec_bbox[i] is None)

    # ---------------- pass 2 over the pool: vocabulary ----------------
    word_idx, word_list = {}, []
    word_first_book, word_books, word_tok = array("i"), {}, array("i")
    tok_flat, tok_off = array("i"), array("i", [0])
    rep_word = [""] * N
    with open(POOL, encoding="utf-8") as fh:
        for n, line in enumerate(fh):
            if n >= N:
                break
            r = json.loads(line)
            lab = r["label"]
            raw = unicodedata.normalize("NFC", lab).split()
            for a_, b_ in zip(raw, raw[1:]):
                if a_ == b_ and len(LETTER_RE.findall(a_)) >= 3:
                    rep_word[n] = a_
                    break
            toks = tokens(lab, prev_hyph[n], ends_hyphen(lab))
            b = book_i[n]
            for t in toks:
                k = word_idx.get(t)
                if k is None:
                    k = word_idx[t] = len(word_list); word_list.append(t)
                    word_first_book.append(b); word_tok.append(0)
                else:
                    if word_first_book[k] != b:
                        s = word_books.get(k)
                        if s is None:
                            word_books[k] = {word_first_book[k], b}
                        else:
                            s.add(b)
                word_tok[k] += 1
                tok_flat.append(k)
            tok_off.append(len(tok_flat))
    support = np.array([len(word_books[k]) if k in word_books else 1 for k in range(len(word_list))], dtype=np.int32)
    log(f"vocab words={len(word_list)} tokens={len(tok_flat)}")

    # Wikisource human vocabulary (el pages only), word -> set of wikisource book keys
    ws_vocab = {}
    ws_pages = ws_lines = 0
    for f in sorted(os.listdir(WIKI_TRANS)):
        if not f.endswith(".json"):
            continue
        d = json.load(open(os.path.join(WIKI_TRANS, f), encoding="utf-8"))
        if d["page"].get("lang") != "el":
            continue
        ws_pages += 1
        key = d["page"]["key"]
        prev = False
        for ln in d.get("lines", []):
            if not ln.get("usable", True):
                continue
            ws_lines += 1
            txt = ln["text"]
            for t in tokens(txt, prev, ends_hyphen(txt)):
                ws_vocab.setdefault(t, set()).add(key)
            prev = ends_hyphen(txt)
    log(f"wikisource vocab: pages={ws_pages} lines={ws_lines} words={len(ws_vocab)}")

    # ---------------- features ----------------
    F = {}
    lw = np.frombuffer(label_len, dtype=np.float64)
    cw = np.frombuffer(crop_w, dtype=np.float64); ch = np.frombuffer(crop_h, dtype=np.float64)
    F["label_len"] = lw.copy()
    F["crop_w"] = cw.copy(); F["crop_h"] = ch.copy()
    F["chars_per_100px"] = lw / np.where(cw > 0, cw, np.nan) * 100.0
    F["chars_per_height"] = lw * ch / np.where(cw > 0, cw, np.nan)   # chars per line-height of width: DPI-invariant density
    F["aspect"] = cw / np.where(ch > 0, ch, np.nan)
    hr, wr, yr = (np.full(N, np.nan) for _ in range(3))
    for i in range(N):
        bb = rec_bbox[i] or pool_bbox[i]
        ctx = page_ctx.get((wave_names[wave_i[i]], page_keys[i]))
        if ctx is None or bb is None:
            continue
        mh, tw, ph, _ = ctx
        h = bb[3] - bb[1]; w = bb[2] - bb[0]
        hr[i] = h / mh if mh > 0 else np.nan
        wr[i] = w / tw if tw > 0 else np.nan
        yr[i] = ((bb[1] + bb[3]) / 2.0) / ph if ph > 0 else np.nan
    F["height_ratio"], F["width_ratio"], F["y_rel"] = hr, wr, yr
    ns = np.frombuffer(nonspace_len, dtype=np.int32).astype(np.float64)
    sc = np.frombuffer(sym_count, dtype=np.float64)
    F["symbol_mismatch"] = ns - sc                     # label non-space chars minus Google symbol count (signed)
    F["symbol_mismatch_rel"] = np.abs(ns - sc) / np.maximum(ns, 1.0)
    F["conf_mean"] = np.frombuffer(conf_mean, dtype=np.float64).copy()
    F["conf_min"] = np.frombuffer(conf_min, dtype=np.float64).copy()
    poly_c = classes.get("greek_poly", -999)
    ws_book_key = {b: k[1] for k, b in books.items() if k[0] == "wikisource_el"}
    oov_p, oov_w = np.full(N, np.nan), np.full(N, np.nan)
    ntok = np.zeros(N, dtype=np.int32)
    n_oov_p = np.zeros(N, dtype=np.int32); n_oov_w = np.zeros(N, dtype=np.int32)
    for i in range(N):
        a, z = tok_off[i], tok_off[i + 1]
        ntok[i] = z - a
        if z == a:
            continue
        ks = tok_flat[a:z]
        o = sum(1 for k in ks if support[k] <= 1)
        n_oov_p[i] = o; oov_p[i] = o / (z - a)
        if cls_i[i] == poly_c:
            own = ws_book_key.get(book_i[i])
            ow = 0
            for k in ks:
                s = ws_vocab.get(word_list[k])
                if not s or (own is not None and s == {own}):
                    ow += 1
            n_oov_w[i] = ow; oov_w[i] = ow / (z - a)
    F["oov_pool"], F["oov_wikisource"] = oov_p, oov_w
    cls_arr = np.frombuffer(cls_i, dtype=np.int32); wave_arr = np.frombuffer(wave_i, dtype=np.int32)
    book_arr = np.frombuffer(book_i, dtype=np.int32)

    # per-book median chars_per_100px for the within-book density ratio
    book_cpp_med = {}
    for b in range(len(books)):
        m = book_arr == b
        book_cpp_med[b] = float(np.nanmedian(F["chars_per_100px"][m]))
    F["cpp_vs_book"] = F["chars_per_100px"] / np.array([book_cpp_med[b] for b in book_arr])
    book_len_med = {b: float(np.median(F["label_len"][book_arr == b])) for b in range(len(books))}
    F["len_vs_book"] = F["label_len"] / np.array([book_len_med[b] for b in book_arr])

    # ---------------- class quantiles and line flags ----------------
    feats = ["label_len", "crop_w", "crop_h", "chars_per_100px", "chars_per_height", "cpp_vs_book", "len_vs_book", "height_ratio",
             "width_ratio", "y_rel", "aspect", "symbol_mismatch", "symbol_mismatch_rel", "conf_mean", "conf_min",
             "oov_pool", "oov_wikisource"]
    CQ = {}
    for c, cname in class_names.items():
        m = cls_arr == c
        CQ[cname] = {f: {p: q(F[f][m], p) for p in (1, 2, 5, 10, 50, 90, 95, 98, 99)} for f in feats}
    # line-level OOV flag reference: lines with >= 3 tokens
    oov_ref = {}
    for c, cname in class_names.items():
        m = (cls_arr == c) & (ntok >= 3)
        oov_ref[cname] = (q(F["oov_pool"][m], 99), int(m.sum()))

    FLAG_TYPES = ["cpp_out_of_range", "height_ratio_high", "height_ratio_low", "cpp_vs_book_out",
                  "symbol_mismatch", "conf_mean_low", "conf_min_low", "aspect_out", "oov_pool_high",
                  # extras (not in the spec; documented in REPORT.md)
                  "cph_out_of_range", "len_vs_book_high", "repeated_word"]

    def line_flags(i):
        cname = class_names[cls_arr[i]]; Q = CQ[cname]; out = []
        out_extra = []
        v = F["chars_per_height"][i]
        if not math.isnan(v):
            if v < Q["chars_per_height"][2]:
                out_extra.append(("cph_out_of_range", f"chars_per_height={v:.2f} < {cname} p2={Q['chars_per_height'][2]:.2f}"))
            elif v > Q["chars_per_height"][98]:
                out_extra.append(("cph_out_of_range", f"chars_per_height={v:.2f} > {cname} p98={Q['chars_per_height'][98]:.2f}"))
        v = F["len_vs_book"][i]
        if not math.isnan(v) and v > Q["len_vs_book"][99]:
            out_extra.append(("len_vs_book_high", f"label_len/book-median={v:.2f} > {cname} p99={Q['len_vs_book'][99]:.2f}"))
        if rep_word[i]:
            out_extra.append(("repeated_word", f"adjacent identical word (>=3 chars) in label: '{rep_word[i]}'"))
        v = F["chars_per_100px"][i]
        if not math.isnan(v):
            if v < Q["chars_per_100px"][2]:
                out.append(("cpp_out_of_range", f"chars_per_100px={v:.2f} < {cname} p2={Q['chars_per_100px'][2]:.2f}"))
            elif v > Q["chars_per_100px"][98]:
                out.append(("cpp_out_of_range", f"chars_per_100px={v:.2f} > {cname} p98={Q['chars_per_100px'][98]:.2f}"))
        v = F["height_ratio"][i]
        if not math.isnan(v):
            if v > HEIGHT_HI:
                out.append(("height_ratio_high", f"height_ratio={v:.2f} > spec 1.7 ({cname} p99={Q['height_ratio'][99]:.2f})"))
            elif v < HEIGHT_LO:
                out.append(("height_ratio_low", f"height_ratio={v:.2f} < spec 0.5 ({cname} p1={Q['height_ratio'][1]:.2f})"))
        v = F["cpp_vs_book"][i]
        if not math.isnan(v):
            if v < Q["cpp_vs_book"][1]:
                out.append(("cpp_vs_book_out", f"cpp/book-median={v:.2f} < {cname} p1={Q['cpp_vs_book'][1]:.2f}"))
            elif v > Q["cpp_vs_book"][99]:
                out.append(("cpp_vs_book_out", f"cpp/book-median={v:.2f} > {cname} p99={Q['cpp_vs_book'][99]:.2f}"))
        v = F["symbol_mismatch_rel"][i]
        if not math.isnan(v) and v > Q["symbol_mismatch_rel"][99] and v > 0:
            out.append(("symbol_mismatch", f"|label_nonspace({int(ns[i])})-google_symbols({int(sc[i])})|/len={v:.3f} > {cname} p99={Q['symbol_mismatch_rel'][99]:.3f}"))
        v = F["conf_mean"][i]
        if not math.isnan(v) and v < Q["conf_mean"][1]:
            out.append(("conf_mean_low", f"conf_mean={v:.3f} < {cname} p1={Q['conf_mean'][1]:.3f}"))
        v = F["conf_min"][i]
        if not math.isnan(v) and v < Q["conf_min"][1]:
            out.append(("conf_min_low", f"conf_min={v:.3f} < {cname} p1={Q['conf_min'][1]:.3f}"))
        v = F["aspect"][i]
        if not math.isnan(v):
            if v < Q["aspect"][1]:
                out.append(("aspect_out", f"aspect={v:.2f} < {cname} p1={Q['aspect'][1]:.2f}"))
            elif v > Q["aspect"][99]:
                out.append(("aspect_out", f"aspect={v:.2f} > {cname} p99={Q['aspect'][99]:.2f}"))
        v = F["oov_pool"][i]
        thr = oov_ref[cname][0]
        if ntok[i] >= 3 and not math.isnan(v) and not math.isnan(thr) and v > thr:
            out.append(("oov_pool_high", f"oov_pool={v:.2f} ({n_oov_p[i]}/{ntok[i]} words in <=1 book) > {cname} p99={thr:.2f} (lines with >=3 words)"))
        return out + out_extra

    flags_all = [line_flags(i) for i in range(N)]
    FL = {t: np.zeros(N, dtype=bool) for t in FLAG_TYPES}
    for i, fl in enumerate(flags_all):
        for t, _ in fl:
            FL[t][i] = True
    any_flag = np.zeros(N, dtype=bool)
    for t in FLAG_TYPES:
        any_flag |= FL[t]

    # ---------------- book stats ----------------
    book_lines = collections.defaultdict(list)
    for i in range(N):
        book_lines[int(book_arr[i])].append(i)
    book_feats = ["label_len", "crop_w", "crop_h", "chars_per_100px", "chars_per_height", "height_ratio", "width_ratio",
                  "y_rel", "aspect", "symbol_mismatch_rel", "conf_mean", "conf_min", "oov_pool", "oov_wikisource"]
    BS, RAW = {}, {}
    for b, idx in book_lines.items():
        raw = RAW[b] = {}
        idx = np.array(idx)
        cc = collections.Counter(class_names[c] for c in cls_arr[idx])
        maj = cc.most_common(1)[0][0]
        majm = idx[cls_arr[idx] == classes[maj]]
        st = {"source": book_names[b][0], "book_key": book_names[b][1],
              "wave": sorted({wave_names[w] for w in wave_arr[idx]}),
              "n_lines": int(idx.size), "majority_class": maj, "class_counts": dict(cc),
              "n_majority_class_lines": int(majm.size)}
        for f in book_feats:
            a = F[f][majm]; a = a[~np.isnan(a)]
            raw[f] = float(np.median(a)) if a.size else np.nan
            st[f] = {"median": fmt(np.median(a)) if a.size else None, "p10": fmt(np.percentile(a, 10)) if a.size else None,
                     "p90": fmt(np.percentile(a, 90)) if a.size else None, "n": int(a.size)}
        st["flag_counts"] = {t: int(FL[t][idx].sum()) for t in FLAG_TYPES}
        st["flag_shares"] = {t: fmt(FL[t][idx].mean(), 4) for t in FLAG_TYPES}
        st["any_flag_share"] = fmt(any_flag[idx].mean(), 4)
        raw["any_flag_share"] = float(any_flag[idx].mean())
        tok = int(ntok[idx].sum())
        st["tokens"] = tok
        raw["oov_pool_share"] = n_oov_p[idx].sum() / tok if tok else np.nan
        st["oov_pool_share"] = fmt(raw["oov_pool_share"], 4)
        polym = idx[cls_arr[idx] == poly_c]
        tokp = int(ntok[polym].sum())
        raw["oov_wikisource_share"] = n_oov_w[polym].sum() / tokp if tokp else np.nan
        st["oov_wikisource_share"] = fmt(raw["oov_wikisource_share"], 4)
        st["oov_wikisource_tokens"] = tokp
        hb = (F["height_ratio"][idx] > HEIGHT_HI) | (F["height_ratio"][idx] < HEIGHT_LO)
        st["height_ratio_extreme_share"] = fmt(hb.mean(), 4)
        raw["height_ratio_extreme_share"] = float(hb.mean())
        BS[b] = st

    # reference populations: books of the same majority class with >= MIN_BOOK_LINES lines
    ref = collections.defaultdict(list)
    for b, st in BS.items():
        if st["n_lines"] >= MIN_BOOK_LINES:
            ref[st["majority_class"]].append(b)
    zfeats = book_feats + ["oov_pool_share", "oov_wikisource_share", "any_flag_share", "height_ratio_extreme_share"]

    def bval(st, f):
        return RAW[st["_b"]][f]

    for b, st in BS.items():
        st["_b"] = b

    REFQ = {}
    for cname, bs in ref.items():
        R = {}
        for f in zfeats:
            vals = np.array([bval(BS[b], f) for b in bs]); vals = vals[~np.isnan(vals)]
            R[f] = {"mean": float(vals.mean()) if vals.size else np.nan, "std": float(vals.std(ddof=1)) if vals.size > 1 else np.nan,
                    "p5": q(vals, 5), "p95": q(vals, 95), "n": int(vals.size)}
        REFQ[cname] = R

    for b, st in BS.items():
        cname = st["majority_class"]; R = REFQ.get(cname)
        z = {}
        if R:
            for f in zfeats:
                v = bval(st, f); s = R[f]["std"]
                z[f] = fmt((v - R[f]["mean"]) / s, 2) if not (math.isnan(v) or math.isnan(s) or s == 0) else None
        st["z"] = z
        st["z_ref"] = {"class": cname, "n_books": len(ref.get(cname, [])), "min_book_lines": MIN_BOOK_LINES}
        st["n_features_beyond_2sigma"] = sum(1 for v in z.values() if v is not None and abs(v) > 2)
        hard = []
        eligible = st["n_lines"] >= MIN_BOOK_LINES and R is not None
        st["hard_suppressed_low_ref_n"] = bool(eligible and len(ref.get(cname, [])) < MIN_REF_BOOKS)
        eligible = eligible and len(ref.get(cname, [])) >= MIN_REF_BOOKS
        Q = CQ[cname]
        if eligible:
            v = bval(st, "chars_per_100px")
            if not math.isnan(v) and (v < Q["chars_per_100px"][2] or v > Q["chars_per_100px"][98]):
                hard.append({"flag": "hard_cpp", "reason": f"book median chars_per_100px={v:.2f} outside {cname} line [p2={Q['chars_per_100px'][2]:.2f}, p98={Q['chars_per_100px'][98]:.2f}]; {st['flag_counts']['cpp_out_of_range']}/{st['n_lines']} lines individually out of range"})
            v = bval(st, "chars_per_height")
            if not math.isnan(v) and (v < Q["chars_per_height"][2] or v > Q["chars_per_height"][98]):
                hard.append({"flag": "hard_cph_extra", "reason": f"[extra, not in spec] book median chars_per_height={v:.2f} outside {cname} line [p2={Q['chars_per_height'][2]:.2f}, p98={Q['chars_per_height'][98]:.2f}]"})
            v = bval(st, "conf_mean")
            if not math.isnan(v) and v < R["conf_mean"]["p5"]:
                hard.append({"flag": "hard_conf", "reason": f"book median confidence={v:.4f} < {cname} book p5={R['conf_mean']['p5']:.4f} (N={R['conf_mean']['n']} books)"})
            v = bval(st, "oov_pool_share")
            if not math.isnan(v) and v > R["oov_pool_share"]["p95"]:
                hard.append({"flag": "hard_oov_pool", "reason": f"book OOV share (pool vocab, support<=1 book)={v:.4f} > {cname} book p95={R['oov_pool_share']['p95']:.4f} (N={R['oov_pool_share']['n']} books)"})
            v = bval(st, "oov_wikisource_share")
            if cname == "greek_poly" and not math.isnan(v) and v > R["oov_wikisource_share"]["p95"]:
                hard.append({"flag": "hard_oov_wikisource", "reason": f"book OOV share vs Wikisource human vocab={v:.4f} > greek_poly book p95={R['oov_wikisource_share']['p95']:.4f} (N={R['oov_wikisource_share']['n']} books)"})
            v = st["height_ratio_extreme_share"]
            if v is not None and v > HEIGHT_BOOK_SHARE:
                hard.append({"flag": "hard_height", "reason": f"{v*100:.1f}% of lines have height_ratio >1.7 or <0.5 (> spec 10%); {cname} book p95={R['height_ratio_extreme_share']['p95']:.4f}"})
        st["hard_flags"] = hard
        st["hard_eligible"] = eligible

    # ---------------- outputs ----------------
    rng = random.Random(SEED)
    examples = {t: [] for t in FLAG_TYPES}
    seen = {t: 0 for t in FLAG_TYPES}
    out_lines = os.path.join(args.out, "line_flags.jsonl.gz")
    with gzip.open(out_lines, "wt", encoding="utf-8") as go, open(POOL, encoding="utf-8") as fh:
        for n, line in enumerate(fh):
            if n >= N:
                break
            r = json.loads(line)
            rec = {"id": r["id"], "wave": r["wave"], "source": r["source"], "book_key": r["book_key"],
                   "script_class": r["script_class"], "crop_path": r["crop_path"]}
            for f in ["label_len", "crop_w", "crop_h", "chars_per_100px", "chars_per_height", "cpp_vs_book", "len_vs_book", "height_ratio",
                      "width_ratio", "y_rel", "aspect", "symbol_mismatch", "symbol_mismatch_rel", "conf_mean", "conf_min",
                      "oov_pool", "oov_wikisource"]:
                v = F[f][n]
                rec[f] = None if math.isnan(v) else (int(v) if f in ("label_len", "crop_w", "crop_h", "symbol_mismatch") else round(float(v), 4))
            rec["n_words"] = int(ntok[n]); rec["n_oov_pool"] = int(n_oov_p[n])
            rec["n_oov_wikisource"] = int(n_oov_w[n]) if cls_i[n] == poly_c else None
            rec["flags"] = [{"flag": t, "reason": why} for t, why in flags_all[n]]
            go.write(json.dumps(rec, ensure_ascii=False) + "\n")
            for t, why in flags_all[n]:
                seen[t] += 1
                ex = {"id": r["id"], "label": r["label"], "crop_path": r["crop_path"], "reason": why, "wave": r["wave"], "class": r["script_class"]}
                if len(examples[t]) < N_EXAMPLES:
                    examples[t].append(ex)
                else:
                    j = rng.randrange(seen[t])
                    if j < N_EXAMPLES:
                        examples[t][j] = ex

    with gzip.open(os.path.join(args.out, "vocab_support.tsv.gz"), "wt", encoding="utf-8") as go:
        go.write("word\tn_books\tn_tokens\tin_wikisource_el\n")
        order = sorted(range(len(word_list)), key=lambda k: (-support[k], -word_tok[k], word_list[k]))
        for k in order:
            go.write(f"{word_list[k]}\t{support[k]}\t{word_tok[k]}\t{int(word_list[k] in ws_vocab)}\n")

    with open(os.path.join(args.out, "book_stats.jsonl"), "w", encoding="utf-8") as go:
        for b in sorted(BS, key=lambda b: (-len(BS[b]["hard_flags"]), -BS[b]["n_features_beyond_2sigma"], BS[b]["source"], BS[b]["book_key"])):
            go.write(json.dumps({k: v for k, v in BS[b].items() if k != "_b"}, ensure_ascii=False) + "\n")

    summary = {"n_lines": N, "n_books": len(books), "records_unmatched_by_wave": dict(diag_missing),
               "page_height_fallbacks": {k: v for k, v in diag.items() if "fallback" in k},
               "vocab_words": len(word_list), "vocab_tokens": len(tok_flat), "wikisource_vocab": {"pages": ws_pages, "lines": ws_lines, "words": len(ws_vocab)},
               "class_quantiles": CQ, "book_reference": {c: {f: R[f] for f in R} for c, R in REFQ.items()},
               "flag_totals": {t: int(FL[t].sum()) for t in FLAG_TYPES}, "any_flag": int(any_flag.sum()),
               "hard_flag_books": dict(collections.Counter(h["flag"] for st in BS.values() for h in st["hard_flags"])),
               "n_hard_flag_books": sum(1 for st in BS.values() if st["hard_flags"])}
    with open(os.path.join(args.out, "summary.json"), "w", encoding="utf-8") as go:
        json.dump(summary, go, ensure_ascii=False, indent=1, default=lambda x: None if isinstance(x, float) and math.isnan(x) else x)

    write_report(args.out, N, F, FL, FLAG_TYPES, any_flag, cls_arr, wave_arr, class_names, wave_names, CQ, BS, REFQ,
                 examples, seen, summary, ntok, oov_ref)
    log(json.dumps({k: summary[k] for k in ("n_lines", "n_books", "flag_totals", "hard_flag_books", "n_hard_flag_books", "records_unmatched_by_wave")}, ensure_ascii=False))


def write_report(out, N, F, FL, FLAG_TYPES, any_flag, cls_arr, wave_arr, class_names, wave_names, CQ, BS, REFQ, examples, seen, summary, ntok, oov_ref):
    L = []
    P = lambda s="": L.append(s)
    dist_feats = ["label_len", "crop_w", "crop_h", "chars_per_100px", "chars_per_height", "height_ratio", "width_ratio", "y_rel",
                  "aspect", "symbol_mismatch", "conf_mean", "conf_min", "oov_pool", "oov_wikisource"]
    P("# Aspect C — length, geometry and label-quality proxies")
    P()
    P(f"Pool: `docs/harvest/collection/admitted_all.jsonl`, {N:,} lines, {summary['n_books']} books (source key = (source, book_key)). "
      f"Generated by `analysis_C.py` in this folder. Page context from `docs/harvest/<wave>/records.jsonl` (round1: `records_all.jsonl`).")
    P()
    P(f"Records matched for every pool line except: {summary['records_unmatched_by_wave'] or 'none'}. "
      f"Page-height fallbacks (PNG missing → max line y1): {summary['page_height_fallbacks'] or 'none'}.")
    P(f"Pool vocabulary: {summary['vocab_words']:,} distinct words from {summary['vocab_tokens']:,} tokens. "
      f"Wikisource human vocabulary (el, cleaned transcriptions, usable lines): {summary['wikisource_vocab']['words']:,} words from "
      f"{summary['wikisource_vocab']['lines']:,} lines on {summary['wikisource_vocab']['pages']} pages.")
    P()
    P("## Headline counts")
    P()
    P("| flag (line level) | lines | share |")
    P("|---|---:|---:|")
    for t in FLAG_TYPES:
        P(f"| {t} | {int(FL[t].sum()):,} | {FL[t].mean()*100:.2f}% |")
    P(f"| any of the above | {int(any_flag.sum()):,} | {any_flag.mean()*100:.2f}% |")
    P()
    hb = collections.Counter(h["flag"] for st in BS.values() for h in st["hard_flags"])
    P("| hard flag (book level) | books |")
    P("|---|---:|")
    for t in ["hard_cpp", "hard_conf", "hard_oov_pool", "hard_oov_wikisource", "hard_height", "hard_cph_extra"]:
        P(f"| {t} | {hb.get(t, 0)} |")
    P(f"| books with ≥1 hard flag | {summary['n_hard_flag_books']} of {summary['n_books']} |")
    P(f"| books with ≥1 spec hard flag (excluding hard_cph_extra) | {sum(1 for st in BS.values() if any(h['flag'] != 'hard_cph_extra' for h in st['hard_flags']))} |")
    P()
    sup = [st for st in BS.values() if st.get("hard_suppressed_low_ref_n")]
    P(f"Book-level hard flags are evaluated only for books with ≥ {MIN_BOOK_LINES} lines whose majority class has ≥ {MIN_REF_BOOKS} reference books; "
      f"{len(sup)} books were not evaluated for that reason (majority class: "
      + ", ".join(f"{k} {v}" for k, v in collections.Counter(st['majority_class'] for st in sup).items()) + f"), "
      f"{sum(1 for st in BS.values() if st['n_lines'] < MIN_BOOK_LINES)} books for having < {MIN_BOOK_LINES} lines.")
    P()
    P("## Distributions per class (all waves) — p2 / p10 / p50 / p90 / p98")
    P()
    hdr = "| feature | " + " | ".join(class_names[c] for c in sorted(class_names)) + " |"
    P(hdr); P("|---|" + "---|" * len(class_names))
    for f in dist_feats:
        row = []
        for c in sorted(class_names):
            Q = CQ[class_names[c]][f]
            if math.isnan(Q[50]):
                row.append("–")
            else:
                row.append(" / ".join(f"{Q[p]:.3g}" for p in (2, 10, 50, 90, 98)))
        P(f"| {f} | " + " | ".join(row) + " |")
    P()
    P("Line counts per class: " + ", ".join(f"{class_names[c]} {int((cls_arr == c).sum()):,}" for c in sorted(class_names)) + ".")
    P()
    P("## Distributions per wave × class — median [p10, p90]")
    P()
    keyf = ["label_len", "chars_per_100px", "chars_per_height", "height_ratio", "width_ratio", "aspect", "conf_mean", "conf_min", "oov_pool", "oov_wikisource"]
    P("| wave | class | n | " + " | ".join(keyf) + " |")
    P("|---|---|---:|" + "---|" * len(keyf))
    for w in sorted(wave_names, key=lambda w: wave_names[w]):
        for c in sorted(class_names):
            m = (wave_arr == w) & (cls_arr == c)
            if m.sum() < 1:
                continue
            cells = []
            for f in keyf:
                a = F[f][m]; a = a[~np.isnan(a)]
                cells.append("–" if a.size == 0 else f"{np.median(a):.3g} [{np.percentile(a,10):.3g}, {np.percentile(a,90):.3g}]")
            P(f"| {wave_names[w]} | {class_names[c]} | {int(m.sum()):,} | " + " | ".join(cells) + " |")
    P()
    P("## Flag rates per wave and class (% of lines)")
    P()
    P("| wave | class | n | " + " | ".join(FLAG_TYPES) + " | any |")
    P("|---|---|---:|" + "---:|" * (len(FLAG_TYPES) + 1))
    for w in sorted(wave_names, key=lambda w: wave_names[w]):
        for c in sorted(class_names):
            m = (wave_arr == w) & (cls_arr == c)
            n = int(m.sum())
            if n < 1:
                continue
            P(f"| {wave_names[w]} | {class_names[c]} | {n:,} | " + " | ".join(f"{FL[t][m].mean()*100:.1f}" for t in FLAG_TYPES) + f" | {any_flag[m].mean()*100:.1f} |")
    P()
    P("## Book reference populations (books with ≥ %d lines, grouped by majority class)" % MIN_BOOK_LINES)
    P()
    P("| class | N books | median conf p5 | OOV-pool share p95 | OOV-Wikisource share p95 | height-extreme share p95 |")
    P("|---|---:|---:|---:|---:|---:|")
    for cname, R in sorted(REFQ.items()):
        g = lambda f, p: ("–" if math.isnan(R[f][p]) else f"{R[f][p]:.4f}")
        P(f"| {cname} | {R['conf_mean']['n']} | {g('conf_mean','p5')} | {g('oov_pool_share','p95')} | {g('oov_wikisource_share','p95')} | {g('height_ratio_extreme_share','p95')} |")
    P()
    P("## Hard-flag books ranked (by number of hard flags, then features beyond 2σ vs same-class books)")
    P()
    hard_books = [st for st in BS.values() if st["hard_flags"]]
    hard_books.sort(key=lambda st: (-len(st["hard_flags"]), -st["n_features_beyond_2sigma"], -(st["any_flag_share"] or 0)))
    P("| # | source | book_key | wave | class | lines | hard flags | >2σ feats | reasons |")
    P("|---:|---|---|---|---|---:|---|---:|---|")
    for k, st in enumerate(hard_books, 1):
        reasons = "<br>".join(h["reason"] for h in st["hard_flags"])
        P(f"| {k} | {st['source']} | `{st['book_key']}` | {','.join(st['wave'])} | {st['majority_class']} | {st['n_lines']} | "
          f"{', '.join(h['flag'] for h in st['hard_flags'])} | {st['n_features_beyond_2sigma']} | {reasons} |")
    P()
    P("## Most anomalous books by z-score (not hard-flagged, ≥4 features beyond 2σ)")
    P()
    zb = [st for st in BS.values() if not st["hard_flags"] and st["n_features_beyond_2sigma"] >= 4]
    zb.sort(key=lambda st: -st["n_features_beyond_2sigma"])
    if not zb:
        P("None.")
    else:
        P("| source | book_key | class | lines | >2σ | features (z) |")
        P("|---|---|---|---:|---:|---|")
        for st in zb[:30]:
            fz = ", ".join(f"{f}={v}" for f, v in st["z"].items() if v is not None and abs(v) > 2)
            P(f"| {st['source']} | `{st['book_key']}` | {st['majority_class']} | {st['n_lines']} | {st['n_features_beyond_2sigma']} | {fz} |")
    P()
    P(f"## Examples — {N_EXAMPLES} random lines per flag type (seeded reservoir sample)")
    P()
    for t in FLAG_TYPES:
        P(f"### {t} ({seen[t]:,} lines flagged)")
        P()
        if not examples[t]:
            P("No lines."); P(); continue
        P("| # | wave | class | label | reason | crop_path |")
        P("|---:|---|---|---|---|---|")
        for k, ex in enumerate(examples[t], 1):
            lab = ex["label"].replace("|", "\\|")
            P(f"| {k} | {ex['wave']} | {ex['class']} | {lab} | {ex['reason'].replace('|', '/')} | `{ex['crop_path']}` |")
        P()
    P(JUDGEMENT)
    with open(os.path.join(out, "REPORT.md"), "w", encoding="utf-8") as go:
        go.write("\n".join(L) + "\n")


JUDGEMENT = r"""## What I judged and why (written after the 15 Oct 2026 full run; numbers above are regenerated on every run, this section is not)

**Definitions I had to choose.**
- *Source key* = (source, book_key). A book's reference class = its **majority** script class; its feature medians/p10/p90 are computed over its
  majority-class lines only (so a Cyrillic book's Latin lines do not shift its medians), while flag counts/shares cover all its lines.
- *Page context* comes from the wave's records file (round1: `records_all.jsonl`). Page median line height and page text width (x-extent) use the
  page's **counted** lines; `y_rel` = box centre / page PNG height (PNG header read only). Every pool line matched a record; no page-height fallbacks.
- *Words*: NFC, whitespace split, edge punctuation stripped, tokens with digits or < 2 letters dropped, then `str.lower()` (Python applies final-sigma).
  The line-final hyphen fragment is dropped, and so is the line-initial word when the previous record line on the page ended with a hyphen.
- *Pool OOV* = share of a line's words whose support (distinct books in the whole pool) is ≤ 1. *Wikisource OOV* (greek_poly lines only) = share of
  words absent from the human transcriptions of the 300 el Wikisource pages (`cleaned_transcriptions`, usable lines), leave-own-book-out.
- *Spec hard flags*: `hard_cpp` = book median chars/100 px outside the class **line** [p2, p98] (the spec's per-line range applied to the book
  median; lines outside the range are also flagged individually as `cpp_out_of_range`); `hard_conf` = book median confidence < class book-median p5;
  `hard_oov_pool` / `hard_oov_wikisource` = book OOV share > class book p95; `hard_height` = > 10 % of lines with height ratio > 1.7 or < 0.5.
  Book reference populations are books with ≥ 20 lines (555 of 557); book-quantile hard flags are not evaluated when the class has < 10
  reference books (greek_latin_cs has 2). z-scores are (book − mean)/sd over that population; N is stored in each book row (`z_ref`).
- *Line flags without a spec constant* use class quantiles (p1/p99 for two-sided shape/confidence features; p2/p98 for density as in the spec).
  `conf_*_low` and `aspect_out` therefore flag ~1–2 % by construction — they are pointers for review, not defects.
- *Extras, not in the spec*: `chars_per_height` (label length × crop height / crop width: chars per line-height of width, resolution-invariant) with
  `cph_out_of_range` (class p2/p98) and `hard_cph_extra`; `cpp_vs_book` (density relative to the book median, class p1/p99); `len_vs_book_high`
  (label length / book median > class p99); `repeated_word` (two adjacent identical words of ≥ 3 letters — a pattern detector, no threshold).

**What the data say.**
1. **Raw chars-per-100-px measures scan resolution, not label quality.** Wave medians range from 2.7 (parliament, ~5000×7600 px pages) to 7.3
   (anemi) and 10.6 (mixed Latin), so the class p2/p98 range mostly flags whole high-resolution waves (parliament greek_latin_cs 75 %, latin 35 %).
   All three `hard_cpp` books (wikisource_ru `34f692a4`, wikisource_el `51fe7386`, openarchives_mixed_apothesis `70165e43`) are inside the class
   range on the resolution-invariant density (`hard_cph_extra` = 0 books). I judge `hard_cpp` books as not label problems. For a line-level
   wrong-label signal use `cpp_vs_book_out` or `cph_out_of_range`, not the raw cpp flag.
2. **Vouli (1850s parliament) has two-column merges.** About 2,160 of 34,542 vouli greek_poly lines (6 %) have a label 1.7–2.4× their book's median
   length — a second length mode at ≈ 2×. Of four such crops I looked at, three run across the column rule and join two unrelated half-lines
   (e.g. `vouli/crops/593b45a064a4/p000007-l0055.png`, `vouli/crops/6469abc6abd1/p000003-l0040.png`), so the reading order is wrong even when the
   transcription of the pixels is right. `len_vs_book_high` (3.5 % of vouli greek_poly) and `aspect_out` > p99 (6.4 %) catch most of them; Aspect D's
   column-crossing measure should confirm.
3. **Repeated adjacent words often mean Google read text twice.** 417 lines (0.14 %). Some are genuine (κάτω κάτω, μία μία, *Hyla arborea arborea*),
   but many are doubled readings: `round1/crops/66112e132fd96ac8e30e5328/p000016-l0033.png` shows «μᾶς ἦλθε μαζὴ μὲ αὐτὴν …» and the label is
   «μαζὴ μὲ μὲ αὐτὴν …» (words missing, one doubled), and round2 `c569ee` has «ἔχει έχει γνώμην γνώμην περί περὶ ὅλων, όλων» (a polytonic and a
   monotonic reading interleaved). The Google symbol count agrees with the label length for all but 15 lines, so `symbol_mismatch` cannot catch
   these; it is the only structural check that does.
4. **The height-ratio rule finds library stamps, not bad books.** All 96 `height_ratio_high` lines are in round1 (74 greek_mono, 22 greek_poly).
   74 are the University of Crete stamp «ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ», admitted as a text line. They are spread over 16 books, at most 16 lines in any
   one book, so `hard_height` fires for 0 books. These stamp lines should be dropped by a pattern rule (label = stamp text).
5. **High OOV marks genre, not wrong labels.** The worst OOV books are lexica and grammars (`b4266bf5…` dictionary entries, `1697d5cc…` and
   `727f1e3f…` verb-form lists with author abbreviations), Homeric/Apollonian verse (wikisource `384c3f89`), dialect poetry, gazetteer lists
   (openarchives_mixed_Pandemos `9440aa94`: place names) and a Soviet law code. Sampled lines read correctly. OOV is useful for finding
   unusual vocabulary for review and for balancing the training mix, not as a drop rule.
6. **Confidence hard flags sit at the edge of a narrow distribution.** greek_poly book medians have p5 = 0.934 against a median of about 0.945;
   most `hard_conf` books miss the cut by < 0.005. The ones that stand out are openarchives_mixed_ntua `37a9179b` (0.920, 30 lines),
   wikisource_ru `9b953170` (0.923), anemi_round2 `6a7f0560…` (0.924), and parliament greek_mono sessions (`30d76051`, `37e22f57` at 0.952 against p5 0.967).

**Limits.**
- `hard_conf` and the two OOV hard flags flag ≈ 5 % of books **by construction** (class p5/p95); their count says nothing about pool health.
  Read the size of the gap in the reason.
- The Wikisource vocabulary is small (≈ 19.9k words from 3,047 lines), so line-level Wikisource OOV is high everywhere (greek_poly median 0.30)
  and only the ranking between books means anything. Wikisource lines have their own book left out.
- Lower-casing all-caps words gives unaccented forms («ΚΕΦΑΛΑΙΟΝ» → «κεφαλαιον»), which do not match their accented running-text forms, so
  books with many headings get inflated OOV. Polytonic/monotonic variants of the same word count as different words.
- `width_ratio` is relative to the x-extent of the page's counted lines. Anemi images are often two-page spreads and parliament pages have two
  columns, so ~0.45 is normal there. This feature is reported, not flagged.
- `symbol_mismatch` is almost always 0 because the labels *are* Google's text; it detects only rare edits made after the read.
- No crop pixels were analysed. Visual checks were limited to the five crops named above.
"""

if __name__ == "__main__":
    main()
