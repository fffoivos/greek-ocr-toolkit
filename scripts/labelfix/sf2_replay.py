"""Offline SF2 measurements in a new scratch directory; saved R1 only."""
from greekocr.ops.data_root import input_path as _data_input
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import json
from pathlib import Path
import socket
import subprocess
import sys
from PIL import Image
from greekocr.labelfix.release_gate import compose_runtime,policy_binding
from scripts.labelfix.m2_run import rows,write_rows,sha


def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')


def m2(out):
    from scripts.labelfix import m2_score as score
    out.mkdir()
    runs=rows('.cache/labelfix/m2/runtime.jsonl')
    for r in runs:
        if r['status']!='ok':continue
        r['modes']={m:compose_runtime(r,m) for m in ('PRESENCE','FULL')}
    write_rows(out/'runtime.jsonl',runs)
    inv=score.inventory();runtime={r['id']:r for r in runs};by={r['id']:r for r in inv}
    ledger=score.pair_ledger(inv)
    scored=[score.score_case(c,by[c['id']],runtime[c['id']]) for c in ledger if c['included']]
    lines=[]
    for r in inv:
        run=runtime[r['id']];changes,coverage=score.changes_for(r,run)
        lines.append(dict(**r,**{k:v for k,v in run.items() if k!='id'},changes=changes,
                          reference_change_alignment_coverage=coverage))
    metrics=score.summarize(inv,runtime,scored,lines)
    dump(out/'metrics.json',metrics);write_rows(out/'pairs.jsonl',scored);write_rows(out/'lines.jsonl.gz',lines)
    dump(out/'receipt.json',dict(policy=policy_binding(),network=False,ctc_runs=0,r1_runs=0,detector_runs=0,
        inputs={p:sha(p) for p in ['.cache/labelfix/m2/runtime.jsonl','docs/records/labelfix/spellcheck/M2_metrics.json']},
        outputs={p.name:sha(p) for p in out.iterdir() if p.is_file()}))
    return metrics['POOLED']


def owners(out):
    from scripts.labelfix import owner_reading as owner,owner_pages_build_combined as builder
    from scripts.labelfix.clariden.r1_extract import extract_line
    from greekocr.labelfix.sheet import load_alignments,crop_key
    from greekocr.labelfix.ctc_align import transfer_alignment
    from greekocr.labelfix.validate import load_three_way
    out.mkdir()
    old=Path('docs/records/labelfix/spellcheck/CN1_evidence')
    ids=rows(old/'owner_lines.jsonl');wanted={r['line_id'] for r in ids}
    write_rows(out/'owner_lines.jsonl',ids)
    lines={r['line_id']:r for r in load_three_way(0) if r['line_id'] in wanted}
    aligns=load_alignments(Path('.cache/labelfix/align_s0.jsonl'))
    coverage=[]
    for lid,line in lines.items():
        al=aligns[crop_key(line['crop'])]
        al=transfer_alignment(line['model'],al)
        with Image.open(line['crop']) as im:
            _,_,_,_,cov,_=extract_line(dict(_line=0,recogniser_text=line['model']),al.to_record(),im,evaluation=True)
        coverage.append(dict(line_id=lid,coverage=cov))
    assert len(coverage)==len(wanted)
    write_rows(out/'coverage.jsonl',coverage)
    cfg=json.loads((old/'combined_config.json').read_text())
    cfg.update(detector_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        source_sha256={p:owner.digest(p) for p in owner.SOURCES},constraint_policy=owner.policy(),
        r1_coverage={str(out/'coverage.jsonl'):sha(out/'coverage.jsonl')})
    # Use equivalent local cached predictions rather than reading another worktree.
    cfg['r1_predictions']={str(Path('artifacts/labelfix_r1/output_3678928/A')/Path(p).name):h for p,h in cfg['r1_predictions'].items()}
    cfg['r1_checkpoint']['path']='artifacts/labelfix_r1/output_3678928/A/best.pt'
    dump(out/'combined_config.json',cfg)
    ctl=deepcopy(cfg);ctl.update(r1_checkpoint=None,r1_predictions={},r1_coverage={});dump(out/'s6_config.json',ctl)
    for combined in (False,True):
        name='combined' if combined else 's6_control';cp=out/('combined_config.json' if combined else 's6_config.json')
        sys.argv=['owner_pages_build_combined','--lines',str(out/'owner_lines.jsonl'),'--out',str(out/(name+'.html')),
            '--boxes-out',str(out/(name+'_boxes.json')),'--reading-config',str(cp)]
        if combined:sys.argv+=['--r1',*cfg['r1_predictions'],'--r1-coverage',str(out/'coverage.jsonl')]
        builder.R1.clear();builder.COVERAGE.clear();builder.main()
    from scripts.labelfix import cn1_measure
    sys.argv=['cn1_measure','--evidence-dir',str(out)];cn1_measure.main()
    from scripts.labelfix.box_regression import compare_pages
    new=json.loads((out/'combined_boxes.json').read_text())['lines']
    oldboxes=json.loads((old/'saved_s6_boxes.json').read_text())['lines']
    for label,baseline in [('saved_s6',oldboxes),('s6_page',json.loads((_data_input(old/'s6_control_boxes.json')).read_text())['lines'])]:
        diff=compare_pages(baseline,new,.3)
        dump(out/f'box_regression_{label}.json',dict(summary={k:sum(len(v[k]) for v in diff.values()) for k in
            ('lost','added','moved','owner_changed','pixels_changed','status_changed','pixels_unknown','owner_unknown','status_unknown')},lines=diff))
    dump(out/'build_receipt.json',dict(policy=policy_binding(),network=False,ctc_runs=0,r1_runs=0,
        detector_lines=2*len(ids),coverage_recomputed_lines=len(coverage),
        outputs={p.name:sha(p) for p in out.iterdir() if p.is_file()}))


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    def forbidden(*args,**kwargs):raise RuntimeError('SF2 forbids network/model execution')
    socket.socket.connect=forbidden;socket.create_connection=forbidden
    from greekocr.labelfix.ctc_align import Recognizer
    from scripts.labelfix.clariden.r1_model import MarkReader
    Recognizer.__init__=forbidden;MarkReader.forward=forbidden
    print(json.dumps(m2(a.out/'m2'),ensure_ascii=False,indent=2),flush=True)
    owners(a.out/'owner')


if __name__=='__main__':main()
