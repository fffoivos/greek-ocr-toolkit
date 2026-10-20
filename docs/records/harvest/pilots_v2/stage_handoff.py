"""Source-bound staging handoff; run in a normal terminal with Git write access."""
import argparse,csv,json,subprocess
from pilotlib import *
from validate import verify_files

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.add_argument('--stage',action='store_true');args=parser.parse_args()
    receipt=json.loads((BASE/'receipts/git-handoff.json').read_text())
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
    if head!=receipt['head'] or branch!=receipt['branch']:raise SystemExit('Branch/HEAD changed; review the handoff before staging.')
    checked=verify_files();paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z','--','docs/harvest/pilots_v2'],cwd=ROOT).decode().split('\0');paths=sorted(set(p for p in paths if p))
    if any(any(part in p.split('/') for part in ['bulk','google','cache','contact_sheets','blind_sheets','logs','__pycache__']) for p in paths):raise SystemExit('Bulk path entered Git scope; stop.')
    with (BASE/'FILES.tsv').open() as stream:manifested={r['path'] for r in csv.DictReader(stream,delimiter='\t')}
    if any(pathlib.Path(p).relative_to(BASE.relative_to(ROOT)).as_posix() not in manifested|{'FILES.tsv'} for p in paths):raise SystemExit('An unmanifested file entered the staging scope; review and rebuild FILES.tsv.')
    print(f'Verified {checked} files; {len(paths)} tracking-compatible deliverable files; {branch} at {head}.')
    if args.stage:
        subprocess.run(['git','add','--',*paths],cwd=ROOT,check=True);print('Deliverables staged. No commit or push performed.')
