"""Readback of 1,038 decisions, stage ordering, frozen arithmetic and source scope."""
import ast
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

D = Path(__file__).resolve().parent
ROOT = D.parents[4]
sys.path.insert(0,str(ROOT))
from greekocr.harvest.line_pipeline_native import JsonService, ASSETS


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def functions(path):
    tree = ast.parse(path.read_text())
    def visit(body,prefix=''):
        result = {}
        for node in body:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                result[prefix+node.name] = ast.dump(node,include_attributes=False)
            if isinstance(node,ast.ClassDef):
                result.update(visit(node.body,prefix+node.name+'.'))
        return result
    return visit(tree.body)


def js_function(text,name):
    # Existing named functions are not nested; stop immediately before the
    # following top-level function, retaining every byte within the function.
    return re.search(r'function '+name+r'\([^\n]*\)\{\n.*?\n\}',text,re.S)[0]


def source_scope():
    initial = json.loads((D/'initial_state.json').read_text())
    for name,expected in initial['protected'].items(): assert sha(ROOT/name)==expected,name
    for name,expected in initial['predictor'].items(): assert sha(ROOT/name)==expected,name
    assert subprocess.check_output(['git','diff','--stat'],cwd=ROOT,text=True)==initial['initial_diff_stat']
    native = 'greekocr/harvest/line_pipeline_native.py'
    crop = 'greekocr/harvest/filtering_assets/crop-tools.py'
    changed = {}
    for name in (native,crop):
        a,b = functions(D/'baseline'/name),functions(ROOT/name)
        changed[name] = sorted(k for k in a.keys()|b.keys() if a.get(k)!=b.get(k))
    assert changed[native] == ['NativeSegmenter.__call__']
    assert changed[crop] == ['line_inventory']
    policy = 'greekocr/harvest/filtering_assets/segmentation-policy.js'
    old,new = (D/'baseline'/policy).read_text(),(ROOT/policy).read_text()
    frozen_functions = {}
    for function in ['boxLengthJudgement','paddingJudgement']:
        a,b = js_function(old,function),js_function(new,function)
        assert a==b,function
        frozen_functions[function] = hashlib.sha256(a.encode()).hexdigest()
    builder = ROOT/'scripts/harvest/build_filter_versions.py'
    spec = importlib.util.spec_from_file_location('gate_versions',builder);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    versions = json.loads((ROOT/'docs/harvest/line_pipeline/tool_versions.json').read_text())
    assert module.build()==versions
    old_versions = json.loads((D/'baseline/docs/harvest/line_pipeline/tool_versions.json').read_text())
    changed_versions = [k for k in versions['tools'] if versions['tools'][k]!=old_versions['tools'][k]]
    assert sorted(changed_versions)==['census','segmentation']
    sources = [native,crop,policy,'scripts/harvest/build_filter_versions.py','docs/harvest/line_pipeline/tool_versions.json']
    patch = ''
    for name in sources:
        patch += ''.join(difflib.unified_diff((D/'baseline'/name).read_text().splitlines(True),(ROOT/name).read_text().splitlines(True),fromfile='a/'+name,tofile='b/'+name))
    (D/'source_changes.patch').write_text(patch)
    receipt = dict(status='PASS',base=initial['base'],protected_files_unchanged=initial['protected'],
        predictor_unchanged=initial['predictor'],changed_functions=changed,
        frozen_js_functions=frozen_functions,policy_sha256=sha(ROOT/policy),policy_changed=sha(ROOT/policy)!=initial['sources'][policy],
        versions_rebuild_exact=True,changed_tool_fingerprints=changed_versions,
        segmentation_digest=versions['tools']['segmentation']['digest'],
        census_change='native segmentation source fingerprint only; version/behavior unchanged',
        design_sha256=sha(D/'DESIGN.md'),design_written_before_sources=all((D/'DESIGN.md').stat().st_mtime < (ROOT/n).stat().st_mtime for n in sources),
        sources={n:sha(ROOT/n) for n in sources})
    assert receipt['design_written_before_sources']
    (D/'scope_guard.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def replay_readback():
    policy_sha = sha(ASSETS/'segmentation-policy.js')
    service = JsonService(['node',str(ASSETS/'service.mjs')])
    predictor = JsonService([str(ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'),str(ASSETS/'font-models.json')])
    counts = dict(rows=0,gate_decisions_exact=0,final_decisions_exact=0,stage_b_exact=0,predictions_exact=0,gate_blocks_stage_b=0,context_invariant=0)
    try:
        for cohort,n in [('segeval1',150),('calibration',888)]:
            rows = [json.loads(l) for l in (D/f'replay_{cohort}.jsonl').read_text().splitlines()]
            assert len(rows)==n and len({r['line_id'] for r in rows})==n
            for r in rows:
                a,b = r['after'],r['before'];e=a['evidence'];g=e['gate'];cut=g['main_cut']
                assert a['policy_sha256']==policy_sha and a['tool_version']=='0.7'
                assert cut['baseline_exit'] == any(c['line']=='baseline' and 'leaves the crop' in c['meaning'] for c in cut['crossings'])
                assert cut['low_visibility_span'] == any(s['min_visible']<.6 for s in cut['cut_spans'])
                assert cut['row_frame_taller'] == (cut['row_frame_height']>cut['upright_box_height'] if cut['row_frame_height'] is not None else False)
                assert cut['cut'] == (cut['baseline_exit'] or cut['low_visibility_span'] or cut['row_frame_taller'])
                assert g == service.call(dict(operation='decide',policy_sha256=policy_sha,evidence=dict(e,gate_only=True)))
                counts['gate_decisions_exact']+=1
                assert service.call(dict(operation='decide',policy_sha256=policy_sha,evidence=e)) == dict(verdict=a['verdict'],reason=a['reason'])
                counts['final_decisions_exact']+=1
                without = dict(e,neighbour_evidence=None)
                assert service.call(dict(operation='decide',policy_sha256=policy_sha,evidence=without)) == dict(verdict=a['verdict'],reason=a['reason'])
                counts['context_invariant']+=1
                for line in e['lines']:
                    assert line['whole_words']==sum(w['whole'] for w in line['word_groups'])
                    assert line['cutoff_words']==sum(not w['whole'] for w in line['word_groups'])
                    assert line['complete']==(line['votes']>=6 and line['bodies']>=6 and line['visible']>=.9 and line['coverage']>=.6)
                    for word in line['word_groups']:
                        assert word['whole']==(word['bodies']>=2 and not word['touches_horizontal_edge'])
                if g['verdict']=='PASS':
                    assert e['box_evidence']==b['evidence']['box_evidence']
                    assert e['padding_evidence']==b['evidence']['padding_evidence']
                    counts['stage_b_exact']+=1
                    box=e['box_evidence'];rf=box['row_frame'];script=box['prediction']['group']
                    p=predictor.call(dict(long_side=max(rf['length'],rf['height']),short_side=min(rf['length'],rf['height']),script=script))
                    assert p==box['prediction']
                    counts['predictions_exact']+=1
                else:
                    assert not e['box_evidence']['available'] and not e['padding_evidence']['available']
                    counts['gate_blocks_stage_b']+=1
                counts['rows']+=1
    finally:
        service.close();predictor.close()
    return counts


if __name__=='__main__':
    scope = source_scope()
    result = dict(status='PASS',**replay_readback())
    (D/'replay_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
