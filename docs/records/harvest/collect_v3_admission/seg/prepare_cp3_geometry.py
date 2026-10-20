"""Explicit once-per-page existing-detector preparation, outside admission.

Writes only CP3_geometry under this checkout. Never invoked by measurement.
Run with the collector interpreter and -B. No OCR/reading/network.
"""
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
COLLECTOR=Path.home()/'Projects/greek-ocr-toolkit-sol-collect'
RUN=Path.home()/'Projects/collect-v3-data/run'
OUT=Path(__file__).resolve().parent/'CP3_geometry'
sys.path.insert(0,str(COLLECTOR))


def main():
    path=COLLECTOR/'collect_v3/vendor/geometry/io.py'
    spec=importlib.util.spec_from_file_location('_cp3_existing_io',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    def audit(event,args):
        if event.startswith('socket.'):
            raise AssertionError('network OFF')
        if event=='open':
            path,mode,flags=args
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                if not Path(path).resolve().is_relative_to(OUT):
                    raise AssertionError('preparation write outside isolated output: '+str(path))
        if event in ('os.mkdir','os.remove','os.rmdir','os.chmod','os.truncate'):
            if not Path(args[0]).resolve().is_relative_to(OUT):
                raise AssertionError('mutation outside isolated output')
        if event in ('os.rename','os.link','os.symlink'):
            if not all(Path(p).resolve().is_relative_to(OUT) for p in args[:2]):
                raise AssertionError('mutation outside isolated output')
    sys.addaudithook(audit)
    OUT.mkdir(exist_ok=True)
    ledger=json.loads((OUT.parent/'calibration_ledger.json').read_text())
    pages=sorted({r['row_id'].rsplit('-l',1)[0] for r in ledger['cases']})
    detector=module.detector_identity()
    for pid in pages:
        marker=OUT/(pid+'.attempt.json')
        if marker.exists():
            print(json.dumps(dict(page_id=pid,status='already_attempted')),flush=True)
            continue
        metadata=list(RUN.glob('*/pages/'+pid+'.json'))
        if len(metadata)!=1:raise ValueError('missing/ambiguous metadata:'+pid)
        m=json.loads(metadata[0].read_text())
        if m['id']!=pid or m['status']!='completed':raise ValueError('invalid metadata')
        # Persistent exclusive marker prevents a crash/retry from redetecting.
        with marker.open('x') as f:
            json.dump(dict(page_id=pid,source=m['image'],source_sha256=m['image_sha256'],detector_sha256=detector),f)
        try:
            _,_,_,receipt=module.cache_page(Path(m['image']),OUT/pid,m['image_sha256'],detector)
            print(json.dumps(dict(page_id=pid,status='prepared',receipt=receipt)),flush=True)
        except Exception as error:
            print(json.dumps(dict(page_id=pid,status='unavailable',reason=f'{type(error).__name__}: {error}')),flush=True)


if __name__=='__main__':main()
