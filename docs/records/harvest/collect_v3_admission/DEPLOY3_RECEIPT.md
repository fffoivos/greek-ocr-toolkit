# DEPLOY3 receipt

Recorded 2026-10-20T00:43:57+03:00. Deployment and the 200-row login-node check succeeded. No jobs or allocations were submitted; no paid services, commits or pushes were used. Network access was limited to `ssh clariden` and `rsync`.

## Source and payload

HEAD: `f8c23ee4ef16295c1c3b385119913dfb6c684e86` (BENCH02I). `git merge-base --is-ancestor f8c23ee4e HEAD` exited 0. Before changes, `git status --porcelain --untracked-files=all -- <all 12 DEPLOY_PATHS entries>` returned no output. Unrelated dirty/untracked paths were preserved.

Runtime dependency review: `run_census05_draw.sh` invokes `bench02_draw.py` directly; it does not invoke `run_ruled_draw.py`. The deployed Python tool uses the standard library. No runtime additions or changes to DEPLOY_PATHS were needed. Only DEPLOY_SHA256SUMS was regenerated; the manifest excludes itself. The package SHA is SHA256 of the manifest bytes.

Following DEPLOY2's working-tree archive method, the exact 12-path payload was copied into a temporary Git repository and archived from tree `aa8975863aa786830a5e14e2c95b4dc8adcf8425` with no commit. Repository-relative layout was preserved. Archive payload: `/private/tmp/deploy3-s1_vgewy/payload`.

Root: `/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/0019ce4b`

Deploy SHA256: `0019ce4b55222400e5539838f828440364e4c439be2423c4c748a7a07bc2762a`

Exclusive `mkdir` followed checks that the root was neither present nor a symlink. Transfer used `rsync -a --ignore-existing`; no deletion option was used. Existing deployment roots were untouched. Remote writes were confined to the new package root and a fresh temporary check directory under `$W/filter_pipeline_20261018/bench02/deploy3_check/`. The check inputs and outputs were retained.

## All per-file hashes, read back from Clariden

Every remote hash below was compared with local bytes and matched, including DEPLOY_SHA256SUMS. Readback exited 0.

```bash
set -eu
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/0019ce4b
sha256sum docs/harvest/collect_v3_admission/bench02/bench02_draw.py docs/harvest/collect_v3_admission/bench02/extract.sbatch docs/harvest/collect_v3_admission/bench02/readout.sbatch docs/harvest/collect_v3_admission/bench02/job_common.sh docs/harvest/collect_v3_admission/bench02/submit_job.sh docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh docs/harvest/collect_v3_admission/bench02/BRIEF.md docs/harvest/collect_v3_admission/bench02/BENCH02D.md docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md docs/harvest/collect_v3_admission/bench02/VERIFY.sh docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS
```

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
7cb76e3a16e2a00a588b71c872fd59f00739e65fa56fca1b132a241910b50582  docs/harvest/collect_v3_admission/bench02/bench02_draw.py
077fbfbc120ed205b80abc8e33c6020892621867566f1cff84671521e0174160  docs/harvest/collect_v3_admission/bench02/extract.sbatch
7fd6e98de83ac3ed696989bbafc54782ad386ab5465ed9f570935f54bd0f2b7a  docs/harvest/collect_v3_admission/bench02/readout.sbatch
2378d662d3ad28adb227785ff6ef4bd65c2de77587ae9a51acda0ab79097fc7d  docs/harvest/collect_v3_admission/bench02/job_common.sh
7891484293752e0beca5c8665c1126649ebf62447bffbd82ab9d807b20ed9ece  docs/harvest/collect_v3_admission/bench02/submit_job.sh
a61205ca16a2ae15bc73c8367ea8a12a6e69e94b2986da5971d99a076a17775a  docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh
90ef155eec4946a00e39c32b2d439feb69c2a5ffd9d8a04f9c37f980ef0b3f12  docs/harvest/collect_v3_admission/bench02/BRIEF.md
3a4432cf84e87a85b070220bc5e9f4f279938ead303fe1e5f3834d80df0be98e  docs/harvest/collect_v3_admission/bench02/BENCH02D.md
e371edebbf8eb290e54b7c5afc1c0878c843e3920cffca98411dc089ac2f9cc7  docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md
3040f02c64358e07c652b65ea4d114cc86ff9c646f82cd9ad4e6aee7f23a8bd9  docs/harvest/collect_v3_admission/bench02/VERIFY.sh
ec88690eefec1831e4ec17885055726c383ce83d4f34b79214bea911b8f08702  docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt
0019ce4b55222400e5539838f828440364e4c439be2423c4c748a7a07bc2762a  docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS
```

## Step 3: VERIFY

Command supplied to `ssh -o BatchMode=yes -o ConnectTimeout=15 clariden bash -s` (exit 0):

```bash
set -eu
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/0019ce4b
bash docs/harvest/collect_v3_admission/bench02/VERIFY.sh /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/attempts/census_03/current
```

Verbatim combined stdout/stderr:

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
docs/harvest/collect_v3_admission/bench02/bench02_draw.py: OK
docs/harvest/collect_v3_admission/bench02/extract.sbatch: OK
docs/harvest/collect_v3_admission/bench02/readout.sbatch: OK
docs/harvest/collect_v3_admission/bench02/job_common.sh: OK
docs/harvest/collect_v3_admission/bench02/submit_job.sh: OK
docs/harvest/collect_v3_admission/bench02/run_census05_draw.sh: OK
docs/harvest/collect_v3_admission/bench02/BRIEF.md: OK
docs/harvest/collect_v3_admission/bench02/BENCH02D.md: OK
docs/harvest/collect_v3_admission/bench02/run_dryrun_census03.md: OK
docs/harvest/collect_v3_admission/bench02/VERIFY.sh: OK
docs/harvest/collect_v3_admission/bench02/DEPLOY_PATHS.txt: OK
usage: bench02_draw.py [-h] {extract,readout,draw} ...

Offline BENCH02 draw, slim extraction and candidate readout (Python >=3.10).

positional arguments:
  {extract,readout,draw}

options:
  -h, --help            show this help message and exit
VERIFY_OK bench02 0019ce4b
```

## Step 4: 200-row extract and receipt checksum

Only `head -n 200` from each original input was read for extraction. The venv_l1 interpreter ran extract on those two small files. Assertions confirmed exactly 200 decisions, 200 diagnostics, 200 tags, matching receipt SHA256 and matching byte count. No larger extract or draw was run.

Command supplied to `ssh -o BatchMode=yes -o ConnectTimeout=15 clariden bash -s` (exit 0):

```bash
set -euo pipefail
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
CENSUS="$W/filter_pipeline_20261018/attempts/census_03/current"
BASE="$W/filter_pipeline_20261018/bench02/deploy3_check"
mkdir -p "$BASE"
CHECK=$(mktemp -d "$BASE/0019ce4b.XXXXXXXX")
printf 'CHECK_/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/0019ce4b %s
' "$CHECK"
head -n 200 "$CENSUS/decisions.jsonl" > "$CHECK/decisions.jsonl"
head -n 200 "$CENSUS/evaluation_diagnostics.jsonl" > "$CHECK/evaluation_diagnostics.jsonl"
wc -l "$CHECK/decisions.jsonl" "$CHECK/evaluation_diagnostics.jsonl"
test "$(wc -l < "$CHECK/decisions.jsonl")" -eq 200
test "$(wc -l < "$CHECK/evaluation_diagnostics.jsonl")" -eq 200
mkdir "$CHECK/output"
"$W/venv_l1/bin/python" -B /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/0019ce4b/docs/harvest/collect_v3_admission/bench02/bench02_draw.py extract --decisions "$CHECK/decisions.jsonl" --diagnostics "$CHECK/evaluation_diagnostics.jsonl" --output-dir "$CHECK/output"
cat "$CHECK/output/tags.jsonl.receipt.json"
printf '
'
sha256sum "$CHECK/output/tags.jsonl.gz"
"$W/venv_l1/bin/python" -B - "$CHECK" <<'PYREMOTE'
import json,sys,subprocess,gzip
from pathlib import Path
p=Path(sys.argv[1]); tags=p/'output/tags.jsonl.gz'
r=json.loads((p/'output/tags.jsonl.receipt.json').read_text())
actual=subprocess.check_output(['sha256sum',str(tags)],text=True).split()[0]
assert r['tags_sha256']==actual,(r['tags_sha256'],actual)
assert r['tags_bytes']==tags.stat().st_size
assert r['decisions']==200 and r['diagnostics']==200,r
with gzip.open(tags,'rt') as f: count=sum(1 for _ in f)
assert count==200,count
print('RECEIPT_SHA256_OK',actual)
print('TINY_EXTRACT_OK decisions=200 diagnostics=200 tags=200')
PYREMOTE
```

Verbatim combined stdout/stderr (the expanded `CHECK_...` label is cosmetic and is preserved exactly):

```text
** WARNING: connection is not using a post-quantum key exchange algorithm.
** This session may be vulnerable to "store now, decrypt later" attacks.
** The server may need to be upgraded. See https://openssh.com/pq.html
CHECK_/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/0019ce4b /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/deploy3_check/0019ce4b.NCWmknZu
    200 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/deploy3_check/0019ce4b.NCWmknZu/decisions.jsonl
    200 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/deploy3_check/0019ce4b.NCWmknZu/evaluation_diagnostics.jsonl
    400 total
{
  "code_sha": "7cb76e3a16e2a00a588b71c872fd59f00739e65fa56fca1b132a241910b50582",
  "decision_join_rate": 1.0,
  "decisions": 200,
  "diagnostic_join_rate": 1.0,
  "diagnostics": 200,
  "diagnostics_unmatched": 0,
  "input_shas": {
    "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/deploy3_check/0019ce4b.NCWmknZu/decisions.jsonl": "afca0f22277fdc34c1e586c7fbd427eca580e153382e375ed2277358d759b8cf",
    "/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/deploy3_check/0019ce4b.NCWmknZu/evaluation_diagnostics.jsonl": "1ca74962c0436d0c9d0d1ad73b0185d7ac9e254371b6a772b53fb437b75eb7d6"
  },
  "joined": 200,
  "tags_bytes": 22818,
  "tags_sha256": "1d22012126645c79e26e73f65b098445646f5dc9983637b362ff5ecddfe4aa25"
}

1d22012126645c79e26e73f65b098445646f5dc9983637b362ff5ecddfe4aa25  /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02/deploy3_check/0019ce4b.NCWmknZu/output/tags.jsonl.gz
RECEIPT_SHA256_OK 1d22012126645c79e26e73f65b098445646f5dc9983637b362ff5ecddfe4aa25
TINY_EXTRACT_OK decisions=200 diagnostics=200 tags=200
```

## census_05 extract submission handoff

Exact submission line with the new deployed root, for the coordinator to execute later. **Documentation only; not executed.** This wrapper exports the deployed BENCH02_DIR, supplies the absolute Slurm output path and uses `$W/venv_l1/bin/python` through job_common.sh. Census_05 readiness and output-directory state were not checked by this deployment task.

```bash
export W=/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3
cd /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/0019ce4b && bash docs/harvest/collect_v3_admission/bench02/submit_job.sh extract "$W/filter_pipeline_20261018/attempts/census_05/current" "$W/filter_pipeline_20261018/bench02/census05"
```

## Files to commit (2)

- `docs/harvest/collect_v3_admission/bench02/DEPLOY_SHA256SUMS`
- `docs/harvest/collect_v3_admission/DEPLOY3_RECEIPT.md`

No staging or commit was performed. DEPLOY_PATHS.txt is unchanged; BENCH02I runtime changes are already in HEAD. The supplied DEPLOY3 brief and unrelated worktree changes are excluded from this handoff.

DEPLOY3: done | bench02 /iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018/bench02_pkg/0019ce4b VERIFY_OK 0019ce4b | receipt sha check on 200 rows ok | no jobs submitted | files to commit 2
