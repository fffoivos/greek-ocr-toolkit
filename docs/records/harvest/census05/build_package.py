"""Build a read-only Git-blob package; no Git metadata writes or source rewrites."""
import ast, gzip, hashlib, json, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent; R=D.parents[2]; S='3b4090bf9b15d2d2cac53ee55161e936157ec0e5'
P=D/'package/projects'; NAME='greek-ocr-toolkit-pipe032'; ROOT=P/NAME

def git(*a):return subprocess.check_output(['git','-C',str(R),*a])
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')
def blob(p):return git('show',S+':'+p)
def main():
 tree={}
 for ln in git('ls-tree','-r',S).decode().splitlines():
  meta,path=ln.split('\t',1);mode,kind,oid=meta.split();tree[path]=(mode,oid)
 manifest=json.loads(blob('docs/harvest/line_pipeline/tool_versions.json'))
 seeds=['tests/fixtures/fonts/GFSDidot-Regular.ttf','docs/records/harvest/collect_v3_admission/segeval1/gate2/replay.py','docs/harvest/line_pipeline/gate03/clear-before.json','docs/harvest/line_pipeline/gate03/part2_analysis.py','docs/records/harvest/collect_v3_admission/segeval1/cells/evaluation_fixtures.json','docs/cleanup_20261019/LAYOUT_ALIASES_2.tsv','greekocr/harvest/line_pipeline_census.py','greekocr/harvest/numeric_cells.py','scripts/harvest/build_filter_versions.py',
  'tests/conftest.py','tests/_paths.py','tests/test_content_gate.py','tests/test_line_pipeline.py','tests/test_integration_fixes.py',
  'tests/test_seg_gate.py','tests/test_seg_deskew.py','tests/test_seg_curve.py','tests/test_seg_small.py','tests/test_numeric_cells.py',
  'docs/harvest/line_pipeline/tool_versions.json','greekocr/_vendor/codec/v2.json']
 components={}
 for src,dst in [
 ('docs/harvest/seg_census/package/projects/ocr-review-sites-20261018/qa/word-tolerance/context-evidence.json','ocr-review-sites-20261018/qa/word-tolerance/context-evidence.json'),
 ('docs/harvest/seg_census/package/projects/greek-ocr-toolkit-spellcheck/artifacts/sf7_rc1/release_edits_only_A.jsonl','greek-ocr-toolkit-spellcheck/artifacts/sf7_rc1/release_edits_only_A.jsonl'),
 ('docs/records/harvest/collect_v3_admission/segeval1/cells_opus/scripts/common.py','greek-ocr-toolkit-sol-recut/docs/harvest/collect_v3_admission/segeval1/cells_opus/scripts/common.py')]:
  components[src]=dst;seeds.append(src)
 adapter='docs/harvest/seg_census/package/projects/greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_census04.py'
 components[adapter]=NAME+'/greekocr/harvest/line_pipeline_census04.py';seeds.append(adapter)
 for t in manifest['tools'].values():
  for component in t['components']:
   project,relative=component.split('/',1)
   source=relative if project==NAME else 'docs/harvest/seg_census/package/projects/'+component
   components[source]=component; seeds.append(source)
 seeds += [p for p in tree if p.startswith('greekocr/harvest/filtering_assets/')]
 seeds += [p for p in tree if p.startswith('scripts/harvest/filter_runtime/')]
 # Historical scripts dynamically imported by the unchanged four segmentation tests.
 seeds += ['docs/records/harvest/seg_steps/'+step+'/replay.py' for step in ['s1','s2','s3','s4']]
 seeds += ['docs/records/harvest/seg_steps/'+step+'/baseline/greekocr/harvest/filtering_assets/crop-tools.py' for step in ['s1','s2','s3','s4']]
 seeds += ['docs/records/harvest/seg_steps/s4/baseline/'+p for p in ['greekocr/harvest/line_pipeline_native.py','greekocr/harvest/filtering_assets/service.mjs','greekocr/harvest/filtering_assets/segmentation-policy.js']]
 pending=list(seeds); selected={}; imports={}
 def module(name):
  rel=name.replace('.','/')
  for f in (rel+'.py',rel+'/__init__.py'):
   if f in tree:return f
 def enqueue(name):
  f=module(name)
  if f:pending.append(f)
 while pending:
  path=pending.pop()
  if path in selected:continue
  if path not in tree:raise ValueError('missing CODE_SHA file '+path)
  data=blob(path);selected[path]=data
  import_path=path
  if path in components and components[path].startswith(NAME+'/'):
   import_path=components[path].split('/',1)[1]
  elif '/baseline/greekocr/' in path:
   import_path='greekocr/'+path.split('/baseline/greekocr/',1)[1]
  parts=import_path.split('/')[:-1]
  for i in range(1,len(parts)+1):
   init='/'.join(parts[:i])+'/__init__.py'
   if init in tree:pending.append(init)
  if not path.endswith('.py'):continue
  try: nodes=ast.walk(ast.parse(data))
  except SyntaxError:continue
  deps=[]
  package=import_path[:-3].replace('/','.').split('.')[:-1]
  if import_path.endswith('/__init__.py'):package=import_path[:-12].replace('/','.').strip('.').split('.')
  for n in nodes:
   if isinstance(n,ast.Import):
    for a in n.names:enqueue(a.name);deps.append(a.name)
   elif isinstance(n,ast.ImportFrom):
    base='.'.join(package[:len(package)-n.level+1]) if n.level else ''
    name='.'.join(v for v in (base,n.module) if v)
    enqueue(name);deps.append(name)
    for a in n.names:enqueue(name+'.'+a.name)
  imports[path]=deps
 old_proofs=json.loads((D/'package_provenance.json').read_text())['files'] if (D/'package_provenance.json').exists() else []
 expected_targets=set()
 for path in selected:
  expected_targets.add(str((P/components[path] if path in components and (path.startswith('docs/harvest/seg_census/package/') or path.endswith('cells_opus/scripts/common.py')) else ROOT/path).relative_to(R)))
 dropped=[]
 for x in old_proofs:
  if x['package_path'] not in expected_targets and '/package/projects/' in x['package_path']:
   target=R/x['package_path'];assert target.is_relative_to(D);target.unlink();dropped.append(x)
 dump(D/'closure_pruning.json',dict(dropped=dropped,reason='unused historical report artifacts and false relative-import closure from an embedded source path; relocated module imports resolve at the installed package root'))
 proofs=[]
 for path,data in sorted(selected.items()):
  target=P/components[path] if path in components and (path.startswith('docs/harvest/seg_census/package/') or path.endswith('cells_opus/scripts/common.py')) else ROOT/path
  target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  mode,oid=tree[path];assert git('cat-file','blob',oid)==data
  target.chmod(0o755 if mode=='100755' else 0o644)
  proofs.append(dict(source_path=path,package_path=str(target.relative_to(R)),bytes=len(data),sha256=sha(data),git_blob=oid,git_ls_tree=mode+' blob '+oid+'\t'+path))
 (D/'PROJECTS_SHA256').write_text(''.join(x['sha256']+'  '+x['source_path']+'\n' for x in proofs))
 dump(D/'package_provenance.json',dict(code_sha=S,files=proofs,imports=imports))
 old=(R/'docs/harvest/seg_census/DEPLOY_PATHS.txt').read_text().splitlines()
 retained={x['source_path'] for x in proofs};comparison=[]
 for path in old:
  rel=path.split('/package/projects/greek-ocr-toolkit-sol-recut/',1)[-1]
  if rel in retained:why='replaced with exact CODE_SHA blob'
  elif '/.pytest_cache/' in path:why='drop inert test cache'
  elif '/package/projects/' not in path:why='job/config/schema/adapter replaced or audited as additive files'
  else:why='drop: outside runtime, test import and component-fingerprint closure'
  comparison.append(dict(census04_path=path,disposition=why))
 dump(D/'census04_file_comparison.json',dict(previous_files=len(old),files=comparison,new_source_paths=sorted(retained)))
 print('CODE_SHA files',len(proofs))
if __name__=='__main__':main()
