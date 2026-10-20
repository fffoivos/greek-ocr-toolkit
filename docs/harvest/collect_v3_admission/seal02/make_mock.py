#!/usr/bin/env python3
"""Explicit MOCK final-list generator for local tests only; no image operations."""
import argparse
from pathlib import Path
from build_suite02 import rows,sha,jsonl,dump

def make(candidates, output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    cs=rows(candidates)
    jsonl(output/'verdicts.MOCK.jsonl',[dict(line_id=r['row_id'],verdict='OK',mock=True,context='MOCK_NO_READER') for r in cs])
    verdict_sha=sha(output/'verdicts.MOCK.jsonl')
    jsonl(output/'final_list.MOCK.jsonl',[dict(parent_id=r['parent_id'],row_id=r['row_id'],split=r['split'],quota_scope=r['quota_scope'],lf1_verdict='OK',replaces=None,lf1_receipt_ref=dict(verdicts_sha256=verdict_sha,line_id=r['row_id']),mock=True) for r in cs if r['in_quota']])
    dump(output/'final_receipt.MOCK.json',dict(status='FINALIZED',mock=True,final_list_sha256=sha(output/'final_list.MOCK.jsonl'),verdicts_sha256=verdict_sha,candidates_sha256=sha(candidates),counts=dict(flagged=0,REPLACED=0,UNFILLED=0)))
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidates',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();make(a.candidates,a.output)
