"""Produce local SR1 evidence and compare pins; no git, cluster or network writes."""
from __future__ import annotations
import json
from pathlib import Path
import runpy
from greekocr.adjudicate._files import dump,sha
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'artifacts/cleanup_sr1'


def main() -> None:
    from greekocr.adjudicate.edit_evidence_crosstab import edit_evidence_crosstab
    from greekocr.adjudicate.release_census import release_census,evidence_dump
    from greekocr.adjudicate.truth_overlay import add,symmetric_rescore
    from greekocr.labelfix.release_gate import policy_binding
    audit=json.loads((OUT/'audit101.json').read_text())
    dump(OUT/'crosstab.json',edit_evidence_crosstab(**audit))
    records=[];selection={}
    for i,tier in enumerate(('agree','other','noink')):
        ident=f'fixture{i}'
        selection[ident]=dict(label='ά',wave='fixture-wave',crop='unused.png')
        records.append(dict(line_id=ident,status='hold',composed_text='ὰ',gate_decisions=[dict(start=0,base='α',r1_parts=['grave'],peer_prediction=dict(parts=['grave']),detector_parts=['grave'] if tier=='agree' else [],evidence=dict(above=[dict(bbox=[0,0,1,1])] if tier!='noink' else [],below=[]),hold_reasons=[])]))
    (OUT/'release_fixture.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in records))
    (OUT/'selection_fixture.jsonl').write_text(''.join(json.dumps(dict(id=k,**v),ensure_ascii=False)+'\n' for k,v in selection.items()))
    dump(OUT/'census_fixture.json',release_census(records,selection,sample_size=1))
    dump(OUT/'single_line_evidence.json',evidence_dump(records,'fixture0'))
    parent=json.loads((OUT/'overlay/truth_overlay_v1.json').read_text())
    expected=json.loads((OUT/'overlay/truth_overlay_v1_1.json').read_text())
    paths=[OUT/'overlay/evidence/tranche6'/n for n in ('answer_r1.json','answer_r2.json','answer_r3.json','letter.png')]
    receipt=add(parent,expected['entries'][0],version='v1.1',expected_parent='v1',evidence_paths=paths)
    assert receipt['overlay']==expected
    # Native R2 scorer is a read-only external instrument, not edited here.
    scorer_path=ROOT.parent/'greek-ocr-toolkit-spellcheck-r2prep/scripts/labelfix/r2_score.py'
    scorer=runpy.run_path(str(scorer_path))['score']
    ident=expected['entries'][0]['id']
    line=dict(line_id=ident.split(':s')[0],doc='fixture',print_slots=[dict(id=ident,base='η',targets=[1,1,0,0],unknown=[])])
    predictions={arm:[dict(line_id=line['line_id'],start=0,base='η',factors=target)] for arm,target in [('A',[1,1,0,0]),('B',[1,3,0,0])]}
    receipt['symmetric_rescore']=symmetric_rescore([line],receipt['overlay'],predictions,scorer)
    receipt['rescore_scope']='One frozen-tuple regression fixture, actual R2 instrument; no population/training claims.'
    receipt['scorer_sha256']=sha(scorer_path)
    dump(OUT/'overlay_reproduction_receipt.json',receipt)
    before=json.loads((OUT/'pinned_before.json').read_text())
    after={p:sha(ROOT/p) if (ROOT/p).is_file() else None for p in before}
    assert before==after,'pinned bytes changed'
    policy=policy_binding()
    assert policy==json.loads((OUT/'policy_before.json').read_text()),'policy binding changed'
    dump(OUT/'pinned_after.json',after);dump(OUT/'policy_after.json',policy)
    (OUT/'pinned_after.sha256').write_text(''.join(f'{s or "MISSING"}  {p}\n' for p,s in after.items()))
    (OUT/'pinned_table.md').write_text('| Pinned path | Before SHA-256 | After SHA-256 | Unchanged |\n|---|---|---|---|\n'+''.join(f'| `{p}` | `{s or "MISSING"}` | `{after[p] or "MISSING"}` | yes |\n' for p,s in after.items()))
    dump(OUT/'pin_receipt.json',dict(unchanged=len(after),total=len(after),present=sum(s is not None for s in after.values()),policy_sources=len(policy['sources']),digest=policy['sha256']))


if __name__=='__main__':main()
