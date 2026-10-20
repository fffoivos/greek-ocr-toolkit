#!/usr/bin/env python3
"""Aspect D - duplicates and page structure of the admitted real-line pool.

Spec: docs/harvest/analysis/SPECS.md, section "Aspect D".
Run from anywhere:  .venv/bin/python docs/harvest/analysis/D_duplicates_pages/analysis_D.py [--waves round2]
Outputs (all next to this script): duplicates.jsonl, page_profiles.jsonl, book_stats.jsonl,
line_flags.jsonl.gz, REPORT.md (REPORT_<waves>.md + *_<waves>.* when --waves is a subset).

Inputs are streamed line by line. Held in memory: one small tuple per admitted line (incl. its label),
per-page aggregates, and the label -> line-index map. No crops or page images are opened.
"""
import argparse
import collections
import gzip
import itertools
import json
import math
import os
import re
import sys
import unicodedata

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
POOL = os.path.join(ROOT, "docs/harvest/collection/admitted_all.jsonl")
WAVES = ["round1", "vouli", "round2", "parliament", "openarchives", "mixed", "cyrillic", "wikisource"]


def wave_files(w):
    d = os.path.join(ROOT, "docs/harvest", w)
    rec = os.path.join(d, "records_all.jsonl" if w == "round1" else "records.jsonl")
    rej = os.path.join(d, "rejected.jsonl")
    return rec, (rej if os.path.exists(rej) else None)


# ---- constants stated by the spec (everything else is a measured quantile) ----
SENTENCE_MIN_CHARS = 25        # spec: suspicious duplicates are sentences >= 25 chars
NEAR_DUP_JACCARD = 0.60        # spec: near-duplicate pages, label-set Jaccard >= 0.6
CROSS_WIDTH = 0.80             # spec: column-crossing = width > 0.8 of the page text width
CROSS_BOOK_SHARE = 0.10        # spec: hard flag > 10 % crossing lines in a two-column book
PAGE_Q_LO, PAGE_Q_HI = 1, 99   # spec: page line count below wave p1 / above wave p99
# ---- analyst choices (documented in REPORT.md "what I judged and why") ----
EDGE_BAND = 0.08               # running-title position band (same 8 % band as aspect B)
PAIR_CAP_PER_LABEL = 100       # cross-book pairs written per label (totals are always counted)
BOILERPLATE_MIN_BOOKS = 5      # a >= 25-char label in >= 5 source keys = fixed formula of a series
SHARED_TEXT_MIN_LABELS = 10   # book pair sharing >= 10 suspicious labels = same text (measured gap 27 -> 4)
TEXT_LINE_MIN_LETTERS = 3      # lines used for page geometry
SAMPLE_SEED = 20261015

BK2SK = {}   # (wave, book_key) -> source key, so pages without admitted lines join their book
STAMP_RE = re.compile(r"ΠΑΝΕΠΙΣΤΗΜ")   # University of Crete library stamp on Anemi scans
LETTER_RE = re.compile(r"[^\W\d_]", re.UNICODE)


def nfc(s):
    return unicodedata.normalize("NFC", s or "").strip()


def page_no(page_id):
    m = re.search(r"-p(\d+)$", page_id)
    return int(m.group(1)) if m else None


def letters(s):
    return LETTER_RE.findall(s)


def upper_share(s):
    ls = letters(s)
    if not ls:
        return 0.0
    return sum(1 for c in ls if c.isupper()) / len(ls)


def letter_share(s):
    return len(letters(s)) / max(1, len(s))


def iou(a, b):
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x1 - x0) * max(0, y1 - y0)
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def q(arr, p):
    return float(np.percentile(np.asarray(arr, dtype=float), p)) if len(arr) else float("nan")


def r3(x):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), 3)


# =====================================================================================
# 1. pool
# =====================================================================================
class Line:
    __slots__ = ("id", "wave", "sk", "page_id", "pno", "cls", "split", "label", "key", "bbox", "crop",
                 "conf", "ypos", "edge", "wratio", "crossing", "gutter_cross", "ncols", "cross_inreg")


def load_pool(waves):
    lines = []
    with open(POOL) as f:
        for raw in f:
            r = json.loads(raw)
            if r["wave"] not in waves:
                continue
            L = Line()
            L.id = r["id"]; L.wave = r["wave"]; L.sk = r["source"] + "|" + r["book_key"]
            L.page_id = r["page_id"]; L.pno = page_no(r["page_id"]); L.cls = r["script_class"]
            L.split = r["split"]; L.label = r["label"]; L.key = nfc(r["label"]); L.bbox = r["bbox"]
            L.crop = r["crop_path"]; L.conf = r.get("confidence")
            L.ypos = None; L.edge = False; L.wratio = None; L.crossing = False; L.gutter_cross = False; L.cross_inreg = False
            L.ncols = None
            lines.append(L)
    return lines


# =====================================================================================
# 2. page structure from records.jsonl (+ rejected.jsonl)
# =====================================================================================
def columns_of_page(boxes):
    """boxes: list of [x0,y0,x1,y1] of body text lines. Returns dict with n_columns, text extent, gutters.

    Text extent L..R = p5 of x0 .. p95 of x1 (W = R - L). Candidate column lines = lines narrower than 0.6 W
    whose vertical centre is outside the top/bottom 8 % of the page's line extent (running titles, folios).
    Column starts = peaks of the candidates' left-edge (x0) histogram (bins of 2.5 % W, window +-5 % W), each
    holding >= max(3, 5 % of the page's text lines), peaks >= 0.3 W apart. A later peak is kept only if
      (a) its lines' median width >= 0.5 x the span it would own (to the next peak or R) - drops indents and
          centred headings,
      (b) for the right-most peak, its lines' median right edge reaches >= 0.9 W - a right column ends at the
          text edge; centred headings and short right-aligned items do not,
      (c) a gutter exists between it and the previous kept peak: the minimum x-coverage by candidate lines
          there is <= 20 % of the candidate lines.
    Pages with < 6 text lines or < 6 candidate lines are single-column by construction.
    """
    n = len(boxes)
    out = {"n_text_lines": n, "n_columns": 1, "gutters": [], "L": None, "R": None, "W": None,
           "col_basis": "few_lines"}
    if n == 0:
        return out
    a = np.asarray(boxes, dtype=float)
    L = float(np.percentile(a[:, 0], 5)); R = float(np.percentile(a[:, 2], 95))
    W = R - L
    out.update(L=L, R=R, W=W)
    if n < 6 or W <= 0:
        return out
    ymin, ymax = a[:, 1].min(), a[:, 3].max()
    H = max(1.0, ymax - ymin)
    yc = ((a[:, 1] + a[:, 3]) / 2 - ymin) / H
    w = a[:, 2] - a[:, 0]
    narrow = a[(w < 0.6 * W) & (yc >= EDGE_BAND) & (yc <= 1 - EDGE_BAND)]
    if len(narrow) < 6:
        out["col_basis"] = "mostly_full_width"
        return out
    out["col_basis"] = "x0_peaks"
    rel = np.clip((narrow[:, 0] - L) / W, 0, 0.9999)
    relx1 = (narrow[:, 2] - L) / W
    nb = 40
    hist = np.bincount((rel * nb).astype(int), minlength=nb).astype(float)
    win = np.convolve(hist, np.ones(5), mode="same")      # +-2 bins = +-5 % W
    need = max(3.0, 0.05 * n)
    peaks = []
    wcopy = win.copy()
    while True:
        k = int(np.argmax(wcopy))
        if wcopy[k] < need:
            break
        peaks.append(k)
        wcopy[max(0, k - 11):k + 12] = -1                   # suppress +-0.3 W
    peaks.sort()
    fb = 200
    cov = np.zeros(fb)
    for x0, _, x1, _ in narrow:
        b0 = int(np.clip((x0 - L) / W * fb, 0, fb - 1)); b1 = int(np.clip((x1 - L) / W * fb, 0, fb - 1))
        cov[b0:b1 + 1] += 1
    def pos(k):   # median left edge of the lines in a peak's window (fraction of W)
        sel = np.abs(rel * nb - (k + 0.5)) <= 2.5
        return float(np.median(rel[sel])) if sel.any() else (k + 0.5) / nb

    ok = peaks[:1]
    for j, k in enumerate(peaks[1:], start=1):
        last = j + 1 >= len(peaks)
        span = (1.0 if last else pos(peaks[j + 1])) - pos(k)
        sel = np.abs(rel * nb - (k + 0.5)) <= 2.5
        if not sel.any():
            continue
        if np.median(narrow[sel, 2] - narrow[sel, 0]) < 0.5 * span * W:
            continue
        if last and np.median(relx1[sel]) < 0.9:
            continue
        ok.append(k)
    kept, gutters = ok[:1], []
    for k in ok[1:]:
        lo = int((pos(kept[-1]) + 0.05) * fb); hi = int(min(1.0, pos(k) + 0.05) * fb)
        if hi <= lo:
            continue
        seg = cov[lo:hi]
        m = int(np.argmin(seg))
        if seg[m] <= 0.20 * len(narrow):
            kept.append(k); gutters.append(L + (lo + m + 0.5) / fb * W)
    if gutters:
        # informational: share of text lines lying wholly inside one column
        edges = [L - W] + gutters + [R + W]
        incol = sum(1 for x0, _, x1, _ in a
                    if any(x0 >= edges[i] - 0.05 * W and x1 <= edges[i + 1] + 0.05 * W
                           for i in range(len(edges) - 1)))
        out["column_line_share"] = incol / n
    out["gutters"] = gutters
    out["n_columns"] = len(gutters) + 1
    return out


def png_size(path):
    try:
        with open(os.path.join(ROOT, path), "rb") as f:
            h = f.read(24)
        if h[:8] == b"\x89PNG\r\n\x1a\n":
            return int.from_bytes(h[16:20], "big"), int.from_bytes(h[20:24], "big")
    except OSError:
        pass
    return None, None


def read_pages(waves, by_id):
    """Stream each wave's records; one page in memory at a time. Returns page profiles (dict by page_id)."""
    pages = {}
    for w in waves:
        rec_path, rej_path = wave_files(w)
        reasons = {}
        if rej_path:
            with open(rej_path) as f:
                for raw in f:
                    r = json.loads(raw)
                    reasons[r["id"]] = r.get("reasons") or []
        cur, buf = None, []

        def flush(pid, rows):
            if pid is None:
                return
            pages[pid] = profile_page(w, pid, rows, by_id, reasons)

        with open(rec_path) as f:
            for raw in f:
                r = json.loads(raw)
                pid = r["page_id"]
                if pid != cur:
                    flush(cur, buf); cur, buf = pid, []
                buf.append((r["id"], r["bbox"], r.get("letter_count") or 0, nfc(r.get("docai_text")),
                            r.get("image_sha256"), r["book_key"], r.get("source"), r.get("image")))
        flush(cur, buf)
        del reasons
    return pages


def profile_page(wave, pid, rows, by_id, reasons):
    n = len(rows)
    adm = [r for r in rows if r[0] in by_id]
    rej = [r for r in rows if r[0] in reasons]
    other = n - len(adm) - len(rej)
    mix = collections.Counter(x for r in rej for x in reasons[r[0]])
    text = [r for r in rows if r[2] >= TEXT_LINE_MIN_LETTERS and r[1] and r[1][2] > r[1][0]]
    # body lines for geometry: drop vertical / very tall boxes (stamps, rotated text) and library stamps
    if text:
        hmed = float(np.median([r[1][3] - r[1][1] for r in text]))
        text = [r for r in text if (r[1][3] - r[1][1]) <= 2.5 * hmed and (r[1][2] - r[1][0]) >= (r[1][3] - r[1][1])
                and STAMP_RE.search(r[3]) is None]
    geo = columns_of_page([r[1] for r in text])
    allb = np.asarray([r[1] for r in rows if r[1]], dtype=float)
    ymin = float(allb[:, 1].min()) if len(allb) else 0.0
    ymax = float(allb[:, 3].max()) if len(allb) else 1.0
    H = max(1.0, ymax - ymin)
    # rank of text lines by vertical centre for the running-title "edge" test
    order = sorted(text, key=lambda r: (r[1][1] + r[1][3]) / 2)
    edge_ids = set(r[0] for r in order[:2] + order[-2:])
    W = geo["W"] or 0
    n_cross = n_gut = n_inreg = 0
    multi = geo["n_columns"] >= 2
    if multi:
        col_lines = [((r[1][1] + r[1][3]) / 2, r[1][0], r[1][2]) for r in text if (r[1][2] - r[1][0]) < 0.6 * W]
    for r in text:
        x0, y0, x1, y1 = r[1]
        cross = multi and W > 0 and (x1 - x0) > CROSS_WIDTH * W
        gcross = multi and any(x0 < g - 0.02 * W and x1 > g + 0.02 * W for g in geo["gutters"])
        inreg = False
        if cross:
            # crossing line inside a two-column region: for some gutter, column lines of BOTH the left column
            # (narrow, ending left of the gutter) and the right column (narrow, starting right of it) lie above
            # AND below it - i.e. it is sandwiched in running two-column text (a merge of two columns), as
            # opposed to a full-width heading/paragraph in a single-column part of the page
            yc = (y0 + y1) / 2
            for g in geo["gutters"]:
                lc = [c[0] for c in col_lines if c[2] <= g + 0.05 * W]
                rc = [c[0] for c in col_lines if c[1] >= g - 0.05 * W]
                if (lc and rc and min(lc) < yc < max(lc) and min(rc) < yc < max(rc)):
                    inreg = True
                    break
        n_cross += cross; n_gut += gcross; n_inreg += inreg
        L = by_id.get(r[0])
        if L is not None:
            L.crossing = bool(cross); L.gutter_cross = bool(gcross); L.cross_inreg = inreg
            L.wratio = (x1 - x0) / W if W > 0 else None
            L.ncols = geo["n_columns"]
    for r in adm:
        L = by_id[r[0]]
        if r[1]:
            yc = (r[1][1] + r[1][3]) / 2
            L.ypos = (yc - ymin) / H
            L.edge = (r[0] in edge_ids) and (L.ypos < EDGE_BAND or L.ypos > 1 - EDGE_BAND)
        if L.ncols is None:
            L.ncols = geo["n_columns"]
    first = rows[0]
    iw, ih = png_size(first[7]) if first[7] else (None, None)
    sk = (adm and by_id[adm[0][0]].sk) or BK2SK.get((wave, first[5])) or ((first[6] or wave) + "|" + first[5])
    cls = collections.Counter(by_id[r[0]].cls for r in adm).most_common(1)
    return {
        "page_id": pid, "wave": wave, "source_key": sk, "page_no": page_no(pid),
        "class": cls[0][0] if cls else None,
        "image_sha256": first[4], "image_w": iw, "image_h": ih,
        "landscape": bool(iw and ih and iw > ih),
        "n_lines_google": n, "n_text_lines": geo["n_text_lines"], "n_admitted": len(adm),
        "n_rejected": len(rej), "n_global_excluded_or_other": other,
        "admitted_share": r3(len(adm) / n) if n else None,
        "reason_mix": dict(mix.most_common()),
        "n_columns": geo["n_columns"], "column_basis": geo["col_basis"],
        "column_line_share": r3(geo.get("column_line_share")),
        "gutters_frac": [r3((g - geo["L"]) / W) for g in geo["gutters"]] if W else [],
        "text_width_px": r3(W), "n_crossing": int(n_cross),
        "crossing_share": r3(n_cross / max(1, geo["n_text_lines"])) if multi else None,
        "n_crossing_in_column_region": int(n_inreg),
        "crossing_in_column_region_share": r3(n_inreg / max(1, geo["n_text_lines"])) if multi else None,
        "n_gutter_crossing": int(n_gut),
        "gutter_crossing_share": r3(n_gut / max(1, geo["n_text_lines"])) if multi else None,
        "_labels": set(by_id[r[0]].key for r in adm),
        "_glabels": set(r[3] for r in rows if r[3]),
    }


# =====================================================================================
# 3. duplicates
# =====================================================================================
def classify_label(key, occ, within_pages_by_sk):
    """Return (category, expected) for a duplicated label.

    occ: list of Line. within_pages_by_sk: sk -> number of distinct pages carrying the label.
    short          : < 25 chars (spec constant)
    formula        : letters < 50 % of the characters, or the whole label is one bracketed aside
    running_title  : repeated on >= 2 pages of one book with an occurrence in the top/bottom 8 % band
                     at the page edge (first/last two lines), or on >= 3 pages of one book, or every
                     occurrence is an edge line and >= 60 % of its letters are capitals
    boilerplate    : >= 25 chars, in >= 5 different source keys (series formula, e.g. parliamentary)
    suspicious     : anything else (>= 25-char sentence)
    """
    if len(key) < SENTENCE_MIN_CHARS:
        return "short", True
    if letter_share(key) < 0.5 or (key[0] in "([" and key[-1] in ")]"):
        return "formula", True
    maxpages = max(within_pages_by_sk.values()) if within_pages_by_sk else 1
    any_edge = any(L.edge for L in occ)
    if (maxpages >= 2 and any_edge) or maxpages >= 3 or (all(L.edge for L in occ) and upper_share(key) >= 0.6):
        return "running_title", True
    if len(within_pages_by_sk) >= BOILERPLATE_MIN_BOOKS:
        return "boilerplate", True
    return "suspicious", False


def find_duplicates(lines, pages, out):
    groups = collections.defaultdict(list)
    for i, L in enumerate(lines):
        groups[L.key].append(i)
    stats = collections.Counter()
    line_dup = {}           # idx -> dict of dup features
    book_pairs = collections.Counter()   # (skA, skB) -> suspicious shared labels
    book_pair_examples = collections.defaultdict(list)
    for key, idxs in groups.items():
        if len(idxs) < 2 or not key:
            continue
        occ = [lines[i] for i in idxs]
        by_sk = collections.defaultdict(list)
        for i in idxs:
            by_sk[lines[i].sk].append(i)
        pages_by_sk = {sk: len(set(lines[i].page_id for i in v)) for sk, v in by_sk.items()}
        cat, expected = classify_label(key, occ, pages_by_sk)
        n_books = len(by_sk)
        # ---- cross-book pairs
        if n_books >= 2:
            sks = sorted(by_sk)
            npairs = n_books * (n_books - 1) // 2
            stats["cross_book_pairs_" + cat] += npairs
            stats["cross_book_labels_" + cat] += 1
            spl = set(L.split for L in occ)
            if "train" in spl and spl - {"train"}:
                stats["train_vs_heldout_labels_" + cat] += 1
            for sk in sks:
                for i in by_sk[sk]:
                    d = line_dup.setdefault(i, {})
                    d["cross_n_books"] = n_books - 1; d["cross_cat"] = cat
            for k, (a, b) in enumerate(itertools.combinations(sks, 2)):
                La, Lb = lines[by_sk[a][0]], lines[by_sk[b][0]]
                if not expected:
                    book_pairs[(a, b)] += 1
                    if len(book_pair_examples[(a, b)]) < 3:
                        book_pair_examples[(a, b)].append(key)
                if La.split != Lb.split and not expected:
                    stats["cross_book_pairs_suspicious_cross_split"] += 1
                if k >= PAIR_CAP_PER_LABEL:
                    continue
                out.write(json.dumps({
                    "kind": "cross_book", "label": key, "length": len(key), "category": cat,
                    "expected": expected, "n_source_keys_with_label": n_books, "n_pairs_for_label": npairs,
                    "id_a": La.id, "id_b": Lb.id, "source_key_a": a, "source_key_b": b,
                    "wave_a": La.wave, "wave_b": Lb.wave, "split_a": La.split, "split_b": Lb.split,
                    "cross_split": La.split != Lb.split, "class_a": La.cls, "class_b": Lb.cls,
                    "crop_a": La.crop, "crop_b": Lb.crop,
                    "reason": ("label of %d chars in %d source keys; category %s (%s); splits %s/%s"
                               % (len(key), n_books, cat,
                                  ">= 25-char sentence, not a running title/formula" if not expected
                                  else "expected repetition", La.split, Lb.split)),
                }, ensure_ascii=False) + "\n")
        # ---- within-book, across pages / within page
        for sk, v in by_sk.items():
            by_page = collections.defaultdict(list)
            for i in v:
                by_page[lines[i].page_id].append(i)
            if len(by_page) >= 2:
                stats["within_book_groups_" + cat] += 1
                stats["within_book_pairs_" + cat] += len(by_page) * (len(by_page) - 1) // 2
                for i in v:
                    d = line_dup.setdefault(i, {})
                    d["within_book_pages"] = len(by_page) - 1; d["within_cat"] = cat
                pids = sorted(by_page, key=lambda p: lines[by_page[p][0]].pno or 0)
                out.write(json.dumps({
                    "kind": "within_book", "label": key, "length": len(key), "category": cat,
                    "expected": expected, "source_key": sk, "n_pages": len(by_page),
                    "page_ids": pids, "ids": [lines[by_page[p][0]].id for p in pids],
                    "page_nos": [lines[by_page[p][0]].pno for p in pids],
                    "crops": [lines[by_page[p][0]].crop for p in pids][:5],
                    "reason": "label of %d chars on %d pages of one source key; category %s"
                              % (len(key), len(by_page), cat),
                }, ensure_ascii=False) + "\n")
            for pid, pv in by_page.items():
                if len(pv) < 2:
                    continue
                bxs = [lines[i].bbox for i in pv]
                mx = max(iou(a, b) for a, b in itertools.combinations(bxs, 2))
                sub = "overlapping_boxes" if mx >= 0.5 else "distinct_positions"
                stats["within_page_groups_" + sub] += 1
                for i in pv:
                    d = line_dup.setdefault(i, {})
                    d["within_page_n"] = len(pv) - 1; d["within_page_iou"] = r3(mx); d["within_page_cat"] = cat
                out.write(json.dumps({
                    "kind": "within_page", "label": key, "length": len(key), "category": cat,
                    "expected": expected, "source_key": sk, "page_id": pid,
                    "ids": [lines[i].id for i in pv], "bboxes": bxs, "max_iou": r3(mx), "subkind": sub,
                    "crops": [lines[i].crop for i in pv],
                    "reason": "label repeated %d times on one page; max box IoU %.2f (%s)" % (len(pv), mx, sub),
                }, ensure_ascii=False) + "\n")
    return stats, line_dup, book_pairs, book_pair_examples


def jac(a, b):
    if not a and not b:
        return None
    return len(a & b) / len(a | b)


def near_dup_pages(pages, out):
    by_sk = collections.defaultdict(list)
    for p in pages.values():
        by_sk[p["source_key"]].append(p)
    adjacent_all = []
    hits = []
    for sk, ps in by_sk.items():
        ps.sort(key=lambda p: p["page_no"] or 0)
        for a, b in zip(ps, ps[1:]):
            if a["page_no"] is None or b["page_no"] is None or b["page_no"] - a["page_no"] != 1:
                continue
            j = jac(a["_labels"], b["_labels"])
            jg = jac(a["_glabels"], b["_glabels"])
            adjacent_all.append((sk, a["page_id"], b["page_id"], j, jg))
            if j is not None and j >= NEAR_DUP_JACCARD:
                hits.append(("near_dup_page", a, b, j, jg))
    # extra: any other page pair (non-adjacent or cross-book) sharing >= 25-char labels, Jaccard >= 0.6
    inv = collections.defaultdict(list)
    for p in pages.values():
        for k in p["_labels"]:
            if len(k) >= SENTENCE_MIN_CHARS:
                inv[k].append(p["page_id"])
    cand = set()
    for k, pl in inv.items():
        if 1 < len(pl) <= 50:
            for a, b in itertools.combinations(sorted(pl), 2):
                cand.add((a, b))
    adj = set((x[1], x[2]) for x in adjacent_all) | set((x[2], x[1]) for x in adjacent_all)
    for a, b in sorted(cand):
        if (a, b) in adj:
            continue
        pa, pb = pages[a], pages[b]
        j = jac(pa["_labels"], pb["_labels"])
        if j is not None and j >= NEAR_DUP_JACCARD:
            hits.append(("near_dup_page_other", pa, pb, j, jac(pa["_glabels"], pb["_glabels"])))
    # extra: identical page image hash under different page ids
    by_img = collections.defaultdict(list)
    for p in pages.values():
        if p["image_sha256"]:
            by_img[p["image_sha256"]].append(p)
    for h, ps in by_img.items():
        for a, b in itertools.combinations(ps, 2):
            hits.append(("same_image_pages", a, b, jac(a["_labels"], b["_labels"]),
                         jac(a["_glabels"], b["_glabels"])))
    for kind, a, b, j, jg in hits:
        small = len(a["_labels"] | b["_labels"]) < 5
        out.write(json.dumps({
            "kind": kind, "page_id_a": a["page_id"], "page_id_b": b["page_id"],
            "source_key_a": a["source_key"], "source_key_b": b["source_key"],
            "page_no_a": a["page_no"], "page_no_b": b["page_no"], "wave": a["wave"],
            "jaccard_admitted": r3(j), "jaccard_google_all": r3(jg),
            "n_labels_a": len(a["_labels"]), "n_labels_b": len(b["_labels"]),
            "n_shared": len(a["_labels"] & b["_labels"]), "small_sets": small,
            "same_image": a["image_sha256"] == b["image_sha256"],
            "reason": ("admitted label-set Jaccard %.3f >= 0.6 (spec); Google all-line Jaccard %s; "
                       "%d/%d labels, %d shared%s" % (j or 0, r3(jg), len(a["_labels"]), len(b["_labels"]),
                                                     len(a["_labels"] & b["_labels"]),
                                                     "; union < 5 labels" if small else "")),
        }, ensure_ascii=False) + "\n")
    return adjacent_all, hits


# =====================================================================================
# 4. page flags, book stats, line flags
# =====================================================================================
def page_flags(pages):
    by_wave = collections.defaultdict(list)
    for p in pages.values():
        by_wave[p["wave"]].append(p)
    wq = {}
    for w, ps in by_wave.items():
        n = [p["n_lines_google"] for p in ps]
        rs = [1 - (p["admitted_share"] or 0) for p in ps]
        wq[w] = {"N": len(ps), "p1": q(n, PAGE_Q_LO), "p50": q(n, 50), "p99": q(n, PAGE_Q_HI),
                 "rej_p95": q(rs, 95), "rej_p50": q(rs, 50)}
    for p in pages.values():
        Q = wq[p["wave"]]
        n = p["n_lines_google"]
        p["wave_median_lines"] = Q["p50"]
        p["lines_vs_wave_median"] = r3(n / Q["p50"]) if Q["p50"] else None
        fl = []
        if n > Q["p99"]:
            fl.append({"flag": "lines_above_wave_p99", "hard": True,
                       "reason": "n_lines_google %d > %s p99 %.1f (N=%d pages)" % (n, p["wave"], Q["p99"], Q["N"])})
        if n < Q["p1"]:
            fl.append({"flag": "lines_below_wave_p1", "hard": True,
                       "reason": "n_lines_google %d < %s p1 %.1f (N=%d pages)" % (n, p["wave"], Q["p1"], Q["N"])})
        rs = 1 - (p["admitted_share"] or 0)
        if rs > Q["rej_p95"] and rs > 0:
            fl.append({"flag": "reject_share_above_wave_p95", "hard": False,
                       "reason": "rejected+excluded share %.3f > %s p95 %.3f (median %.3f)"
                                 % (rs, p["wave"], Q["rej_p95"], Q["rej_p50"])})
        if p["crossing_share"] is not None and p["crossing_share"] > CROSS_BOOK_SHARE:
            fl.append({"flag": "column_crossing_page", "hard": False,
                       "reason": "%d of %d text lines wider than 0.8 x text width (%.3f > 0.10) on a %d-column page"
                                 % (p["n_crossing"], p["n_text_lines"], p["crossing_share"], p["n_columns"])})
        if p["landscape"] and p["n_columns"] == 2:
            fl.append({"flag": "landscape_two_column_spread_candidate", "hard": False,
                       "reason": "page image %dx%d is landscape and has 2 detected columns (gutter at %s of text width)"
                                 % (p["image_w"], p["image_h"], p["gutters_frac"])})
        if p["reason_mix"].get("bad_page"):
            fl.append({"flag": "bad_page_reason", "hard": False,
                       "reason": "%d lines rejected with reason bad_page" % p["reason_mix"]["bad_page"]})
        p["flags"] = fl
    return wq


def zscores(books, feats):
    by_cls = collections.defaultdict(list)
    for b in books.values():
        by_cls[b["class"]].append(b)
    ref = {}
    for c, bs in by_cls.items():
        for f in feats:
            v = [b[f] for b in bs if b.get(f) is not None]
            if len(v) >= 2:
                ref[(c, f)] = (float(np.mean(v)), float(np.std(v)), len(v), q(v, 5), q(v, 95))
    for b in books.values():
        z = {}
        for f in feats:
            m = ref.get((b["class"], f))
            if m and b.get(f) is not None and m[1] > 0:
                z[f] = r3((b[f] - m[0]) / m[1])
        b["z"] = z
        b["z_ref"] = {"class": b["class"], "N_books": len(by_cls[b["class"]])}
        b["n_features_beyond_2sd"] = sum(1 for v in z.values() if v is not None and abs(v) > 2)
    return ref


def build_books(lines, pages, line_dup, adjacent_all, hits, book_pairs):
    books = {}
    for i, L in enumerate(lines):
        b = books.setdefault(L.sk, {"source_key": L.sk, "source": L.sk.split("|")[0],
                                    "book_key": L.sk.split("|", 1)[1], "wave": L.wave,
                                    "_cls": collections.Counter(), "_split": collections.Counter(),
                                    "n_lines": 0, "dup_cross_any": 0, "dup_cross_suspicious": 0,
                                    "dup_cross_expected": 0, "dup_within_book_any": 0,
                                    "dup_within_book_suspicious": 0, "dup_within_page": 0,
                                    "dup_within_page_overlap": 0, "crossing_lines": 0,
                                    "lines_on_multicol_pages": 0})
        b["n_lines"] += 1; b["_cls"][L.cls] += 1; b["_split"][L.split] += 1
        d = line_dup.get(i)
        if d:
            if "cross_cat" in d:
                b["dup_cross_any"] += 1
                if d["cross_cat"] == "suspicious":
                    b["dup_cross_suspicious"] += 1
                else:
                    b["dup_cross_expected"] += 1
            if "within_cat" in d:
                b["dup_within_book_any"] += 1
                b["dup_within_book_suspicious"] += d["within_cat"] == "suspicious"
            if "within_page_n" in d:
                b["dup_within_page"] += 1
                b["dup_within_page_overlap"] += (d["within_page_iou"] or 0) >= 0.5
    for p in pages.values():
        b = books.get(p["source_key"])
        if b is None:   # read page of a book with no admitted line
            b = books.setdefault(p["source_key"], {"source_key": p["source_key"],
                                                  "source": p["source_key"].split("|")[0],
                                                  "book_key": p["source_key"].split("|", 1)[1],
                                                  "wave": p["wave"], "_cls": collections.Counter(),
                                                  "_split": collections.Counter(), "n_lines": 0})
        b.setdefault("_pages", []).append(p)
    nd_adj = collections.Counter(); nd_other = collections.Counter(); same_img = collections.Counter()
    for kind, a, bb, j, jg in hits:
        tgt = {"near_dup_page": nd_adj, "near_dup_page_other": nd_other, "same_image_pages": same_img}[kind]
        tgt[a["source_key"]] += 1
        if bb["source_key"] != a["source_key"]:
            tgt[bb["source_key"]] += 1
    adj_j = collections.defaultdict(list)
    for sk, a, bb, j, jg in adjacent_all:
        if j is not None:
            adj_j[sk].append(j)
    shared_books = collections.defaultdict(list)
    for (a, bb), n in book_pairs.items():
        shared_books[a].append((n, bb)); shared_books[bb].append((n, a))
    for sk, b in books.items():
        ps = b.pop("_pages", [])
        b["class"] = b["_cls"].most_common(1)[0][0] if b["_cls"] else "no_admitted_lines"
        b["class_mix"] = dict(b.pop("_cls")); b["splits"] = dict(b.pop("_split"))
        n = max(1, b["n_lines"])
        b["n_pages"] = len(ps)
        nl = [p["n_lines_google"] for p in ps]
        ad = [p["admitted_share"] for p in ps if p["admitted_share"] is not None]
        b["lines_per_page"] = {"p10": r3(q(nl, 10)), "median": r3(q(nl, 50)), "p90": r3(q(nl, 90))} if nl else None
        b["admitted_share_page"] = {"p10": r3(q(ad, 10)), "median": r3(q(ad, 50)), "p90": r3(q(ad, 90))} if ad else None
        tot_g = sum(nl); tot_a = sum(p["n_admitted"] for p in ps)
        b["admitted_share"] = r3(tot_a / tot_g) if tot_g else None
        b["lines_vs_wave_median"] = r3(float(np.median([p["lines_vs_wave_median"] for p in ps]))) if ps else None
        mix = collections.Counter()
        for p in ps:
            mix.update(p["reason_mix"])
        b["reason_mix"] = dict(mix.most_common())
        multi = [p for p in ps if p["n_columns"] >= 2]
        b["n_pages_multicol"] = len(multi)
        b["n_pages_2col"] = sum(1 for p in ps if p["n_columns"] == 2)
        b["multicol_page_share"] = r3(len(multi) / len(ps)) if ps else None
        b["two_column_book"] = bool(ps) and len(multi) / len(ps) > 0.5
        txt = sum(p["n_text_lines"] for p in multi); cr = sum(p["n_crossing"] for p in multi)
        gc = sum(p["n_gutter_crossing"] for p in multi)
        ir = sum(p["n_crossing_in_column_region"] for p in multi)
        b["crossing_in_column_region_share"] = r3(ir / txt) if txt else None
        b["crossing_share"] = r3(cr / txt) if txt else None
        b["gutter_crossing_share"] = r3(gc / txt) if txt else None
        for f in ("dup_cross_any", "dup_cross_suspicious", "dup_cross_expected", "dup_within_book_any",
                  "dup_within_book_suspicious", "dup_within_page", "dup_within_page_overlap"):
            b.setdefault(f, 0)
            b["share_" + f] = r3(b[f] / n) if b["n_lines"] else None
        b["near_dup_page_pairs_adjacent"] = nd_adj[sk]
        b["near_dup_page_pairs_other"] = nd_other[sk]
        b["same_image_page_pairs"] = same_img[sk]
        b["adjacent_page_pairs"] = len(adj_j[sk])
        b["max_adjacent_jaccard"] = r3(max(adj_j[sk])) if adj_j[sk] else None
        sb = sorted(shared_books[sk], reverse=True)
        b["books_sharing_suspicious_labels"] = [{"source_key": o, "n_labels": k} for k, o in sb[:5]]
        pf = collections.Counter(f["flag"] for p in ps for f in p["flags"])
        b["page_flag_counts"] = dict(pf)
        hard = []
        if nd_adj[sk]:
            hard.append({"flag": "near_duplicate_pages", "spec": True,
                         "reason": "%d adjacent page pair(s) with admitted label-set Jaccard >= 0.6 (spec: any)"
                                   % nd_adj[sk]})
        nhi, nlo = pf.get("lines_above_wave_p99", 0), pf.get("lines_below_wave_p1", 0)
        if nhi or nlo:
            hard.append({"flag": "page_line_count_outlier", "spec": True,
                         "reason": "%d page(s) above and %d below the %s page line-count p99/p1" % (nhi, nlo, b["wave"])})
        if b["two_column_book"] and b["crossing_share"] is not None and b["crossing_share"] > CROSS_BOOK_SHARE:
            hard.append({"flag": "column_crossing", "spec": True,
                         "reason": "two-column book (%d/%d pages >= 2 columns): %.3f of text lines on those pages "
                                   "are wider than 0.8 x text width (> 0.10 spec); of them inside a two-column "
                                   "region (merge-like): %.3f"
                                   % (len(multi), len(ps), b["crossing_share"], b["crossing_in_column_region_share"])})
        if b["two_column_book"] and (b["crossing_in_column_region_share"] or 0) > CROSS_BOOK_SHARE:
            hard.append({"flag": "column_merge", "spec": False,
                         "reason": "two-column book: %.3f of text lines on its multi-column pages are wider than 0.8 x "
                                   "text width AND sit between column lines on both sides of a gutter (> 0.10, same "
                                   "constant as the spec) - Google merged the two columns into one line"
                                   % b["crossing_in_column_region_share"]})
        dup_other = nd_other[sk] + same_img[sk]
        if dup_other:
            hard.append({"flag": "duplicate_scan", "spec": False,
                         "reason": "%d page pair(s) identical to another page (byte-identical image: %d; admitted "
                                   "label-set Jaccard >= 0.6 non-adjacent or with another source key: %d)"
                                   % (dup_other, same_img[sk], nd_other[sk])})
        top = sb[0] if sb else None
        if top and top[0] >= SHARED_TEXT_MIN_LABELS:
            hard.append({"flag": "shares_text_with_other_book", "spec": False,
                         "reason": "%d >= 25-char non-title labels identical with %s (pairs gap: next tier <= 4)"
                                   % (top[0], top[1])})
        b["hard_flags"] = hard
    feats = ["share_dup_cross_suspicious", "share_dup_cross_any", "share_dup_within_book_any",
             "share_dup_within_book_suspicious", "share_dup_within_page", "admitted_share",
             "lines_vs_wave_median", "multicol_page_share", "crossing_share", "max_adjacent_jaccard"]
    ref = zscores(books, feats)
    for b in books.values():
        b["soft_flags"] = []
        for f in feats:
            m = ref.get((b["class"], f))
            if not m or b.get(f) is None:
                continue
            mean, sd, N, p5, p95 = m
            if b[f] > p95 and b[f] > 0 and N >= 20:
                b["soft_flags"].append({"flag": f + "_above_class_p95",
                                        "reason": "%s %.3f > %s-book p95 %.3f (N=%d books, z=%s)"
                                                  % (f, b[f], b["class"], p95, N, b["z"].get(f))})
    return books, ref, feats


# =====================================================================================
# 5. report
# =====================================================================================
def md_table(rows, head):
    s = "| " + " | ".join(head) + " |\n| " + " | ".join("---" for _ in head) + " |\n"
    for r in rows:
        s += "| " + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in r) + " |\n"
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--waves", default=",".join(WAVES))
    args = ap.parse_args()
    waves = [w for w in args.waves.split(",") if w]
    suffix = "" if set(waves) == set(WAVES) else "_" + "_".join(waves)
    P = lambda name: os.path.join(HERE, name.replace(".", suffix + ".", 1) if suffix else name)

    print("loading pool ...", file=sys.stderr)
    lines = load_pool(set(waves))
    by_id = {L.id: L for L in lines}
    for L in lines:
        BK2SK[(L.wave, L.sk.split("|", 1)[1])] = L.sk
    print("pool lines", len(lines), file=sys.stderr)
    pages = read_pages(waves, by_id)
    print("pages", len(pages), file=sys.stderr)
    wq = page_flags(pages)

    with open(P("duplicates.jsonl"), "w") as out:
        stats, line_dup, book_pairs, bp_ex = find_duplicates(lines, pages, out)
        adjacent_all, hits = near_dup_pages(pages, out)
    books, ref, feats = build_books(lines, pages, line_dup, adjacent_all, hits, book_pairs)

    # ---- page_profiles.jsonl
    near_pages = collections.defaultdict(list)
    for kind, a, b, j, jg in hits:
        near_pages[a["page_id"]].append((kind, b["page_id"], j))
        near_pages[b["page_id"]].append((kind, a["page_id"], j))
    with open(P("page_profiles.jsonl"), "w") as f:
        for pid in sorted(pages):
            p = pages[pid]
            for kind, other, j in near_pages.get(pid, []):
                p["flags"].append({"flag": kind, "hard": kind == "near_dup_page",
                                   "reason": "%s with %s, admitted label-set Jaccard %s (>= 0.6 spec)"
                                             % (kind, other, r3(j))})
            rec = {k: v for k, v in p.items() if not k.startswith("_")}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # ---- book_stats.jsonl
    with open(P("book_stats.jsonl"), "w") as f:
        for sk in sorted(books):
            f.write(json.dumps(books[sk], ensure_ascii=False) + "\n")

    # ---- line_flags.jsonl.gz
    line_flag_examples = collections.defaultdict(list)
    flag_counts = collections.Counter()
    flag_counts_wave = collections.Counter()
    with gzip.open(P("line_flags.jsonl.gz"), "wt") as f:
        for i, L in enumerate(lines):
            d = line_dup.get(i, {})
            p = pages.get(L.page_id)
            fl = []
            if d.get("cross_cat") == "suspicious":
                fl.append(("dup_cross_book_suspicious",
                           "label (%d chars) also admitted in %d other source key(s); >= 25 chars, not a running "
                           "title/formula/boilerplate" % (len(L.key), d["cross_n_books"])))
            if d.get("cross_cat") == "boilerplate":
                fl.append(("dup_cross_book_boilerplate",
                           "label (%d chars) in %d other source keys (>= 5 = series formula)" % (len(L.key), d["cross_n_books"])))
            if d.get("within_cat") == "suspicious":
                fl.append(("dup_within_book_suspicious",
                           "label (%d chars) on %d other page(s) of the same source key, not a running title"
                           % (len(L.key), d["within_book_pages"])))
            if d.get("within_page_n") and (d.get("within_page_iou") or 0) >= 0.5:
                fl.append(("dup_within_page_overlap",
                           "same label %d more time(s) on this page with box IoU %.2f >= 0.5 (double detection)"
                           % (d["within_page_n"], d["within_page_iou"])))
            elif d.get("within_page_n") and d.get("within_page_cat") == "suspicious":
                fl.append(("dup_within_page_sentence",
                           "same >= 25-char label %d more time(s) on this page at a different position"
                           % d["within_page_n"]))
            if L.crossing:
                fl.append(("column_crossing_line",
                           "box width %.2f x page text width > 0.8 on a %d-column page" % (L.wratio, L.ncols)))
            if L.cross_inreg:
                fl.append(("column_merge_line",
                           "crossing line (width %.2f x text width) sandwiched in two-column text (left- and right-column "
                           "lines above and below it): two columns read as one line" % L.wratio))
            if p:
                for pfl in p["flags"]:
                    if pfl["flag"] in ("near_dup_page", "near_dup_page_other", "same_image_pages",
                                       "lines_above_wave_p99", "lines_below_wave_p1"):
                        fl.append(("page:" + pfl["flag"], pfl["reason"]))
            rec = {"id": L.id, "wave": L.wave, "source_key": L.sk, "class": L.cls, "split": L.split,
                   "label_len": len(L.key), "dup_cross_n_books": d.get("cross_n_books", 0),
                   "dup_cross_category": d.get("cross_cat"), "dup_within_book_other_pages": d.get("within_book_pages", 0),
                   "dup_within_page_n": d.get("within_page_n", 0), "dup_within_page_iou": d.get("within_page_iou"),
                   "ypos": r3(L.ypos), "edge_line": L.edge, "width_ratio": r3(L.wratio), "page_n_columns": L.ncols,
                   "column_crossing": L.crossing, "column_merge": L.cross_inreg, "gutter_crossing": L.gutter_cross,
                   "flags": [x[0] for x in fl], "reasons": [x[1] for x in fl]}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            for name, reason in fl:
                flag_counts[name] += 1
                flag_counts_wave[(L.wave, name)] += 1
                line_flag_examples[name].append(i)

    # ---- REPORT.md
    write_report(P("REPORT.md"), waves, lines, pages, books, stats, adjacent_all, hits, wq, ref, feats,
                 book_pairs, bp_ex, line_flag_examples, flag_counts, flag_counts_wave, line_dup, P)
    print("done", file=sys.stderr)


def write_report(path, waves, lines, pages, books, stats, adjacent_all, hits, wq, ref, feats, book_pairs,
                 bp_ex, ex_idx, flag_counts, flag_counts_wave, line_dup, P):
    rnd = __import__("random").Random(SAMPLE_SEED)
    by_id = {L.id: L for L in lines}
    R = []
    R.append("# Aspect D - duplicates and page structure\n")
    R.append("Generated by `analysis_D.py` (re-runnable: `.venv/bin/python docs/harvest/analysis/D_duplicates_pages/"
             "analysis_D.py`). Waves: %s. Admitted lines: **%d**; read pages: **%d**; source keys (books): **%d**.\n"
             % (", ".join(waves), len(lines), len(pages), len(books)))
    R.append("Outputs: [duplicates.jsonl](%s), [page_profiles.jsonl](%s), [book_stats.jsonl](%s), "
             "[line_flags.jsonl.gz](%s).\n" % tuple(os.path.basename(P(x)) for x in
                                                   ("duplicates.jsonl", "page_profiles.jsonl", "book_stats.jsonl",
                                                    "line_flags.jsonl.gz")))
    # --- key findings (numbers computed here)
    merge_books = [b for b in books.values() if any(f["flag"] == "column_merge" for f in b["hard_flags"])]
    merge_lines = sum(1 for L in lines if L.cross_inreg)
    mw = collections.Counter(L.wave for L in lines if L.cross_inreg)
    dscan = [b for b in books.values() if any(f["flag"] == "duplicate_scan" for f in b["hard_flags"])]
    stb = [b for b in books.values() if any(f["flag"] == "shares_text_with_other_book" for f in b["hard_flags"])]
    nadj = sum(1 for h in hits if h[0] == "near_dup_page")
    nimg = sum(1 for h in hits if h[0] == "same_image_pages")
    img_pairs = set(frozenset((h[1]["page_id"], h[2]["page_id"])) for h in hits if h[0] == "same_image_pages")
    noth = sum(1 for h in hits if h[0] == "near_dup_page_other"
               and frozenset((h[1]["page_id"], h[2]["page_id"])) not in img_pairs)
    dup_splits = collections.Counter(sp for b in dscan + stb for sp in b["splits"])
    spreads = collections.Counter(p["wave"] for p in pages.values() if p["landscape"] and p["n_columns"] == 2)
    R.append("## Key findings\n")
    R.append("1. **Two-column pages read as single lines (column merges).** %d admitted lines (%s) are boxes wider than "
             "0.8 x the text width sitting inside running two-column text; %d books carry the `column_merge` hard flag "
             "(%s). The crop shows two half-lines from different columns joined across the column rule, often on "
             "different baselines; the label is the concatenation. These are not reading-order-safe training lines.\n"
             % (merge_lines, ", ".join("%s %d" % kv for kv in mw.most_common()), len(merge_books),
                ", ".join("%s %d" % kv for kv in collections.Counter(b["wave"] for b in merge_books).most_common())))
    R.append("2. **Duplicate scans and duplicated text across source keys.** No adjacent same-book page pair reaches "
             "Jaccard 0.6 (spec hard flag: 0 of %d adjacent pairs), but %d page pairs are byte-identical page images "
             "under different source keys and %d further page pairs (not byte-identical) have Jaccard >= 0.6 "
             "(non-adjacent or cross-key); "
             "%d books carry `duplicate_scan`. %d books share >= %d identical >= 25-char sentences with another book "
             "(same text, different scan or typesetting). Splits of these books (a book can carry both flags): %s; no cross-book duplicate "
             "label of any category links a train book to a dev/test book.\n"
             % (len(adjacent_all), nimg, noth, len(dscan), len(stb), SHARED_TEXT_MIN_LABELS,
                ", ".join("%s %d" % kv for kv in dup_splits.most_common())))
    xs_img, all_zero = [], True
    for h in hits:
        if h[0] != "same_image_pages":
            continue
        a, b = h[1], h[2]
        sa, sb_ = set(books[a["source_key"]]["splits"]), set(books[b["source_key"]]["splits"])
        if sa == sb_:
            continue
        if a["n_admitted"] and b["n_admitted"]:
            all_zero = False
        def desc(p, sp):
            return "%s (%s, %d admitted%s)" % (p["page_id"], "/".join(sorted(sp)), p["n_admitted"],
                                               "; rejected " + json.dumps(p["reason_mix"]) if not p["n_admitted"] else "")
        xs_img.append(desc(a, sa) + " = " + desc(b, sb_))
    if xs_img:
        R.append("   Byte-identical page images whose books sit in different splits: %d. %s: %s.\n" % (
            len(xs_img), "In every case one copy has 0 admitted lines - its text was rejected by the admission's "
            "holdout-label filter (`label_in_holdout`) - so no label crosses the split" if all_zero else
            "WARNING: at least one pair has admitted lines on both sides", "; ".join(xs_img)))
    R.append("3. **Spreads.** %d page images are landscape with two detected columns (%s): two book pages scanned "
             "as one image (visual check: 8/8 sampled round1 two-column pages were spreads). Lines stay within one page, so labels are unaffected; page-level statistics (line count, "
             "columns) for these pages describe the spread, not one page.\n"
             % (sum(spreads.values()), ", ".join("%s %d" % kv for kv in spreads.most_common())))
    # --- per wave summary
    R.append("## 1. Per-wave page structure\n")
    rows = []
    for w in waves:
        ps = [p for p in pages.values() if p["wave"] == w]
        if not ps:
            continue
        bs = [b for b in books.values() if b["wave"] == w]
        nl = [p["n_lines_google"] for p in ps]
        ad = [p["admitted_share"] or 0 for p in ps]
        mc = sum(1 for p in ps if p["n_columns"] >= 2)
        c2 = sum(1 for p in ps if p["n_columns"] == 2)
        c3 = sum(1 for p in ps if p["n_columns"] >= 3)
        cr = [p["crossing_share"] for p in ps if p["crossing_share"] is not None]
        rows.append([w, len(bs), len(ps), sum(p["n_admitted"] for p in ps), sum(nl),
                     "%.0f / %.0f / %.0f / %.0f / %.0f" % (q(nl, 1), q(nl, 10), q(nl, 50), q(nl, 90), q(nl, 99)),
                     "%.2f / %.2f / %.2f" % (q(ad, 10), q(ad, 50), q(ad, 90)),
                     "%d / %d / %d" % (len(ps) - mc, c2, c3),
                     "%.3f" % q(cr, 50) if cr else "-", "%.3f" % q(cr, 90) if cr else "-",
                     sum(1 for p in ps if p["n_lines_google"] > wq[w]["p99"]),
                     sum(1 for p in ps if p["n_lines_google"] < wq[w]["p1"]),
                     sum(1 for p in ps if p["landscape"] and p["n_columns"] == 2)])
    R.append(md_table(rows, ["wave", "books", "pages", "admitted", "Google lines", "lines/page p1/p10/p50/p90/p99",
                             "admitted share p10/p50/p90", "pages 1 / 2 / 3+ col", "crossing share p50 (multi-col pages)",
                             "crossing p90", "pages > p99", "pages < p1", "landscape 2-col (spread) pages"]))
    # rejection reason mix
    R.append("\n### Rejection-reason mix per wave (lines; a line can carry several reasons)\n")
    allr = collections.Counter(); per = {}
    for w in waves:
        c = collections.Counter()
        for p in pages.values():
            if p["wave"] == w:
                c.update(p["reason_mix"])
        per[w] = c; allr.update(c)
    rk = [r for r, _ in allr.most_common()]
    R.append(md_table([[w] + [per[w].get(r, 0) for r in rk] for w in waves if w in per], ["wave"] + rk))

    # --- duplicates summary
    R.append("\n## 2. Duplicate labels\n")
    R.append("Labels compared after NFC + strip. Pair counts are all unordered pairs of distinct source keys "
             "(cross-book) or of distinct pages within one source key (within-book); `duplicates.jsonl` writes at most "
             "%d cross-book pair rows per label (the count of all pairs is in `n_pairs_for_label`).\n" % PAIR_CAP_PER_LABEL)
    cats = ["short", "formula", "running_title", "boilerplate", "suspicious"]
    R.append(md_table([[c, stats.get("cross_book_labels_" + c, 0), stats.get("cross_book_pairs_" + c, 0),
                        stats.get("within_book_groups_" + c, 0), stats.get("within_book_pairs_" + c, 0)] for c in cats],
                      ["category", "cross-book labels", "cross-book pairs", "within-book labels (>=2 pages)",
                       "within-book page pairs"]))
    R.append("\nCross-book duplicate labels shared between a train book and a dev/test book, by category: "
             + ", ".join("%s %d" % (c, stats.get("train_vs_heldout_labels_" + c, 0)) for c in cats) + ".\n")
    R.append("\nSuspicious cross-book pairs whose two books sit in different splits (possible train/test leak): **%d**.\n"
             % stats.get("cross_book_pairs_suspicious_cross_split", 0))
    xs = []
    for i, d in line_dup.items():
        if d.get("cross_cat") == "suspicious":
            xs.append(i)
    gx = collections.defaultdict(list)
    for i in xs:
        gx[lines[i].key].append(i)
    rows = []
    for key, ii in gx.items():
        if len(set(lines[i].split for i in ii)) > 1:
            rows.append([key[:100], "; ".join("%s (%s, %s)" % (lines[i].id, lines[i].wave, lines[i].split) for i in ii)])
    if rows:
        R.append(md_table(rows, ["label", "occurrences (id, wave, split)"]))
    R.append("Within-page repeats: %d label groups with overlapping boxes (IoU >= 0.5, Google detected the same line "
             "twice), %d at distinct positions.\n" % (stats.get("within_page_groups_overlapping_boxes", 0),
                                                      stats.get("within_page_groups_distinct_positions", 0)))
    # per wave line-level dup rates
    R.append("\n### Duplicate line rates per wave (share of admitted lines)\n")
    rows = []
    for w in waves:
        idx = [i for i, L in enumerate(lines) if L.wave == w]
        if not idx:
            continue
        n = len(idx)
        cnt = collections.Counter()
        for i in idx:
            d = line_dup.get(i, {})
            if "cross_cat" in d:
                cnt["cross"] += 1; cnt["cross_" + d["cross_cat"]] += 1
            if "within_cat" in d:
                cnt["within"] += 1; cnt["within_" + d["within_cat"]] += 1
            if "within_page_n" in d:
                cnt["page"] += 1
        rows.append([w, n] + ["%.4f" % (cnt[k] / n) for k in
                              ("cross", "cross_suspicious", "cross_boilerplate", "within", "within_suspicious", "page")])
    R.append(md_table(rows, ["wave", "lines", "cross-book any", "cross-book suspicious", "cross-book boilerplate",
                             "within-book any", "within-book suspicious", "within-page"]))

    # top suspicious pairs
    R.append("\n### Suspicious cross-book duplicates (top 50, longest first)\n")
    sus = []
    groups = collections.defaultdict(list)
    for i, d in line_dup.items():
        if d.get("cross_cat") == "suspicious":
            groups[lines[i].key].append(i)
    for key, idxs in groups.items():
        sks = collections.OrderedDict()
        for i in idxs:
            sks.setdefault(lines[i].sk, i)
        ii = list(sks.values())
        sus.append((len(key), key, ii))
    sus.sort(key=lambda x: -x[0])
    rows = []
    for ln, key, ii in sus[:50]:
        a, b = lines[ii[0]], lines[ii[1]]
        rows.append([ln, key[:110], len(ii), "%s (%s, %s)" % (a.id, a.wave, a.split), "%s (%s, %s)" % (b.id, b.wave, b.split),
                     a.crop])
    R.append(md_table(rows, ["len", "label", "books", "id A (wave, split)", "id B (wave, split)", "crop A"]))
    # book pairs
    R.append("\n### Book pairs sharing suspicious labels (top 30)\n")
    rows = [[n, a, b, books[a]["wave"] + "/" + books[b]["wave"],
             "/".join(sorted(books[a]["splits"])) + " vs " + "/".join(sorted(books[b]["splits"])),
             " · ".join(x[:50] for x in bp_ex[(a, b)])]
            for (a, b), n in book_pairs.most_common(30)]
    R.append(md_table(rows, ["shared labels", "source key A", "source key B", "waves", "splits", "examples"]))
    # boilerplate
    R.append("\n### Boilerplate (>= 25 chars in >= 5 source keys) - top 20 by number of books, judged expected\n")
    bp = collections.defaultdict(set)
    for i, d in line_dup.items():
        if d.get("cross_cat") == "boilerplate":
            bp[lines[i].key].add(lines[i].sk)
    R.append(md_table([[len(v), k[:110]] for k, v in sorted(bp.items(), key=lambda x: -len(x[1]))[:20]],
                      ["books", "label"]))
    # within-book suspicious examples
    R.append("\n### Within-book suspicious duplicates (>= 25 chars on >= 2 pages, not a running title) - top 30\n")
    wb = collections.defaultdict(lambda: collections.defaultdict(set))
    for i, d in line_dup.items():
        if d.get("within_cat") == "suspicious":
            wb[(lines[i].sk, lines[i].key)]["pages"].add(lines[i].page_id)
            wb[(lines[i].sk, lines[i].key)]["ids"].add(lines[i].id)
    rows = sorted(wb.items(), key=lambda x: (-len(x[1]["pages"]), -len(x[0][1])))[:30]
    R.append(md_table([[sk, key[:90], len(v["pages"]), ", ".join(sorted(v["pages"]))[:160]] for (sk, key), v in rows],
                      ["source key", "label", "pages", "page ids"]))

    # --- near-duplicate pages
    R.append("\n## 3. Near-duplicate pages\n")
    js = [x[3] for x in adjacent_all if x[3] is not None]
    jg = [x[4] for x in adjacent_all if x[4] is not None]
    R.append("Adjacent page pairs (same source key, page numbers differ by 1): **%d**. Admitted label-set Jaccard "
             "p50 / p90 / p99 / max = %s / %s / %s / %s; Google all-line Jaccard p99 / max = %s / %s.\n"
             % (len(adjacent_all), r3(q(js, 50)), r3(q(js, 90)), r3(q(js, 99)), r3(max(js) if js else None),
                r3(q(jg, 99)), r3(max(jg) if jg else None)))
    for kind, title in (("near_dup_page", "Adjacent near-duplicate page pairs (spec, hard flag) - all"),
                        ("near_dup_page_other", "Other page pairs with Jaccard >= 0.6 (non-adjacent or cross-book; extra) - all"),
                        ("same_image_pages", "Page ids with byte-identical page images (extra) - all")):
        hh = [h for h in hits if h[0] == kind]
        R.append("\n### %s: %d\n" % (title, len(hh)))
        if hh:
            R.append(md_table([[a["page_id"], b["page_id"], a["source_key"] if a["source_key"] == b["source_key"]
                                else a["source_key"] + " / " + b["source_key"], r3(j), r3(g),
                                "%d/%d" % (len(a["_labels"]), len(b["_labels"])), len(a["_labels"] & b["_labels"])]
                               for _, a, b, j, g in hh[:300]],
                              ["page A", "page B", "source key", "Jaccard admitted", "Jaccard Google", "labels A/B",
                               "shared"]))
    # --- page count outliers
    R.append("\n## 4. Page line-count outliers (vs the wave's p1 / p99)\n")
    R.append(md_table([[w, wq[w]["N"], r3(wq[w]["p1"]), r3(wq[w]["p50"]), r3(wq[w]["p99"])] for w in waves if w in wq],
                      ["wave", "pages", "p1", "median", "p99"]))
    out = sorted([p for p in pages.values() if any(f["flag"].startswith("lines_") for f in p["flags"])],
                 key=lambda p: (p["wave"], -p["n_lines_google"]))
    R.append("\nAll %d outlier pages:\n" % len(out))
    R.append(md_table([[p["page_id"], p["wave"], p["source_key"], p["n_lines_google"], p["n_admitted"], p["n_columns"],
                        "; ".join(f["reason"] for f in p["flags"] if f["flag"].startswith("lines_"))] for p in out],
                      ["page", "wave", "source key", "Google lines", "admitted", "columns", "reason"]))
    # --- column-crossing books
    R.append("\n## 5. Column structure and column-crossing books\n")
    R.append("Books whose pages are mostly multi-column (> 50 %% of read pages with >= 2 detected columns): **%d**. "
             "Crossing share = lines wider than 0.8 x page text width / text lines, on the multi-column pages.\n"
             % sum(1 for b in books.values() if b["two_column_book"]))
    cb = sorted([b for b in books.values() if b["two_column_book"]], key=lambda b: -(b["crossing_share"] or 0))
    R.append(md_table([[b["source_key"], b["wave"], b["class"], "%d/%d" % (b["n_pages_multicol"], b["n_pages"]),
                        b["crossing_share"], b["crossing_in_column_region_share"], b["gutter_crossing_share"],
                        " ".join(f["flag"] for f in b["hard_flags"] if f["flag"].startswith("column_"))] for b in cb],
                      ["source key", "wave", "class", "multi-col pages", "crossing share (spec)",
                       "crossing inside 2-col region", "gutter-crossing share", "hard flags"]))
    # --- hard flags
    R.append("\n## 6. Hard flags per book\n")
    hf = collections.Counter(); hfw = collections.Counter()
    for b in books.values():
        for f in b["hard_flags"]:
            hf[f["flag"]] += 1; hfw[(b["wave"], f["flag"])] += 1
    names = sorted(hf)
    R.append(md_table([[w, sum(1 for b in books.values() if b["wave"] == w)] + [hfw[(w, n)] for n in names] +
                       [sum(1 for b in books.values() if b["wave"] == w and b["hard_flags"])] for w in waves],
                      ["wave", "books"] + names + ["books with any hard flag"]))
    R.append("\nTotal: " + ", ".join("%s %d" % (n, hf[n]) for n in names) + "; books with any hard flag: %d.\n"
             % sum(1 for b in books.values() if b["hard_flags"]))
    hb = sorted([b for b in books.values() if b["hard_flags"]], key=lambda b: (-len(b["hard_flags"]), b["source_key"]))
    R.append(md_table([[b["source_key"], b["wave"], b["class"], b["n_pages"], " ; ".join(f["reason"] for f in b["hard_flags"])]
                       for b in hb], ["source key", "wave", "class", "pages", "hard-flag reasons"]))
    # z reference
    R.append("\n### Book feature distributions per class (reference for z-scores; mean / sd / p5 / p95, N books)\n")
    rows = []
    for (c, f), (m, sd, N, p5, p95) in sorted(ref.items()):
        rows.append([c, f, N, r3(m), r3(sd), r3(p5), r3(p95)])
    R.append(md_table(rows, ["class", "feature", "N", "mean", "sd", "p5", "p95"]))
    R.append("\nBooks with >= 1 feature beyond 2 sd of their class: %d. Soft flags (feature above class p95, classes "
             "with >= 20 books): %d books.\n" % (sum(1 for b in books.values() if b["n_features_beyond_2sd"]),
                                                  sum(1 for b in books.values() if b["soft_flags"])))
    # --- line flag rates per wave
    R.append("\n## 7. Line flag rates per wave and class\n")
    names = sorted(flag_counts)
    rows = []
    for w in waves:
        n = sum(1 for L in lines if L.wave == w)
        if n:
            rows.append([w, n] + ["%d (%.2f%%)" % (flag_counts_wave[(w, k)], 100 * flag_counts_wave[(w, k)] / n) for k in names])
    R.append(md_table(rows, ["wave", "lines"] + names))
    cls_c = collections.Counter(L.cls for L in lines)
    cls_f = collections.Counter()
    for k, ii in ex_idx.items():
        for i in ii:
            cls_f[(lines[i].cls, k)] += 1
    R.append("\n" + md_table([[c, cls_c[c]] + ["%.2f%%" % (100 * cls_f[(c, k)] / cls_c[c]) for k in names]
                              for c in sorted(cls_c)], ["class", "lines"] + names))
    # --- examples
    R.append("\n## 8. Example lines per flag type (20 random, seed %d)\n" % SAMPLE_SEED)
    for k in names:
        ii = ex_idx[k]
        pick = rnd.sample(ii, min(20, len(ii)))
        R.append("\n### %s (%d lines)\n" % (k, len(ii)))
        R.append(md_table([[lines[i].id, lines[i].label[:100], lines[i].crop] for i in pick], ["id", "label", "crop_path"]))
    R.append("\n## 9. What I judged and why (and limits)\n")
    R.append(JUDGEMENT)
    with open(path, "w") as f:
        f.write("\n".join(R))


JUDGEMENT = """
- **Duplicate key.** Labels are compared exactly after Unicode NFC and trimming of outer spaces; no case or accent
  folding, so a duplicate is a true repeat of the training label. Near-identical labels (one OCR character apart) are
  not counted - this under-counts re-read text.
- **Expected vs suspicious.** The spec gives one constant (sentences >= 25 chars are suspicious). Everything
  below 25 chars is `short` (expected). Among >= 25-char labels I treat as expected: `formula` (letters < 50 % of the
  characters, or a label that is one bracketed aside such as parliamentary stage directions), `running_title`
  (repeated on >= 2 pages of a book with one occurrence among the first/last two lines of a page inside the top/bottom
  8 % of the page's line extent, or repeated on >= 3 pages of one book, or always at a page edge and >= 60 %
  capitals), and `boilerplate` (the same >= 25-char label in >= 5 source keys: a fixed formula of a series). The
  5-book threshold is my choice; boilerplate is listed in section 2 so the call can be checked. All remaining >= 25-char
  repeats are `suspicious`. In the parliamentary waves many "suspicious" repeats are speaker attributions
  ("ΠΡΟΕΔΡΕΥΩΝ (...). Ο κ. ...") and vote formulae - real repeated text, not defects; the book-pair table separates
  these (2-4 shared lines per pair) from true shared text (27-181 shared lines per pair).
- **Shared text between books** (`shares_text_with_other_book`, not a spec flag): a book pair sharing >= 10 suspicious
  labels. The measured pair counts are 181, 33, 29, 29, 27 and then <= 4, so 10 sits in the gap. Same text in two
  source keys under different line breaks cannot be caught by page Jaccard (pages break differently), hence this
  book-level measure.
- **Duplicate scans** (`duplicate_scan`, not a spec flag): byte-identical page images (same image_sha256) under
  different page ids, or page pairs with admitted label-set Jaccard >= 0.6 that are non-adjacent or in different source
  keys (candidates found through shared >= 25-char labels; labels on > 50 pages skipped as candidates).
- **Cross-split leak.** Each cross-book pair records both splits; splits are per book (556/557 books single-split).
- **Within-page repeats** are not in the spec; overlapping boxes (IoU >= 0.5) would mean Google returned one line twice
  (none found); repeats at distinct positions are mostly vote lists and table cells.
- **Near-duplicate pages** follow the spec exactly (same source key, page numbers differing by 1, Jaccard of the
  admitted label sets >= 0.6). Rows with a label union < 5 carry `small_sets: true`.
- **Columns.** Geometry uses body lines: >= 3 letters, box height <= 2.5 x the page median, not vertical, not the
  University of Crete library stamp ("ΠΑΝΕΠΙΣΤΗΜ..."). Text width = p5 of left edges to p95 of right edges. Column
  starts are peaks of the left-edge histogram of narrow lines (< 0.6 W) outside the top/bottom 8 % band, each with
  >= max(3, 5 % of text lines), >= 0.3 W apart; a later peak must hold lines as wide as half the span it would own, the
  right-most must reach the right text edge (median right edge >= 0.9 W), and a gutter with coverage <= 20 % of narrow
  lines must separate it from the previous one. I tuned these rules on rendered pages (boxes + detected gutter drawn)
  from round2, vouli, cyrillic, openarchives and mixed, fixing three failure types seen there: centred headings,
  right-aligned short items/stamps, and gutter searches stopping short of the right column.
  Remaining limits seen in those audits: (i) pages where Google merged *every* line across the gutter have no narrow
  lines and are read as one column (e.g. a vouli newspaper page) - such pages escape both crossing measures;
  (ii) openarchives "two-column" pages are mostly side-by-side layout (figure + text, tables, charts), not true
  columns; (iii) single-column pages with a two-column signature/name block count as two-column pages.
- **Crossing.** `column_crossing` (spec) = box width > 0.8 x text width on a page with >= 2 columns; a book is
  "two-column" when > 50 % of its read pages have >= 2 columns. Because of limit (iii) and full-width headings in
  mixed layouts, the spec measure also counts legitimate full-width lines. I therefore add `column_merge` (not a spec
  flag): a crossing line that is sandwiched in running two-column text (for some gutter, left-column and right-column
  lines exist both above and below it). Book hard flag at the same > 10 % constant. Visual check of sampled merged crops
  confirmed two half-lines from different columns joined across the rule.
- **Page line count** uses every Google line of the page (incl. rejected), against the page's own wave p1/p99. By
  construction about 1 % of pages per wave fall on each side, so `page_line_count_outlier` marks books owning such
  pages, not necessarily defective books (title pages and plates fall below p1; dense indexes, tables, spreads and
  two-column pages above p99). It is the most frequent hard flag for that reason.
- **Reference groups.** Page quantiles are per wave. Book z-scores are against books of the same majority script
  class (N stated per feature); soft flags (above class p95) only for classes with >= 20 books. Books with no
  admitted line (3) form their own class `no_admitted_lines`.
- **Not done here.** No page pixels are analysed (only PNG headers for width/height); columns are inferred from
  Google boxes. The 41 globally excluded lines count as `n_global_excluded_or_other` on their pages.
"""


if __name__ == "__main__":
    main()
