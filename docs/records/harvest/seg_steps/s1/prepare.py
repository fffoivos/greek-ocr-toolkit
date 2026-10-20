from pathlib import Path
import hashlib,json,subprocess
R=Path.cwd(); D=R/'docs/harvest/seg_steps/s1'
paths=set(subprocess.check_output(['git','ls-files'],text=True).splitlines())
paths|={str(p.relative_to(R)) for p in (R/'docs/harvest/seg_census/package').rglob('*') if p.is_file()}
paths.add('docs/harvest/seg09/cp1_initial_hashes.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
state={p:sha(R/p) for p in sorted(paths) if (R/p).is_file()}
(D/'initial_hashes.json').write_text(json.dumps(state,indent=2)+'\n')
for p in ['greekocr/harvest/filtering_assets/crop-tools.py','scripts/harvest/build_filter_versions.py','docs/harvest/line_pipeline/tool_versions.json','tests/test_seg_gate.py']:
 t=D/'baseline'/p;t.parent.mkdir(parents=True,exist_ok=True);t.write_bytes((R/p).read_bytes())
(D/'initial_git_status.txt').write_text(subprocess.check_output(['git','status','--short'],text=True))
