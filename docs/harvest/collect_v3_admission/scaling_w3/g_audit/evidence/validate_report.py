import pathlib,json,hashlib,csv,collections
R=pathlib.Path(__file__).resolve().parent.parent;D=R/'evidence'
load=lambda p:json.loads(p.read_text())
for p in R.rglob('*.json'):load(p)
m=list(csv.DictReader((R/'coverage_matrix.csv').open()));c=collections.Counter(r['status'] for r in m);assert c=={'partial':920,'no':368};assert len(m)==1288
summary=load(D/'benchmark_summary.json');assert sum(summary['splits'].values())==sum(summary['sources'].values())==sum(summary['classes'].values())==2690
bm=[json.loads(x) for x in (D/'benchmark_metadata.jsonl').read_text().splitlines()];assert len(bm)==2690;assert len({r['row_id'] for r in bm})==2690
join=load(D/'benchmark_edition_join.json');assert join['joined']==2690 and join['edition_count']==199 and join['split_conflicts']==0
fi=load(D/'font_inventory.json');assert len(fi)==67 and all(f['local_hash_match'] and f['historical_full_sha_match'] for f in fi);assert sum(f['rendered_rows_all_splits']>0 for f in fi)==64
E=load(D/'e1_build_info.json');A=load(D/'a12_build_info.json');assert hashlib.sha256((D/'e1_build_info.json').read_bytes()).hexdigest()==A['encoding_derivation']['source_receipt_sha256'];assert hashlib.sha256((D/'recipe.v5.json').read_bytes()).hexdigest()==A['recipe_sha256']==E['recipe_sha256'];assert A['recipe_effective_sha256']==E['recipe_effective_sha256']
ex=load(R/'exposure_hits.json');assert ex['observed_input_manifest_hits']==2 and ex['upstream_o5_complete']['binding_match'];assert sum(x.get('dropped',0) for x in load(D/'mix1_prior_text_audit.json')['synthetic_v5']['per_source'].values())==287
line='G-AUDIT: done | renderer inputs <fonts 67, recipes 2, text sources 9> | coverage yes/partial/no/unknown 0/920/368/0 over 1288 | exposure hits 2 (o1d_real) | gaps 7 | no jobs';assert (R/'G_AUDIT.md').read_text().splitlines()[-1]==line
manifest=R/'GUARDED_COMMIT_LIST.json'
if manifest.exists():
 for r in load(manifest)['files']:
  p=R/r['relative_path'];assert p.is_relative_to(R) and not p.is_symlink();assert p.stat().st_size==r['bytes'];assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
print('PASS: metadata, counts, custody, font and exposure bindings, final line'+(', guarded hashes' if manifest.exists() else ''))
