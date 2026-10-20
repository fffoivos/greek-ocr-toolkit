"""Offline S8a7 equivalent of s8_prepare --masked, preserving the frozen deck.

Run from the repo with PYTHONPATH=$PWD and the S8 Python, -B. All writes are
restricted by an audit hook to this directory and the new S8a7 report.
"""
import os
import sys
sys.dont_write_bytecode = True
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
             'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS', 'BLIS_NUM_THREADS'):
    os.environ[name] = '1'
os.environ.update(PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', GIT_OPTIONAL_LOCKS='0')
import collections as C
from copy import deepcopy
import gzip
import json
import math
from pathlib import Path
import socket
import subprocess
import time
import numpy as np
from PIL import Image
from scripts.labelfix import s8_prepare as p, s8_score_truth as t

DEST = Path(__file__).resolve().parent
REPORT = p.OUT.parent / 'S8a7_MASKED_DETECTOR.md'
WAVES = t.WAVES
REQUESTED_HEAD = '78883b629fe1c48e5fe48b5be55f3a815a6f53dc'


def audit(event, args):
    if event.startswith('socket.'):
        raise RuntimeError('S8a7 network OFF')
    paths = []
    if event == 'open':
        path, mode, flags = args
        if (mode and any(c in mode for c in 'wax+')) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            paths = [path]
    elif event in ('os.mkdir', 'os.remove', 'os.rmdir', 'os.chmod', 'os.truncate'):
        paths = [args[0]]
    elif event in ('os.rename', 'os.link', 'os.symlink'):
        paths = args[:2]
    for path in paths:
        if isinstance(path, int):
            continue
        target = Path(os.fsdecode(path)).resolve()
        if target != REPORT and target != DEST and DEST not in target.parents:
            raise RuntimeError(f'S8a7 write outside output boundary: {target}')


sys.addaudithook(audit)


def dump(name, obj):
    p.dump(DEST / name, obj)


def write(name, rows):
    p.write(DEST / name, rows)


def protected():
    paths = [x for x in p.OUT.rglob('*') if x.is_file() and DEST not in x.parents]
    paths += list(p.OUT.parent.glob('S8a*_*.md'))
    return {str(x.relative_to(p.ROOT)): p.sha(x) for x in sorted(paths) if x != REPORT}


def aggregate(records):
    c, hist = C.Counter(), C.Counter()
    for r in records:
        c.update({k: v for k, v in r['metrics'].items() if k != 'components_per_letter_histogram'})
        hist.update({int(k): v for k, v in r['metrics']['components_per_letter_histogram'].items()})
    n = c['letters']
    return dict(lines=len(records), **c, components_per_letter=c['component_assignments']/n if n else None,
                components_per_letter_histogram=dict(sorted(hist.items())),
                rates_percent={k: 100*c[k]/n if n else None for k in p.METRICS},
                affected_lines={k: sum(bool(r['metrics'][k]) for r in records) for k in p.METRICS},
                gate={m: dict(C.Counter(r['decisions'][m]['status'] for r in records)) for m in p.MODES})


def run_baseline(ids, sources, remote, staged, binding):
    p.case.configure_model(p.ROOT/'docs/labelfix/case_model_S5.json')
    model = p.markshape.load_model(p.ROOT/'docs/labelfix/markshape_model_S4.json')
    bp = dict(detector='s6', r1_sha256='719a06b9b18f082ec627a64e7f60c501491bcb6c63a9a78e7eba41ec7adb4636',
              policy_sha256=binding['policy']['sha256'])
    original, effective, custody, replays = {}, {}, [], []
    started, runs, cache_hits = time.monotonic(), 0, 0
    for i, k in enumerate(ids, 1):
        src = sources[k]
        orig_path = Path(src['original_path'])
        old_path = p.E/'baseline/original'/(k+'.json.gz')
        old = json.loads(gzip.decompress(old_path.read_bytes()))
        assert old['crop_sha256'] == p.sha(orig_path)
        assert old['binding_sha256'] == p.digest(binding)
        saved = remote['runtime'][k]
        al = p.Alignment.from_record(remote['alignments'][k]['alignment'])
        assert saved['historical_A_verified'] and p.nfd(saved['recogniser_text']) == al.prediction
        reader_hash = p.digest({key: saved.get(key) for key in ('recogniser_text', 'recogniser_nfd', 'r1_predictions', 'coverage', 'peer_predictions', 'peer_coverage', 'k1_flags')})
        assert reader_hash == old['reader_inputs_sha256']
        original[k] = old
        if k not in staged:
            assert src['wave'] == 'parliament'
            effective[k] = old
            continue
        sr = staged[k]
        crop, own = p.MASK/sr['masked_path'], p.MASK/sr['ownership_path']
        assert sr['wave'] == src['wave'] and not sr['custody_failures'] and sr['originals_unchanged']
        assert p.sha(orig_path) == sr['original_crop_sha256']
        assert p.sha(crop) == sr['masked_sha256'] and p.sha(own) == sr['ownership_sha256']
        with Image.open(orig_path) as oi, Image.open(crop) as mi, Image.open(own) as om:
            labels = np.asarray(om)
            assert oi.size == mi.size and labels.shape == (oi.height, oi.width)
            assert set(np.unique(labels)) <= set(range(6))
            changed = int(np.count_nonzero(np.any(np.asarray(oi.convert('RGB')) != np.asarray(mi.convert('RGB')), axis=2)))
            assert changed == sr['native_changed_pixels']
        custody.append(dict(id=k, wave=sr['wave'], mask_applied=sr['mask_applied'], failure_kind=sr['failure_kind'],
                            changed_pixels=changed, crop=str(crop), crop_sha256=p.sha(crop), ownership=str(own), ownership_sha256=p.sha(own),
                            original_crop_sha256=p.sha(orig_path), original_baseline_sha256=p.sha(old_path)))
        if not sr['mask_applied']:
            assert sr['failure_kind'] in ('unmatched', 'ambiguous') and not changed
            assert p.sha(crop) == old['crop_sha256']
            effective[k] = old
            continue
        cache = DEST/'baseline/masked'/(k+'.json.gz')
        if cache.exists():
            record = json.loads(gzip.decompress(cache.read_bytes()))
            assert record['binding_sha256'] == p.digest(binding) and record['crop_sha256'] == p.sha(crop)
            assert record['reader_inputs_sha256'] == reader_hash
            cache_hits += 1
        else:
            with Image.open(crop) as im:
                ci = p.ink.analyse(im)
            serial = p.gate.serialize(p.reading.read_ink(ci, al.prediction, al, model, filtered=False))
            runtime = {key: deepcopy(v) for key, v in saved.items() if key not in ('evidence_sha256', 'modes', 'historical_A_verified')}
            runtime['detector'] = serial
            modes = {m: p.gate.compose_runtime(runtime, m) for m in p.MODES}
            decisions = {m: p.overlay(src, runtime, m, bp) for m in p.MODES}
            record = dict(id=k, wave=src['wave'], variant='masked', crop=str(crop), crop_sha256=p.sha(crop),
                          crop_size=[ci.width, ci.height], binding_sha256=p.digest(binding), metrics=p.metrics(serial),
                          detector=serial, modes=modes, decisions=decisions, reader_inputs_sha256=reader_hash)
            cache.parent.mkdir(parents=True, exist_ok=True)
            cache.write_bytes(gzip.compress(json.dumps(record, ensure_ascii=False, allow_nan=False).encode(), mtime=0))
            runs += 1
        # Compare serialized evidence: detector tuples and histogram integer keys
        # become lists/string keys in the saved baseline JSON.
        record = json.loads(json.dumps(record, ensure_ascii=False, allow_nan=False))
        assert record['metrics']['letters'] == old['metrics']['letters']
        # All 67 pixel-identical matched masks are exact frozen-runtime replay witnesses.
        if not changed:
            same = {field: record[field] == old[field] for field in ('detector', 'metrics', 'modes', 'decisions')}
            assert all(same.values()), (k, same)
            replays.append(dict(id=k, identical=same))
        effective[k] = record
        if i % 50 == 0:
            print(f'S8a7 baseline {i}/600; runs {runs}; {time.monotonic()-started:.1f}s', flush=True)
    dump('input_custody.json', custody)
    dump('pixel_identical_replay.json', replays)
    return original, effective, dict(detector_runs_this_invocation=runs, cache_hits=cache_hits,
                                     seconds=time.monotonic()-started, pixel_identical_replay_witnesses=len(replays))


def estimate_pair(rows, family, seed):
    output = {}
    for variant in ('original', 'masked'):
        def num(r): return r['presence'][variant]['counts'][family]['TP']
        output[variant] = dict(counts={event: dict(raw=sum(r['presence'][variant]['counts'][family][event] for r in rows),
            weighted=sum(r['weight']*r['presence'][variant]['counts'][family][event] for r in rows)) for event in ('TP', 'FP', 'FN', 'TN')})
        for metric, error in (('precision', 'FP'), ('recall', 'FN')):
            output[variant][metric] = t.estimate(rows, num, lambda r: num(r)+r['presence'][variant]['counts'][family][error], seed)
    output['paired_change'] = {}
    for metric, error in (('precision', 'FP'), ('recall', 'FN')):
        delta = dict(value=None, document_bootstrap95=None, line_bootstrap95=None)
        a, b = (output[v][metric]['value'] for v in ('original', 'masked'))
        if a is not None and b is not None:
            delta['value'] = b-a
            for level in ('document', 'line'):
                group = lambda r: r['line_id'].split('-p')[0] if level == 'document' else r['line_id']
                groups = sorted({group(r) for r in rows})
                ix = {k: i for i, k in enumerate(groups)}
                matrix = np.zeros((len(groups), 4))
                for r in rows:
                    cells = []
                    for v in ('original', 'masked'):
                        c = r['presence'][v]['counts'][family]
                        cells += [r['weight']*c['TP'], r['weight']*(c['TP']+c[error])]
                    matrix[ix[group(r)]] += cells
                rng = np.random.default_rng(seed)
                totals = rng.multinomial(len(groups), np.full(len(groups), 1/len(groups)), size=t.REPS) @ matrix
                valid = (totals[:, 1] > 0) & (totals[:, 3] > 0)
                diffs = totals[valid, 2]/totals[valid, 3] - totals[valid, 0]/totals[valid, 1]
                delta[level+'_bootstrap95'] = np.quantile(diffs, [.025, .975]).tolist() if len(diffs) else None
                delta[level+'_bootstrap_valid'] = int(valid.sum())
        output['paired_change'][metric] = delta
    return output


def score_words(census, keys, truth_rows, remote, sources, original, effective, staged):
    by_line = C.defaultdict(list)
    for r in census:
        by_line[r['line_id']].append(r)
    deck = {r['uid']: r for r in keys if not r['control']}
    truth = {r['uid']: r for r in truth_rows if r.get('type') == 'item' and not r['control']}
    comparisons, deltas, scores = [], [], []
    for lid, old_words in by_line.items():
        forms = dict(google=sources[lid]['label'], r1_A=p.r1_text(remote['runtime'][lid], canonical=False),
                     detector_original=original[lid]['detector']['text'], frozen_AB=original[lid]['modes']['ENSEMBLE_AB']['text'],
                     detector_masked=effective[lid]['detector']['text'])
        groups = p.word_groups(remote['runtime'][lid]['recogniser_nfd'], forms, retain_raw=True)
        assert [(r['start'], r['end']) for r in old_words] == [(g['start'], g['end']) for g in groups], lid
        for old, g in zip(old_words, groups):
            assert all(g['forms'][s] == v and g['raw_forms'][s] == old['raw_forms'][s] for s, v in old['forms'].items())
            key, tr = deck.get(old['uid']), truth.get(old['uid'])
            # Canonical aliases count as existing options, exactly as in S8a6.
            options = key['options'] if key else {'population_consensus': next(iter(old['forms'].values())) or '∅'}
            new = t.canonical(g['forms']['detector_masked']) not in {t.canonical(v) for v in options.values()}
            row = dict(uid=old['uid'], id=key['id'] if key else None, line_id=lid, wave=old['wave'], start=old['start'], end=old['end'],
                       forms=old['forms'] | {'detector_masked': g['forms']['detector_masked']}, frozen_options=options,
                       new_candidate=new, in_frozen_deck=key is not None, truth_status=tr['status'] if tr else 'not_in_deck',
                       in_cut=bool(tr and tr['in_cut']), mask_applied=bool(staged.get(lid, {}).get('mask_applied')),
                       fallback_kind=staged.get(lid, {}).get('failure_kind'), weight=tr.get('weight') if tr else None,
                       scored=bool(tr and tr['status'] == 'resolved' and not new))
            comparisons.append(row)
            if new:
                assert lid in staged and staged[lid]['mask_applied']
                deltas.append(row | dict(exclusion='new masked candidate; no adjudication or scoring'))
            if not tr or tr['status'] != 'resolved':
                continue
            assert math.isclose(tr['weight'], 1/(tr['card_inclusion_probability']*tr['cut_probability']), rel_tol=1e-14)
            ss = lambda record: [s for s in record['detector']['slots'] if tr['start'] <= s['start'] < tr['end'] and t.letter(s)]
            orig_presence, _ = t.score_presence(tr, 'detector_original', ss(original[lid]))
            assert orig_presence == tr['presence']['detector_original'], tr['id']
            scored = {k: row[k] for k in ('uid', 'id', 'line_id', 'wave', 'start', 'end', 'forms', 'mask_applied', 'fallback_kind', 'weight', 'scored', 'new_candidate')}
            scored.update(truth=tr['truth'], selection=tr['selection'], presence={'original': orig_presence})
            if not new:
                dummy = dict(tr, forms=dict(tr['forms'], detector_original=g['forms']['detector_masked']))
                scored['presence']['masked'], _ = t.score_presence(dummy, 'detector_original', ss(effective[lid]))
            scores.append(scored)
    assert len(comparisons) == 4942 and len(scores) == 976
    order = {r['uid']: i for i, r in enumerate(truth_rows) if r.get('type') == 'item' and not r['control']}
    scores.sort(key=lambda r: order[r['uid']])
    write('word_comparison.jsonl', comparisons)
    write('delta_cards.jsonl', deltas)
    write('scores_per_word.jsonl.gz', scores)
    return comparisons, deltas, scores


def pair_rate(b, key):
    return f"{b['original'].get(key, 0)}/{b['original']['letters']} → {b['effective'].get(key, 0)}/{b['effective']['letters']} ({b['original']['rates_percent'][key]:.2f}→{b['effective']['rates_percent'][key]:.2f}%)"


def brief(cell):
    return '—' if cell['value'] is None else f"{100*cell['value']:.2f}%"


def change(cell):
    if cell['value'] is None:
        return '—'
    lo, hi = cell['document_bootstrap95']
    return f"{100*cell['value']:+.2f} [{100*lo:+.2f}, {100*hi:+.2f}]"


def gate_status(agg, mode):
    c = agg['gate'][mode]
    return f"{c.get('corrected', 0)+c.get('unchanged', 0)} kept ({c.get('corrected', 0)} corrected / {c.get('unchanged', 0)} unchanged), {c.get('hold', 0)} hold"


def report(summary, head, run):
    waves = summary['waves']
    out = ['# S8a7 — masked detector against frozen DEV truth', '',
           '**441/450 non-parliament lines have matched masks; nine retain their originals (six unmatched, three ambiguous). Parliament remains unmasked.** '
           'The frozen S6 detector and SF4 gate use the saved recogniser alignment and R1 A/B/E predictions. No reader inference, network access, source changes or new adjudication.', '',
           '**On the paired eligible adjudicated words, physical presence recall is exactly unchanged in every wave.** '
           'Precision changes are small: round1 +0.27 pp, vouli −0.20 pp, other waves unchanged. '
           'Across the full DEV, clipping flags fall sharply (top 3,307→1,383; bottom 3,124→1,764) and AB kept rises 56→114, '
           'while loc_unknown barely moves (876→875) and seg_uncertain increases (1,389→1,394). '
           'Clipping diagnostics and gate releases improve, without demonstrated recall recovery on the eligible cut. '
           'There are 44 delta candidate words: 35 in the frozen data deck, including ten resolved words excluded from paired scoring, plus nine outside that deck.', '',
           f'Analysis HEAD `{head}`. [Receipt](S8_DEV/masked/receipt.json), [summary](S8_DEV/masked/summary.json), '
           '[per-line original→masked comparison](S8_DEV/masked/baseline_per_line.jsonl), '
           '[per-word scores](S8_DEV/masked/scores_per_word.jsonl.gz), [delta candidates](S8_DEV/masked/delta_cards.jsonl).', '',
           '## Inputs and preservation', '',
           f"Saved runtime SHA256 `{p.sha(p.E/'remote.json.gz')}`; frozen truth SHA256 `{p.sha(p.E/'dev_truth.jsonl.gz')}`. "
           'The runtime matches the S8a3/S8a4 request-bound receipt, with 600 complete runtimes and alignments and zero inference. '
           'Mask receipt and lines hashes, all 450 original/masked crop hashes, all ownership-map hashes, dimensions, 0–5 class values and changed-pixel counts are verified. '
           'The handoff guard records 0/450 over 30% wrong-line-risk threshold (maximum 26.58%); it was evaluated after the sourcing run and would change no line. '
           'Ownership maps are detector attribution, not semantic truth. Masking changed pixels on 374 lines; 67 matched masks were pixel-identical.', '',
           f"All {run['pixel_identical_replay_witnesses']} pixel-identical matched masks reproduce the original detector, metrics, composed modes and gate decisions exactly. "
           'The saved original baseline binding and all bound sources are checked against frozen commit `c6064650fa5451cbc3bd13197d7a31c0d3bbf33d`. '
           'A Python audit hook prohibits writes outside `S8_DEV/masked/` and this report, and prohibits sockets. '
           'Every pre-existing DEV artifact, including all three protected card directories, truth, and the S8a6 report, is hashed before/after. No `.git` writes.', '',
           f'The workspace advanced externally from task-start HEAD `{REQUESTED_HEAD}` to the analysis HEAD; '
           'the only intervening change adds `docs/briefs/S8b_detector_iteration.md`. All S8a7 input and runtime content is unchanged.', '',
           '## Baseline on the complete line population', '',
           'These are unweighted recogniser-indexed letter counts across all 600 lines. Effective masked means the 441 matched-mask outputs plus the nine unchanged fallbacks and 150 unchanged parliament originals. '
           'Loc/seg/clip flags are detector diagnostics; truth presence below is a separate measurement.']
    t.table(out, ['Wave', 'Lines / matched / changed', 'Letters', 'loc_unknown original→masked', 'seg_uncertain original→masked'],
            [(w, f"{s['lines']} / {s['matched_masks']} / {s['changed_lines']}", s['baseline']['original']['letters'], pair_rate(s['baseline'], 'localisation_unknown'), pair_rate(s['baseline'], 'segmentation_uncertain')) for w, s in waves.items()])
    t.table(out, ['Population', 'Lines / letters', 'loc_unknown', 'seg_uncertain', 'Clipped top / bottom'],
            [(name, f"{b['original']['lines']} / {b['original']['letters']}", pair_rate(b, 'localisation_unknown'), pair_rate(b, 'segmentation_uncertain'),
              f"{b['original']['clipped_top']}→{b['effective']['clipped_top']} / {b['original']['clipped_bottom']}→{b['effective']['clipped_bottom']}")
             for name, b in (('all DEV', summary['ALL']['baseline']), ('non-parliament', summary['nonparliament_baseline']), ('matched masks only', summary['matched_baseline']))])
    t.table(out, ['Wave', 'Clipped top', 'Clipped bottom', 'Unnamed letters', 'Unnamed blobs', 'Components/letter'],
            [(w, pair_rate(s['baseline'], 'clipped_top'), pair_rate(s['baseline'], 'clipped_bottom'), pair_rate(s['baseline'], 'unnamed'),
              f"{s['baseline']['original']['unnamed_blobs']}→{s['baseline']['effective']['unnamed_blobs']}",
              f"{s['baseline']['original']['components_per_letter']:.4f}→{s['baseline']['effective']['components_per_letter']:.4f}") for w, s in waves.items()])
    t.table(out, ['Wave', 'ENSEMBLE_AB original→masked', 'PRESENCE original→masked'],
            [(w, *[gate_status(s['baseline']['original'], m)+' → '+gate_status(s['baseline']['effective'], m) for m in p.MODES]) for w, s in waves.items()])
    out += ['Full status transition matrices, per-line proposals/holds/labels, component histograms and affected-line counts are in the machine-readable outputs.', '',
            '## Frozen truth, eligibility and delta candidates', '',
            'S8a6 read 978 data cards; 976 resolved and two parliament UNKNOWN. Other deck words remain unread. '
            'Weights are copied exactly: `1/(saved card inclusion probability × wave cut probability)`, including the exact all-agree sampling fraction. '
            'No UNKNOWN or unread word is scored. Masked forms are compared with the original per-word deck options after S8a6 canonicalization (including elision aliases, preposed breathing and keraia). '
            '**Every new masked candidate is excluded from both sides of the paired score.** Original full-cut scores are shown separately so exclusions cannot masquerade as improvement. '
            'For unselected all-agree census words, the saved consensus is the sole implicit candidate. `delta_cards.jsonl` lists all new candidate word groups, '
            'with separate counts for existing deck, resolved cut, unread deck and words absent from the original deck; no cards are rendered.']
    t.table(out, ['Wave', 'Resolved', 'Delta all census / existing deck / resolved excluded / unread deck / no deck', 'Paired scored / matched-mask scored / fallback scored', 'Retained Σw / resolved Σw'],
            [(w, s['resolved'], ' / '.join(str(s['delta'][k]) for k in ('all_census', 'in_deck', 'resolved', 'unread_deck', 'no_deck')),
              f"{s['cohorts']['eligible_paired']['cards']} / {s['cohorts']['masked_only']['cards']} / {s['cohorts']['unmasked_fallback']['cards']}",
              f"{s['cohorts']['eligible_paired']['sum_weights']:.2f} / {s['resolved_weight']:.2f}") for w, s in waves.items()])
    out += ['Delta exclusion makes the paired result conditional on existing-candidate coverage. It does not estimate performance on all masked words. '
            'Weights are retained without redistribution. Physical evidence can change even when the named word form remains an existing candidate.', '',
            '## Presence precision and recall', '',
            'Primary **any** is physical saved detector `above OR below`, including unnamed ink. Breathing/accent/subscript/diaeresis are emitted family presence, '
            'so family results include naming behavior. `emitted_any` and physical `above`/`below` are also retained. '
            'S8a6 mark-blind casefolded base alignment, punctuation anchors, deterministic ties, union slots and gap FP/FN rules are reused unchanged. '
            'All loc/seg/clip cases remain eligible when truth is resolved and the form is not a delta.', '',
            'Cells are weighted % [95% interval], B = document-cluster percentile bootstrap (4,000 replicates, seed 20261017 + wave index); '
            'W = Wilson–Kish fallback for degenerate bootstrap, as in S8a6. Line-cluster intervals and valid-replicate counts are retained. '
            'Paired changes use the same resampled documents on both variants; intervals condition on the fixed eligible cohort and exclude reader uncertainty.']
    t.table(out, ['Wave', 'Original full-cut any P / R', 'Paired original any P / R', 'Paired masked any P / R', 'Paired ΔP / ΔR pp [95%]'],
            [(w, t.display(s['original_full']['any']['original']['precision'])+' / '+t.display(s['original_full']['any']['original']['recall']),
              *[t.display(s['cohorts']['eligible_paired']['presence']['any'][v]['precision'])+' / '+t.display(s['cohorts']['eligible_paired']['presence']['any'][v]['recall']) for v in ('original', 'masked')],
              change(s['cohorts']['eligible_paired']['presence']['any']['paired_change']['precision'])+' / '+change(s['cohorts']['eligible_paired']['presence']['any']['paired_change']['recall'])) for w, s in waves.items()])
    t.table(out, ['Wave', 'Family/zone', 'Original P / R [95%]', 'Masked P / R [95%]', 'Raw TP/FP/FN original→masked'],
            [(w, f, *[t.display(s['cohorts']['eligible_paired']['presence'][f][v]['precision'])+' / '+t.display(s['cohorts']['eligible_paired']['presence'][f][v]['recall']) for v in ('original', 'masked')],
              ' → '.join('/'.join(str(s['cohorts']['eligible_paired']['presence'][f][v]['counts'][k]['raw']) for k in ('TP', 'FP', 'FN')) for v in ('original', 'masked')))
             for w, s in waves.items() for f in (*t.FAMILY, 'emitted_any', 'above', 'below')])
    out += ['## Separate matched masks and nine original fallbacks', '',
            'This sensitivity removes all nine fallbacks from the masking estimate. Parliament has no matched-mask score.']
    t.table(out, ['Wave', 'Matched-mask eligible cards', 'Original any P / R', 'Masked any P / R', 'Δ recall pp [95%]'],
            [(w, s['cohorts']['masked_only']['cards'], *[t.display(s['cohorts']['masked_only']['presence']['any'][v]['precision'])+' / '+t.display(s['cohorts']['masked_only']['presence']['any'][v]['recall']) for v in ('original', 'masked')],
              change(s['cohorts']['masked_only']['presence']['any']['paired_change']['recall'])) for w, s in waves.items()])
    fallback = summary['fallbacks']
    t.table(out, ['Line ID', 'Wave', 'Reason', 'Resolved cards', 'loc / seg / clipped top / bottom', 'AB / PRESENCE status'],
            [(r['id'], r['wave'], r['reason'], r['resolved_cards'], ' / '.join(str(r['metrics'][k]) for k in ('localisation_unknown', 'segmentation_uncertain', 'clipped_top', 'clipped_bottom')),
              ' / '.join(r['gate'][m] for m in p.MODES)) for r in fallback])
    t.table(out, ['Fallback wave', 'Lines / letters', 'loc / seg / top / bottom', 'Eligible cards', 'Unchanged any P / R [95%]'],
            [(w, f"{s['fallback_baseline']['original']['lines']} / {s['fallback_baseline']['original'].get('letters', 0)}",
              ' / '.join(str(s['fallback_baseline']['original'].get(k, 0)) for k in ('localisation_unknown', 'segmentation_uncertain', 'clipped_top', 'clipped_bottom')),
              s['cohorts']['unmasked_fallback']['cards'], t.display(s['cohorts']['unmasked_fallback']['presence']['any']['original']['precision'])+' / '+t.display(s['cohorts']['unmasked_fallback']['presence']['any']['original']['recall'])) for w, s in waves.items() if w != 'parliament'])
    out += ['All nine fallback crops are byte-identical to originals: baseline, detector, gate decisions and eligible presence counts are therefore unchanged. '
            'Fallback subgroup weights are inherited S8a6 weights; its small-sample intervals are descriptive.', '', '## Per-wave verdict', '']
    for w, s in waves.items():
        cell = s['cohorts']['eligible_paired']['presence']['any']
        delta = cell['paired_change']['recall']
        lo, hi = delta['document_bootstrap95']
        if w == 'parliament':
            text = 'Unmasked reference only: no masking experiment or masking effect is established.'
        else:
            text = f"Eligible any recall {brief(cell['original']['recall'])}→{brief(cell['masked']['recall'])}, Δ {change(delta)} pp: no physical recall gain on this cohort."
        b = s['baseline']
        ab_kept = lambda variant: sum(b[variant]['gate']['ENSEMBLE_AB'].get(k, 0) for k in ('corrected', 'unchanged'))
        out.append(f"- **{w}:** {text} loc_unknown {b['original']['localisation_unknown']}→{b['effective']['localisation_unknown']}; "
                   f"seg_uncertain {b['original']['segmentation_uncertain']}→{b['effective']['segmentation_uncertain']}; "
                   f"clipping top/bottom {b['original']['clipped_top']}/{b['original']['clipped_bottom']}→{b['effective']['clipped_top']}/{b['effective']['clipped_bottom']}; "
                   f"AB kept {ab_kept('original')}→{ab_kept('effective')}; "
                   f"{s['delta']['resolved']} resolved words excluded for new candidates ({s['delta']['all_census']} total delta words).")
    out += ['', 'These DEV comparisons do not establish held-out generalization or causal geometric recovery. New masked candidates require a later, separately authorized adjudication.', '',
            '## Reproduction and validation', '',
            '`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -B docs/labelfix/spellcheck/S8_DEV/masked/run_s8a7.py`', '',
            'The equivalent runner imports the frozen detector/gate and the original S8a6 scoring functions; it never invokes the card builders. '
            'Cached masked records are hash-bound. Original per-word physical scores are reproduced exactly for every resolved word; full-cut P/R and confidence outputs are checked against S8a6. '
            'Validation also independently reaggregates all score cells from per-slot boolean presence, checks denominator equality, delta exclusion, fallback identity and protected file hashes.']
    out += ['', 'Validation command: replace `run_s8a7.py` above with `validate_s8a7.py`. '
            'The final [validation receipt](S8_DEV/masked/validation.json) records 240 source/family/cohort/wave cells and 23 independently rebuilt paired document intervals; '
            'the unchanged S8a6 validator also passes.']
    all_b = summary['ALL']['baseline']
    prs = '; '.join(w+' '+brief(s['cohorts']['eligible_paired']['presence']['any']['original']['precision'])+'/'+brief(s['cohorts']['eligible_paired']['presence']['any']['original']['recall'])+'→'+brief(s['cohorts']['eligible_paired']['presence']['any']['masked']['precision'])+'/'+brief(s['cohorts']['eligible_paired']['presence']['any']['masked']['recall']) for w, s in waves.items())
    kept = lambda v: sum(all_b[v]['gate']['ENSEMBLE_AB'].get(k, 0) for k in ('corrected', 'unchanged'))
    out += ['', f"S8a7 RESULT: masked 441/450; detector presence P/R original→masked by wave {prs}; loc_unknown {all_b['original']['localisation_unknown']}/{all_b['original']['letters']}→{all_b['effective']['localisation_unknown']}/{all_b['effective']['letters']}; seg_uncertain {all_b['original']['segmentation_uncertain']}/{all_b['original']['letters']}→{all_b['effective']['segmentation_uncertain']}/{all_b['effective']['letters']}; clipping top {all_b['original']['clipped_top']}→{all_b['effective']['clipped_top']}, bottom {all_b['original']['clipped_bottom']}→{all_b['effective']['clipped_bottom']}; AB kept {kept('original')}→{kept('effective')}; delta cards {summary['delta_total']}"]
    REPORT.write_text('\n'.join(out)+'\n')


def main():
    start = time.monotonic()
    head = subprocess.check_output(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=p.ROOT, text=True).strip()
    head_changes = subprocess.check_output(['git', '--no-optional-locks', 'diff', '--name-only', REQUESTED_HEAD, head], cwd=p.ROOT, text=True).splitlines()
    assert head_changes == ['docs/briefs/S8b_detector_iteration.md']
    before = protected()
    dump('protected_inputs.json', before)
    binding = p.load(p.E/'frozen_binding.json')
    # The baseline imported additional page modules during audit preparation.
    assert p.binding(tuple(binding['sources'])) == binding
    dump('frozen_binding.json', binding)
    ids = (p.OUT/'S8_DEV_ids.txt').read_text().split()
    sources = p.load(p.E/'sources.json')
    receipt, guard = p.load(p.MASK/'receipt.json'), p.load(p.MASK/'guard_note.json')
    assert receipt['status'] == 'completed' and receipt['completed_pages'] == receipt['selected_pages'] == 411
    assert p.sha(p.MASK/'lines.jsonl') == receipt['lines_sha256']
    staged = {r['id']: r for r in p.rows(p.MASK/'lines.jsonl')}
    assert set(staged) == {k for k in ids if sources[k]['wave'] != 'parliament'} and len(staged) == 450
    assert sum(r['mask_applied'] for r in staged.values()) == receipt['totals']['masked'] == 441
    assert C.Counter(r['failure_kind'] for r in staged.values() if not r['mask_applied']) == {'unmatched': 6, 'ambiguous': 3}
    assert guard['lines_evaluated'] == 450 and guard['lines_over_threshold'] == 0
    remote = json.loads(gzip.decompress((p.E/'remote.json.gz').read_bytes()))
    rr, request = p.load(p.E/'S8a3/remote_receipt.json'), p.load(p.E/'S8a3/request.json')
    assert p.sha(p.E/'remote.json.gz') == rr['remote_sha256'] == 'fae3140ea1e789ca817d3eec3ec71ae5d47774cf43503b9fa0b25aa54d64e4a2'
    import hashlib
    assert hashlib.sha256(json.dumps(request, sort_keys=True).encode()).hexdigest() == rr['request_sha256'] == remote['request_sha256']
    assert rr['complete'] and remote['complete'] and rr['error'] is None and remote['inference_runs'] == 0
    assert set(remote['runtime']) == set(remote['alignments']) == set(remote['ids']) == set(request['ids']) == set(ids)
    truth_rows = p.rows(p.E/'dev_truth.jsonl.gz')
    truth_summary = truth_rows[-1]
    assert p.sha(p.E/'dev_truth.jsonl.gz') == 'bbfba1509215d60517ab651324a44323f6a5cedd8378c97fdcadab48bc78a3ec'
    dump('mask_handoff.json', dict(receipt_sha256=p.sha(p.MASK/'receipt.json'), lines_sha256=p.sha(p.MASK/'lines.jsonl'),
                                  guard_note_sha256=p.sha(p.MASK/'guard_note.json'), guard=guard, totals=receipt['totals'], per_wave=receipt['per_wave']))
    original, effective, run = run_baseline(ids, sources, remote, staged, binding)
    per_line = []
    for k in ids:
        per_line.append(dict(id=k, wave=sources[k]['wave'], mask_applied=bool(staged.get(k, {}).get('mask_applied')),
            fallback_kind=staged.get(k, {}).get('failure_kind'),
            **{v: dict(metrics=r[k]['metrics'], gate={m: dict(status=r[k]['decisions'][m]['status'], label=r[k]['decisions'][m].get('label'),
                proposal=r[k]['modes'][m]['text'], holds=r[k]['decisions'][m]['hold_slots']) for m in p.MODES}) for v, r in (('original', original), ('effective', effective))}))
    write('baseline_per_line.jsonl', per_line)
    census, keys = p.rows(p.E/'word_census.jsonl'), p.load(p.OUT/'private/cards/items_key.json')
    comparisons, deltas, scores = score_words(census, keys, truth_rows, remote, sources, original, effective, staged)
    summary = dict(schema='s8a7-masked-detector-v1', waves={}, delta_total=len(deltas), delta_resolved=sum(r['truth_status'] == 'resolved' for r in deltas))
    for wi, w in enumerate((*WAVES, 'ALL')):
        lids = [k for k in ids if w == 'ALL' or sources[k]['wave'] == w]
        baseline = {v: aggregate([r[k] for k in lids]) for v, r in (('original', original), ('effective', effective))}
        transitions = {m: dict(C.Counter(original[k]['decisions'][m]['status']+'→'+effective[k]['decisions'][m]['status'] for k in lids)) for m in p.MODES}
        if w == 'ALL':
            summary['ALL'] = dict(baseline=baseline, gate_transitions=transitions)
            continue
        rr = [r for r in scores if r['wave'] == w]
        eligible = [r for r in rr if r['scored']]
        dd = [r for r in deltas if r['wave'] == w]
        ws = dict(lines=len(lids), matched_masks=sum(staged.get(k, {}).get('mask_applied', False) for k in lids),
            changed_lines=sum(bool(staged.get(k, {}).get('native_changed_pixels')) for k in lids), baseline=baseline, gate_transitions=transitions,
            fallback_baseline={v: aggregate([r[k] for k in lids if staged.get(k, {}).get('failure_kind')]) for v, r in (('original', original), ('effective', effective))},
            resolved=len(rr), resolved_weight=sum(r['weight'] for r in rr),
            delta=dict(all_census=len(dd), in_deck=sum(r['in_frozen_deck'] for r in dd), resolved=sum(r['truth_status'] == 'resolved' for r in dd),
                       unread_deck=sum(r['truth_status'] == 'unadjudicated' for r in dd), no_deck=sum(not r['in_frozen_deck'] for r in dd)), cohorts={}, original_full={})
        # Preserve the original full-cut comparator and verify S8a6 intervals, not only ratios.
        for family in t.KINDS:
            data = {}
            for metric, error in (('precision', 'FP'), ('recall', 'FN')):
                n = lambda r: r['presence']['original']['counts'][family]['TP']
                data[metric] = t.estimate(rr, n, lambda r: n(r)+r['presence']['original']['counts'][family][error], t.SEED+wi)
                assert data[metric] == truth_summary['waves'][w]['presence']['detector_original'][family][metric]
            ws['original_full'][family] = dict(original=data)
        for name, cohort in (('eligible_paired', eligible), ('masked_only', [r for r in eligible if r['mask_applied']]),
                             ('unmasked_fallback', [r for r in eligible if r['fallback_kind']])):
            ws['cohorts'][name] = dict(cards=len(cohort), sum_weights=sum(r['weight'] for r in cohort),
                truth_letters=sum(sum(t.letter(a) for a in t.tokens(r['truth'])) for r in cohort),
                presence={f: estimate_pair(cohort, f, t.SEED+wi) for f in t.KINDS})
        summary['waves'][w] = ws
        print(f"S8a7 scored {w}: {len(eligible)}/{len(rr)} paired, {len(dd)} delta census words", flush=True)
    summary['fallbacks'] = [dict(id=k, wave=sources[k]['wave'], reason=staged[k]['failure_kind'], metrics=original[k]['metrics'],
        resolved_cards=sum(r['line_id'] == k for r in scores), gate={m: original[k]['decisions'][m]['status'] for m in p.MODES}) for k in ids if staged.get(k, {}).get('failure_kind')]
    for name, kk in (('nonparliament_baseline', list(staged)), ('matched_baseline', [k for k in staged if staged[k]['mask_applied']])):
        summary[name] = {v: aggregate([source[k] for k in kk]) for v, source in (('original', original), ('effective', effective))}
    dump('summary.json', summary)
    report(summary, head, run)
    assert protected() == before
    assert p.binding(tuple(binding['sources'])) == binding
    assert subprocess.check_output(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=p.ROOT, text=True).strip() == head
    outputs = {str(x.relative_to(DEST)): p.sha(x) for x in sorted(DEST.rglob('*')) if x.is_file() and x.name not in ('receipt.json', 'validation.json')}
    dump('receipt.json', dict(schema='s8a7-receipt-v1', status='PASS', head=head, network=False, reader_inference_runs=0,
         requested_head=REQUESTED_HEAD, externally_added_paths=head_changes,
         frozen_detector_lines=441, reused_fallback_originals=9, parliament_originals=150, run=run,
         protected_files=len(before), protected_unchanged=True, original_scores_reproduced=976, original_full_metric_intervals_reproduced=80,
         delta_words=len(deltas), delta_resolved_excluded=summary['delta_resolved'], paired_scored=sum(r['scored'] for r in scores),
         seconds=time.monotonic()-start, output_sha256=outputs, report_sha256=p.sha(REPORT)))
    print(REPORT.read_text().splitlines()[-1], flush=True)


if __name__ == '__main__':
    main()
