"""B6 postprocessing of unchanged R2C2 outputs; offline, no git operations.
Run after all 32 CLI dry-runs and ID-joined resolver runs (see report).
"""
import sys,json,hashlib,shutil,collections
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from scripts.labelfix import r2_cards_resolve as R
SRC=Path('/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/b1155dbd-56e0-4e2f-8bf5-349babd21b48/scratchpad')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def inventory(rows,keys,pending=False):
    groups=collections.defaultdict(lambda:dict(cards=set(),slots=set(),unknown=set(),known_heads={h:set() for h in R.HEADS}))
    for row in rows:
        k=keys[row['card_id']]; ident=k['card_id']; role='T2 supervision' if k['deck']=='T2' else 'T4 witness'
        labels=[('role',role),('target_head',k['target_head']),('slice',k.get('slice','untagged')),('subtype',k.get('subtype','untagged'))]
        # Only explicit tags are admitted. Fine-grained requested slices are not inferred from OCR text.
        tag={'capitals':'capital/ALL-CAPS/numeral (pooled tag)','omicron_monotonic':'ο/οι monotonic (pooled tag)'}.get(k.get('slice'))
        if k.get('subtype')=='crasis': tag='crasis'
        labels.append(('hallucination_tag',tag or 'untagged'))
        anchor=(k['crop_sha256'],k['crop_letter_offset']+k['anchor_index'])
        for dim,label in labels:
            g=groups[(dim,label)];g['cards'].add(ident)
            if pending:
                g['slots'].add(anchor);continue
            if row['printed_form'] is None or not row['letter_heads']:
                g['unknown'].add(anchor)
            ownership_na=row['ownership_ok'] is None and any(r['index']==row['anchor_index'] and R.unmarked(r) for r in row['letter_heads'])
            for r in row['letter_heads']:
                slot=(k['crop_sha256'],k['crop_letter_offset']+r['index'])
                eligible=row['ownership_ok'] is True or ownership_na
                for h in R.HEADS:
                    if eligible and r[h]!='unknown':g['known_heads'][h].add(slot)
                if eligible and all(r[h]!='unknown' for h in R.HEADS):g['slots'].add(slot)
                else:g['unknown'].add(slot)
    return {dim+':'+label:dict(cards=len(g['cards']),**({'pending_unique_anchor_slots':len(g['slots'])} if pending else dict(usable_complete_slots=len(g['slots']),unknown_slots=len(g['unknown']),known_head_slots={h:len(v) for h,v in g['known_heads'].items()}))) for (dim,label),g in sorted(groups.items())}

summaries={}
for t in ['T2','T4']:
    out=ROOT/'artifacts/r2_resolve'/t;deck=ROOT/'docs/labelfix/spellcheck/R2/decks'/t
    keys={k['card_id']:dict(k,deck=t) for k in R.read(deck/'private/key.jsonl')}
    controls=json.loads((deck/'private/controls_proposed.json').read_text())['controls'];controlids={c['card_id'] for c in controls}
    batchgates={f'{r}/b{i:02}':json.loads((out/'batch_gates'/r/f'b{i:02}'/'validation_receipt.json').read_text()) for r in ['r1','r2'] for i in range(8)}
    assert all(g['accepted'] for g in batchgates.values()),'Failing batches require explicit handling; no silent drop'
    original=R.read(deck/'blind/cards.jsonl');cards={x['card_id']:x for x in original}
    readers=[R.batch(out/'inputs'/f'r{i}.jsonl',cards,controls,[x['card_id'] for x in (original if i==1 else original[::-1])])[0] for i in [1,2]]
    tb=R.read(out/'tiebreak/blind/cards.jsonl') if (out/'tiebreak/blind/cards.jsonl').exists() else []
    pending={c['card_id'] for c in tb}-controlids
    expected={ident for ident,k in keys.items() if not k['control'] and (any(ident not in r for r in readers) or R.signature(readers[0][ident])!=R.signature(readers[1][ident]))}
    assert pending==expected
    truth=R.read(out/'truth.jsonl')
    resolved=[r for r in truth if r['card_id'] not in pending and r['status']=='resolved']
    unknown=[r for r in truth if r['card_id'] not in pending and r['status']!='resolved']
    R.write(out/'resolved.jsonl',resolved);R.write(out/'unknown_agreements.jsonl',unknown)
    R.write(out/'pending_tiebreak.jsonl',[dict(card_id=i,reason='invalid_vote' if any(i not in r for r in readers) else 'disagreement',reader_valid=[i in r for r in readers]) for i in sorted(pending)])
    assert len(resolved)+len(unknown)+len(pending)==800
    R.dump(out/'gate.json',dict(per_batch=batchgates,all_batches_passed=True,aggregate=json.loads((out/'controls_gate.json').read_text()),unscored_control_ids=[i for i,k in keys.items() if k['control'] and i not in controlids]))
    inv=dict(resolved_now=inventory(resolved,keys),pending_tiebreak=inventory([dict(card_id=i) for i in pending],keys,True),unknown_agreements=inventory(unknown,keys),pending_is_potential_not_usable=True)
    R.dump(out/'b6_usable_slot_inventory.json',inv)
    # All quality classifications retain source answers; no new truth is introduced.
    raw=[{a['card_id']:a for a in R.read(out/'inputs'/f'r{i}.jsonl')} for i in [1,2]]
    low=[]
    for ident,k in keys.items():
        a=[r[ident] for r in raw]
        if all(x['readability']=='unreadable' or x['confidence']=='low' for x in a):
            low.append(dict(card_id=ident,control=k['control'],both_unreadable=all(x['readability']=='unreadable' for x in a),both_low_confidence=all(x['confidence']=='low' for x in a),answers=a))
    mono=[dict(card_id=c['card_id'],form=c['expected_form'],script_class=keys[c['card_id']]['script_class']) for c in controls if keys[c['card_id']]['script_class']=='greek_mono']
    no_poly=[dict(card_id=c['card_id'],form=c['expected_form']) for c in controls if all(h['breathing']=='none' and h['subscript']=='none' and h['accent'] in ('none','acute') for h in c['expected_letter_heads'])]
    candidates=json.loads((out/'base_letter_candidates.json').read_text())
    for c in candidates:
        forms=[a['form'] for a in c['readings']]
        c['both_same_alternative_base']=forms[0] is not None and forms[1] is not None and R.letters(forms[0])==R.letters(forms[1])
    R.dump(out/'card_quality.json',dict(base_letter_candidates=candidates,base_letter_candidate_count=len(candidates),both_same_alternative_base=sum(c['both_same_alternative_base'] for c in candidates),monotonic_source_controls=mono,monotonic_compatible_form_controls=no_poly,both_unreadable_or_low=low))
    folders=[]
    if pending:
        n=(len(tb)+99)//100
        for j in range(n):
            assigned=tb[j::n];p=SRC/f'r2read_{t}_r3'/f'b{j:02}'
            p.mkdir(parents=True,exist_ok=False);(p/'img').mkdir()
            R.write(p/'cards.jsonl',assigned)
            shutil.copyfile(out/'tiebreak/blind/answer_schema.json',p/'answer_schema.json')
            readme=(out/'tiebreak/blind/README.md').read_text()
            readme='# Isolated offline reading assignment\n\nWork ONLY in this folder. Open only README.md, answer_schema.json, cards.jsonl, and named PNGs under img/. Do not list or read parents, siblings, private material or earlier answers. No network or web search. Read cards.jsonl in its given order. Write only answers.jsonl; temporary enlargements may go in zoom/ inside this folder. Use img/<image name> for card image fields. Never infer marks from grammar. Give unknown for undecided heads, and ownership_ok null for an unmarked anchor. Usage zeros are placeholders.\n\n'+readme
            (p/'README.md').write_text(readme);(p/'answers.jsonl').write_text('')
            images={f for c in assigned for f in [c['word_image'],c['line_image']]+[v['image'] for v in c.get('paired_views',[])]}
            for f in images:
                assert Path(f).name==f and f.endswith('.png')
                shutil.copyfile(out/'tiebreak/blind'/f,p/'img'/f)
            findings=[];files=sorted(x for x in p.rglob('*') if x.is_file())
            assert all(not x.is_symlink() for x in p.rglob('*'))
            assert {x.name for x in p.iterdir()}=={'cards.jsonl','img','README.md','answer_schema.json','answers.jsonl'}
            allowed={'card_id','word_image','line_image','anchor_index','anchor_base','options','extra_options','paired_views','witness_group'}
            for c in assigned:
                assert set(c)<=allowed
                assert c['options']!=keys[c['card_id']]['public']['options'] or len(c['options'])<=1
            needles=['geometry_response','mining_key','expected_form','expected_letter_heads','crop_sha256','Google','google','/Users/','../','file://','http://','https://']
            needles += [k[f] for k in keys.values() for f in ['crop','line_id','doc','source']]
            for f in files:
                if f.suffix=='.png':
                    assert sha(f)==f.stem
                    with Image.open(f) as im:
                        if im.info:findings.append(dict(file=str(f.relative_to(p)),reason='PNG metadata'))
                else:
                    txt=f.read_text()
                    for needle in set(needles):
                        if needle and needle in txt:findings.append(dict(file=f.name,reason='private text/path',needle=needle))
            assert not findings,findings
            assert len(assigned)<=100 and len({c['card_id'] for c in assigned})==len(assigned)
            folders.append(dict(folder=str(p),cards=len(assigned),data_cards=sum(c['card_id'] in pending for c in assigned),controls=sum(c['card_id'] in controlids for c in assigned),card_ids=[c['card_id'] for c in assigned],hashes={str(f.relative_to(p)):sha(f) for f in files},leak_scan=dict(passed=True,findings=findings,scope='All files recursively: allowlist, no symlinks, local-only image references, PNG content hashes and metadata, private identifiers/text. Reader file allowlist is required; this is not an OS access sandbox. Printed image content is retained.')))
    dealt=[i for f in folders for i in f['card_ids']];assert len(dealt)==len(set(dealt))==len(tb)
    assert set(dealt)=={c['card_id'] for c in tb}
    R.dump(out/'r3_deal_receipt.json',dict(folders=folders,full_resolver_manifest_sha256=sha(out/'tiebreak/blind/cards.jsonl') if tb else None,private_map=str(out/'tiebreak/private/option_mapping.json'),private_map_outside_reader_folders=True,reader3_answers_empty=True,model_requested='gpt-6.1-sol',reasoning_effort_requested='medium',network='OFF; no reader launched',max_cards_per_context=100))
    s=dict(resolved=len(resolved),agreement_unknown=len(unknown),tiebreak=len(pending),folders=len(folders),controls_flagged=80,controls_scored=len(controls),raw_resolver_resolved=sum(x['status']=='resolved' for x in truth),quality=dict(base_candidates=len(candidates),concordant_base=sum(c['both_same_alternative_base'] for c in candidates),mono_controls=len(mono),mono_compatible=len(no_poly),both_low_or_unreadable=len(low),both_unreadable=sum(x['both_unreadable'] for x in low),both_low=sum(x['both_low_confidence'] for x in low)))
    summaries[t]=s;print(t,s)
R.dump(ROOT/'artifacts/r2_resolve/b6_summary.json',summaries)
