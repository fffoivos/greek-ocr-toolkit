"""REL4 overlay and custody contracts. Standard library only; no side effects."""
import json
from pathlib import Path


def parse_overlay_record(row, spec):
    # Exact parsing statements: bench/e4_wave1c.py:66-74, called by
    # bench/e4_wave2.py:25,277,556. Extra fields are retained unchanged.
    ident, text = row.get(spec['id_field']), row.get(spec['text_field'])
    provenance = row.get('provenance', spec.get('provenance'))
    if not isinstance(ident, str) or not ident or not isinstance(text, str) or not provenance:
        raise ValueError('label row requires exact string row_id, text, provenance')
    return dict(row, row_id=ident, text=text, provenance=provenance)


def apply_spans(raw, edits):
    previous = None
    for e in edits:
        a, z = e['start'], e['end']
        if not (type(a) is int and type(z) is int and 0 <= a <= z <= len(raw) and raw[a:z] == e['before']):
            raise ValueError('invalid raw span')
        if previous and (a < previous[1] or a == previous[0] or (a == previous[1] and a == z)):
            raise ValueError('overlapping edits')
        previous = a, z
    text = raw
    for e in reversed(edits):
        text = text[:e['start']] + e['after'] + text[e['end']:]
    return text


def reason(decision):
    route = decision.get('routes', {}).get('polytonic', {})
    if route.get('status') == 'required_evidence_unresolved' or route.get('status') == 'hold':
        return 'polytonic hold'
    if route.get('status') == 'applied' and route.get('edits'):
        return 'polytonic edit'
    return 'other'


def sf7_index(root, cfg, records, sha, require, digest, canonical):
    index = {}
    for spec in cfg['sf7']['ledgers']:
        if spec['parent_id'] not in cfg['parents']:
            continue
        p = Path(spec['path']); p = p if p.is_absolute() else root/p
        require(spec['status'] == 'released' and sha(p) == spec['sha256'], 'sf7 ledger sha/status mismatch')
        for line, record in enumerate(records(p), 1):
            binding = record.get('binding', {})
            ident = binding.get('id', record.get('id', record.get('line_id')))
            require(isinstance(ident, str) and ident, 'sf7 ledger missing ID')
            require(all(record.get(k, ident) == ident for k in ('id','line_id')), 'sf7 contradictory ID aliases')
            key = spec['parent_id'], ident
            require(key not in index, 'duplicate sf7 ledger key')
            index[key] = (spec, record, dict(path=str(p), line=line, record_sha256=digest(canonical(record))))
    return index


def sf7_record(row, index, require, digest, canonical):
    route = row['decision']['routes'].get('polytonic', {})
    key = row['parent_id'], row['id']
    if route.get('status') != 'applied' or not route.get('edits'):
        return None
    require(route['status'] == 'applied' and key in index, 'sf7 applied route lacks ledger record')
    spec, ledger, ref = index[key]
    ev = route['evidence']; rebound = ev.get('split_input_binding', {})
    source_sha = rebound.get('source_artifact_sha256', ev['artifact_sha256'])
    record_sha = rebound.get('source_record_sha256', ev.get('original_record_sha256'))
    require(source_sha == spec['sha256'] and record_sha == ref['record_sha256'], 'sf7 ledger record reference mismatch')
    raw = row['raw_text']; target = apply_spans(raw, route['edits'])
    fields = ('start','end','before','after')
    if spec.get('format') == 'line-tool-result-v1':
        require(ledger['tool'] == 'polytonic' and ledger['status'] == 'applied', 'sf7 canonical status/tool mismatch')
        expected_binding = rebound.get('original_binding', route['binding'])
        require(ledger['binding'] == expected_binding, 'sf7 original binding mismatch')
        require(ledger['raw_text_sha256'] == digest(raw), 'sf7 ledger raw mismatch')
        require(ledger['tool_version'] == route['tool_version'] and ledger['tool_digest'] == route['tool_digest'], 'sf7 ledger tool mismatch')
        require([{k:e[k] for k in fields} for e in ledger['edits']] == [{k:e[k] for k in fields} for e in route['edits']], 'sf7 ledger spans mismatch')
        require(not ledger.get('evidence', {}).get('legacy_holds'), 'sf7 ledger holds')
    else:
        # Same legacy parent/target/hold semantics as pinned line_pipeline_adapters.py:27-64.
        parent = ledger.get('label_parent', ledger.get('parent_text'))
        parent_sha = ledger.get('parent_text_sha256', ledger.get('original_label_sha256'))
        require(parent == raw if parent is not None else parent_sha == digest(raw), 'sf7 legacy raw mismatch')
        require(not (ledger.get('holds') or ledger.get('hold_slots') or ledger.get('status','ok') in ('hold','out_of_scope','failed')), 'sf7 ledger holds')
        require(ledger.get('text', ledger.get('label', ledger.get('composed_text', raw))) == target, 'sf7 ledger target mismatch')
        if 'byte_patches' in ledger:
            patches=[]; encoded=raw.encode('utf-8')
            for e in ledger['byte_patches']:
                a,z=e['raw_byte_start'],e['raw_byte_end']
                require(type(a) is int and type(z) is int and 0 <= a <= z <= len(encoded), 'sf7 invalid byte span')
                patches.append(dict(start=len(encoded[:a].decode()),end=len(encoded[:z].decode()),before=encoded[a:z].decode(),after=e['after']))
                require(patches[-1]['before']==e['before'], 'sf7 byte parent mismatch')
            require(patches == [{k:e[k] for k in fields} for e in route['edits']], 'sf7 legacy spans mismatch')
    require(target != raw, 'sf7 applied edit changes no text')
    record = dict(row_id=key[1],parent_id=key[0],parent_text=raw,text=target,
        raw_text_sha256=digest(raw),tool_version=route['tool_version'],tool_digest=route['tool_digest'],
        provenance=dict(route=route,ledger_sha256=spec['sha256'],ledger_record=ref))
    require(parse_overlay_record(record, dict(id_field='row_id',text_field='text')) == record, 'overlay round trip mismatch')
    return record
