# Guarded SPLIT2 commit list

Only these paths are authorized for a prospective SPLIT2 commit:

- docs/briefs/SPLIT2_final_row_split.md
- docs/harvest/collect_v3_admission/split2/build_split2.py
- docs/harvest/collect_v3_admission/split2/test_split2.py
- docs/harvest/collect_v3_admission/split2/row_split.jsonl.gz
- docs/harvest/collect_v3_admission/split2/edition_map.jsonl
- docs/harvest/collect_v3_admission/split2/receipt.json
- docs/harvest/collect_v3_admission/split2/SPLIT2.md
- docs/harvest/collect_v3_admission/split2/GUARDED_COMMIT_LIST.md
- docs/harvest/collect_v3_admission/split2/tests.log
- docs/harvest/collect_v3_admission/split2/tests.xml

No staging, commit, push, Clariden access, network request, OCR, or paid operation
was performed. Existing unrelated modifications remain outside this list.
Do not use `git add .`, `git add -A`, or commit with `-a`.
Before committing, stage the exact files above and compare `git diff --cached
--name-only` with this allowlist; stop if any other path is staged. Inspect
`git diff --cached --stat` and the text diff before committing. SPLIT1 and all
external input worktrees are read-only; never include changes to them.

Validation receipts: `receipt.json`, `tests.log`, and `tests.xml`.
