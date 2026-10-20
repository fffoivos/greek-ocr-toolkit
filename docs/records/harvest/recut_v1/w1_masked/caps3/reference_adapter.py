"""Read-only reference-tool routing. CAPS3 compatibility approved by user CAPS3b ruling 2.

No reference file is copied or modified. Narrow, count-checked substitutions
configure the reference source in memory; source and adaptation diffs are saved.
"""
from __future__ import annotations

import difflib
import importlib.util
import json
from pathlib import Path
import sys
import types

from build import HERE, REFERENCE, PACK_ROOT, BED, FIELDS, dump, rows, sha

TOOLS = REFERENCE / 'tools'
APPROVAL = HERE / 'adapter_approval.json'


def require_approval():
    if not APPROVAL.is_file() or json.loads(APPROVAL.read_text()).get('approved') is not True:
        raise RuntimeError('CAPS3 scanner compatibility approval is pending; strict reference scanner is incompatible')


def load_reference(name, substitutions=()):
    sys.path.insert(0, str(TOOLS))
    path = TOOLS / (name + '.py')
    bindings = HERE / 'runtime_bindings.json'
    if bindings.is_file():
        expected = json.loads(bindings.read_text())['reference_sources'].get(str(path))
        if expected is None or sha(path) != expected:
            raise RuntimeError('reference source changed or unbound: ' + str(path))
    source = path.read_text()
    changed = source
    for old, new, count in substitutions:
        if changed.count(old) != count:
            raise RuntimeError('reference adaptation site changed: ' + name + ': ' + old)
        changed = changed.replace(old, new)
    module = types.ModuleType('caps3_reference_' + name)
    module.__file__ = str(path)
    exec(compile(changed, str(path), 'exec'), module.__dict__)
    module.ROOT = HERE
    module.PACK_ROOT = PACK_ROOT
    if hasattr(module, 'FIELDS'):
        module.FIELDS = dict(module.FIELDS, caps3=FIELDS)
    module.__adaptation__ = dict(source=str(path), source_sha256=sha(path),
        diff=''.join(difflib.unified_diff(source.splitlines(True), changed.splitlines(True),
                                        fromfile=str(path), tofile='CAPS3 in-memory configuration')))
    return module


CLOSURE_SUBSTITUTIONS = (
    ("im.mode!='RGB'", "(im.mode!='RGB' and not (bed=='caps3' and im.mode=='L'))", 1),
    ("if directory.name!='r3':", "if bed!='caps3' and directory.name!='r3':", 1),
)

# These are path vocabulary substitutions only. The v4 image matching,
# replay validation, literal scanning, and manifest integrity logic are intact.
ROLLOUT_SUBSTITUTIONS = (
    ("name!='items.jsonl'", "name!='cards.jsonl'", 1),
    ("n=='items.jsonl'", "n=='cards.jsonl'", 1),
    ("startswith('img/')", "startswith('crops/')", 2),
    ("for other in ('r1','r2','r3'):", "for other in ('c1','c2','c3'):", 1),
    ("sol_reading_packs\\b", "sol_packs\\b", 1),
    ("str(Path(__file__).with_name('replay_literal.py'))", "str(CAPS_REPLAY)", 1),
)

REPLAY_SUBSTITUTIONS = (
    ("rest=='cat items.jsonl'", "rest=='cat cards.jsonl'", 1),
    ("(?:img|zoom)/", "(?:crops|zoom)/", 1),
)


def private_contract(directory):
    """Additional CAPS3 gates replace duplicate-reader design with disjoint batches."""
    key = json.loads((HERE / 'keys/caps3.json').read_text())
    errors = []
    if BED.resolve() in HERE.resolve().parents or PACK_ROOT.resolve() in HERE.resolve().parents:
        errors.append('private output is under PACK_ROOT')
    ids_by_context = []
    line_ids = []
    controls = []
    for context in ('c1', 'c2'):
        cards = rows(BED / context / 'cards.jsonl')
        ids = [c['card_id'] for c in cards]
        ids_by_context.append(set(ids))
        if len(ids) != 55 or ids != key['readers'][context]:
            errors.append(context + ': count/order differs from private assignment')
        meta = [key['items'][i] for i in ids]
        c = [m for m in meta if m['control']]
        b = [m for m in meta if not m['control']]
        controls += c
        line_ids += [m['line_id'] for m in b]
        if len(c) != 5 or len(b) != 50:
            errors.append(context + ': not 50 bed + 5 controls')
        if any(m['primary_class'] == 'headings_caps' for m in c):
            errors.append(context + ': control from stratum under test')
        if any(m['primary_class'] != 'headings_caps' for m in b):
            errors.append(context + ': bed row from another stratum')
        for card in cards:
            p = BED / context / card['crop']
            if not p.is_file() or sha(p) != key['items'][card['card_id']]['crop_sha256']:
                errors.append(context + ': original crop hash mismatch')
    if ids_by_context[0] & ids_by_context[1] or len(set(line_ids)) != 100:
        errors.append('contexts overlap')
    if set(line_ids) != {r['id'] for r in rows(HERE / 'keys/draw.jsonl')}:
        errors.append('bed coverage differs from seeded draw')
    if len({m['line_id'] for m in controls}) != 10:
        errors.append('controls are duplicated')
    if sum(m['expected'] == {'letters': 'y', 'crop_ok': 'y'} for m in controls) != 7:
        errors.append('control positive/negative mix differs from 7/3')
    return errors


def closure(directory, compatible=False):
    if compatible:
        require_approval()
    scanner = load_reference('scan_packs', CLOSURE_SUBSTITUTIONS if compatible else ())
    result = scanner.scan(directory, 'caps3', write_manifest=compatible)
    result['reference'] = scanner.__adaptation__
    if compatible:
        result['caps3_contract_violations'] = private_contract(directory)
        result['violations'] += result['caps3_contract_violations']
        result['ok'] = not result['violations']
        if not result['ok']:
            # Do not leave a success manifest after any additional CAPS3 gate fails.
            (Path(directory).parent / ('MANIFEST.' + Path(directory).name + '.json')).unlink(missing_ok=True)
    return result


def rollout_scanner():
    require_approval()
    module = load_reference('scan_rollout', ROLLOUT_SUBSTITUTIONS)
    module.CAPS_REPLAY = HERE / 'tools/replay_literal.py'
    module.REPLAY_TMP = HERE / 'scan/replay_tmp'
    module.REPLAY_TMP.mkdir(parents=True, exist_ok=True)
    return module


def map_answers(context, answers):
    require_approval()
    module = load_reference('map_answers')
    key = json.loads((HERE / 'keys/caps3.json').read_text())
    mapped, controls = module.map_records('bsb', context, rows(answers), key, rows(BED / context / 'cards.jsonl'))
    controls['bed'] = 'caps3'
    destination = HERE / 'answers/caps3'
    module.jsonl(destination / (context + '.mapped.jsonl'), mapped)
    dump(destination / (context + '.controls.json'), controls)
    return dict(mapped=len(mapped), control_errors=controls['control_errors'], flagged=controls['flagged'])


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['strict-closure', 'closure'])
    args = parser.parse_args()
    results = [closure(BED / c, compatible=args.action == 'closure') for c in ('c1', 'c2')]
    destination = HERE / 'scan' / ('closure.json' if args.action == 'closure' else 'strict_reference_closure.json')
    dump(destination, results)
    print(json.dumps([dict(context=Path(r['directory']).name, ok=r['ok'], items=r['items'],
                           violations=r['violations']) for r in results], indent=2))
    sys.exit(0 if all(r['ok'] for r in results) else 2)
