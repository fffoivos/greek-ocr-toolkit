"""New deterministic draw, refreeze, source-bound gate preparation and sealed packs.

Run phases individually: freeze, gate, draw, geometry, packs. No readers.
"""
import gzip, shutil, random
from collections import Counter
from r2_common import *
import freeze as oldfreeze, build, measure
import prepare_population_geometry as prep
from greekocr.harvest.admission import page_medians,_page_key

def select_r2(pool):
    return random.Random(SEED_R2).sample(sorted(pool,key=lambda r:r['id']),100)

def freeze():
    old=read(SEG/'CP7_FREEZE.json')
    paths={ROOT/p for p in old['files']}
    paths.update((ROOT/'greekocr/harvest').glob('*.py'))
    paths.update(SEG.glob('*.py'))
    paths.update(BASE.glob('*.py'))
    paths.update((BASE/'r2').rglob('*.py'))
    paths.update((BASE/'r2/launchers').glob('*.sh'))
    paths.update((BASE/'prompts').glob('*.md'))
    paths.add(BASE/'launch_cp7_r2.sh')
    paths.add(SEG/'CP5pb_calibration.json')
    paths.add(ROOT/'tests/test_seg_cp7c.py')
    f=dict(old,schema='SEG-CP7-freeze-r2',files={str(p.relative_to(ROOT)):sha(p) for p in sorted(paths)},
        seed=SEED_R2,geometry_policy='CP2 fallback once per source-bound page; >=10GB free; separate cache; geometry_unavailable is policy, not screen error',
        end_clip_policy='Option C: admitted known class; edge_clip_candidate is diagnostic lower bound only',reading='NOT RUN')
    dump(FREEZE,f,exclusive=True)
    verify()
    lines=sorted(set(f['files'])|set(f['geometry_files']))
    (BASE/'freeze_bound_paths_r2.txt').write_text('DO NOT DELETE: every path below is freeze-bound. Relative paths are relative to repository root.\n'+'\n'.join(lines)+'\n')

def gate():
    verify()
    # Reuse the native witness driver unchanged; redirect only r2 outputs.
    original_dump=oldfreeze.dump; original_sha=oldfreeze.sha
    oldfreeze.verify_freeze=verify
    oldfreeze.HERE=R2
    oldfreeze.inputs=lambda: oldfreeze_records
    oldfreeze.dump=lambda p,obj,*a,**k: original_dump(R2/'frozen_gate.json',obj,*a,**k)
    oldfreeze.sha=lambda p: original_sha(FREEZE if Path(p)==SEG/'CP7_FREEZE.json' else p)
    oldfreeze.gate()

def draw():
    verify();assert not (R2/'keys/draw.jsonl').exists(),'refuse redraw'
    old=read(BASE/'build_receipt.json')
    paths=[Path(p) for p in old['inputs'] if Path(p).name.startswith(('W1_features_','W2_features_'))]
    assert len(paths)==2 and all(p.name.endswith('_20261018_0524.jsonl') for p in paths)
    bindings={p:h for p,h in old['inputs'].items() if Path(p).name.startswith(('W1_features_','W2_features_','SHA256_'))}
    assert all(sha(p)==h for p,h in bindings.items())
    records=[r for p in paths for r in rows(p)]
    assert len(records)==len({r['id'] for r in records})
    _,classes,exbindings=build.exclusion_sets()
    fresh=build.fresh_ids(read(SEG/'calibration_ledger.json'))
    first={r['id'] for r in rows(BASE/'keys/draw.jsonl')}
    pool=population(records,set().union(*classes.values()),fresh|first)
    selected=select_r2(pool)
    assert selected==select_r2(list(reversed(pool)))
    assert not {r['id'] for r in selected}&(fresh|first)
    jsonl(R2/'keys/draw.jsonl',selected)
    jsonl(R2/'gate_geometry_pages.jsonl',prep.page_manifest(selected))
    dump(R2/'draw_receipt.json',dict(seed=SEED_R2,inputs=bindings|exbindings,first_draw_sha256=sha(BASE/'keys/draw.jsonl'),overlap=0,excluded_first=100,excluded_calibration=len(fresh),population=dict(Counter(r['tranche'] for r in pool)),population_per_wave_source_class=dict(Counter('|'.join((r['tranche'],r['source'],r['primary_class'])) for r in pool)),draw_sha256=sha(R2/'keys/draw.jsonl'),pages=len(prep.page_manifest(selected))))

def geometry():
    verify()
    # Existing CP7a3 caches remain valid on unchanged geometry implementation.
    original_identity=prep.identity
    oldsha=sha(SEG/'CP7_FREEZE.json')
    prep.identity=lambda page,dry_run=False: dict(original_identity(page,dry_run),freeze_sha256=oldsha)
    pages=rows(R2/'gate_geometry_pages.jsonl');out=SEG/'CP7_geometry'
    assert prep.enough_disk(out),'disk below 10GB: stop'
    rc=prep.run(pages,out,workers=2,minimum=10_000_000_000)
    assert rc==0,'geometry incomplete; inspect progress'

def packs():
    verify();selected=rows(R2/'keys/draw.jsonl');pages=prep.page_manifest(selected)
    assert all(prep.valid(SEG/'CP7_geometry',p) for p in pages)
    measure.HERE=R2
    by={pid:p for p in pages for pid in p['page_ids']}
    measure.cache_for=lambda r: SEG/'CP7_geometry/cache'/by[r['id'].rsplit('-l',1)[0]]['page_id']
    records=[]
    for p in read(R2/'draw_receipt.json')['inputs']:
        if Path(p).name.startswith(('W1_features_','W2_features_')):records.extend(rows(p))
    medians=page_medians(records)
    sys.path.insert(0,str(SEG));import calibrate_cp5pb as diag
    tolerance=read(SEG/'CP5pb_calibration.json')['selected_tolerance']['value']
    sealed=[]
    for n,r in enumerate(selected):
        c=measure.observe(r,median=medians.get(_page_key(r)))
        try:
            binding=dict(source=r['crop_source_image'],source_sha256=r['crop_source_sha256'],cache_directory=str(measure.cache_for(r)))
            d=diag.measure(r['id'],c['structural'],r['crop_bbox'],binding)
            c['edge_clip_candidate']=d['max_xh']>tolerance if d['status']=='measured' else None
            c['edge_clip_diagnostic']=d
        except (OSError,ValueError,KeyError,StopIteration) as e:
            c['edge_clip_candidate']=None;c['edge_clip_diagnostic']=dict(status='unavailable',reason=str(e))
        sealed.append(c);print(f'sealed {n+1}/100',flush=True)
    path=R2/'keys/sealed_decisions.jsonl.gz'
    path.write_bytes(gzip.compress(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in sealed).encode(),mtime=0));os.chmod(path,0o600)
    build.HERE=R2;build.BEDS=BEDS_R2;build.SEED=SEED_R2;build.crop=measure.crop
    keys=build.make_packs(selected)
    mapping={i:m['line_id'] for items in keys.values() for i,m in items.items() if not m['control']}
    assert len(mapping)==len(set(mapping.values()))==100
    dump(R2/'keys/answer_mapping.json',mapping)
    rules=Counter()
    for c in sealed:
        for rule in ('merged','neighbour_words','orientation','geometry_unavailable'):
            if c[rule] is True:rules[rule]+=1
        if c['crossing']['drop'] is True:rules['crossing']+=1
    dump(R2/'build_receipt.json',dict(freeze_sha256=sha(FREEZE),draw_sha256=sha(R2/'keys/draw.jsonl'),sealed_decisions_sha256=sha(path),pages=len(pages),geometry_unavailable=sum(c['geometry_unavailable'] for c in sealed),orientation_unknown=sum(c['orientation_unknown'] for c in sealed),edge_clip_candidate=sum(c['edge_clip_candidate'] is True for c in sealed),edge_clip_unavailable=sum(c['edge_clip_candidate'] is None for c in sealed),screen_drop=sum(c['screen_drop'] is True for c in sealed),drop_by_rule=dict(rules),mapping_prepared=100,readers_started=0,network='OFF'))
    verify()

oldfreeze_records=oldfreeze.inputs()
if __name__=='__main__':
    guard()
    {'freeze':freeze,'gate':gate,'draw':draw,'geometry':geometry,'packs':packs}[sys.argv[1]]()
