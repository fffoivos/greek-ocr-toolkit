"""Pure R2 text/option helpers ported verbatim from r2_cards_prepare.py.

The source module is never imported: it includes other preparation entry points.
Only the six named pure functions are copied. Rendering is ported in build_owner39.py.
"""
import random
import re
import unicodedata as U

HEADS = ('breathing', 'accent', 'diaeresis', 'subscript')
VALUES = {'breathing': {'none','psili','dasia','unknown'},
          'accent': {'none','acute','grave','circumflex','unknown'},
          'diaeresis': {'none','present','unknown'},
          'subscript': {'none','present','unknown'}}

def literal_normalize(form,text):
    # Copied S8 convention: preserve printed keraia codepoints through Unicode
    # normalisation. U+0384 is not an accent head; U+0374 is not a letter slot.
    return ''.join(c if c in ('\u0374','\u0384') else U.normalize(form,c)
                   for c in re.split('([\u0374\u0384])',text))

def is_letter(c):
    return U.category(c) in ('Lu','Ll','Lt','Lo')

def skeleton(text):
    return ''.join(c for c in literal_normalize('NFD',text) if is_letter(c))

def clusters(text):
    out=[]
    for c in literal_normalize('NFD',text):
        if U.combining(c) and out:
            out[-1]+=c
        else:
            out.append(c)
    return out

def tuple_heads(cluster):
    return dict(breathing='dasia' if '\u0314' in cluster else 'psili' if '\u0313' in cluster else 'none',
                accent='acute' if '\u0301' in cluster else 'grave' if '\u0300' in cluster else 'circumflex' if '\u0342' in cluster else 'none',
                diaeresis='present' if '\u0308' in cluster else 'none',
                subscript='present' if '\u0345' in cluster else 'none')

def options(base,anchor,head,seed):
    # No provider mark is copied. Only base letters and punctuation survive.
    spacing_names=('PSILI','DASIA','VARIA','OXIA','PERISPOMENI','DIALYTIKA','TONOS','KORONIS')
    cc=[c for c in literal_normalize('NFD',base) if not U.category(c).startswith('M') and
        not (c not in ('\u0374','\u0384') and not is_letter(c) and 'GREEK' in U.name(c,'') and
             any(s in U.name(c,'') for s in spacing_names))]
    positions=[i for i,c in enumerate(cc) if is_letter(c)]
    pos=positions[anchor]
    marks={'breathing':['','\u0313','\u0314'], 'accent':['','\u0301','\u0300','\u0342'],
           'diaeresis':['','\u0308'], 'subscript':['','\u0345']}[head]
    forms=[literal_normalize('NFC',''.join(cc[:pos+1])+m+''.join(cc[pos+1:])) for m in marks]
    random.Random(seed).shuffle(forms)
    return {chr(65+i):v for i,v in enumerate(forms)}
