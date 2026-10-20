"""Detached-safe resumable tranche execution. Live launch requires explicit host selection."""
from __future__ import annotations
from collections import Counter
import json,logging,os,platform,time,math,signal
from pathlib import Path
from PIL import Image
import numpy as np
from .common import lock,read_json,write_json,write_rows,rows,sha,scrub,disk_bytes,sha_bytes,atomic_bytes
from .config import SPECS
from .exclusions import Exclusions
from .ledger import Ledger,UncertainRead
from .reader import DocumentAI,read_once
from .transport import HTTP,HostBucket
from .routes.providers import Routes
from .pipeline import analyse,detector
from .rules import apply_rules
from .audits import reports

log=logging.getLogger('collect_v3')

# Deterministic page rejections raised before the paid read (frozen F2 gates, exclusion hashes, draw bounds).
PRE_READ_REJECTIONS=frozenset({'excluded page/PDF hash','page scan construction unresolved','F2 detector page gate','blank page gate','draw outside resolved bounds'})


def go_entries(out):
    """W2_owner_go.json holds one go (legacy dict) or {"entries": [...]}, one entry per owner go, each with sources and cap_usd."""
    go=Path(out)/'W2_owner_go.json'
    if not go.exists():return []
    record=read_json(go)
    return record['entries'] if isinstance(record,dict) and 'entries' in record else [record]


def tranche_caps(c,out,tranche):
    """The owner's W2 go caps W2 spend at the sum of the stated plans' caps when that is below the configured cap."""
    caps=dict(c['caps_usd']);entries=go_entries(out)
    if tranche=='W2' and entries:caps['W2']=min(caps['W2'],sum(float(e['cap_usd']) for e in entries))
    return caps


def gate_extension_ok(out,old,new):
    """A W2 resume may proceed under a gate that only adds passed sources: every source the run started
    with keeps its exact entry. The starting gate is read from its snapshot, never reconstructed."""
    if {k for k in set(old)|set(new) if old.get(k)!=new.get(k)}!={'gate_sha256'} or not old.get('gate_sha256'):return False
    snap=Path(out)/'W2'/'gate_snapshots'/(old['gate_sha256']+'.json')
    if not snap.exists():return False
    before=read_json(snap);after=read_json(Path(out)/'c1_gate.json')
    if before.get('tranche')!=after.get('tranche'):return False
    return all(after.get('sources',{}).get(s)==v for s,v in before.get('sources',{}).items())


def gate_sources(path,requested):
    if not Path(path).exists():raise ValueError('W2 requires coordinator c1_gate.json')
    gate=read_json(path)
    if gate.get('tranche')!='W1':raise ValueError('gate must reference W1')
    sources=gate.get('sources',{})
    if not isinstance(sources,dict):raise ValueError('gate.sources must be a mapping')
    for source in requested:
        value=sources.get(source,{})
        if not isinstance(value,dict) or value.get('passed') is not True:raise ValueError('W2 source not passed: '+source)
        if not isinstance(value.get('classes'),dict) or not any(v is True for v in value['classes'].values()):raise ValueError('W2 requires explicit passed class mapping: '+source)
    if 'gazette_modern' in requested:probe_qualified(sources['gazette_modern'])
    return sources

def probe_qualified(source_gate):
    value=source_gate.get('probe_1982_1985')
    if not value or value.get('passed') is not True:return False
    letters=value.get('letters',{});n=letters.get('n',0);y=letters.get('y',-1);share=value.get('monotonic_share')
    if not (isinstance(n,int) and isinstance(y,int) and 40<=n and 0<=y<=n and y/n>=.9 and value.get('pages')==40):raise ValueError('Gazette probe requires C1 letters >=90%, n>=40 and 40 W1 pages')
    if isinstance(share,bool) or not isinstance(share,(int,float)) or not math.isfinite(share) or not 0<=share<=1:raise ValueError('Gazette probe requires reported monotonic_share in [0,1]')
    return True

def finalize(out,tranche,gate=None,serbian=True,cache=None):
    """Corpus-level T4b join evidence and deterministic exact crop+label dedupe.

    Page records remain the recovery truth; this atomic aggregate is rebuilt
    after resume, including conventions that need evidence from other pages.
    """
    out=Path(out);allrows=[]
    for t in ('W1','W2'):
        if t=='W2' and tranche=='W1':continue
        for p in sorted((out/t/'pages').glob('*.json')):
            page=read_json(p)
            if page.get('status')=='completed':
                from .storage import page_rows
                contextpath=out/'convention_context.json'
                allrows.extend(page_rows(page,cache or out/'cache',out,read_json(contextpath) if contextpath.exists() else None,serbian))
    contextpath=out/'convention_context.json';context=read_json(contextpath) if contextpath.exists() else None
    apply_rules(allrows,context,serbian=serbian);seen=set()
    from .rules import boundary_hyphens
    boundary_hyphens(allrows,context)
    for r in allrows:
        r['tags']=sorted(set(r['tags']+r['text_exclusions']))
        key=(r['crop_sha256'],r['label']);r['duplicate_exact']=key in seen
        r['candidate_before_dedupe']=bool(r['candidate_usable'])
        if r['candidate_usable']:seen.add(key)
        r['candidate_usable']=bool(r['candidate_usable'] and not r['duplicate_exact'])
        if r['tranche']=='W2' and gate:r['candidate_usable']=r['candidate_usable'] and gate[r['source']]['classes'].get(r['primary_class']) is True
        r['usable_final']=bool(r['candidate_usable'] and not r['crop_tight_page'])
    result=[r for r in allrows if r['tranche']==tranche]
    reports(out,tranche,result,context)
    write_rows(out/tranche/'features.jsonl',result)
    write_rows(out/tranche/'candidates.jsonl',[r for r in result if r['usable_final']])
    write_rows(out/tranche/'crop_tight_page.jsonl',[r for r in result if r['crop_tight_page'] and r['candidate_usable']])
    write_rows(out/tranche/'excluded.jsonl',[r for r in result if not r['candidate_usable']])
    return result

def run(c,tranche,sources,http=None,reader=None,routes=None,hook=None,fixture_detector=None,baseline_overrides=None):
    binding=read_json(Path(__file__).with_name('label_rules_binding.json'))
    if sha(Path(__file__).parent/'vendor/lookalike_rule.py')!=binding['lookalike_sha256']:raise ValueError('lookalike rule hash binding changed')
    out=Path(c['output_root']);cache=Path(c['cache']);out.mkdir(parents=True,exist_ok=True)
    unknown=set(sources)-set(SPECS)
    if unknown:raise ValueError('unknown sources: '+','.join(sorted(unknown)))
    if not sources:raise ValueError('at least one source required')
    live=reader is None
    if live:
        if not c['network_enabled']:raise ValueError('network_enabled is false; no live launch')
        if (out/'OFFLINE_FIXTURE_ONLY.json').exists():raise ValueError('offline fixture output cannot be launched live')
        host=c.get('execution_host')
        if host not in ('worker','owner_mac'):raise ValueError('owner must select execution_host=worker (or owner_mac for the owner-authorised W1 run) at launch')
        if host=='worker' and (platform.system()!='Linux' or platform.machine() not in ('x86_64','AMD64')):raise ValueError('worker requires Linux x86_64')
        if host=='owner_mac':
            # Owner authorised W1 on the MacBook (17 Oct 2026). W2 there needs the owner's go on the stated
            # W2 plan, recorded in the run root as W2_owner_go.json (sources and USD cap), besides the C1 gate.
            if platform.system()!='Darwin':raise ValueError('owner_mac requires macOS')
            if tranche=='W2':
                entries=go_entries(out)
                if not entries:raise ValueError('owner_mac W2 requires W2_owner_go.json (owner go on the stated W2 plan)')
                if not set(sources)<={x for e in entries for x in e.get('sources',[])}:raise ValueError('W2 sources outside the owner go')
                for e in entries:
                    cap=e.get('cap_usd')
                    if isinstance(cap,bool) or not isinstance(cap,(int,float)) or not cap>0:raise ValueError('W2_owner_go.json needs a positive cap_usd')
            elif tranche!='W1':raise ValueError('owner_mac is authorised for W1 and owner-approved W2 only')
            import shutil
            if shutil.disk_usage(out).free<10_000_000_000:raise ValueError('owner_mac needs >=10 GB free')
        if 'serbia' in sources and not c['serbian_codec']:raise ValueError('Serbia requires --serbian-codec; default codec stays v1')
    gate=gate_sources(out/'c1_gate.json',sources) if tranche=='W2' else None
    manifest=out/f'{tranche}_manifest.jsonl'
    plan=rows(manifest)
    if not plan:raise ValueError('manifest missing; run plan offline first')
    selected=[p for p in plan if p['source'] in sources]
    if tranche=='W2' and 'gazette_modern' in sources and probe_qualified(gate['gazette_modern']):
        alternate=rows(out/'W2_gazette_probe_qualified.jsonl')
        if len(alternate)!=960 or any(r['source']!='gazette_modern' for r in alternate):raise ValueError('qualified Gazette manifest missing or invalid')
        selected=[p for p in selected if p['source']!='gazette_modern']+alternate
    if live and not c.get('limiter_root'):raise ValueError('worker requires an explicit shared limiter_root')
    limiter_root=Path(c.get('limiter_root') or cache/'hosts')
    bucket=HostBucket(limiter_root,c['request_per_second'],mdz_daily_image_cap=c['mdz_daily_image_cap']);http=http or HTTP(cache,network=c['network_enabled'],bucket=bucket)
    reader=reader or DocumentAI(bucket)
    exclusion_path=out/'exclusions_index.json'
    ex=Exclusions(read_json(exclusion_path)) if exclusion_path.exists() else Exclusions()
    if live and not exclusion_path.exists():raise ValueError('exclusion index missing')
    frozen=out/'exclusions_manifest.json'
    if live:
        if not frozen.exists() or sha(frozen)!=sha(exclusion_path):raise ValueError('frozen exclusion manifest missing or index differs')
        digest=sha(frozen)
        if any(r.get('exclusion_manifest_sha256')!=digest for r in plan):raise ValueError('draw not bound to frozen exclusions')
    if live and not (out/'convention_context.json').exists():raise ValueError('frozen T4b convention context missing; prepare offline first')
    routes=routes or Routes(http,cache,ex)
    contextpath=out/'convention_context.json'
    convention_context=read_json(contextpath) if contextpath.exists() else None
    statepath=out/tranche/'state.json';identity=dict(manifest_sha256=sha(manifest),serbian_codec=c['serbian_codec'],binding_sha256=sha(Path(__file__).parent/'processor_binding.json'),reader_sha256=sha(Path(__file__).parent/'reader.py'),pipeline_sha256=sha(Path(__file__).parent/'pipeline.py'),assembly_sha256=sha(Path(__file__).parent/'vendor/assembly_fix.py'),conventions_sha256=sha(Path(__file__).parent/'vendor/conventions.py'),rules_sha256=sha(Path(__file__).parent/'rules.py'),resolution_sha256=sha(Path(__file__).parent/'resolution.py'),planner_sha256=sha(Path(__file__).parent/'planner.py'),storage_diet=c['storage_diet'],classify_sha256=sha(Path(__file__).parent/'vendor/classify.py'),lookalike_sha256=sha(Path(__file__).parent/'vendor/lookalike_rule.py'),gate_sha256=sha(out/'c1_gate.json') if gate else None,qualified_manifest_sha256=sha(out/'W2_gazette_probe_qualified.jsonl') if gate and 'gazette_modern' in sources and probe_qualified(gate['gazette_modern']) else None,retention_prune_images=c['prune_images'],convention_context_sha256=sha(contextpath) if contextpath.exists() else None,exclusions_sha256=sha(exclusion_path) if exclusion_path.exists() else None)
    with lock(out/'run.lock',blocking=False):
        if tranche=='W1':
            urls=set()
            if live:
                for draw in selected:
                    item=draw.get('item_record',{})
                    if item.get('route')=='ia':urls.add('https://archive.org/metadata/'+item['id'])
                    urls.update(item[k] for k in ('manifest_url','catalogue_url','pdf_url','item_url','url') if item.get(k))
            http.refresh_robots(urls)
        if live:
            from .resolution import resolve_source
            resolved=[]
            needs_resolution={p['source'] for wave in ('W1','W2') for p in rows(out/f'{wave}_manifest.jsonl') if p.get('resolve_at_run') and p['source']!='gazette_modern'}
            for source in sources:
                source_pages=[p for p in selected if p['source']==source]
                if source in needs_resolution or (out/'resolution'/(source+'.json')).exists():
                    try:source_pages=resolve_source(out,source,tranche,routes,c['seed'],c['page_micro_usd'])
                    except ValueError as e:
                        # One source's resolution failure (exhausted frame, required item unavailable) stops that
                        # source only; it is recorded and the other sources continue.
                        (out/tranche).mkdir(parents=True,exist_ok=True)
                        with open(out/tranche/'source_failures.jsonl','a') as f:f.write(json.dumps(dict(source=source,error_class=type(e).__name__,error=scrub(str(e))))+'\n')
                        continue
                resolved.extend(source_pages)
            selected=resolved
            if any(r.get('exclusion_manifest_sha256')!=digest for r in selected):raise ValueError('resolved draw not bound to frozen exclusions')
            write_rows(out/tranche/'resolved_manifest.jsonl',selected)
        state=read_json(statepath) if statepath.exists() else dict(identity=identity,tranche=tranche,pages={})
        if state['identity']!=identity:
            if not (tranche=='W2' and gate_extension_ok(out,state['identity'],identity)):raise ValueError('manifest/codec/processor changed; use a fresh output root')
            state.setdefault('gate_history',[]).append(dict(old=state['identity']['gate_sha256'],new=identity['gate_sha256'],at=time.time()))
            log.info('%s gate extended: %s -> %s',tranche,state['identity']['gate_sha256'][:12],identity['gate_sha256'][:12]);state['identity']=identity
        if tranche=='W2' and identity.get('gate_sha256'):
            snap=out/'W2'/'gate_snapshots'/(identity['gate_sha256']+'.json')
            if not snap.exists():snap.parent.mkdir(parents=True,exist_ok=True);snap.write_bytes((out/'c1_gate.json').read_bytes())
        ledger=Ledger(out/'ledger.sqlite3',tranche_caps(c,out,tranche),sha(frozen) if frozen.exists() else None)
        state['status']='running';write_json(statepath,state)
        stop_requested=False;old_handlers={}
        def request_stop(signum,frame):
            # Finish the in-flight read and durable page before stopping. A token
            # refresh must not terminate a paid request halfway through its save.
            nonlocal stop_requested
            stop_requested=True
        if live:
            for signum in (signal.SIGTERM,signal.SIGINT):old_handlers[signum]=signal.signal(signum,request_stop)
        failures_in_row=0;streak_items=set();deferred=set()
        try:
            for draw in selected:
                if stop_requested:break
                if draw['source'] in deferred:continue
                dest=out/tranche/'pages'/(draw['id']+'.json')
                if dest.exists() and read_json(dest).get('status') in ('completed','excluded'):continue
                page=None
                try:
                    if hook:hook('before_fetch',draw)
                    page=routes.fetch(draw)
                    hits=ex.match({k:page.get(k) for k in ('pdf_sha256','image_sha256','original_sha256')})
                    if hits:raise ValueError('excluded page/PDF hash')
                    if live:
                        # Frozen F2 pre-read page gates use scan evidence and detector rows.
                        if page.get('physical')!='raster_scan_candidate':raise ValueError('page scan construction unresolved')
                        dr,_=detector(page,cache)
                        heights=[float(np.median(np.array(r['bottom'])-np.array(r['top']))) for r in dr if r['x1']-r['x0']>=50]
                        slopes=[float(np.degrees(np.arctan(np.polyfit(np.arange(len(r['baseline'])),r['baseline'],1)[0]))) for r in dr if len(r['baseline'])>=100]
                        if not dr or (heights and np.median(heights)<10) or (slopes and abs(np.median(slopes))>12):raise ValueError('F2 detector page gate')
                        with Image.open(page['image']) as im:
                            if np.mean(np.asarray(im.convert('L'))<180)<.0015:raise ValueError('blank page gate')
                    def saved_hook():
                        if hook:hook('after_response',page)
                    raw=read_once(ledger,reader,page,tranche,out/'responses',after_response=saved_hook)
                    if hook:hook('after_read',page)
                    fixture=fixture_detector.get(page['id']) if fixture_detector else None
                    from .storage import textless
                    if textless(raw):
                        rr=[]  # Google found no text (blank leaf, plate): the paid read stands, zero rows.
                    else:
                        rr=analyse(page,raw,cache,out/tranche/'crops',serbian=c['serbian_codec'],fixture_cache=fixture,baseline_overrides=baseline_overrides,convention_context=convention_context)
                    for r in rr:r['tranche']=tranche;r['exclusion_manifest_sha256']=draw.get('exclusion_manifest_sha256')
                    # The blind page check references the one retained raster.
                    preview=Path(page['image'])
                    for r in rr:
                        r['crop_source_image']=page['image'];r['crop_source_sha256']=page['image_sha256']
                    record=dict(id=page['id'],source=draw['source'],tranche=tranche,status='completed',image_sha256=page['image_sha256'],pdf_sha256=page.get('pdf_sha256'),original_sha256=page.get('original_sha256'),page=page['page'],item=page['item'],year=page.get('year'),preview=str(preview),preview_sha256=sha(preview),rights=draw.get('rights'),image=str(page['image']),response=str(out/'responses'/(page['image_sha256']+'.json')),response_sha256=sha(out/'responses'/(page['image_sha256']+'.json')),geometry_retained=True,exclusion_manifest_sha256=draw.get('exclusion_manifest_sha256'),analysis_page=page,rows=rr,completed=time.time())
                    write_json(dest,record)
                    if c['storage_diet']:
                        from .storage import discard_page_work
                        discard_page_work(record,cache,out)
                        if hasattr(routes,'prune'):routes.prune(page,True)
                    state['pages'][draw['id']]='completed'
                    if hook:hook('completed',page)
                except UncertainRead:
                    state['pages'][draw['id']]='requires_reconciliation';write_json(statepath,state);raise
                except Exception as e:
                    from .transport import DailyLimit
                    if isinstance(e,DailyLimit):
                        # A provider's rolling daily cap: defer the rest of this source to a later resume (its pages stay
                        # pending, no failure record) and let the other sources continue. Not a fault; outside the brake.
                        deferred.add(draw['source']);state.setdefault('deferred_sources',{})[draw['source']]=dict(reason=str(e),at=time.time())
                        write_json(statepath,state);log.info('%s %s deferred: %s',tranche,draw['source'],e)
                        continue
                    if type(e) is ValueError and str(e) in PRE_READ_REJECTIONS:
                        # A deterministic pre-read rejection: no paid read, not a fault. Recorded once and skipped
                        # on resume; it neither feeds nor resets the failure brake.
                        state['pages'][draw['id']]='excluded'
                        write_json(dest,dict(id=draw['id'],source=draw['source'],tranche=tranche,status='excluded',reason=str(e),item=draw.get('item'),exclusion_manifest_sha256=draw.get('exclusion_manifest_sha256')))
                        write_json(statepath,state);log.info('%s %s excluded: %s',tranche,draw['id'],e)
                        continue
                    state['pages'][draw['id']]='failed';write_json(statepath,state)
                    write_json(out/tranche/'errors'/(draw['id']+'.json'),dict(page_id=draw['id'],error_class=type(e).__name__,error=scrub(str(e)),exclusion_manifest_sha256=draw.get('exclusion_manifest_sha256')))
                    from .ledger import BudgetExceeded
                    if isinstance(e,BudgetExceeded):raise
                    # A page failure is recorded and the run continues. Safety brake against a systematic
                    # fault burning paid reads: 10 consecutive failures, or >20% failed after 50 attempts.
                    failures_in_row+=1;streak_items.add(draw.get('item'));attempted=sum(v in ('completed','failed') for v in state['pages'].values())
                    failed=sum(v=='failed' for v in state['pages'].values())
                    if (failures_in_row>=10 and len(streak_items)>=3) or (attempted>=50 and failed>0.2*attempted):
                        raise RuntimeError(f'failure brake: {failures_in_row} consecutive, {failed}/{attempted} failed') from e
                    continue
                failures_in_row=0;streak_items=set()
                state['updated']=time.time();write_json(statepath,state)
                log.info('%s %s completed',tranche,draw['id'])
            rr=finalize(out,tranche,gate,serbian=c['serbian_codec'],cache=cache);state['status']='stopped_at_page_boundary' if stop_requested else 'deferred_daily_limit' if deferred else 'completed_selected_sources';state['selected_sources']=sources;write_json(statepath,state)
            snapshot=ledger.rows();write_rows(out/'ledger.jsonl',snapshot)
            result=dict(tranche=tranche,completed_pages=sum(v=='completed' for v in state['pages'].values()),ledger_rows=len(snapshot),reserved_usd=sum(r['micro_usd'] for r in snapshot)/1e6,usable_rows=sum(r['usable_final'] for r in rr),classes=dict(Counter(r['primary_class'] for r in rr if r['usable_final'])),disk_bytes_output=disk_bytes(out),disk_bytes_cache=disk_bytes(cache),prune_images=c['prune_images'],live_provider_calls=getattr(reader,'calls',None) if live else 0,mock_reads=getattr(reader,'calls',0) if not live else 0)
            if c['storage_diet']:
                from .storage import compact
                result['storage']=compact(out,cache,tranche)
            result['disk_bytes_output']=disk_bytes(out);result['disk_bytes_cache']=disk_bytes(cache)
            write_json(out/tranche/'receipt.json',result);return result
        finally:
            ledger.close()
            for signum,handler in old_handlers.items():signal.signal(signum,handler)
