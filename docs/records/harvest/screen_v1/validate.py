"""Offline evidence checks for the final T4b handoff; writes only its receipt."""
from collections import Counter, defaultdict
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import statistics
import sys
import time
import numpy as np
from PIL import Image
from assembly_fix import assemble_line, page_tokens, normalise
from screen import OUT, ROOT, TRACKS, rows, sha, write_json, positive, reject, confusion, pixel_features


def main():
    started = time.time()
    checks = {}
    features = rows(OUT/'features.jsonl')
    cards = rows(OUT/'card_eval.jsonl')
    byid = {r['id']: r for r in features}
    stats = json.loads((OUT/'receipts/statistics.json').read_text())
    model = json.loads((OUT/'receipts/model.json').read_text())
    protocol = json.loads((OUT/'receipts/screen_protocol.json').read_text())
    assert protocol['g1b_measurements_in_screen'] is False
    assert protocol['assembly_sha256']==sha(OUT/'assembly_fix.py')
    assert protocol['screen_code_sha256']==sha(OUT/'screen.py')
    allowed={'height_ratio','token_y_spread_xh','internal_gap_xh','density_ratio','google_paragraph_contributors','projection_peaks','crop_height_xh'}
    assert all(set(b)<=allowed for b in model['branches'])
    assert all(r['xheight_method'] in {'crop_component_median_body_height_proxy','google_token_height_half_fallback'} for r in features)
    assert len(features) == len(byid) == 52658
    assert len(cards) == 640
    counts = Counter((c['track'],c['source'],c['split']) for c in cards)
    assert len(counts)==32 and set(counts.values())=={20}
    checks['coverage'] = dict(lines=len(features), cards=len(cards), source_split_counts=dict((('/'.join(k)),v) for k,v in counts.items()))
    inputs = json.loads((OUT/'receipts/inputs.json').read_text())
    unique_inputs = {r['path']:r['sha256'] for r in inputs['input_files']}
    for path, expected in unique_inputs.items():
        assert sha(Path(path)) == expected, ('input changed',path)
    checks['all_bound_inputs_unchanged'] = len(unique_inputs)
    provenance = json.loads((OUT/'receipts/code_provenance.json').read_text())
    for f in provenance['shipped_files']:
        assert sha(Path(f['path']))==f['sha256'], ('shipped source changed',f['path'])
    checks['shipped_code_bindings_unchanged'] = len(provenance['shipped_files'])
    for track, base in TRACKS.items():
        original = rows(base/'lines.jsonl')
        rr = [r for r in features if r['track']==track]
        assert {r['id'] for r in original} == {r['id'] for r in rr}
        for old in original:
            new = byid[old['id']]
            assert new['original_usable'] == old['usable_candidate']
            assert new['source']==old['source'] and new['page_id']==old['page_id']
            assert new['crop_bbox']==old['crop_bbox']
            assert new['crop_sha256']==old['crop_sha256']
        bypage=defaultdict(list)
        for r in rr:
            bypage[r['page_id']].append(r)
        for ident, group in bypage.items():
            bulk=rows(base/'bulk/lines'/(ident+'.jsonl'))
            heights=[b['bbox'][3]-b['bbox'][1] for b in bulk if sum(c.isalpha() for c in b['docai_raw_text'])>=3]
            median=statistics.median(heights or [b['bbox'][3]-b['bbox'][1] for b in bulk])
            assert all(r['page_median_row_height']==median for r in group)
    checks['one_row_per_original_line_and_crop_binding'] = True
    # Reconstruct every blind card at exactly its original native crop rectangle.
    cardfiles = {}
    for track, base in TRACKS.items():
        for f in (base/'label_cards').rglob('cards.jsonl'):
            for c in rows(f):
                ident = c.get('card_id',c.get('card'))
                cardfiles[(track,f.parent.name,ident)] = (f,c)
    crop_checks = []
    cardtraces={r['id']:r for r in rows(OUT/'receipts/card_traces.jsonl')}
    for c in cards:
        f, record = cardfiles[(c['track'],c['source'],c['card_id'])]
        r = byid[c['id']]
        cardpath = f.parent/record['crop']
        assert normalise(record.get('google_text',record.get('text'))) == r['old_label']
        with Image.open(cardpath) as crop, Image.open(r['crop_page_path']) as page:
            expected = np.asarray(crop.convert('RGB'))
            actual = np.asarray(page.crop(r['crop_bbox']).convert('RGB'))
            kept=[t for t in cardtraces[c['id']]['tokens'] if t['token_id'] not in r['dropped_token_ids']]
            heights=[t['bbox'][3]-t['bbox'][1] for t in kept if t['bbox'] and any(ch.isalpha() for ch in t['text'])]
            fallback=statistics.median(heights)*.5 if heights else r['page_median_row_height']*.5
            pix=pixel_features(crop,fallback)
            for field,value in pix.items():
                assert r[field]==value, ('crop-only feature replay mismatch',c['id'],field)
        assert expected.shape==actual.shape and np.array_equal(expected,actual), ('crop pixel mismatch', c['id'])
        assert sha(cardpath)==r['crop_sha256'], ('crop hash mismatch',c['id'])
        crop_checks.append(dict(track=c['track'],source=c['source'],card_id=c['card_id'],id=c['id'],
              crop_path=str(cardpath),crop_sha256=sha(cardpath),native_pixels_equal=True))
    from screen import write_rows
    write_rows(OUT/'receipts/crop_pixel_checks.jsonl',crop_checks)
    checks['card_pixel_and_original_png_hash_identity'] = len(crop_checks)
    checks['strict_crop_google_feature_contract_and_640_pixel_feature_replays'] = True
    # Replay changed lines and every blind card directly from original responses.
    traces = {r['id']:r for r in rows(OUT/'receipts/assembly_changes.jsonl')}
    traces.update({r['id']:r for r in rows(OUT/'receipts/card_traces.jsonl')})
    grouped = defaultdict(list)
    pages = {p['id']:p for base in TRACKS.values() for p in rows(base/'pages.jsonl')}
    for trace in traces.values():
        grouped[trace['raw_path']].append(trace)
    replayed = 0
    for rawpath, tt in grouped.items():
        doc = json.loads(Path(rawpath).read_text())['document']
        p = pages[tt[0]['page_id']]
        tokens, _, _ = page_tokens(doc,(p['width'],p['height']))
        for trace in tt:
            r = byid[trace['id']]
            result = assemble_line(doc,trace['line_index'],tokens)
            assert result['old_label']==r['old_label']
            assert result['fixed_label']==r['fixed_label'], ('assembly mismatch',r['id'])
            assert result['changed']==r['assembly_changed']
            assert result['drops']==trace['drops']
            assert json.loads(json.dumps(result['tokens']))==trace['tokens'], ('token trace differs',r['id'])
            replayed += 1
    assert byid['openarchives--hf-1ac7969a077332d2-48a986cf--000019-l0212']['fixed_label']=='τῶφλι τῆς μυστικῆς ἀνεμόσκαλας τοῦ Ἰακώβ.'
    assert byid['elstat--GRESYE_01_0001_00164-fbc4a190--000021-l0015']['fixed_label']=='1/1-30/6 Ἔτος – Year'
    controls = {('ia','poly1850','c032'),('intl','bsb','c020'),('gr','pleias','c021')}
    assert all(not c['assembly_changed'] for c in cards if (c['track'],c['source'],c['card_id']) in controls)
    checks['response_token_native_box_and_assembly_replays'] = replayed
    checks['positive_and_stacked_numeric_negative_witnesses'] = True
    # Reproduce calibration on the archived final crop/Google feature snapshot.
    archive = OUT/'receipts/calibration_base_features.jsonl.gz'
    h=hashlib.sha256()
    with gzip.open(archive,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):
            h.update(b)
    assert h.hexdigest()==model['inputs']['features_sha256']
    assert sha(OUT/'receipts/calibration_split.jsonl')==model['inputs']['split_sha256']
    assert rows(OUT/'receipts/calibration_split.jsonl')==rows(OUT/'receipts/split.jsonl')
    old = {r['id']:r for r in rows(archive)}
    cal = [c for c in cards if c['split']=='calibration']
    test = [c for c in cards if c['split']=='test']
    assert confusion([positive(c) for c in cal],[reject(old[c['id']],model) for c in cal])==model['calibration']
    assert all(reject(old[c['id']],model)==reject(byid[c['id']],model) for c in cards)
    cm=confusion([positive(c) for c in test],[reject(byid[c['id']],model) for c in test])
    assert all(stats['test_primary'][k]==v for k,v in cm.items())
    checks['frozen_screen_and_independent_confusion_counts'] = dict(calibration_cards=len(cal),test_cards=len(test),test=cm,final_feature_snapshot_card_prediction_parity=len(cards))
    for r in features:
        assert r['screen_reject']==reject(r,model)
        assert r['usable_after_screen']==(r['fixed_usable'] and not r['screen_reject'])
        assert r['usable_final']==(r['usable_after_screen'] and not r['text_exclusions'])
        assert r['training_usable_final']==(r['usable_final'] and r['source']!='wikisource_ru')
        for fix in r['roman_fixes']:
            assert re.fullmatch('[IVXLCMD]+',fix['new'])
        if 'dropped_line_end_hyphen' in r['text_exclusions']:
            nxt = byid[r['next_column_line_id']]
            assert (r['track'],r['page_id'])==(nxt['track'],nxt['page_id'])
            assert len(r['join_evidence']['other_pages'])>=2
        if not r['assembly_changed']:
            assert r['fixed_text_gate_pass']
    for s in stats['sources']:
        rr=[r for r in features if r['track']==s['track'] and r['source']==s['source']]
        assert all(('marks_correction_required' in r['tags'])==s['marks_correction_required'] for r in rr)
    assert all('marks_correction_required' in r['tags'] for r in features if r['track']=='gr' and r['source'] in {'elstat','pergamos','lekythos'})
    checks['decisions_convention_branches_and_source_marks_tags'] = True
    for key, field in [('original_usable','original_usable'),('after_screen','usable_after_screen'),('after_conventions','usable_final'),('changed_lines','assembly_changed')]:
        assert sum(r[field] for r in features)==stats['totals'][key]
    for c in cards:
        if c['assembly_changed'] and c['letters']=='y':
            assert 'not manually adjudicated' not in c['adjudication']
    checks['totals_and_changed_card_adjudication_coverage'] = True
    footer=(OUT/'receipts/final_line.txt').read_text().strip()
    report=(OUT/'REPORT.md').read_text()
    assert report.splitlines()[-1]==footer
    for target in re.findall(r'\]\(([^)]+)\)',report):
        assert (OUT/target).exists(), ('broken report link',target)
    for path in OUT.glob('*.py'):
        compile(path.read_text(),str(path),'exec')
    checks['report_links_footer_and_python_compilation'] = True
    from screen import write_json
    write_json(OUT/'receipts/validation.json',dict(status='pass',checks=checks,elapsed_seconds=time.time()-started))
    print(json.dumps(dict(status='pass',checks=checks,elapsed_seconds=time.time()-started),indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        write_json(OUT/'receipts/validation.json',dict(status='failed',error=type(exc).__name__,detail=str(exc)))
        raise
