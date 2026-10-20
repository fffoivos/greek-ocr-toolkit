"""Run the byte-identical CP7c scorer with only CP7c2's runtime exception.

Usage (collector interpreter): python -B seg/cp7/score_cp7d.py
No reading, measurements, threshold changes, or new freeze exceptions.
"""
import score_r2 as scorer
import runtime_r2

FREEZE_SHA = 'dd2e7234c4f0f96a19b552daf8863c8dcd4eacaef074abd37c99ac3d22066833'
AMENDMENT_SHA = '20d7b3ad44b8801f0c65c02efa35c687b105f443afb22170a56a693bf1e6d41b'
CP7C2_COMMIT = '1eea5e9b9a778544a6e4ea97dfdc4c6989730b99'


def verify():
    assert scorer.sha(scorer.FREEZE) == FREEZE_SHA, 'original r2 freeze drift'
    assert scorer.sha(runtime_r2.AMENDMENT) == AMENDMENT_SHA, 'CP7c2 amendment record drift'
    # This verifier checks the real amended runtime hash, substitutes its old
    # hash only for that path, and runs all original binding checks unchanged.
    return runtime_r2.verify_runtime_freeze()


def main():
    original = scorer.verify
    try:
        scorer.verify = verify
        scorer.main()
    finally:
        scorer.verify = original


if __name__ == '__main__':
    main()
