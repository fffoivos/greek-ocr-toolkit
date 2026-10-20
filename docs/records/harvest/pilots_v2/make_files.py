"""Inventory durable P1 evidence, including ignored bulk files, without self-hashing."""
import csv,os
from pilotlib import BASE,ROOT,sha

def durable(path):
    rel=path.relative_to(BASE)
    return path.is_file() and rel.as_posix()!='FILES.tsv' and not any(part in ('__pycache__','logs') for part in rel.parts) and path.suffix not in ('.log','.lock','.tmp','.pyc') and not path.name.startswith('.') and path.name!='.DS_Store'

def role(path):
    first=path.relative_to(BASE).parts[0]
    return {'bulk':'source/derived bulk evidence','google':'raw/parsed provider response or live ledger','cache':'detector/HTTP cache','contact_sheets':'20-page contact sheet','blind_sheets':'unadjudicated blind audit pack','receipts':'receipt or ledger copy'}.get(first,'method/report/manifest')

if __name__=='__main__':
    paths=sorted(p for p in BASE.rglob('*') if durable(p))
    # Include the ignore policy explicitly; omit only generated hidden cache state.
    paths=sorted(set(paths+[BASE/'.gitignore',ROOT/'tests/test_p1b_alignment.py']))
    total=0
    with (BASE/'FILES.tsv').open('w',newline='') as stream:
        writer=csv.writer(stream,delimiter='\t',lineterminator='\n');writer.writerow(['path','bytes','sha256','role'])
        for path in paths:
            size=path.stat().st_size;total+=size
            writer.writerow([os.path.relpath(path,BASE),size,sha(path),role(path) if path.is_relative_to(BASE) else 'P1b regression tests'])
    print(f'Inventoried {len(paths)} durable files, {total:,} bytes; FILES.tsv excludes its own checksum and ephemeral logs/locks/bytecode.')
