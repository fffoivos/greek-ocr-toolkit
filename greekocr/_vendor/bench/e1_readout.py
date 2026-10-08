#!/usr/bin/env python3
"""Strict atom readout; predictions remain untouched (including mark ordering errors)."""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
import sys
import unicodedata as ud

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from greekocr._vendor.train.cer import levenshtein
from greekocr._vendor.bench.common import read_rows, script
from greekocr._vendor.bench.e1_common import read_json, ROOT, CLASSES, FRACTIONS, SEEDS, atomic_json, sha256

MARKS = {'acute': '\u0301', 'grave': '\u0300', 'circumflex': '\u0342\u0302',
         'smooth_breathing': '\u0313', 'rough_breathing': '\u0314',
         'iota_subscript': '\u0345', 'dialytika': '\u0308'}
# Explicit diagnostic groups, case-sensitive. No scoring folds.
HOMOGLYPHS = ('ΑAА', 'ΒBВ', 'ΕEЕ', 'ΖZ', 'ΗHН', 'ΙIІ', 'ΚKК', 'ΜMМ', 'ΝN',
              'ΟOО', 'ΡPР', 'ΤTТ', 'ΥY', 'ΧXХ', 'ϹCС', 'οoо', 'ρpр', 'νv', 'аa', 'сc', 'еe', 'хx', 'іi')
DIMENSIONS = ('font_status', 'font', 'severity', 'bg_type', 'polarity', 'width_bucket', 'length_bucket', 'crop_augmentation')
SCRIPTS = ('greek', 'latin', 'cyrillic')


def alignment(ref, pred):
    """Strip shared prefix/suffix, then unit-cost path with diagonal/del/ins ties."""
    prefix=0
    while prefix < min(len(ref),len(pred)) and ref[prefix] == pred[prefix]:
        prefix+=1
    suffix=0
    while suffix < min(len(ref),len(pred))-prefix and ref[len(ref)-suffix-1] == pred[len(pred)-suffix-1]:
        suffix+=1
    before=list(zip(ref[:prefix],pred[:prefix]))
    after=list(zip(ref[len(ref)-suffix:],pred[len(pred)-suffix:])) if suffix else []
    ref=ref[prefix:len(ref)-suffix];pred=pred[prefix:len(pred)-suffix]
    dp = [list(range(len(pred)+1))] + [[i]+[0]*len(pred) for i in range(1, len(ref)+1)]
    for i, a in enumerate(ref, 1):
        for j, b in enumerate(pred, 1):
            dp[i][j] = min(dp[i-1][j-1]+(a != b), dp[i-1][j]+1, dp[i][j-1]+1)
    i, j, path = len(ref), len(pred), []
    while i or j:
        if i and j and dp[i][j] == dp[i-1][j-1]+(ref[i-1] != pred[j-1]):
            path.append((ref[i-1], pred[j-1])); i -= 1; j -= 1
        elif i and dp[i][j] == dp[i-1][j]+1:
            path.append((ref[i-1], None)); i -= 1
        else:
            path.append((None, pred[j-1])); j -= 1
    return before+list(reversed(path))+after


def metric(rows):
    edits = sum(r['edits'] for r in rows)
    ref = sum(len(r['gt']) for r in rows)
    return dict(cer=edits/ref if ref else None, edits=edits, ref_len=ref, lines=len(rows))


def mark_metrics(rows):
    counts = {k: dict(tp=0, fp=0, fn=0) for k in MARKS}
    names = {atom:name for name,atoms in MARKS.items() for atom in atoms}
    for row in rows:
        for a, b in alignment(row['gt'], row['prediction']):
            # Circumflex atoms are grouped for reporting, but identities stay strict.
            if a == b and a in names:
                counts[names[a]]['tp'] += 1
            elif a != b:
                if a in names:
                    counts[names[a]]['fn'] += 1
                if b in names:
                    counts[names[b]]['fp'] += 1
    for c in counts.values():
        c.update(precision=c['tp']/(c['tp']+c['fp']) if c['tp']+c['fp'] else None,
                 recall=c['tp']/(c['tp']+c['fn']) if c['tp']+c['fn'] else None,
                 cer=(c['fp']+c['fn'])/(c['tp']+c['fn']) if c['tp']+c['fn'] else None,
                 support=c['tp']+c['fn'])
    return counts


def confusion(rows):
    matrices = {c: {a: {b: 0 for b in SCRIPTS} for a in SCRIPTS} for c in (*CLASSES, 'furniture', 'other')}
    for row in rows:
        matrix = matrices.get(row['script_class'], matrices['other'])
        for a, b in alignment(row['gt'], row['prediction']):
            if a and b and a != b and any(a in g and b in g for g in HOMOGLYPHS):
                sa, sb = script(a), script(b)
                if sa in SCRIPTS and sb in SCRIPTS and sa != sb:
                    matrix[sa][sb] += 1
    return matrices


def summarize(rows):
    by_class = {c: metric([r for r in rows if r['script_class'] == c]) for c in (*CLASSES, 'furniture')}
    marks = mark_metrics(rows)
    marks_by_class = {c: mark_metrics([r for r in rows if r['script_class'] == c]) for c in CLASSES}
    breakdown = {}
    for field in DIMENSIONS:
        groups = defaultdict(list)
        for r in rows:
            groups[str(r.get(field, 'unknown'))].append(r)
        if field == 'font_status':
            for status in ('seen', 'held_out', 'unknown'):
                groups[status]
        breakdown[field] = {k: metric(v) for k, v in sorted(groups.items())}
    baseline = by_class['greek_mono']['cer']
    pain = []
    if baseline is not None:
        for c, m in by_class.items():
            if m['cer'] is not None and m['cer'] > 2*baseline:
                pain.append(dict(kind='class', name=c, cer=m['cer'], threshold=2*baseline,
                    next_experiment='C5 script-aware rescoring' if c in ('greek_latin_cs','cyrillic_latin_cs','cyrillic','latin') else 'C4 Experiment3: 48 vs 64 px and training-only guidance'))
        for name, m in marks.items():
            if m['cer'] is not None and m['cer'] > 2*baseline:
                pain.append(dict(kind='mark', name=name, cer=m['cer'], threshold=2*baseline,
                    next_experiment='C4 Experiment3: 48 vs 64 px and training-only guidance'))
        fonts = breakdown['font_status']['held_out']
        if fonts['cer'] is not None and fonts['cer'] > 2*baseline:
            pain.append(dict(kind='font', name='held_out', cer=fonts['cer'], threshold=2*baseline,
                next_experiment='C4 Experiment2: mixture/f choice'))
    from greekocr._vendor.bench.line_categories import categories
    category_groups = defaultdict(list)
    for row in rows:
        for category in categories(row):
            category_groups[category].append(row)
    return dict(overall=metric(rows), per_script_class=by_class, marks=marks, marks_by_class=marks_by_class,
                by_category={k: metric(v) for k, v in sorted(category_groups.items())},
                by=breakdown, homoglyph_confusions=confusion(rows), pain_points=pain,
                missing_classes=[c for c in CLASSES if not by_class[c]['lines']],
                worst={c: sorted([r for r in rows if r['script_class'] == c],
                           key=lambda r: (-r['line_cer'], r['crop_path'], r['prediction']))[:50] for c in CLASSES})


def clean_row(raw):
    row = dict(raw)
    if ud.normalize('NFD', row['gt']) != row['gt']:
        raise ValueError('GT must be decoded NFD label_ids; refusing precomposed fake GT')
    row['edits'] = levenshtein(row['gt'], row['prediction'])
    scripts = {script(c) for c in row['gt']} - {None}
    if row.get('script_class') == 'cyrillic' and scripts == {'cyrillic', 'latin'}:
        row['source_script_class'] = row['script_class']
        row['script_class'] = 'cyrillic_latin_cs'  # readout stratum; frozen import labels stay untouched
    row['line_cer'] = row['edits']/max(1, len(row['gt']))
    width = row.get('width')
    row['width_bucket'] = str(((width+127)//128)*128) if isinstance(width, int) else 'unknown'
    row['length_bucket'] = next((str(n) for n in (20, 40, 80, 140) if len(row['gt']) <= n), '>140')
    row.setdefault('crop_augmentation', 'crop' if any('crop' in op for op in row.get('applied_ops', [])) else 'clean')
    row.setdefault('font_status', 'unknown')
    for key in ('arm', 'seed', 'instrument', 'script_class', 'crop_path'):
        if key not in row:
            raise ValueError(f'prediction metadata missing: {key}')
    return row


def fmt(value):
    return 'NA' if value is None else f'{value:.6f}' if isinstance(value, float) else str(value)


def table(header, rows, disclosure=None):
    escape = lambda v: fmt(v).replace('|', '\\|').replace('\n', ' ')
    if disclosure:
        header = header + ['provenance disclosure (all numbers in this row)']
        rows = [(*r, disclosure) for r in rows]
    return ['| '+' | '.join(header)+' |', '| '+' | '.join(['---']*len(header))+' |'] + ['| '+' | '.join(map(escape, r))+' |' for r in rows] + ['']


def readout(predictions, out, *, require_complete=False, transfer_enabled=None, expected=None, title='E1'):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    rows = [clean_row(r) for p in predictions for r in read_rows(p)]
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r['arm'], int(r['seed']), r['instrument'])].append(r)
    if transfer_enabled is None:
        plan = read_json(out/'mix_plan.json') if (out/'mix_plan.json').exists() else {}
        transfer_enabled = plan.get('transfer_enabled', any(r['instrument']=='transfer_dev' for r in rows))
    if not transfer_enabled and any(r['instrument']=='transfer_dev' for r in rows):
        raise ValueError('transfer predictions present despite disabled transfer evaluation')
    instruments = ('real_test','synthetic_heldout') + (('transfer_dev',) if transfer_enabled else ())
    expected = (set(expected) if expected is not None else
                {(f'f{f}', s, i) for f in FRACTIONS for s in SEEDS for i in instruments})
    if require_complete and set(grouped) != expected:
        raise ValueError(f'incomplete {title} evaluations: missing={sorted(expected-set(grouped))}, extra={sorted(set(grouped)-expected)}')
    results = {f'{arm}_s{seed}/{instrument}': summarize(v) for (arm, seed, instrument), v in sorted(grouped.items())}
    for (arm, seed, instrument), values in grouped.items():
        statuses = {r.get('word_tags_status', 'unknown') for r in values}
        results[f'{arm}_s{seed}/{instrument}'].update(
            word_tags=next(iter(statuses)) if len(statuses) == 1 else 'mixed',
            word_tags_sources=sorted({r.get('word_tags_source', 'unknown') for r in values}))
        legacy = [r for r in values if r.get('component_kind') == 'legacy_eval' or r.get('provenance_status') == 'unprovenanced_recipe']
        if legacy:
            disclosures = {r.get('disclosure') for r in legacy}
            if len(legacy) != len(values) or len(disclosures) != 1 or not all(isinstance(d, str) and d.strip() for d in disclosures):
                raise ValueError('legacy evaluation requires one consistent nonempty disclosure on every prediction')
            results[f'{arm}_s{seed}/{instrument}'].update(provenance_status='unprovenanced_recipe', disclosure=disclosures.pop())
    report = dict(schema_version=1, metric='strict NFD codepoints: unchanged train.cer.levenshtein / train.eval_cer.evaluate',
        complete=set(grouped) == expected, results=results, transfer_enabled=transfer_enabled,
        transfer_status='included' if transfer_enabled else 'omitted: --transfer-mix was not supplied; no transfer columns or metrics',
        mark_cer_definition='(FP+FN)/GT mark occurrences; NA when no reference support; substitutions contribute outgoing FN and incoming FP',
        alignment_ties='shared identical prefix/suffix, then diagonal, deletion, insertion; no renormalization of predictions',
        confusion_groups=list(HOMOGLYPHS), pain_rule='CER > 2 * greek_mono CER on the SAME arm/seed/instrument; missing baseline = unassessable',
        page_readout={'status':'not_measured', 'next_experiment':'C1/C2 page attribution; detector coverage -> C4 Experiment1',
                      'reason':'line-only predictions cannot establish detector coverage or page CER'},
        galleries={arm: {c: sorted([r for r in rows if r['arm'] == arm and r['script_class'] == c],
                     key=lambda r: (-r['line_cer'], int(r['seed']), r['crop_path']))[:50] for c in CLASSES}
                   for arm in sorted({r['arm'] for r in rows})})
    receipts = [p for p in (out/'runs').glob('*/E1_RUN_COMPLETE.json')]
    if receipts:
        import json
        report['runs'] = {p.parent.name: json.loads(p.read_text()) for p in receipts}
        report['actual_training_counts']={}
        for p in receipts:
            provenance=p.parent/'data_provenance.json'
            if sha256(provenance) != report['runs'][p.parent.name]['provenance_sha256']:
                raise ValueError('changed training provenance during readout')
            report['actual_training_counts'][p.parent.name]=json.loads(provenance.read_text())['epochs']
    if (out/'build_info.json').exists():
        import json
        build=json.loads((out/'build_info.json').read_text())
        report['coverage']=build['coverage']
        report['strata_shortfalls']=build.get('strata_shortfalls',[])
    if (out/'mix_plan.json').exists():
        import json
        report['training_counts']=json.loads((out/'mix_plan.json').read_text())
    if (out/'concurrency.json').exists():
        import json
        report['concurrency_history']=[json.loads(p.read_text()) for p in sorted((out/'logs').glob('concurrency-*.json'))]
    report['update_status'] = ('equal planned budgets, early-stopped' if any(r.get('early_stopped') for r in report.get('runs', {}).values()) else 'equal planned updates; consult per-run receipts for realized updates')
    md = ['# '+title+' pain-point map', '', 'PROVISIONAL machine-admitted labels. No model-release claim.', '',
          report['metric'], '', report['update_status'], '', 'Transfer evaluation: '+report['transfer_status'], '', report['mark_cer_definition'], '', report['pain_rule'], '',
          'Missing strata are NA, never zero CER. O5 real TEST has no polytonic/Cyrillic support.', '',
          'Page detector attribution: not measured here; C1/C2 -> C4 Experiment1.', '']
    if report.get('training_counts'):
        md += ['## Planned assembled training counts', '', 'Recipe build remains v5 target200000; assembled TRAIN exposure is capped at real TRAIN size. Early stopping can leave later planned epochs untrained.', '']
        md += table(['fraction','seed','epoch','rows','batches']+list(CLASSES),
            [(f,s,e,p['marginals']['n_rows'],p['batches'],*[p['marginals']['counts']['script_class'].get(c,0) for c in CLASSES])
             for f,seeds in report['training_counts']['planned'].items() for s,epochs in seeds.items() for e,p in epochs.items()])
    if report.get('actual_training_counts'):
        md += ['## Actual trained epoch strata', '']+table(['run','epoch','rows']+list(CLASSES),
            [(name,e,p['train']['marginals']['n_rows'],*[p['train']['marginals']['counts']['script_class'].get(c,0) for c in CLASSES])
             for name,epochs in sorted(report['actual_training_counts'].items()) for e,p in epochs.items()])
    if report.get('strata_shortfalls'):
        md += ['## Source strata shortfalls', '']+table(['component','split','class','count','reason'],
            [(r['component'],r['split'],r['script_class'],r['count'],r['reason']) for r in report['strata_shortfalls']])
    for key, result in results.items():
        def result_table(header, values):
            return table(header, values, result.get('disclosure'))
        md += ['## '+key, '', 'word_tags: '+result['word_tags']+'; displayed tag sources: '+
               ', '.join(result['word_tags_sources']), '', '### Overall and script classes', '']
        md += result_table(['class','CER','edits','reference atoms','lines'], [(c, m['cer'],m['edits'],m['ref_len'],m['lines']) for c,m in [('overall',result['overall']),*result['per_script_class'].items()]])
        md += ['### NFD marks', ''] + result_table(['mark','precision','recall','mark CER','GT support','TP','FP','FN'],
                    [(k,m['precision'],m['recall'],m['cer'],m['support'],m['tp'],m['fp'],m['fn']) for k,m in result['marks'].items()])
        md += ['### NFD marks by script class', ''] + result_table(['class','mark','precision','recall','mark CER','GT support'],
                    [(c,k,m['precision'],m['recall'],m['cer'],m['support']) for c,marks in result['marks_by_class'].items() for k,m in marks.items()])
        for field, buckets in result['by'].items():
            md += ['### '+field, ''] + result_table(['bucket','CER','edits','reference atoms','lines'], [(k,m['cer'],m['edits'],m['ref_len'],m['lines']) for k,m in buckets.items()])
        md += ['### Rule categories (overlapping; absent font metadata stays unknown)', ''] + result_table(
            ['category','CER','edits','reference atoms','lines'],
            [(k,m['cer'],m['edits'],m['ref_len'],m['lines']) for k,m in result['by_category'].items()])
        md += ['### Cross-script homoglyph substitutions', ''] + result_table(['class','GT script','prediction script','count'], [(c,a,b,n) for c,matrix in result['homoglyph_confusions'].items() for a,d in matrix.items() for b,n in d.items()])
        md += ['### Preset pain points', ''] + result_table(['kind','name','CER','threshold','next experiment'], [(p['kind'],p['name'],p['cer'],p['threshold'],p['next_experiment']) for p in result['pain_points']])
        for c, worst in result['worst'].items():
            md += ['### Worst lines: '+c, ''] + result_table(['CER','crop path','GT','prediction'], [(r['line_cer'],r['crop_path'],r['gt'],r['prediction']) for r in worst])
    from greekocr._vendor.train.mix import disclose_numbers
    for result in results.values():
        if result.get('disclosure'):
            disclose_numbers(result, result['disclosure'])
    atomic_json(out/'report.json', report)
    (out/'REPORT.md').write_text('\n'.join(md)+'\n')
    return report


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=ROOT/'out/e1')
    ap.add_argument('--predictions', type=Path, nargs='+')
    ap.add_argument('--require-complete', action='store_true')
    a = ap.parse_args()
    readout(a.predictions or sorted((a.out/'predictions').glob('*.jsonl')), a.out, require_complete=a.require_complete)
