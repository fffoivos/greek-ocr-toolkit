"""Current sealed artifact validation; frozen CP7a2 verifier remains unchanged."""
from cp7_common import *
from freeze import verify_freeze
from prepare_population_geometry import page_manifest, valid
import verify_artifacts


def main():
    offline_guard();verify_freeze()
    current=read(HERE/'build_receipt_cp7a3.json')
    assert current['supersedes']=='build_receipt.json'
    assert current['draw_sha256']==sha(HERE/'keys/draw.jsonl')
    assert current['sealed_decisions_sha256']==sha(HERE/'keys/sealed_decisions.jsonl.gz')
    original_read=verify_artifacts.read
    def current_receipt(path):
        if Path(path)==HERE/'build_receipt.json':return current
        return original_read(path)
    verify_artifacts.read=current_receipt
    verify_artifacts.main()
    pages=page_manifest(rows(HERE/'keys/draw.jsonl'))
    assert all(valid(SEG/'CP7_geometry',p) for p in pages)
    assert (HERE/'keys/sealed_decisions.jsonl.gz').stat().st_mode & 0o777==0o600
    assert (HERE/'keys/sealed_decisions_cp7a2.jsonl.gz').stat().st_mode & 0o777==0o600
    preservation=read(HERE/'pack_preservation_cp7a3.json')
    assert preservation['unchanged']
    assert all(sha(p)==d for p,d in preservation['files'].items())
    verify_freeze()
    print(json.dumps(dict(gate_caches=len(pages),all_hash_valid=True,packs_unchanged=True,
                         current_seal_verified=True,readers_started=0,population_run_started=False)))

if __name__=='__main__':main()
