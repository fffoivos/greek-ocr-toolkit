"""Verify mechanical Q3 module moves/parameter names against the committed Q2 AST.

Imports are relocated, named literals are expanded, and the unused private
_gaps(persistent=False) branch is removed. No numeric tolerance is involved.
"""
import ast
import copy
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
MODULES = dict(pixel_segments='pixels', page_text_lines='lines', page_font='font',
               boundary_evidence='boundaries', line_structure='structure',
               table_lines='tables', statistics='statistics')


def normalise(source):
    tree = ast.parse(source)
    constants = {}
    dictionaries = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name.isupper():
                try:
                    ast.literal_eval(node.value)
                    constants[name] = node.value
                except (ValueError, TypeError):pass
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'dict':
                    try:
                        dictionaries[name] = {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords}
                        constants[name] = node.value
                    except (ValueError, TypeError):pass
    class Fold(ast.NodeTransformer):
        def visit_Import(self, node):return None
        def visit_ImportFrom(self, node):return None
        def visit_Name(self, node):
            if node.id in constants:return ast.copy_location(copy.deepcopy(constants[node.id]), node)
            if node.id == '_mean':node.id = '_median_or_mean'
            return node
        def visit_Subscript(self, node):
            if isinstance(node.value, ast.Name) and node.value.id in dictionaries and isinstance(node.slice, ast.Constant):
                return ast.copy_location(ast.Constant(dictionaries[node.value.id][node.slice.value]), node)
            return self.generic_visit(node)
        def visit_FunctionDef(self, node):
            if node.name == '_mean':node.name = '_median_or_mean'
            if node.name == '_gaps':
                node.args.kwonlyargs=[];node.args.kw_defaults=[]
                class LiveBranch(ast.NodeTransformer):
                    def visit_IfExp(self, term):
                        return term.body if isinstance(term.test, ast.Name) and term.test.id == 'persistent' else self.generic_visit(term)
                node=LiveBranch().visit(node)
            return self.generic_visit(node)
    tree.body=[node for node in tree.body if not (
        isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and (t.id.isupper() or t.id=='__all__') for t in node.targets))]
    return ast.dump(Fold().visit(tree), include_attributes=False)


def main():
    results=[]
    for old,new in MODULES.items():
        before=subprocess.check_output(['git','show',f'10eda96:greekocr/glyphs/{old}.py'],cwd=ROOT).decode()
        after=(ROOT/f'greekocr/pages/{new}.py').read_text()
        equal=normalise(before)==normalise(after)
        results.append(dict(old=f'greekocr/glyphs/{old}.py',new=f'greekocr/pages/{new}.py',equivalent=equal))
    print(json.dumps(results,indent=2))
    return int(not all(r['equivalent'] for r in results))

if __name__=='__main__':raise SystemExit(main())
