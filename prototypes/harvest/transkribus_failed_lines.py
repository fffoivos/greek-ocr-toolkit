"""T12 Anemi-first credit-guarded run and offline three-engine comparison."""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import unicodedata

from greekocr.readers.services.transkribus import TranskribusReader, _reading
from greekocr.score import edit_distance
from prototypes.harvest import google_failed_lines as g
from prototypes.harvest.vision_comparison import md_text

ENGINES = ('docai', 'vision', 'transkribus')
PAIRS = (('docai', 'vision'), ('docai', 'transkribus'), ('vision', 'transkribus'))
RARE = 'ϗȣϛϲϝϙϡ'


def transkribus_crop_metrics(raw, width, height):
    reading = _reading(raw, {})
    text = reading.raw_text
    characters = text.replace('\r', '').replace('\n', '')
    return dict(width_px=width, height_px=height, lines_returned=len(reading.lines),
        text_per_line=reading.lines, line_confidences=reading.line_confidences,
        line_count_source=reading.line_count_source, text=text, total_characters=len(characters),
        characters_per_100px_width=100*len(characters)/width,
        mean_symbol_confidence=reading.mean_symbol_conf, min_symbol_confidence=reading.min_symbol_conf,
        symbol_count=len(reading.symbol_confidences), empty=not text.strip(),
        greek_characters=sorted({c for c in text if 'GREEK' in unicodedata.name(c, '')}, key=ord))


def three_way_metrics(texts):
    """Strict NFD CER plus separately labelled line-break-free majority metrics."""
    result = {}
    normalized = {e:unicodedata.normalize('NFD', texts[e]) for e in ENGINES}
    for a,b in PAIRS:
        x,y = normalized[a],normalized[b]
        edits = edit_distance(x,y)
        prefix = a+'_'+b
        forward = edits/len(x) if x else (0.0 if not y else None)
        reverse = edits/len(y) if y else (0.0 if not x else None)
        result.update({prefix+'_edits':edits, prefix+'_cer':forward,
                       prefix+'_reverse_cer':reverse,
                       prefix+'_mean_bidirectional_cer':(forward+reverse)/2 if forward is not None and reverse is not None else None})
    for key, readings in [('raw',texts), ('nfd',normalized),
                          ('nfd_without_cr_lf',{e:t.replace('\r','').replace('\n','') for e,t in normalized.items()}),
                          ('raw_without_cr_lf',{e:t.replace('\r','').replace('\n','') for e,t in texts.items()})]:
        count = max(Counter(readings.values()).values())
        result['majority_'+key] = count >= 2
        result['unanimous_'+key] = count == 3
        for a,b in PAIRS:
            result[a+'_'+b+'_'+key+'_equal'] = readings[a]==readings[b]
    result.update({e+'_nfd_characters':len(normalized[e]) for e in ENGINES})
    return result


def compare_rows(groups, out):
    maps = {e:{r['crop_id']:r for r in groups[e]} for e in ENGINES}
    if any(len(maps[e]) != len(groups[e]) for e in ENGINES):
        raise ValueError('duplicate crop IDs')
    result = []
    for row in groups['transkribus']:
        item = {k:row[k] for k in ('crop_id','crop_sha256','source','failure_type','failure_types')}
        for engine in ENGINES:
            r = maps[engine].get(row['crop_id'])
            if r and r['crop_sha256'] != row['crop_sha256']:
                raise ValueError('engine image SHA mismatch')
            item[engine+'_status'] = r['status'] if r else 'missing'
            for k in ('text','mean_symbol_confidence','min_symbol_confidence','lines_returned',
                      'line_confidences','text_per_line','treatment','exposure_signals'):
                item[engine+'_'+k] = r.get(k) if r else None
            if r and r['status'] == 'ok':
                path = g.response_path(out/(engine+'_failed_lines'),r,engine)
                value = json.loads(path.read_text())
                if value['crop_sha256'] != r['crop_sha256'] or hashlib.sha256(g.canonical(value['response']).encode()).hexdigest() != value['response_sha256']:
                    raise ValueError('raw response SHA changed')
                for k,v in g.crop_metrics(value['response'],r['width_px'],r['height_px'],engine=engine).items():
                    if r[k] != v:
                        raise ValueError(f'{engine} metric differs from raw: {k}')
                item[engine+'_response_sha256'] = value['response_sha256']
        item['triple_available'] = all(item[e+'_status']=='ok' for e in ENGINES)
        item['rare_glyphs_transkribus'] = ''.join(c for c in RARE if c in (item['transkribus_text'] or ''))
        item['docai_kappa_iota_grave'] = 'κὶ' in (item['docai_text'] or '')
        item.update(three_way_metrics({e:item[e+'_text'] for e in ENGINES}) if item['triple_available'] else
                    {k:None for k in three_way_metrics({e:'' for e in ENGINES})})
        # Compatibility fields for the shared T10/T11 review generator.
        item['nfd_cer_docai_reference'] = item['docai_transkribus_cer']
        item['nfd_equal'] = item['docai_transkribus_nfd_equal']
        result.append(item)
    return result


def agreement(rows):
    triples = [r for r in rows if r['triple_available']]
    result = dict(n_crops=len(rows), n_triples=len(triples))
    for key in ('raw','nfd','raw_without_cr_lf','nfd_without_cr_lf'):
        for kind in ('majority','unanimous'):
            name=kind+'_'+key
            result[name] = sum(r[name] for r in triples)
            result[name+'_rate'] = result[name]/len(triples) if triples else None
    for a,b in PAIRS:
        prefix = a+'_'+b
        edits = sum(r[prefix+'_edits'] for r in triples)
        na,nb = (sum(r[e+'_nfd_characters'] for r in triples) for e in (a,b))
        result[prefix] = dict(edits=edits, denominator=na, reverse_denominator=nb,
            pooled_cer=edits/na if na else None, pooled_reverse_cer=edits/nb if nb else None,
            pooled_mean_bidirectional_cer=(edits/na+edits/nb)/2 if na and nb else (0.0 if not na and not nb and triples else None),
            mean_crop_cer=g.distribution([r[prefix+'_cer'] for r in triples])['mean'],
            nfd_equal=sum(r[prefix+'_nfd_equal'] for r in triples),
            nfd_without_cr_lf_equal=sum(r[prefix+'_nfd_without_cr_lf_equal'] for r in triples))
    result['consensus_disagreement_scores']={
        e:g.distribution([result[a+'_'+b]['pooled_mean_bidirectional_cer'] for a,b in PAIRS if e in (a,b)])['mean']
        for e in ENGINES}
    return result


def _receipt(rows, directory, output, reader, status, error, before, after, prior):
    pages=[]
    events={}
    by_sha={r['crop_sha256']:r for r in rows}
    for folder,mode in ((output,'single_line'),(output/'default_layout','default'),
                        (output/'omitted_layout','omitted_layout_probe'),
                        (output/'empty_line_detection','empty_line_detection_probe')):
        legacy_pilots=list(folder.glob('pilot*.json'))
        for path in sorted((folder/'responses').glob('*.json')):
            r=json.loads(path.read_text())
            pages.append({k:r.get(k) for k in ('crop_sha256','request_id','receipt_id','credits_before','credits_after','credits_used','latency_s')} | dict(mode=mode,source=by_sha.get(r['crop_sha256'],{}).get('source')))
            for i,c in enumerate(r.get('calls',[])):
                if c.get('call_id'):
                    events[c['call_id']]=c
                elif not legacy_pilots:
                    key=f'legacy:{mode}:{r["request_id"]}:{i}'
                    events[key]=dict(c,call_id=key)
        for pilot in legacy_pilots:
            for i,c in enumerate(json.loads(pilot.read_text()).get('calls',[])):
                key=c.get('call_id',f'pilot:{mode}:{pilot.name}:{i}')
                events[key]=dict(c,call_id=key)
    for c in prior.get('http_call_records',[])+reader.calls:
        if c.get('call_id'):events[c['call_id']]=c
    for filename in ('recovery_calls.json','reconciliation.json','unassigned_recovery_calls.json'):
        extra=output/filename
        if extra.exists():
            for c in json.loads(extra.read_text()).get('http_call_records',[]):
                if c.get('call_id'):events[c['call_id']]=c
    for path in (output/'error_receipts').glob('*.json'):
        for c in json.loads(path.read_text()).get('calls',[]):
            if c.get('call_id'):events[c['call_id']]=c
    reconciliation=output/'reconciliation.json'
    unassigned=json.loads(reconciliation.read_text()).get('unassigned_debits',[]) if reconciliation.exists() else []
    unassigned_credit_total=-sum(r['creditValue'] for r in unassigned)
    completed_credit_total=sum(p['credits_used'] or 0 for p in pages)
    retry_path=output/'bounded_retries.json'
    retries=json.loads(retry_path.read_text()) if retry_path.exists() else None
    measured=[r for r in rows if r['status']=='ok']
    return dict(schema_version=1, engine='transkribus', status=status, error=error,
        credentials='environment credentials used', binding=reader.binding(),
        timestamp=datetime.now(timezone.utc).isoformat(), catalogue_directory=str(directory),
        credits_before=before, credits_after=after, credits_used=before-after if before is not None and after is not None else None,
        credit_floor=reader.credit_floor, reserved_max_credits_per_page=reader.max_page_credits,
        page_credit_total=completed_credit_total, pages=pages,
        unassigned_charged_jobs=unassigned, unassigned_credits=unassigned_credit_total,
        reconciled_page_credit_total=completed_credit_total+unassigned_credit_total,
        credits_reconciled=(abs((before-after)-(completed_credit_total+unassigned_credit_total))<1e-8) if before is not None and after is not None else False,
        bounded_retries=retries,
        exploratory_preflight_http_calls=15,
        exploratory_preflight_roles=dict(token=5,balance=8,costs=1,credit_transactions=1),
        calls=len([c for c in events.values() if c['role']=='submit']),
        http_calls=len(events), http_call_roles=dict(Counter(c['role'] for c in events.values())),
        http_call_records=list(events.values()), successful_pages=len(pages),
        catalogue_crop_ids=len(rows), source_crop_ids=dict(Counter(r['source'] for r in rows)),
        measured_crop_ids=len(measured), measured_by_source=dict(Counter(r['source'] for r in measured)),
        unresolved_crops=[dict(crop_id=r['crop_id'],crop_sha256=r['crop_sha256'],status=r['status'],error=r.get('error')) for r in rows if r['status']=='unresolved_submission'],
        unique_measured_crop_sha256=len({r['crop_sha256'] for r in measured}),
        next_unmeasured_crop=next((r['crop_id'] for r in rows if r['status']=='pending'),None),
        include_anemi=g.ALLOW_ANEMI, withheld_anemi=sum(r['status']=='withheld_anemi' for r in rows),
        monetary_cost='not exposed; credits are measured; no EUR/USD conversion',
        input_hashes={f:g.sha256(directory/f) for f in ['README.md',*g.CATALOGUES,'page_comments.json']},
        request_policy='Anemi fully drained before Vouli; six one-image jobs maximum; one-credit reservation per pending+next page; SHA cache; no automatic resubmission; live balance and per-job debits; stop new submissions at floor or any error and drain accepted jobs')


def _prepare_bounded_retries(rows, output, reader):
    """Explicit runner opt-in, never an implicit service-reader retry.

    Keep every original attempt. One extra reservation remains for each unknown
    original submission; reject a second retry or an unknown-account shortfall.
    """
    candidates=[]
    seen=set()
    for row in rows:
        if row['crop_sha256'] in seen or g.is_anemi(row['page'],row['crop_path']):continue
        seen.add(row['crop_sha256'])
        path=output/'attempts'/(row['crop_sha256']+'.json')
        if path.exists() and not g.response_path(output,row,'transkribus').exists():
            state=json.loads(path.read_text())
            if state.get('binding')!=reader.binding():raise ValueError('retry attempt binding mismatch')
            if not state.get('request_id') and not (output/'prior_attempts'/(row['crop_sha256']+'.json')).exists():
                candidates.append((row,path,state))
    if not candidates:return
    balance=reader.credit_balance()
    reservation=2*len(candidates)*reader.max_page_credits
    if balance-reservation<reader.credit_floor:
        raise ValueError('bounded retry credit reservation would breach the floor')
    previous=output/'prior_attempts'
    previous.mkdir(parents=True,exist_ok=True)
    entries=[]
    for row,path,state in candidates:
        target=previous/path.name
        path.replace(target)
        entries.append(dict(crop_id=row['crop_id'],crop_sha256=row['crop_sha256'],
            prior_attempt=str(target),prior_acceptance='unknown; may already have charged',
            retry_limit=1,reason='explicit T12 runner recovery for missing catalogue results; original retained'))
    g.atomic_json(output/'bounded_retries.json',dict(credentials='environment credentials used',
        credits_before=balance,credit_floor=reader.credit_floor,reserved_credits=reservation,entries=entries))
    reader.credit_floor+=len(candidates)*reader.max_page_credits


def run_transkribus(directory, out, *, offline=False, reader=None, retry_unresolved=False):
    output=out/'transkribus_failed_lines'
    reader=reader or TranskribusReader(responses_dir=output/'responses',mode='single_line')
    out.mkdir(parents=True,exist_ok=True)
    with g.run_lock(output/'run.lock'):
        rows=g.load_catalogues(directory)
        comments=g.derive_comment_crops(directory,rows,output)
        rows.sort(key=lambda r:(r['source']!='Anemi',r['source'],r['crop_id']))
        if retry_unresolved:
            if offline:raise ValueError('offline mode cannot retry')
            _prepare_bounded_retries(rows,output,reader)
        # A rejected/uncertain prior submission stays unresolved, without blocking
        # independent later crops. Its original attempt and call remain retained.
        unresolved=[]
        for row in rows:
            attempt=output/'attempts'/(row['crop_sha256']+'.json')
            if attempt.exists() and not g.response_path(output,row,'transkribus').exists():
                state=json.loads(attempt.read_text())
                if not state.get('request_id'):
                    row.update(status='unresolved_submission',error=state.get('error','prior submission has no process ID; acceptance unknown; no automatic resubmission'))
                    unresolved.append(row)
        g.atomic_json(output/'inventory.json',rows)
        receipt_path=output/'receipt.json'
        prior=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
        initial=output/'initial_balance.json'
        if initial.exists():before=json.loads(initial.read_text())['balance']
        elif not offline:
            candidates=[reader.credit_balance()]
            for path in output.glob('**/pilot_receipt.json'):
                candidates.append(json.loads(path.read_text())['credits_before'])
            before=max(candidates)
            g.atomic_json(initial,dict(balance=before,credentials='environment credentials used'))
        else:before=prior.get('credits_before')
        status,error=('complete_with_errors','unresolved submission(s); no automatic resubmission') if unresolved else ('complete',None)
        permitted=[r for r in rows if r['status'] not in ('withheld_anemi','unresolved_submission')]
        try:
            i=0
            for source in dict.fromkeys(r['source'] for r in permitted):
                selected=[r for r in permitted if r['source']==source]
                for row,reading in reader.read_many(selected,offline=offline):
                    i+=1
                    path=g.response_path(output,row,'transkribus')
                    envelope=json.loads(path.read_text())
                    row.update(g.crop_metrics(envelope['response'],row['width_px'],row['height_px'],engine='transkribus'))
                    row.update(status='ok',request_id=reading.request_id,receipt_id=reading.receipt_id,cached=reading.cached)
                    if i%10==0 or i==len(permitted):
                        print(f'Transkribus completed {i}/{len(permitted)}; {row["source"]}; balance {reader.balance_snapshots[-1]["balance"] if reader.balance_snapshots else "cached"}',flush=True)
                        after=reader.balance_snapshots[-1]['balance'] if reader.balance_snapshots else prior.get('credits_after')
                        rec=_receipt(rows,directory,output,reader,'running',None,before,after,prior)
                        g.atomic_json(receipt_path,rec)
                        g.atomic_json(output/'metrics.json',rows)
        except Exception as exc:
            status,error='stopped',str(exc)
            stopped=next((r for r in rows if r['status']=='pending'),None)
            if stopped:
                stopped['status']='stopped'
                stopped['error']=error
            print('STOPPED: '+error,flush=True)
        if offline:
            after=prior.get('credits_after')
            status=prior.get('status',status)
            error=prior.get('error',error)
        else:
            try:after=reader.credit_balance()
            except Exception:after=reader.balance_snapshots[-1]['balance'] if reader.balance_snapshots else None
        rec=_receipt(rows,directory,output,reader,status,error,before,after,prior)
        build_artifacts(rows,comments,directory,out,rec)
        return rec


def build_artifacts(rows,comments,directory,out,rec):
    output=out/'transkribus_failed_lines'
    effects=json.loads((directory/'page_comments.json').read_text())['effects']
    groups=dict(transkribus=rows)
    findings_path=output/'visual_findings.json'
    findings=json.loads(findings_path.read_text()) if findings_path.exists() else []
    by_crop={r['crop_id']:r for r in rows}
    for finding in findings:
        row=by_crop[finding['crop_id']]
        value=json.loads(g.response_path(output,row,'transkribus').read_text())
        if finding['crop_sha256']!=row['crop_sha256'] or finding['response_sha256']!=value['response_sha256']:
            raise ValueError('visual finding evidence changed')
        row['visual_observation']=finding['observation']
    for engine in ('docai','vision'):
        groups[engine]=json.loads((out/(engine+'_failed_lines')/'metrics.json').read_text())
    summaries={e:g.summarise(r,list(effects),engine_name={'docai':'Document AI','vision':'Cloud Vision','transkribus':'Transkribus'}[e]) for e,r in groups.items()}
    chars={e:g.characters_table(r) for e,r in groups.items()}
    for kind,s in summaries['transkribus']['types'].items():
        associated=[c for c in comments if kind in c['failure_types']]
        s.update(n_page_comments=len(associated),n_bound_page_comments=sum(any(b['failure_type']==kind for b in c['bindings']) for c in associated))
    pairs=compare_rows(groups,out)
    sources={source:agreement([r for r in pairs if r['source']==source]) for source in ('Anemi','Vouli')}
    sources['ALL']=agreement(pairs)
    controls=agreement([r for r in pairs if r['failure_type']=='control_owner_verified'])
    unique_sources={source:agreement(list({r['crop_sha256']:r for r in pairs if source=='ALL' or r['source']==source}.values())) for source in sources}
    comparison=dict(sources=sources,unique_image_sources=unique_sources,controls=controls,
        rare_glyph_crops_transkribus=sum(bool(r['rare_glyphs_transkribus']) for r in pairs),
        rare_glyph_unique_images_transkribus=len({r['crop_sha256'] for r in pairs if r['rare_glyphs_transkribus']}))
    anemi=sources['Anemi']
    scores=anemi['consensus_disagreement_scores']
    available={e:s for e,s in scores.items() if s is not None}
    best=min(available,key=available.get) if available else None
    source_diagnostics={e:{s:dict(measured=sum(r['source']==s and r['status']=='ok' for r in groups[e]),
        empty=sum(r['source']==s and r['status']=='ok' and r['empty'] for r in groups[e]),
        rare_glyph_crops=sum(r['source']==s and r['status']=='ok' and any(c in r['text'] for c in RARE) for r in groups[e]))
        for s in ('Anemi','Vouli')} for e in ENGINES}
    comparison.update(source_diagnostics=source_diagnostics,best_anemi_by_consensus_disagreement=best,
                      winner_is_accuracy_claim=False)
    for filename,value in [('metrics.json',rows),('summary.json',summaries['transkribus']),('characters.json',chars['transkribus']),
                           ('page_comment_coverage.json',comments),('receipt.json',rec),('comparison.json',comparison),('three_engines.json',pairs)]:
        g.atomic_json(output/filename,value)
    g.write_csv(output/'crops.csv',rows)
    g.write_csv(output/'three_engines.csv',pairs)
    g.write_csv(output/'characters.csv',[dict(source=s,character=c,codepoint=f'U+{ord(c):04X}',count=n) for s,t in chars['transkribus'].items() for c,n in t['character_counts'].items()])
    g.write_csv(output/'three_engine_characters.csv',[dict(engine=e,source=s,character=c,codepoint=f'U+{ord(c):04X}',count=n) for e,table in chars.items() for s,t in table.items() for c,n in t['character_counts'].items()])
    lines=['# Three OCR engines on the failed-lines catalogue — T12 v1','',
        f'Status: **{rec["status"]}**. Transkribus model **148525**, supplied single-line layout, Anemi first. {rec["measured_crop_ids"]}/{len(rows)} crop IDs measured, {rec["unique_measured_crop_sha256"]} unique images. Source coverage: `{rec["measured_by_source"]}`. Stop reason: `{rec["error"]}`. Next unmeasured crop: `{rec["next_unmeasured_crop"]}`.','',
        'No engine is a reference. CER here measures disagreement, not transcription accuracy. Strict pairwise NFD CER preserves case, spaces, punctuation and line breaks; forward denominators are the first named engine. Reverse CER and mean bidirectional CER are in the raw CSV. Empty denominators with nonempty counterparts are null, two empty strings have CER zero. Majority is at least two identical readings and is separately reported raw, NFD, and with only CR/LF removed; spaces are never collapsed.','',
        '## Anemi assessment','',
        f'**{best or "No engine"} looks best on Anemi by cross-engine agreement**: the mean of its two pooled bidirectional NFD disagreement rates is lowest. Scores: '+', '.join(f'{e} {g.fmt(scores[e])}' for e in ENGINES)+f'. Common cohort: {anemi["n_triples"]}/{anemi["n_crops"]} Anemi crop IDs. This is a consensus ranking, not measured accuracy. No engine is a reference, two engines can agree on a shared error, and a manual transcription is needed for an accuracy winner.','',
        'Anemi output diagnostics (full measured engine coverage): '+ '; '.join(f'{e}: {source_diagnostics[e]["Anemi"]["measured"]} measured, {source_diagnostics[e]["Anemi"]["empty"]} empty, {source_diagnostics[e]["Anemi"]["rare_glyph_crops"]} rare-glyph crop IDs' for e in ENGINES)+'. Rare-glyph output is complementary evidence to review, not proof of a correct historical transcription.','',
        '## Pairwise disagreement and majority agreement','',
        '| Source | Three readings / catalogue | DocAI–Vision NFD CER | DocAI–Transkribus NFD CER | Vision–Transkribus NFD CER | Majority raw | Majority NFD | Majority raw without CR/LF | Majority NFD without CR/LF |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for source,s in sources.items():
        lines.append(f'| {source} | {s["n_triples"]}/{s["n_crops"]} | '+ ' | '.join(g.fmt(s[a+'_'+b]['pooled_cer']) for a,b in PAIRS)+f' | {s["majority_raw"]} | {s["majority_nfd"]} | {s["majority_raw_without_cr_lf"]} | {s["majority_nfd_without_cr_lf"]} |')
    lines+=['','All three-way statistics use the common measured cohort. Existing DocAI–Vision readings for crops without Transkribus remain visible but are excluded from those denominators. Crop-ID weighting follows T10/T11; duplicate SHA images share one charge. The comparison JSON also reports unique-image cohorts, controls, unanimous counts and source agreement rates. Consensus score = the mean of the engine’s two pairwise pooled bidirectional CERs; this ranking is an inference about agreement.','',
        '## Controls baseline and treatment by failure type','',
        'The same T10/T11 exposure rule is used: multiple returned lines, empty text, or mean/min symbol confidence below that engine’s control p05. PAGE line confidence is preserved separately; it is not treated as character confidence. Missing glyph confidence remains null, so confidence-triggered exposure is unavailable for Transkribus when PAGE has no Glyph objects. Controls are owner-verified geometry, not gold text. Density is descriptive.','',
        '| Type | Engine | Measured / total | Lines distribution | Empty rate | Mean symbol median (p05) | Min symbol median | Line confidence median | Chars/100px median (p05–p95) | Exposed / silent |','| --- | --- | ---: | --- | ---: | --- | ---: | ---: | --- | --- |']
    for kind in ['control_owner_verified',*effects]:
        for e in ENGINES:
            s=summaries[e]['types'][kind]
            confidences=[c for r in groups[e] if r['status']=='ok' and kind in r['failure_types'] for c in r['line_confidences'] if c is not None]
            lines.append(f'| {kind} | {e} | {s["n_measured"]}/{s["n_crops"]} | `{s["lines_returned_distribution"]}` | {g.fmt(s["empty_rate"])} | {g.fmt(s["mean_symbol_confidence"]["median"])} ({g.fmt(s["mean_symbol_confidence"]["p05"])}) | {g.fmt(s["min_symbol_confidence"]["median"])} | {g.fmt(g.distribution(confidences)["median"])} | {g.fmt(s["characters_per_100px_width"]["median"])} ({g.fmt(s["characters_per_100px_width"]["p05"])}–{g.fmt(s["characters_per_100px_width"]["p95"])}) | {s["exposed_count"]}/{s["silent_candidate_count"]} |')
    lines+=['','Google rows above retain their full existing 469-crop treatment baselines; Transkribus coverage is explicitly smaller if credit-limited. Per-engine confidence scales differ. Missing ink without a catalogue crop has no OCR evidence. Bound page-comment coverage is in the JSON; no whole-page substitute was submitted.','',
        '## Rare glyphs actually emitted','',
        'Counts are raw code points over unique measured image SHA values. They do not prove glyph correctness; no glyph-level reference or exposure denominator is supplied. Each engine’s coverage is shown.','',
        '| Source | Character | DocAI count | Vision count | Transkribus count |','| --- | --- | ---: | ---: | ---: |']
    for source in ('Anemi','Vouli','ALL'):
        lines.append(f'| {source} | unique measured images | '+ ' | '.join(str(chars[e].get(source,{}).get('n_calls',0)) for e in ENGINES)+' |')
        for c in g.SPECIAL:
            lines.append(f'| {source} | {c} U+{ord(c):04X} | '+' | '.join(str(chars[e].get(source,{}).get('character_counts',{}).get(c,0)) for e in ENGINES)+' |')
    lines+=['','## DocAI kai-sign readings (`κὶ`)','',
        '| Crop | Source | Document AI | Vision | Transkribus |','| --- | --- | --- | --- | --- |']
    for r in pairs:
        if r['docai_kappa_iota_grave']:
            lines.append(f'| [{r["crop_id"]}](three_engines_review.html#{r["crop_id"]}) | {r["source"]} | '+' | '.join(md_text(r[e+'_text']) for e in ENGINES)+' |')
    selected=[r for r in pairs if r['rare_glyphs_transkribus']]
    lines+=['','## Transkribus rare-glyph crops','',f'{len(selected)} crop IDs; {comparison["rare_glyph_unique_images_transkribus"]} distinct images.','']
    for r in selected[:20]:lines.append(f'- [{r["crop_id"]}](three_engines_review.html#{r["crop_id"]}): `{r["rare_glyphs_transkribus"]}`; {md_text(r["transkribus_text"])}')
    if not selected:lines.append('None of ϗ ȣ ϛ ϲ ϝ ϙ ϡ was emitted on measured crops.')
    if findings:
        lines+=['','## Native crop checks','',
            'Four native crop images were inspected against the three readings. These are illustrative observations, not complete reference transcripts or a held-out accuracy evaluation. [Hash-bound findings](transkribus_failed_lines/visual_findings.json).','']
        for finding in findings:lines.append(f'- [{finding["crop_id"]}](three_engines_review.html#{finding["crop_id"]}): {finding["observation"]}')
    mode_rows=[]
    for p in sorted((output/'default_layout'/'responses').glob('*.json')):
        d=json.loads(p.read_text()); single=output/'responses'/p.name
        v=json.loads(single.read_text()) if single.exists() else None
        mode_rows.append(dict(crop_sha256=d['crop_sha256'],single_line_text=_reading(v['response'],v).raw_text if v else None,
            default_text=_reading(d['response'],d).raw_text,credits_used=d['credits_used']))
    g.atomic_json(output/'layout_modes.json',mode_rows)
    lines+=['','## Supplied whole-crop line mode','',
        'The API supports preliminary `content.regions[].lines` with polygon/baseline. One region and one line span the crop with a horizontal baseline at 75% height; native image bytes remain unchanged. Three paired probes explicitly used layout model 49272 from the published legacy API example, with its other detection parameters at defaults; all returned zero lines. Earlier omitted-layout and empty-block probes are retained separately and included in cost, not used to infer detection capability. The main comparison uses supplied single-line layout. This is a geometry hypothesis, especially on curved or multi-line failures; one returned line is imposed and cannot diagnose multiple printed rows. [Request schema](https://transkribus.eu/processing/v1/openapi.json).','',
        '| Crop SHA | Default layout | Supplied single line | Credits |','| --- | --- | --- | ---: |']
    for r in mode_rows:lines.append(f'| `{r["crop_sha256"]}` | {md_text(r["default_text"])} | {md_text(r["single_line_text"])} | {r["credits_used"]} |')
    lines+=['','## Credits and calls','',
        f'Credits before: **{rec["credits_before"]}**; after: **{rec["credits_after"]}**; observed consumption: **{rec["credits_used"]}**. Sum of crop-bound per-page charges: **{rec["page_credit_total"]}**, plus **{rec["unassigned_credits"]}** for an unassigned charged process. {rec["calls"]} submissions, {rec["successful_pages"]} cached pages with verified crop binding (including layout-mode probes), {rec["http_calls"]} recorded HTTP calls; roles `{rec["http_call_roles"]}`. Floor **50**; every pending and next page reserves **{rec["reserved_max_credits_per_page"]}** credit. Cash cost was not exposed, so no monetary charge is invented. Six one-image jobs maximum; main source cohorts drain in Anemi-first order. Per-page charges use job-matched debit transactions; early sequential pilot charges used before/after balances. Queue snapshots overlap jobs and are not individual charges.','',
        'Credit snapshots use `GET /TrpServer/rest/credits?onlyActive=true&includeExpired=false`; only the balance and safe call metadata are retained. Credentials were read from environment only. OAuth access/refresh tokens and account identity fields are never persisted. [Credit API schema](https://transkribus.eu/TrpServer/rest/openapi.json), [processing credit policy](https://docs.transkribus.org/start/credits).','',
        '| Mode | Process | Image SHA | Credits before | Credits after | Used per page |','| --- | --- | --- | ---: | ---: | ---: |']
    for p in rec['pages']:lines.append(f'| {p["mode"]} | {p["request_id"]} | `{p["crop_sha256"]}` | {p["credits_before"]} | {p["credits_after"]} | {p["credits_used"]} |')
    if rec.get('unresolved_crops'):
        lines+=['','## Unresolved submissions','',
        'These submissions supplied no durable process ID (an HTTP 502 and/or an interrupted request). Original attempts are retained. These crops have no Transkribus reading and are excluded from the common cohort. Account reconciliation detects extra debits but cannot manufacture an input image hash for an unassigned job.','']
        for r in rec['unresolved_crops']:
            lines.append(f'- [{r["crop_id"]}](three_engines_review.html#{r["crop_id"]}): {r["error"]}; [original attempt](transkribus_failed_lines/attempts/{r["crop_sha256"]}.json).')
    if rec.get('bounded_retries'):
        lines+=['','## Bounded recovery retries','',
            'To finish the explicitly authorized catalogue test, the runner made one separately receipted recovery attempt for each submission with no process ID. The service reader never retries implicitly. Original attempts remain in `prior_attempts/`; a second recovery retry is disabled. Extra maximum-charge reservations protect against a late debit from the original unknown submissions. Any originally charged page is included in account reconciliation.','']
        for r in rec['bounded_retries']['entries']:
            lines.append(f'- `{r["crop_id"]}`: one recovery attempt; [original attempt](transkribus_failed_lines/prior_attempts/{r["crop_sha256"]}.json).')
    lines+=['',f'Account reconciliation: completed-page charges {rec["page_credit_total"]}, unassigned debits {rec["unassigned_credits"]}, total {rec["reconciled_page_credit_total"]}; matches balance change: **{rec["credits_reconciled"]}**. There were also 15 exploratory read-only account/authentication calls before durable run receipts (5 token, 8 balance, 1 cost-table, 1 transaction query); no paid submission occurred in those calls.','']
    for r in rec.get('unassigned_charged_jobs',[]):
        lines.append(f'- Charged process `{r["jobId"]}`: {-r["creditValue"]} credits, {r["nrOfPages"]} page. Its JSON result exists, but original image bytes are unavailable from the tested result routes, so it is not assigned to a crop by an unverified text match.')
    validation_path=output/'validation.json'
    if validation_path.exists():
        validation=json.loads(validation_path.read_text())
        lines+=['','## Verification and review limit','',
            f'{validation["tests"]["passed"]} offline tests passed. The artifact validator recomputes all three engines’ crop metrics from hash-checked raw responses, recomputes pairwise/majority/source metrics, checks every source and review image hash, all 469 cards and local links, CSV readings and IDs, and the complete credit reconciliation. Offline regeneration made zero network calls. [Validation receipt](transkribus_failed_lines/validation.json).','',
            'Four native crop samples were inspected visually. Browser rendering remains unverified: Computer Use denied Firefox access, and the local Playwright browser executable was absent. Source/link/card validation is not a browser layout check.','']
    lines+=['','## Every crop: three readings','',
        '[Raw CSV](transkribus_failed_lines/three_engines.csv) · [three-way metrics](transkribus_failed_lines/comparison.json) · [full character CSV](transkribus_failed_lines/three_engine_characters.csv) · [receipt](transkribus_failed_lines/receipt.json) · [review page](three_engines_review.html)','',
        '| Crop | Source | Transkribus status | Document AI | Cloud Vision | Transkribus |','| --- | --- | --- | --- | --- | --- |']
    for r in pairs:lines.append(f'| [{r["crop_id"]}](three_engines_review.html#{r["crop_id"]}) | {r["source"]} | {r["transkribus_status"]} | '+' | '.join(md_text(r[e+'_text']) for e in ENGINES)+' |')
    (out/'THREE_ENGINES_v1.md').write_text('\n'.join(lines)+'\n')
    by_id={r['crop_id']:r for r in pairs}
    # The shared historical generator expects a numeric price placeholder. It
    # is immediately replaced by credits in HTML and is never a receipt field.
    review_receipt=dict(rec,estimated_cost_usd=0.0)
    g.build_review(rows,summaries['transkribus'],comments,out,review_receipt,engine='transkribus',comparison=by_id,three_way=by_id)
