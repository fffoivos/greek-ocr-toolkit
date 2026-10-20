"""Local full-loader measurement using registered rows already qualified by regeneration."""
from pathlib import Path
import json,sys,time
D=Path(__file__).resolve().parent;P=D/'package/projects/greek-ocr-toolkit-pipe032';sys.path.insert(0,str(P))
from greekocr.harvest.line_pipeline_census import Ledger,ArtifactCorrector
r=json.loads((D/'corrections/report.json').read_text());release=next(x for x in r['releases'] if x['tool']=='numerics' and x['parent_id']=='collection-v2-train')
pid=release['parent_id'];parent=next(p for p in json.loads((D/'census05_config.json').read_text())['parents'] if p['id']==pid)
ledger=Ledger(D/'corrections/work'/(pid+'.sqlite'),dict(parent=parent,code_sha='3b4090bf9b15d2d2cac53ee55161e936157ec0e5'))
ledger.db.execute("DELETE FROM corrections WHERE tool='numerics'");ledger.db.execute('DELETE FROM releases');ledger.db.commit()
release=dict(release,path=release['local_path']);versions=json.loads((P/'docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']
s=time.monotonic();ArtifactCorrector(ledger,versions,{pid:parent['sha256']}).load(release);elapsed=time.monotonic()-s;ledger.db.close()
(D/'load_timing.json').write_text(json.dumps(dict(location='local macOS; not Clariden throughput qualification',records=parent['rows'],bytes=Path(release['path']).stat().st_size,seconds=elapsed,records_per_second=parent['rows']/elapsed),indent=2)+'\n')
