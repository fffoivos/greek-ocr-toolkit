"""Read-only CP1 verification: saved gate, guarded entrypoints, bound artifacts."""
import hashlib
import json
import runpy
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'docs/harvest/collect_v3_admission'
sys.path.insert(0,str(BASE/'nw1b'))
sys.path.insert(0,str(ROOT))
sys.dont_write_bytecode=True
import calibrate
from greekocr.harvest import neighbour_words
import greekocr.pages


def main():
    before=json.loads((BASE/'seg/protected_before.json').read_text())
    protected={}
    for name,expected in before.items():
        p=ROOT/name
        actual=dict(sha256=calibrate.sha(p),size=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns)
        if actual != expected: raise ValueError('protected artifact changed: '+name)
        protected[name]=actual
    ledger=json.loads(calibrate.LEDGER.read_text())
    for name,digest in ledger['sources'].items():
        p=Path(name) if Path(name).is_absolute() else ROOT/name
        if calibrate.sha(p)!=digest: raise ValueError('source drift: '+name)
    # Read existing staged PNGs only; compare against the unchanged initial manifest.
    manifest=[json.loads(l) for l in (BASE/'crops_manifest.jsonl').read_text().splitlines()]
    for row in manifest:
        if calibrate.sha(BASE/row['path'])!=row['sha256']:
            raise ValueError('staged crop mismatch: '+row['row_id'])
    events=[]; state={'guarding':False,'detector_calls':0}
    def detector(*args,**kwargs):
        state['detector_calls']+=1
        raise AssertionError('CP1 detector call forbidden')
    greekocr.pages.process_page=detector
    neighbour_words.page_measurements=detector
    def audit(event,args):
        if not state['guarding']: return
        if event.startswith('socket.'):
            raise AssertionError('network OFF')
        write=False
        if event=='open':
            mode=args[1]
            flags=args[2]
            write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags & 3))
        if event in ('os.rename','os.remove','os.rmdir','os.mkdir','os.truncate','os.link','os.symlink'):
            write=True
        if write:
            events.append(event)
            raise AssertionError('CP1 guard attempted a filesystem mutation')
    sys.addaudithook(audit)
    stopped=[]
    state['guarding']=True
    try:
        for name in ('prepare_w1','reissue'):
            try: runpy.run_path(str(BASE/'nw1b'/(name+'.py')),run_name='__main__')
            except calibrate.QualificationError as e:
                if 'GATE_FAIL' not in str(e): raise
                stopped.append(name)
            else: raise AssertionError(name+' did not stop')
    finally: state['guarding']=False
    result=dict(protected_artifacts_unchanged=len(protected), pngs_matching_unchanged_manifest=len(manifest),
                bound_sources_unchanged=len(ledger['sources']), stopped_entrypoints=stopped,
                entrypoint_write_attempts=len(events),detector_calls=state['detector_calls'],publish_actions=0,
                ledger_sha256=calibrate.sha(calibrate.LEDGER),
                scope='Current local checks only. No live-run writes, locks, reader, reissue, staging or publication. Synthetic tests write only under /tmp. PNG hashes match the original unchanged staged manifest.')
    print(json.dumps(result,indent=2))

if __name__=='__main__': main()
