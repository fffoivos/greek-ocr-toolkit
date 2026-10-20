"""R0c offline scoring. Reads frozen evidence; never imports/runs the recogniser.

Rates are conditional on adjudicated word cards, not whole-line/population CER.
Run with the R0 Python, PYTHONPATH=$PWD, and PYTHONDONTWRITEBYTECODE=1.
"""
from __future__ import annotations

import base64
from collections import Counter, defaultdict
import gzip
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import unicodedata as U

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/labelfix/spellcheck'
EV = OUT / 'R0_evidence/scoring'
LABELS = {
    'continuity_666': '666 = continuity instrument',
    'newsource': '(ii) = mark-enriched, not a population estimate',
    'wikisource_ia': '(i-a) = selection-exposed (v2 val)',
    'owner_DEV_supplement': 'owner DEV supplement; excluded from all strata',
}
APOS = "'’ʼ᾽`´"
QUOTES = '‘“”«»„"‟‹›′″'
SIGNS = APOS + QUOTES
STRATA = list(LABELS)[:3]


def read(p):
    with (gzip.open if str(p).endswith('.gz') else open)(p, 'rt') as f:
        return [json.loads(s) for s in f if s.strip()]


def dump(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def write(p, rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(r, ensure_ascii=False, allow_nan=False) + '\n' for r in rows))


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def bare(s):
    # Preserve spacing punctuation before NFD, notably U+1FBD spacing koronis.
    return ''.join(c for ch in (s or '').replace('∅', '') for c in
                   (ch if ch in SIGNS else U.normalize('NFD', ch))
                   if not U.category(c).startswith('M'))


def letter(c):
    return c.isalpha() and c not in SIGNS


def letters(s, unknown=False):
    return ''.join(c for c in bare(s) if letter(c) or (unknown and c == '?'))


def align(a, b, fold=False):
    """Unit edit path, reference then output. '?' is an explicitly masked glyph."""
    def cost(x, y):
        return 0 if x == '?' else int((x.casefold() if fold else x) !=
                                     (y.casefold() if fold else y))
    d = [list(range(len(b) + 1))] + [[i] + [0] * len(b) for i in range(1, len(a) + 1)]
    for i, x in enumerate(a, 1):
        for j, y in enumerate(b, 1):
            d[i][j] = min(d[i-1][j-1] + cost(x, y), d[i-1][j] + 1, d[i][j-1] + 1)
    i, j, path = len(a), len(b), []
    while i or j:
        if i and j and d[i][j] == d[i-1][j-1] + cost(a[i-1], b[j-1]):
            path.append((i-1, j-1)); i -= 1; j -= 1
        elif i and d[i][j] == d[i-1][j] + 1:
            path.append((i-1, None)); i -= 1
        else:
            path.append((None, j-1)); j -= 1
    return list(reversed(path))


def distance(a, b, fold=False):
    return sum(1 for i, j in align(a, b, fold)
               if (i is None or a[i] != '?') and
               (i is None or j is None or
                (a[i].casefold() if fold else a[i]) != (b[j].casefold() if fold else b[j])))


def script(c):
    n = U.name(c or ' ', '')
    return 'Greek' if 'GREEK' in n else 'Latin' if 'LATIN' in n else 'other'


def pct(n, d):
    return 100 * n / d if d else None


def strata_row(s, **kw):
    return dict(stratum=s, stratum_label=LABELS[s], **kw)


def load():
    lines = {}
    for path, s in [('R0_evidence/continuity_666.jsonl', 'continuity_666'),
                    ('R0_newsource_locked.jsonl', 'newsource'),
                    ('R0_locked_set.jsonl', 'wikisource_ia')]:
        for r in read(OUT / path):
            lines[r['line_id']] = dict(r, stratum=s)
    for r in read(ROOT/'.cache/labelfix/r0/align_locked_ia.jsonl'):
        lines[r['line_id']]['model'] = r['alignment']['prediction']
    # Only this explicitly requested DEV witness; no other worktree traversal.
    l = next(r for r in read(OUT / 'R0_evidence/owner_letter_punctuation_evidence.jsonl')
             if r.get('recorded_model') and 'ξa' in r['recorded_model'])
    k = next(r for r in json.loads((OUT/'R0_adjudication_private/items_key.json').read_text())
             if 'owner_Latin_a_witness' in r['kinds'])
    # Full-line pixels and references already bound in the blind deck / word census.
    lines[l['line_id']] = dict(line_id=l['line_id'], stratum='owner_DEV_supplement',
        doc='wikisource:02a3a2a6', model=U.normalize('NFD', l['recorded_model']),
        google=None, human=None, crop=str(OUT/'R0_cards'/k['line_img']))
    previous=(OUT/'R0_review_positions.html').read_text()
    article=re.search(r'<article data-line="'+re.escape(l['line_id'])+r'".*?</article>',previous,re.S).group()
    lines[l['line_id']]['google']=html.unescape(re.search(r'<p>Google</p><div class="text">(.*?)</div>',article,re.S).group(1))
    cards = []
    for suffix, keypath in [('', 'R0_adjudication_private/items_key.json'),
                            ('_ia', 'R0_adjudication_private/ia/items_key.json')]:
        ks = json.loads((OUT/keypath).read_text())
        ts = {r['id']:r for r in json.loads((OUT/f'R0_expected_truth{suffix}.json').read_text())}
        assert len(ts) == len(ks) and set(ts) == {r['id'] for r in ks}
        for k in ks:
            t = ts[k['id']]; a = t['adjudicated']
            truth = a.get('transcription')
            if truth is None and a.get('choice') in ['A', 'B', 'C']:
                truth = k[a['choice']]
            if a['status'] == 'UNRESOLVED':
                assert a.get('transcription') is None
                truth = None
            if a.get('choice') in ['A', 'B', 'C'] and truth is not None:
                assert bare(truth) == bare(k[a['choice']]), k['id']
            if k['control']:
                assert a['status'] == 'CONTROL' and bare(truth) == bare(k['known_answer'])
                for reader in ['reader_1', 'reader_2']:
                    r = t[reader]
                    answer = r.get('transcription') if r.get('transcription') is not None else k.get(r['choice'])
                    assert bare(answer) == bare(k['known_answer']), (k['id'], reader)
            cards.append(dict(k, truth=bare(truth) if truth is not None else None,
                              truth_status=a['status'], reader_record=t,
                              stratum=lines[k['line_id']]['stratum']))
    assert Counter(c['truth_status'] for c in cards) == dict(AGREED=956, CONTROL=86,
                                                          MAJORITY_OF_3=14, UNRESOLVED=2)
    assert not [c for c in cards for r in ['reader_1','reader_2']
                if c['reader_record'][r].get('full_line_letters')]
    return lines, cards


def training_evidence():
    path = ROOT / 'docs/harvest/collection/v2/import_real_v2_train.jsonl'
    original = json.loads((OUT/'R0_evidence/training_label_frequencies.json').read_text())
    assert sha(path) == original['sha256']
    counts = Counter(); rows = Counter(); by_script = defaultdict(Counter); n = 0
    # A streaming manifest count only. No data rewrite / inference / training.
    with open(path) as f:
        for raw in f:
            r = json.loads(raw); text = bare(r['label']); n += 1
            counts.update(text); rows.update(set(text)); by_script[r['script_class']].update(text)
    assert n == original['lines'] == 214436
    d = dict(path=str(path), sha256=original['sha256'], rows=n,
             symbols={c:dict(occurrences=counts[c], lines=rows[c],
                       by_script={s:v[c] for s,v in by_script.items()}) for c in sorted(counts)},
             original_symbol_frequencies='R0_evidence/training_label_frequencies.json',
             scope='manifest labels, not a receipt of E3 examples actually consumed')
    dump(EV/'training_frequencies.json', d)
    return d


def letter_scores(lines, cards, frequencies):
    units = []; failures = []; unknowns = []
    for c in cards:
        # Word cards certify word letters. Case/punctuation probes certify only
        # their requested attribute, not the forced anchor's letter identity.
        if c['control'] or 'model_words' not in c:
            continue
        s = c['stratum']; l = lines[c['line_id']]
        stream = 'native_cached_variant' if c.get('model_variant') else 'stored_instrument'
        if c['truth'] is None:
            unknowns.append(dict(card_id=c['id'], line_id=c['line_id'], stratum=s,
                                 reason='UNRESOLVED whole card', scope='word letters and punctuation'))
            continue
        ref = letters(c['truth'], unknown=True); hyp = letters(c['forms']['model'])
        offsets = [i for i in range(c['start'], c['end'])
                   if letter(U.normalize('NFD', c.get('locator_text', l['model']))[i])]
        assert len(offsets) == len(hyp), c['id']
        google = letters(c['forms'].get('google', ''))
        gp = align(ref, google)
        gmap = {i:(google[j] if j is not None else None) for i,j in gp if i is not None}
        ginsert = Counter()
        for pi, (i,j) in enumerate(gp):
            if i is None:
                boundary = next((ii for ii,jj in gp[pi+1:] if ii is not None), len(ref))
                ginsert[(boundary,google[j])] += 1
        errors = Counter(); path = align(ref,hyp)
        for pi, (i,j) in enumerate(path):
            expected = ref[i] if i is not None else None
            actual = hyp[j] if j is not None else None
            if expected == '?':
                unknowns.append(dict(card_id=c['id'],line_id=c['line_id'],stratum=s,
                                     slot=offsets[j] if j is not None else None,
                                     reason='MAJORITY_OF_3 retains explicit ?; glyph UNKNOWN'))
                continue
            if expected == actual:
                continue
            typ = ('insertion' if i is None else 'deletion' if j is None else
                   'case' if expected.casefold() == actual.casefold() else
                   'script_mixup' if script(expected) != script(actual) and
                   {script(expected),script(actual)} == {'Greek','Latin'} else 'substitution')
            errors[typ] += 1
            boundary = i if i is not None else next((ii for ii,jj in path[pi+1:] if ii is not None),len(ref))
            google_correct = gmap.get(i) == expected if i is not None else not ginsert[(boundary,actual)]
            verdict = 'MODEL' if google_correct else 'DATA'
            nearby = j if j is not None else next((jj for ii,jj in path[pi+1:] if jj is not None),len(hyp))
            slot = offsets[nearby] if nearby < len(offsets) else c['end']
            failures.append(strata_row(s, type=typ, DATA_MODEL=verdict,
                status='CONFIRMED_ADJUDICATED', line_id=c['line_id'], doc=l['doc'],
                source=l.get('source', l['doc']), slot=slot,
                slot_kind='NFD output index' if j is not None else 'NFD insertion boundary (missing printed letter)',
                card_id=c['id'], prediction_stream=stream, expected=expected, emitted=actual,
                google_at_truth_slot=gmap.get(i), google_correct=google_correct,
                evidence=dict(print_truth=c['truth_status'], truth_word=c['truth'],
                    recogniser_word=c['forms']['model'], google_word=c['forms'].get('google'),
                    training_expected=frequencies['symbols'].get(expected),
                    classification_rule='DATA when paired Google label also disagrees with print; MODEL when paired Google label is correct',
                    causal_limit='route for the training track; held-out Google error is not proof that this exact bad label was consumed by E3')))
        kept = sum(errors.values()); folded = distance(ref,hyp,True)
        assert kept == distance(ref,hyp)
        assert folded == kept-errors['case'], (c['id'], ref,hyp,errors,folded)
        units.append(strata_row(s,card_id=c['id'],line_id=c['line_id'],doc=l['doc'],
            source=l.get('source',l['doc']),prediction_stream=stream,
            start=c['start'],end=c['end'],truth=c['truth'],recogniser=c['forms']['model'],
            truth_slots=sum(ch!='?' for ch in ref),unknown_glyphs=ref.count('?'),
            errors=kept,errors_case_folded=folded,by_type=dict(errors)))
    # All primary word windows are disjoint within a prediction stream.
    windows = defaultdict(list)
    for u in units:
        windows[(u['line_id'],u['prediction_stream'])].append((u['start'],u['end']))
    for key,v in windows.items():
        v.sort(); assert all(a[1] <= b[0] for a,b in zip(v,v[1:])), (key,v)
    def aggregate(us):
        den=sum(u['truth_slots'] for u in us);err=sum(u['errors'] for u in us)
        fold=sum(u['errors_case_folded'] for u in us); types=Counter()
        for u in us:types.update(u['by_type'])
        return dict(cards=len(us),lines=len({u['line_id'] for u in us}),truth_slots=den,
                    errors=err,errors_case_folded=fold,letter_error_pct=pct(err,den),
                    letter_error_case_folded_pct=pct(fold,den),by_type=dict(types),
                    full_line_letter_error_pct=None,full_line_letter_error_case_folded_pct=None)
    summary=[]; bysource=[]
    for s in LABELS:
        us=[u for u in units if u['stratum']==s and u['prediction_stream']=='stored_instrument']
        summary.append(strata_row(s,**aggregate(us)))
        for group in ['doc', 'source'] if s=='newsource' else ['doc']:
            for src in sorted({(l['doc'] if group=='doc' else l.get('source',l['doc']))
                               for l in lines.values() if l['stratum']==s}):
                bysource.append(strata_row(s,grouping='book_document' if group=='doc' else 'source',
                    source=src,**aggregate([u for u in us if u[group]==src])))
    variants=[u for u in units if u['prediction_stream']=='native_cached_variant']
    write(EV/'letter_units.jsonl',units)
    write(EV/'unknowns.jsonl',unknowns)
    return summary,bysource,dict(scope='ten native-cache variant cards only; not the complete native-cache error rate',
                               **aggregate(variants)),failures,unknowns,units


def case_scores(cards):
    receipt=json.loads((OUT/'R0_evidence/case_sampling_receipt.json').read_text())
    rows=[]
    for c in cards:
        if 'case_disagreement' not in c['kinds']:continue
        assert c['truth'] in c['forms'].values()
        rows.append(strata_row(c['stratum'],card_id=c['id'],line_id=c['line_id'],
            doc=c['case_reference']['doc'],slot=c['frozen_slot'],
            recogniser_right=c['truth']==c['forms']['recogniser'],
            S5_pixel_right=c['truth']==c['forms']['S5_pixel'],
            scope='case only; candidate body identity is not newly certified'))
    bybook=[]; total=0;var=0
    for book,N in sorted(receipt['population_by_book'].items()):
        rr=[r for r in rows if r['doc']==book];n=len(rr);a=sum(r['recogniser_right'] for r in rr)
        assert n==receipt['sample_by_book'][book]
        total+=N*a/n
        # Unbiased stratified SRS variance. A zero plug-in variance with all
        # successes is not an informative confidence interval.
        if n>1:var+=N*N*(1-n/N)*(a/n)*(1-a/n)/(n-1)
        bybook.append(strata_row('continuity_666',doc=book,population=N,sampled=n,
                      recogniser_right=a,S5_pixel_right=n-a,extrapolated_right=N*a/n))
    write(EV/'case_scored_160.jsonl',rows)
    return dict(stratum='continuity_666',stratum_label=LABELS['continuity_666'],population=753,
        sampled=160,recogniser_right=sum(r['recogniser_right'] for r in rows),S5_pixel_right=0,
        unknown=0,weighted_recogniser_right_pct=100*total/753,extrapolated_recogniser_right=total,
        extrapolated_S5_pixel_wrong=total,by_book=bybook,
        estimator='sum_h N_h * recogniser_right_h/n_h; N=753',
        plug_in_standard_error_count=var**0.5,
        confidence_interval=None,uncertainty='All 160 successes yield zero plug-in variance, not certainty on all 753. No 753/753 pixel-truth claim.',
        locator_caveat='item00818 frozen slot 7 offers Ο/ο while NFD start 6 is Τ; this cohort certifies uppercase case only, not body identity or its text index.')


def punct_maps(text, model):
    """Signs mapped onto letter boundaries; alternate apostrophe shapes retained."""
    text=bare(text); model=letters(model); ls=letters(text)
    path=align(model,ls,True); mp={j:i for i,j in path if i is not None and j is not None}
    out=defaultdict(list);n=0
    for ch in text:
        if letter(ch):n+=1
        elif ch in SIGNS:
            boundary=(mp[n-1]+1 if n-1 in mp else mp[n] if n in mp else
                      (0 if n==0 else len(model)))
            out[boundary].append(ch)
    return dict(out)


def role(ch, c):
    if not ch:return 'absent'
    if ch not in APOS:return 'quote'
    if ch in "'’":
        notes=' '.join(c['reader_record'][r].get('note') or '' for r in ['reader_1','reader_2']).lower()
        # A closing single quote can have the same glyph as an elision.
        if any(w in notes for w in ['closing quote','closing single','close quote','single closing','end quote']):
            return 'quote'
    return 'apostrophe_elision'


def punct_scores(lines,cards,freq):
    observations=defaultdict(list); wordcards=[]; unresolved=[]; rejected_quotes=[]; masked_sites=set()
    fullmaps={}
    for lid,l in lines.items():
        fullmaps[lid]={src:punct_maps(l[src],l['model']) if l.get(src) is not None else None
                       for src in ['model','google','human']}
    for c in cards:
        if c['control'] or c.get('model_variant') or c['stratum']=='owner_DEV_supplement':continue
        if c['truth'] is None:
            unresolved.append(c['id'])
            if 'model_words' in c:
                before=len(letters(U.normalize('NFD',lines[c['line_id']]['model'])[:c['start']]))
                for form in c['forms'].values():
                    for boundary, signs in punct_maps(form,c['forms']['model']).items():
                        for rank in range(len(signs)):masked_sites.add((c['line_id'],before+boundary,rank))
            continue
        l=lines[c['line_id']]; forms=c['forms']; kinds=c['kinds']
        before=len(letters(U.normalize('NFD',l['model'])[:c['start']]))
        base=dict(card_id=c['id'],line_id=c['line_id'],stratum=c['stratum'],doc=l['doc'])
        if 'model_words' in c:
            maps={src:punct_maps(forms[src],forms['model']) if src in forms else None
                  for src in ['model','google','human']}
            truthmap=punct_maps(c['truth'],forms['model'])
            boundaries=set(truthmap)
            for m in maps.values():boundaries.update(m or {})
            wordcards.append((c,before,truthmap,maps))
            for b in sorted(boundaries):
                for rank in range(max([len(truthmap.get(b,[]))]+[len((m or {}).get(b,[])) for m in maps.values()])):
                    get=lambda m:(m or {}).get(b,[])[rank] if len((m or {}).get(b,[]))>rank else ''
                    ch=get(truthmap)
                    observations[(c['line_id'],before+b,rank)].append(dict(base,
                        printed=ch,printed_role=role(ch,c),
                        emitted={src:get(m) if m is not None else None for src,m in maps.items()}))
        elif any(t in kinds for t in ['S4_apostrophe_candidate','M2_apostrophe_candidate','S4_opening_quote_candidate']):
            signs=[ch for ch in c['truth'] if ch in SIGNS]
            ch=signs[0] if signs else ''
            if 'S4_opening_quote_candidate' in kinds and not ch:
                # These are physical component probes, sometimes breathing on
                # an interior letter. Their key start=0 is a crop locator, NOT
                # a claim about punctuation at the beginning of the line.
                rejected_quotes.append(dict(card_id=c['id'],line_id=c['line_id'],bbox=c['bbox'],
                    truth='no punctuation at this component',stratum=c['stratum']))
                continue
            b=0 if 'S4_opening_quote_candidate' in kinds else before+len(letters(forms['no_sign']))
            em={src:(m.get(b,[''])[0] if m is not None else None) for src,m in fullmaps[c['line_id']].items()}
            observations[(c['line_id'],b,0)].append(dict(base,printed=ch,printed_role=role(ch,c),emitted=em))
    # A complete word card also certifies absence at any anchor site inside it.
    for c,before,tm,maps in wordcards:
        for key,oo in list(observations.items()):
            lid,b,rank=key
            if lid!=c['line_id'] or any(o['card_id']==c['id'] for o in oo):continue
            local=b-before;nletters=len(letters(c['forms']['model']))
            if not (0<=local<=nletters):continue
            # Boundaries at the edge belong only when the whole word has that
            # edge (the key's word scope includes its terminal punctuation).
            if local==0 and b!=0:continue
            ch=(tm.get(local,[])+['']*(rank+1))[rank]
            get=lambda m: ((m or {}).get(local,[])+['']*(rank+1))[rank]
            oo.append(dict(card_id=c['id'],line_id=lid,stratum=c['stratum'],doc=lines[lid]['doc'],
                           printed=ch,printed_role=role(ch,c),
                           emitted={src:get(m) if m is not None else None for src,m in maps.items()}))
    events=[];failures=[]
    for (lid,b,rank),oo in sorted(observations.items()):
        l=lines[lid];roles={o['printed_role'] for o in oo};shape={o['printed'] for o in oo}
        # Conflicting adjudicated scopes remain UNKNOWN, never priority-voted.
        status=('UNKNOWN_UNRESOLVED_CARD' if (lid,b,rank) in masked_sites else
                'KNOWN' if len(roles)==1 else 'UNKNOWN_CONFLICT')
        emitted={}; emission_conflicts=[]
        for src in ['model','google','human']:
            vals={o['emitted'][src] for o in oo if o['emitted'][src] is not None}
            emitted[src]=next(iter(vals)) if len(vals)==1 else None
            if len(vals)>1:emission_conflicts.append(src)
        event=strata_row(l['stratum'],line_id=lid,doc=l['doc'],letter_boundary=b,rank=rank,
            status=status,printed_role=next(iter(roles)) if status=='KNOWN' else None,
            printed_shapes=sorted(shape),emitted=emitted,card_ids=sorted({o['card_id'] for o in oo}),
            emission_conflicts=emission_conflicts,observations=oo)
        events.append(event)
        if status!='KNOWN' or emitted['model'] is None:continue
        printed=event['printed_role']; actual=emitted['model']; gp=emitted['google']
        is_apo=printed=='apostrophe_elision';positive=printed!='absent'
        same_function=lambda ch: bool(ch) and ((ch in APOS) if is_apo else True)
        typ=None
        if positive and not actual:typ='apostrophe_omission' if is_apo else 'quote_omission'
        elif not positive and actual:typ='spurious_apostrophe_or_quote'
        elif positive and not same_function(actual):typ='punctuation_function_confusion'
        elif positive and actual not in shape:typ='apostrophe_shape' if is_apo else 'quote_shape'
        if typ:
            google_correct=(same_function(gp) if positive else gp=='') if gp is not None else None
            # Shape failures use exact adjudicated shape, not function.
            if typ.endswith('_shape'):google_correct=gp in shape if gp is not None else None
            verdict='MODEL' if google_correct else 'DATA'
            failures.append(strata_row(l['stratum'],type=typ,DATA_MODEL=verdict,
                status='CONFIRMED_ADJUDICATED',line_id=lid,doc=l['doc'],source=l.get('source',l['doc']),
                slot=b,slot_kind='letter boundary (punctuation)',prediction_stream='stored_instrument',
                expected=sorted(shape),emitted=actual,google=gp,card_ids=event['card_ids'],
                evidence=dict(print_role=printed,google_correct=google_correct,
                    training_symbols={ch:freq['symbols'].get(ch,dict(occurrences=0,lines=0)) for ch in shape if ch},
                    classification_rule='DATA when paired Google label omits/misencodes adjudicated sign; MODEL when Google is correct',
                    causal_limit='paired held-out label evidence; no assertion that the exact label was consumed by E3')))
    summary=[]
    for s in STRATA:
        evs=[e for e in events if e['stratum']==s]
        for r in ['apostrophe_elision','quote']:
            pos=[e for e in evs if e['status']=='KNOWN' and e['printed_role']==r]
            counts={}
            for src in ['model','google','human']:
                available=[e for e in pos if e['emitted'][src] is not None]
                present=[e for e in available if e['emitted'][src] and
                         (r=='quote' or e['emitted'][src] in APOS)]
                counts[src]=dict(printed_with_reference=len(available),emitted_same_function=len(present),
                    emitted_pct=pct(len(present),len(available)),
                    exact_printed_shape=sum(e['emitted'][src] in e['printed_shapes'] for e in available))
            summary.append(strata_row(s,kind=r,printed=len(pos),systems=counts,
                candidate_sites=len(evs),unknown_conflicts=sum(e['status']!='KNOWN' for e in evs)))
    write(EV/'punctuation_sites.jsonl',events)
    write(EV/'rejected_opening_quote_probes.jsonl',rejected_quotes)
    return summary,failures,dict(unresolved_cards=unresolved,
        unresolved_punctuation_boundaries=[list(k) for k in sorted(masked_sites)],
        rejected_physical_opening_quote_probes=len(rejected_quotes),
        conflicting_sites=[dict(line_id=e['line_id'],letter_boundary=e['letter_boundary'],card_ids=e['card_ids'])
                           for e in events if e['status']!='KNOWN'],
        emission_conflicts=[dict(line_id=e['line_id'],letter_boundary=e['letter_boundary'],systems=e['emission_conflicts'])
                            for e in events if e['emission_conflicts']])


def spans_and_geometry(lines):
    slots=read(OUT/'R0_evidence/span_slots.jsonl.gz')+read(OUT/'R0_evidence/ia/span_slots.jsonl.gz')
    failures=[]
    for r in slots:
        typ=('span_outside_blob' if r['outside_blob'] else
             r['status'] if r['status']!='clean_one_blob_one_character' else None)
        if not typ:continue
        failures.append(strata_row(r['stratum'],type=typ,DATA_MODEL='MODEL',
            status='GEOMETRY_DIAGNOSTIC',line_id=r['line_id'],doc=r['doc'],slot=r['slot'],
            slot_kind='native recogniser alphabetic slot ordinal',prediction_stream='native_cached',
            evidence=dict(r,classification_rule='MODEL/runtime localisation and component ownership; text-label symbol frequency cannot repair this mapping',
                          causal_limit='not an adjudicated letter error; shared/split connected components can be legitimate print')))
    for r in read(OUT/'R0_evidence/R1_unmapped_715.jsonl'):
        failures.append(strata_row('continuity_666',type='R1_frozen_mapping_omission',DATA_MODEL='MODEL',
            status='GEOMETRY_DIAGNOSTIC',line_id=r['line_id'],doc=lines[r['line_id']]['doc'],slot=r['slot'],
            slot_kind='historical frozen S4 sample slot',prediction_stream='historical_S4_mapping',
            evidence=dict(r,classification_rule='MODEL/runtime frozen mapper rejects unlocated/shared ownership; not a missing training-label character')))
    rows=[]
    for s in STRATA:
        ss=[r for r in slots if r['stratum']==s]
        for dimension in ['all','script_class','size_bucket']:
            for val in (['all'] if dimension=='all' else sorted({r[dimension] for r in ss})):
                rs=ss if dimension=='all' else [r for r in ss if r[dimension]==val]
                clean=[r for r in rs if r['status']=='clean_one_blob_one_character']
                outside=sum(bool(r['outside_blob']) for r in clean)
                rows.append(strata_row(s,dimension=dimension,bucket=val,all_slots=len(rs),clean=len(clean),
                            outside=outside,outside_pct=pct(outside,len(clean)),statuses=dict(Counter(r['status'] for r in rs))))
    return rows,failures


def failure_summary(failures):
    result=[]
    for s in LABELS:
        rr=[r for r in failures if r['stratum']==s]
        for typ,verdict,stream in sorted({(r['type'],r['DATA_MODEL'],r['prediction_stream']) for r in rr}):
            rs=[r for r in rr if r['type']==typ and r['DATA_MODEL']==verdict and r['prediction_stream']==stream]
            examples=sorted({r['line_id'] for r in rs})
            result.append(strata_row(s,type=typ,DATA_MODEL=verdict,prediction_stream=stream,count=len(rs),lines=len(examples),
                example_line_ids=examples[:3],example_requirement='met' if len(examples)>=3 else
                f'only {len(examples)} observed line(s); no invented examples',
                interpretation='diagnostic slots, not confirmed text errors' if rs[0]['status']=='GEOMETRY_DIAGNOSTIC' else
                'adjudicated output errors (shape errors distinct from omissions)'))
    return result


def review(lines,failures,case,cards):
    pools=defaultdict(list)
    for f in failures:pools[(f['stratum'],f['type'],f['DATA_MODEL'])].append(f['line_id'])
    for r in case['by_book']:
        lid=next(c['line_id'] for c in cards if 'case_disagreement' in c['kinds'] and c['case_reference']['doc']==r['doc'])
        pools[('continuity_666','S5_pixel_case_wrong','MODEL')].append(lid)
    for k in pools:pools[k]=sorted(set(pools[k]))
    chosen=[]
    for i in range(60):
        for key,ls in sorted(pools.items()):
            if i<len(ls) and ls[i] not in chosen:chosen.append(ls[i])
            if len(chosen)==60:break
        if len(chosen)==60:break
    assert len(chosen)<=60 and all(set(ls)&set(chosen) for ls in pools.values())
    cache={r['crop']:r['alignment'] for r in read(ROOT/'.cache/labelfix/align_s0.jsonl')}
    for path in [OUT/'R0_evidence/align_locked_s0.jsonl',ROOT/'.cache/labelfix/r0/align_locked_ia.jsonl']:
        for r in read(path):cache[r['crop']]=r['alignment']
    parts=['''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>R0c adjudicated recogniser review</title><style>
body{margin:20px;background:#f4f2ed;color:#211e18;font:16px system-ui}main{max-width:1200px;margin:auto}
article{padding:15px;margin:20px 0;background:white;border:1px solid #ccc}h1{font-size:28px}h2{font-size:18px;overflow-wrap:anywhere}
.crop{overflow-x:auto;padding-top:22px}.crop svg{display:block;max-width:none}.text{font:22px Georgia;overflow-wrap:anywhere}
small,p{overflow-wrap:anywhere}textarea{box-sizing:border-box;width:100%;height:70px}label{display:block;margin-top:12px}
.badge{display:inline-block;background:#eee7dc;padding:4px 8px;margin:3px;font-size:13px}@media(max-width:600px){body{margin:8px}article{padding:10px}}
</style><main><h1>R0c adjudicated recogniser review</h1>
<p>60 lines covering every observed failure type and stratum. Thin red boxes are native cached CTC letter spans.
Google and human are references; adjudicated card truth covers only the listed word/attribute windows. No full line is certified.
Geometry entries are diagnostics. Stored text is shown separately when it differs from native CTC. Draft page; the track lead publishes.</p>
<button id="export">Export owner notes</button>''']
    selection=[]
    key_by_line=defaultdict(list)
    for c in cards:
        if not c['control']:key_by_line[c['line_id']].append(c)
    for lid in chosen:
        l=lines[lid];crop=l['crop'];al=cache.get(crop)
        if al is None and l['stratum']=='continuity_666':
            tail='/'.join(Path(crop).parts[-2:])
            matches=[v for k,v in cache.items() if k.endswith(tail)]
            assert len(matches)==1,(lid,len(matches))
            al=matches[0]
        if al is None and l['stratum']=='owner_DEV_supplement':
            al=next(v for k,v in cache.items() if k.endswith('/p000318-l0017.png') and '/02a3a2a6/' in k)
        assert al is not None,lid
        with Image.open(crop) as im:w,h=im.size
        encoded=base64.b64encode(Path(crop).read_bytes()).decode()
        cats=sorted({f['DATA_MODEL']+' '+f['type'] for f in failures if f['line_id']==lid})
        if any('case_disagreement' in c['kinds'] for c in key_by_line[lid]):cats.append('MODEL S5_pixel_case_wrong (recogniser right)')
        parts.append(f'<article id="{html.escape(lid)}"><h2>{html.escape(lid)}</h2><p>{html.escape(LABELS[l["stratum"]])}</p>')
        parts.append(''.join(f'<span class="badge">{html.escape(c)}</span>' for c in cats))
        parts.append(f'<div class="crop"><svg role="img" aria-label="Line crop with native recogniser letter spans" width="{w}" height="{h+23}" viewBox="0 -23 {w} {h+23}"><image href="data:image/png;base64,{encoded}" x="0" y="0" width="{w}" height="{h}"/>')
        for ch,f0,f1,x0,x1 in al['spans']:
            if not letter(ch):continue
            parts.append(f'<rect x="{x0}" y="0" width="{max(.1,x1-x0):.2f}" height="{h}" fill="none" stroke="#ba463f" stroke-width=".6"/><text x="{(x0+x1)/2:.2f}" y="-5" text-anchor="middle" font-size="13" fill="#702a25">{html.escape(ch)}</text>')
        parts.append('</svg></div>')
        for label,text in [('Google',l.get('google')),('Recogniser — native cached CTC',al['prediction']),
                           ('Recogniser — stored instrument',l['model'] if l['model']!=al['prediction'] else None),
                           ('Human reference',l.get('human'))]:
            if text is not None:parts.append(f'<p>{label}</p><div class="text">{html.escape(U.normalize("NFC",text))}</div>')
        truth='; '.join(c['id']+': '+(c['truth'] if c['truth'] is not None else 'UNKNOWN') for c in key_by_line[lid])
        parts.append(f'<p><small>Adjudicated card windows: {html.escape(truth)}</small></p>')
        parts.append(f'<label>Owner note<textarea data-id="{html.escape(lid)}" placeholder="Letters, case, apostrophe or span position"></textarea></label></article>')
        selection.append(strata_row(l['stratum'],line_id=lid,categories=cats,native_prediction=al['prediction'],stored_prediction=l['model']))
    parts.append('''</main><script>
const key='r0c-owner-notes-v1';let notes={};try{notes=JSON.parse(localStorage.getItem(key)||'{}')}catch(e){}
for(const t of document.querySelectorAll('textarea')){t.value=notes[t.dataset.id]||'';t.oninput=()=>{notes[t.dataset.id]=t.value;try{localStorage.setItem(key,JSON.stringify(notes))}catch(e){}}}
document.querySelector('#export').onclick=()=>{const a=document.createElement('a');const u=URL.createObjectURL(new Blob([JSON.stringify(notes,null,2)],{type:'application/json'}));a.href=u;a.download='R0c_owner_notes.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000)};
</script></html>''')
    (OUT/'R0_review_failures.html').write_text('\n'.join(parts))
    write(EV/'review_selection_60.jsonl',selection)
    return selection


def main():
    EV.mkdir(parents=True,exist_ok=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    paths=[OUT/'R0_expected_truth.json',OUT/'R0_expected_truth_ia.json',
        OUT/'R0_adjudication_private/items_key.json',OUT/'R0_adjudication_private/ia/items_key.json',
        ROOT/'.cache/labelfix/align_s0.jsonl',ROOT/'.cache/labelfix/m2/align_s0.jsonl',
        ROOT/'.cache/labelfix/r0/align_locked_ia.jsonl',OUT/'R0_evidence/align_locked_s0.jsonl',
        OUT/'R0_newsource_locked.jsonl',OUT/'R0_locked_set.jsonl',OUT/'R0_evidence/continuity_666.jsonl']
    # Also bind unchanged runtime files from the R0a source receipt.
    old=json.loads((OUT/'R0_evidence/input_binding.json').read_text())
    paths+= [ROOT/p for p in old['files'] if p.startswith('greekocr/')]
    before={str(p.relative_to(ROOT)):sha(p) for p in paths}
    lines,cards=load();freq=training_evidence()
    ls,bs,native,failures,unknown,units=letter_scores(lines,cards,freq)
    cs=case_scores(cards)
    ps,pf,pc=punct_scores(lines,cards,freq);failures+=pf
    spans,gf=spans_and_geometry(lines);failures+=gf
    # Case failures belong to S5's pixel-case reader, not the recogniser.
    for c in cards:
        if 'case_disagreement' in c['kinds'] and c['truth']==c['forms']['recogniser']:
            failures.append(strata_row(c['stratum'],type='S5_pixel_case_wrong',DATA_MODEL='MODEL',
                status='CONFIRMED_ADJUDICATED_CASE',line_id=c['line_id'],doc=c['case_reference']['doc'],
                source=c['case_reference']['doc'],slot=c['frozen_slot'],slot_kind='frozen S5 slot',
                prediction_stream='S5_pixel_case',expected=c['forms']['recogniser'],emitted=c['forms']['S5_pixel'],
                card_id=c['id'],evidence=dict(recogniser_right=True,scope='case only',
                    training_expected=freq['symbols'].get(c['forms']['recogniser']),
                    classification_rule='MODEL/runtime pixel-case estimation; recogniser case agrees with adjudicated print')))
    failures.sort(key=lambda r:(r['stratum'],r['line_id'],r['prediction_stream'],r['type'],str(r['slot'])))
    fs=failure_summary(failures);selection=review(lines,failures,cs,cards)
    coverage=[]
    for s in LABELS:
        cc=[c for c in cards if c['stratum']==s and not c['control']]
        u=[u for u in units if u['stratum']==s and u['prediction_stream']=='stored_instrument']
        coverage.append(strata_row(s,cohort_lines=sum(l['stratum']==s for l in lines.values()),
            noncontrol_cards=len(cc),resolved_cards=sum(c['truth'] is not None for c in cc),
            card_touched_lines=len({c['line_id'] for c in cc}),
            word_identity_cards=len(u),word_identity_truth_slots=sum(x['truth_slots'] for x in u),
            word_identity_truth_lines=len({x['line_id'] for x in u}),
            case_only_cards=sum('case_disagreement' in c['kinds'] for c in cc),
            full_lines_certified=0,full_line_truth_slots=0,
            unresolved_card_ids=[c['id'] for c in cc if c['truth'] is None]))
    truth_inventory=[]
    for lid,l in sorted(lines.items()):
        cc=[c for c in cards if c['line_id']==lid and not c['control']]
        uu=[u for u in units if u['line_id']==lid and u['prediction_stream']=='stored_instrument']
        truth_inventory.append(strata_row(l['stratum'],line_id=lid,full_line_certified=False,
            full_line_letters=None,word_identity_truth_slots=sum(u['truth_slots'] for u in uu),
            word_cards=[dict(card_id=u['card_id'],start=u['start'],end=u['end'],truth=u['truth']) for u in uu],
            attribute_cards=[dict(card_id=c['id'],kinds=c['kinds'],truth=c['truth'],status=c['truth_status'])
                             for c in cc if 'model_words' not in c],
            unresolved_card_ids=[c['id'] for c in cc if c['truth'] is None]))
    write(EV/'line_truth_inventory.jsonl',truth_inventory)
    metrics=dict(schema_version='R0c-1',head_at_launch=head,network=False,new_CTC_forwards=0,
        measurement_only=True,stratum_labels=LABELS,
        truth_first=dict(coverage=coverage,source='R0b adjudicated print forms; NFD marks removed, case kept',
            full_lines_certified=0,control_cards=86,controls_excluded=True,
            main_statuses=dict(Counter(c['truth_status'] for c in cards if not c['id'].startswith('ia_'))),
            ia_statuses=dict(Counter(c['truth_status'] for c in cards if c['id'].startswith('ia_'))),
            warning='Word cards certify their word only; case and punctuation anchors certify only the requested attribute. Three-way agreement is not print truth.'),
        letters=dict(scope='adjudicated, selected word-card letters only; NOT full-line/population CER',
            normalization='NFD marks removed; alphabetic bases only, apostrophe modifier letters excluded; case-folded uses Python Unicode casefold (including final sigma)',
            by_stratum=ls,by_book_source=bs,native_cache_variant_cards=native,unknowns=unknown),
        case=cs,punctuation=dict(scope='deduplicated adjudicated candidate sites, not prevalence in all lines',
            by_stratum=ps,conflicts=pc,functional_equivalence="apostrophe variants ' ’ ʼ ᾽ ` ´; quote glyph differences reported separately",
            projection='local letter alignment maps signs to recogniser letter boundaries; repeated cards deduplicated; contradictory roles remain UNKNOWN'),
        spans=dict(scope='R0a native detector blob diagnostic; historical 3.9234% pools 666+(ii) only; no new cross-stratum accuracy estimate',
                   historical_R0a_outside_pct=3.9234186421354718,by_stratum=spans),
        failure_types=fs,classification=dict(rule='DATA: paired Google label wrong/missing at the adjudicated error; MODEL: paired Google label correct or runtime localisation/pixel-case failure',
            causal_limit='Not causal identification of training history. Manifest frequencies establish availability only. No wider-model gain is established.'),
        review=dict(path='R0_review_failures.html',lines=len(selection),published=False),
        inputs_sha256=before)
    dump(OUT/'R0_metrics.json',metrics);write(OUT/'R0_failures.jsonl',failures)
    assert before=={str(p.relative_to(ROOT)):sha(p) for p in paths}
    assert head==subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    dump(EV/'validation.json',dict(input_hashes_unchanged=True,full_lines_certified=0,
        controls_main_per_reader='83/83',controls_ia_per_reader='3/3',
        primary_word_windows_disjoint=True,case_sample_complete=len(read(EV/'case_scored_160.jsonl'))==160,
        unknown_cards_preserved=2,explicit_unknown_glyphs=1,
        all_failure_types_represented_on_review=True,review_lines=len(selection),
        new_CTC_forwards=0,network_calls=0,git_mutation_commands=0))
    print(json.dumps(dict(coverage=coverage,letters=ls,native=native,case=cs,
                         punctuation=ps,punctuation_conflicts=pc,failures=fs),ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
