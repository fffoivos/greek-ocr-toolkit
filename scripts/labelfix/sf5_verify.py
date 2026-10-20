"""Verify SF5 artifact custody and change scope without Git mutation."""
from greekocr.ops.data_root import input_path as _data_input
import ast
import json
from pathlib import Path
import re
import subprocess

from greekocr.labelfix import release_gate as gate
from scripts.labelfix.clariden.r1_common import rows,sha256,write_json
from scripts.labelfix.sf5_measure import DOC


def main():
    ev=DOC/'SF5_evidence'
    changes={
        'greekocr/labelfix/text.py':{'word_final_elision','spacing_breathing','punctuation_sites','elision_alias_key'},
        'greekocr/labelfix/release_gate.py':{'_render_reading','_punctuation','_letters','_breathing_pair','release_text','edit_guard'},
        'scripts/labelfix/clariden/l1_common.py':{'overlay','release'},
    }
    changed_functions={};sources={}
    for path,allowed in changes.items():
        frozen=Path('artifacts/labelfix_sf5/before')/path
        assert subprocess.check_output(['git','show','c6064650:'+path])==frozen.read_bytes()
        old=ast.parse(frozen.read_text());new=ast.parse(Path(path).read_text())
        def functions(tree):return {n.name:ast.dump(n,include_attributes=False) for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
        a,b=functions(old),functions(new)
        actual={n for n in a.keys()|b.keys() if a.get(n)!=b.get(n)}
        assert actual<=allowed,(path,actual-allowed)
        changed_functions[path]=sorted(actual)
        sources[path]=sha256(path)
    for name in ('witness_inputs_receipt.json','heldout/receipt.json','m2_dev/receipt.json'):
        r=json.loads((ev/name).read_text())
        for path,digest in r['inputs'].items():assert sha256(path)==digest,path
        if 'outputs' in r:
            for path,digest in r['outputs'].items():assert sha256((ev/name).parent/path)==digest,path
            assert r['script_sha256']==sha256('scripts/labelfix/sf5_measure.py')
            assert r['policy']==gate.policy_binding()
    wi=json.loads((ev/'witness_inputs_receipt.json').read_text())
    assert wi['runtime_sha256']==sha256(_data_input(ev/'witness_inputs.jsonl.gz'))
    w=list(rows(ev/'witness_results.jsonl.gz'))
    assert len(w)==56 and sum(x['consensus_kept'] for x in w)==sum(x['consensus'] for x in w)==59
    assert not any(x['consensus_deleted'] or x['combining_marks_changed'] for x in w)
    known=[x for x in w if x['kind'].startswith('known_reader_')]
    assert len(known)==2 and all(x['before']==x['after'] for x in known)
    capitals=[x for x in w if x['kind']=='capital_breathing']
    assert len(capitals)==2 and all(x['after']==x['before'].replace("-'Ἀ",'-Ἀ') for x in capitals)
    h=json.loads((ev/'heldout/metrics.json').read_text())
    assert h['mark_rows']['before']==h['mark_rows']['after']
    assert h['slot_mode_records_identical']==81700 and h['mark_events_identical']
    for mode in gate.MODES:
        e=h['elision']['after'][mode]['effective_release']
        assert e['kept']+e['deleted']==213 and e['added']==1
        assert h['elision_census']['after'][mode]['both_deleted']==0
    dev=json.loads((ev/'m2_dev/metrics.json').read_text())
    assert dev['before']['marks']==dev['after']['marks']
    for mode in gate.MODES:
        assert dev['after']['elision'][mode]['kept'] is None
    git_before=json.loads((ev/'git_before.json').read_text())
    gitdir=Path(subprocess.check_output(['git','rev-parse','--absolute-git-dir'],text=True).strip())
    git_after={str(p):sha256(p) for p in gitdir.rglob('*') if p.is_file()}
    assert git_before==git_after
    log=(ev/'tests_after.log').read_text()
    assert 'FAILED ' not in log
    passed=int(re.findall(r'(\d+) passed',log)[-1])
    assert passed==847
    assert '1 error' in log and 'test_server_appends_each_decision_and_serves_static' in log
    report=(DOC/'SF5_REPORT.md').read_text()
    assert report.splitlines()[-1].startswith('SF5 RESULT: policy sf5-release-v1;')
    witness_table=report.split('| Line ID | Google original |',1)[1].split('Other Google→released changes',1)[0]
    assert len([x for x in witness_table.splitlines() if x.startswith('| ') and any(r['id'] in x for r in w)])==56
    diff=subprocess.run(['git','diff','--check'],check=True,capture_output=True,text=True)
    result=dict(schema='sf5-verification-v1',policy=gate.policy_binding(),complete=True,
        production_change_scope=changed_functions,source_hashes=sources,
        frozen_sources_match_c6064650=True,git_metadata_files=len(git_after),git_metadata_unchanged=True,
        witnesses=56,consensus_elision_atoms_kept=59,consensus_elision_atoms=59,
        double_breathings_fixed=2,known_reader_errors_unchanged=2,
        heldout_mark_slot_mode_records_identical=81700,heldout_mark_rows_identical=True,
        locked_ii_records_evaluated=0,m2_dev_elision_truth='UNKNOWN: zero certified scopes',
        tests_passed=passed,tests_environment_setup_errors=1,all_labelfix_tests_green=False,
        unresolved_environment='sandbox denies socket.bind in unchanged HTTP capture test',
        network=False,detector_runs=0,r1_runs=0,ctc_runs=0,git_diff_check_passed=diff.returncode==0,
        evidence={str(p):sha256(p) for p in sorted(ev.rglob('*')) if p.is_file() and p.name!='verification.json'},
        report_sha256=sha256(DOC/'SF5_REPORT.md'),
        implementation_scripts={str(p):sha256(p) for p in (Path(__file__),Path('scripts/labelfix/sf5_measure.py'),Path('scripts/labelfix/sf5_report.py'),Path('tests/labelfix/test_sf5.py'))})
    write_json(ev/'verification.json',result)
    print('SF5 verified:',passed,'passed; 1 environment setup error; Git metadata unchanged')


if __name__=='__main__':main()
