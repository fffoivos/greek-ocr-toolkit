"""Offline calibration recovery, dash seal and root namespace regression checks."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/numerics'))
from n1_map_answers import map_answers, output_stem, ROOTS
from n1_calibration import score, lead_gate


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def calibration():
    base = ROOT/'artifacts/n1'
    key = json.loads((base/'n1cal2/keys/cal01.json').read_text())
    answers = rows(base/'n1cal2/answers/cal01.r1.jsonl')
    return key, map_answers(key, answers), rows(base/'controls/approved.jsonl'), rows(base/'controls/dash_types.jsonl')


def test_real_raw_answers_dash_seal_and_lead_gate():
    result = score(*calibration())
    assert result['items'] == 82 and result['correct'] == 81
    assert lead_gate(result)['status'] == 'PASS'
    assert lead_gate(result)['typed_dash_correct'] == 24
    assert result['per_class']['any dash']['correct'] == 2
    assert result['confusion_matrix']['en dash'] == {'en dash': 5, 'hyphen': 1}
    assert [d['item_id'] for d in result['disagreements']] == ['kd4ec059384']


@pytest.mark.parametrize('defect', ['missing_type', 'duplicate_type', 'wrong_type', 'missing_row', 'duplicate_row', 'wrong_slot'])
def test_scoring_rejects_broken_seals_or_mapping(defect):
    key, mapped, approved, assignments = calibration()
    if defect == 'missing_type': assignments.pop()
    elif defect == 'duplicate_type': assignments.append(assignments[0])
    elif defect == 'wrong_type': assignments[0]['truth'] = 'em dash'
    elif defect == 'missing_row': mapped['slots'].pop()
    elif defect == 'duplicate_row': mapped['slots'][-1] = mapped['slots'][0]
    else: mapped['slots'][0]['slot_id'] = mapped['slots'][1]['slot_id']
    with pytest.raises(ValueError): score(key, mapped, approved, assignments)


@pytest.mark.parametrize('defect', ['raised', 'false_raised', 'dash', 'disagreements'])
def test_each_lead_gate_fails_independently(defect):
    result = copy.deepcopy(score(*calibration()))
    if defect == 'raised': result['per_class']['raised dot']['correct'] = 3
    elif defect == 'false_raised': result['confusion_matrix']['comma']['raised dot'] = 1
    elif defect == 'dash': result['per_class']['hyphen']['correct'] = 12
    else: result['disagreements'] *= 4
    assert lead_gate(result)['status'] == 'HOLD'


def test_dash_threshold_inclusive_and_three_disagreements_allowed():
    result = copy.deepcopy(score(*calibration()))
    result['per_class']['hyphen']['correct'] = 13
    result['disagreements'] *= 3
    assert lead_gate(result)['typed_dash_correct'] == 23
    assert lead_gate(result)['status'] == 'PASS'


def test_namespace_includes_every_root_and_rejects_traversal(tmp_path):
    stems = [output_stem(tmp_path, root, 'cal01' if 'cal' in root else 'ctx01', 'r1') for root in ROOTS]
    assert len(set(stems)) == len(ROOTS)
    assert all(p.parent == tmp_path/'answers'/root for p, root in zip(stems, ROOTS))
    for args in [('n1cal2', '../cal01', 'r1'), ('../n1', 'ctx01', 'r1'), ('n1', 'ctx01', '../r1')]:
        with pytest.raises(ValueError): output_stem(tmp_path, *args)


def test_mapper_cli_uses_same_root_namespace(tmp_path):
    base = ROOT/'artifacts/n1'
    result = subprocess.run([sys.executable, '-B', str(ROOT/'scripts/numerics/n1_map_answers.py'),
        str(base/'n1cal2/keys/cal01.json'), str(base/'n1cal2/answers/cal01.r1.jsonl'),
        '--root', 'n1cal2', '--context', 'cal01', '--output-base', str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    target = tmp_path/'answers/n1cal2/cal01.r1.mapped.json'
    assert len(json.loads(target.read_text())['slots']) == 82
    assert not list((tmp_path/'answers').glob('cal01.*'))


def test_combiner_consumes_canonical_answer_directory(tmp_path):
    from n1t_combine import load_reads
    private = tmp_path/'n1t2'
    (private/'keys').mkdir(parents=True)
    key = dict(readers={'r1': ['item']}, items={'item': dict(slot_id='slot', control_truth=None,
        option_map={'A': 'comma'})})
    (private/'keys/ctx01.json').write_text(json.dumps(key))
    stem = output_stem(tmp_path, 'n1t2', 'ctx01', 'r1')
    stem.parent.mkdir(parents=True)
    for suffix, value in [('jsonl', dict(item_id='item', answer='A', confidence='high')),
                          ('scan.json', dict(ok=True, scanner_version=4)),
                          ('run.json', dict(rc=0, model='gpt-6.1-sol'))]:
        Path(str(stem)+'.'+suffix).write_text(json.dumps(value)+'\n')
    reads, gates = load_reads(private)
    assert reads['slot'][0]['meaning'] == 'comma'
    assert gates['ctx01.r1']['status'] == 'VALID'
