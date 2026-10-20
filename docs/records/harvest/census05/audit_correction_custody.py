"""Recheck immutable census_03 ledger custody and active method identities only.

Not regeneration and not a substitute for ArtifactCorrector.load of every row.
"""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent;R=D.parents[2]
FP3=R.parent/'greek-page-ocr-wave2/out/fp3/prepared/87407ec7430a375f'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
 old=json.loads((D/'runtime_contract_audit.json').read_text())
 versions=json.loads((D/'package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
 rows=[]
 for x in old['ledgers']:
  release=x['release'];path=FP3/Path(release['path']).name
  assert sha(path)==release['sha256']
  methods=x['methods'];tool=release['tool'];matches=all(m['version']==versions[tool]['version'] and m['digest']==versions[tool]['digest'] for m in methods)
  action='not bound in census_05 (planned)' if tool=='polytonic' else 'standing (pending full load validation)' if matches else 'regeneration required (not run)'
  rows.append(dict(tool=tool,parent_id=release['parent_id'],status=release['status'],local_path=str(path),remote_path=release['path'],bytes=path.stat().st_size,
   sha256=sha(path),records=x['records'],edits=x['edited_rows'],holds=x['hold_rows'],no_change=x['no_change_rows'],
   count_provenance='attempt-2 complete scan, transferred by fresh exact file SHA256 equality',methods=methods,active_method=dict(version=versions[tool]['version'],digest=versions[tool]['digest']),
   identity_matches=matches,planned_disposition=action,ArtifactCorrector_load='NOT RUN',regenerated=False))
 result=dict(status='CUSTODY_PASS_NOT_LOAD_QUALIFIED',ledgers=rows,unbound_planned=sum(x['tool']=='polytonic' for x in rows),regeneration_required=sum(not x['identity_matches'] and x['tool']!='polytonic' for x in rows),
  new_ledgers=0,record_diffs=None,superseded_source_references=old['superseded_standing_sources'])
 (D/'correction_custody_audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='ledgers'},indent=2))
if __name__=='__main__':main()
