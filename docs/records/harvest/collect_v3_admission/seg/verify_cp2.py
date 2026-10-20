"""Offline CP2 read-only native probe; stdout only, no detector preparation.

Run with -B using the collector interpreter. Outputs are numerical evidence,
not readings, whole-word truth, or later-checkpoint qualification.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
import numpy as np
from PIL import Image
import greekocr.pages
from greekocr.glyphs import foreign_ink
from greekocr.harvest import geometry_observations as g
from greekocr.harvest.neighbour_words import measure_rows
from greekocr.harvest.admission import evaluate

RUN=Path.home()/'Projects/collect-v3-data/run'


def main():
    detector_calls=[];writes=[]
    def no_detector(*args,**kwargs):
        detector_calls.append(True)
        raise AssertionError('detector forbidden')
    def no_network(*args,**kwargs):
        raise AssertionError('network forbidden')
    greekocr.pages.process_page=no_detector
    socket.socket.connect=no_network
    socket.socket.connect_ex=no_network
    def audit(event,args):
        if event=='open':
            path,mode,flags=args
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                writes.append(str(path));raise AssertionError('write forbidden:'+str(path))
        if event in ('os.mkdir','os.rename','os.remove','os.rmdir','os.link','os.symlink','os.chmod','os.truncate'):
            writes.append(str(args));raise AssertionError('mutation forbidden:'+event)
    sys.addaudithook(audit)
    ledger=ROOT/'docs/harvest/collect_v3_admission/seg/calibration_ledger.json'
    truth=json.loads(ledger.read_text())
    witnesses={c['row_id'] for c in truth['cases']} | {c['row_id'] for c in truth['c1_witnesses']}
    pages=sorted({i.rsplit('-l',1)[0] for i in witnesses})
    coverage=[];mask_checks=[];snapshots={};native=None
    for pid in pages:
        cache=RUN/'cache/g1b'/pid
        metadata=RUN/'W1/pages'/f'{pid}.json'
        if not metadata.exists() or not (cache/'receipt.json').exists():
            coverage.append(dict(page_id=pid,status='unavailable',reason='missing_W1_cache_or_metadata'));continue
        try:
            m=json.loads(metadata.read_text())
            page=g.load_cached_page(m['image'],cache,m['image_sha256'])
            coverage.append(dict(page_id=pid,status='loaded',rows=len(page['rows']),binding=page['binding']))
            if len(page['rows'])>1 and native is None:native=page;native_pid=pid;native_status=m['status']
        except (OSError,KeyError,ValueError) as error:
            coverage.append(dict(page_id=pid,status='unavailable',reason=str(error)))
    # Existing calibration caches may have been pruned. A separate W1 cache
    # demonstrates the contract without pretending to recover missing witnesses.
    if native is None:
        # Use the review's stable retained W1 control. Do not select from
        # unrelated live caches that another process may be pruning.
        native_pid='ia_poly1850--3773a91327e98bc0--s000'
        meta=RUN/'W1/pages'/f'{native_pid}.json'
        cache=RUN/'cache/g1b'/native_pid
        m=json.loads(meta.read_text())
        rec=json.loads((cache/'receipt.json').read_text())
        native=g.load_cached_page(rec['source'],cache,rec['source_sha256'])
        native_status=m['status']
    if native is None:raise AssertionError('no complete valid W1 native cache')
    source=native['source']
    paths=[source,Path(native['binding']['cache_receipt']['source'])]
    pid=native_pid
    paths += list((RUN/'cache/g1b'/pid).iterdir())
    snapshots={str(p):g.sha(p) for p in paths if p.is_file()}
    with Image.open(source) as image:prepared=foreign_ink.prepare_mask_page(image)
    pixels=prepared.pixels.copy();labels=prepared.labels.copy()
    for row in native['rows'][:10]:
        others=[r for r in native['rows'] if r['row_id']!=row['row_id']]
        if not others:continue
        x0,y0,x1,y1=row['owned_box'];h,w=native['ink'].shape
        box=[max(0,x0),max(0,y0-30),min(w,x1),min(h,y1+30)]
        expected=foreign_ink._foreign_mask(prepared.ink,foreign_ink._centre_fit(row),
                  [foreign_ink._centre_fit(r) for r in others],tuple(box))
        observed=g.measure_foreign(prepared,row,others,box)
        assert np.array_equal(expected,observed['mask'])
        mask_checks.append(dict(row_id=row['row_id'],box=box,pixels=int(expected.sum()),
                                identical=True,sha256=hashlib.sha256(expected.tobytes()).hexdigest()))
    assert np.array_equal(pixels,prepared.pixels) and np.array_equal(labels,prepared.labels)
    assert snapshots=={p:g.sha(p) for p in snapshots}
    unavailable=[None,dict(matched=False),dict(matched=True,decision_status='unqualified_cp2',components=[]),
        dict(matched=True,xheight=10.,components=[]),
        dict(matched=True,xheight=10.,components=[],status='stale',binding={'source_sha256':'wrong'}),
        dict(matched=True,xheight=10.,components=[],decision_status='unresolved'),
        dict(matched=True,xheight=10.,components=[],status='measured',decision_status='qualified',binding={})]
    verified_keeps=sum(evaluate(dict(label='ἑλληνικὸς πλήρης λόγος',source='bsb_poly1850',primary_class='poly1850'),
                                neighbour_measurement=m)['passed'] for m in unavailable)
    assert not verified_keeps and not writes and not detector_calls
    print(json.dumps(dict(schema='SEG-CP2-native-verification-v1',ledger_sha256=g.sha(ledger),
         detector_calls=len(detector_calls),runtime_write_attempts=len(writes),fallback_preparations=0,
         unavailable_verified_keeps=verified_keeps,unavailable_checks=len(unavailable),
         mask_comparisons=len(mask_checks),identical_masks=sum(m['identical'] for m in mask_checks),
         native_page_id=native_pid,native_page_status=native_status,native_binding=native['binding'],unchanged_input_sha256=snapshots,
         calibration_page_coverage=coverage,masks=mask_checks),indent=2))


if __name__=='__main__':main()
