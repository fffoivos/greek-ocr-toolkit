"""Measure-only CP5p feasibility replay. No detector, reader, or integration.

CP4 H2 letter boxes retain full parent ink partitioned by toolkit split cuts.
Native components omitted by letter_boxes (including punctuation) are retained
separately, using the same CP3 rule exclusions. No ownership is changed.
"""
import gzip
import hashlib
import json
import os
from pathlib import Path
import socket
import sys
import numpy as np
from scipy import ndimage as ndi
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from greekocr.harvest.geometry_observations import load_cached_page
SEG = Path(__file__).resolve().parent
CLIPS = {
    'nlg--6ae0ac01064a587e--s007-l0013',
    'gazette_modern--feb39c43ac177ef8--s000-l0665',
    'gazette_modern--73f0e4003296ba2e--s000-l0097',
    'bsb_poly1850--9342f9a56a4065cd--s004-l0005',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def measure(case, observation, box, binding):
    if observation['status'] == 'unavailable':
        return dict(row_id=case, status='unavailable', max_px=None, max_xh=None)
    page = load_cached_page(binding['source'], binding['cache_directory'], binding['source_sha256'])
    target = observation['target_row_id']
    row = next(r for r in page['rows'] if r['row_id'] == target)
    support = next(r for r in observation['row_inclusion']['rows'] if r['row_id'] == target)
    extents = []; represented = set()
    for group in support['local_groups']:
        for letter in group['letters']:
            represented.update(letter['native_component_ids'])
            extents.append(dict(box=letter['box'], kind='H2_letter',
                parent_ids=letter['native_component_ids'], resolved=letter['resolved'],
                shared_parent_split=letter['shared_parent_split']))
    objects = ndi.find_objects(page['labels'])
    for cid in sorted(set(row['component_ids']) - represented - set(support['excluded_component_ids'])):
        sy, sx = objects[cid-1]
        extents.append(dict(box=[sx.start, sy.start, sx.stop, sy.stop],
                            kind='native_component', parent_ids=[int(cid)], resolved=True))
    hits = []
    for extent in extents:
        x, y, z, bottom = extent['box']
        if y < box[3] and bottom > box[1] and x < box[2] and z > box[0]:
            overflow = max(box[0]-x, z-box[2], 0)
            if overflow:
                hits.append(dict(extent, overflow_px=overflow, overflow_xh=overflow/row['xheight']))
    return dict(row_id=case, status='measured', target_row_id=target, crop_box=box,
        xheight=float(row['xheight']), assigned_row_x_extent=[row['x0'],row['x1']],
        native_components=len(row['component_ids']), examined_extents=extents, hits=hits,
        max_px=max((h['overflow_px'] for h in hits), default=0),
        max_xh=max((h['overflow_xh'] for h in hits), default=0))


def curve(rows, keeps, unit):
    key = 'max_'+unit
    cuts = sorted({0., *(r[key] for r in rows+keeps if r['status']=='measured')})
    out = []
    for i, cut in enumerate(cuts):
        dropped = [r['row_id'] for r in rows if r['status']=='measured' and r[key]>cut]
        owner = [r['row_id'] for r in keeps if r[key]>cut]
        out.append(dict(lower_inclusive=cut, upper_exclusive=cuts[i+1] if i+1<len(cuts) else None,
            clips=len(set(dropped)&CLIPS), nonclip_false_drops=len(set(dropped)-CLIPS),
            owner_keep_false_drops=len(owner), dropped_ids=dropped, owner_drop_ids=owner,
            passes=len(set(dropped)&CLIPS)==4 and not set(dropped)-CLIPS and not owner))
    return out


def main():
    def forbidden(*args, **kwargs):
        raise AssertionError('network/detector forbidden')
    socket.socket.connect = socket.socket.connect_ex = forbidden
    import greekocr.pages
    greekocr.pages.process_page = forbidden
    def audit(event,args):
        if event.startswith('socket.'): raise AssertionError('network forbidden')
        if event == 'open':
            path, mode, flags = args
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                raise AssertionError('read-only replay: write forbidden')
        if event in ('os.mkdir','os.rename','os.remove','os.rmdir','os.link','os.symlink','os.chmod','os.truncate'):
            raise AssertionError('mutation forbidden')
    sys.addaudithook(audit)
    rows = []
    for c in map(json.loads,gzip.open(SEG/'cp7/keys/sealed_decisions.jsonl.gz','rt')):
        rows.append(measure(c['row_id'], c['structural'], c['crop_bbox'], c['geometry_binding']))
    keeps = []
    old = json.loads((SEG/'CP4_verification.json').read_text())
    for c in old['cases']:
        if c['truth'] != 'keep': continue
        o = c['observation']; binding = next(p['binding'] for p in old['page_coverage']
            if p['page_id']==c['row_id'].rsplit('-l',1)[0])
        keeps.append(measure(c['row_id'],o,o['row_inclusion']['crop_box'],binding))
    paths = [SEG/n for n in ('calibration_ledger.json','CP1_RECEIPT.md','CP3_verification.json',
        'CP4_verification.json','CP5_verification.json','CP7_FREEZE.json',
        'cp7/keys/sealed_decisions.jsonl.gz','cp7/keys/draw.jsonl')]
    paths += [ROOT/'greekocr/harvest'/n for n in ('admission.py','neighbour_words.py','row_inclusion.py','orientation_screen.py')]
    paths += [ROOT/'docs/harvest/recut_v1/w1_masked/caps3/screen_receipt.json']
    print(json.dumps(dict(schema='SEG-CP5p-feasibility-v1', status='STOP: no passing interval',
        input_sha256={str(p.relative_to(ROOT)):sha(p) for p in paths}, rows=rows, owner_keeps=keeps,
        curve_xh=curve(rows,keeps,'xh'), curve_px=curve(rows,keeps,'px'),
        geometry_unavailable=[r['row_id'] for r in rows if r['status']=='unavailable'],
        selected_tolerance=None, passing_interval=None, detector_calls=0, network_calls=0,
        runtime_write_attempts=0, publish_actions=0),indent=2))

if __name__=='__main__': main()
