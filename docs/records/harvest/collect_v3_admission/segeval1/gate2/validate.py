"""Offline independent readback, diagnostic invariance and strict 0.7 source scope."""
import ast
from collections import Counter
import copy
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

D=Path(__file__).resolve().parent
ROOT=D.parents[4]
sys.path.insert(0,str(ROOT))
from greekocr.harvest.line_pipeline_native import JsonService, ASSETS


def offline(event,args):
    if event in ('socket.connect','socket.connect_ex','socket.getaddrinfo'):
        raise RuntimeError('network OFF: SEG-GATE-2')


sys.addaudithook(offline)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return [json.loads(s) for s in path.read_text().splitlines()]
def read(path):return json.loads(path.read_text())


def functions(path):
    def visit(body,prefix=''):
        result={}
        for node in body:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
                result[prefix+node.name]=ast.dump(node,include_attributes=False)
            if isinstance(node,ast.ClassDef):result.update(visit(node.body,prefix+node.name+'.'))
        return result
    return visit(ast.parse(path.read_text()).body)


def js_function(text,name):
    return re.search(r'function '+name+r'\([^\n]*\)\{\n.*?\n\}',text,re.S)[0]


def source_scope():
    initial=read(D/'initial_state.json')
    for group in ('protected','predictor','immutable_sources'):
        for name,expected in initial[group].items():assert sha(ROOT/name)==expected,name
    assert subprocess.check_output(['git','diff','--stat'],cwd=ROOT,text=True)==initial['initial_diff_stat']
    assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==initial['head']
    changed={}
    for name in ['greekocr/harvest/line_pipeline_native.py','greekocr/harvest/filtering_assets/crop-tools.py']:
        a,b=functions(D/'baseline'/name),functions(ROOT/name)
        changed[name]=sorted(k for k in a.keys()|b.keys() if a.get(k)!=b.get(k))
    assert changed['greekocr/harvest/line_pipeline_native.py']==[]
    assert changed['greekocr/harvest/filtering_assets/crop-tools.py']==['line_inventory']
    crop=(ROOT/'greekocr/harvest/filtering_assets/crop-tools.py').read_text()
    assert 'row_frame_taller' not in crop
    policy='greekocr/harvest/filtering_assets/segmentation-policy.js'
    old,new=(D/'baseline'/policy).read_text(),(ROOT/policy).read_text()
    assert 'gate: target line cut' not in new
    assert js_function(old,'lineInventoryJudgement').replace(" if(main_cut.cut)return {...result,verdict:'DROP',reason:'gate: target line cut'};\n",'')==js_function(new,'lineInventoryJudgement')
    assert js_function(old,'combinedBoxJudgement')==js_function(new,'combinedBoxJudgement')
    frozen={}
    frozen05=(D.parent/'gate/baseline'/policy).read_text()
    for name in ('boxLengthJudgement','paddingJudgement'):
        a=js_function(old,name)
        assert a==js_function(new,name)==js_function(frozen05,name)
        frozen[name]=hashlib.sha256(a.encode()).hexdigest()
    builder=ROOT/'scripts/harvest/build_filter_versions.py'
    spec=importlib.util.spec_from_file_location('gate2_versions',builder);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    versions=read(ROOT/'docs/harvest/line_pipeline/tool_versions.json')
    assert module.build()==versions
    old_versions=read(D/'baseline/docs/harvest/line_pipeline/tool_versions.json')
    changed_tools=[k for k in versions['tools'] if versions['tools'][k]!=old_versions['tools'][k]]
    assert changed_tools==['segmentation'] and versions['tools']['segmentation']['version']=='0.8'
    changed_components=[k for k,v in versions['tools']['segmentation']['components'].items() if v!=old_versions['tools']['segmentation']['components'][k]]
    assert sorted(Path(k).name for k in changed_components)==['crop-tools.py','segmentation-policy.js']
    sources=initial['production']
    changed_sources=[n for n in sources if sha(ROOT/n)!=initial['sources'][n]]
    assert set(changed_sources)==set(sources)-{'greekocr/harvest/line_pipeline_native.py'}
    patch=''.join(''.join(difflib.unified_diff((D/'baseline'/n).read_text().splitlines(True),(ROOT/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n)) for n in sources)
    (D/'source_changes.patch').write_text(patch)
    receipt=dict(status='PASS',base=initial['base'],protected_files_unchanged=initial['protected'],predictor_unchanged=initial['predictor'],immutable_source_files_verified=len(initial['immutable_sources']),changed_functions=changed,frozen_js_functions=frozen,policy_sha256=sha(ROOT/policy),policy_version='0.8',policy_rules=['Other lines: additional complete line DROP; >2 whole words from other rows DROP; cut-off words do not count.','Length: unchanged 0.6 de-skewed main-row box and predictor; boxLengthJudgement 0.5–1.5.','Padding: unchanged paddingJudgement; (segment_height-upright_box_height)/row_frame_height <= 1.5.'],no_rule_beyond_the_three=True,removed=['row-frame-taller-than-upright guard','target-line-cut veto'],cut_evidence='skew_line diagnostics only; no verdict dependence',versions_rebuild_exact=True,changed_tool_fingerprints=changed_tools,changed_component_fingerprints=changed_components,segmentation_digest=versions['tools']['segmentation']['digest'],native_stage_unchanged=True,census_unchanged=True,sources={n:sha(ROOT/n) for n in sources})
    (D/'scope_guard.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
    return receipt


def replay_readback():
    policy_sha=sha(ASSETS/'segmentation-policy.js')
    service=JsonService(['node',str(ASSETS/'service.mjs')])
    predictor=JsonService([str(ROOT/'scripts/harvest/filter_runtime/target/debug/greekocr-frozen-font-predict'),str(ASSETS/'font-models.json')])
    counts=Counter();witnesses={}
    try:
        for cohort,n in [('segeval1',150),('calibration',888)]:
            rows=load(D/f'replay_{cohort}.jsonl');assert len(rows)==n and len({r['line_id'] for r in rows})==n
            old06={r['line_id']:r for r in load(D.parent/f'deskew/replay_{cohort}.jsonl')}
            old07={r['line_id']:r for r in load(D.parent/f'gate/replay_{cohort}.jsonl')}
            summary=read(D/f'summary_{cohort}.json');prior_summary=read(D.parent/f'gate/summary_{cohort}.json')
            for p,h in summary['source_sha256'].items():assert sha(Path(p))==h,p
            assert summary['failures']==[]
            if cohort=='segeval1':
                owners={r['line_id']:r for r in load(D.parent/'scored/owner_rows.jsonl')}
                sealed={r['row_id']:r for r in load(D.parent/'keys/sealed_decisions.jsonl')}
                assert summary['owner_standard_states']==dict(fine=118,faulty=30,unresolved=2)
                for version in ('05','06','07'):assert summary['confusion'][version]==prior_summary['confusion'][version]
                for version in ('05','06','07','08'):
                    table={v:{s:sum(r['verdict_'+version]==v and r['owner_standard_state']==s for r in rows) for s in ('fine','faulty','unresolved')} for v in ('DROP','KEEP','UNCERTAIN')}
                    assert summary['confusion'][version]==table
                    assert summary['errors'][version]==dict(FP=table['DROP']['fine'],FN=table['KEEP']['faulty'],UNC=sum(table['UNCERTAIN'].values()))
            else:
                assert summary['owner_rated']==135
                for version in ('06','07'):assert summary['rating_agreement'][version]==prior_summary['rating_agreement'][version]
                rated=[r for r in rows if (r.get('owner_rating') or {}).get('decision') in ('KEEP','DROP')]
                assert len(rated)==135
                for version in ('05','06','07','08'):
                    assert summary['rating_agreement'][version]==dict(agree=sum(r['verdict_'+version]==r['owner_rating']['decision'] for r in rated),FP=sum(r['verdict_'+version]=='DROP' and r['owner_rating']['decision']=='KEEP' for r in rated),FN=sum(r['verdict_'+version]=='KEEP' and r['owner_rating']['decision']=='DROP' for r in rated),UNC=sum(r['verdict_'+version]=='UNCERTAIN' for r in rated))
                    table={v:{rating:sum(r['verdict_'+version]==v and (r.get('owner_rating') or {}).get('decision','unrated')==rating for r in rows) for rating in ('KEEP','DROP','unrated')} for v in ('DROP','KEEP','UNCERTAIN')}
                    assert summary['rating_confusion'][version]==table
                    assert sum(sum(t.values()) for t in table.values())==888
            flips=load(D/f'flips_{cohort}.jsonl')
            assert {r['line_id'] for r in rows if r['verdict_07']!=r['verdict_08']}=={f['line_id'] for f in flips}
            assert summary['flip_count']==len(flips)
            for r in rows:
                a,b,previous=r['after'],r['before'],r['previous'];e=a['evidence'];g=e['gate'];cut=g['main_cut'];prev=previous['evidence']
                rid=r['line_id']
                assert b==old06[rid]['after'] and previous==old07[rid]['after']
                assert r['verdict_06']==b['verdict'] and r['verdict_07']==previous['verdict'] and r['verdict_08']==a['verdict']
                if cohort=='segeval1':
                    answer=owners[rid]['reader_answer']
                    assert r['reader_answer']==answer and r['reader_state']==owners[rid]['reader_state']
                    assert r['verdict_05']==sealed[rid]['segmentation']['verdict']
                    flags=('multi_line','neighbour_whole_word','rotated','horizontally_missegmented')
                    faulty=any(answer.get(k)=='yes' for k in flags) or bool(set(answer.get('errors',[])) & {'extra_text','missing_word_or_span','crop_clipped','merged_two_lines'})
                    unresolved=any(answer.get(k)!='no' for k in flags) or not isinstance(answer.get('errors'),list)
                    assert r['owner_standard_state']==('faulty' if faulty else 'unresolved' if unresolved else 'fine')
                else:
                    assert r['owner_rating']==old06[rid]['owner_rating']==old07[rid]['owner_rating']
                    assert r['verdict_05']==old06[rid]['verdict_before']==old06[rid]['before']['judgements']['current']['verdict']
                assert a['policy_sha256']==policy_sha and a['tool_version']=='0.8'
                assert a['binding']==b['binding']==previous['binding'] and a['raw_text_sha256']==b['raw_text_sha256']==previous['raw_text_sha256']
                # Fresh orientation records carry elapsed wall time; compare every
                # other frame field exactly, and retain both original timings.
                frames=[copy.deepcopy(x['frame']) for x in (a,previous)]
                for frame in frames:
                    if frame.get('orientation'):
                        frame['orientation']['evidence'].pop('seconds',None)
                assert frames[0]==frames[1] and e['detected_rows']==prev['detected_rows'] and e['lines']==prev['lines']
                counts['frame_and_detector_evidence_exact_excluding_elapsed_seconds']+=1
                assert 'row_frame_taller' not in cut
                expected_cut={k:v for k,v in prev['gate']['main_cut'].items() if k not in ('row_frame_taller','cut')}
                assert {k:v for k,v in cut.items() if k!='cut'}==expected_cut
                assert cut['baseline_exit']==any(c['line']=='baseline' and 'leaves the crop' in c['meaning'] for c in cut['crossings'])
                assert cut['low_visibility_span']==any(s['min_visible']<.6 for s in cut['cut_spans'])
                assert cut['cut']==(cut['baseline_exit'] or cut['low_visibility_span'])
                counts['inventory_and_skew_diagnostics_exact']+=1
                # Independent gate reconstruction uses only the crop inventory and orientation.
                neighbours=[l for l in e['lines'] if l['side']!='main']
                assert g['whole_words']==sum(l['whole_words'] for l in neighbours)
                assert g['cutoff_words']==sum(l['cutoff_words'] for l in neighbours)
                assert g['complete_rows']==[l['index'] for l in neighbours if l['complete']]
                expected=('PASS','gate: pass')
                if not any(l['side']=='main' and l['votes']>0 for l in e['lines']):expected=('UNCERTAIN','gate: no main row found')
                elif e['orientation_resolved'] is False:expected=('UNCERTAIN','gate: reading direction unresolved')
                elif g['complete_rows']:expected=('DROP','gate: second complete line')
                elif g['whole_words']>2:expected=('DROP','gate: too many whole neighbour words')
                assert (g['verdict'],g['reason'])==expected
                request=dict(operation='decide',policy_sha256=policy_sha)
                assert g==service.call(dict(request,evidence=dict(e,gate_only=True)))
                counts['gate_decisions_exact']+=1
                decision=dict(verdict=a['verdict'],reason=a['reason'])
                assert service.call(dict(request,evidence=e))==decision
                counts['final_decisions_exact']+=1
                for diagnostic in ({},dict(cut=True,baseline_exit=True,low_visibility_span=True,crossings=[{'line':'baseline','meaning':'leaves the crop'}],cut_spans=[{'min_visible':0}],cut_letters=[{'body_cut':1}],row_frame_height=1000000,upright_box_height=1)):
                    without=dict(e,gate=dict(main_cut=diagnostic),neighbour_evidence=None,lines=[{k:v for k,v in l.items() if not k.startswith('context_')} for l in e['lines']])
                    assert service.call(dict(request,evidence=without))==decision
                counts['context_and_cut_diagnostics_invariant']+=1
                for line in e['lines']:
                    assert line['whole_words']==sum(w['whole'] for w in line['word_groups'])
                    assert line['cutoff_words']==sum(not w['whole'] for w in line['word_groups'])
                    assert line['complete']==(line['votes']>=6 and line['bodies']>=6 and line['visible']>=.9 and line['coverage']>=.6)
                    for word in line['word_groups']:assert word['whole']==(word['bodies']>=2 and not word['touches_horizontal_edge'])
                if g['verdict']=='PASS':
                    assert e['box_evidence']==b['evidence']['box_evidence'] and e['padding_evidence']==b['evidence']['padding_evidence']
                    counts['stage_b_exact']+=1
                    box=e['box_evidence'];rf=box['row_frame'];script=box['prediction']['group']
                    assert predictor.call(dict(long_side=max(rf['length'],rf['height']),short_side=min(rf['length'],rf['height']),script=script))==box['prediction']
                    counts['predictions_exact']+=1
                    ratio=(e['characters']+1)/(box['predictions'][2]+1)
                    expected_verdict='DROP' if ratio<.5 or ratio>1.5 or e['padding_evidence']['total_padding_line_heights']>1.5 else 'KEEP'
                    assert a['verdict']==expected_verdict
                    if r['line_id'] in ('847e1ec1-p000015-l0035','b8b6779da9a68fbed0ccdb5b-p000011-l0018','51db636c-p000048-l0024'):
                        witnesses[r['line_id']]=dict(verdict=a['verdict'],reason=a['reason'],ratio=ratio,characters=e['characters'],expected=box['predictions'][2],padding=e['padding_evidence']['total_padding_line_heights'],theta=rf['angle_deg'],gate=g['verdict'],skew_diagnostic_cut=cut['cut'],whole_words=g['whole_words'],cutoff_words=g['cutoff_words'])
                else:
                    assert not e['box_evidence']['available'] and not e['padding_evidence']['available']
                    counts['gate_blocks_stage_b']+=1
                counts['rows']+=1
    finally:service.close();predictor.close()
    (D/'witnesses.json').write_text(json.dumps(witnesses,ensure_ascii=False,indent=2)+'\n')
    return dict(counts)


if __name__=='__main__':
    source_scope()
    result=dict(status='PASS',**replay_readback())
    (D/'replay_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
