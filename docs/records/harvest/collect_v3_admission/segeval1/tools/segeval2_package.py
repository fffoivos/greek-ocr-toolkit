"""Package SEGEVAL-2 evidence in an isolated Git bundle; no shared Git writes."""
import hashlib,json,shutil,subprocess,tempfile
from pathlib import Path
D=Path(__file__).resolve().parents[1]
BUNDLE=D/'SEGEVAL2.bundle'
assert not BUNDLE.exists(),'Refuse overwrite'
assert json.loads((D/'segeval2_verification.json').read_text())['ok']
relative=Path('docs/harvest/collect_v3_admission/segeval1')
files=[]
for folder in ('answers','scan','scored','prompts'):
 files.extend(p for p in (D/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
for name in ('HANDOFF.md','SEGEVAL1_RESULT.md','SEGEVAL2_HANDOFF.md','segeval1_score.py','test_score.py','draw_receipt.json','pack_closure.json','unresolved_population.json','segeval2_tests.log','segeval2_score.log','segeval2_verification.json','segeval2_verification.log','keys/segeval1_a.json','keys/segeval1_b.json','keys/sealed_decisions.jsonl','launchers/run_read.sh','tools/segeval2_rescan.py','tools/segeval2_verify.py','tools/segeval2_package.py'):
 files.append(D/name)
with tempfile.TemporaryDirectory(prefix='segeval2-package-',dir='/private/tmp') as tmp:
 root=Path(tmp)
 for p in files:
  target=root/relative/p.relative_to(D);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
 def git(*args):return subprocess.check_output(['git','-C',tmp,'-c','core.hooksPath=/dev/null',*args],stderr=subprocess.STDOUT).decode().strip()
 git('init','-q','-b','segeval2-artifacts');git('add','--',str(relative))
 git('-c','user.name=Codex','-c','user.email=codex@local','commit','-q','-m','SEGEVAL2: canonical v4.5.5 rescans and final blind evaluation score')
 commit=git('rev-parse','HEAD');git('bundle','create',str(BUNDLE),'segeval2-artifacts')
 verification=git('bundle','verify',str(BUNDLE));git('fsck','--full')
 receipt=dict(commit=commit,branch='segeval2-artifacts',bundle=str(BUNDLE),sha256=hashlib.sha256(BUNDLE.read_bytes()).hexdigest(),bytes=BUNDLE.stat().st_size,bundle_verification=verification,shared_git_modified=False,scope='Standalone scoring/custody/report evidence; existing crop packs and raw rollouts are referenced by path and SHA256, not duplicated. Original SEGEVAL1.bundle unchanged.',files={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)})
 (D/'segeval2_package_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({k:v for k,v in receipt.items() if k!='files'},indent=2))
