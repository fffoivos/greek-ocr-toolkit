"""Strict owner-note replay on saved S4/S5/S6 snapshots, with explicit note versions."""
from pathlib import Path
from collections import Counter
import hashlib
import json
from scripts.labelfix.s6_notes import clause,current_review_specs
from scripts.labelfix.s5_notes import specs
from scripts.labelfix.s5_validate import read,write

O=Path('docs/labelfix/spellcheck')

def category(kind):
    if kind in ('fusion','base','split_union','union_base','word_slots'):return 'segmentation'
    if kind=='no_regression':return 'complete_note'
    if kind in ('named','whole_marks'):return 'naming'
    return 'physical'

def main():
    versions={k:{l['line_id']:l for l in read(O/f'{k}_lines.jsonl.gz')} for k in ('S4','S5','S6')}
    summary={};records=[];lookup=specs();lookup['8b6b0de9-p000021-l0012']=[('no_top',1,None)]
    for file,sp in [('owner_notes_review_v16_20261016.jsonl',current_review_specs()),('owner_notes_examples_v10_20261016.jsonl',lookup)]:
        checks=[]
        for note in read(O/file):
            lid=note['line_id'];cs=sp.get(lid) if note['note'] else [('no_regression',None,None)]
            row=dict(note,note_set=file,reviewed_snapshot='S4_lines.jsonl.gz',versions={})
            for name,by in versions.items():
                out=[]
                for kind,target,value in cs or [('uncertain',None,None)]:
                    ok,ev=clause(by.get(lid),versions['S4'].get(lid),kind,target,value)
                    out.append(dict(kind=kind,target=target,value=value,category=category(kind),fixed=bool(ok),evidence=ev))
                row['versions'][name]=dict(fixed=all(c['fixed'] for c in out),clauses=out)
            checks.append(row)
        summary[file]={name:dict(fixed=sum(r['versions'][name]['fixed'] for r in checks),n=len(checks),
            dimensions={cat:dict(fixed=sum(c['fixed'] for r in checks for c in r['versions'][name]['clauses'] if c['category']==cat),n=sum(c['category']==cat for r in checks for c in r['versions'][name]['clauses'])) for cat in ('physical','naming','segmentation','complete_note')}) for name in versions}
        records.extend(checks)
    result=dict(schema='sf1-owner-notes-v1',summary=summary,source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [O/f'{k}_lines.jsonl.gz' for k in versions]+[O/f for f in summary]+[Path('scripts/labelfix/s6_notes.py'),Path(__file__)]})
    (O/'SF1_owner_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    write(O/'SF1_owner_checks.jsonl',records)
    print({file:{k:f"{v['fixed']}/{v['n']}" for k,v in counts.items()} for file,counts in summary.items()})

if __name__=='__main__':main()
