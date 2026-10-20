"""Offline validation with collector functions and an exact three-file temp mirror."""
import hashlib
import json
from pathlib import Path
import shutil
import socket
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
sys.dont_write_bytecode = True
# Fail closed if an import or validator attempts network access.
def deny_network(event, args):
    if event in {'socket.connect', 'socket.connect_ex', 'socket.getaddrinfo', 'socket.sendto'}:
        raise RuntimeError('Network disabled for GATE2b validation')
sys.addaudithook(deny_network)
from collect_v3 import runner

RUN = Path.home() / 'Projects/collect-v3-data/run'
OLD_SHA = 'eb4a17ed1924ff77a863460fe8445f8437c62a5a68a9b4418f159e71fbf7dc98'
SOURCES = ['bsb_poly1850', 'ia_poly1850', 'nlg', 'serbia', 'elstat', 'gazette_modern']
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

raw = (RUN / 'c1_gate.json').read_bytes()
assert hashlib.sha256(raw).hexdigest() == OLD_SHA
before = json.loads(raw)
after = json.loads((HERE / 'c1_gate.next.json').read_bytes())
assert set(after) == set(before) | {'extended_at', 'extended_by'}
assert all(after[k] == v for k, v in before.items() if k != 'sources')
assert set(after['sources']) == set(before['sources']) | {'gazette_modern'}
assert all(after['sources'][k] == v for k, v in before['sources'].items())
assert after['sources']['gazette_modern'] == {
    'passed': True, 'classes': {'modern_scanned': True},
    'note': 'T6b masked cards 97/96 (sol/recut-v1 7f70de90); admission = masked rows for the wave-1d arm only; W2 reads measured_1986_1990 only (all 960 W2 manifest pages)',
    'probe_1982_1985': {'passed': False, 'letters': {'n': 40, 'y': 35}},
}
with tempfile.TemporaryDirectory(prefix='.validation-', dir=HERE) as temp:
    mirror = Path(temp)
    snapshot = Path('W2/gate_snapshots') / (OLD_SHA + '.json')
    (mirror / snapshot).parent.mkdir(parents=True)
    shutil.copyfile(HERE / 'c1_gate.next.json', mirror / 'c1_gate.json')
    shutil.copyfile(RUN / 'W2/state.json', mirror / 'W2/state.json')
    shutil.copyfile(RUN / snapshot, mirror / snapshot)
    files = sorted(str(p.relative_to(mirror)) for p in mirror.rglob('*') if p.is_file())
    assert files == sorted(['c1_gate.json', 'W2/state.json', str(snapshot)])
    assert (mirror / snapshot).read_bytes() == raw
    state = json.loads((mirror / 'W2/state.json').read_bytes())
    old_identity = state['identity']
    assert old_identity['gate_sha256'] == OLD_SHA
    new_identity = dict(old_identity, gate_sha256=sha(mirror / 'c1_gate.json'))
    sources = runner.gate_sources(mirror / 'c1_gate.json', SOURCES)
    probe = runner.probe_qualified(sources['gazette_modern'])
    extension = runner.gate_extension_ok(mirror, old_identity, new_identity)
    assert probe is False and extension is True
    result = {
        'old_gate_sha256': OLD_SHA, 'next_gate_sha256': new_identity['gate_sha256'],
        'gate_sources_ok': True, 'requested_sources': SOURCES,
        'probe_qualified': probe, 'gate_extension_ok': extension,
        'existing_source_values_unchanged': True, 'existing_provenance_unchanged': True,
        'live_gate_equals_starting_snapshot': True, 'gazette_entry_matches_brief': True,
        'identity_changed_fields': ['gate_sha256'], 'mirror_files': files,
        'copied_state_sha256': sha(mirror / 'W2/state.json'),
        'runner_sha256': sha(Path(runner.__file__)), 'python': sys.executable,
        'network': 'OFF; socket audit guard installed', 'live_run_writes': False,
        'collector_recheck': 'Lead must run check_live.py outside sandbox; local ps execution denied by sandbox',
        'temporary_mirror_removed_on_exit': True,
    }
assert not mirror.exists()
(HERE / 'validation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
