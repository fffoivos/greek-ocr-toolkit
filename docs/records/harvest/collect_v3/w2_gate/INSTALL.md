# GATE2b installation handoff

Prepared only; installation belongs to the lead's coordinator-authorised Gazette launch one-off. Run these exact two lines in order, outside the restricted sandbox, while keeping the collector stopped throughout the install. The re-check does not reserve the run root or take locks; the lead must prevent concurrent launches.

```sh
(set -eu; "$HOME/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python" "$HOME/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/w2_gate/check_live.py")
(set -eu; run="$HOME/Projects/collect-v3-data/run"; prep="$HOME/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/w2_gate"; py="$HOME/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python"; "$py" "$prep/check_live.py"; shasum -a 256 "$run/c1_gate.json"; tmp=$(mktemp "$run/.c1_gate.GATE2b.XXXXXX"); trap 'rm -f "$tmp"' EXIT; cp "$prep/c1_gate.next.json" "$tmp"; shasum -a 256 "$tmp"; test "$(shasum -a 256 "$tmp" | cut -d " " -f 1)" = "4652febb230ee37306e9c27a732e6989f53a5e22c56d1645f459f467e72e3545"; "$py" "$prep/check_live.py"; mv -f "$tmp" "$run/c1_gate.json"; shasum -a 256 "$run/c1_gate.json"; test "$(shasum -a 256 "$run/c1_gate.json" | cut -d " " -f 1)" = "4652febb230ee37306e9c27a732e6989f53a5e22c56d1645f459f467e72e3545")
```

The first line requires the live gate SHA to equal `eb4a17ed1924ff77a863460fe8445f8437c62a5a68a9b4418f159e71fbf7dc98`, both recorded PIDs to be absent, no collector command in the process table, and no open descriptor on `run.lock` (a conservative check for a held lock). An unavailable or inconclusive check aborts. Local preparation could verify the gate and snapshot; the sandbox denied `/bin/ps`, so the live process/lock re-check is delegated to the lead.

The second line repeats the guard, prints the old SHA, copies to a unique temp file in the run root, verifies the copied SHA, re-checks immediately before the atomic rename, then prints and verifies the installed SHA. No collector is launched by either line.

Expected installed SHA: `4652febb230ee37306e9c27a732e6989f53a5e22c56d1645f459f467e72e3545`.

Offline validation: run `"$HOME/Projects/greek-ocr-toolkit-sol-collect/.venv/bin/python" "$HOME/Projects/greek-ocr-toolkit-sol-collect/docs/harvest/collect_v3/w2_gate/validate.py"`. It uses a temporary mirror under this folder with exactly three files and removes the mirror afterward. Existing provenance, including the historical `not_admitted` wording, is preserved as requested; the new source entry records the extension scope.

Guarded commit list: `commit-list.json` binds the six payload files by SHA-256 and includes itself in the exact commit path list. Run `guard_commit.py` with the same Python to verify; `--stage` stages only those seven paths after verification and rejects unrelated staged paths. No staging or commit was performed during preparation. Temporary mirrors and unrelated worktree changes are excluded.
