"""Custody and exclusion checks for the real offline N1-Cb products (no ink judgments)."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from greekocr.numerics.locks import load_locks

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/n1'

def rows(name):
    return [json.loads(s) for s in (OUT/name).read_text().splitlines()]

def generation():
    return json.loads((OUT/'N1Cb_GENERATION.json').read_text())

def test_step1_partition_and_explicit_drops():
    frame={r['slot_id'] for r in rows('frame_step1.jsonl') if r['partition']=='step1'}
    bed=rows('step1_rendered_v2.jsonl');dropped=rows('step1_dropped_misaligned_v2.jsonl')
    assert len(bed)==558 and len(dropped)==42
    assert {r['slot_id'] for r in bed}.isdisjoint(r['slot_id'] for r in dropped)
    assert {r['slot_id'] for r in bed+dropped}==frame
    assert Counter(r['reason'] for r in dropped)['digit box outside crop']==28
    assert all(r['geometry']['geom_status']=='ok' for r in bed)
    load_locks(OUT).assert_fit_rows(r['line_id'] for r in bed)

def test_control_exclusions_and_replacements():
    old=rows('controls/candidates.jsonl');new=rows('controls/candidates_v2.jsonl')
    bad={r['slot_id'] for r in old if r['geometry']['geom_status']!='ok'}
    assert len(bad)==15
    assert not bad.intersection(r['slot_id'] for r in new)
    assert {r['slot_id'] for r in old}-bad <= {r['slot_id'] for r in new}
    assert len({r['slot_id'] for r in new})==len(new)
    assert Counter(r['control_group'] for r in new)==dict(thousands_dot=24,decimal_comma=24,range_dash=22,inner_dash=12,empty=12)
    data=generation()
    assert data['summary']['all_W1_range_pool']==24
    assert sum(r['control_group']=='range_dash' for r in rows('controls/rejected_v2.jsonl'))==2
    locks=load_locks(OUT);devdocs={r['document'] for r in rows('frame_step1.jsonl') if r['partition']=='step1'}
    c1=set(json.loads((OUT/'locked_eval_docs.json').read_text())['excluded_c1_line_ids'])
    locks.assert_fit_rows(r['line_id'] for r in new)
    assert all(r['document'] not in devdocs|locks.reserved_docs and r['line_id'] not in c1 for r in new)

def test_sheet_index_and_reference_isolation():
    data=generation();paths=data['summary']['sheets']
    index=json.loads((Path(paths[0]).parent/'sheets_index.json').read_text())
    counts=Counter(r['sheet'] for r in index)
    assert all(n<=12 for n in counts.values())
    controls=rows('controls/candidates_v2.jsonl');refs=rows('controls/c1_references_v2.jsonl')
    assert len(refs)==4 and len({r['line_id'] for r in refs})==2
    assert all(r['reference_only'] for r in refs)
    assert {r['slot_id'] for r in refs}.isdisjoint(r['slot_id'] for r in controls)
    assert {r['slot_id'] for r in index if not r['reference_only']}=={r['slot_id'] for r in controls if r['line']}
    assert {r['slot_id'] for r in index if r['reference_only']}=={r['slot_id'] for r in refs}
    assert counts[data['summary']['c1_sheet']]==4

def test_hash_custody_and_interpreters():
    data=generation()
    for section in ['inputs','outputs']:
        for name,digest in data[section].items():
            assert hashlib.sha256(Path(name).read_bytes()).hexdigest()==digest,name
    collector=data['interpreters']['collector'];renderer=data['interpreters']['renderer']
    assert collector['machine']=='arm64' and collector['pillow']=='12.3.0'
    assert '3.11.3' in collector['version']
    assert renderer['machine']=='x86_64'
    assert data['constraints']==dict(network=False,git_writes=False,reader_run=False,real_packs=False,calibration_pack=False,glyph_classification=False)

def test_verified_crops_and_private_measurements():
    checks=rows('controls/crop_checks_v2.jsonl');byid={r['line_id']:r for r in checks}
    for r in checks:
        if not r['crop_unavailable']:
            assert '/scratchpad/n1_cache/crops/' in r['crop']
            assert hashlib.sha256(Path(r['crop']).read_bytes()).hexdigest()==r['crop_sha256']
    for r in rows('step1_rendered_v2.jsonl')+rows('controls/candidates_v2.jsonl')+rows('controls/c1_references_v2.jsonl'):
        assert r['crop_unavailable']==byid[r['line_id']]['crop_unavailable']
        if not r['crop_unavailable']:
            assert all(k in r['measurements'] for k in ['digit_top','baseline','digit_height','gap_width','components'])
            assert all(Path(r[k]).is_file() for k in ['line','zoom'])
