"""Q7 diagnostic orchestration, evidence reuse, and fresh-path composition timing."""
import importlib,json,time,random
from pathlib import Path
import cv2,numpy as np
from .shared.manifest import ROOT,OUT,digest
from .shared.context import Context,read_product,materialize_primitives
from .shared.timing import Registry,dump,append,key,summary
from .shared.geometry import bbox,roi,height_proxy
from .shared.detector import Detector,postprocess,VARIANTS
from .shared.scheduler import scout,dispatch
from .shared import review
from .shared.perturbations import variants as physical_variants

NAMES=['native_contours','layout_barriers','local_ribbons','sheet_lattice','foreground_profiles','residual_ledger','font_guides','image_motifs','selective_rerun','ink_condition','map_graph','classical_residual']
ORDER=['native_contours','layout_barriers','font_guides','local_ribbons','sheet_lattice','foreground_profiles','image_motifs','ink_condition','residual_ledger','map_graph','classical_residual','selective_rerun']
SHARED=OUT/'shared'; CACHE=SHARED/'cache'

PREDICTIONS={
'native_contours':('Existing contours preserve some bent geometry; thresholds trade pale fronts against ghosts.', 's2-3229200bf47ca465a42d-p00004; s2-0ce9d1025b3f23c7119e-p00001'),
'layout_barriers':('Persistent separators split merged prose columns while table cell boxes remain intact.', 'an-a73d22211479-p000301; an-a73d22211479-p000141; s2-661ddf05c8865e7b2c45-p00005'),
'local_ribbons':('Sparse endpoint witnesses nominate curved ends, and clean controls avoid dense tracing.', 's2-3229200bf47ca465a42d-p00004; s2-86865c33eef5932c013b-p00005; s2-77d1bd63d5babbe0df73-p00001'),
'sheet_lattice':('Several lines can share a displacement but mixed leaves and sizes defeat one field.', 's2-3229200bf47ca465a42d-p00004; an-c8b96a901917-p000068; an-d83e7a198ade-p000099'),
'foreground_profiles':('Contrast and edge cues expose uncertainty; sharp ghosts prevent safe automatic rejection.', 's2-09f5dfca4af4d74173c6-p00005; s2-0ce9d1025b3f23c7119e-p00001; an-1be60011c435-p000215'),
'residual_ledger':('Support subtraction reveals omissions hidden by envelopes but still nominates ghosts.', 'an-fd4fa0018ae1-p000037; s2-49598b2e848ab1f0ee1e-p00001; an-d6002cf45e4d-p000058'),
'font_guides':('Local profile families separate scales; baseline and accent semantics often remain unknown.', 'an-ffccc97c07de-p000152; an-d83e7a198ade-p000099; an-e74539ae215c-p000338'),
'image_motifs':('Area texture suppresses some speculative engraving recovery without erasing detected lettering.', 'an-d6002cf45e4d-p000058; an-1f8e7d022643-p000003; an-778126cc8c2b-p000010'),
'selective_rerun':('More samples recover tiny structure and also ghosts; crop inference may cost a full pass.', 'an-7a2b17a3fb0f-p000200; an-d83e7a198ade-p000099; s2-0ce9d1025b3f23c7119e-p00001'),
'ink_condition':('Stroke axes differ from darkness; bold and detached accents defeat automatic damage labels.', 's2-86865c33eef5932c013b-p00005; an-3352d912f2e9-p000104; an-1f8e7d022643-p000003'),
'map_graph':('Regional map paths join some fragments but cannot recover map-absent fronts.', 's2-49598b2e848ab1f0ee1e-p00001; an-d83e7a198ade-p000099'),
'classical_residual':('Stable regions supply independent candidates but also form coherent ghost lines.', 'an-1be60011c435-p000215; s2-09f5dfca4af4d74173c6-p00005; s2-0ce9d1025b3f23c7119e-p00001')}

def config_source(name):
    files=[ROOT/'prototypes/fast_lines'/name/'run.py']+sorted((ROOT/'prototypes/fast_lines/shared').glob('*.py'))
    return key(*[digest(f) for f in files])

def load_context(row,detector=None):
    t=time.perf_counter(); gray=cv2.imread(str(ROOT/row['path']),0); decode=time.perf_counter()-t
    base=json.loads((CACHE/f"{row['page']}.json").read_text()); pm=np.load(CACHE/f"{row['page']}.npy")
    products={n:read_product(n,row['page']) for n in NAMES}
    ref=json.loads((SHARED/'references'/f"{row['page']}.json").read_text())
    ctx=Context(gray,pm,base['items'],products,ref,detector)
    return ctx,decode

def prepare_readmes():
    plan=(ROOT/'docs/research/FAST_LINES_ROUND1_PLAN.md').read_text()
    for index,name in enumerate(NAMES,1):
        p=ROOT/'prototypes/fast_lines'/name/'README.md'
        if p.exists(): continue
        title=f'### A{index:02d} — `{name}`'
        section=plan.split(title,1)[1].split('\n### A',1)[0].split('\n## 7.',1)[0]
        p.write_text(f'# A{index:02d}: {name}\n\nIsolated Q7 prototype. All 174 allowed pages; orientation parked as in the manifest.\n\n'+section+'\n\n## Reproduce\n\nFrom the worktree root:\n\n```sh\nPYTHONDONTWRITEBYTECODE=1 /Users/foivoskarounos-zamparloukos/Projects/greek-ocr-toolkit/.venv/bin/python -m prototypes.fast_lines.run prototype --approach '+name+' --phase 2\n```\n\nRun shared manifest, baseline and references first; dependencies use saved outputs in the topological order in `../README.md`. Configurations are global in code and experiments.json.\n\nLegend: green retained line candidates, cyan explicit support, amber uncertain requests. Baselines stay null unless supported. Discounted results never reach the renderer. Unreviewed candidates are not claimed corrections.\n\n## Running prediction → result → next-step log\n\n')

def log(name,text):
    with (ROOT/'prototypes/fast_lines'/name/'README.md').open('a') as f: f.write(text+'\n\n')

def prototype(rows,args):
    prepare_readmes(); names=ORDER if args.approach=='all' else [args.approach]
    for name in names:
        assert name in NAMES
        if args.phase==1:
            log(name,'### Step 1 — explicit evidence before the heuristic\n\nPrediction: '+PREDICTIONS[name][0]+' Inspect '+PREDICTIONS[name][1]+', both supplied sets and agreement controls.\n\nResult: shared S5 supplies all-line original-pixel crops, dense raw support, contrast/persistence and original-size stroke panels. Initial unconstrained ridges jumped rows even on s2-77d1; those are retained as references-v1. Continuity-constrained v2 is a hypothesis, not a truth label.\n\nNext: run the globally fixed witness/variant study; retain per-line differences and abstain on semantic ownership.')
            continue
        if args.phase==3:
            path=OUT/name/'summary.json'
            if path.exists(): log(name,'### Step 3 — freeze and next decision\n\nResult: raw measurements in the linked `summary.json` and per-page evidence, including all failures/unknowns. No detector rerun or parameter reselection.\n\nNext: use the reviewed findings and failure list in FAST_LINES_ROUND1_RESULTS.md. A candidate is not promoted based on agreement with the old detector.')
            continue
        log(name,'### Step 2 — registered fixed-input prototype study\n\nPrediction (before execution): '+PREDICTIONS[name][0]+' On '+PREDICTIONS[name][1]+'. All other supplied pages and 40 agreement controls test generality. Lengths use body-height proxies/page fractions; no page-name decisions.\n\nDuplicate check: E00 maps, ER dense supports, S2 primitives and saved dependency products are reused. The registry keys image, dependencies, algorithm/source and fixed configuration; successful repeated calls are cache hits.')
        module=importlib.import_module(f'prototypes.fast_lines.{name}.run'); registry=Registry(SHARED/'registry')
        d=Detector() if name=='selective_rerun' else None
        directory=OUT/name; directory.mkdir(parents=True,exist_ok=True); times=[]; source=config_source(name)
        for nr,row in enumerate(rows):
            dep_hashes={n:digest(OUT/n/f"{row['page']}.evidence.json") for n in ORDER[:ORDER.index(name)] if (OUT/n/f"{row['page']}.evidence.json").exists()}
            cfg=dict(phase=2,dependencies=dep_hashes,experiment='one fixed compact study')
            with registry.claim(f'E{NAMES.index(name)+1:02d}',row['sha256'],cfg,source) as event:
                if event is None:
                    p=directory/f"{row['page']}.timing.json"
                    if p.exists(): times.append(json.loads(p.read_text()))
                    continue
                ctx,decode=load_context(row,d)
                primitive_source=key(digest(ROOT/'prototypes/fast_lines/shared/image_evidence.py'),digest(ROOT/'prototypes/fast_lines/shared/geometry.py'))
                primitives=materialize_primitives(ctx,SHARED/'primitives'/f"{row['sha256']}-{primitive_source[:12]}.npz")
                start=time.perf_counter()
                data=dict(items=ctx.items,status='orientation parked; unchanged',regions=[]) if row['parked'] else module.run(ctx,phase=2)
                compute=time.perf_counter()-start
                # Strip diagnostics from candidate-path marginal cost; never hide them from raw totals.
                offline=float(data.get('full_page_seconds',0))
                correction=max(0,compute-offline)
                if name=='native_contours': correction=data.get('variant_seconds',{}).get('poly',compute)
                data.update(event=event['id'],source_hash=source,reference=f'../shared/references/{row["page"]}.html',baseline_items=len(ctx.items))
                t=time.perf_counter(); review.write_result(directory,row,ctx.gray,data,correction,data['reference']); io=time.perf_counter()-t
                for variant,items in data.get('variants',{}).items():
                    if isinstance(items,list):
                        seconds=data.get('variant_seconds',{}).get(variant)
                        if seconds is None:
                            seconds=sum(call['seconds'] for call in data.get('calls',[]) if call['variant']==variant)
                        dump(directory/'variants'/variant/f"{row['page']}.json",review.detector_record(row,items,seconds))
                timing=dict(page=row['page'],group=row['group'],category=row.get('selection',{}).get('category'),parked=row['parked'],
                    compute_s=compute,correction_s=correction,offline_s=offline,decode_s=decode,review_write_s=io,primitives=primitives,
                    items=len(data['items']),base_items=len(ctx.items),event=event['id'],cache='shared primitives reused; marginal algorithm measured')
                dump(directory/f"{row['page']}.timing.json",timing); append(directory/'timing.jsonl',timing); times.append(timing)
                event.update(page=row['page'],algorithm_s=compute)
            if (nr+1)%20==0 or nr==len(rows)-1: print(name,nr+1,len(rows),flush=True)
        sums={group:summary([r['correction_s'] for r in times if r['group']==group and not r['parked']]) for group in ('development','agreement','discrepancy')}
        sums.update(total_records=len(times),changed_count_pages=sum(r['items']!=r['base_items'] for r in times))
        dump(directory/'summary.json',sums); review.gallery(directory,rows,name)
        (directory/'README-results.md').write_text(f'# {name}\n\nMeasured timing: algorithm-only after shared cached dependencies; review I/O and full-page comparators are separate. See fresh composed timing for paid runtime.\n\n```json\n'+json.dumps(sums,indent=2)+'\n```\n\nLegend: green retained candidates, cyan support, amber requests. All original-pixel line crops: ../shared/references/. Per-line and per-page verdicts remain explicitly unreviewed unless adjudication.jsonl says otherwise.\n')
        log(name,'Measured result: `'+json.dumps(sums,sort_keys=True)+'`. These are marginal times with diagnostic inputs reused, not complete page latency.\n\nNext: inspect changed regions and raw supports; compare against the fresh composed path. No automatic acceptance from counts or old-model overlap.')


def compose(rows,args):
    """One real fresh path, three repetitions. Competing repairs are not stacked."""
    registry=Registry(SHARED/'registry'); d=Detector(); d.infer(cv2.imread(str(ROOT/rows[0]['path']),0))
    order=list(rows); random.Random(20261010).shuffle(order); modules={n:importlib.import_module(f'prototypes.fast_lines.{n}.run') for n in ORDER}
    source=key(*[config_source(n) for n in ORDER]); all_times=[]; directory=OUT/'composition'; directory.mkdir(exist_ok=True)
    for nr,row in enumerate(order):
        with registry.claim('ET',row['sha256'],dict(repeats=3,dispatch='barriers + witnessed local ribbons; all unresolved evidence remains in ledger'),source) as event:
            if event is None:
                all_times+=json.loads((directory/f"{row['page']}.timing.json").read_text()); continue
            timings=[]
            for rep in range(1 if row['parked'] else 3):
                start=time.perf_counter(); t=time.perf_counter(); gray=cv2.imread(str(ROOT/row['path']),0); decode=time.perf_counter()-t
                t=time.perf_counter(); pm,meta=d.infer(gray); tpost=time.perf_counter(); items=postprocess(pm,row['image_size']); post=time.perf_counter()-tpost; base=time.perf_counter()-t
                ctx=Context(gray,pm,items); t=time.perf_counter(); witness=scout(gray,pm,items); scout_s=time.perf_counter()-t
                cost={}; data=dict(items=items,status='orientation parked; unchanged',regions=[])
                if not row['parked']:
                    # Baseline quad retained. Layout is checked regardless of residual coverage.
                    for name in ('layout_barriers','local_ribbons'):
                        t=time.perf_counter(); product=modules[name].run(ctx,2); cost[name]=time.perf_counter()-t; ctx.products[name]=product
                    lay=ctx.get('layout_barriers'); loc=ctx.get('local_ribbons')
                    data=lay if lay.get('changes') else loc
                    # Scout remains explicit and unresolved; no covert cached correction.
                    data=dict(data,regions=witness['regions'],scout=witness,dispatch='layout split if supported, otherwise local ribbon candidates',unresolved=bool(witness['regions']))
                wall=time.perf_counter()-start; correction=wall-decode-base
                timings.append(dict(page=row['page'],group=row['group'],parked=row['parked'],repeat=rep,decode_s=decode,baseline_s=base,postprocess_s=post,
                    **meta,scout_s=scout_s,branches=cost,added_s=correction,compute_s=wall-decode,wall_s=wall,trigger=witness['trigger'],unresolved_regions=len(witness['regions']),event=event['id']))
            review.write_result(directory,row,gray,data,float(np.median([r['compute_s'] for r in timings])))
            dump(directory/f"{row['page']}.timing.json",timings)
            for r in timings: append(directory/'timing.jsonl',r)
            all_times+=timings; event['page']=row['page']
        if (nr+1)%20==0 or nr==len(rows)-1: print('composition',nr+1,len(rows),flush=True)
    dump(directory/'summary.json',{group:{k:summary([r[k] for r in all_times if r['group']==group and not r['parked']]) for k in ('baseline_s','scout_s','added_s','compute_s','wall_s')} for group in ('development','agreement','discrepancy')})
    review.gallery(directory,rows,'Fresh-path conditional composition')


def perturb(rows,args):
    directory=SHARED/'perturbations'; directory.mkdir(exist_ok=True)
    measurement_path=directory/'measurements.json'
    saved=json.loads(measurement_path.read_text()) if measurement_path.exists() else []
    records={(r['page'],r['variant']):r for r in saved}
    # Deterministic uniform manifest positions, not a tuned named-page selection.
    selected=[rows[i] for i in np.linspace(0,len(rows)-1,min(8,len(rows)),dtype=int) if not rows[i]['parked']]
    registry=Registry(SHARED/'registry')
    for row in selected:
        with registry.claim('EP',row['sha256'],dict(seed=20261010,exemplar='middle baseline line'),digest(ROOT/'prototypes/fast_lines/shared/perturbations.py')) as event:
            if event is None: continue
            gray=cv2.imread(str(ROOT/row['path']),0); base=json.loads((CACHE/f"{row['page']}.json").read_text()); items=base['items']
            if not items: continue
            item=items[len(items)//2]; height=height_proxy(items,row['image_size']); b=bbox(item); x0,y0,x1,y1=roi(b,gray.shape); crop=gray[y0:y1,x0:x1]
            cells=[]
            from .shared.image_evidence import ImageEvidence,profile_features
            for name,(image,change) in physical_variants(crop,height).items():
                e=ImageEvidence(image,height); gx,gy=e.gradients; f=profile_features(e.contrast,gx,gy,e.persistence)
                path=directory/f'{row["page"]}-{name}.jpg'; review.save_image(path,image); np.save(directory/f'{row["page"]}-{name}.npy',change)
                records[(row['page'],name)]=dict(page=row['page'],bbox=[x0,y0,x1,y1],variant=name,features=f,synthetic=True,event=event['id'])
                cells.append((name,image))
            review.atlas(cells,directory/f'{row["page"]}-sheet.jpg',columns=2,cell_width=700)
    dump(measurement_path,list(records.values()))


def report(rows,args):
    records={name:json.loads((OUT/name/'summary.json').read_text()) for name in NAMES}
    dump(SHARED/'all_summaries.json',records)
    links=''.join(f'<li><a href="../{n}/index.html">A{i:02d} {n}</a></li>' for i,n in enumerate(NAMES,1))
    (SHARED/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Q7 fast lines</title><h1>Q7 fast line finding</h1><p>174 allowed pages, 173 upright. Prototype outputs and explicit references; candidates are not validated corrections.</p><ul>'+links+'</ul><a href="../composition/index.html">Fresh composition and timing</a> · <a href="baseline/index.html">Baseline</a> · <a href="manifest.json">Manifest</a> · <a href="adjudication.jsonl">Visual verdicts</a>')
