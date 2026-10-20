"""Bind compiled evidence to an exact historical source snapshot and replay code."""
import ast
import hashlib
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_source(recorded_sha,current,snapshot):
    current,snapshot=Path(current),Path(snapshot)
    if not snapshot.exists() and digest(current)==recorded_sha:
        snapshot.parent.mkdir(parents=True,exist_ok=True)
        snapshot.write_bytes(current.read_bytes())
    if digest(snapshot)!=recorded_sha:raise ValueError('compiled source snapshot SHA mismatch')
    def functions(path):
        return {node.name:ast.dump(node,include_attributes=False)
                for node in ast.parse(path.read_text()).body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
    before,after=functions(snapshot),functions(current)
    if set(before)!=set(after):raise ValueError('compiled source function scope changed')
    changed=sorted(name for name in before if before[name]!=after[name])
    if set(changed)-{'read_records','validate','publish'}:
        raise ValueError('raster/admission source changed: '+', '.join(changed))
    return dict(executed_source_sha256=recorded_sha,snapshot_path=str(snapshot),
        current_replay_source_sha256=digest(current),changed_functions=changed,
        raster_admission_builder_ast_unchanged=True,
        policy='exact execution-source SHA plus unchanged raster/admission AST; all final rasters/layouts/JPEG hashes independently replayed')
