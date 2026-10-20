"""Fresh pre-screen uniform draw and isolated 2x55 packs. Never runs readers."""
import gzip,os,shutil,sys
from collections import Counter
from cp7_common import *
sys.path.insert(0,str(ROOT))
from greekocr.harvest.admission import page_medians,_page_key
from freeze import verify_freeze
from measure import observe,crop


def snapshot_paths(w1_only=False):
    for manifest in sorted(SNAPSHOTS.glob('SHA256_*.txt'),reverse=True):
        ts=manifest.stem[len('SHA256_'):]
        names=[f'W1_features_{ts}.jsonl']+([] if w1_only else [f'W2_features_{ts}.jsonl'])
        paths=[SNAPSHOTS/n for n in names]
        if not all(p.is_file() for p in paths):continue
        declared={}
        for line in manifest.read_text().splitlines():
            m=re.fullmatch(r'([0-9a-f]{64})\s+\*?(.+)',line.strip())
            if m:declared[Path(m[2]).name]=m[1]
        if not all(p.name in declared for p in paths):continue
        for p in paths:assert sha(p)==declared[p.name],'snapshot sha mismatch: '+p.name
        return paths,manifest
    raise FileNotFoundError('No complete hash-verified '+('W1' if w1_only else 'W1+W2')+' snapshot set')


def exclusion_sets():
    base=COLLECTOR/'docs/harvest/collect_v3/release_exclusions'
    config=read(base/'release_exclusions.json');assert EVAL_CLASSES<=set(config['classes'])
    sets={};bindings={str(base/'release_exclusions.json'):sha(base/'release_exclusions.json')}
    for name in sorted(EVAL_CLASSES):
        meta=config['classes'][name];p=base/meta['file'];assert sha(p)==meta['sha256']
        ids={l.strip() for l in p.read_text().splitlines() if l.strip() and not l.lstrip().startswith('#')}
        assert len(ids)==meta['n'];sets[name]=ids;bindings[str(p)]=sha(p)
    return config,sets,bindings


def fresh_ids(ledger):
    return {c['row_id'] for field in ('cases','gallery_witnesses','c1_witnesses','non_gating_witnesses') for c in ledger[field]}


def make_packs(selected):
    prior=ROOT/'docs/harvest/recut_v1/w1_masked/caps1'
    controls=read(prior/'keys/control_truth.json');old=read(prior/'keys/caps1.json')
    assert {c['source_card']['card_id'] for c in controls}==CONTROL_IDS
    assert Counter(c['context'] for c in controls)=={'c1':5,'c2':5}
    existing={c['card_id'] for p in PACK_ROOT.glob('*/*/cards.jsonl') for c in rows(p)}
    allkeys={};custody=[];checks=[]
    for n,bed in enumerate(BEDS):
        ctx='c'+str(n+1);directory=PACK_ROOT/bed/'r1'
        assert not directory.parent.exists(),'Refuse pack overwrite: '+bed
        (directory/'crops').mkdir(parents=True)
        batch=[(r,None) for r in selected[n*50:(n+1)*50]]+[(None,c) for c in controls if c['context']==ctx]
        random.Random(SEED+':order:'+bed).shuffle(batch)
        public=[];key={}
        for row,control in batch:
            if control:
                meta=dict(old['items'][control['opaque_id']]);rid=meta['line_id']
                card=control['source_card'];text=card['google_text'];ws=card['word_scripts']
                previous=next(c for c in rows(PACK_ROOT/'caps1'/ctx/'cards.jsonl') if c['card_id']==control['opaque_id'])
                original=PACK_ROOT/'caps1'/ctx/previous['crop']
                assert sha(original)==meta['crop_sha256']
                meta.update(control_public_id=card['card_id'])
            else:
                rid=row['id'];original=crop(row);text=row['label'];ws=scripts(text)
                meta=dict(control=False,line_id=rid,tranche=row['tranche'],source=row['source'],primary_class=row['primary_class'],crop_sha256=row['crop_sha256'])
            iid='k'+hashlib.sha256((SEED+':opaque:'+bed+':'+rid).encode()).hexdigest()[:10]
            assert iid not in existing;existing.add(iid)
            digest=sha(original);dest=directory/'crops'/(digest+'.png')
            shutil.copyfile(original,dest);assert sha(dest)==meta['crop_sha256']
            key[iid]=meta
            public.append(dict(card_id=iid,crop='crops/'+dest.name,google_text=text,word_scripts=ws))
            custody.append(dict(bed=bed,reader='r1',card_id=iid,line_id=rid,source=str(original),destination=str(dest),sha256=digest))
        jsonl(directory/'cards.jsonl',public)
        ids=[c['card_id'] for c in public];files=closure(directory,ids)
        dump(directory.parent/'MANIFEST.r1.json',dict(bed=bed,reader='r1',files=files))
        dump(HERE/'keys'/(bed+'.json'),dict(bed=bed,readers={'r1':ids},items=key))
        allkeys[bed]=key
        checks.append(dict(bed=bed,reader='r1',bed_items=50,controls=5,items=len(public),
            closure='pass',files=files,canonical_scanner_sha256=SCANNER))
    jsonl(HERE/'keys/crop_custody.jsonl',custody)
    dump(HERE/'pack_closure.json',dict(contexts=checks,canonical_scanner_sha256=SCANNER,violations=0,readers_started=0))
    return allkeys


def build(w1_only=False):
    verify_freeze();assert sha(HERE/'tools/scan_rollout.py')==SCANNER
    assert not (HERE/'build_receipt.json').exists(),'Refuse second draw'
    paths,manifest=snapshot_paths(w1_only);bindings={str(p):sha(p) for p in [*paths,manifest]}
    records=[]
    for p in paths:
        wave=p.name[:2];rr=rows(p);assert all(r['tranche']==wave for r in rr)
        records.extend(rr)
    assert len({r['id'] for r in records})==len(records),'W1/W2 id overlap'
    ledger=read(SEG/'calibration_ledger.json');fresh=fresh_ids(ledger)
    # Source/crop/target bindings of the independently replayed witnesses must
    # agree with the snapshot; do not silently reuse historical labels/flags.
    witness=rows(HERE/'keys/witness_inputs.jsonl');native={r['id']:r for r in records if r['id'] in fresh}
    for r in witness:
        assert r['id'] in native
        for k in ('crop_bbox','crop_sha256','crop_source_image','crop_source_sha256'):
            assert r[k]==native[r['id']][k],('witness snapshot disagreement',r['id'],k)
        if r.get('measured_row_id') is not None:assert r['measured_row_id']==native[r['id']]['measured_row_id']
    cfg,classes,exbindings=exclusion_sets();bindings.update(exbindings)
    excluded=set().union(*classes.values())
    pool=population(records,excluded,fresh)
    selected=select(pool);assert [r['id'] for r in selected]==[r['id'] for r in select(list(reversed(pool)))]
    assert not ({r['id'] for r in selected}&(excluded|fresh))
    jsonl(HERE/'keys/population_ids.jsonl',[dict(id=r['id'],tranche=r['tranche'],source=r['source'],primary_class=r['primary_class']) for r in sorted(pool,key=lambda r:r['id'])])
    jsonl(HERE/'keys/draw.jsonl',selected)
    dump(HERE/'keys/fresh_id_exclusion.json',sorted(fresh))
    dump(HERE/'keys/release_exclusions.json',cfg)
    medians=page_medians(records)
    measurements=[]
    for n,r in enumerate(selected):
        measurements.append(observe(r,median=medians.get(_page_key(r))))
        print(f'drawn measurement {n+1}/100',file=sys.stderr,flush=True)
    assert len(measurements)==100
    data=''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in measurements).encode()
    sealed=HERE/'keys/sealed_decisions.jsonl.gz';sealed.write_bytes(gzip.compress(data,mtime=0));os.chmod(sealed,0o600)
    key=make_packs(selected)
    mapping={iid:m['line_id'] for items in key.values() for iid,m in items.items() if not m['control']}
    assert len(mapping)==len(set(mapping.values()))==100
    dump(HERE/'keys/answer_mapping.json',mapping)
    counts=Counter((r['tranche'],r['source'],r['primary_class']) for r in pool)
    before=Counter((r['tranche'],r['source'],r['primary_class']) for r in records if included(r))
    summary=dict(schema='SEG-CP7a-build-1',freeze_sha256=sha(SEG/'CP7_FREEZE.json'),
        canonical_scanner_sha256=SCANNER,seed=SEED,selection='random.Random(seed).sample(sorted(unique rows by id),100)',
        w1_only=w1_only,population=dict(Counter(r['tranche'] for r in pool)),
        population_per_wave_source_class={'|'.join(k):v for k,v in sorted(counts.items())},
        before_exclusions_per_wave_source_class={'|'.join(k):v for k,v in sorted(before.items())},
        excluded_calibration_ids=len(fresh),excluded_classes={k:len(v) for k,v in classes.items()},
        included_crop_rejection_classes=sorted(set(cfg['classes'])-EVAL_CLASSES),
        draw=100,screen_drop=sum(c['screen_drop'] is True for c in measurements),
        admission_drop=sum(c['admission_drop'] is True for c in measurements),
        unresolved=sum(c['screen_drop'] is None for c in measurements),
        geometry_unavailable=sum(c['geometry_unavailable'] for c in measurements),
        orientation_unknown=sum(c['orientation_unknown'] for c in measurements),
        sealed_decisions_sha256=sha(sealed),draw_sha256=sha(HERE/'keys/draw.jsonl'),
        population_ids_sha256=sha(HERE/'keys/population_ids.jsonl'),inputs=bindings,
        contexts=2,bed_items=100,controls=10,mapping_prepared=100,readers_started=0,
        publish_actions=0,network='OFF',interpreter=sys.executable,
        prompt_comparison=dict(base_verbatim=sha(HERE/'prompts/bsb.md')==sha(REFERENCE/'prompts/bsb.md'),
            base_sha256=sha(HERE/'prompts/bsb.md'),rubric_sha256=sha(HERE/'prompts/segcp7_crop_rubric.md')))
    assert all(sha(p)==d for p,d in bindings.items()),'input drift'
    verify_freeze();dump(HERE/'build_receipt.json',summary,exclusive=True)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':
    offline_guard()
    build('--w1-only' in sys.argv)
