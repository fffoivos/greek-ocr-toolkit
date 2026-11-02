"""One CAS commit to public greek-ocr-lines main: add metadata/real_lines.parquet + updated README. Read back, then tag v0.5. Token from HF_TOKEN."""
import os, sys, json, hashlib
from huggingface_hub import HfApi, CommitOperationAdd, hf_hub_download
REPO, PARENT = 'fffoivos/greek-ocr-lines', '859fa9873d5ed23e49f01ae7628be6ef3d9c4e50'
D = '/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/release_v0/builds/hfd-e1-001/lines-meta'
api = HfApi(token=os.environ['HF_TOKEN'])
assert not api.repo_info(REPO, repo_type='dataset').private
assert api.repo_info(REPO, repo_type='dataset').sha == PARENT, 'main moved'
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
files = {'metadata/real_lines.parquet': D + '/metadata/real_lines.parquet', 'README.md': D + '/README.md'}
def tree(rev):
    return {e.path: (e.blob_id, e.lfs.sha256 if getattr(e, 'lfs', None) else None) for e in
            api.list_repo_tree(REPO, repo_type='dataset', revision=rev, recursive=True) if getattr(e, 'blob_id', None)}
before = tree(PARENT)
info = api.create_commit(REPO, repo_type='dataset', parent_commit=PARENT,
    operations=[CommitOperationAdd(path_in_repo=k, path_or_fileobj=v) for k, v in files.items()],
    commit_message='Greek OCR lines v0.5: per-line book source and position (line_metadata); card')
new = info.oid; print('COMMIT', new, flush=True)
after = tree(new)
assert after['metadata/real_lines.parquet'][1] == sha(files['metadata/real_lines.parquet']), 'parquet sha differs'
rd = hf_hub_download(REPO, 'README.md', repo_type='dataset', revision=new, local_dir='/tmp/fffoivos-readme-check')
assert sha(rd) == sha(files['README.md']), 'README differs'
unchanged = {p: v for p, v in before.items() if p != 'README.md'}
assert all(after.get(p) == v for p, v in unchanged.items()), 'other files changed'
assert set(after) == set(before) | {'metadata/real_lines.parquet'}, 'unexpected paths'
print('READBACK PASS', len(after), 'files;', len(unchanged), 'unchanged from parent', flush=True)
api.create_tag(REPO, repo_type='dataset', tag='v0.5', revision=new, tag_message='Greek OCR lines v0.5')
t = [x for x in api.list_repo_refs(REPO, repo_type='dataset').tags if x.name == 'v0.5'][0]
assert t.target_commit == new
print('TAG v0.5 ->', t.target_commit, flush=True)
