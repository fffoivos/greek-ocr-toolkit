import pathlib,json,hashlib,collections,unicodedata,csv,ast
from fontTools.ttLib import TTFont
D=pathlib.Path(__file__).parent;ROOT=D.parent; repo=ROOT.parents[4];P=pathlib.Path('/Users/foivoskarounos-zamparloukos/Projects/greek-page-ocr')
def dump(n,x): (D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
details=json.loads((D/'remote_details.json').read_text()); build=json.loads((D/'e1_build_info.json').read_text()); audit=json.loads((D/'audit_report.json').read_text());used=next(x['detail']['per_font'] for x in audit['checks'] if x['name']=='font_spread');bind=next(x for x in details if 'keys' in x)
fonts=[]
for x in details:
 if 'font_path' not in x:continue
 p=P/'assets/fonts'/pathlib.Path(x['font_path']).name; row=dict(x);row['stem']=p.stem;row['receipt_sha16']=next((f['sha16'] for f in build['fonts'] if f['stem']==p.stem),None);row['rendered_rows_all_splits']=used.get(p.stem,0);row['held_out']=p.stem in build['held_out_fonts'];row['local_hash_match']=p.exists() and sha(p)==x['sha256'];row['historical_full_sha_match']=bind['inputs'].get('/home/ubuntu/work/greek-page-ocr/assets/fonts/'+p.name)==x['sha256']
 if row['local_hash_match']:
  f=TTFont(p,lazy=True);name=f['name'];cmap=f.getBestCmap();row.update(family=name.getDebugName(1),style=name.getDebugName(2),weight=f['OS/2'].usWeightClass,width_class=f['OS/2'].usWidthClass,cmap_codepoints=sorted(cmap),gsub_features=sorted({r.FeatureTag for r in f['GSUB'].table.FeatureList.FeatureRecord}) if 'GSUB' in f and f['GSUB'].table.FeatureList else [])
 fonts.append(row)
dump('font_inventory.json',fonts)
refs=[]
for split in ['test','dev']:
 for line in (D/f'benchmark_v02_{split}.jsonl').read_text().splitlines():
  r=json.loads(line);refs.append(r)
assert len(refs)==2690
# Reference strings, metadata only: no image open, shaping, rasterization, OCR.
def scripts(s):
 out=set()
 for c in s:
  if not c.isalpha():continue
  n=unicodedata.name(c,'')
  out.add('greek' if 'GREEK' in n else 'cyrillic' if 'CYRILLIC' in n else 'latin' if 'LATIN' in n else 'other')
 return '+'.join(sorted(out)) or 'none'
rows=[]
for r in refs:
 rows.append(dict(source=r['source'],doc=r['doc'],edition_id=r.get('edition_id'),edition_identity=r.get('edition_id') or r['doc'],edition_identity_kind='edition_id' if r.get('edition_id') else 'doc_fallback_not_reviewed_edition',row_id=r['row_id'],split=r['split'],primary_class=r['class'],scripts_from_reference=scripts(r['reference']),tags=r['tags'],facets=r.get('facets',[]),reference=r['reference'],work_identity_status=r.get('work_identity_status'),global_holdout_status=r.get('global_holdout_status')))
# Compact witness preserves all requested dimensions, no image paths or image data.
with (D/'benchmark_metadata.jsonl').open('w') as f:
 for r in rows:f.write(json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n')
groups=collections.defaultdict(list)
for r in rows:groups[(r['source'],r['primary_class'],r['scripts_from_reference'])].append(r)
summary=dict(rows=len(rows),splits=dict(collections.Counter(r['split'] for r in rows)),sources=dict(collections.Counter(r['source'] for r in rows)),classes=dict(collections.Counter(r['primary_class'] for r in rows)),scripts_from_reference=dict(collections.Counter(r['scripts_from_reference'] for r in rows)),docs=len({r['doc'] for r in rows}),explicit_edition_ids=sum(r['edition_id'] is not None for r in rows),joint_groups=len(groups),tags={k:dict(collections.Counter(json.dumps(r['tags'].get(k,'missing'),sort_keys=True) for r in rows)) for k in rows[0]['tags'] if k!='evidence_facets'})
dump('benchmark_summary.json',summary)
# Extract and execute the exact MIX1 code only, avoiding unrelated module imports/pycache.
core=repo/'mix1/core.py'
if not core.exists():core=pathlib.Path('docs/harvest/collect_v3_admission/mix1/core.py')
src=core.read_text(); tree=ast.parse(src);parts=[ast.get_source_segment(src,n) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ['normalize_text','TextExposure']];code='\n\n'.join(parts)+'\n';(D/'mix1_text_exposure.py').write_text(code)
ns={'require':lambda ok,msg:None if ok else (_ for _ in ()).throw(ValueError(msg))};exec(code,ns);index=ns['TextExposure']([r['reference'] for r in rows]);norm=ns['normalize_text']
old=json.loads(pathlib.Path('docs/harvest/collect_v3_admission/mix1/REAL_SAMPLE_RECEIPT.json').read_text())['text_audit'];syn=old['families']['synthetic_v5'];dump('mix1_prior_text_audit.json',dict(source='docs/harvest/collect_v3_admission/mix1/REAL_SAMPLE_RECEIPT.json',source_sha256=sha(pathlib.Path('docs/harvest/collect_v3_admission/mix1/REAL_SAMPLE_RECEIPT.json')),method={k:old[k] for k in ['method','normalization','references','windows','exactness']},synthetic_v5={k:v for k,v in syn.items() if k!='shards'}))
heads=[]
for x in details:
 if 'head_path' in x:
  field='text' if x['head_path'].endswith('corpus.jsonl') else 'gt_nfd';heads.append(dict(path=x['head_path'],bytes=x['bytes'],scope='bounded first 3 rows only',rows=3,hits=[dict(source=r['source_dataset'],kind=index.hit(r[field])) for r in x['rows']]))
excl=(D/'realcrops_v1.txt').read_text().splitlines();hits=collections.Counter(index.hit(x) or 'none' for x in excl)
exposure=dict(status='partial; full corpus text-source manifests not scanned under small-read constraint',method='Unmodified MIX1 normalize_text/TextExposure functions extracted with AST',code_origin=str(core),code_sha256=sha(core),reference_rows=len(rows),reference_exact_unique=len(index.exact),reference_windows=len(index.windows),bounded_manifest_heads=heads,legacy_exclusion=dict(path='factory/exclusions/realcrops_v1.txt',lines=len(excl),vs_seal04_reference_hits=dict(hits),covers_seal04=False,reason='Predates seal04; no bound seal04 edition/key/reference exclusion set. Shared reference matches are incidental, not comprehensive protection.'),per_text_source={s:dict(manifest_exact=None,manifest_substring30=None,manifest_rows=None,status='unknown: no full source-manifest scan',prior_rendered_train=ledger) for s,ledger in syn['per_source'].items()},prior_rendered_train_total_hits=syn['dropped'],prior_rendered_train_hit_sources=[s for s,v in syn['per_source'].items() if v.get('dropped')],prior_rendered_train_scope='MIX1 historical full 190486-label audit, not input-corpus totals',raw_input_bindings={k:v for k,v in bind['inputs'].items() if k.startswith('/home/ubuntu/data/')})
(ROOT/'exposure_hits.json').write_text(json.dumps(exposure,ensure_ascii=False,indent=2)+'\n')
# Actual joint groups crossed with 7 distinct Track-G features, not marginal totals.
features=['capital_marks','bold_caps','condensed_caps','letter_spaced_caps','old_style_numerals','light_on_dark','leader_dots']
active=[f for f in fonts if f['rendered_rows_all_splits']>0 and f.get('cmap_codepoints')]
mat=[]
for (source,cls,script),rs in sorted(groups.items()):
 needed={ord(c) for r in rs for c in unicodedata.normalize('NFC',r['reference']) if not c.isspace()};qualified=[f for f in active if needed<=set(f['cmap_codepoints'])]
 for feature in features:
  status='unknown';reason='Benchmark has no per-face attribution or feature-specific visual qualification.';faces=[]
  if feature=='capital_marks':
   faces=[f['stem'] for f in qualified];status='partial' if faces else 'unknown';reason='Cmap candidates only; v5 has no Track G orthography-specific capital rewrite/paired visibility qualification. Historical Cyrillic acceptance also codec-limited.'
  elif feature=='bold_caps':
   faces=[f['stem'] for f in qualified if f.get('weight',0)>=700];status='partial' if faces else 'unknown';reason='Bold sampled globally; no caps-conditional source/style sampling or visual qualification.'
  elif feature=='condensed_caps':
   faces=[f['stem'] for f in qualified if f.get('width_class',5)<5];status='partial' if faces else 'no';reason='No eligible sampled condensed face in the metadata inventory.' if not faces else 'Condensed metadata candidate; caps/source qualification absent.'
  elif feature=='letter_spaced_caps':
   faces=[f['stem'] for f in qualified];status='partial' if faces else 'unknown';reason='v5 letterspacing_fraction=.03, not caps/source conditioned; benchmark letter_spaced unavailable.'
  elif feature=='old_style_numerals':
   faces=[f['stem'] for f in qualified if 'onum' in f.get('gsub_features',[])];status='partial' if faces else 'unknown';reason='onum candidates only: renderer supplies no explicit OpenType onum feature; grouped-number/old-style face routing absent; default numeral shapes not established.'
  elif feature=='light_on_dark':
   faces=[f['stem'] for f in qualified];status='partial' if faces else 'unknown';reason='v5 .02 input; audit .019915470670125293 all splits; target .05 absent; benchmark polarity unrecorded.'
  elif feature=='leader_dots':
   faces=[f['stem'] for f in qualified if ord('.') in f['cmap_codepoints']];status='no';reason='Dot glyph presence does not supply explicit leader-run GT/crop ownership; Track G contract absent.'
  mat.append(dict(source=source,primary_class=cls,script=script,benchmark_rows=len(rs),feature=feature,status=status,font_candidates=';'.join(faces),font_qualification='cmap/metadata only; no visual qualification',reason=reason,evidence='evidence/benchmark_metadata.jsonl; evidence/font_inventory.json; evidence/recipe.v5.json; evidence/audit_report.json; evidence/source_witnesses.json'))
with (ROOT/'coverage_matrix.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(mat[0]));w.writeheader();w.writerows(mat)
dump('coverage_summary.json',dict(groups=len(groups),features=features,cells=len(mat),status_counts=dict(collections.Counter(r['status'] for r in mat)),font_files=len(fonts),active_fonts=len(active),held_out=[f['stem'] for f in fonts if f['held_out']],never_sampled=[f['stem'] for f in fonts if f['rendered_rows_all_splits']==0],recipes=2,text_sources=len(syn['per_source']),raw_file_bindings=len(exposure['raw_input_bindings'])))
print(json.dumps(summary,ensure_ascii=False)[:4000]);print((D/'coverage_summary.json').read_text())
