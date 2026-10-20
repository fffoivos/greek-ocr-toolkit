"""Package only SEGEVAL1 artifacts in a temporary Git repository, no shared .git writes."""
import hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
D=Path(__file__).resolve().parents[1]
assert not (D/'SEGEVAL1.bundle').exists(),'Refuse overwrite'
tmp=Path(tempfile.mkdtemp(prefix='segeval1-package-',dir='/private/tmp'))
relative=Path('docs/harvest/collect_v3_admission/segeval1');dest=tmp/relative
shutil.copytree(D,dest,ignore=shutil.ignore_patterns('SEGEVAL1.bundle','package_receipt.json','__pycache__'))
def git(*args):return subprocess.check_output(['git','-C',str(tmp),'-c','core.hooksPath=/dev/null',*args],stderr=subprocess.STDOUT).decode().strip()
git('init','-q','-b','segeval1-artifacts');git('add','--',str(relative))
git('-c','user.name=Codex','-c','user.email=codex@local','commit','-q','-m','SEGEVAL1: sealed blind 50 reject / 100 accept evaluation artifacts')
commit=git('rev-parse','HEAD')
git('bundle','create',str(D/'SEGEVAL1.bundle'),'segeval1-artifacts')
verification=git('bundle','verify',str(D/'SEGEVAL1.bundle'))
bundle=D/'SEGEVAL1.bundle'
receipt=dict(commit=commit,branch='segeval1-artifacts',bundle=str(bundle),sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),bytes=bundle.stat().st_size,bundle_verification=verification,shared_git_modified=False,excluded=['SEGEVAL1.bundle','package_receipt.json'],files=git('ls-tree','-r','--name-only','HEAD').splitlines())
(D/'package_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='files'},indent=2))
shutil.rmtree(tmp)
