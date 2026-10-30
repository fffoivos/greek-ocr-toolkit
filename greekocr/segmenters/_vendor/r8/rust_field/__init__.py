"""Explicit experimental M15 batch selector; pure Python needs no build."""
import ctypes
import os
from pathlib import Path
import sys
import numpy as np

BACKEND = os.environ.get('FAST_LINES_FIELD_BACKEND', 'python')
if BACKEND not in ('python', 'rust'):
    raise ValueError('FAST_LINES_FIELD_BACKEND must be python or rust')
COUNTERS = dict(python=0, rust=0, fallback=0, prepared=0, copied_bytes=0)
_LIB = None


def native_library():
    global _LIB
    if _LIB is None:
        suffix = '.dylib' if sys.platform == 'darwin' else '.so'
        target = Path(os.environ.get('CARGO_TARGET_DIR', Path(__file__).parent/'target'))
        path = Path(os.environ.get('FAST_LINES_FIELD_LIBRARY', target/'release'/('libfast_lines_field'+suffix)))
        try:
            lib = ctypes.CDLL(str(path.resolve()))
        except OSError as e:
            raise RuntimeError('Explicit M15 Rust backend needs a usable build; run rust_field/build.sh or set FAST_LINES_FIELD_LIBRARY') from e
        p = ctypes.c_void_p
        lib.field_shifts.argtypes = [p]*8+[ctypes.c_size_t]*6+[p]*3
        lib.field_shifts.restype = None
        _LIB = lib
    return _LIB


# Fail at selector import before any page work if Rust was explicitly requested.
if BACKEND == 'rust':
    native_library()


def shifts_python(before, moved, columns, profiles, ys, lag, lengths, energy=None, *, diagnostic=False, prepared=None):
    """Readable frozen oracle, same operations/order as checked render."""
    COUNTERS['python'] += 1
    width = moved.shape[-1]
    valid, valid_lengths = prepared if prepared is not None else (np.arange(width)[None, :] < lengths[:, None], np.maximum(lengths, 1))
    after = np.stack([np.interp(m+lag[None, :, None], ys, profiles[:, col], left=0, right=0)
                      for m, col in zip(moved[:, :, None, :], columns)])
    after = np.where(valid[None, :, None, :], after-(after*valid[None, :, None, :]).sum(-1, keepdims=True)/valid_lengths[None, :, None, None], 0)
    if energy is None:
        energy = np.sum(before**2, axis=2)
    scores = np.sum(after*before[:, :, None, :], axis=3)/(np.sqrt(np.sum(after**2, axis=3)*energy[:, :, None])+1e-9)
    js = np.argmax(scores, axis=2)
    cc, kk = np.indices(js.shape)
    delta = lag[js].copy()
    middle = (js>0)&(js<len(lag)-1)
    ci, ii, jj = cc[middle], kk[middle], js[middle]
    delta[middle] += .5*(scores[ci, ii, jj-1]-scores[ci, ii, jj+1])/np.minimum(-1e-9, scores[ci, ii, jj-1]-2*scores[ci, ii, jj]+scores[ci, ii, jj+1])*(lag[1]-lag[0])
    weight = np.maximum(0, scores[cc, kk, js])
    delta[:, lengths<5] = 0
    weight[:, lengths<5] = 0
    return (delta, weight, scores) if diagnostic else (delta, weight)


class Batch:
    """Invocation-local immutable numeric inputs; no pixel/row decisions."""
    def __init__(self, profiles, ys, lag, lengths, *, backend=None):
        self.backend = BACKEND if backend is None else backend
        if self.backend not in ('python', 'rust'):
            raise ValueError('unknown M15 backend')
        self.profiles, self.ys, self.lag, self.lengths = profiles, ys, lag, lengths
        self.valid = (np.arange(int(max(lengths, default=0)))[None, :] < lengths[:, None], np.maximum(lengths, 1))
        if self.backend == 'rust':
            native_library()
            self.native_profiles = self.array(np.asarray(profiles).T)
            self.native_ys = self.array(ys)
            self.native_lag = self.array(lag)
            self.native_lengths = self.array(lengths, np.int64)
            assert len(ys)>=2 and np.all(np.diff(ys)>0) and len(lag)>=2
            COUNTERS['prepared'] += 1

    @staticmethod
    def array(value, dtype=np.float64):
        a = np.ascontiguousarray(value, dtype=dtype)
        if not isinstance(value, np.ndarray) or not np.shares_memory(a, value):
            COUNTERS['copied_bytes'] += a.nbytes
        return a

    def shifts_many(self, before, moved, columns, energy=None, *, diagnostic=False):
        if self.backend == 'python':
            return shifts_python(before, moved, columns, self.profiles, self.ys, self.lag, self.lengths, energy, diagnostic=diagnostic, prepared=self.valid)
        c, k, w = moved.shape
        assert before.shape == moved.shape and k == len(self.lengths)
        assert np.all((self.lengths>=0)&(self.lengths<=w))
        cols = self.array(columns, np.int64)
        assert cols.shape == (c,) and np.all((cols>=0)&(cols<self.profiles.shape[1]))
        b, m = self.array(before), self.array(moved)
        e = None if energy is None else self.array(np.broadcast_to(energy, (c,k)))
        delta, weight, scores = np.empty((c,k)), np.empty((c,k)), np.empty((c,k,len(self.lag)))
        arrays = [b, m, self.native_profiles, self.native_ys, self.native_lag, self.native_lengths, cols, e]
        COUNTERS['rust'] += 1  # actual FFI entry, never inferred from field count
        native_library().field_shifts(*[None if a is None else a.ctypes.data for a in arrays],
            c, k, w, len(self.ys), self.profiles.shape[1], len(self.lag),
            delta.ctypes.data, weight.ctypes.data, scores.ctypes.data)
        return (delta, weight, scores) if diagnostic else (delta, weight)
