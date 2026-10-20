#!/usr/bin/env python3
"""Validate and flag actual SR-G3 pass-1 answers; optionally build blind rereads."""
import argparse, tempfile, shutil
from common_full import *
sys.path.insert(0,str(SR/"tools"))
import scan_rollout

def analyze(key, answers, g1_answers):
    bed=[]
    for iid,m in key.items():
        if m['role']!='bed': continue
        a=answers[iid]
        bed.append(dict(item_id=iid,bed_id=m['bed_id'],context=m['context'],card_id=m['card_id'],line_id=m['line_id'],
                        word_index=m['word_index'],word_labelled=m['word_labelled'],touches_punct=m['touches_punct'],
                        label=m['label_accent'],answer=a['accent'],confidence=a['confidence'],note=a['note'],
                        flagged=a['accent']!=m['label_accent'],g1_id=m['g1_id']))
    flags=[r for r in bed if r['flagged']]; overlap=[]
    for r in bed:
        if r['g1_id']:
            a=g1_answers[r['g1_id']]['accent']
            overlap.append(dict(item_id=r['item_id'],g1_id=r['g1_id'],g1_answer=a,p1_answer=r['answer'],agreement=a==r['answer']))
    return dict(status='complete',items=len(bed),flagged=len(flags),
                flagged_by_answer={a:[r['item_id'] for r in flags if r['answer']==a] for a in ACCENTS},
                flagged_counts_by_answer={a:sum(r['answer']==a for r in flags) for a in ACCENTS},
                sol_grave_share=fraction(sum(r['answer']=='grave' for r in bed),len(bed)),
                label_grave_share=fraction(sum(r['label']=='grave' for r in bed),len(bed)),
                controls=control_report(key,answers),overlap=overlap,
                overlap_agreement=fraction(sum(r['agreement'] for r in overlap),len(overlap)),
                bed=bed,flags=flags)

def markdown(result):
    lines=['# SR-G4 pass 1','',f"Items: {result['items']}; flagged: {result['flagged']}.",
           f"Sol grave share: {frac(result['sol_grave_share']['count'],result['items'])}.",
           f"Label grave share: {frac(result['label_grave_share']['count'],result['items'])}.",
           f"SR-G1 overlap agreement: {frac(result['overlap_agreement']['count'],len(result['overlap']))}.",
           f"Overlap coverage: {len(result['overlap'])}/{result['overlap_expected']} eligible; {len(result['overlap_void'])} VOID.",
           '', 'Control errors flag a context when more than one; bed flags are retained regardless of control performance.',
           '', '| Context | Control passes | Context flagged |','| --- | --- | --- |']
    for name in result['void_contexts']: lines.append(f'| {name} | VOID | Excluded: provenance scan failed |')
    for name,c in result['controls'].items(): lines.append(f"| {name} | {c['passes']}/{c['total']} | {c['flagged']} |")
    lines += ['', 'VOID contexts: '+(', '.join(result['void_contexts']) or 'none')+'.', '', '| Flag answer | Count |','| --- | --- |']
    for a,n in result['flagged_counts_by_answer'].items(): lines.append(f'| {a} | {n} |')
    lines += ['', '| Item | Label | P1 | Confidence | touches_punct |', '| --- | --- | --- | --- | --- |']
    for r in result['flags']: lines.append(f"| {r['item_id']} | {r['label']} | {r['answer']} | {r['confidence']} | {r['touches_punct']} |")
    lines += ['', '| Overlap item | G1 id | G1 | P1 | Agree |','| --- | --- | --- | --- | --- |']
    for r in result['overlap_void']: lines.append(f"| {r['item_id']} | {r['g1_id']} | Excluded | VOID ({r['context']}) | Unscored |")
    for r in result['overlap']: lines.append(f"| {r['item_id']} | {r['g1_id']} | {r['g1_answer']} | {r['p1_answer']} | {r['agreement']} |")
    return '\n'.join(lines)+'\n'

def build_reread(result,key):
    entries=[]; pool=control_pool()
    for r in result['flags']:
        iid=r['item_id']; m=copy.deepcopy(key[iid]); m['p1_id']=iid
        folder=BED/m['context']; p=next(p for p in public_rows(folder) if p['item_id']==iid)
        entries.append((m,p,folder))
    random.Random('sol-grave-full:p2').shuffle(entries)
    # P2 total including controls must fit in 90: 81 + ceil(81/9) = 90.
    chunks=[entries[i:i+81] for i in range(0,len(entries),81)] or [[]]
    newkey={}; receipts=[]
    for j,chunk in enumerate(chunks):
        name='p2' if len(chunks)==1 else ('p2a' if j==0 else 'p2b' if j==1 else f'p2c{j+1}')
        avoid={m['g1_id'] for m in key.values() if m['role']=='control' and m['context'] in {e[0]['context'] for e in chunk}}
        controls=choose_controls(pool,max(2,math.ceil(len(chunk)/9)),f'sol-grave-full:{name}:controls',avoid)
        mixed=chunk+control_entries(controls); random.Random('sol-grave-full:'+name+':mix').shuffle(mixed)
        part,rec=write_context(name,mixed); newkey.update(part); receipts.append(rec)
    dump(ROOT/'keys/p2_key.json',newkey)
    dump(ROOT/'keys/P2_BUILD_RECEIPT.json',dict(contexts=receipts,flags=len(entries),key_sha256=sha(ROOT/'keys/p2_key.json'),
        pass1_sha256=sha(ROOT/'PASS1.json'),avoidance='Prefer controls absent from every contributing pass-1 context; reuse unavoidable when the verified pool lacks an unused member of a required type.'))
    return receipts

def run(build=False,answer_root=None):
    fullkey=load(ROOT/'keys/key.json')
    root=Path(answer_root) if answer_root else SR/'answers/grave_full'
    names=list(dict.fromkeys(m['context'] for m in fullkey.values()))
    expected={n+'.jsonl' for n in names}
    if {p.name for p in root.glob('p1c*.jsonl')}!=expected:raise ValueError('Pass-1 answer file set mismatch')
    scans={n:load(root/(n+'.scan.json')) for n in names}
    valid=[n for n in names if scans[n].get('ok') and scans[n].get('scanner_version')==4]
    void=[n for n in names if n not in valid]
    key={i:m for i,m in fullkey.items() if m['context'] in valid};answers={}
    for name in valid:
        part={i:m for i,m in key.items() if m['context']==name}
        errors,_=scan_rollout.integrity(BED/name)
        if errors:raise ValueError('Pack integrity: '+str(errors))
        # Verify strict original closure separately from permitted reader artifacts.
        with tempfile.TemporaryDirectory(prefix='flag-closure-',dir=scan_rollout.REPLAY_TMP) as tmp:
            folder=Path(tmp);manifest=load(BED/f'MANIFEST.{name}.json')
            for rel in manifest['files']:
                dest=folder/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BED/name/rel,dest)
            closure=g1.scan(folder,part)
            if closure['files']!=manifest['files']:raise ValueError('Original closure mismatch')
        answers.update(validate(g2.load_answers(root/(name+'.jsonl')),part))
    old={a['item_id']:a for a in g2.load_answers(SR/'answers/grave/r1.jsonl')}
    result=analyze(key,answers,old)
    result['contexts']={n:dict(status='OK' if n in valid else 'VOID',violations=scans[n]['violations'],scan_sha256=sha(root/(n+'.scan.json'))) for n in names}
    result['void_contexts']=void
    result['excluded_items']=sum(m['role']=='bed' and m['context'] in void for m in fullkey.values())
    result['overlap_void']=[dict(item_id=i,g1_id=m['g1_id'],context=m['context'],status='VOID',agreement=None) for i,m in fullkey.items() if m['role']=='bed' and m['g1_id'] and m['context'] in void]
    result['overlap_expected']=sum(m['role']=='bed' and bool(m['g1_id']) for m in fullkey.values())
    result['key_sha256']=sha(ROOT/'keys/key.json')
    root=Path(answer_root) if answer_root else SR/'answers/grave_full'
    result['answer_shas']={str(p):sha(p) for p in sorted(root.glob('p1c*.jsonl'))}
    dump(ROOT/'PASS1.json',result); (ROOT/'PASS1.md').write_text(markdown(result))
    if build: build_reread(result,key)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--build-reread',action='store_true'); args=p.parse_args()
    try: r=run(args.build_reread)
    except (OSError,ValueError,KeyError) as e: p.exit(2,f'Invalid/incomplete pass 1: {e}\n')
    print(f"Pass 1: {r['items']} items, {r['flagged']} flags")
if __name__=='__main__': main()
