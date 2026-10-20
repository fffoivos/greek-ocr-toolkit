"""Writer for rules.json and DECISIONS.md (called by compile_decisions.py; not run on its own)."""
import collections
import json
import os
import re

SPLIT_ORDER = ['train', 'dev', 'test']
CLASS_ORDER = ['greek_poly', 'greek_mono', 'greek_latin_cs', 'latin', 'cyrillic']
WAVE_ORDER = ['round1', 'round2', 'mixed', 'vouli', 'parliament', 'openarchives', 'cyrillic', 'wikisource']
DEC_ORDER = ['DROP_BOOK', 'DROP_PATTERN', 'RELABEL', 'KEEP']


def esc(s):
    return str(s).replace('|', '\\|').replace('\n', ' ')


def short(s, n):
    s = ' '.join(str(s).split())
    return s if len(s) <= n else s[:n - 1] + '…'


def first_sentence(s, n=170):
    s = ' '.join(str(s).split())
    m = re.match(r'(.+?[.;])(\s|$)', s)
    return short(m.group(1) if m else s, n)


def spl(c):
    return ' / '.join(format(c['split'].get(s, 0), ',') for s in SPLIT_ORDER)


def fmt_mix(cm):
    return ', '.join(f'{k} {v}' for k, v in sorted(cm.items(), key=lambda t: -t[1]))


def fmt_splits(sp):
    return ', '.join(f'{k} {sp[k]}' for k in SPLIT_ORDER if k in sp)


RULE_SPECS = [
    dict(id='DROP_BOOK', action='drop book', level='BOOK',
         description='Books adjudicated DROP_BOOK: every admitted line is removed.',
         scope={'books': 'dossiers 009, 028, 043, 052, 060, 063, 064, 074, 105, 122'},
         predicate='(source|book_key) in the DROP_BOOK set of dossiers/*/decision.json',
         provenance={'dossiers': ['009', '028', '043', '052', '060', '063', '064', '074', '105', '122']}),
    dict(id='R1', action='drop', level='LINE', description='Library / digitisation stamp labels and the Thessaly university logo admitted as text.',
         scope={'waves': 'all', 'classes': 'all'},
         predicate=r"re.match(r'^[-–\s]*(ΠΑΝΕΠΙΣΤΗΜΙΟ?Ν?(\s+ΚΡ\w*)?|ΒΙΒΛΙΟΘΗΚΗ|Digiti[sz]ed\s+by\s+\w+|Πανεπιστήμιο\s+Θεσσαλίας)\W*$', label) OR B:digitisation_stamp",
         provenance={'findings': ['ANOMALIES §3.1', 'B §0.3', 'C finding 4'], 'dossiers': ['040']},
         notes='Whole-label match only; a bare ^ΠΑΝΕΠΙΣΤΗΜΙ prefix would hit genuine OpenArchives title-page lines (ANOMALIES §3.1).'),
    dict(id='R2', action='drop', level='LINE', description='Two columns read as one line (column merges / gutter crossings) in two-column books.',
         scope={'books': 'two-column books = page majority (pages with admitted lines, D page_profiles n_columns >= 2) OR adjudicated two-column '
                         '(dossiers 005 017 018 021 030 032 033 045 047 048 053 076 078 085 086 098 099 101 103 104 111 119), MINUS books adjudicated '
                         'single-column / false column flags (020 049 055 097 108 134 012 088 100 125) and 117 (crossing flag hits real prose; 117 uses its own merge-only R15)'},
         predicate='book in TWO_COL_BOOKS AND (D:column_crossing_line OR D:column_merge_line OR (D width_ratio > 0.8 AND (page_n_columns >= 2 OR book in {017,018,021,030,047,085})))',
         provenance={'findings': ['ANOMALIES §3.2', 'D §0.1', 'C finding 2'],
                     'dossiers': ['005', '009', '010', '017', '018', '021', '025', '030', '032', '033', '047', '048', '053', '063', '074', '076', '078',
                                  '085', '086', '098', '099', '101', '103', '104', '105', '111', '119', '122'],
                     'exclusions_from': ['012', '020', '049', '055', '088', '097', '100', '108', '117', '125', '134']},
         notes='Deviation from the brief: width_ratio > 0.8 is applied on 1-column-detected pages only for the six vouli books whose adjudicators said every page is two-column. '
               'On other page-majority books the page majority comes from landscape two-page spreads (round1/round2), and a full-width line on a single-page scan is normal prose '
               '(seen in KEEP books 011, 057, 114: 73 correct lines would have been dropped).'),
    dict(id='R3', action='drop', level='LINE', description='Crop/label mismatch proxies: label far too short for the crop, density out of class range, or label far longer than the book median.',
         scope={'waves': 'scanned: round1, round2, vouli, parliament, cyrillic, and the non-OpenArchives part of mixed (anemi_mixed, archive_*); NOT openarchives*, NOT wikisource',
                'classes': 'all, except all-caps labels (B is_all_caps)'},
         predicate="scanned(wave, source) AND NOT B.is_all_caps AND (C:cpp_vs_book_out on the low side ('<' in reason) OR C:cph_out_of_range (either side) OR C:len_vs_book_high)",
         provenance={'findings': ['ANOMALIES §3.2 (len_vs_book)', 'C finding 2'],
                     'dossiers': ['001', '002', '013', '014', '019', '024', '031', '032', '033', '034', '036', '045', '046', '048', '051', '053', '056', '059',
                                  '072', '084', '096', '098', '099', '101', '103', '104', '106', '107', '109', '111', '119', '121']},
         notes='As specified in the brief. 61 % of R3 lines are triggered by C:cph_out_of_range alone and 15 % by len_vs_book_high alone; '
               'see impact.json variant_R3_strict and the contradictions section (KEEP books 003, 010, 088 lose correct lines).'),
    dict(id='R4', action='drop', level='LINE', description='Doubled readings: Google read words twice, or interleaved a polytonic and a monotonic reading.',
         scope={'waves': 'all', 'classes': 'all'},
         predicate="C:repeated_word OR >= 2 adjacent identical tokens (punctuation kept, >= 2 letters) OR an adjacent pair equal after removing diacritics and casefolding "
                   "but differing in marks (grave treated = acute; case-only pairs excluded); EXCEPT a single exact pair whose word is on the reduplication allowlist "
                   "(κάτω, λίγο, σιγά, ένα, δυο, καλά, γύρω, πέρα, ίσα, αργά, τώρα, ψιλά, κοντά, φρού, άκρη, ορθά, μόνο, πολύ, τσιγκάνα, όλο, όλα, μια, ευθύς) and no C geometry flag",
         provenance={'findings': ['ANOMALIES §3.9', 'C finding 3'],
                     'dossiers': ['001', '010', '024', '032', '033', '034', '045', '046', '048', '049', '055', '076', '098', '099'],
                     'against': ['002', '114']}),
    dict(id='R5', action='drop', level='LINE', description="Next print line's word appended after a hyphen break ('Κυ- βέρνησης').",
         scope={'waves': 'all', 'classes': 'all'},
         predicate=r"re.search(r'[^\W\d_]- (?!(and|und|or|oder|et|ou|e|y|καὶ|και|ἢ|ή|ἤ|καί)\b)[^\W\d_]', label) with the letter after '- ' lower-case, "
                   r"AND no opening parenthetical dash (^|\s)[-—–]\s?letter earlier in the label",
         provenance={'dossiers': ['084', '102', '117']},
         notes="Brief: label matches `\\S- \\S`. Narrowed to letter-hyphen-space-lowercase letter; suspended hyphens ('pre- and') and parenthetical dash pairs "
               "('—αὐτὸ … ἐργαζόμενου- ἀλλὰ', parliament) are excluded."),
    dict(id='R6', action='relabel (+ drop when ambiguous)', level='LINE', description='Breathing/accent on a capital written as a separate spacing mark: normalise to the precomposed capital.',
         scope={'waves': 'all', 'classes': 'all (spacing marks); ASCII-quote and spacing-tonos handling only in greek_poly lines and vouli greek_mono lines'},
         predicate="RELABEL: (^|[\\s(«\\[“\"‘'])(U+1FBF|U+1FBD|U+1FFE|U+1FCE|U+1FCD|U+1FCF|U+1FDE|U+1FDD|U+1FDF|U+0384)([ΑΕΗΙΟΥΩΡ]) -> capital + combining "
                   "(U+0313 / U+0314 / U+0313+0301 / U+0313+0300 / U+0313+0342 / U+0314+0301 / U+0314+0300 / U+0314+0342 / U+0301), NFC, only when a single precomposed "
                   "capital results. ASCII '\"' + bare capital vowel (polytonic lines): candidate words of Ἄ/Ἅ/Ἂ/Ἃ type looked up in the pool vocabulary; exactly one "
                   "attested -> RELABEL to it; none or several -> DROP. Spacing tonos U+0384 + capital in a polytonic line -> DROP (it renders a breathing there, "
                   "΄Αγιον = Ἅγιον, ΄Ελασσῶνα = Ἐλασσῶνα); in monotonic lines -> Ά/Έ/... relabel.",
         provenance={'findings': ['ANOMALIES §3.3', 'B finding 1'], 'dossiers': ['109', '016', '102', '104', '114', '042', '050']},
         notes="Brief: '\"' -> Ἄ-type 'per the 109 decision only where unambiguous, else drop'. 'Unambiguous' is made data-driven (exactly one breathing variant attested "
               "in the pool) and applied pool-wide, including 109."),
    dict(id='R7', action='drop', level='LINE', description='Bare initial capital vowel without breathing in polytonic text (Google drops the breathing on capitals).',
         scope={'waves': 'all except OpenArchives sources', 'classes': 'greek_poly; plus greek_mono lines of vouli (polytonic print, see 003/008)'},
         predicate="evaluated on the label after R6; NOT all-caps; re.search(r'(?:^|(?<=[\\s(\\[«•·|]))([ΑΕΗΙΟΥΩ])(?![\\u1F00-\\u1FFF])([\\u03B1-\\u03C9\\u03AC-\\u03CE]|\\s|$)') "
                   "where a single-letter match counts only for the articles Ο/Η and only when the next word is not ALL CAPS, and a line-final bare capital (vote mark) is ignored",
         provenance={'dossiers': ['008', '012', '015', '113'], 'supporting_notes': ['003', '019', '027', '049', '087', '102', '144']},
         notes="113's own regex ((?=[α-ωάέήίόύώϊϋΐΰἀ-ᾯὰ-ώᾳῃῳ])) also matches correctly breathed diphthongs (Αἰ, Εὐ, Οἱ) — the 008/012/015 form is used."),
    dict(id='R8', action='relabel', level='LINE', description='στ ligature read as ς (word-internal) or as plain σ.',
         scope={'waves': 'all', 'classes': 'greek_poly, greek_mono, greek_latin_cs (ς); greek_poly, greek_mono (plain σ)'},
         predicate="(a) word-internal ς followed by a Greek letter -> στ when the resulting word (NFC lower-case) is attested in the pool; words starting προς/πρὸς/πρός/εις/εἰς/ὡς/ως/ὥς/ὥςτε "
                   "or containing δηποτ excluded. (b) plain σ + consonant (not τ) in a word of >= 5 letters attested only once in the pool, whose σ->στ form is attested >= 3 times -> στ.",
         provenance={'findings': ['ANOMALIES §3.4', 'B §0.2'], 'dossiers': ['018', '072', '087']},
         notes="ANOMALIES §3.4(b) also proposed dropping remaining word-final σ / internal ς: NOT applied — adjudicators 002, 035, 037, 038, 046, 110, 126, 127, 137 found those "
               "flags are printed elisions (μέσ᾽, ζῶσ᾽)."),
    dict(id='R9', action='drop', level='LINE', description='Whole wrong-script words (homoglyph reads): Cyrillic letters in Greek/Latin text, look-alike foreign tokens.',
         scope={'waves': 'all', 'classes': 'all'},
         predicate="(any Cyrillic letter U+0400-052F in a line whose class, wave and book majority are not cyrillic) OR (A residue kinds include unexpected_word / "
                   "unexpected_standalone_lookalike / isolated_standalone_lookalike AND some whitespace token has all its letters in a script other than the line's "
                   "majority script, is not a unit (km, mm, kg …), contains no digit and is not adjacent to a number token; for isolated_* kinds only single letters count)",
         provenance={'findings': ['ANOMALIES §3.5', 'A finding 1'], 'dossiers': ['014', '022', '031', '034', '050', '083', '088', '096', '123', '125', '128']}),
    dict(id='R10', action='drop', level='LINE', description='Duplicate scans: byte-identical page images, and vouli book pairs sharing >= 27 sentences.',
         scope={'books': 'D duplicates.jsonl same_image_pages (7 pairs) + cross_book suspicious pairs with >= 27 shared >= 25-char labels (5 pairs, 9 books)'},
         predicate="keep one copy: the train copy if exactly one is train, else the copy with the earliest (year, book_key); identical page: drop every admitted line of the "
                   "other page (skipped when one copy has 0 admitted lines); book pair: drop the other book's shared (>= 25-char) lines, and its whole page when >= 50 % of "
                   "the page's admitted lines are shared",
         provenance={'findings': ['ANOMALIES §3.7', 'D §0.2'], 'dossiers': ['003', '008', '015', '022', '026', '072', '119', '144']},
         notes="Brief says '9 book pairs sharing >= 27 sentences'; the data has 5 pairs (they involve 9 books). ANOMALIES §3.7 would keep the dev/test copy; the brief "
               "keeps the train copy — no realised conflict: the 3 cross-split identical pages have 0 admitted lines on the train side."),
    dict(id='R11', action='metadata', level='BOOK', description='OpenArchives metadata unreliable: year -> null, title_unreliable = true.',
         scope={'sources': 'all openarchives* sources (wave openarchives and the OpenArchives part of mixed)'},
         predicate="source.startswith('openarchives') -> year := null, title_unreliable := true (labels unchanged; recorded as 'R11' in rules_applied)",
         provenance={'findings': ['ANOMALIES §3.8', 'A §0.3'], 'dossiers': 'see DECISIONS.md (dossiers whose notes say the catalogue title/year does not match)'}),
    dict(id='R12', action='drop', level='LINE', description='Inline maths / code in born-digital OpenArchives theses.',
         scope={'sources': 'openarchives* only', 'classes': 'math symbols and code: all; single Latin letters: Greek-class lines'},
         predicate="label contains any of ∈∑≤≥≠∃∀±×√∞∂∫∉⊂⊆⊇∪∩∅ OR code pattern (:=|==|!=|\\w_\\w|\\.\\w+\\(|\\(\\)|[{}]|</?[A-Za-z]+>|\\bxl[A-Z]\\w+) OR (class in "
                   "greek_mono/greek_poly/greek_latin_cs AND a standalone single Latin letter token (?<![\\w.'’\\-/\\\\@])[A-Za-z](?![\\w'’.\\-/\\\\@]) after removing a "
                   "line-start list marker ^[A-Za-z]\\); in greek_latin_cs lines a/A/I are ignored)",
         provenance={'dossiers': ['004', '028', '064', '069', '073', '075', '079', '129'], 'against': ['130', '131', '132']}),
    dict(id='R13', action='drop page', level='PAGE', description='Whole pages adjudicators named as skewed / mis-segmented, plus pages where >= 30 % of admitted lines carry R3.',
         scope={'pages': 'named: c3468c02b6d929362f6e3fe7-p000191 (019), 87d33c70-p000007 (045), 8b231047fdbd96ec30e1eded-p000009/13/22 (051), '
                          '1be3f9227e2b68a2b9974abe-p000023 (056); share rule: scanned waves (R3 scope)'},
         predicate="page_id in NAMED OR (count of the page's admitted lines with R3) / (admitted lines on the page) >= 0.30 (no minimum page size)",
         provenance={'dossiers': ['019', '045', '051', '056']},
         notes='As specified. The share rule inherits R3\'s false positives; with R3-strict the share rule would hit 25 pages / 1,891 lines instead.'),
    dict(id='R14', action='drop', level='LINE', description='Roll-call / dot-leader lines: arbitrary leader dot counts, vote marks as Latin N/O/0.',
         scope={'waves': 'leader runs: all; trailing vote mark: vouli only'},
         predicate=r"re.search(r'(?:[.·•]\s?){5,}|…{2,}', label) OR (wave == vouli AND re.search(r'\s[ONΟΝ0]$', label))",
         provenance={'dossiers': ['034'], 'against': ['089', '029', '042']}),
    dict(id='R15', action='drop / relabel (per book)', level='BOOK-SPECIFIC LINE', description='Book-specific patterns from DROP_PATTERN / RELABEL decisions that do not generalise.',
         scope={'books': 'one entry per dossier, see book_rules'}, predicate='see book_rules',
         provenance={'dossiers': 'see book_rules'}),
]


def write(S, G):
    AN = G['AN']
    imp = S['impact']; DOSS = S['DOSS']; HITS = S['DOSS_HITS']; SUB = S['SUB']; R15 = S['R15']
    drop_imp = S['drop_imp']; rel_imp = S['rel_imp']; rel_surv = S['rel_surv']; uniq = S['uniq']
    before = S['before']; after = S['after']; SPLITS = S['SPLITS']; BOOK_LINES = S['BOOK_LINES']
    BK_OF = G['BK_OF']

    # ---------------- rules.json ----------------
    book_rules = []
    for no in sorted(R15):
        d = G['BYNO'][no]
        for kind, desc, fn in R15[no]:
            key = ('R15', no + (' relabel' if kind == 'relabel' else ''))
            book_rules.append({'dossier': no, 'book': d['bk'], 'decision': d['decision'], 'kind': kind, 'predicate': desc,
                               'adjudicator_rule': d['rule'], 'lines': SUB.get(key, 0)})
    rules = []
    for spec in RULE_SPECS:
        r = dict(spec)
        rid = r['id']
        r['impact'] = {'lines_dropped': drop_imp[rid]['total'], 'lines_dropped_only_by_this_rule': uniq.get(rid, 0),
                       'lines_relabelled': rel_imp[rid]['total'], 'lines_relabelled_surviving': rel_surv.get(rid, 0),
                       'sub_predicates': {k.split(' | ', 1)[1]: v for k, v in imp['sub_predicates'].items() if k.split(' | ')[0] == rid and rid != 'R15'}}
        if rid == 'R15':
            r['book_rules'] = book_rules
        if rid == 'R11':
            r['impact']['books'] = len({x.bk for x in G['R11_LINES']})
            r['impact']['dossiers_noting_wrong_title_or_year'] = TITLE_DOSS
        rules.append(r)
    with open(os.path.join(AN, 'rules.json'), 'w') as f:
        json.dump({'generated_by': 'docs/harvest/analysis/compile_decisions.py', 'pool': 'docs/harvest/collection/admitted_all.jsonl',
                   'pool_lines': imp['pool_lines'], 'applied': False,
                   'order': 'relabels first (R6 spacing marks + ASCII quote, R8 στ, R15 relabels), then drop rules evaluated on the original label '
                            '(R7 on the R6-normalised label); a line is dropped if any drop rule fires',
                   'rules': rules}, f, ensure_ascii=False, indent=1)

    # ---------------- DECISIONS.md ----------------
    L = []
    P = L.append
    P('# Adjudication decisions and pool-wide line rules (compiled 15 Oct 2026)')
    P('')
    P('Inputs: 120 `dossiers/*/decision.json` (+ `dossier.json`), [ANOMALIES.md](ANOMALIES.md), the four aspect line-flag files, D `duplicates.jsonl` / `page_profiles.jsonl`, '
      'and the pool `docs/harvest/collection/admitted_all.jsonl` (293,439 lines). Generated by `compile_decisions.py` (+ `compile_report.py`). '
      '**Nothing is applied to the pool**: [rules.json](rules.json) holds the rules, [impact.json](impact.json) the measurements, and `clean_preview/` a preview of '
      'the pool after all rules (`admitted_all_clean_preview.jsonl.gz`: surviving lines + `rules_applied` + `label_v2`; `dropped_preview.jsonl.gz`: id, rule ids, old label).')
    P('')
    # 1 counts
    P('## 1. Decision counts')
    P('')
    dc = collections.Counter(d['decision'] for d in DOSS)
    P('| decision | dossiers | lines in those books | of which dev | of which test |')
    P('|---|---:|---:|---:|---:|')
    for k in DEC_ORDER:
        ds = [d for d in DOSS if d['decision'] == k]
        P(f"| {k} | {len(ds)} | {sum(d['n_lines'] for d in ds):,} | {sum(d['splits'].get('dev', 0) for d in ds):,} | {sum(d['splits'].get('test', 0) for d in ds):,} |")
    P(f"| **all** | {len(DOSS)} | {sum(d['n_lines'] for d in DOSS):,} | {sum(d['splits'].get('dev', 0) for d in DOSS):,} | {sum(d['splits'].get('test', 0) for d in DOSS):,} |")
    P('')
    P('Per wave:')
    P('')
    P('| wave | ' + ' | '.join(DEC_ORDER) + ' | all |')
    P('|---|' + '---:|' * (len(DEC_ORDER) + 1))
    for w in WAVE_ORDER:
        c = collections.Counter(d['decision'] for d in DOSS if d['wave'] == w)
        if c:
            P(f'| {w} | ' + ' | '.join(str(c.get(k, 0)) for k in DEC_ORDER) + f' | {sum(c.values())} |')
    P('')
    P(f"Confidence: mean {sum(d['confidence'] for d in DOSS) / len(DOSS):.2f}; below 0.7: "
      + ', '.join(f"{d['no']} ({d['decision']} {d['confidence']})" for d in sorted(DOSS, key=lambda d: d['no']) if d['confidence'] < 0.7) + '.')
    P('')
    # 2 table
    P('## 2. All 120 dossiers (sorted by decision, then rank)')
    P('')
    P('"after rules" = lines of the book that the full rule set (DROP_BOOK + R1–R15) removes, from impact.json `per_dossier`.')
    P('')
    P('| rank | dossier | source | key | wave | split(s) | lines | class mix | decision | conf | rule / pattern | note | after rules: dropped (%) |')
    P('|---:|---|---|---|---|---|---:|---|---|---:|---|---|---:|')
    for d in sorted(DOSS, key=lambda d: (DEC_ORDER.index(d['decision']), d['rank'])):
        h = HITS[d['no']]
        P(f"| {d['rank']} | [{d['no']}](dossiers/{d['folder']}/question.md) | {d['source']} | `{d['key']}` | {d['wave']} | {fmt_splits(d['splits'])} | {d['n_lines']} | "
          f"{esc(fmt_mix(d['class_mix']))} | {d['decision']} | {d['confidence']} | {esc(short(d['rule'], 150)) or '—'} | {esc(first_sentence(d['notes']))} | "
          f"{h['dropped']} ({h['dropped'] / h['n'] * 100:.0f} %) |")
    P('')
    # 3 dev/test books
    P('## 3. Books whose decision affects dev/test lines')
    P('')
    P('Non-KEEP decisions on books with dev or test lines. "before → after" counts the book\'s dev/test lines before and after the full rule set (the book is in one split only unless noted). '
      'Hold-out sets stay document-disjoint by construction (no rule moves a line between splits); a DROP_BOOK on a test book only shrinks test.')
    P('')
    P('| dossier | book | decision | split | lines before → after | rules that drop most |')
    P('|---|---|---|---|---|---|')
    for d in sorted(DOSS, key=lambda d: (DEC_ORDER.index(d['decision']), d['rank'])):
        if d['decision'] == 'KEEP' or not (set(d['splits']) & {'dev', 'test'}):
            continue
        ls = BOOK_LINES[d['bk']]
        parts = []
        for s in ('dev', 'test'):
            b = sum(1 for x in ls if x.split == s)
            if b:
                a = sum(1 for x in ls if x.split == s and x.i not in G['DROP'])
                parts.append((s, b, a))
        top = ', '.join(f'{r} {n}' for r, n in sorted(HITS[d['no']]['by_rule'].items(), key=lambda t: -t[1])[:4])
        rel = HITS[d['no']]['relabelled']
        if rel:
            top += '; relabel ' + ', '.join(f'{r} {n}' for r, n in rel.items())
        for s, b, a in parts:
            P(f"| {d['no']} | `{d['bk']}` | {d['decision']} | {s} | {b} → {a} | {top} |")
    P('')
    multi = sorted((bk, dict(c)) for bk, c in SPLITS.items() if len(c) > 1)
    if multi:
        P('Pre-existing split overlap (not caused by any rule): ' + '; '.join(f'`{bk}` {c}' for bk, c in multi)
          + ' — the same book has lines in more than one split, so train and the hold-outs are not document-disjoint for it.')
        P('')
    # 4 rules table
    P('## 4. Rules and their impact')
    P('')
    P('Full predicates in [rules.json](rules.json). "dropped" counts every line the rule fires on (lines can carry several rules); "only this rule" = lines no other rule drops; '
      '"relabelled" counts lines whose label_v2 the rule changed (in brackets: of those, lines that survive all drops).')
    P('')
    P('| id | action | scope | dropped | only this rule | relabelled (surviving) | train / dev / test dropped |')
    P('|---|---|---|---:|---:|---:|---|')
    for spec in RULE_SPECS:
        rid = spec['id']
        sc = '; '.join(f'{k}: {v}' for k, v in spec['scope'].items())
        di = drop_imp[rid]; ri = rel_imp[rid]
        rel = f"{ri['total']:,} ({rel_surv.get(rid, 0):,})" if ri['total'] else '—'
        P(f"| {rid} | {spec['action']} | {esc(short(sc, 230))} | {di['total']:,} | {uniq.get(rid, 0):,} | {rel} | "
          f"{spl(di)} |")
    P('')
    P(f"**Total: {imp['lines_dropped_total']:,} of {imp['pool_lines']:,} lines dropped ({imp['lines_dropped_total'] / imp['pool_lines'] * 100:.1f} %), "
      f"{imp['lines_surviving']:,} survive; {imp['lines_relabelled_surviving']:,} surviving lines get a new label_v2 (R6/R8/R15); "
      f"{rel_surv.get('R11', 0):,} surviving OpenArchives lines carry the R11 metadata flag.**")
    P('')
    v = imp['variant_R3_strict']
    P(f"Variant (measured, not applied): {v['description']} → R3 {v['R3_lines']:,} lines, share rule {v['R13_share_pages']} pages / {v['R13_share_lines']:,} lines, "
      f"total dropped {v['lines_dropped_total']:,} (keeps back {sum(v['lines_kept_back_vs_spec_by_split'].values()):,}: "
      + ', '.join(f"{k} {n:,}" for k, n in sorted(v['lines_kept_back_vs_spec_by_split'].items())) + ').')
    P('')
    P('Sub-predicates:')
    P('')
    P('| rule | sub-predicate | lines |')
    P('|---|---|---:|')
    for k, n in imp['sub_predicates'].items():
        r, sp = k.split(' | ', 1)
        if r == 'R15':
            continue
        P(f'| {r} | {esc(sp)} | {n:,} |')
    P('')
    # per wave / class
    P('### 4.1 Lines dropped per rule × wave')
    P('')
    P('| rule | ' + ' | '.join(WAVE_ORDER) + ' |')
    P('|---|' + '---:|' * len(WAVE_ORDER))
    for spec in RULE_SPECS:
        rid = spec['id']
        if drop_imp[rid]['total']:
            P(f'| {rid} | ' + ' | '.join(f"{drop_imp[rid]['wave'].get(w, 0):,}" for w in WAVE_ORDER) + ' |')
    tw = collections.Counter(G['LINES'][i].wave for i in G['DROP'])
    aw = collections.Counter(x.wave for x in G['LINES'])
    P('| **any rule** | ' + ' | '.join(f"{tw.get(w, 0):,} ({tw.get(w, 0) / aw[w] * 100:.1f} %)" for w in WAVE_ORDER) + ' |')
    P('')
    P('### 4.2 Lines dropped per rule × script class')
    P('')
    P('| rule | ' + ' | '.join(CLASS_ORDER) + ' |')
    P('|---|' + '---:|' * len(CLASS_ORDER))
    for spec in RULE_SPECS:
        rid = spec['id']
        if drop_imp[rid]['total']:
            P(f'| {rid} | ' + ' | '.join(f"{drop_imp[rid]['class'].get(c, 0):,}" for c in CLASS_ORDER) + ' |')
    P('')
    P('### 4.3 Relabels per rule × wave')
    P('')
    P('| rule | ' + ' | '.join(WAVE_ORDER) + ' | train / dev / test |')
    P('|---|' + '---:|' * len(WAVE_ORDER) + '---|')
    for rid in ('R6', 'R8', 'R11', 'R15'):
        ri = rel_imp[rid]
        P(f'| {rid} | ' + ' | '.join(f"{ri['wave'].get(w, 0):,}" for w in WAVE_ORDER) + f" | {spl(ri)} |")
    P('')
    # overlap
    P('### 4.4 Overlap between drop rules')
    P('')
    P('Cell = lines dropped by both the row and the column rule (diagonal = rule total).')
    P('')
    ids = [s['id'] for s in RULE_SPECS if drop_imp[s['id']]['total']]
    P('| | ' + ' | '.join(ids) + ' |')
    P('|---|' + '---:|' * len(ids))
    ov = imp['drop_overlap_matrix']
    for a in ids:
        P(f'| **{a}** | ' + ' | '.join(f"{ov.get(a, {}).get(b, 0):,}" if ov.get(a, {}).get(b, 0) else '·' for b in ids) + ' |')
    P('')
    # dev/test
    P('## 5. Dev/test impact')
    P('')
    P('| split | before | after | dropped | DROP_BOOK books | dropped by rule |')
    P('|---|---:|---:|---:|---|---|')
    for s in ('dev', 'test'):
        dt = imp['dev_test'][s]
        P(f"| {s} | {dt['before']:,} | {dt['after']:,} | {dt['before'] - dt['after']:,} ({(dt['before'] - dt['after']) / dt['before'] * 100:.1f} %) | "
          f"{', '.join('`' + b + '`' for b in dt['books_dropped_whole']) or '—'} | {', '.join(f'{r} {n:,}' for r, n in dt['drop_by_rule'].items())} |")
    P('')
    hb = collections.Counter(); hs = {}
    for i in G['DROP']:
        x = G['LINES'][i]
        if x.split in ('dev', 'test'):
            hb[x.bk] += 1; hs[x.bk] = x.split
    P('Hold-out books losing the most lines (all rules):')
    P('')
    P('| book | split | lines | dropped | dossier / decision |')
    P('|---|---|---:|---:|---|')
    for bk, n in hb.most_common(20):
        nb = len(BOOK_LINES[bk]); no = G['NO_OF_BK'].get(bk)
        P(f"| `{bk}` | {hs[bk]} | {nb} | {n} ({n / nb * 100:.0f} %) | {no + ' ' + G['BYNO'][no]['decision'] if no else '—'} |")
    P('')
    P(f"Library stamps (R1): {drop_imp['R1']['split'].get('test', 0)} test + {drop_imp['R1']['split'].get('dev', 0)} dev lines removed. "
      f"R10 removes no dev/test line (the 3 cross-split identical pages have 0 admitted train lines).")
    P('')
    # class x split
    P('## 6. Script class × split, before → after')
    P('')
    P('| class | ' + ' | '.join(f'{s} before | {s} after' for s in SPLIT_ORDER) + ' | all before | all after |')
    P('|---|' + '---:|' * (2 * len(SPLIT_ORDER) + 2))
    for c in CLASS_ORDER + ['**all**']:
        if c == '**all**':
            bs = {s: sum(v for (cc, ss), v in before.items() if ss == s) for s in SPLIT_ORDER}
            as_ = {s: sum(v for (cc, ss), v in after.items() if ss == s) for s in SPLIT_ORDER}
        else:
            bs = {s: before.get((c, s), 0) for s in SPLIT_ORDER}
            as_ = {s: after.get((c, s), 0) for s in SPLIT_ORDER}
        P(f'| {c} | ' + ' | '.join(f'{bs[s]:,} | {as_[s]:,}' for s in SPLIT_ORDER) + f' | {sum(bs.values()):,} | {sum(as_.values()):,} |')
    P('')
    # R15 per book
    P('## 7. R15 — book-specific rules')
    P('')
    P('| dossier | book | decision | kind | predicate as implemented | lines |')
    P('|---|---|---|---|---|---:|')
    for br in book_rules:
        P(f"| {br['dossier']} | `{br['book']}` | {br['decision']} | {br['kind']} | {esc(short(br['predicate'], 200))} | {br['lines']:,} |")
    P('')
    P('Book-specific requests already covered by a pool rule (no separate R15 entry): 008/012/015/113 → R7; 019, 045, 051, 056 page drops → R13; 021/030/047/085 width > 0.8 on all pages → R2; '
      '040 logo → R1; 078 crossing lines and 119 duplicate copy → R2/R10; 121 cpp low → R3; 109 ASCII quote → R6.')
    P('')
    # R10 log
    P('## 8. R10 — duplicate scans')
    P('')
    P('| kind | keep | drop | lines dropped | note |')
    P('|---|---|---|---:|---|')
    for r in imp['r10_dedup']:
        if r['kind'] == 'same_image_page' and 'keep' not in r:
            P(f"| identical page | — | {r['pages'][0]} / {r['pages'][1]} | 0 | admitted lines {r['admitted']}; splits {r['splits']} |")
        elif r['kind'] == 'same_image_page':
            P(f"| identical page | {r['keep_page']} | {r['drop_page']} | {r['lines_dropped']} | splits {r['splits']} |")
        else:
            P(f"| book pair ({r['shared_sentences']} shared) | `{r['keep']}` | `{r['drop']}` | {r['lines_dropped']} | splits {r['splits']}"
              + ('; the shared lines are the identical page above, already dropped' if r['lines_dropped'] == 0 else '') + ' |')
    P('')
    # contradictions
    P('## 9. Contradictions between decisions, and between decisions and rules')
    P('')
    for c in CONTRA:
        P('- ' + c)
    P('')
    P('## 10. Implementation notes and deviations from the brief')
    P('')
    for c in NOTES:
        P('- ' + c)
    P('')
    out = []
    for line in L:
        if line.startswith('|'):
            line = re.sub(r'`([^`|]+)\|([^`]+)`', lambda m: '`' + m.group(1) + '\\|' + m.group(2) + '`', line)
        out.append(line)
    with open(os.path.join(AN, 'DECISIONS.md'), 'w') as f:
        f.write('\n'.join(out) + '\n')


TITLE_DOSS = []
CONTRA = []
NOTES = []


def prepare(S, G):
    """build the contradiction / note lists from the measurements (called before write)."""
    HITS = S['DOSS_HITS']; BYNO = G['BYNO']
    for d in G['DOSS']:
        n = d['notes'].lower()
        if d['source'].startswith('openarchives') and 'title' in n and re.search(r'does not match|doesn.t match|wrong|unrelated|belongs to another|not the cinema|is not', n):
            TITLE_DOSS.append(d['no'])

    def hit(no, r):
        return HITS[no]['by_rule'].get(r, 0)

    def pct(no):
        h = HITS[no]
        return f"{h['dropped']}/{h['n']} ({h['dropped'] / h['n'] * 100:.0f} %)"
    CONTRA.extend([
        f"**R3 / R13 vs KEEP books.** 010 (KEEP 0.75, 'both the Greek and the Italian read correctly') loses {pct('010')} — R3 {hit('010', 'R3')}, R13 {hit('010', 'R13')}, "
        f"almost all from C:len_vs_book_high / cph_out_of_range on full parallel-column lines; 003 (KEEP 0.85, 'len_vs_book_high only reflects full-width prose lines against a "
        f"book dominated by short signature lines') loses {pct('003')} (R3 {hit('003', 'R3')}, R13 {hit('003', 'R13')}, R10 {hit('003', 'R10')}); 088 (KEEP 0.9) loses {pct('088')} "
        f"(R3 {hit('088', 'R3')}, R13 {hit('088', 'R13')}); also 061 {pct('061')}, 068 {pct('068')}, 027 {pct('027')}. R3 as briefed treats a book-relative length outlier and a "
        f"class-level density outlier as mismatch; these adjudicators say the lines are correct.",
        f"**R4 vs 002 and 114.** 002 says 'Τσιγκάνα Τσιγκάνα', 'φροὺ φροὺ' and the running head 'ΛΟΓΗΣ ΛΟΓΗΣ' are really printed; 114 says 'τοῦ τοῦ' is in the print. "
        f"The allowlist keeps the first two kinds; R4 still drops {hit('002', 'R4')} line(s) in 002 and {hit('114', 'R4')} in 114. Conversely 001, 032, 033, 045, 046, 048, 049, 055, 098, 099 "
        f"ask for every C:repeated_word line to go.",
        f"**R14 vs 089, 029, 042.** 034 (dev) drops roll-call / dot-leader lines because leader dot counts are arbitrary; 089 (KEEP 0.75, train) describes the same roll-call genre "
        f"('dot leaders transcribed loosely') as acceptable, and 029/042 (KEEP) say their dot-leader tables match. R14 drops {hit('089', 'R14')} lines in 089, {hit('029', 'R14')} in 029, "
        f"{hit('042', 'R14')} in 042.",
        "**D column detection is wrong in both directions inside vouli.** 012 says D:column_crossing on 21–28/35–40 are false positives on single full-width prose lines; "
        "017, 018, 021, 030, 047, 085 say two-column pages were detected as one column so the gutter flag misses merges; 119 says its pages are two-column though the book "
        "is recorded as not. Outside vouli, 020, 049, 055, 097, 100, 108, 125, 134, 088 and 117 say crossing flags are false (single-column text, table rows, justified lines).",
        "**Width thresholds differ by book:** 017/018 width_ratio > 0.6 on all pages; 021/030/047/085 > 0.8 on all pages; 103/111 > 0.55 on two-column pages; 072 > 0.9 with "
        "cpp_vs_book < 0.8 on a single-column book. Not contradictory (different layouts), but there is no single pool-wide width threshold.",
        f"**R12 vs KEEP OpenArchives books 130, 131, 132.** 132: 'residue flags are real Latin symbols (axes x, y, z; E, Q, J …) and read correctly' — R12 drops {hit('132', 'R12')}; "
        f"131: list markers a) b) and formulas are in the print — R12 drops {hit('131', 'R12')}; 130: 'M:8,2, S:41' stats correct — R12 drops {hit('130', 'R12')}. "
        "R12's single-Latin-letter predicate removes correct lines where Latin symbols are genuine.",
        "**113's regex vs 008/012/015.** 113's R7 pattern (?=[α-ωάέήίόύώϊϋΐΰἀ-ᾯὰ-ώᾳῃῳ]) also matches correctly breathed diphthongs (Αἰ, Εὐ, Οἱ), which 008/015 explicitly exempt "
        "('or on the following diphthong vowel'). 012 adds the bare article 'Ο' before names; 008 does not. R7 uses 012's form.",
        "**ANOMALIES §3.4(b) vs adjudicators.** The proposal to drop remaining word-final σ / word-internal ς lines contradicts 002, 035, 037, 038, 046, 110, 126, 127, 137, which found "
        "the final-sigma flags are printed elisions (μέσ᾽, ζῶσ᾽, Φυσῶσ᾽); not applied. 110 shows another source (superscript numerals read as ς before ')'), handled in R15-110.",
        "**ANOMALIES §3.7 vs the brief on which duplicate copy to keep** (eval copy vs train copy). Not realised: the three identical page images that cross train/test have no admitted "
        "lines on the train side, so nothing is dropped from either split for them.",
        "**'9 book pairs sharing ≥ 27 sentences' (brief) vs data:** 5 pairs reach ≥ 27 shared ≥ 25-char sentences (181, 33, 29, 29, 27); they involve 9 books (D's "
        "shares_text_with_other_book count). The next pairs share ≤ 4 such sentences (pairs with 20–50 shared lines are short signature-list names).",
        f"**069's regex includes '«'.** As written it drops every line with a Greek guillemet quotation in that book, not only maths ({hit('069', 'R15')} lines dropped by R15-069 "
        "in total); implemented literally, likely unintended.",
        "**084's split-word regex** `[α-ωά-ώ]{2,} [α-ωά-ώ]{1,2}\\b` matches ordinary text ('και το', 'να'); implemented instead as 'joined form attested ≥ 2 times in the pool and one "
        "part attested ≤ 1 time'.",
        "**117 vs R2:** 117 is a two-column-page majority book, but its adjudicator says the crossing flag mostly hits real full-width prose; it is excluded from R2 and gets a "
        "merge-only rule in R15.",
        "**RELABEL decisions that also drop:** 006 (lines with '/' in the pronunciation parenthesis), 014 (mis-segmented and '1......' lines), 109 (cpp_vs_book_out and drop-capital 'H' lines) "
        "are RELABEL decisions that include drop patterns; 086 offers drop as an alternative to relabel (relabel implemented).",
        "**Suggestions in KEEP notes not turned into rules:** 011 (test) strip a leading ✓/*/· footnote marker; 131 'CI'→'Cl'; 100 'ся'→'сж' in pre-1945 Bulgarian; 037/038 em-dash "
        "labelled as hyphen (pool-wide Google habit); 097 general Latin→Cyrillic homoglyph mapping (only 'Ha'→'На' implemented).",
        "**Wikisource scope.** The brief limits R3 to scanned waves and leaves out wikisource, although wikisource lines are scans too (5 test books in the dossiers: 037, 050, 127, 137 KEEP). "
        "R3/R13 therefore never fire on wikisource.",
    ])
    NOTES.extend([
        "R2: width_ratio > 0.8 on pages detected as 1-column only for the six all-pages vouli books (see rules.json R2 notes). Page majority uses pages with ≥ 1 admitted line.",
        "R3: low/high side of C:cpp_vs_book_out read from the flag reason ('<' = low); all-caps from B is_all_caps.",
        "R4: C:repeated_word compares tokens with punctuation; the extra exact-pair check also keeps punctuation (so 'μέτρα, μέτρα' is not a doubled reading); the "
        "accent-variant check strips punctuation and treats grave = acute (ποτέ / ποτὲ is a positional variant, not a second reading).",
        "R5: narrowed from `\\S- \\S` (see rules.json).",
        "R6: the spacing tonos U+0384 is only a tonos in monotonic lines; in polytonic lines it stands for a breathing and those lines are dropped as ambiguous. Spacing marks before "
        "Υ/Ρ with no precomposed capital (psili on Υ, psili on Ρ) are left unchanged.",
        "R7: single-letter matches only for the articles Ο/Η (Α, Ι … are figure letters in geometry/physics books); a bare capital at line end (vote mark) and all-caps lines are ignored.",
        "R8(b) (plain σ for στ) is a RELABEL, not a drop: every sampled case is 'σρατ-', 'κατασρέφ-', 'ἐπέσρεψ-' with an attested στ form.",
        "R9: the 'Cyrillic in non-Cyrillic text' half excludes the cyrillic wave and Cyrillic-majority books, whose Latin-class lines legitimately contain Bulgarian/Russian words.",
        "R10: when one copy of an identical page has 0 admitted lines nothing is dropped (keeping the empty copy would only delete the other).",
        "R11 is metadata only: the clean preview keeps `year` and adds 'R11' to `rules_applied` for every OpenArchives line; consumers should treat year as null and the title as "
        f"unreliable. OpenArchives dossiers whose notes say the catalogue title/year does not match the content: {', '.join(TITLE_DOSS)} ({len(TITLE_DOSS)}).",
        "R13: no minimum page size (as briefed); 5 lines come from pages with fewer than 5 admitted lines.",
        "R14: leader runs apply pool-wide (they also catch ellipses written as ≥ 5 dots and table-of-contents leaders); the trailing vote mark only in vouli.",
        "R15: predicates are the adjudicators' rules as written, except 084 (split-word) and 113 (folded into R7). 'C:cpp_vs_book_out' in a book rule means either side, "
        "since the adjudicators did not restrict it.",
        "Line order of evaluation: relabels first (R6, R8, R15 relabels) to build label_v2; R7 is tested on the R6-normalised label; every other drop predicate on the original label.",
    ])
