"""Committed lossless test fixtures; no replay directory or native build needed."""
import hashlib
import json
from pathlib import Path
import numpy as np

HERE=Path(__file__).parent/'fixtures'

def checked_npz(path,expected):
    assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,path
    with np.load(path,allow_pickle=False) as data:return {k:data[k] for k in data.files}

def profiles():
    manifest=json.loads((HERE/'manifest.json').read_text())
    pool=manifest['profile_pool']
    return checked_npz(HERE/pool['file'],pool['sha256'])

def batch(entry):
    data=checked_npz(HERE/entry['file'],entry['sha256'])
    data['profiles']=profiles()[entry['profiles_ref']]
    return data

def render(path):
    data=json.loads(path.read_text());manifest=json.loads((HERE/'manifest.json').read_text())
    assert data['prepared_profiles_sha256']==manifest['profile_pool']['sha256']
    source=data['source'];keys=source.pop('component_columns');rows=source.pop('component_rows')
    source['components']=[dict(zip(keys,row,strict=True)) for row in rows]
    pool=profiles()
    return data,{name:pool[key] for name,key in data['profiles_refs'].items()}
