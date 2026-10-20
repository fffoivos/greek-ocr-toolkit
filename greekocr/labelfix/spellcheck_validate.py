"""Offline S1 validation, both seeds, cached CTC only; writes report, rows and v4 sheets.

python -m greekocr.labelfix.spellcheck_validate --seed 0 --seed 1 --out docs/records/labelfix/spellcheck
"""
from __future__ import annotations
from greekocr.ops.data_root import input_path as _data_input
import argparse
from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import time
import os
import sys
import shlex

for _thread_var in ('VECLIB_MAXIMUM_THREADS', 'OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS'):
    os.environ.setdefault(_thread_var, '1')

from PIL import Image
import numpy as np

from .candidates import pair_tokens
from .constraints import ENCLITICS, syllables
from .ctc_align import transfer_alignment
from .ink import Blob, MarkEvidence, analyse, mark_evidence, slope_sign
from .lexicon import load_all
from .markshape import load_model
from .sheet import crop_key, load_alignments, render_spellcheck
from .spellink import evidence_abstention, judge_grave, locate, spell_ink_line
from .text import clusters, lexicon_key, nfc, nfd, tokenize
from .validate import DEV_BOOKS, TOOLKIT, lb95, load_three_way, truth_map

STAGES = ('D1', 'D2', 'L1', 'L2')
COLS = ('ACCEPT', 'HOLD')


def read_jsonl(path):
    with open(_data_input(path), encoding='utf-8') as f:
        return [json.loads(x) for x in f if x.strip()]


def write_jsonl(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def calibrate_contradict(model, path):
    # Read only DEV samples. The existing classifier was fitted on these books;
    # this is a dev operational choice, not a new independent accuracy estimate.
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        rows = [r for x in f if (r := json.loads(x))['doc'] in DEV_BOOKS]
    probs = model.probs(np.asarray([r['x'] for r in rows]))
    pred = probs.argmax(axis=1)
    conf = probs.max(axis=1)
    right = np.asarray([model.classes[i] == r['label'] for i, r in zip(pred, rows)])
    curve = []
    for t in (.90, .95, .98, .99, .995, .998, .999, 1.0):
        sel = conf >= t
        n = int(sel.sum())
        k = int(right[sel].sum())
        curve.append(dict(tau=t, n=n, correct=k, precision=k/n if n else None))
    viable = [r for r in curve if r['n'] >= 50 and r['precision'] >= .99]
    tau = viable[0]['tau'] if viable else 1.0
    return dict(tau_contradict=tau, source='DEV_BOOKS only; >=99% dev classification precision, >=50 samples',
                n_dev=len(rows), curve=curve)


def style_observations(line, al, ink):
    """Final vowel locations only: neither Google's accent type nor the model's type votes."""
    if nfd(al.prediction) != line['model']:
        al = transfer_alignment(line['model'], al)
    ts = tokenize(line['google'])
    ms = {g.index:m for g,m in pair_tokens(line['google'], line['model'])}
    stats = Counter()
    for g in ts[:-1]:
        nxt = ts[g.index + 1].core
        if g.trail or not nxt or lexicon_key(nxt) in ENCLITICS:
            continue
        ss = syllables(clusters(g.core))
        if not ss:
            continue
        # Last cluster of the last syllable (normal diphthong bearer).
        loc = locate(g, ms.get(g.index), al, ss[-1][-1])
        if loc is None:
            continue
        _, x0,x1,b0,b1 = loc
        ev = mark_evidence(ink,x0,x1,core_x0=b0,core_x1=b1)
        if evidence_abstention(ev) or ev.n_above != 1:
            continue
        sign = slope_sign(ev.above[0])
        if sign:
            stats[sign] += 1
    return stats


def dev_style_truth(lines):
    # Used ONLY for selecting the style thresholds on the declared dev books.
    out = defaultdict(Counter)
    from .spellink import final_accent_index
    for l in lines:
        if l['doc'] not in DEV_BOOKS:
            continue
        ts = tokenize(l['human'])
        for t in ts[:-1]:
            if t.trail or lexicon_key(ts[t.index+1].core) in ENCLITICS:
                continue
            i = final_accent_index(t.core)
            if i is not None:
                marks = clusters(t.core)[i].marks
                for ch, label in [('̀','grave'), ('́','acute')]:
                    if ch in marks:
                        out[l['doc']][label] += 1
    return {d: dict(c) for d,c in out.items()}


def style_of(counts, min_samples, share):
    n = counts.get('acute',0) + counts.get('grave',0)
    if n < min_samples:
        return 'unknown'
    for s in ('grave','acute'):
        if counts.get(s,0)/n >= share:
            return s
    return 'unknown'


def calibrate_style(stats, dev_truth):
    curve=[]
    for n in (3,5,10):
        for t in (.6,.7,.8,.9):
            correct=wrong=0
            for seed, books in stats.items():
                for d, h in dev_truth.items():
                    expected = max(h, key=h.get)
                    got = style_of(books.get(d,{}),n,t)
                    correct += got == expected
                    wrong += got not in ('unknown',expected)
            curve.append(dict(min_samples=n, share=t, correct=correct, wrong=wrong))
    # Maximise correct dev books with zero wrong; ties prefer the stricter supported setting.
    good=[c for c in curve if c['wrong']==0]
    best=max(good, key=lambda c:(c['correct'],c['share'],c['min_samples'])) if good else dict(min_samples=10,share=1.0)
    return dict(**best, dev_truth=dev_truth, curve=curve, source='DEV_BOOKS only; book truth from dev human midline accents')


def evidence_from_record(r):
    def blobs(xs):
        return [Blob(*x['bbox'], x['area'], x['source'], x['angle_deg'], x['elongation'],
                     x.get('darkness',0), x.get('faint',False), x.get('touches_border',False)) for x in xs]
    return MarkEvidence(blobs(r['above']),blobs(r['below']),tuple(r['window']),r['xh'],r['meanline'],r['baseline'],
                        tuple(r['body']),r['body_source'],r['n_letters_in_span'],r['neighbour_marks'],r['clipped_top'],r['clipped_bottom'])


def finalize_grave(r, style):
    r['book_style']=style
    if style == 'acute' and r['stage'] != 'D2':
        from .spellink import final_accent_index
        gi=final_accent_index(r['google_core'])
        gc=clusters(r['google_core'])
        for key in ('decision','ratio_decision'):
            d=r[key]
            form=d.get('proposal')
            if d['column'] and form and gi is not None:
                pc=clusters(nfd(form))
                if '́' in gc[gi].marks and '̀' in pc[gi].marks:
                    d.update(accept=False,column=None,reason='abstain:book_prints_acute',proposal=None)
                    if key=='decision':r['ink_verdict']='abstains'
    if r['stage']!='D2' or r['decision']['reason'].startswith('excluded:') or not r.get('ink'):
        return
    from .spellink import Proposal
    p = r['proposals'][0]
    i,gm,pm = p['changes'][0]
    prop = Proposal(nfd(p['form']),p['count'],i,gm,pm,p['cls'],tuple(p['changes']))
    ev = evidence_from_record(r['ink'])
    j = judge_grave(prop,ev,r['shape'],positional=r['d2_positional'],book_style=style)
    col = 'ACCEPT' if j.accept else None
    r['decision']=dict(accept=j.accept,column=col,reason=j.reason,proposal=p['form'] if col else None)
    r['ratio_decision']=dict(r['decision'])
    r['ink_verdict']='supports' if col else 'abstains'


def score(r,h):
    r['human_token']=h.text if h else None
    r['human_nfc']=nfc(h.text) if h else None
    r['human_word_index']=h.index if h else None
    def outcome(form):
        if h is None:
            return 'unknown'
        if form and nfd(form)==h.core:
            return 'correct'
        if r['google_core']==h.core:
            return 'google_right'
        return 'both_wrong'
    r['outcome']=outcome(r.get('proposal_core'))
    r['ratio_outcome']=outcome(r['ratio_decision'].get('proposal'))
    return r


def score_print(r, printed):
    """Score proposed form against print; null truth stays unknown, HOLD stays separate."""
    r['printed_core'] = printed
    def outcome(form):
        if printed is None:
            return 'unknown'
        if form and nfd(form) == nfd(printed):
            return 'correct'
        return 'google_right' if nfd(r['google_core']) == nfd(printed) else 'both_wrong'
    r['print_outcome'] = outcome(r['decision'].get('proposal'))
    r['ratio_print_outcome'] = outcome(r['ratio_decision'].get('proposal'))
    return r


def metrics(rows,col,policy='strict'):
    dk='decision' if policy=='strict' else 'ratio_decision'
    ok='outcome' if policy=='strict' else 'ratio_outcome'
    dd=[r for r in rows if r[dk]['column']==col]
    c=Counter(r[ok] for r in dd)
    n=c['correct']+c['google_right']+c['both_wrong']
    return dict(candidates=sum(bool(r['proposals'] if policy=='strict' else r['ratio_proposals']) for r in rows),decided=len(dd),tp=c['correct'],fp=c['google_right'],
                both_wrong=c['both_wrong'],unknown=c['unknown'],precision=c['correct']/n if n else None,lb95=lb95(c['correct'],n))


def pc(k,n):
    return f'{100*k/n:.1f}%' if n else '—'


def pm(m):
    return f"{100*m['precision']:.1f}%" if m['precision'] is not None else '—'


def write_report(out,results,universes,cal,styles,receipt):
    L=['# S1 — deterministic + lexicon-proposes / ink-decides', '',
       'Strict attestation is the default. ACCEPT and HOLD are always separate. CTC only locates: its reading is a diagnostic, never a proposal or a voting gate. Human text is used only for scoring and the declared dev calibration.', '',
       f"Run: `{receipt['command']}`. CPU, network off, **0 CTC forward passes**; {receipt['alignment_coverage']}. Elapsed including sheets: {receipt.get('elapsed_seconds', 'pending')} seconds.", '',
       'T1 is fixed: 185 non-human-text Google mark errors per seed (370 seed/error observations). Both seeds share images and reference text: pooled confidence bounds describe observations and do not imply independent replicated images.', '',
       '## Frozen thresholds and policies', '',
       f"`tau_contradict = {cal['contradiction']['tau_contradict']}` selected on DEV_BOOKS only: first threshold in the prespecified grid with ≥99% dev classifier precision and ≥50 samples. The existing shape model and ACCEPT tau=0.998 are reused without retraining. Its original tau was calibrated on the old held-out books; consequently S1 held-out results are book-separated for the new choices, not an untouched classifier calibration test. Dev samples were used to fit the existing classifier, so dev calibration is descriptive.", '',
       f"D2 book style uses only ink slopes over final vowels of midline words (no trailing punctuation, no following enclitic), regardless of Google's written accent. New threshold selected on DEV_BOOKS only: ≥{cal['style']['min_samples']} readable isolated accents, ≥{cal['style']['share']:.0%} one slope. Other books supply unlabeled ink to this frozen style detector. Mixed/insufficient books are unknown; they require an individual decisive grave slope. Acute books suppress all D2 grave changes.", '',
       'D1 tries attested constraint-valid mark variants first (including multi-cluster repairs); otherwise only a unique constraint-valid minimum mark edit. Every changed cluster must pass the ink checks. D1 overrides attestation only for impossible forms. D2 is positional only midline before non-enclitics; line ends and punctuation always require a decisive grave slope. In those slope-only contexts D2 applies only when its ink test passes; otherwise the lexical stages may propose a non-grave repair (final-acute/grave-only lexical proposals remain excluded). The failed D2 attempt is retained as a diagnostic. L1 uses written_freq and one-cluster alternatives; final acute/grave and initial-rho-only alternatives are excluded. L2 scans only Google vowel/rho clusters (including unmarked vowels) with an attested constraint-valid alternative, and always needs classifier tau plus physical checks. Ratio is a separate diagnostic policy: an attested alternative ≥20× the Google count can additionally trigger L1; it never changes strict decisions.', '',
       'HOLD requires exactly one D1/L1 proposal, existing image evidence, and no contradiction. A combined D1/L1 repair that also changes final acute to grave is still slope-only at punctuation or line end and cannot HOLD; acute-book suppression also covers combined repairs. It is forbidden for D2/L2, competing proposals and dialytika-only changes. On a readable, unmerged band, absent subscript, absent required two dots, clearly insufficient added above marks, or a confident classifier reading of Google contradicts. Faint, clipped, merged, neighbour and localisation failures abstain and permit HOLD. With no located image evidence HOLD abstains. All-caps, Latin/digits, hyphen line end, abbreviations and capitalised non-initial words stay guarded. Initial capitals require the proposed lower form ≥50 and name count <3.', '',
       'Calibration details and full grid: `calibration.json`; book ink counts and resulting style: `book_styles.json`. No held-out human label selects a new threshold.', '',
       '## Book styles', '', '| seed | book | split | acute slopes | grave slopes | style |','|---|---|---|---:|---:|---|']
    for s,books in styles.items():
        for d,c in sorted(books.items()):
            L.append(f"| {s} | {d} | {'dev' if d in DEV_BOOKS else 'held-out'} | {c.get('acute',0)} | {c.get('grave',0)} | {c['style']} |")
    L += ['', '## Stage × column precision', '', 'Candidates are words with lexical/deterministic alternatives before ink, including guarded candidates. L2 is a prefilter workload; only a differing classifier class at tau can decide. A word is counted once per stage; the two column candidate counts share that pool. Unknown references are excluded from precision. LB95 is validate.lb95, the exact one-sided 95% Clopper–Pearson lower bound.', '']
    for policy in ('strict','ratio'):
        for seed in list(results)+['both']:
            rows=results[seed] if seed!='both' else [r for rs in results.values() for r in rs]
            for split in ('dev','held-out','both'):
                sub=[r for r in rows if split=='both' or r['dev']==(split=='dev')]
                L += [f'### {policy} · seed {seed} · {split}', '', '| stage | column | candidates | decided | = human | Google-right FP | both-wrong | unknown | precision | LB95 |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
                for st in STAGES+('all',):
                    rr=sub if st=='all' else [r for r in sub if r['stage' if policy=='strict' else 'ratio_stage']==st]
                    for col in COLS:
                        m=metrics(rr,col,policy)
                        L.append(f"| {st} | {col} | {m['candidates']} | {m['decided']} | {m['tp']} | {m['fp']} | {m['both_wrong']} | {m['unknown']} | {pm(m)} | {100*m['lb95']:.1f}% |")
                L.append('')
    L += ['## Recall on fixed T1 universe', '', 'Old = unchanged cached rules.py strict ACCEPT; old+ink also includes its separate ink_decisive diagnostic. Union uses old+ink and S1 ACCEPT+HOLD. Corrections count only when they equal the T1 human core.', '', '| seed | split | T1 stage / model stratum | errors | ACCEPT | ACCEPT+HOLD | old | old+ink | union |','|---|---|---|---:|---:|---:|---:|---:|---:|']
    all_unreached=[]
    for seed in list(results)+['both']:
        rows=results[seed] if seed!='both' else [r for rs in results.values() for r in rs]
        uu=universes[seed] if seed!='both' else [e for es in universes.values() for e in es]
        by={(r['seed'],r['line_id'],r['word_index']):r for r in rows}
        for split in ('dev','held-out','both'):
            u=[e for e in uu if split=='both' or (e['doc'] in DEV_BOOKS)==(split=='dev')]
            labels=['all','model also wrong','model right']+sorted({e['stage'] for e in u})
            for label in labels:
                us=[e for e in u if label=='all' or label=='model also wrong' and not e['model_right'] or label=='model right' and e['model_right'] or e['stage']==label]
                counts=Counter()
                for e in us:
                    r=by.get((e['seed'],e['line_id'],e['word_index']))
                    hit=bool(r and r['decision']['column'] and r.get('proposal_core')==nfd(e['human']))
                    a=hit and r['decision']['column']=='ACCEPT'
                    counts['a']+=a;counts['ah']+=hit
                    old=(r or {}).get('old',{})
                    oldhit=old.get('proposal_core')==nfd(e['human'])
                    counts['old']+=bool(oldhit and old.get('accept'))
                    oi=bool(oldhit and (old.get('accept') or old.get('ink_decisive')))
                    counts['oi']+=oi;counts['union']+=hit or oi
                def cp(k): return f"{counts[k]} ({pc(counts[k],len(us))})"
                L.append(f"| {seed} | {split} | {label} | {len(us)} | {cp('a')} | {cp('ah')} | {cp('old')} | {cp('oi')} | {cp('union')} |")
        if seed!='both':
            for e in uu:
                r=by.get((seed,e['line_id'],e['word_index']))
                if r and r['decision']['column'] and r.get('proposal_core')==nfd(e['human']):
                    continue
                reason='missing engine word' if not r else r['decision']['reason']
                target_check = (r or {}).get('proposal_checks',{}).get(e['human'])
                if target_check and not (r or {}).get('decision',{}).get('reason','').startswith('excluded:'):
                    reason = 'target proposal: '+target_check['reason']
                elif r and r['proposals'] and not r['decision']['reason'].startswith('excluded:'):
                    reason += '; target absent from proposals'
                if r and r.get('d2_attempt'):
                    reason += '; D2 slope-only attempt: '+r['d2_attempt']
                if r and r['decision']['column']:
                    reason='decided_other_form: '+r['corrected_nfc']+'; '+reason
                all_unreached.append(dict(**e,engine_stage=r['stage'] if r else None,unreached_reason=reason,
                                          contradiction_reasons=r.get('contradiction_reasons',[]) if r else []))
    write_jsonl(out/'unreached.jsonl',all_unreached)
    L += ['', '### Ratio policy recall (diagnostic, separate from strict)', '',
          '| seed | split | stratum | errors | ratio ACCEPT | ratio ACCEPT+HOLD |',
          '|---|---|---|---:|---:|---:|']
    for seed in list(results)+['both']:
        rows=results[seed] if seed!='both' else [r for rs in results.values() for r in rs]
        uu=universes[seed] if seed!='both' else [e for es in universes.values() for e in es]
        by={(r['seed'],r['line_id'],r['word_index']):r for r in rows}
        for split in ('dev','held-out','both'):
            u=[e for e in uu if split=='both' or (e['doc'] in DEV_BOOKS)==(split=='dev')]
            for label in ['all','model also wrong','model right']+sorted({e['stage'] for e in u}):
                us=[e for e in u if label=='all' or label=='model also wrong' and not e['model_right'] or label=='model right' and e['model_right'] or e['stage']==label]
                aa=ah=0
                for e in us:
                    r=by.get((e['seed'],e['line_id'],e['word_index']))
                    d=(r or {}).get('ratio_decision',{})
                    hit=bool(d.get('column') and d.get('proposal')==e['human'])
                    ah+=hit;aa+=hit and d['column']=='ACCEPT'
                L.append(f'| {seed} | {split} | {label} | {len(us)} | {aa} ({pc(aa,len(us))}) | {ah} ({pc(ah,len(us))}) |')
    L += ['', '## False fires on correct Google words', '', '| seed | stage | column | word | proposal | line id |','|---|---|---|---|---|---|']
    fps=[]
    for rows in results.values():
        for r in rows:
            if r['decision']['column'] and r['outcome']=='google_right':
                fps.append(r)
                L.append(f"| {r['seed']} | {r['stage']} | {r['decision']['column']} | {r['google_nfc']} | {r['corrected_nfc']} | {r['line_id']} |")
    if not fps: L.append('| — | — | — | none | — | — |')
    L += ['', '### False-fire counts (strict / ratio, separate columns)', '', '| seed | policy | stage | ACCEPT FP | HOLD FP |','|---|---|---|---:|---:|']
    for s,rows in results.items():
        for policy in ('strict','ratio'):
            for st in STAGES:
                rr=[r for r in rows if r['stage' if policy=='strict' else 'ratio_stage']==st]
                L.append(f"| {s} | {policy} | {st} | {metrics(rr,'ACCEPT',policy)['fp']} | {metrics(rr,'HOLD',policy)['fp']} |")
    write_jsonl(out/'false_fires.jsonl',fps)
    L += ['', 'Ratio false-fire words (diagnostic):', '']
    for rows in results.values():
        for r in rows:
            if r['ratio_decision']['column'] and r['ratio_outcome']=='google_right':
                L.append(f"- s{r['seed']} {r['ratio_stage']} {r['ratio_decision']['column']} `{r['line_id']}` word {r['word_index']}: {r['google_nfc']} → {r['ratio_decision']['proposal']}")
    L += ['', '## Guards and abstentions', '', '| seed | stage | reason | words |','|---|---|---|---:|']
    for s,rows in results.items():
        cc=Counter((r['stage'],r['decision']['reason'].split(';')[0]) for r in rows if not r['decision']['column'])
        for (st,why),n in sorted(cc.items()): L.append(f'| {s} | {st} | {why} | {n} |')
    L += ['', 'D2 slope-only attempts before stage dispatch (failed attempts may continue to lexical stages):', '', '| seed | reason | attempts |', '|---|---|---:|']
    for seed,rows in results.items():
        for why,n in Counter(r['d2_attempt'] for r in rows if r.get('d2_attempt')).most_common():
            L.append(f'| {seed} | {why} | {n} |')
    L += ['', '## What each stage reaches; every unreached error', '',
          'D1 reaches hard-invalid spellings; D2 reaches final acute→grave in positional or slope-only contexts; L1 reaches unattested one-cluster spellings with a unique or ink-resolved lexical repair; L2 reaches attested real-word errors whose mark classifier contradicts Google. The following line IDs expose what each stage actually recovered. Guarded names, unattested targets, multi-cluster L1 changes, absent lexical variants and unreadable marks remain visible in unreached.jsonl.', '']
    for st in STAGES:
        hits=[r for rows in results.values() for r in rows if r['stage']==st and r['decision']['column'] and r['outcome']=='correct']
        L.append(f"- {st}: "+('; '.join(f"s{r['seed']} `{r['line_id']}` w{r['word_index']} {r['google_nfc']}→{r['corrected_nfc']} ({r['decision']['column']})" for r in hits) or 'no matching decisions'))
    L += ['', '| seed | T1 stage | line id / word | Google → human | engine stage | why unreached |','|---|---|---|---|---|---|']
    for e in all_unreached:
        why=e['unreached_reason'] + ('; contradiction='+','.join(e['contradiction_reasons']) if e['contradiction_reasons'] else '')
        L.append(f"| {e['seed']} | {e['stage']} | {e['line_id']} / {e['word_index']} | {e['google']} → {e['human']} | {e['engine_stage']} | {why} |")
    L += ['', '## Artifacts and verification', '',
          'Per-word records (including guards and no-proposal words): `words_s0.jsonl`, `words_s1.jsonl`. Every strict decision, true or false: `sheets/{D1,D2,L1,L2}.rows.jsonl` and self-contained v4 HTML. Reference CSS is copied verbatim. Each card contains the full crop, enlarged detector-mark raster, caption, Google / Human (test reference) / Tool table with the word highlighted, and stage / column / outcome pills. For unknown one-to-one human references the display-only aligned span is highlighted and labelled; scoring stays unknown. Ratio decisions are diagnostic columns in per-word rows and report tables; they are not folded into strict sheets.', '',
          'The 185-error instruments, Google labels, cached alignments and old rules are unchanged. The 4 known human-text errors are excluded from T1 recall only; precision tables retain the literal human-reference outcome, so a physically justified change can still be both-wrong against that reference. `run_receipt.json` records input hashes and timing. New thresholds use only DEV_BOOKS. Exact old decisions are read from the existing validation_candidates_s{seed}_strict.jsonl; no old-rule output is rewritten.', '']
    rows=[r for rs in results.values() for r in rs]
    ma,mh=metrics(rows,'ACCEPT'),metrics(rows,'HOLD')
    uu=[e for es in universes.values() for e in es]
    by={(r['seed'],r['line_id'],r['word_index']):r for r in rows}
    counts=Counter()
    for e in uu:
        r=by.get((e['seed'],e['line_id'],e['word_index']))
        hit=bool(r and r['decision']['column'] and r.get('proposal_core')==nfd(e['human']))
        counts['mw_n']+=not e['model_right']
        if hit:
            counts[r['decision']['column']]+=1
            counts['mw_a']+=not e['model_right'] and r['decision']['column']=='ACCEPT'
    l2=metrics([r for r in rows if r['stage']=='L2'],'ACCEPT')
    d2=metrics([r for r in rows if r['stage']=='D2'],'ACCEPT')
    last=(f"S1 RESULT: ACCEPT p={pm(ma)} (LB95 {100*ma['lb95']:.1f}%) recall {pc(counts['ACCEPT'],len(uu))} "
          f"(model-wrong {pc(counts['mw_a'],counts['mw_n'])}); HOLD p={pm(mh)} (LB95 {100*mh['lb95']:.1f}%) "
          f"+{pc(counts['HOLD'],len(uu))} recall; L2 {l2['decided']} ACCEPT/{l2['tp']} TP/{l2['fp']} FP; "
          f"D2 {d2['decided']} ACCEPT/{d2['tp']} TP/{d2['fp']} FP")
    qa_path=out/'verification.json'
    if qa_path.exists():
        qa=json.loads(qa_path.read_text())
        L += ['## Verification and limitations', '', qa['summary'], '']
    L += [last]
    (out/'S1_REPORT.md').write_text('\n'.join(L)+'\n',encoding='utf-8')
    return last


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed',type=int,action='append')
    ap.add_argument('--out',type=Path,default=TOOLKIT/'docs/records/labelfix/spellcheck')
    ap.add_argument('--shape-model',type=Path,default=TOOLKIT/'docs/records/labelfix/markshape_model.json')
    ap.add_argument('--samples',type=Path,default=TOOLKIT/'docs/records/labelfix/markshape_samples.jsonl.gz')
    ap.add_argument('--print-truth',type=Path)
    ap.add_argument('--no-sheets',action='store_true')
    a=ap.parse_args(argv)
    a.shape_model=a.shape_model.resolve()
    a.samples=_data_input(a.samples).resolve()
    start=time.monotonic()
    a.out=a.out.resolve()
    a.out.mkdir(parents=True,exist_ok=True)
    seeds=list(dict.fromkeys(a.seed or [0,1]))
    model=load_model(a.shape_model)
    lexicons=load_all(TOOLKIT/'docs/records/labelfix/lexicons')
    lines={s:load_three_way(s) for s in seeds}
    aligns={s:load_alignments(TOOLKIT/f'.cache/labelfix/align_s{s}.jsonl') for s in seeds}
    missing=[(s,l['line_id']) for s in seeds for l in lines[s] if crop_key(l['crop']) not in aligns[s]]
    if missing:
        (a.out/'S1_REPORT.md').write_text(f'# S1 blocked\nMissing cached alignments: {missing}. No forward pass attempted.\n')
        raise RuntimeError('missing alignment cache; see S1_REPORT.md')
    cal=dict(contradiction=calibrate_contradict(model,a.samples))
    regimes={s:{r['line_id']:r['regime'] for r in read_jsonl(TOOLKIT/f'docs/records/labelfix/validation_lines_s{s}.jsonl')} for s in seeds}
    old={s:{(r['line_id'],r['word_index']):r for r in read_jsonl(TOOLKIT/f'docs/records/labelfix/validation_candidates_s{s}_strict.jsonl')} for s in seeds}
    universes={s:[dict(e,seed=s) for e in read_jsonl(TOOLKIT/f'docs/records/labelfix/spellcheck/reach_s{s}.jsonl') if e['stage']!='human_error'] for s in seeds}
    assert all(len(u)==185 for u in universes.values()), 'T1 universe drift'
    byline={s:{l['line_id']:l for l in lines[s]} for s in seeds}
    results={s:[] for s in seeds}
    stats={s:defaultdict(Counter) for s in seeds}
    # One physical extraction per unique crop, shared across both seeds, then discarded.
    crops=defaultdict(list)
    for s in seeds:
        for l in lines[s]:
            if regimes[s][l['line_id']]!='mono': crops[l['crop']].append((s,l))
    for k,(crop,ls) in enumerate(crops.items()):
        with Image.open(crop) as im:
            ink=analyse(im)
        for s,l in ls:
            al=aligns[s][crop_key(crop)]
            stats[s][l['doc']].update(style_observations(l,al,ink))
            reg=regimes[s][l['line_id']]
            rows=spell_ink_line(l['line_id'],l['google'],l['model'],al,ink,lexicons[reg],model,
                tau_contradict=cal['contradiction']['tau_contradict'],
                extra=dict(seed=s,doc=l['doc'],dev=l['doc'] in DEV_BOOKS,regime=reg,crop_path=crop))
            truth=truth_map(l['google'],l['human'])
            ts=tokenize(l['google'])
            for r in rows:
                idx=r['word_index']
                r['d2_positional']=bool(idx+1<len(ts) and not ts[idx].trail)
                o=old[s].get((l['line_id'],idx))
                r['old']=dict(accept=o['decision']['accept'],ink_decisive=o['decision'].get('ink_decisive',False),
                    reason=o['decision']['reason'],rule=o['decision']['rule'],proposal_core=o['model_core']) if o else {}
                if r.get('proposal_core'):
                    r['proposal_count']=next((p['count'] for p in r['proposals'] if nfd(p['form'])==r['proposal_core']),0)
                results[s].append(score(r,truth.get(idx)))
        if k%200==0:
            print(f'[S1] {k}/{len(crops)} unique crops, {time.monotonic()-start:.1f}s',flush=True)
        if time.monotonic()-start>840:
            raise RuntimeError('S1 run approaching 15 min budget; stopped')
    dev_truth=dev_style_truth(lines[seeds[0]])
    cal['style']=calibrate_style(stats,dev_truth)
    styles={s:{d:dict(c,style=style_of(c,cal['style']['min_samples'],cal['style']['share'])) for d,c in ds.items()} for s,ds in stats.items()}
    from .linemetric import printed_words
    adjudicated=json.loads(a.print_truth.read_text()) if a.print_truth else None
    print_maps={s:{lid:printed_words(l,adjudicated) for lid,l in ls.items()} for s,ls in byline.items()} if adjudicated is not None else {}
    for s,rows in results.items():
        for r in rows:
            finalize_grave(r,styles[s].get(r['doc'],{}).get('style','unknown'))
            if r['stage']=='D2':
                h=truth_map(byline[s][r['line_id']]['google'],byline[s][r['line_id']]['human']).get(r['word_index'])
                score(r,h)
            if adjudicated is not None:
                score_print(r,print_maps[s][r['line_id']].get(r['word_index']))
        write_jsonl(a.out/f'words_s{s}.jsonl',rows)
    (a.out/'calibration.json').write_text(json.dumps(cal,ensure_ascii=False,indent=2)+'\n')
    (a.out/'book_styles.json').write_text(json.dumps(styles,ensure_ascii=False,indent=2)+'\n')
    sheetdir=a.out/'sheets';sheetdir.mkdir(exist_ok=True)
    for st in (() if a.no_sheets else STAGES):
        rr=[r for rows in results.values() for r in rows if r['stage']==st and r['decision']['column']]
        write_jsonl(sheetdir/f'{st}.rows.jsonl',rr)
        (sheetdir/f'{st}.html').write_text(render_spellcheck(rr,byline,f'S1 · {st} · all ACCEPT and HOLD'),encoding='utf-8')
    input_paths=[TOOLKIT/'greekocr/labelfix/rules.py',a.shape_model,TOOLKIT/'docs/records/harvest/collection/v2/import_real_v2_test.jsonl']
    input_paths += [TOOLKIT/'greekocr/labelfix/ink.py', TOOLKIT/'greekocr/labelfix/spellink.py', a.samples]
    if a.print_truth: input_paths.append(a.print_truth.resolve())
    input_paths += [TOOLKIT/f'.cache/labelfix/align_s{s}.jsonl' for s in seeds]+[TOOLKIT/f'docs/records/labelfix/spellcheck/reach_s{s}.jsonl' for s in seeds]
    receipt=dict(command='python -m greekocr.labelfix.spellcheck_validate '+shlex.join(argv if argv is not None else sys.argv[1:]),
        shape_model=str(a.shape_model),print_truth=str(a.print_truth),ctc_forward_passes=0,alignment_coverage={s:dict(lines=len(lines[s]),cached=len(aligns[s]),missing=0) for s in seeds},
        elapsed_seconds=round(time.monotonic()-start,2),cpu_only=True,input_sha256={str(p.relative_to(TOOLKIT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in input_paths})
    last=write_report(a.out,results,universes,cal,styles,receipt)
    receipt['elapsed_seconds']=round(time.monotonic()-start,2)
    (a.out/'run_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(last,flush=True)
    print(f'[S1] complete in {receipt["elapsed_seconds"]}s',flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
