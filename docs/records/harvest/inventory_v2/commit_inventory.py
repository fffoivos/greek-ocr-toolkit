"""Source-bound commit handoff after the managed sandbox denied index.lock.

`python3 docs/harvest/inventory_v2/commit_inventory.py --check` is read-only.
Without --check it stages only this inventory directory and commits locally.
It never pushes, uses another index, changes worktrees, or retries a denied write.
"""
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE=pathlib.Path(__file__).resolve().parent
SCOPE='docs/harvest/inventory_v2'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def stop(s):raise SystemExit(s)
if sys.argv[1:] not in ([],['--check']):stop('Usage: commit_inventory.py [--check]')
receipt=json.loads((BASE/'receipts/local/commit-inputs.json').read_text())
if str(ROOT)!=receipt['worktree']:stop('Wrong worktree')
if git('rev-parse','--show-toplevel')!=str(ROOT):stop('Wrong Git root')
if git('branch','--show-current')!=receipt['branch']:stop('Branch changed')
if git('rev-parse','HEAD')!=receipt['head']:stop('Source HEAD changed; review and regenerate the handoff')
for r in receipt['files']:
    p=ROOT/r['path']
    if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:stop('Inventory input changed: '+r['path'])
staged=git('diff','--cached','--name-only').splitlines()
if any(not p.startswith(SCOPE+'/') for p in staged):stop('Unrelated staged changes exist; refusing a combined commit')
v=json.loads((BASE/'receipts/local/validation.json').read_text())
if v['status']!='PASS':stop('Inventory validation is not PASS')
known={r['path'] for r in receipt['files']}|{SCOPE+'/receipts/local/commit-inputs.json'}
visible=set(git('ls-files','--cached','--others','--exclude-standard','--',SCOPE).splitlines())
if visible-known:stop('New inventory files require review: '+str(sorted(visible-known)))
print('PASS: branch, HEAD, inventory hashes, validation and commit scope')
if '--check' in sys.argv:raise SystemExit(0)
subprocess.run(['git','add','--',SCOPE],cwd=ROOT,check=True)
subprocess.run(['git','commit','-m','docs: inventory data-plan v2 sources, rights and bounded probes'],cwd=ROOT,check=True)
print(git('log','-1','--format=%h %s'))
