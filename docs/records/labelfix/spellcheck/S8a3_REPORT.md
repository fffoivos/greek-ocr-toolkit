# S8a3 — resumable DEV evidence debug job

**Ready for coordinator submission; NOT SUBMITTED.** The final payload is deployed and hash-verified, the local mock passes, all **639 labelfix tests pass**, and `sbatch --test-only` succeeds. No production extraction or inference ran in this task. The exhausted login-node STOP remains byte-identical to HEAD.

The clean starting HEAD was `d1fe4e36018a73237f52712ebc20cb8076684d9e`: the S8a3 brief commit immediately after the specified `c4734407`. Both S8a/S8a2 briefs were read. No `.git` writes or other-worktree writes were made.

## Verified checkpoint and request

Remote output root, also the only remote write destination:

`/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/`

| Item | Verified value |
|---|---|
| Request SHA256, S8a2 canonical serialization | `0d8a0ad72d0eb59d3ab47d8b81dc21f8e6341d1362b481823106957700238c5c` |
| `request.json` file SHA256 | Same as above |
| Existing `partial.json.gz` SHA256 | `9cb877b1c788e60ec93b0593b49212b4fec79a463a1d7bc1cbfbe1bff5a4c436` |
| Checkpoint size | 6,624,843 bytes |
| B/E completed | 863 shards, through `shard-00862-combined.jsonl.gz` |
| Saved runtime | 527/600 lines |
| Historical A verification | 0 lines / 0 completed shards |
| Remote requested alignments | 0/166 lines; four input worker files |
| Local alignment cache | 434 DEV lines, exact complement of the 166 requested remotely |

**Inventory correction:** the live B/E and A directories each contain **974** combined shards, numbered `00000` through `00973`. Thus the actual resume point is **863/974**, with **111** B/E shards left. The brief's `973` is preserved as a labelled nominal denominator in the requested closing line; the executable configuration gates on **974** and includes shard `00973`. No final shard is silently excluded. [Preflight](S8_DEV/evidence/S8a3/remote_preflight.json), [inventory](S8_DEV/evidence/S8a3/shard_inventory.json), [request](S8_DEV/evidence/S8a3/request.json).

Request and checkpoint hashes were unchanged after both deployment and the final scheduler dry run. The job independently verifies the checkpoint's request SHA against the remote `request.json` and the bound configuration before resuming; a missing checkpoint, mismatched request, damaged selected-field digest, or wrong cache fails closed.

## Prepared execution

- [Job entry point](../../../../scripts/labelfix/s8_fetch_job.py): standard-library-only Python **3.6+**; production runtime **`/usr/bin/python3`**, verified remotely as **3.6.15**. No venv or model imports are needed. Remote preparation syntax-compiled the deployed Python in memory without invoking extraction.
- [L1M helper](../../../../scripts/labelfix/s8_fetch_l1m.py): shares saved-record selection, historical-A field hashes, receipt custody, and the proven `docs/harvest/` crop-key join. Its legacy login fetch path and STOP policy were not executed or superseded.
- [Slurm script](../../../../scripts/labelfix/clariden/s8_fetch_job.sbatch): account **a0140**, partition **debug**, **one node**, one task, **32 CPUs / 32 shard workers**, **20 minutes**, no GPU work. The scheduler predicts 288 processors because the partition allocates whole nodes. Worker processes use explicit `spawn`; native thread environment limits are one.
- Compute extraction requires a Slurm debug allocation on a `nid*` compute hostname. The shell also rejects direct login-node invocation. A nonblocking output lock prevents concurrent writers.
- The parent alone merges and atomically checkpoints completed shards; worker processes only read inputs. Existing B/E progress is retained, including reconciliation of identical rows saved just before an old shard completion marker. Historical A's recogniser text/NFD, coverage and R1 predictions must match exactly. Reader peer predictions/coverage are retained; detector evidence and SF4 overlays are excluded.
- The internal extraction budget is **1,050 seconds (17.5 minutes)**, leaving 150 seconds within the Slurm limit for shutdown/checkpoint/receipt work. Deadline, signal, shard error, or A mismatch terminates readers, retains the checkpoint and writes a failed receipt. No retries or submissions occur inside the job.
- Success writes **`remote.json.gz` + `receipt.json` in the output root**. The final payload merges the hash-bound 434-line local cache with 166 remote alignments, checks recogniser/alignment identity, and contains all 600 runtimes and 600 alignments for `s8_prepare.py`. `partial.json.gz` retains only the requested remote alignments, so it remains resumable. The receipt binds request, starting/final checkpoints, output SHA, cache SHA, counts, runtime, interpreter and Slurm job ID.

Inputs in L1/L1E/L1R are read-only. Existing custody limits remain explicit: selected historical-A fields are compared exactly, existing shard receipts are read, and full large input shards are not rehashed. The STOP marker SHA256 is `82fb35152ffbff0fc2f62f9d88a8573676c9c492526e8bd43d5025068485dcbc`.

**Estimated compute runtime: 8 minutes**, a planning estimate rather than a measured Clariden result. It allows for 111 remaining B/E shard reads, selected A-shard checks, four alignment inputs totalling about 23.2 MB compressed, process startup and serialized checkpoint compression. The hard budget preserves progress if this estimate is exceeded. No allocation or queue reservation is implied.

## Validation and deployment

The local synthetic mock has real-shaped gzip JSONL combined shards, historical A inputs/receipts, crop-key alignment records, an unselected distractor, one cached alignment and a pre-existing checkpoint with one of three B/E shards already complete. It runs the same extraction/merge/checkpoint entry point, verifies input hashes unchanged, three complete runtimes/alignments, no detector fields, and a second successful resume from the completed checkpoint. [Mock receipt](S8_DEV/evidence/S8a3/mock_receipt.json).

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  scripts/labelfix/s8_fetch_job.py mock \
  --receipt docs/records/labelfix/spellcheck/S8_DEV/evidence/S8a3/mock_receipt.json

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  -m pytest -q tests/labelfix
```

Final result: **639 passed in 8.72 s**, including **11** tests in [test_s8_fetch_job.py](../../../../tests/labelfix/test_s8_fetch_job.py). Coverage includes request/checkpoint/cache SHA rejection without checkpoint mutation, mid-shard resume, historical-A mismatch recovery, immediate and in-flight deadline shutdown, compute/output guards, and selection/crop joins. Shell syntax, Python 3.6 grammar and `git diff --check` pass. [Test output](S8_DEV/evidence/S8a3/all_labelfix.txt), [validation receipt](S8_DEV/evidence/S8a3/validation.json).

An earlier synthetic validation stalled in the old pool-shutdown path; the final code uses explicit `spawn` and checks an expired budget before starting workers. The sandbox denied termination of that old local test process (PID 1688), which may remain. It never accessed production inputs.

Deploy root: `…/s8_dev_extract/job/`. The five manifest entries are both Python files, the Slurm script, `job_config.json`, and `dev_c1_alignments.json.gz`. [Manifest](S8_DEV/evidence/S8a3/S8F_DEPLOY_SHA256.txt), [configuration](S8_DEV/evidence/S8a3/job_config.json), [deployment receipt](S8_DEV/evidence/S8a3/deployment_receipt.json).

`S8F_DEPLOY_SHA256.txt` SHA256, **local = remote**:

`73d5133ffdc057d71f65e76a9e37ed05a02d38422d657eff4b5de6fe4767854f`

All five remote file checks returned `OK`. The [staging helper](../../../../scripts/labelfix/s8_fetch_stage.py) can reproduce the bundle/deployment/dry run, and contains no real submission path:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD \
  /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B \
  scripts/labelfix/s8_fetch_stage.py --bundle /tmp/s8a3_bundle \
  --deploy-test-only \
  --log docs/records/labelfix/spellcheck/S8_DEV/evidence/S8a3/deploy_test_only.json
```

SSH uses only `clariden` through its configured Ela jump. Each operation permits **at most three total attempts**, with **5 s / 15 s backoff** only for recognized transient transport failures. Authentication/certificate/host-key errors stop immediately, without refresh. Every remote operation here succeeded on its first attempt; no certificate was refreshed. The payload is rechecked before starting the compute step.

Final dry-run command executed remotely:

```bash
sbatch --test-only --uenv-passthrough=ignore \
  --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/job \
  /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/job/scripts/labelfix/clariden/s8_fetch_job.sbatch
```

Exit status **0**, exact scheduler output:

```text
sbatch: Job 3680434 to start at 03:35:31 a using 288 processors on nodes nid006295 in partition debug
```

This is test-only output, not a submitted job ID or reservation. [Raw final transport/dry-run log](S8_DEV/evidence/S8a3/deploy_test_only.json).

## Coordinator commands — prepared, not executed

Exact submit command:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=10 \
  -o ServerAliveCountMax=2 -o StrictHostKeyChecking=yes clariden \
  'sbatch --uenv-passthrough=ignore --chdir=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/job /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/job/scripts/labelfix/clariden/s8_fetch_job.sbatch'
```

After confirmed job success, pull from the repository root:

```bash
scp -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes \
  clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/remote.json.gz \
  docs/records/labelfix/spellcheck/S8_DEV/evidence/remote.json.gz

scp -o BatchMode=yes -o ConnectTimeout=15 -o StrictHostKeyChecking=yes \
  clariden:/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_l1_20261017/s8_dev_extract/receipt.json \
  docs/records/labelfix/spellcheck/S8_DEV/evidence/S8a3/remote_receipt.json
```

Check the pulled payload SHA against the successful receipt's `remote_sha256`, its request SHA against the verified value above, and the 600/600 populations before using it. The receipt destination avoids overwriting the existing S8 evidence receipt. DEV baseline/cards remain outside S8a3's preparation scope. Unrelated reader files appearing under `S8_DEV/audit_private/` during this task were left untouched.

S8a3 READY: resume from 863/973 B/E (brief denominator; live 863/974); mock ok; deploy sha256 73d5133ffdc057d71f65e76a9e37ed05a02d38422d657eff4b5de6fe4767854f/73d5133ffdc057d71f65e76a9e37ed05a02d38422d657eff4b5de6fe4767854f; test-only sbatch: Job 3680434 to start at 03:35:31 a using 288 processors on nodes nid006295 in partition debug; est 8 min
