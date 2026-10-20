"""Bounded read-only watches. Every terminal state emits a liveness line."""
from __future__ import annotations
from dataclasses import dataclass
import math
import subprocess
import time
from typing import Callable, Literal, Sequence
__all__ = ['Observation', 'WatchResult', 'watch', 'bounded_ssh']
State = Literal['DONE', 'FAILED', 'STALL', 'TIMEOUT', 'LOST']

@dataclass(frozen=True)
class Observation:
    alive: bool
    log_bytes: int
    done: bool = False
    failed: bool = False

@dataclass(frozen=True)
class WatchResult:
    state: State
    polls: int
    elapsed_s: float


def watch(label: str, probe: Callable[[], Observation], *, max_seconds: float = 1800,
          stall_seconds: float = 900, poll_seconds: float = 20, lost_after: int = 4,
          emit: Callable[[str], None] = print, clock: Callable[[], float] = time.monotonic,
          sleep: Callable[[float], None] = time.sleep) -> WatchResult:
    """Caller probes must also be bounded; growth measures liveness, never kills."""
    if any(not math.isfinite(v) or v <= 0 for v in (max_seconds, stall_seconds, poll_seconds)) or lost_after < 1:
        raise ValueError('positive finite watch bounds and lost_after required')
    start = progress = clock()
    last_bytes = -1
    failures = polls = 0
    emit(f'START {label}')
    def finish(state: State) -> WatchResult:
        emit(f'{state} {label} polls={polls}')
        return WatchResult(state, polls, clock()-start)
    while True:
        if clock()-start >= max_seconds: return finish('TIMEOUT')
        polls += 1
        try:
            current = probe()
            failures = 0
        except Exception:
            failures += 1
            if failures >= lost_after: return finish('LOST')
        else:
            if current.failed: return finish('FAILED')
            if current.done: return finish('DONE')
            if not current.alive: return finish('FAILED')
            if current.log_bytes != last_bytes:
                progress, last_bytes = clock(), current.log_bytes
            elif clock()-progress >= stall_seconds: return finish('STALL')
            emit(f'PROGRESS {label} log_bytes={current.log_bytes}')
        sleep(min(poll_seconds, max(0, max_seconds-(clock()-start))))


def bounded_ssh(host: str, command: Sequence[str], *, timeout: float = 45) -> subprocess.CompletedProcess[str]:
    """Batch SSH with connection bound, keepalive and a local process timeout."""
    import shlex
    if not host or host.startswith('-'): raise ValueError('explicit SSH host required')
    return subprocess.run(['ssh', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=15', '-o',
                           'ServerAliveInterval=10', '-o', 'ServerAliveCountMax=3', host,
                           shlex.join(command)], text=True, capture_output=True, check=True, timeout=timeout)
