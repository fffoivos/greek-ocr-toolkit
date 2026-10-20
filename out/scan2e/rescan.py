"""Offline SCAN2 rescan; writes only to this output directory."""
import sys,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'docs/harvest/sol_reading/tools'
sys.path.insert(0,str(TOOLS))
import scan_rollout as current
CQ=ROOT.parent/'greek-ocr-toolkit-spellcheck-r2cards/artifacts/cq4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    output_dir=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'out/scan2'
    output_dir.mkdir(parents=True,exist_ok=True)
    scanner_digest=sha(TOOLS/'scan_rollout.py')
    diagnosis=json.loads((CQ/'void_diagnosis.json').read_text())
    protected=[CQ/'initial_ledger.json',CQ/'void_diagnosis.json',*sorted((CQ/'scans').glob('*.json'))]
    before={str(p):sha(p) for p in protected}
    expected=json.loads((ROOT/'out/scan2/cq4_receipts_sha256.json').read_text())
    assert all(sha(Path(p))==digest for p,digest in expected.items())
    entries=[]
    for c in diagnosis['contexts']:
        rollout=Path(c['rollout']);directory=Path(c['directory'])
        assert sha(rollout)==c['scan']['rollout_sha256']
        manifest=directory.parent/f'MANIFEST.{directory.name}.json'
        assert sha(manifest)==c['custody']['expected_sha256']
        baseline=c['scan'] # preserved v4.4 receipt; unchanged canonical hash checked below
        result=current.inspect(rollout,directory)
        assert baseline['violations']==c['scan']['violations'],c['tag']
        (output_dir/(c['tag']+'.v454.scan.json')).write_text(json.dumps(result,indent=2)+'\n')
        entries.append(dict(tag=c['tag'],rollout=str(rollout),rollout_sha256=sha(rollout),reader_dir=str(directory),manifest_sha256=sha(manifest),v44_verdict='VALID' if baseline['ok'] else 'VOID',v44_flags=baseline['violations'],v454_verdict='VALID' if result['ok'] else 'VOID',flags_remaining=result['violations'],image_match_counts=result['image_match_counts']))
        print(c['tag'],entries[-1]['v454_verdict'],len(result['violations']),flush=True)
        output=dict(schema='scan2-rescan-v454',network_used=False,scanner_sha256=scanner_digest,baseline_source='CQ4E preserved v4.4 receipt (read only)',baseline_sha256=sha(CQ/'tools/scan_rollout.py'),original_receipts_unchanged=all(sha(Path(p))==h for p,h in before.items()),contexts=entries,summary=dict(valid=sum(e['v454_verdict']=='VALID' for e in entries),void=sum(e['v454_verdict']=='VOID' for e in entries)))
        (output_dir/'rescan_v454.json').write_text(json.dumps(output,indent=2)+'\n')
    assert output['original_receipts_unchanged']
    assert scanner_digest==sha(TOOLS/'scan_rollout.py')
    assert output['baseline_sha256']=='dd2fc59d6385601146f8cfb3f23ff48aec2e769188f65def282f4b72e489c547'
if __name__=='__main__':main()
