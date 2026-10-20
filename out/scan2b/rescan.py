"""Offline v4.5.1 rescan; preserved v4.5 receipts and CQ4 inputs stay read-only."""
import hashlib,json,sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'docs/harvest/sol_reading/tools'
sys.path.insert(0,str(TOOLS))
import scan_rollout as scanner
OUT=ROOT/'out/scan2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    baseline=OUT/'rescan_v45.json'
    old=json.loads(baseline.read_text())
    protected=json.loads((OUT/'cq4_receipts_sha256.json').read_text())
    digest=sha(TOOLS/'scan_rollout.py')
    entries=[]
    def inspect_context(previous):
        return scanner.inspect(Path(previous['rollout']),Path(previous['reader_dir']))
    # Separate fresh replay roots per inspect; at most three concurrent scans.
    with ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(inspect_context,old['contexts']))
    for previous,result in zip(old['contexts'],results):
        rollout=Path(previous['rollout']);directory=Path(previous['reader_dir'])
        assert sha(rollout)==previous['rollout_sha256']
        assert sha(directory.parent/f'MANIFEST.{directory.name}.json')==previous['manifest_sha256']
        (OUT/(previous['tag']+'.v451.scan.json')).write_text(json.dumps(result,indent=2)+'\n')
        verdict='VALID' if result['ok'] else 'VOID'
        entries.append(dict(previous,v451_verdict=verdict,verdict_changed=verdict!=previous['v45_verdict'],
            flags_remaining=result['violations'],image_match_counts=result['image_match_counts']))
        print(previous['tag'],verdict,len(result['violations']),flush=True)
    assert digest==sha(TOOLS/'scan_rollout.py')
    # Preserve the exact protected-receipt manifest and verify each original file.
    assert protected==json.loads((OUT/'cq4_receipts_sha256.json').read_text())
    for path,expected in protected.items():assert sha(Path(path))==expected,path
    output=dict(schema='scan2-rescan-v451',network_used=False,scanner_sha256=digest,
        baseline_source=str(baseline.relative_to(ROOT)),baseline_sha256=sha(baseline),
        original_receipts_unchanged=True,contexts=entries,
        summary=dict(valid=sum(e['v451_verdict']=='VALID' for e in entries),
            void=sum(e['v451_verdict']=='VOID' for e in entries),
            verdict_changes=[e['tag'] for e in entries if e['verdict_changed']]))
    (OUT/'rescan_v451.json').write_text(json.dumps(output,indent=2)+'\n')
if __name__=='__main__':main()
