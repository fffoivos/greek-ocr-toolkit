"""CLI for the literal same-class/source replacement hook. JSONL inputs."""
import argparse
from lf1 import rows, jsonl, replace_flagged, dump, sha

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--flagged',required=True,help='JSONL rows with line_id, in requested replacement order')
    p.add_argument('--selected',required=True,help='drawn JSONL: line_id, class, source')
    p.add_argument('--overdraw',required=True,help='ordered JSONL overdraw, same schema')
    p.add_argument('--used',help='optional JSONL already consumed replacements with line_id')
    p.add_argument('--output',required=True)
    a=p.parse_args()
    records=replace_flagged([r['line_id'] for r in rows(a.flagged)],rows(a.selected),rows(a.overdraw),
                            [r['line_id'] for r in rows(a.used)] if a.used else ())
    jsonl(a.output,records)
    dump(a.output+'.receipt.json',dict(inputs={f:sha(f) for f in (a.flagged,a.selected,a.overdraw,a.used) if f},
         output_sha256=sha(a.output),replacements=records))

if __name__=='__main__':main()
