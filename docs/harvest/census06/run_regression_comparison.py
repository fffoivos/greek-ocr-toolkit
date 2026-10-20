"""Run identical fixtures in two copied trees; isolate installed `tests` packages."""
import json,os,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
D=Path(__file__).resolve().parent
names=['test_content_gate','test_line_pipeline','test_integration_fixes','test_numeric_cells','test_seg_gate','test_seg_deskew','test_seg_curve','test_seg_small']
bootstrap='''import sys,types,pathlib,pytest
p=types.ModuleType("tests");p.__path__=[str(pathlib.Path.cwd()/"tests")];sys.modules["tests"]=p
raise SystemExit(pytest.main(sys.argv[1:]))
'''
results={}
for tag,root in [('baseline',D/'baseline/package/projects/greek-ocr-toolkit-pipe032'),('033',D/'package/projects/greek-ocr-toolkit-pipe032')]:
    args=[sys.executable,'-B','-c',bootstrap,'-q','-p','no:cacheprovider','--basetemp='+str(D/(tag+'-regression-tmp')),*['tests/'+n+'.py' for n in names],'--junitxml='+str(D/(tag+'-regression.xml'))]
    if "--compare-only" not in sys.argv:
        p=subprocess.run(args,cwd=root,env=dict(os.environ,PYTHONPATH=str(root)),capture_output=True,text=True)
        (D/(tag+'-regression.log')).write_text(p.stdout+p.stderr)
        print(tag,p.returncode,(p.stdout+p.stderr)[-2000:],flush=True)
        assert p.returncode==0
    tree=ET.parse(D/(tag+'-regression.xml'))
    results[tag]={(c.attrib['classname'].split('.tests.')[-1],c.attrib['name']): ('failed' if c.find('failure') is not None else 'error' if c.find('error') is not None else 'skipped' if c.find('skipped') is not None else 'passed') for c in tree.iter('testcase')}
changes=[dict(test=list(k),before=v,after=results['033'].get(k)) for k,v in results['baseline'].items() if results['033'].get(k)!=v]
report=dict(existing_fixture_changes=changes,baseline_tests=len(results['baseline']),amended_tests=len(results['033']),counts={tag:{s:list(r.values()).count(s) for s in set(r.values())} for tag,r in results.items()},test_source_changes=1,version_expectation_only=True,environment_note='In-memory tests namespace prevents collision with installed tests package; existing assertions unchanged except the explicit 0.3.3 version expectation.')
(D/'regression_comparison.json').write_text(json.dumps(report,indent=2)+'\n')
assert not changes and results['033'].keys()==results['baseline'].keys()
