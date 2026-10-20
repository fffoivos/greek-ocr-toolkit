"""Offline S8a6 analysis of the frozen DEV deck; no runtime imports or inference."""
from __future__ import annotations

import collections as C
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import unicodedata as U

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DEV = ROOT / 'docs/labelfix/spellcheck/S8_DEV'
REPORT = DEV.parent / 'S8a6_DEV_TRUTH.md'
WAVES = ('parliament', 'round1', 'round2', 'mixed', 'vouli')
SOURCES = ('google', 'r1_A', 'detector_original', 'frozen_AB')
FAMILY = dict(breathing=set('̓̔'), accent=set('́̀͂'), subscript=set('ͅ'), diaeresis=set('̈'))
KINDS = ('any', *FAMILY, 'emitted_any', 'above', 'below')
ELISION = "'’ʼ᾽᾿"
DEFECT = 'item_fa47d3102d8d11bd'
REPS, SEED = 4000, 20261017


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def lines(p):
    return [json.loads(s) for s in Path(p).read_text().splitlines() if s.strip()]


def frozen():
    return {str(p.relative_to(ROOT)): sha(p) for folder in ('cards', 'private/cards')
            for p in sorted((DEV / folder).rglob('*')) if p.is_file()}


def canonical(s):
    if s is None or s.upper() in ('UNREADABLE', 'UNKNOWN'):
        return None
    if s == '∅':
        return ''
    # Spacing psili BEFORE a capital is a breathing, never an elision atom.
    def preposed(m):
        base = U.normalize('NFD', m[1])
        return base[0] + '̓' + base[1:] if m[1].isupper() else m[0]
    s = re.sub('᾿(.)', preposed, s)
    chunks = re.split('([ʹ΄])', s)  # retain printed numeral keraia identities
    for j, t in enumerate(chunks):
        if t in ('ʹ', '΄'):
            continue
        t = U.normalize('NFD', t)
        out = []
        for i, ch in enumerate(t):
            prev = i - 1
            while prev >= 0 and U.category(t[prev]).startswith('M'):
                prev -= 1
            final = i + 1 == len(t) or not t[i + 1].isalpha()
            greek = prev >= 0 and 'GREEK' in U.name(t[prev], '') and t[prev].isalpha()
            out.append('’' if ch in ELISION and greek and final else ch)
        chunks[j] = ''.join(out)
    return ''.join(chunks)


def tokens(s):
    out = []
    for ch in canonical(s):
        if U.category(ch).startswith('M') and out:
            out[-1]['marks'] += ch
        else:
            out.append(dict(base=ch, marks=''))
    return out


def letter(t):
    return t['base'].isalpha() and t['base'] not in ELISION + 'ʹ΄ʹ´'


def align(a, b):
    """Mark-blind unit-cost base alignment, diagonal then delete then insert ties."""
    a, b = [t['base'].casefold() for t in a], [t['base'].casefold() for t in b]
    n, m = len(a), len(b)
    dp = [list(range(m + 1))] + [[i] + [0] * m for i in range(1, n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dp[i][j] = min(dp[i-1][j-1] + (a[i-1] != b[j-1]), dp[i-1][j] + 1, dp[i][j-1] + 1)
    i, j, path = n, m, []
    while i or j:
        if i and j and dp[i][j] == dp[i-1][j-1] + (a[i-1] != b[j-1]):
            path.append((i-1, j-1)); i -= 1; j -= 1
        elif i and dp[i][j] == dp[i-1][j] + 1:
            path.append((i-1, None)); i -= 1
        else:
            path.append((None, j-1)); j -= 1
    return path[::-1]


def features(t):
    marks = set(t['marks']) if t else set()
    f = {k: bool(marks & chars) for k, chars in FAMILY.items()}
    return dict(f, any=bool(marks), emitted_any=bool(marks), above=bool(marks-set('ͅ')), below=f['subscript'])


def vote(r, options):
    if r['answer'] in options:
        return canonical(options[r['answer']])
    assert r['answer'] in ('none of these', 'unreadable'), r
    return canonical(r.get('printed')) if r['answer'] == 'none of these' else None


def wilson(p, n):
    if not n:
        return None
    z = 1.959963984540054
    d = 1 + z*z/n
    mid = (p + z*z/(2*n))/d
    half = z*math.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
    return [max(0., mid-half), min(1., mid+half)]


def estimate(rows, numer, denom, seed):
    if not rows:
        return dict(value=None, raw_num=0, raw_den=0, weighted_num=0., weighted_den=0., ci=None)
    w = np.array([r['weight'] for r in rows])
    a = np.array([numer(r) for r in rows], dtype=float)
    b = np.array([denom(r) for r in rows], dtype=float)
    num, den = float(w@a), float(w@b)
    out = dict(raw_num=int(a.sum()), raw_den=int(b.sum()), weighted_num=num, weighted_den=den,
               value=num/den if den else None, ci=None)
    if not den:
        return out
    # Each contributing binary event inherits its card weight; this is not a count of independent cards.
    neff = den*den / float((w*w)@b)
    out.update(effective_event_n=neff, wilson95=wilson(num/den, neff))
    for level in ('document', 'line'):
        ids = sorted({r['line_id'].split('-p')[0] if level == 'document' else r['line_id'] for r in rows})
        ix = {k: i for i, k in enumerate(ids)}
        matrix = np.zeros((len(ids), 2))
        for r, wa, wb in zip(rows, w*a, w*b):
            k = r['line_id'].split('-p')[0] if level == 'document' else r['line_id']
            matrix[ix[k]] += (wa, wb)
        rng = np.random.default_rng(seed)
        counts = rng.multinomial(len(ids), np.full(len(ids), 1/len(ids)), size=REPS)
        totals = counts @ matrix
        valid = totals[:, 1] > 0
        ratios = totals[valid, 0] / totals[valid, 1]
        out[level+'_clusters'] = len(ids)
        out[level+'_bootstrap_valid'] = int(valid.sum())
        out[level+'_bootstrap95'] = np.quantile(ratios, [.025, .975]).tolist() if len(ratios) else None
    interval = out['document_bootstrap95']
    degenerate = interval is None or interval[1]-interval[0] < 1e-12
    out.update(ci=out['wilson95'] if degenerate else interval, ci_method='Wilson-Kish' if degenerate else 'document-bootstrap')
    return out


def score_presence(row, source, serial):
    truth, pred = tokens(row['truth']), tokens(row['forms'][source])
    source_letters = [t for t in pred if letter(t)]
    physical = source == 'detector_original'
    if physical:
        assert ''.join(s['base'] for s in serial) == ''.join(t['base'] for t in source_letters), row['id']
    index = {i: j for j, i in enumerate(k for k, t in enumerate(pred) if letter(t))}
    counts = {k: dict(TP=0, FP=0, FN=0, TN=0) for k in KINDS}
    slots, failures = [], []
    for i, j in align(truth, pred):
        t = truth[i] if i is not None and letter(truth[i]) else None
        p = pred[j] if j is not None and letter(pred[j]) else None
        if t is None and p is None:
            continue
        tf, pf = features(t), features(p)
        s = serial[index[j]] if physical and p else None
        if physical:
            ev = s.get('evidence', {}) if s else {}
            pf.update(any=bool(ev.get('above') or ev.get('below')), above=bool(ev.get('above')), below=bool(ev.get('below')))
        result = {k: 'TP' if tf[k] and pf[k] else 'FP' if pf[k] else 'FN' if tf[k] else 'TN' for k in KINDS}
        for k, value in result.items():
            counts[k][value] += 1
        slot = dict(truth_index=i if t else None, prediction_index=j if p else None,
                    truth=t, prediction=p, truth_presence=tf, prediction_presence=pf, results=result)
        if physical:
            slot['detector_slot'] = s
            classes = []
            for zone in ('above', 'below'):
                if tf[zone] != pf[zone]:
                    classes.append(('missing_' if tf[zone] else 'false_')+zone+'_presence')
            for family in FAMILY:
                zone = 'below' if family == 'subscript' else 'above'
                if tf[zone] and pf[zone] and tf[family] != pf[family]:
                    classes.append(('missing_' if tf[family] else 'extra_')+family+'_name_with_ink')
                a = set(t['marks']) & FAMILY[family] if t else set()
                b = set(p['marks']) & FAMILY[family] if p else set()
                if a and b and a != b:
                    classes.append('wrong_'+family+'_identity')
            for cls in classes:
                failures.append(dict(failure_class=cls, truth_index=slot['truth_index'], prediction_index=slot['prediction_index']))
        slots.append(slot)
    return dict(counts=counts, slots=slots), failures


def display(x):
    if x.get('value') is None:
        return '— (0 denominator)'
    lo, hi = x['ci']
    suffix = 'W' if x['ci_method'] == 'Wilson-Kish' else 'B'
    return f"{100*x['value']:.2f} [{100*lo:.2f}, {100*hi:.2f}]{suffix}"


def table(out, headers, rows):
    out.extend(['', '| '+' | '.join(headers)+' |', '|'+'|'.join('---' for _ in headers)+'|'])
    out.extend('| '+' | '.join(str(v) for v in row)+' |' for row in rows)
    out.append('')


def main():
    start_frozen = frozen()
    head = subprocess.check_output(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    blind = read(DEV/'cards/items_blind.json')
    keys = read(DEV/'private/cards/items_key.json')
    key = {x['id']: x for x in keys}
    cut, cut_deck = read(DEV/'cards/cut_receipt.json'), read(DEV/'cards/items_blind_cut.json')
    assert len(key) == len(blind) == 1793 and [x['id'] for x in keys] == [x['id'] for x in blind]
    assert all(all(it[k] == b[k] for k in b) for it, b in zip(keys, blind))
    for it in keys:
        assert all(s in it['candidate_sources'][a] for s, form in it['forms'].items()
                   for a, text in it['options'].items() if text == (form or '∅'))
    assert sha(DEV/'cards/items_blind_cut.json') == cut['sha256_cut_deck']
    selected = {blind[i]['id'] for i in cut['selected_indices']}
    assert selected == {x['id'] for x in blind[:360]} | {x['id'] for x in cut_deck}
    readers, inputs = {}, {}
    for name in ('r1', 'r2'):
        answers = {}
        for path in sorted((DEV/'cards_private/readers').glob(name+'_*.jsonl')):
            rows = lines(path); start = int(path.stem.split('_')[-1])
            deck = cut_deck if '_cut_' in path.name else blind
            assert {r['id'] for r in rows} == {r['id'] for r in deck[start:start+len(rows)]}, path
            inputs[str(path.relative_to(ROOT))] = sha(path)
            for line, r in enumerate(rows, 1):
                assert r['id'] not in answers
                answers[r['id']] = dict(r, file=str(path.relative_to(ROOT)), file_line=line)
        assert set(answers) == selected and len(answers) == 1063
        readers[name] = answers
    tb = {x['id']: x for x in read(DEV/'cards_private/tiebreak/items_tb.json')}
    r3 = {x['id']: dict(x, file='docs/labelfix/spellcheck/S8_DEV/cards_private/tiebreak/r3.jsonl', file_line=i)
          for i, x in enumerate(lines(DEV/'cards_private/tiebreak/r3.jsonl'), 1)}
    assert len(tb) == len(r3) == 42 and set(tb) == set(r3)
    census = lines(DEV/'evidence/word_census.jsonl')
    census_key = {r['uid']: r for r in census}
    assert {r['uid'] for r in keys if not r['control']} == {r['uid'] for r in census if r['selected']}
    assert all(all(it[f] == census_key[it['uid']][f] for f in ('forms', 'selection', 'inclusion_probability', 'wave'))
               for it in keys if not it['control'])
    baseline = {r['wave']: r for r in read(DEV/'evidence/baseline_by_wave.json') if r['variant'] == 'original'}
    population = C.Counter(r['wave'] for r in census)
    deck_n = C.Counter(r['wave'] for r in keys if not r['control'])
    cut_n = C.Counter(key[k]['wave'] for k in selected if not key[k]['control'])
    assert cut_n == dict(parliament=578, round1=100, round2=100, mixed=100, vouli=100)
    cache, rows, agreements, tb_outcomes = {}, [], {}, C.Counter()
    disagreement_ids = set()
    for it in keys:
        k, w = it['id'], it['wave']
        row = {field: it[field] for field in ('id', 'wave', 'control', 'selection', 'line_id', 'uid', 'forms', 'raw_forms', 'elision_alias_only', 'scoring_policy', 'AB_status')}
        row.update(type='item', in_cut=k in selected, truth=None, status='unadjudicated', start=it['start'], end=it['end'])
        if not it['control']:
            row.update(card_inclusion_probability=it['inclusion_probability'], cut_probability=cut_n[w]/deck_n[w],
                       weight=1/(it['inclusion_probability']*cut_n[w]/deck_n[w]))
        if k in selected:
            votes = [vote(readers[r][k], it['options']) for r in ('r1', 'r2')]
            row['readers'] = {r: dict(readers[r][k], canonical_vote=v) for r, v in zip(('r1', 'r2'), votes)}
            row['reader_agreement'] = votes[0] == votes[1]
            if it['control']:
                row.update(status='excluded_control_construction_defect' if k == DEFECT else 'control', expected_choice=it['expected_choice'])
            else:
                if votes[0] != votes[1]:
                    disagreement_ids.add(k)
                    assert k in tb
                    v3 = vote(r3[k], tb[k]['options'])
                    row['tiebreak'] = dict(r3[k], options=tb[k]['options'], canonical_vote=v3)
                    votes.append(v3)
                    tb_outcomes['supports_r1' if v3 == votes[0] else 'supports_r2' if v3 == votes[1] else 'third_distinct'] += 1
                counts = C.Counter(votes)
                truth, n = counts.most_common(1)[0]
                known = n >= 2 and truth is not None
                row.update(status='resolved' if known else 'UNKNOWN', truth=truth if known else None,
                           resolution='three_reader_majority' if len(votes) == 3 else 'two_reader_agreement')
                if not known:
                    row['unknown_reason'] = 'majority_unreadable' if n >= 2 else 'no_majority'
                if len(votes) == 3:
                    tb_outcomes['resolved' if known else 'UNKNOWN'] += 1
                if known:
                    row['word_correct'] = {s: canonical(it['forms'][s]) == truth for s in SOURCES}
                    row['ordinary_letter_match'] = all(''.join(t['base'].casefold() for t in tokens(it['forms'][s]) if letter(t)) ==
                        ''.join(t['base'].casefold() for t in tokens(truth) if letter(t)) for s in ('r1_A', 'detector_original'))
                    lid = it['line_id']
                    if lid not in cache:
                        path = DEV/'evidence/baseline/original'/(lid+'.json.gz')
                        inputs[str(path.relative_to(ROOT))] = sha(path)
                        cache[lid] = json.loads(gzip.decompress(path.read_bytes()))
                    ss = [s for s in cache[lid]['detector']['slots'] if it['start'] <= s['start'] < it['end'] and letter(s)]
                    row['presence'] = {}
                    for s in ('detector_original', 'r1_A'):
                        row['presence'][s], failures = score_presence(row, s, ss)
                        if s == 'detector_original':
                            row['detector_failures'] = failures
                    row['elision_presence'] = {s: '’' in canonical(it['forms'][s]) for s in SOURCES}
                    row['truth_elision_presence'] = '’' in truth
        rows.append(row)
    assert disagreement_ids == set(tb)
    controls = [r for r in rows if r['in_cut'] and r['control'] and r['id'] != DEFECT]
    quality, misses = {}, {}
    for name in ('r1', 'r2'):
        misses[name] = [r['id'] for r in controls if r['readers'][name]['answer'] != r['expected_choice']]
        quality[name] = dict(correct=len(controls)-len(misses[name]), denominator=len(controls), missed_ids=misses[name])
    assert len(controls) == 84 and all(q['correct'] == 82 for q in quality.values())
    assert not set(misses['r1']) & set(misses['r2'])
    summary = dict(type='summary', reader_quality=quality, shared_control_misses=[], tiebreak=dict(tb_outcomes), waves={})
    for wi, w in enumerate(WAVES):
        cut_rows = [r for r in rows if r['wave'] == w and r['in_cut'] and not r['control']]
        resolved = [r for r in cut_rows if r['status'] == 'resolved']
        unknown = [r for r in cut_rows if r['status'] == 'UNKNOWN']
        ws = dict(population_words=population[w], deck_data_cards=deck_n[w], cut_data_cards=len(cut_rows), resolved=len(resolved),
                  unknown_ids=[r['id'] for r in unknown], unknown_weight=sum(r['weight'] for r in unknown),
                  unadjudicated=deck_n[w]-len(cut_rows), baseline=baseline[w], strata={}, word_accuracy={}, presence={}, failures=[])
        ws['reader_agreement'] = dict(n=sum(r['reader_agreement'] for r in cut_rows), denominator=len(cut_rows))
        ws['presence_sample'] = dict(truth_letters=sum(sum(letter(t) for t in tokens(r['truth'])) for r in resolved),
            weighted_truth_letters=sum(r['weight']*sum(letter(t) for t in tokens(r['truth'])) for r in resolved),
            union_slots={s: sum(len(r['presence'][s]['slots']) for r in resolved) for s in ('detector_original', 'r1_A')})
        for selection in ('disagreement', 'all_agree_sample'):
            rr = [r for r in cut_rows if r['selection'] == selection]
            ws['strata'][selection] = dict(population=sum(x['wave'] == w and x['selection'] == selection for x in census),
                deck=sum(x['wave'] == w and x['selection'] == selection and not x['control'] for x in keys),
                cut=len(rr), resolved=sum(r['status'] == 'resolved' for r in rr), weight=rr[0]['weight'] if rr else None)
        agreed = [r for r in resolved if r['selection'] == 'all_agree_sample']
        ws['all_agree_shared_errors'] = [r['id'] for r in agreed if not r['word_correct']['google']]
        for label, cohort in [('all', resolved), ('ordinary', [r for r in resolved if not r['elision_alias_only']]),
                              ('elision', [r for r in resolved if r['elision_alias_only']])]:
            ws['word_accuracy'][label] = {s: estimate(cohort, lambda r, s=s: r['word_correct'][s], lambda r: 1, SEED+wi) for s in SOURCES}
        ws['elision'] = dict(deck=sum(r['wave'] == w and not r['control'] and r['elision_alias_only'] for r in rows),
            cut=sum(r['elision_alias_only'] for r in cut_rows), resolved=sum(r['elision_alias_only'] for r in resolved))
        for source in ('detector_original', 'r1_A'):
            ws['presence'][source] = {}
            for family in KINDS:
                def num(r, s=source, f=family): return r['presence'][s]['counts'][f]['TP']
                def den(r, error, s=source, f=family): return num(r, s, f)+r['presence'][s]['counts'][f][error]
                counts = {k: dict(raw=sum(r['presence'][source]['counts'][family][k] for r in resolved),
                    weighted=sum(r['weight']*r['presence'][source]['counts'][family][k] for r in resolved)) for k in ('TP', 'FP', 'FN', 'TN')}
                ws['presence'][source][family] = dict(counts=counts,
                    precision=estimate(resolved, num, lambda r: den(r, 'FP'), SEED+wi),
                    recall=estimate(resolved, num, lambda r: den(r, 'FN'), SEED+wi))
            clean = [r for r in resolved if r['ordinary_letter_match']]
            ws['presence'][source]['exact_letters_sensitivity'] = dict(cards=len(clean),
                precision=estimate(clean, lambda r: r['presence'][source]['counts']['any']['TP'],
                    lambda r: sum(r['presence'][source]['counts']['any'][k] for k in ('TP', 'FP')), SEED+wi),
                recall=estimate(clean, lambda r: r['presence'][source]['counts']['any']['TP'],
                    lambda r: sum(r['presence'][source]['counts']['any'][k] for k in ('TP', 'FN')), SEED+wi))
        failure_groups = C.defaultdict(list)
        for r in resolved:
            for f in r['detector_failures']:
                failure_groups[f['failure_class']].append((r, f))
        for cls, group in failure_groups.items():
            ids = list(dict.fromkeys(r['id'] for r, _ in sorted(group, key=lambda x: (-x[0]['weight'], x[0]['id']))))
            ws['failures'].append(dict(failure_class=cls, raw=len(group), weighted=sum(r['weight'] for r, _ in group), examples=ids))
        ws['failures'].sort(key=lambda f: (-f['weighted'], f['failure_class']))
        summary['waves'][w] = ws
    input_names = ('cards/items_blind.json', 'private/cards/items_key.json', 'cards/cut_receipt.json', 'cards/items_blind_cut.json',
                   'cards_private/tiebreak/items_tb.json', 'cards_private/tiebreak/r3.jsonl', 'evidence/word_census.jsonl', 'evidence/baseline_by_wave.json')
    inputs.update({str((DEV/p).relative_to(ROOT)): sha(DEV/p) for p in input_names})
    assert frozen() == start_frozen
    assert subprocess.check_output(['git', '--no-optional-locks', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip() == head
    meta = dict(type='metadata', schema='s8-dev-truth-v1', head=head, network=False, inference_runs=0,
                script_sha256=sha(__file__), audit_sha256=sha(Path(__file__).with_name('s8_validate_truth.py')),
                python=sys.version, seed=SEED, bootstrap_replicates=REPS,
                protected_files_sha256=start_frozen, input_sha256=inputs,
                weight='1 / (saved card inclusion probability * wave cut data n / wave deck data N)',
                confidence='Document-cluster percentile bootstrap; Wilson-Kish fallback for degenerate bootstrap; line bootstrap also retained',
                physical_any='Boolean saved detector evidence above or below, including unnamed ink; R1-A any emitted combining mark',
                families='Presence of emitted combining family; subscript is named, physical below is separately recorded',
                alignment='Mark-blind casefolded base Levenshtein including punctuation anchors; union letter slots, gaps count FP/FN',
                defect=dict(id=DEFECT, printed='ἔχη', reason='wrong key has iota subscript; track-lead image verification; excluded, never repaired'))
    payload = ''.join(json.dumps(r, ensure_ascii=False, allow_nan=False)+'\n' for r in [meta, *rows, summary]).encode()
    output = DEV/'evidence/dev_truth.jsonl.gz'
    output.write_bytes(gzip.compress(payload, mtime=0))
    write_report(rows, summary, head, sha(output))
    print(json.dumps(dict(head=head, states=dict(C.Counter(r['status'] for r in rows)), reader_quality=quality,
                         tiebreak=dict(tb_outcomes), evidence_sha256=sha(output)), ensure_ascii=False, indent=2))


def write_report(rows, summary, head, digest):
    waves = summary['waves']
    out = ['# S8a6 — print-adjudicated training-wave DEV', '',
           '**978 data cards read: parliament 578, round1/round2/mixed/vouli 100 each; 976 resolved, two UNKNOWN.** '
           'The cut contains 1,063 items with 85 controls. The other 671 data cards and 59 controls remain unadjudicated. This is training-wave DEV, not a held-out test.', '',
           f'Analysis HEAD `{head}`. Network OFF; saved evidence only; zero inference; no detector, reader, gate, deck or key edits. '
           f'[Machine-readable evidence](S8_DEV/evidence/dev_truth.jsonl.gz), SHA256 `{digest}`. '
           'The gzip contains metadata, all 1,793 item states and one summary record, with ID joins, votes, weights, letter-slot outcomes, input hashes and both cluster intervals.', '',
           '## Readers and adjudication', '',
           '**R1 82/84, R2 82/84 (97.62% each); zero shared control misses.** The 85th control, '
           '`item_fa47d3102d8d11bd`, is a control-construction defect: the print is **ἔχη**, without iota subscript; both options/key contain a subscript. '
           'Both readers correctly rejected both options. Exclusion follows the track lead’s image verification; the frozen key is preserved.']
    table(out, ['Reader', 'Correct / valid controls', 'Missed control IDs'],
          [(r, f"{q['correct']}/{q['denominator']}", ', '.join('`'+k+'`' for k in q['missed_ids'])) for r, q in summary['reader_quality'].items()])
    table(out, ['Wave', 'R1/R2 data-form agreement', 'Adjudicated', 'Resolved truth', 'UNKNOWN', 'Unread data cards'],
          [(w, f"{s['reader_agreement']['n']}/{s['reader_agreement']['denominator']} ({100*s['reader_agreement']['n']/s['reader_agreement']['denominator']:.2f}%)",
            s['cut_data_cards'], s['resolved'], len(s['unknown_ids']), s['unadjudicated']) for w, s in waves.items()])
    out += [f"Tiebreak: **42/42 resolved; {summary['tiebreak']['supports_r1']} support R1 and {summary['tiebreak']['supports_r2']} support R2; zero third-distinct or unresolved outcomes.** "
            'Agreement above includes the two shared-unreadable parliament cards. Third-reader A/B letters are decoded against the tiebreak deck, never the original options. '
            'Forms, including none-of-these transcriptions, vote by canonical text. Majority unreadable or no majority becomes UNKNOWN and is excluded, counted and never scored as absence.', '',
            'UNKNOWN IDs: '+', '.join('`'+k+'`' for s in waves.values() for k in s['unknown_ids'])+'.', '',
            'The `r?_000…270` files are checked against full-deck slices 0–359; `r?_cut_*` against the 703-item remaining-cut deck. '
            'Reader output ordering differs, so all joins use IDs. Exactly 1,063 unique IDs per reader cover the cut; there are no duplicate votes.', '',
            '## Population, weights and uncertainty', '',
            'The target population is the **4,942 connected word groups** in the 600-line DEV census, not only disagreements or mark-positive words. '
            'Data-card inclusion is 1 for disagreements and the stored exact ceil(5%)/population fraction for all-agree words. '
            'The second-stage wave fraction is 578/578 for parliament and 100/N for each other wave’s data deck. '
            'Use **w = 1/(card inclusion × wave cut fraction)** for every card and all its slots. '
            'The shuffled first 360 plus seeded remainder are treated as the coordinator’s marginal wave cut; no additional conditional cut probabilities were supplied. '
            'Ratios use weighted sums (Hájek); unread cards supply no truth. UNKNOWN weights are excluded without redistributing them.', '',
            '**Intervals are 95% document-cluster percentile bootstrap (B), 4,000 replicates, seed 20261017 plus wave index; '
            'line-cluster bootstrap is also retained in the evidence.** Fixed inclusion weights are carried through cluster resampling; no finite-population correction is applied. '
            'Replicates with zero relevant denominator are omitted; valid replicate counts are retained. '
            'For a degenerate bootstrap only, W denotes a Wilson interval using Kish effective event n. W ignores clustering and is a boundary-data diagnostic; '
            'neither method includes reader error or proves performance outside these DEV lines. Undefined P/R denominators remain undefined.']
    table(out, ['Wave', 'Word population', 'Deck D / agree', 'Cut D / agree', 'Weight D / agree', 'Resolved Σw', 'UNKNOWN Σw'],
          [(w, s['population_words'], f"{s['strata']['disagreement']['deck']} / {s['strata']['all_agree_sample']['deck']}",
            f"{s['strata']['disagreement']['cut']} / {s['strata']['all_agree_sample']['cut']}",
            f"{s['strata']['disagreement']['weight']:.4f} / {s['strata']['all_agree_sample']['weight']:.4f}",
            f"{s['word_accuracy']['all']['google']['weighted_den']:.2f}", f"{s['unknown_weight']:.2f}") for w, s in waves.items()])
    out += ['Σw need not equal the census total after random cut sampling and UNKNOWN exclusion; it is not a count of distinct adjudicated words.', '',
            '## Source word accuracy', '',
            'Each cell is **weighted % [95% interval]; unweighted correct/resolved cards**. All resolved data cards, including the tagged elision subset, are included here. '
            'Equality preserves ink and misprints, case, punctuation, boundaries and missing elision; NFC/NFD equivalents and word-final codec v2.1 elision aliases count as one atom. '
            'U+1FBF before a capital attaches as smooth breathing. Printed keraia identities remain significant. '
            '**Frozen AB is the saved ENSEMBLE_AB proposal**, including HOLD lines, not an assertion that it was released.']
    table(out, ['Wave', *SOURCES], [(w, *[display(s['word_accuracy']['all'][src])+f"; {s['word_accuracy']['all'][src]['raw_num']}/{s['resolved']}" for src in SOURCES]) for w, s in waves.items()])
    out += ['All-agree adjudication is not assumed error-free: '+', '.join(
        f"{w} {len(s['all_agree_shared_errors'])}/{s['strata']['all_agree_sample']['resolved']} shared-error cards" for w, s in waves.items())+
        '. Shared-error IDs: '+', '.join('`'+k+'`' for s in waves.values() for k in s['all_agree_shared_errors'])+
        '. The small, highly weighted mixed all-agree sample is responsible for much of that wave’s word-accuracy uncertainty.', '']
    out += ['## Presence precision / recall', '',
            '**Primary detector `any` uses saved physical above-or-below ink evidence, including unnamed detections.** R1-A `any` uses its saved emitted marks. '
            'Breathing, accent, subscript and diaeresis use emitted family presence for both sources; family identity therefore depends on naming. '
            'An acute/grave/circumflex swap remains accent-present; smooth/rough remains breathing-present. '
            'Detector `emitted_any` and physical above/below zone results are given separately below. '
            'This prevents a naming error being misreported as a physical detection loss.', '',
            'Scores use the union of letter slots under a mark-blind base alignment with punctuation anchors and deterministic diagonal/delete/insert ties. '
            'Paired letter substitutions are location pairs for presence; base correctness is evaluated by word accuracy. '
            'Deleted positive truth slots count FN and inserted positive predictions count FP. Case does not alter presence alignment. '
            'Localisation-unknown, fused, uncertain and clipped slots stay in the scored cohort when the word truth is known; absent detector evidence is an emission miss, not proof of blank print. '
            'Elision is excluded from combining-mark presence and evaluated separately. These per-slot any-mark results are not the older S6 three-zone event denominator.']
    table(out, ['Wave', 'Resolved word cards', 'Print letter slots', 'Weighted print letter slots', 'Union slots detector / R1-A', 'Documents / lines'],
          [(w, s['resolved'], s['presence_sample']['truth_letters'], f"{s['presence_sample']['weighted_truth_letters']:.2f}",
            ' / '.join(str(s['presence_sample']['union_slots'][src]) for src in ('detector_original', 'r1_A')),
            f"{s['word_accuracy']['all']['google']['document_clusters']} / {s['word_accuracy']['all']['google']['line_clusters']}") for w, s in waves.items()])
    table(out, ['Wave', 'Detector any P / R', 'R1-A any P / R', 'Baseline loc_unknown', 'Baseline seg_uncertain'],
          [(w, display(s['presence']['detector_original']['any']['precision'])+' / '+display(s['presence']['detector_original']['any']['recall']),
            display(s['presence']['r1_A']['any']['precision'])+' / '+display(s['presence']['r1_A']['any']['recall']),
            f"{s['baseline']['localisation_unknown']}/{s['baseline']['letters']} ({s['baseline']['rates_percent']['localisation_unknown']:.2f}%)",
            f"{s['baseline']['segmentation_uncertain']}/{s['baseline']['letters']} ({s['baseline']['rates_percent']['segmentation_uncertain']:.2f}%)") for w, s in waves.items()])
    out += ['Baseline rates above cover all 600 original lines and use recogniser-indexed letters; they are not cut-weighted adjudication rates.', '',
            'Raw TP/FP/FN beside family results are unweighted letter-slot counts. Weighted TP/FP/FN/TN, effective n and every denominator are in the gzip.']
    for src in ('detector_original', 'r1_A'):
        out += ['', '### '+src]
        table(out, ['Wave', 'Family', 'Weighted precision % [95%]', 'Weighted recall % [95%]', 'Raw TP / FP / FN'],
              [(w, family, display(s['presence'][src][family]['precision']), display(s['presence'][src][family]['recall']),
                ' / '.join(str(s['presence'][src][family]['counts'][k]['raw']) for k in ('TP', 'FP', 'FN'))) for w, s in waves.items() for family in ('any', *FAMILY)])
    out += ['### Detector physical zones and emitted marks', '']
    table(out, ['Wave', 'Measure', 'Weighted precision % [95%]', 'Weighted recall % [95%]', 'Raw TP / FP / FN'],
          [(w, f, display(s['presence']['detector_original'][f]['precision']), display(s['presence']['detector_original'][f]['recall']),
            ' / '.join(str(s['presence']['detector_original'][f]['counts'][k]['raw']) for k in ('TP', 'FP', 'FN'))) for w, s in waves.items() for f in ('emitted_any', 'above', 'below')])
    out += ['### Exact-letter sensitivity', '', 'This sensitivity retains only cards whose complete detector and R1-A letter sequences match the print (casefolded). Main scores above retain gaps/substitutions.']
    table(out, ['Wave', 'Cards retained', 'Detector any P / R', 'R1-A any P / R'],
          [(w, s['presence']['detector_original']['exact_letters_sensitivity']['cards'],
            *[display(s['presence'][src]['exact_letters_sensitivity']['precision'])+' / '+display(s['presence'][src]['exact_letters_sensitivity']['recall']) for src in ('detector_original', 'r1_A')]) for w, s in waves.items()])
    out += ['## Elision / alias-only cards', '',
            '**33 tagged data cards in the frozen deck; only '+str(sum(s['elision']['cut'] for s in waves.values()))+' were read in this cut.** '
            'The rest remain unadjudicated. Alias normalization does not forgive an omitted elision or a different printed raised dot. '
            'These are small selected subsets; do not read the wide intervals as an independent elision benchmark.']
    out += ['', 'Deck tags are 32 elision-presence-only and one alias-only. Alias-only coverage: '+str(sum(
        r['in_cut'] and not r['control'] and r['scoring_policy'] == 'alias_only' for r in rows))+
        '/1 read. R1-A elision comes from saved recogniser punctuation; its mark head does not predict elision.']
    table(out, ['Wave', 'Tagged deck / cut / resolved', *SOURCES],
          [(w, f"{s['elision']['deck']} / {s['elision']['cut']} / {s['elision']['resolved']}",
            *[display(s['word_accuracy']['elision'][src])+f"; {s['word_accuracy']['elision'][src]['raw_num']}/{s['elision']['resolved']}" for src in SOURCES]) for w, s in waves.items()])
    out += ['Ordinary-only word accuracy, with all tagged cards removed (same weights):']
    table(out, ['Wave', *SOURCES], [(w, *[display(s['word_accuracy']['ordinary'][src])+f"; {s['word_accuracy']['ordinary'][src]['raw_num']}/{s['word_accuracy']['ordinary'][src]['raw_den']}" for src in SOURCES]) for w, s in waves.items()])
    out += ['## S8b targets from detector errors', '',
            'Rank by inverse-probability weighted **letter-slot failure events** in each wave. Counts estimate wave word-population events, not distinct cards. '
            'Physical above/below errors and naming errors have separate classes; classes can overlap on a slot. '
            'These are observed failure types, not proven geometric causes: localisation, clipping, ownership and font mechanisms still require pixel review. '
            'Example links point to the frozen word crops; per-slot flags, boxes and source baseline hashes remain in the gzip.']
    targets = []
    for w, s in waves.items():
        chosen = s['failures'][:3]
        targets.append(w+': '+', '.join(f['failure_class'] for f in chosen))
        out += ['', '### '+w]
        table(out, ['Failure class', 'Weighted events', 'Raw events / cards', 'Example IDs'],
              [(f['failure_class'], f"{f['weighted']:.2f}", f"{f['raw']} / {len(f['examples'])}",
                ', '.join(f"[{k}](S8_DEV/cards/img/{k}.png)" for k in f['examples'][:3])) for f in chosen])
        assert all(len(f['examples']) >= 3 for f in chosen), (w, chosen)
    out += ['The next bounded iteration should first test the ranked physical presence losses/additions on these examples, with naming held fixed; '
            'where naming classes rank highly, retain the physical/naming distinction in S8b qualification. No change is implemented or accepted by this analysis.', '',
            '## Reproduction and limits', '',
            '`PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=$PWD /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python scripts/labelfix/s8_score_truth.py`', '',
            'Audit: replace the final script path with `scripts/labelfix/s8_validate_truth.py`. Independent reaggregation verifies all 80 source/family/wave presence cells and all 20 source/wave accuracy cells; '
            'hand-calculated witnesses cover weighted ratios, elision aliases, spacing breathing, keraia, shifted marks, insertion/deletion and unnamed physical ink.', '',
            'The scorer checks full/cut file membership by ID, all 42 tiebreak identities, candidate decoding, control denominators, source-slot base identity, '
            'both frozen directories byte-for-byte before/after scoring and unchanged HEAD. All input file hashes are retained. '
            'No unadjudicated card is inferred correct from source agreement. UNKNOWN exclusions and cut sampling limit generalization; the existing masked DEV baseline remains pending.', '']
    def pr(s, src):
        return '/'.join(f"{100*s['presence'][src]['any'][k]['value']:.2f}%" for k in ('precision', 'recall'))
    out += ['S8 DEV TRUTH: adjudicated 978 data cards (parliament 578, others 4×100); controls r1 82/84 r2 82/84; detector presence P/R by wave '+
            ', '.join(w+' '+pr(s, 'detector_original') for w, s in waves.items())+'; R1-A '+
            ', '.join(w+' '+pr(s, 'r1_A') for w, s in waves.items())+'; Google word accuracy '+
            ', '.join(f"{w} {100*s['word_accuracy']['all']['google']['value']:.2f}%" for w, s in waves.items())+'; S8b targets '+'; '.join(targets)+'.']
    REPORT.write_text('\n'.join(out)+'\n')


if __name__ == '__main__':
    main()
