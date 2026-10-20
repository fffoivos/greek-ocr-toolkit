"""R2-schema normalization and descriptive scoring of the 39 owner slots.

Readers stay separate: no majority vote or resolver/adoption policy is invented.
One owner-confirmed anchor slot per card is scored. Other letter_heads are
checked for schema/ink-transcription consistency, but have no independent truth.
"""
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


def summary(pairs, expected):
    """Unknown is abstention: included in denominators, never correct vs truth."""
    agree=sum(a==b and a!='unknown' and b!='unknown' for _,a,b in pairs)
    return dict(agree=agree,disagree=len(pairs)-agree,compared=len(pairs),expected=expected,
                missing=expected-len(pairs),rate=agree/len(pairs) if pairs else None,
                unknown_left=sum(a=='unknown' for _,a,_ in pairs),unknown_right=sum(b=='unknown' for _,_,b in pairs),
                literal_call_agree=sum(a==b for _,a,b in pairs),
                literal_call_rate=sum(a==b for _,a,b in pairs)/len(pairs) if pairs else None)


def agreement(left, right, truth):
    common=sorted(set(left)&set(right)&set(truth))
    fields={'base':summary([(i,left[i]['base'],right[i]['base']) for i in common],len(truth))}
    for h in HEADS:
        expected=sum(h in t['scored_heads'] for t in truth.values())
        fields[h]=summary([(i,left[i]['heads'][h],right[i]['heads'][h]) for i in common if h in truth[i]['scored_heads']],expected)
        fields[h]['excluded_card_ids']=[i for i,t in truth.items() if h not in t['scored_heads']]
    per_card=[]
    for i in common:
        hs=truth[i]['scored_heads'];a=left[i];b=right[i]
        decided=all(a['heads'][h]!='unknown' and b['heads'][h]!='unknown' for h in hs)
        marks=decided and all(a['heads'][h]==b['heads'][h] for h in hs)
        base=a['base']==b['base'] and a['base']!='unknown'
        per_card.append(dict(card_id=i,base_agree=base,mark_tuple_agree=marks,all_scored_fields_agree=base and marks,
                             scored_heads=list(hs),left=a,right=b))
    # Tuple counts include any undecided component as a non-agreement. Counts
    # of literal unknown values are reported per head, not synthetic tuples.
    def tuple_summary(flag):
        n=sum(c[flag] for c in per_card)
        return dict(agree=n,disagree=len(common)-n,compared=len(common),expected=len(truth),
                    missing=len(truth)-len(common),rate=n/len(common) if common else None)
    return dict(expected_items=len(truth),compared_items=len(common),fields=fields,
                mark_tuple_per_slot=tuple_summary('mark_tuple_agree'),
                all_fields_per_card=tuple_summary('all_scored_fields_agree'),per_card=per_card,
                missing_left_items=sorted(set(truth)-set(left)),missing_right_items=sorted(set(truth)-set(right)))


def distribution(actual, truth):
    calls={h:dict(Counter(v['heads'][h] for v in actual.values())) for h in HEADS}
    return dict(calls=calls,unknown_counts={**{h:sum(v['heads'][h]=='unknown' for v in actual.values()) for h in HEADS},
                'base':sum(v['base']=='unknown' for v in actual.values()),
                'cards_with_unknown':sum(v['base']=='unknown' or any(x=='unknown' for x in v['heads'].values()) for v in actual.values()),
                'scored_head_unknowns':sum(v['heads'][h]=='unknown' for i,v in actual.items() for h in truth[i]['scored_heads'])},
                confidence=dict(Counter(v['confidence'] for v in actual.values())),
                readability=dict(Counter(v['readability'] for v in actual.values())),missing_items=sorted(set(truth)-set(actual)))


def score_bed(manifest, truth, submissions, usage, root, efficiency):
    packs=[p for p in manifest['packs'] if p['bed']=='owner39']
    assignments={(p['arm'],p['reader']):p for p in packs}
    data={};seen=set()
    for bed,arm,reader,records in submissions:
        if bed!='owner39': continue
        key=(arm,reader)
        if key not in assignments or key in seen:
            raise ValueError('Unknown or duplicate owner39 reader submission')
        seen.add(key);pack=assignments[key]
        items={v['card_id']:v for v in (json.loads(s) for s in (Path(root)/pack['path']/'cards.jsonl').read_text().splitlines())}
        actual={}
        for row in records:
            if not isinstance(row,dict):
                raise ValueError('owner39 answers must be JSON objects')
            cid=row.get('card_id')
            if not isinstance(cid,str) or cid not in items or cid in actual:
                raise ValueError('Duplicate, wrong-reader or unknown owner39 card_id')
            actual[cid]=normalize(row,items[cid])
        data[key]=actual
    result=dict(arms={},E0a_E0b_agreement={},
                scoring_scope='One owner-confirmed anchor slot per card; punctuation, other letters, ownership, readability and confidence have no owner truth and are not accuracy targets.',
                unknown_policy='Unknown is an unconfirmed head, never none or a correct guess: it remains in denominators and is reported separately; unknown/unknown is not confirmed agreement. Owner-unknown breathing is excluded in every comparison.',
                replication='Two independent readers per card; report r1 and r2 separately; no majority/adjudication is inferred.')
    for reader in ('r1','r2'):
        result['E0a_E0b_agreement'][reader]=agreement(data.get(('E0a',reader),{}),data.get(('E0b',reader),{}),truth)
    for arm in dict.fromkeys(p['arm'] for p in packs):
        arm_packs=[p for p in packs if p['arm']==arm]; readers={}
        for p in arm_packs:
            reader=p['reader'];actual=data.get((arm,reader),{})
            readers[reader]=dict(submitted=(arm,reader) in seen,complete=set(actual)==set(truth),
                agreement_with_truth=agreement(actual,truth,truth),
                agreement_with_E0a=agreement(actual,data.get(('E0a',reader),{}),truth),**distribution(actual,truth))
        costs=efficiency(arm_packs,usage)
        result['arms'][arm]=dict(factor=manifest['arms'][arm],expected_readers=2,submitted_readers=sum((arm,r) in seen for r in readers),
            complete=all(v['complete'] for v in readers.values()),readers=readers,
            between_readers_agreement=agreement(data.get((arm,'r1'),{}),data.get((arm,'r2'),{}),truth),
            efficiency={**costs,'unique_cards':len(truth),'assigned_card_reads':sum(p['items_per_reader'] for p in arm_packs),
                        'tokens_per_unique_card':costs['total_tokens']/len(truth) if costs['usage_complete'] else None,
                        'reader_wall_ms_per_unique_card':costs['summed_reader_duration_ms']/len(truth) if costs['usage_complete'] else None,
                        'tool_uses_per_unique_card':costs['total_tool_uses']/len(truth) if costs['usage_complete'] else None,
                        'unit':'per card-read; each unique card is assigned to both readers'})
    return result
