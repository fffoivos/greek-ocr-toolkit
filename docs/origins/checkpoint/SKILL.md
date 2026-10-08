---
name: checkpoint
description: Use whenever the owner says "checkpoint", "add checkpoints", "review checkpoint", "CP-…", or asks for reviews (Sol / Astra / cross-model) at stages of a plan, and whenever launching anything long (a review, a Slurm chain, a build) whose outcome you will act on. Covers (A) the checkpoint policy: where checkpoints go, the soft limit of 2 Sol review cycles per checkpoint, the final Astra xhigh review that verifies the fixes, briefs, replies, model assertion, and what a HOLD blocks; and (B) watching long work so that every outcome (done, failed, stalled, lost, timed out) arrives as an event, with tested watcher scripts (watch_proc.sh, watch_slurm.sh) and Monitor re-arming. Written after the DPO07/08 review cycles and a 9-hour silent stall on 26–27 Sept 2026.
---

# Checkpoints: independent review at the right points, watched properly

## Part A: Checkpoint policy (owner rules; subproject 14 practice, Sept 2026)

### Where checkpoints go

Define them in the plan **before** executing, as a table: CP id, when, evidence, reviewers, and what it gates. Place one at each of these points:

1. **Before any new code path trains or any money or judge budget is spent.** The evidence is the code, its fixtures, a real smoke run (not just unit tests), dry runs and configs.
2. **Before integration or composition:** the pieces about to be wired together.
3. **After any gate retraction or false-green.** A gate that passed while broken makes the harness suspect.
4. **After results, before the report or any promotion claim.** The evidence is the readout, the raw scorecards and the claims text.
5. **Before a held-out or confirmation set is used:** freeze it and its contamination report first.

Do not spend a review per gate or per loop tick. Do not certify plans alone: certify results and the code that produces them.

### Reviewers and cycle limits (owner, 26 Sept: "checkpoints all along the way with up to 2 sol reviews if needed, also an astra xhigh review to verify the fixes")

- **Sol (gpt-5.6-sol, xhigh) is the per-checkpoint reviewer, with a soft limit of 2 cycles per checkpoint.**
  - Cycle 1 reviews the evidence.
  - The implementer fixes every BLOCKER/HIGH and writes `CP-X_reply_N.md`, mapping each finding to a fix or an explicit deferral.
  - Cycle 2 re-certifies against the new hashes.
  - The limit is soft: after a second HOLD, do not start a third Sol cycle by reflex.
    - **Diagnose the structural cause**; memory "third review cycle is a signal".
    - Scope what remains. If the remaining HIGHs do not touch what the checkpoint gates (e.g. an analysis script that runs only after results), the coordinator may proceed. **Disclose that decision in the reply document and state file.**
- **Astra (gpt-6-astra, xhigh) gives the final verification of the fixes.**
  - Run it alongside or after the last Sol cycle, and for new code paths.
  - It may be **scoped**, e.g. "verify only the readout fix", so each re-check stays cheap.
  - Astra cycles are not capped by the Sol limit, but each one must be scoped to what changed.
  - Astra found issues Sol missed in this project: float ties, unprescribed labels, a precompute gap. Keep it as the last word on fixes.
- Other projects may name other reviewers (memory: Fable/Opus for SFT v2). **Use the project's reviewer policy.** Never use the implementer's own model family as the certifier.
- **A HOLD blocks what the checkpoint gates,** even after an earlier "launch it" (memory "review HOLD blocks launch"). The only exception is the disclosed soft-limit decision above.

### Harness (subproject 14)

- **Sol:** `bash cluster/run_review.sh <LABEL> <brief.md> gpt-5.6-sol xhigh`.
  - It writes `reviews/<LABEL>_review_1.md` and `.codexlog`.
  - It is read-only, and the reviewer's shell stays on.
  - **Never pass `-c features.code_mode_host=false`** (memory).
  - Since 27 Sept it asserts the model from the rollout named by the session id in the log, and exits 9 when it cannot.
- **Astra:** `python3 data/rlhf/astra_review.py <LABEL> <handoff.md> <out.md> --effort xhigh --brief <brief.md>`. It asserts the model from the rollout it tags with a marker.
- **Labels:** use a new label for each cycle (`CP-F1`, `CP-F1c2`, …). `run_review.sh` always writes `_review_1`, so reusing a label overwrites the old review.
- **Model identity comes from the rollout, never from the reviewer's self-description.** `asserted=UNKNOWN` means the review is **not certified**; fix the harness.

### Brief and reply shape

- **Brief:**
  - the role (independent certifier, adversarial, recompute numbers, report raw failures);
  - the documents to read;
  - the exact scope (files, evidence directories and job ids);
  - numbered acceptance criteria;
  - what is out of scope;
  - the disposition policy (BLOCKER/HIGH fixed before what the checkpoint gates; MEDIUM/LOW fixed or explicitly deferred);
  - "do not start background jobs";
  - the last line exactly `VERDICT: <PASS|HOLD> … | BLOCKERS: n | HIGH: n`.
- **A cycle-2 brief** adds: the previous reviews, the reply, the prior code copy to diff against, and the new evidence job ids.
- **Reply:** a table of every finding → Fixed / Deferred / Declared, each with the evidence. Record the cycle and its verdict in the plan's state file.
- **Results checkpoints:** the reviewer re-derives every number from raw scorecards. Correct overclaims (significance, "all", "removes", "no bug") in the report, not only in the reply.

### Cost and timing

A Sol xhigh review took 8–13 min in this project, and Astra xhigh 7–9 min. Run Sol and Astra in parallel. Launch each so it can be watched (Part B). While a pre-launch checkpoint is out, prepare the next work, but never apply edits to files the brief hashes (memory "no edits while a pass is in flight").

# Part B: Watching long work (reviews, Slurm, builds). Silence is not success

## Why this skill exists

These failures happened on 26–27 Sept 2026 and are all real:

| # | What happened | Why it was silent | Cost |
|---|---|---|---|
| 1 | A watcher `until ssh clariden 'sacct …'; do sleep 60; done` hung on an unresponsive login node. | There was no keepalive and no bound. The background task never exited, so no notification ever came. | **9 h of nothing** while the owner slept (00:16 → 09:10) |
| 2 | Every Sol review printed `asserted=UNKNOWN` and was accepted. | The harness used `find -newermt "@epoch" 2>/dev/null`. BSD `/usr/bin/find` under bash cannot parse `@epoch`, and the error was hidden. The empty result then skipped the mismatch check (`[ -n "$ACTUAL" ] && …`). | Three reviews were never model-asserted; this was verified afterwards from their rollouts. |
| 3 | Review waits were written as `for i in $(seq 1 60); do …; sleep 30; done; tail …`. | They exit 0 whether the review finished, crashed or ran past 30 min. "Completed (exit 0)" was read as "done". | The design could not tell success, timeout and crash apart. |
| 4 | Nothing checked whether a running review was still producing output. | There was no stall detection. A hung codex process looks exactly like a slow one until the cap. | Risk of waiting hours on a dead process |
| 5 | A cleanup used `ps … \| grep -E "[s]sh .*clariden\|[u]ntil …" \| kill`. | The pattern matched the cleanup's own shell (exit 144) and several unrelated tasks. | Lost tasks and misleading "failed" notices |
| 6 | 23 `ssh clariden` processes piled up. | Foreground ssh calls timed out after 120 s, were moved to the background and never ended. | Resources, and confusion about what was still running |
| 7 | A chain watcher reported only at the very end. | There were no intermediate events, so a job finishing or failing mid-chain went unseen until the whole wait ended. | Late reaction |
| 8 | The new watcher's own 90 s ssh watchdog blocked every poll for the full 90 s. | Inside `$(…)`, the background `sleep` inherited stdout and held the pipe open. Found by testing, before use. | Nothing, because it was tested first. **Test every watcher in every terminal state before relying on it.** |

## The rules

1. **Every watch has named terminal states, and every one of them emits a line.** The states are DONE, FAILED, STALL, TIMEOUT and LOST. A watcher that can end silently in any of them is broken. Before arming a watch, ask: *if the process crashed / hung / lost the network right now, what line would I get?*
2. **Every loop is bounded, and every remote call is bounded.**
   - Use `--max-min` on the loop.
   - Give ssh `ConnectTimeout=15`, `ServerAliveInterval=10` and `ServerAliveCountMax=3`, plus a local watchdog.
   - After N consecutive unanswered polls, report **LOST**. Do not keep waiting.
3. **Liveness is measured, not assumed.** For a local process, check that the pid is alive **and** that its log is growing. A live pid with a frozen log is a **STALL**. Report it; do not kill it.
4. **Use a Monitor for anything with more than one state, and a background Bash only for a single, bounded "tell me when done".**
   - A Monitor expires after at most 30 min, and you are **told** when it expires. That expiry is your guaranteed wake-up.
   - Re-arm it with the same (restartable) script, which re-emits the current state first.
   - A background Bash notifies once, only when it exits; if it hangs, you hear nothing.
5. **Interpret the exit status, not the exit code of the wait.** Read the event line (DONE / FAILED / …). Then **confirm with one direct probe** (the output file, the verdict line, `sacct`) before acting.
6. **Assertions fail closed.**
   - Never hide the stderr of an assertion step with `2>/dev/null`.
   - An empty assertion result is a failure, not a pass.
   - After changing a harness, re-run the assertion on one real past output to prove it works. The fix to `run_review.sh` was proven this way on three past reviews.
7. **Stop things by identity, never by pattern.**
   - Use TaskStop with the task id.
   - Or `kill <PID>` with the PID **captured at launch** (`cmd & PID=$!`). Check it with `ps -o command= -p $PID` first.
   - Never `pkill -f`, and never `ps | grep | kill`. Never `pkill -f codex` in particular.
8. **Heartbeats.**
   - A long watch emits PROGRESS lines (`--progress-min`), so a dead watcher is distinguishable from a quiet job.
   - Stay selective: one line per state change plus a heartbeat every 10–30 min, never raw logs.
9. **Tell the owner promptly** when a watch ends in anything but DONE. Also tell them when a watch has been re-armed more than twice without a state change.

## Tools in `scripts/`

Both scripts are bash 3.2 compatible and never kill or cancel anything.

### `watch_proc.sh`: one local process (reviews, local builds)

```bash
watch_proc.sh --label CP-X --pid $PID --log review.codexlog --out review.md --done-regex '^VERDICT:' \
              [--stall-min 15] [--max-min 180] [--poll-sec 20] [--progress-min 10]
```

- **Events:** START (it prints the pid's command line, which proves the right process is being watched), PROGRESS, WARN (a failure signature appeared in the log while running), and the terminal states DONE, FAILED, STALL, TIMEOUT.
- **Exit codes:** 0 DONE, 1 FAILED, 2 TIMEOUT, 3 STALL.
- **Tested on 27 Sept:**
  - success;
  - exit with no output;
  - output without a verdict;
  - live-but-silent process → STALL.

### `watch_slurm.sh`: a set of Slurm jobs over ssh

```bash
watch_slurm.sh --host clariden2 --jobs 3529101,3529102 [--poll-sec 240] [--max-min 240] [--lost-after 4] [--progress-min 30]
```

- **Events:** START (all states), CHANGE (per job, including PENDING-reason changes), PROGRESS, and the terminal states:
  - JOB_FAILED: FAILED, CANCELLED, TIMEOUT, OUT_OF_MEMORY, NODE_FAIL, PREEMPTED, BOOT_FAIL, DEADLINE, and **DependencyNeverSatisfied**, which never resolves on its own;
  - ALL_DONE;
  - LOST;
  - TIMEOUT.
- **Exit codes:** 0, 1, 2, and 5 for LOST.
- **Tested on 27 Sept:**
  - completed jobs → ALL_DONE;
  - a failed job → JOB_FAILED;
  - an unknown host → LOST in 2 s;
  - a blackholed IP → LOST in 31 s, not a hang.

## Failures of 27–28 Sept (S1_NEXT confirmation). The watchers worked; **I pointed them at the wrong signals**

| # | What happened | Rule it broke | Fix |
|---|---|---|---|
| 9 | A detached `judge_panel.py` was watched with `--log run_all.log`. The launcher redirects stdout there, but the judge prints only at exit, so the file stayed at 0 B. `watch_proc` fired a **false STALL** at 15 min and the watch ENDED. The real run then hit its call cap and had 24 failed orders, all unwatched. | 3 (liveness is measured) | `--log` must be a file the process appends to **continuously**: for the judge, `judged.jsonl` (or `attempts.jsonl`); for codex reviews, the `.codexlog`. **Check it grows within ~2 min of START.** If it doesn't, re-arm on the right file at once. |
| 10 | A 30-min Monitor expired (CP-N3c5 Astra) and was not re-armed. | 4 (expiry is the wake-up: re-arm) | On every "Monitor expired" notice, re-arm immediately with the same command, unless the watched thing is confirmed finished. |
| 11 | `watch_slurm.sh clariden2 <id>` (positional) → `bad argument`, and the watch died at once. | 1 | Always use `--host … --jobs …`. Read the first event of every new watcher: START means it's running; anything else is a broken watch. |
| 12 | A STALL or FAILED event ended a watch and nothing replaced it. | 9 (report / act) | After ANY terminal event that isn't DONE / ALL_DONE: inspect **and** either re-arm a correct watch or confirm the process is gone. Never leave live work without a watch. |

### Which file shows progress, per job type (subproject 14)

| Job | `--log` (grows during the run) | `--out` / done signal |
|---|---|---|
| `run_review.sh` (Sol) | `reviews/<L>_review_1.codexlog` | `reviews/<L>_review_1.md`, `--done-regex VERDICT:` |
| `astra_review.py` | `<out>.md.codexlog` | `<out>.md`, `VERDICT:` |
| `judge_panel.py` (detached) | `<run>/judged.jsonl` | calibration: `calibration_gate.txt` + `GATE`; `--ids all`: `summary.json`. Then check `json_validity.complete` and the `CAP REACHED` line in `run_*.log` |
| Slurm jobs | — | `watch_slurm.sh --host clariden2 --jobs <ids>` |

## Recipes

### A cross-model review (codex), launched so it can be watched

```bash
nohup bash cluster/run_review.sh LABEL brief.md gpt-5.6-sol xhigh </dev/null > run.log 2>&1 &
PID=$!                                   # capture NOW; never find it later with pgrep -f
```

Then arm a Monitor (description e.g. "CP-N1 Sol review"; `timeout_ms` 1800000):

```bash
~/.claude/skills/checkpoint/scripts/watch_proc.sh --label CP-N1 --pid $PID \
   --log docs/.../reviews/LABEL_review_1.codexlog --out docs/.../reviews/LABEL_review_1.md \
   --done-regex '^VERDICT:' --stall-min 15 --max-min 120 \
   --fail-regex 'stream error|stream disconnected|rate limit|usage limit|unauthorized|panicked|Killed'
```

For reviews, **always pass that narrow `--fail-regex`.** The default catches `Error:`, and a reviewer's log contains the source code it reads, so `ImportError:` in a file fired false WARNs on 27 Sept (CP-N1a). WARN never ends the watch; DONE, FAILED and STALL decide.

On DONE:
1. Read the verdict.
2. Check the harness's own last lines in `run.log`: the `requested=… asserted=…` line and the shell-command count. `asserted=UNKNOWN` or a missing line is a **harness failure**. Treat it as uncertified.

On STALL:
1. Read the codexlog / rollout (`~/.codex/sessions/…/rollout-*<session id>.jsonl`) to see what the model is doing.
2. A long tool call can be legitimate. Re-arm with a larger `--stall-min` rather than killing.

On FAILED: read the log tail the event printed, fix, and re-run. A re-run counts toward the review-cycle budget only if the reviewer actually produced a verdict.

### Slurm chains

- Arm one Monitor running `watch_slurm.sh` over **all** job ids of the chain, with `--progress-min 30` and `timeout_ms` 1800000.
- Every expiry notice is your wake-up: re-arm.
- On CHANGE to COMPLETED of an intermediate job, you may start reading its outputs right away. You do not have to wait for the chain.
- On JOB_FAILED, stop and inspect the job's `.out` (use the job's `--output` path) before resubmitting anything.
- On LOST, switch to another login node (`clariden2` = ln002 via ela, keepalive in `~/.ssh/config`). Re-sign the CSCS certificate if it is near expiry.

### When the harness itself is the thing being changed

Test it on a real past output before the next real use, as with rule 6 and failure #8. Keep a copy of the pre-change version next to the change note.

## Things that look like watching but are not

- `until <remote check>; do sleep N; done` with no bound and no ssh timeouts. This caused failure #1.
- `for i in $(seq 1 N); do …; done; tail file` presented as a "wait for completion". It cannot tell success from a timeout. This is failure #3.
- `tail -f log | grep --line-buffered SUCCESS_MARKER`. It is silent on crash, hang or exit.
- `… | grep … | head -1` or `| cut` / `| awk` without flushing at the end of a Monitor pipeline. Events sit in a buffer (memory note of 15 Sept).
- `grep -c` over logs written by several ranks. Accelerate ranks can share a line; count occurrences with `grep -o … | wc -l`.
