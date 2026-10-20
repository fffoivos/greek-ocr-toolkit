"""Append RU1-0b evidence and bind the completed packs; never launches a reader."""
import json
from pathlib import Path
from collections import Counter
from ru1_census import ART, COLLECT, sha, dump, rows
from ru1_build_packs import WORK, PACK_ROOT, CACHE, COLLECTOR_PYTHON


def finalize():
    build=json.loads((ART/'build.json').read_text());c=build['counts']
    scans=json.loads((ART/'scan_packs_RU10b.json').read_text())
    tests=json.loads((ART/'tests_RU10b.json').read_text())
    assert build['status']=='READY' and len(scans)==c['contexts']==4
    assert all(s['ok'] for s in scans) and tests['passed']>=24
    inventory=json.loads((ART/'keys/control_inventory.json').read_text())
    assert len(inventory)==59 and sum(len(i['slots']) for i in inventory)==65
    assert sum(i['w1_id'] is None for i in inventory)==40
    assert len({i['source_id'] for i in inventory})==59
    appearances=Counter();bed=set();images=0
    for ctx,scan in zip(build['contexts'],scans):
        name=ctx['context'];key=json.loads((ART/f'keys/{name}.json').read_text())
        items=list(rows(PACK_ROOT/name/'r1/items.jsonl'))
        assert 0<len(items)<=100 and ctx['bed_lines']<=90 and ctx['control_lines']==9
        assert len({m['source_id'] for m in key['items'].values()})==len(items)
        for item in items:
            m=key['items'][item['item_id']];p=PACK_ROOT/name/'r1'/item['crop']
            assert sha(p)==m['source_crop_sha256']
            if m['control']:
                assert m['slots'];appearances[m['adjudication_id']]+=1
            else:
                assert m['w1_id'] not in bed;bed.add(m['w1_id'])
            images+=1
        manifest=PACK_ROOT/name/'MANIFEST.r1.json'
        assert sha(manifest)==scan['manifest_sha256']
    assert len(bed)==c['bed_lines'] and len(appearances)==31
    assert max(appearances.values())==2 and min(appearances.values())==1
    assert c['crops_regenerated']==c['crops_needed']==1146 and c['crop_unavailable']==0
    assert not list(rows(ART/'crop_unavailable.jsonl'))
    closure=dict(ok=True,status='ok',scan_packs=scans,contexts_built=4,
                 verification='All packed PNG bytes equal their verified source SHA256; unique source IDs within each context; complete bed covered once; nine slot-bearing controls per context; manifests verified.')
    dump(ART/'pack_closure.json',closure)
    report=WORK/'docs/records/labelfix/secondary/RU10_REPORT.md'
    assert '\n## RU1-0b\n' not in report.read_text(), 'already appended'
    text=['', '## RU1-0b', '',
          '**READY: four blind reader packs built and closure verified.** This section supersedes the earlier blocked readiness and rebuild instructions; the RU1-0 receipt is preserved.', '',
          f"Regenerated **{c['crops_regenerated']}/{c['crops_needed']} W1 crops**, unavailable **{c['crop_unavailable']}**, using `{COLLECTOR_PYTHON}` (arm64, Python {build['regeneration']['python_version']}, Pillow {build['regeneration']['pillow_version']}). Each `ensure_crop` call received a shallow row copy with its crop redirected into `ru1_cache/crops/`. Source-raster and crop SHA256 checks passed. `crop_unavailable.jsonl` is empty. No collector or .git writes, network, image viewing, reader run, or limit probe occurred.", '',
          'The packs contain byte-exact copies of verified PNGs. The copied closure checker permits grayscale L as well as RGB PNGs so W1 bytes remain unchanged; it still checks content-hash names, metadata absence, links, public fields and closure. No image was visually read.', '',
          '**Modern spot check: dropped**, as instructed: all 10 W1 books are pre-1918; no modern sample or replacement population was added.', '',
          f"Bed: **{c['bed_lines']} lines / {c['bed_slots']} masked slots**, with **{c['bed_target_soft_positions']} Google-final-ь edit candidates**. Every bed line appears in exactly one context. Both signs and pre-hyphen slots remain masked; only final Google-ь positions can later yield edit proposals.", '',
          'All **59 control lines / 65 slots** are available: 19 C1 lines use regenerated W1 crops; 40 v2 lines use the saved `items_*.jsonl` adjudication crop paths, matched against the original recorded SHA256 before copying. Private keys retain their original source IDs and explicit `w1_id: null` for v2. The inventory includes 31 slot-bearing lines and 28 zero-slot lines. Zero-slot lines can test only the unmarked-final-hard-sign field and do not count toward the control gate; none were needed in these contexts.', '',
          'Each context has nine slot-bearing controls. Round-robin allocation uses all 31 slot-bearing lines once before repeating five in another context; no line repeats within a context.', '',
          '| Context | Bed lines | Bed slots | Control lines | Control slots | Total items |',
          '|---|---:|---:|---:|---:|---:|']
    for x in build['contexts']:
        text.append('| '+' | '.join(str(x[k]) for k in ['context','bed_lines','bed_slots','control_lines','control_slots','items'])+' |')
    n=sum(x['items'] for x in build['contexts'])
    text+=['',f"Pack root: `{PACK_ROOT}`. Each `ctxNN/r1/` contains only `items.jsonl` and `crops/`; each `ctxNN/MANIFEST.r1.json` binds its files per HANDOVER §4. The copied `scan_packs.py` reports **ok** for all four contexts. Private keys and control truth stay in `artifacts/ru1/keys/`.", '',
           f"Estimated reading cost: {n} items × 0.2 weekly points / 100 = **{n*.002:.3f} weekly points**. No live meter was probed; the ledger remains unused.", '',
           f"Tests re-run: **{tests['passed']} passed** ({tests['text_passed']} text and {tests['scanner_passed']} copied scanner-v4 tests); launcher shell syntax passed. Automatic artifact checks additionally verified complete bed coverage, source-byte equality, source-ID uniqueness, control rotation, availability of all controls, and all four manifests.", '',
           f"Rebuild (requires a fresh empty pack root): `{COLLECTOR_PYTHON} -B scripts/secondary/ru1_build_packs.py`. Receipt: `artifacts/ru1/RU10b_RECEIPT.json`; previous `RU10_RECEIPT.json` kept unchanged."]
    report.write_text(report.read_text()+'\n'.join(text)+'\n')
    inputs=dict(build['inputs'])
    old=json.loads((ART/'RU10_RECEIPT.json').read_text())
    for p,h in old['inputs'].items():
        if p not in inputs: inputs[p]=h
    for p in [WORK/'docs/records/briefs/RU10b_regen_fix.md',ART/'RU10_RECEIPT.json']:
        inputs[str(p)]=sha(p)
    assert all(sha(p)==h for p,h in inputs.items()), 'input drift'
    outputs={}
    for root in [WORK/'scripts/secondary',ART,WORK/'docs/records/labelfix/secondary',PACK_ROOT]:
        for p in root.rglob('*'):
            if p.is_file() and p.name!='RU10b_RECEIPT.json' and '__pycache__' not in p.parts:
                outputs[str(p)]=sha(p)
    for n in ['test_ru1_census.py','test_ru1_map_answers.py']:
        p=WORK/'tests'/n;outputs[str(p)]=sha(p)
    cache={str(p):sha(p) for p in (CACHE/'crops').glob('*.png')}
    receipt=dict(schema='RU10b-v1',status='READY',inputs=inputs,outputs=outputs,regenerated_crop_outputs=cache,
                 regeneration=build['regeneration'],counts=c,contexts=build['contexts'],
                 usable_rule=build['usable_rule'],prior_method=build['prior_method'],pack_closure=closure,tests=tests,
                 no_reader_run=True,no_images_viewed=True,network=False,collector_writes=False,git_writes=False,
                 modern_spot_check='dropped: all 10 books pre1918',
                 receipt_hash_policy='Receipt excludes itself; all pack files and manifests and local deliverables hashed; original RU10 receipt retained.')
    dump(ART/'RU10b_RECEIPT.json',receipt)
    print(f"RU10b READY: crops regenerated {c['crops_regenerated']}/{c['crops_needed']} (unavailable {c['crop_unavailable']}); bed lines {c['bed_lines']} slots {c['bed_slots']} (Google-ь edit candidates {c['bed_target_soft_positions']}); controls {c['controls_lines']} lines / {c['controls_slots']} slots; contexts {c['contexts']}; closure ok; tests {tests['passed']} passed")

if __name__=='__main__':finalize()
