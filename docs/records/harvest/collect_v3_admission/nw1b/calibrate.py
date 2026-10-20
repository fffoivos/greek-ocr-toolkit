"""CP1 qualification over frozen observations only; no detection or publication.

Historical merged/rotated flags retain their actual union effect as diagnostics.
They are not semantic truth; CP3/CP5 will replace their admission meaning.
"""
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from greekocr.harvest.neighbour_words import DEFAULTS, PARAMS_SHA, runs

BASE = Path(__file__).resolve().parent
LEDGER = BASE.parent / 'seg/calibration_ledger.json'
CANDIDATE_PARAMS = dict(min_components=10, min_width_xh=3., min_height_xh=.6)


class QualificationError(ValueError):
    pass


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def truth(path=LEDGER):
    ledger = json.loads(Path(path).read_text())
    cards = ledger['cases']
    ids = [c['row_id'] for c in cards]
    if len(ids) != len(set(ids)):
        raise QualificationError('duplicate calibration IDs')
    keep = {c['row_id'] for c in cards if c['truth'] == 'keep'}
    drop = {c['row_id'] for c in cards if c['truth'] == 'drop'}
    if len(keep) != 22 or keep & drop:
        raise QualificationError('owner truth partition changed')
    if len(drop) != ledger['counts']['required_drop'] or any(not c['provenance'] for c in cards):
        raise QualificationError('missing DROP provenance or count mismatch')
    brief = (ROOT/'docs/briefs/NW1b_neighbour_words_recalibrated.md').read_text()
    owner_keep = set(re.findall(r'^- ([\w]+--[\w]+--s\d+-l\d+)$', brief.split('**KEEP')[1].split('**BORDERLINE')[0], re.M))
    named = brief.split('the 8 owner')[1].split('- **Note')[0]
    owner_issues = set()
    prefix = None
    for token in re.findall(r'(?:[\w]+--[\w]+--s\d+)?-l\d+', named):
        if '--' in token:
            prefix = token.rsplit('-l',1)[0]
        owner_issues.add(prefix + '-l' + token.rsplit('-l',1)[1])
    gallery_merges = {w['row_id'] for w in ledger['gallery_witnesses'] if w['type']=='merged_multi_line'}
    if keep != owner_keep or len(owner_issues) != 7 or drop != gallery_merges | owner_issues:
        raise QualificationError('invented or missing owner labels / required positives')
    if ledger['counts'] != dict(keep=22, required_drop=len(drop), named_owner_issues=7,
                                borderline=1, c1=len(ledger['c1_witnesses']), gallery_merges=len(gallery_merges)):
        raise QualificationError('invented truth counts')
    if ledger['eighth_owner_issue']['status'] != 'unidentified' or ledger['eighth_owner_issue']['row_id'] is not None:
        raise QualificationError('unproven eighth owner issue')
    ledger_name = str(Path(path).relative_to(ROOT)) if Path(path).is_relative_to(ROOT) else str(path)
    code_paths = [Path(__file__), BASE/'prepare_w1.py', BASE/'reissue.py', ROOT/'greekocr/harvest/neighbour_words.py']
    return cards, dict(ledger_path=ledger_name, ledger_sha256=sha(path),
                       code_sha256={str(p.relative_to(ROOT)):sha(p) for p in code_paths})


def predictions(card, measurement, params):
    available = measurement is not None and measurement.get('matched') is True and bool(measurement.get('xheight'))
    nw = bool(runs(measurement, **params)) if available else None
    values = dict(neighbour_words=nw, screen_merged=card.get('screen_merged'), rotated_crop=card.get('rotated_crop'))
    bits = list(values.values())
    values['union'] = True if any(v is True for v in bits) else None if any(v is None for v in bits) else False
    return values


def rate(numerator, denominator):
    """Descriptive Wilson 95% interval; targeted, shared-page data are not IID."""
    if not denominator:
        return dict(numerator=numerator, denominator=denominator, value=None, wilson95=None)
    p = numerator / denominator
    z = 1.959963984540054
    a = 1 + z*z/denominator
    centre = (p + z*z/(2*denominator))/a
    half = z*math.sqrt(p*(1-p)/denominator + z*z/(4*denominator**2))/a
    return dict(numerator=numerator, denominator=denominator, value=p, wilson95=[max(0., centre-half), min(1., centre+half)])


def score(cards, measurements, params, combined=False, *, screen=None):
    screen = screen or ('union' if combined else 'neighbour_words')
    counts = dict(tp=0, fp=0, fn=0, tn=0)
    unknown = []; false_drops = []; missed = []
    ids = [c['row_id'] for c in cards]
    if len(ids) != len(set(ids)):
        raise QualificationError('duplicate IDs cannot enter a gate denominator')
    for c in cards:
        if c['truth'] not in ('keep', 'drop'):
            continue
        detected = predictions(c, measurements.get(c['row_id']), params)[screen]
        if detected is None:
            unknown.append(c['row_id']); continue
        positive = c['truth'] == 'drop'
        counts['tp' if detected and positive else 'fp' if detected else 'fn' if positive else 'tn'] += 1
        if detected and not positive: false_drops.append(c['row_id'])
        if not detected and positive: missed.append(c['row_id'])
    tp, fp, fn, tn = (counts[k] for k in ('tp','fp','fn','tn'))
    return dict(confusion=counts, precision=rate(tp,tp+fp), recall=rate(tp,tp+fn),
                keep_false_drop_rate=rate(fp,fp+tn), survivor_defect_rate=rate(fn,fn+tn),
                unknown_count=len(unknown), unknown=unknown, false_drop_ids=false_drops, missed_ids=missed,
                gate=bool(tp+fp+fn+tn) and fp == 0 and fn == 0 and not unknown)


def evaluate(cards, params):
    measurements = {c['row_id']: c['measurement'] for c in cards}
    screens = {s:score(cards, measurements, params, screen=s) for s in ('neighbour_words','screen_merged','rotated_crop','union')}
    return dict(params=params, standalone=screens['neighbour_words'], combined=screens['union'], screens=screens)


def build_report(ledger_path=LEDGER):
    cards, bindings = truth(ledger_path)
    ledger = json.loads(Path(ledger_path).read_text())
    candidate = evaluate(cards, CANDIDATE_PARAMS)
    by_id = {c['row_id']:c for c in cards}
    witnesses = {}
    for name, entries in [('c1',ledger['c1_witnesses']), ('gallery_merges',[w for w in ledger['gallery_witnesses'] if w['type']=='merged_multi_line'])]:
        witnesses[name] = dict(total=len(entries), detected=[], missed=[], unknown=[])
        for w in entries:
            c = by_id[w['row_id']]
            hit = predictions(c,c['measurement'],CANDIDATE_PARAMS)['union']
            witnesses[name]['detected' if hit is True else 'missed' if hit is False else 'unknown'].append(c['row_id'])
    gate = candidate['combined']['gate'] and all(not w['missed'] and not w['unknown'] for w in witnesses.values())
    return dict(schema='SEG-CP1-qualification-v1', bindings=bindings, ownership_params_sha256=PARAMS_SHA,
                defaults=DEFAULTS, default=evaluate(cards,DEFAULTS), candidate=candidate,
                selected=candidate if gate else None, gate=gate, witnesses=witnesses,
                keep=ledger['counts']['keep'], drop=ledger['counts']['required_drop'],
                non_gating=[dict(row_id=c['row_id'],truth=c['truth'], predictions=predictions(c,c['measurement'],CANDIDATE_PARAMS)) for c in cards if c['truth'] not in ('keep','drop','challenge')],
                limitations='Saved development observations only; historical flags are diagnostics. No fresh draw, semantic screen qualification, detection, reading, or publishing. Wilson intervals are descriptive; targeted selection and shared pages limit inference.')


def require_qualification(report_path=BASE/'calibration.json', ledger_path=LEDGER):
    """All callers re-evaluate the same union; stale or forged passes stop."""
    report = json.loads(Path(report_path).read_text())
    current = build_report(ledger_path)
    if report != current:
        raise QualificationError('stale/inconsistent qualification report; regenerate from frozen ledger')
    ledger = json.loads(Path(ledger_path).read_text())
    for path, digest in ledger['sources'].items():
        source = Path(path) if Path(path).is_absolute() else ROOT/path
        if sha(source) != digest:
            raise QualificationError('stale provenance: ' + path)
    if not current['gate']:
        raise QualificationError('GATE_FAIL: actual segmentation union rejects owner KEEP or misses required witnesses')
    return current


def main():
    report = build_report()
    (BASE/'calibration.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    failure = BASE/'GATE_FAIL.md'
    if not report['gate']:
        failure.write_text('# SEG-CP1: GATE_FAIL\n\nThe saved standalone passer fails the actual merged/rotated/neighbour union: '
                           f"{report['candidate']['combined']['confusion']['fp']}/22 owner KEEP rejected. "
                           'Preparation and reissue are blocked. Historical flags remain diagnostics; no publication is authorized.\n')
    print(json.dumps(dict(gate=report['gate'],keep=report['keep'],drop=report['drop'],union=report['candidate']['combined']['confusion'])))
    return 0 if report['gate'] else 1


if __name__ == '__main__':
    sys.exit(main())
