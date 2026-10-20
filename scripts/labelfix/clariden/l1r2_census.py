"""Job 2: saved-evidence inventory, HOLD counts and SF6c deletion census."""
import argparse
from pathlib import Path
import time

try:
    from . import l1c_census as hold, l1r2_changes as changes, l1r3_evidence as evidence
except ImportError:
    import l1c_census as hold
    import l1r2_changes as changes
    import l1r3_evidence as evidence


def run(root, out, workers=16, *, config):
    started = time.monotonic()
    out = Path(out)
    paths = (__file__, hold.__file__, changes.__file__, evidence.__file__)
    code = {Path(p).name: hold.sha256(p) for p in paths}
    config_sha = hold.sha256(config)
    evidence.inventory_release(root, out / 'evidence_availability.json', config)
    hold.census(root, out / 'hold', workers)
    changes.census(root, out / 'changes', workers)
    if code != {Path(p).name: hold.sha256(p) for p in paths} or hold.sha256(config) != config_sha:
        raise ValueError('census job code changed')
    result = dict(schema='l1r3-combined-census-v1', complete=True, analysis_only=True,
                  input_directory=str(Path(root).resolve()), code_sha256=code,
                  config_sha256=config_sha,
                  outputs={name: hold.sha256(out / name) for name in ('evidence_availability.json', 'hold/receipt.json', 'changes/receipt.json')},
                  elapsed_seconds=time.monotonic()-started)
    hold.atomic_json(out / 'receipt.json', result)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=16)
    ap.add_argument('--config', type=Path, required=True)
    a = ap.parse_args()
    run(a.input_dir, a.out, a.workers, config=a.config)
