"""Compare saved worker receipts; does not run image processing or OCR."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scientific(value, versions):
    value = deepcopy(value)
    # Source/runtime-generation identity necessarily changes across the repair.
    value.pop('run_binding_sha256', None)
    value.pop('toolchain_digest', None)
    value.get('toolchain_versions', {}).pop('census', None)
    repair = value.get('routes', {}).get('content_repair', {})
    if 'tool_digest' in repair:
        # This fingerprint includes the changed census orchestration module.
        # Require the exact source registry binding before normalizing it.
        assert repair['tool_digest'] == versions['content_repair']['digest']
        repair.pop('tool_digest')
    for stage in value.get('stages', []):
        if stage['stage'] == 'segmentation':
            orientation = stage['result'].get('frame', {}).get('orientation', {})
            if isinstance(orientation, dict):
                orientation.get('evidence', {}).pop('seconds', None)
    return value


p = argparse.ArgumentParser()
p.add_argument('before', type=Path)
p.add_argument('after', type=Path)
p.add_argument('output', type=Path)
a = p.parse_args()
assert sha(a.before / 'sample.jsonl') == sha(a.after / 'sample.jsonl')
old_path, new_path = [d / 'w1/decisions.jsonl' for d in (a.before, a.after)]
old_rows, new_rows = [list(map(json.loads, path.open())) for path in (old_path, new_path)]
assert len(old_rows) == len(new_rows) == 768
old_ids, new_ids = [[(v['binding']['parent_id'], v['binding']['id']) for v in rows]
    for rows in (old_rows, new_rows)]
assert len(set(old_ids)) == len(set(new_ids)) == 768 and old_ids == new_ids
old = {v['binding']['id']: v for v in old_rows}
new = {v['binding']['id']: v for v in new_rows}
assert len(old) == len(new) == 768
old_versions, new_versions = [json.loads(Path(json.loads((d / 'config_w1.json').read_text())['versions']).read_text())['tools']
    for d in (a.before, a.after)]
witness = 'lekythos--dcfa99599048d352--s002-l0114'
assert old[witness]['disposition'] == 'INFRA_ERROR'
changed = [i for i in old if i != witness and scientific(old[i], old_versions) != scientific(new[i], new_versions)]
seg = next(v['result'] for v in new[witness]['stages'] if v['stage'] == 'segmentation')
assert not changed, changed
assert seg['verdict'] == 'UNCERTAIN' and new[witness]['disposition'] == 'HOLD'
assert seg['evidence']['context_unavailable']['reason'] == 'empty_oblique_rule_refit'
assert all(v['disposition'] != 'INFRA_ERROR' for v in new.values())
def receipt(directory, decisions):
    path = directory / 'config_w1.json'
    config = json.loads(path.read_text())
    versions = Path(config['versions'])
    return dict(decisions_path=str(decisions), decisions_sha256=sha(decisions),
        config_path=str(path), config_sha256=sha(path), versions_sha256=sha(versions),
        source_manifest_sha256=sha(versions.parents[4] / 'SHA256SUMS'))


result = dict(status='PASS', sample_sha256=sha(a.after / 'sample.jsonl'), rows=768,
    before=receipt(a.before, old_path), after=receipt(a.after, new_path), ordered_bindings_equal=True,
    previously_successful_rows=767, changed_previously_successful_rows=changed,
    comparison_exclusions=['run_binding_sha256', 'toolchain_digest', 'toolchain_versions.census',
        'routes.content_repair.tool_digest (validated against respective frozen registries)',
        'segmentation.result.frame.orientation.evidence.seconds'],
    witness=dict(id=witness, before_disposition=old[witness]['disposition'],
        after_disposition=new[witness]['disposition'], verdict=seg['verdict'], reason=seg['reason'],
        context_unavailable=seg['evidence']['context_unavailable']))
a.output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
