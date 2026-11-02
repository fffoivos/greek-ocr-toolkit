"""Cooperative checkpoints plus an alarm: rollback unfinished work before Slurm kills it."""
from contextlib import contextmanager
from contextvars import ContextVar
import signal
import time


active_deadline = ContextVar("build_deadline", default=None)


class BuildPaused(BaseException):
    """An intentional, successful allocation handoff, never a failed build."""


class Deadline:
    def __init__(self, seconds=None):
        self.seconds = seconds
        self.ends = None
        self.expired = False

    def check(self):
        if self.expired or self.ends is not None and time.monotonic() >= self.ends:
            self.expired = True
            raise BuildPaused()

    def interrupt_sql(self):
        self.expired = self.expired or self.ends is not None and time.monotonic() >= self.ends
        return int(self.expired)

    def __enter__(self):
        self.token = active_deadline.set(self)
        if self.seconds is not None:
            self.ends = time.monotonic() + self.seconds
            self.previous = signal.signal(signal.SIGALRM, self.alarm)
            signal.setitimer(signal.ITIMER_REAL, self.seconds)
        return self

    def alarm(self, *_):
        self.expired = True
        raise BuildPaused()

    def __exit__(self, *_):
        active_deadline.reset(self.token)
        if self.seconds is not None:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, self.previous)


@contextmanager
def atomic_boundary():
    """Do not interrupt the tiny file-rename/checkpoint or SQLite commit window."""
    old = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGALRM})
    try:
        yield
    finally:
        signal.pthread_sigmask(signal.SIG_SETMASK, old)
