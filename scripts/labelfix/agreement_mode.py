"""Score saved runtime decisions through the SF2 gate; no inference.

The old component/proxy arithmetic is agreement_mode_historical.py. This command
requires detector, coverage and R1 predictions, exactly as M2 and L1r do.
"""
import argparse
from collections import Counter
from greekocr.labelfix.release_gate import compose_runtime, decide, MODES
from scripts.labelfix.clariden.r1_common import rows


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('runtime');ap.add_argument('--mode',choices=MODES,default='PRESENCE')
    ap.add_argument('--flags',help='JSONL line id and constraint_flags')
    a=ap.parse_args();flags={}
    if a.flags:
        flags={r.get('line_id',r.get('id')):r['constraint_flags'] for r in rows(a.flags)}
    counts=Counter()
    for r in rows(a.runtime):
        if r.get('status','ok')!='ok':continue
        out=compose_runtime(r,a.mode,flags.get(r['id'],()))
        counts.update(s['label_status'] for s in out['slots'])
        counts['lines_with_HOLD']+=bool(out['hold_slots'])
    print(dict(counts))


if __name__=='__main__':main()
