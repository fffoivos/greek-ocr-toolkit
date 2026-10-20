"""Create and check the source-bound add-only handoff patch without staging."""
from f2lib import *
import subprocess,hashlib
def main():
 manifest=json.loads((BASE/'receipts/commit-inputs.json').read_text());files=list(manifest['files']);mp=BASE/'receipts/commit-inputs.json';files.append(dict(path=str(mp.relative_to(ROOT)),sha256=sha(mp)))
 dest=BASE/'bulk/F2-GR.patch';dest.parent.mkdir(exist_ok=True);binary=0
 with dest.open('wb') as output:
  for r in files:
   path=ROOT/r['path'];data=path.read_bytes();assert digest(data)==r['sha256'];name=r['path']
   if b'\0' in data:
    result=subprocess.run(['git','diff','--no-index','--binary','--','/dev/null',name],cwd=ROOT,capture_output=True)
    if result.returncode not in [0,1]:raise RuntimeError('binary patch failed')
    output.write(result.stdout);binary+=1;continue
   blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
   output.write(f'diff --git a/{name} b/{name}\nnew file mode 100644\nindex {"0"*40}..{blob}\n'.encode())
   if not data:continue
   lines=data.splitlines(keepends=True);output.write(f'--- /dev/null\n+++ b/{name}\n@@ -0,0 +1,{len(lines)} @@\n'.encode())
   for line in lines:
    output.write(b'+'+line)
    if not line.endswith(b'\n'):output.write(b'\n\\ No newline at end of file\n')
 checkdir=BASE/'bulk/patch-check-empty';checkdir.mkdir(exist_ok=True)
 gitdir=subprocess.check_output(['git','rev-parse','--git-dir'],cwd=ROOT,text=True).strip()
 result=subprocess.run(['git','--git-dir='+gitdir,'--work-tree='+str(checkdir),'apply','--check',str(dest)],cwd=checkdir,text=True,capture_output=True)
 receipt=dict(base_HEAD=manifest['base_HEAD'],patch=str(dest.relative_to(BASE)),patch_sha256=sha(dest),bytes=dest.stat().st_size,files=len(files),binary_metadata_files=binary,media_files=0,provider_response_payloads=0,git_apply_check_passed=result.returncode==0,check_stderr=result.stderr,git_index_written=False,commit_created=False,at=stamp())
 write(BASE/'receipts/patch-receipt.json',receipt);print(json.dumps(receipt,ensure_ascii=False,indent=2))
 if result.returncode:raise SystemExit(result.returncode)
if __name__=='__main__':main()
