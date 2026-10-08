"""600-line gold/control teacher bake-off, with a fixed real-gold mark-F1 rule."""
from __future__ import annotations
import argparse
import time
import re
import unicodedata as ud
from pathlib import Path
from greekocr._vendor.bench.common import read_rows, write_rows, sha256
from greekocr._vendor.bench.e1_common import ROOT, atomic_json, read_json
from greekocr._vendor.bench.e1_readout import clean_row, summarize
from greekocr._vendor.bench.e2_teachers import reader, Unavailable

SELECTION_RULE = ('top two enabled image readers by pooled micro mark F1 on all 300 real gold lines; '
                  'require at least two fully scored, overlap-qualified non-E1 candidates; '
                  'refuse an E1-only selected pair; '
                  'ties: NFD CER, warmed wall ms/line, candidate ID; layer excluded; control never selects; services require --service')


def key(text): return ud.normalize('NFD', ' '.join(text.split()))


def shared_texts(e1):
    def texts(instrument):
        return {key(r['gt']) for r in read_rows(Path(e1)/'predictions'/f'f50_s0_{instrument}.jsonl')}
    return texts('synthetic_heldout') & texts('transfer_dev')


def calibration_exclusions(rows, shared=()):
    # Corpus membership alone is not exposure: its reserved band supplies v7.
    return set(shared) | {key(r.get('gt_nfd',r.get('text',''))) for r in rows
                          if r.get('split') in ('train','val')}


def select_gold(rows, excluded=(), count=300):
    blocked = set(excluded); selected = []; seen = set()
    for r in sorted(rows, key=lambda x: x['line_id']):
        text = key(r['text'])
        if (r.get('label_tier') != 'gold' or r.get('script_class') != 'greek_poly'
                or not r.get('admitted') or text in blocked or text in seen): continue
        seen.add(text); selected.append(dict(r, cohort='real_gold'))
    if len(selected) < count: raise ValueError(f'gold polytonic line shortfall: {len(selected)} < {count}')
    return selected[:count]


def gold_from_release(manifest, fallback, partition, out, excluded):
    from greekocr._vendor.bench.o4b_import_datasets import convert
    specs = read_json(manifest)['datasets']
    if {s['source_dataset'] for s in specs} != {'polyton_db'}:
        raise ValueError('primary gold source must be Polyton-DB')
    # Fallback only for release with no native line images, never for an invalid licence/schema.
    roots = [(Path(manifest).resolve().parent/s['root']).resolve() for s in specs]
    if any(not root.is_dir() for root in roots): raise ValueError('Polyton-DB release must be staged; missing payload is not evidence of absent line images')
    from greekocr._vendor.bench.o4b_common import rights
    for spec in specs: rights(spec)
    images = any(p.suffix.lower() in ('.png', '.tif', '.tiff', '.jpg', '.jpeg')
                 for root in roots for p in root.rglob('*'))
    images |= any(s['format'] in ('lmdb','kraken-arrow') and (root/s['path']).exists() for s,root in zip(specs,roots))
    chosen = manifest
    if not images:
        if not fallback: raise ValueError('Polyton-DB lacks line images; provide GRPOLY MachinePrinted-B manifest')
        chosen = fallback
        if any(s['source_dataset'] != 'grpoly_db' or s.get('subset') != 'MachinePrinted-B'
               for s in read_json(chosen)['datasets']):
            raise ValueError('fallback must be GRPOLY-DB MachinePrinted-B only')
    convert(chosen, partition, out)
    gold = select_gold(read_rows(Path(out)/'records.jsonl'), excluded)
    return gold, dict(manifest=str(chosen), sha256=sha256(chosen), fallback=chosen != manifest)


def control(e1, out, excluded, count=300):
    from greekocr._vendor.train.mix import validate, load_rows
    from greekocr._vendor.bench.line_categories import word_tags
    rows = load_rows(validate(Path(e1)/'synthetic_test_mix.json', role='eval'), 'reserved')[0]
    selected = []; seen = set(excluded)
    for row in sorted(rows, key=lambda r: r['line_id']):
        text = key(row['gt_nfd'])
        if row['script_class'] != 'greek_poly' or text in seen: continue
        seen.add(text); crop = Path(out)/'control_crops'/f'{len(selected):04d}.png'
        crop.parent.mkdir(parents=True, exist_ok=True); crop.write_bytes(row['image_png'])
        selected.append(dict(line_id=row['line_id'], source_doc_id=row['source_doc_id'],
            crop_path=str(crop.resolve()), crop_sha256=sha256(crop), text=row['gt_nfd'],
            script_class='greek_poly', cohort='v7_control', word_tags=word_tags(row['gt_nfd'])))
        if len(selected) == count: break
    if len(selected) < count: raise ValueError('v7 control shortfall after exclusions')
    return selected


def score(readings):
    # Reader APIs may return NFC. Canonically decompose BOTH scorer inputs,
    # including mark attribution; never collapse whitespace for CER. Raw saved
    # readings and the frozen E1 atom scorer remain unchanged.
    rows = [clean_row(dict(r, gt=ud.normalize('NFD', r['text']),
        prediction=ud.normalize('NFD', r['prediction']),
        arm='teacher', seed=0, instrument=r['cohort'])) for r in readings]
    result = summarize(rows)
    marks = result['marks']; tp = sum(m['tp'] for m in marks.values())
    fp = sum(m['fp'] for m in marks.values()); fn = sum(m['fn'] for m in marks.values())
    result['mark_f1'] = 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None
    for m in marks.values(): m['f1'] = 2*m['tp']/(2*m['tp']+m['fp']+m['fn']) if 2*m['tp']+m['fp']+m['fn'] else None
    result['greek_to_latin_homoglyphs'] = sum(m['greek']['latin'] for m in result['homoglyph_confusions'].values())
    return result


def overlap_exclusion(name, spec, gold):
    risk = spec.get('gold_overlap_risk', False) or name == 'kalchas_polytondb' or spec.get('model_name') == 'Polyton-DB'
    if not risk or not any(r.get('source_dataset') == 'polyton_db' for r in gold): return None
    proof = spec.get('gold_overlap_disproof')
    if proof:
        from greekocr._vendor.bench.e1_common import check_files
        evidence = read_json(proof)
        if (evidence.get('reviewed') is True and evidence.get('overlap_disproven') is True
                and evidence.get('gold_dataset') == 'polyton_db' and evidence.get('reason')
                and evidence.get('files')):
            check_files(evidence['files'])
            return None
    return 'gold_overlap_risk: Polyton-DB training/gold overlap has not been disproven'


def bakeoff(gold, synthetic, candidates, out, *, service=False, required=300, parity_mix=None):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    if len(gold) != required or len(synthetic) != required: raise ValueError('exactly 300+300 distinct lines required')
    if len({key(r['text']) for r in gold+synthetic}) != 2*required: raise ValueError('gold/control text overlap')
    if 'vouli_layer' in candidates: raise ValueError('layer candidate is intrinsic; do not configure it as a reader')
    # A failed/missing parity check stops before any scoring or teacher selection.
    from greekocr._vendor.bench.e2_reader_parity import qualify_readers
    try:
        e1_engines = qualify_readers(candidates, parity_mix, out)
    except Exception as error:
        atomic_json(out/'teachers.json', dict(schema='e2-teachers-v1', rule=SELECTION_RULE,
            ready=False, teachers=[], reason='reader parity gate failed: '+str(error)))
        raise
    allrows = gold+synthetic; results = {}; eligible = []
    for name, spec in [('vouli_layer', dict(kind='layer')), *sorted(candidates.items())]:
        if not re.fullmatch(r'[A-Za-z0-9_-]+',name): raise ValueError('candidate ID must be a safe file stem')
        predictions = []; errors = []; bound = None
        try:
            engine = None if spec['kind'] == 'layer' else e1_engines[name] if spec['kind'] == 'e1' else reader(spec, service=service)
            bound = getattr(engine, 'binding', None)
            if engine: engine.read(Path(gold[0]['crop_path']))  # warmup outside timing
            for r in allrows:
                try:
                    start = time.perf_counter()
                    hyp = r.get('layer_text') if engine is None else engine.read(Path(r['crop_path']))
                    elapsed = (time.perf_counter()-start)*1000
                    if hyp is None: raise Unavailable('NA: no Vouli OCR-layer twin')
                    if not isinstance(hyp, str): raise ValueError('reader must return text')
                    predictions.append(dict(r, prediction=hyp, elapsed_ms=elapsed))
                except Exception as error:
                    errors.append(dict(line_id=r['line_id'], cohort=r['cohort'], reason=str(error)))
        except Unavailable as error:
            errors = [dict(line_id=r['line_id'], cohort=r['cohort'], reason=str(error)) for r in allrows]
        except Exception as error:
            # Candidate load/schema failures are visible; they never become zero errors.
            errors = [dict(line_id=r['line_id'], cohort=r['cohort'], reason='candidate load failed: '+str(error)) for r in allrows]
        cohorts = {}
        for cohort in ('real_gold', 'v7_control'):
            success = [r for r in predictions if r['cohort'] == cohort]
            m = score(success) if success else None
            cohorts[cohort] = dict(scored=len(success), missing=required-len(success), metrics=m,
                ms_per_line_wall=sum(r['elapsed_ms'] for r in success)/len(success) if success else None,
                ms_per_line_cpu=(sum(r['elapsed_ms'] for r in success)/len(success) if success and spec['kind'] != 'service' else None),
                latency_kind='remote wall' if spec['kind'] == 'service' else 'CPU warmed wall, preprocessing+decode included')
        exclusion = overlap_exclusion(name, spec, gold)
        results[name] = dict(spec=spec, binding=bound, cohorts=cohorts, errors=errors,
            gold_overlap_risk=bool(spec.get('gold_overlap_risk') or name == 'kalchas_polytondb' or spec.get('model_name') == 'Polyton-DB'),
            selection_exclusion=exclusion)
        write_rows(out/f'{name}.predictions.jsonl', predictions)
        real = cohorts['real_gold']
        if not exclusion and spec['kind'] != 'layer' and (spec['kind'] != 'service' or service) and real['missing'] == 0 and real['metrics']['mark_f1'] is not None:
            eligible.append(name)
    eligible.sort(key=lambda n: (-results[n]['cohorts']['real_gold']['metrics']['mark_f1'],
        results[n]['cohorts']['real_gold']['metrics']['overall']['cer'],
        results[n]['cohorts']['real_gold']['ms_per_line_wall'], n))
    non_e1 = [n for n in eligible if results[n]['spec']['kind'] != 'e1']
    reason = None if len(non_e1) >= 2 else f'fewer than two fully scored non-E1 candidates ({len(non_e1)}); refusing E1-only self-agreement'
    selected = eligible[:2] if reason is None else []
    if selected and all(results[n]['spec']['kind']=='e1' for n in selected):
        reason = 'top-ranked pair is E1-only; refusing self-agreement even though external comparisons scored'
        selected = []
    report = dict(rule=SELECTION_RULE, normalization='NFD on both sides before CER and mark alignment; whitespace unchanged',
                  results=results, selected=selected, complete=len(selected)==2, reason=reason,
                  non_e1_eligible=non_e1, reader_parity_sha256=sha256(out/'reader_parity.json'),
                  gold_lines=required, control_lines=required,
                  candidate_coverage={n: ('scored' if r['cohorts']['real_gold']['missing']==0 else 'unavailable_or_incomplete')
                                      for n,r in results.items()},
                  completion_scope='two selected teachers; completion does not establish all candidate/backend qualifications')
    atomic_json(out/'bakeoff.json', report)
    from greekocr._vendor.bench.e1_readout import table
    md=['# E2 teacher bake-off','',SELECTION_RULE,'',
        'Missing readings are NA. Candidate selection requires every real-gold crop; control scores are diagnostic.',
        report['completion_scope'], '']
    md += table(['candidate','cohort','scored','NA','strict NFD CER','micro mark F1','Greek to Latin homoglyphs','CPU ms/line'],
        [(name,cohort,c['scored'],c['missing'],c['metrics']['overall']['cer'] if c['metrics'] else None,
          c['metrics']['mark_f1'] if c['metrics'] else None,c['metrics']['greek_to_latin_homoglyphs'] if c['metrics'] else None,
          c['ms_per_line_cpu']) for name,r in results.items() for cohort,c in r['cohorts'].items()])
    md += table(['candidate','cohort','mark','precision','recall','F1','TP','FP','FN'],
        [(name,cohort,mark,m['precision'],m['recall'],m['f1'],m['tp'],m['fp'],m['fn'])
         for name,r in results.items() for cohort,c in r['cohorts'].items() if c['metrics'] for mark,m in c['metrics']['marks'].items()])
    md += ['Selected: '+(', '.join(selected) if len(selected)==2 else 'unqualified: '+reason),'']
    (out/'BAKEOFF.md').write_text('\n'.join(md)+'\n')
    atomic_json(out/'teachers.json', dict(schema='e2-teachers-v1', rule=SELECTION_RULE,
        service_enabled=service,
        ready=len(selected)==2, reason=reason, non_e1_eligible=non_e1,
        reader_parity_sha256=sha256(out/'reader_parity.json'),
        teachers=[dict(id=n, **results[n]) for n in selected],
        bakeoff_sha256=sha256(out/'bakeoff.json')))
    write_rows(out/'gold.jsonl', gold); write_rows(out/'control.jsonl', synthetic)
    if len(selected) != 2: raise ValueError(reason+'; see bakeoff.json, no default selection')
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--config', type=Path, required=True); p.add_argument('--out', type=Path, required=True)
    p.add_argument('--e1', type=Path, default=ROOT/'out/e1_run4'); p.add_argument('--service', action='store_true')
    a = p.parse_args(); cfg = read_json(a.config); excluded = shared_texts(a.e1)
    required = {'f50_s0':'e1','f75_s0':'e1','kalchas':'kalchas','kalchas_polytondb':'kalchas','cllg':'cllg'}
    if any(cfg['candidates'].get(n,{}).get('kind') != kind for n,kind in required.items()):
        raise ValueError('candidate inventory must include retrained f50_s0/f75_s0, both pinned Kalchas models and CLLG')
    for name,registry in (('kalchas','Kalchas'),('kalchas_polytondb','Polyton-DB')):
        if cfg['candidates'][name].get('model_name') != registry:
            raise ValueError('candidate registry mismatch: '+name+' must use '+registry)
    cfg['candidates']['kalchas_polytondb']['gold_overlap_risk'] = True
    from greekocr._vendor.bench.e2_teachers import SERVICE_ENV
    for name in SERVICE_ENV:
        cfg['candidates'].setdefault(name,dict(kind='service',service=name))
    # Pool split is authoritative; reserved corpus membership is never exposure.
    sources=[a.e1/'real_records_source.jsonl',a.e1/'pool.jsonl']
    excluded = calibration_exclusions([r for path in sources for r in read_rows(path)],excluded)
    gold, source = gold_from_release(Path(cfg['polyton_manifest']),
        Path(cfg['grpoly_manifest']) if cfg.get('grpoly_manifest') else None,
        cfg['partition'], a.out/'imported_gold', excluded)
    synthetic = control(a.e1, a.out, excluded | {key(r['text']) for r in gold})
    atomic_json(a.out/'selection.json', dict(source=source, shared_gt_excluded=len(shared_texts(a.e1)),
        exposure_sources={str(p):sha256(p) for p in sources},
        excluded_texts=sorted(excluded), gold_docs=sorted({r['source_doc_id'] for r in gold})))
    bakeoff(gold, synthetic, cfg['candidates'], a.out, service=a.service,
            parity_mix=a.e1/'synthetic_test_mix.json')


if __name__ == '__main__': main()
