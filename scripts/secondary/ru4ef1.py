"""Offline phase-1 extension. Leaves the original hash-bound protocol untouched."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from collections import Counter, defaultdict
import html
import json
from pathlib import Path
import random

import ru4e2 as n
m = n.m
ART, PACK = n.ART, n.PACK
OUT = m.SCRATCH/'ru1_review/ru4e2'
SEED = 'RU4EF1:20261018:audit:20+10'
ORIGINAL_COLLECT = m.collect
ORIGINAL_REPLACEMENT = m.replacement
ORIGINAL_CLOSURE = m.closure


def signature(art, pack, ctx, reader):
    rd = pack/ctx/reader
    runpath = art/'answers'/(m.stem(ctx, reader)+'.run.json')
    run = json.loads(runpath.read_text())
    return m.bindings([runpath, Path(run['rollout']),
        art/f'keys/{m.stem(ctx, reader)}.json',
        rd.parent/f'MANIFEST.{reader}.json', *rd.rglob('*'),
        Path(n.__file__), Path(m.__file__), *n.BOUND.glob('*')])


def precollect(task):
    art, pack, ctx, reader = task
    art, pack = Path(art), Path(pack)
    cache = art/'phase1_cache'/(m.stem(ctx, reader)+'.json')
    before = signature(art, pack, ctx, reader)
    if cache.exists():
        obj = json.loads(cache.read_text())
        # Orchestration edits do not change ORIGINAL_COLLECT. Its engine,
        # adapter and every bound scanner/helper remain signature-bound.
        obj['inputs'].pop(str(Path(__file__).resolve()), None)
        if obj['inputs'] == before and all(m.sha(p) == h for p,h in obj.get('outputs',{}).items()):
            return ctx+'/'+reader, obj
    try:
        mapped, gate, cov, ev = ORIGINAL_COLLECT(art, pack, ctx, reader, set())
        obj = dict(result=[mapped, gate, cov, ev], outputs=ev)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        obj = dict(error=str(exc))
    if signature(art, pack, ctx, reader) != before:
        raise ValueError('input changed during collection')
    obj['inputs'] = before
    m.dump(cache, obj)
    print(ctx+'/'+reader+': '+(obj.get('error') or obj['result'][1]['status']), flush=True)
    return ctx+'/'+reader, obj


def closure(pack, art, runtime=False, replacement=False):
    if not replacement or not list(Path(pack).glob('*/r4')):
        return ORIGINAL_CLOSURE(pack, art, runtime, replacement)
    m.external(pack)
    m.scan_packs.ROOT = art
    results = []
    for ctx in Path(pack).iterdir():
        if ctx.name != 'ctx01' or ctx.is_symlink() or {p.name for p in ctx.iterdir()} != {'r4','MANIFEST.r4.json'}:
            if runtime:
                raise ValueError('unexpected r4 pack closure')
            if {p.name for p in ctx.iterdir()} != {'r4'}:
                raise ValueError('unexpected r4 pack closure')
        results.append(m.scan_packs.scan(ctx/'r4', 'yer', write_manifest=not runtime, allow_runtime=runtime))
    if not results or any(not r['ok'] for r in results):
        raise ValueError('r4 pack closure failed')
    return results


def replacement(art, pack, ctx, reader, role='r3'):
    # Reuse the canonical r3 construction; rename the second independent
    # assignment to r4 without changing any original bound pack or receipt.
    if role == 'r3':
        return ORIGINAL_REPLACEMENT(art, pack, ctx, reader)
    rp = pack.parent/'ru4e_r4'/(ctx+'-'+reader)
    ra = art/'r4_replacements'/(ctx+'-'+reader)
    receipt = ra/'replacement.json'
    if receipt.exists():
        obj = json.loads(receipt.read_text())
        if obj['replaces'] != ctx+'/'+reader or obj['reader'] != 'r4':
            raise ValueError('r4 identity mismatch')
        if any(m.sha(p)!=h for p,h in obj['bindings'].items()):
            raise ValueError('r4 binding changed')
        closure(rp, ra, runtime=True, replacement=True)
        return obj
    if rp.exists() or ra.exists():
        raise ValueError('partial r4 exists')
    key = json.loads((art/f'keys/{m.stem(ctx,reader)}.json').read_text())
    public = m.rows(pack/ctx/reader/'items.jsonl')
    seed = SEED+':'+ctx+':'+reader+':r4'
    random.Random(seed).shuffle(public)
    order = [dict(key['items'][i['item_id']], masked_text=i['masked_text'], image=str(pack/ctx/reader/i['crop'])) for i in public]
    used = {iid for p in [*(art/'keys').glob('*.json'), *art.glob('r[34]_replacements/*/keys/*.json')] for iid in json.loads(p.read_text())['items']}
    m.assignment(rp/'ctx01/r4',ra,'ctx01','r4',order,used)
    closure(rp,ra,replacement=True)
    obj = dict(identity=ctx+'/'+reader+'/r4',logical_reader=reader,replaces=ctx+'/'+reader,
        art=str(ra),pack=str(rp),context='ctx01',reader='r4',seed=seed,
        bindings=m.bindings([*rp.rglob('*'),*(ra/'keys').glob('*.json')]),status='READY_FOR_READING',no_reader_run=True)
    m.dump(receipt,obj)
    return obj


def sheets(decisions, report):
    OUT.mkdir(parents=True,exist_ok=True)
    lookup = {}
    positions = defaultdict(list)
    for ctx in PACK.glob('ctx*'):
        key = json.loads((ART/f'keys/{ctx.name}.json').read_text())['items']
        for item in m.rows(ctx/'r1/items.jsonl'):
            meta=key[item['item_id']]
            lookup[meta['row_id']] = (ctx/'r1'/item['crop'],item,meta)
    # Agreement references may include Google-hard slots outside candidate scope.
    for identity, state in report['contexts'].items():
        if state['status']!='VALID': continue
        parts=identity.split('/')
        if len(parts)==2:
            a,ctx,reader=ART,parts[0],parts[1]
        else:
            repl=next(r for r in report['replacements'] if r['identity']==identity)
            a,ctx,reader=Path(repl['art']),repl['context'],repl['reader']
        for p in m.rows(a/'answers'/(m.stem(ctx,reader)+'.mapped.jsonl')):
            if not p['control']: positions[p['row_id'],p['offset']].append(p)
    refs={}
    rng=random.Random(SEED)
    hard=sorted([d for d in decisions if d['decision']=='edit_hard'],key=lambda d:(d['row_id'],d['offset']))
    soft=sorted([d for d in decisions if d['decision']=='keep_soft'],key=lambda d:(d['row_id'],d['offset']))
    if len(hard)<20 or len(soft)<10: raise ValueError('audit population shortfall')
    audit=rng.sample(hard,20)+rng.sample(soft,10)
    review=[d for d in decisions if d['decision']=='hold']
    cells=[dict(d,set=kind,cell=i+1) for i,(kind,d) in enumerate([('review',d) for d in review]+[('audit',d) for d in audit])]
    target_keys={(c['row_id'],c['offset']) for c in cells}
    for book in sorted({d['book'] for d in cells}):
        refs[book]={}
        for sign in ('ъ','ь'):
            choices=[]
            for (rid,off),votes in positions.items():
                if (rid,off) in target_keys:continue
                if rid not in lookup or lookup[rid][2]['book']!=book: continue
                if len(votes)==2 and all(p['call']==sign for p in votes):
                    choices.append((rid,off))
            basis='two_valid_reader_agreement_not_adjudicated'
            if not choices:
                basis='raw_google_label_only_not_adjudicated'
                for rid,(_,_,meta) in lookup.items():
                    if meta['book']==book:
                        choices += [(rid,s['offset']) for s in meta['slots'] if s['google']==sign and (rid,s['offset']) not in target_keys]
            if not choices:
                # Modern books can lack word-final hard signs. A labelled
                # internal sign is a comparison only, never inferred truth.
                basis='raw_google_internal_sign_only_not_adjudicated'
                for row in sorted(m.rows(ART/'census_all_rows.jsonl'),key=lambda r:r['id']):
                    if m.bid(row)!=book or sign not in row['label']:continue
                    offsets=[i for i,ch in enumerate(row['label']) if ch==sign and (row['id'],i) not in target_keys]
                    if not offsets:continue
                    off=offsets[0]
                    source=Path(row['crop']).expanduser()
                    if not source.is_absolute():source=m.SOURCES[row['ru4e_split']].parents[4]/source
                    cleaned,provenance=n.clean_crop(source)
                    lookup[row['id']]=(cleaned,dict(masked_text=row['label']),dict(book=book,slots=[],source_crop_sha256=m.sha(cleaned),**provenance))
                    choices=[(row['id'],off)]
                    break
            if not choices: raise ValueError('no same-book reference '+book+' '+sign)
            rid,off=sorted(choices)[0]
            refs[book][sign]=dict(row_id=rid,offset=off,basis=basis,
                crop=str(lookup[rid][0]),crop_sha256=lookup[rid][2]['source_crop_sha256'],
                provenance={k:v for k,v in lookup[rid][2].items() if k.startswith(('original_crop','native_'))})

    inputs={}
    def image_block(rid,offset):
        source,item,meta=lookup[rid]
        dest=OUT/'crops'/source.name;dest.parent.mkdir(exist_ok=True)
        if not dest.exists(): m.shutil.copyfile(source,dest)
        if m.sha(dest)!=meta['source_crop_sha256']: raise ValueError('sheet crop changed')
        inputs[str(source)]=m.sha(source)
        text=item['masked_text']
        for j,slot in enumerate(meta['slots'],1): text=text.replace(f'⟦{j}⟧',slot['google'])
        if offset>=len(text): raise ValueError('reference offset outside raw text')
        marked=text[:offset]+'【'+text[offset]+'】'+text[offset+1:]
        from PIL import Image
        with Image.open(dest) as im: im.load();width=im.width
        return f'<code>{html.escape(marked)}</code><br><img src="crops/{dest.name}"><br><img width="{4*width}" src="crops/{dest.name}">'
    template=[];links=[]
    for kind in ('review','audit'):
        group=[c for c in cells if c['set']==kind]
        for start in range(0,len(group),10):
            name=f'{kind}_{start//10+1:03}.html';links.append(name)
            page=['<!doctype html><meta charset="utf-8"><style>body{font:16px sans-serif}article{border:1px solid;padding:16px;margin:16px}img{image-rendering:pixelated}code{white-space:pre-wrap}section{overflow:auto}</style>',
                '<p>Native full lines and 4× nearest-neighbour views. Brackets mark RAW Google code-point offsets, not inferred glyph boxes. References are same-book comparisons, not adjudicated truth. No pixel review has been performed.</p>']
            for c in group[start:start+10]:
                page += [f'<article><h2>Cell {c["cell"]}: {kind} / {c["decision"]}</h2><p>{html.escape(c["row_id"])} offset {c["offset"]} / {c["reason"]}</p><section>'+image_block(c['row_id'],c['offset'])+'</section>']
                for sign,ref in refs[c['book']].items():
                    page += [f'<h3>Same-book {sign}: {ref["basis"]}</h3><section>'+image_block(ref['row_id'],ref['offset'])+'</section>']
                page += ['</article>']
                template.append({k:c[k] for k in ('cell','set','row_id','offset','decision','reason','book')} | dict(crop_sha256=lookup[c['row_id']][2]['source_crop_sha256'],call=None,pixel_checked=False,reviewer=None,note=None))
            (OUT/name).write_text('\n'.join(page))
    (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8">'+''.join(f'<p><a href="{p}">{p}</a></p>' for p in links))
    m.jsonl(OUT/'template.jsonl',template);m.jsonl(OUT/'cells.jsonl',cells);m.dump(OUT/'references.json',refs)
    assert Counter(c['decision'] for c in cells if c['set']=='audit')=={'edit_hard':20,'keep_soft':10}
    assert len({(c['row_id'],c['offset']) for c in audit})==30
    result=dict(path=str(OUT),audit_cells=30,review_cells=len(review),seed=SEED,
        audit_counts={'edit_hard':20,'keep_soft':10},inputs=inputs,
        outputs=m.bindings([p for p in OUT.rglob('*') if p.is_file() and p.name!='manifest.json']),
        validation='counts, distinct audit positions, crop hashes, native PNG decoding; no visual reading')
    m.dump(OUT/'manifest.json',result)
    return result


def finalize(workers=4):
    n.configure();info=m.validate(ART,PACK)
    tasks=[(str(ART),str(PACK),c['context'],r) for c in info['contexts'] for r in ('r1','r2')]
    with ProcessPoolExecutor(max_workers=workers) as pool: results=dict(pool.map(precollect,tasks))
    original_rollouts=set()
    for _,_,ctx,reader in tasks:
        digest=m.sha(json.loads((ART/'answers'/(m.stem(ctx,reader)+'.run.json')).read_text())['rollout'])
        if digest in original_rollouts:results[ctx+'/'+reader]=dict(error='rollout reused across independent reads')
        original_rollouts.add(digest)
    bad={k for k,v in results.items() if v.get('error') or v['result'][1]['status']!='VALID'}
    replacements=[]
    for c in info['contexts']:
        ctx=c['context'];roles=[r for r in ('r1','r2') if ctx+'/'+r in bad]
        for j,r in enumerate(roles): replacements.append(replacement(ART,PACK,ctx,r,'r3' if j==0 else 'r4'))
    def collect(a,p,ctx,r,seen):
        if a==ART:
            obj=results[ctx+'/'+r]
            if obj.get('error'): raise ValueError(obj['error'])
            digest=m.sha(json.loads((a/'answers'/(m.stem(ctx,r)+'.run.json')).read_text())['rollout'])
            if digest in seen: raise ValueError('rollout reused across independent reads')
            seen.add(digest)
            return obj['result']
        return ORIGINAL_COLLECT(a,p,ctx,r,seen)
    # The original finaliser routes VOID; failed reads are routed below as well.
    byrole={r['replaces']:r for r in replacements}
    m.collect=collect;m.closure=closure
    m.replacement=lambda a,p,c,r: byrole[c+'/'+r]
    report=m.finalize(ART,PACK)
    # m.finalize only understands canonical r3 run names. Route r4 and invalid
    # originals explicitly, reconstructing votes from admitted evidence.
    votes=defaultdict(list)
    report['replacements']=replacements
    for ctx in info['contexts']:
        for role in ('r1','r2'):
            identity=ctx['context']+'/'+role
            if identity in bad:
                repl=byrole[identity];a,p=Path(repl['art']),Path(repl['pack'])
                if not (a/'answers'/(m.stem('ctx01',repl['reader'])+'.run.json')).exists(): continue
                try: mapped,gate,cov,ev=ORIGINAL_COLLECT(a,p,'ctx01',repl['reader'],original_rollouts)
                except (OSError,ValueError,KeyError,TypeError) as exc:
                    report['contexts'][repl['identity']]=dict(status='FAILED',reason=str(exc));continue
                identity=repl['identity'];report['contexts'][identity]=dict(status=gate['status'],gate=gate)
                report['coverage'][identity]=cov;report['evidence'].update(ev)
                if gate['status']!='VALID': continue
            else:
                if report['contexts'][identity]['status']!='VALID': continue
                mapped,gate,cov,ev=results[identity]['result']
            for pos in mapped:
                if pos['control'] or pos['google']!='ь' or pos['kind']!='final':continue
                votes[pos['row_id'],pos['offset']].append(dict(logical_reader=role,context=identity,call=pos['call'],gate_status='VALID',confidence=pos['confidence'],item_id=pos['item_id'],evidence=ev))
    ds=[m.combine(p,votes[p['row_id'],p['offset']]) for p in m.rows(ART/'candidate_positions.full.jsonl')]
    m.jsonl(ART/'decisions.jsonl',ds);m.jsonl(ART/'r3_to_run.jsonl',replacements)
    report.update(counts=dict(Counter(d['decision'] for d in ds)),decisions_sha256=m.sha(ART/'decisions.jsonl'),status='PENDING_READS' if any(len(d['reads'])!=2 for d in ds) else 'AWAITING_LEAD')
    _,report['lead']=m.lead_sheets(ART,PACK,ds)
    report['lead_material']=sheets(ds,report)
    report['lead_review_reasons']=dict(Counter(d['reason'] for d in ds if d['decision']=='hold'))
    items=sum(len(m.rows(Path(r['pack'])/'ctx01'/r['reader']/'items.jsonl')) for r in replacements)
    report['replacement_budget']=dict(contexts=len(replacements),items=items,estimated_points=round(items*.002,3),threshold=70)
    m.dump(ART/'finalize.json',report)
    m.dump(ART/'RU4EF1_RECEIPT.json',dict(report,network_used=False,git_writes=False,new_reader_runs=0,version_written=False,
        orchestration=m.bindings([Path(__file__),m.HERE/'run_ru4e2_r3_all.sh',m.HERE/'ru4e2_finalize_f1.sh'])))
    print(json.dumps(dict(counts=report['counts'],bad=sorted(bad),replacement_budget=report['replacement_budget'],lead=report['lead_material']['path']),indent=2))


def drive(dry_run):
    n.configure();m.closure=closure
    m.tasks=lambda info,a,p: m.rows(a/'r3_to_run.jsonl')
    # Canonical driver enforces the measured 70% stop and no repeated attempts.
    # It validates r3 bindings itself; validate r4 here before entering it.
    for task in m.rows(ART/'r3_to_run.jsonl'):
        for path,digest in task['bindings'].items():
            if m.sha(path)!=digest:raise ValueError('replacement changed')
        closure(Path(task['pack']),Path(task['art']),runtime=True,replacement=True)
    def checked_runner(cmd,**kwargs):
        task=next(t for t in m.rows(ART/'r3_to_run.jsonl') if str(Path(t['pack'])/t['context']/t['reader'])==cmd[3])
        for path,digest in task['bindings'].items():
            if m.sha(path)!=digest:raise ValueError('replacement changed')
        closure(Path(task['pack']),Path(task['art']),runtime=True,replacement=True)
        return m.subprocess.run(cmd,**kwargs)
    print(json.dumps(m.drive(ART,PACK,dry_run=dry_run,runner=checked_runner),indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['finalize','drive'])
    parser.add_argument('--dry-run',action='store_true');parser.add_argument('--workers',type=int,default=4)
    args=parser.parse_args()
    if args.action=='finalize':finalize(args.workers)
    else:drive(args.dry_run)
