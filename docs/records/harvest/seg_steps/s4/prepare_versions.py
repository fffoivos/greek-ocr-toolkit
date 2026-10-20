"""Rebuild segmentation and affected census dependency fingerprints locally."""
from pathlib import Path
import ast,json,hashlib
R=Path(__file__).resolve().parents[4]
p=R/'scripts/harvest/build_filter_versions.py'
tree=ast.parse(p.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='build')
env=dict(ROOT=R,PROJECTS=R.parent)
exec(compile(ast.Module(body=[fn.body[0]],type_ignores=[]),str(p),'exec'),env)
vp=R/'docs/harvest/line_pipeline/tool_versions.json';v=json.loads(vp.read_text())
version,history,paths,scope=env['definitions']['segmentation']
components={'greek-ocr-toolkit-sol-recut/'+str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
v['tools']['segmentation']=dict(version=version,documented_iterations=history,iteration_count=len(history),scope=scope,components=components,digest=hashlib.sha256(json.dumps(components,sort_keys=True,separators=(',',':')).encode()).hexdigest())
c=v['tools']['census'];key='greek-ocr-toolkit-sol-recut/greekocr/harvest/line_pipeline_native.py'
assert key in c['components'];c['components'][key]=hashlib.sha256((R/'greekocr/harvest/line_pipeline_native.py').read_bytes()).hexdigest();c['digest']=hashlib.sha256(json.dumps(c['components'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
vp.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
