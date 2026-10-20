"""Port of efficiency owner39_score.normalize, unchanged, source bound in receipt."""
from collections import Counter
import json
from pathlib import Path

from owner39_common import HEADS, VALUES, clusters, is_letter, tuple_heads


def letters(text):
    return [c for c in clusters(text) if is_letter(c[0])]


def validate_heads(heads):
    if not isinstance(heads, dict) or set(heads)!=set(HEADS):
        raise ValueError('owner39 requires all four heads')
    if any(not isinstance(heads[h],str) or heads[h] not in VALUES[h] for h in HEADS):
        raise ValueError('Invalid owner39 head')


def normalize(row, item):
    if not isinstance(row,dict):
        raise ValueError('owner39 answers must be JSON objects')
    required={'card_id','choice','anchor_heads','letter_heads','readability','ownership_ok','confidence','note','usage'}
    if not required <= set(row):
        raise ValueError('Missing owner39 answer-schema fields')
    choice=row['choice']; opts=item['options']
    if not isinstance(choice,str) or choice not in {*opts,'literal','unreadable'}:
        raise ValueError('Invalid owner39 choice')
    text=row.get('transcription') if choice=='literal' else opts.get(choice)
    if choice=='literal' and (not isinstance(text,str) or not text.strip()):
        raise ValueError('owner39 literal requires complete transcription')
    if not isinstance(row['readability'],str) or not isinstance(row['confidence'],str) or row['readability'] not in {'readable','partial','unreadable'} or row['confidence'] not in {'high','medium','low'}:
        raise ValueError('Invalid owner39 readability/confidence')
    if row['ownership_ok'] is not None and type(row['ownership_ok']) is not bool:
        raise ValueError('Invalid owner39 ownership_ok')
    if not isinstance(row['note'],str):
        raise ValueError('Invalid owner39 note')
    # R2 asks readers for zero placeholders; these are never measured usage.
    if not isinstance(row['usage'],dict) or row['usage']!={'input_tokens':0,'output_tokens':0} or any(type(v) is not int for v in row['usage'].values()):
        raise ValueError('owner39 answer usage must be R2 zero placeholders; supply measured usage separately')
    validate_heads(row['anchor_heads'])
    ls=letters(text) if text is not None else []
    anchor=item['anchor_index']
    if choice!='unreadable' and len(ls)<=anchor:
        raise ValueError('owner39 transcription lacks anchor letter')
    if choice=='unreadable' and any(v!='unknown' for v in row['anchor_heads'].values()):
        raise ValueError('owner39 unreadable requires unknown heads')
    all_heads={anchor:row['anchor_heads']}
    if not isinstance(row['letter_heads'],list):
        raise ValueError('owner39 letter_heads must be a list')
    for entry in row['letter_heads']:
        if not isinstance(entry,dict) or set(entry)!={'index',*HEADS}:
            raise ValueError('Invalid owner39 letter_heads entry')
        index=entry['index']
        if type(index) is not int or index<0 or index>=len(ls) or index in all_heads:
            raise ValueError('Duplicate/invalid owner39 letter index')
        heads={h:entry[h] for h in HEADS};validate_heads(heads);all_heads[index]=heads
    for index,heads in all_heads.items():
        if not ls: continue
        printed=tuple_heads(ls[index])
        if any(v!='unknown' and v!=printed[h] for h,v in heads.items()):
            raise ValueError('owner39 known head disagrees with transcription')
    if all(v=='none' for v in row['anchor_heads'].values()) and row['ownership_ok'] is not None:
        raise ValueError('owner39 unmarked anchor requires null ownership_ok')
    return dict(card_id=row['card_id'],base=ls[anchor][0] if ls else 'unknown',
                heads=dict(row['anchor_heads']),confidence=row['confidence'],readability=row['readability'])

