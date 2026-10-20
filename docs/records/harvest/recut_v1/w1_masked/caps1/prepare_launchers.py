"""Copy the three reference launchers; substitute output/workspace paths only."""
from __future__ import annotations

import difflib
import json
from pathlib import Path
import shutil

from build import HERE, REPO, REFERENCE, PACK_ROOT, dump, sha, io_guard

NAMES = ('run_bed.sh', 'run_read.sh', 'limit_probe.sh')


def configured(name):
    text = (REFERENCE / 'launchers' / name).read_text()
    if name == 'run_bed.sh':
        old = 'S=$(cd "$(dirname "$0")" && pwd); W=~/Projects/greek-ocr-toolkit-sol-reading; D=$W/docs/harvest/sol_reading'
        new = 'S=' + str(HERE / 'launchers') + '; W=' + str(REPO) + '; D=$W/docs/harvest/recut_v1/w1_masked/caps1'
        assert text.count(old) == 1
        text = text.replace(old, new)
        text = text.replace('RD=$S/sol_reading_packs/', 'RD=' + str(PACK_ROOT) + '/')
        text = text.replace('$D/answers/$BED/$RDR.scan.json', '$D/scan/$BED/$RDR.scan.json')
    else:
        old = 'S=$(cd "$(dirname "$0")" && pwd)'
        assert text.count(old) == 1
        text = text.replace(old, 'S=' + str(HERE / 'launchers'))
    return text


def prepare():
    private = HERE / 'launchers'
    public = PACK_ROOT / 'launchers'
    for directory in (private, public, private / 'logs', private / 'prompts_rendered', HERE / 'scan/caps1', HERE / 'answers/caps1'):
        directory.mkdir(parents=True, exist_ok=True)
    diffs = []
    sources = {}
    for name in NAMES:
        original = REFERENCE / 'launchers' / name
        target = private / name
        target.write_text(configured(name))
        target.chmod(0o755)
        shutil.copyfile(target, public / name)
        (public / name).chmod(0o755)
        assert sha(target) == sha(public / name)
        sources[str(original)] = sha(original)
        diffs.append(''.join(difflib.unified_diff(original.read_text().splitlines(True), target.read_text().splitlines(True),
                     fromfile='Sol-reading/launchers/' + name, tofile='CAPS1/launchers/' + name)))
    (HERE / 'launchers.diff').write_text('\n'.join(diffs))
    tools = HERE / 'tools'
    tools.mkdir(parents=True, exist_ok=True)
    wrappers = {
        'scan_rollout.py': 'from reference_adapter import rollout_scanner\nraise SystemExit(rollout_scanner().main())\n',
        'replay_literal.py': "from reference_adapter import load_reference, REPLAY_SUBSTITUTIONS\nload_reference('replay_literal', REPLAY_SUBSTITUTIONS).worker(sys.argv[1], sys.stdin.read())\n",
        'map_answers.py': '''import json
from reference_adapter import map_answers
if len(sys.argv) != 4 or sys.argv[1] != 'caps1' or sys.argv[2] not in ('c1', 'c2'):
    raise SystemExit('expected: caps1 c1|c2 answers.jsonl')
print(json.dumps(map_answers(sys.argv[2], sys.argv[3])))
''',
        'ledger.py': "from reference_adapter import load_reference, require_approval\nrequire_approval()\nload_reference('ledger').main()\n",
        'scan_packs.py': '''import json
from reference_adapter import closure
from build import BED
directories = [Path(x) for x in sys.argv[1:]] or [BED / c for c in ('c1', 'c2')]
results = [closure(d, compatible=True) for d in directories]
print(json.dumps(results, ensure_ascii=False, indent=2))
raise SystemExit(0 if all(r['ok'] for r in results) else 2)
''',
    }
    prefix = '# Read-only Sol-reading tool routing; no reference worktree writes.\nimport sys\nfrom pathlib import Path\nsys.dont_write_bytecode = True\nsys.path.insert(0, str(Path(__file__).resolve().parents[1]))\n'
    for name, body in wrappers.items():
        (tools / name).write_text(prefix + body)
    for name in ('common.py', 'scan_packs.py', 'scan_rollout.py', 'replay_literal.py', 'map_answers.py', 'ledger.py', 'owner39_validate.py', 'owner39_common.py'):
        path = REFERENCE / 'tools' / name
        sources[str(path)] = sha(path)
    dump(HERE / 'runtime_bindings.json', dict(reference_sources=sources,
         launchers={name: sha(private / name) for name in NAMES}, public_launcher_directory=str(public),
         output_root=str(HERE), tools='local entrypoints import read-only Sol-reading source functions',
         logic_changes_to_launchers=False, adapter_approval='approved: user CAPS1b ruling 2', readers_started=0))
    print('Prepared 3 launchers in both locations; 5 read-only reference-tool entrypoints; no reader run.')


if __name__ == '__main__':
    io_guard()
    prepare()
