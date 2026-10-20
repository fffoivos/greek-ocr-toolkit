# CENSUS05-A exact lead commit list

Package `17b0eb1ca7fe81a7` is locally READY, not deployed or remotely verified. Use the exact pathspec, which includes new files, changed files and removed unused partial-capture files. Every final changed path is inside docs/harvest/census05/. No .git write occurred here.

```bash
cd /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit-segcensus
git add --pathspec-from-file=docs/harvest/census05/commit_paths.txt
git diff --cached --stat
git commit -m "CENSUS05-A: package PIPE032 census with regenerated N1 and version-bound readout"
```

The code payload manifest has 167 files (154 CODE_SHA-identical; 13 additive). Already tracked identical source blobs need no new diff. No ignored payload or verifier allow-list is needed. Full numerics inputs, SQLite validation databases, native target symlink and mock runtime are excluded. The 35 committed correction gzip chunks, their receipt and restore_inputs.py reproduce the five ignored full-size inputs exactly. The finalized sourcing split stays external.

readout_version.patch targets the canonical relocated CODE_SHA docs/records/harvest/census05/readout paths for the coordinator's separate docs-only merge. The local package mirror edits three files under docs/harvest/census05/readout/. Do not change production code or the frozen tool manifest.

FOLLOW_UP.md contains the unexecuted deployment/readback/verifier/smoke/full and main hash-comparison commands. Require actual VERIFY_OK and coordinator smoke approval before full submission. Four batch kinds are named in the brief; its “all five” wording remains a documented ambiguity.
