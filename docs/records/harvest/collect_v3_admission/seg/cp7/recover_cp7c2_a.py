"""Recover A's receipt from logged evidence only. Never launch or reread a card."""
import argparse
import sys
import runtime_r2 as r2
import runtime
from r2_common import BASE, R2, SCANNER, read, sha, dump


def recover(dry_run=False):
    log=(BASE/'run_r2.log').read_text().splitlines()
    runs=[r2.json.loads(line) for line in log if line.startswith('{"label":')]
    run,=[r for r in runs if r['label']=='SEG-CP7-segcp7r2_a-r1']
    before,=[line for line in log if ' before:segcp7r2_a/r1 ' in line]
    after,=[line for line in log if ' after:segcp7r2_a/r1 ' in line]
    assert run['rc']==0 and run['model']=='gpt-6.1-sol'
    assert r2.json.dumps(dict(mapped=50,controls=5,scored=False)) in log
    assert sha(BASE/'tools/scan_rollout.py')==SCANNER
    scan=read(R2/'scan/segcp7r2_a/r1.scan.json')
    assert scan['ok'] is True and scan['violations']==[]
    assert scan['manifest_check_skipped'] is False
    assert scan['rollout']==run['rollout'] and sha(scan['rollout'])==scan['rollout_sha256']
    assert scan['total_token_usage']==run['usage'] and scan['tool_calls']==sum(run['tool_calls'].values())
    assert len(r2.rows(R2/'answers/segcp7r2_a/r1.mapped.jsonl'))==50
    assert len(r2.rows(R2/'answers/segcp7r2_a/r1.controls.jsonl'))==5
    assert sha(R2/'answers/segcp7r2_a/r1.jsonl')==sha(r2.PACK_ROOT/'segcp7r2_a/r1/answers.jsonl')
    captured=[]
    original_dump=runtime.dump
    original_argv=sys.argv
    try:
        runtime.dump=lambda path,value: captured.append((path,value))
        sys.argv=['runtime_r2.py','receipt','segcp7r2_a',r2.json.dumps(run),before,after,'0','0']
        r2.main()
    finally:
        runtime.dump=original_dump
        sys.argv=original_argv
    (path,receipt),=captured
    assert receipt['status']=='scan clean and mapped; adjudication pending'
    if not dry_run:
        dump(path,receipt)
        assert read(path)==receipt
    print(r2.json.dumps(dict(context='segcp7r2_a/r1',scan_ok=True,reader_rc=0,
        mapped=50,controls=5,dry_run=dry_run,receipt_written=not dry_run,
        receipt_sha256=None if dry_run else sha(path))))
    return receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run',action='store_true')
    recover(parser.parse_args().dry_run)
