"""Offline SR1 tools. Run with PYTHONPATH=$PWD python scripts/review/sr1.py --help.

All commands consume staged local JSON/JSONL; no live artifact-db or cluster IO.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from greekocr.adjudicate._files import rows, dump


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    for name in ('page','crosstab','census','controls','deck','deal','notes','custody','truth-overlay','batch-check'):
        p = sub.add_parser(name)
        p.add_argument('--spec',type=Path,required=True)
        p.add_argument('--output',type=Path,required=True)
        if name=='truth-overlay':
            p.add_argument('action',choices=['add'])
        if name=='batch-check':
            p.add_argument('--batch-check',action='store_true',required=True,help='validation dry run, never write truth')
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text())
    if args.output.exists():
        raise FileExistsError(args.output)
    command = args.command
    if command=='page':
        from greekocr.adjudicate.page_specs import render_spec
        args.output.write_text(render_spec(spec['path']))
        return
    if command=='crosstab':
        from greekocr.adjudicate.edit_evidence_crosstab import edit_evidence_crosstab
        result = edit_evidence_crosstab(spec['records'],spec['verdicts'])
    elif command=='census':
        from greekocr.adjudicate.release_census import release_census, evidence_dump
        result = evidence_dump(rows(spec['release']),spec['line_id']) if 'line_id' in spec else release_census(rows(spec['release']),{r['id']:r for r in rows(spec['selection'])},seed=spec.get('seed',20261017),sample_size=spec.get('sample_size',20))
    elif command=='controls':
        from greekocr.adjudicate.controls_review_sheets import controls_review_sheets
        result = controls_review_sheets(spec['controls'],args.output,per_sheet=spec.get('per_sheet',12))
        dump(args.output/'receipt.json',result); return
    elif command=='deck':
        from greekocr.adjudicate.deck import build_deck
        spec['blind_dir'] = str(args.output)
        build_deck(spec); return
    elif command=='deal':
        from greekocr.adjudicate.deal_batches import deal_batches
        deal_batches(spec['deck'],args.output,batch_size=spec.get('batch_size',110)); return
    elif command=='notes':
        from greekocr.adjudicate.owner_notes_export import owner_notes_export
        owner_notes_export(spec['documents'],spec['cards'],spec['sheets'],args.output); return
    elif command=='custody':
        from greekocr.adjudicate.artifact_custody import copy_artifacts
        copy_artifacts(spec['source'],args.output,spec['paths']); return
    elif command=='truth-overlay':
        from greekocr.adjudicate.truth_overlay import add, symmetric_rescore
        result = add(spec['parent'],spec['entry'],version=spec['version'],evidence_paths=spec['evidence_paths'],expected_parent=spec['expected_parent'])
        if 'rescore' in spec:
            # Staged R2 instrument supplied locally; no invocation of inference.
            import runpy
            r = spec['rescore']
            score = runpy.run_path(r['scorer_path'])['score']
            result['symmetric_rescore'] = symmetric_rescore(r['lines'],result['overlay'],r['predictions'],score)
    else:
        from greekocr.adjudicate.batch_check import batch_check
        result = batch_check(spec['folder'],spec['assignment'],spec['answers'],spec['keys'],adapter=spec.get('adapter','canonical'),gate_spec=spec.get('gate_spec'))
    dump(args.output,result)
    if command=='batch-check' and result['status']!='BATCH_CHECK_PASSED':
        raise SystemExit(1)


if __name__=='__main__':
    main()
