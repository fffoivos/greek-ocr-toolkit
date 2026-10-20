#!/bin/sh
# Usage: launch_detached.sh OUTPUT_ROOT [global run.py args] run --tranche W1 ...
# Environment is inherited in memory. No env dumps, tokens or shell tracing.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
OUT=$1
shift
mkdir -p "$OUT"
OUT=$(CDPATH= cd -- "$OUT" && pwd)
for F in collector.pid collector.worker.pid; do
  if [ -s "$OUT/$F" ]; then
    PID=$(cat "$OUT/$F")
    if kill -0 "$PID" 2>/dev/null; then
      echo "Collector already running ($F): $PID" >&2
      exit 1
    fi
  fi
done
PYTHON=${COLLECT_V3_PYTHON:-python3}
# Python starts a new session on both macOS and Linux, ignores SIGHUP and
# supervises stdout through the scrubber before anything reaches the log.
nohup "$PYTHON" "$ROOT/collect_v3/detach.py" "$OUT" "$ROOT" "$@" </dev/null >/dev/null 2>&1 &
echo "$!" > "$OUT/collector.pid"
echo "Collector PID $!; log $OUT/collector.log"
