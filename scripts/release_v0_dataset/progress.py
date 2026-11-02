"""Periodic, flushed progress even while a stage is inside a long SQL operation."""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import resource
import sys
import threading
import time


active = ContextVar('dataset_progress', default=None)


class Progress:
    def __init__(self, stage, total_bytes=None, interval=60):
        self.stage, self.total = stage, total_bytes
        self.rows = self.bytes = 0
        self.started = time.monotonic()
        self.stop = threading.Event()
        self.interval = min(interval, 240)

    def report(self, final=False):
        seconds = max(time.monotonic() - self.started, 1e-9)
        rate = self.bytes / seconds
        value = dict(stage=self.stage, rows=self.rows, bytes=self.bytes,
                     rows_per_second=self.rows / seconds, bytes_per_second=rate,
                     eta_seconds=max(0, self.total - self.bytes) / rate if self.total and rate else None,
                     elapsed_seconds=seconds, complete=final)
        print(json.dumps(value, sort_keys=True), file=sys.stderr, flush=True)
        return value

    def pulse(self):
        while not self.stop.wait(self.interval):
            self.report()

    def __enter__(self):
        self.token = active.set(self)
        self.report()
        self.thread = threading.Thread(target=self.pulse, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *exc):
        active.reset(self.token)
        self.stop.set()
        self.thread.join()
        self.result = self.report(final=not exc[0])
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        self.result['peak_rss_bytes'] = rss if sys.platform == 'darwin' else rss * 1024
