#!/usr/bin/env bash
# Coordinator only: run with nohup from the verified deployment's checkout root.
# Serial --wait submissions use one debug slot; no queued fan-out, tokens or Slurm retries.
set -euo pipefail
out= work= log=
while (($#)); do
    case "$1" in
        --out) out=$2; shift 2;;
        --work) work=$2; shift 2;;
        --log) log=$2; shift 2;;
        --) shift; break;;
        *) echo 'usage: debug_chain.sh --out PATH --work PATH --log PATH -- BUILDER_FLAGS...' >&2; exit 2;;
    esac
done
[[ -n "$out" && -n "$work" && -n "$log" ]] || exit 2
for arg in "$@"; do
    case "$arg" in
        --out|--out=*|--work|--work=*|--resume|--deadline-seconds|--deadline-seconds=*|--smoke|--smoke=*|--measure|--freeze|--plan|--independent-readback)
            echo "chain owns or disallows builder argument: $arg" >&2; exit 2;;
    esac
done
P=${REL0_DATASET_PYTHON:-/capstor/scratch/cscs/fffoivos/greek-ocr-e3/venv/bin/python}
mkdir -p -- "$(dirname -- "$log")" "$(dirname -- "$work")"
exec 9>"$work.chain.lock"
flock -n 9 || { echo 'another chain holds this work directory' >&2; exit 1; }
previous= stagnant=0 before=none
if [[ -f "$work/RUN_STATUS.json" ]]; then
    read -r _ before _ < <("$P" -m scripts.release_v0_dataset.chain_status "$work")
fi
while :; do
    resume=(); dependency=()
    [[ ! -f "$work/BINDING.json" ]] || resume=(--resume)
    [[ -z "$previous" ]] || dependency=(--dependency="afterok:$previous")
    # 85 minutes for the entire job, 80 minutes inside Python: 5 minutes for
    # startup, rollback/closing and srun teardown. PAUSED exits with status zero.
    set +e
    submission=$(sbatch --parsable --wait --partition=debug --time=01:25:00 \
        --job-name=HFD-P2j --output="$(dirname -- "$log")/build-%j.log" \
        "${dependency[@]}" scripts/release_v0_dataset/build.sbatch \
        "$@" --independent-readback --out "$out" --work "$work" "${resume[@]}" --deadline-seconds 4800)
    rc=$?
    set -e
    job=${submission%%;*}
    if [[ ! "$job" =~ ^[0-9]+$ ]]; then
        printf '%s job=unknown state=SUBMIT_FAILED rc=%s status=FAILED progress=none\n' "$(date -Is)" "$rc" >> "$log"
        exit 1
    fi
    state=
    for ((i=0; i<30; i++)); do
        state=$(sacct -n -X -j "$job" --format=State --parsable2 | head -n 1 | cut -d '|' -f 1) || state=
        [[ -z "$state" || "$state" == RUNNING || "$state" == PENDING || "$state" == COMPLETING ]] || break
        sleep 2
    done
    status=FAILED progress=none final=0
    if [[ -f "$work/RUN_STATUS.json" ]] && "$P" -m scripts.release_v0_dataset.chain_status "$work" --job-id "$job" >/dev/null; then
        read -r status progress final < <("$P" -m scripts.release_v0_dataset.chain_status "$work" --job-id "$job")
    fi
    printf '%s job=%s state=%s rc=%s status=%s progress=%s\n' "$(date -Is)" "$job" "${state:-UNKNOWN}" "$rc" "$status" "$progress" >> "$log"
    [[ "$rc" == 0 && "$state" == COMPLETED && "$status" != FAILED ]] || exit 1
    [[ "$status" != COMPLETE || "$final" != 1 ]] || exit 0
    [[ "$status" == PAUSED ]] || exit 1
    if [[ "$progress" == "$before" ]]; then stagnant=$((stagnant+1)); else stagnant=0; fi
    ((stagnant < 2)) || exit 1
    before=$progress previous=$job
done
