"""Greek+Latin text-side look-alike rule (coordinator ruling 2, 17 Oct 00:00).
A token whose letters are 1-3 Greek letters, all with a one-to-one Latin look-alike and no diacritics,
adjacent (prev/next alphabetic word) to >=1 Latin-script word:
  - if it has two alphabetic neighbours and both are Latin -> map the token to Latin (counted 'mapped');
  - otherwise -> exclude the line (counted 'excluded')."""
import unicodedata, re
MAP = dict(zip('ΑΒΕΖΗΙΚΜΝΟΡΤΥΧαικνορτχ', 'ABEZHIKMNOPTYXaikvoptx'))
AMBIG = set('υ')  # u or v: never mapped; a look-alike token containing it excludes the line
def script(w):
    s = set()
    for c in w:
        if c.isalpha():
            n = unicodedata.name(c, '')
            s.add('G' if 'GREEK' in n else 'L' if 'LATIN' in n else 'O')
    return s.pop() if len(s) == 1 else ('M' if s else None)
def core(tok): return re.sub(r'[^\w]', '', tok)
def is_lookalike(tok):
    # Inspect the complete token before core() can discard combining marks.
    if any(unicodedata.category(ch).startswith('M') for ch in unicodedata.normalize('NFD', tok)):
        return False
    c = core(tok)
    return 1 <= len(c) <= 3 and all(ch in MAP or ch in AMBIG for ch in c) and unicodedata.normalize('NFD', c) == c
def apply(label):
    label = unicodedata.normalize('NFC', label)
    toks = label.split(' '); words = [(i, script(t)) for i, t in enumerate(toks) if script(t)]
    out = list(toks); mapped = 0
    for k, (i, sc) in enumerate(words):
        if sc != 'G' or not is_lookalike(toks[i]): continue
        nb = [words[j][1] for j in (k - 1, k + 1) if 0 <= j < len(words)]
        if 'L' not in nb: continue
        if len(nb) == 2 and all(x == 'L' for x in nb) and not (set(core(toks[i])) & AMBIG):
            out[i] = ''.join(MAP.get(ch, ch) for ch in toks[i]); mapped += 1
        else:
            return None, 'excluded'
    return ' '.join(out), ('mapped' if mapped else 'unchanged')
