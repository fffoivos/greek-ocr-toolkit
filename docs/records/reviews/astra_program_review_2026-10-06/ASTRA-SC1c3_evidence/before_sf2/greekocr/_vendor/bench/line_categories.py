"""A3b rule tags, version 1. Overlapping diagnostic strata, never admission gates.

Leaders >=3 dots; numerics >=20% nonspace characters; all-caps >=3 letters;
footnote <=9pt or <=0.8*page median; punctuation >=20% nonspace; long >=100
NFD atoms or strip width >=1600. Italic/bold require explicit font metadata.
"""
from __future__ import annotations
import re
import unicodedata as ud
from greekocr._vendor.bench.common import script
from greekocr._vendor.bench.o4b_common import tag

RULE_VERSION = 'e2-a3b-v1'


def word_tags(text):
    return [dict(text_nfd=ud.normalize('NFD', word), script_class=tag(word),
                 tagger='o4b_common.tag / factory classify parity') for word in text.split()]


def categories(row):
    text = row.get('gt', row.get('gt_nfd', row.get('text', '')))
    visible = [c for c in text if not c.isspace() and not ud.category(c).startswith('M')]
    letters = [c for c in text if c.isalpha()]
    result = []
    if re.search(r'\.{3,}|(?:\.\s*){3,}|…{2,}', text): result.append('dotted_leaders')
    if visible and sum(c.isdigit() for c in visible)/len(visible) >= .2: result.append('numerics')
    if len(letters) >= 3 and all(c.isupper() for c in letters): result.append('all_caps')
    size = row.get('font_size_pt', row.get('size_pt', row.get('size')))
    median = row.get('page_median_font_size_pt')
    if isinstance(size, (float, int)) and (size <= 9 or isinstance(median, (float, int)) and size <= .8*median):
        result.append('footnote_size')
    elif size is None: result.append('footnote_size_unknown')
    fonts = row.get('font_names', [row.get('font', '')]) or []
    if isinstance(fonts, str): fonts = [fonts]
    names = ' '.join(fonts).casefold()
    if row.get('italic') is True or re.search(r'italic|oblique', names): result.append('italic')
    if row.get('bold') is True or re.search(r'bold|semibold|demi', names): result.append('bold')
    if not names or names in ('real', 'unknown'):
        result.append('font_style_unknown')
    if re.search(r'\w[-‐‑]\s*$|\w[-‐‑]\w', text): result.append('hyphenation')
    if visible and sum(ud.category(c).startswith('P') for c in visible)/len(visible) >= .2:
        result.append('punctuation_heavy')
    if len({script(c) for c in letters}-{None}) >= 2: result.append('mixed_script')
    if len(ud.normalize('NFD', text)) >= 100 or row.get('width', 0) >= 1600: result.append('long_lines')
    return sorted(result or ['ordinary'])
