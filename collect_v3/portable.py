"""Prepare/verify the cached F2 proof bundle, without acquisition or inference."""
import argparse,copy,os,shutil
from pathlib import Path
from .common import read_json,write_json,write_rows_gz,rows,sha

def pack(projects,dest,manifest):
    from .offline import fixtures
    if os.environ.get('COLLECT_V3_FIXTURE_ROOT'):raise ValueError('pack requires original cached F2 inputs')
    dest=Path(dest)
    if dest.exists():raise ValueError('choose a fresh fixture destination')
    fs,overrides,expected=fixtures(projects);dest.mkdir(parents=True)
    ids={f['page']['id'] for f in fs};portable=[]
    for original in fs:
        f=copy.deepcopy(original);key=f['page']['id'];sub=dest/key;sub.mkdir()
        for source,name in ((f['page']['image'],'page.jpg'),(f['raw'],'raw.json')):
            shutil.copyfile(source,sub/name)
        for name in ('receipt.json','detector.json.gz','ink.png','labels.npz'):
            target=sub/'detector'/name;target.parent.mkdir(exist_ok=True);shutil.copyfile(Path(f['detector_cache'])/name,target)
        f['page']['image']=key+'/page.jpg';f['raw']=key+'/raw.json';f['detector_cache']=key+'/detector';portable.append(f)
    expected=[dict(r,crop_page_path=r['page_id']+'/page.jpg') for r in expected if r['page_id'] in ids]
    write_rows_gz(dest/'expected.jsonl.gz',expected)
    write_rows_gz(dest/'overrides.jsonl.gz',[r for r in overrides.values() if r['page_id'] in ids])
    write_json(dest/'fixtures.json',portable)
    base=Path(projects)/'greek-ocr-toolkit-sol-funnel-gr/docs/harvest/screen_v1/receipts/statistics.json'
    shutil.copyfile(base,dest/'statistics.json')
    shutil.copyfile(Path(__file__).resolve().parents[1]/'docs/harvest/collect_v3/convention_context.json',dest/'convention_context.json')
    hashes={str(p.relative_to(dest)):sha(p) for p in sorted(dest.rglob('*')) if p.is_file()}
    write_json(manifest,dict(schema='collect-v3-portable-f2-1',pages=len(fs),network=False,sha256=hashes))
    return len(hashes)

def verify(dest,manifest=None):
    dest=Path(dest).resolve();manifest=Path(manifest or Path(__file__).resolve().parents[1]/'worker/fixture_manifest.json')
    binding=read_json(manifest)
    for name,digest in binding['sha256'].items():
        path=dest/name
        if path.is_symlink() or dest not in path.resolve().parents or not path.is_file() or sha(path)!=digest:
            raise ValueError('portable fixture missing or hash mismatch: '+name)
    return binding

def load(dest):
    dest=Path(dest).resolve();verify(dest);fs=read_json(dest/'fixtures.json')
    for f in fs:
        for key in ('raw','detector_cache'):f[key]=str(dest/f[key])
        f['page']['image']=str(dest/f['page']['image'])
    expected=[dict(r,crop_page_path=str(dest/r['crop_page_path'])) for r in rows(dest/'expected.jsonl.gz')]
    return fs,{r['id']:r for r in rows(dest/'overrides.jsonl.gz')},expected

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['pack','verify']);p.add_argument('--root',required=True);p.add_argument('--manifest');p.add_argument('--projects-root');a=p.parse_args()
    if a.operation=='pack':print('packed files:',pack(a.projects_root,a.root,a.manifest))
    else:print('fixture pages verified:',verify(a.root,a.manifest)['pages'])
