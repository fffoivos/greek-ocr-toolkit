#!/bin/bash
# watch_slurm.sh - watch a set of Slurm jobs over ssh and emit one event line per STATE CHANGE, plus a terminal summary.
#   watch_slurm.sh --host ALIAS --jobs ID[,ID...] [--poll-sec 240] [--max-min 240] [--lost-after 4] [--progress-min 30]
# Every ssh call has ConnectTimeout + ServerAliveInterval and is wrapped so a hung login node cannot hang the watcher.
# Events (prefixed "[slurm]"): START (initial states), CHANGE job old->new (incl. PENDING reason changes), PROGRESS heartbeat,
#   JOB_FAILED (any FAILED/CANCELLED/TIMEOUT/OUT_OF_MEMORY/NODE_FAIL/PREEMPTED/BOOT_FAIL/DEADLINE, or a PENDING reason
#   DependencyNeverSatisfied - which never resolves on its own), ALL_DONE (every job COMPLETED), LOST (--lost-after
#   consecutive polls without an answer), TIMEOUT.
# Exit codes: 0 ALL_DONE, 1 JOB_FAILED, 2 TIMEOUT, 5 LOST, 4 bad arguments. Never cancels anything. bash 3.2 compatible.
set -u
HOST=""; JOBS=""; POLL=240; MAX=240; LOSTN=4; PROG=30
while [ $# -gt 0 ]; do case "$1" in
  --host) HOST=$2; shift 2;; --jobs) JOBS=$2; shift 2;; --poll-sec) POLL=$2; shift 2;; --max-min) MAX=$2; shift 2;;
  --lost-after) LOSTN=$2; shift 2;; --progress-min) PROG=$2; shift 2;; *) echo "[slurm] bad argument $1"; exit 4;; esac; done
[ -n "$HOST" ] && [ -n "$JOBS" ] || { echo "[slurm] need --host --jobs"; exit 4; }
say(){ echo "[slurm] $(date '+%H:%M:%S') $*"; }
q(){  # one bounded query: sacct for state, squeue for the pending reason; the local watchdog kills a hung ssh after 90 s
  ( ssh -o BatchMode=yes -o ConnectTimeout=15 -o ServerAliveInterval=10 -o ServerAliveCountMax=3 "$HOST" \
      "sacct -X -n -P -j $JOBS -o JobID,JobName,State,Elapsed; echo __SQ__; squeue -h -j $JOBS -o '%i|%r' 2>/dev/null" 2>/dev/null ) &
  # the watchdog must NOT inherit stdout: inside $(q) a child holding the pipe open blocks the substitution until it exits
  # (found in testing: every poll took the full 90 s)
  local p=$!; ( sleep 90; kill $p 2>/dev/null ) >/dev/null 2>&1 & local w=$!; wait $p 2>/dev/null; local rc=$?
  kill $w 2>/dev/null; return $rc; }
T0=$(date +%s); last_prog=$T0; miss=0; prev=""
while :; do
  el=$(( ($(date +%s) - T0) / 60 ))
  R=$(q); if [ -z "$R" ]; then miss=$((miss+1)); [ $miss -ge $LOSTN ] && { say "LOST: $miss consecutive polls without an answer from $HOST (try another login node)"; exit 5; }
  else
    miss=0
    ST=$(echo "$R" | sed '/__SQ__/,$d' | awk -F'|' 'NF>=3{print $1"|"$2"|"$3}' | sed 's/CANCELLED by [0-9]*/CANCELLED/')
    RS=$(echo "$R" | sed '1,/__SQ__/d')
    CUR=$(echo "$ST" | while IFS='|' read -r id nm st; do r=$(echo "$RS" | awk -F'|' -v i="$id" '$1==i{print $2}'); echo "$id|$nm|$st${r:+ ($r)}"; done | sort)
    if [ -z "$prev" ]; then say "START $(echo "$CUR" | tr '\n' ';')"
    else echo "$CUR" | while read -r line; do id=${line%%|*}; old=$(echo "$prev" | grep "^$id|"); [ "$line" != "$old" ] && say "CHANGE ${old:-$id|?} -> ${line#*|}"; done; fi
    prev=$CUR
    bad=$(echo "$CUR" | grep -E "FAILED|CANCELLED|TIMEOUT|OUT_OF_ME|NODE_FAIL|PREEMPTED|BOOT_FAIL|DEADLINE|DependencyNeverSatisfied")
    [ -n "$bad" ] && { say "JOB_FAILED: $(echo "$bad" | tr '\n' ';')"; exit 1; }
    n=$(echo "$CUR" | grep -c .); c=$(echo "$CUR" | grep -c "|COMPLETED")
    [ "$n" -gt 0 ] && [ "$n" = "$c" ] && { say "ALL_DONE: $n jobs COMPLETED"; exit 0; }
  fi
  [ "$el" -ge "$MAX" ] && { say "TIMEOUT at ${el}m (jobs not all terminal; nothing cancelled)"; exit 2; }
  [ $(( $(date +%s) - last_prog )) -ge $(( PROG * 60 )) ] && { say "PROGRESS ${el}m $(echo "$prev" | awk -F'|' '{print $1":"$3}' | tr '\n' ' ')"; last_prog=$(date +%s); }
  sleep "$POLL"
done
