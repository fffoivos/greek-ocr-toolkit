"""Offline v4.5.2 rescan; verify preserved identities before and after replay."""
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
    baseline=OUT/'rescan_v451.json'
    baseline_digest=sha(baseline)
    old=json.loads(baseline.read_text())
    protected_path=OUT/'cq4_receipts_sha256.json'
    protected_digest=sha(protected_path)
    protected=json.loads(protected_path.read_text())
    scanner_path=TOOLS/'scan_rollout.py'
    digest=sha(scanner_path)
    assert scanner.VERSION=='4.5.2'
    assert digest in (ROOT/'docs/harvest/sol_reading/HANDOVER.md').read_text()
    assert len(old['contexts'])==15
    def verify():
        assert sha(baseline)==baseline_digest
        assert sha(protected_path)==protected_digest
        assert sha(scanner_path)==digest
        for path,expected in protected.items():assert sha(Path(path))==expected,path
        for previous in old['contexts']:
            rollout=Path(previous['rollout']);directory=Path(previous['reader_dir'])
            assert sha(rollout)==previous['rollout_sha256']
            assert sha(directory.parent/f'MANIFEST.{directory.name}.json')==previous['manifest_sha256']
    verify()
    def inspect_context(previous):
        return scanner.inspect(Path(previous['rollout']),Path(previous['reader_dir']))
    with ThreadPoolExecutor(max_workers=3) as pool:
        results=list(pool.map(inspect_context,old['contexts']))
    verify()
    entries=[]
    for previous,result in zip(old['contexts'],results):
        receipt=OUT/(previous['tag']+'.v452.scan.json')
        receipt.write_text(json.dumps(result,indent=2)+'\n')
        prior_result=json.loads((OUT/(previous['tag']+'.v451.scan.json')).read_text())
        verdict='VALID' if result['ok'] else 'VOID'
        entries.append(dict(previous,v452_verdict=verdict,
            verdict_changed=verdict!=previous['v451_verdict'],
            flags_remaining=result['violations'],image_match_counts=result['image_match_counts'],
            image_match_counts_changed=result['image_match_counts']!=prior_result['image_match_counts'],
            receipt=str(receipt.relative_to(ROOT)),receipt_sha256=sha(receipt)))
        print(previous['tag'],verdict,len(result['violations']),flush=True)
    output=dict(schema='scan2-rescan-v452',network_used=False,scanner_sha256=digest,
        baseline_source=str(baseline.relative_to(ROOT)),baseline_sha256=baseline_digest,
        original_receipts_unchanged=True,contexts=entries,
        summary=dict(valid=sum(e['v452_verdict']=='VALID' for e in entries),
            void=sum(e['v452_verdict']=='VOID' for e in entries),
            verdict_changes=[e['tag'] for e in entries if e['verdict_changed']],
            image_match_count_changes=[e['tag'] for e in entries if e['image_match_counts_changed']]))
    (OUT/'rescan_v452.json').write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output['summary']),flush=True)
if __name__=='__main__':main()
