#!/usr/bin/env python3
"""Aggregation of the four aspect analyses (A-D) of the admitted pool.

Outputs (docs/harvest/analysis/): book_profiles.jsonl, aggregate_stats.json (numbers used by ANOMALIES.md),
dossiers/<rank>_<source>_<key8>/{dossier.json, sheet*.jpg, page.jpg, question.md}, dossiers/INDEX.md.
ANOMALIES.md is written by write_anomalies.py from aggregate_stats.json + book_profiles.jsonl.

Run: .venv/bin/python docs/harvest/analysis/aggregate.py   (from the repo root)
"""
import collections
import gzip
import json
import os
import random
import re
import shutil
import sys
import unicodedata

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
AN = os.path.join(ROOT, 'docs/harvest/analysis')
HB = os.path.join(ROOT, 'docs/harvest/harvest_big')
POOL = os.path.join(ROOT, 'docs/harvest/collection/admitted_all.jsonl')
ASPECTS = {'A': 'A_language_script', 'B': 'B_content_style', 'C': 'C_geometry_quality', 'D': 'D_duplicates_pages'}
SEED = 20261015
TOP_N = 60
CAP = 120
SHEET_MAX_H = 6000
LINE_H = 48

# ---------------------------------------------------------------- hard-flag weights (discounts)
# weight 1 = counts fully ("non-discounted"); <1 = discounted because the aspect report itself calls it by construction / expected.
def hard_weight(aspect, flag, book):
    if aspect == 'A':
        if flag['flag'] == 'other_script_residue':
            return (0.0, 'all residue lines explained (letter+digit / number-adjacent reference letter), A §7') if flag.get('explained_only') else (1.0, '')
        if flag['flag'] == 'poly_mark_density_low':
            return (0.5, 'class-p5 rule, ~5 % of polytonic books flagged by construction (A §7)')
        if flag['flag'] == 'book_other_lang_gt2pct':
            lc = book.get('language_counts', {})
            maj = book.get('majority_language')
            other = {k: v for k, v in lc.items() if k not in (maj, 'unknown')}
            tot = sum(other.values())
            slav = sum(v for k, v in other.items() if k in ('ru', 'bg', 'sr'))
            if maj in ('ru', 'bg', 'sr') and tot and slav / tot >= 0.8:
                return (0.0, f'{slav}/{tot} other-language lines are ru/bg/sr confusions of the function-word detector (A key finding 2)')
            return (1.0, '')
        return (1.0, '')
    if aspect == 'B':
        if flag['flag'] == 'all_caps_above_class_p95':
            return (0.5, 'class-p95 rule; all-caps describes content type, not label quality (B §6)')
        if flag['flag'] == 'below_support':
            return (0.0, 'below support')
        return (1.0, '')
    if aspect == 'C':
        if flag['flag'] in ('hard_conf', 'hard_oov_pool', 'hard_oov_wikisource'):
            return (0.5, 'class p5/p95 rule, ~5 % of books flagged by construction (C Limits)')
        if flag['flag'] == 'hard_cpp':
            return (0.0, 'raw chars/100 px measures scan resolution; C judges hard_cpp books not label problems (hard_cph_extra = 0)')
        return (1.0, '')
    if aspect == 'D':
        if flag['flag'] == 'page_line_count_outlier':
            return (0.0, 'wave p1/p99 page rule, ~1 % of pages per side by construction (D §9)')
        return (1.0, '')
    return (1.0, '')


def norm_hard(aspect, row):
    h = row.get('hard_flags')
    out = []
    if isinstance(h, dict):
        for k, v in h.items():
            out.append({'flag': k, 'reason': v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)})
    elif isinstance(h, list):
        for x in h:
            if isinstance(x, dict):
                out.append(dict(x))
            else:
                out.append({'flag': str(x), 'reason': ''})
    return out


def zfeatures(aspect, row):
    """Return list of (feature, z, value) for every z-scored feature the aspect provides."""
    res = []
    if aspect == 'A':
        for k, v in (row.get('zscores') or {}).items():
            if v and v.get('z') is not None:
                res.append((k, v['z'], v.get('value')))
    elif aspect == 'B':
        for k, z in (row.get('z_median') or {}).items():
            if z is not None:
                res.append(('median ' + k, z, (row.get(k) or {}).get('median')))
        for k, z in (row.get('z_flag_share') or {}).items():
            if z is not None:
                res.append(('share ' + k, z, (row.get('flag_shares') or {}).get(k)))
    elif aspect == 'C':
        for k, z in (row.get('z') or {}).items():
            if z is None:
                continue
            v = row.get(k)
            if isinstance(v, dict):
                v = v.get('median')
            res.append((k, z, v))
    elif aspect == 'D':
        for k, z in (row.get('z') or {}).items():
            if z is not None:
                res.append((k, z, row.get(k)))
    return res


def r4(x):
    return round(x, 4) if isinstance(x, float) else x


# ---------------------------------------------------------------- titles
def clean_title(t):
    t = re.sub(r'\s+', ' ', t or '').strip()
    t = re.sub(r'\s*\(EL\)\s*$', '', t)
    return t


def load_titles(keys):
    titles = {}

    def walk(o):
        if isinstance(o, dict):
            t = o.get('title')
            for kf in ('key', 'book_key', 'volume'):
                k = o.get(kf)
                if isinstance(k, str) and k in keys and isinstance(t, str) and t.strip() and k not in titles:
                    titles[k] = clean_title(t)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    import glob
    files = []
    for pat in ('books*.json', 'selection.json', 'manifest.json'):
        files += glob.glob(os.path.join(ROOT, 'docs/harvest/*', pat))
    for f in sorted(files):
        try:
            walk(json.load(open(f)))
        except Exception as e:  # noqa
            print('title load failed', f, e, file=sys.stderr)
    return titles


# ---------------------------------------------------------------- compiled pages
def load_compiled():
    m = {}  # (wave, page_id) -> abs path
    spec = {'round1': ['round1/reads_d1_compiled', 'round1/reads_rest_compiled']}
    for w in ('round2', 'vouli', 'parliament', 'openarchives', 'mixed', 'cyrillic', 'wikisource'):
        spec[w] = [f'{w}/compiled']
    for w, dirs in spec.items():
        for d in dirs:
            rp = os.path.join(HB, d, 'compile_receipt.json')
            if not os.path.exists(rp):
                continue
            for p in json.load(open(rp)).get('pages', []):
                path = p['path']
                ap = os.path.join(ROOT, path) if path.startswith('docs/') else os.path.join(HB, d, path)
                if os.path.exists(ap):
                    m[(w, p['page_id'])] = ap
    return m


# ---------------------------------------------------------------- fonts / sheet
TNR = '/System/Library/Fonts/Supplemental/Times New Roman.ttf'
AU = '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
LABEL_PX = 26
F_TNR = ImageFont.truetype(TNR, LABEL_PX)
F_AU = ImageFont.truetype(AU, LABEL_PX)
F_NUM = ImageFont.truetype(AU, 22)
_glyph_cache = {}


def _sig(font, ch):
    m = font.getmask(ch)
    return (m.size, bytes(m))


NOTDEF = {id(F_TNR): _sig(F_TNR, '\U0010FFFD'), id(F_AU): _sig(F_AU, '\U0010FFFD')}


def has_glyph(font, ch):
    k = (id(font), ch)
    if k not in _glyph_cache:
        _glyph_cache[k] = _sig(font, ch) != NOTDEF[id(font)]
    return _glyph_cache[k]


def runs(text):
    out = []
    cur_f, buf = None, ''
    for ch in text:
        if ch.isspace() or unicodedata.combining(ch):
            f = cur_f or F_TNR
        elif has_glyph(F_TNR, ch):
            f = F_TNR
        elif has_glyph(F_AU, ch):
            f = F_AU
        else:
            f = F_TNR
        if f is not cur_f and buf:
            out.append((cur_f, buf))
            buf = ''
        cur_f = f
        buf += ch
    if buf:
        out.append((cur_f, buf))
    return out


def text_len(text):
    return sum(f.getlength(s) for f, s in runs(text))


def wrap(text, width):
    words = text.split(' ')
    lines, cur = [], ''
    for w in words:
        cand = (cur + ' ' + w) if cur else w
        if text_len(cand) <= width or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    # hard-break any single over-long token
    out = []
    for ln in lines:
        while text_len(ln) > width and len(ln) > 1:
            i = len(ln)
            while i > 1 and text_len(ln[:i]) > width:
                i -= 1
            out.append(ln[:i])
            ln = ln[i:]
        out.append(ln)
    return out or ['']


def draw_text(draw, x, y_base, text, fill=(0, 0, 0)):
    for f, s in runs(text):
        draw.text((x, y_base), s, font=f, fill=fill, anchor='ls')
        x += f.getlength(s)


def build_sheets(samples, out_dir):
    GUT, PAD, GAP, LH = 70, 10, 14, 28
    BG = (200, 200, 200)
    crops = []
    maxw = 0
    for s in samples:
        p = os.path.join(ROOT, s['crop_path'])
        im = None
        if os.path.exists(p):
            try:
                im = Image.open(p).convert('RGB')
                w = max(1, round(im.width * LINE_H / im.height))
                im = im.resize((w, LINE_H), Image.LANCZOS)
            except Exception:
                im = None
        crops.append(im)
        if im is not None:
            maxw = max(maxw, im.width)
    content_w = min(max(maxw, 1000), 2400)
    W = GUT + content_w + PAD
    rows = []
    for s, im in zip(samples, crops):
        if im is not None and im.width > content_w:
            im = im.resize((content_w, max(1, round(LINE_H * content_w / im.width))), Image.LANCZOS)
        lab_lines = wrap(s['label'], content_w)
        h = PAD + (im.height if im is not None else LINE_H) + 4 + LH * len(lab_lines) + GAP
        rows.append((s, im, lab_lines, h))
    pages, cur, ch = [], [], PAD
    for r in rows:
        if cur and ch + r[3] > SHEET_MAX_H:
            pages.append(cur)
            cur, ch = [], PAD
        cur.append(r)
        ch += r[3]
    if cur:
        pages.append(cur)
    names = ['sheet.jpg'] if len(pages) == 1 else [f'sheet_{i + 1}.jpg' for i in range(len(pages))]
    for name, pg in zip(names, pages):
        H = PAD + sum(r[3] for r in pg)
        sheet = Image.new('RGB', (W, H), BG)
        d = ImageDraw.Draw(sheet)
        y = PAD
        for s, im, lab_lines, h in pg:
            y0 = y + PAD
            col = (0, 0, 0) if s['sample'] == 'random' else (150, 0, 0)
            d.text((8, y0 + LINE_H // 2), str(s['n']), font=F_NUM, fill=col, anchor='lm')
            if im is not None:
                sheet.paste(im, (GUT, y0))
                yb = y0 + im.height + 4
            else:
                d.rectangle([GUT, y0, GUT + 300, y0 + LINE_H], fill=(255, 255, 255), outline=(0, 0, 0))
                d.text((GUT + 8, y0 + LINE_H // 2), 'crop missing', font=F_NUM, fill=(150, 0, 0), anchor='lm')
                yb = y0 + LINE_H + 4
            for i, ln in enumerate(lab_lines):
                draw_text(d, GUT, yb + LH * (i + 1) - 7, ln)
            y += h
        sheet.save(os.path.join(out_dir, name), 'JPEG', quality=85)
    return names, W


# ---------------------------------------------------------------- line-flag handling
# flags excluded from the per-line anomaly count (by construction / not a label signal)
EXCLUDE_FROM_COUNT = {'D:page:lines_above_wave_p99', 'D:page:lines_below_wave_p1', 'C:cpp_out_of_range'}
EXPLAINED_KINDS = ('alnum', 'ref_letter')
LQ_FLAGS = {  # label-quality flags (used for per-wave rates and as tie-break)
    'A:other_script_residue', 'A:homoglyph_word', 'B:final_sigma_error', 'B:digitisation_stamp', 'B:spacing_apostrophe',
    'B:repeated_run', 'C:repeated_word', 'C:symbol_mismatch', 'C:height_ratio_high', 'C:len_vs_book_high',
    'D:column_merge_line', 'D:dup_cross_book_suspicious', 'D:page:same_image_pages', 'D:page:near_dup_page_other'}


def strip_marks(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c)).lower().replace('ς', 'σ')


def main():
    # ---------------- pool
    pool_lines = {}
    by_book = collections.defaultdict(list)
    for l in open(POOL, encoding='utf-8'):
        r = json.loads(l)
        k = (r['source'], r['book_key'])
        rec = {'id': r['id'], 'wave': r['wave'], 'page_id': r['page_id'], 'label': r['label'], 'confidence': r['confidence'],
               'crop_path': r['crop_path'], 'script_class': r['script_class'], 'split': r['split'], 'year': r.get('year'),
               'bbox': r.get('bbox')}
        pool_lines[r['id']] = (k, rec)
        by_book[k].append(rec)
    keys = set(by_book)
    print('pool', len(pool_lines), 'books', len(keys))

    # ---------------- aspect book stats
    stats = {a: {} for a in ASPECTS}
    extra = {}
    for a, d in ASPECTS.items():
        for l in open(os.path.join(AN, d, 'book_stats.jsonl'), encoding='utf-8'):
            r = json.loads(l)
            k = (r['source'], r['book_key'])
            if k not in keys:
                extra.setdefault(a, []).append({'source': r['source'], 'book_key': r['book_key'], 'n_lines': r.get('n_lines'),
                                                'class': r.get('class')})
                continue
            stats[a][k] = r
    inconsistencies = []
    for a in ASPECTS:
        miss = keys - set(stats[a])
        if miss:
            inconsistencies.append(f'aspect {a}: {len(miss)} pool books missing from book_stats')
        if a in extra:
            inconsistencies.append(f'aspect {a}: {len(extra[a])} book rows not in the pool (0 admitted lines): ' +
                                   ', '.join(f"{e['source']}|{e['book_key']}" for e in extra[a]))
        for k in keys & set(stats[a]):
            if stats[a][k].get('n_lines') != len(by_book[k]):
                inconsistencies.append(f'aspect {a}: n_lines mismatch for {k}')
    # class agreement
    cls_field = {'A': 'majority_script_class', 'B': 'script_class', 'C': 'majority_class', 'D': 'class'}
    cls_dis = []
    for k in keys:
        cs = {a: stats[a][k].get(cls_field[a]) for a in ASPECTS}
        if len(set(cs.values())) > 1:
            cls_dis.append((k, cs))
    # reference populations
    refN = {}
    for a, fld in (('A', 'zscore_reference'), ('B', 'z_reference'), ('C', 'z_ref'), ('D', 'z_ref')):
        c = collections.Counter()
        for k in keys:
            c[str(stats[a][k].get(fld))[:120]] += 1
        refN[a] = c.most_common(8)
    # recount vs reported n beyond 2sd
    rep_field = {'A': 'n_features_beyond_2sd', 'B': 'n_beyond_2sd', 'C': 'n_features_beyond_2sigma', 'D': 'n_features_beyond_2sd'}

    titles = load_titles({k for _, k in keys})

    profiles = []
    recount_mismatch = collections.Counter()
    degenerate_A = 0
    for k in keys:
        lines = by_book[k]
        src, bk = k
        waves = collections.Counter(x['wave'] for x in lines)
        prof = {'source': src, 'book_key': bk, 'wave': waves.most_common(1)[0][0], 'waves': dict(waves),
                'title': titles.get(bk), 'year': lines[0]['year'], 'n_lines': len(lines),
                'class_mix': dict(collections.Counter(x['script_class'] for x in lines).most_common()),
                'majority_class': collections.Counter(x['script_class'] for x in lines).most_common(1)[0][0],
                'splits': dict(collections.Counter(x['split'] for x in lines)),
                'n_pages': len({x['page_id'] for x in lines}),
                'aspects': {}}
        aspects_beyond = 0
        hard_total = 0.0
        hard_all = []
        for a in ASPECTS:
            row = stats[a][k]
            zf = zfeatures(a, row)
            beyond = sorted([(f, z, v) for f, z, v in zf if abs(z) > 2], key=lambda t: -abs(t[1]))
            if a == 'A':
                for f, z, v in beyond:
                    zz = row['zscores'][f]
                    if zz.get('ref_sd') is not None and zz['ref_sd'] < 1e-3 and abs(z) > 2:
                        degenerate_A += 1
            rep = row.get(rep_field[a])
            if rep is not None and rep != len(beyond):
                recount_mismatch[a] += 1
            hf = []
            for h in norm_hard(a, row):
                w, why = hard_weight(a, h, row)
                hf.append({'aspect': a, 'flag': h['flag'], 'weight': w, 'discount_reason': why or None,
                           'reason': h.get('reason', '')})
            # B 'below_support' entries are listed (weight 0) for completeness
            if a == 'B' and row.get('below_support'):
                for kk, vv in row['below_support'].items():
                    hf.append({'aspect': 'B', 'flag': f'below_support:{kk}', 'weight': 0.0,
                               'discount_reason': 'below support (single occurrence), B §6', 'reason': str(vv)})
            score = len(beyond)
            if score:
                aspects_beyond += 1
            hsum = sum(h['weight'] for h in hf)
            hard_total += hsum
            hard_all += hf
            prof['aspects'][a] = {'score': score, 'n_z_features': len(zf), 'reported_n_beyond_2sd': rep,
                                  'beyond_2sd': [{'feature': f, 'z': round(z, 2), 'value': r4(v)} for f, z, v in beyond],
                                  'hard_flags': hf, 'hard_weighted': hsum}
        prof['aspects_beyond_2sd'] = aspects_beyond
        prof['hard_weighted'] = hard_total
        prof['suspicion'] = round(aspects_beyond + hard_total, 2)
        prof['n_hard_flags'] = sum(1 for h in hard_all if not h['flag'].startswith('below_support'))
        prof['nondiscounted_hard_flags'] = [f"{h['aspect']}:{h['flag']}" for h in hard_all if h['weight'] >= 1]
        # aspect-specific context
        A, B, C, D = (stats[x][k] for x in 'ABCD')
        prof['context'] = {
            'A_majority_language': A.get('majority_language'), 'A_other_language_share': A.get('other_language_share'),
            'A_language_counts': A.get('language_counts'), 'A_residue_lines': A.get('residue_lines'),
            'A_residue_lines_unexplained': A.get('residue_lines_unexplained'),
            'B_flag_counts': {kk: v for kk, v in (B.get('flag_counts') or {}).items() if v},
            'B_precomposed_breathing_capitals': B.get('precomposed_breathing_capitals'),
            'B_sigma_error_parts': B.get('sigma_error_parts'), 'B_verse_like': B.get('verse_like'),
            'C_flag_counts': {kk: v for kk, v in (C.get('flag_counts') or {}).items() if v},
            'C_conf_median': (C.get('conf_mean') or {}).get('median'), 'C_oov_pool_share': C.get('oov_pool_share'),
            'D_two_column_book': D.get('two_column_book'), 'D_crossing_share': D.get('crossing_share'),
            'D_dup_cross_suspicious': D.get('dup_cross_suspicious'), 'D_books_sharing_suspicious_labels': D.get('books_sharing_suspicious_labels'),
            'D_same_image_page_pairs': D.get('same_image_page_pairs'), 'D_near_dup_page_pairs_other': D.get('near_dup_page_pairs_other'),
        }
        profiles.append(prof)

    profiles.sort(key=lambda p: (-p['suspicion'], -p['n_lines'], p['source'], p['book_key']))
    for i, p in enumerate(profiles, 1):
        p['rank'] = i

    # reasons string
    def reasons(p, short=False):
        rs = []
        for a in ASPECTS:
            for h in p['aspects'][a]['hard_flags']:
                if h['flag'].startswith('below_support'):
                    continue
                if h['weight'] == 0 and short:
                    continue
                tag = '' if h['weight'] == 1 else f" (w={h['weight']:g})"
                rs.append(f"{a}:{h['flag']}{tag}")
        for a in ASPECTS:
            b = p['aspects'][a]['beyond_2sd']
            if b:
                top = ', '.join(f"{x['feature']} z={x['z']:+.1f}" for x in b[:3])
                rs.append(f"{a}>2σ[{len(b)}]: {top}")
        return rs
    for p in profiles:
        p['reasons'] = reasons(p)

    # ---------------- dossier selection
    top = profiles[:TOP_N]
    hard_books = [p for p in profiles[TOP_N:] if p['nondiscounted_hard_flags']]
    room = CAP - len(top)
    dossier_books = top + hard_books[:room]
    left_out = hard_books[room:]
    dkeys = {(p['source'], p['book_key']) for p in dossier_books}
    print('dossiers', len(dossier_books), 'hard-flag books beyond top-60', len(hard_books), 'left out', len(left_out))

    # ---------------- line flags stream
    line_flags = collections.defaultdict(list)     # id -> ['A:flag', ...]  (all lines)
    line_detail = collections.defaultdict(dict)    # id -> details for dossier-book lines
    line_feat = collections.defaultdict(dict)
    Bline = {}                                       # id -> selected B features for cross-cutting counts
    for a, d in ASPECTS.items():
        with gzip.open(os.path.join(AN, d, 'line_flags.jsonl.gz'), 'rt', encoding='utf-8') as fh:
            for l in fh:
                r = json.loads(l)
                lid = r['id']
                if lid not in pool_lines:
                    continue
                k = pool_lines[lid][0]
                names = []
                reasons_ = {}
                if a == 'A':
                    for f in r['flags']:
                        n = f['flag']
                        if n == 'other_script_residue':
                            n = f'other_script_residue:{f.get("kind")}'
                        names.append(n)
                        reasons_[n] = f.get('reason', '')
                elif a == 'B':
                    for f in r['flags']:
                        names.append(f)
                        reasons_[f] = (r.get('reasons') or {}).get(f, '')
                    if r.get('spacing_apos_before_capital') or r.get('precomposed_breathing_capital') or r.get('final_sigma_for_st') \
                            or r.get('stamp') or r.get('sigma_end_strong') or r.get('final_sigma_medial'):
                        Bline[lid] = (r.get('spacing_apos_before_capital', 0), r.get('precomposed_breathing_capital', 0),
                                      r.get('final_sigma_for_st', 0), r.get('stamp', False), r.get('sigma_end_strong', 0),
                                      r.get('final_sigma_medial', 0))
                elif a == 'C':
                    for f in r['flags']:
                        names.append(f['flag'])
                        reasons_[f['flag']] = f.get('reason', '')
                else:
                    rs = r.get('reasons') or []
                    for i, f in enumerate(r['flags']):
                        names.append(f)
                        reasons_[f] = rs[i] if i < len(rs) else ''
                full = [f'{a}:{n}' for n in names]
                if full:
                    line_flags[lid].extend(full)
                if k in dkeys:
                    if full:
                        line_detail[lid].update({f'{a}:{n}': reasons_.get(n, '') for n in names})
                    if a == 'A':
                        ft = r.get('features', {})
                        line_feat[lid]['lang_guess'] = ft.get('lang_guess')
                        line_feat[lid]['script_shares'] = ft.get('script_shares')
                    elif a == 'C':
                        for kk in ('len_vs_book', 'cpp_vs_book', 'height_ratio', 'conf_min', 'oov_pool'):
                            line_feat[lid][kk] = r.get(kk)
                    elif a == 'D':
                        line_feat[lid]['page_n_columns'] = r.get('page_n_columns')
                        line_feat[lid]['width_ratio'] = r.get('width_ratio')

    def counted(fl):
        return [f for f in fl if f not in EXCLUDE_FROM_COUNT and not (f.startswith('A:other_script_residue:') and f.endswith(EXPLAINED_KINDS))]

    def is_lq(f):
        base = f.split(':')[0] + ':' + f.split(':')[1] if not f.startswith('D:page:') else ':'.join(f.split(':')[:3])
        return base in LQ_FLAGS and not (f.startswith('A:other_script_residue:') and f.endswith(EXPLAINED_KINDS))

    # ---------------- per-wave rates
    wave_stats = collections.defaultdict(lambda: collections.Counter())
    for lid, (k, rec) in pool_lines.items():
        w = rec['wave']
        fl = counted(line_flags.get(lid, []))
        ws = wave_stats[w]
        ws['lines'] += 1
        for a in 'ABCD':
            if any(f.startswith(a + ':') for f in fl):
                ws['any_' + a] += 1
        if fl:
            ws['any'] += 1
        if any(is_lq(f) for f in fl):
            ws['lq'] += 1
    wave_books = collections.defaultdict(lambda: collections.Counter())
    for p in profiles:
        wb = wave_books[p['wave']]
        wb['books'] += 1
        wb['susp_sum'] += p['suspicion']
        if p['nondiscounted_hard_flags']:
            wb['hard_books'] += 1
        if p['rank'] <= TOP_N:
            wb['top60'] += 1
        if p['aspects_beyond_2sd']:
            wb['any_beyond'] += 1

    # ---------------- cross-cutting counts
    cc = {}
    fl_count = collections.Counter()
    fl_books = collections.defaultdict(set)
    fl_wave = collections.defaultdict(collections.Counter)
    fl_split = collections.defaultdict(collections.Counter)
    for lid, fl in line_flags.items():
        k, rec = pool_lines[lid]
        for f in set(fl):
            fl_count[f] += 1
            fl_books[f].add(k)
            fl_wave[f][rec['wave']] += 1
            fl_split[f][rec['split']] += 1
    # stamps
    stamp_re = re.compile(r'^(ΠΑΝΕΠΙΣΤΗΜΙ|Digitized by Google|ΒΙΒΛΙΟΘΗΚΗ)')
    stamp_ids = {lid for lid in pool_lines if 'B:digitisation_stamp' in line_flags.get(lid, [])}
    hr_stamp = {lid for lid in pool_lines if 'C:height_ratio_high' in line_flags.get(lid, []) and stamp_re.match(pool_lines[lid][1]['label'])}
    regex_hits = {lid for lid, (k, rec) in pool_lines.items() if stamp_re.match(rec['label'].strip())}
    cc['stamp'] = {'B_digitisation_stamp_lines': len(stamp_ids), 'C_height_ratio_high_stamp_lines': len(hr_stamp),
                   'union': len(stamp_ids | hr_stamp), 'regex_hits': len(regex_hits),
                   'books': len({pool_lines[i][0] for i in stamp_ids | regex_hits}),
                   'by_split': dict(collections.Counter(pool_lines[i][1]['split'] for i in stamp_ids | regex_hits)),
                   'by_wave': dict(collections.Counter(pool_lines[i][1]['wave'] for i in stamp_ids | regex_hits))}
    # column merges
    cm = {lid for lid, fl in line_flags.items() if 'D:column_merge_line' in fl}
    lvb = {lid for lid, fl in line_flags.items() if 'C:len_vs_book_high' in fl}
    asp = {lid for lid, fl in line_flags.items() if 'C:aspect_out' in fl}
    cc['column_merge'] = {'D_column_merge_lines': len(cm), 'by_wave': dict(collections.Counter(pool_lines[i][1]['wave'] for i in cm)),
                          'by_split': dict(collections.Counter(pool_lines[i][1]['split'] for i in cm)),
                          'C_len_vs_book_high': len(lvb), 'overlap_len_vs_book': len(cm & lvb), 'overlap_aspect_out': len(cm & asp),
                          'C_len_vs_book_high_vouli': sum(1 for i in lvb if pool_lines[i][1]['wave'] == 'vouli'),
                          'books_hard_column_merge': sorted(f'{s}|{b}' for (s, b) in keys if any(h['flag'] == 'column_merge' for h in norm_hard('D', stats['D'][(s, b)]))),
                          'books_hard_column_crossing': sum(1 for kk in keys if any(h['flag'] == 'column_crossing' for h in norm_hard('D', stats['D'][kk])))}
    # breathing two ways
    sp_lines = {i for i, v in Bline.items() if v[0]}
    pre_lines = {i for i, v in Bline.items() if v[1]}
    both_books = set()
    sp_books = collections.Counter(pool_lines[i][0] for i in sp_lines)
    pre_books = collections.Counter(pool_lines[i][0] for i in pre_lines)
    both_books = set(sp_books) & set(pre_books)
    cc['breathing'] = {'lines_spacing_mark_before_capital': len(sp_lines), 'lines_precomposed_breathing_capital': len(pre_lines),
                       'books_spacing_form': len(sp_books), 'books_both_forms': len(both_books),
                       'B_spacing_apostrophe_flag_lines': fl_count['B:spacing_apostrophe'],
                       'by_wave_spacing': dict(collections.Counter(pool_lines[i][1]['wave'] for i in sp_lines))}
    # sigma
    st_lines = {i for i, v in Bline.items() if v[2]}
    cc['sigma'] = {'B_final_sigma_error_lines': fl_count['B:final_sigma_error'], 'lines_st_ligature_read_as_final_sigma': len(st_lines),
                   'books_st': len({pool_lines[i][0] for i in st_lines}),
                   'st_by_wave': dict(collections.Counter(pool_lines[i][1]['wave'] for i in st_lines)),
                   'books_hard_final_sigma': sum(1 for kk in keys if 'final_sigma_above_class_p95' in (stats['B'][kk].get('hard_flags') or {}))}
    # wrong-script words
    res_kinds = collections.Counter()
    for f, n in fl_count.items():
        if f.startswith('A:other_script_residue:'):
            res_kinds[f.split(':', 2)[2]] += n
    unexpl = {lid for lid, fl in line_flags.items() if any(f.startswith('A:other_script_residue:') and not f.endswith(EXPLAINED_KINDS) for f in fl)}
    wordlike = {lid for lid, fl in line_flags.items() if any(f in ('A:other_script_residue:unexpected_word', 'A:other_script_residue:isolated_word',
                                                                     'A:other_script_residue:unexpected_standalone_lookalike',
                                                                     'A:other_script_residue:isolated_standalone_lookalike') for f in fl)}
    homo = {lid for lid, fl in line_flags.items() if 'A:homoglyph_word' in fl}
    cyr_in_non_cyr = 0
    for lid in unexpl:
        k, rec = pool_lines[lid]
        if rec['script_class'] != 'cyrillic' and re.search('[Ѐ-ӿ]', rec['label']):
            cyr_in_non_cyr += 1
    cc['wrong_script'] = {'residue_lines_all': sum(1 for fl in line_flags.values() if any(f.startswith('A:other_script_residue:') for f in fl)),
                          'residue_unexplained_lines': len(unexpl), 'residue_kinds': dict(res_kinds),
                          'word_or_lookalike_lines': len(wordlike), 'homoglyph_word_lines': len(homo),
                          'union_word_lookalike_homoglyph': len(wordlike | homo), 'cyrillic_letters_in_non_cyrillic_lines': cyr_in_non_cyr,
                          'books_unexplained_residue': len({pool_lines[i][0] for i in unexpl})}
    # foreign language
    lne = {lid for lid, fl in line_flags.items() if 'A:lang_ne_book' in fl}
    lne_latin_in_greek = sum(1 for i in lne if pool_lines[i][1]['script_class'] == 'latin' and stats['A'][pool_lines[i][0]].get('majority_script') == 'greek')
    cc['foreign'] = {'lang_ne_book_lines': len(lne), 'latin_lines_in_greek_books': lne_latin_in_greek,
                     'books_greek_other_lang_gt2pct': sum(1 for kk in keys if any(h['flag'] == 'greek_book_other_lang_gt2pct' for h in norm_hard('A', stats['A'][kk]))),
                     'books_other_lang_gt2pct_nongreek': sum(1 for kk in keys if any(h['flag'] == 'book_other_lang_gt2pct' for h in norm_hard('A', stats['A'][kk]))),
                     'by_split': dict(collections.Counter(pool_lines[i][1]['split'] for i in lne))}
    # duplicates
    dup_books_scan = sorted(f'{s}|{b}' for (s, b) in keys if any(h['flag'] == 'duplicate_scan' for h in norm_hard('D', stats['D'][(s, b)])))
    dup_books_text = sorted(f'{s}|{b}' for (s, b) in keys if any(h['flag'] == 'shares_text_with_other_book' for h in norm_hard('D', stats['D'][(s, b)])))
    dset = set(dup_books_scan) | set(dup_books_text)
    dup_lines = {lid for lid, fl in line_flags.items() if f'{pool_lines[lid][0][0]}|{pool_lines[lid][0][1]}' in dset and
                 any(f in ('D:dup_cross_book_suspicious', 'D:page:same_image_pages', 'D:page:near_dup_page_other') for f in fl)}
    cc['duplicates'] = {'books_duplicate_scan': len(dup_books_scan), 'books_shares_text': len(dup_books_text), 'books_union': len(dset),
                        'lines_dup_in_those_books': len(dup_lines),
                        'D_dup_cross_book_suspicious_lines': fl_count['D:dup_cross_book_suspicious'],
                        'D_same_image_pages_lines': fl_count['D:page:same_image_pages'],
                        'D_near_dup_page_other_lines': fl_count['D:page:near_dup_page_other'],
                        'dup_by_wave': dict(collections.Counter(pool_lines[i][1]['wave'] for i in dup_lines))}
    # OA year metadata
    oa = [kk for kk in keys if kk[0].startswith('openarchives')]
    oa_old_mono = [kk for kk in oa if (by_book[kk][0]['year'] or 9999) < 1950 and stats['A'][kk].get('majority_script_class') == 'greek_mono']
    oa_years = collections.Counter(((by_book[kk][0]['year'] or 0) // 10) * 10 for kk in oa)
    cc['oa_year'] = {'oa_books': len(oa), 'oa_year_lt_1950_mono': len(oa_old_mono),
                     'oa_year_lt_1950_any': sum(1 for kk in oa if (by_book[kk][0]['year'] or 9999) < 1950),
                     'oa_year_missing': sum(1 for kk in oa if not by_book[kk][0]['year']),
                     'lines_in_oa_old_mono': sum(len(by_book[kk]) for kk in oa_old_mono),
                     'books': sorted(f'{s}|{b} ({by_book[(s, b)][0]["year"]})' for s, b in oa_old_mono), 'decades': dict(sorted(oa_years.items()))}
    # doubled readings
    rw = {lid for lid, fl in line_flags.items() if 'C:repeated_word' in fl}
    exact = variant = 0
    tokre = re.compile(r"[^\W\d_][\w'᾿’]*", re.U)
    variant_ids = []
    for lid in rw:
        toks = [t.strip('.,;:·!?()[]«»"\'') for t in pool_lines[lid][1]['label'].split()]
        ex = va = False
        for x, y in zip(toks, toks[1:]):
            if len(x) >= 3 and strip_marks(x) == strip_marks(y):
                if x == y:
                    ex = True
                else:
                    va = True
        exact += ex
        variant += va
        if va:
            variant_ids.append(lid)
    # accent-variant adjacent pairs anywhere in the pool (not only C-flagged)
    pool_variant = 0
    for lid, (k, rec) in pool_lines.items():
        toks = [t.strip('.,;:·!?()[]«»"\'') for t in rec['label'].split()]
        for x, y in zip(toks, toks[1:]):
            if len(x) >= 3 and x != y and strip_marks(x) == strip_marks(y):
                pool_variant += 1
                break
    cc['doubled'] = {'C_repeated_word_lines': len(rw), 'with_exact_repeat': exact, 'with_accent_variant_repeat': variant,
                     'pool_lines_with_accent_variant_adjacent_pair': pool_variant,
                     'D_dup_within_page_sentence_lines': fl_count['D:dup_within_page_sentence'],
                     'by_wave': dict(collections.Counter(pool_lines[i][1]['wave'] for i in rw)),
                     'books': len({pool_lines[i][0] for i in rw}),
                     'variant_examples': [pool_lines[i][1]['label'] for i in sorted(variant_ids)[:6]]}

    # ---------------- dossiers
    compiled = load_compiled()
    ddir = os.path.join(AN, 'dossiers')
    os.makedirs(ddir, exist_ok=True)
    index_rows = []
    for p in dossier_books:
        k = (p['source'], p['book_key'])
        lines = by_book[k]
        rng = random.Random(f'{SEED}|{p["source"]}|{p["book_key"]}')

        def anom_key(rec):
            fl = counted(line_flags.get(rec['id'], []))
            return (len(fl), sum(1 for f in fl if is_lq(f)))
        scored = [(anom_key(rec), rng.random(), rec) for rec in lines]
        scored.sort(key=lambda t: (-t[0][0], -t[0][1], t[1]))
        anomalous = [rec for (c, lq), _, rec in scored if c > 0][:20]
        aset = {r['id'] for r in anomalous}
        rest = [rec for rec in lines if rec['id'] not in aset]
        n_random = 40 - len(anomalous)
        randoms = rng.sample(rest, min(n_random, len(rest)))
        randoms.sort(key=lambda r: r['id'])
        samples = []
        for i, rec in enumerate(randoms + anomalous, 1):
            fl = line_flags.get(rec['id'], [])
            samples.append({'n': i, 'sample': 'random' if rec['id'] not in aset else 'anomalous', 'id': rec['id'],
                            'page_id': rec['page_id'], 'split': rec['split'], 'script_class': rec['script_class'],
                            'label': rec['label'], 'confidence': round(rec['confidence'], 4) if rec['confidence'] is not None else None,
                            'n_flags_counted': len(counted(fl)), 'flags': sorted(set(fl)),
                            'flag_reasons': line_detail.get(rec['id'], {}),
                            'features': {kk: r4(v) if not isinstance(v, dict) else v for kk, v in line_feat.get(rec['id'], {}).items()},
                            'crop_path': rec['crop_path']})
        name = f"{p['rank']:03d}_{p['source']}_{p['book_key'][:8]}"
        od = os.path.join(ddir, name)
        if os.path.isdir(od):
            for fn in os.listdir(od):
                if fn.startswith('sheet') and fn.endswith('.jpg'):
                    os.remove(os.path.join(od, fn))
        os.makedirs(od, exist_ok=True)
        sheets, sheet_w = build_sheets(samples, od)
        # page image: the compiled page holding most anomalous samples, else most samples, else any page of the book
        pc = collections.Counter(s['page_id'] for s in samples if s['sample'] == 'anomalous')
        pc2 = collections.Counter(s['page_id'] for s in samples)
        cand = [pid for pid, _ in pc.most_common()] + [pid for pid, _ in pc2.most_common()] + sorted({r['page_id'] for r in lines})
        page_src = None
        for pid in cand:
            for w in p['waves']:
                if (w, pid) in compiled:
                    page_src = (pid, compiled[(w, pid)])
                    break
            if page_src:
                break
        if page_src:
            shutil.copyfile(page_src[1], os.path.join(od, 'page.jpg'))
            page_info = {'file': 'page.jpg', 'page_id': page_src[0], 'copied_from': os.path.relpath(page_src[1], ROOT),
                         'note': 'compiled page: the scan (left) beside the Google reading of every line of the page (right); admitted and rejected lines'}
        else:
            page_info = {'file': None, 'note': 'no compiled page image exists for this book in the wave compiled folders'}
        dossier = {'rank': p['rank'], 'source': p['source'], 'book_key': p['book_key'], 'wave': p['wave'], 'waves': p['waves'],
                   'year': p['year'], 'title': p['title'], 'class_mix': p['class_mix'], 'majority_class': p['majority_class'],
                   'n_lines': p['n_lines'], 'n_lines_per_split': p['splits'], 'n_pages': p['n_pages'],
                   'suspicion': p['suspicion'], 'aspects_beyond_2sd': p['aspects_beyond_2sd'], 'hard_weighted': p['hard_weighted'],
                   'selected_because': ('top-60 by suspicion' if p['rank'] <= TOP_N else 'non-discounted hard flag'),
                   'scores': {a: {'score': p['aspects'][a]['score'], 'beyond_2sd': p['aspects'][a]['beyond_2sd']} for a in ASPECTS},
                   'hard_flags': [h for a in ASPECTS for h in p['aspects'][a]['hard_flags']],
                   'reasons': p['reasons'], 'context': p['context'],
                   'sheets': sheets, 'sheet_note': 'lines 1-%d random admitted lines (number in black), %d-40 most anomalous (number in dark red; most line flags across A-D)' % (len(randoms), len(randoms) + 1) if anomalous else 'all 40 lines random (no flagged lines)',
                   'page_image': page_info, 'samples': samples,
                   'line_count_rule': 'anomalous = most line flags across A-D, excluding D page:lines_above/below (by construction), C cpp_out_of_range (scan resolution) and A residue of explained kinds (alnum, ref_letter); ties broken by label-quality flags then seeded random'}
        json.dump(dossier, open(os.path.join(od, 'dossier.json'), 'w'), ensure_ascii=False, indent=1)
        open(os.path.join(od, 'question.md'), 'w').write(question_md(dossier))
        index_rows.append((p, name, page_src is not None, sheets))
        p['dossier'] = 'dossiers/' + name

    # ---------------- outputs
    with open(os.path.join(AN, 'book_profiles.jsonl'), 'w') as fh:
        for p in profiles:
            fh.write(json.dumps(p, ensure_ascii=False) + '\n')
    write_index(index_rows, left_out)
    agg = {'n_books': len(profiles), 'n_dossiers': len(dossier_books), 'hard_books_beyond_top60': len(hard_books),
           'hard_books_left_out': [f"{p['rank']}:{p['source']}|{p['book_key']}" for p in left_out],
           'inconsistencies': inconsistencies, 'class_disagreements': [[f'{k[0]}|{k[1]}', v] for k, v in cls_dis],
           'reference_populations': refN, 'recount_mismatch': dict(recount_mismatch), 'degenerate_A_z_beyond': degenerate_A,
           'wave_line_stats': {w: dict(v) for w, v in wave_stats.items()}, 'wave_book_stats': {w: dict(v) for w, v in wave_books.items()},
           'cross_cutting': cc, 'flag_counts': dict(fl_count), 'flag_books': {f: len(v) for f, v in fl_books.items()},
           'flag_wave': {f: dict(v) for f, v in fl_wave.items()}, 'flag_split': {f: dict(v) for f, v in fl_split.items()},
           'suspicion_hist': dict(collections.Counter(p['suspicion'] for p in profiles)),
           'compiled_pages_indexed': len(compiled), 'dossiers_without_page': sum(1 for r in index_rows if not r[2]),
           'dossiers_split_sheets': sum(1 for r in index_rows if len(r[3]) > 1)}
    json.dump(agg, open(os.path.join(AN, 'aggregate_stats.json'), 'w'), ensure_ascii=False, indent=1)
    print(json.dumps({k: agg[k] for k in ('n_books', 'n_dossiers', 'hard_books_beyond_top60', 'inconsistencies', 'recount_mismatch',
                                          'degenerate_A_z_beyond', 'dossiers_without_page', 'dossiers_split_sheets')}, ensure_ascii=False, indent=1))
    print('class disagreements', len(cls_dis))


GLOBAL_RULES = """Pool-wide LINE-LEVEL rules that will be applied to every book anyway (do not answer DROP_PATTERN/RELABEL just for these, unless this
book shows them at an unusual rate or in a form the rule would miss):
- breathing/accent on a capital written as a separate spacing mark (`᾿Α`) is normalised to the precomposed capital (`Ἀ`);
- the University of Crete library stamp (`ΠΑΝΕΠΙΣΤΗΜΙΟ ΚΡΗΤΗΣ`), `ΒΙΒΛΙΟΘΗΚΗ` stamps and `Digitized by Google` footers are dropped;
- lines whose box runs across the gutter of a two-column page (two half-lines from different columns joined) are dropped;
- `ς` inside a word where the same word with `στ` is attested (the στ ligature read as final sigma) is relabelled to `στ`;
- duplicate copies of the same page/text under two keys keep one copy only."""


def fmt_flags(s):
    fl = [f for f in s['flags'] if f not in EXCLUDE_FROM_COUNT]
    return ', '.join(fl) if fl else '–'


def question_md(d):
    t = d['title'] or '(title unknown)'
    L = []
    L.append(f"# Adjudication request — dossier {d['rank']:03d}: {d['source']} / {d['book_key']}\n")
    L.append('You are reviewing one book (source document) from a pool of Google Document AI line readings that will be used as OCR training and '
             'evaluation data (line image → text). Each admitted line is a crop of the scan plus Google\'s transcription (the "label"). '
             'An automatic analysis in four aspects (A language/script, B content/style, C geometry/label-quality proxies, D duplicates/page structure) '
             'flagged this book as unusual compared with books of the same script class. Your job: look at the crops and labels and decide whether the '
             'book\'s labels are usable.\n')
    L.append('## The book\n')
    L.append(f"- Title: {t}")
    L.append(f"- Source / key: `{d['source']}` / `{d['book_key']}` (wave `{d['wave']}`), year {d['year']}")
    L.append(f"- Admitted lines: {d['n_lines']} on {d['n_pages']} pages; split {d['n_lines_per_split']}")
    L.append(f"- Script classes of its lines: {d['class_mix']} (majority `{d['majority_class']}`; greek_poly = polytonic Greek, greek_mono = monotonic, "
             f"greek_latin_cs = Greek with Latin words, latin, cyrillic)")
    L.append(f"- Suspicion score {d['suspicion']} (rank {d['rank']} of 557): {d['aspects_beyond_2sd']} aspect(s) with a feature beyond 2σ of same-class books "
             f"+ weighted hard flags {d['hard_weighted']:g}; selected as {d['selected_because']}.\n")
    L.append('## Why it was flagged\n')
    hf = [h for h in d['hard_flags'] if not h['flag'].startswith('below_support')]
    if hf:
        L.append('Hard flags (weight 1 = counts fully; lower weight = the aspect itself says the rule flags ~5 % of books by construction or is not a label signal):\n')
        for h in hf:
            L.append(f"- **{h['aspect']}:{h['flag']}** (weight {h['weight']:g}) — {h['reason']}" + (f" — discount: {h['discount_reason']}" if h.get('discount_reason') else ''))
        L.append('')
    for a in 'ABCD':
        b = d['scores'][a]['beyond_2sd']
        if b:
            L.append(f"Aspect {a} features beyond 2σ vs same-class books ({len(b)}): " + '; '.join(f"{x['feature']} z={x['z']:+.1f} (value {x['value']})" for x in b[:8]))
    L.append('')
    ctx = d['context']
    L.append(f"Context: majority language `{ctx.get('A_majority_language')}`, other-language share {ctx.get('A_other_language_share')}; "
             f"other-script residue lines {ctx.get('A_residue_lines')} (unexplained {ctx.get('A_residue_lines_unexplained')}); "
             f"B line-flag counts {ctx.get('B_flag_counts')}; C line-flag counts {ctx.get('C_flag_counts')}; median confidence {ctx.get('C_conf_median')}; "
             f"two-column book {ctx.get('D_two_column_book')}, column-crossing share {ctx.get('D_crossing_share')}.\n")
    L.append('## What to look at\n')
    sh = ' and '.join(f'`{s}`' for s in d['sheets'])
    L.append(f"1. {sh}: 40 line crops, each scaled to 48 px height, numbered at the left, with the admitted label printed under each crop. "
             f"{d['sheet_note']}. Compare every label with the pixels above it.")
    if d['page_image']['file']:
        L.append(f"2. `page.jpg`: one compiled page of this book (page `{d['page_image']['page_id']}`): the scan on the left, Google's reading of every line "
                 f"drawn at its position on the right (includes lines that were not admitted). Use it to judge layout (columns, spreads, stamps, tables) "
                 f"and whether the text really is in the language/script the labels say.")
    else:
        L.append('2. No compiled page image exists for this book; judge from the sheet only.')
    L.append('3. The table below lists the same 40 lines with their automatic line flags (aspect:flag).\n')
    L.append('| # | sample | id | class | conf | flags | label |')
    L.append('|---:|---|---|---|---:|---|---|')
    for s in d['samples']:
        lab = s['label'].replace('|', '\\|')
        L.append(f"| {s['n']} | {s['sample']} | `{s['id']}` | {s['script_class']} | {s['confidence']} | {fmt_flags(s)} | {lab} |")
    L.append('')
    L.append(GLOBAL_RULES + '\n')
    L.append('## Your answer\n')
    L.append('Write `decision.json` in this folder:\n')
    L.append('```json\n{"decision": "KEEP | DROP_BOOK | DROP_PATTERN | RELABEL", "confidence": 0.0, "rule_or_pattern": "", "evidence": [], "notes": ""}\n```\n')
    L.append('- **KEEP** — labels match the crops; the flags reflect genre/layout (dictionary, verse, bilingual edition, tables), not wrong labels.')
    L.append('- **DROP_BOOK** — the labels are unreliable throughout (wrong script or language, garbled, columns merged everywhere, not text) or the book duplicates another.')
    L.append('- **DROP_PATTERN** — most lines are fine but a describable subset is not; give the subset as a regex on the label or a precise rule '
             '(e.g. "lines whose label starts with `ΠΑΝΕΠΙΣΤΗΜ`", "lines wider than 0.8 of the text width on two-column pages", "Latin-script lines").')
    L.append('- **RELABEL** — the readings are systematically wrong in a fixable way; say exactly what to replace with what (e.g. "`ς` before a letter → `στ`", '
             '"Latin `A` before a Greek letter → Greek `Α`").')
    L.append('- `confidence`: 0–1, how sure you are. `evidence`: the sheet line numbers that support the decision (e.g. [3, 17, 22]). '
             '`notes`: 2–4 sentences on what you saw (what is wrong, how widespread, anything the flags missed).')
    L.append('- Judge the labels against the pixels, not against modern spelling: 19th-century orthography, katharevousa, polytonic accents, foreign quotations '
             'and abbreviations are correct when the print has them.')
    return '\n'.join(L) + '\n'


def write_index(rows, left_out):
    L = ['# Dossier index', '',
         f'{len(rows)} dossiers: the top-{TOP_N} books by suspicion plus every book with a non-discounted hard flag (weight 1), capped at {CAP}, in rank order. '
         'Suspicion = number of aspects (A–D) with any feature beyond 2σ of same-class books + weighted hard flags (see ../ANOMALIES.md §1). '
         'Each folder holds dossier.json, sheet.jpg (or sheet_1/2.jpg), page.jpg and question.md; the adjudicator writes decision.json there.', '']
    if left_out:
        L.append(f'Hard-flag books not given a dossier because of the cap: {len(left_out)} (ranks {left_out[0]["rank"]}–{left_out[-1]["rank"]}).')
        L.append('')
    L.append('| rank | folder | source | key | title | year | lines | class mix | suspicion | why selected | reasons |')
    L.append('|---:|---|---|---|---|---:|---:|---|---:|---|---|')
    for p, name, has_page, sheets in rows:
        mix = ', '.join(f'{k} {v}' for k, v in p['class_mix'].items())
        t = (p['title'] or '').replace('|', '/')
        if len(t) > 70:
            t = t[:67] + '…'
        why = 'top-60' if p['rank'] <= TOP_N else 'hard flag'
        rs = '; '.join(p['reasons']).replace('|', '/')
        L.append(f"| {p['rank']} | [{name}]({name}/question.md) | {p['source']} | `{p['book_key']}` | {t} | {p['year']} | {p['n_lines']} | {mix} | {p['suspicion']:g} | {why} | {rs} |")
    open(os.path.join(AN, 'dossiers', 'INDEX.md'), 'w').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
