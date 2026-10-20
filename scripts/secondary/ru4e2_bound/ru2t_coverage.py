"""Offline command-input provenance for canonical v4.4 image matches.
Only the replay allowlist is interpreted; magick calls are traced, never run.
No filenames, item order, comments or mere path mentions establish ancestry.
"""
import io
import json
import shlex
from pathlib import Path
from types import SimpleNamespace
import replay_literal
import scan_rollout


def trace_command(command, items):
    events = []
    def magick(args, **kwargs):
        if not isinstance(args, list) or not args or args[0] != 'magick':
            raise ValueError('unsupported command')
        operands = []; i = 1
        options = dict(replay_literal.OPTIONS, **{'-rotate': 1})
        while i < len(args):
            a = args[i]
            if a in ('(', ')'): i += 1; continue
            if a in options:
                i += 1 + options[a]; continue
            p = replay_literal.relative(a)
            if p.suffix != '.png' or p.parts[0] not in {'crops', 'img', 'zoom'}:
                raise ValueError('unsupported image operand')
            operands.append(str(p)); i += 1
        if len(operands) < 2 or not operands[-1].startswith('zoom/'):
            raise ValueError('missing image inputs/output')
        events.append(dict(inputs=operands[:-1], output=operands[-1]))
    if command.startswith('magick '):
        magick(shlex.split(command))
        return events
    _, code = replay_literal.parse(command)
    if code is None: return events
    def open_items(path, mode='r'):
        if path != 'items.jsonl' or mode != 'r': raise ValueError('only assignment reads allowed')
        return io.StringIO(''.join(json.dumps(i)+'\n' for i in items))
    def imports(name, *args, **kwargs):
        if name == 'json': return json
        if name == 'subprocess': return SimpleNamespace(run=magick)
        raise ValueError('unsupported trace import')
    safe = {k: getattr(__import__('builtins'), k) for k in replay_literal.BUILTINS}
    safe.update(open=open_items, print=lambda *a, **k: None, __import__=imports)
    exec(compile(code, '<coverage-literal-replay>', 'exec'), {'__builtins__': safe})
    return events


def coverage(scan, rollout, directory, items, image_fields=('crop',)):
    """Trace dependencies at each matched view, preserving command/view order."""
    records = list(scan_rollout.rows(rollout))
    scan_rollout.resolve(records, scan_rollout.CALL_TYPES)
    scan_rollout.resolve_templates(records, Path(directory).resolve())
    origins = {i[field]: {i[field]} for i in items for field in image_fields}
    witnessed = {}; log = []
    matches = {}
    for match in scan['image_matches']:
        matches.setdefault(match['record'], []).append(match)
    for ordinal, obj in enumerate(records):
        payload = obj.get('payload') or {}
        if payload.get('type') in scan_rollout.CALL_TYPES:
            raw = payload.get('input', payload.get('arguments', payload.get('action', {})))
            if payload.get('name') == 'exec':
                commands = scan_rollout.quoted_property(raw, 'cmd') if isinstance(raw, str) else []
            else:
                try: args = json.loads(raw) if isinstance(raw, str) else raw
                except ValueError: args = {}
                command = args.get('cmd', args.get('command')) if isinstance(args, dict) else None
                commands = [command] if isinstance(command, str) else []
            for command in commands:
                event = dict(record=ordinal, command=command)
                try:
                    traced = trace_command(command, items)
                except (ValueError, SyntaxError, AttributeError, TypeError, KeyError, NameError) as exc:
                    event.update(status='skipped', reason=str(exc))
                else:
                    event.update(status='traced', images=traced)
                    for image in traced:
                        origins[image['output']] = set().union(*(origins.get(p, set()) for p in image['inputs']))
                log.append(event)
        for match in matches.get(ordinal, []):
            for crop in origins.get(match['path'], set()):
                witnessed.setdefault(crop, []).append(dict(record=ordinal, image=match['path']))
    assigned = {i[field] for i in items for field in image_fields}
    direct = assigned & set(scan['images_viewed'])
    derived = (assigned & set(witnessed)) - direct
    unviewed = assigned - direct - derived
    return dict(direct=len(direct), derived=len(derived), unviewed=len(unviewed),
                assigned_crops=len(assigned), direct_crops=sorted(direct), derived_crops=sorted(derived),
                unviewed_crops=sorted(unviewed), dropped_items=[i['item_id'] for i in items if all(i[field] in unviewed for field in image_fields)],
                witnesses=witnessed, replay_log=log)
