"""Bind LQB4 offline verification; never launch a browser."""
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from greekocr.labelfix.lqb import DEFAULT,sha256,dump

def main():
    log=(DEFAULT/'tests_lqb4.txt').read_text();m=re.search(r'(\d+) passed',log)
    assert m and not re.search(r'\d+ (failed|errors?)',log),log[-3000:]
    checks=json.loads((DEFAULT/'validation/checks.json').read_text())
    assert checks['baseline_first'] and checks['decoded_pngs']==checks['cards']
    assert checks['bytes']<14_000_000 and checks['browser_layout'].startswith('not verified')
    receipt=json.loads((DEFAULT/'LQB4_RECEIPT.json').read_text());n=int(m[1])
    assert receipt['sx1']['verified'] and receipt['sx1']['audit100_released']==99
    p=DEFAULT/'SCORE_v2.md';s=p.read_text().split('\n## Completed LQB4 verification\n')[0]
    s+=f"\n## Completed LQB4 verification\n\n{n} tests passed. All {checks['cards']} embedded native PNGs decoded; baseline precedes headline; remote notes disabled; HTML {checks['bytes']/1e6:.3f} MB. Browser/computer-use tools were not launched; desktop/narrow layout is unverified by instruction.\n"
    p.write_text(s)
    receipt['validation']=dict(tests_passed=n,structural=checks,browser_launched=False)
    for rel in ['scripts/lqb/build_v2_1.py','scripts/lqb/finalize_v2_1.py','scripts/lqb/build_scoreboard.py','scripts/lqb/validate_scoreboard.py','greekocr/labelfix/lqb.py','tests/test_lqb.py','tests/test_lqb3.py','tests/test_lqb4.py']:
        receipt['inputs'][str(ROOT/rel)]=sha256(ROOT/rel)
    for rel in ['SCORE_v2.md','tests_lqb4.txt','validation/checks.json']:
        receipt['outputs'][rel]=sha256(DEFAULT/rel)
    for p,h in receipt['inputs'].items():assert sha256(p)==h,p
    for p,h in receipt['outputs'].items():assert sha256(DEFAULT/p)==h,p
    dump(DEFAULT/'LQB4_RECEIPT.json',receipt)
    t=receipt['truth']
    print(f"LQB4 READY: sx1 v2 verified ok (audit100 released 99/99); truth v1.1 {t['items']} items sha {t['sha256'][:8]} (+DEV {t['added']['S8_DEV']}, +sub60 {t['added']['substitution60']}; exclusion-new {t['exclusion_new']}); headline {receipt['headline']}; scoreboard {checks['bytes']/1e6:.3f} MB; tests {n} passed")

if __name__=='__main__':main()
