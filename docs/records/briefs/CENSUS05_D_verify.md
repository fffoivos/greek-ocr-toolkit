# CENSUS05-D: VERIFY_OK for the redeployed census_05 package 997b7d2ab5a8775b (gpt-6.1-sol, medium, network ON; no .git writes; no deploy; NO submission)

**Worktree:** `~/Projects/greek-ocr-toolkit-segcensus`, branch `opus/seg-census`. HEAD must be `66f0774fa` (CENSUS05-C committed), or
a descendant touching only `docs/briefs/`. `git status --porcelain` must show nothing tracked as modified. Check both first.

CENSUS05-C deployed package `997b7d2ab5a8775b` to `$W/census_05_20261020/code/997b7d2ab5a8775b/` (readback 178/178). Its verifier
calls failed only because the tree was not committed. It is committed now.

## Do

1. **Run the unchanged verifier**, `~/Projects/greek-page-ocr-wave2/scripts/ops/verify_deploy.py`, for the four kinds
   (regression, parity, census, readout), with exactly the arguments in `docs/harvest/census05/c_evidence/verify.py`, except
   for one thing.
   - Every `--out` and log must go OUTSIDE the repository, to
     `/private/tmp/claude-501/-Users-foivoskarounos-zamparloukos/84051317-02f9-484c-90f2-e64ba6f33b29/scratchpad/census05d/`.
   - Reason: the in-repo `c_evidence/verify-*.json` files are tracked, so rewriting them between kinds dirties the tree and fails
     the next kind.
   - Run all four first. Only after the fourth has finished, copy the outputs into `docs/harvest/census05/d_evidence/`, a new
     directory.
   - Each kind must print VERIFY_OK. If one fails for any reason other than the tree, stop and report it verbatim.
   - If ssh or authentication fails, stop: the certificate is owner-gated.
2. **Update the "C" section** of `HANDOFF_CENSUS05.md` and `REVIEW_INPUTS.md`:
   - the VERIFY result per kind, pointing at `d_evidence/`, with hashes;
   - keep everything else as written.
   - The final coordinator commands stay as in section C: smoke `--partition=debug --time=00:30:00`, then full. Check that they
     point at `code/997b7d2ab5a8775b`.

**Last line:** `CENSUS05-D READY: package 997b7d2ab5a8775b; VERIFY_OK regression <ok> parity <ok> census <ok> readout <ok>; HEAD <sha8>; commands point at 997b7d2a <yes|no>`
