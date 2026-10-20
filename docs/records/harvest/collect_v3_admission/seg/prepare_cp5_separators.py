"""Explicit once-per-source separator preparation, outside the live run root."""
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from greekocr.harvest import geometry_observations as g, separator_inventory as s
from prepare_cp4_geometry import claim_attempt
SEG=Path(__file__).resolve().parent
OUT=SEG/'CP5_separators'


def main():
    def audit(event,args):
        if event.startswith('socket.') or event=='subprocess.Popen':
            raise AssertionError('network/subprocess forbidden')
        if event=='open':
            path,mode,flags=args
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                if not Path(path).resolve().is_relative_to(OUT):
                    raise AssertionError('write outside isolated separator cache')
        if event in ('os.mkdir','os.remove','os.rmdir','os.chmod','os.truncate'):
            if not Path(args[0]).resolve().is_relative_to(OUT):raise AssertionError('mutation outside cache')
        if event in ('os.rename','os.link','os.symlink'):
            if not all(Path(p).resolve().is_relative_to(OUT) for p in args[:2]):raise AssertionError('mutation outside cache')
    sys.addaudithook(audit)
    OUT.mkdir(exist_ok=True)
    cp4=json.loads((SEG/'CP5_cp4_verification.json').read_text())
    for entry in cp4['page_coverage']:
        b=entry.get('binding')
        if not b:
            print(json.dumps(dict(page_id=entry.get('page_id'),status='geometry_unavailable')),flush=True);continue
        page=g.load_cached_page(b['source'],b['cache_directory'],b['source_sha256'])
        pid=Path(b['cache_directory']).name
        metadata=dict(id=pid,image=b['source'],image_sha256=b['source_sha256'])
        if not claim_attempt(OUT,metadata,b['runtime_geometry_sha256'],s.binding(page)):
            print(json.dumps(dict(page_id=pid,status='already_attempted')),flush=True);continue
        try:
            data=s.prepare(page)
            directory=OUT/pid;directory.mkdir()
            (directory/'inventory.json').write_text(json.dumps(data,sort_keys=True,ensure_ascii=False))
            receipt=dict(binding=s.binding(page),inventory_sha256=g.sha(directory/'inventory.json'),
                         preparation_calls=1,row_detector_calls=0)
            (directory/'receipt.json').write_text(json.dumps(receipt,sort_keys=True))
            print(json.dumps(dict(page_id=pid,status='prepared',boundaries=len(data['boundaries']),receipt=receipt)),flush=True)
        except Exception as error:
            print(json.dumps(dict(page_id=pid,status='unavailable',reason=f'{type(error).__name__}: {error}')),flush=True)

if __name__=='__main__':main()
