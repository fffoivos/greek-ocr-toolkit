"""Paths for relocated evidence; immutable fixture sources stay byte-identical."""
from __future__ import annotations

import ast
import importlib.machinery
from pathlib import Path

from scripts.layout_paths import MOVES as _MOVES, relocated

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / 'docs/records'
ADMISSION = RECORDS / 'harvest/collect_v3_admission'
SOL_READING = RECORDS / 'harvest/sol_reading'
SEG_STEPS = RECORDS / 'harvest/seg_steps'


def require_file(path):
    """Skip only the caller that needs an actually absent evidence file."""
    import pytest
    from greekocr.ops.data_root import input_path
    path = relocated(path)
    try:
        resolved = input_path(path)
    except FileNotFoundError:
        resolved = path
    if not resolved.is_file():
        pytest.skip(str(path))
    return resolved


def evidence_params(path, loader, *, ids=None):
    """Keep synthetic tests runnable when a saved parameter input is absent."""
    import pytest
    try:
        source = require_file(path)
    except pytest.skip.Exception as exc:
        return [pytest.param(None, marks=pytest.mark.skip(reason=str(exc)), id=Path(path).name)]
    values = loader(source)
    return [pytest.param(value, id=ids(value) if ids else None) for value in values]


def install_record_loader():
    """Rebase documentation Python fixtures in memory during this test run.

    Python evidence under docs is frozen. Its old repository-root calculation
    and literal local input paths need the same relocation as its test caller.
    Frozen baseline predictor paths resolve through the shared binary helper.
    No decision code, source bytes, receipt strings or hash values are changed.
    Explicit spec loaders and ordinary imports both use SourceFileLoader here.
    """
    loader = importlib.machinery.SourceFileLoader
    original = loader.source_to_code
    original_get_code = loader.get_code

    def source_to_code(self, data, path, *, _optimize=-1):
        current = Path(path).resolve()
        try:
            relative = current.relative_to(ROOT).as_posix()
        except ValueError:
            return original(self, data, path, _optimize=_optimize)
        old_file = None
        for old, new in _MOVES:
            if relative == new or relative.startswith(new + '/'):
                old_file = ROOT / (old + relative[len(new):])
                break
        if not relative.startswith('docs/'):
            return original(self, data, path, _optimize=_optimize)
        if old_file is None:
            old_file = current
        tree = ast.parse(data, filename=path)
        # Evaluate only path arithmetic, never fixture code. Track the original
        # location to recognize expressions that formerly selected this repo.
        paths = {'__file__': old_file}

        def path_value(node):
            if isinstance(node, ast.Name):
                return paths.get(node.id)
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            if isinstance(node, ast.Call):
                if isinstance(node.func, (ast.Name, ast.Attribute)) and (
                        getattr(node.func, 'id', '') in ('Path', '_Path') or
                        getattr(node.func, 'attr', '') == 'Path') and len(node.args) == 1:
                    value = path_value(node.args[0])
                    return Path(value) if value is not None else None
                if isinstance(node.func, ast.Attribute) and node.func.attr in ('resolve', 'absolute'):
                    return path_value(node.func.value)
            if isinstance(node, ast.Attribute) and node.attr == 'parent':
                value = path_value(node.value)
                return value.parent if isinstance(value, Path) else None
            if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) and node.value.attr == 'parents':
                value = path_value(node.value.value)
                if isinstance(value, Path) and isinstance(node.slice, ast.Constant):
                    return value.parents[node.slice.value]
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
                left, right = path_value(node.left), path_value(node.right)
                if isinstance(left, Path) and isinstance(right, str):
                    return left / right
            return None

        class Rebase(ast.NodeTransformer):
            @staticmethod
            def input_path(node):
                module = ast.Call(func=ast.Name(id='__import__', ctx=ast.Load()),
                    args=[ast.Constant('greekocr.ops.data_root')],
                    keywords=[ast.keyword(arg='fromlist', value=ast.List(
                        elts=[ast.Constant('input_path')], ctx=ast.Load()))])
                return ast.copy_location(ast.Call(func=ast.Attribute(value=module,
                    attr='input_path', ctx=ast.Load()), args=[node], keywords=[]), node)

            def visit_Call(self, node):
                # Frozen documentation readers use the same custody adapter in
                # memory. Output calls and source bytes remain unchanged.
                node = self.generic_visit(node)
                if not isinstance(node.func, ast.Attribute):
                    return node
                method, owner = node.func.attr, node.func.value
                if method in ('read_text', 'read_bytes'):
                    node.func.value = self.input_path(owner)
                elif method == 'open':
                    mode = next((k.value for k in node.keywords if k.arg == 'mode'), None)
                    module_open = isinstance(owner, ast.Name) and owner.id in ('Image', 'gzip')
                    if mode is None:
                        mode = node.args[1] if module_open and len(node.args) > 1 else (
                            node.args[0] if not module_open and node.args else ast.Constant('r'))
                    if isinstance(mode, ast.Constant) and isinstance(mode.value, str) and mode.value in ('r', 'rb', 'rt'):
                        if module_open and node.args:
                            arg = node.args[0]
                            in_memory = isinstance(arg, ast.Call) and (
                                getattr(arg.func, 'id', '') == 'BytesIO' or
                                getattr(arg.func, 'attr', '') == 'BytesIO')
                            if not in_memory:
                                node.args[0] = self.input_path(arg)
                        elif not module_open:
                            node.func.value = self.input_path(owner)
                return node

            def visit_Subscript(self, node):
                if path_value(node) == ROOT:
                    return ast.copy_location(ast.Call(
                        func=ast.Attribute(value=ast.Call(func=ast.Name(id='__import__', ctx=ast.Load()),
                            args=[ast.Constant('pathlib')], keywords=[]), attr='Path', ctx=ast.Load()),
                        args=[ast.Constant(str(ROOT))], keywords=[]), node)
                return self.generic_visit(node)

            def visit_BinOp(self, node):
                if (isinstance(node.op, ast.Div) and isinstance(node.right, ast.Constant)
                        and node.right.value == 'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'):
                    module = ast.Call(func=ast.Name(id='__import__', ctx=ast.Load()),
                        args=[ast.Constant('greekocr.harvest.predictor_path')],
                        keywords=[ast.keyword(arg='fromlist', value=ast.List(
                            elts=[ast.Constant('predictor_binary')], ctx=ast.Load()))])
                    return ast.copy_location(ast.Call(func=ast.Attribute(value=module,
                        attr='predictor_binary', ctx=ast.Load()), args=[], keywords=[]), node)
                # Resolve joined documentation paths at runtime: a literal
                # following COLLECTOR must keep that explicit sibling's layout.
                if (isinstance(node.op, ast.Div) and isinstance(node.right, ast.Constant)
                        and isinstance(node.right.value, str) and node.right.value.startswith('docs/')):
                    node.left = self.visit(node.left)
                    module = ast.Call(func=ast.Name(id='__import__', ctx=ast.Load()),
                        args=[ast.Constant('scripts.layout_paths')],
                        keywords=[ast.keyword(arg='fromlist', value=ast.List(
                            elts=[ast.Constant('relocated')], ctx=ast.Load()))])
                    return ast.copy_location(ast.Call(func=ast.Attribute(value=module,
                        attr='relocated', ctx=ast.Load()), args=[node], keywords=[]), node)
                return self.generic_visit(node)

            def visit_Constant(self, node):
                if isinstance(node.value, str) and node.value.startswith('docs/'):
                    value = str(relocated(node.value))
                    if value != node.value:
                        return ast.copy_location(ast.Constant(value), node)
                return node

        rebase = Rebase()
        for statement in tree.body:
            if isinstance(statement, ast.Assign):
                value = path_value(statement.value)
                if isinstance(value, Path):
                    for target in statement.targets:
                        if isinstance(target, ast.Name):
                            paths[target.id] = value
            rebase.visit(statement)
        return original(self, ast.fix_missing_locations(tree), path, _optimize=_optimize)

    def get_code(self, fullname):
        # Moved trees contain historical __pycache__ files. Never execute those
        # unadapted code objects or overwrite them during a path-only test run.
        path = Path(self.path).resolve()
        if path.is_relative_to(ROOT / 'docs'):
            return self.source_to_code(self.get_data(str(path)), str(path))
        return original_get_code(self, fullname)

    loader.source_to_code = source_to_code
    loader.get_code = get_code

    def restore():
        loader.source_to_code = original
        loader.get_code = original_get_code
    return restore


def run_record(path):
    """Execute a documentation fixture with the same path adapter as imports."""
    path = relocated(path).resolve()
    loader = importlib.machinery.SourceFileLoader('<run_path>', str(path))
    namespace = dict(__name__='<run_path>', __file__=str(path),
                     __package__='', __spec__=None, __cached__=None)
    exec(loader.get_code('<run_path>'), namespace)
    return namespace
