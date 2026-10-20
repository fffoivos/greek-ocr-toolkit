import pathlib,json,hashlib,subprocess,collections
D=pathlib.Path(__file__).parent;P=pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr')
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
details=json.loads((D/'remote_details.json').read_text());bind=next(x for x in details if 'keys' in x)
w=[]
specs=[('docs/data_contracts.md',185,208),('docs/ocr_program_2026-10-06/TRAINING_DIRECTIONS_20261016.md',53,55),('docs/ocr_program_2026-10-06/POST_CLEANUP_PROGRAMME_20261019.md',1,1),('factory/src/build.rs',75,143),('factory/src/render.rs',177,205),('factory/src/corpus.rs',1,20),('bench/e1_prepare.py',128,153)]
for path,start,end in specs:
 p=P/path;b=p.read_bytes();ls=b.decode().splitlines();w.append(dict(path=str(p),sha256=sha(b),start=start,end=end,excerpt='\n'.join(ls[start-1:end]),scope='current local source; historical identity checked separately'))
for path in ['factory/src/build.rs','factory/src/render.rs','factory/src/select.rs','factory/src/corpus.rs','bench/e1_prepare.py','docs/data_contracts.md']:
 r=subprocess.run(['git','-C',str(P),'show','2e3cf6f2b68dfca94a8c4ae7403a6b61a37d8d7b:'+path],capture_output=True)
 if r.returncode:continue
 b=r.stdout;lines=b.decode().splitlines(); needles=['let tracking','rustybuzz::shape','font','uppercase','letterspac','leader','onum','unmapped','Pre-reform']
 ex=[dict(line=i,text=l) for i,l in enumerate(lines,1) if any(n in l for n in needles)]
 expected=bind['inputs'].get('/home/ubuntu/work/greek-page-ocr/'+path)
 w.append(dict(path=path,revision='2e3cf6f2b68dfca94a8c4ae7403a6b61a37d8d7b',sha256=sha(b),prepare_sha256=expected,prepare_match=expected==sha(b),selected_lines=ex))
dump('source_witnesses.json',w)
# Source/edition inventory, without pretending doc hashes are bibliographic titles.
bench=[json.loads(x) for x in (D/'benchmark_metadata.jsonl').read_text().splitlines()];join=json.loads((D/'benchmark_edition_join.json').read_text());ed={r['row_id']:r['edition_id'] for r in join['bindings']};by=collections.defaultdict(list)
for r in bench:by[r['source']].append(r)
inv={s:dict(rows=len(rs),classes=dict(collections.Counter(r['primary_class'] for r in rs)),scripts=dict(collections.Counter(r['scripts_from_reference'] for r in rs)),edition_ids=sorted({ed[r['row_id']] for r in rs}),seal_docs=sorted({r['doc'] for r in rs}),orthographies=dict(collections.Counter(str(r['tags']['evidence_facets'].get('orthography')) for r in rs)),titles='not present in seal04 row metadata; no title inferred from source name') for s,rs in by.items()};dump('benchmark_source_inventory.json',inv)
ex=json.loads((D.parent/'exposure_hits.json').read_text());o5=json.loads((D/'o5_source_exposure.json').read_text());ex['upstream_o5_complete']=o5;ex['observed_input_manifest_hits']=len(o5['hits']);ex['observed_input_manifest_hit_sources']=['o1d_real'];ex['per_text_source']['o1d_real']['upstream_o5_before_filter']=o5['per_source']['o1d_real'];(D.parent/'exposure_hits.json').write_text(json.dumps(ex,ensure_ascii=False,indent=2)+'\n')
# Compact witnesses: do not keep the full seal records, repeated glyph maps or unrelated crop bindings.
for x in details:
 if 'inputs' in x:
  x['inputs']={k:v for k,v in x['inputs'].items() if k.startswith('/home/ubuntu/data/') or '/assets/fonts/' in k or '/factory/' in k or k.endswith(('synth_corpus.jsonl','exclusions_test.txt','e1_prepare.py'))}
  x['other']={k:v for k,v in x['other'].items() if k!='document_assignment'}
dump('remote_details.json',details)
fonts=json.loads((D/'font_inventory.json').read_text());cmaps={f['stem']:f.pop('cmap_codepoints') for f in fonts if 'cmap_codepoints' in f};dump('font_cmaps.json',cmaps);dump('font_inventory.json',fonts)
# Slim benchmark rows retain references for exact audit reproducibility, dimensions and all tags.
for r in bench:
 r['edition_id']=ed[r['row_id']];r['edition_identity']=r['edition_id'];r['edition_identity_kind']='row_id_join_to_bound_candidates_v3'
 r['tags']['evidence_facets']={k:v for k,v in r['tags']['evidence_facets'].items() if k in ['orthography','expected_scripts','collector_class','xheight_px','ink_density']}
with (D/'benchmark_metadata.jsonl').open('w') as f:
 for r in bench:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
# Remove only our temporary full copies; hashes and compact projections remain.
for name in ['benchmark_v02_test.jsonl','benchmark_v02_dev.jsonl']:(D/name).unlink()
print('source witnesses',len(w),'source inventory',len(inv),'O5 input hits',ex['observed_input_manifest_hits'])
