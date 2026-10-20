"""Bind completed LQB3 offline verification into the receipt and SCORE_v2."""
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from greekocr.labelfix.lqb import DEFAULT,sha256,dump


def main():
    log=(DEFAULT/'tests_lqb3.txt').read_text()
    match=re.search(r'(\d+) passed',log)
    assert match and not re.search(r'\d+ (?:failed|errors?)',log),log[-3000:]
    count=int(match.group(1));checks=json.loads((DEFAULT/'validation/checks.json').read_text())
    assert checks['baseline_first'] and checks['decoded_pngs']==checks['cards']==130
    receipt=json.loads((DEFAULT/'LQB3_RECEIPT.json').read_text())
    report=DEFAULT/'SCORE_v2.md';text=report.read_text().split('\n### Completed LQB3 verification\n')[0]
    text+='\n### Completed LQB3 verification\n\n'
    text+=f"**{count} tests passed** ([log](tests_lqb3.txt)); all {checks['decoded_pngs']} embedded PNGs decoded, baseline precedes headline, remote notes disabled, HTML {checks['bytes']/1e6:.3f} MB. "
    text+='Visible desktop/narrow layout remains unverified: offline Chrome and Firefox launch attempts both aborted with SIGABRT before rendering. No browser was downloaded and no network request was authorized.\n'
    text+='\nFinalize the receipt after the test and structural-validation commands: `PYTHONDONTWRITEBYTECODE=1 ../greek-ocr-toolkit-sol-collect/.venv/bin/python -B scripts/lqb/finalize_v2.py`.\n'
    report.write_text(text)
    for p in [ROOT/'scripts/lqb/build_v2.py',ROOT/'scripts/lqb/build_scoreboard.py',ROOT/'scripts/lqb/validate_scoreboard.py',Path(__file__),ROOT/'greekocr/labelfix/lqb.py',ROOT/'tests/test_lqb.py',ROOT/'tests/test_lqb3.py']:
        receipt['inputs'][str(p)]=sha256(p)
    receipt['validation']=dict(tests_passed=count,structural=checks,browser_layout='unverified; Chrome and Firefox SIGABRT before rendering',network=False)
    for name in ['SCORE_v2.md','tests_lqb3.txt','validation/checks.json','validation/browser_lqb3.log','scoreboard_build.json','scoreboard_cards.json']:
        receipt['outputs'][name]=sha256(DEFAULT/name)
    for p,h in receipt['inputs'].items():assert sha256(p)==h,p
    for p,h in receipt['outputs'].items():assert sha256(DEFAULT/p)==h,p
    dump(DEFAULT/'LQB3_RECEIPT.json',receipt)
    print(f"LQB3 READY: baseline rows {receipt['baseline_rows']} (measured {receipt['measured']}, not measured {receipt['not_measured']}); versions {receipt['versions']} (sf6 {receipt['sf6']}, n1_proposal_v1 scored); headline {receipt['headline']}; scoreboard {checks['bytes']/1e6:.3f} MB; tests {count} passed")

if __name__=='__main__':main()
