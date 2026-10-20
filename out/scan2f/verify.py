"""Verify v4.5.5 offline identities, protected receipts and replay effects."""
import ast,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'docs/harvest/sol_reading/tools'))
from replay_literal import parse

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def effects(commands):
    result=[]
    for event in commands:
        if event['status']!='replayed':continue
        pre,code=parse(event['command'])
        result.extend(('mkdir',p) for p in pre)
        if code is not None:result.append(('python',ast.dump(ast.parse(code)),event['returncode'],event['stderr']))
    return result

def evidence(matches):
    stripped=json.loads(json.dumps(matches))
    for match in stripped:
        if 'reproduction' in match:match['reproduction'].pop('commands',None)
    return stripped

def main():
    output=ROOT/'out/scan2'
    summary=json.loads((output/'rescan_v455.json').read_text())
    assert len(summary['contexts'])==15
    scanner=ROOT/'docs/harvest/sol_reading/tools/scan_rollout.py'
    assert summary['scanner_sha256']==sha(scanner)
    protected=json.loads((output/'cq4_receipts_sha256.json').read_text())
    assert all(sha(path)==digest for path,digest in protected.items())
    receipts={};changed=[];effect_comparisons=0
    for entry in summary['contexts']:
        assert sha(entry['rollout'])==entry['rollout_sha256']
        directory=Path(entry['reader_dir'])
        assert sha(directory.parent/('MANIFEST.'+directory.name+'.json'))==entry['manifest_sha256']
        path=output/(entry['tag']+'.v455.scan.json')
        current=json.loads(path.read_text())
        previous=json.loads(path.with_name(entry['tag']+'.v454.scan.json').read_text())
        for field in ('ok','violations','image_match_counts','loop_expansions'):
            assert current[field]==previous[field],(entry['tag'],field)
        assert evidence(current['image_matches'])==evidence(previous['image_matches']),entry['tag']
        for now,old in zip(current['image_matches'],previous['image_matches']):
            if 'reproduction' not in now:continue
            nc=now['reproduction']['commands'];oc=old['reproduction']['commands']
            assert effects(nc)==effects(oc),(entry['tag'],now['record'])
            effect_comparisons+=1
            if nc!=oc:changed.append(dict(tag=entry['tag'],record=now.get('record'),path=now['path']))
        assert current['scanner_version']=='4.5.5'
        assert current['ok'] and not current['violations']
        receipts[str(path.relative_to(ROOT))]=sha(path)
    report=dict(scanner_sha256=sha(scanner),contexts_verified=15,
        protected_hashes_verified=len(protected),baseline='v4.5.4',
        unchanged_fields=['ok','violations','image_match_counts','loop_expansions','image_matches excluding replay command grouping/skips'],
        identical_replayed_effect_comparisons=effect_comparisons,
        replay_command_receipt_changes=changed,receipts_sha256=receipts)
    (ROOT/'out/scan2f/verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Verified 15/15 VALID;',len(protected),'protected hashes unchanged;',effect_comparisons,'identical replay effect sequences;',len(changed),'receipt formatting/skip changes.')
if __name__=='__main__':main()
