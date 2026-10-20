"""Finalize FP3 fingerprint: conservative numeric adjacency and held-out inputs.

Extends the existing held-out crop set with declared external hashes; its DROP
rule and all segmentation/correction/final-eligibility thresholds are unchanged.
"""
import collections as C,difflib,gzip,hashlib,json,pathlib as P,re,shutil,sqlite3
R=P.Path('/iopsstor/scratch/cscs/fffoivos/greek-ocr-e3/filter_pipeline_20261018');A=R/'attempts/census_03'
paths=json.loads((A/'paths.json').read_text());B=P.Path(paths['prepared']);CODE=P.Path(paths['projects']);S=A/'sources'
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def sha(p):
    with P.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def digest(x):return hashlib.sha256(x.encode()).hexdigest()
def dump(p,x):P.Path(p).write_text(canonical(x)+'\n')
cfg=json.loads((B/'census_w64_pf64.json').read_text())
assert (A/'coverage.json').is_file(),'preparation must finish first'
core=CODE/'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline.py'
s=core.read_text();old='not re.search(r"\\d[.\\-·]\\d", text)';new='not re.search(r"\\d\\s*[.\\-·]\\s*\\d", text)'
assert s.count(old)==1;core.write_text(s.replace(old,new))
for name in ['test_numeric_adjacency.py','test_external_crop_input.py']:
    shutil.copyfile(A/name,CODE/'greek-ocr-toolkit-sol-recut/tests'/('test_fp3_'+name.removeprefix('test_')))

# Mechanical identity/crop extraction from the existing historical instruments;
# no new references, labels, pixels, work identities or splits are created.
cohorts={};crops=set();editions=set();lineids=set();records=[]
bench=R.parent/'benchmark_20261019/attempts/build_01'
for cohort,name in [('wikisource_human','historical_proofread.jsonl'),('e1_real_test','historical_digital.jsonl')]:
    p=bench/name;count=0;docs=set()
    with p.open() as f:
        for line in f:
            r=json.loads(line);count+=1;crops.add(r['crop_sha256']);docs.add(r['doc'].removesuffix(':human'))
            i=r['id'].removesuffix('-human');lineids.add(i)
            records.append(dict(cohort=cohort,id=r['id'],source_id=i,edition_id=r['doc'].removesuffix(':human'),crop_sha256=r['crop_sha256'],source_record_sha256=digest(canonical(r))))
    editions|=docs
    cohorts[cohort]=dict(path=str(p),sha256=sha(p),rows=count,edition_ids=sorted(docs),reference_protocol='unchanged historical exact factory image_png')
lqb=json.loads((S/'lqb_truth_ids.json').read_text());lineids|=set(lqb['line_ids'])
cohorts['LQB_truth']=dict(path=str(S/'lqb_truth_ids.json'),sha256=sha(S/'lqb_truth_ids.json'),rows=len(lqb['line_ids']),sources=lqb['source_sha256'])
db=sqlite3.connect('file:'+str(R/'attempts/census_02/census/ledger.sqlite')+'?mode=ro&immutable=1',uri=True)
matches=[]
for parent in cfg['parents']:
    wanted=sorted(lineids)
    for start in range(0,len(wanted),400):
        batch=wanted[start:start+400]
        query='select parent,id,payload from observations where parent=? and id in ('+','.join('?' for _ in batch)+')'
        for p,i,raw in db.execute(query,[parent['id'],*batch]):
            r=json.loads(raw);crops.add(r['crop_sha256']);matches.append(dict(parent_id=p,id=i,book_id=r['book_id'],crop_sha256=r['crop_sha256'],LQB=i in set(lqb['line_ids'])))
db.close()
cohorts['bound_population_matches']=dict(rows=len(matches),LQB_rows=sum(x['LQB'] for x in matches),matched=matches)
cohorts['heldout_crop_sha256']=sorted(crops);cohorts['heldout_editions']=sorted(editions)
dump(A/'protected_cohorts.json',cohorts)
with (A/'external_reference_identities.jsonl').open('w') as f:
    for r in records:f.write(canonical(r)+'\n')
meta=json.loads((B/'metadata.json').read_text());meta['protected_cohorts']=dict(path=str(A/'protected_cohorts.json'),sha256=sha(A/'protected_cohorts.json'),cohorts=['v2-dev','v2-test','wikisource_human','e1_real_test','LQB_truth'])
# Retain the source policy's explicit mixed-class branch (admission.py:445-446)
# when declarations replace the fallback; never infer it from observed letters.
for group in ['books','pages']:
    for entry in meta[group].values():
        if set(entry.get('classes',[])) & {'greek_latin_cs','mixed_greek_latin'} and 'greek' in entry['scripts']:
            entry['scripts']=sorted(set(entry['scripts'])|{'latin'})
            entry['languages']=sorted(set(entry['languages'])|{'latin'})
            entry['latin_policy']='allowed'
            entry['mixed_class_provenance']='frozen admission.py:445-446 explicit MIXED_CLASSES branch; declared class metadata, no label-text inference'
dump(B/'metadata.json',meta)
cfg['final_policy']=dict(cfg.get('final_policy',{}),heldout_editions=sorted(editions),heldout_crop_sha256=sorted(crops))

# Existing exact-crop exclusion logic, now supplied with the external input set.
census=CODE/'greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census.py'
s=census.read_text();anchor='        groups={}\n        for parent,i,payload,decision in self.db.execute('
assert s.count(anchor)==1
insert='        binding=json.loads(self.db.execute("SELECT value FROM run WHERE key=\'binding\'").fetchone()[0])\n        held_crops.update(binding.get("config",{}).get("final_policy",{}).get("heldout_crop_sha256",[]))\n'
census.write_text(s.replace(anchor,insert+anchor))
vpath=P.Path(cfg['versions']);versions=json.loads(vpath.read_text())
for t in versions['tools'].values():
    for name in t['components']:t['components'][name]=sha(CODE/name)
    t['digest']=digest(json.dumps(t['components'],sort_keys=True,separators=(',',':')))
versions['build_patch'].update(id='FP3-numeric-adjacency-and-heldout-inputs-v1',source_sha256=sha(core),heldout_input_wiring_sha256=sha(census))
dump(vpath,versions)
for release in cfg['corrections']:
    path=P.Path(release['path']);tmp=path.with_suffix('.rebind.tmp')
    with path.open() as f,tmp.open('w') as o:
        for line in f:
            r=json.loads(line);r['tool_digest']=versions['tools'][r['tool']]['digest'];o.write(canonical(r)+'\n')
    tmp.replace(path);release['sha256']=sha(path)
oldroot=R/'code/d74ad2830c479f7b/projects'
diff=[]
for p in [core,census]:
    q=oldroot/p.relative_to(CODE)
    diff.extend(difflib.unified_diff(q.read_text().splitlines(True),p.read_text().splitlines(True),fromfile='census_02/'+str(p.relative_to(CODE)),tofile='census_03/'+str(p.relative_to(CODE))))
(A/'integration_fixes.diff').write_text(''.join(diff))
dump(A/'numeric_patch.json',dict(old_sha256=sha(oldroot/core.relative_to(CODE)),new_sha256=sha(core),
    before='not any(c in text for c in ".-·")',after=new,spaces_preserve_numeric_uncertainty=True))
fingerprint_recipe=dict(base_recipe_sha256=sha(A/'build_recipe.json'),core=sha(core),census=sha(census),versions=sha(vpath),
    metadata=sha(B/'metadata.json'),corrections=[{k:v for k,v in r.items() if k!='path'} for r in cfg['corrections']],
    protected_cohorts=sha(A/'protected_cohorts.json'),numeric_test=sha(A/'test_numeric_adjacency.py'),crop_test=sha(A/'test_external_crop_input.py'))
build=digest(canonical(fingerprint_recipe))[:16];NEW=R/'prepared'/build
assert not NEW.exists()
B.rename(NEW)
newcode=NEW/'code'/build/'projects'
(NEW/'code'/paths['build']).rename(NEW/'code'/build)
def mapped(path):return str(path).replace(str(CODE),str(newcode)).replace(str(B),str(NEW))
for key in ['versions','metadata','codec']:cfg[key]=mapped(cfg[key])
cfg['component_roots']={k:mapped(v) for k,v in cfg['component_roots'].items()}
for release in cfg['corrections']:release['path']=mapped(release['path'])
dump(NEW/'census_w64_pf64.json',cfg)
dump(A/'paths.json',dict(build=build,prepared=str(NEW),projects=str(newcode)))
dump(A/'final_build_recipe.json',fingerprint_recipe)
metasha=sha(NEW/'metadata.json')
tmp=A/'row_metadata.rebind.jsonl.gz'
with gzip.open(A/'row_metadata.jsonl.gz','rt') as f,gzip.open(tmp,'wt',compresslevel=1) as o:
    for line in f:
        r=json.loads(line);r['field_provenance']['metadata_sha256']=metasha
        expected=meta['pages'].get(r['field_provenance']['page_key'],meta['books'][r['field_provenance']['book_key']])
        r['expectations']={k:v for k,v in expected.items() if k in {'languages','scripts','orthography','latin_policy','allowed_characters'}}
        o.write(canonical(r)+'\n')
tmp.replace(A/'row_metadata.jsonl.gz')
files=sorted(p for p in newcode.rglob('*') if p.is_file() and p.name!='SHA256SUMS' and '__pycache__' not in p.parts)
(newcode/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(newcode))+'\n' for p in files))
dump(A/'code_receipt.json',dict(projects=str(newcode),manifest_sha256=sha(newcode/'SHA256SUMS'),files=len(files),core_sha256=sha(newcode/core.relative_to(CODE)),versions_sha256=sha(cfg['versions'])))
dump(A/'config_receipt.json',dict(build=build,config=dict(path=str(NEW/'census_w64_pf64.json'),sha256=sha(NEW/'census_w64_pf64.json')),
    metadata=dict(path=cfg['metadata'],sha256=sha(cfg['metadata'])),versions=dict(path=cfg['versions'],sha256=sha(cfg['versions'])),
    codec=dict(path=cfg['codec'],sha256=sha(cfg['codec'])),predictor=dict(path=cfg['predictor'],sha256=sha(cfg['predictor'])),runtime=dict(path=cfg['runtime_manifest'],sha256=sha(cfg['runtime_manifest'])),
    parents={p['id']:dict(path=p['path'],sha256=p['sha256'],rows=p['rows']) for p in cfg['parents']}))
print(canonical(dict(status='FINALIZED',build=build,config=str(NEW/'census_w64_pf64.json'),config_sha256=sha(NEW/'census_w64_pf64.json'),protected_crops=len(crops),population_matches=len(matches))),flush=True)
