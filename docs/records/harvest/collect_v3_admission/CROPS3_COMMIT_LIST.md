# CROPS3 guarded commit list

Preparation artifacts only. No commit, push, upload or full-scale staging was performed. The worktree contains unrelated pre-existing edits and untracked artifacts; do not use `git add .`, `git add -A`, or directory-wide staging.

`CROPS3_COMMIT_LIST.json` contains the exact allowlist and SHA256 for each file, including the supplied CROPS3 brief. It excludes all PNGs, generated crop trees, input snapshots, sample selections, private retained pages and unrelated work. `CROPS3_COMMIT_LIST.json` itself may also be staged after verifying the allowlist. This list does not authorize any subsequent Mac processing run or upload.

When preparing a commit, verify each listed file's SHA256 and stage only those exact paths, plus the commit-list JSON. Then inspect `git diff --cached --name-only` and `git diff --cached --check`. Stop if any staged path is outside that exact set or any PNG is staged. Review any previously staged work separately; do not reset it automatically.

The 2,000 crop PNGs and their manifest/selection/receipt remain outside git at `/private/tmp/crops3-estimate-20261019/`. The requested external sample destination was sandbox-denied; relocation there remains undone. `CROPS3_ESTIMATE.json` includes the measurement receipt and hashes of the out-of-git selection/manifest. All 29 offline tests passed; no live Clariden test was attempted.
