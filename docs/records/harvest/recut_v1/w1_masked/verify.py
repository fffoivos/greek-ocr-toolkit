"""Independent all-row custody, guard, audit and uniform-card verification."""
from __future__ import annotations
import sys
sys.dont_write_bytecode = True
import ast
from collections import Counter
import hashlib
import io
import json
from pathlib import Path
import random
import time
import numpy as np
from PIL import Image
import run
sys.path.insert(0, str(run.ROOT))
from greekocr.glyphs.components import binarise, to_gray


def verify():
    start = time.monotonic()
    run.io_guard()
    frozen = run.frozen()
    original_audit = next(n for n in ast.parse(run.SHARED_AUDIT.read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'component_audit')
    local_audit = next(n for n in ast.parse((run.BASE / 'component_audit.py').read_text()).body if isinstance(n, ast.FunctionDef) and n.name == 'component_audit')
    assert ast.dump(original_audit) == ast.dump(local_audit), 'component audit must be unchanged'
    eligible, excluded, population = run.population()
    assert population == json.loads((run.BASE / 'population.json').read_text())
    assert excluded == run.rows(run.BASE / 'excluded.jsonl')
    originals = {r['id']:r for r in eligible}
    binding = json.loads((run.BASE / 'binding.json').read_text())
    materializer_frozen = binding['frozen']
    if materializer_frozen != frozen:
        fix = json.loads((run.BASE / 'report_fix.json').read_text())
        archive = run.BASE / fix['materializer_source']
        assert run.sha(archive) == materializer_frozen['runner_sha256'] == fix['materializer_sha256']
        assert run.sha(run.BASE / 'run.py') == fix['reporter_sha256'] == frozen['runner_sha256']
        old_tree, new_tree = ast.parse(archive.read_text()), ast.parse((run.BASE / 'run.py').read_text())
        for tree in (old_tree, new_tree):
            tree.body = [n for n in tree.body if not (isinstance(n, ast.FunctionDef) and n.name == 'finish')]
        assert ast.dump(old_tree) == ast.dump(new_tree), 'materialization code changed'
        assert {k:v for k,v in materializer_frozen.items() if k != 'runner_sha256'} == {k:v for k,v in frozen.items() if k != 'runner_sha256'}
    for path, digest in binding['inputs'].items():
        assert run.sha(path) == digest, 'input changed: ' + path
    totals, manifests = {}, {}
    for source in run.SOURCES:
        record_path = run.BASE / source / 'records.jsonl'
        audit_path = run.BASE / source / 'component_audit.jsonl'
        records = run.rows(record_path); audits = {r['id']:r for r in run.rows(audit_path)}
        receipt_path = run.BASE / (source + '_receipt.json'); receipt = json.loads(receipt_path.read_text())
        assert {r['id'] for r in records} == {r['id'] for r in eligible if r['source'] == source} == set(audits)
        assert receipt['records_sha256'] == run.sha(record_path)
        assert receipt['component_audit_sha256'] == run.sha(audit_path)
        assert receipt['frozen'] == frozen
        assert receipt['admitted'] is False and receipt['gate']['applied_here'] is False
        for provenance in run.rows(run.BASE / source / 'provenance.jsonl'):
            assert provenance['frozen'] == materializer_frozen, 'mixed materializer revisions'
            assert run.sha(provenance['raster']) == provenance['raster_sha256']
            assert run.sha(provenance['response']) == provenance['response_sha256']
            assert run.sha(run.BASE / provenance['curve_path']) == provenance['curves_sha256']
        pages = {}
        counts = Counter()
        for row in records:
            original = originals[row['id']]
            raster = Path(original['crop_source_image'])
            if raster not in pages:
                pages.clear()
                assert run.sha(raster) == original['crop_source_sha256']
                with Image.open(raster) as image:
                    native = image.copy()
                pages[raster] = native, binarise(to_gray(native))
            image = pages[raster][0].crop(tuple(original['crop_bbox']))
            buffer = io.BytesIO(); image.save(buffer, format='PNG', compress_level=3)
            original_bytes = buffer.getvalue()
            assert hashlib.sha256(original_bytes).hexdigest() == original['crop_sha256'] == row['original_crop_sha256']
            stored = Path(original['crop'])
            if stored.exists(): assert stored.read_bytes() == original_bytes
            dest = run.BASE / row['masked_crop']
            assert run.sha(dest) == row['masked_crop_sha256']
            with Image.open(dest) as output:
                assert output.mode == image.mode and output.size == image.size
                a, b = np.asarray(image), np.asarray(output)
                changes = a != b
                assert int(changes.sum()) == row['native_changed_pixels']
                assert bool(changes.any()) == row['changed']
                # The frozen mask changes foreground only, in the original rectangle.
                if not row['wrong_line_risk']:
                    assert row['masked_pixel_count'] >= int(changes.sum())
            audit = audits[row['id']]
            before, after = audit['would_be'], audit['applied']
            assert before['own_pixels'] >= 0 and after['own_pixels'] == before['own_pixels']
            assert before['own_pixels'] or before['own_component_pixels_lost'] == 0
            assert row['own_ink_empty'] == audit['own_ink_empty'] == (before['own_pixels'] == 0)
            if row['wrong_line_risk']:
                witness = run.BASE / source / 'guard_witnesses' / (row['id'] + '.png')
                with Image.open(witness) as overlay:
                    proposed_changes = np.all(np.asarray(overlay) == (255, 0, 0), axis=2)
                assert int(proposed_changes.sum()) == row['would_be']['native_changed_pixels']
            else:
                proposed_changes = changes
            x0, y0, x1, y1 = original['crop_bbox']
            dark = pages[raster][1][y0:y1, x0:x1]
            assert not (proposed_changes & ~dark).any(), 'background pixels changed'
            if row['native_changed_pixels'] == row['masked_pixel_count']:
                assert hashlib.sha256(changes.tobytes()).hexdigest() == row['mask_sha256']
            total_dark, changed_dark = int(dark.sum()), int((dark & proposed_changes).sum())
            fraction = changed_dark/total_dark if total_dark else 0.
            assert row['guard_measurement'] == audit['guard_measurement'] == dict(
                original_dark_ink_pixels=total_dark, would_be_dark_ink_pixels_changed=changed_dark,
                own_ink_masked_fraction=fraction, original_dark_ink_empty=total_dark == 0)
            assigned_fraction = before['own_component_pixels_lost']/before['own_pixels'] if before['own_pixels'] else None
            assert row['assigned_own_ink_masked_fraction'] == audit['assigned_own_ink_masked_fraction'] == assigned_fraction
            assert fraction == row['own_ink_masked_fraction'] == audit['own_ink_masked_fraction']
            assert row['wrong_line_risk'] == audit['wrong_line_risk'] == (fraction > .30)
            assert row['component_audit'] == after
            if row['wrong_line_risk']:
                assert dest.read_bytes() == original_bytes
                assert row['mask_applied'] is False and after['own_component_pixels_lost'] == 0
                assert row['masked_pixel_count'] == row['masked_component_count'] == 0
                assert not row['changed'] and row['fills'] == []
            else:
                assert before == after
                assert row['mask_applied'] == row['matched']
            assert not row['admitted'] and not row['usable_final']
            assert row['params_sha256'] == run.PARAM_SHA and row['library_sha256'] == run.LIB_SHA
            assert row['google_text'] == original['label_after_conventions']
            counts['rows'] += 1; counts['changed'] += row['changed']; counts['guarded'] += row['wrong_line_risk']; counts['mask_applied'] += row['mask_applied']
        cards_path = run.BASE / receipt['cards']['cards']
        key_path = run.BASE / receipt['cards']['key']
        cards = run.rows(cards_path); key = json.loads(key_path.read_text())
        expected = random.Random('t6b:' + source).sample(sorted(records, key=lambda r:r['id']), 100)
        assert len(cards) == len({r['card_id'] for r in cards}) == 100
        assert [key[c['card_id']]['line_id'] for c in cards] == [r['id'] for r in expected]
        assert key['_pool'] == len(records)
        for card, row in zip(cards, expected):
            assert set(card) == {'card_id', 'crop', 'google_text', 'word_scripts'}
            assert card['google_text'] == row['google_text'] and card['word_scripts'] == run.word_scripts(row['google_text'])
            assert (cards_path.parent / card['crop']).read_bytes() == (run.BASE / row['masked_crop']).read_bytes()
            assert key[card['card_id']]['masked_crop_sha256'] == row['masked_crop_sha256']
        assert run.sha(cards_path) == receipt['cards']['cards_sha256'] and run.sha(key_path) == receipt['cards']['key_sha256']
        assert receipt['rows_masked'] == counts['mask_applied']
        assert receipt['rows_guarded'] == counts['guarded'] and receipt['changed_crops'] == counts['changed']
        assert counts['rows'] == receipt['rows_processed']
        assert receipt['own_ink_audit']['zero_assigned_own_ink_rows'] == sum(r['own_ink_empty'] for r in records)
        for sheet in receipt['contact_sheet']['sheets']:
            assert run.sha(run.BASE / sheet['path']) == sheet['sha256']
            assert all(next(r for r in records if r['id'] == ident)['wrong_line_risk'] for ident in sheet['rows'])
        totals[source] = dict(counts)
        for path in (record_path, audit_path, receipt_path, cards_path, key_path, run.BASE/source/'provenance.jsonl'):
            manifests[str(path.relative_to(run.BASE))] = run.sha(path)
        print(source, dict(counts), flush=True)
    assert run.sha(run.INSTRUCTIONS) == run.sha(run.BASE / 'cards/LABEL_CHECK_v2.md')
    artifacts = [dict(path=str(p.relative_to(run.BASE)), sha256=run.sha(p), bytes=p.stat().st_size)
        for p in sorted(run.BASE.rglob('*')) if p.is_file() and p.relative_to(run.BASE).parts[0] not in ('tmp', 'logs')
        and (p.suffix == '.png' or p.name.endswith('.json.gz'))]
    run.write_rows(run.BASE / 'artifact_hashes.jsonl', artifacts)
    manifests['artifact_hashes.jsonl'] = run.sha(run.BASE / 'artifact_hashes.jsonl')
    value = dict(passed=True, rows=sum(c['rows'] for c in totals.values()), cards=300,
        sources=totals, all_row_custody_verified=True, guard_byte_exact_verified=True,
        all_row_audits_present=True, uniform_seeded_draw_verified=True, labels_unchanged=True,
        checker_instructions_unchanged=True, shared_audit_ast_exact=True, frozen=frozen,
        materializer_frozen=materializer_frozen, materialization_ast_unchanged=True,
        artifact_hashes=len(artifacts), manifests=manifests, seconds=time.monotonic()-start,
        network='OFF', W1_read_only=True, created_utc=run.utc())
    run.write_json(run.BASE / 'validation.json', value)
    print(json.dumps({k:v for k,v in value.items() if k not in ('frozen','manifests')}, indent=2))


if __name__ == '__main__': verify()
