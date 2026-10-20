# DEL1: approved deletion of collect-v3-data/v2_masked/l1e_sample_r2 (gpt-6.1-sol, medium, network OFF)

**Owner-approved** deletion sheet (via coordinator, 17 Oct), confirmed by the sourcing lead, who owns the folder: delete ONLY
`/Users/foivoskarounos-zamparloukos/Projects/collect-v3-data/v2_masked/l1e_sample_r2` (about 2.4 MB).

**Never touch** anything else under `collect-v3-data`, in particular the siblings `l1e_sample`, `l1e_sample_r3`, `l1e_sample_r4`,
`l1e_sample_vouli`, `l1e_sample_vouli_r2`, `pilot`, `s8_dev`, `v2_test`, `w1_masked_records`, and the `run/` root. The cited siblings
are explicitly kept.

Do:
1. **Before:**
   - full listing of `l1e_sample_r2`: relative path, size, sha256 per file;
   - `du -sh` of it and of `v2_masked/`;
   - a citation re-check: `grep -rIl` for `v2_masked/l1e_sample_r2` across `~/Projects/greek-ocr-toolkit*` and `~/Projects/collect-v3-data`
     excluding the folder itself. If ANY citation appears, STOP without deleting.
2. **Delete:** `rm -r` of exactly that one directory.
3. **After:** `du -sh v2_masked/`, and confirm the folder is absent and the siblings are untouched (their file count + total size before
   and after are identical).
4. **Receipt:** `docs/records/labelfix/spellcheck/R2/receipts/DEL1_v2masked_l1e_sample_r2.json` in THIS worktree, containing: the approval
   chain (owner sheet via coordinator; sourcing lead confirmation), the listing with sha256, sizes before/after, the citation check, and
   the sibling invariance.

No `.git` writes.

Last line: `DEL1 DONE: deleted l1e_sample_r2 <files>/<bytes>; citations 0; siblings unchanged yes; receipt <path>`.
