"""R1 science contract and text-only helpers. Never imports ink/SciPy."""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input

import gzip
import json
from pathlib import Path
import random
import numpy as np

from scripts.labelfix.clariden.c1_common import crop_key, crop_path, sha256, text_functions, write_json
from greekocr.labelfix.text import MARK_BEARERS, clusters, nfd

SEED = 20261016
HEADS = dict(breathing=('none', 'psili', 'dasia'), accent=('none', 'acute', 'grave', 'circumflex'),
             dialytika=('none', 'dialytika'), subscript=('none', 'subscript'))
LETTERS = 'αεηιουωρΑΕΗΙΟΥΩΡ'
MARKS = dict(psili='\u0313', dasia='\u0314', acute='\u0301', grave='\u0300',
             circumflex='\u0342', dialytika='\u0308', subscript='\u0345')
ARMS = {a: dict(embedding=a != 'B', left_heights=.75 if a == 'C' else 1.5,
               balanced=a != 'D', none_fraction='natural' if a in 'DE' else .4,
               rare_min_fraction=0 if a == 'D' else .05) for a in 'ABCDE'}
INDEX_DTYPE = np.dtype([('shard', '<i4'), ('offset', '<i4'), ('line', '<i4'), ('start', '<i4'),
                       ('letter', 'u1'), ('validation', 'u1'), ('target', 'i1', (4,)),
                       ('mask', '<f4', (2, 2))])


def rows(path):
    with (gzip.open if str(path).endswith('.gz') else open)(_data_input(path), 'rt', encoding='utf8') as f:
        yield from (json.loads(x) for x in f if x.strip())


def write_rows(path, data):
    with (gzip.open if str(path).endswith('.gz') else open)(path, 'wt', encoding='utf8') as f:
        for r in data:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def canonical_doc(s):
    return s.removesuffix(':human')


def canonical_line(s):
    return s.removesuffix('-human')


def document_split(selection):
    docs = sorted({r['doc'] for r in selection})
    if len(docs) != 316:
        raise ValueError(f'expected 316 C1 documents, got {len(docs)}')
    val = set(random.Random(SEED).sample(docs, 16))
    return dict(seed=SEED, train=[d for d in docs if d not in val], validation=sorted(val))


def check_disjointness(selection, exclusions):
    docs = {canonical_doc(r['doc']) for r in selection}
    ids = {canonical_line(r.get('id', r.get('line_id', ''))) for r in selection}
    result = {}
    for name, group in exclusions['sets'].items():
        ds = sorted(docs & {canonical_doc(d) for d in group['documents']})
        ls = sorted(ids & {canonical_line(i) for i in group['line_ids']})
        result[name] = dict(document_count=len(ds), line_count=len(ls), documents=ds, line_ids=ls,
                            excluded_documents=len(group['documents']), excluded_lines=len(group['line_ids']))
    if any(r['document_count'] or r['line_count'] for r in result.values()):
        raise ValueError('C1 overlap: ' + json.dumps(result))
    return result


def factors(marks):
    cls = text_functions()['mark_class'](marks)
    if cls is None:
        return None
    parts = cls.split('+')
    values = []
    for choices in HEADS.values():
        hit = [i for i, c in enumerate(choices) if i and c in parts]
        if len(hit) > 1:
            return None
        values.append(hit[0] if hit else 0)
    if set(marks) - set(MARKS.values()):
        return None
    return values


def compose(values):
    names = {choices[int(i)] for choices, i in zip(HEADS.values(), values) if int(i)}
    return '+'.join(k for k in ('psili','dasia','dialytika','acute','grave','circumflex','subscript') if k in names) or 'none'


def agreement_targets(google, recogniser):
    """Exact NFD core equality including case and marks; indices belong to recogniser."""
    out = {}
    for g, m in text_functions()['pair_tokens'](nfd(google), nfd(recogniser)):
        if m is not None and g.core and g.core == m.core:
            for cl in clusters(m.core):
                if cl.base in MARK_BEARERS:
                    out[m.core_start + cl.start] = factors(cl.marks)
    return out


def verify_receipt(directory):
    directory = Path(directory)
    receipt = json.loads((directory/'extraction_receipt.json').read_text())
    if not receipt['complete']:
        raise ValueError('extraction incomplete')
    for p, digest in receipt['sha256'].items():
        if sha256(directory/p) != digest:
            raise ValueError(f'extracted shard changed: {p}')
    return receipt


def transfer_record(text, alignment):
    """Same matched/nearest-neighbour span transfer as ctc_align.transfer_alignment.

    Frozen recogniser text defines slots. Never reads labels, never runs CTC.
    """
    text=nfd(text)
    if text==alignment['prediction']:return alignment,False
    path=text_functions()['align_chars'](text,alignment['prediction'])
    owner=[None]*len(text)
    for i,j in path:
        if i is not None and j is not None:owner[i]=j
    last=None
    for i in range(len(text)):
        if owner[i] is None:owner[i]=last
        else:last=owner[i]
    nxt=None
    for i in range(len(text)-1,-1,-1):
        if owner[i] is None:owner[i]=nxt
        else:nxt=owner[i]
    spans=[[ch,*alignment['spans'][owner[i]][1:]] if owner[i] is not None else [ch,0,0,0.,0.]
           for i,ch in enumerate(text)]
    return dict(alignment,prediction=text,spans=spans),True
