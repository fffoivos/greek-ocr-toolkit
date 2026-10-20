from pathlib import Path
import importlib.util,json
R=Path.cwd();p=R/'scripts/harvest/build_filter_versions.py'
s=p.read_text().replace('"segmentation":("0.8",','"segmentation":("0.9-s1",').replace('"owner\'s three rules; remove target-cut veto and taller-than-upright guard"],','"owner\'s three rules; remove target-cut veto and taller-than-upright guard","every letter body >=95% visible for a whole neighbour word"],').replace('"0.8 exactly the owner\'s three rules:', '"0.9-s1 exactly the owner\'s three rules; whole word = every existing letter body >=95% visible:')
p.write_text(s)
spec=importlib.util.spec_from_file_location('build',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
# Read only the segmentation definition without resolving absent unrelated runtime inputs.
old=json.loads((R/'docs/harvest/seg_steps/s1/baseline/docs/harvest/line_pipeline/tool_versions.json').read_text())['tools']['segmentation']
new=dict(old,version='0.9-s1',documented_iterations=old['documented_iterations']+['every letter body >=95% visible for a whole neighbour word'],iteration_count=9,
    scope="0.9-s1 exactly the owner's three rules; whole word = every existing letter body >=95% visible; grouping, body definition, completeness, length and padding unchanged")
import hashlib
new['components']={k:hashlib.sha256((R/Path(k).relative_to('greek-ocr-toolkit-sol-recut')).read_bytes()).hexdigest() for k in old['components']}
new['digest']=hashlib.sha256(json.dumps(new['components'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
p=R/'docs/harvest/line_pipeline/tool_versions.json';v=json.loads(p.read_text());v['tools']['segmentation']=new;p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
