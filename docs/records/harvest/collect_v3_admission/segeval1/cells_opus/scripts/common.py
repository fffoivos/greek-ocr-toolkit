"""Shared definitions for the cells_opus analysis (read-only)."""
import re
import unicodedata

SEPS = set(".,:;/-–—%()+'′§№° ")
ROMAN = re.compile(r'M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})')


def nchars(text):
    """Google text's non-space characters (NFC codepoints that are not whitespace)."""
    return sum(not c.isspace() for c in unicodedata.normalize('NFC', text or ''))


def output_type(text):
    s = (text or '').strip()
    if not s:
        return 'non-numeric'
    if any(c.isdecimal() for c in s) and all(c.isdecimal() or c in SEPS or c.isspace() for c in s):
        return 'numeric'
    tok = s[:-1] if s[-1] in '.)' else s
    if tok and ROMAN.fullmatch(tok):
        return 'numeric'
    digits = sum(c.isdecimal() for c in s)
    letters = sum(unicodedata.category(c).startswith('L') for c in s)
    if digits and letters <= 2:
        return 'mixed'
    return 'non-numeric'


REASON = {
    'OCR length matches': 'KEEP',
    'The complete neighbouring-word count': 'UNCERTAIN:neighbour/extent unresolved',
    'The reading direction': 'UNCERTAIN:direction unresolved',
    'The detector returned no row': 'UNCERTAIN:no detected row',
    'No usable text box': 'UNCERTAIN:no text box',
    'Too little OCR output': 'DROP:too little OCR for box',
    'Too much OCR output': 'DROP:too much OCR for box',
    'Top and bottom padding': 'DROP:padding',
    'A second complete printed line': 'DROP:second line',
    'More than 2 complete neighbouring': 'DROP:neighbour words',
}


def reason_code(verdict, reason):
    if verdict is None:
        return 'NOT_EVALUATED'
    r = (reason or '').split(': ', 1)[-1] if (reason or '').startswith(('length:', 'gate:', 'padding:', 'neighbour')) else (reason or '')
    for k, v in REASON.items():
        if r.startswith(k):
            if not v.startswith(verdict):
                return f'{verdict}:{v}'
            return v
    return f'{verdict}:{(reason or "")[:60]}'
