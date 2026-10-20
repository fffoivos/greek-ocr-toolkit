# W1e: remote bootstrap of the collect_v3 worker box over SSH (gpt-6.1-sol, xhigh, network ON for the box, package sources and python.org only; no OCR spend; ≤ 90 min)

**Fill in before launch.** Replace these placeholders with the values the owner gives the coordinator:

| Placeholder | Meaning |
|---|---|
| `<BOX_HOST>` | SSH host or alias |
| `<SSH_USER>` | login user |
| `<SSH_KEY>` | key path, if not the default |

**Box.** Fresh Debian 12, x86_64, ≥80 GB disk, no GPU. It was created by the owner for this collection only.

**Local side.** This worktree (`~/Projects/greek-ocr-toolkit-sol-collect`, branch `sol/collect-v3`, W1d 04f9367f/53ca565c). Read `worker/README_WORKER.md` first; it is the procedure. Keep the kit as is, and fix only what fails on real Linux, as a minimal, tested change.

## Scope: steps 1–4 and 6 of README_WORKER, never step 7

1. **Transfer and verify.** scp `worker/handoff/collect-v3-w1d-final.tar.gz` (sha256 `7fdbf4885046d641e9e068792ab5a2dbf66e236cc05991c33585f610469490db`) to the box. Extract it to `/srv/collect-v3` and run `sha256sum --check HANDOFF_SHA256SUMS`.
2. **System packages.** `bash worker/system_packages.sh`, using the box's Debian apt mirrors.
3. **Exact Python.**
   - Download the official CPython 3.11.3 source tarball from python.org on the box.
   - Verify it against python.org's published SHA-256 (record the value and its source URL in the receipt).
   - Run `sudo bash worker/install_python.sh <tarball> '<SHA256>' /opt/collect-v3-python`.
4. **Wheelhouse.** On the box, using a throwaway venv: `pip download --only-binary=:all:` against `requirements.lock`, then `wheels.py --seal`. PyPI is the only index.
5. **Bootstrap.** Set the paths first:
   `COLLECT_V3_OUTPUT_ROOT=/srv/collect-v3-data/run`
   `COLLECT_V3_LIMITER_ROOT=/srv/collect-v3-data/shared-limiter`

   Then run `bash worker/bootstrap.sh`: offline tests and parity with sockets and DNS blocked, then preflight.
   - **The credential check depends on the coordinator's option.**
     - **If option A was chosen:** the coordinator places the ADC file at a 600 path outside the checkout, for example `/run/collect-secrets/creds.json`, and tells you its path. Export `GOOGLE_APPLICATION_CREDENTIALS` to it only inside the preflight command's environment.
     - **If option B was chosen,** or nothing is placed yet: run preflight with the credential check reported as `pending_owner_credential`. Never fabricate a credential to make it pass.

## Rules (the same as on the Mac)

| Area | Rule |
|---|---|
| Credentials | Never print, echo, cat, log, copy or `env`-dump the values of `GOOGLE_APPLICATION_CREDENTIALS`, `COLLECT_V3_ACCESS_TOKEN` or the ADC file. Check only that a variable is set and that the file is mode 600 and outside the checkout and data trees. |
| Files | No secrets in the checkout, the receipts or this worktree. |
| Network | Only SSH to the box; the box reaches the apt mirrors, python.org (CPython source) and PyPI (wheel download). No collection source host and no Google OCR endpoint is contacted. Preflight DNS checks are resolution only. |
| Launch | **Do not run `launch_w1.sh`, or anything that reads, OCRs or spends.** Step 7 waits for the owner's spend go, which the coordinator relays. |
| Box use | Do not modify the box beyond the README's prescribed paths, plus the apt packages it lists. |

## Receipts

Copy back to `docs/records/harvest/collect_v3/worker_receipts/<BOX_HOST>/`:
- the handoff checksum result;
- the apt package list with versions;
- the Python build log tail and version;
- the CPython source SHA-256 and its source;
- the wheelhouse seal (`SHA256.json`);
- the bootstrap test summary and parity result;
- the preflight JSON, with the credential state as `set`, `missing` or `pending_owner_credential` and no values;
- disk free;
- `uname -a`.

## Hand-off

`docs/records/harvest/collect_v3/worker_receipts/<BOX_HOST>/BOOTSTRAP.md` must hold:
- what passed;
- any kit fix made, with its diff;
- the exact remaining steps: credential, if pending, and the step-7 launch command.

Commit with the guarded helper; it excludes ignored paths. The last line must be exactly:

`W1e: done | box: <BOX_HOST> | python: 3.11.3 <ok> | wheels sealed: <n> | tests: <n> passed parity: <ok> | preflight: <ok|pending_owner_credential> | launched: no`
