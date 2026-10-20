"""Opt-in horizontal eligibility around the exact, unmodified T6a2 matcher.

T6a2 already requires 50% crop-width overlap. Requesting 0.5 is consequently
redundant; this adapter does not remove that original gate to manufacture a gain.
No scoring, vertical eligibility, fit sampling or tie-breaking is changed.
"""
from __future__ import annotations

import ast
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[5]
PROBE = ROOT / "docs/harvest/recut_v1/masking/probe.py"
sys.path.insert(0, str(ROOT))

import numpy as np
from greekocr.glyphs.recut import LineFit


def load_original():
    tree = ast.parse(PROBE.read_text(), filename=str(PROBE))
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef)
             and n.name in ("match", "runtime_fit")]
    if len(nodes) != 2:
        raise RuntimeError("missing original T6a2 functions")
    scope = dict(np=np, LineFit=LineFit)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(PROBE), "exec"), scope)
    return scope["match"], scope["runtime_fit"]


original_match, runtime_fit = load_original()


def overlap_fraction(box, fit):
    x0, _, x1, _ = box
    return max(0, min(x1, fit.x1) - max(x0, fit.x0)) / (x1 - x0)


def _restricted(box, fits, min_horizontal_overlap):
    if min_horizontal_overlap is None:
        return list(enumerate(fits))
    if not 0 <= min_horizontal_overlap <= 1:
        raise ValueError("overlap must be between zero and one")
    return [(i, f) for i, f in enumerate(fits)
            if overlap_fraction(box, f) >= min_horizontal_overlap]


def match(box, fits, *, min_horizontal_overlap=None):
    """Defaults call the original directly; opt-in only removes ineligible fits."""
    if min_horizontal_overlap is None:
        return original_match(box, fits)
    eligible = _restricted(box, fits, min_horizontal_overlap)
    index = original_match(box, [f for _, f in eligible])
    return eligible[index][0] if index is not None else None


def _load_ranked():
    # Execute the exact original eligibility/scoring statements. Replace ONLY
    # its final reduction with sorted(candidates), retaining (distance, index).
    tree = ast.parse(PROBE.read_text(), filename=str(PROBE))
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "match")
    if not isinstance(node.body[-1], ast.Return):
        raise RuntimeError("original match shape changed")
    node.name = "ranked_original"
    node.body[-1] = ast.Return(value=ast.Call(func=ast.Name(id="sorted", ctx=ast.Load()),
                                            args=[ast.Name(id="candidates", ctx=ast.Load())], keywords=[]))
    module = ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[]))
    scope = dict(np=np)
    exec(compile(module, str(PROBE), "exec"), scope)
    return scope[node.name]


_ranked = _load_ranked()


def candidates(box, fits, *, min_horizontal_overlap=None):
    eligible = _restricted(box, fits, min_horizontal_overlap)
    return [dict(index=eligible[j][0], distance_xh=d,
                 overlap=overlap_fraction(box, eligible[j][1]))
            for d, j in _ranked(box, [f for _, f in eligible])]


def status(rows):
    return "unmatched" if not rows else "ambiguous" if len(rows) > 1 else "matched"
