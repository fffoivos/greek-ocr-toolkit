"""Offline v4.2 wrapper: v4.1 plus proven read-only OS-font operands.

Unknown use fails closed. No rollout code is executed. Only absolute-path
violations are waived; forbidden names, parent escapes, provenance and manifest
checks are retained. Supported read proofs: magick -font operands in literal
subprocess.run argv, and standalone cat/stat/ls shell commands. Every occurrence
must have a read proof, so an additional write of the same path still fails.
"""
import sys
sys.dont_write_bytecode = True
import ast, argparse, importlib.util, json, re, shlex
from pathlib import Path
from scan_rollout_v41 import inspect as inspect_v41
from build import dump, sha


def ruc1_scanner():
    # Isolate the task-specific read-only adapter from kosmo2's module names.
    root = Path(__file__).resolve().parents[2] / 'ruc1'
    old = sys.modules.get('build')
    try:
        for name in ('build', 'reference_adapter'):
            spec = importlib.util.spec_from_file_location('ruc1_v42_' + name, root / (name + '.py'))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if name == 'build': sys.modules['build'] = mod
        return mod.rollout_scanner()
    finally:
        if old is not None: sys.modules['build'] = old
        else: sys.modules.pop('build', None)


def font_path(path):
    p = Path(path)
    return '..' not in p.parts and any(path.startswith(prefix) and len(path)>len(prefix)
        for prefix in ('/System/Library/Fonts/', '/Library/Fonts/'))


def read_proofs(cmd, path):
    """Return the number of statically proven read operands, or zero."""
    heredoc = re.fullmatch(r"python3 - <<'PY'\n(.*)\nPY", cmd, re.S)
    if heredoc:
        try: tree = ast.parse(heredoc[1])
        except SyntaxError: return 0
        occurrences = [n for n in ast.walk(tree) if isinstance(n, ast.Constant) and n.value == path]
        proved = set()
        for node in ast.walk(tree):
            if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == 'subprocess'
                and node.func.attr == 'run' and node.args and isinstance(node.args[0], ast.List)):
                continue
            args = node.args[0].elts
            if not args or not isinstance(args[0], ast.Constant) or args[0].value != 'magick': continue
            for i, arg in enumerate(args):
                if (i>0 and i<len(args)-1 and isinstance(arg, ast.Constant) and arg.value == path
                    and isinstance(args[i-1], ast.Constant) and args[i-1].value == '-font'):
                    proved.add(id(arg))
        return len(proved) if occurrences and all(id(n) in proved for n in occurrences) else 0
    try: args = shlex.split(cmd)
    except ValueError: return 0
    if args and args[0] in ('cat','stat','ls') and all(
        a == path or (a.startswith('-') and re.fullmatch(r'-[A-Za-z-]+', a)) for a in args[1:]):
        return args.count(path)
    return 0


def inspect(rollout, directory, scanner_factory=ruc1_scanner):
    result = inspect_v41(rollout, directory, scanner_factory=scanner_factory)
    baseline = list(result['violations'])
    scanner = scanner_factory()
    records = [json.loads(l) for l in Path(rollout).read_text().splitlines()]
    allowed = []; keep = []
    for v in baseline:
        path = v.get('path', '')
        if v['reason'] != 'absolute path outside reader_dir' or not font_path(path):
            keep.append(v); continue
        payload = records[v['record']]['payload']
        raw = payload.get('input', payload.get('arguments', ''))
        commands = scanner.quoted_property(raw, 'cmd') if payload.get('name') == 'exec' else []
        proofs = sum(read_proofs(cmd, path) for cmd in commands)
        if proofs and isinstance(raw, str) and raw.count(path) == proofs:
            allowed.append(dict(v, access='read-only', proof='statically checked command operand'))
        else: keep.append(v)
    result.update(scanner_version='4.2', rule=result['rule']+'; read-only OS font resources allowed',
        v41_violations=baseline, os_resource_allowances=allowed, violations=keep, ok=not keep,
        v42_path_witness_ok=not [v for v in keep if not v['reason'].startswith('image provenance:')])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rollout', type=Path); parser.add_argument('reader_dir', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(); result = inspect(args.rollout, args.reader_dir); dump(args.output, result)
    print(json.dumps({k:result[k] for k in ('ok','returned_images','image_match_counts','violations','os_resource_allowances')}, indent=2))
    raise SystemExit(0 if result['ok'] else 2)
