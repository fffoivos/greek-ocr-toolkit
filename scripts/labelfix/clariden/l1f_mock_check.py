"""Audit real 64-line L1F output and before/after frozen-SF6c deletions."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from PIL import Image
from greekocr.labelfix.ctc_align import Alignment, recognition_fields
from greekocr.labelfix.release_gate import _recogniser_scored
from scripts.labelfix.clariden.l1r_recompose_ext import overlay
from scripts.labelfix.clariden.l1f_run import load, sha256, rows, digest, crop_path


def check(config, output, destination):
    cfg = load(config); output = Path(output)
    receipt = load(output / 'receipt.json')
    assert receipt['complete'] and receipt['verification_only'] and receipt['lines'] == 64
    runtimes = {r['id']: r for path in cfg['mock_runtime'] for r in rows(path)}
    selected = {r['id']: r for r in rows(cfg['selection'])}
    db = sqlite3.connect(f'file:{output / "plan.sqlite"}?mode=ro', uri=True)
    saved = {r[0]: json.loads(r[1]) for r in db.execute('SELECT id,saved FROM lines')}; db.close()
    evidence = []
    for shard in receipt['shards']:
        assert sha256(output / shard['output']) == shard['output_sha256']
        evidence.extend(rows(output / shard['output']))
    assert len(evidence) == len({r['line_id'] for r in evidence}) == 64
    assert set(selected) == set(runtimes) == {r['line_id'] for r in evidence}
    counts = Counter(); transitions = []; held = []; mismatches = []
    binding = dict(detector='s6', r1_sha256='verification-saved-A', policy_sha256='frozen-SF6c')
    for row in evidence:
        line_id = row['line_id']; old = runtimes[line_id]
        assert set(row) == {'line_id','recognition_confidence','recognition_evidence',
                           'frame_confidences','image_width','provenance'}
        scores = row['frame_confidences']; confidence = row['recognition_confidence']
        assert scores and all(isinstance(v, float) and math.isfinite(v) and 0 <= v <= 1 for v in scores)
        assert math.isclose(sum(scores)/len(scores), confidence, rel_tol=0, abs_tol=2e-7)
        assert row['image_width'] > 0 and isinstance(row['image_width'], int)
        with Image.open(crop_path(selected[line_id]['crop'], cfg['crop_root'], cfg['layout'])) as native:
            assert row['image_width'] == native.width
        new = dict(old, **recognition_fields(row))
        counts['fields_verified'] += 1
        if row['provenance']['alignment_identity_match']:
            reconstructed = Alignment.from_record(saved[line_id])
            reconstructed.confidence = confidence; reconstructed.frame_confidences = scores
            # The identity compares the saved pixel-rounded spans. Rebuilding
            # the full evidence also checks the frozen alignment record hash.
            expected = reconstructed.recognition_evidence(old['detector']['slots'], row['image_width'])
            assert expected == row['recognition_evidence']
            assert digest({k:saved[line_id][k] for k in ('prediction','n_frames','scale','strip_width','spans')}) == row['provenance']['alignment_identity_sha256']
            counts['alignment_identity_matches'] += 1
        else:
            assert row['recognition_evidence']['scored'] is False
            assert row['recognition_evidence']['regions'] == []
            mismatches.append(dict(line_id=line_id, reasons=row['provenance']['alignment_mismatches']))
        for slot in old['detector']['slots']:
            counts['sf6c_certified_slots'] += _recogniser_scored(new, slot, slot.get('evidence', {}).get('window'))
        before = overlay(selected[line_id], old, 'presence', binding)
        after = overlay(selected[line_id], new, 'presence', binding)
        # Native width can enable reader bounds. Isolate the added score from
        # that effect to prove each chosen transition needs recogniser absence.
        width_only = overlay(selected[line_id], dict(old, image_width=row['image_width']), 'presence', binding)
        assert len(before['deletion_checks']) == len(after['deletion_checks']) == len(width_only['deletion_checks'])
        for a, b, w in zip(before['deletion_checks'], after['deletion_checks'], width_only['deletion_checks']):
            example = dict(line_id=line_id, original_label=selected[line_id]['label'],
                recogniser_text=old['recogniser_text'], proposal=after.get('label', after['composed_text']),
                before_line_status=before['status'], after_line_status=after['status'],
                before=a, after=b, native_width_only=w)
            if not a['allowed'] and not w['allowed'] and b['allowed'] and b['signals']['recogniser']:
                transitions.append(example)
            if not a['allowed'] and not b['allowed']:
                held.append(example)
    assert counts['fields_verified'] == 64 and counts['alignment_identity_matches'] == 62
    assert len(mismatches) == 2 and all('saved_transferred' in m['reasons'] for m in mismatches)
    unique_moves = {r['line_id']: r for r in reversed(transitions)}
    unique_held = {r['line_id']: r for r in reversed(held)}
    assert len(unique_moves) >= 2 and len(unique_held) >= 2
    result = dict(complete=True, verification_only=True, **counts,
        alignment_identity_mismatches=mismatches, mismatches_withheld=True,
        natural_deletions_becoming_allowed=len(transitions),
        natural_deletions_still_held=len(held),
        deletion_allowed_examples=list(unique_moves.values())[:2],
        deletion_hold_examples=list(unique_held.values())[:2],
        scope='Deletion checks; other slot HOLDs can keep the whole line held.',
        receipt_sha256=sha256(output/'receipt.json'), output_binding=receipt['binding'])
    Path(destination).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if 'examples' not in k}, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--config', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--evidence', required=True)
    args = ap.parse_args(); check(args.config, args.out, args.evidence)
