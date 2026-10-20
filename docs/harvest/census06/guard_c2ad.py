"""Read-only exact C2a-D commit allowlist check; never stages or commits."""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[3];D=R/'docs/harvest/census06'
paths=(D/'C2AD_COMMIT_PATHS.txt').read_text().splitlines()
assert paths==sorted(set(paths))
assert all(p.startswith('docs/harvest/census06/') or p=='docs/briefs/CENSUS06C2aD_deploy_verify.md' for p in paths)
sums={line[66:]:line[:64] for line in (D/'C2AD_COMMIT_SHA256SUMS').read_text().splitlines()}
assert set(sums)==set(paths)-{'docs/harvest/census06/C2AD_COMMIT_SHA256SUMS'}
for p,sha in sums.items():
 assert (R/p).is_file() and (R/p).resolve().is_relative_to(R)
 assert hashlib.sha256((R/p).read_bytes()).hexdigest()==sha,p
print(f'C2AD_GUARD_OK: {len(paths)} exact paths; {len(sums)} sealed files; no staging or commit')
