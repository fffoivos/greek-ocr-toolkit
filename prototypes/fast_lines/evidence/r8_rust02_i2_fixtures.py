"""Lossless one-time fixture compaction and independent old/new byte proof.

Archives originals in i2 evidence first. Does not compute expected answers.
"""
import hashlib, json, shutil
from pathlib import Path
import numpy as np
from .r8_curl_trace import ROOT, dump, sha
O=ROOT/'.astra/fast_lines/out/round8/R8-RUST-02-i2'
F=ROOT/'prototypes/fast_lines/rust_field/fixtures'

def identity(a):
    header=json.dumps(dict(dtype=a.dtype.str,shape=a.shape,fortran=bool(a.flags.f_contiguous and not a.flags.c_contiguous)),sort_keys=True).encode()
    return hashlib.sha256(header+b'\0'+a.tobytes(order='A')).hexdigest()

def compact():
    archive=O/'original-fixtures'
    if not archive.exists():shutil.copytree(F,archive)
    else:
        receipt=json.loads((O/'FIXTURE_EQUIVALENCE.json').read_text())
        assert receipt['old_files']=={p.name:sha(p) for p in archive.iterdir()}
    old=json.loads((archive/'manifest.json').read_text());pool={};references=[];ledger=[]
    def intern(a):
        key='p'+identity(a)
        if key in pool:assert identity(pool[key])==identity(a)
        else:pool[key]=a
        references.append(key);return key
    for entry in old['batches']:
        path=F/entry['file'];d=dict(np.load(archive/entry['file']));entry['original_sha256']=entry['sha256'];entry['profiles_ref']=intern(d.pop('profiles'))
        np.savez_compressed(path,**d);entry['sha256']=sha(path)
    renders=[]
    for path in sorted(F.glob('*-render.json')):
        data=json.loads((archive/path.name).read_text());arraypath=path.with_suffix('.npz');arrays=dict(np.load((archive/path.name).with_suffix('.npz')))
        components=data['source'].pop('components');keys=list(components[0])
        assert all(list(q)==keys for q in components)
        data['source']['component_columns']=keys
        data['source']['component_rows']=[[q[k] for k in keys] for q in components]
        data['profiles_refs']={k:intern(a) for k,a in arrays.items()}
        data['original_prepared_profiles_sha256']=data['prepared_profiles_sha256'];renders.append((path,data));arraypath.unlink(missing_ok=True)
    poolpath=F/'profiles.npz';np.savez_compressed(poolpath,**pool)
    old['profile_pool']=dict(file=poolpath.name,sha256=sha(poolpath),identity='SHA256 of dtype.str/shape/Fortran-order header, zero separator, exact bytes in physical order',arrays={k:dict(dtype=a.dtype.str,shape=list(a.shape),fortran=bool(a.flags.f_contiguous and not a.flags.c_contiguous)) for k,a in pool.items()})
    for path,data in renders:
        data['prepared_profiles_sha256']=sha(poolpath)
        path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
    (F/'manifest.json').write_text(json.dumps(old,ensure_ascii=False,separators=(',',':'))+'\n')
    # Compare each reconstructed original array independently, including NaN payloads.
    for entry in old['batches']:
        before=dict(np.load(archive/entry['file']));after=dict(np.load(F/entry['file']));after['profiles']=pool[entry['profiles_ref']]
        assert before.keys()==after.keys()
        for k in before:
            assert identity(before[k])==identity(after[k]),(entry['file'],k)
            ledger.append(dict(file=entry['file'],array=k,identity=identity(before[k]),bytes=before[k].nbytes,dtype=before[k].dtype.str,shape=list(before[k].shape)))
    for path,data in renders:
        previous=json.loads((archive/path.name).read_text());previous_arrays=dict(np.load((archive/path.name).with_suffix('.npz')))
        for k,a in previous_arrays.items():
            assert identity(a)==identity(pool[data['profiles_refs'][k]])
            ledger.append(dict(file=path.with_suffix('.npz').name,array=k,identity=identity(a),bytes=a.nbytes,dtype=a.dtype.str,shape=list(a.shape)))
        # Canonical JSON preserves every parsed float, integer and NaN representation.
        reconstructed={k:v for k,v in data.items() if k not in ('profiles_refs','original_prepared_profiles_sha256')}
        reconstructed['prepared_profiles_sha256']=data['original_prepared_profiles_sha256']
        source=dict(reconstructed['source']);keys=source.pop('component_columns');rows=source.pop('component_rows')
        source['components']=[dict(zip(keys,row,strict=True)) for row in rows]
        reconstructed['source']=source
        assert json.dumps(previous,sort_keys=True,separators=(',',':'))==json.dumps(reconstructed,sort_keys=True,separators=(',',':'))
    dump(O/'FIXTURE_EQUIVALENCE.json',dict(old_files={p.name:sha(p) for p in archive.iterdir()},new_files={p.name:sha(p) for p in F.iterdir()},original_bytes=sum(p.stat().st_size for p in archive.iterdir()),compacted_bytes=sum(p.stat().st_size for p in F.iterdir()),profile_references=len(references),unique_profile_identities=len(pool),arrays=ledger,batches=24,render_consumers=6,expected_values='preserved from original JSON; never regenerated',all_exact=True))

if __name__=='__main__':compact()
