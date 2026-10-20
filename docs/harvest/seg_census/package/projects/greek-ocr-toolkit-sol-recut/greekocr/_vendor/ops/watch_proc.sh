#!/bin/bash
# watch_proc.sh - watch ONE local long-running process (a codex/claude review, a local build) and emit an event line on
# every state that matters. Built to be the command of a Monitor (one line = one notification) or a run_in_background job.
#   watch_proc.sh --label L --pid PID --log FILE [--out FILE] [--done-regex RE] [--fail-regex RE]
#                 [--stall-min 15] [--max-min 180] [--poll-sec 20] [--progress-min 10]
# Events (stdout, one line each, prefixed "[L]"):
#   START        what is being watched, and the pid's command line (proves the pid is the right process)
#   PROGRESS     every --progress-min: elapsed, log bytes, growth since last PROGRESS (a heartbeat: silence = watcher dead)
#   STALL        pid alive but the log has not grown for --stall-min (NOT killed: inspect the trace first)
#   DONE         pid exited AND --out is non-empty AND (if given) --done-regex matches the out file; prints the match
#   FAILED       pid exited without that (no/empty out, done-regex missing, or --fail-regex seen in log/out); prints log tail
#   TIMEOUT      --max-min reached with the pid still alive (NOT killed)
# Exit codes: 0 DONE, 1 FAILED, 2 TIMEOUT, 3 STALL (exits on the first STALL so it cannot be missed), 4 bad arguments.
# Never kills anything. Needs no network. bash 3.2 compatible (macOS /bin/bash).
set -u
LABEL=""; PID=""; LOG=""; OUT=""; DONE_RE=""; FAIL_RE="Traceback|Error:|ERROR|panicked|Killed|No space left|unauthorized|rate limit|usage limit"
STALL=15; MAX=180; POLL=20; PROG=10
while [ $# -gt 0 ]; do case "$1" in
  --label) LABEL=$2; shift 2;; --pid) PID=$2; shift 2;; --log) LOG=$2; shift 2;; --out) OUT=$2; shift 2;;
  --done-regex) DONE_RE=$2; shift 2;; --fail-regex) FAIL_RE=$2; shift 2;; --stall-min) STALL=$2; shift 2;;
  --max-min) MAX=$2; shift 2;; --poll-sec) POLL=$2; shift 2;; --progress-min) PROG=$2; shift 2;;
  --stall-sec) STALL_S=$2; shift 2;;   # test hook: stall threshold in seconds
  *) echo "[?] bad argument $1"; exit 4;; esac; done
[ -n "$LABEL" ] && [ -n "$PID" ] && [ -n "$LOG" ] || { echo "[?] need --label --pid --log"; exit 4; }
say(){ echo "[$LABEL] $(date '+%H:%M:%S') $*"; }
sz(){ [ -f "$1" ] && wc -c < "$1" | tr -d ' ' || echo 0; }
alive(){ kill -0 "$PID" 2>/dev/null; }
T0=$(date +%s); last_grow=$T0; last_size=$(sz "$LOG"); last_prog=$T0; prog_size=$last_size
if alive; then say "START pid $PID ($(ps -o command= -p "$PID" 2>/dev/null | cut -c1-120)) log $LOG ($last_size B)"
else say "START pid $PID is ALREADY GONE - evaluating its outputs now"; fi
while :; do
  now=$(date +%s); el=$(( (now - T0) / 60 ))
  if ! alive; then
    o=$(sz "${OUT:-/dev/null}")
    if [ -n "$OUT" ] && [ "$o" -gt 0 ] && { [ -z "$DONE_RE" ] || grep -qE "$DONE_RE" "$OUT"; }; then
      say "DONE after ${el}m: out $OUT ($o B) $( [ -n "$DONE_RE" ] && grep -oE "$DONE_RE.*" "$OUT" | tail -1 | cut -c1-200)"; exit 0
    fi
    say "FAILED after ${el}m: pid gone, out '${OUT:-<none>}' $o B$( [ -n "$DONE_RE" ] && echo ", done-regex '$DONE_RE' not found")"
    tail -5 "$LOG" 2>/dev/null | sed "s/^/[$LABEL]   log: /" | cut -c1-220
    exit 1
  fi
  s=$(sz "$LOG"); [ "$s" != "$last_size" ] && { last_size=$s; last_grow=$now; }
  hit=$(grep -oE "$FAIL_RE" "$LOG" 2>/dev/null | sort -u | head -3 | tr '\n' ' ')
  [ -n "$hit" ] && [ -z "${warned:-}" ] && { warned=1; say "WARN failure signature in log while running: $hit(continuing; check the log)"; }
  if [ $(( now - last_grow )) -ge ${STALL_S:-$(( STALL * 60 ))} ]; then
    say "STALL: pid $PID alive but $LOG unchanged for $(( (now - last_grow) / 60 ))m (size $s B). Inspect the trace; do not kill blindly."; exit 3
  fi
  [ "$el" -ge "$MAX" ] && { say "TIMEOUT at ${el}m: pid $PID still alive (not killed)"; exit 2; }
  if [ $(( now - last_prog )) -ge $(( PROG * 60 )) ]; then say "PROGRESS ${el}m, log $s B (+$(( s - prog_size )) B)"; last_prog=$now; prog_size=$s; fi
  sleep "$POLL"
done
