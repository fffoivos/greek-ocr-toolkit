"""Apply the lead's fingerprint ruling without changing named generations."""
from pathlib import Path
import hashlib, importlib.util, json
D=Path(__file__).resolve().parent
P=D/'package/projects/greek-ocr-toolkit-pipe032'
BASE=D.parents[2].parent/'greek-ocr-toolkit-segcensus/docs/harvest/census05'
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 spec=importlib.util.spec_from_file_location('generator',D/'build_filter_versions_main.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.ROOT=P;m.PROJECTS=P.parent
 target=P/'docs/harvest/line_pipeline/tool_versions.json';released=json.loads(target.read_text());base=json.loads((BASE/'package/projects/greek-ocr-toolkit-pipe032/docs/harvest/line_pipeline/tool_versions.json').read_text())
 new=m.build()
 new['tools']['polytonic']=released['tools']['polytonic'];new['owner_decisions']=released['owner_decisions'];new['coordinator_decisions']=released['coordinator_decisions']
 assert new['tools']['cyrillic']==base['tools']['cyrillic']
 assert new['tools']['polytonic']==released['tools']['polytonic']
 changes={k:{'before':v['digest'],'after':new['tools'][k]['digest'],'version':v['version']} for k,v in base['tools'].items() if v['digest']!=new['tools'][k]['digest']}
 assert len(changes)==8
 assert all(new['tools'][k]['version']==v['version'] for k,v in base['tools'].items())
 dump(target,new);dump(D/'fingerprints.json',dict(changed=changes,cyrillic_entry_unchanged=True,polytonic_released_entry_unchanged=True,polytonic_digest=new['tools']['polytonic']['digest'],versions_unchanged=True))
 # Same census05 converter method; only local custody/config sources and comparison target change.
 src=(BASE/'regenerate_n1.py').read_text()
 src=src.replace("oldcfg=json.loads((R/'docs/harvest/seg_census/census04_config.json').read_text());inputaudit=json.loads((D/'input_audit.json').read_text())", "oldcfg=json.loads((D/'census05_config.json').read_text());inputaudit=json.loads((BASE/'input_audit.json').read_text())")
 src=src.replace("custody=json.loads((D/'correction_custody_audit.json').read_text())", "custody=json.loads((BASE/'correction_custody_audit.json').read_text())")
 src=src.replace("original=F/'prepared/87407ec7430a375f'/Path(release['path']).name;assert sha(original)==release['sha256']", "original=(BASE/'corrections'/Path(release['path']).name) if release['tool']=='numerics' else F/'prepared/87407ec7430a375f'/Path(release['path']).name;assert sha(original)==release['sha256']")
 src=src.replace("c=next(x for x in custody['ledgers'] if x['remote_path']==release['path']); entry=dict(c)", "entry=dict(release,old_bytes=original.stat().st_size,old_sha256=sha(original))")
 src=src.replace("entry.update(records_after=generated", "assert not changes, 'STOP: converter output changed beyond tool identity'\n    entry.update(records_after=generated")
 src=src.replace("F=R.parent/", "BASE=R.parent/'greek-ocr-toolkit-segcensus/docs/harvest/census05'\nF=R.parent/")
 (D/'regenerate_n1.py').write_text(src.replace('unbound=4','unbound=5'))
if __name__=='__main__':main()
