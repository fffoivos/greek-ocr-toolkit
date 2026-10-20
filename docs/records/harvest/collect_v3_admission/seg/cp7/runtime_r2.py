"""R2 launcher mapping, enforcing all five crop questions."""
from r2_common import *
import runtime
import r2_common

AMENDMENT=R2/'runtime_amendment_cp7c2.json'

def verify_runtime_freeze():
    """Verify the original freeze with exactly one declared runtime amendment."""
    amendment=read(AMENDMENT)
    path=Path(__file__).resolve()
    relative=str(path.relative_to(ROOT))
    frozen=read(FREEZE)
    assert amendment['freeze_sha256']==sha(FREEZE)
    assert amendment['path']==relative
    assert amendment['original_sha256']==frozen['files'][relative]
    assert amendment['amended_sha256']==sha(path), 'runtime amendment drift'
    original=r2_common.sha
    def bound_sha(p):
        return amendment['original_sha256'] if Path(p).resolve()==path else original(p)
    try:
        r2_common.sha=bound_sha
        return verify()
    finally:
        r2_common.sha=original

def post_read_closure(directory,expected):
    """Hash the recorded originals; permit only HANDOVER reader products."""
    directory=Path(directory)
    assert directory.is_dir() and not directory.is_symlink()
    for rel,digest in expected.items():
        p=Path(rel)
        assert not p.is_absolute() and '..' not in p.parts
        original=directory/p
        assert original.is_file() and not original.is_symlink(), rel
        assert sha(original)==digest, 'original changed: '+rel
    for p in directory.rglob('*'):
        rel=p.relative_to(directory).as_posix()
        assert not p.is_symlink(), 'symlink: '+rel
        if p.is_file():
            assert p.stat().st_nlink==1, 'hardlink: '+rel
            assert rel in expected or rel=='answers.jsonl' or rel.startswith('zoom/'), 'unallowed file: '+rel
        else:
            assert p.is_dir(), 'special file: '+rel
            assert rel=='zoom' or rel.startswith('zoom/') or any(f.startswith(rel+'/') for f in expected), 'unallowed directory: '+rel
    return dict(expected)

def verify_packs(beds,pre_read=False):
    recorded=read(R2/'pack_closure.json')['contexts']
    for bed in beds:
        expected=next(c['files'] for c in recorded if c['bed']==bed and c['reader']=='r1')
        directory=PACK_ROOT/bed/'r1'
        assert read(directory.parent/'MANIFEST.r1.json')['files']==expected
        if pre_read:
            key=read(R2/'keys'/f'{bed}.json')
            assert closure(directory,key['readers']['r1'])==expected
        else:
            post_read_closure(directory,expected)

def map_records(answers,items,key):
    previous=runtime.RUBRIC
    try:
        runtime.RUBRIC=previous+('end_clip',)
        return runtime.map_records(answers,items,key)
    finally:runtime.RUBRIC=previous

def main():
    guard()
    runtime.HERE=R2;runtime.BEDS=BEDS_R2
    runtime.RUBRIC=runtime.RUBRIC+('end_clip',)
    action,*args=sys.argv[1:]
    if action in ('verify','pre-read'):
        verify_runtime_freeze();receipt=read(R2/'build_receipt.json')
        assert receipt['freeze_sha256']==sha(FREEZE)
        assert receipt['draw_sha256']==sha(R2/'keys/draw.jsonl')
        assert receipt['sealed_decisions_sha256']==sha(R2/'keys/sealed_decisions.jsonl.gz')
        if action=='pre-read':
            assert len(args)==1 and args[0] in BEDS_R2
            verify_packs(args,pre_read=True)
        else:
            verify_packs(BEDS_R2)
        return
    if action=='receipt':
        verify_runtime_freeze()
        assert args[0] in BEDS_R2
        verify_packs([args[0]])
        # Keep the native receipt schema with the r2 freeze binding.
        original=runtime.sha
        runtime.sha=lambda p: original(FREEZE if Path(p)==SEG/'CP7_FREEZE.json' else p)
    runtime.main()

if __name__=='__main__':main()
