"""Offline R0a2: the authorized 133-line (i-a) extension, isolated from R0b.

Run with the project Python, PYTHONPATH=$PWD, PYTHONDONTWRITEBYTECODE=1.
Stages: freeze, align, spans, preview, cards, finish. Review the newly generated
control sheet before writing ia/controls_pixel_verified.jsonl and running cards.
No existing private key, original deck, or reader response is ever opened.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time

os.environ.update(PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1',
                  TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1',
                  GIT_OPTIONAL_LOCKS='0', TOKENIZERS_PARALLELISM='false')
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'docs/records/labelfix/spellcheck'
EVIDENCE = OUT/'R0_evidence'
WORK = EVIDENCE/'ia'
CACHE = ROOT/'.cache/labelfix/r0/align_locked_ia.jsonl'
COUNTS = {'81d8091c': 1, '309ff6cf': 10, 'f7c74d15': 122}
DOMINANCE = 'Ἀστέρια (f7c74d15) supplies 122/133 lines: stratum (i-a) is dominated by one book'
PROTECTED = [OUT/'R0_cards', OUT/'R0_expected_truth.json',
             OUT/'R0_line_truth_placeholders.jsonl']
PRIVATE = OUT/'R0_adjudication_private'
IO = Counter()


def audit(event, args):
    if event.startswith('socket.') and event in ('socket.connect', 'socket.getaddrinfo', 'socket.sendto'):
        raise RuntimeError('R0a2 network OFF')
    if event != 'open' or isinstance(args[0], int):
        return
    path, mode, flags = args
    p = Path(os.fsdecode(path)).absolute()
    writing = bool(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND))
    if any(p == q or q in p.parents for q in PROTECTED):
        raise RuntimeError(f'Original R0b inputs protected: {p}')
    if p == PRIVATE or PRIVATE in p.parents:
        if not writing or p != PRIVATE/'ia/items_key.json' or not flags & os.O_EXCL:
            raise RuntimeError('Private material is write-once IA key only; no private reads')
        IO['new_private_key_writes'] += 1
    if writing:
        resolved = p.resolve()
        if not (resolved == Path(os.devnull) or resolved.is_relative_to(ROOT) or resolved.is_relative_to(Path('/private/tmp'))
                or resolved.is_relative_to(Path('/private/var/folders'))):
            raise RuntimeError(f'No writes to other worktrees: {p} -> {resolved}')


sys.addaudithook(audit)
from scripts.labelfix import r0_prepare as r0
from PIL import Image, ImageDraw, ImageFont


def binding():
    old = json.loads((EVIDENCE/'input_binding.json').read_text())
    files = {p: h for p, h in old['files'].items()
             if p.startswith(('greekocr/', 'docs/records/harvest/wikisource/', '.cache/'))
             or p in ('docs/records/labelfix/case_model_S5.json', 'docs/records/labelfix/markshape_model_S4.json')}
    for p, h in files.items():
        assert r0.sha(ROOT/p) == h, ('changed R0a input', p)
    assert r0.sha(r0.CKPT[0]) == old['checkpoint_sha256']
    assert r0.sha(EVIDENCE/'L1_input_documents.txt') == old['l1_manifest_sha256']
    return dict(head=subprocess.check_output(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
        requested_head='b7fd49ba', branch=subprocess.check_output(
            ['git', '--no-optional-locks', 'branch', '--show-current'], cwd=ROOT).decode().strip(),
        checkpoint=str(r0.CKPT[0]), checkpoint_sha256=old['checkpoint_sha256'],
        files=files, l1_manifest_sha256=old['l1_manifest_sha256'], l1_commit=old['l1_commit'],
        l1_note='Use only the R0a local copy already bound byte-for-byte to commit 6b91ebaa; do not revisit the L1 worktree.',
        network=False, device='cpu', seed=r0.SEED)


def local_cache_directory():
    """Replace only this checkout's parent link; preserve all existing referents."""
    parent = ROOT/'.cache/labelfix'
    if parent.is_symlink():
        target = parent.resolve()
        assert not (target/'r0').exists(), 'An existing shared r0 cache must not be shadowed'
        stage = ROOT/'.cache/labelfix_local_r0a2'
        stage.mkdir()
        names = sorted(p.name for p in parent.iterdir())
        for name in names:
            (stage/name).symlink_to(target/name, target_is_directory=(target/name).is_dir())
        original = os.readlink(parent)
        parent.unlink()  # Unlink the workspace symlink, never its target.
        stage.rename(parent)
        r0.dump(WORK/'cache_localization_receipt.json', dict(
            previous_symlink=original, local_parent=str(parent),
            preserved_entries=names, shared_targets_modified=False,
            new_output_directory=str(parent/'r0')))
    assert not parent.is_symlink()
    (parent/'r0').mkdir(exist_ok=True)
    assert CACHE.parent.resolve().is_relative_to(ROOT)


def freeze():
    WORK.mkdir(parents=True, exist_ok=True)
    bind = binding()
    held = r0.read(EVIDENCE/'continuity_666.jsonl')
    dev = r0.read(EVIDENCE/'dev_598.jsonl')
    ii = r0.read(OUT/'R0_newsource_locked.jsonl')
    ii_dev = r0.read(OUT/'R0_newsource_dev.jsonl')
    l1 = (EVIDENCE/'L1_input_documents.txt').read_text().splitlines()
    assert len(held) == 666 and len(dev) == 598 and len(ii) == 200
    inventory, pools = r0.fresh_wiki_inventory({r['doc'] for r in held+dev} | set(l1))
    candidates = [r for k in sorted(pools) for r in pools[k]]
    # Re-evaluate the actual R0a function, then verify the prior inventory exactly.
    for k, rows in pools.items():
        assert rows == r0.read(EVIDENCE/f'fresh_candidates_{k}.jsonl'), k
    assert Counter(r['doc'].split(':')[1] for r in candidates) == COUNTS
    chosen, quotas = r0.stratified(candidates, 133, lambda r: r['doc'])
    again, _ = r0.stratified(candidates, 133, lambda r: r['doc'])
    assert chosen == again and len({r['line_id'] for r in chosen}) == 133
    chosen = [dict(r, book=r['doc'].split(':')[1], stratum='wikisource_ia',
                   selection_role='never_tune_locked_test') for r in chosen]
    checks = r0.overlap_receipt(chosen, dict(continuity_666=held, DEV=dev,
        L1_input=l1, stratum_ii=ii, stratum_ii_development=ii_dev))
    own_hashes = {r['crop_sha256'] for r in chosen}
    crop_checks = {}
    for name, pool in dict(continuity_666=held, DEV=dev, stratum_ii=ii,
                           stratum_ii_development=ii_dev).items():
        hits = sorted(own_hashes & {r0.sha(r['crop']) for r in pool})
        assert not hits, (name, hits)
        crop_checks[name] = dict(intersection=hits, count=0, comparison_crops=len(pool))
    assert len(own_hashes) == 133
    r0.write(OUT/'R0_locked_set.jsonl', chosen)
    (OUT/'R0_locked_ia_ids.txt').write_text(''.join(r['line_id']+'\n' for r in chosen))
    receipt = dict(schema='r0-locked-ia-v1', status='FROZEN_IA', seed=r0.SEED,
        coordinator_ruling='2026-10-17 option (c): freeze the 133 available lines as (i-a); (i-b) requires a new harvest.',
        stratum_i_lines=133, stratum_i_books=3, stratum='i-a', books=quotas,
        book_counts=COUNTS, book_inventory=inventory, dominance_note=DOMINANCE,
        eligibility='Unchanged R0a fresh_wiki_inventory: Greek book outside 666/DEV/L1; admitted existing whole crop; nonempty human label; aligned human line; explicit NFD POLY mark. No recogniser prediction or accuracy used.',
        determinism='All 133 eligible rows retained. R0a stratified largest-remainder, random.Random(20261017), stable line-id ordering. Repeated output identical; exact match to all R0a candidate inventories.',
        zero_intersections=checks, exact_crop_zero_intersections=crop_checks,
        comparison_manifest_sha256={
            'continuity_666':r0.sha(EVIDENCE/'continuity_666.jsonl'),
            'DEV':r0.sha(EVIDENCE/'dev_598.jsonl'),
            'L1_input_documents':r0.sha(EVIDENCE/'L1_input_documents.txt'),
            'stratum_ii':r0.sha(OUT/'R0_newsource_locked.jsonl'),
            'stratum_ii_development':r0.sha(OUT/'R0_newsource_dev.jsonl')},
        L1_input_documents=dict(path='R0_evidence/L1_input_documents.txt', sha256=bind['l1_manifest_sha256'],
            commit='6b91ebaa', documents=len(l1),
            scope='Document IDs and normalized stems compared; this input is document-only and has no line/crop list.'),
        document_identity_note='Identifier and exact-pixel checks do not exclude undocumented editions/copies across archives.',
        never_tune='Stratum (i-a), and all locked strata, must never be used for tuning, policy/checkpoint/threshold selection, or training releases. They judge L1 and wave 1c. The 666 remain the continuity instrument.',
        newsource_lines=200, newsource_dev_lines=273,
        cross_stratum_intersection_status='ZERO',
        newsource_manifest_sha256=r0.sha(OUT/'R0_newsource_locked.jsonl'),
        newsource_receipt_sha256=r0.sha(OUT/'R0_newsource_split_receipt.json'),
        locked_set_sha256=r0.sha(OUT/'R0_locked_set.jsonl'),
        release_exclusion_ids_sha256=r0.sha(OUT/'R0_locked_ia_ids.txt'),
        human_truth='Wikisource reference only; full pixel letter truth remains PENDING_R0b.',
        execution=bind)
    r0.dump(OUT/'R0_locked_set_receipt.json', receipt)
    r0.dump(WORK/'input_binding.json', bind)
    local_cache_directory()
    print('FROZEN_IA', len(chosen), COUNTS, flush=True)


def locked():
    receipt = json.loads((OUT/'R0_locked_set_receipt.json').read_text())
    assert receipt['status'] == 'FROZEN_IA'
    assert r0.sha(OUT/'R0_locked_set.jsonl') == receipt['locked_set_sha256']
    rows = r0.read(OUT/'R0_locked_set.jsonl')
    assert len(rows) == 133 and Counter(r['book'] for r in rows) == COUNTS
    for r in rows:
        assert r0.sha(r['crop']) == r['crop_sha256']
    return rows, receipt


def align():
    rows, receipt = locked()
    ckhash = receipt['execution']['checkpoint_sha256']
    assert r0.sha(r0.CKPT[0]) == ckhash
    assert CACHE.parent.resolve().is_relative_to(ROOT)
    have = {r['line_id']: r for r in r0.read(CACHE)} if CACHE.exists() else {}
    assert set(have) <= {r['line_id'] for r in rows}
    for r in rows:
        if r['line_id'] in have:
            prior = have[r['line_id']]
            assert prior['crop_sha256'] == r['crop_sha256'] and prior['checkpoint_sha256'] == ckhash
    missing = [r for r in rows if r['line_id'] not in have]
    start = time.monotonic()
    if missing:
        rec = r0.Recognizer(r0.CKPT[0], device='cpu', threads=4)
        # Same Recognizer.align_paths / masked_forward as the 666 cache.
        # Match its batch size 16; only this frozen list can reach the model.
        als = rec.align_paths([r['crop'] for r in missing], bs=16, log=lambda s: print(s, flush=True))
        assert set(als) == {r['crop'] for r in missing}
        for r in missing:
            have[r['line_id']] = dict(crop=r['crop'], line_id=r['line_id'],
                crop_sha256=r['crop_sha256'], checkpoint_sha256=ckhash,
                alignment=als[r['crop']].to_record(), origin='R0a2_CPU_forward',
                stratum='wikisource_ia')
        r0.write(CACHE, [have[r['line_id']] for r in rows])
    assert len(have) == 133
    result = dict(schema='r0-ia-align-v1', locked_crops=133, new_forward_crops=len(missing),
        total_R0a2_forward_crops=133, reused_ia_cache_crops=133-len(missing),
        checkpoint=str(r0.CKPT[0]), checkpoint_sha256=ckhash, model='E3 full_s0',
        cpu_only=True, device='cpu', threads=4, batch_size=16, network=False,
        code_path='greekocr.labelfix.ctc_align.Recognizer.align_paths -> align_batch -> masked_forward -> frames_to_spans (same as validate.alignments_for / 666 cache)',
        code_sha256=r0.sha(ROOT/'greekocr/labelfix/ctc_align.py'),
        never_forward_on_666=True, only_frozen_ia_forward=True,
        elapsed_seconds=round(time.monotonic()-start, 3),
        frozen_manifest_sha256=receipt['locked_set_sha256'],
        cache=str(CACHE.relative_to(ROOT)), sha256=r0.sha(CACHE))
    r0.dump(CACHE.with_suffix('.receipt.json'), result)
    print('Aligned', len(have), 'new forwards', len(missing), flush=True)


def aligned():
    rows, _ = locked()
    cache = r0.read(CACHE)
    assert [r['line_id'] for r in cache] == [r['line_id'] for r in rows]
    als = {r['line_id']: r0.Alignment.from_record(r['alignment']) for r in cache}
    for r in rows:
        r['model'] = als[r['line_id']].prediction
    return rows, als


def plan():
    rows, als = aligned()
    return r0.planned_cards(rows, als, work=WORK)


def preview():
    items, controls, lmap, als = plan()
    needed = math.ceil(len(items)*.08/.92)
    rng = random.Random(r0.SEED)
    rng.shuffle(controls)
    controls = controls[:max(needed*2, 20)]
    for i, c in enumerate(controls):
        c['control_id'] = f'ia_ctrl{i:03d}'
    r0.write(WORK/'control_review_queue.jsonl', controls)
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 18)
    for start in range(0, len(controls), 16):
        subset = controls[start:start+16]
        canvas = Image.new('RGB', (1750, len(subset)*110), '#eeeeee')
        draw = ImageDraw.Draw(canvas)
        for j, c in enumerate(subset):
            l = lmap[c['line_id']]
            with Image.open(l['crop']) as im:
                crop = im.crop(r0.card_window(c, l, als[c['line_id']])).convert('RGB')
            crop.thumbnail((1100, 90))
            canvas.paste(crop, (620, j*110+8))
            draw.text((8, j*110+12), c['control_id']+' '+c['correct'], fill='black', font=font)
        canvas.save(WORK/f'control_review_{start//16:02d}.png')
    print('Adjudication cards', len(items), 'controls needed', needed, 'preview candidates', len(controls), flush=True)


def cards():
    planned = plan()
    verified = r0.read(WORK/'controls_pixel_verified.jsonl')
    candidates = {(r['line_id'], r['start'], r['end'], r['correct']) for r in planned[1]}
    assert all((r['line_id'], r['start'], r['end'], r['correct']) in candidates for r in verified)
    receipt, blind, key = r0.build_cards(plan=planned, verified=verified, tag='ia', work=WORK)
    assert all(set(b) <= {'id', 'img', 'line_img', 'A', 'B', 'C'} for b in blind)
    assert len({b['id'] for b in blind}) == len(blind)
    assert sum(k['control'] for k in key) == receipt['controls']
    assert receipt['control_fraction'] >= .08
    assert all(k['zoom_scale'] <= 3 for k in key)
    assert {k['line_id'] for k in key} <= set(planned[2])
    assert all(k['expected_choice'] is None for k in key if not k['control'])
    receipt['adjudication_lines'] = len({k['line_id'] for k in key if not k['control']})
    receipt['lines_with_any_card'] = len({k['line_id'] for k in key})
    receipt['locked_lines_without_disagreement_cards'] = len(planned[2])-receipt['adjudication_lines']
    receipt['control_rule'] = 'ceil(adjudication_cards * 0.08 / 0.92), unchanged from R0a; discreteness gives 3/27 = 11.11% here.'
    r0.dump(WORK/'cards_receipt.json', receipt)
    r0.dump(WORK/'private_write_receipt.json', dict(key_written_once=True,
        key_sha256=receipt['key_sha256'], key_validated_in_memory=True,
        existing_private_reads=0, new_private_reads=0, original_deck_opens=0,
        controls=receipt['controls'], source='New IA pixel-verified controls only', io=dict(IO)))


def finish():
    rows, locked_receipt = locked()
    bind = binding()
    cr = json.loads((WORK/'cards_receipt.json').read_text())
    card_plan = r0.read(WORK/'card_plan.jsonl')
    control_rows = r0.read(WORK/'controls_pixel_verified.jsonl')[:cr['controls']]
    covered = {r['line_id'] for r in card_plan}
    cr.update(adjudication_lines=len(covered),
        lines_with_any_card=len(covered | {r['line_id'] for r in control_rows}),
        locked_lines_without_disagreement_cards=133-len(covered),
        control_rule='ceil(adjudication_cards * 0.08 / 0.92), unchanged from R0a; discreteness gives 3/27 = 11.11% here.')
    assert len(card_plan) == cr['adjudication_cards']
    r0.dump(WORK/'cards_receipt.json', cr)
    spans = json.loads((WORK/'span_summary.json').read_text())
    ar = json.loads(CACHE.with_suffix('.receipt.json').read_text())
    blind = json.loads((OUT/'R0_cards_ia/items_blind.json').read_text())
    truth = json.loads((OUT/'R0_expected_truth_ia.json').read_text())
    assert [r['id'] for r in blind] == [r['id'] for r in truth]
    assert all(r['reader_1']['choice'] is None and r['reader_2']['choice'] is None
               and r['adjudicated']['status'] == 'PENDING_R0b' for r in truth)
    line_truth = r0.read(OUT/'R0_line_truth_placeholders_ia.jsonl')
    assert len(line_truth) == 133 and all(r['full_line_letter_truth'] is None for r in line_truth)
    assert len(r0.read(WORK/'span_line_census.jsonl')) == 133
    assert len(r0.read(WORK/'span_slots.jsonl.gz')) == spans['pooled']['all_alphabetic_slots']
    assert r0.sha(CACHE) == ar['sha256']
    assert r0.sha(OUT/'R0_cards_ia/items_blind.json') == cr['blind_sha256']
    image_count = 0
    for p in sorted((OUT/'R0_cards_ia/img').glob('*.png')):
        with Image.open(p) as im:
            im.verify()
        image_count += 1
    for b in blind:
        assert (OUT/'R0_cards_ia'/b['img']).is_file() and (OUT/'R0_cards_ia'/b['line_img']).is_file()
    viewer = (OUT/'R0_cards_ia/index.html').read_text()
    assert 'R0_adjudication_private' not in viewer and 'r0-blind-ia-v1' in viewer
    assert all(set(b) <= {'id','img','line_img','A','B','C'} for b in blind)
    assert ar['locked_crops'] == 133 and ar['cpu_only'] and not ar['network']
    assert cr['control_fraction'] >= .08
    viewer_validation = json.loads((WORK/'viewer_validation.json').read_text())
    visual_qa = json.loads((WORK/'visual_qa_receipt.json').read_text())
    assert viewer_validation['syntax'] == 'PASS' and viewer_validation['rendered_articles'] == len(blind)
    assert visual_qa['card_zooms_inspected'] == len(blind)
    # Verify the original non-reader artifacts against R0a's recorded hashes.
    original_hashes = json.loads((EVIDENCE/'artifact_hashes.json').read_text())
    preserved = {}
    for name in ('R0_newsource_locked.jsonl', 'R0_newsource_dev.jsonl',
                 'R0_newsource_split_receipt.json', 'R0_newsource_exclusion_ids.txt',
                 'R0_newsource_dev_ids.txt', 'R0_failures.jsonl'):
        actual = r0.sha(OUT/name)
        assert actual == original_hashes[name], name
        preserved[name] = actual
    r0.dump(WORK/'validation.json', dict(lines=133, book_counts=COUNTS,
        zero_intersections=locked_receipt['zero_intersections'],
        blind_items=len(blind), pngs_decoded=image_count, blank_truth_records=len(truth),
        blank_full_line_records=133, controls=cr['controls'],
        viewer_validation=viewer_validation, visual_qa=visual_qa,
        private_key_validation='In-memory at write time; private files never reopened.',
        original_deck_access='Forbidden by Python audit hook throughout R0a2 stages.',
        network='Offline environment and Python socket-connect/DNS/sendto audit rejection.',
        preserved_R0a_artifacts=preserved, runtime_checkpoint_shared_cache_hashes_verified=bind,
        no_git_writes=True, no_other_worktree_writes=True))
    p = spans['pooled']
    final = (f"R0a2 READY: stratum (i-a) 133 lines / 3 books (Ἀστέρια 122); zero overlap with 666, DEV, L1 input, (ii); "
             f"cards {cr['adjudication_cards']} (+controls {cr['controls']}); spans outside blob {p['outside_pct']:.4f}%")
    section = '\n\n## R0a2 — frozen stratum (i-a), 17 October 2026\n\n'
    section += ('Coordinator option (c) supersedes the earlier scope-pending status: **133 lines / 3 books frozen as (i-a)**; (i-b) awaits a new harvest. '
        'Counts: 81d8091c 1, 309ff6cf 10, f7c74d15 122. **'+DOMINANCE+'**. '
        'Rerunning unchanged R0a eligibility matched all prior candidate rows; seed 20261017, all eligible lines retained. '
        '[Manifest](R0_locked_set.jsonl), [freeze/exclusion receipt](R0_locked_set_receipt.json), [release-exclusion IDs](R0_locked_ia_ids.txt). '
        'Line/document/normalized-stem intersections with 666, DEV, L1 input and (ii) are zero; crop hashes also exclude 666/DEV/(ii). L1 uses its locally bound document-only manifest. '
        '**Never tune or train on locked strata:** they judge L1 and wave 1c; the 666 remain continuity.\n\n')
    section += (f"**133 E3 full_s0 CPU forwards**, same `Recognizer.align_paths` as the 666 cache; no other lines forwarded. "
        '[Alignment receipt](../../../.cache/labelfix/r0/align_locked_ia.receipt.json). '
        'The workspace cache parent was localized before writing; shared cache hashes are unchanged. '
        f"Head `{bind['head'][:8]}` adds only the R0a2 brief to `b7fd49ba`. Network off; no Git/other-worktree writes.\n\n")
    section += (f"Separate [blind IA deck](R0_cards_ia/index.html): **{cr['adjudication_cards']} cards + {cr['controls']} planted controls** "
        f"({100*cr['control_fraction']:.2f}%; unchanged minimum-8% rounding rule), using R0a's generator and seeded ordering. "
        f"Disagreement cards cover {cr['adjudication_lines']}/133 lines; fresh lines have no historical S4/S5/M2 cohorts. "
        'New controls were pixel-verified. The IA key was written once under `R0_adjudication_private/ia/`, validated in memory, never reopened. '
        'No existing private material, original deck or R0b truth file was read or modified. IA IDs/answer storage are separate. '
        '[Blank truth](R0_expected_truth_ia.json) and [133 full-line placeholders](R0_line_truth_placeholders_ia.jsonl) await R0b; shared errors remain unadjudicated.\n\n')
    section += (f"Native span census, all 133 lines: **{p['outside']} / {p['clean_slots']} clean alphabetic slots = {p['outside_pct']:.4f}% outside blob**, "
        f"from {p['all_alphabetic_slots']} alphabetic slots (31 split, 45 fused, 6 without a letter blob). "
        'Same native component/ownership method as R0a; geometry only, no letter-error claim. '
        '[Script/size/book summary](R0_evidence/ia/span_summary.json), [all slots](R0_evidence/ia/span_slots.jsonl.gz), '
        '[line/atom census](R0_evidence/ia/span_line_census.jsonl), [validation](R0_evidence/ia/validation.json).\n\n')
    report = OUT/'R0_REPORT.md'
    current = report.read_text()
    assert '## R0a2 — frozen stratum' not in current, 'Append only once'
    report.write_text(current.rstrip()+section+final+'\n')
    print(final, flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stage', choices=['freeze','align','spans','preview','cards','finish'])
    stage = ap.parse_args().stage
    if stage == 'spans':
        rows, als = aligned()
        r0.audit_spans(rows, als, work=WORK)
    else:
        globals()[stage]()


if __name__ == '__main__':
    main()
