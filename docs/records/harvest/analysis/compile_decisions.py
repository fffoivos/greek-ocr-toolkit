#!/usr/bin/env python3
"""Compile the 120 adjudication decisions + ANOMALIES.md findings into pool-wide line rules.

Run (from the repo root):  .venv/bin/python docs/harvest/analysis/compile_decisions.py

Reads (never modifies): docs/harvest/collection/admitted_all.jsonl, the four aspect line-flag
files, D duplicates.jsonl + page_profiles.jsonl, dossiers/*/{dossier,decision}.json.
Writes ONLY under docs/harvest/analysis/: rules.json, impact.json, DECISIONS.md,
clean_preview/admitted_all_clean_preview.jsonl.gz, clean_preview/dropped_preview.jsonl.gz.
Nothing is applied to the pool: the clean preview is a measurement artefact.
"""
import collections
import glob
import gzip
import json
import os
import re
import sys
import unicodedata as ud

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
AN = os.path.join(ROOT, 'docs/harvest/analysis')
POOL = os.path.join(ROOT, 'docs/harvest/collection/admitted_all.jsonl')
OUTP = os.path.join(AN, 'clean_preview')

NFC = lambda s: ud.normalize('NFC', s)
NFD = lambda s: ud.normalize('NFD', s)


def strip_marks(s):
    return ''.join(c for c in NFD(s) if not ud.combining(c))


def log(*a):
    print(*a, file=sys.stderr, flush=True)


# ----------------------------------------------------------------------------------------------
# 1. dossiers + decisions
# ----------------------------------------------------------------------------------------------
DOSS = []
for p in sorted(glob.glob(os.path.join(AN, 'dossiers/*/decision.json'))):
    folder = os.path.basename(os.path.dirname(p))
    dec = json.load(open(p))
    ds = json.load(open(os.path.join(os.path.dirname(p), 'dossier.json')))
    DOSS.append(dict(no=folder[:3], folder=folder, rank=ds['rank'], source=ds['source'], key=ds['book_key'],
                     bk=ds['source'] + '|' + ds['book_key'], wave=ds['wave'], splits=ds['n_lines_per_split'],
                     n_lines=ds['n_lines'], class_mix=ds['class_mix'], title=ds.get('title'), year=ds.get('year'),
                     decision=dec['decision'], confidence=dec['confidence'], rule=dec.get('rule_or_pattern', ''),
                     notes=dec.get('notes', ''), evidence=dec.get('evidence', [])))
BYNO = {d['no']: d for d in DOSS}
BK_OF = {d['no']: d['bk'] for d in DOSS}
NO_OF_BK = {d['bk']: d['no'] for d in DOSS}
assert len(DOSS) == 120, len(DOSS)
DROP_BOOK = {d['bk'] for d in DOSS if d['decision'] == 'DROP_BOOK'}

# ----------------------------------------------------------------------------------------------
# 2. load pool + aspect flags (all five files are in the same line order; asserted)
# ----------------------------------------------------------------------------------------------


class L:
    __slots__ = ('i', 'id', 'wave', 'source', 'bk', 'page', 'split', 'cls', 'label', 'year',
                 'akinds', 'aflags', 'ashares', 'caps', 'bflags', 'cflags', 'cpb', 'lvb', 'hr', 'dflags', 'dwr', 'ncol')


LINES = []
log('loading pool + flags ...')
fa = gzip.open(os.path.join(AN, 'A_language_script/line_flags.jsonl.gz'), 'rt')
fb = gzip.open(os.path.join(AN, 'B_content_style/line_flags.jsonl.gz'), 'rt')
fc = gzip.open(os.path.join(AN, 'C_geometry_quality/line_flags.jsonl.gz'), 'rt')
fd = gzip.open(os.path.join(AN, 'D_duplicates_pages/line_flags.jsonl.gz'), 'rt')
with open(POOL) as fp:
    for i, (lp, la, lb, lc, ld) in enumerate(zip(fp, fa, fb, fc, fd)):
        r = json.loads(lp); a = json.loads(la); b = json.loads(lb); c = json.loads(lc); d = json.loads(ld)
        assert r['id'] == a['id'] == b['id'] == c['id'] == d['id'], (i, r['id'])
        x = L()
        x.i = i; x.id = r['id']; x.wave = r['wave']; x.source = r['source']; x.bk = r['source'] + '|' + r['book_key']
        x.page = r['page_id']; x.split = r['split']; x.cls = r['script_class']; x.label = r['label']; x.year = r['year']
        kinds = set(); af = set()
        for f in a['flags']:
            af.add(f['flag'])
            if f['flag'] == 'other_script_residue':
                kinds.update(f.get('kinds', []))
        x.akinds = kinds; x.aflags = af; x.ashares = a['features'].get('script_shares') or {}
        x.caps = bool(b.get('is_all_caps')); x.bflags = set(b['flags'])
        cf = {}
        for f in c['flags']:
            cf[f['flag']] = 'low' if '<' in f['reason'] else 'high'
        x.cflags = cf; x.cpb = c.get('cpp_vs_book'); x.lvb = c.get('len_vs_book'); x.hr = c.get('height_ratio')
        x.dflags = set(d['flags']); x.dwr = d.get('width_ratio'); x.ncol = d.get('page_n_columns')
        LINES.append(x)
for f in (fa, fb, fc, fd):
    assert f.readline() == '', 'flag file longer than pool'
N = len(LINES)
log('lines', N)
assert N == 293439

BOOK_LINES = collections.defaultdict(list)
PAGE_LINES = collections.defaultdict(list)
for x in LINES:
    BOOK_LINES[x.bk].append(x)
    PAGE_LINES[x.page].append(x)
for no, bk in BK_OF.items():
    assert bk in BOOK_LINES, (no, bk)

BOOK_MAJ = {bk: collections.Counter(x.cls for x in ls).most_common(1)[0][0] for bk, ls in BOOK_LINES.items()}

# vocabulary (NFC lowercase word tokens) for the στ rule and the split-word check
WORD = re.compile(r'[^\W\d_]+')
VOCAB = collections.Counter()
for x in LINES:
    for w in WORD.findall(NFC(x.label)):
        VOCAB[w.lower()] += 1

# page profiles: book two-column majority
PAGE_PROF = {}
BOOK_PAGES = collections.defaultdict(list)
for l in open(os.path.join(AN, 'D_duplicates_pages/page_profiles.jsonl')):
    r = json.loads(l)
    PAGE_PROF[r['page_id']] = r
    BOOK_PAGES[r['source_key']].append(r)


def two_col_majority(bk):
    ps = [p for p in BOOK_PAGES.get(bk, []) if p.get('n_admitted', 0) > 0]
    n2 = sum(1 for p in ps if (p.get('n_columns') or 0) >= 2)
    return (n2 * 2 > len(ps)) if ps else False, n2, len(ps)


# ----------------------------------------------------------------------------------------------
# 3. rule scopes / constants
# ----------------------------------------------------------------------------------------------
SCANNED_WAVES = {'round1', 'round2', 'vouli', 'parliament', 'cyrillic'}


def is_oa(x):
    return x.source.startswith('openarchives')


def is_scanned(x):
    # round1, round2, vouli, parliament, cyrillic + the Anemi / Internet-Archive parts of `mixed`
    return x.wave in SCANNED_WAVES or (x.wave == 'mixed' and not is_oa(x))


# R2 book sets ---------------------------------------------------------------------------------
R2_ADJ_TWO_COL = ['005', '017', '018', '021', '030', '032', '033', '045', '047', '048', '053', '076', '078',
                  '085', '086', '098', '099', '101', '103', '104', '111', '119']
R2_EXCLUDE = ['049', '055', '020', '097', '108', '134', '012', '088', '100', '125', '117']
R2_ALL_PAGES_W08 = ['017', '018', '021', '030', '047', '085']   # adjudicators: width > 0.8 on ALL pages
TWO_COL_BOOKS = set()
for bk in BOOK_LINES:
    if two_col_majority(bk)[0]:
        TWO_COL_BOOKS.add(bk)
TWO_COL_MAJ = set(TWO_COL_BOOKS)
for no in R2_ADJ_TWO_COL:
    TWO_COL_BOOKS.add(BK_OF[no])
for no in R2_EXCLUDE:
    TWO_COL_BOOKS.discard(BK_OF[no])
R2_ALL_PAGES_BK = {BK_OF[n] for n in R2_ALL_PAGES_W08}

# R1 ------------------------------------------------------------------------------------------
R1_RE = re.compile(r'^[-–\s]*(ΠΑΝΕΠΙΣΤΗΜΙΟ?Ν?(\s+ΚΡ\w*)?|ΒΙΒΛΙΟΘΗΚΗ|Digiti[sz]ed\s+by\s+\w+|Πανεπιστήμιο\s+Θεσσαλίας)\W*$')

# R4 ------------------------------------------------------------------------------------------
TOK = re.compile(r'\S+')
PUNCT_STRIP = '.,;:·!?«»"\'()[]{}—–-‘’“”*'
REDUP_OK = {'κατω', 'λιγο', 'σιγα', 'ενα', 'δυο', 'καλα', 'γυρω', 'περα', 'ισα', 'αργα', 'τωρα', 'ψιλα',
            'κοντα', 'φρου', 'ακρη', 'ορθα', 'μονο', 'πολυ', 'τσιγκανα', 'ολο', 'ολα', 'μια', 'ευθυς'}


def grave_to_acute(s):
    # oxia and varia are positional variants of one accent (final acute -> grave before a word): not a doubled reading
    return NFC(NFD(s).replace('\u0300', '\u0301'))


def doubled_pairs(label):
    """(n exact adjacent pairs compared WITH punctuation, n accent-variant pairs, exact words); tokens need >= 2 letters"""
    raw = TOK.findall(NFC(label))
    ex = 0; av = 0; words = []
    for a, b in zip(raw, raw[1:]):
        if sum(ch.isalpha() for ch in a) < 2:
            continue
        if a == b:
            ex += 1; words.append(strip_marks(a.strip(PUNCT_STRIP)).lower())
            continue
        sa, sb = grave_to_acute(a.strip(PUNCT_STRIP)), grave_to_acute(b.strip(PUNCT_STRIP))
        if sum(ch.isalpha() for ch in sa) < 2:
            continue
        if sa.casefold() != sb.casefold() and strip_marks(sa).casefold() == strip_marks(sb).casefold():
            av += 1
    return ex, av, words


# R5 ------------------------------------------------------------------------------------------
R5_RE = re.compile(r'[^\W\d_]- (?!(?:and|und|or|oder|et|ou|e|y|καὶ|και|ἢ|ή|ἤ|καί)\b)(?=[^\W\d_])(?=\w)')
R5_OPEN_DASH = re.compile(r'(?:^|\s)[-—–]\s?[^\W\d_]')


def r5_hit(label):
    m = R5_RE.search(label)
    if not m:
        return False
    nxt = label[m.end()]
    if not nxt.islower():          # continuation of a hyphenated word starts lower-case
        return False
    if R5_OPEN_DASH.search(label[:m.start() + 1]):   # closing half of a parenthetical dash pair ('—αὐτὸ ... ἐργαζόμενου- ἀλλὰ')
        return False
    return True

# R6 ------------------------------------------------------------------------------------------
SPACING = {'᾿': '̓', '᾽': '̓', '῾': '̔', '῎': '̓́',
           '῍': '̓̀', '῏': '̓͂', '῞': '̔́', '῝': '̔̀',
           '῟': '̔͂', '΄': '́'}
R6_RE = re.compile(r'(^|[\s(«\[“"‘\'])([' + ''.join(SPACING) + r'])([ΑΕΗΙΟΥΩΡ])')


def r6_relabel(label, poly):
    """returns (new_label, n_relabelled, n_ambiguous).  In polytonic lines a spacing TONOS (U+0384) before a capital
    is Google's rendering of a breathing (΄Αγιον = Ἅγιον, ΄Ελασσῶνα = Ἐλασσῶνα), so it is ambiguous there (dropped);
    in monotonic lines it is the tonos and becomes Ά/Έ/... ."""
    n = 0; amb = 0

    def sub(m):
        nonlocal n, amb
        if m.group(2) == '\u0384' and poly:
            amb += 1
            return m.group(0)
        comb = NFC(m.group(3) + SPACING[m.group(2)])
        if len(comb) != 1:          # no precomposed capital (e.g. psili on Υ or Ρ): leave as printed
            return m.group(0)
        n += 1
        return m.group(1) + comb
    out = R6_RE.sub(sub, label)
    return out, n, amb


R6B_RE = re.compile(r'(?<![\w])"([ΑΕΗΙΟΥΩ])([^\W\d_]*)')
R6B_MARKS = ['\u0313\u0301', '\u0314\u0301', '\u0313\u0300', '\u0314\u0300']   # Ἄ Ἅ Ἂ Ἃ types


def r6b(label):
    """ASCII '"' used as breathing+accent before a bare capital vowel ('"Αλλο').  For each occurrence the candidate
    words of Ἄ/Ἅ/Ἂ/Ἃ type are looked up in the pool vocabulary: exactly one attested -> relabel to it (unambiguous);
    none or several -> the line is dropped.  Returns (new_label, n_relabelled, n_ambiguous)."""
    n_ok = 0; n_amb = 0

    def sub(m):
        nonlocal n_ok, n_amb
        att = []
        for mk in R6B_MARKS:
            cap = NFC(m.group(1) + mk)
            if len(cap) != 1:
                continue
            c = cap + m.group(2)
            if VOCAB.get(c.lower(), 0) > 0:
                att.append(c)
        if len(att) == 1:
            n_ok += 1
            return att[0]
        n_amb += 1
        return m.group(0)
    out = R6B_RE.sub(sub, label)
    return out, n_ok, n_amb


# R7 ------------------------------------------------------------------------------------------
R7_RE = re.compile(r'(?:^|(?<=[\s(\[«•·|]))([ΑΕΗΙΟΥΩ])(?![ἀ-῿])([α-ωά-ώ]|\s|$)')


def r7_hit(label):
    for m in R7_RE.finditer(label):
        rest = label[m.end(1):]
        nxt = rest.lstrip()
        if m.group(2) == '' or not nxt:          # line-final bare capital (vote mark Ο / initial at line end)
            continue
        if m.group(2).isspace():
            if m.group(1) not in 'ΟΗ':      # only the articles Ὁ/Ἡ are one-letter vowel words; Α, Ι ... are figure letters
                continue
            # single-letter word: article Ο/Η/Ὁ... skip when the next word is ALL CAPS (caps text carries no breathings)
            w = nxt.split()[0].strip(PUNCT_STRIP)
            if w and w.upper() == w:
                continue
        return True
    return False


# R8 ------------------------------------------------------------------------------------------
ST_EXCL_PREFIX = ('προς', 'πρὸς', 'πρός', 'εις', 'εἰς', 'ὡς', 'ως', 'ὥς', 'ὥςτε', 'ωςτε', 'ὁπωςδήποτε')
GREEK_LETTER = re.compile(r'[Ͱ-Ͽἀ-῿]')


def r8_relabel(label):
    """ς followed by a Greek letter inside a word -> στ when the στ-form is attested in the pool."""
    lab = NFC(label); out = []; last = 0; n = 0
    for m in WORD.finditer(lab):
        w = m.group(0)
        if 'ς' not in w[:-1]:
            continue
        lw = w.lower()
        if lw.startswith(ST_EXCL_PREFIX) or 'δηποτ' in strip_marks(lw):
            continue
        cand = re.sub(r'ς(?=[Ͱ-Ͽἀ-῿])', 'στ', w)
        if cand != w and VOCAB.get(cand.lower(), 0) > 0:
            out.append(lab[last:m.start()]); out.append(cand); last = m.end(); n += 1
    if not n:
        return label, 0
    out.append(lab[last:])
    return ''.join(out), n


GREEK_CONS = 'βγδζθκλμνξπρσςτφχψ'


def r8b_relabel(label):
    """plain σ for the στ ligature ('σρατοῦ'): word attested only here (pool count <= 1), its σ->στ form attested
    >= 3 times in the pool, σ followed by a consonant -> relabel σ->στ."""
    lab = NFC(label); out = []; last = 0; n = 0
    for m in WORD.finditer(lab):
        w = m.group(0)
        if len(w) < 5 or 'σ' not in w or VOCAB.get(w.lower(), 0) > 1:
            continue
        for j, ch in enumerate(w[:-1]):
            if ch == 'σ' and strip_marks(w[j + 1]).lower() in GREEK_CONS and w[j + 1] != 'τ':
                cand = w[:j] + 'στ' + w[j + 1:]
                if VOCAB.get(cand.lower(), 0) >= 3:
                    out.append(lab[last:m.start()]); out.append(cand); last = m.end(); n += 1
                    break
    if not n:
        return label, 0
    out.append(lab[last:])
    return ''.join(out), n


# R9 ------------------------------------------------------------------------------------------
UNITS = {'km', 'm', 'cm', 'mm', 'kg', 'g', 'mg', 'ml', 'l', 'nm', 'kw', 'mw', 'hz', 'khz', 'mhz', 'ghz', 'v', 'kv',
         'w', 'n', 'kn', 'pa', 'kpa', 'mpa', 'gb', 'mb', 'kb', 's', 'ms', 'h', 'min', 'ha', 'db', 'mm²', 'km²', 'm²'}
R9_KINDS = {'unexpected_word', 'unexpected_standalone_lookalike', 'isolated_standalone_lookalike'}


def script_of(ch):
    o = ord(ch)
    if 0x0370 <= o <= 0x03FF or 0x1F00 <= o <= 0x1FFF:
        return 'greek'
    if 0x0400 <= o <= 0x052F:
        return 'cyrillic'
    if ch.isalpha() and o < 0x0250:
        return 'latin'
    return None


def r9_hit(x):
    lab = NFC(x.label)
    if x.wave != 'cyrillic' and x.cls != 'cyrillic' and BOOK_MAJ.get(x.bk) != 'cyrillic' \
            and any(0x0400 <= ord(ch) <= 0x052F for ch in lab):
        return 'cyrillic_in_non_cyrillic'
    if not (x.akinds & R9_KINDS):
        return None
    sh = x.ashares or {}
    maj = max(('greek', 'latin', 'cyrillic'), key=lambda k: sh.get(k, 0))
    toks = lab.split()
    for j, t in enumerate(toks):
        letters = [ch for ch in t if ch.isalpha()]
        if not letters:
            continue
        scr = {script_of(ch) for ch in letters} - {None}
        if not scr or maj in scr:
            continue
        core = t.strip(PUNCT_STRIP)
        if any(ch.isdigit() for ch in t) or core.lower() in UNITS:
            continue
        prev = toks[j - 1] if j else ''; nxt = toks[j + 1] if j + 1 < len(toks) else ''
        if re.search(r'\d\W*$', prev) or re.match(r'^\W*\d', nxt):
            continue
        # isolated_* kinds: the line expects the other script; only single look-alike letters count
        if x.akinds <= {'isolated_standalone_lookalike', 'isolated_standalone', 'isolated_ref_letter', 'isolated_alnum'} \
                and len(letters) > 1:
            continue
        return 'lookalike_token'
    return None


# R12 -----------------------------------------------------------------------------------------
R12_MATH = re.compile(r'[∈∑≤≥≠∃∀±×√∞∂∫∉⊂⊆⊇∪∩∅]')
R12_SINGLE_LATIN = re.compile(r"(?<![\w.'’\-/\\@])[A-Za-z](?![\w'’.\-/\\@])")
R12_LISTMARK = re.compile(r'^\s*[A-Za-z]\)')
R12_CODE = re.compile(r':=|==|!=|\w_\w|\.\w+\(|\(\)|[{}]|</?[A-Za-z]+>|\bxl[A-Z]\w+')


def r12_hit(x):
    lab = x.label
    if R12_MATH.search(lab):
        return 'math_symbol'
    if R12_CODE.search(lab):
        return 'code'
    if x.cls in ('greek_mono', 'greek_poly', 'greek_latin_cs'):
        s = R12_LISTMARK.sub('', lab)
        for m in R12_SINGLE_LATIN.finditer(s):
            ch = m.group(0)
            if x.cls == 'greek_latin_cs' and ch in 'aAI':
                continue
            return 'single_latin_letter'
    return None


# R14 -----------------------------------------------------------------------------------------
R14_LEADER = re.compile(r'(?:[.·•]\s?){5,}|…{2,}')
R14_VOTE = re.compile(r'\s[ONΟΝ0]$')

# R15 book-specific -----------------------------------------------------------------------------


def cany(x, *fl):
    return any(f in x.cflags for f in fl)


def cpp_low(x):
    return x.cflags.get('cpp_vs_book_out') == 'low'


def crossmerge(x):
    return 'column_crossing_line' in x.dflags or 'column_merge_line' in x.dflags


SINGLE_GR_NOT_ARTICLE = re.compile(r"(?<![\w'’])(?![οηήΟΗΉ](?![\w'’]))[Α-Ωα-ωά-ώ](?![\w'’])")
SINGLE_ANY_NOT_ARTICLE = re.compile(r"(?<![\w'’])(?![οηήΟΗΉ](?![\w'’]))[A-Za-zΑ-Ωα-ωά-ώ](?![\w'’])")


def split_word_084(x):
    toks = WORD.findall(NFC(x.label))
    for a, b in zip(toks, toks[1:]):
        if a.islower() and b.islower() and len(a) >= 2 and len(b) <= 3:
            j = (a + b).lower()
            if VOCAB.get(j, 0) >= 2 and (VOCAB.get(a.lower(), 0) <= 1 or VOCAB.get(b.lower(), 0) <= 1):
                return True
    return False


def wide_on_2col_page(x, thr):
    return (x.ncol or 0) >= 2 and (x.dwr or 0) > thr


HOMO_L2G = str.maketrans('ABEHIKMNOPTXYZ', 'ΑΒΕΗΙΚΜΝΟΡΤΧΥΖ')


def relabel_096(lab):
    def sub(m):
        return m.group(0).translate(HOMO_L2G)
    return re.sub(r'(?<![A-Za-z])[ABEHIKMNOPTXYZ]{2,}(?![A-Za-z])', sub, lab)


def relabel_006(lab):
    lab = re.sub(r'(?<![\wА-яѣъ])п\.(?=\s|$|,)', 'n.', lab)
    lab = re.sub(r'(?<![\wА-яѣъ])ст\.(?=\s)', 'vt.', lab)
    lab = re.sub(r'(?<![\wА-яѣъ])α\.(?=\s|$)', 'a.', lab)
    lab = re.sub(r'(?<![\wА-яѣъ])в\.(?= [A-Za-z])', 'v.', lab)
    return lab


CYR2GR_CAP = {'А': 'Α', 'В': 'Β', 'Е': 'Ε', 'Г': 'Γ', 'К': 'Κ', 'М': 'Μ', 'Н': 'Η', 'О': 'Ο', 'Р': 'Ρ', 'С': 'Σ', 'Т': 'Τ', 'Х': 'Χ'}


def relabel_014(lab):
    lab = lab.replace('Г', 'Γ')
    return re.sub(r'(?<![\w])([АВЕКМНОРТХ])(?=[.:])', lambda m: CYR2GR_CAP[m.group(1)], lab)


def relabel_016(lab):
    lab = re.sub(r'^([ΙIΟO]{2,4})\.', lambda m: m.group(1).translate(str.maketrans('ΙIΟO', '1100')) + '.', lab)
    return re.sub(r'^(\d+ )?– ', lambda m: (m.group(1) or '') + '= ', lab)


def relabel_086(lab):
    lab = lab.replace('(6)', '(ὁ)').replace('(5)', '(ὁ)').replace('(ή)', '(ἡ)').replace('(το)', '(τὸ)')
    return re.sub(r'(?<=[a-zé\-], )[60]\.(?=\s|$|,)', 'θ.', lab)


def relabel_087(lab):
    lab = re.sub(r"^(?:Ε['΄’]?ρ|Εἰρ)\.", 'Ἐρ.', lab)
    return re.sub(r"^Α['΄’]?π\.", 'Ἀπ.', lab)


R15 = {  # dossier no -> list of (sub-id, kind, description, predicate or relabel fn)
    '001': [('drop', 'C:cpp_vs_book_out (either side) | C:cph_out_of_range | C:repeated_word | label ~ \\b(\\S+\\.?) \\1\\b (all-caps included)',
             lambda x: cany(x, 'cpp_vs_book_out', 'cph_out_of_range', 'repeated_word') or re.search(r'\b(\S+\.?) \1\b', x.label))],
    '002': [('drop', 'C:cph_out_of_range | C:cpp_vs_book_out (either side) | C:len_vs_book_high (all-caps included)',
             lambda x: cany(x, 'cph_out_of_range', 'cpp_vs_book_out', 'len_vs_book_high'))],
    '004': [('drop', 'script_class=latin | V/A subscript-formula regex | \\bWu\\b | C:cph_out_of_range',
             lambda x: x.cls == 'latin' or re.search(r'(?:[VA]s?w?|V)(?:Rd|Ed|sw),(?:max|min)|\bWu\b', x.label) or cany(x, 'cph_out_of_range'))],
    '006': [('relabel', "italic Latin abbreviations read as Cyrillic/Greek: п.→n., ст.→vt., α.→a., в.+Latin→v.", relabel_006),
            ('drop', "stress mark written '/' inside the pronunciation parenthesis", lambda x: re.search(r'\([^)]*/[^)]*\)', x.label))],
    '007': [('drop', 'optical-rotation prefix d-/l- misread before a Greek name | molecular formula C\\d+H\\d+',
             lambda x: re.search(r'(?:^|[\s,(])(?:[0-9]|[IΙldὰ])\s?-\s?[Ͱ-Ͽἀ-῿]', x.label) or re.search(r'C\d+H\d+', x.label))],
    '013': [('drop', 'C:cph_out_of_range | C:cpp_vs_book_out (either side)', lambda x: cany(x, 'cph_out_of_range', 'cpp_vs_book_out'))],
    '014': [('relabel', 'Cyrillic look-alike recipe enumerators → Greek (Г→Γ; lone Cyrillic capital before . or :)', relabel_014),
            ('drop', '(C:cpp_vs_book_out & C:cph_out_of_range) | label starts with digit + dot run (misread italic recipe letter)',
             lambda x: (cany(x, 'cpp_vs_book_out') and cany(x, 'cph_out_of_range')) or re.match(r'^\d\s?\.{4,}', x.label))],
    '016': [('relabel', "typewriter district codes ΙΙΙ./ΙΟΙ. → 111./101.; leading '–' → '='", relabel_016)],
    '017': [('drop', 'D width_ratio > 0.6 on all pages', lambda x: (x.dwr or 0) > 0.6)],
    '018': [('drop', 'D width_ratio > 0.6 on all pages', lambda x: (x.dwr or 0) > 0.6)],
    '019': [('drop', 'C:cph_out_of_range & C:cpp_vs_book_out', lambda x: cany(x, 'cph_out_of_range') and cany(x, 'cpp_vs_book_out'))],
    '024': [('drop', 'cpp_vs_book < 0.5', lambda x: x.cpb is not None and x.cpb < 0.5),
            ('relabel', "'Σχ. δον' → 'Σχ. 8ον'", lambda lab: re.sub(r'Σχ\. δον', 'Σχ. 8ον', lab))],
    '031': [('drop', 'C:cpp_vs_book_out (either side) & label not all-caps', lambda x: cany(x, 'cpp_vs_book_out') and not x.caps)],
    '032': [('drop', 'C:cpp_vs_book_out | C:repeated_word', lambda x: cany(x, 'cpp_vs_book_out', 'repeated_word'))],
    '033': [('drop', 'C:cpp_vs_book_out | C:repeated_word', lambda x: cany(x, 'cpp_vs_book_out', 'repeated_word'))],
    '034': [('drop', "dot-leader run (\\.{2,}|[·•]\\s?[·•]) | trailing vote mark \\s[ONΟΝ0]$ | C:cpp_vs_book_out | C:repeated_word",
             lambda x: re.search(r'(\.{2,}|[·•]\s?[·•])', x.label) or re.search(r'\s[ONΟΝ0]$', x.label) or cany(x, 'cpp_vs_book_out', 'repeated_word'))],
    '036': [('drop', 'C:cpp_vs_book_out (cpp_vs_book < 0.5 side)', lambda x: cany(x, 'cpp_vs_book_out')),
            ('relabel', "ordinal β read as 6 after ἀορ./παρκ./μελ./ὑπερσ.", lambda lab: re.sub(r'(ἀορ|παρκ|μελ|ὑπερσ)\. 6\.', r'\1. β.', lab))],
    '045': [('drop', 'C:cpp_vs_book_out | C:repeated_word', lambda x: cany(x, 'cpp_vs_book_out', 'repeated_word'))],
    '046': [('drop', 'C:cpp_vs_book_out | C:repeated_word', lambda x: cany(x, 'cpp_vs_book_out', 'repeated_word'))],
    '048': [('drop', 'C:cpp_vs_book_out | C:repeated_word', lambda x: cany(x, 'cpp_vs_book_out', 'repeated_word'))],
    '049': [('drop', 'C:repeated_word', lambda x: cany(x, 'repeated_word'))],
    '051': [('drop', 'C:cpp_vs_book_out', lambda x: cany(x, 'cpp_vs_book_out'))],
    '053': [('drop', 'D:column_crossing_line | C:cpp_vs_book_out | C:len_vs_book_high',
             lambda x: 'column_crossing_line' in x.dflags or cany(x, 'cpp_vs_book_out', 'len_vs_book_high'))],
    '055': [('drop', 'C:height_ratio_low | C:repeated_word', lambda x: cany(x, 'height_ratio_low', 'repeated_word'))],
    '056': [('drop', 'C:cpp_vs_book_out', lambda x: cany(x, 'cpp_vs_book_out'))],
    '059': [('drop', 'C:cph_out_of_range', lambda x: cany(x, 'cph_out_of_range'))],
    '069': [('drop', 'inline maths: [=<>«≪√∂|] or a standalone single letter other than ο/η/ή/Ο/Η/Ή',
             lambda x: re.search(r'[=<>«≪√∂|]', x.label) or SINGLE_ANY_NOT_ARTICLE.search(x.label))],
    '072': [('drop', 'D width_ratio > 0.9 & cpp_vs_book < 0.8', lambda x: (x.dwr or 0) > 0.9 and x.cpb is not None and x.cpb < 0.8)],
    '073': [('drop', 'any Latin letter | maths symbols | standalone single Greek letter other than ο/η/ή',
             lambda x: re.search(r'[A-Za-z=≠≤≥∈∉⊂⊆⊇√∅Ø⟨⟩<>|]', x.label) or SINGLE_GR_NOT_ARTICLE.search(x.label))],
    '075': [('drop', 'monospaced VBA listing regex',
             lambda x: re.search(r'''(:=|\bxl[A-Z]\w+|^\s*(Call|Selection|Active\w+|Add|Origin|DataOption|Range)\b|^\s*[.'"]|\w_\w|\.\w+\()''', x.label))],
    '076': [('drop', 'two or more immediate word repeats', lambda x: re.search(r'(\b\S+) \1\b.*(\b\S+) \2\b', x.label)),
            ('relabel', "'§' misread as 8 between numbers: (\\d) 8 (\\d) → '\\1 § \\2'", lambda lab: re.sub(r'(\d) 8 (\d)', r'\1 § \2', lab))],
    '079': [('drop', "inline maths: [=×<>|∈] | ',...,' | capital + ';' | standalone single letter other than ο/η/ή",
             lambda x: re.search(r'[=×<>|∈]|,\.\.\.,|[A-ZΑ-Ω];', x.label) or SINGLE_ANY_NOT_ARTICLE.search(x.label))],
    '084': [('drop', 'C:cpp_vs_book_out | Greek mid-label hyphen break | split word (joined form attested, a part unattested)',
             lambda x: cany(x, 'cpp_vs_book_out') or re.search(r'[α-ωά-ώΑ-Ω]- [α-ωά-ώ]', x.label) or split_word_084(x))],
    '086': [('relabel', "gender markers (6)/(5)→(ὁ), (ή)→(ἡ), (το)→(τὸ), ', 6.'/', 0.'→', θ.'", relabel_086)],
    '087': [('relabel', "catechism markers Ερ./Ε΄ρ./Εἰρ.→Ἐρ., Απ./Α΄π.→Ἀπ. at line start", relabel_087)],
    '090': [('drop', "'\\d0 ΒΗΜΑ' (ordinal 3ο read as 30)", lambda x: re.search(r'\d0 ΒΗΜΑ', x.label))],
    '096': [('drop', 'C:cpp_vs_book_out | C:len_vs_book_high | height_ratio > 1.4',
             lambda x: cany(x, 'cpp_vs_book_out', 'len_vs_book_high') or (x.hr or 0) > 1.4),
            ('relabel', 'Latin look-alike capitals in Greek caps words → Greek (ENOIKIA → ΕΝΟΙΚΙΑ)', relabel_096)],
    '097': [('relabel', "Latin 'Ha' before a number → Cyrillic 'На'", lambda lab: re.sub(r'(?<![A-Za-z])Ha(?= \d)', 'На', lab))],
    '098': [('drop', 'C:len_vs_book_high | C:cpp_vs_book_out | C:repeated_word | D crossing/merge | height_ratio > 1.4',
             lambda x: cany(x, 'len_vs_book_high', 'cpp_vs_book_out', 'repeated_word') or crossmerge(x) or (x.hr or 0) > 1.4)],
    '099': [('drop', 'C:len_vs_book_high | C:cpp_vs_book_out | C:repeated_word | D crossing/merge | height_ratio > 1.4 | \\b(\\w{4,})\\w*,? \\1',
             lambda x: cany(x, 'len_vs_book_high', 'cpp_vs_book_out', 'repeated_word') or crossmerge(x) or (x.hr or 0) > 1.4
             or re.search(r'\b(\w{4,})\w*,? \1', x.label))],
    '101': [('drop', 'C:cpp_vs_book_out | C:len_vs_book_high | D crossing/merge | (C:cph_out_of_range & cpp_vs_book < 0.6) | height_ratio > 1.4',
             lambda x: cany(x, 'cpp_vs_book_out', 'len_vs_book_high') or crossmerge(x)
             or (cany(x, 'cph_out_of_range') and x.cpb is not None and x.cpb < 0.6) or (x.hr or 0) > 1.4)],
    '102': [('drop', "[^\\s\\d-]- \\S (next line's word appended after a hyphen break)", lambda x: re.search(r'[^\s\d-]- \S', x.label))],
    '103': [('drop', 'D width_ratio > 0.55 on 2-column pages | C:cpp_vs_book_out | C:len_vs_book_high | C:cph_out_of_range',
             lambda x: wide_on_2col_page(x, 0.55) or cany(x, 'cpp_vs_book_out', 'len_vs_book_high', 'cph_out_of_range'))],
    '104': [('drop', 'C:cpp_vs_book_out | D crossing/merge', lambda x: cany(x, 'cpp_vs_book_out') or crossmerge(x))],
    '106': [('drop', 'C:height_ratio_high | C:cpp_vs_book_out', lambda x: cany(x, 'height_ratio_high', 'cpp_vs_book_out'))],
    '107': [('drop', "running head '^ΣΥΝΕΔΡΙΑΣΗ .*ΦΕΒΡΟΥΑΡΙΟΥ 19\\d\\d$' (koppa misread) | C:len_vs_book_high",
             lambda x: re.search(r'^ΣΥΝΕΔΡΙΑΣΗ .*ΦΕΒΡΟΥΑΡΙΟΥ 19\d\d$', x.label) or cany(x, 'len_vs_book_high'))],
    '109': [('drop', "C:cpp_vs_book_out | label begins with a lone Latin 'H' (drop capital)",
             lambda x: cany(x, 'cpp_vs_book_out') or re.match(r'^H(?![A-Za-z])', x.label))],
    '110': [('drop', "[ς\"*]\\) (superscript footnote numeral misread before ')')", lambda x: re.search(r'[ς"*]\)', x.label))],
    '111': [('drop', 'D width_ratio > 0.55 on 2-column pages | C:cpp_vs_book_out | C:cph_out_of_range | C:len_vs_book_high',
             lambda x: wide_on_2col_page(x, 0.55) or cany(x, 'cpp_vs_book_out', 'cph_out_of_range', 'len_vs_book_high'))],
    '117': [('drop', "numismatic metal-sign misreads | '|' in label | marginal heading after a hyphen break (letter- Capital) | D:column_merge_line on 2-column pages",
             lambda x: re.search(r'(?:^|[\s.])(?:Ο|ΚΕ|[AP]\.|Α\.|Ρ\.)\s*(?:[Σσ]τατ|[Δδ]ρ|[Tτ]ετρ|[Δδ]ίδρ|[Ὀὀ]βολ|[Ἡἡ]μ)', x.label)
             or '|' in x.label or re.search(r'[^\W\d_]- [Α-ΩἈ-Ὧ]', x.label) or ('column_merge_line' in x.dflags and (x.ncol or 0) >= 2))],
    '119': [('drop', 'D:column_crossing_line | D:column_merge_line | C:len_vs_book_high', lambda x: crossmerge(x) or cany(x, 'len_vs_book_high'))],
    '129': [('drop', 'C:conf_min_low | A:other_script_residue', lambda x: cany(x, 'conf_min_low') or 'other_script_residue' in x.aflags)],
}
R13_NAMED = {  # pages adjudicators named as skewed / mis-segmented
    '019': ['c3468c02b6d929362f6e3fe7-p000191'],
    '045': ['87d33c70-p000007'],
    '051': ['8b231047fdbd96ec30e1eded-p000009', '8b231047fdbd96ec30e1eded-p000013', '8b231047fdbd96ec30e1eded-p000022'],
    '056': ['1be3f9227e2b68a2b9974abe-p000023'],
}

# ----------------------------------------------------------------------------------------------
# 4. evaluate rules
# ----------------------------------------------------------------------------------------------
DROP = collections.defaultdict(set)        # line index -> rule ids
RELABEL = collections.defaultdict(list)    # line index -> rule ids (in order)
LABEL2 = {}                                # line index -> new label
SUB = collections.Counter()                # (rule, sub-predicate) -> lines
EXAMPLES = collections.defaultdict(list)


def ex(rule, x, extra=None):
    if len(EXAMPLES[rule]) < 6:
        EXAMPLES[rule].append({'id': x.id, 'label': x.label, **({'note': extra} if extra else {})})


log('evaluating rules ...')
bk_no = NO_OF_BK
R6B_AMBIG = set()
# pass A: relabels (R6, R6b-109, R8, R15 relabels) -> label_v2
for x in LINES:
    lab = x.label; rules = []
    poly = x.cls == 'greek_poly' or (x.wave == 'vouli' and x.cls == 'greek_mono')
    new, n, amb = r6_relabel(lab, poly)
    if amb:
        R6B_AMBIG.add(x.i)
    if n:
        lab = new; rules.append('R6'); SUB[('R6', 'spacing_mark_capital')] += 1
    no = bk_no.get(x.bk)
    if (x.cls == 'greek_poly' or (x.wave == 'vouli' and x.cls == 'greek_mono')) and '"' in lab:
        new, n_ok, n_amb = r6b(lab)
        if n_amb:
            R6B_AMBIG.add(x.i)
        if n_ok:
            lab = new; rules.append('R6'); SUB[('R6', 'ascii_quote_unambiguous')] += 1; ex('R6_quote', x, new)
    if x.cls in ('greek_poly', 'greek_mono'):
        new, n8b = r8b_relabel(lab)
        if n8b:
            lab = new; rules.append('R8'); SUB[('R8', 'plain σ for στ ligature')] += 1; ex('R8_plain_sigma', x, new)
    if x.cls in ('greek_poly', 'greek_mono', 'greek_latin_cs'):
        new, n = r8_relabel(lab)
        if n:
            lab = new; rules.append('R8'); SUB[('R8', 'final_sigma_for_st')] += 1; ex('R8', x, new)
    for kind, desc, fn in R15.get(no, []):
        if kind == 'relabel':
            new = fn(lab)
            if new != lab:
                lab = new; rules.append('R15'); SUB[('R15', no + ' relabel')] += 1; ex('R15_relabel_' + no, x, new)
    if rules:
        RELABEL[x.i] = list(dict.fromkeys(rules)); LABEL2[x.i] = lab

# R11 metadata (not a label change; recorded separately)
R11_LINES = [x for x in LINES if is_oa(x)]

# pass B: drops
R3_FLAG = {}
for x in LINES:
    lab2 = LABEL2.get(x.i, x.label)
    no = bk_no.get(x.bk)
    hits = DROP[x.i]
    if x.bk in DROP_BOOK:
        hits.add('DROP_BOOK')
    # R1
    if R1_RE.match(x.label) or 'digitisation_stamp' in x.bflags:
        hits.add('R1'); ex('R1', x)
    # R2
    if x.bk in TWO_COL_BOOKS:
        if 'column_crossing_line' in x.dflags or 'column_merge_line' in x.dflags:
            hits.add('R2'); SUB[('R2', 'D crossing/merge')] += 1
        elif (x.dwr or 0) > 0.8 and ((x.ncol or 0) >= 2 or x.bk in R2_ALL_PAGES_BK):
            hits.add('R2'); SUB[('R2', 'width_ratio>0.8 only' + ('' if (x.ncol or 0) >= 2 else ' (1-col page, all-pages book)'))] += 1; ex('R2', x)
    # R3
    if is_scanned(x) and not x.caps:
        r3 = []
        if x.cflags.get('cpp_vs_book_out') == 'low': r3.append('cpp_vs_book_low')
        if 'cph_out_of_range' in x.cflags: r3.append('cph_out_of_range_' + x.cflags['cph_out_of_range'])
        if 'len_vs_book_high' in x.cflags: r3.append('len_vs_book_high')
        if r3:
            hits.add('R3'); R3_FLAG[x.i] = r3
            for s in r3: SUB[('R3', s)] += 1
            if len(r3) == 1: SUB[('R3', 'only ' + r3[0])] += 1
            ex('R3', x, ','.join(r3))
    # R4
    exn, avn, words = doubled_pairs(x.label)
    rep = 'repeated_word' in x.cflags
    if rep or exn >= 2 or avn:
        geom = 'len_vs_book_high' in x.cflags or 'cpp_vs_book_out' in x.cflags
        allow = (exn <= 1 and avn == 0 and words and words[0] in REDUP_OK and not geom)
        if allow:
            SUB[('R4', 'kept: allowlisted single reduplication')] += 1
        else:
            hits.add('R4')
            SUB[('R4', 'accent-variant pair' if avn else ('>=2 exact pairs' if exn >= 2 else 'C:repeated_word (single pair)'))] += 1
            if avn: ex('R4', x, 'accent-variant')
    # R5
    if r5_hit(x.label):
        hits.add('R5'); ex('R5', x)
    # R6b drop: ASCII quote before a capital vowel whose breathing cannot be resolved from the pool vocabulary
    if x.i in R6B_AMBIG:
        hits.add('R6'); SUB[('R6', 'drop: ambiguous breathing encoding (ASCII quote / spacing tonos before a capital in a polytonic line)')] += 1; ex('R6_drop', x)
    # R7 (after R6 relabel)
    if (x.cls == 'greek_poly' and not is_oa(x)) or (x.wave == 'vouli' and x.cls == 'greek_mono'):
        if not x.caps and r7_hit(lab2):
            hits.add('R7'); SUB[('R7', x.wave + '/' + x.cls)] += 1; ex('R7', x)
    # R9
    k9 = r9_hit(x)
    if k9:
        hits.add('R9'); SUB[('R9', k9)] += 1; ex('R9_' + k9, x)
    # R12
    if is_oa(x):
        k12 = r12_hit(x)
        if k12:
            hits.add('R12'); SUB[('R12', k12)] += 1; ex('R12_' + k12, x)
    # R13 named pages
    for pno, pages in R13_NAMED.items():
        if x.page in pages:
            hits.add('R13'); SUB[('R13', 'named page (' + pno + ')')] += 1
    # R14
    if R14_LEADER.search(x.label):
        hits.add('R14'); SUB[('R14', 'leader run >= 5')] += 1; ex('R14', x)
    elif x.wave == 'vouli' and R14_VOTE.search(x.label):
        hits.add('R14'); SUB[('R14', 'vouli trailing vote mark')] += 1; ex('R14_vote', x)
    # R15 drops
    for kind, desc, fn in R15.get(no, []):
        if kind == 'drop' and fn(x):
            hits.add('R15'); SUB[('R15', no)] += 1
    if not hits:
        del DROP[x.i]

# R13 share rule: pages where >= 30 % of admitted lines carry R3 flags
R13_SHARE_PAGES = {}
for pid, ls in PAGE_LINES.items():
    n3 = sum(1 for x in ls if x.i in R3_FLAG)
    if n3 and n3 / len(ls) >= 0.30:
        R13_SHARE_PAGES[pid] = (n3, len(ls))
for pid, (n3, n) in R13_SHARE_PAGES.items():
    for x in PAGE_LINES[pid]:
        DROP[x.i].add('R13')
        SUB[('R13', 'page R3 share >= 30%' + (' (page < 5 lines)' if n < 5 else ''))] += 1

# variant (measured only, not applied): R3 strict = cpp_vs_book low, or >= 2 of the three R3 signals; R13 share on it
R3_STRICT = {i for i, r3 in R3_FLAG.items() if 'cpp_vs_book_low' in r3 or len(r3) >= 2}
R13_STRICT_PAGES = set()
for pid, ls in PAGE_LINES.items():
    n3 = sum(1 for x in ls if x.i in R3_STRICT)
    if n3 and n3 / len(ls) >= 0.30:
        R13_STRICT_PAGES.add(pid)

# R10 duplicates ---------------------------------------------------------------------------------
YEAR = {bk: (ls[0].year if ls[0].year is not None else 9999) for bk, ls in BOOK_LINES.items()}
SPLITS = {bk: collections.Counter(x.split for x in ls) for bk, ls in BOOK_LINES.items()}


def keeper(bka, bkb):
    ta = 'train' in SPLITS.get(bka, {}); tb = 'train' in SPLITS.get(bkb, {})
    if ta != tb:
        return bka if ta else bkb
    return min(bka, bkb, key=lambda b: (YEAR.get(b, 9999), b))


R10_LOG = []
page_pairs = []
pair_labels = collections.defaultdict(set)
for l in open(os.path.join(AN, 'D_duplicates_pages/duplicates.jsonl')):
    r = json.loads(l)
    if r['kind'] == 'same_image_pages':
        page_pairs.append((r['source_key_a'], r['page_id_a'], r['source_key_b'], r['page_id_b']))
    elif r['kind'] == 'cross_book' and r['category'] == 'suspicious':
        k = tuple(sorted([r['source_key_a'], r['source_key_b']]))
        pair_labels[k].add(r['label'])
for ska, pa, skb, pb in page_pairs:
    na, nb = len(PAGE_LINES.get(pa, [])), len(PAGE_LINES.get(pb, []))
    if na == 0 or nb == 0:      # one copy has no admitted lines: the other is already the only copy
        R10_LOG.append({'kind': 'same_image_page', 'pages': [pa, pb], 'admitted': [na, nb], 'lines_dropped': 0,
                        'note': 'one copy has 0 admitted lines (holdout-label filter at admission); nothing to dedupe',
                        'splits': {ska: dict(SPLITS.get(ska, {})), skb: dict(SPLITS.get(skb, {}))}})
        continue
    keep = keeper(ska, skb)
    drop_page = pb if keep == ska else pa
    drop_bk = skb if keep == ska else ska
    n = 0
    for x in PAGE_LINES.get(drop_page, []):
        DROP[x.i].add('R10'); n += 1
    SUB[('R10', 'byte-identical page')] += n
    R10_LOG.append({'kind': 'same_image_page', 'keep': keep, 'keep_page': pa if keep == ska else pb,
                    'drop': drop_bk, 'drop_page': drop_page, 'lines_dropped': n,
                    'splits': {ska: dict(SPLITS.get(ska, {})), skb: dict(SPLITS.get(skb, {}))}})
BOOK_PAIRS = sorted([(k, len(v)) for k, v in pair_labels.items() if len(v) >= 27], key=lambda t: -t[1])
for (ska, skb), nshared in BOOK_PAIRS:
    keep = keeper(ska, skb); drop_bk = skb if keep == ska else ska
    kept_labels = {x.label for x in BOOK_LINES[keep]}
    by_page = collections.defaultdict(list)
    for x in BOOK_LINES[drop_bk]:
        by_page[x.page].append(x)
    n = 0
    for pid, ls in by_page.items():
        shared = [x for x in ls if x.label in kept_labels and len(x.label) >= 25]
        if not shared:
            continue
        whole = len(shared) / len(ls) >= 0.5
        for x in (ls if whole else shared):
            if 'R10' not in DROP[x.i]:
                DROP[x.i].add('R10'); n += 1
    for i in [i for i, v in DROP.items() if not v]:
        del DROP[i]
    SUB[('R10', 'book pair >= 27 shared sentences')] += n
    R10_LOG.append({'kind': 'book_pair', 'pair': [ska, skb], 'shared_sentences': nshared, 'keep': keep, 'drop': drop_bk,
                    'lines_dropped': n, 'splits': {ska: dict(SPLITS.get(ska, {})), skb: dict(SPLITS.get(skb, {}))},
                    'policy': 'drop the shared (>= 25-char) lines of the dropped copy; whole page when >= 50 % of its admitted lines are shared'})

# ----------------------------------------------------------------------------------------------
# 5. impact
# ----------------------------------------------------------------------------------------------
RULE_IDS = ['DROP_BOOK', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15']


def cnt():
    return {'total': 0, 'wave': collections.Counter(), 'class': collections.Counter(), 'split': collections.Counter()}


drop_imp = {r: cnt() for r in RULE_IDS}
uniq = collections.Counter()
overlap = collections.defaultdict(collections.Counter)
for i, rs in DROP.items():
    x = LINES[i]
    for r in rs:
        c = drop_imp[r]; c['total'] += 1; c['wave'][x.wave] += 1; c['class'][x.cls] += 1; c['split'][x.split] += 1
        for r2 in rs:
            overlap[r][r2] += 1
    if len(rs) == 1:
        uniq[next(iter(rs))] += 1
rel_imp = {r: cnt() for r in RULE_IDS}
rel_surv = collections.Counter()
for i, rs in RELABEL.items():
    x = LINES[i]
    for r in rs:
        c = rel_imp[r]; c['total'] += 1; c['wave'][x.wave] += 1; c['class'][x.cls] += 1; c['split'][x.split] += 1
        if i not in DROP:
            rel_surv[r] += 1
for x in R11_LINES:
    c = rel_imp['R11']; c['total'] += 1; c['wave'][x.wave] += 1; c['class'][x.cls] += 1; c['split'][x.split] += 1
    if x.i not in DROP:
        rel_surv['R11'] += 1

VARIANT = {}
_v = 0; _vs = collections.Counter(); _gain = collections.Counter()
for i, rs in DROP.items():
    rs2 = set(rs)
    x = LINES[i]
    if 'R3' in rs2 and i not in R3_STRICT:
        rs2.discard('R3')
    if 'R13' in rs2 and x.page not in R13_STRICT_PAGES and not any(x.page in v for v in R13_NAMED.values()):
        rs2.discard('R13')
    if rs2:
        _v += 1
    else:
        _gain[x.split] += 1
VARIANT = {'description': 'R3 restricted to lines with C:cpp_vs_book_out (low side) or >= 2 of {cpp low, cph_out_of_range, len_vs_book_high}; R13 share rule recomputed on that R3; all other rules unchanged',
           'R3_lines': sum(1 for i in R3_STRICT), 'R13_share_pages': len(R13_STRICT_PAGES),
           'R13_share_lines': sum(len(PAGE_LINES[p]) for p in R13_STRICT_PAGES),
           'lines_dropped_total': _v, 'lines_kept_back_vs_spec_by_split': dict(_gain)}
before = collections.Counter((x.cls, x.split) for x in LINES)
after = collections.Counter((x.cls, x.split) for x in LINES if x.i not in DROP)
n_drop = len(DROP)
log('dropped', n_drop, 'relabelled', len(RELABEL))

# per dossier: rule hits
DOSS_HITS = {}
for d in DOSS:
    ls = BOOK_LINES[d['bk']]
    c = collections.Counter(); tot = 0; cr = collections.Counter()
    for x in ls:
        if x.i in DROP:
            tot += 1
            for r in DROP[x.i]:
                c[r] += 1
        for r in RELABEL.get(x.i, []):
            cr[r] += 1
    DOSS_HITS[d['no']] = {'n': len(ls), 'dropped': tot, 'by_rule': dict(c), 'relabelled': dict(cr),
                          'surviving': len(ls) - tot}

# ----------------------------------------------------------------------------------------------
# 6. outputs
# ----------------------------------------------------------------------------------------------


def plain(c):
    return {'total': c['total'], 'wave': dict(c['wave'].most_common()), 'class': dict(c['class'].most_common()),
            'split': dict(c['split'].most_common())}


R1_COUNT_BY_BOOK = collections.Counter(LINES[i].bk for i, rs in DROP.items() if 'R1' in rs)
impact = {
    'pool_lines': N,
    'lines_dropped_total': n_drop,
    'lines_surviving': N - n_drop,
    'lines_relabelled_total': len(RELABEL),
    'lines_relabelled_surviving': sum(1 for i in RELABEL if i not in DROP),
    'drop_by_rule': {r: plain(drop_imp[r]) for r in RULE_IDS if drop_imp[r]['total']},
    'drop_unique_to_rule': dict(uniq),
    'drop_overlap_matrix': {r: dict(overlap[r]) for r in RULE_IDS if overlap[r]},
    'relabel_by_rule': {r: plain(rel_imp[r]) for r in RULE_IDS if rel_imp[r]['total']},
    'relabel_surviving_by_rule': dict(rel_surv),
    'sub_predicates': {f'{a} | {b}': v for (a, b), v in sorted(SUB.items())},
    'class_split_before': {f'{c}|{s}': v for (c, s), v in sorted(before.items())},
    'class_split_after': {f'{c}|{s}': v for (c, s), v in sorted(after.items())},
    'dev_test': {
        s: {'before': sum(v for (c, s2), v in before.items() if s2 == s),
            'after': sum(v for (c, s2), v in after.items() if s2 == s),
            'drop_by_rule': {r: drop_imp[r]['split'].get(s, 0) for r in RULE_IDS if drop_imp[r]['split'].get(s, 0)},
            'books_dropped_whole': sorted(bk for bk in DROP_BOOK if s in SPLITS[bk]),
            'books_losing_all_lines': sorted(bk for bk, ls in BOOK_LINES.items() if ls[0].split == s and all(x.i in DROP for x in ls))}
        for s in ('dev', 'test')},
    'r10_dedup': R10_LOG,
    'variant_R3_strict': VARIANT,
    'r13_share_pages': {pid: {'r3_lines': a, 'admitted': b} for pid, (a, b) in sorted(R13_SHARE_PAGES.items())},
    'r2_books': {'two_column_books_total': len(TWO_COL_BOOKS), 'by_page_majority': len(TWO_COL_MAJ),
                 'adjudicated_added': [BK_OF[n] for n in R2_ADJ_TWO_COL if BK_OF[n] not in TWO_COL_MAJ],
                 'excluded': [BK_OF[n] for n in R2_EXCLUDE]},
    'r1_by_book': dict(R1_COUNT_BY_BOOK.most_common()),
    'per_dossier': DOSS_HITS,
    'examples': EXAMPLES,
}
with open(os.path.join(AN, 'impact.json'), 'w') as f:
    json.dump(impact, f, ensure_ascii=False, indent=1)

# clean preview ------------------------------------------------------------------------------
os.makedirs(OUTP, exist_ok=True)
log('writing clean preview ...')
with open(POOL) as fp, gzip.open(os.path.join(OUTP, 'admitted_all_clean_preview.jsonl.gz'), 'wt') as fo, \
        gzip.open(os.path.join(OUTP, 'dropped_preview.jsonl.gz'), 'wt') as fdp:
    for i, line in enumerate(fp):
        if i in DROP:
            r = json.loads(line)
            strict = set(DROP[i])
            if 'R3' in strict and i not in R3_STRICT:
                strict.discard('R3')
            if 'R13' in strict and r['page_id'] not in R13_STRICT_PAGES and not any(r['page_id'] in v for v in R13_NAMED.values()):
                strict.discard('R13')
            fdp.write(json.dumps({'id': r['id'], 'rules': sorted(DROP[i], key=RULE_IDS.index),
                                  'rules_strict': sorted(strict, key=RULE_IDS.index), 'label': r['label'],
                                  'label_v2': LABEL2.get(i, r['label']), 'relabel_rules': list(RELABEL.get(i, []))},
                                 ensure_ascii=False) + '\n')
            continue
        r = json.loads(line)
        ra = list(RELABEL.get(i, []))
        if r['source'].startswith('openarchives'):
            ra.append('R11')
        r['rules_applied'] = ra
        r['label_v2'] = LABEL2.get(i, r['label'])
        fo.write(json.dumps(r, ensure_ascii=False) + '\n')

# stash for the markdown/json writer
STATE = dict(DOSS=DOSS, DOSS_HITS=DOSS_HITS, impact=impact, before=before, after=after, uniq=uniq,
             drop_imp=drop_imp, rel_imp=rel_imp, rel_surv=rel_surv, SUB=SUB, R15=R15, BOOK_PAIRS=BOOK_PAIRS,
             TWO_COL_BOOKS=TWO_COL_BOOKS, R13_SHARE_PAGES=R13_SHARE_PAGES, SPLITS=SPLITS, BOOK_LINES=BOOK_LINES)
import compile_report  # noqa: E402  (writes rules.json and DECISIONS.md)
compile_report.prepare(STATE, globals())
compile_report.write(STATE, globals())
log('done')
