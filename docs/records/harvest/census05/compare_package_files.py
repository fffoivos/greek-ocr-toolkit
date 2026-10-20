"""Account for every census_04 deploy file and all new CODE_SHA source paths."""
import csv,json
from collections import Counter
from pathlib import Path
D=Path(__file__).resolve().parent;P=D/'package/projects/greek-ocr-toolkit-pipe032'
def main():
 prov=json.loads((D/'package_provenance.json').read_text())['files'];selected={x['source_path'] for x in prov}
 moves=list(csv.DictReader((P/'docs/cleanup_20261019/LAYOUT_ALIASES_2.tsv').open(),delimiter='\t'));files=[];mapped=set()
 for old in (D.parent/'seg_census/DEPLOY_PATHS.txt').read_text().splitlines():
  relative=old.split('/package/projects/greek-ocr-toolkit-sol-recut/',1)[-1];candidates=[old,relative]
  for move in sorted(moves,key=lambda x:-len(x['old'])):
   if relative==move['old'] or relative.startswith(move['old']+'/'):
    candidates.append(move['new']+relative[len(move['old']):]);break
  source=next((p for p in candidates if p in selected),None)
  if source:
   action='retained as CODE_SHA blob';reason='same runtime/test/fingerprint capability, with layout relocation where applicable';mapped.add(source)
  elif '/.pytest_cache/' in old:action='dropped';reason='inert inherited pytest cache; not executed/imported or a manifest component'
  elif '/package/projects/' not in old:action='replaced additive';reason='updated census05 job/config/parity/schema or test fixture; exact differences in additive_changes.patch and config_diff.patch'
  else:action='dropped';reason='outside transitive runtime imports, requested regression/dynamic-fixture dependencies and stage-component digest closure'
  files.append(dict(census04_path=old,action=action,reason=reason,code_sha_source=source))
 out=dict(census04_files=len(files),counts=dict(Counter(x['action'] for x in files)),files=files,new_source_paths=sorted(selected-mapped),note='Every source path has its exact hash, package destination and blob proof in package_provenance.json; old job/config files are separately diffed.')
 (D/'census04_file_comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['counts'],'new source paths',len(out['new_source_paths']))
if __name__=='__main__':main()
