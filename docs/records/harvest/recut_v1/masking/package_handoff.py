"""Package a validated text-only source manifest after a terminal commit block.

Never stages, changes an index, or retries a commit. Applies only in a fresh
private temporary directory to verify the exact handoff bytes.
"""
from __future__ import annotations
import gzip,hashlib,json,subprocess,tempfile
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]


def main():
    status=json.loads((OUT/'COMMIT_STATUS.json').read_text())
    assert status['status']=='commit_blocked' and not status['retry_attempted'] and not status['alternate_index_used']
    subprocess.run([str(ROOT/'.venv/bin/python'),str(OUT/'guarded_commit.py'),'--check-only'],cwd=ROOT,check=True)
    manifest=json.loads((OUT/'commit-inputs.json').read_text())
    files=manifest['files']+[dict(path=str((OUT/'commit-inputs.json').relative_to(ROOT)),sha256=hashlib.sha256((OUT/'commit-inputs.json').read_bytes()).hexdigest())]
    chunks=[]
    for row in files:
        path=row['path'];data=(ROOT/path).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
        # This task adds new files only. Refuse to synthesize a replacement for
        # an existing tracked path or to put a binary payload in the patch.
        tracked=subprocess.run(['git','cat-file','-e',manifest['base_HEAD']+':'+path],cwd=ROOT,capture_output=True)
        assert tracked.returncode!=0,path
        if not data:
            chunks.extend([f'diff --git a/{path} b/{path}\n','new file mode 100644\n',
                           'index 0000000..e69de29\n'])
            continue
        content=data.decode('utf-8');assert content.endswith('\n'),path
        lines=content.splitlines(keepends=True)
        chunks.extend([f'diff --git a/{path} b/{path}\n',f'new file mode 100644\n',
                       '--- /dev/null\n',f'+++ b/{path}\n',f'@@ -0,0 +1,{len(lines)} @@\n'])
        chunks.extend('+'+line for line in lines)
    patch=''.join(chunks).encode();dest=OUT/'handoff.patch.gz';dest.write_bytes(gzip.compress(patch,mtime=0))
    with tempfile.TemporaryDirectory(prefix='t6a2-handoff-') as tmp:
        subprocess.run(['git','apply','--check','-'],cwd=tmp,input=patch,check=True)
        subprocess.run(['git','apply','-'],cwd=tmp,input=patch,check=True)
        for row in files:assert hashlib.sha256((Path(tmp)/row['path']).read_bytes()).hexdigest()==row['sha256']
    receipt=dict(status='validated_patch_no_worker_commit',source_HEAD=manifest['base_HEAD'],
        manifest_sha256=hashlib.sha256((OUT/'commit-inputs.json').read_bytes()).hexdigest(),
        patch_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),files=len(files),
        applied_in_fresh_temporary_directory=True,every_file_sha256_verified=True,
        commit_retry=False,alternate_index=False,ignored_rasters_excluded=True)
    (OUT/'HANDOFF.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
