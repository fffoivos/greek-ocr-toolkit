"""Canonical CP8 application closure identity, with content validation."""
import hashlib,json,sys
import importlib.metadata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DEFAULT=ROOT/'docs/harvest/collect_v3_admission/seg/cp8a/application_manifest.json'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def identity(path=DEFAULT,verify=True):
    data=Path(path).read_bytes();manifest=json.loads(data)
    if verify:
        if manifest.get('python') is not None and manifest['python'] != sys.version:
            raise ValueError('application Python dependency drift')
        for name,version in manifest.get('dependencies', {}).items():
            if importlib.metadata.version(name) != version:
                raise ValueError('application dependency drift: '+name)
        for name,expected in manifest['files'].items():
            if digest(ROOT/name)!=expected:raise ValueError('application closure drift: '+name)
    return hashlib.sha256(data).hexdigest()
