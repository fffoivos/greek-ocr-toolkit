# Guarded local commit list

Scope: only the exact paths in `COMMIT_PATHS.txt`, with byte hashes in `COMMIT_SHA256SUMS.txt`. Includes the proposal, unpublished owner sheet, its 410 referenced crops, builders, local variant table, requested offline tests and their results, evidence, and explicit screenshot-QA limitation. The checksum manifest excludes itself because a file cannot contain its own hash.

No files outside `docs/records/harvest/collect_v3_admission/split1/` belong to this proposed commit. The checkout already contained unrelated tracked edits and many untracked files when SPLIT1 started. None were staged, reverted, included or modified for this task. The review checkout, data snapshots, v2 inputs and live collector root were read-only. No final splits or admissions were changed.

Verify the exact bytes and ensure no unrelated paths are staged:

```sh
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/split1/verify_commit_scope.py
```

The following are reviewable commands for the lead, **not commands executed by SPLIT1**:

```sh
git add --pathspec-from-file=docs/records/harvest/collect_v3_admission/split1/COMMIT_PATHS.txt
~/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python docs/records/harvest/collect_v3_admission/split1/verify_commit_scope.py
git diff --cached --stat
git commit -m "SPLIT1: propose W1/W2 edition splits and owner review sheet"
```

No push command is authorized or included. `QA_STATUS.md` records the uncompleted screenshot verification; the offline JavaScript fixture is not a visual check. Publication belongs to the lead and requires the reference notes-dump/reload protocol.
