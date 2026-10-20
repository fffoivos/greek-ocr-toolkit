"""Bounded native-worker concurrency; SQLite and decisions stay coordinator-owned."""
from collections import deque
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
import threading
import time

MAX_PENDING_OBSERVATIONS = 4096


@dataclass
class Observation:
    result: object = None
    error: object = None
    seconds: float = 0
    attempted: bool = False
    cached: bool = False


class NativePool:
    def __init__(self, factory, workers, prefetch_factor=2):
        if type(workers) is not int or not 1 <= workers <= 256:
            raise ValueError("native_workers must be an integer from 1 through 256")
        if type(prefetch_factor) is not int or not 1 <= prefetch_factor <= 64:
            raise ValueError('native_prefetch_factor must be an integer from 1 through 64')
        if workers * prefetch_factor > MAX_PENDING_OBSERVATIONS:
            raise ValueError('native_workers times native_prefetch_factor must be at most 4096')
        self.prefetch_factor=prefetch_factor
        self.factory=factory;self.workers=workers
        self.local=threading.local();self.instances=[];self.lock=threading.Lock()
        self.executor=ThreadPoolExecutor(max_workers=workers,thread_name_prefix="native-filter")

    def measure(self, row):
        started=time.monotonic()
        try:
            if not hasattr(self.local,"native"):
                self.local.native=self.factory()
                with self.lock:self.instances.append(self.local.native)
            return Observation(result=self.local.native(row),seconds=time.monotonic()-started,attempted=True)
        except Exception as exc:
            return Observation(error=exc,seconds=time.monotonic()-started,attempted=True)

    def ordered(self, rows, prepare):
        """Coordinator-owned prepare/cache lookup with explicitly bounded lookahead."""
        pending=deque()
        for row in rows:
            ready=prepare(row)
            if ready is None:future=self.executor.submit(self.measure,row)
            else:
                future=Future();future.set_result(ready)
            pending.append((row,future))
            if len(pending)>=self.prefetch_factor*self.workers:
                item,future=pending.popleft();yield item,future.result()
        while pending:
            item,future=pending.popleft();yield item,future.result()

    def close(self):
        # Running requests retain their hard per-row deadline. Never close a
        # worker concurrently with its protocol read/write or start a new child
        # after cleanup has inspected the instance list.
        errors=[]
        try:
            self.executor.shutdown(wait=True,cancel_futures=True)
        except Exception as exc:errors.append(dict(stage="executor",error_type=type(exc).__name__,detail=str(exc)))
        finally:
            for native in self.instances:
                try:
                    if hasattr(native,"close"):native.close()
                except Exception as exc:errors.append(dict(stage="native",error_type=type(exc).__name__,detail=str(exc)))
        return errors
