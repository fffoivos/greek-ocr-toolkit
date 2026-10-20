"""Bind LQB5 offline verification; no browser or git operations."""
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from greekocr.labelfix.lqb import DEFAULT,ROOT,sha256,dump

def main():
    log=(DEFAULT/'tests_lqb5.txt').read_text();m=re.search(r'(\d+) passed',log)
    assert m and not re.search(r'\d+ (failed|errors?)',log),log[-4000:]
    checks=json.loads((DEFAULT/'validation/checks.json').read_text())
    assert checks['baseline_first'] and checks['decoded_pngs']==checks['cards'] and checks['bytes']<14_000_000
    assert checks['browser_layout'].startswith('not verified')
    receipt=json.loads((DEFAULT/'LQB5_RECEIPT.json').read_text());n=int(m[1])
    p=DEFAULT/'SCORE_v2.md';s=p.read_text().split('\n## Completed LQB5 verification\n')[0]
    s+=f"\n## Completed LQB5 verification\n\n{n} tests passed. All {checks['cards']} embedded native PNGs decoded; baseline precedes headline and begins with measured rows within each class; HTML {checks['bytes']/1e6:.3f} MB. Browser/computer-use tools were not launched; rendered desktop/narrow layout is unverified by instruction.\n"
    p.write_text(s)
    receipt['validation']=dict(tests_passed=n,structural=checks,browser_launched=False)
    for rel in ['scripts/lqb/build_v2_2.py','scripts/lqb/finalize_v2_2.py','scripts/lqb/validate_scoreboard.py','tests/test_lqb.py','tests/test_lqb3.py','tests/test_lqb4.py','tests/test_lqb5.py']:
        receipt['inputs'][str(ROOT/rel)]=sha256(ROOT/rel)
    for rel in ['SCORE_v2.md','tests_lqb5.txt','validation/checks.json']:receipt['outputs'][rel]=sha256(DEFAULT/rel)
    for p,h in receipt['inputs'].items():assert sha256(p)==h,p
    for p,h in receipt['outputs'].items():assert sha256(DEFAULT/p)==h,p
    dump(DEFAULT/'LQB5_RECEIPT.json',receipt)
    t=receipt['truth']
    print(f"LQB5 READY: truth v1.1 {t['items']} sha {t['sha256'][:8]}; headline {receipt['headline']}; baseline measured rows {receipt['baseline_measured_rows']}; scoreboard {checks['bytes']/1e6:.3f} MB; tests {n} passed")

if __name__=='__main__':main()
