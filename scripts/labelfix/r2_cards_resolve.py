"""Offline R2C control gating, disagreement deck and explicit-head 2-of-3 truth.

Usage: --deck .../T2 --reader1 r1.jsonl --reader2 r2.jsonl --out ...
Validation only: --dry-run --deck ... --reader1 answers.jsonl --manifest cards.jsonl --out ...
Optional --reader3 r3.jsonl consumes the generated tiebreak manifest. The lead
must first pixel-verify every private controls_proposed.json entry. No proposed
selection text is ever admitted as truth. Repeated views count once.
"""
from greekocr.ops.data_root import input_path as _data_input
import sys
sys.dont_write_bytecode=True
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import unicodedata as U

HEADS={'breathing':{'none','psili','dasia','unknown'},
       'accent':{'none','acute','grave','circumflex','unknown'},
       'diaeresis':{'none','present','unknown'},'subscript':{'none','present','unknown'}}


def read(path):
    return [json.loads(s) for s in _data_input(Path(path)).read_text().splitlines() if s.strip()]


def dump(path,obj):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def write(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(''.join(json.dumps(r,ensure_ascii=False,allow_nan=False)+'\n' for r in data))


def literal_normalize(form,text):
    return ''.join(c if c in ('\u0374','\u0384') else U.normalize(form,c)
                   for c in re.split('([\u0374\u0384])',text))


def letters(form):
    return [c for c in literal_normalize('NFD',form) if U.category(c) in ('Lu','Ll','Lt','Lo')]


def form_heads(form):
    cc=[]
    for c in literal_normalize('NFD',form):
        if U.combining(c) and cc:
            cc[-1]+=c
        else:
            cc.append(c)
    return [dict(breathing='dasia' if '\u0314' in c else 'psili' if '\u0313' in c else 'none',
                 accent='acute' if '\u0301' in c else 'grave' if '\u0300' in c else 'circumflex' if '\u0342' in c else 'none',
                 diaeresis='present' if '\u0308' in c else 'none',subscript='present' if '\u0345' in c else 'none')
            for c in cc if U.category(c[0]) in ('Lu','Ll','Lt','Lo')]


def unmarked(heads):
    return all(heads.get(h)=='none' for h in HEADS)


def ownership(value,anchor_heads):
    # R2C2 protocol/key correction: an unmarked anchor has no mark to own.
    return None if unmarked(anchor_heads) else value


def normalise(answer,card):
    if answer['card_id']!=card['card_id']:
        raise ValueError('card ID mismatch')
    choice=answer['choice']
    if choice in card['options']:
        form=card['options'][choice]
    elif choice=='literal':
        form=answer.get('transcription','')
        if not isinstance(form,str) or not form.strip():
            raise ValueError('literal answer requires complete transcription')
    elif choice=='unreadable':
        form=None
    else:
        raise ValueError('unknown option identity')
    if answer['readability'] not in ('readable','partial','unreadable'):
        raise ValueError('invalid readability')
    if answer['ownership_ok'] is not None and type(answer['ownership_ok']) is not bool:
        raise ValueError('invalid ownership')
    if answer['confidence'] not in ('high','medium','low') or not isinstance(answer['note'],str):
        raise ValueError('invalid confidence or note')
    if choice=='unreadable' and answer['readability']!='unreadable':
        raise ValueError('unreadable choice contradicts readability')
    targets={}
    supplied=list(answer.get('letter_heads',[]))
    supplied.append(dict(index=card['anchor_index'],**answer['anchor_heads']))
    for row in supplied:
        idx=row['index']
        missing_anchor=(idx==card['anchor_index'] and all(row.get(h)=='unknown' for h in HEADS))
        if type(idx) is not int or idx<0 or (form is not None and idx>=len(letters(form)) and not missing_anchor):
            raise ValueError('letter index outside transcription')
        if idx in targets:
            raise ValueError('duplicate letter-head index')
        if any(row.get(h) not in values for h,values in HEADS.items()):
            raise ValueError('invalid or missing head value')
        if form is not None and not missing_anchor and any(row[h]!='unknown' and row[h]!=form_heads(form)[idx][h] for h in HEADS):
            raise ValueError('head tuple contradicts literal form; use unknown for undecided heads')
        targets[idx]={h:row[h] for h in HEADS}
    usage=answer.get('usage',{})
    if any(type(v) is not int or v<0 for v in usage.values()):
        raise ValueError('invalid token usage')
    return dict(card_id=answer['card_id'],form=literal_normalize('NFC',form) if form is not None else None,
                heads=targets,anchor_index=card['anchor_index'],readability=answer['readability'],
                ownership_ok=ownership(answer['ownership_ok'],targets[card['anchor_index']]),
                confidence=answer['confidence'],note=answer['note'],usage=usage)


def batch(path,cards,controls,expected_order):
    answers=read(path)
    ids=[a['card_id'] for a in answers]
    if ids!=expected_order:
        raise ValueError('reader IDs/order differ from assigned manifest (reader 2 must use reverse order)')
    normal={};invalid=[]
    for a in answers:
        try:
            normal[a['card_id']]=normalise(a,cards[a['card_id']])
        except (ValueError,KeyError,TypeError,AttributeError,IndexError) as exc:
            invalid.append(dict(card_id=a['card_id'],reason=str(exc)))
    failures=[]
    for control in controls:
        ident=control['card_id'];card=cards[ident]
        if ident not in normal:
            failures.append(ident);continue
        a=normal[ident]
        expected=next(r for r in control['expected_letter_heads'] if r['index']==card['anchor_index'])
        ownership_na=unmarked(a['heads'][card['anchor_index']]) or unmarked(expected)
        if (a['form']!=literal_normalize('NFC',control['expected_form']) or
            a['readability']!=control['expected_readability'] or
            (not ownership_na and a['ownership_ok']!=control['expected_ownership_ok']) or
            any(a['heads'][card['anchor_index']][h]!=expected[h] for h in HEADS)):
            failures.append(ident)
    # Invalid readings still consumed tokens. Retain well-formed usage even when
    # another field is invalid; malformed/missing usage remains unreported.
    usages=[a.get('usage',{}) for a in answers]
    usages=[u if isinstance(u,dict) and all(type(v) is int and v>=0 for v in u.values()) else {} for u in usages]
    gate=dict(invalid_answers=invalid,invalid_answer_count=len(invalid),valid_answers=len(normal),
              answers=len(answers),control_failures=failures,control_errors=len(failures),
              accepted=len(failures)<=1,
              input_tokens=sum(u.get('input_tokens',0) for u in usages),
              output_tokens=sum(u.get('output_tokens',0) for u in usages),
              tokens_reported=all('input_tokens' in u and 'output_tokens' in u for u in usages))
    return normal,gate


def signature(a):
    return (a['form'],a['readability'],ownership(a['ownership_ok'],a['heads'][a['anchor_index']]),
            json.dumps(a['heads'],sort_keys=True))


def majority(values,default):
    count=Counter(values)
    if count:
        value,n=count.most_common(1)[0]
        if n>=2:
            return value
    return default


def resolve_card(key,answers):
    form=majority([a['form'] for a in answers],None)
    selected=[a for a in answers if a['form']==form] if form is not None else []
    ownership=majority([a['ownership_ok'] for a in selected],None)
    readability=majority([a['readability'] for a in selected],'unknown')
    decided=[]
    if form is not None:
        for i,base in enumerate(letters(form)):
            targets={}
            for head in HEADS:
                values=[a['heads'].get(i,{}).get(head,'unknown') for a in selected
                        if (a['ownership_ok'] is True or
                            unmarked(a['heads'].get(key['anchor_index'],{})))
                        and a['readability'] in ('readable','partial')]
                targets[head]=majority(values,'unknown')
            decided.append(dict(index=i,base=base,**targets))
    return dict(card_id=key['card_id'],deck=key.get('deck'),slice=key['slice'],
                crop_sha256=key['crop_sha256'],word_index=key['word_index'],
                printed_form=form,letter_heads=decided,anchor_index=key['anchor_index'],
                target_head=key['target_head'],ownership_ok=ownership,readability=readability,
                status='resolved' if form is not None and (ownership is True or
                (ownership is None and any(r['index']==key['anchor_index'] and unmarked(r) for r in decided))) and
                any(all(r[h]!='unknown' for h in HEADS) for r in decided) else 'unresolved',
                votes=len(answers),control=False)


def inventory(truth,keys):
    # Letter index is crop-relative, not word-relative: otherwise the first
    # letters of different words in one crop would collapse into the same slot.
    groups=defaultdict(lambda:dict(complete=set(),absent=set(),marked=set(),unknown=set()))
    for t in truth:
        key=keys[t['card_id']];g=groups[(key.get('deck','unknown'),t['slice'])]
        offset=key['crop_letter_offset']
        if t['printed_form'] is None or not t['letter_heads']:
            g['unknown'].add((t['crop_sha256'],offset+t['anchor_index']))
        ownership_na=t['ownership_ok'] is None and any(
            r['index']==t['anchor_index'] and unmarked(r) for r in t['letter_heads'])
        for r in t['letter_heads']:
            slot=(t['crop_sha256'],offset+r['index'])
            if (t['ownership_ok'] is not True and not ownership_na) or any(r[h]=='unknown' for h in HEADS):
                g['unknown'].add(slot);continue
            g['complete'].add(slot)
            # Absent/marked is relative to the prespecified target head.
            g['absent' if r[t['target_head']]=='none' else 'marked'].add(slot)
    return {deck+':'+sl:{k:len(v) for k,v in g.items()} for (deck,sl),g in sorted(groups.items())}


def tiebreak(deck,out,keys,disagreements,controls):
    blind=out/'tiebreak/blind';private=out/'tiebreak/private'
    blind.mkdir(parents=True,exist_ok=True);private.mkdir(parents=True,exist_ok=True)
    selected=sorted(set(disagreements)|{c['card_id'] for c in controls},
                    key=lambda x:hashlib.sha256(('R2:tiebreak:'+x).encode()).hexdigest())
    cards=[];mapping={}
    for ident in selected:
        pub=deepcopy(keys[ident]['public'])
        old=list(pub['options'].values());new=list(old)
        random.Random('R2:tiebreak:'+ident).shuffle(new)
        if len(new)>1 and new==old:
            new=new[1:]+new[:1]
        pub['options']={chr(65+i):v for i,v in enumerate(new)}
        cards.append(pub);mapping[ident]=pub
        files=[pub['word_image'],pub['line_image']]+[v['image'] for v in pub.get('paired_views',[])]
        for filename in files:
            shutil.copyfile(deck/'blind'/filename,blind/filename)
    write(blind/'cards.jsonl',cards)
    shutil.copyfile(deck/'blind/answer_schema.json',blind/'answer_schema.json')
    original=(deck/'blind/README.md').read_text()
    (blind/'README.md').write_text('# Independent tiebreak reading\n\nRead cards.jsonl in its given order. Use only its newly assigned option letters.\nThis batch includes controls. Do not see the earlier readers or their answers.\nThere is no reverse-order assignment for reader 3.\n\n'+original.replace(
        'Use cards.jsonl in order for reader 1 and cards_reverse.jsonl for reader 2.',
        'For this third-reader batch, use cards.jsonl in its given order.'))
    dump(private/'option_mapping.json',mapping)
    dump(private/'control_ids.json',[c['card_id'] for c in controls])
    return mapping,selected


def run(deck,reader1,reader2,out,reader3=None):
    deck=Path(deck);out=Path(out)
    root=Path(os.environ.get('GREEK_OCR_R2C_TEST_OUTPUT_ROOT', Path(__file__).resolve().parents[2]))
    if not out.resolve().is_relative_to(root):
        raise ValueError('R2C output must stay inside this worktree')
    proposed=json.loads((deck/'private/controls_proposed.json').read_text())
    controls=proposed['controls']
    if not controls or not all(c.get('lead_verified') is True for c in controls):
        raise ValueError('lead must pixel-verify every control before readers are used')
    keys={r['card_id']:dict(r,deck=deck.name) for r in read(deck/'private/key.jsonl')}
    public=read(deck/'blind/cards.jsonl');cards={p['card_id']:p for p in public}
    order=[p['card_id'] for p in public]
    batches=[];gates={}
    for name,path,assigned in [('reader1',reader1,order),('reader2',reader2,list(reversed(order)))]:
        answers,gate=batch(path,cards,controls,assigned);gates[name]=gate
        if gate['accepted']:
            batches.append(answers)
    data=[ident for ident in order if not keys[ident]['control']]
    disagreements=[ident for ident in data if len(batches)==2 and
                   (any(ident not in b for b in batches) or
                    signature(batches[0][ident])!=signature(batches[1][ident]))]
    mapping,thirdorder=tiebreak(deck,out,keys,disagreements,controls) if disagreements else ({},[])
    if reader3:
        if not disagreements:
            raise ValueError('no eligible disagreement batch for reader 3')
        answers,gate=batch(reader3,mapping,controls,thirdorder);gates['reader3']=gate
        if gate['accepted']:
            batches.append(answers)
    truth=[]
    for ident in data:
        votes=[a[ident] for a in batches if ident in a]
        truth.append(resolve_card(keys[ident],votes))
    inv=inventory(truth,keys)
    usage=[dict(reader=name,cards=g['answers'],readings=g['answers'],
                tiebreaks=g['answers']-len(controls) if name=='reader3' else 0,
                control_readings=len(controls),accepted=g['accepted'],
                invalid_answers=g['invalid_answer_count'],valid_answers=g['valid_answers'],
                input_tokens=g['input_tokens'] if g['tokens_reported'] else None,
                output_tokens=g['output_tokens'] if g['tokens_reported'] else None) for name,g in gates.items()]
    write(out/'truth.jsonl',truth);dump(out/'controls_gate.json',gates)
    dump(out/'usable_slot_inventory.json',inv);dump(out/'opus_usage.json',usage)
    dump(out/'resolution_receipt.json',dict(data_cards=len(data),controls_excluded=len(controls),
         invalid_answers={name:g['invalid_answers'] for name,g in gates.items()},
         invalid_answer_count=sum(g['invalid_answer_count'] for g in gates.values()),
         disagreements=len(disagreements),resolved=sum(t['status']=='resolved' for t in truth),
         usable_reader_batches=sum(g['accepted'] for g in gates.values()),
         controls_gate_passed=len(batches)>=2,paired_views_count_as_one=True,
         input_sha256={str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in
                       [reader1,reader2,deck/'private/key.jsonl',deck/'private/controls_proposed.json']+([reader3] if reader3 else [])}))
    return truth,gates,inv


def validate_batch(deck,reader,manifest,out):
    """Validation only: no truth, inventory, images or tiebreak deck is emitted.

    The manifest is the exact assigned batch order (including reader 2's
    already-reversed assignment). Partial files remain an assignment error.
    """
    deck=Path(deck);reader=Path(reader);manifest=Path(manifest);out=Path(out)
    root=Path(os.environ.get('GREEK_OCR_R2C_TEST_OUTPUT_ROOT', Path(__file__).resolve().parents[2]))
    forbidden=[root/'docs/records/labelfix/spellcheck/R2/decks',deck,reader.parent,manifest.parent]
    if not out.resolve().is_relative_to(root) or any(out.resolve().is_relative_to(p.resolve()) for p in forbidden):
        raise ValueError('dry-run output must stay in this worktree outside deck and reader folders')
    assigned=read(manifest);cards={a['card_id']:a for a in assigned}
    if len(cards)!=len(assigned):
        raise ValueError('duplicate assigned card ID')
    original={a['card_id']:a for a in read(deck/'blind/cards.jsonl')}
    if any(ident not in original or card!=original[ident] for ident,card in cards.items()):
        raise ValueError('assigned manifest differs from deck cards')
    controls=[c for c in json.loads((deck/'private/controls_proposed.json').read_text())['controls'] if c['card_id'] in cards]
    if not controls or not all(c.get('lead_verified') is True for c in controls):
        raise ValueError('lead must pixel-verify every control before readers are used')
    _,gate=batch(reader,cards,controls,[c['card_id'] for c in assigned])
    dump(out/'controls_gate.json',gate)
    dump(out/'validation_receipt.json',dict(dry_run=True,controls=len(controls),**gate,
         input_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                       [reader,manifest,deck/'private/controls_proposed.json']}))
    dump(out/'opus_usage.json',dict(cards=gate['answers'],invalid_answers=gate['invalid_answer_count'],
         accepted=gate['accepted'],
         input_tokens=gate['input_tokens'] if gate['tokens_reported'] else None,
         output_tokens=gate['output_tokens'] if gate['tokens_reported'] else None))
    return gate


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for arg in ('deck','reader1','out'):
        parser.add_argument('--'+arg,type=Path,required=True)
    parser.add_argument('--reader2',type=Path)
    parser.add_argument('--reader3',type=Path)
    parser.add_argument('--dry-run',action='store_true',help='validate one assigned batch without producing truth or a tiebreak deck')
    parser.add_argument('--manifest',type=Path,help='exact assigned batch cards.jsonl for --dry-run')
    args=parser.parse_args()
    if args.dry_run:
        if args.manifest is None or args.reader2 or args.reader3:
            parser.error('--dry-run requires --manifest and one --reader1 answer file')
        validate_batch(args.deck,args.reader1,args.manifest,args.out)
    else:
        if args.reader2 is None:
            parser.error('--reader2 is required for resolution')
        run(args.deck,args.reader1,args.reader2,args.out,args.reader3)
