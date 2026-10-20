"""Verify final offline rescan identities and compare retained v4.5.2 receipts."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    output=ROOT/'out/scan2'
    summary=json.loads((output/'rescan_v454.json').read_text())
    assert len(summary['contexts'])==15
    scanner=ROOT/'docs/harvest/sol_reading/tools/scan_rollout.py'
    assert summary['scanner_sha256']==sha(scanner)
    protected=json.loads((output/'cq4_receipts_sha256.json').read_text())
    assert all(sha(path)==digest for path,digest in protected.items())
    receipts={}
    for entry in summary['contexts']:
        assert sha(entry['rollout'])==entry['rollout_sha256']
        directory=Path(entry['reader_dir'])
        assert sha(directory.parent/('MANIFEST.'+directory.name+'.json'))==entry['manifest_sha256']
        path=output/(entry['tag']+'.v454.scan.json')
        current=json.loads(path.read_text())
        previous=json.loads(path.with_name(entry['tag']+'.v452.scan.json').read_text())
        for field in ('ok','violations','image_matches','image_match_counts','loop_expansions'):
            assert current[field]==previous[field],(entry['tag'],field)
        assert current['scanner_version']=='4.5.4'
        assert current['ok'] and not current['violations']
        receipts[str(path.relative_to(ROOT))]=sha(path)
    report=dict(scanner_sha256=sha(scanner),contexts_verified=15,
        protected_hashes_verified=len(protected),unchanged_fields_vs_v452=[
        'ok','violations','image_matches','image_match_counts','loop_expansions'],
        receipts_sha256=receipts)
    (ROOT/'out/scan2e/verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Verified 15/15 VALID; identical adjudication to v4.5.2;',len(protected),'protected hashes unchanged.')
if __name__=='__main__':main()
