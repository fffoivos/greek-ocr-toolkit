"""Bounded read-only Clariden retrieval. No submissions or remote writes."""
import subprocess,sys,tarfile,io,json,pathlib
ROOT='/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/labelfix_sf7_test_20261019'
OUT=pathlib.Path(__file__).resolve().parent/'output_3702849'
def remote(code):
 p=subprocess.run(['ssh','clariden','python3 -B -'],input=code.encode(),stdout=subprocess.PIPE,check=True)
 return p.stdout
code=f'''import pathlib,json,tarfile,sys
root=pathlib.Path({ROOT!r});run=root/'output_3702849'
files=[]
for p in run.rglob('*'):
 if not p.is_file():continue
 if (p.suffix=='.json' and (any(t in p.name.lower() for t in ('receipt','summary')) or p.name.startswith('release_'))) or p.name.startswith('release_edits_only_'):files.append(p)
files.append(root/'logs/TR2_3702849.log')
assert sum(p.stat().st_size for p in files)<190_000_000
with tarfile.open(fileobj=sys.stdout.buffer,mode='w|') as t:
 for p in sorted(files):t.add(p,arcname=str(p.relative_to(run)) if str(p).startswith(str(run)+'/') else p.name,recursive=False)
'''
b=remote(code)
assert len(b)<200_000_000
with tarfile.open(fileobj=io.BytesIO(b)) as t:
 for m in t:
  assert m.isfile() and not m.name.startswith('/') and '..' not in pathlib.Path(m.name).parts
  p=OUT/m.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(t.extractfile(m).read())
p=subprocess.run(['ssh','clariden','sacct -j 3702849 --parsable2 --format=JobID,State,ExitCode,Elapsed,ElapsedRaw,Start,End,AllocTRES'],stdout=subprocess.PIPE,check=True)
(OUT/'job_state.txt').write_bytes(p.stdout)
print('Retrieved',sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file()),'bytes')
