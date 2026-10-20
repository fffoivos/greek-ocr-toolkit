"""Read-only reconciliation of admissions, withdrawals and every retained PNG."""
import hashlib
import json
from pathlib import Path
BASE=Path(__file__).resolve().parent
OUT=BASE.parent


def rows(path):
    return [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]


def main():
    before=json.loads((BASE/'w1_before.json').read_text())
    summary=json.loads((BASE/'w1_summary.json').read_text())
    inputs={r['row_id']:r for r in rows(before['receipt']['input_path'])}
    old=set(before['passed_ids'])
    admitted=rows(OUT/'w1_originals_v3_admitted.jsonl')
    new={r['row_id'] for r in admitted}
    assert len(new)==len(admitted)==summary['after'] and not new-old
    withdrawn=set((OUT/'w1_neighbour_words_withdrawn.txt').read_text().splitlines())
    assert old-new==withdrawn and len(withdrawn)==summary['withdrawn']
    manifest=rows(OUT/'crops_manifest.jsonl')
    assert len(manifest)==len(old)==28798 and {r['row_id'] for r in manifest}==old
    assert {r['row_id'] for r in manifest if r['admitted']}==new
    expected_paths=set()
    total=0
    for r in manifest:
        path=OUT/r['path'];expected_paths.add(path)
        assert path.is_file() and not path.is_symlink()
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        assert digest==r['sha256']==inputs[r['row_id']]['crop_sha256']
        assert path.stat().st_size==r['bytes'];total+=r['bytes']
        assert r['admitted']==(r['row_id'] in new)
    assert set((OUT/'crops').rglob('*.png'))==expected_paths
    crop_receipt=json.loads((OUT/'crops_receipt.json').read_text())
    assert crop_receipt['failures']==0 and crop_receipt['withdrawn_count']==len(withdrawn)
    assert crop_receipt['total_bytes']==total
    receipt=json.loads((OUT/'w1_originals_v3_admission_receipt.json').read_text())
    assert receipt['input_sha256']==before['receipt']['input_sha256']==summary['input_sha256']
    assert receipt['rows_pass']==len(new)
    assert receipt['drops_per_rule']['neighbour_words']==summary['all_neighbour_drops']
    result=dict(before=28798,after=len(new),withdrawn=len(withdrawn),retained_pngs=len(manifest),
                deleted_pngs=0,all_pngs_match_original_crop_hash=True,retained_bytes=total,
                original_input_sha256=receipt['input_sha256'])
    (BASE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
