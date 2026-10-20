"""Analysis-only NFD label-change census of verified SF6c releases (stdlib only).

No policy imports, recomposition, model execution, network, or source writes.
Edit counts are codepoint insertions/deletions; an alias substitution counts
once. Character classes describe label orthography, not adjudicated print truth.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import time
import unicodedata as ud
import uuid

try:
    from . import l1c_census as c
except ImportError:
    import l1c_census as c

ALIASES = "'’ʼ᾽᾿"
KERAIA = '\u0374\u0384\u02b9'
QUOTES = '"“”„‟«»‹›‘❝❞〝〞〟'
CLASSES = ('combining_mark', 'numeral_keraia', 'elision_apostrophe', 'quote',
           'other_mark', 'base_letter', 'whitespace', 'other')
METRICS = ('deletions_by_class', 'single_source_deletions_by_class',
           'shared_deletions_by_class', 'insertions_by_class')
NUMERALS = 'ΑΒΓΔΕϚϜΖΗΘΙΚΛΜΝΞΟΠϞΡΣΤΥΦΧΨΩϠ'
VOWELS = 'αεηιουω'
SF6_CLASSES = ('mark', 'apostrophe', 'quote', 'keraia', 'other')
SF6_PREFIX = 'sf6:deletion_needs_two_positive_absences:'
AUDIT_LIST = 'real_mark_correction_lines.jsonl'


def letter(ch):
    return ch.isalpha() and ch not in ALIASES + KERAIA


def adjacent(text, pos, direction):
    pos += direction
    while 0 <= pos < len(text) and ud.combining(text[pos]):
        pos += direction
    return text[pos] if 0 <= pos < len(text) else ''


def numeral_apostrophe(text, pos):
    """Explicit keraia always wins; apostrophe after an uppercase numeral token.

    Bare lowercase μ'/κ' remain elisions. Without print truth a lowercase
    letter followed by an ASCII apostrophe is intrinsically ambiguous; this
    census does not silently count all short Greek words as numerals.
    """
    before = text[:pos]
    token = re.search(r'[^\W_]+$', before, re.UNICODE)
    token = token.group() if token else ''
    return bool(token and (token.isdecimal() or all(ud.category(x) == 'Nl' for x in token)
                or (len(token) <= 3 and all(x in NUMERALS for x in token))))


def character_classes(text):
    result = []
    # A pair of ASCII/curly single quotes enclosing a word/phrase is a quote.
    paired = set()
    for match in re.finditer(r"(?<!\w)(['‘])([^\n]+?)(['’])(?!\w)", text):
        paired.update((match.start(1), match.start(3)))
    for i, ch in enumerate(text):
        prev, nxt = adjacent(text, i, -1), adjacent(text, i, 1)
        if ch in KERAIA or (i not in paired and ch in ALIASES and numeral_apostrophe(text, i)):
            kind = 'numeral_keraia'
        elif i in paired or ch in QUOTES:
            kind = 'quote'
        elif ch in ALIASES:
            final = bool(prev and letter(prev) and not (nxt and letter(nxt)))
            # Word-initial elision aliases such as ᾿στὸν -> 'στὸν. Spacing
            # breathings before capitals/vowels are deliberately not aliases.
            initial = bool(nxt and letter(nxt) and not nxt.isupper() and nxt not in VOWELS
                           and not (prev and letter(prev)))
            opening_quote = bool(ch in "'’ʼ" and nxt and letter(nxt)
                                 and not (prev and letter(prev)))
            kind = 'elision_apostrophe' if final or initial else 'quote' if opening_quote else 'other_mark'
        elif ud.combining(ch):
            kind = 'combining_mark'
        elif letter(ch):
            kind = 'base_letter'
        elif ch.isspace():
            kind = 'whitespace'
        elif ud.category(ch)[0] in 'MPS':
            kind = 'other_mark'
        else:
            kind = 'other'
        result.append(kind)
    return result


def tokens(text):
    """Return NFD bytes, classes, alias-folded comparison and letter anchors."""
    text = ud.normalize('NFD', text)
    kinds = character_classes(text)
    folded = ''.join('’' if k == 'elision_apostrophe' else ch for ch, k in zip(text, kinds))
    boundary, occurrence, anchors = 0, Counter(), []
    for ch, kind, folded_ch in zip(text, kinds, folded):
        if kind == 'base_letter':
            boundary += 1
        key = (boundary, folded_ch)
        anchors.append((key, occurrence[key]))
        occurrence[key] += 1
    return text, kinds, folded, anchors


def diff_line(original, released, recogniser):
    old, ok, of, oa = tokens(original)
    new, nk, nf, na = tokens(released)
    rec, rk, rf, ra = tokens(recogniser)
    # Source support must be measured in the same letter domain, never guessed.
    skeleton = lambda text, kinds: ''.join(ch for ch, k in zip(text, kinds) if k == 'base_letter')
    if not skeleton(old, ok) == skeleton(new, nk) == skeleton(rec, rk):
        raise ValueError('unaligned corrected-line letter skeleton')
    rec_anchors = set(ra)
    old_elisions = {a[0][0] for a, k in zip(oa, ok) if k == 'elision_apostrophe'}
    rec_elisions = {a[0][0] for a, k in zip(ra, rk) if k == 'elision_apostrophe'}
    new_elisions = {a[0][0] for a, k in zip(na, nk) if k == 'elision_apostrophe'}
    result = {m: Counter() for m in METRICS}
    result.update(elision_alias=0, real_mark_change_edits=0, diff_hunks=0,
                  consensus_elision_deleted=len((old_elisions & rec_elisions) - new_elisions))
    for tag, i, j, a, b in SequenceMatcher(None, of, nf, autojunk=False).get_opcodes():
        if tag == 'equal':
            result['elision_alias'] += sum(old[x] != new[y] for x, y in zip(range(i, j), range(a, b)))
            continue
        result['diff_hunks'] += 1
        for x in range(i, j):
            kind = ok[x]
            result['deletions_by_class'][kind] += 1
            support = 'shared' if oa[x] in rec_anchors else 'single_source'
            result[support + '_deletions_by_class'][kind] += 1
            result['real_mark_change_edits'] += kind == 'combining_mark'
        for x in range(a, b):
            result['insertions_by_class'][nk[x]] += 1
            result['real_mark_change_edits'] += nk[x] == 'combining_mark'
    # Every edited codepoint is represented; alias-only lines are not mark corrections.
    result['real_mark_correction_line'] = bool(result['real_mark_change_edits'])
    result['any_single_source_deletion'] = bool(sum(result['single_source_deletions_by_class'].values()))
    return result


def empty():
    return dict(total_lines=0, corrected_status_lines=0, real_mark_correction_lines=0,
                sf6_deletion_held_lines=0, sf6_move_proposal_lines=0,
                sf6_move_exceptions_applied=0, sf6_move_lines_applied=0,
                sf6_deletion_holds_by_class={k: dict(lines=0, checks=0, example_ids=[]) for k in SF6_CLASSES},
                corrected_lines_with_any_single_source_deletion=0,
                real_mark_correction_lines_with_any_single_source_deletion=0, alias_only_status_lines=0,
                lines_per_class=Counter(), edits_per_class=Counter(), examples={},
                **{m: {k: dict(lines=0, edits=0, example_ids=[]) for k in CLASSES} for m in METRICS})


def examples(target, ids):
    return sorted(set(target) | set(ids))[:20]


def add(bucket, row, change):
    bucket['total_lines'] += 1
    bucket['alias_only_status_lines'] += bool(row.get('alias_only') and row['status'] == 'unchanged')
    holds = Counter(s['detail'][len(SF6_PREFIX):] for s in row.get('hold_slots', [])
                    if s['detail'].startswith(SF6_PREFIX))
    blocked = Counter(x['category'] for x in row.get('deletion_checks', []) if not x['allowed'])
    if holds != blocked or any(k not in SF6_CLASSES for k in holds):
        raise ValueError('SF6 deletion checks / hold reasons mismatch')
    if holds and row['status'] != 'hold':
        raise ValueError('blocked SF6 deletion released')
    bucket['sf6_deletion_held_lines'] += bool(holds)
    for kind, count in holds.items():
        b = bucket['sf6_deletion_holds_by_class'][kind]
        b['lines'] += 1; b['checks'] += count
        b['example_ids'] = examples(b['example_ids'], [row['line_id']])
    moves = [x for x in row.get('deletion_checks', []) if x.get('operation') == 'MOVE']
    if any(not x['allowed'] or x['reason'] is not None for x in moves):
        raise ValueError('invalid saved MOVE exception')
    bucket['sf6_move_proposal_lines'] += bool(moves)
    if row['status'] == 'corrected':
        bucket['sf6_move_exceptions_applied'] += len(moves)
        bucket['sf6_move_lines_applied'] += bool(moves)
    if change is None:
        return
    lid = row['line_id']
    bucket['corrected_status_lines'] += 1
    bucket['real_mark_correction_lines'] += change['real_mark_correction_line']
    bucket['corrected_lines_with_any_single_source_deletion'] += change['any_single_source_deletion']
    bucket['real_mark_correction_lines_with_any_single_source_deletion'] += (change['real_mark_correction_line'] and change['any_single_source_deletion'])
    # Orthogonal edit classes: real mark edits, alias substitutions, consensus
    # elisions deleted, then all deletion/insertion character-class marginals.
    for key in ('real_mark_change_edits', 'elision_alias', 'consensus_elision_deleted'):
        count = change[key]
        bucket['edits_per_class'][key] += count
        bucket['lines_per_class'][key] += bool(count)
        if count:
            bucket['examples'][key] = examples(bucket['examples'].get(key, []), [lid])
    for metric in METRICS:
        for kind, count in change[metric].items():
            if not count:
                continue
            b = bucket[metric][kind]
            b['lines'] += 1
            b['edits'] += count
            b['example_ids'] = examples(b['example_ids'], [lid])


def code_binding():
    return {Path(p).name: c.sha256(p) for p in (__file__, c.__file__)}


def shard(task):
    spec, out, binding = task
    dest = Path(out) / 'partials' / f'shard-{spec["shard"]:05d}'
    rp = dest / 'receipt.json'
    if rp.exists():
        r = c.load(rp)
        if (r.get('complete') is not True or r['binding'] != binding or r['input'] != spec
                or r['counts_sha256'] != c.sha256(dest / 'counts.json')
                or r['audit_list_sha256'] != c.sha256(dest / AUDIT_LIST)):
            raise ValueError('changed deletion-census partial')
        return r
    directory = Path(spec['directory'])
    records = {r['id']: r for r in c.rows(directory / 'selection.jsonl')}
    if len(records) != spec['lines']:
        raise ValueError('selection population mismatch')
    groups = defaultdict(empty)
    audit_rows = []
    for mode in c.MODES:
        seen, statuses = set(), Counter()
        for row in c.rows(directory / 'release' / f'overlay_{mode.lower()}.jsonl.gz'):
            lid = row['line_id']
            if lid in seen or lid not in records:
                raise ValueError('overlay population mismatch')
            seen.add(lid)
            statuses[row['status']] += 1
            record = records[lid]
            if row['status'] != 'out_of_scope' and 'deletion_checks' not in row:
                raise ValueError('missing SF6 deletion checks')
            if hashlib.sha256(record['label'].encode()).hexdigest() != row['original_label_sha256']:
                raise ValueError('original v2 label binding mismatch')
            change = None
            if row['status'] == 'corrected':
                sources = {x['evidence']['recogniser_text'] for x in row['changes']}
                if len(sources) != 1 or 'label' not in row:
                    raise ValueError('missing/ambiguous recogniser source')
                change = diff_line(record['label'], row['label'], sources.pop())
                if (ud.normalize('NFD', record['label']) == ud.normalize('NFD', row['label'])
                        or not (sum(change[m].total() for m in ('deletions_by_class', 'insertions_by_class'))
                                + change['elision_alias'])):
                    raise ValueError('corrected status has no classified edits')
            elif row['status'] == 'unchanged' and row['label'] != record['label']:
                raise ValueError('unchanged label changed')
            if change and change['real_mark_correction_line']:
                audit_rows.append(dict(line_id=lid, wave=record['wave'], mode=mode))
            for wave in ('*', record['wave']):
                add(groups[c.canonical([mode, wave])], row, change)
        if seen != set(records) or statuses != Counter(c.load(directory / 'release' / f'release_{mode.lower()}.json')['counts_by_status']):
            raise ValueError('shard line/status mismatch')
    c.atomic_json(dest / 'counts.json', dict(groups))
    write_audit_list(dest / AUDIT_LIST, sorted(audit_rows, key=lambda r: (r['mode'], r['line_id'])))
    result = dict(complete=True, input=spec, binding=binding, counts_sha256=c.sha256(dest / 'counts.json'),
                  audit_list_sha256=c.sha256(dest / AUDIT_LIST), audit_list_rows=len(audit_rows))
    c.atomic_json(rp, result)
    return result


def merge_bucket(target, source):
    for key in ('total_lines', 'corrected_status_lines', 'real_mark_correction_lines',
                'corrected_lines_with_any_single_source_deletion',
                'real_mark_correction_lines_with_any_single_source_deletion', 'alias_only_status_lines',
                'sf6_deletion_held_lines', 'sf6_move_proposal_lines',
                'sf6_move_exceptions_applied', 'sf6_move_lines_applied'):
        target[key] += source[key]
    for kind, b in source['sf6_deletion_holds_by_class'].items():
        dest = target['sf6_deletion_holds_by_class'][kind]
        for key in ('lines', 'checks'):
            dest[key] += b[key]
        dest['example_ids'] = examples(dest['example_ids'], b['example_ids'])
    for key in ('lines_per_class', 'edits_per_class'):
        target[key].update(source[key])
    for key, ids in source['examples'].items():
        target['examples'][key] = examples(target['examples'].get(key, []), ids)
    for metric in METRICS:
        for kind, source_class in source[metric].items():
            b = target[metric][kind]
            for key in ('lines', 'edits'):
                b[key] += source_class[key]
            b['example_ids'] = examples(b['example_ids'], source_class['example_ids'])


def write_audit_list(path, records):
    path = Path(path)
    temp = path.with_name(path.name + '.partial-' + uuid.uuid4().hex)
    with temp.open('x', encoding='utf-8') as f:
        for record in records:
            f.write(c.canonical(record) + '\n')
    temp.replace(path)


def markdown(result):
    lines = ['# L1R3 deletion / change census', '',
             'Analysis only. The reported correction count is real mark-correction lines:',
             'corrected-status lines with at least one combining-mark insertion or deletion.',
             'NFD difflib, autojunk=False. Mark replacements count two codepoint edits;',
             'an elision alias substitution counts once. Classes and source support describe',
             'labels, not printed truth. Class marginals overlap real-mark totals.', '',
             'Word-final and lowercase consonant-initial elision aliases are folded for',
             "comparison (including ᾿στὸν → 'στὸν). Spacing breathings before capitals/vowels",
             'are not folded. Explicit U+0374/U+0384/U+02B9 and apostrophes after uppercase',
             'Greek numeral tokens, decimal tokens or Unicode numeral letters are keraia.',
             'Lowercase ASCII-apostrophe numeral/elision ambiguity needs print adjudication.',
             'Single-source means original-label codepoint/alias atom absent from recogniser',
             'at the same letter boundary and occurrence. All deleted classes are counted.', '']
    lines += ['SF6 deletion HOLD classes count each line once per class; checks count atoms.',
              'MOVE applied counts only actual corrected releases. Proposal lines may still HOLD',
              'on another veto. The full audit population is real_mark_correction_lines.jsonl',
              '(line_id, wave, mode); alias-only and punctuation-only changes are excluded.', '']
    for mode, data in result.items():
        lines += [f'## {mode}', '', '| Wave | Lines | Corrected status | Real mark-correction lines | Real mark lines with single-source deletion | Share of real mark-correction lines |',
                  '|---|---:|---:|---:|---:|---:|']
        groups = [('ALL', data['overall']), *data['per_wave'].items()]
        for wave, b in groups:
            share = b['share_real_mark_correction_lines_with_any_single_source_deletion']
            lines.append(f'| {wave} | {b["total_lines"]} | {b["corrected_status_lines"]} | {b["real_mark_correction_lines"]} | {b["real_mark_correction_lines_with_any_single_source_deletion"]} | {share:.6%} |')
        for wave, b in groups:
            lines += ['', f'### SF6 {wave}', '',
                      f'Deletion HOLD lines: {b["sf6_deletion_held_lines"]}; MOVE proposal lines: {b["sf6_move_proposal_lines"]}; '
                      f'MOVE applied: {b["sf6_move_exceptions_applied"]} checks / {b["sf6_move_lines_applied"]} lines.', '',
                      '| Deletion HOLD class | Lines | Checks | Example IDs |', '|---|---:|---:|---|']
            for kind, counts in b['sf6_deletion_holds_by_class'].items():
                lines.append(f'| {kind} | {counts["lines"]} | {counts["checks"]} | {", ".join(counts["example_ids"])} |')
            lines += ['', f'### {wave}', '', '| Class | Lines | Edits | Example IDs (up to 20) |', '|---|---:|---:|---|']
            for key in ('real_mark_change_edits', 'elision_alias', 'consensus_elision_deleted'):
                lines.append(f'| {key} | {b["lines_per_class"].get(key, 0)} | {b["edits_per_class"].get(key, 0)} | {", ".join(b["examples"].get(key, []))} |')
            for metric in METRICS:
                for kind, counts in b[metric].items():
                    lines.append(f'| {metric}/{kind} | {counts["lines"]} | {counts["edits"]} | {", ".join(counts["example_ids"])} |')
    return '\n'.join(lines) + '\n'


def census(root, out, workers=8):
    started = time.monotonic()
    root, out = Path(root).resolve(), Path(out).resolve()
    if workers < 1 or root == out or root in out.parents or out in root.parents:
        raise ValueError('positive workers and disjoint input/output required')
    verification, specs, l1r = c.verify_inputs(root, min(workers, 8))
    if verification['policy']['schema'] != 'sf6-release-v1':
        raise ValueError('SF6c input required')
    binding = dict(schema='l1r3-change-census-v1', input_hashes_sha256=c.digest(verification['hashes']), code_sha256=code_binding())
    if (out / 'binding.json').exists() and c.load(out / 'binding.json') != binding:
        raise ValueError('change-census restart binding changed')
    c.atomic_json(out / 'binding.json', binding)
    c.atomic_json(out / 'input_verification.json', verification)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        partials = list(pool.map(shard, [(s, str(out), binding) for s in specs]))
    groups = defaultdict(empty)
    for r in partials:
        for key, b in c.load(out / 'partials' / f'shard-{r["input"]["shard"]:05d}' / 'counts.json').items():
            merge_bucket(groups[key], b)
    for mode in c.MODES:
        overall = groups[c.canonical([mode, '*'])]
        if overall['corrected_status_lines'] != l1r['counts'][mode.lower()]['corrected'] or overall['total_lines'] != verification['lines']:
            raise ValueError('aggregate population mismatch')
        for wave in c.WAVES:
            groups[c.canonical([mode, wave])]
        coverage = c.load(root / 'release' / f'release_{mode.lower()}.json')['coverage_per_wave']
        for wave, b in coverage.items():
            observed = groups[c.canonical([mode, wave])]
            if observed['total_lines'] != b['total'] or observed['corrected_status_lines'] != b['corrected']:
                raise ValueError('wave population mismatch')
    for b in groups.values():
        b['share_corrected_status_lines_with_any_single_source_deletion'] = (
            b['corrected_lines_with_any_single_source_deletion'] / b['corrected_status_lines'] if b['corrected_status_lines'] else 0)
    for b in groups.values():
        b['share_real_mark_correction_lines_with_any_single_source_deletion'] = (
            b['real_mark_correction_lines_with_any_single_source_deletion'] / b['real_mark_correction_lines'] if b['real_mark_correction_lines'] else 0)
    result = {m: dict(overall=groups[c.canonical([m, '*'])],
                      per_wave={json.loads(k)[1]: b for k, b in sorted(groups.items()) if json.loads(k)[0] == m and json.loads(k)[1] != '*'}) for m in c.MODES}
    audit_counts = Counter(); audit_seen = set()
    def audit_population():
        for partial in partials:
            path = out / 'partials' / f'shard-{partial["input"]["shard"]:05d}' / AUDIT_LIST
            if c.sha256(path) != partial['audit_list_sha256']:
                raise ValueError('changed real mark-correction partial')
            n = 0
            for row in c.rows(path):
                key = (row['mode'], row['line_id'])
                if key in audit_seen or row['mode'] not in c.MODES:
                    raise ValueError('duplicate/invalid real mark-correction audit row')
                audit_seen.add(key); n += 1
                audit_counts[row['mode'], '*'] += 1
                audit_counts[row['mode'], row['wave']] += 1
                yield row
            if n != partial['audit_list_rows']:
                raise ValueError('real mark-correction partial count mismatch')
    write_audit_list(out / AUDIT_LIST, audit_population())
    if any(audit_counts[tuple(json.loads(key))] != b['real_mark_correction_lines'] for key, b in groups.items()):
        raise ValueError('real mark-correction audit population mismatch')
    with ThreadPoolExecutor(max_workers=min(workers, 8)) as pool:
        for name, got in pool.map(lambda p: (p, c.sha256(p)), verification['hashes']):
            if got != verification['hashes'][name]:
                raise ValueError('input changed during change census')
    if code_binding() != binding['code_sha256']:
        raise ValueError('census code changed')
    consensus_deleted = sum(b['overall']['edits_per_class']['consensus_elision_deleted'] for b in result.values())
    c.atomic_json(out / 'CHANGES.json', dict(schema='l1r3-changes-v1', modes=result,
                                          real_mark_correction_list=AUDIT_LIST,
                                          real_mark_correction_list_rows=len(audit_seen),
                                          real_mark_correction_unique_lines=len({lid for mode, lid in audit_seen}),
                                          consensus_elision_deleted=consensus_deleted,
                                          consensus_elision_zero=consensus_deleted == 0))
    (out / 'CHANGES.md').write_text(markdown(result), encoding='utf-8')
    receipt = dict(schema='l1r3-changes-receipt-v1', complete=consensus_deleted == 0,
                   analysis_only=True, binding=binding, lines=verification['lines'], shards=len(specs),
                   detector_runs=0, reader_runs=0, gate_runs=0, consensus_elision_deleted=consensus_deleted,
                   elapsed_seconds=time.monotonic()-started,
                   outputs={p: c.sha256(out / p) for p in ('CHANGES.json', 'CHANGES.md', 'binding.json', 'input_verification.json', AUDIT_LIST)},
                   partial_receipts={f'partials/shard-{r["input"]["shard"]:05d}/receipt.json': c.sha256(out / 'partials' / f'shard-{r["input"]["shard"]:05d}' / 'receipt.json') for r in partials})
    c.atomic_json(out / 'receipt.json', receipt)
    if consensus_deleted:
        raise ValueError('consensus elision deletion: census failed zero gate')
    print('L1R3_CHANGES_COMPLETE ' + c.canonical(receipt), flush=True)
    return receipt


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--workers', type=int, default=8)
    a = ap.parse_args()
    census(a.input_dir, a.out, a.workers)
