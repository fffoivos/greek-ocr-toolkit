"""Reproduce CODE_SHA runtime contract blockers without importing readers.

Compile the exact AST function definitions from Git blobs. This avoids package
initializers and native I/O; no implementation body or manifest is modified.
"""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

D = Path(__file__).resolve().parent
REPO = D.parents[2]
CODE_SHA = '4f4b085d69bc2cf39436ac176331492d11d89249'
FP3 = REPO.parent / 'greek-page-ocr-wave2/out/fp3/prepared/87407ec7430a375f'
SECONDARY = REPO.parent / 'greek-ocr-toolkit-secondary'


def blob(path):
    return subprocess.check_output(['git', '-C', str(REPO), 'show', CODE_SHA + ':' + path])


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def exact_function(path, name, namespace):
    source = blob(path)
    module = ast.parse(source, filename=CODE_SHA + ':' + path)
    function = next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.Module(body=[function], type_ignores=[]), CODE_SHA + ':' + path, 'exec'), namespace)
    return namespace[name], dict(path=path, sha256=sha(source), function=name,
                                 first_line=function.lineno, last_line=function.end_lineno,
                                 source=ast.get_source_segment(source.decode(), function))


def main():
    versions = json.loads(blob('docs/harvest/line_pipeline/tool_versions.json'))['tools']
    verify, verify_source = exact_function('greekocr/harvest/line_pipeline_census.py', 'verify_versions',
        dict(Path=Path, digest=lambda s: sha(s.encode()), json=json, file_sha=file_sha, __file__=__file__))
    try:
        verify({'segmentation': versions['segmentation']})
    except ValueError as exc:
        version_error = str(exc)
    else:
        raise AssertionError('expected segmentation version/history rejection disappeared')
    assert version_error == 'version/iteration history mismatch: segmentation'

    validate, validate_source = exact_function('greekocr/harvest/line_pipeline.py', 'validate_result', {})
    # Use the literal first bound train-parent record, not a fabricated row.
    train = REPO.parent / 'greek-ocr-toolkit/docs/harvest/collection/v2/import_real_v2_train.jsonl'
    config = json.loads((REPO/'docs/harvest/seg_census/census04_config.json').read_text())
    train_spec = next(p for p in config['parents'] if p['id'] == 'collection-v2-train')
    assert file_sha(train) == train_spec['sha256']
    parent_record = json.loads(train.open().readline())
    release = next(c for c in config['corrections'] if c['tool']=='numerics' and c['parent_id']==train_spec['id'])
    ledger_path = FP3/Path(release['path']).name
    assert file_sha(ledger_path) == release['sha256']
    record = json.loads(ledger_path.open().readline())
    assert parent_record['id'] == record['binding']['id']
    assert sha(parent_record['label'].encode()) == record['raw_text_sha256']
    row = dict(record['binding'], raw_text=parent_record['label'])
    try:
        validate(record, row, 'numerics', versions)
    except ValueError as exc:
        correction_error = str(exc)
    else:
        raise AssertionError('expected standing-ledger version rejection disappeared')
    assert correction_error == 'tool/version mismatch'

    registry_path = SECONDARY/'docs/labelfix/lqb/versions.json'
    registry = json.loads(registry_path.read_text())['versions']
    by_sha = {v.get('sha256'): name for name,v in registry.items()}
    inventories = []
    for release in config['corrections']:
        local = FP3/Path(release['path']).name
        assert file_sha(local) == release['sha256']
        states, methods, sources, scans = Counter(), Counter(), Counter(), Counter()
        records = edits = held = no_change = 0
        for line in local.open():
            r = json.loads(line)
            records += 1
            edits += bool(r['edits'])
            held += r['status'] == 'required_evidence_unresolved'
            no_change += r['status'] == 'verified_no_change'
            states[r['status']] += 1
            methods[canonical(dict(version=r['tool_version'], digest=r['tool_digest']))] += 1
            e = r['evidence']
            if e.get('source_artifact_sha256'):
                h = e['source_artifact_sha256']
                name = by_sha.get(h)
                sources[canonical(dict(path=e.get('source_artifact'),sha256=h,
                    registered_version=name, registered_status=registry[name]['status'] if name else None))] += 1
            else:
                scans[canonical({k:e[k] for k in ('candidate_scan','scope','definition','definition_sha256','tokens_sha256') if k in e})] += 1
        replacement = ((release['tool']=='cyrillic' and release['parent_id'].startswith('collection-v2'))
                       or (release['tool']=='numerics' and release['parent_id'].startswith('collect-v3-W1')))
        inventories.append(dict(release=release,local_path=str(local),sha256_match=True,bytes=local.stat().st_size,
            disposition_in_brief='rule-2 overlay' if replacement else 'standing unchanged',
            records=records,edited_rows=edits,hold_rows=held,no_change_rows=no_change,
            states=dict(states),methods=[dict(json.loads(k),records=n) for k,n in methods.items()],
            source_artifacts=[dict(json.loads(k),records=n) for k,n in sources.items()],
            scoped_negative_definitions=[dict(json.loads(k),records=n) for k,n in scans.items()]))
    superseded_standing = [dict(ledger=v['release']['path'], source=s) for v in inventories
        if v['disposition_in_brief']=='standing unchanged' for s in v['source_artifacts']
        if s['registered_status']=='superseded']
    incompatible_standing = [v['release']['path'] for v in inventories if v['disposition_in_brief']=='standing unchanged'
        and any(m['version']!=versions[v['release']['tool']]['version'] or m['digest']!=versions[v['release']['tool']]['digest'] for m in v['methods'])]
    result = dict(status='BLOCKED_RUNTIME_CONTRACTS', code_sha=CODE_SHA,
        method='exact source AST functions; zero rewritten statements; no imports of pipeline/native/readers',
        segmentation=dict(recorded_version=versions['segmentation']['version'],
            iteration_count=versions['segmentation']['iteration_count'],
            documented_iterations=len(versions['segmentation']['documented_iterations']),
            required_by_code='0.'+str(versions['segmentation']['iteration_count']),error=version_error, source=verify_source),
        correction=dict(error=correction_error, source=validate_source,
            standing_release=next(c for c in config['corrections'] if c['tool']=='numerics' and c['parent_id']==train_spec['id']),
            record=record,parent_local_path=str(train),parent_sha256=train_spec['sha256'],
            raw_parent_verified=True,expected_version=versions['numerics']['version'],expected_digest=versions['numerics']['digest']),
        versions_registry=dict(path=str(registry_path),sha256=file_sha(registry_path)),
        ledgers=inventories, superseded_standing_sources=superseded_standing,
        incompatible_standing_ledgers=incompatible_standing,
        no_ledger_writes=True,no_verdict_changes=True,reader_runs=0,native_image_runs=0,network=False)
    (D/'runtime_contract_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],segmentation_error=version_error,correction_error=correction_error,
                         ledgers=len(inventories),incompatible_standing_ledgers=len(incompatible_standing),
                         superseded_standing_sources=len(superseded_standing)),indent=2))


if __name__ == '__main__':
    main()
