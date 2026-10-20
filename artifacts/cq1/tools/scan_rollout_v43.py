"""PROVISIONAL v4.3: literal store/load concatenations before v4.2 checks.

No rollout code is executed. Unbound/dynamic loads fail closed. All v4.2
provenance, manifest, forbidden-name and read-only font checks are retained.
"""
import sys
sys.dont_write_bytecode = True
import argparse, ast, json, re, tempfile
from pathlib import Path
from scan_rollout_v42 import inspect as inspect_v42, ruc1_scanner
from build import dump, sha

# Consume quoted strings/comments atomically: commands and comments cannot
# manufacture bindings. Templates are deliberately opaque and unsupported.
TOKEN = re.compile(r'''//[^\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|[A-Za-z_$][\w$]*|[^\s]''')

def literal(token):
    if not token or token[0] not in "\"'":
        return None
    try:
        value = json.loads(token) if token[0] == '"' else ast.literal_eval(token)
    except (ValueError, SyntaxError):
        return None
    # Keep decoding conservative across Python and JavaScript string syntax.
    if re.search(r'\\(?![\\\'"/bfnrt]|u[0-9a-fA-F]{4})', token):
        return None
    return value if isinstance(value, str) else None


def resolve(records, call_types):
    bindings = {}; resolutions = []; failures = []
    for ordinal, obj in enumerate(records):
        p = obj.get('payload', {})
        if p.get('type') not in call_types or p.get('name') != 'exec':
            continue
        field = 'input' if 'input' in p else 'arguments'
        raw = p.get(field)
        if not isinstance(raw, str): continue
        tokens = [m for m in TOKEN.finditer(raw) if not m[0].startswith(('//', '/*'))]
        edits = []
        for i, token in enumerate(tokens):
            t = [m[0] for m in tokens[i:i+8]]
            if i and tokens[i-1][0] in ('.', 'function'): continue
            if len(t) >= 4 and t[:2] == ['store', '('] and t[3] == ',':
                name = literal(t[2])
                if name is not None:
                    value = literal(t[4]) if len(t) >= 6 and t[5] == ')' else None
                    bindings.pop(name, None)
                    if value is not None:
                        bindings[name] = dict(value=value, record=ordinal,
                            expression=raw[token.start():tokens[i+5].end()])
            if len(t) >= 4 and t[:2] == ['load', '('] and t[3] == ')':
                name = literal(t[2]); binding = bindings.get(name)
                suffix = literal(t[5]) if len(t) >= 6 and t[4] == '+' else None
                if binding is None or suffix is None:
                    failures.append(dict(record=ordinal, reason='unresolvable load expression',
                        expression=raw[token.start():tokens[i+3].end()], name=name))
                    continue
                end = tokens[i+5].end(); value = binding['value'] + suffix
                edits.append((token.start(), end, json.dumps(value)))
                resolutions.append(dict(record=ordinal, expression=raw[token.start():end],
                    name=name, literal_suffix=suffix, binding=binding.copy(), resolved=value))
        for start, end, replacement in reversed(edits):
            raw = raw[:start] + replacement + raw[end:]
        p[field] = raw
    return resolutions, failures


def inspect(rollout, directory, scanner_factory=ruc1_scanner):
    records = [json.loads(l) for l in Path(rollout).read_text().splitlines()]
    resolutions, failures = resolve(records, scanner_factory().CALL_TYPES)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl') as f:
        for obj in records: f.write(json.dumps(obj)+'\n')
        f.flush()
        result = inspect_v42(f.name, directory, scanner_factory=scanner_factory)
    result['v41_template_resolutions'] = result.pop('template_resolutions', [])
    result['violations'].extend(failures)
    result.update(scanner_version='4.3', status='PROVISIONAL',
        coordinator_ruling='pending lead report', rollout=str(rollout), rollout_sha256=sha(rollout),
        template_resolutions=resolutions, unresolved_loads=failures,
        rule=result['rule']+'; resolve recorded literal store/load plus literal suffix',
        ok=not result['violations'],
        v43_path_witness_ok=not [v for v in result['violations'] if not v['reason'].startswith('image provenance:')])
    return result

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('rollout', type=Path); p.add_argument('reader_dir', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); r = inspect(a.rollout, a.reader_dir); dump(a.output, r)
    print(json.dumps({k:r[k] for k in ('ok','scanner_version','status','returned_images','image_match_counts','violations')}, indent=2))
    print('template_resolutions:', len(r['template_resolutions']))
    raise SystemExit(0 if r['ok'] else 2)
