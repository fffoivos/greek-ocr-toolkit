"""Read-only CP4 native witness check. No detection, reading, or preparation.

Stdout is the only output. A missing cache cannot enter KEEP/detection counts.
"""
import json
import hashlib
import os
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import greekocr.pages
from greekocr.harvest import geometry_observations as g
from greekocr.harvest.neighbour_words import neighbour_word_evidence, WORD_PROXY
from greekocr.harvest.admission import compose_segmentation_decision, TOOL_VERSION

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
                    ('crop_bbox','crop_sha256','crop_source_image','crop_source_sha256','measured_row_id')}
    pages = {}; observations = []
    for case in sorted(ledger['cases'], key=lambda c: c['row_id']):
        rid = case['row_id']; pid = rid.rsplit('-l',1)[0]
        if pid not in pages:
            # Sorted cases consume one page at a time; retain bindings only.
            for previous in pages.values():
                previous.pop('page', None)
            cache = SEG/'CP4_geometry'/pid
            if not (cache/'receipt.json').exists():
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
                pages[pid] = dict(status='unavailable',reason=f'{type(error).__name__}: {error}',
                    attempted_cache=str(cache),cache_files={n:g.sha(cache/n) for n in
                    ('receipt.json','ink.png','labels.npz','detector.json.gz') if (cache/n).exists()})
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
            observed = neighbour_word_evidence(entry['page'],box, target_row_id=crop['measured_row_id'])
            full_sha=hashlib.sha256(json.dumps(observed,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            structural=observed['row_inclusion']
            if structural.get('rows'):
                remote=[r for r in structural['rows'] if not r['assigned_pixels']]
                structural['rows']=[r for r in structural['rows'] if r['assigned_pixels']]
                structural['zero_hit_row_ids']=[r['row_id'] for r in remote]
            observations.append(dict(row_id=rid,truth=case['truth'],
                status=observed['status'],full_observation_sha256=full_sha,observation=observed))
        except (ValueError, KeyError, TypeError) as error:
            observations.append(dict(row_id=rid,truth=case['truth'],status='unavailable',reason=str(error)))
    for row in observations:
        row['composed_decision'] = compose_segmentation_decision(
            row.get('observation', dict(status=row['status'], reason=row.get('reason'))))
    by_id = {r['row_id']:r for r in observations}
    keeps = {r['row_id'] for r in ledger['cases'] if r['truth']=='keep'}
    c1 = {r['row_id'] for r in ledger['c1_witnesses']}
    gallery = {r['row_id'] for r in ledger['gallery_witnesses'] if r['type']=='merged_multi_line'}
    drops = {r['row_id'] for r in ledger['cases'] if r['truth']=='drop'}
    def count(ids, expected, screen='union_drop'):
        measured = [i for i in sorted(ids) if not by_id[i]['composed_decision']['geometry_unavailable']
                    and by_id[i].get('observation',{}).get(screen) is not None]
        return dict(required=len(ids),measured=len(measured),
            met=sum(by_id[i]['observation'][screen]==expected for i in measured),
            unresolved=sorted(ids-set(measured)),
            failed=[i for i in measured if by_id[i]['observation'][screen]!=expected])
    def composed_count(ids, expected):
        resolved = [i for i in sorted(ids) if by_id[i]['composed_decision']['drop'] is not None]
        unavailable = [i for i in sorted(ids) if by_id[i]['composed_decision']['geometry_unavailable']]
        return dict(required=len(ids), met=sum(by_id[i]['composed_decision']['drop'] == expected for i in resolved),
                    geometry_unavailable=len(unavailable), unavailable_ids=unavailable,
                    unresolved=sorted(ids-set(resolved)),
                    failed=[i for i in resolved if by_id[i]['composed_decision']['drop'] != expected])
    def interval(n,d):
        if not d: return None
        z=1.959963984540054; p=n/d; den=1+z*z/d
        centre=(p+z*z/(2*d))/den
        radius=z*((p*(1-p)/d+z*z/(4*d*d))**.5)/den
        return [max(0,centre-radius),min(1,centre+radius)]
    def matrix(screen):
        out=dict(tp=0,fp=0,fn=0,tn=0,unknown=0)
        for rid in keeps|drops:
            value=(None if by_id[rid]['composed_decision']['geometry_unavailable'] else
                   by_id[rid].get('observation',{}).get(screen))
            if value is None: out['unknown']+=1; continue
            out['tp' if rid in drops and value else 'fn' if rid in drops else 'fp' if value else 'tn']+=1
        metrics={}
        for name,n,d in [('precision',out['tp'],out['tp']+out['fp']),
                         ('recall',out['tp'],out['tp']+out['fn']),
                         ('keep_false_drop_rate',out['fp'],out['fp']+out['tn']),
                         ('survivor_defect_rate',out['fn'],out['fn']+out['tn'])]:
            metrics[name]=dict(numerator=n,denominator=d,value=n/d if d else None,wilson95=interval(n,d))
        return dict(confusion=out,metrics=metrics)
    protected = json.loads((SEG/'protected_before.json').read_text())
    for path, before in protected.items():
        if g.sha(ROOT/path) != before['sha256']:
            raise AssertionError('protected artifact changed: '+path)
    base = SEG.parent
    manifest = [json.loads(l) for l in (base/'crops_manifest.jsonl').read_text().splitlines()]
    for row in manifest:
        if g.sha(base/row['path']) != row['sha256']:
            raise AssertionError('crop changed: '+row['row_id'])
    from greekocr.harvest.neighbour_words import row_word_evidence
    from greekocr.harvest.row_inclusion import supported_rows
    fixture=json.loads((SEG/'CP4_one_letter_words.json').read_text())
    assert g.sha(fixture['response'])==fixture['response_sha256']
    native=g.load_cached_page(fixture['source'],fixture['cache'],fixture['source_sha256'])
    response=json.loads(Path(fixture['response']).read_text())['document']
    word_results=[]
    for word in fixture['words']:
        token=response['pages'][0]['tokens'][word['token_index']]
        text=''.join(response['text'][int(a.get('startIndex',0)):int(a['endIndex'])]
            for a in token['layout']['textAnchor']['textSegments']).strip()
        assert text==word['text']
        vertices=token['layout']['boundingPoly']['vertices']
        recorded=[min(v['x'] for v in vertices),min(v['y'] for v in vertices),
                  max(v['x'] for v in vertices),max(v['y'] for v in vertices)]
        assert recorded==word['recorded_box']
        assert word['crop_box']==[recorded[0]-3,recorded[1]-3,recorded[2]+3,recorded[3]+3]
        row=next(r for r in native['rows'] if r['row_id']==word['geometry_row_id'])
        support=supported_rows(native,word['crop_box'])
        rs=next(r for r in support['rows'] if r['row_id']==row['row_id'])
        record={**{k:fixture[k] for k in ('source','source_sha256','response','response_sha256')},**word}
        evidence=row_word_evidence(native,row,word['crop_box'],rs,recorded_word=record)
        assert evidence==word['evidence']
        word_results.append(dict(token_index=word['token_index'],text=text,
            positive=any(g['positive'] for g in evidence['groups']),
            unresolved=any(g['unresolved'] for g in evidence['groups'])))
    controls=json.loads((SEG/'CP4_controls.json').read_text())
    assert controls['binding']==g.implementation_binding()
    assert controls['tests_sha256']==g.sha(ROOT/'tests/test_seg_cp4.py')
    assert controls['verifier_sha256']==g.sha(SEG/'verify_cp4_controls.py')
    result = dict(schema='SEG-CP4c-native-verification-v1',admission_version=TOOL_VERSION,gate=False,
        ledger_sha256=g.sha(SEG/'calibration_ledger.json'),binding=g.implementation_binding(),
        verifier_sha256=g.sha(__file__),word_fixture_sha256=g.sha(SEG/'CP4_one_letter_words.json'),
        keeps=count(keeps,False),drops=count(drops,True),c1=count(c1,True),gallery=count(gallery,True),
        composed_drops=composed_count(drops,True),composed_keeps=composed_count(keeps,False),
        geometry_unavailable=composed_count(keeps|drops,True)['unavailable_ids'],
        required_unresolved_non_unavailable=composed_count(keeps|drops|c1|gallery,True)['unresolved'],
        screens={k:matrix(k) for k in ('neighbour_drop','merged','union_drop')},
        proxy_parameters=WORD_PROXY,
        controls_sha256=g.sha(SEG/'CP4_controls.json'),
        controls={k:controls[k] for k in ('cp3_planted','original_fragments','fragments','mechanics')},
        recorded_one_letter_words=dict(required=len(word_results),
            caught=sum(w['positive'] for w in word_results),
            unresolved=sum(w['unresolved'] for w in word_results),cases=word_results),
        borderline=[by_id[r['row_id']] for r in ledger['cases'] if r['truth']=='borderline'],
        required_unresolved=count(keeps|drops,True)['unresolved'],
        witness_overlap_ids=sorted(c1 & gallery),unique_merge_witnesses=len(c1 | gallery),
        page_coverage=[dict(page_id=k,**{a:b for a,b in v.items() if a!='page'}) for k,v in sorted(pages.items())],
        cases=observations,detector_or_network_calls=len(calls),runtime_write_attempts=len(writes),
        fallback_preparations=len(list((SEG/'CP4_geometry').glob('*.attempt.json'))),
        fallback_receipts=len(list((SEG/'CP4_geometry').glob('*/receipt.json'))),
        fallback_measurement_detector_calls=0,
        inherited_preparations=len(list((SEG/'CP3_geometry').glob('*.attempt.json'))),
        preparation_successes=sum(1 for _ in (SEG/'CP3_geometry').glob('*/receipt.json')),
        original_features_sha256=features_sha,publish_actions=0,protected_artifacts_unchanged=len(protected),
        pngs_matching_manifest=len(manifest))
    assert g.sha(features) == features_sha
    # Qualification requires all three native denominators, never zero FP
    # among an empty measured population. Synthetic tests cannot fill this gap.
    result['gate'] = (all(result[k]['met']==result[k]['required'] for k in ('keeps','composed_keeps','composed_drops','c1','gallery'))
        and all(w['positive'] for w in word_results))
    acceptance=dict(
        keep_false_drops=result['keeps']['met']==22 and not result['keeps']['unresolved'],
        required_drops=result['composed_drops']['met']==9 and not result['composed_drops']['unresolved'],
        fragment_drops=controls['fragments']['union_drops']==0,
        short_words=(controls['mechanics']['union_drops']==controls['mechanics']['required']
                     and all(w['positive'] for w in word_results)),
        required_resolution=not result['required_unresolved_non_unavailable'])
    result['acceptance']=dict(met=sum(acceptance.values()),required=5,requirements=acceptance)
    result['gate']=result['gate'] and all(acceptance.values())
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
