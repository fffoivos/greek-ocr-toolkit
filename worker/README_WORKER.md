# collect_v3 Linux worker

W1d is an offline build. No worker was provisioned, no source was contacted, no OCR was purchased, and no collection was launched. Launch remains the owner's separate decision. Use a fresh worker box, never the Mac or the host named `home`.

Supported runtime: **Linux x86_64, CPython 3.11.3 exactly**. The package/bootstrap logic targets the **Debian family (Debian 12)**. Shell syntax and failure paths, preflight, resume, sync and offline parity are tested locally with injected Linux/disk/DNS facts; an actual Linux installation and live DNS remain untested. This is explicit qualification work for the owner's new box, not evidence that the box already exists.

## Disk and system prerequisites

Provide **at least 60,000,000,000 bytes total and free** on every output/cache/limiter filesystem at launch. A nominal 60 GB disk cannot have 60 GB free after the OS; provision enough additional capacity (80 GB or more is practical). Use local POSIX storage supporting flock, fsync, atomic rename, hardlinks and SQLite WAL. Linux `/proc` must be mounted for PID identity/status. One worker/collector at a time; keep the limiter directory across restarts and W1/W2, never reset it to evade the rolling MDZ cap. The output and cache share a filesystem. No GPU, CUDA, browser, Keychain, Docling or model download is required.

W1c's full 6,850-page projection was **17.32 GB retained**, **30.46 GB peak working set**, and **30.64 GB regenerable derivatives**. W1d's source-weighted update is **17.40 GB retained / 30.73 GB peak / 30.52 GB regenerable**, recorded in `docs/harvest/collect_v3/retention_projection.json`; it is a forecast from three cached F2 pages/source, not measured collection size. The default retains one raster, raw Google line/token/symbol geometry and page/hash/route records; bulk derivatives are disposable. One 160 MB source-PDF slot and atomic finalization headroom are included. Unstable-URL PDFs add measured exception bytes. The 60 GB free check includes room for these projections, OS, fixtures, venv and review work; do not interpret the forecast as an extra allocation of 60 GB.

System packages are scripted in `system_packages.sh`: bash/coreutils/tar/gzip, Git, CA certificates, rsync, OpenSSH client, util-linux (setsid/flock), procps, libjpeg, libpng, libgomp, DejaVu fonts and CPython build prerequisites (compiler/make, OpenSSL, SQLite, zlib, bz2, readline, ffi, lzma). `pypdfium2` uses its pinned **Linux wheel with bundled libpdfium**. Pillow and headless OpenCV use wheels; no system PDFium or GUI OpenCV is installed. Missing wheels fail bootstrap rather than compiling dependencies.

## Prepare the box (owner commands, later)

All angle-bracket values are placeholders. The checkout and pre-staged assets must be on the worker. `worker/fixtures/` is a **129 MB cached proof bundle**, prepared locally without acquisition, bound by tracked `fixture_manifest.json`, and intentionally excluded from Git. Transfer this directory separately with the checkout; a Git clone alone is insufficient. `worker/prepare.py` copies hash-bound planning inputs into the runtime directory without replacing mismatched resume inputs. Original sibling worktrees are not required by tests or parity. To create a transfer archive with code, planning inputs and the verified fixture bundle (no venv, live outputs or secrets), run `python -m worker.package_handoff /path/collect-v3-handoff.tar.gz` from a prepared checkout. Extract on the box and run `sha256sum --check HANDOFF_SHA256SUMS` before bootstrap. Wheels and credentials are staged separately.

```bash
cd /srv/collect-v3
bash worker/system_packages.sh
# Owner supplies an official, independently verified CPython source archive.
sudo bash worker/install_python.sh /path/Python-3.11.3.tar.xz '<SHA256>' /opt/collect-v3-python
export COLLECT_V3_BASE_PYTHON=/opt/collect-v3-python/bin/python3.11
```

The system package script is a separate provisioning step and uses the box's configured apt repositories. The source build only reads the provided archive. Neither is invoked during W1d.

`requirements.lock` freezes all **24 direct and transitive collector/test dependencies** from the local venv's installed metadata, evaluated for Linux CPython 3.11.3. It intentionally excludes unrelated research packages in that venv. Bootstrap pip/setuptools are supplied by the pinned CPython `ensurepip`, with no upgrade. Target Linux wheels were unavailable with network off; installed Mac RECORD hashes are not wheel hashes, so no fabricated hashes are present in the lock.

On a separately authorized Linux x86_64 CPython 3.11.3 provisioning environment, prepare the wheelhouse once (this step contacts the configured package index, outside the collector runtime allowlist):

```bash
/opt/collect-v3-python/bin/python3.11 -m venv /path/wheel-prep
/path/wheel-prep/bin/python -m pip download --only-binary=:all: \
  --dest /srv/collect-v3/worker/wheelhouse -r /srv/collect-v3/worker/requirements.lock
# Seal exact wheel versions, compatible Linux tags and SHA-256 hashes.
/path/wheel-prep/bin/python /srv/collect-v3/worker/wheels.py --seal /srv/collect-v3/worker/wheelhouse
```

Alternatively stage an already verified wheelhouse plus its `SHA256.json`. No package-index access occurs in `bootstrap.sh`: it verifies every wheel hash and the lock hash before `pip install --no-index --no-deps --only-binary=:all:`. Hashes bind the delivered artifacts, not their upstream authenticity; the owner verifies provisioning inputs. Re-running bootstrap reuses the venv, checks pins and performs fresh offline proofs. A missing/incompatible wheel or fixture fails clearly.

## Credentials: environment only

Turn shell tracing off. Never put credentials in a config, command argument, repo, retained-output tree, shell startup file or log. The collector does not use Keychain or implicit ADC lookup. Preflight requires **exactly one** of the two variables. It reports only that a credential is set; it neither refreshes it nor calls HTTP.

Option A: the owner places a private ADC authorized-user or service-account JSON outside the checkout/data directories. This file is the only intentional on-box credential file. Preflight accepts these OAuth2 formats only (external-account federation/custom token hosts are outside the allowlist). Automatic refresh uses `oauth2.googleapis.com` and stays in memory; the collector never copies or rewrites the file.

```bash
set +x
unset COLLECT_V3_ACCESS_TOKEN
chmod 600 /run/collect-secrets/owner-credentials.json
export GOOGLE_APPLICATION_CREDENTIALS=/run/collect-secrets/owner-credentials.json
```

Option B: the owner obtains a fresh short-lived access token using their authorized coordinator credential flow, then pastes it into a silent prompt on the box. Token content is not entered in shell history, command arguments or a file:

```bash
set +x
unset GOOGLE_APPLICATION_CREDENTIALS
IFS= read -r -s -p 'Paste short-lived access token: ' COLLECT_V3_ACCESS_TOKEN
printf '\n'
export COLLECT_V3_ACCESS_TOKEN
```

A running process cannot inherit an updated shell variable. To refresh a token, stop gracefully, wait for `status.sh` to report `stopped`, repeat the silent prompt and relaunch W1. Keep the original run root and ledger:

```bash
bash worker/status.sh --stop
bash worker/status.sh
# Repeat the silent prompt above only after status reports stopped.
bash worker/launch_w1.sh --tranche W1
```

Do not kill the box or force SIGKILL during a paid request. Any `request_started` ledger entry lacking a saved response is **uncertain** and stops resume until coordinator/billing reconciliation; the collector never automatically rereads it. An expired token is not silently replaced by a credential file. Logs and exception text scrub both token values and the credential path; the fake-token end-to-end scrub test remains part of bootstrap.

## Bootstrap, preflight and launch

```bash
cd /srv/collect-v3
export COLLECT_V3_OUTPUT_ROOT=/srv/collect-v3-data/run
export COLLECT_V3_LIMITER_ROOT=/srv/collect-v3-data/shared-limiter
# Set one credential option above, then:
bash worker/bootstrap.sh
# Bootstrap does not launch collection. Only after the owner's launch go:
bash worker/launch_w1.sh --tranche W1
bash worker/status.sh
```

Optional `COLLECT_V3_WHEELHOUSE`, `COLLECT_V3_FIXTURE_ROOT`, `COLLECT_V3_BASE_PYTHON` and `COLLECT_V3_CONFIG` select existing inputs. Scripts default to `worker/.venv/bin/python`; `COLLECT_V3_PYTHON` selects that interpreter for launcher/status/sync and local offline verification. Output defaults to `worker/run`; cache is always `<output>/cache`; limiter defaults to `worker/limiter`. Use absolute paths and preserve them through resume. The config may override `mdz_daily_image_cap` **only when MDZ states a number**; its default remains **500 Image-API attempts per rolling 24 h**, shared across host/process/relaunch. Save the stated limit and its source with the run handoff. Per-host metadata, robots, retries and redirects retain the 1 request/s limiter and Retry-After policy.

Bootstrap runs the full collector suite and dry-run parity with sockets **and DNS blocked**, then prepares inputs and runs real preflight: Linux/architecture, exact Python, >=60 GB free, credential presence, allowlisted DNS only, writable shared limiter. No preflight HTTP or token validation occurs. To run just the offline proof on a coordination machine (no Linux installation/preflight claim):

```bash
COLLECT_V3_PYTHON=/path/to/local/venv/bin/python bash worker/bootstrap.sh --verify-only
```

The launcher starts the scrubbed Python supervisor in a new `setsid` session, disconnects stdio and ignores SIGHUP. `collector.pid` plus Linux boot/process start-time identity guards PID reuse. `launch.lock` serializes launchers; `run.lock` serializes collectors. Re-launch while alive returns `already_running`; re-launch after exit keeps the manifest-bound state, saved responses and unique-image ledger. `status.sh --stop` forwards SIGTERM to the child. During the read loop, the collector finishes its current read, saves the response/page and stops at the next page boundary before finalization. Wait for `stopped`; do not force termination while it is finishing. A stop during metadata preparation precedes paid reads. There is no automatic restart loop. Logs, exit code and state live in the output root. Only W1 is accepted by this launcher; even with a gate it cannot launch W2. Direct W2 execution requires a coordinator `c1_gate.json` with explicitly passed sources/classes and the separate launch decision; no gate is shipped.

## Runtime network allowlist

`collect_v3/egress.py` is the single exact host allowlist, enforced before provider/auth requests and on every redirect. HTTPS/443 only; user-info URLs, arbitrary hosts and proxy routing are rejected/disabled. Unlisted CDN/redirect hosts stop collection and need an explicit reviewed update. DNS preflight resolves these names only; it sends no HTTP request and does not prove service availability:

| Route | Allowed host |
|---|---|
| Internet Archive metadata, scandata, page JPEG | `archive.org` |
| BSB/MDZ IIIF metadata and Image API | `api.digitale-sammlungen.de` |
| NLG IIIF/catalogue | `digitalcollections.nlg.gr` |
| Kosmopolis OJS/catalogue/download | `kosmopolis.library.upatras.gr` |
| Lekythos | `lekythos.library.ucy.ac.cy` |
| Gazette official site/catalogue | `et.gr`, `search.et.gr` |
| Gazette's frozen official PDF host | `ia37rg02wpsa01.blob.core.windows.net` |
| ELSTAT | `dlib.statistics.gr` |
| Serbia NBS | `digitalna.nb.rs` |
| Pinned EU Document AI process endpoint | `eu-documentai.googleapis.com` |
| Google credential refresh | `oauth2.googleapis.com` |

Permit DNS to the worker's configured resolver and HTTPS to these hosts at launch. Package repositories and a later owner-selected sync destination are provisioning/transfer exceptions, not collector egress. The fixed host list was derived from frozen route/catalogue evidence without live lookups.

## Retained-output sync

The destination is supplied later, never hard-coded. Stop the collector first. Default is a dry run; `--execute` applies. Both use rsync `--checksum`; an applied transfer performs a second checksum comparison and fails if differences remain.

```bash
bash worker/status.sh --stop
bash worker/status.sh
bash worker/sync_back.sh '<DESTINATION>'
bash worker/sync_back.sh --execute '<DESTINATION>'
```

The sync holds the run/launch locks and stages hardlinks on the source filesystem. SQLite uses its backup API, so committed WAL entries are included. It copies frozen manifests/inventories/context, page records, state/resolution/route/hash receipts, a consistent ledger, shared limiter state, rasters, raw Google responses, review cards/keys/verdicts, audits and explicit unstable-PDF exceptions. Detector caches, ordinary HTTP bodies, working row exports/crops, the venv, fixtures and credentials are excluded. Card images are retained when present. No destination files are deleted. `retained_SHA256SUMS` covers every selected payload; the local `sync_receipt.json` distinguishes dry-run from executed/verified. Archive that receipt with the destination after successful verification. To verify the received payload:

```bash
cd '<RECEIVED_OUTPUT_DIRECTORY>'
sha256sum --check retained_SHA256SUMS
```

Records retain the worker's absolute runtime paths. For later regeneration, restore the tree at the same absolute output path (or mount that path to the received tree); verify checksums before any relocation. Keep the exact committed code and fixture/wheel manifests separately from run outputs. Before any continued collection on a replacement worker, restore `shared_limiter/` to its configured limiter directory without resetting timestamps. Follow `teardown_checklist.md` before deleting the box.
