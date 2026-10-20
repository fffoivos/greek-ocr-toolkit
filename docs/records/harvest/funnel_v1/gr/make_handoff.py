"""Build a source-bound, media-free fallback after the managed Git write refusal."""
from funnellib import *
import difflib,subprocess,tempfile

def run():
    root=BASE.parents[3]
    base=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
    files=[]
    for p in sorted(BASE.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts:continue
        rel=p.relative_to(BASE)
        if 'bulk' in rel.parts and rel.as_posix()!='bulk/.gitignore':continue
        if rel.as_posix()=='receipts/commit-inputs.json':continue
        ignored=subprocess.run(['git','check-ignore',str(p)],cwd=root,capture_output=True,text=True)
        if ignored.returncode==0:continue
        files.append(dict(path=str(p.relative_to(root)),sha256=sha(p.read_bytes()),bytes=p.stat().st_size))
    manifest=BASE/'receipts/commit-inputs.json'
    write(manifest,dict(base_HEAD=base,branch='sol/funnel-gr',files=files,excluded='All bulk payloads, credentials and Python caches; bulk/.gitignore retained',worker_commit=None,reason='Managed shared-index write refusal'))
    paths=[root/r['path'] for r in files]+[manifest]
    patch=BASE/'bulk/F1-GR.patch'
    with patch.open('w') as out:
        for p in paths:
            rel=str(p.relative_to(root));data=p.read_text();assert not data or data.endswith('\n')
            out.write(f'diff --git a/{rel} b/{rel}\nnew file mode 100644\n')
            if not data:
                out.write('index 0000000..e69de29\n');continue
            out.writelines(difflib.unified_diff([],data.splitlines(keepends=True),fromfile='/dev/null',tofile='b/'+rel,n=3))
    # All handoff paths are new at the pinned base; test the patch in an empty
    # isolated directory without staging or changing the protected worktree.
    existing=subprocess.run(['git','ls-tree','-r','--name-only',base,'--','docs/harvest/funnel_v1/gr'],cwd=root,capture_output=True,text=True,check=True).stdout
    if existing.strip():raise RuntimeError('handoff paths already tracked at base; new-file patch not applicable')
    with tempfile.TemporaryDirectory(prefix='f1-gr-patch-',dir='/private/tmp') as tmp:
        check=subprocess.run(['git','apply','--check','--whitespace=error',str(patch)],cwd=tmp,capture_output=True,text=True)
    receipt=dict(base_HEAD=base,patch=str(patch.relative_to(BASE)),patch_sha256=sha(patch.read_bytes()),patch_bytes=patch.stat().st_size,files=len(paths),manifest_sha256=sha(manifest.read_bytes()),apply_check_passed=check.returncode==0,apply_check_stderr=check.stderr,worker_commit=None)
    write(BASE/'bulk/patch-validation.json',receipt)
    if check.returncode:raise RuntimeError(check.stderr)
    print(json.dumps(receipt))

if __name__=='__main__':run()
