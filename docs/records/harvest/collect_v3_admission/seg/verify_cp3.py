"""Read-only CP3 native witness check. No detection, reading, or preparation.

Stdout is the only output. A missing cache cannot enter KEEP/detection counts.
"""
import json
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import greekocr.pages
from greekocr.harvest import geometry_observations as g
from greekocr.harvest.row_inclusion import screen_merged

RUN = Path.home()/'Projects/collect-v3-data/run'
SEG = ROOT/'docs/harvest/collect_v3_admission/seg'


def main():
    calls = []; writes = []
    def forbidden(*args, **kwargs):
        calls.append(True)
        raise AssertionError('detector/network forbidden')
    greekocr.pages.process_page = forbidden
    socket.socket.connect = socket.socket.connect_ex = forbidden
    def audit(event,args):
        if event == 'open':
            _, mode, flags = args
            if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND):
                writes.append(str(args[0])); raise AssertionError('write forbidden')
        if event in ('os.mkdir','os.rename','os.remove','os.rmdir','os.link','os.symlink','os.chmod','os.truncate'):
            writes.append(str(args)); raise AssertionError('mutation forbidden')
        if event.startswith('socket.'):
            raise AssertionError('network forbidden')
    sys.addaudithook(audit)
    ledger = json.loads((SEG/'calibration_ledger.json').read_text())
    # Original, PRE-screen feature population includes the C1 c068 challenge
    # absent from the old neighbour measurement cache. Retain only geometry.
    features = RUN/'W1/features.jsonl'
    features_sha = g.sha(features)
    required = {c['row_id'] for c in ledger['cases']}
    crops = {}
    with features.open() as stream:
        for raw in stream:
            record = json.loads(raw)
            if record['id'] in required:
                if record['id'] in crops:
                    raise ValueError('duplicate_original_crop')
                crops[record['id']] = {k: record[k] for k in
                    ('crop_bbox','crop_sha256','crop_source_image','crop_source_sha256')}
    pages = {}; observations = []
    for case in sorted(ledger['cases'], key=lambda c: c['row_id']):
        rid = case['row_id']; pid = rid.rsplit('-l',1)[0]
        if pid not in pages:
            # Sorted cases consume one page at a time; retain bindings only.
            for previous in pages.values():
                previous.pop('page', None)
            cache = RUN/'cache/g1b'/pid
            if not (cache/'receipt.json').exists():
                cache = SEG/'CP3_geometry'/pid
            metadata = list(RUN.glob('*/pages/'+pid+'.json'))
            try:
                if len(metadata) != 1:
                    raise ValueError('missing_or_ambiguous_page_metadata')
                m = json.loads(metadata[0].read_text())
                if m['id'] != pid or m['status'] != 'completed':
                    raise ValueError('incomplete_page_metadata')
                page = g.load_cached_page(m['image'],cache,m['image_sha256'])
                pages[pid] = dict(status='loaded',binding=page['binding'],page=page,
                    invalid_geometry_count=page['invalid_geometry_count'],
                    invalid_rows=page['invalid_rows'])
            except (OSError, ValueError, KeyError) as error:
                pages[pid] = dict(status='unavailable',reason=f'{type(error).__name__}: {error}')
        entry = pages[pid]
        try:
            if entry['status'] != 'loaded':
                raise ValueError(entry['reason'])
            crop = crops[rid]
            box = crop['crop_bbox']
            if case['measurement'] and list(box) != case['measurement']['crop_box']:
                raise ValueError('original_crop_geometry_mismatch')
            if case.get('crop_sha256') and crop['crop_sha256'] != case['crop_sha256']:
                raise ValueError('original_crop_hash_mismatch')
            binding = entry['page']['binding']
            if (crop['crop_source_sha256'] != binding['source_sha256'] or
                    Path(crop['crop_source_image']).resolve() != Path(binding['source'])):
                raise ValueError('original_crop_source_mismatch')
            observed = screen_merged(entry['page'],box,
                legacy_features={'screen_merged':case.get('screen_merged')})
            observations.append(dict(row_id=rid,truth=case['truth'],
                status=observed['status'],observation=observed))
        except (ValueError, KeyError, TypeError) as error:
            observations.append(dict(row_id=rid,truth=case['truth'],status='unavailable',reason=str(error)))
    by_id = {r['row_id']:r for r in observations}
    keeps = {r['row_id'] for r in ledger['cases'] if r['truth']=='keep'}
    c1 = {r['row_id'] for r in ledger['c1_witnesses']}
    gallery = {r['row_id'] for r in ledger['gallery_witnesses'] if r['type']=='merged_multi_line'}
    def count(ids, expected):
        measured = [i for i in sorted(ids) if by_id[i]['status']=='measured']
        return dict(required=len(ids),measured=len(measured),
            met=sum(by_id[i]['observation']['merged']==expected for i in measured),
            unresolved=sorted(ids-set(measured)),
            failed=[i for i in measured if by_id[i]['observation']['merged']!=expected])
    protected = json.loads((SEG/'protected_before.json').read_text())
    for path, before in protected.items():
        if g.sha(ROOT/path) != before['sha256']:
            raise AssertionError('protected artifact changed: '+path)
    base = SEG.parent
    manifest = [json.loads(l) for l in (base/'crops_manifest.jsonl').read_text().splitlines()]
    for row in manifest:
        if g.sha(base/row['path']) != row['sha256']:
            raise AssertionError('crop changed: '+row['row_id'])
    result = dict(schema='SEG-CP3-native-verification-v1',gate=False,
        ledger_sha256=g.sha(SEG/'calibration_ledger.json'),binding=g.implementation_binding(),
        keeps=count(keeps,False),c1=count(c1,True),gallery=count(gallery,True),
        witness_overlap_ids=sorted(c1 & gallery),unique_merge_witnesses=len(c1 | gallery),
        page_coverage=[dict(page_id=k,**{a:b for a,b in v.items() if a!='page'}) for k,v in sorted(pages.items())],
        cases=observations,detector_or_network_calls=len(calls),runtime_write_attempts=len(writes),
        fallback_preparations=len(list((SEG/'CP3_geometry').glob('*.attempt.json'))),
        preparation_successes=sum(1 for _ in (SEG/'CP3_geometry').glob('*/receipt.json')),
        original_features_sha256=features_sha,publish_actions=0,protected_artifacts_unchanged=len(protected),
        pngs_matching_manifest=len(manifest))
    assert g.sha(features) == features_sha
    # Qualification requires all three native denominators, never zero FP
    # among an empty measured population. Synthetic tests cannot fill this gap.
    result['gate'] = all(result[k]['met']==result[k]['required'] for k in ('keeps','c1','gallery'))
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
