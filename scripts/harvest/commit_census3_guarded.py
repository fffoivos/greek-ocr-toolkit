"""Verify CENSUS3 artifacts; stage and commit only with explicit --commit."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import greekocr

ROOT = Path(__file__).resolve().parents[2]
assert Path.cwd().resolve() == ROOT
assert Path(greekocr.__file__).resolve().is_relative_to(ROOT), greekocr.__file__
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--commit', action='store_true')
args = parser.parse_args()
manifest_path = ROOT / 'docs/records/harvest/collection/v2/census3_commit_manifest.json'
assert hashlib.sha256(manifest_path.read_bytes()).hexdigest() == '1c55591e268f878b91f251c4b850972d4779419c099ddba36854ac6b28c5c346'
manifest = json.loads(manifest_path.read_text())
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip() == manifest['head']
assert subprocess.check_output(['git','branch','--show-current'],text=True).strip() == manifest['branch']
assert not subprocess.check_output(['git','diff','--cached','--name-only'])
for path, expected in manifest['files'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
from greekocr.harvest import admission as a
receipt = json.loads((ROOT/'docs/records/harvest/collection/v2/ADMISSION_CENSUS_20261018b_admission_receipt.json').read_text())
assert receipt['expected_table_sha256'] == a.expected_table_sha256()
assert receipt['rows_total'] == 271987
subprocess.run(['git','diff','--check'],check=True)
if args.commit:
    subprocess.run(['git','add','--sparse','--',*manifest['stage_paths']],check=True)
    assert set(subprocess.check_output(['git','diff','--cached','--name-only'],text=True).splitlines()) == set(manifest['stage_paths'])
    subprocess.run(['git','diff','--cached','--check'],check=True)
    subprocess.run(['git','commit','-m','CENSUS3: admit distinguishing secondary-script words and reissue v2 census'],check=True)
else:
    print('CENSUS3 guard passed; no staging or commit performed.')
